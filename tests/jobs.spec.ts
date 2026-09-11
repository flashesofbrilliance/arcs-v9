import { test, expect, request } from "@playwright/test"

// Jobs-board security-boundary + API-contract coverage. The board and every
// forge bundle are admin-gated (magic link), so an unauthenticated client can
// only ever prove the gate holds — that is exactly the regression we most need
// to catch. API-contract checks run only when JOBS_PIPELINE_TOKEN is present
// (the pipeline caller); they are skipped, not failed, without it, so CI stays
// green without the secret. Point SMOKE_BASE_URL at https://jobs.arcs.care.
// Run: SMOKE_BASE_URL=https://jobs.arcs.care npm run test:smoke -- jobs.spec.ts

const BASE = process.env.SMOKE_BASE_URL ?? "https://jobs.arcs.care"
const TOKEN = process.env.JOBS_PIPELINE_TOKEN
const BUILT = "4441207605" // Bain — a built bundle
const noFollow = { maxRedirects: 0 }

test.describe("gate holds for anonymous visitors", () => {
  test("board redirects to sign-in", async () => {
    const c = await request.newContext({ baseURL: BASE })
    const r = await c.get("/jobs", noFollow)
    expect([307, 308]).toContain(r.status())
    expect(r.headers()["location"]).toContain("/compass")
  })

  test("forge bundle page redirects to sign-in", async () => {
    const c = await request.newContext({ baseURL: BASE })
    const r = await c.get(`/jobs/${BUILT}/forge`, noFollow)
    expect([307, 308]).toContain(r.status())
    expect(r.headers()["location"]).toContain("/compass")
  })

  test("forge file + download endpoints never leak a file unauthenticated", async () => {
    const c = await request.newContext({ baseURL: BASE })
    for (const q of ["?file=resume-bain-ai-eng-lead.pdf", "?file=resume-bain-ai-eng-lead.pdf&dl=1", "?file=../../.env"]) {
      const r = await c.get(`/jobs/${BUILT}/forge${q}`, noFollow)
      expect([307, 308], `unauth ${q} must redirect, not serve`).toContain(r.status())
      expect(r.headers()["content-type"] ?? "").not.toContain("application/pdf")
    }
  })

  test("lane surfaces page redirects anon to sign-in", async () => {
    const c = await request.newContext({ baseURL: BASE })
    const r = await c.get("/jobs/lane", noFollow)
    expect([307, 308]).toContain(r.status())
    expect(r.headers()["location"]).toContain("/compass")
  })

  test("API rejects a missing/blank token", async () => {
    const c = await request.newContext({ baseURL: BASE })
    const r = await c.get("/api/jobs")
    expect(r.status()).toBe(401)
  })
})

test.describe("API contract (pipeline token)", () => {
  test.skip(!TOKEN, "JOBS_PIPELINE_TOKEN not set")
  const hdr = () => ({ "x-jobs-token": TOKEN as string })

  test("GET /api/jobs returns rows + a spec", async () => {
    const c = await request.newContext({ baseURL: BASE, extraHTTPHeaders: hdr() })
    const r = await c.get("/api/jobs")
    expect(r.status()).toBe(200)
    const d = await r.json()
    expect(Array.isArray(d.rows)).toBeTruthy()
    expect(d.rows.length).toBeGreaterThan(0)
    expect(d.caller).toBe("pipeline")
  })

  test("GET /api/jobs/lane returns seeded sources", async () => {
    const c = await request.newContext({ baseURL: BASE, extraHTTPHeaders: hdr() })
    const r = await c.get("/api/jobs/lane")
    expect(r.status()).toBe(200)
    const d = await r.json()
    expect(Array.isArray(d.sources)).toBeTruthy()
    expect(d.sources.length).toBeGreaterThan(0)
    expect(d.sources.map((s: { key: string }) => s.key)).toContain("linkedin_alert_digest")
  })

    test("every built forge row has a unique-named resume download link", async () => {
    const c = await request.newContext({ baseURL: BASE, extraHTTPHeaders: hdr() })
    const r = await c.get("/api/jobs/forge?status=built")
    expect(r.status()).toBe(200)
    const body = await r.json()
    const runs = Array.isArray(body) ? body : body.runs
    expect(Array.isArray(runs)).toBeTruthy()
    expect(runs.length).toBeGreaterThan(0)
    for (const run of runs) {
      expect(run.resumeUrl, `${run.jobid} missing resumeUrl`).toBeTruthy()
      expect(run.resumeUrl).toMatch(/\/forge\?file=resume-.+\.pdf&dl=1$/)
    }
  })
})
