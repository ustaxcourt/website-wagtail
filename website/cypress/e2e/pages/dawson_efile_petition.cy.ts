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

    it("opens all five phases by default and supports collapse and expand", () => {
        cy.get(".detailed-timeline-expand-button")
            .should("have.attr", "aria-expanded", "true")
            .and("contain.text", "Collapse All");
        cy.get(".detailed-timeline-accordion-content").should("be.visible");

        cy.get(".detailed-timeline-expand-button").click()
            .should("have.attr", "aria-expanded", "false")
            .and("contain.text", "Expand All");
        cy.get(".detailed-timeline-accordion-content.hidden").should("have.length", 5);

        cy.get(".detailed-timeline-expand-button").click()
            .should("have.attr", "aria-expanded", "true")
            .and("contain.text", "Collapse All");
        cy.get(".detailed-timeline-accordion-content").should("be.visible");
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

    [375, 600, 768, 834, 1024, 1200].forEach((width) => {
        it(`uses petitioner-page responsive styling at ${width}px`, () => {
            cy.viewport(width, 1000);
            cy.visit("/petitioners-timeline/");

            const styleProperties = {
                ".enhanced-page": ["padding-top", "padding-right", "padding-bottom", "padding-left"],
                '[data-testid="page-title"]': ["font-size", "line-height", "font-weight"],
                ".detailed-timeline-header": ["align-items", "gap"],
                ".detailed-timeline-expand-button": ["font-size", "padding", "min-height"],
                ".detailed-timeline-expand-button-icon": ["width", "height"],
                ".detailed-timeline-accordion-title": ["font-size", "padding"],
            };

            cy.document().then((referenceDocument) => {
                const referenceStyles = Object.entries(styleProperties).map(([selector, properties]) => {
                    const element = referenceDocument.querySelector(selector);
                    expect(element, selector).not.to.be.null;
                    const styles = referenceDocument.defaultView!.getComputedStyle(element!);
                    return { selector, properties: properties.map((property) => [property, styles.getPropertyValue(property)]) };
                });

                cy.visit("/dawson-how-to-e-file-a-petition/");
                cy.document().then((guideDocument) => {
                    referenceStyles.forEach(({ selector, properties }) => {
                        const element = guideDocument.querySelector(selector);
                        expect(element, selector).not.to.be.null;
                        const styles = guideDocument.defaultView!.getComputedStyle(element!);
                        properties.forEach(([property, value]) => {
                            expect(styles.getPropertyValue(property), `${selector} ${property}`).to.equal(value);
                        });
                    });
                });
            });

            if (width < 480) {
                cy.get(".detailed-timeline-controls").then(($controls) => {
                    const controls = $controls[0].getBoundingClientRect();
                    cy.get(".detailed-timeline-control-button").each(($button) => {
                        const button = $button[0].getBoundingClientRect();
                        expect(button.width).to.be.at.least(controls.width - 8);
                        expect(button.right).to.be.at.most(controls.right);
                    });
                });
            }

            cy.get(".detailed-timeline-expand-button").should("contain.text", "Collapse All");
            cy.get(".detailed-timeline-accordion-content").should("be.visible");
            cy.get(".enhanced-page").should(($page) => {
                expect($page[0].scrollWidth).to.be.at.most($page[0].clientWidth);
            });
        });
    });

    it("preserves the desktop design", () => {
        cy.get(".enhanced-page")
            .should("have.css", "padding-left", "32px")
            .and("have.css", "padding-top", "45px");
        cy.get('[data-testid="page-title"]').should("have.css", "font-size", "28px");
        cy.get(".detailed-timeline-expand-button")
            .should("have.css", "width", "130px")
            .and("have.css", "font-size", "14px");
    });

    it("passes the accessibility audit", () => {
        checkA11y(".enhanced-page");
    });
});
