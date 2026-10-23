import { checkA11y } from "../../support/commands";

describe("DAWSON How to e-file a Petition guide", () => {
    beforeEach(() => {
        cy.viewport(1440, 1000);
        cy.visit("/dawson-how-to-e-file-a-petition/");
    });

    it("renders the breadcrumb, introduction, reminder, and numbered phases", () => {
        cy.get('[data-testid="page-title"]').should("contain.text", "How to e-file a Petition");
        cy.get(".petitioner-breadcrumb-link")
            .should("contain.text", "DAWSON User Guides & Electronic Filing Instructions")
            .and("have.attr", "href")
            .and("match", /dawson-user-guides/);
        cy.get(".blue-page-links-bar").should("not.exist");
        cy.get(".detailed-timeline-header-text").should(
            "contain.text",
            "Before starting the e-filing process",
        );
        cy.get(".detailed-timeline-warning")
            .find("h3")
            .should("contain.text", "Important Reminder")
            .and("have.css", "text-transform", "uppercase");
        cy.get(".detailed-timeline-warning")
            .and("contain.text", "A petition should only be filed once.");

        const phaseTitles = [
            "Gather Your Information and Documents",
            "Create a DAWSON Account",
            "Start Your Case and File Your Petition",
            "Receive Your Docket Number and Pay the Filing Fee",
            "Manage Your Case in DAWSON",
        ];
        cy.get(".detailed-timeline-phase").should("have.length", phaseTitles.length);
        phaseTitles.forEach((title, index) => {
            cy.get(".detailed-timeline-phase")
                .eq(index)
                .should("have.class", "bubble-number")
                .and("contain.text", title)
                .then(($phase) => {
                    const bubble = getComputedStyle($phase[0], "::before");
                    expect(bubble.content).to.equal("counter(bubbleitem)");
                    expect(bubble.counterIncrement).to.equal("bubbleitem 1");
                });
        });
    });

    it("expands and collapses all five phases", () => {
        cy.get(".detailed-timeline-expand-button")
            .should("have.attr", "aria-expanded", "false")
            .and("contain.text", "Expand All")
            .click();

        cy.get(".detailed-timeline-expand-button")
            .should("have.attr", "aria-expanded", "true")
            .and("contain.text", "Collapse All");
        cy.get(".detailed-timeline-accordion-content").should("be.visible");

        cy.get(".detailed-timeline-expand-button").click();
        cy.get(".detailed-timeline-expand-button")
            .should("have.attr", "aria-expanded", "false")
            .and("contain.text", "Expand All");
        cy.get(".detailed-timeline-accordion-content.hidden").should("have.length", 5);
    });

    it("prints the page title, reminder, and expanded guide content", () => {
        cy.window().then((window) => cy.stub(window, "print").as("nativePrint"));
        cy.get(".detailed-timeline-print-button").should("contain.text", "Print").click();

        cy.get(".detailed-timeline-print-host")
            .should("contain.text", "How to e-file a Petition")
            .and("contain.text", "A petition should only be filed once.");
        cy.get(".detailed-timeline-print-host .detailed-timeline-accordion-content.hidden")
            .should("not.exist");
        cy.get("@nativePrint").should("have.been.calledOnce");
    });

    it("passes the accessibility audit", () => {
        checkA11y(".enhanced-page");
    });
});
