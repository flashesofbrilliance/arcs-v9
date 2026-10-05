// Job Factory slice 1: culture evidence. Runs against the REAL phrase lists in
// runtime/specs/target-role-scan.json, so a spec edit that breaks a fixture fails
// here. Fails-on-bad (grind posting gates and caps) and passes-on-good (a
// family-friendly posting quotes three positives and is left alone), plus the
// word-edge test the 2025 prototype failed (/ai/ matched "said").
import { test } from "node:test"
import assert from "node:assert/strict"
import { readFileSync } from "node:fs"
import { extractCultureCues, applyCultureGuard, mergeJdHits, type CultureCues } from "../../src/lib/culture-cues.ts"

const CUES: CultureCues = JSON.parse(readFileSync(new URL("../../runtime/specs/target-role-scan.json", import.meta.url), "utf8")).rubric.culture_cues

const GRIND = "We are a fast-paced startup. You will wear many hats and act like a rockstar. We work hard, play hard."
const GOOD = "We offer 16 weeks of parental leave. We are an async-first team. We run blameless postmortems after every incident."
const NEAR_MISS = "We maintain a detailed email digest. Our backhustler program is unrelated. Grindstone is our CI vendor."

test("grind posting: three negatives quoted, culture capped at 1, grind gate fires", () => {
  const hits = extractCultureCues(GRIND, CUES)
  assert.equal(hits.neg.length, 3)
  assert.ok(hits.neg.some((h) => h.startsWith("Unbounded scope: ") && h.includes("wear many hats")))
  const g = applyCultureGuard({ culture: 3, role_shape: 2 }, [], hits, CUES)
  assert.equal(g.dims.culture, 1)
  assert.equal(g.dims.role_shape, 2)
  assert.deepEqual(g.gates, ["grind-culture red flags in reviews"])
})

test("fast-paced alone is not a negative (deliberate: too common to gate on)", () => {
  assert.equal(extractCultureCues("A fast-paced team shipping weekly.", CUES).neg.length, 0)
})

test("good posting: three positives quoted, guard leaves the score alone", () => {
  const hits = extractCultureCues(GOOD, CUES)
  assert.equal(hits.pos.length, 3)
  assert.equal(hits.neg.length, 0)
  const g = applyCultureGuard({ culture: 3 }, [], hits, CUES)
  assert.equal(g.dims.culture, 3)
  assert.deepEqual(g.gates, [])
})

test("word edges: substrings never count", () => {
  const hits = extractCultureCues(NEAR_MISS, CUES)
  assert.deepEqual(hits, { pos: [], neg: [] })
})

test("one negative is below the cap; the guard never raises a score", () => {
  const hits = extractCultureCues("Expect nights and weekends during launches.", CUES)
  assert.equal(hits.neg.length, 1)
  assert.equal(applyCultureGuard({ culture: 2 }, [], hits, CUES).dims.culture, 2)
  const two = extractCultureCues("Hustle is our culture. Ninjas only.", CUES)
  assert.equal(applyCultureGuard({ culture: 0 }, [], two, CUES).dims.culture, 0)
})

test("percent-ending phrase matches (a bare \\b would refuse it)", () => {
  assert.equal(extractCultureCues("We hire the top 1% of engineers.", CUES).neg.length, 1)
})

test("jdHits merge keeps both existing shapes", () => {
  const hits = { pos: ["Boundaries: x"], neg: [] }
  assert.deepEqual(JSON.parse(mergeJdHits('{"A":["a hit"]}', hits)), { A: ["a hit"], culture_pos: ["Boundaries: x"], culture_neg: [] })
  assert.deepEqual(JSON.parse(mergeJdHits('["claim-1"]', hits)), { scout_claims: ["claim-1"], culture_pos: ["Boundaries: x"], culture_neg: [] })
  assert.deepEqual(JSON.parse(mergeJdHits(null, hits)), { culture_pos: ["Boundaries: x"], culture_neg: [] })
})

// Regression: every false positive the 2026-10-05 dry run (20 live rows) surfaced.
test("dry-run false positives stay out", () => {
  const fp = [
    "j.async=true;j.src='https://sgtm.example.com/gtm.js';",
    "agents that run inside the client's own cloud and governance boundary.",
    "We've pushed the boundaries of what AI can do with unstructured data.",
    "turn the failure patterns you spot into checks and boundaries that raise quality.",
    "files made available in response to the federal Transparency in Coverage Rule.",
    "Your work has a direct feedback loop to our products.",
  ]
  for (const s of fp) assert.deepEqual(extractCultureCues(s, CUES), { pos: [], neg: [] }, s)
})

test("dry-run true positives still match", () => {
  for (const s of ["Family planning programs + paid parental leave.", "Transparent culture, amazing mission!", "We support a flexible workplace: work from home, or both."])
    assert.equal(extractCultureCues(s, CUES).pos.length, 1, s)
})
