describe('WAG-98 External Links Report', () => {
    const ADMIN_USERNAME = Cypress.env('ADMIN_USERNAME') || 'admin';
    const ADMIN_PASSWORD = Cypress.env('ADMIN_PASSWORD') || 'ustcAdminPW!';

    const testPageSlug = 'external-links-report-test'
    const testPageUrl = '/'+testPageSlug+'/'
    const externalLinksReportUrl = '/admin/reports/external-links/'

    it('verifies that the external links in the External Links Test Page appear in the External Links Report', () => {
        cy.exec('. ../.venv/bin/activate && python manage.py create_external_links_report_test_page').then((result) =>
        {
            cy.request({ url: testPageUrl, followRedirect: false }).then((response) => {
                expect(response.status, `${testPageUrl} should return 200`).to.eq(200);
            });

            cy.adminLogin(ADMIN_USERNAME, ADMIN_PASSWORD);

            cy.visit(externalLinksReportUrl);
            cy.get('#'+testPageSlug).should(($tr) => {expect($tr).to.have.length(1)});
            cy.get('#'+testPageSlug).first().within(($testPageRowInReport) => {
                cy.get("tr").should(($rowsForTestPage) => {
                    expect($rowsForTestPage).to.have.length(21);
                    expect($rowsForTestPage).to.not.contain("internal");
                });
            })
        }).then((result) => {
            cy.exec('. ../.venv/bin/activate && python manage.py create_external_links_report_test_page --delete');
        })
    });
});
