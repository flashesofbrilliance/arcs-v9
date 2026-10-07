// tributariesOf (src/lib/tributaries.ts): atgTributaries first, then the
// tributaries array in rawResponse with the compass route's fence stripping.
import { test } from "node:test"
import assert from "node:assert/strict"
import { tributariesOf } from "../../src/lib/tributaries.ts"

const atg = [
  { type: "meta", label: "Meta-question", prompt: "a" },
  { type: "challenge", label: "Need to hear", prompt: "b" },
  { type: "adjacent", label: "Adjacent lens", prompt: "c" },
]
const rawTribs = [{ type: "meta", prompt: "from raw" }]

test("atgTributaries present wins, even when rawResponse is fenced", () => {
  const out = tributariesOf({ atgTributaries: JSON.stringify(atg), rawResponse: "```json\n{\"tributaries\":" + JSON.stringify(rawTribs) + "}\n```" })
  assert.deepEqual(out, atg)
})

test("atg null + plain JSON rawResponse falls back to raw.tributaries", () => {
  const out = tributariesOf({ atgTributaries: null, rawResponse: JSON.stringify({ tributaries: rawTribs }) })
  assert.deepEqual(out, rawTribs)
})

test("atg null + fenced rawResponse (the prod cmuxxvcbj shape) still parses", () => {
  const raw = "```json\n" + JSON.stringify({ true_north: "x", tributaries: rawTribs }) + "\n```"
  assert.deepEqual(tributariesOf({ atgTributaries: null, rawResponse: raw }), rawTribs)
})

test("both unparseable -> []", () => {
  assert.deepEqual(tributariesOf({ atgTributaries: "not json", rawResponse: "```json\n{broken" }), [])
  assert.deepEqual(tributariesOf({ atgTributaries: null, rawResponse: null }), [])
  assert.deepEqual(tributariesOf(null), [])
})

test("empty atg array does not shadow a usable rawResponse", () => {
  assert.deepEqual(tributariesOf({ atgTributaries: "[]", rawResponse: JSON.stringify({ tributaries: rawTribs }) }), rawTribs)
})
