/**
 * Screen-reader accessibility tests for the Judge Information page.
 *
 * These tests simulate the experience of a blind user navigating entirely by
 * keyboard and VoiceOver.  Each test answers one question:
 *   "Can a VoiceOver user accomplish this task?"
 *
 * ── Strategy ──────────────────────────────────────────────────────────────────
 * Tests 1–21 drive a real browser with keyboard input (Tab, Space, Shift+Tab,
 * Escape) and query ARIA attributes to compute what VoiceOver would announce.
 * This mirrors exactly what a blind user hears — fast and deterministic.
 *
 * Test 22 drives real VoiceOver via AppleScript to verify the actual spoken
 * output end-to-end.
 *
 * ── Core helper: getAnnouncement(page) ────────────────────────────────────────
 * Returns the string VoiceOver would speak for the currently focused element:
 *   "name, [states…,] role"  e.g.  "All Judges, pressed, button"
 * Implements the ARIA accessible-name algorithm:
 *   aria-label  >  aria-labelledby  >  visible text (skipping aria-hidden subtrees)
 *
 * Figma reference: file MpYvDySIPULl7f1RQBvb3y, node 13913-8013
 * Run:   npx playwright test --config playwright/playwright.config.ts
 */

import { test, expect, Page } from "@playwright/test";
import { voiceOverTest } from "@guidepup/playwright";
import { voiceOverKeyCodeCommands, macOSActivate } from "@guidepup/guidepup";

const BASE        = process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:8000";
const JUDGES_URL  = `${BASE}/judges/`;
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
 * Returns the announcement for the matching element.
 * Throws a clear error after maxTabs presses so failures are easy to diagnose.
 *
 * The predicate may be sync OR async (async predicates can read additional
 * state from the page via `page.evaluate`). A previous version typed `match`
 * as a sync `(string) => boolean`, but the caller in "Tab moves from the last
 * filter button directly to the first judge card" passed an async predicate.
 * Since an async function always returns a Promise — which is truthy — the
 * loop would exit on the very first iteration without checking the real
 * condition. Awaiting the result and constraining the return type fixes that.
 */
async function tabUntil(
    page:    Page,
    match:   (announcement: string) => boolean | Promise<boolean>,
    maxTabs: number = 40,
): Promise<string> {
    for (let i = 0; i < maxTabs; i++) {
        await page.keyboard.press("Tab");
        const a = await getAnnouncement(page);
        if (await match(a)) return a;
    }
    const last = await getAnnouncement(page);
    throw new Error(
        `tabUntil: condition not met within ${maxTabs} Tab presses.  Last: "${last}"`,
    );
}

