/**
 * Private Seminar Disclosures page — Cypress E2E tests
 * WAG-1247
 *
 * Route: /judges/private-seminar-disclosures/
 * Template: home/templates/home/private_seminar_disclosures.html
 *
 * NOTE: The year-filter and disclosure-card tests branch on whether
 * seed data exists in the test database. If running against a clean DB,
 * only the empty-state path is exercised; with seed data both paths run.
 */

import { checkA11y, checkHeaderOrder, checkHeaderStyles, terminalLog } from "../../support/commands";

const PAGE_URL = "/judges/private-seminar-disclosures/";

// ─── Page structure ──────────────────────────────────────────────────────────

describe("Private Seminar Disclosures — page structure", () => {
    beforeEach(() => {
        cy.visit(PAGE_URL);
    });

    it("returns HTTP 200", () => {
        cy.request(PAGE_URL).its("status").should("eq", 200);
    });

    it("has a visible h1 that contains 'Private Seminar Disclosures'", () => {
        cy.get('[data-testid="page-title"]')
            .should("be.visible")
            .and("contain", "Private Seminar Disclosures");
    });

    it("h1 contains a link back to the Judge Information page", () => {
        cy.get('[data-testid="page-title"] a')
            .should("be.visible")
            .and("contain", "Judge Information")
            .and("have.attr", "href");
    });

    it("back-link navigates to /judges/", () => {
        cy.get('[data-testid="page-title"] a').click();
        cy.url().should("include", "/judges/");
    });

    it("page container exists", () => {
        cy.get("#private-seminar-page").should("exist");
    });

    it("displays introductory text when set", () => {
        // Intro text is optional — just confirm the container exists
        cy.get(".seminar-intro").should("exist");
    });

    it("passes basic accessibility check (axe serious+critical)", () => {
        checkA11y();
    });

    it("heading hierarchy has no skips (h1 → h2, etc.)", () => {
        checkHeaderOrder();
    });
});

// ─── Disclosure cards (when seed data is present) ────────────────────────────

describe("Private Seminar Disclosures — disclosure cards", () => {
    beforeEach(() => {
        cy.visit(PAGE_URL);
    });

    it("shows the disclosure grid or the empty-state message — never both", () => {
        cy.get("body").then(($body) => {
            const hasGrid = $body.find(".disclosure-grid").length > 0;
            const hasEmpty = $body.find(".disclosure-empty").length > 0;
            // Exactly one branch must be true
            expect(hasGrid || hasEmpty).to.be.true;
            expect(hasGrid && hasEmpty).to.be.false;
        });
    });

    it("each disclosure card has a judge name element", () => {
        cy.get("body").then(($body) => {
            if ($body.find(".disclosure-card").length === 0) return; // empty state OK
            cy.get(".disclosure-card").each(($card) => {
                cy.wrap($card).find(".judge-name").should("exist").and("not.be.empty");
            });
        });
    });

    it("each disclosure card has Program Provider, Program, Date, and Location fields", () => {
        cy.get("body").then(($body) => {
            if ($body.find(".disclosure-card").length === 0) return;
            cy.get(".disclosure-card").each(($card) => {
                const dtTexts = $card.find("dt").toArray().map((el) => el.textContent?.trim());
                expect(dtTexts).to.include("Program Provider(s):");
                expect(dtTexts).to.include("Program:");
                expect(dtTexts).to.include("Date:");
                expect(dtTexts).to.include("Location:");
            });
        });
    });

    it("date field is formatted as MM/DD/YYYY", () => {
        cy.get("body").then(($body) => {
            if ($body.find(".disclosure-card").length === 0) return;
            cy.get(".disclosure-card").first().within(() => {
                // Find the dd after the Date dt
                cy.contains("dt", "Date:").next("dd").invoke("text").should("match", /^\d{2}\/\d{2}\/\d{4}$/);
            });
        });
    });

    it("disclosure grid uses 2-column layout at desktop", () => {
        cy.viewport(1440, 900);
        cy.visit(PAGE_URL);
        cy.get("body").then(($body) => {
            if ($body.find(".disclosure-grid").length === 0) return;
            cy.get(".disclosure-grid").then(($grid) => {
                const cols = window.getComputedStyle($grid[0]).gridTemplateColumns.split(" ");
                expect(cols).to.have.length(2);
            });
        });
    });

    it("disclosure grid collapses to 1 column on mobile", () => {
        cy.viewport(390, 844);
        cy.visit(PAGE_URL);
        cy.get("body").then(($body) => {
            if ($body.find(".disclosure-grid").length === 0) return;
            cy.get(".disclosure-grid").then(($grid) => {
                const cols = window.getComputedStyle($grid[0]).gridTemplateColumns.split(" ");
                expect(cols).to.have.length(1);
            });
        });
    });
});

// ─── Empty state ─────────────────────────────────────────────────────────────

