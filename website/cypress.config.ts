import { defineConfig } from "cypress";

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
      })
    },
    baseUrl: 'http://127.0.0.1:8000'
  },
});
