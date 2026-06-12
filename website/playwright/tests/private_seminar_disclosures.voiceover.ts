/**
 * Screen-reader accessibility tests for the Private Seminar Disclosures page.
 *
 * These tests simulate the experience of a blind user navigating entirely by
 * keyboard and VoiceOver.  Each test answers one question:
 *   "Can a VoiceOver user accomplish this task?"
 *
 * ── Strategy ──────────────────────────────────────────────────────────────────
 * Tests in sections 1–5 drive a real browser with keyboard input (Tab, Space,
 * Shift+Tab) and query ARIA attributes to compute what VoiceOver would announce.
 * This mirrors exactly what a blind user hears — fast and deterministic.
 *
 * Test in section 6 drives real VoiceOver via AppleScript to verify the actual
 * spoken output end-to-end.
 *
 * ── Core helper: getAnnouncement(page) ────────────────────────────────────────
 * Returns the string VoiceOver would speak for the currently focused element:
 *   "name, [states…,] role"  e.g.  "Filter disclosures by year, combobox"
 * Implements the ARIA accessible-name algorithm:
 *   aria-label  >  aria-labelledby  >  visible text (skipping aria-hidden subtrees)
 *
 * Figma reference: file MpYvDySIPULl7f1RQBvb3y, node 13913:9549
 * Run:  npx playwright test --config playwright/playwright.config.ts
 */

import { test, expect, Page } from "@playwright/test";
import { voiceOverTest } from "@guidepup/playwright";
import { voiceOverKeyCodeCommands, macOSActivate } from "@guidepup/guidepup";

const BASE        = process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:8000";
const PAGE_URL    = `${BASE}/judges/private-seminar-disclosures/`;
const CHROME_APP  = "Google Chrome for Testing";

// ── helpers ───────────────────────────────────────────────────────────────────

/**
 * Compute what VoiceOver would announce for the currently focused element.
 * Format mirrors VoiceOver speech:  "name, [state, …,] role"
 */
async function getAnnouncement(page: Page): Promise<string> {
    return page.evaluate(() => {
        const el = document.activeElement as HTMLElement | null;
        if (!el || el === document.body) return "(body)";

        // Accessible name — ARIA spec §4.3
        function visibleText(node: Element): string {
            if (node.getAttribute("aria-hidden") === "true") return "";
            return Array.from(node.childNodes)
                .map(child =>
                    child.nodeType === Node.TEXT_NODE
                        ? (child.textContent ?? "")
                        : visibleText(child as Element),
                )
                .join(" ")
                .replace(/\s+/g, " ")
                .trim();
        }
        const ariaLabel    = el.getAttribute("aria-label");
        const labelledById = el.getAttribute("aria-labelledby");
        const name =
            ariaLabel?.trim() ??
            (labelledById
                ? labelledById
                      .split(" ")
                      .map(id => document.getElementById(id)?.textContent?.trim() ?? "")
                      .join(" ")
                      .trim()
                : visibleText(el));

        // Semantic role
        const explicitRole = el.getAttribute("role");
        const tag = el.tagName.toLowerCase();
        const role =
            explicitRole ??
            (tag === "a" && el.hasAttribute("href") ? "link"
             : tag === "button"                      ? "button"
             : tag === "select"                      ? "combobox"
             :                                         tag);
        const headingLevel = /^h([1-6])$/.exec(tag)?.[1];
        const roleStr = headingLevel ? `heading level ${headingLevel}` : role;

        // ARIA states
        const states: string[] = [];
        if (el.getAttribute("aria-pressed")  === "true")  states.push("pressed");
        if (el.getAttribute("aria-expanded") === "true")  states.push("expanded");
        if (el.getAttribute("aria-expanded") === "false") states.push("collapsed");
        if (el.getAttribute("aria-checked")  === "true")  states.push("checked");
        if (el.getAttribute("aria-checked")  === "false") states.push("unchecked");

        return [name, ...states, roleStr].filter(Boolean).join(", ");
    });
}

/**
 * Press Tab until the focused element satisfies a predicate.
 * Throws a clear error after maxTabs presses so failures are easy to diagnose.
 */
