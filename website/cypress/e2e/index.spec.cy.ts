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

  it('can expand Trials & Case Management navigation to show Case Related Forms link', () => {
    // Check initial state
    cy.get('[data-testid="nav-button-trials-case-management"]')
      .should('be.visible').realHover()

    cy.get('[data-testid="nav-link-case-related-forms"]')
      .should('be.visible')
      .click();

    cy.url().should('include', '/case-related-forms/')
  })

  it('quick access tile links point to destinations other than the home page', () => {
    cy.url().then((homeUrl) => {
      const homeResolved = new URL(homeUrl)
      cy.get('.cards-grid a').each(($a) => {
        const href = $a.attr('href')
        expect(href, 'tile link href should not be empty').to.be.a('string').and.not.be.empty
        const resolvedUrl = new URL(href!, homeUrl)
        // Cross-origin links are never the home page; only check pathname for same-origin links
        if (resolvedUrl.origin === homeResolved.origin) {
          expect(resolvedUrl.pathname, 'tile link should not point to home page').to.not.equal(homeResolved.pathname)
        }
      })
    })
  })

  it('quick access tiles have GTM tracking attributes', () => {
    cy.get('[data-gtm-element="quick-access-tile"]').then(($tiles) => {
      expect($tiles.length).to.be.greaterThan(0)
      $tiles.each((_, el) => {
        expect(el.getAttribute('data-gtm-label')).to.be.a('string').and.not.be.empty
      })
    })
  })

  it('nav menu items have GTM tracking attributes', () => {
    cy.get('[data-gtm-element="nav-menu-item"]').then(($links) => {
      expect($links.length).to.be.greaterThan(0)
      $links.each((_, el) => {
        expect(el.getAttribute('data-gtm-label')).to.be.a('string').and.not.be.empty
      })
    })
  })

  it('search buttons contain text or title attribute for accessibility', () => {
    cy.get('[data-testid="search-button"]').should(($button) => {

      expect($button).to.have.length(3) //checking that home page has three search buttons
      expect($button.eq(0)).to.contain('Search') //test tablet search box
      expect($button.eq(1)).to.contain('Search') //test desktop search box
      expect($button.eq(2).attr('title')).to.contain('Search') //test mobile search box
    });
  })
})
