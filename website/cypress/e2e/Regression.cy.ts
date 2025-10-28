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

    cy.get('[href="/dawson/"] > .nav-card > h2').should('be.visible');
    cy.get('[href="/dawson/"] > .nav-card > h2').click();
    cy.get('.display-none').click();
    cy.get('[href="/petitioners-start/"] > .nav-card > h2').should('be.visible');
    cy.get('[href="/petitioners-start/"] > .nav-card > h2').click();
    cy.get('.display-none').click();
    cy.get('[aria-label="DAWSON Case Management"] > .nav-card > h2').should('be.visible');
    cy.get('[aria-label="DAWSON Case Management"] > .nav-card > h2').click();
    cy.get('[href="/rules/"] > .nav-card > p').should('be.visible');
    cy.get('[href="/rules/"] > .nav-card > p').click();
    cy.get('.display-none').click();
    cy.get('[href="https://dev.ef-cms.ustaxcourt.gov/todays-opinions"] > .nav-card > h2').should('be.visible');
    cy.get('[href="https://dev.ef-cms.ustaxcourt.gov/todays-opinions"] > .nav-card > h2').click();
    cy.get('[href="https://dev.ef-cms.ustaxcourt.gov/todays-orders"] > .nav-card > h2').should('be.visible');
    cy.get('[href="https://dev.ef-cms.ustaxcourt.gov/todays-orders"] > .nav-card > h2').click();
    cy.get('[href="/practitioners/"] > .nav-card > h2').should('be.visible');
    cy.get('[href="/practitioners/"] > .nav-card > h2').click();
    cy.get('.display-none').click();
    cy.get('[href="/case-related-forms/"] > .nav-card > h2').should('be.visible');
    cy.get('[href="/case-related-forms/"] > .nav-card').click();
    cy.get('#logo-link > .display-none').click();
    cy.get('[href="https://dev.ef-cms.ustaxcourt.gov/trial-sessions"] > .nav-card > p').should('be.visible');
    cy.get('[href="https://dev.ef-cms.ustaxcourt.gov/trial-sessions"] > .nav-card').click();
    cy.get('.wide-nav-card > h2').should('have.text', 'Find a Case, Order, Opinion or Practitioner');
    cy.get('.wide-nav-card > h2').should('be.visible');
    cy.get('.wide-nav-card > h2').click();
  
  });

  it('Search Bar', function() {
    cy.visit('/');

    cy.get('#desktop-search-form > [data-testid="search-input"]').click();
    cy.get('#desktop-search-form > [data-testid="search-input"]').should('have.attr', 'type', 'text');
    cy.get('#desktop-search-form > [data-testid="search-input"]').should('have.attr', 'data-testid', 'search-input');
    cy.get('#desktop-search-form > [data-testid="search-input"]').click();
    cy.get('#desktop-search-form > [data-testid="search-input"]').should('be.visible');
    cy.get('#desktop-search-form > [data-testid="search-input"]').should('be.enabled');
    cy.get('#desktop-search-form > [data-testid="search-button"]').should('have.text', '\n                            \n                            Search\n                        ');
    cy.get('#desktop-search-form > [data-testid="search-button"]').should('be.visible');
    cy.get('#desktop-search-form > [data-testid="search-button"]').should('be.enabled');
    cy.get('#desktop-search-form > [data-testid="search-input"]').clear('j');
    cy.get('#desktop-search-form > [data-testid="search-input"]').type('judge');
    cy.get('#desktop-search-form > [data-testid="search-button"]').click();
    cy.get('.pagination > a').click();
    cy.get('[href="/search/?query=judge&page=1"]').click();
    cy.get(':nth-child(1) > h2 > a').click();
  
  });

  it('Header', function() {
    cy.visit('/');

    cy.get('.display-none').should('have.class', 'tablet:display-block');
    cy.get('.display-none').should('have.attr', 'alt', 'US Tax Court Logo');
    cy.get('.display-none').should('be.visible');
    cy.get('.display-none').click();
    cy.get('.dawson-link > .dawson').should('have.class', 'dawson');
    cy.get('.dawson-link > .dawson').should('have.attr', 'alt', 'Dawson Logo');
    cy.get('.dawson-link > .dawson').should('be.visible');
    cy.get('.dawson-link > .dawson').click();
    cy.get('.usa-banner__header-text').should('have.text', 'An official website of the United States government');
    cy.get('.usa-banner__header-text').should('have.class', 'usa-banner__header-text');
    cy.get('.usa-banner__header-text').should('be.visible');
    cy.get('.usa-banner__button-text').should('have.text', 'Here’s how you know');
    cy.get('.usa-banner__button-text').should('have.class', 'usa-banner__button-text');
    cy.get('.usa-banner__button-text').should('be.visible');
    cy.get('.usa-banner__button-text').click();
    cy.get(':nth-child(1) > .usa-media-block__body > p > :nth-child(1)').should('have.text', 'Official websites use .gov');
    cy.get(':nth-child(1) > .usa-media-block__body > p').should('have.text', '\n                            Official websites use .gov\n                            \n                            A\n                            .gov website belongs to an official government organization in the United States.\n                        ');
    cy.get(':nth-child(1) > .usa-media-block__body > p').should('be.visible');
    cy.get(':nth-child(2) > .usa-media-block__body > p > :nth-child(1)').should('have.text', 'Secure .gov websites use HTTPS');
    cy.get(':nth-child(2) > .usa-media-block__body > p > :nth-child(1)').should('be.visible');
    cy.get(':nth-child(2) > .usa-media-block__body > p').should('be.visible');
    cy.get('.alert-content > p').should('have.text', '\n            This is a testing site for the U.S. Tax Court and not intended for public use.  To learn more about starting a case, visit the U.S. Tax Court website.\n        ');
    cy.get('.alert-content > p').should('be.visible');
    cy.get('.alert-content > p > a').should('have.text', 'U.S. Tax Court website.');
    cy.get('.alert-content > p > a').should('have.attr', 'href', 'https://www.ustaxcourt.gov/');
    cy.get('.alert-content > p > a').should('be.visible');
    cy.get('.alert-content > p > a').click();
    cy.get('.close-btn > img').should('have.attr', 'src', 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path d="M19 6.41 17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>');
    cy.get('.give-feedback-btn').should('have.text', '\n    Give Feedback\n');
    cy.get('.give-feedback-btn').should('have.class', 'give-feedback-btn');
    cy.get('.give-feedback-btn').should('have.attr', 'href', 'https://forms.office.com/r/45R5iAguPG');
    cy.get('.give-feedback-btn').should('be.visible');
    cy.get('.give-feedback-btn').click();
  
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
    cy.get('.seal').should('have.class', 'seal');
    cy.get('.seal').should('have.attr', 'src', '/static/images/footer/ustc-seal.svg');
    cy.get('.seal').should('be.visible');
    cy.get('.font-heading').should('have.text', 'United States Tax Court\n                            \n                                \n                                    400 Second Street, NW\n                                    Washington, DC 20217\n                                \n                            \n                    ');
    cy.get('.font-heading').should('have.class', 'font-heading');
    cy.get('.font-heading > a > span').should('be.visible');
    cy.get('.seal').click();
    cy.get('.court-hours').should('have.text', 'Tax Court Hours of Operation:');
    cy.get('.court-hours').should('have.class', 'court-hours');
    cy.get('.court-hours').should('be.visible');
    cy.get('.footer-time-container > p').should('have.text', ' Tax Court Hours of Operation: 8 a.m. to 4:30 p.m. (EST)\n                 on all days except Saturdays, Sundays, and\n                  legal holidays \n                    in the District of Columbia.\n                ');
    cy.get('.footer-time-container > p').should('be.visible');
    cy.get('.footer-time-container > p > a > span').should('have.text', 'legal holidays');
    cy.get('.footer-time-container > p > a > span').should('have.attr', 'style', 'text-decoration: underline; color:white;');
    cy.get('.footer-time-container > p > a > span').should('be.visible');
    cy.get(':nth-child(3) > p').should('have.text', '\n                        (202) 521-0700\n                        All rights reserved\n                        Build: 31e73f7\n                    ');
    cy.get(':nth-child(3) > p').should('be.visible');
    cy.get('.footer-address > .grid-container > .content').click();
    cy.get(':nth-child(3) > [href="https://dawson.ustaxcourt.gov/"] > .dawson').should('have.class', 'dawson');
    cy.get(':nth-child(3) > [href="https://dawson.ustaxcourt.gov/"] > .dawson').should('have.attr', 'src', '/static/images/footer/dawson-logo.svg');
    cy.get(':nth-child(3) > [href="https://dawson.ustaxcourt.gov/"] > .dawson').should('be.visible');
    cy.get(':nth-child(3) > [href="https://dawson.ustaxcourt.gov/"] > .dawson').click();
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
})