describe("Private Seminar Disclosures — empty state", () => {
    it("empty-state message is visible when no disclosures exist", () => {
        cy.visit(PAGE_URL);
        cy.get("body").then(($body) => {
            if ($body.find(".disclosure-card").length > 0) return; // skip if data present
            cy.get('[data-testid="empty-message"]')
                .should("be.visible")
                .and("not.be.empty");
        });
    });

    it("empty-state message does not appear when disclosures are present", () => {
        cy.visit(PAGE_URL);
        cy.get("body").then(($body) => {
            if ($body.find(".disclosure-card").length === 0) return; // skip if no data
            cy.get('[data-testid="empty-message"]').should("not.exist");
        });
    });
});

// ─── Year filter ─────────────────────────────────────────────────────────────

describe("Private Seminar Disclosures — year filter", () => {
    beforeEach(() => {
        cy.visit(PAGE_URL);
    });

    it("year-filter select is only rendered when years exist", () => {
        cy.get("body").then(($body) => {
            const hasCards = $body.find(".disclosure-card").length > 0;
            const hasSelect = $body.find("#year-select").length > 0;
            // If there are disclosures there should be a select; if not there shouldn't be
            expect(hasCards).to.equal(hasSelect);
        });
    });

    it("filter select has an 'All Years' default option", () => {
        cy.get("body").then(($body) => {
            if ($body.find("#year-select").length === 0) return;
            cy.get("#year-select option[value='']").should("contain", "All Years");
        });
    });

    it("filter select options are year values (4-digit numbers)", () => {
        cy.get("body").then(($body) => {
            if ($body.find("#year-select").length === 0) return;
            cy.get("#year-select option").each(($opt) => {
                const val = $opt.val() as string;
                if (val !== "") {
                    expect(val).to.match(/^\d{4}$/);
                }
            });
        });
    });

    it("select has an accessible label", () => {
        cy.get("body").then(($body) => {
            if ($body.find("#year-select").length === 0) return;
            // Either a visible label or aria-label satisfies 508
            cy.get("#year-select").then(($sel) => {
                const hasAriaLabel = $sel.attr("aria-label");
                const labelFor = Cypress.$(`label[for="year-select"]`).length > 0;
                expect(Boolean(hasAriaLabel) || labelFor).to.be.true;
            });
        });
    });

    it("selecting a year submits the form and filters results", () => {
        cy.get("body").then(($body) => {
            if ($body.find("#year-select").length === 0) return;
            // Pick the first non-empty option
            cy.get("#year-select option").not("[value='']").first().then(($opt) => {
                const year = $opt.val() as string;
                cy.get("#year-select").select(year);
                // The onchange handler auto-submits; wait for the new URL
                cy.url().should("include", `year=${year}`);
                cy.get("#year-select").should("have.value", year);
            });
        });
    });

    it("filtered results only show disclosures for the selected year", () => {
        cy.get("body").then(($body) => {
            if ($body.find("#year-select").length === 0) return;
            cy.get("#year-select option").not("[value='']").first().then(($opt) => {
                const year = $opt.val() as string;
                cy.get("#year-select").select(year);
                // Wait for the page to reload with the year filter applied
                cy.url().should("include", `year=${year}`);
                cy.get(".disclosure-card").each(($card) => {
                    cy.wrap($card).contains("dt", "Date:").next("dd").invoke("text").then((dateText) => {
                        // MM/DD/YYYY — last 4 chars are the year
                        expect(dateText.trim().slice(-4)).to.equal(year);
                    });
                });
            });
        });
    });

    it("selecting 'All Years' shows all disclosures and removes year param from URL", () => {
        cy.get("body").then(($body) => {
            if ($body.find("#year-select").length === 0) return;
            // First apply a year filter
            cy.get("#year-select option").not("[value='']").first().then(($opt) => {
                cy.get("#year-select").select($opt.val() as string);
                cy.url().should("include", "year=");
                // Then reset to All Years
                cy.get("#year-select").select("");
                cy.url().should("not.include", "year=");
                cy.get("#year-select").should("have.value", "");
            });
        });
    });

    it("year filter form uses GET method", () => {
        cy.get("body").then(($body) => {
            if ($body.find("#year-filter-form").length === 0) return;
            cy.get("#year-filter-form").should("have.attr", "method", "get");
        });
    });
});

// ─── 508 / WCAG accessibility ────────────────────────────────────────────────

