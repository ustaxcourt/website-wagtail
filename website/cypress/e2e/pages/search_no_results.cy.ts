import {checkA11y, checkHeaderOrder, checkHeaderStyles} from "../../support/commands"

describe('Search page - No results', () => {
  beforeEach(() => {
    cy.visit('/search/?query=zyxwv')
  })

  it('Verify text color of "No results found" message is black', () => {
    cy.get('div.no-results').should('include.text', 'No results found').and('have.css', 'color').should('include', 'rgb(0, 0, 0)')

    checkA11y();
  })

  it('Verify font weight of "No results found" message is bold', () => {
    cy.get('div.no-results').should('include.text', 'No results found').and('have.css', 'font-weight').should('include', '700')

    checkA11y();
  })

  it('Verify aria-label existence on search button inside search page', () => {
    cy.get('input[data-testid="search-inpage-input"]').should(($button) => {
      expect($button.eq(0).attr('aria-label')).to.contain('Search button')
    });

    checkA11y();
  })
})
