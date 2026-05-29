/// <reference types="node" />

import { defineConfig } from "cypress";
import * as path from "path";
import * as XLSX from "xlsx";

const includeAdminValidation = process.env.CYPRESS_INCLUDE_ADMIN_VALIDATION === 'true';
const includeLocalValidation = process.env.CYPRESS_INCLUDE_LOCAL_VALIDATION === 'true';
const adminValidationSpecPattern = '**/admin*_validation.cy.{js,jsx,ts,tsx}';
const localValidationSpecPattern = '**/local*cy.{js,jsx,ts,tsx}';
const baseUrl = process.env.CYPRESS_BASE_URL || 'http://localhost:8000';
const coverageEnabled = process.env.CYPRESS_COVERAGE !== 'false';
const adminUsername = process.env.CYPRESS_ADMIN_USERNAME || undefined;
const adminPassword = process.env.CYPRESS_ADMIN_PASSWORD || undefined;
const env = {
  ...(adminUsername ? { ADMIN_USERNAME: adminUsername } : {}),
  ...(adminPassword ? { ADMIN_PASSWORD: adminPassword } : {}),
};

function getExcludeSpecPattern() {
  let result : string[] = [];
  if (!includeAdminValidation) {
    result.push(adminValidationSpecPattern);
  }
  if (!includeLocalValidation) {
    result.push(localValidationSpecPattern);
  }
  return result;
}

export default defineConfig({
  e2e: {
    experimentalStudio: true,
    setupNodeEvents(on, config) {
      if (coverageEnabled) {
        require('@cypress/code-coverage/task')(on, config);
      }

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
        getRedirectsFromXlsx(xlsxRelativePath: string) {
          const fullPath = path.resolve(__dirname, xlsxRelativePath);
          const wb = XLSX.readFile(fullPath);
          const ws = wb.Sheets[wb.SheetNames[0]];
          const rows = XLSX.utils.sheet_to_json<string[]>(ws, { header: 1 }) as string[][];
          // Skip header row; columns are: From, To, Type, Site
          return rows.slice(1).map(([from, to]) => ({ from, to }));
        },
      });

      return config;
    },
    baseUrl,
    ...(Object.keys(env).length > 0 ? { env } : {}),
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    excludeSpecPattern: getExcludeSpecPattern()
  },
});
