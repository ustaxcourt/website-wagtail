import { checkA11y } from "../support/commands"

describe('index page', () => {
  beforeEach(() => {
    cy.visit('/')
    cy.get('.entries-list').should('exist')
    checkA11y();
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

    checkA11y();

    button.click()
    bannerContent().should('be.hidden')
  })

  it('can expand eFiling navigation to show Case Related Forms link', () => {
    // Check initial state
    cy.get('[data-testid="nav-button-efiling-case-maintenance"]')
      .should('be.visible').realHover()

    cy.get('[data-testid="nav-link-case-related-forms"]')
      .should('be.visible')
      .click();

    cy.url().should('include', '/case_related_forms/')
  })
})
