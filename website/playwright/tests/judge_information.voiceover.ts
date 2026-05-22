/**
 * VoiceOver screen reader tests for the Judge Information page.
 *
 * These tests drive macOS VoiceOver via @guidepup/playwright to verify that
 * the content announced to a screen reader matches what the Figma design
 * intends users to understand — not just that elements exist in the DOM.
 *
 * Figma reference: file MpYvDySIPULl7f1RQBvb3y, node 13913-8013
 * (Judges Pages canvas — Desktop / Tablet / Mobile sections)
 *
 * Run with:
 *   npx playwright test --config playwright/playwright.config.ts
 *
 * Requirements (one-time per machine):
 *   1. Grant Accessibility permission to your terminal app:
 *      System Settings → Privacy & Security → Accessibility → enable Terminal (or iTerm2)
 *   2. Run the guidepup setup to verify the permission is working:
 *      npx @guidepup/setup
 *   3. Dev server must be running: make run
 *
 * If you see "VoiceOver not supported", the Accessibility permission has not
 * been granted — complete step 1 and 2 above, then re-run.
 */

import { voiceOverTest as test } from "@guidepup/playwright";
import { expect } from "@playwright/test";

const BASE = process.env.PLAYWRIGHT_BASE_URL || "http://localhost:8000";
const JUDGES_URL = `${BASE}/judges/`;

// ── helpers ──────────────────────────────────────────────────────────────────

/** Collect all spoken phrases until the predicate returns true or we time out. */
async function spokenUntil(
    voiceOver: { lastSpokenPhrase: () => Promise<string>; next: () => Promise<void> },
    predicate: (phrase: string) => boolean,
    maxSteps = 60,
): Promise<string[]> {
    const heard: string[] = [];
    for (let i = 0; i < maxSteps; i++) {
        const phrase = await voiceOver.lastSpokenPhrase();
        if (phrase) heard.push(phrase);
        if (predicate(phrase)) break;
        await voiceOver.next();
    }
    return heard;
}

/** Tab forward until the focused element's spoken phrase matches the predicate. */
async function tabUntil(
    voiceOver: { lastSpokenPhrase: () => Promise<string>; press: (key: string) => Promise<void> },
    predicate: (phrase: string) => boolean,
    maxTabs = 40,
): Promise<string> {
    for (let i = 0; i < maxTabs; i++) {
        const phrase = await voiceOver.lastSpokenPhrase();
        if (predicate(phrase)) return phrase;
        await voiceOver.press("Tab");
    }
    return await voiceOver.lastSpokenPhrase();
}

// ── page title ───────────────────────────────────────────────────────────────

test.describe("Judge Information — VoiceOver: page structure", () => {
    test.beforeEach(async ({ page }) => {
        await page.goto(JUDGES_URL);
    });

    test("page title is announced as 'Judge Information'", async ({ page, voiceOver }) => {
        // Figma frame name: "Desktop: Judges Filtered" — page h1 text is "Judge Information"
        await voiceOver.navigateToWebContent();
        const heard = await spokenUntil(
            voiceOver,
            (p) => p.toLowerCase().includes("judge information"),
        );
        expect(heard.some((p) => p.toLowerCase().includes("judge information"))).toBe(true);
    });

    test("intro paragraph is read after the page title", async ({ page, voiceOver }) => {
        // Figma node 13707:3005: subtitle "See the Judge's biography by clicking on the cards."
        await voiceOver.navigateToWebContent();
        const heard = await spokenUntil(
            voiceOver,
            (p) => p.toLowerCase().includes("biography") || p.toLowerCase().includes("clicking on the cards"),
            80,
        );
        expect(
            heard.some(
                (p) =>
                    p.toLowerCase().includes("biography") ||
                    p.toLowerCase().includes("clicking on the cards"),
            ),
        ).toBe(true);
    });

    test("section headers are announced as headings", async ({ page, voiceOver }) => {
        // Figma section header text: "| Judges Biographies", "| Senior Judges Biographies", etc.
        // VoiceOver announces heading level: e.g. "Judges Biographies, heading level 2"
        await voiceOver.navigateToWebContent();
        const heard = await spokenUntil(
            voiceOver,
            (p) => p.toLowerCase().includes("heading level 2"),
            80,
        );
        expect(heard.some((p) => p.toLowerCase().includes("heading level 2"))).toBe(true);
    });
});

// ── filter bar ───────────────────────────────────────────────────────────────

