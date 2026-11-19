/**
 * Scheduled Publishing End-to-End — WAG-1411
 *
 * Schedules a draft page through the editor UI, then checks that Wagtail's
 * `publish_scheduled` command (run hourly in AWS by EventBridge) publishes it
 * once the go-live time has passed and unpublishes it once it has expired.
 *
 * Instead of waiting for real dates, the `scheduled_publishing_test_page
 * --fast-forward` management command moves the scheduled time into the past.
 * Local only: it runs management commands through cy.exec.
 */

const MANAGE = '. ../.venv/bin/activate && python manage.py';
const TEST_PAGE = `${MANAGE} scheduled_publishing_test_page`;
const PUBLIC_URL = '/scheduled-publishing-test/';

// Wagtail admin datetime format ("Y-m-d H:i"), some days from now.
function daysFromNow(days: number): string {
  const d = new Date(Date.now() + days * 24 * 60 * 60 * 1000);
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} 12:00`;
}

function expectPublicStatus(status: number) {
  cy.request({ url: PUBLIC_URL, failOnStatusCode: false }).its('status').should('eq', status);
}

function expectPageStatus(live: boolean, expired: boolean) {
  cy.exec(`${TEST_PAGE} --status`)
    .its('stdout')
    .should('contain', `PAGE_STATUS live=${live ? 'True' : 'False'} expired=${expired ? 'True' : 'False'}`);
}

describe('WAG-1411 Scheduled publishing', () => {
  const ADMIN_USERNAME = Cypress.env('ADMIN_USERNAME') || 'admin';
  const ADMIN_PASSWORD = Cypress.env('ADMIN_PASSWORD') || 'ustcAdminPW!';

  let pageId: string;

  before(() => {
    cy.exec(`${TEST_PAGE} --delete`);
    cy.exec(TEST_PAGE).then((result) => {
      const match = result.stdout.match(/PAGE_ID=(\d+)/);
      expect(match, 'test page id').to.not.be.null;
      pageId = match![1];
    });
  });

  after(() => {
    cy.exec(`${TEST_PAGE} --delete`);
  });

  it('publishes on the go-live date and unpublishes on the expiry date', () => {
    cy.adminLogin(ADMIN_USERNAME, ADMIN_PASSWORD);
    // Set the schedule through the "Set schedule" dialog and save it.
    cy.visitAndOpenScheduleDialog(`/admin/pages/${pageId}/edit/`);
    cy.get('#schedule-publishing-dialog').within(() => {
      cy.get('input[name="go_live_at"]').invoke('val', daysFromNow(2)).trigger('change');
      cy.get('input[name="expire_at"]').invoke('val', daysFromNow(5)).trigger('change');
      cy.contains('button', 'Save schedule').click();
    });
    cy.url().should('include', `/admin/pages/${pageId}/edit/`);

    // A saved future go-live date turns "Publish" into "Schedule to publish".
    cy.get('button[name="action-publish"]')
      .should('contain.text', 'Schedule to publish')
      .click({ force: true }); // may sit in the collapsed actions dropdown

    cy.get('.messages').should('contain.text', 'scheduled for publishing');

    // Scheduled, but not live yet.
    expectPageStatus(false, false);
    expectPublicStatus(404);

    // The hourly job finds nothing to do before the go-live time.
    cy.exec(`${MANAGE} publish_scheduled`);
    expectPageStatus(false, false);
    expectPublicStatus(404);

    // Go-live time passes -> the job publishes the page.
    cy.exec(`${TEST_PAGE} --fast-forward go-live`);
    cy.exec(`${MANAGE} publish_scheduled`);
    expectPageStatus(true, false);
    expectPublicStatus(200);

    // Expiry time passes -> the job unpublishes it and marks it expired.
    cy.exec(`${TEST_PAGE} --fast-forward expiry`);
    cy.exec(`${MANAGE} publish_scheduled`);
    expectPageStatus(false, true);
    expectPublicStatus(404);
  });
});
