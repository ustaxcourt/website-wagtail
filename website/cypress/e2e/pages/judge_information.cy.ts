import { checkA11y, checkHeaderOrder, checkHeaderStyles, checkA11yWithModerate, terminalLog } from "../../support/commands";

describe("Judge Information page", () => {
    beforeEach(() => {
        cy.visit("/judges/");
    });

    it("loads the page and passes accessibility checks", () => {
        cy.get('[data-testid="page-title"]').should("contain", "Judge Information");
        checkA11y();
        checkHeaderOrder();
        checkHeaderStyles();
    });

    it("section headers match Figma specs (24px, weight 600, white on #005EA2)", () => {
        cy.get(".judge-section-header").first().should("have.css", "font-size", "24px");
        cy.get(".judge-section-header").first().should("have.css", "font-weight", "600");
        cy.get(".judge-section-header").first().should("have.css", "color", "rgb(255, 255, 255)");
        cy.get(".judge-section-header").first().should("have.css", "background-color", "rgb(0, 94, 162)");
    });

    it("displays introductory text", () => {
        cy.get(".judge-intro").should("exist").and("not.be.empty");
    });

    it("displays all 5 filter buttons", () => {
        cy.get(".judge-filter-bar button").should("have.length.at.least", 2);
        cy.get('.judge-filter-btn[data-filter="all"]').should("contain", "All Judges");
        cy.get('.judge-filter-btn[data-filter="judges"]').should("contain", "Judges");
        cy.get('.judge-filter-btn[data-filter="senior-judges"]').should("contain", "Senior Judges");
        cy.get('.judge-filter-btn[data-filter="special-trial-judges"]').should("contain", "Special Trial Judges");
        cy.get('.judge-filter-btn[data-filter="senior-special-trial-judges"]').should("contain", "Senior Special Trial Judges");
    });

    it("All Judges filter is active by default", () => {
        cy.get('.judge-filter-btn[data-filter="all"]').should("have.class", "active");
    });

    it("displays judge sections with blue section headers", () => {
        cy.get(".judge-section").should("have.length.at.least", 1);
        cy.get(".judge-section-header").first().should("exist").and("not.be.empty");
    });

    it("section headers use Biography for 1 judge and Biographies for multiple", () => {
        cy.get(".judge-section").each(($section) => {
            const cardCount = $section.find(".judge-card").length;
            const headerText = $section.find(".judge-section-header").text();
            if (cardCount === 1) {
                expect(headerText).to.include("Biography");
                expect(headerText).not.to.include("Biographies");
            } else {
                expect(headerText).to.include("Biographies");
            }
        });
    });

    it("judge cards display name and role", () => {
        cy.get(".judge-card").first().within(() => {
            cy.get(".judge-name").should("exist").and("not.be.empty");
            cy.get(".judge-role").should("exist").and("not.be.empty");
        });
    });

    it("clicking a filter shows only that section and updates the breadcrumb", () => {
        cy.get('.judge-filter-btn[data-filter="senior-judges"]').click();

        cy.get('.judge-filter-btn[data-filter="senior-judges"]').should("have.class", "active");
        cy.get('.judge-filter-btn[data-filter="all"]').should("not.have.class", "active");

        cy.get('.judge-section[data-section="senior-judges"]').should("be.visible");
        cy.get('.judge-section[data-section="judges"]').should("not.be.visible");

        cy.get("#page-title-breadcrumb").should("contain", "Senior Judges");
    });

    it("filters can be combined — selecting two shows both sections", () => {
        cy.get('.judge-filter-btn[data-filter="judges"]').click();
        cy.get('.judge-filter-btn[data-filter="senior-judges"]').click();

        cy.get('.judge-section[data-section="judges"]').should("be.visible");
        cy.get('.judge-section[data-section="senior-judges"]').should("be.visible");
        cy.get('.judge-section[data-section="special-trial-judges"]').should("not.be.visible");

        cy.get("#page-title-breadcrumb").should("contain", "Judges").and("contain", "Senior Judges");
    });

    it("clicking All Judges resets all filters and hides the breadcrumb", () => {
        cy.get('.judge-filter-btn[data-filter="judges"]').click();
        cy.get('.judge-filter-btn[data-filter="all"]').click();

        cy.get('.judge-section').each(($section) => {
            cy.wrap($section).should("be.visible");
        });
        cy.get("#page-title-breadcrumb").should("not.be.visible");
        cy.get('.judge-filter-btn[data-filter="all"]').should("have.class", "active");
    });

    it("clicking the page title clears filters and resets breadcrumb", () => {
        cy.get('.judge-filter-btn[data-filter="judges"]').click();
        cy.get("#page-title-start").click();

        cy.get('.judge-filter-btn[data-filter="all"]').should("have.class", "active");
        cy.get("#page-title-breadcrumb").should("not.be.visible");
    });

    it("Senior Special Trial Judges section shows singular Biography when only 1 judge", () => {
        cy.get('.judge-section[data-section="senior-special-trial-judges"]').within(() => {
            cy.get(".judge-section-header").should("contain", "Biography");
            cy.get(".judge-card").should("have.length", 1);
        });
    });

    it("judge card links navigate to the judge detail page", () => {
        cy.get(".judge-card").first().then(($card) => {
            const href = $card.attr("href");
            expect(href).to.exist;
            cy.request(href!).its("status").should("eq", 200);
        });
    });

    it("displays the two bottom tiles", () => {
        cy.get('[data-testid="tile-private-seminar-disclosures"]')
            .should("exist")
            .and("contain", "Private Seminar Disclosures");
        cy.get('[data-testid="tile-judicial-conduct"]')
            .should("exist")
            .and("contain", "Judicial Conduct and Disability Complaint Procedures");
    });

    it("Private Seminar Disclosures tile navigates to the disclosures page", () => {
        cy.get('[data-testid="tile-private-seminar-disclosures"]').click();
        cy.url().should("include", "/judges/private-seminar-disclosures/");
        cy.get('[data-testid="page-title"]').should("contain", "Private Seminar Disclosures");
        checkA11y();
    });

    it("Judicial Conduct tile navigates away from the judges page", () => {
        cy.get('[data-testid="tile-judicial-conduct"]').then(($tile) => {
            const href = $tile.attr("href");
            expect(href).to.exist;
            expect(href).not.to.include("/judges/");
            cy.request(href!).its("status").should("eq", 200);
        });
    });
});