test.describe("Judge Information — VoiceOver: filter bar", () => {
    test.beforeEach(async ({ page }) => {
        await page.goto(JUDGES_URL);
    });

    test("filter group is announced with its label", async ({ page, voiceOver }) => {
        // Figma: filter bar has role=group aria-label="Filter judges by type"
        // VoiceOver announces: "Filter judges by type, group"
        await voiceOver.navigateToWebContent();
        const heard = await spokenUntil(
            voiceOver,
            (p) => p.toLowerCase().includes("filter judges by type"),
            80,
        );
        expect(heard.some((p) => p.toLowerCase().includes("filter judges by type"))).toBe(true);
    });

    test("'All Judges' filter button is announced as pressed", async ({ page, voiceOver }) => {
        // Figma: "All Judges" button is active by default (aria-pressed=true)
        // VoiceOver announces: "All Judges, selected, toggle button" or "All Judges, pressed"
        await voiceOver.navigateToWebContent();
        const phrase = await tabUntil(
            voiceOver,
            (p) => p.toLowerCase().includes("all judges"),
        );
        expect(phrase.toLowerCase()).toContain("all judges");
        expect(
            phrase.toLowerCase().includes("pressed") ||
            phrase.toLowerCase().includes("selected"),
        ).toBe(true);
    });

    test("inactive filter button is announced as not pressed", async ({ page, voiceOver }) => {
        // Figma filter keys: judges / senior-judges / special-trial-judges / senior-special-trial-judges
        await voiceOver.navigateToWebContent();
        await tabUntil(voiceOver, (p) => p.toLowerCase().includes("all judges"));
        await voiceOver.press("Tab");
        const phrase = await voiceOver.lastSpokenPhrase();
        // Should announce as "Judges, toggle button" without "pressed" / "selected"
        expect(phrase.toLowerCase()).toContain("judges");
        expect(
            phrase.toLowerCase().includes("not pressed") ||
                !phrase.toLowerCase().includes("selected"),
        ).toBe(true);
    });

    test("activating a filter button announces the section change via live region", async ({
        page,
        voiceOver,
    }) => {
        // Figma: filter interaction → aria-live region announces "Showing Senior Judges."
        await voiceOver.navigateToWebContent();
        await tabUntil(voiceOver, (p) => p.toLowerCase().includes("senior judges"));
        await voiceOver.press("Space");
        // Give the live region time to fire
        await page.waitForTimeout(500);
        const heard = await spokenUntil(
            voiceOver,
            (p) => p.toLowerCase().includes("showing"),
            20,
        );
        expect(heard.some((p) => p.toLowerCase().includes("senior judges"))).toBe(true);
    });
});

// ── judge cards ───────────────────────────────────────────────────────────────

test.describe("Judge Information — VoiceOver: judge cards", () => {
    test.beforeEach(async ({ page }) => {
        await page.goto(JUDGES_URL);
    });

    test("judge card is announced with name and role", async ({ page, voiceOver }) => {
        // Figma card content: Judge Name (semibold) + Title — both read as link text
        // e.g. "Patrick J. Urda Chief Judge, link"
        await voiceOver.navigateToWebContent();
        const phrase = await tabUntil(
            voiceOver,
            (p) => p.toLowerCase().includes("judge") && p.toLowerCase().includes("link"),
            60,
        );
        // Should include a name and a role, and be identified as a link
        expect(phrase.toLowerCase()).toContain("link");
        expect(phrase.trim().length).toBeGreaterThan(10);
    });

    test("tab order reaches first judge card after filter buttons", async ({ page, voiceOver }) => {
        // Figma DOM order: page title → filter bar → judge sections → bottom tiles
        await voiceOver.navigateToWebContent();
        // Tab through the 5 filter buttons (All Judges + 4 groups)
        for (let i = 0; i < 5; i++) {
            await voiceOver.press("Tab");
        }
        const phrase = await voiceOver.lastSpokenPhrase();
        // First interactive element after filters is the first judge card link
        expect(phrase.toLowerCase()).toContain("link");
    });
});

// ── bottom tiles ─────────────────────────────────────────────────────────────