async function tabUntil(
    page:    Page,
    match:   (announcement: string) => boolean,
    maxTabs: number = 40,
): Promise<string> {
    for (let i = 0; i < maxTabs; i++) {
        await page.keyboard.press("Tab");
        const a = await getAnnouncement(page);
        if (match(a)) return a;
    }
    const last = await getAnnouncement(page);
    throw new Error(
        `tabUntil: condition not met within ${maxTabs} Tab presses.  Last: "${last}"`,
    );
}

/**
 * VoiceOver-only: exit all nested containers and position VO cursor on the h1.
 */
async function enterWebContent(page: Page, voiceOver: any): Promise<void> {
    await macOSActivate(CHROME_APP);
    await page.bringToFront();
    await page.locator("body").waitFor();
    for (let i = 0; i < 6; i++) {
        await voiceOver.perform(voiceOverKeyCodeCommands.stopInteractingWithItem);
    }
    await voiceOver.clearItemTextLog();
    await voiceOver.clearSpokenPhraseLog();
    await voiceOver.perform(voiceOverKeyCodeCommands.findNextHeading); // → h1
}


// ═══════════════════════════════════════════════════════════════════════════════
// 1. PAGE STRUCTURE
//    What does the user hear when they first arrive on the page?
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Private Seminar Disclosures — page structure", () => {
    test.beforeEach(async ({ page }) => { await page.goto(PAGE_URL); });

    test("h1 is a real heading element containing 'Private Seminar Disclosures'", async ({ page }) => {
        // VoiceOver's heading rotor (VO+U → Headings) only shows real <h1>–<h6>.
        // A <div> styled to look like a heading is invisible to that navigation.
        const h1 = page.locator("h1").first();
        await expect(h1).toBeVisible();
        await expect(h1).toContainText("Private Seminar Disclosures");
        expect(await h1.evaluate(el => el.tagName.toLowerCase())).toBe("h1");
    });

    test("h1 contains a link back to the Judge Information page", async ({ page }) => {
        // A blind user arriving here via the tile needs to know how to go back.
        // The link must be in the heading so it's discoverable via the heading rotor.
        const backLink = page.locator("h1 a").first();
        await expect(backLink).toBeVisible();
        await expect(backLink).toContainText("Judge Information");
        const href = await backLink.getAttribute("href");
        expect(href).toBeTruthy();
    });

    test("h1 has tabindex=0 — VoiceOver focus can land on it via Tab", async ({ page }) => {
        // Pages without a focusable h1 force VoiceOver users to Tab past all nav chrome
        // before reaching page content.  tabindex=0 lets them jump to the title directly.
        const h1 = page.locator('[data-testid="page-title"]');
        const tabindex = await h1.getAttribute("tabindex");
        expect(tabindex).toBe("0");
    });

    test("intro text is visible in the page container", async ({ page }) => {
        // After landing on the h1, the user reads down to understand the page.
        // The intro container must exist and not be empty.
        const intro = page.locator(".seminar-intro");
        await expect(intro).toBeVisible();
    });

    test("page container exists with id 'private-seminar-page'", async ({ page }) => {
        // Scoping landmark — lets AT users navigate directly to page content.
        await expect(page.locator("#private-seminar-page")).toBeVisible();
    });
});


