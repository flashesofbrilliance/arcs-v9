---
spec: engagement-record
version: v0
date: 2026-11-06
owner: Zach Harris
renderer: scripts/engagement_render.py
first_instance: _ARTIFACTS/engagements/myally-ld/engagement.json
---

# Engagement record v0

**Why:** each client engagement (asks, steps, deliverables, assumptions, prices, terms) used to be retyped into a
proposal page, a reply email and an agreement by hand, so a changed price or date drifted between them.
**What:** one JSON record per engagement; every client artifact renders from it, and a check fails when a cited value
changed but its outputs were not regenerated. Same record in, same bytes out.
**How to read this:** the shape first, then the rules the validator enforces, then how to add an engagement.

## Where it lives

```
_ARTIFACTS/engagements/<slug>/
  engagement.json          the record (private repo; never under public/)
  templates/*.md.tpl       one per text artifact (reply, agreement, exhibit-a, ...)
  out/*.md, proposal.html  rendered; never hand-edit
  out/render.lock.json     sha256 per output + the value of every field it cites
```

## Shape

| Key | Holds |
|---|---|
| `schema` | `"engagement-record-v0"` |
| `meta` | `id`, `title`, `internal_note`, `record_date`, `last_sent` (YYYY-MM-DD or null) |
| `client` | `legal_name`, `product`, `contacts[]`, `reply_to` (cite as `{{client.<key>}}`) |
| `fields` | the values everything cites. Stored: `kind`, `value`, `label`, `source {kind, ref, date}`, `history[]`. Derived: `kind`, `label`, `derive` |
| `asks[]` | the client's questions: `id`, `short`, `text`, `answered_by[]`, `source` |
| `phases[]` | steps of the offer: `id`, `name`, `question`, `fee` (may cite), `status` |
| `lists` | named bullet lists (`{{list:<name>}}`), items `{id, text}`; text may cite |
| `assumptions[]` | `id`, `text`, `test_that_would_decide`, `status`, `source` (row shape follows `scripts/assumptions.py`) |
| `scenarios[]` | best, base, worst: `what`, `earn`, `watch`, `guard` |
| `terms[]` | agreement clauses `{id, title, body}`, numbered in order by `{{terms}}` |
| `altitudes` | one line each: `exec`, `strategic`, `operational`, `tactical`, `surgical` |
| `cold_read` | `why`, `what`, `why_now`, `before`, `during`, `after` (the cold-read header) |
| `counsel_notes` | where counsel is likely to push back |

Field kinds: `money` ($1,500), `int`, `days`, `hours`, `date` (Nov 13), `text`.
Formats: `|long` (Nov 13, 2026), `|nda` (10.26.26), `|weeks` (21 days as "three weeks"), `|word` / `|Word` (four / Four).
Derive ops: `["mul", a, b]`, `["div", a, b]`, `["add_days", date, days]`; arguments are field ids, numbers or nested ops.

## Rules (the validator refuses the record otherwise)

- Every stored value has a source: `kind` in sent, email, doc, decision, judgment, call; a non-empty `ref`; a `date`.
  `judgment` means it is Zach's call, with no measured odds.
- A derived field has no value or source of its own; its inputs are its provenance.
- History is append-only: when a value changes, move the old one into `history` as `{value, until, source}`.
- Every assumption carries `test_that_would_decide`.
- An unknown `{{cite}}`, a derive cycle or an em-dash anywhere is an error.

## Self-updating

- `--check` re-renders in memory and fails when an output on disk differs. If a cited value moved, it names the field,
  its old and new value, and every output that cites it; otherwise it says the record text, a template or a hand edit changed.
- Once `meta.last_sent` is set, any cited field (or derive input) with a history entry `until` after that date gets a
  "CHANGED SINCE LAST SENT" block in each text output (as an HTML comment above the body, so the email itself stays clean)
  and a gold "changed DATE, was X" mark on the page. A change is shown, never kept silently.
- Pre-commit runs `--check` whenever anything under `_ARTIFACTS/engagements/` or the renderer is staged, and the
  `--self-test` when the renderer is staged.

## Add an engagement

1. Copy `_ARTIFACTS/engagements/myally-ld/` to a new slug; replace the record's values and sources.
2. Edit the templates only where the wording differs for this client.
3. `python3 scripts/engagement_render.py --dir _ARTIFACTS/engagements/<slug>`, read `out/`, commit.

Nothing renders under `public/`, and nothing here sends. Agreements are drafts for a Connecticut lawyer, not legal advice.

## v1: honest proposals (2026-11-08)

A record with `"schema": "engagement-record-v1"` carries the honest-proposals rules
(design: `_PROPOSALS/2026-11-08-honest-proposals-design.md`). v0 records are unchanged and skipped by the lint.
Worked example (every name, figure and date invented): `_ARTIFACTS/engagements/example-fictional/`.

The renderer refuses a v1 record unless:

| Rule | Record shape |
|---|---|
| The first step is a fixed fee | `phases[0].fee` cites one `money` field |
| Later steps are ranges with written assumptions | `phases[1:].fee` cites one `money_range` field (`value: [low, high]`, rendered "$X to $Y") and `phases[i].assumptions[]` names existing assumption ids |
| Paid state is explicit | every phase has `paid: true` or `false` |
| What is not proven is said out loud | `not_proven[]` has at least one `{id, text}`; it renders as its own section |
| Full-build pricing has a ceiling | `leak.ceiling_usd` is a positive number |
| A reliance disclaimer, not a sharing ban | `terms[]` has a term with `id: "reliance"` |
| Optional, checked when present | `ex_ante {expect, p (0 to 1), basis {kind: stated, measured or judgment, text}, date}`; `close {what_happened, held, date}` (needs `ex_ante`); `counsel_review {date, by_role, template_version}`; `gauntlet {date, ref, open_findings}` |

`scripts/proposal_lint.py` then checks the templates, the record's text and the client outputs (`out/*.md`, exported
`out/*.json`; header comments and the internal `proposal.html` are not client text):

1. **figures**: no `$` amount, percent or "N hours/days/weeks" typed into a template or record text; cite a field.
   Known gap: numbers written as words ("three thousand dollars") pass.
2. **sharing**: no ban phrase ("may not be shared", "do not forward"); the agreement says "not legal" advice and "as is".
3. **leak**: while `phases[0].paid` is false, no `$` figure at or above `leak.ceiling_usd`, and no three or more table
   rows carrying a price or hours (a task-level bid sheet).
4. **voice**: no em-dash, no we / our / us.

`--send-ready` adds: outputs fresh (`engagement_render.py --check`), `counsel_review` set, `gauntlet` set with
`open_findings: 0`, and `ex_ante` written. Nothing in either script sends. Pre-commit runs the lint on any staged
engagement and its `--self-test` when the lint or renderer is staged.
