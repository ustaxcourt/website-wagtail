const XLSX_PATH = 'home/migrations/0116_create_redirects_for_broken_pdf_links.xlsx';

function isEquivalentDocumentRedirect(actual: string, expected: string): boolean {
    if (actual === expected) {
        return true;
    }

    const expectedMatch = expected.match(/^\/files\/documents\/([^/?#]+)$/i);
    const actualMatch = actual.match(/^\/documents\/\d+\/([^/?#]+)$/i);
    if (!expectedMatch || !actualMatch) {
        return false;
    }

    return decodeURIComponent(actualMatch[1]).toLowerCase() === decodeURIComponent(expectedMatch[1]).toLowerCase();
}

describe('WAG-1222 broken PDF link redirects', () => {
    let redirects: { from: string; to: string }[] = [];

    before(() => {
        cy.task('getRedirectsFromXlsx', XLSX_PATH).then((data) => {
            redirects = (data as { from: string; to: string }[]).map(({ from, to }) => ({
                from: from.trim(),
                to: to.trim(),
            }));
        });
    });

    it('verifies each redirect occurs and the destination is not 404', () => {
        expect(redirects, 'redirects loaded from spreadsheet').to.have.length.greaterThan(0);

        cy.then(() => {
            redirects.forEach(({ from, to }) => {
                cy.request({ url: from, followRedirect: false }).then((response) => {
                    expect(response.status, `${from} should return 301`).to.eq(301);

                    const location = response.headers['location'] as string | undefined;
                    expect(location, `${from} should include a Location header`).to.exist;
                    const matchesExpected = location ? isEquivalentDocumentRedirect(location, to) : false;
                    expect(matchesExpected, `${from} should redirect to expected destination`).to.eq(true);

                    if (!location || location.startsWith('/files/documents/') || location.startsWith('/documents/')) {
                        return;
                    }

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