// ═══════════════════════════════════════════════════════════════════════════════
// 2. YEAR FILTER
//    Can a blind user find, read, and operate the year filter?
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Private Seminar Disclosures — year filter", () => {
    test.beforeEach(async ({ page }) => { await page.goto(PAGE_URL); });

    test("year-filter select has an accessible label", async ({ page }) => {
        // VoiceOver announces the label of a <select> before its role.
        // Without a label, the user hears only "combobox" — no context.
        const hasSelect = await page.locator("#year-select").count() > 0;
        if (!hasSelect) {
            test.info().annotations.push({ type: "note", description: "No disclosures — year filter not rendered" });
            return;
        }
        const select = page.locator("#year-select");
        const ariaLabel = await select.getAttribute("aria-label");
        const labelFor  = await page.locator('label[for="year-select"]').count() > 0;
        expect(Boolean(ariaLabel) || labelFor).toBe(true);
        if (ariaLabel) {
            expect(ariaLabel.trim().length).toBeGreaterThan(0);
        }
    });

    test("Tab reaches the year-filter select — it announces as a combobox with a label", async ({ page }) => {
        // Users press Tab to reach interactive controls.  VoiceOver announces:
        //   "Filter disclosures by year, combobox" (or similar label).
        // Without Tab reachability, a keyboard-only user cannot use the filter.
        const hasSelect = await page.locator("#year-select").count() > 0;
        if (!hasSelect) return; // no disclosures — filter not rendered, skip

        const announcement = await tabUntil(
            page,
            a => /year-select|filter.*year|year.*filter|combobox/i.test(a),
        );
        expect(announcement.toLowerCase()).toMatch(/combobox|listbox|select/);
    });

    test("year-filter select is keyboard-operable — focus lands and is held", async ({ page }) => {
        const hasSelect = await page.locator("#year-select").count() > 0;
        if (!hasSelect) return;

        await page.locator("#year-select").focus();
        const focused = await page.evaluate(
            () => document.activeElement?.getAttribute("id"),
        );
        expect(focused).toBe("year-select");
    });

    test("filter form uses GET — URL is shareable and readable by screen readers", async ({ page }) => {
        // GET forms update the URL when submitted.  VoiceOver users can share the
        // filtered URL and return to the same state — a POST form would break this.
        const hasForm = await page.locator("#year-filter-form").count() > 0;
        if (!hasForm) return;

        const method = await page.locator("#year-filter-form").getAttribute("method");
        expect(method?.toLowerCase()).toBe("get");
    });

    test("year-filter options have 4-digit year values — meaningful when read aloud", async ({ page }) => {
        // VoiceOver reads the text of each <option>.  Non-numeric values like 'yr2024'
        // sound awkward.  Pure years ('2024') are announced clearly.
        const hasSelect = await page.locator("#year-select").count() > 0;
        if (!hasSelect) return;

        const options = page.locator("#year-select option");
        const count = await options.count();
        for (let i = 0; i < count; i++) {
            const val = await options.nth(i).getAttribute("value");
            if (val && val !== "") {
                expect(val).toMatch(/^\d{4}$/);
            }
        }
    });
});


// ═══════════════════════════════════════════════════════════════════════════════
// 3. DISCLOSURE CARDS
//    Can a blind user find and read individual disclosure records?
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Private Seminar Disclosures — disclosure cards", () => {
    test.beforeEach(async ({ page }) => { await page.goto(PAGE_URL); });

    test("each disclosure card has a non-empty judge name element", async ({ page }) => {
        // The judge name is the first thing a blind user encounters in each card.
        // If it's empty, VoiceOver announces nothing — no identity for the record.
        const cards = page.locator(".disclosure-card");
        const count = await cards.count();
        if (count === 0) return; // empty state — nothing to check

        for (let i = 0; i < count; i++) {
            const name = await cards.nth(i).locator(".judge-name").textContent();
            expect((name ?? "").trim().length).toBeGreaterThan(0);
        }
    });

    test("each disclosure card contains text labels for all required fields", async ({ page }) => {
        // The card body markup uses `.disclosure-field-group` rather than
        // dl/dt/dd. "Program Provider(s):" lives in a `.field-label`; Program,
        // Date, and Location are inlined into `.field-value` strings (e.g.
        // "Date: 06/15/2024"). VoiceOver reads each <p> on its own, so the
        // labels are still announced — they're just in a different element.
        const cards = page.locator(".disclosure-card");
        const count = await cards.count();
        if (count === 0) return;

        const body = cards.first().locator(".disclosure-body");
        const bodyText = (await body.textContent()) ?? "";
        expect(/program provider/i.test(bodyText)).toBe(true);
        expect(/program:/i.test(bodyText)).toBe(true);
        expect(/date/i.test(bodyText)).toBe(true);
        expect(/location/i.test(bodyText)).toBe(true);
    });

    test("disclosure body groups labels with their values — no orphaned labels", async ({ page }) => {
        // An explicit `.field-label` (Provider / Topics / Supporter) must
        // always sit inside a `.disclosure-field-group` next to its
        // corresponding `.field-value`, so VoiceOver reads label → value in
        // order. We assert each label paragraph has a sibling value paragraph
        // inside the same field-group.
        const cards = page.locator(".disclosure-card");
        const count = await cards.count();
        if (count === 0) return;

        const orphans = await cards.first().evaluate((el) => {
            const labels = Array.from(el.querySelectorAll(".disclosure-body .field-label"));
            return labels
                .filter((label) => {
                    const group = label.closest(".disclosure-field-group");
                    return !group || !group.querySelector(".field-value");
                })
                .map((l) => l.textContent?.trim());
        });
        expect(orphans, `expected zero orphaned labels, got: ${JSON.stringify(orphans)}`).toEqual([]);
    });

    test("date field is formatted MM/DD/YYYY — VoiceOver reads it naturally", async ({ page }) => {
        // Dates like '2024-01-15' are announced as "two thousand twenty-four hyphen…"
        // MM/DD/YYYY is announced as "January fifteenth twenty twenty-four" on most platforms.
        // The Date is inlined into `.field-value--light` as "Date: MM/DD/YYYY".
        const cards = page.locator(".disclosure-card");
        if (await cards.count() === 0) return;

        const dateText = await cards.first()
            .locator(".field-value--light", { hasText: "Date:" })
            .textContent();
        expect((dateText ?? "").trim()).toMatch(/^Date:\s*\d{2}\/\d{2}\/\d{4}$/);
    });

    test("judge name header background is Figma-confirmed light blue (visual + AT safe)", async ({ page }) => {
        // Confirmed from Figma file MpYvDySIPULl7f1RQBvb3y, node 13913:9549 Frame 14.
        // The color itself doesn't affect AT, but we assert it for design-spec fidelity.
        const cards = page.locator(".disclosure-card");
        if (await cards.count() === 0) return;

        const bg = await cards.first().locator(".judge-name").evaluate(
            el => getComputedStyle(el).backgroundColor,
        );
        expect(bg).toBe("rgb(241, 249, 252)");
    });
});


