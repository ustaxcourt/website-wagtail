/// <reference types="node" />

import { defineConfig } from "cypress";

const includeAdminValidation = process.env.CYPRESS_INCLUDE_ADMIN_VALIDATION === 'true';
const adminValidationSpecPattern = '**/admin*_validation.cy.{js,jsx,ts,tsx}';
const baseUrl = process.env.CYPRESS_BASE_URL || 'http://localhost:8000';
const adminUsername = process.env.CYPRESS_ADMIN_USERNAME || undefined;
const adminPassword = process.env.CYPRESS_ADMIN_PASSWORD || undefined;

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
    baseUrl,
    env: {
      ADMIN_USERNAME: adminUsername,
      ADMIN_PASSWORD: adminPassword,
    },
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    excludeSpecPattern: includeAdminValidation
      ? []
      : [adminValidationSpecPattern]
  },
});
