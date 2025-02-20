import {checkA11y, checkHeaderOrder, checkHeaderStyles} from "../../support/commands"

describe('clinics page', () => {
  beforeEach(() => {
    cy.visit('/clinics/')
  })

  it('verify page content and document is downloadable  and check accessibility & header consistency', () => {
    cy.get('h1').should('contain', 'Clinics & Pro Bono Programs')
    cy.get('h3').should('contain', 'Procedures for Programs Not Currently Participating')
    cy.get(`a[href="mailto:litc@ustaxcourt.gov"]`).should('exist')

    checkA11y();
    checkHeaderOrder();
    checkHeaderStyles();
  })
})