// ═══════════════════════════════════════════════════════════════════════════════
// 4. EMPTY STATE
//    When no disclosures exist, the user must be told — not left with silence.
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Private Seminar Disclosures — empty state", () => {
    test("empty-state message exists and is non-empty when no cards are present", async ({ page }) => {
        await page.goto(PAGE_URL);
        const hasCards = await page.locator(".disclosure-card").count() > 0;
        if (hasCards) {
            test.info().annotations.push({ type: "note", description: "Disclosures present — empty-state skipped" });
            return;
        }
        // Without this message, VoiceOver reads a completely blank page after the intro.
        // The user has no way to distinguish "no records" from a page-load error.
        const msg = page.locator('[data-testid="empty-message"]');
        await expect(msg).toBeVisible();
        const text = await msg.textContent();
        expect((text ?? "").trim().length).toBeGreaterThan(5);
    });

    test("empty-state message is not present when disclosures exist", async ({ page }) => {
        await page.goto(PAGE_URL);
        const hasCards = await page.locator(".disclosure-card").count() > 0;
        if (!hasCards) return;
        await expect(page.locator('[data-testid="empty-message"]')).toHaveCount(0);
    });

    test("grid and empty state never appear simultaneously", async ({ page }) => {
        await page.goto(PAGE_URL);
        const hasGrid  = await page.locator(".disclosure-grid").count() > 0;
        const hasEmpty = await page.locator(".disclosure-empty").count() > 0;
        // Exactly one must be true (XOR)
        expect(hasGrid && hasEmpty).toBe(false);
        expect(hasGrid || hasEmpty).toBe(true);
    });
});


