import { checkA11y } from "../../support/commands";
import {
    checkNoClickableText,
    checkNoDoubleAnnouncements,
    trackClickListeners,
} from "../../support/screen_reader";

describe("Petitioners Help FAQ filter and accordion", () => {
    const filters = () => cy.get("[data-faq-filter]");
    const visibleQuestions = () => cy.get("[data-faq-item]:visible");

    beforeEach(() => {
        cy.viewport(1280, 800);
        cy.visit("/petitioners-help/", { onBeforeLoad: trackClickListeners });
        cy.get("[data-faq]").should("exist");
    });

    it("passes axe checks", () => {
        checkA11y("[data-faq]");
    });

    it("reads each filter pill and question tag only once", () => {
        checkNoDoubleAnnouncements("[data-faq]");
    });

    it("doesn't announce the question tags as clickable", () => {
        checkNoClickableText("[data-faq]");
    });

    it("lets keyboard users tab to every filter pill", () => {
        filters().first().focus();
        filters().each(($filter, index) => {
            if (index > 0) cy.realPress("Tab");
            cy.focused().should("have.text", $filter.text());
        });
    });

    it("filters with Enter or Space and announces the result", () => {
        filters().contains("Deadlines").focus();
        cy.realPress("Enter");
        filters().contains("Deadlines").should("have.attr", "aria-pressed", "true");
        filters().contains("All").should("have.attr", "aria-pressed", "false");
        visibleQuestions().should("have.length", 2);
        visibleQuestions().each(($item) => {
            cy.wrap($item).should("have.attr", "data-filtertag", "deadlines");
        });
        cy.get("[data-faq-status]").should("have.text", "Showing 2 of 11 questions");

        filters().contains("All").focus();
        cy.realPress("Space");
        filters().contains("All").should("have.attr", "aria-pressed", "true");
        visibleQuestions().should("have.length", 11);
    });

    it("opens a question from anywhere on its header, but not from the answer", () => {
        // realClick hits whatever is on top at those coordinates, like a real
        // mouse; the question link is stretched over the tag and chevron.
        cy.get("#petition-deadline").as("item");
        cy.get("@item").find("[data-faq-answer]").should("not.be.visible");
        cy.get("@item").find(".faq__tag").realClick();
        cy.get("@item").find("[data-faq-link]").should("have.attr", "aria-expanded", "true");
        cy.get("@item").find("[data-faq-answer]").should("be.visible").click();
        cy.get("@item").find("[data-faq-link]").should("have.attr", "aria-expanded", "true");
        cy.get("@item").find(".faq__toggle").realClick();
        cy.get("@item").find("[data-faq-link]").should("have.attr", "aria-expanded", "false");
    });

    it("toggles a question with Enter on its link", () => {
        cy.get("#petition-deadline [data-faq-link]").as("link").focus();
        cy.realPress("Enter");
        cy.get("@link").should("have.attr", "aria-expanded", "true");
        cy.realPress("Enter");
        cy.get("@link").should("have.attr", "aria-expanded", "false");
    });

    [
        { name: "desktop", width: 1280, height: 800 },
        { name: "tablet", width: 768, height: 1024 },
        { name: "mobile", width: 375, height: 812 },
    ].forEach(({ name, width, height }) => {
        it(`uses 14px semibold question tags on ${name}`, () => {
            cy.viewport(width, height);
            cy.get(".faq__tag")
                .first()
                .should("have.css", "font-size", "14px")
                .and("have.css", "font-weight", "600");
        });
    });
});
