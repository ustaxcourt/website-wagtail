/**
 * Enhanced Standard Page Page Edit Validation
 *
 * This test logs into the Wagtail admin, adds a new Enhanced Standard Page
 * to the Home directory, and verifies the components that can be added
 * to the page's body.
 */

import { text } from "stream/consumers";

describe('Enhanced Standard Page Edit Validation', () => {
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

  it('logs in and verifies expected components can be added to a new Enhanced Standard Page', () => {
    // Login to admin first!
    cy.adminLogin(ADMIN_USERNAME, ADMIN_PASSWORD);

    //Navigate to the "New: Enhanced Standard Page" page in Wagtail Admin for adding a page in the Home folder
    cy.visit('/admin/pages/add/home/enhancedstandardpage/3/');
    cy.url({ timeout: 10000 }).should('include', '/admin/pages/add/home/enhancedstandardpage/3');

    //Click the "+" button under Body
    cy.get('button.c-sf-add-button').click();

    let componentsExpectedToFind: string[] = ["Heading", "Heading 2", "Heading 3", "Heading 4", "Paragraph", "Indented Paragraph", "Snippet", "Button",
        "Horizontal Rule", "Iframe", "Alert", "Image", "Photo + Text", "Table", "Unstyled table", "Enhanced Table", "List", "List of Links",
        "Question and Answer", "Columns", "Embedded video", "Card Set", "Accordion Block", "Callout Block", "Grid", "Card Tiles", "Quick Access Tiles"
    ];
    //Find the element that represents the menu that appears when the "+" button is clicked
    cy.get('div#downshift-0-menu').within(() => {
        //Get each item in that menu. These represent a component that could be added to the Enhanced Standard Page.
        cy.get('div.w-combobox__option-text').each(($el, index, $list) => {

            //Determine if component is in the array of expected components
            const rawText: string = $el.text();
            const textToSearchFor: string = rawText.replace(/\s+/g, ' ').trim();
            let message: string = `Component '${textToSearchFor}' is in list of expected components`;
            expect(componentsExpectedToFind, message).to.include(textToSearchFor);

            //Update the array to remove the found component
            if (componentsExpectedToFind.includes(textToSearchFor))
            {
                componentsExpectedToFind = componentsExpectedToFind.filter(x => x !== textToSearchFor);
            }
        }).then(() => {
            //Determine if there are any components that were not found in the menu that should be displayed.
            expect(componentsExpectedToFind).to.be.empty;
        });
    });
  });
});
