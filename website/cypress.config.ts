/// <reference types="node" />

import { defineConfig } from "cypress";

const includeAdminValidation = process.env.CYPRESS_INCLUDE_ADMIN_VALIDATION === 'true';
const adminValidationSpecPattern = '**/admin*_validation.cy.{js,jsx,ts,tsx}';

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
    baseUrl: 'http://localhost:3000',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    excludeSpecPattern: includeAdminValidation
      ? []
      : [adminValidationSpecPattern]
  },
});
