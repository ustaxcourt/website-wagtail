import { checkA11y } from "../../support/commands"

describe('dawson page', () => {
  it('verify the page load and links are displayed and clickable', function() {
    cy.visit('/dawson/')

    const logoLink = cy.get('a[data-testid="dawson-logo"]');
    logoLink.should('exist');

    checkA11y()

    logoLink
      .then($link => {
        const href = $link.prop('href');
        cy.request(href).then((response) => {
          expect(response.status).to.eq(200);
          expect(response.headers['content-type']).to.exist;
        });
      });
  });
})
