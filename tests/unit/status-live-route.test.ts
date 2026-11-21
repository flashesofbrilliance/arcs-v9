// status.arcs.care route handler (2026-11-21): an ISR route handler (`export const revalidate`) crashes on
// every OPTIONS request in Next 16, because the auto-implemented 204 reply is cached as an empty buffer and
// rebuilt with a body, which the Response constructor rejects. The route must not export `revalidate`; its
// caching lives in a Cache-Control header instead. Source check, so it runs without a Next build.
import { test } from "node:test"
import assert from "node:assert/strict"
import { readFileSync } from "node:fs"

const SRC = readFileSync(new URL("../../src/app/status-live.html/route.ts", import.meta.url), "utf8")

test("status-live is not an ISR route handler (OPTIONS would 500)", () => {
  assert.ok(!/^export const revalidate\b/m.test(SRC), "export const revalidate is back: OPTIONS on status.arcs.care will crash")
  assert.ok(!/force-static/.test(SRC), "force-static also makes it ISR")
})

test("status-live keeps a 10-minute CDN cache on GET", () => {
  assert.match(SRC, /s-maxage=600/)
  assert.match(SRC, /"Cache-Control": CACHE_CONTROL/)
})
