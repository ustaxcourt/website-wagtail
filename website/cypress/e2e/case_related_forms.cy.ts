import { checkA11y } from "../support/commands"

describe('case related forms page', () => {
  beforeEach(() => {
    cy.visit('/admin')
  })

  it('has required federal banner', () => {
    cy.get('[data-testid="usa-banner"]').contains('An official website of the United States government')
  })

})
