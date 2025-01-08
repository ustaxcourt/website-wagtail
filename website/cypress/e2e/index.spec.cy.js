describe('index page', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('has required federal banner', () => {
    cy.get('[data-testid="usa-banner"]').contains('An official website of the United States government')
  })

  it('unhides/hides banner content when button is clicked', () => {
    // arrange
    let button = cy.get('[data-testid="toggle-usa-banner"]')
    let bannerContent = () => cy.get('[data-testid="usa-banner-content"]')

    // state when loaded
    bannerContent().should('be.hidden')

    button.click()
    bannerContent().should('be.visible')

    button.click()
    bannerContent().should('be.hidden')
  })

  // note: would have liked to have tested that the lists are visible but the behavior is driven by CSS, but Cypress does not support
  it('has navigation headers with hidden navigation links', () => {
    cy.get('[data-testid="navigation-bar"]')
      .should('be.visible')
      .find('.navigation')
      .children('.navigation-header')
      .each((header) => {

        cy.wrap(header)
          .find('.navigation-list')
          .should('be.hidden');
      })
  })
})
