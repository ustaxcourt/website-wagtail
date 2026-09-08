import { checkA11y } from "../../support/commands";

// Covers the reshaped Card Set component (WAG-1338) via the real
// "Which Case Procedure Should I Choose?" page, which renders 3 green
// "Check" cards and 1 yellow "Exclamation" card (Examples 4/5 in the story).
describe('Case Procedure Information - Card Set', () => {
  it('renders the green and yellow numbered-icon cards with no a11y violations', () => {
    cy.visit('/case-procedure/');
    cy.get('h1').should('contain', 'Which Case Procedure Should I Choose?');

    cy.get('.info-cards').should('have.length', 2);

    cy.get('.info-cards').eq(0).within(() => {
      cy.get('.info-card').should('have.length', 3);
      cy.get('.info-card.green').should('have.length', 3);
      cy.get('.info-card__icon-badge i[role="img"][aria-label="Success"]').should('have.length', 3);
      cy.contains('.info-card .title', 'More trial location options');
      cy.contains('.info-card .title', 'Less formal procedures');
      cy.contains('.info-card .title', 'Relaxed evidence rules');
    });

    cy.get('.info-cards').eq(1).within(() => {
      cy.get('.info-card').should('have.length', 1);
      cy.get('.info-card.yellow').should('have.length', 1);
      cy.get('.info-card__icon-badge i[role="img"][aria-label="Warning"]').should('have.length', 1);
      cy.contains('.info-card .title', 'No appeals process');
    });

    // No buttons/links live inside this page's card set - confirms the
    // component itself introduces no keyboard traps or unexpected tab stops.
    cy.get('.info-cards a, .info-cards button, .info-cards [tabindex]').should('not.exist');

    checkA11y('.info-cards');
  });

  it('stacks into a single column on mobile and stays a single row on tablet/desktop', () => {
    cy.visit('/case-procedure/');

    cy.viewport(1280, 800);
    cy.get('.info-cards').first().should('have.css', 'flex-direction', 'row');

    cy.viewport(900, 1024); // tablet width - the site's mobile breakpoint is max-width:768px
    cy.get('.info-cards').first().should('have.css', 'flex-direction', 'row');

    cy.viewport('iphone-x'); // mobile width, below the 768px breakpoint
    cy.get('.info-cards').first().should('have.css', 'flex-direction', 'column');
  });
});
