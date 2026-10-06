import { test } from 'node:test'
import assert from 'node:assert/strict'
import { scrubProse, scrubProseArray } from '../../src/lib/prose.ts'

test('spaced em-dash becomes a colon', () => {
  assert.equal(scrubProse('Spend 15 minutes right now — low stakes, reversible.'), 'Spend 15 minutes right now: low stakes, reversible.')
})

test('second dash in one string becomes a comma', () => {
  assert.equal(scrubProse('The first is centrifugal — the pull. The second — the question.'), 'The first is centrifugal: the pull. The second, the question.')
})

test('unspaced em-dash between words is scrubbed', () => {
  assert.equal(scrubProse('good—or not'), 'good: or not')
})

test('spaced en-dash is scrubbed, hyphens and ranges are kept', () => {
  assert.equal(scrubProse('three – four'), 'three: four')
  assert.equal(scrubProse('pages 3–4 and well-known'), 'pages 3–4 and well-known')
})

test('internal door codes become plain words', () => {
  assert.equal(scrubProse('The ONE_WAY door here is identity'), 'The one-way door here is identity')
  assert.equal(scrubProse('TWO_WAY'), 'two-way')
})

test('clean prose is unchanged; empty and null are safe', () => {
  const s = 'Name one decision you face this week.'
  assert.equal(scrubProse(s), s)
  assert.equal(scrubProse(''), '')
  assert.equal(scrubProse(null), '')
  assert.deepEqual(scrubProseArray(['a — b', 3]), ['a: b', '3'])
})

test('scrubReceiptProse cleans stored model prose but keeps the user question and enums', async () => {
  const { scrubReceiptProse } = await import('../../src/lib/prose.ts')
  const r = scrubReceiptProse({
    decision: 'Take the job — or not?',
    trueNorth: 'Wait — the window is open.',
    whyBullets: JSON.stringify(['Runway — six months', 'Clean']),
    rawResponse: JSON.stringify({ question: 'a — b', door_class: 'ONE_WAY', tributaries: [{ prompt: 'Ask — then act' }] }),
    children: [{ id: 'c1', trueNorth: 'Go — now' }],
  })!
  assert.equal(r.decision, 'Take the job — or not?')
  assert.equal(r.trueNorth, 'Wait: the window is open.')
  assert.deepEqual(JSON.parse(r.whyBullets as string), ['Runway: six months', 'Clean'])
  const raw = JSON.parse(r.rawResponse as string)
  assert.equal(raw.question, 'a — b')
  assert.equal(raw.door_class, 'ONE_WAY')
  assert.equal(raw.tributaries[0].prompt, 'Ask: then act')
  assert.equal((r.children as Array<{ trueNorth: string }>)[0].trueNorth, 'Go: now')
})
