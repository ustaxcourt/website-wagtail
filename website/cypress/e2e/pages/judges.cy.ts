import { checkA11y } from "../../support/commands";

describe('Judges page', () => {
  it('should hit the users endpoint and display expected elements', () => {
    cy.visit('/judges');

    cy.get('.judge-card').should('have.length.at.least', 1);
    cy.get('.judge-card').first().then(($link) => {
      const expectedUrl = $link.attr('href');

      cy.wrap($link).click();

      cy.url().should('include', expectedUrl);

      cy.get('.judge-name').should('be.visible').and('not.be.empty');
      cy.get('.judge-bio').should('be.visible').and('not.be.empty');
    });

    checkA11y();
  })
})
