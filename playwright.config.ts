import { defineConfig, devices } from "@playwright/test"

// Minimal smoke config — checks key routes render without console errors
// against a server you already have running (local dev or a deployed
// preview). No webServer block: the /recoil-report skill points baseURL at
// whichever target it's verifying that run.
export default defineConfig({
  testDir: "./tests",
  timeout: 30_000,
  use: {
    baseURL: process.env.SMOKE_BASE_URL ?? "http://localhost:3000",
    headless: true,
  },
  reporter: [["list"]],
  // "desktop" (default viewport) covers the console-error/status smoke checks.
  // "mobile-portrait" catches layout regressions (e.g. overflow/wrap bugs)
  // that only show up at narrow widths — see tests/layout.spec.ts.
  projects: [
    { name: "desktop" },
    { name: "mobile-portrait", use: { ...devices["Desktop Chrome"], viewport: { width: 375, height: 812 } } },
  ],
})
