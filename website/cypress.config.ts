import { defineConfig } from "cypress";

const includeAdminValidation = process.env.CYPRESS_INCLUDE_ADMIN_VALIDATION === 'true';

export default defineConfig({
  e2e: {
    experimentalStudio: true,
    setupNodeEvents(on, config) {
      // implement node event listeners here
      on('task', {
        table(message) {
          console.table(message);
          return null;
        },
        log(message) {
          console.log(message);
          return null;
        },
      })
    },
    baseUrl: 'http://127.0.0.1:8000',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    excludeSpecPattern: includeAdminValidation
      ? []
      : ['**/admin_page_validation.cy.{js,jsx,ts,tsx}']
  },
});
