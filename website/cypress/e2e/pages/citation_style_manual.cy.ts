import {checkA11y, checkHeaderOrder, checkHeaderStyles} from "../../support/commands"

describe('citation style manual page', () => {
  beforeEach(() => {
    cy.visit('/citation_and_style_manual/')
  })

  it('verify page content and document is downloadable  and check accessibility & header consistency', () => {
    // Check title exists
    cy.get('[data-testid="page-title"]').should('contain', 'Citation and Style Manual')

    // Check body text exists
    cy.get('[data-testid="page-body-paragraph"]').should('contain', 'In January 2022')

    checkA11y();
    checkHeaderOrder();
    checkHeaderStyles();

    // Check document link exists and is downloadable
    const documentLink = cy.get('[data-testid="document-link"]')
    documentLink.should('exist')

    documentLink.then($link => {
      const href = $link.prop('href')
      cy.request(href).then((response) => {
        expect(response.status).to.eq(200)
        expect(response.headers['content-type']).to.include('application/pdf')
      })
    })
  })
})