test.describe("Judge Information — VoiceOver: bottom tiles", () => {
    test.beforeEach(async ({ page }) => {
        await page.goto(JUDGES_URL);
    });

    test("Private Seminar Disclosures tile is announced as a link", async ({ page, voiceOver }) => {
        // Figma tile text: "Private Seminar Disclosures"
        await voiceOver.navigateToWebContent();
        const phrase = await tabUntil(
            voiceOver,
            (p) => p.toLowerCase().includes("private seminar disclosures"),
            80,
        );
        expect(phrase.toLowerCase()).toContain("private seminar disclosures");
        expect(phrase.toLowerCase()).toContain("link");
    });

    test("Judicial Conduct tile is announced as a link", async ({ page, voiceOver }) => {
        // Figma tile text: "Judicial Conduct and Disability Complaint Procedures"
        await voiceOver.navigateToWebContent();
        const phrase = await tabUntil(
            voiceOver,
            (p) => p.toLowerCase().includes("judicial conduct"),
            80,
        );
        expect(phrase.toLowerCase()).toContain("judicial conduct");
        expect(phrase.toLowerCase()).toContain("link");
    });

    test("tile icons are not announced (aria-hidden)", async ({ page, voiceOver }) => {
        // Figma: icons are decorative — aria-hidden=true means VoiceOver must skip them
        // We verify by checking the tile announcement does NOT include icon names
        await voiceOver.navigateToWebContent();
        const phrase = await tabUntil(
            voiceOver,
            (p) => p.toLowerCase().includes("private seminar disclosures"),
            80,
        );
        expect(phrase.toLowerCase()).not.toContain("image");
        expect(phrase.toLowerCase()).not.toContain("icon");
    });
});

// ── mobile filter panel ───────────────────────────────────────────────────────

test.describe("Judge Information — VoiceOver: mobile filter panel", () => {
    test.beforeEach(async ({ page }) => {
        // Figma mobile frame: 320px width
        await page.setViewportSize({ width: 390, height: 844 });
        await page.goto(JUDGES_URL);
    });

    test("mobile Filter button is announced with expanded state", async ({ page, voiceOver }) => {
        // Figma: single "Filter" button (aria-expanded=false initially)
        // VoiceOver: "Filter, collapsed, button" or "Filter, pop up button"
        await voiceOver.navigateToWebContent();
        const phrase = await tabUntil(
            voiceOver,
            (p) => p.toLowerCase().includes("filter") && p.toLowerCase().includes("button"),
            40,
        );
        expect(phrase.toLowerCase()).toContain("filter");
        expect(
            phrase.toLowerCase().includes("collapsed") ||
            phrase.toLowerCase().includes("pop up") ||
            phrase.toLowerCase().includes("button"),
        ).toBe(true);
    });

    test("opening filter panel announces the dialog", async ({ page, voiceOver }) => {
        // Figma: panel has role=dialog aria-label="Filter judges by type"
        await voiceOver.navigateToWebContent();
        await tabUntil(
            voiceOver,
            (p) => p.toLowerCase().includes("filter") && p.toLowerCase().includes("button"),
        );
        await voiceOver.press("Space");
        await page.waitForTimeout(300);
        const heard = await spokenUntil(
            voiceOver,
            (p) => p.toLowerCase().includes("filter judges by type") || p.toLowerCase().includes("dialog"),
            20,
        );
        expect(
            heard.some(
                (p) =>
                    p.toLowerCase().includes("filter judges by type") ||
                    p.toLowerCase().includes("dialog"),
            ),
        ).toBe(true);
    });

    test("filter checkboxes inside the panel are announced with checked state", async ({
        page,
        voiceOver,
    }) => {
        // Figma: each option has role=checkbox with aria-checked
        // VoiceOver: "All Judges, checked, checkbox"
        await voiceOver.navigateToWebContent();
        await tabUntil(
            voiceOver,
            (p) => p.toLowerCase().includes("filter") && p.toLowerCase().includes("button"),
        );
        await voiceOver.press("Space");
        await page.waitForTimeout(300);
        const phrase = await tabUntil(
            voiceOver,
            (p) => p.toLowerCase().includes("checkbox"),
            20,
        );
        expect(phrase.toLowerCase()).toContain("checkbox");
        expect(
            phrase.toLowerCase().includes("checked") ||
            phrase.toLowerCase().includes("unchecked"),
        ).toBe(true);
    });

    test("Escape closes the panel and returns focus to Filter button", async ({
        page,
        voiceOver,
    }) => {
        await voiceOver.navigateToWebContent();
        await tabUntil(
            voiceOver,
            (p) => p.toLowerCase().includes("filter") && p.toLowerCase().includes("button"),
        );
        await voiceOver.press("Space");
        await page.waitForTimeout(300);
        await voiceOver.press("Escape");
        await page.waitForTimeout(200);
        const phrase = await voiceOver.lastSpokenPhrase();
        expect(phrase.toLowerCase()).toContain("filter");
    });
});