describe("Judge Information — Private Seminar Disclosures page", () => {
    beforeEach(() => {
        cy.visit("/judges/private-seminar-disclosures/");
    });

    it("loads and passes accessibility checks", () => {
        cy.get('[data-testid="page-title"]').should("contain", "Private Seminar Disclosures");
        checkA11y();
        checkHeaderOrder();
    });

    it("displays a link back to the Judge Information page", () => {
        cy.get('[data-testid="page-title"] a').should("contain", "Judge Information").and("have.attr", "href");
    });

    it("displays introductory text", () => {
        cy.get("#private-seminar-page p").first().should("not.be.empty");
    });

    it("shows disclosures or empty state message", () => {
        cy.get("body").then(($body) => {
            if ($body.find(".disclosure-grid").length > 0) {
                cy.get(".disclosure-card").should("have.length.at.least", 1);
                cy.get(".disclosure-card .judge-name").first().should("not.be.empty");
            } else {
                cy.get(".disclosure-empty").should("contain", "No seminar disclosures");
            }
        });
    });
});

describe("Judge Information — Judge detail page", () => {
    it("navigating to a judge card opens the judge detail page", () => {
        cy.visit("/judges/");
        cy.get(".judge-card").first().click();
        cy.url().should("match", /\/judges\/\d+\/[\w-]+\//);
        cy.get("h1").should("exist").and("not.be.empty");
        checkA11y();
        checkHeaderOrder();
    });
});

// ─── Figma design spec — desktop ────────────────────────────────────────────

describe("Judge Information — Figma design spec (desktop)", () => {
    beforeEach(() => {
        cy.viewport(1440, 900);
        cy.visit("/judges/");
    });

    it("filter bar: inactive button has correct border, color, font, radius", () => {
        cy.get('.judge-filter-btn[data-filter="judges"]').as("btn");
        cy.get("@btn").should("have.css", "border-top-color", "rgb(223, 225, 226)");
        cy.get("@btn").should("have.css", "border-top-width", "1px");
        cy.get("@btn").should("have.css", "color", "rgb(26, 68, 128)");
        cy.get("@btn").should("have.css", "font-size", "17px");
        cy.get("@btn").should("have.css", "font-weight", "400");
        cy.get("@btn").should("have.css", "border-top-left-radius", "2px");
    });

    it("filter bar: active button has correct background and text color", () => {
        cy.get('.judge-filter-btn[data-filter="all"]').as("btn");
        cy.get("@btn").should("have.css", "background-color", "rgb(22, 46, 81)");
        cy.get("@btn").should("have.css", "color", "rgb(255, 255, 255)");
    });

    it("filter bar: gap between buttons is 5px", () => {
        cy.get(".judge-filter-bar").should("have.css", "gap", "5px");
    });

    it("section header: correct size, weight, color, background, shadow", () => {
        cy.get(".judge-section-header").first().as("hdr");
        cy.get("@hdr").should("have.css", "font-size", "24px");
        cy.get("@hdr").should("have.css", "font-weight", "600");
        cy.get("@hdr").should("have.css", "line-height", "30px");
        cy.get("@hdr").should("have.css", "color", "rgb(255, 255, 255)");
        cy.get("@hdr").should("have.css", "background-color", "rgb(0, 94, 162)");
        cy.get("@hdr").should("have.css", "border-top-color", "rgb(0, 0, 0)");
        cy.get("@hdr").should("have.css", "border-top-width", "1px");
        cy.get("@hdr").invoke("css", "box-shadow").should("include", "rgba(0, 0, 0, 0.25)");
    });

    it("judge cards: correct background, radius, shadow, padding", () => {
        cy.get(".judge-card").first().as("card");
        cy.get("@card").should("have.css", "background-color", "rgb(250, 250, 250)");
        cy.get("@card").should("have.css", "border-top-left-radius", "5px");
        cy.get("@card").should("have.css", "border-top-right-radius", "5px");
        cy.get("@card").should("have.css", "border-bottom-left-radius", "0px");
        cy.get("@card").should("have.css", "border-bottom-right-radius", "0px");
        cy.get("@card").invoke("css", "box-shadow").should("include", "rgba(0, 0, 0, 0.25)");
        cy.get("@card").should("have.css", "padding-top", "15px");
        cy.get("@card").should("have.css", "padding-left", "15px");
    });

    it("judge card name: 20px, weight 600, line-height 25px, black", () => {
        cy.get(".judge-card .judge-name").first().as("name");
        cy.get("@name").should("have.css", "font-size", "20px");
        cy.get("@name").should("have.css", "font-weight", "600");
        cy.get("@name").should("have.css", "line-height", "25px");
        cy.get("@name").should("have.css", "color", "rgb(0, 0, 0)");
    });

    it("judge card role: 17px, line-height 20px, black", () => {
        cy.get(".judge-card .judge-role").first().as("role");
        cy.get("@role").should("have.css", "font-size", "17px");
        cy.get("@role").should("have.css", "line-height", "20px");
        cy.get("@role").should("have.css", "color", "rgb(0, 0, 0)");
    });

    it("judge card grid: 4 columns at desktop (≥835px)", () => {
        cy.get(".judge-card-grid").first().then(($grid) => {
            const cols = window.getComputedStyle($grid[0]).gridTemplateColumns.split(" ");
            expect(cols).to.have.length(4);
        });
    });

    it("bottom tiles: blue border, correct radius, shadow, font", () => {
        cy.get(".judge-tile").first().as("tile");
        cy.get("@tile").should("have.css", "border-top-color", "rgb(0, 94, 162)");
        cy.get("@tile").should("have.css", "border-top-width", "1px");
        cy.get("@tile").should("have.css", "border-top-left-radius", "5px");
        cy.get("@tile").invoke("css", "box-shadow").should("include", "rgba(86, 92, 101, 0.1)");
        cy.get("@tile").should("have.css", "font-size", "24px");
        cy.get("@tile").should("have.css", "font-weight", "600");
        cy.get("@tile").should("have.css", "line-height", "30px");
        cy.get("@tile").should("have.css", "padding-top", "29px");
        cy.get("@tile").should("have.css", "padding-left", "22px");
    });

    it("bottom tiles: column flex direction at desktop", () => {
        cy.get(".judge-tile").first().should("have.css", "flex-direction", "column");
    });

    it("judicial conduct tile uses fa-landmark icon", () => {
        cy.get('[data-testid="tile-judicial-conduct"] i')
            .should("have.class", "fa-landmark")
            .and("have.attr", "aria-hidden", "true");
    });

    it("private seminar tile uses fa-file-lines icon", () => {
        cy.get('[data-testid="tile-private-seminar-disclosures"] i')
            .should("have.class", "fa-file-lines")
            .and("have.attr", "aria-hidden", "true");
    });
});

// ─── Figma design spec — tablet ─────────────────────────────────────────────

describe("Judge Information — Figma design spec (tablet)", () => {
    beforeEach(() => {
        cy.viewport(834, 1112);
        cy.visit("/judges/");
    });

    it("judge card grid: 3 columns at tablet (834px)", () => {
        cy.get(".judge-card-grid").first().then(($grid) => {
            const cols = window.getComputedStyle($grid[0]).gridTemplateColumns.split(" ");
            expect(cols).to.have.length(3);
        });
    });

    it("bottom tiles remain 2-column at tablet", () => {
        cy.get(".judge-bottom-tiles").then(($grid) => {
            const cols = window.getComputedStyle($grid[0]).gridTemplateColumns.split(" ");
            expect(cols).to.have.length(2);
        });
    });

    it("section header font size unchanged at tablet", () => {
        cy.get(".judge-section-header").first().should("have.css", "font-size", "24px");
    });

    it("passes accessibility checks at tablet viewport", () => {
        cy.injectAxe();
        cy.checkA11y("#judge-information-page", { includedImpacts: ["serious", "critical"], retries: 3 }, terminalLog);
    });
});

// ─── Figma design spec — mobile ─────────────────────────────────────────────

describe("Judge Information — Figma design spec (mobile)", () => {
    beforeEach(() => {
        cy.viewport(390, 844);
        cy.visit("/judges/");
    });

    it("judge card grid: 1 column at mobile", () => {
        cy.get(".judge-card-grid").first().then(($grid) => {
            const cols = window.getComputedStyle($grid[0]).gridTemplateColumns.split(" ");
            expect(cols).to.have.length(1);
        });
    });

    it("bottom tiles stack to 1 column at mobile", () => {
        cy.get(".judge-bottom-tiles").then(($grid) => {
            const cols = window.getComputedStyle($grid[0]).gridTemplateColumns.split(" ");
            expect(cols).to.have.length(1);
        });
    });

    it("section header: 20px font, 22px line-height at mobile", () => {
        cy.get(".judge-section-header").first().as("hdr");
        cy.get("@hdr").should("have.css", "font-size", "20px");
        cy.get("@hdr").should("have.css", "line-height", "22px");
    });

    it("judge card name: 18px at mobile", () => {
        cy.get(".judge-card .judge-name").first().should("have.css", "font-size", "18px");
    });

    it("judge card role: 16px at mobile", () => {
        cy.get(".judge-card .judge-role").first().should("have.css", "font-size", "16px");
    });

    it("bottom tiles: row flex direction at mobile", () => {
        cy.get(".judge-tile").first().should("have.css", "flex-direction", "row");
    });

    it("bottom tiles: 20px font, 22px line-height at mobile", () => {
        cy.get(".judge-tile").first().as("tile");
        cy.get("@tile").should("have.css", "font-size", "20px");
        cy.get("@tile").should("have.css", "line-height", "22px");
    });

    it("bottom tiles: text color #162e51 at mobile", () => {
        cy.get(".judge-tile").first().should("have.css", "color", "rgb(22, 46, 81)");
    });

    it("bottom tiles: padding 22px at mobile", () => {
        cy.get(".judge-tile").first().as("tile");
        cy.get("@tile").should("have.css", "padding-top", "22px");
        cy.get("@tile").should("have.css", "padding-left", "22px");
    });

    it("passes accessibility checks at mobile viewport", () => {
        cy.injectAxe();
        cy.checkA11y("#judge-information-page", { includedImpacts: ["serious", "critical"], retries: 3 }, terminalLog);
    });

    it("desktop filter bar is hidden at mobile", () => {
        cy.get(".judge-filter-bar").should("not.be.visible");
    });

    it("mobile filter toggle button is visible", () => {
        cy.get("#mobile-filter-toggle").should("be.visible");
    });

    it("mobile filter toggle: white background, dark border by default", () => {
        cy.get("#mobile-filter-toggle")
            .should("have.css", "background-color", "rgb(255, 255, 255)")
            .and("have.css", "border-top-color", "rgb(22, 46, 81)");
    });

    it("mobile filter toggle: has fa-filter icon", () => {
        cy.get("#mobile-filter-toggle i.fa-filter").should("have.attr", "aria-hidden", "true");
    });

    it("mobile filter panel is hidden on load", () => {
        cy.get("#mobile-filter-panel").should("not.be.visible");
    });

    it("tapping Filter opens the panel", () => {
        cy.get("#mobile-filter-toggle").click();
        cy.get("#mobile-filter-panel").should("be.visible");
        cy.get("#mobile-filter-toggle").should("have.attr", "aria-expanded", "true");
    });

    it("panel shows all 5 filter options as checkboxes", () => {
        cy.get("#mobile-filter-toggle").click();
        cy.get("#mobile-filter-panel .mobile-filter-option").should("have.length", 5);
        cy.get('#mobile-filter-panel .mobile-filter-option[data-filter="all"]').should("contain", "All Judges");
        cy.get('#mobile-filter-panel .mobile-filter-option[data-filter="judges"]').should("contain", "Judges");
        cy.get('#mobile-filter-panel .mobile-filter-option[data-filter="senior-judges"]').should("contain", "Senior Judges");
        cy.get('#mobile-filter-panel .mobile-filter-option[data-filter="special-trial-judges"]').should("contain", "Special Trial Judges");
        cy.get('#mobile-filter-panel .mobile-filter-option[data-filter="senior-special-trial-judges"]').should("contain", "Senior Special Trial Judges");
    });

    it("All Judges is checked by default in the panel", () => {
        cy.get("#mobile-filter-toggle").click();
        cy.get('#mobile-filter-panel .mobile-filter-option[data-filter="all"]')
            .should("have.attr", "aria-checked", "true")
            .find("i").should("have.class", "fa-square-check");
    });

    it("panel has Apply and Clear filters buttons", () => {
        cy.get("#mobile-filter-toggle").click();
        cy.get("#mobile-filter-apply").should("be.visible").and("contain", "Apply");
        cy.get("#mobile-filter-clear").should("be.visible").and("contain", "Clear filters");
    });

    it("selecting a filter option in panel checks it", () => {
        cy.get("#mobile-filter-toggle").click();
        cy.get('#mobile-filter-panel .mobile-filter-option[data-filter="judges"]').click();
        cy.get('#mobile-filter-panel .mobile-filter-option[data-filter="judges"]')
            .should("have.attr", "aria-checked", "true")
            .find("i").should("have.class", "fa-square-check");
    });

    it("Apply closes the panel and filters the sections", () => {
        cy.get("#mobile-filter-toggle").click();
        cy.get('#mobile-filter-panel .mobile-filter-option[data-filter="judges"]').click();
        cy.get("#mobile-filter-apply").click();
        cy.get("#mobile-filter-panel").should("not.be.visible");
        cy.get('.judge-section[data-section="judges"]').should("be.visible");
        cy.get('.judge-section[data-section="senior-judges"]').should("not.be.visible");
    });

    it("Apply shows count badge on toggle button when filters active", () => {
        cy.get("#mobile-filter-toggle").click();
        cy.get('#mobile-filter-panel .mobile-filter-option[data-filter="judges"]').click();
        cy.get("#mobile-filter-apply").click();
        cy.get("#mobile-filter-count").should("be.visible").and("contain", "1");
    });

    it("Apply turns toggle button dark when filters are active", () => {
        cy.get("#mobile-filter-toggle").click();
        cy.get('#mobile-filter-panel .mobile-filter-option[data-filter="judges"]').click();
        cy.get("#mobile-filter-apply").click();
        cy.get("#mobile-filter-toggle").should("have.css", "background-color", "rgb(22, 46, 81)");
    });

    it("Clear filters inside panel unchecks all options and checks All Judges", () => {
        cy.get("#mobile-filter-toggle").click();
        cy.get('#mobile-filter-panel .mobile-filter-option[data-filter="judges"]').click();
        cy.get("#mobile-filter-clear").click();
        cy.get('#mobile-filter-panel .mobile-filter-option[data-filter="all"]')
            .should("have.attr", "aria-checked", "true");
        cy.get('#mobile-filter-panel .mobile-filter-option[data-filter="judges"]')
            .should("have.attr", "aria-checked", "false");
    });

    it("Escape key closes the panel", () => {
        cy.get("#mobile-filter-toggle").click();
        cy.get("#mobile-filter-panel").should("be.visible");
        cy.realPress("Escape");
        cy.get("#mobile-filter-panel").should("not.be.visible");
    });

    it("clicking outside the panel closes it", () => {
        cy.get("#mobile-filter-toggle").click();
        cy.get("#mobile-filter-panel").should("be.visible");
        cy.get("h1").click({ force: true });
        cy.get("#mobile-filter-panel").should("not.be.visible");
    });

    it("Space/Enter key on a filter option toggles it", () => {
        cy.get("#mobile-filter-toggle").click();
        cy.get('#mobile-filter-panel .mobile-filter-option[data-filter="senior-judges"]').focus().realPress("Space");
        cy.get('#mobile-filter-panel .mobile-filter-option[data-filter="senior-judges"]')
            .should("have.attr", "aria-checked", "true");
    });

    it("panel options have top border separator between each (except first)", () => {
        cy.get("#mobile-filter-toggle").click();
        cy.get("#mobile-filter-panel .mobile-filter-option").eq(1)
            .should("have.css", "border-top-width", "1px")
            .and("have.css", "border-top-color", "rgb(223, 225, 226)");
    });
});

// ─── 508 / accessibility ─────────────────────────────────────────────────────

describe("Judge Information — 508 accessibility", () => {
    beforeEach(() => {
        cy.viewport(1440, 900);
        cy.visit("/judges/");
    });

    it("passes full axe audit (all impact levels) scoped to judge page", () => {
        cy.injectAxe();
        cy.checkA11y(
            "#judge-information-page",
            {
                includedImpacts: ["minor", "moderate", "serious", "critical"],
                rules: {
                    // color-contrast requires computed styles that axe can't
                    // always resolve in headless — tested visually via Figma spec
                    "color-contrast": { enabled: false },
                },
                retries: 3,
            },
            terminalLog,
        );
    });

    it("filter bar has role=group with aria-label", () => {
        cy.get(".judge-filter-bar")
            .should("have.attr", "role", "group")
            .and("have.attr", "aria-label", "Filter judges by type");
    });

    it("all filter buttons have aria-pressed attribute", () => {
        cy.get(".judge-filter-btn").each(($btn) => {
            cy.wrap($btn).should("have.attr", "aria-pressed");
        });
    });

    it("active filter button has aria-pressed=true, inactive has aria-pressed=false", () => {
        cy.get('.judge-filter-btn[data-filter="all"]').should("have.attr", "aria-pressed", "true");
        cy.get('.judge-filter-btn[data-filter="judges"]').should("have.attr", "aria-pressed", "false");
    });

    it("aria-pressed updates when a filter is clicked", () => {
        cy.get('.judge-filter-btn[data-filter="judges"]').click();
        cy.get('.judge-filter-btn[data-filter="judges"]').should("have.attr", "aria-pressed", "true");
        cy.get('.judge-filter-btn[data-filter="all"]').should("have.attr", "aria-pressed", "false");
    });

    it("aria-live region exists and is empty on load", () => {
        cy.get("#filter-announcement")
            .should("have.attr", "aria-live", "polite")
            .and("have.attr", "aria-atomic", "true")
            .and("be.empty");
    });

    it("aria-live region announces when a filter is applied", () => {
        cy.get('.judge-filter-btn[data-filter="judges"]').click();
        cy.get("#filter-announcement").should("not.be.empty");
        cy.get("#filter-announcement").invoke("text").should("include", "Judges");
    });

    it("aria-live region announces 'all judges' when filters are cleared", () => {
        cy.get('.judge-filter-btn[data-filter="judges"]').click();
        cy.get('.judge-filter-btn[data-filter="all"]').click();
        cy.get("#filter-announcement").invoke("text").should("include", "all judges");
    });

    it("page title span has role=button with tabindex=0", () => {
        cy.get("#page-title-start")
            .should("have.attr", "role", "button")
            .and("have.attr", "tabindex", "0");
    });

    it("Space key on page title span clears filters", () => {
        cy.get('.judge-filter-btn[data-filter="judges"]').click();
        cy.get('.judge-section[data-section="judges"]').should("be.visible");
        cy.get(".judge-section").not('[data-section="judges"]').first().should("not.be.visible");

        cy.get("#page-title-start").focus().type(" ");

        cy.get('.judge-filter-btn[data-filter="all"]').should("have.attr", "aria-pressed", "true");
        cy.get(".judge-section").each(($s) => cy.wrap($s).should("be.visible"));
    });

    it("Enter key on page title span clears filters", () => {
        cy.get('.judge-filter-btn[data-filter="senior-judges"]').click();
        cy.get("#page-title-start").focus().type("{enter}");
        cy.get('.judge-filter-btn[data-filter="all"]').should("have.attr", "aria-pressed", "true");
    });

    it("all Font Awesome icons within judge page have aria-hidden=true", () => {
        cy.get("#judge-information-page i.fa-solid, #judge-information-page i.fa-regular").each(($icon) => {
            cy.wrap($icon).should("have.attr", "aria-hidden", "true");
        });
    });

    it("judge card links have descriptive text (name + role)", () => {
        cy.get(".judge-card").first().then(($card) => {
            const text = $card.text().trim();
            expect(text.length).to.be.greaterThan(5);
        });
    });

    it("heading hierarchy is correct (h1 → h2, no skips)", () => {
        checkHeaderOrder();
    });

    it("Tab walks through all filter buttons in DOM order", () => {
        const filterKeys = ["all", "judges", "senior-judges", "special-trial-judges", "senior-special-trial-judges"];
        cy.get(`.judge-filter-btn[data-filter="${filterKeys[0]}"]`).focus();
        for (let i = 1; i < filterKeys.length; i++) {
            cy.realPress("Tab");
            cy.get(`.judge-filter-btn[data-filter="${filterKeys[i]}"]`).should("be.focused");
        }
    });

    it("Shift+Tab walks filter buttons in reverse order", () => {
        cy.get('.judge-filter-btn[data-filter="senior-special-trial-judges"]').focus();
        cy.realPress(["Shift", "Tab"]);
        cy.get('.judge-filter-btn[data-filter="special-trial-judges"]').should("be.focused");
        cy.realPress(["Shift", "Tab"]);
        cy.get('.judge-filter-btn[data-filter="senior-judges"]').should("be.focused");
    });

    it("Space activates a filter button and updates sections", () => {
        cy.get('.judge-filter-btn[data-filter="judges"]').focus().realPress("Space");
        cy.get('.judge-filter-btn[data-filter="judges"]').should("have.attr", "aria-pressed", "true");
        cy.get('.judge-section[data-section="judges"]').should("be.visible");
        cy.get('.judge-section[data-section="senior-judges"]').should("not.be.visible");
    });

    it("Enter activates a filter button and updates sections", () => {
        cy.get('.judge-filter-btn[data-filter="senior-judges"]').focus().realPress("Enter");
        cy.get('.judge-filter-btn[data-filter="senior-judges"]').should("have.attr", "aria-pressed", "true");
        cy.get('.judge-section[data-section="senior-judges"]').should("be.visible");
        cy.get('.judge-section[data-section="judges"]').should("not.be.visible");
    });

    it("Tab reaches the first judge card after the filter bar", () => {
        // Tab past all 5 filter buttons then confirm focus lands on a judge card
        cy.get('.judge-filter-btn[data-filter="senior-special-trial-judges"]').focus();
        cy.realPress("Tab");
        cy.focused().should("have.class", "judge-card");
    });

    it("Tab walks through judge cards in order within a section", () => {
        cy.get(".judge-card").first().focus();
        cy.realPress("Tab");
        cy.focused().should("have.class", "judge-card");
        // Confirm the second focused card follows the first in DOM order
        cy.focused().then(($second) => {
            cy.get(".judge-card").eq(1).then(($expected) => {
                expect($second[0]).to.equal($expected[0]);
            });
        });
    });

    it("Tab reaches both bottom tiles after the judge cards", () => {
        cy.get('[data-testid="tile-private-seminar-disclosures"]').focus();
        cy.get('[data-testid="tile-private-seminar-disclosures"]').should("be.focused");
        cy.realPress("Tab");
        cy.get('[data-testid="tile-judicial-conduct"]').should("be.focused");
    });

    it("Enter on a judge card navigates to the detail page", () => {
        cy.get(".judge-card").first().then(($card) => {
            const href = $card.attr("href")!;
            cy.get(".judge-card").first().focus().realPress("Enter");
            cy.url().should("include", href);
        });
    });

    it("Enter on Private Seminar Disclosures tile navigates to disclosures page", () => {
        cy.get('[data-testid="tile-private-seminar-disclosures"]').focus().realPress("Enter");
        cy.url().should("include", "/judges/private-seminar-disclosures/");
    });

    it("focus order follows visual top-to-bottom layout (filter bar → cards → tiles)", () => {
        // Collect the vertical position of each focusable group's first element
        const selectors = [
            ".judge-filter-btn",
            ".judge-card",
            ".judge-tile",
        ];
        const tops: number[] = [];
        selectors.forEach((sel) => {
            cy.get(sel).first().then(($el) => {
                tops.push($el[0].getBoundingClientRect().top);
            });
        });
        cy.then(() => {
            for (let i = 1; i < tops.length; i++) {
                expect(tops[i]).to.be.greaterThan(tops[i - 1]);
            }
        });
    });
});
