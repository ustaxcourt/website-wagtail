describe('Homepage redesign', () => {
  it('Menu Bar', () => {
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

  it('Quick Access Tiles', function() {
    cy.visit('/');

    /* ==== Generated with Cypress Studio ==== */
    cy.get('[href="/dawson/"] > .nav-card').should('have.class', 'nav-card');
    cy.get('[href="/dawson/"] > .nav-card').should('be.visible');
    cy.get('[href="/petitioners-start/"] > .nav-card').should('have.class', 'nav-card');
    cy.get('[href="/petitioners-start/"] > .nav-card').should('be.visible');
    cy.get('[aria-label="DAWSON Case Management"] > .nav-card').should('have.class', 'nav-card');
    cy.get('[aria-label="DAWSON Case Management"] > .nav-card').should('be.visible');
    cy.get('[href="/rules/"] > .nav-card').should('have.class', 'nav-card');
    cy.get('[href="/rules/"] > .nav-card').should('be.visible');
    cy.get('[href="https://dev.ef-cms.ustaxcourt.gov/todays-opinions"] > .nav-card').should('have.class', 'nav-card');
    cy.get('[href="https://dev.ef-cms.ustaxcourt.gov/todays-opinions"] > .nav-card').should('be.visible');
    cy.get('[href="https://dev.ef-cms.ustaxcourt.gov/todays-orders"] > .nav-card').should('have.class', 'nav-card');
    cy.get('[href="https://dev.ef-cms.ustaxcourt.gov/todays-orders"] > .nav-card').should('be.visible');
    cy.get('[href="/practitioners/"] > .nav-card').should('have.class', 'nav-card');
    cy.get('[href="/practitioners/"] > .nav-card').should('be.visible');
    cy.get('[href="/case-related-forms/"] > .nav-card').should('have.class', 'nav-card');
    cy.get('[href="/case-related-forms/"] > .nav-card').should('be.visible');
    cy.get('[href="https://dev.ef-cms.ustaxcourt.gov/trial-sessions"] > .nav-card').should('have.class', 'nav-card');
    cy.get('[href="https://dev.ef-cms.ustaxcourt.gov/trial-sessions"] > .nav-card').should('be.visible');
    cy.get('.wide-nav-card').should('have.class', 'wide-nav-card');
    cy.get('.wide-nav-card').should('be.visible');
    /* ==== End Cypress Studio ==== */
  });

  it('Search Bar', function() {
    cy.visit('/');

    /* ==== Generated with Cypress Studio ==== */
    cy.get('#tablet-search-form > [data-testid="search-input"]').should('have.attr', 'name', 'query');
    cy.get('#tablet-search-form > [data-testid="search-input"]').should('be.visible');
    cy.get('#tablet-search-form > [data-testid="search-input"]').should('be.enabled');
    cy.get('#tablet-search-form > [data-testid="search-input"]').should('not.be.checked');
    cy.get('#tablet-search-form > [data-testid="search-button"]').should('have.text', '\n                                    \n                                    Search\n                                ');
    cy.get('#tablet-search-form > [data-testid="search-button"]').should('have.attr', 'type', 'submit');
    cy.get('#tablet-search-form > [data-testid="search-button"]').should('be.visible');
    cy.get('#tablet-search-form > [data-testid="search-button"]').should('be.enabled');
    cy.get('#tablet-search-form > [data-testid="search-input"]').clear('j');
    cy.get('#tablet-search-form > [data-testid="search-input"]').type('j');
    cy.get('#tablet-search-form > [data-testid="search-button"]').click();
    cy.get('.pagination > a').click();
    cy.get(':nth-child(1) > h2 > a').click();
    /* ==== End Cypress Studio ==== */
  });

  it('Header', function() {
    cy.visit('/');

    /* ==== Generated with Cypress Studio ==== */
    cy.get('.desktop-header-logo-section > #logo-link > .logo-seal').should('have.class', 'logo-seal');
    cy.get('.desktop-header-logo-section > #logo-link > .logo-seal').should('be.visible');
    cy.get('.logo-content > .logo-heading').should('have.text', 'United States Tax Court');
    cy.get('.logo-content > .logo-heading').should('have.class', 'logo-heading');
    cy.get('.logo-content > .logo-heading').should('have.attr', 'href', '/');
    cy.get('.logo-content > .logo-heading').should('be.visible');
    cy.get('.logo-subheadings > :nth-child(1) > :nth-child(1)').should('have.text', 'Patrick J. Urda, Chief Judge');
    cy.get('.logo-subheadings > :nth-child(1) > :nth-child(1)').should('have.class', 'logo-subheading');
    cy.get('.logo-subheadings > :nth-child(1) > :nth-child(1)').should('be.visible');
    cy.get('.logo-subheadings > :nth-child(1) > :nth-child(2)').should('have.text', 'Charles G. Jeane, Clerk of the Court');
    cy.get('.logo-subheadings > :nth-child(1) > :nth-child(2)').should('have.class', 'logo-subheading');
    cy.get('.logo-subheadings > :nth-child(1) > :nth-child(2)').should('be.visible');
    /* ==== End Cypress Studio ==== */
  })

  it('Warning about Tax Scams', function() {
    cy.visit('/');
    cy.get('[href="https://reportfraud.ftc.gov/"]').should('have.text', 'Federal Trade Commission ');
    cy.get('[href="https://reportfraud.ftc.gov/"]').should('have.attr', 'href', 'https://reportfraud.ftc.gov/');
    cy.get('[href="https://reportfraud.ftc.gov/"]').click();
    cy.get('[href="https://www.ic3.gov/"]').should('have.text', 'Federal Bureau of Investigation');
    cy.get('[href="https://www.ic3.gov/"]').should('have.attr', 'href', 'https://www.ic3.gov/');
    cy.get('[href="https://www.ic3.gov/"]').click();

  });

  it('Questions?', function() {
    cy.visit('/');
    cy.get('.grid-col-12 > h2').should('be.visible');
    cy.get('.grid-col-12 > p').should('have.text', '\n                        For assistance with DAWSON, the Court\'s Electronic Filing and Case Management System, refer to the DAWSON page or email  dawson.support@ustaxcourt.gov.Be sure to include your case docket number in your email. For all other questions contact the Office of the Clerk of Court at (202) 521-0700.\n                    ');
    cy.get('.grid-col-12 > p').should('be.visible');
    cy.get('[href="/dawson"]').should('have.text', 'DAWSON');
    cy.get('[href="/dawson"]').should('have.attr', 'href', '/dawson');
    cy.get('[href="/dawson"]').should('be.visible');
    cy.get('[href="/dawson"]').click();
    cy.get('[href="mailto:dawson.support@ustaxcourt.gov?subject=Assistance%20for%20Dawson"]').should('have.text', ' dawson.support@ustaxcourt.gov');
    cy.get('[href="mailto:dawson.support@ustaxcourt.gov?subject=Assistance%20for%20Dawson"]').should('have.attr', 'href', 'mailto:dawson.support@ustaxcourt.gov?subject=Assistance%20for%20Dawson');
    cy.get('[style="text-decoration: underline;"]').should('have.text', '202) 521-0700');
    cy.get('[style="text-decoration: underline;"]').should('have.attr', 'href', 'tel:+2025210700');
    cy.get('[style="text-decoration: underline;"]').should('be.visible');
  
  });

  it('Footer', function() {
    cy.visit('/');

    /* ==== Generated with Cypress Studio ==== */
    cy.get('.seal').should('have.class', 'seal');
    cy.get('.seal').should('be.visible');

    cy.get('.font-heading').should(
      'have.text',
      '\n                            United States Tax Court\n                            \n                            \n                                \n                                    400 Second Street, NW\n                                    \n                                    Washington, DC 20217\n                                \n                            \n                        '
    );

    cy.get('.font-heading').should('have.class', 'font-heading');
    cy.get('.font-heading').should('be.visible');
    cy.get('.footer-time-container > p').should('have.text', '\n                        Tax Court Hours of Operation: 8 a.m. to 4:30 p.m. (EST)\n                        on all days except Saturdays, Sundays, and\n                         legal holidays \n                        in the District of Columbia.\n                    ');
    cy.get('.footer-time-container > p').should('be.visible');
    cy.get('.phone').should('have.text', '202) 521-0700');
    cy.get('.phone').should('be.visible');
    cy.get(':nth-child(3) > p').should('be.visible');
    cy.get('.dawson').should('have.class', 'dawson');
    cy.get('.dawson').should('be.visible');
    cy.get('.dawson').click();
    cy.get('.give-feedback-btn').should('have.text', 'Give Feedback');
    cy.get('.give-feedback-btn').should('have.attr', 'href', 'https://forms.office.com/r/45R5iAguPG');
    cy.get('.give-feedback-btn').should('be.visible');
    cy.get('.give-feedback-btn').click();
    /* ==== End Cypress Studio ==== */
  });

  describe('Banner expiration test', () => {
const bannerSelector = '[data-testid=".alert-text"]'; // Adjust to match your app
const pageUrl = '/'; // Replace with your target page
beforeEach(() => {
 cy.visit('/');
});

it('should not display the banner after expiration date', () => {
 // Verify that the banner does not exist in the DOM
 cy.get('body').then(($body) => {
   if ($body.find('.alert-text').length > 0) {
     // If the banner element exists, fail the test
     cy.get('.alert-text').should('not.be.visible');
   } else {
     // If it doesn't exist at all, that’s expected
     cy.log('✅ Banner element not found — it has expired as expected.');
     }
 });
});
});

  it('should not display banner after expiration', () => {
   // Mock current date to a time *after* expiration
   const expiredDate = new Date('2025-10-28T00:00:00Z'); // Adjust date as needed
   cy.clock(expiredDate);
   cy.visit('/');
   cy.get('.alert-text').should('not.exist');

  });

  /* ==== Test Created with Cypress Studio ==== */
  it('New and Notices', function() {
    /* ==== Generated with Cypress Studio ==== */
    cy.visit('/');
    cy.get(':nth-child(1) > .news-card-image').should('have.class', 'news-card-image');
    cy.get(':nth-child(1) > .news-card-image').should('be.visible');
    cy.get(':nth-child(1) > .news-card-content').should('have.class', 'news-card-content');
    cy.get(':nth-child(1) > .news-card-content').should('be.visible');
    cy.get(':nth-child(1) > .news-card-content > .news-card-link').should('have.text', 'See the Press Release.');
    cy.get(':nth-child(1) > .news-card-content > .news-card-link').should('have.class', 'news-card-link');
    cy.get(':nth-child(1) > .news-card-content > .news-card-link').should('be.visible');
    cy.get(':nth-child(2) > .news-card-image').should('have.class', 'news-card-image');
    cy.get(':nth-child(2) > .news-card-image').should('be.visible');
    cy.get(':nth-child(2) > .news-card-content').should('have.class', 'news-card-content');
    cy.get(':nth-child(2) > .news-card-content').should('be.visible');
    cy.get(':nth-child(2) > .news-card-content > .news-card-link').should('have.text', 'See the Press Release.');
    cy.get(':nth-child(2) > .news-card-content > .news-card-link').should('have.class', 'news-card-link');
    cy.get(':nth-child(2) > .news-card-content > .news-card-link').should('have.attr', 'href', '/documents/104/04072025.pdf');
    cy.get(':nth-child(2) > .news-card-content > .news-card-link').should('be.visible');
    cy.get(':nth-child(3) > .news-card-image').should('have.class', 'news-card-image');
    cy.get(':nth-child(3) > .news-card-image').should('be.visible');
    cy.get(':nth-child(3) > .news-card-content').should('have.class', 'news-card-content');
    cy.get(':nth-child(3) > .news-card-content').should('be.visible');
    cy.get(':nth-child(3) > .news-card-content > .news-card-link').should('have.class', 'news-card-link');
    cy.get(':nth-child(3) > .news-card-content > .news-card-link').should('have.text', 'See the Press Release.');
    cy.get(':nth-child(3) > .news-card-content > .news-card-link').should('be.visible');
    /* ==== End Cypress Studio ==== */
  });

  });
