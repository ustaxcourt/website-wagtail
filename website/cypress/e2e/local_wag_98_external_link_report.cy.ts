describe('WAG-98 External Links Report', () => {
    const ADMIN_USERNAME = Cypress.env('ADMIN_USERNAME') || 'admin';
    const ADMIN_PASSWORD = Cypress.env('ADMIN_PASSWORD') || 'ustcAdminPW!';

    const testPageSlug = 'external-links-report-test'
    const testPageUrl = '/'+testPageSlug+'/'
    const externalLinksReportUrl = '/admin/reports/external-links/'

    before(() => {
        //Create the test page used by this test if it does not already exist
        cy.exec('. ../.venv/bin/activate && python manage.py create_external_links_report_test_page')
    });

    after(() => {
        //Delete the test page used by this test case
        cy.exec('. ../.venv/bin/activate && python manage.py create_external_links_report_test_page --delete');
    });

    it('verifies that the external links in the External Links Test Page appear in the External Links Report', () => {
        //Verify that the test page exists and can be accessed
        cy.request({ url: testPageUrl, followRedirect: false }).then((response) => {
            expect(response.status, `${testPageUrl} should return 200`).to.eq(200);
        });

        //Access the External Links Report and verify the following:
        cy.adminLogin(ADMIN_USERNAME, ADMIN_PASSWORD);
        cy.visit(externalLinksReportUrl);
        // - The test page verified above shows up in the report
        cy.get('#'+testPageSlug).should(($tr) => {expect($tr).to.have.length(1)});
        // - The test page's row in report has 21 rows in the subtable
        // - None of the rows in the subtable for the test page contain the word "internal" (there are a few instances
        //      of the word "internal" associated with internal links on the test page that should not appear in this
        //      report)
        cy.get('#'+testPageSlug).first().within(($testPageRowInReport) => {
            cy.get("tr").should(($rowsForTestPage) => {
                expect($rowsForTestPage).to.have.length(21);
                expect($rowsForTestPage).to.not.contain("internal");
            });
        })
    });
});
