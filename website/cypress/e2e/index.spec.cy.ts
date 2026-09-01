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

  it('collapses a submenu when keyboard focus leaves its navigation header', () => {
    const menuButton = '[data-testid="nav-button-trials-case-management"]'
    const menuList = '[data-testid="nav-list-trials-case-management"]'

    cy.get(menuButton).focus().realPress('Enter')
    cy.get(menuButton).should('have.attr', 'aria-expanded', 'true')
    cy.get(menuList).should('be.visible')
    cy.get(`${menuList} a`).last().focus().realPress('Tab')

    cy.get(menuList).should('not.be.visible')
    cy.get(menuButton).should('have.attr', 'aria-expanded', 'false')
  })

  it('resets aria-expanded when a keyboard-opened submenu is closed with Escape', () => {
    const menuButton = '[data-testid="nav-button-trials-case-management"]'
    const menuList = '[data-testid="nav-list-trials-case-management"]'

    // Open the submenu via keyboard so toggleMenuItems sets aria-expanded="true"
    cy.get(menuButton).focus().realPress('Enter')
    cy.get(menuButton).should('have.attr', 'aria-expanded', 'true')
    cy.get(menuList).should('be.visible')

    // Close it with Escape
    cy.get(menuButton).realPress('Escape')

    // The submenu is visually collapsed...
    cy.get(menuList).should('not.be.visible')
    // ...but the button must not still advertise itself as expanded.
    cy.get(menuButton).should('have.attr', 'aria-expanded', 'false')
  })

  it('resets aria-expanded when a keyboard-opened submenu is closed by clicking outside the nav', () => {
    const menuButton = '[data-testid="nav-button-trials-case-management"]'
    const menuList = '[data-testid="nav-list-trials-case-management"]'

    cy.get(menuButton).focus().realPress('Enter')
    cy.get(menuButton).should('have.attr', 'aria-expanded', 'true')
    cy.get(menuList).should('be.visible')

    // Click somewhere outside .navigation-bar (the federal banner sits above the nav)
    cy.get('[data-testid="usa-banner"]').click()

    cy.get(menuList).should('not.be.visible')
    cy.get(menuButton).should('have.attr', 'aria-expanded', 'false')
  })

  it('header dropdown nav buttons expose exactly the section title as aria-label', () => {
    cy.get('li.navigation-header > button.link').each(($button) => {
      const sectionTitle = $button.find('span').first().text().trim()
      expect(sectionTitle, 'section title text should be present').to.not.equal('')
      expect($button.attr('aria-label')).to.equal(sectionTitle)

      const spans = $button.children('span')
      expect(spans.length, 'button should have inner spans').to.be.greaterThan(0)
      spans.each((_, span) => {
        expect(span.getAttribute('aria-hidden')).to.equal('true')
      })
    })
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

  it('has DAWSON login link in the header pointing to the DAWSON login page', () => {
    cy.get('[data-testid="header-dawson-login-link"]')
      .should('exist')
      .and('be.visible')
      .and('have.attr', 'href', 'https://app.dawson.ustaxcourt.gov/login')
      .and('have.attr', 'target', '_blank')
      .and('have.attr', 'rel', 'noopener noreferrer')
  })

  it('has DAWSON login link visible on mobile viewport', () => {
    cy.viewport('iphone-x')
    cy.visit('/')
    cy.get('[data-testid="header-dawson-login-link"]')
      .should('exist')
      .and('be.visible')
      .and('have.attr', 'href', 'https://app.dawson.ustaxcourt.gov/login')
  })

  it('search buttons contain text or title attribute for accessibility', () => {
    cy.get('[data-testid="search-button"]').should(($button) => {

      expect($button).to.have.length(3) //checking that home page has three search buttons
      expect($button.eq(0).attr('aria-label')).to.contain('Search') //test tablet search box (icon-only, uses aria-label)
      expect($button.eq(1).attr('aria-label')).to.contain('Search') //test desktop search box (icon-only, uses aria-label)
      expect($button.eq(2).attr('title')).to.contain('Search') //test mobile search box
    });
  })
})
