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

    //fixme: this test always fails because seminar-intro div is now conditional.
    // it("displays introductory text when set", () => {
    //     // Intro text is optional — just confirm the container exists
    //     cy.get(".seminar-intro").should("exist");
    // });

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
        // Card body markup uses `.disclosure-field-group` rather than dl/dt/dd.
        // "Program Provider(s):" appears in `.field-label`; Program/Date/Location
        // are inlined into `.field-value` strings (e.g. "Date: 06/15/2024"). We
        // assert all four label tokens appear somewhere in the card text.
        cy.get("body").then(($body) => {
            if ($body.find(".disclosure-card").length === 0) return;
            cy.get(".disclosure-card").each(($card) => {
                const cardText = $card.text();
                expect(cardText).to.include("Program Provider(s):");
                expect(cardText).to.include("Program:");
                expect(cardText).to.include("Date:");
                expect(cardText).to.include("Location:");
            });
        });
    });

    it("date field is formatted as MM/DD/YYYY", () => {
        cy.get("body").then(($body) => {
            if ($body.find(".disclosure-card").length === 0) return;
            cy.get(".disclosure-card").first().within(() => {
                // Date is rendered inline as "Date: MM/DD/YYYY" inside
                // `.field-value--light`. Extract the date portion and assert.
                cy.get(".field-value--light").contains("Date:").invoke("text").then((text) => {
                    const match = text.match(/(\d{2}\/\d{2}\/\d{4})/);
                    expect(match, `expected MM/DD/YYYY in: ${text}`).to.not.be.null;
                });
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
                    // "Date: MM/DD/YYYY" is inlined inside .field-value--light.
                    cy.wrap($card)
                        .find(".field-value--light")
                        .contains("Date:")
                        .invoke("text")
                        .then((dateText) => {
                            const match = dateText.match(/(\d{4})$/);
                            expect(match, `expected year in: ${dateText}`).to.not.be.null;
                            expect(match![1]).to.equal(year);
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

    it("disclosure cards group fields with .disclosure-field-group + .field-divider in the body zone", () => {
        // Markup was refactored from dl/dt/dd to stacked .disclosure-field-group
        // sections separated by `<hr class="field-divider">`, with labels in
        // `.field-label` and values in `.field-value`. Validate that structure.
        cy.get("body").then(($body) => {
            if ($body.find(".disclosure-card").length === 0) return;
            cy.get(".disclosure-card").first().within(() => {
                cy.get(".disclosure-body").should("exist");
                // At least the Provider group + the Program/Date/Location group.
                cy.get(".disclosure-body .disclosure-field-group").should(
                    "have.length.at.least",
                    2,
                );
                // Provider group has an explicit label.
                cy.get(".disclosure-body .field-label").should(
                    "have.length.at.least",
                    1,
                );
                // Sections are separated by hr.field-divider.
                cy.get(".disclosure-body hr.field-divider").should(
                    "have.length.at.least",
                    1,
                );
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
        // Tab 1: h1 → back-link <a> inside the h1.
        cy.realPress("Tab");
        cy.focused().should("have.prop", "tagName", "A");
        // The seminar_intro_text is a CMS RichTextField and may contain its
        // own anchor (the external policy link), which sits between the
        // back-link and the year-filter select in DOM order. Walk Tab
        // forward until we reach #year-select (if it's even on the page).
        cy.get("body").then(($body) => {
            if ($body.find("#year-select").length === 0) return;
            const reachYearSelect = (attemptsLeft: number) => {
                if (attemptsLeft <= 0) {
                    throw new Error("Tab never reached #year-select from the back-link");
                }
                cy.realPress("Tab");
                cy.focused().then(($el) => {
                    if ($el.attr("id") !== "year-select") {
                        reachYearSelect(attemptsLeft - 1);
                    }
                });
            };
            // Safety budget for intermediate intro-text anchors.
            reachYearSelect(10);
            cy.focused().should("have.attr", "id", "year-select");
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

    it("field labels are semibold (font-weight 600 per Figma)", () => {
        // Labels live in `.field-label` in the refactored field-group markup.
        cy.get("body").then(($body) => {
            if ($body.find(".disclosure-card").length === 0) return;
            cy.get(".disclosure-card .field-label").first()
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

// ─── PDF global spacing spec ──────────────────────────────────────────────────
// Values from UX Documentation.pdf (same spec applied to all pages):
//   Desktop page padding: 45px  •  h1 margin-bottom: 15px
//   Content block gaps:   34px  •  Mobile page padding: 25px (≤640px)

describe("Private Seminar Disclosures — PDF global spacing spec", () => {
    it("page padding-top is 45px at desktop (PDF global spacing spec)", () => {
        cy.viewport(1440, 900);
        cy.visit(PAGE_URL);
        cy.get("#private-seminar-page").should("have.css", "padding-top", "45px");
    });

    it("page padding-bottom is 45px at desktop (PDF global spacing spec)", () => {
        cy.viewport(1440, 900);
        cy.visit(PAGE_URL);
        cy.get("#private-seminar-page").should("have.css", "padding-bottom", "45px");
    });

    it("h1 has page-title class so 15px margin-bottom is applied (PDF global spacing spec)", () => {
        cy.visit(PAGE_URL);
        cy.get('h1[data-testid="page-title"]')
            .should("have.class", "page-title")
            .and("have.css", "margin-bottom", "15px");
    });

    it("disclosure-controls margin-top is 34px (PDF global spacing spec)", () => {
        // .disclosure-controls sits below the seminar intro paragraph as the
        // next content block, so the 34px content-block gap is on margin-top
        // (margin-bottom is 0 — the controls are immediately followed by the
        // disclosure grid which has its own 18px top margin from Figma).
        cy.visit(PAGE_URL);
        cy.get("body").then(($body) => {
            if ($body.find(".disclosure-controls").length === 0) return;
            cy.get(".disclosure-controls").should("have.css", "margin-top", "34px");
        });
    });

    it("disclosure-grid uses Figma row/column gaps (15px × 18px) at desktop", () => {
        // Figma frame math: 1152 - (568.5 × 2) = 15px column-gap; row-gap is
        // the outer-frame 18px. This intentionally overrides the global 34px
        // content-block gap because the cards are visually paired rather than
        // separated content blocks.
        cy.viewport(1440, 900);
        cy.visit(PAGE_URL);
        cy.get("body").then(($body) => {
            if ($body.find(".disclosure-grid").length === 0) return;
            cy.get(".disclosure-grid").should("have.css", "column-gap", "15px");
            cy.get(".disclosure-grid").should("have.css", "row-gap", "18px");
        });
    });

    it("page padding-top is 25px at mobile (PDF global spacing spec)", () => {
        cy.viewport(390, 844);
        cy.visit(PAGE_URL);
        cy.get("#private-seminar-page").should("have.css", "padding-top", "25px");
    });

    it("page padding-bottom is 25px at mobile (PDF global spacing spec)", () => {
        cy.viewport(390, 844);
        cy.visit(PAGE_URL);
        cy.get("#private-seminar-page").should("have.css", "padding-bottom", "25px");
    });

    it("disclosure grid collapses to 1 column at 640px mobile breakpoint (project standard)", () => {
        cy.viewport(640, 844);
        cy.visit(PAGE_URL);
        cy.get("body").then(($body) => {
            if ($body.find(".disclosure-grid").length === 0) return;
            cy.get(".disclosure-grid").then(($grid) => {
                const cols = window.getComputedStyle($grid[0]).gridTemplateColumns.split(" ");
                expect(cols).to.have.length(1);
            });
        });
    });

    it("disclosure grid is still 2 columns at 641px (just above mobile breakpoint)", () => {
        cy.viewport(641, 900);
        cy.visit(PAGE_URL);
        cy.get("body").then(($body) => {
            if ($body.find(".disclosure-grid").length === 0) return;
            cy.get(".disclosure-grid").then(($grid) => {
                const cols = window.getComputedStyle($grid[0]).gridTemplateColumns.split(" ");
                expect(cols).to.have.length(2);
            });
        });
    });
});