// ═══════════════════════════════════════════════════════════════════════════════
// 5. DOM TEXT AUDIT
//    Fast, complete verification that every visible text element on the page
//    is accessible to VoiceOver.
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Private Seminar Disclosures — DOM text accessibility audit", () => {
    test.beforeEach(async ({ page }) => { await page.goto(PAGE_URL); });

    test("no visible text in page content is hidden from screen readers via aria-hidden", async ({ page }) => {
        // Walk every text node in the page container.  If a text node is visible to
        // sighted users but its ancestor has aria-hidden="true", VoiceOver will
        // never read it — an invisible barrier for blind users.
        const violations = await page.evaluate(() => {
            const found: string[] = [];

            function isAriaHidden(el: Element | null): boolean {
                let node: Element | null = el;
                while (node) {
                    if (node.getAttribute("aria-hidden") === "true") return true;
                    node = node.parentElement;
                }
                return false;
            }

            function isVisuallyHidden(el: Element): boolean {
                const s = getComputedStyle(el);
                return s.display === "none" || s.visibility === "hidden";
            }

            function walk(node: Node): void {
                if (node.nodeType === Node.TEXT_NODE) {
                    const text = node.textContent?.trim();
                    if (!text || text.length < 3) return;
                    const parent = node.parentElement;
                    if (!parent || isVisuallyHidden(parent)) return;
                    if (isAriaHidden(parent)) {
                        found.push(`"${text.substring(0, 80)}"`);
                    }
                } else if (node.nodeType === Node.ELEMENT_NODE) {
                    if (isVisuallyHidden(node as Element)) return;
                    node.childNodes.forEach(walk);
                }
            }

            const root =
                document.getElementById("private-seminar-page") ??
                document.querySelector("main") ??
                document.body;
            walk(root);
            return found;
        });

        expect(
            violations,
            `These visible text fragments are inside aria-hidden containers — ` +
            `VoiceOver cannot read them:\n${violations.join("\n")}`,
        ).toHaveLength(0);
    });

    test("all interactive elements in the page container have a non-empty accessible name", async ({ page }) => {
        // Every button, link, and select within the page container must have an
        // accessible name.  Without one, VoiceOver announces only the role —
        // e.g. "combobox" — leaving blind users unable to tell elements apart.
        const nameless = await page.evaluate(() => {
            const found: string[] = [];
            const root = document.getElementById("private-seminar-page") ?? document.body;

            function computeName(el: Element): string {
                const ariaLabel  = el.getAttribute("aria-label")?.trim();
                const labelledBy = el.getAttribute("aria-labelledby");
                if (ariaLabel)  return ariaLabel;
                if (labelledBy) return document.getElementById(labelledBy)?.textContent?.trim() ?? "";

                // <select> is labelled by <label for="...">
                const id = el.getAttribute("id");
                if (id) {
                    const label = document.querySelector(`label[for="${id}"]`);
                    if (label) return label.textContent?.trim() ?? "";
                }
                return el.textContent?.trim() ?? "";
            }

            const selectors = ["button", "a[href]", "select", '[role="button"]', '[role="combobox"]'];
            for (const sel of selectors) {
                root.querySelectorAll<Element>(sel).forEach(el => {
                    const s = getComputedStyle(el);
                    if (s.display === "none" || s.visibility === "hidden") return;
                    if (el.hasAttribute("hidden")) return;
                    if (computeName(el).length === 0) {
                        found.push(
                            `<${el.tagName.toLowerCase()}> — ` +
                            el.outerHTML.substring(0, 120),
                        );
                    }
                });
            }
            return found;
        });

        expect(
            nameless,
            `These interactive elements have no accessible name — ` +
            `VoiceOver says only the role with no context:\n${nameless.join("\n")}`,
        ).toHaveLength(0);
    });

    test("all images are either aria-hidden (decorative) or have non-empty alt text", async ({ page }) => {
        // An image without alt text is announced as the filename or URL — confusing.
        const violations = await page.evaluate(() => {
            const found: string[] = [];
            document.querySelectorAll("img").forEach(img => {
                const s = getComputedStyle(img);
                if (s.display === "none" || s.visibility === "hidden") return;
                const ariaHidden = img.getAttribute("aria-hidden") === "true";
                const alt = img.getAttribute("alt"); // null = missing; "" = decorative OK
                if (!ariaHidden && alt === null) {
                    found.push(img.src || img.getAttribute("src") || "<img no src>");
                }
            });
            return found;
        });

        expect(
            violations,
            `These images have no alt attribute and are not aria-hidden — ` +
            `VoiceOver will announce the filename:\n${violations.join("\n")}`,
        ).toHaveLength(0);
    });
});


