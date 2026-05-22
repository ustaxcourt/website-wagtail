import { defineConfig } from "@playwright/test";
import { voConfig } from "@guidepup/playwright";

export default defineConfig({
    ...voConfig,
    testDir: "./tests",
    timeout: 60_000,
    use: {
        baseURL: process.env.PLAYWRIGHT_BASE_URL || "http://localhost:8000",
        headless: false,
    },
    projects: [
        {
            name: "voiceover",
            use: { ...voConfig.use },
        },
    ],
});
