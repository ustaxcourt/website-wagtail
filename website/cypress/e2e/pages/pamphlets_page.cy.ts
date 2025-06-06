import {checkA11y, checkHeaderOrder, checkHeaderStyles} from "../../support/commands"

describe('pamphlets page', () => {
  it('verify the documents are displayed, clickable and check accessibility & header consistency', function() {
    cy.visit('/pamphlets/')

    const documentLink = cy.get('a[data-testid="Volume 161, Numbers 5 and 6"]');
    documentLink.should('exist');

      checkA11y();
      checkHeaderOrder();
      checkHeaderStyles();

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
