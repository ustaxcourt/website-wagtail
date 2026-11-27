/**
 * Scheduled Publishing ("Go live" / "Expiry") Editor Validation — WAG-1411
 *
 * For every page type that can be added under Home, opens the add form and checks:
 *  - the form renders exactly one go_live_at / expire_at input and one
 *    #schedule-publishing-dialog (duplicate PublishingPanels create duplicate DOM
 *    ids, and the jQuery datetimepicker then binds to the wrong input);
 *  - the "Set schedule" dialog opens from the Status side panel;
 *  - focusing the "Go live date/time" input shows a populated calendar.
 *
 * Nothing is saved, so this is safe to run against AWS environments.
 */

describe('Scheduled publishing panel renders a working date picker', () => {
  const ADMIN_USERNAME = Cypress.env('ADMIN_USERNAME') || 'admin';
  const ADMIN_PASSWORD = Cypress.env('ADMIN_PASSWORD') || 'ustcAdminPW!';

  it('every addable page type has one schedule panel with a working calendar', () => {
    cy.adminLogin(ADMIN_USERNAME, ADMIN_PASSWORD);

    // Collect the "add page" URL of every page type that can be created under Home.
    cy.request('/admin/api/main/pages/?slug=home').then((response) => {
      const homeId = response.body.items[0].id;
      cy.visit(`/admin/pages/${homeId}/add_subpage/`);
      return cy.get(`a[href*="/admin/pages/add/"][href$="/${homeId}/"]`).then(($links) => {
        const urls = $links
          .toArray()
          .map((a) => a.getAttribute('href') as string)
          .filter((href, i, all) => all.indexOf(href) === i);
        expect(urls, 'page types addable under Home').to.not.be.empty;
        return urls;
      });
    }).each((url: string) => {
      cy.log(`Checking ${url}`);
      cy.visitAndOpenScheduleDialog(url);

      cy.get('input[name="go_live_at"]').should('have.length', 1);
      cy.get('input[name="expire_at"]').should('have.length', 1);
      cy.get('[id="schedule-publishing-dialog"]').should('have.length', 1);

      cy.get('#schedule-publishing-dialog').within(() => {
        cy.get('input[name="go_live_at"]').should('be.visible').click();
      });

      cy.get('.xdsoft_datetimepicker')
        .filter(':visible')
        .should('have.length', 1)
        .find('.xdsoft_calendar td.xdsoft_date')
        .should('have.length.at.least', 28);
    });
  });
});
