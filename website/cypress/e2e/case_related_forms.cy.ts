import { checkA11y } from "../support/commands"

describe('case related forms page', () => {

  it('verify the documents are displayed and clickable', function() {
    cy.visit('/case_related_forms/')
    checkA11y()

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
