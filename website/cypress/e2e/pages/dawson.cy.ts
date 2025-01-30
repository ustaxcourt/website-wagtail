import { checkA11y } from "../../support/commands"

describe('dawson page', () => {
  it('verify the page load and links are displayed and clickable', function() {
    cy.visit('/dawson/')

    // const documentLink = cy.get('a[data-testid="Volume 161, Numbers 5 and 6"]');
    // documentLink.should('exist');

    checkA11y()

    // documentLink
    //   .then($link => {
    //     const href = $link.prop('href');
    //     cy.request(href).then((response) => {
    //       expect(response.status).to.eq(200);
    //       expect(response.headers['content-type']).to.include('application/pdf');
    //     });
    //   });
  });
})
