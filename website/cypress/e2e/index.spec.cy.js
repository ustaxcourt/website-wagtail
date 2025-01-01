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
})
