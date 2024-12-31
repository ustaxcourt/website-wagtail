describe('index page', () => {
  beforeEach(() => {
    cy.visit('http://127.0.0.1:8000/')
  })

  it('has required federal banner', () => {
    cy.get('section').should('have.class', 'usa-banner')
  })

  it('unhides/hides banner content when button is clicked', () => {
    // arrange
    let button = cy.get('button').should('have.class', 'usa-accordion__button').should('have.class', 'usa-accordion__button')
    let bannerContent = () => cy.get('div').should('have.class', 'usa-banner__content').should('have.class', 'usa-accordion__content wide-container')

    // state when loaded
    bannerContent().should('be.hidden')

    button.click()
    bannerContent().should('be.visible')

    button.click()
    bannerContent().should('be.hidden')
  })
})
