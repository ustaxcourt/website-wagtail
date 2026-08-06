// Named local_* so it's excluded from the default e2e-coverage/test-e2e run: the
// redirect destinations are real production documents that a freshly migrated/seeded
// test database doesn't have, so run this manually (e.g. via test-e2e-aws) against an
// environment with real document media.
const XLSX_PATH = 'home/migrations/0116_create_redirects_for_broken_pdf_links.xlsx';

describe('WAG-1222 broken PDF link redirects', () => {
    let fromUrls: string[];

    before(() => {
        cy.task('getRedirectsFromXlsx', XLSX_PATH).then((data) => {
            fromUrls = (data as { from: string; to: string }[]).map((r) => r.from);
        });
    });

    it('verifies each redirect occurs and the destination is not 404', () => {
        cy.wrap(null).then(() => {
            fromUrls.forEach((from) => {
                cy.request({ url: from, followRedirect: false }).then((response) => {
                    expect(response.status, `${from} should return 301`).to.eq(301);

                    const location = response.headers['location'] as string;
                    if (!location.startsWith('http')) {
                        cy.request({ url: location, failOnStatusCode: false }).then((destResponse) => {
                            expect(destResponse.status, `${location} should not be 404`).to.not.eq(404);
                        });
                    }
                });
            });
        });
    });
});
