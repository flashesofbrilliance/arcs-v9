import { defineConfig } from "@playwright/test"

// Minimal smoke config — checks key routes render without console errors
// against a server you already have running (local dev or a deployed
// preview). No webServer block: the /recoil-report skill points baseURL at
// whichever target it's verifying that run.
export default defineConfig({
  testDir: "./tests",
  // tests/unit/*.test.ts are node:test files run by `npm run test:unit` with the
  // `@/` loader (tests/unit/register.mjs). Playwright's default testMatch also
  // matches *.test.ts and would load them without that loader.
  testIgnore: "unit/**",
  timeout: 30_000,
  use: {
    baseURL: process.env.SMOKE_BASE_URL ?? "http://localhost:3000",
    headless: true,
  },
  reporter: [["list"]],
})
