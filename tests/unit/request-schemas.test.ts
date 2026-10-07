import { test } from 'node:test'
import assert from 'node:assert/strict'
import { CompassBody, PrepBody, SaveBody, isThreadId, tributaryIndexFor } from '../../src/lib/request-schemas.ts'

test('thread ids must be UUIDs', () => {
  assert.equal(isThreadId(crypto.randomUUID()), true)
  assert.equal(isThreadId('abc'), false)
  assert.equal(isThreadId(42), false)
})

test('compass: dashboard payload passes, null knobs fall back to defaults', () => {
  const r = CompassBody.safeParse({
    question: 'Take the job?', horizon: null, stakes: 'HIGH', sessionId: crypto.randomUUID(),
    prepId: null, parentReceiptId: null, extra: 'stripped',
  })
  assert.ok(r.success)
  assert.equal(r.data.horizon, undefined)
  assert.equal('extra' in r.data, false)
})

test('compass: missing or non-string question is rejected', () => {
  assert.equal(CompassBody.safeParse({}).success, false)
  assert.equal(CompassBody.safeParse({ question: 7 }).success, false)
  assert.equal(CompassBody.safeParse(null).success, false)
})

test('prep: non-string entity is a 400, not a 500', () => {
  assert.equal(PrepBody.safeParse({ entity: 5 }).success, false)
})

test('prep: prep page payload normalizes blanks to null', () => {
  const r = PrepBody.safeParse({ stakes: 'HIGH', protecting: ['team'], confidence: 60, entity: '  ', adversarialInput: null })
  assert.ok(r.success)
  assert.equal(r.data.entity, null)
  assert.equal(r.data.outcomeHorizon, null)
})

test('save: bearing needs string question and true_north, keeps other fields', () => {
  assert.equal(SaveBody.safeParse({ bearing: { question: 'q' } }).success, false)
  const r = SaveBody.safeParse({ bearing: { question: 'q', true_north: 't', nci_score: 70 } })
  assert.ok(r.success)
  assert.equal((r.data.bearing as Record<string, unknown>).nci_score, 70)
})

test('compass: an oversized sessionId still parses (re-minted later, not a 400)', () => {
  assert.ok(CompassBody.safeParse({ question: 'q', sessionId: 'x'.repeat(500) }).success)
})

test("CompassBody accepts owner provenance + resolveBy, rejects junk", async () => {
  const { CompassBody } = await import("../../src/lib/request-schemas.ts")
  assert.equal(CompassBody.safeParse({ question: "q", provenance: "real", resolveBy: "2026-12-01" }).success, true)
  assert.equal(CompassBody.safeParse({ question: "q", provenance: "fake" }).success, false)
  assert.equal(CompassBody.safeParse({ question: "q", resolveBy: "next week" }).success, false)
})

test('compass: tributaryIndex accepts 0..2 and refuses every other shape', () => {
  for (const i of [0, 1, 2]) {
    const r = CompassBody.safeParse({ question: 'q', parentReceiptId: 'r0', tributaryIndex: i })
    assert.ok(r.success, `tributaryIndex=${i}`)
    assert.equal(r.data.tributaryIndex, i)
  }
  for (const bad of [3, -1, 1.5, '1', true, {}, [1]]) {
    const r = CompassBody.safeParse({ question: 'q', parentReceiptId: 'r0', tributaryIndex: bad })
    assert.equal(r.success, false, `tributaryIndex=${JSON.stringify(bad)} should be a 400`)
  }
})

test('compass: tributaryIndex is optional and never defaults', () => {
  const a = CompassBody.safeParse({ question: 'q', tributaryIndex: null })
  assert.ok(a.success)
  assert.equal(a.data.tributaryIndex, null)
  const b = CompassBody.safeParse({ question: 'q' })
  assert.ok(b.success)
  assert.equal(b.data.tributaryIndex, undefined)
})

test('lineage: the tributary index lands only when the parent was accepted', () => {
  assert.equal(tributaryIndexFor(true, 1), 1)
  assert.equal(tributaryIndexFor(true, 0), 0)
  assert.equal(tributaryIndexFor(true, null), null)
  assert.equal(tributaryIndexFor(true, undefined), null)
  // Parent dropped (missing, foreign, anonymous): the index goes with it.
  assert.equal(tributaryIndexFor(false, 2), null)
})
