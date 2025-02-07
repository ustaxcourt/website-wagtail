import {checkA11y, checkHeaderOrder, checkHeaderStyles} from "../../support/commands";

describe('Case Related Forms Page', () => {
    it('Verify the documents are displayed, clickable, and check accessibility & header consistency', function () {
        cy.visit('/case_related_forms/');

        checkA11y();
        checkHeaderOrder();
        checkHeaderStyles();

        const documentLink = cy.get('a[data-testid="Application for Order to Take Deposition to Perpetuate Evidence"]');
        documentLink.should('exist');


        documentLink
            .then($link => {
                const href = $link.prop('href');
                cy.request(href).then((response) => {
                    expect(response.status).to.eq(200);
                    expect(response.headers['content-type']).to.include('application/pdf');
                });
            });
    });
})
