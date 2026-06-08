import { defineConfig } from "@playwright/test";
import { screenReaderConfig } from "@guidepup/playwright";

export default defineConfig({
    ...screenReaderConfig,
    testDir: "./tests",
    testMatch: "**/*.voiceover.ts",
    timeout: 60_000,
    use: {
        ...screenReaderConfig.use,
        baseURL: process.env.PLAYWRIGHT_BASE_URL || "http://localhost:8000",
    },
    projects: [
        {
            name: "voiceover",
            use: { ...screenReaderConfig.use },
        },
    ],
});
