const { checkA11y } = require("../../support/commands")

describe('Transcripts & Copies Page', () => {
  it('displays correct content, has working links, and passes accessibility', () => {
    cy.visit('/transcripts_and_copies')
    cy.get('h1').should('be.visible')
    checkA11y()

    cy.get('h1').should('contain', 'Transcripts & Copies')


    // Verify key content sections exist
    cy.get('strong').should('contain', 'Transcripts')
    cy.get('strong').should('contain', 'Copies')

    // Check some specific content to ensure correct page
    cy.contains('Transcripts of proceedings before the Tax Court').should('exist')
    cy.contains('eScribers').should('exist')

    // Check external link
    cy.get('a[href="https://www.escribers.net/"]')
      .should('exist')
      .and('have.attr', 'href', 'https://www.escribers.net/')

    // Check internal link
    cy.get('a[href="/dawson"]')
      .contains('Register for DAWSON instructions')
      .should('exist')
      .then(($link) => {
        expect($link.text().trim()).to.equal('Register for DAWSON instructions')
      })
  })
})