// ═══════════════════════════════════════════════════════════════════════════════
// 6. VOICEOVER FULL-PAGE SWEEP
//    Drives real VoiceOver through the entire Private Seminar Disclosures page.
//
//    Navigation path:
//      h1  → next (back-link)  →  next (intro text)
//          →  [if year filter] next (year-filter select)  →  stopInteracting
//          →  [if disclosures] findNextLink (judge name — first card)
//                               findNextLink (second card, if present)
//          →  [if empty state] next (empty-state message)
//
//    The page has no section headings below the h1, so we navigate purely with
//    next() and findNextLink rather than findNextHeading.
//
//    Each navigation step takes ~10 s.  Timeout is 10 minutes.
// ═══════════════════════════════════════════════════════════════════════════════

voiceOverTest.describe("Private Seminar Disclosures — VoiceOver full-page sweep", () => {
    voiceOverTest.setTimeout(600_000);

    voiceOverTest.beforeEach(async ({ page }) => {
        await page.goto(PAGE_URL);
    });

    voiceOverTest(
        "VoiceOver announces all page content — h1, back-link, intro, year filter (if present), and disclosures or empty state",
        async ({ page, voiceOver }) => {

            // ── 1. Land on h1 ─────────────────────────────────────────────────────
            await enterWebContent(page, voiceOver);

            // ── 2. Back-link inside h1 ────────────────────────────────────────────
            // The h1 contains a link back to the Judge Information page.
            // VoiceOver reads the link text when it moves past it.
            await voiceOver.next();

            // ── 3. Introductory text ──────────────────────────────────────────────
            await voiceOver.next();

            // ── 4. Year filter (conditional) ─────────────────────────────────────
            const hasFilter = await page.locator("#year-select").count() > 0;
            if (hasFilter) {
                // VoiceOver announces: "Filter disclosures by year, combobox"
                await voiceOver.next();
                // Exit the form control before using jump commands
                await voiceOver.perform(voiceOverKeyCodeCommands.stopInteractingWithItem);
            }

            // ── 5. Disclosure cards (conditional) ─────────────────────────────────
            // Find the first two cards (if present) using findNextLink.
            // Each card's judge-name is not a link, so we look for any link in the
            // page after the filter (e.g. the back-link resolved via the h1 is
            // already past — so the next links are in the card body or empty-state).
            const hasCards = await page.locator(".disclosure-card").count() > 0;
            if (hasCards) {
                // Walk forward from current position using next() to reach each card
                let cardsReached = 0;
                for (let i = 0; i < 20 && cardsReached < 2; i++) {
                    await voiceOver.next();
                    const phrase = await voiceOver.lastSpokenPhrase();
                    if (/disclosure-card|judge name|program provider|program:|date:|location/i.test(phrase)) {
                        cardsReached++;
                    }
                }
            }

            // ── 6. Collect everything VoiceOver spoke ────────────────────────────
            const log = (await voiceOver.spokenPhraseLog()).join("\n").toLowerCase();

            // ── 7. Assert every key element was announced ────────────────────────
            const assertions: [string, string | RegExp][] = [
                // Page title and heading level
                ["page title h1",              "private seminar disclosures"],
                ["heading level 1 announced",  "heading level 1"],

                // Back-link to Judge Information page
                ["back-link to Judge Info",    "judge information"],
            ];

            // Introductory text assertion (default is always present via model default)
            assertions.push(["intro text present", /seminar|disclosure|tax court/]);

            // Year filter — only assert if rendered
            if (hasFilter) {
                assertions.push(["year filter combobox label", /filter.*year|year.*filter|combobox/]);
            }

            // Cards or empty state
            if (hasCards) {
                assertions.push(["at least one judge name announced", /judge|chief|senior|special|trial/]);
                assertions.push(["program provider field announced",   /program provider/]);
            } else {
                assertions.push(["empty-state message announced", /no disclosures|nothing to report|at this time/]);
            }

            for (const [label, pattern] of assertions) {
                if (typeof pattern === "string") {
                    expect(log, `VoiceOver never announced: ${label}`).toContain(pattern);
                } else {
                    expect(log, `VoiceOver never announced: ${label}`).toMatch(pattern);
                }
            }
        },
    );

    voiceOverTest(
        "VoiceOver speaks every disclosure card's judge name and all required field labels — DOM-driven full card traversal",
        async ({ page, voiceOver }) => {
            // ── 1. Get the expected card list directly from the live DOM ──────────────
            // Source of truth: whatever the server renders is what VoiceOver must speak.
            // Test adapts automatically when disclosures are added/removed in the CMS.
            // If no disclosures exist, the test verifies the empty-state message instead.
            const expectedCards = await page.evaluate(() =>
                Array.from(document.querySelectorAll(".disclosure-card")).map(card => ({
                    judgeName: card.querySelector(".judge-name")?.textContent?.trim() ?? "",
                    // Card body uses .disclosure-field-group instead of dl/dt/dd.
                    // Collect each <p class="field-label"> + each .field-value
                    // text so we can audit that VoiceOver hits every visible label.
                    fields: Array.from(
                        card.querySelectorAll(".disclosure-body .field-label, .disclosure-body .field-value"),
                    ).map(el => el.textContent?.trim() ?? ""),
                })),
            );

            const hasCards = expectedCards.length > 0;

            // ── 2. Enter the page and position VoiceOver on the h1 ───────────────────
            await enterWebContent(page, voiceOver);

            if (!hasCards) {
                // ── Empty state path ──────────────────────────────────────────────────
                // Walk forward until we find the empty-state message.  It should appear
                // within a few next() calls after the intro text.
                let found = false;
                for (let i = 0; i < 10 && !found; i++) {
                    await voiceOver.next();
                    const phrase = await voiceOver.lastSpokenPhrase();
                    if (/no disclosures|nothing to report|at this time/i.test(phrase)) found = true;
                }
                const log = (await voiceOver.spokenPhraseLog()).join("\n").toLowerCase();
                expect(log, "VoiceOver must announce the empty-state message").toMatch(
                    /no disclosures|nothing to report|at this time/,
                );
                return;
            }

            // ── 3. Navigate past h1, intro, and optional year filter ─────────────────
            // This mirrors the setup in the full-page sweep so we start from a
            // deterministic position — right before the first disclosure card.
            await voiceOver.next(); // back-link inside h1
            await voiceOver.next(); // intro text

            const hasFilter = await page.locator("#year-select").count() > 0;
            if (hasFilter) {
                await voiceOver.next(); // year-filter combobox
                await voiceOver.perform(voiceOverKeyCodeCommands.stopInteractingWithItem);
            }

            // ── 4. Walk every disclosure card using next() ────────────────────────────
            // Disclosure cards are <li> elements with tabindex=0 — not links — so
            // findNextLink skips them entirely. next() (VO+Right) reads sequentially
            // through every element in the VO reading order: judge-name h2 → each
            // .field-label / .field-value <p>.
            //
            // We walk until we've seen every expected judge name, then stop.
            // maxSteps budget: per card ≈ 1 (name) + ~7 (label/value paragraphs) +
            // 1 (border) = ~10 steps.
            const maxSteps = expectedCards.length * 12 + 20;
            const namesRemaining = new Set(expectedCards.map(c => c.judgeName.toLowerCase()));
            const requiredLabels = new Set(["program provider", "program:", "date:", "location:"]);
            const foundLabels    = new Set<string>();

            for (let i = 0; i < maxSteps && namesRemaining.size > 0; i++) {
                await voiceOver.next();
                const phrase = await voiceOver.lastSpokenPhrase();
                const lower  = phrase.toLowerCase();

                // Check for judge names
                for (const name of namesRemaining) {
                    if (lower.includes(name)) namesRemaining.delete(name);
                }

                // Check for required field labels
                for (const label of requiredLabels) {
                    if (lower.includes(label)) foundLabels.add(label);
                }
            }

            // ── 5. Assert every judge's name was actually spoken ──────────────────────
            const log = (await voiceOver.spokenPhraseLog()).join("\n").toLowerCase();

            for (const card of expectedCards) {
                expect(
                    log,
                    `VoiceOver never spoke judge name "${card.judgeName}"`,
                ).toContain(card.judgeName.toLowerCase());
            }

            // ── 6. Assert all required field labels were spoken at least once ─────────
            // These appear in every card — if VoiceOver skipped any, the
            // .disclosure-field-group structure is broken.
            for (const label of requiredLabels) {
                expect(
                    log,
                    `VoiceOver never announced field label "${label}"`,
                ).toContain(label);
            }
        },
    );
});