/**
 * VoiceOver-only: escape all nested containers and position VO cursor on the h1.
 * Uses stopInteractingWithItem (VO-Shift-Up) to exit Chrome containers before
 * findNextHeading jumps directly to the page title.
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

test.describe("Judge Information — page structure", () => {
    test.beforeEach(async ({ page }) => { await page.goto(JUDGES_URL); });

    test("h1 is a real heading element containing 'Judge Information'", async ({ page }) => {
        // VoiceOver's heading rotor (VO+U → Headings) only shows real <h1>–<h6> elements.
        // A <div> styled to look like a heading would be invisible to that navigation.
        // A blind user's first action on a new page is jump to h1 to orient themselves.
        const h1 = page.locator("h1").first();
        await expect(h1).toBeVisible();
        await expect(h1).toContainText("Judge Information");
        expect(await h1.evaluate(el => el.tagName.toLowerCase())).toBe("h1");
    });

    test("intro paragraph explains how to use the page", async ({ page }) => {
        // After landing on the h1, the user reads down (VO+Right) to understand the page.
        // This text must be present and visible — not hidden or replaced by ARIA description.
        const intro = page.locator(".judge-intro");
        await expect(intro).toBeVisible();
        await expect(intro).toContainText(/biography|clicking on the cards/i);
    });

    test("intro paragraph is keyboard-tab-focusable so Tab users hear it announced", async ({ page }) => {
        // Static <p>/<div> text isn't in the Tab order by default, so a
        // screen-reader user pressing Tab from the h1 would jump straight to
        // the filter buttons and never hear the intro. tabindex="0" puts the
        // intro into the focus chain so Tab from the page title lands on it
        // and the screen reader announces its content on focus.
        const intro = page.locator(".judge-intro");
        await expect(intro).toHaveAttribute("tabindex", "0");

        // Tab from the page-title button lands on the intro next.
        await page.locator("#page-title-start").focus();
        await page.keyboard.press("Tab");
        const focusedClass = await page.evaluate(
            () => document.activeElement?.className ?? "",
        );
        expect(focusedClass).toContain("judge-intro");
    });

    test("'Judge Biographies' section is an h2 — jumpable via VoiceOver heading rotor", async ({ page }) => {
        // Blind users jump between sections with H (quick nav) or VO+Cmd+H.
        // That only picks up real <h2> elements — not <div class="section-header">.
        // Without a true h2, the user must read through every judge card to find a new section.
        const hasH2 = await page.evaluate(() =>
            Array.from(document.querySelectorAll("h2")).some(el =>
                /biograph/i.test(el.textContent ?? ""),
            ),
        );
        expect(hasH2).toBe(true);
    });
});


// ═══════════════════════════════════════════════════════════════════════════════
// 2. FILTER BAR
//    Can a blind user find, read, and operate the judge-type filter?
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Judge Information — filter bar", () => {
    test.beforeEach(async ({ page }) => { await page.goto(JUDGES_URL); });

    test("filter bar has a group label — VoiceOver announces context on entry", async ({ page }) => {
        // Without aria-label on the <div role="group">, VoiceOver says only "group".
        // The user has no idea they've entered a filter control.
        // With aria-label="Filter judges by type", VoiceOver announces that label.
        const group = page.locator('[role="group"][aria-label="Filter judges by type"]');
        await expect(group).toBeVisible();
    });

    test("Tab reaches the filter bar — 'All Judges' announces name + pressed state", async ({ page }) => {
        // The user presses Tab repeatedly to move through the page.
        // The first filter button must announce BOTH its name AND that it is the active selection.
        // Expected: "All Judges, pressed, button"
        // Without "pressed": the user can't tell which filter is currently active.
        const announcement = await tabUntil(
            page,
            a => /all judges/i.test(a) && /button/.test(a),
        );
        expect(announcement.toLowerCase()).toContain("all judges");
        expect(announcement.toLowerCase()).toContain("pressed");
        expect(announcement.toLowerCase()).toContain("button");
    });

    test("all 5 filter buttons are Tab-reachable in order with correct labels", async ({ page }) => {
        // A screen reader user presses Tab through all five filter options.
        // Each must announce a meaningful label so the user knows what they're selecting.
        // Order must match the visual order (All Judges → Judges → Senior Judges → …).
        await tabUntil(page, a => /all judges/i.test(a) && /button/.test(a));

        const expectedLabels = [
            /^judges/i,
            /senior judges/i,
            /special trial judges/i,
            /senior special trial judges/i,
        ];
        for (const pattern of expectedLabels) {
            await page.keyboard.press("Tab");
            const a = await getAnnouncement(page);
            expect(a).toMatch(pattern);
            expect(a.toLowerCase()).toContain("button");
            // Inactive buttons must NOT carry "pressed" — that would confuse the user
            expect(a.toLowerCase()).not.toContain("pressed");
        }
    });

    test("Space activates 'Judges' filter — announcement changes to 'Judges, pressed, button'", async ({ page }) => {
        // Core interaction: the user selects a filter with Space.
        // Before: "Judges, button"        (not active)
        // After:  "Judges, pressed, button"  (now active)
        // Without this state change, the user has no confirmation their action worked.
        await tabUntil(page, a => /all judges/i.test(a) && /button/.test(a));
        await page.keyboard.press("Tab"); // advance to "Judges" button
        expect((await getAnnouncement(page)).toLowerCase()).not.toContain("pressed");

        await page.keyboard.press("Space");
        await page.waitForTimeout(300);
        expect((await getAnnouncement(page)).toLowerCase()).toContain("pressed");
    });

    test("activating 'Judges' makes 'All Judges' un-pressed — mutual exclusion is announced", async ({ page }) => {
        // If the previously active button keeps its "pressed" state after a new one is selected,
        // the user believes two filters are active simultaneously — misleading information.
        await tabUntil(page, a => /all judges/i.test(a) && /button/.test(a));
        await page.keyboard.press("Tab"); // "Judges" button
        await page.keyboard.press("Space");
        await page.waitForTimeout(300);

        await page.keyboard.press("Shift+Tab"); // back to "All Judges"
        const allJudges = await getAnnouncement(page);
        expect(allJudges.toLowerCase()).toContain("all judges");
        // Must no longer be pressed
        expect(allJudges.toLowerCase()).not.toContain("pressed");
    });

    test("activating a filter populates aria-live region — VoiceOver auto-announces the result", async ({ page }) => {
        // The aria-live="polite" region (#filter-announcement) is read automatically
        // by VoiceOver after the current speech finishes — the user hears "Showing Judges."
        // without having to navigate to it.  Without this, the filter change is silent.
        await tabUntil(page, a => /all judges/i.test(a) && /button/.test(a));
        await page.keyboard.press("Tab"); // "Judges" button
        await page.keyboard.press("Space");
        await page.waitForTimeout(400);

        const region = page.locator("#filter-announcement[aria-live]");
        const text   = await region.textContent();
        expect(text?.trim().length).toBeGreaterThan(0);
        expect(text?.toLowerCase()).toMatch(/show|judg/i);
    });
});


// ═══════════════════════════════════════════════════════════════════════════════
// 3. JUDGE CARDS
//    Can a blind user navigate to and read information about each judge?
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Judge Information — judge cards", () => {
    test.beforeEach(async ({ page }) => { await page.goto(JUDGES_URL); });

    test("Tab moves from the last filter button directly to the first judge card", async ({ page }) => {
        // After the filter bar the DOM order goes straight to judge card links.
        // If something is focusable in between but not useful, the user is confused.
        // This test confirms: 5 filter buttons → first judge card (≤3 extra tabs).
        await tabUntil(page, a => /all judges/i.test(a) && /button/.test(a));
        for (let i = 0; i < 4; i++) await page.keyboard.press("Tab"); // skip to last filter btn

        const isJudgeCard = await tabUntil(
            page,
            async (a) => {
                const pathname = await page.evaluate(
                    () => (document.activeElement as HTMLAnchorElement)?.pathname ?? "",
                );
                return /^\/judges\/.+\/$/.test(pathname);
            },
            3,
        );
        // The announcement must be a link
        const announcement = await getAnnouncement(page);
        expect(announcement.toLowerCase()).toContain("link");
    });

    test("first judge card announces both the judge's name and title", async ({ page }) => {
        // VoiceOver reads the full visible text of the link (name + title),
        // e.g. "Patrick J. Urda Chief Judge, link".
        // If the card contained only an image with no alt text, VoiceOver would say
        // "[filename] image, link" — useless to a blind user.
        const firstCard = page.locator('a[href^="/judges/"]:not([href="/judges/"])').first();
        await expect(firstCard).toBeVisible();

        const linkText = await firstCard.evaluate((el: HTMLElement) => {
            function visibleText(node: Element): string {
                if (node.getAttribute("aria-hidden") === "true") return "";
                return Array.from(node.childNodes)
                    .map(c =>
                        c.nodeType === Node.TEXT_NODE
                            ? (c.textContent ?? "")
                            : visibleText(c as Element),
                    )
                    .join(" ")
                    .replace(/\s+/g, " ")
                    .trim();
            }
            return visibleText(el);
        });

        // Must contain a person's name (longer than just a title keyword)
        expect(linkText.length).toBeGreaterThan(10);
        // Must include a judge title so the user knows this person's role
        expect(linkText.toLowerCase()).toMatch(/judge|chief|senior|special/i);
    });

    test("3 consecutive judge cards are Tab-reachable and each announces a unique name", async ({ page }) => {
        // A blind user can navigate through multiple judge entries by pressing Tab.
        // Two requirements: no focus trap between cards, and each card has a unique announcement
        // (if all said "link", the user could not distinguish them).
        await tabUntil(page, a => /all judges/i.test(a) && /button/.test(a));

        const cards: string[] = [];
        for (let i = 0; i < 30; i++) {
            await page.keyboard.press("Tab");
            const pathname = await page.evaluate(
                () => (document.activeElement as HTMLAnchorElement)?.pathname ?? "",
            );
            if (/^\/judges\/.+\/$/.test(pathname)) {
                cards.push(await getAnnouncement(page));
                if (cards.length >= 3) break;
            }
        }

        expect(cards.length).toBeGreaterThanOrEqual(3);
        // Every announcement must be unique — no duplicate names
        expect(new Set(cards).size).toBe(cards.length);
    });

    test("every judge card is Tab-reachable in DOM order and announces name + role — DOM-driven", async ({ page }) => {
        // ── 1. Extract expected cards from the live DOM ───────────────────────────
        // Source of truth: whatever the server renders is what we assert against.
        // If judges are added/removed the test adapts automatically.
        const expectedCards = await page.evaluate(() => {
            function visibleText(node: Element): string {
                if (node.getAttribute("aria-hidden") === "true") return "";
                return Array.from(node.childNodes)
                    .map(c =>
                        c.nodeType === Node.TEXT_NODE
                            ? (c.textContent ?? "")
                            : visibleText(c as Element),
                    )
                    .join(" ")
                    .replace(/\s+/g, " ")
                    .trim();
            }
            return Array.from(document.querySelectorAll("a.judge-card")).map(card => ({
                name:     card.querySelector(".judge-name")?.textContent?.trim() ?? "",
                role:     card.querySelector(".judge-role")?.textContent?.trim() ?? "",
                section:  card.closest(".judge-section")?.getAttribute("data-section") ?? "",
                fullText: visibleText(card as HTMLElement),
            }));
        });

        expect(expectedCards.length, "page must have at least one judge card").toBeGreaterThan(0);

        // ── 2. Anchor to the first section h2 via its id (added by WAG-1246) ──────
        // Each section h2 has id="{{ group.filter_key }}" and tabindex="0".
        // (The header is in the tab order so keyboard users can land on it as a
        // landmark.)  We focus it programmatically here purely to establish our
        // starting position in the DOM; one Tab from here advances to the first
        // judge card link in the section below.
        const firstSectionHeaderId = await page.evaluate(() =>
            document.querySelector(".judge-section .judge-section-header")?.id ?? null,
        );
        expect(firstSectionHeaderId, "first section h2 must have an id (WAG-1246 requirement)").toBeTruthy();

        await page.evaluate(
            id => (document.getElementById(id!) as HTMLElement | null)?.focus(),
            firstSectionHeaderId,
        );
        await page.keyboard.press("Tab"); // h2 is tabindex=-1 → Tab exits to first card

        // ── 3. Tab through every card in DOM order ─────────────────────────────────
        // h2 section dividers between groups have tabindex="-1" so they are skipped
        // by Tab — cards from all sections flow as one continuous tab sequence.
        for (let i = 0; i < expectedCards.length; i++) {
            const expected     = expectedCards[i];
            const announcement = await getAnnouncement(page);
            const lower        = announcement.toLowerCase();

            expect(
                lower,
                `Card ${i + 1}/${expectedCards.length} — section "${expected.section}" ` +
                `— expected name "${expected.name}" in: "${announcement}"`,
            ).toContain(expected.name.toLowerCase());

            expect(
                lower,
                `Card ${i + 1}/${expectedCards.length} (${expected.name}): ` +
                `expected role "${expected.role}" in: "${announcement}"`,
            ).toContain(expected.role.toLowerCase());

            expect(
                lower,
                `Card ${i + 1}/${expectedCards.length} (${expected.name}): ` +
                `expected "link" in: "${announcement}"`,
            ).toContain("link");

            if (i < expectedCards.length - 1) {
                await page.keyboard.press("Tab");
            }
        }
    });

    test("judge card photos are aria-hidden — VoiceOver reads name and title only, not 'image'", async ({ page }) => {
        // Without aria-hidden="true" on the photo, VoiceOver announces:
        //   "Patrick J. Urda Chief Judge [long URL or filename] image, link"
        // With aria-hidden="true":
        //   "Patrick J. Urda Chief Judge, link"   ← clean, informative
        const cards = page.locator('a[href^="/judges/"]:not([href="/judges/"])');
        for (let i = 0; i < Math.min(await cards.count(), 4); i++) {
            const img = cards.nth(i).locator("img").first();
            if (await img.count() > 0) {
                const ariaHidden = await img.getAttribute("aria-hidden");
                const alt        = await img.getAttribute("alt");
                // Acceptable: decorative (aria-hidden) OR meaningful alt text
                expect(
                    ariaHidden === "true" || (alt !== null && alt.trim() !== ""),
                ).toBe(true);
            }
        }
    });
});


// ═══════════════════════════════════════════════════════════════════════════════
// 4. BOTTOM TILES
//    Can a blind user find the related-resource links at the bottom of the page?
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Judge Information — bottom tiles", () => {
    test.beforeEach(async ({ page }) => { await page.goto(JUDGES_URL); });

    test("'Private Seminar Disclosures' is a keyboard-reachable link", async ({ page }) => {
        // If this were a <div> with an onclick handler, keyboard users (and VoiceOver)
        // would never find it — Tab skips non-interactive elements.
        const link = page.locator('a:has-text("Private Seminar Disclosures")').first();
        await expect(link).toBeVisible();
        expect(await link.getAttribute("aria-hidden")).toBeNull();    // not hidden from AT
        expect(await link.getAttribute("href")).toBeTruthy();         // has a destination
        expect(await link.getAttribute("tabindex")).not.toBe("-1");   // not removed from tab order
    });

    test("'Judicial Conduct' tile is a keyboard-reachable link", async ({ page }) => {
        const link = page.locator('a:has-text("Judicial Conduct")').first();
        await expect(link).toBeVisible();
        expect(await link.getAttribute("aria-hidden")).toBeNull();
        expect(await link.getAttribute("href")).toBeTruthy();
    });

    test("tile icons are aria-hidden so VoiceOver doesn't announce 'image' inside tile text", async ({ page }) => {
        // Without aria-hidden on the icon, VoiceOver announces:
        //   "Private Seminar Disclosures [icon description] image, link"
        // With aria-hidden="true" on the icon:
        //   "Private Seminar Disclosures, link"   ← clean announcement
        const tile    = page.locator('a:has-text("Private Seminar Disclosures")').first();
        const hidden  = tile.locator('[aria-hidden="true"]');
        expect(await hidden.count()).toBeGreaterThan(0);
    });
});


// ═══════════════════════════════════════════════════════════════════════════════
// 5. MOBILE FILTER PANEL
//    At 390 px, the 5 desktop buttons are replaced by a dialog.
//    Can a blind user open it, read options, and close it?
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Judge Information — mobile filter panel (390 px viewport)", () => {
    test.beforeEach(async ({ page }) => {
        await page.setViewportSize({ width: 390, height: 844 }); // iPhone 14 Pro
        await page.goto(JUDGES_URL);
    });

    test("Filter button announces as 'collapsed, button' — user knows it opens a panel", async ({ page }) => {
        // aria-expanded="false"  → VoiceOver: "Filter, collapsed, button"
        // aria-haspopup          → signals a popup will appear
        // aria-controls          → links button to the panel it controls
        // Without these, a blind user cannot tell that pressing this button does anything.
        const btn = page.locator("#mobile-filter-toggle");
        await expect(btn).toBeVisible();
        expect(await btn.getAttribute("aria-expanded")).toBe("false");
        expect(await btn.getAttribute("aria-haspopup")).toBeTruthy();
        expect(await btn.getAttribute("aria-controls")).toBe("mobile-filter-panel");
    });

    test("pressing Space opens the dialog — panel becomes visible with role=dialog and label", async ({ page }) => {
        // After activation:
        //   aria-expanded becomes "true"
        //   panel appears with role="dialog" + aria-label="Filter judges by type"
        // VoiceOver auto-announces: "Filter judges by type, web dialog" on appearance.
        const btn = page.locator("#mobile-filter-toggle");
        await btn.focus();
        await page.keyboard.press("Space");
        await page.waitForTimeout(400);

        expect(await btn.getAttribute("aria-expanded")).toBe("true");

        const panel = page.locator("#mobile-filter-panel");
        await expect(panel).toBeVisible();
        expect(await panel.getAttribute("role")).toBe("dialog");
        expect(await panel.getAttribute("aria-label")).toBe("Filter judges by type");
    });

    test("Tab inside the dialog reaches checkboxes announcing name + checked state", async ({ page }) => {
        // Once the dialog opens, Tab must reach the filter options.
        // Each announces: "All Judges, checked, checkbox" or "Judges, unchecked, checkbox"
        // Without aria-checked, the user cannot tell which options are currently active.
        const btn = page.locator("#mobile-filter-toggle");
        await btn.focus();
        await page.keyboard.press("Space");
        await page.waitForTimeout(400);

        await page.keyboard.press("Tab");
        const announcement = await getAnnouncement(page);
        expect(announcement.toLowerCase()).toContain("checkbox");
        expect(announcement.toLowerCase()).toMatch(/checked|unchecked/);
        expect(announcement.split(",")[0].trim().length).toBeGreaterThan(0); // has a name
    });

    test("all 5 filter options are present in the dialog, each with a non-empty label", async ({ page }) => {
        // Every filter available on desktop must also be available in the mobile dialog.
        // If an option lacks a label, VoiceOver says only "checkbox" — useless.
        const btn = page.locator("#mobile-filter-toggle");
        await btn.focus();
        await page.keyboard.press("Space");
        await page.waitForTimeout(400);

        const checkboxes = page.locator('[role="checkbox"]');
        expect(await checkboxes.count()).toBe(5);

        for (let i = 0; i < 5; i++) {
            const name =
                (await checkboxes.nth(i).getAttribute("aria-label")) ??
                (await checkboxes.nth(i).textContent())?.trim();
            expect((name ?? "").length).toBeGreaterThan(0);
        }
    });

    test("Escape closes the dialog and returns focus to the Filter button", async ({ page }) => {
        // Standard ARIA dialog keyboard pattern: Escape exits the dialog and focus
        // returns to the element that opened it.
        // Without this: after closing, keyboard focus is lost and the user must Tab
        // from the very top of the page to find their place again.
        const btn = page.locator("#mobile-filter-toggle");
        await btn.focus();
        await page.keyboard.press("Space");
        await page.waitForTimeout(400);

        await page.keyboard.press("Escape");
        await page.waitForTimeout(300);

        expect(await btn.getAttribute("aria-expanded")).toBe("false");
        const activeText = await page.evaluate(
            () => document.activeElement?.textContent?.toLowerCase().trim(),
        );
        expect(activeText).toContain("filter");
    });
});


// ═══════════════════════════════════════════════════════════════════════════════
// 6. DOM TEXT AUDIT
//    Fast, complete verification that every visible text element on the page
//    is accessible to VoiceOver.  VoiceOver reads from the accessibility tree;
//    these tests verify that all text is present in it.
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Judge Information — DOM text accessibility audit", () => {
    test.beforeEach(async ({ page }) => { await page.goto(JUDGES_URL); });

    test("no visible text in main content is hidden from screen readers via aria-hidden", async ({ page }) => {
        // Walk every text node in main content.  If a text node is visible to
        // sighted users but its ancestor has aria-hidden="true", VoiceOver will
        // never read it — an invisible barrier for blind users.
        //
        // Note: intentionally-decorative elements (icons, images) that ARE
        // aria-hidden are excluded because they have no text content.
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
                document.querySelector("main") ??
                document.getElementById("main-content") ??
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

    test("all interactive elements in <main> have a non-empty accessible name", async ({ page }) => {
        // Every button, link, and checkbox within the page's main content must have
        // an accessible name.  Without one, VoiceOver announces only the role —
        // e.g. "button" with no context — leaving blind users unable to tell elements apart.
        //
        // Scope: <main> only.  Shared site-chrome (nav, header, footer) and third-party
        // embeds (status widget iframe) are excluded — their accessible names are tested
        // at the site/component level, not per-page.
        const nameless = await page.evaluate(() => {
            const found: string[] = [];
            const root = document.querySelector("main") ?? document.body;

            function computeName(el: Element): string {
                const ariaLabel   = el.getAttribute("aria-label")?.trim();
                const labelledBy  = el.getAttribute("aria-labelledby");
                if (ariaLabel)   return ariaLabel;
                if (labelledBy)  return document.getElementById(labelledBy)?.textContent?.trim() ?? "";
                return el.textContent?.trim() ?? "";
            }

            const selectors = [
                "button",
                "a[href]",
                '[role="button"]',
                '[role="checkbox"]',
                '[role="link"]',
            ];
            for (const sel of selectors) {
                root.querySelectorAll<Element>(sel).forEach(el => {
                    const s = getComputedStyle(el);
                    if (s.display === "none" || s.visibility === "hidden") return;
                    if (el.hasAttribute("hidden")) return;
                    if (computeName(el).length === 0) {
                        const label = el.getAttribute("aria-label") ?? el.getAttribute("data-testid") ?? "";
                        found.push(
                            `<${el.tagName.toLowerCase()}${label ? ` aria-label="${label}"` : ""}> — ` +
                            (el.outerHTML.substring(0, 120)),
                        );
                    }
                });
            }
            return found;
        });

        expect(
            nameless,
            `These <main> interactive elements have no accessible name — ` +
            `VoiceOver says only the role with no context:\n${nameless.join("\n")}`,
        ).toHaveLength(0);
    });

    test("all images are either aria-hidden (decorative) or have non-empty alt text", async ({ page }) => {
        // An image without alt text is announced as the filename or URL — confusing.
        // An image with aria-hidden="true" is correctly skipped by VoiceOver.
        // An image with alt="" is also treated as decorative (correct).
        const violations = await page.evaluate(() => {
            const found: string[] = [];
            document.querySelectorAll("img").forEach(img => {
                const s = getComputedStyle(img);
                if (s.display === "none" || s.visibility === "hidden") return;
                const ariaHidden = img.getAttribute("aria-hidden") === "true";
                const alt = img.getAttribute("alt"); // null = missing; "" = decorative
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
// 6b. DESIGN-SPEC DOM REQUIREMENTS
//     These are the structural guarantees that VoiceOver navigation depends on.
//     They were identified during the UX/design review of WAG-1246 and are placed
//     here because they directly affect what screen-reader users can and cannot do.
//
//     Each test captures a specific failure mode that caused a real design review
//     comment — tests that were missing and would have caught the issue earlier.
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Judge Information — design-spec requirements (WAG-1246 review)", () => {
    test.beforeEach(async ({ page }) => { await page.goto(JUDGES_URL); });

    test("h1 has class='page-title' so its 15px margin-bottom CSS rule is applied", async ({ page }) => {
        // The CSS selector is '#judge-information-page .page-title'.
        // Without class="page-title" on the <h1>, the rule never fires and there is
        // no spacing between the page title and the intro paragraph.
        const h1 = page.locator("h1[data-testid='page-title']");
        const classes = await h1.getAttribute("class");
        expect(classes, "h1 must include 'page-title' for 15px spacing to apply").toContain("page-title");

        const marginBottom = await h1.evaluate(
            (el) => parseFloat(getComputedStyle(el).marginBottom),
        );
        expect(marginBottom, "h1 margin-bottom must be 15px").toBe(15);
    });

    test("section header margin-bottom is 24px (not 16px/1rem)", async ({ page }) => {
        // Figma spec: 24px between the section header bar and the first judge card.
        // Previously this was set to 1rem (16px), violating the global spacing document.
        const header = page.locator(".judge-section-header").first();
        const marginBottom = await header.evaluate(
            (el) => parseFloat(getComputedStyle(el).marginBottom),
        );
        expect(marginBottom, "section header margin-bottom must be 24px").toBe(24);
    });

    test("judge card grid gap is 8px (not 20px)", async ({ page }) => {
        // Figma annotation: "Theres a 8px gap in between" (between judge cards).
        // Previously gap was 20px, giving cards too much breathing room vs. mockup.
        const grid = page.locator(".judge-card-grid").first();
        const gap = await grid.evaluate(
            (el) => parseFloat(getComputedStyle(el).gap),
        );
        expect(gap, "judge card grid gap must be 8px").toBe(8);
    });

    test("judge card role text is not bold (font-weight 400)", async ({ page }) => {
        // Figma annotation: "The bottom text is NOT bolded".
        // The judge name (.judge-name) is weight 600; the role (.judge-role) must
        // stay at 400 so the two are visually distinct.
        const role = page.locator(".judge-card .judge-role").first();
        const weight = await role.evaluate(
            (el) => getComputedStyle(el).fontWeight,
        );
        expect(weight, "judge-role font-weight must be 400 (normal)").toBe("400");
    });

    test("every visible section h2 has a non-empty id attribute", async ({ page }) => {
        // The id is required for two things:
        //   1. Direct anchor linking from the admin side (#judges, #senior-judges, …)
        //   2. Programmatic focus — tabindex=-1 is useless without an id target
        // Without id, hash-URL navigation silently no-ops.
        const headers = page.locator(".judge-section-header");
        const count = await headers.count();
        expect(count).toBeGreaterThan(0);

        for (let i = 0; i < count; i++) {
            const id = await headers.nth(i).getAttribute("id");
            expect(id, `h2 at index ${i} must have a non-empty id`).toBeTruthy();
        }
    });

    test("every section h2 id matches the parent section's data-section key", async ({ page }) => {
        // The id must be the same value as the section's data-section attribute so
        // that filter buttons (data-filter) and headings share a consistent naming scheme.
        const sections = page.locator(".judge-section");
        const count = await sections.count();
        expect(count).toBeGreaterThan(0);

        for (let i = 0; i < count; i++) {
            const section = sections.nth(i);
            const filterKey = await section.getAttribute("data-section");
            const h2Id = await section.locator(".judge-section-header").getAttribute("id");
            expect(h2Id, `h2 id must equal data-section="${filterKey}"`).toBe(filterKey);
        }
    });

    test("every section h2 has tabindex=0 (keyboard users can Tab onto each section landmark)", async ({ page }) => {
        // Per UX feedback the section headers were promoted to tabindex=0 (not
        // tabindex=-1) so a keyboard-only user can Tab through them as landmarks.
        // Browsers still send #hash anchor focus to an element with any non-null
        // tabindex, so anchor navigation continues to work.
        const headers = page.locator(".judge-section-header");
        const count = await headers.count();

        for (let i = 0; i < count; i++) {
            const tabindex = await headers.nth(i).getAttribute("tabindex");
            expect(tabindex, `h2 at index ${i} must have tabindex="0"`).toBe("0");
        }
    });

    test("HR separator (.judge-tiles-rule) exists between judge sections and bottom tiles", async ({ page }) => {
        // Figma annotation: "There is also a Horizontal rule above this to separate
        // it from the cards."  Without the HR, the tiles visually run into the last
        // judge section with no clear boundary.
        const hr = page.locator(".judge-tiles-rule");
        await expect(hr, "HR separator must exist before .judge-bottom-tiles").toBeVisible();

        // Verify DOM order: HR must immediately precede the tiles grid
        const isBeforeTiles = await hr.evaluate((el) => {
            const next = el.nextElementSibling;
            return next?.classList.contains("judge-bottom-tiles") ?? false;
        });
        expect(isBeforeTiles, ".judge-tiles-rule must be the immediate sibling before .judge-bottom-tiles").toBe(true);
    });

    test("mobile filter toggle uses filter_icon.svg (not Font Awesome fa-filter)", async ({ page }) => {
        // The filter icon on this page was using fa-solid fa-filter (Font Awesome),
        // while definitions_page and litc_page use the shared filter_icon.svg from
        // the USTC design library.  Using Font Awesome here creates visual inconsistency.
        await page.setViewportSize({ width: 390, height: 844 });

        const imgIcon = page.locator("#mobile-filter-toggle img.mobile-filter-icon");
        await expect(imgIcon, "filter toggle must use img.mobile-filter-icon").toBeVisible();

        const src = await imgIcon.getAttribute("src");
        expect(src, "filter icon src must include filter_icon.svg").toContain("filter_icon.svg");

        const ariaHidden = await imgIcon.getAttribute("aria-hidden");
        expect(ariaHidden, "filter icon must be aria-hidden (decorative)").toBe("true");

        // Font Awesome icon must not be present
        const faIcon = page.locator("#mobile-filter-toggle i.fa-filter");
        await expect(faIcon, "fa-filter icon must not be used").toHaveCount(0);
    });

    test("bottom tiles are left-aligned (justify-content flex-start) at tablet viewport", async ({ page }) => {
        // Figma annotation: "In tablet view, the design is using the long QAT rather
        // than regular ones."  Long QAT = full-width single-column, horizontal layout
        // with icon on the left.  justify-content: flex-start ensures the icon + text
        // group anchors left rather than centering inside the full-width tile.
        await page.setViewportSize({ width: 834, height: 1112 });

        const tile = page.locator(".judge-tile").first();
        const justifyContent = await tile.evaluate(
            (el) => getComputedStyle(el).justifyContent,
        );
        expect(justifyContent, "judge-tile must be flex-start at tablet").toBe("flex-start");

        const flexDirection = await tile.evaluate(
            (el) => getComputedStyle(el).flexDirection,
        );
        expect(flexDirection, "judge-tile must be flex-direction row at tablet").toBe("row");
    });

    test("bottom tiles are left-aligned (justify-content flex-start) at mobile viewport", async ({ page }) => {
        // Mobile (≤640px): same long-QAT style — icon on left, text to its right,
        // group left-anchored.  Previously justify-content was unset (inherited 'center'
        // from the base tile), causing the icon+text row to float in the middle.
        await page.setViewportSize({ width: 390, height: 844 });

        const tile = page.locator(".judge-tile").first();
        const justifyContent = await tile.evaluate(
            (el) => getComputedStyle(el).justifyContent,
        );
        expect(justifyContent, "judge-tile must be flex-start at mobile").toBe("flex-start");
    });
});


// ═══════════════════════════════════════════════════════════════════════════════
// 7. VOICEOVER FULL-PAGE SWEEP
//    Drives real VoiceOver through every major section of the page using
//    VO+Right (next) to walk sequentially and jump commands for long-distance
//    navigation.  Collects every spoken phrase in the log, then asserts all
//    key text was actually announced.
//
//    Navigation path:
//      h1  → next (intro)  → next × 6 (filter group label + 5 buttons)
//          → stopInteracting
//          → findNextHeading  (§1 h2: "Judge Biographies")
//          → findNextLink     (§1 first card: Chief Judge)
//          → findNextHeading  (§2 h2: "Senior Judge Biographies")     ← skips all §1 cards
//          → findNextLink     (§2 first card: first Senior Judge)
//          → findNextHeading  (§3 h2: "Special Trial Judge Biographies")
//          → findNextLink     (§3 first card: first Special Trial Judge)
//          → findNextHeading  (§4 h2: "Senior Special Trial Judge Biography")
//          → findNextLink     (§4 first card: Lewis R. Carluzzo)
//          → findNextLink × ≤15  (remaining §4 cards + both bottom tiles)
//
//    Key design choice 1: use next() for filter buttons (not findNextControl).
//    VoiceOver's findNextControl inside a <div role="group"> wraps after 2
//    elements.  next() reliably walks all 5 buttons.
//
//    Key design choice 2: alternate findNextHeading / findNextLink per section
//    instead of one long findNextLink loop.  A single loop across all four
//    judge sections produces ~50+ links with "last link" overhead; the loop
//    exhausted 45 iterations before exiting section 2.  The section-by-section
//    approach needs only 8 navigation steps to cover all 4 h2s and all 4
//    representative judge cards.
//
//    Each navigation step takes ~10 s; the full sweep runs in ~5–6 minutes.
//    Timeout is set to 10 minutes to accommodate slower machines.
// ═══════════════════════════════════════════════════════════════════════════════

voiceOverTest.describe("Judge Information — VoiceOver full-page sweep", () => {
    // Each navigation step takes ~10 s.
    // Budget: ~60 s startup + 7 next() + 1 stopInteract +
    //         8 (heading+link pairs × 4 sections) + ≤15 tile loop ≈ 6 min.
    voiceOverTest.setTimeout(600_000);

    voiceOverTest.beforeEach(async ({ page }) => {
        await page.goto(JUDGES_URL);
    });

    voiceOverTest(
        "VoiceOver announces all page content — every section heading, every judge card, and both bottom tiles",
        async ({ page, voiceOver }) => {

            // ── 1. Land on h1 ─────────────────────────────────────────────────────
            // enterWebContent clears the phrase log then positions VO on the h1.
            await enterWebContent(page, voiceOver);

            // ── 2. Intro paragraph ────────────────────────────────────────────────
            await voiceOver.next();

            // ── 3. Filter group label + all 5 filter buttons ──────────────────────
            // next() on role="group" enters it (interact mode) and announces the
            // label.  Subsequent next() calls walk the children one by one.
            await voiceOver.next(); // "Filter judges by type, group"
            await voiceOver.next(); // "All Judges, pressed, toggle button"
            await voiceOver.next(); // "Judges, toggle button"
            await voiceOver.next(); // "Senior Judges, toggle button"
            await voiceOver.next(); // "Special Trial Judges, toggle button"
            await voiceOver.next(); // "Senior Special Trial Judges, toggle button"

            // ── 4. Exit the filter group ──────────────────────────────────────────
            // Without this, jump commands search inside the group and return
            // "heading not found" / "link not found".
            await voiceOver.perform(voiceOverKeyCodeCommands.stopInteractingWithItem);

            // ── 5. Section 1 — "Judge Biographies" + first judge card ───────────────
            await voiceOver.perform(voiceOverKeyCodeCommands.findNextHeading); // "Judge Biographies, heading level 2"
            await voiceOver.perform(voiceOverKeyCodeCommands.findNextLink);    // "Patrick J. Urda Chief Judge, link"

            // ── 6. Section 2 — jump past all §1 cards to next h2, then first card ──
            // findNextHeading skips every judge link (they are not headings) and
            // lands directly on the next section heading.
            await voiceOver.perform(voiceOverKeyCodeCommands.findNextHeading); // "Senior Judge Biographies, heading level 2"
            await voiceOver.perform(voiceOverKeyCodeCommands.findNextLink);    // first Senior Judge card

            // ── 7. Section 3 — same pattern ──────────────────────────────────────
            await voiceOver.perform(voiceOverKeyCodeCommands.findNextHeading); // "Special Trial Judge Biographies, heading level 2"
            await voiceOver.perform(voiceOverKeyCodeCommands.findNextLink);    // first Special Trial Judge card

            // ── 8. Section 4 — same pattern → Lewis R. Carluzzo ─────────────────
            await voiceOver.perform(voiceOverKeyCodeCommands.findNextHeading); // "Senior Special Trial Judge Biography, heading level 2"
            await voiceOver.perform(voiceOverKeyCodeCommands.findNextLink);    // first card in §4 (likely Lewis R. Carluzzo)

            // ── 9. Bottom tiles — walk forward from end of §4 ────────────────────
            // Section 4 typically has only 1–3 judges, so the tiles are reachable
            // within 15 findNextLink calls.  The loop stops as soon as both are found.
            let tilesFound = 0;
            for (let i = 0; i < 15 && tilesFound < 2; i++) {
                await voiceOver.perform(voiceOverKeyCodeCommands.findNextLink);
                const phrase = await voiceOver.lastSpokenPhrase();
                if (/private seminar disclosures/i.test(phrase)) tilesFound++;
                if (/judicial conduct/i.test(phrase))            tilesFound++;
            }

            // ── 10. Collect everything VoiceOver spoke ────────────────────────────
            const log = (await voiceOver.spokenPhraseLog()).join("\n").toLowerCase();

            // ── 11. Assert every section of the page was announced ───────────────
            const assertions: [string, string | RegExp][] = [
                // Page title and structure
                ["page title h1",                        "judge information"],
                ["heading level 1 announced",            "heading level 1"],
                ["intro paragraph",                      /biography|clicking on the cards/],

                // Filter bar
                ["filter group label",                   "filter judges by type"],
                ["'All Judges' button",                  "all judges"],
                ["'Judges' button",                      /\bjudges\b/],
                ["'Senior Judges' button",               "senior judges"],
                ["'Special Trial Judges' button",        /special trial judges/],
                ["'Senior Special Trial Judges' button", "senior special trial judges"],

                // All 4 section headings
                ["'Judge Biographies' h2",               "judge biographies"],
                ["'Senior Judge Biographies' h2",        "senior judge biographies"],
                ["'Special Trial Judge Biographies' h2", "special trial judge biographies"],
                ["'Senior Special Trial' h2",            "senior special trial judge biograph"],

                // One judge card per section (representative of each section traversed)
                ["a judge in section 1",                 /chief judge|judge link/],
                ["a judge in section 2",                 "senior judge"],
                ["a judge in section 3",                 "special trial judge"],
                ["Lewis R. Carluzzo (section 4)",        "carluzzo"],

                // Bottom tiles
                ["Private Seminar Disclosures tile",     "private seminar disclosures"],
                ["Judicial Conduct tile",                "judicial conduct"],
            ];

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
        "VoiceOver speaks every judge's name and role — DOM-driven full card traversal",
        async ({ page, voiceOver }) => {
            // ── 1. Get the expected card list directly from the live DOM ──────────────
            // Whatever the server renders is what VoiceOver must speak.
            // The test adapts automatically when judges are added or removed in the CMS —
            // no hardcoded names, no stale assertions.
            const expectedCards = await page.evaluate(() =>
                Array.from(document.querySelectorAll("a.judge-card")).map(card => ({
                    name:    card.querySelector(".judge-name")?.textContent?.trim() ?? "",
                    role:    card.querySelector(".judge-role")?.textContent?.trim() ?? "",
                    section: card.closest(".judge-section")?.getAttribute("data-section") ?? "",
                })),
            );
            expect(expectedCards.length, "page must have at least one judge card").toBeGreaterThan(0);

            // ── 2. Enter the page and navigate to the first judge section h2 ──────────
            // VoiceOver's findNextLink searches forward from the current cursor
            // position — if we start at h1 the search wraps through page header/nav
            // links before reaching the judge cards.  We replicate the same setup as
            // the full-page sweep: walk the filter group, exit it, then jump to the
            // first section h2.  From that anchor, findNextLink finds judge cards only.
            await enterWebContent(page, voiceOver);

            await voiceOver.next();                  // intro paragraph
            await voiceOver.next();                  // "Filter judges by type, group"
            await voiceOver.next();                  // "All Judges, pressed, button"
            await voiceOver.next();                  // "Judges, button"
            await voiceOver.next();                  // "Senior Judges, button"
            await voiceOver.next();                  // "Special Trial Judges, button"
            await voiceOver.next();                  // "Senior Special Trial Judges, button"
            await voiceOver.perform(voiceOverKeyCodeCommands.stopInteractingWithItem);
            await voiceOver.perform(voiceOverKeyCodeCommands.findNextHeading); // → §1 h2

            // ── 3. Walk every link in document order using findNextLink ───────────────
            // findNextLink targets <a href> elements only — the <button> filter buttons
            // are skipped entirely.  Document order on this page is:
            //   judge cards (all 4 sections, left-to-right, top-to-bottom)
            //   → "Private Seminar Disclosures" tile
            //   → "Judicial Conduct and Disability Complaint Procedures" tile
            //
            // After each jump, lastSpokenPhrase() returns exactly what VoiceOver said
            // aloud — the accessible name of the link plus role/state suffixes.
            // We collect every phrase and stop as soon as both bottom tiles have been
            // announced (they come after the last judge card so we know we're done).
            const spoken: string[] = [];
            let tilesFound = 0;
            const maxLinks = expectedCards.length + 10; // cards + tiles + small buffer

            for (let i = 0; i < maxLinks && tilesFound < 2; i++) {
                await voiceOver.perform(voiceOverKeyCodeCommands.findNextLink);
                const phrase = await voiceOver.lastSpokenPhrase();
                spoken.push(phrase);
                if (/private seminar disclosures/i.test(phrase)) tilesFound++;
                if (/judicial conduct/i.test(phrase))            tilesFound++;
            }

            expect(tilesFound, "loop must reach both bottom tiles to confirm all cards were traversed").toBe(2);

            // ── 4. Assert every judge's name and role was actually spoken ─────────────
            // Joining into one string lets us check each card with a single
            // .toContain() call and get a clear failure message naming the card.
            const fullLog = spoken.join("\n").toLowerCase();

            for (const card of expectedCards) {
                expect(
                    fullLog,
                    `VoiceOver never spoke name "${card.name}" (section: ${card.section})`,
                ).toContain(card.name.toLowerCase());

                expect(
                    fullLog,
                    `VoiceOver never spoke role "${card.role}" for "${card.name}" (section: ${card.section})`,
                ).toContain(card.role.toLowerCase());
            }

            // ── 5. Bottom tiles also confirmed ────────────────────────────────────────
            expect(fullLog, "VoiceOver never spoke 'Private Seminar Disclosures'").toMatch(/private seminar disclosures/);
            expect(fullLog, "VoiceOver never spoke 'Judicial Conduct'").toMatch(/judicial conduct/);
        },
    );
});
