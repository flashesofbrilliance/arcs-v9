// Job Factory slice 4: the autonomy dial. The BAR-lens probe the teardown asked
// for: locked stations refuse Auto, and a hand-edited stored row cannot unlock them.
import { test } from "node:test"
import assert from "node:assert/strict"
import { effective, applyChange, STATIONS } from "../../src/lib/autonomy.ts"

test("defaults match the spec", () => {
  const e = effective(null)
  assert.equal(e.find.mode, "auto"); assert.equal(e.cut_t12.mode, "auto"); assert.equal(e.cut_t3.mode, "ask")
  assert.equal(e.send.mode, "off"); assert.equal(e.go_public.mode, "ask"); assert.equal(e.outcome.mode, "off")
})

test("every locked station refuses any write, Auto above all", () => {
  for (const [k, s] of Object.entries(STATIONS)) if (s.locked) {
    assert.ok("error" in applyChange(null, { [k]: "auto" }), `${k} auto`)
    assert.ok("error" in applyChange(null, { [k]: s.default }), `${k} default`)
  }
})

test("a hand-edited stored row cannot unlock a locked station", () => {
  const e = effective(JSON.stringify({ send: "auto", go_public: "auto", cut_t3: "auto" }))
  assert.equal(e.send.mode, "off")
  assert.equal(e.go_public.mode, "ask")
  assert.equal(e.cut_t3.mode, "auto") // unlocked stations do take the stored value
})

test("unlocked stations move; bad modes and unknown stations are refused", () => {
  const r = applyChange(JSON.stringify({ cut_t3: "ask" }), { cut_t3: "auto", prose: "off" })
  assert.deepEqual(r, { next: { cut_t3: "auto", prose: "off" } })
  assert.ok("error" in applyChange(null, { cut_t3: "yolo" }))
  assert.ok("error" in applyChange(null, { deploy: "auto" }))
  assert.ok("error" in applyChange(null, "auto"))
})

test("a write drops locked keys that slipped into the stored row", () => {
  const r = applyChange(JSON.stringify({ send: "auto", find: "ask" }), { score: "ask" })
  assert.deepEqual(r, { next: { find: "ask", score: "ask" } })
})

test("garbage in storage falls back to defaults, never to auto", () => {
  assert.equal(effective("{not json").send.mode, "off")
  assert.equal(effective("[1,2]").cut_t3.mode, "ask")
})
