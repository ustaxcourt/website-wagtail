import { checkA11y, checkHeaderOrder, checkHeaderStyles } from "../../support/commands";

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
