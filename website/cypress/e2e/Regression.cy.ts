describe('Tax Court Website Menu Bar', () => {
  it('passes', () => {
    cy.visit('/')
    cy.get('[data-testid="nav-link-mission"]').click({ force: true });
    cy.get('[data-testid="nav-link-history"]').click({ force: true });
    cy.get('[data-testid="nav-link-reports-statistics"]').click({ force: true });
    cy.get('[data-testid="nav-link-judges"]').click({ force: true });
    cy.get('[data-testid="nav-link-directory"]').click({ force: true });
    cy.get('[data-testid="nav-link-trial-sessions"]').click({ force: true });
    cy.get('[data-testid="nav-link-fees-charges"]').click({ force: true });
    cy.get('[data-testid="nav-link-employment"]').click({ force: true });
    cy.get('[data-testid="nav-link-press-releases-news"]').click({ force: true });
    cy.get('[data-testid="nav-link-remote-proceedings"]').click({ force: true });
    cy.get('[data-testid="nav-link-administrative-orders"]').click({ force: true });
    cy.get('[data-testid="nav-link-tax-court-rules"]').click({ force: true });
    cy.get('[data-testid="nav-link-guidance-for-petitioners"]').click({ force: true });
    cy.get('[data-testid="nav-link-clinics-pro-bono-programs"]').click({ force: true });
    cy.get('[data-testid="nav-link-guidance-for-practitioners"]').click({ force: true });
    cy.get('[data-testid="nav-link-todays-opinions"]').click({ force: true });
    cy.get('[data-testid="nav-link-todays-orders"]').click({ force: true });
    cy.get(':nth-child(3) > [data-testid="nav-link-search-case-order-opinion-practitioner"]').click({ force: true });
    cy.get('[data-testid="nav-link-citation-style-manual"]').click({ force: true });
    cy.get('[data-testid="nav-link-transcripts-copies"]').click({ force: true });
    cy.get('[data-testid="nav-link-tax-court-reports-pamphlets"]').click({ force: true });
    cy.get(':nth-child(1) > [data-testid="nav-link-search-case-order-opinion-practitioner"]').click({ force: true });
    cy.get('[data-testid="nav-link-dawson-efiling-system"]').click({ force: true });
    cy.get('[data-testid="nav-link-case-related-forms"]').click({ force: true });

  })

  it('Tax Court Quick Access Tiles', function() {

    cy.visit('/');
    cy.get('[href="/dawson/"] > .nav-card > h2').click();
    cy.get('.desktop-header-logo-section > #logo-link > .logo-seal').click();
    cy.get('[href="/petitioners-start/"] > .nav-card > h2').click();
    cy.get('.desktop-header-logo-section > #logo-link > .logo-seal').click();
    cy.get('[aria-label="DAWSON Case Management"] > .nav-card > h2').click();
    cy.get('[href="/rules/"] > .nav-card > h2').click();
    cy.get('.desktop-header-logo-section > #logo-link > .logo-seal').click();
    cy.get('[href="https://dev.ef-cms.ustaxcourt.gov/todays-opinions"] > .nav-card > h2').click();
    cy.get('[href="https://dev.ef-cms.ustaxcourt.gov/todays-orders"] > .nav-card > h2').click();
    cy.get('[href="/practitioners/"] > .nav-card > h2').click();
    cy.get('.desktop-header-logo-section > #logo-link > .logo-seal').click();
    cy.get('[href="/case-related-forms/"] > .nav-card').click();
    cy.get('.desktop-header-logo-section > #logo-link > .logo-seal').click();
    cy.get('[href="https://dev.ef-cms.ustaxcourt.gov/trial-sessions"] > .nav-card > .icon > svg').click();
    cy.get('.wide-nav-card > h2').click();

  });

  it('Tax Court Search Bar', function() {

    cy.visit('/');
    cy.get('#tablet-search-form > [data-testid="search-input"]').clear('j');
    cy.get('#tablet-search-form > [data-testid="search-input"]').type('judge');
    cy.get('#tablet-search-form > [data-testid="search-button"]').click();
    cy.get('.pagination > a').click();
    cy.get(':nth-child(1) > h2 > a').click();
    cy.get('#tablet-search-form > [data-testid="search-input"]').click();
    cy.get('#tablet-search-form > [data-testid="search-input"]').should('be.visible');
    cy.get('#tablet-search-form > [data-testid="search-button"]').should('have.text', '\n                                    \n                                    Search\n                                ');
    cy.get('#tablet-search-form > [data-testid="search-button"]').should('be.visible');
    cy.get('#tablet-search-form > [data-testid="search-button"]').should('be.enabled');
    cy.get('#tablet-search-form > [data-testid="search-input"]').click();

  });

  it('Tax Court Header', function() {
    cy.visit('/');
    cy.get('.logo-content > .logo-heading').should('have.text', 'United States Tax Court');
    cy.get('.logo-subheadings > :nth-child(1) > :nth-child(1)').should('have.text', 'Patrick J. Urda, Chief Judge');
    cy.get('.logo-subheadings > :nth-child(1) > :nth-child(1)').should('have.class', 'logo-subheading');
    cy.get('.logo-subheadings > :nth-child(1) > :nth-child(2)').should('have.text', 'Charles G. Jeane, Clerk of the Court');
    cy.get('.logo-subheadings > :nth-child(1) > :nth-child(2)').should('have.class', 'logo-subheading');
    cy.get('.logo-subheadings > :nth-child(1) > :nth-child(1)').should('be.visible');
    cy.get('.logo-subheadings > :nth-child(1) > :nth-child(2)').should('be.visible');
    cy.get('.desktop-header-logo-section > #logo-link > .logo-seal').should('have.class', 'logo-seal');
    cy.get('.desktop-header-logo-section > #logo-link > .logo-seal').should('have.attr', 'src', '/static/images/header/logo_seal.782be2b36569.webp');
    cy.get('.logo-content > .logo-heading').should('be.visible');

  });


  it('Tax Court Warning about Tax Scams', function() {
    cy.visit('/');
    cy.get('.entry > h2').should('have.text', 'U.S. Tax Court Warning about Tax Scams');
    cy.get('.entry > h2').should('be.visible');
    cy.get('[data-block-key="wffhy"]').should('have.attr', 'data-block-key', 'wffhy');
    cy.get('[data-block-key="wffhy"]').should('be.visible');
    cy.get('[data-block-key="mnfk5"]').should('have.attr', 'data-block-key', 'mnfk5');
    cy.get('[data-block-key="mnfk5"]').should('be.visible');
    cy.get('[data-block-key="kytzu"]').should('have.attr', 'data-block-key', 'kytzu');
    cy.get('[data-block-key="kytzu"]').should('be.visible');
    cy.get('[data-block-key="ykqkn"]').should('have.attr', 'data-block-key', 'ykqkn');
    cy.get('[data-block-key="ykqkn"]').should('be.visible');
    cy.get('[data-block-key="zdoou"]').should('have.attr', 'data-block-key', 'zdoou');
    cy.get('[data-block-key="zdoou"]').should('be.visible');
    cy.get('[data-block-key="2jsoc"]').should('have.attr', 'data-block-key', '2jsoc');
    cy.get('[data-block-key="2jsoc"]').should('be.visible');
    cy.get('[href="https://www.irs.gov/newsroom/tax-scams-consumer-alerts"]').should('have.attr', 'href', 'https://www.irs.gov/newsroom/tax-scams-consumer-alerts');
    cy.get('[href="https://www.irs.gov/newsroom/tax-scams-consumer-alerts"]').click();
    cy.get('[href="https://www.ftc.gov"]').should('have.attr', 'href', 'https://www.ftc.gov');
    cy.get('[href="https://www.ftc.gov"]').should('be.visible');
    cy.get('[href="https://www.ftc.gov"]').click();
    cy.get('[href="https://www.ic3.gov"]').should('have.attr', 'href', 'https://www.ic3.gov');
    cy.get('[href="https://www.ic3.gov"]').should('be.visible');
    cy.get('[href="https://www.ic3.gov"]').click();
    cy.get('[data-block-key="r4mim"]').should('have.attr', 'data-block-key', 'r4mim');
    cy.get('[data-block-key="r4mim"]').should('be.visible');
  });

  it('Tax Court Questions?', function() {
    cy.visit('/');
    cy.get('.grid-col-12 > h2').should('have.text', 'Questions?');
    cy.get('.grid-col-12 > h2').should('be.visible');
    cy.get('[data-block-key="m2xtc"]').should('have.attr', 'data-block-key', 'm2xtc');
    cy.get('[data-block-key="m2xtc"]').should('be.visible');
    cy.get('[href="/dawson"]').click();
    cy.get('.desktop-header-logo-section > #logo-link > .logo-seal').click();
    cy.get('[data-block-key="m2xtc"]').click();

  });
})
