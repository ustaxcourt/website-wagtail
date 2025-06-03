import {checkA11y} from "../../support/commands";

describe('StatusPage Embed Accessibility Fix', () => {
    it('removes tabindex from StatusPage iframe and passes a11y check', () => {
        cy.visit('/');
        cy.window().then(win => win.statusEmbedTest())
        cy.get('iframe[src*="statuspage.io/embed/frame"]', { timeout: 10000 })
            .should('be.visible');
        checkA11y();
        cy.get('iframe[src*="statuspage.io/embed/frame"]')
            .should('not.have.attr', 'tabindex');
    });
});
