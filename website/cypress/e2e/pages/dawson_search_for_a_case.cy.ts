import { checkA11y } from "../../support/commands";

const PHASES: [string, "number" | "info"][] = [
        ["Search by Docket Number", "number"],
        ["Search by Petitioner Name", "number"],
        ["Tips and Tricks", "info"],
];

// [phase index, text that must appear in that phase], taken from the Figma mockup.
const PHASE_CONTENT: [number, string[]][] = [
        [0, ["The docket number must include the dash (for example, 123-18).", "(S, L, SL, R, X, D, or P)", "No Matches Found"]],
        [1, ["Partial name searches are not currently supported.", "Case Type (Docket Suffix)", "U.S. Territories and military bases are included."]],
        [2, ["If your search does not return a result:", "Apply filters to refine your search results."]],
];

// [resource card title, expected link]
const RESOURCE_CARDS: [string, RegExp][] = [
        ["DAWSON", /^https:\/\/(dawson|dev\.ef-cms|test\.ef-cms)\.ustaxcourt\.gov\/$/],
];

describe("DAWSON How to search for a case guide", () => {
    beforeEach(() => {
        cy.viewport(1440, 1000);
        cy.visit("/dawson-how-to-search-for-a-case/");
    });

    it("renders the breadcrumb, title and introduction without a navigation ribbon", () => {
        cy.get('[data-testid="page-title"]').should("contain.text", "How to search for a case");
        cy.get(".petitioner-breadcrumb-link")
            .should("contain.text", "DAWSON User Guides & Electronic Filing Instructions")
            .and("have.attr", "href")
            .and("match", /dawson-user-guides/);
        cy.get(".blue-page-links-bar").should("not.exist");
        cy.get(".dawson-efile-guide").should("exist");
        ["Docket Access Within and Secure Online Network", "docket number and petitioner name"].forEach((text) => {
            cy.get(".detailed-timeline-header-text").should("contain.text", text);
        });

    });

    it("shows the numbered phases with the right bubbles", () => {
        cy.get(".detailed-timeline-phase").should("have.length", PHASES.length);
        PHASES.forEach(([title, bubble], index) => {
            cy.get(".detailed-timeline-phase")
                .eq(index)
                .should("have.class", `bubble-${bubble}`)
                .find("h2.detailed-timeline-accordion-title")
                .should("contain.text", title);
        });
        cy.get(".detailed-timeline-phase.bubble-info").should(
            "have.length",
            PHASES.filter(([, bubble]) => bubble === "info").length,
        );
    });

    it("shows each phase's content and loads its screenshots", () => {
        PHASE_CONTENT.forEach(([index, texts]) => {
            texts.forEach((text) => {
                cy.get(".detailed-timeline-phase")
                    .eq(index)
                    .find(".detailed-timeline-accordion-content")
                    .should("contain.text", text);
            });
        });

        cy.get(".detailed-timeline-accordion-content img")
            .should("have.length", 2)
            .each(($img) => {
                expect($img).to.have.attr("alt").and.not.to.be.empty;
                expect(($img[0] as HTMLImageElement).naturalWidth, "image loaded").to.be.greaterThan(0);
            });
    });

    it("shows the Resources column with the right cards and links", () => {
        cy.get("#petitioner-resources-heading").should("have.text", "Resources");
        cy.get(".petitioner-resource-items a.quick-access-tile-link").should(
            "have.length",
            RESOURCE_CARDS.length,
        );
        RESOURCE_CARDS.forEach(([title, href], index) => {
            cy.get(".petitioner-resource-items a.quick-access-tile-link")
                .eq(index)
                .should("contain.text", title)
                .and("have.attr", "href")
                .and("match", href);
            cy.get(".petitioner-resource-items .quick-access-tile svg, .petitioner-resource-items .quick-access-tile img")
                .eq(index)
                .should("exist");
        });
    });

    it("opens every phase by default and supports collapse and expand", () => {
        cy.get(".detailed-timeline-expand-button")
            .should("have.attr", "aria-expanded", "true")
            .and("contain.text", "Collapse All");
        cy.get(".detailed-timeline-accordion-content").should("be.visible");

        cy.get(".detailed-timeline-expand-button")
            .click()
            .should("have.attr", "aria-expanded", "false")
            .and("contain.text", "Expand All");
        cy.get(".detailed-timeline-accordion-content.hidden").should("have.length", PHASES.length);

        cy.get(".detailed-timeline-expand-button")
            .click()
            .should("have.attr", "aria-expanded", "true")
            .and("contain.text", "Collapse All");
        cy.get(".detailed-timeline-accordion-content").should("be.visible");
    });

    it("prints the guide with every phase expanded and the button labelled Print", () => {
        cy.get(".detailed-timeline-expand-button")
            .click()
            .should("have.attr", "aria-expanded", "false");
        cy.window().then((window) => cy.stub(window, "print").as("nativePrint"));
        cy.get(".detailed-timeline-print-button")
            .should(($button) => expect($button.text().trim()).to.equal("Print"))
            .click();

        cy.get(".detailed-timeline-print-host .detailed-timeline-title-block h2").should(
            "have.text",
            "How to search for a case",
        );
        cy.get(".detailed-timeline-print-host .detailed-timeline-phase").should(
            "have.length",
            PHASES.length,
        );
        cy.get(".detailed-timeline-print-host .detailed-timeline-accordion-content.hidden").should(
            "not.exist",
        );
        cy.get("@nativePrint").should("have.been.calledOnce");
    });

    [375, 834, 1440].forEach((width) => {
        it(`lays out the page without horizontal scrolling at ${width}px`, () => {
            cy.viewport(width, 1000);
            cy.visit("/dawson-how-to-search-for-a-case/");

            cy.get(".enhanced-page").should(($page) => {
                expect($page[0].scrollWidth).to.be.at.most($page[0].clientWidth);
            });

            // Desktop: Resources sit beside the timeline. Tablet and mobile: underneath it.
            cy.get(".detailed-timeline-phase").last().then(($lastPhase) => {
                const phase = $lastPhase[0].getBoundingClientRect();
                cy.get("#petitioner-resources-heading").then(($heading) => {
                    const heading = $heading[0].getBoundingClientRect();
                    if (width >= 1200) {
                        expect(heading.left).to.be.at.least(phase.right - 1);
                    } else {
                        expect(heading.top).to.be.at.least(phase.bottom - 1);
                    }
                });
            });
        });
    });

    it("passes the accessibility audit", () => {
        checkA11y(".enhanced-page");
    });
});
