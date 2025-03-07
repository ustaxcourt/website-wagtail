import { checkA11y } from "../../support/commands";

describe('Guidance for Petitioners Page', () => {
    it('successfully loads', () => {
      cy.visit('/petitioners/')
      cy.get('h1').should('contain', 'Guidance for Petitioners')
      checkA11y();
    })
  })