describe("Private Seminar Disclosures — 508 accessibility", () => {
    beforeEach(() => {
        cy.viewport(1440, 900);
        cy.visit(PAGE_URL);
    });

    it("passes full axe audit scoped to the page container", () => {
        cy.injectAxe();
        cy.checkA11y(
            "#private-seminar-page",
            {
                includedImpacts: ["minor", "moderate", "serious", "critical"],
                rules: {
                    // color-contrast requires computed styles that axe can't always
                    // resolve in headless — verified visually against Figma spec
                    "color-contrast": { enabled: false },
                },
                retries: 3,
            },
            terminalLog,
        );
    });

    it("page title has tabindex=0 for keyboard / VoiceOver access", () => {
        cy.get('[data-testid="page-title"]').should("have.attr", "tabindex", "0");
    });

    it("year-filter select is keyboard-operable", () => {
        cy.get("body").then(($body) => {
            if ($body.find("#year-select").length === 0) return;
            cy.get("#year-select").focus().should("be.focused");
        });
    });

    it("all Font Awesome icons in the page have aria-hidden=true", () => {
        // This page has no FA icons; the test is a no-op but guards future additions.
        cy.get("body").then(($body) => {
            const icons = $body.find("#private-seminar-page i.fa-solid, #private-seminar-page i.fa-regular");
            if (icons.length === 0) return; // no icons present — nothing to assert
            cy.get("#private-seminar-page i.fa-solid, #private-seminar-page i.fa-regular").each(($icon) => {
                cy.wrap($icon).should("have.attr", "aria-hidden", "true");
            });
        });
    });

    it("disclosure cards use a dl/dt/dd structure inside the body zone for field labels and values", () => {
        cy.get("body").then(($body) => {
            if ($body.find(".disclosure-card").length === 0) return;
            cy.get(".disclosure-card").first().within(() => {
                cy.get(".disclosure-body dl").should("exist");
                cy.get(".disclosure-body dt").should("have.length.at.least", 4); // provider, program, date, location
                cy.get(".disclosure-body dd").should("have.length.at.least", 4);
            });
        });
    });

    it("passes accessibility check at tablet viewport (834px)", () => {
        cy.viewport(834, 1112);
        cy.visit(PAGE_URL);
        cy.injectAxe();
        cy.checkA11y(
            "#private-seminar-page",
            { includedImpacts: ["serious", "critical"], retries: 3 },
            terminalLog,
        );
    });

    it("passes accessibility check at mobile viewport (390px)", () => {
        cy.viewport(390, 844);
        cy.visit(PAGE_URL);
        cy.injectAxe();
        cy.checkA11y(
            "#private-seminar-page",
            { includedImpacts: ["serious", "critical"], retries: 3 },
            terminalLog,
        );
    });

    it("Tab order flows from page title → back-link → year filter (if present)", () => {
        cy.get('[data-testid="page-title"]').focus();
        // Tab 1: h1 → back-link <a> inside the h1
        cy.realPress("Tab");
        cy.focused().should("have.prop", "tagName", "A");
        cy.get("body").then(($body) => {
            if ($body.find("#year-select").length > 0) {
                // Tab 2: back-link → year-filter select
                cy.realPress("Tab");
                cy.focused().should("have.attr", "id", "year-select");
            }
        });
    });
});

// ─── Figma design spec — disclosure card styling ─────────────────────────────
// All values confirmed from Figma file MpYvDySIPULl7f1RQBvb3y node 13913:9549.

describe("Private Seminar Disclosures — Figma design spec", () => {
    beforeEach(() => {
        cy.viewport(1440, 900);
        cy.visit(PAGE_URL);
    });

    it("disclosure card has a visible border and white background", () => {
        cy.get("body").then(($body) => {
            if ($body.find(".disclosure-card").length === 0) return;
            cy.get(".disclosure-card").first()
                .should("have.css", "background-color", "rgb(255, 255, 255)")
                .and("have.css", "border-top-width", "1px");
        });
    });

    it("judge name is semibold (font-weight 600)", () => {
        cy.get("body").then(($body) => {
            if ($body.find(".disclosure-card").length === 0) return;
            cy.get(".disclosure-card .judge-name").first()
                .should("have.css", "font-weight", "600");
        });
    });

    it("judge name is a full-width block header (display: block)", () => {
        cy.get("body").then(($body) => {
            if ($body.find(".disclosure-card").length === 0) return;
            cy.get(".disclosure-card .judge-name").first()
                .should("have.css", "display", "block");
        });
    });

    it("judge name header band background is Figma-confirmed light blue rgb(241,249,252)", () => {
        // Confirmed from Figma file MpYvDySIPULl7f1RQBvb3y node 13913:9549
        // Frame 14 fill: rgb(241,249,252) — #f1f9fc
        cy.get("body").then(($body) => {
            if ($body.find(".disclosure-card").length === 0) return;
            cy.get(".disclosure-card .judge-name").first()
                .should("have.css", "background-color", "rgb(241, 249, 252)");
        });
    });

    it("dt labels are semibold (font-weight 600 per Figma)", () => {
        cy.get("body").then(($body) => {
            if ($body.find(".disclosure-card").length === 0) return;
            cy.get(".disclosure-card dt").first()
                .should("have.css", "font-weight", "600");
        });
    });

    it("year-filter select aligns to the right of the controls row", () => {
        cy.get("body").then(($body) => {
            if ($body.find(".disclosure-controls").length === 0) return;
            cy.get(".disclosure-controls")
                .should("have.css", "justify-content", "flex-end");
        });
    });
});
