/**
 * Enhanced Standard Page Page Edit Validation
 *
 * This test logs into the Wagtail admin, adds a new Enhanced Standard Page
 * to the Home directory, and verifies the components that can be added
 * to the page's body.
 */

import { text } from "stream/consumers";

describe('Enhanced Standard Page List Item Label Validation', () => {
  const ADMIN_USERNAME = Cypress.env('ADMIN_USERNAME') || 'admin';
  const ADMIN_PASSWORD = Cypress.env('ADMIN_PASSWORD') || 'ustcAdminPW!';

  let allPages: any[] = [];
  let testResults: Array<{
    pageId: string;
    title: string;
    slug?: string;
    status: 'success' | 'failed';
    error?: string;
  }> = [];

  it('logs in and verifies list item has a label of "Item" when added to a new Enhanced Standard Page', () => {
    // Login to admin first!
    cy.adminLogin(ADMIN_USERNAME, ADMIN_PASSWORD);

    //Navigate to the "New: Enhanced Standard Page" page in Wagtail Admin for adding a page in the Home folder
    cy.visit('/admin/pages/add/home/enhancedstandardpage/3/');
    cy.url({ timeout: 10000 }).should('include', '/admin/pages/add/home/enhancedstandardpage/3');

    //Click the "+" button under Body
    cy.get('button.c-sf-add-button').click();

    //Find the element that represents the menu that appears when the "+" button is clicked
    cy.get('div#downshift-1-menu').within(() => {
        cy.get('div.w-combobox__option-text').contains(/^List$/).click();
    });
    cy.get('div[data-streamfield-list-container=""]').within(() => {
      cy.get('button.c-sf-add-button').click();
    });
    cy.get('div[data-streamfield-list-container=""]').first().within(() => {
      cy.get('div[data-streamfield-child=""]').first().within(() => {
        cy.get('span.c-sf-block__type').first().should('have.text', 'Item');
      })
    });
  });
});

it('test', function() {});
