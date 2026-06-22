import {checkA11y} from "../../support/commands";

describe('StatusPage Embed Accessibility Fix', () => {
    it('removes tabindex from StatusPage iframe and passes a11y check', () => {
        cy.visit('/');
        cy.window().then((win) => {
            if (typeof (win as any).statusEmbedTest === 'function') {
                (win as any).statusEmbedTest();
            }
        });
        cy.get('iframe[src*="statuspage.io/embed/frame"]', { timeout: 20000 })
            .should('exist');
        checkA11y(undefined, {
            exclude: [['iframe[src*="statuspage.io/embed/frame"]']],
        });
        cy.get('iframe[src*="statuspage.io/embed/frame"]')
            .should('not.have.attr', 'tabindex');
    });
});
