describe('Tax Court Website Regression', () => {
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
})
