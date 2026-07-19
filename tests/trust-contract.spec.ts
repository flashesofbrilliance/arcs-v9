import { test, expect } from "@playwright/test"
import { Client } from "pg"

// Ledger TC-004: regression tests for trust contract §1 — "If you are not
// signed in … nothing is written server-side." This exact invariant was
// violated by the pre-2026-07-13 defect disclosed in /trust §1; these tests
// keep it from silently recurring.
//
// Row-count assertions need a direct DB connection; they run wherever
// DATABASE_URL is set (CI's ephemeral Postgres, local dev). The pure
// HTTP-status assertions run everywhere.

const DB_URL = process.env.DATABASE_URL

async function countRows(table: string): Promise<number> {
  const client = new Client({ connectionString: DB_URL, ssl: DB_URL?.includes("localhost") ? undefined : { rejectUnauthorized: false } })
  await client.connect()
  try {
    const r = await client.query(`SELECT count(*)::int AS n FROM "${table}"`)
    return r.rows[0].n
  } finally {
    await client.end()
  }
}

test("anonymous POST /api/compass writes no Receipt rows (trust §1)", async ({ request }) => {
  test.skip(!DB_URL, "DATABASE_URL not set — row-count assertion unavailable")
  const before = await countRows("Receipt")
  // The upstream Claude call may fail (CI uses a placeholder key) — that's
  // fine: the invariant is that NO code path of an anonymous request writes,
  // whether the pipeline succeeds or errors mid-way.
  await request.post("/api/compass", { data: { question: "trust contract §1 smoke probe" } })
  const after = await countRows("Receipt")
  expect(after, "anonymous compass request must not persist a Receipt").toBe(before)
})

test("anonymous POST /api/prep writes no PrepSession rows (trust §1)", async ({ request }) => {
  test.skip(!DB_URL, "DATABASE_URL not set — row-count assertion unavailable")
  const before = await countRows("PrepSession")
  const res = await request.post("/api/prep", { data: { stakes: "HIGH", horizon: "TODAY", confidence: 3 } })
  expect(res.status(), "anonymous prep should be accepted (echoed), not rejected").toBeLessThan(500)
  const after = await countRows("PrepSession")
  expect(after, "anonymous prep must be echoed, never persisted").toBe(before)
})

test("anonymous POST /api/receipts/save is rejected (write path requires auth)", async ({ request }) => {
  const res = await request.post("/api/receipts/save", { data: {} })
  expect(res.status()).toBe(401)
})

test("anonymous POST /api/account/delete is rejected", async ({ request }) => {
  const res = await request.post("/api/account/delete")
  expect(res.status()).toBe(401)
})
