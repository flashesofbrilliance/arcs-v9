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

## Progress (added 2026-11-08)

- `progress` (optional, top level) is an append-only list of `{row, state, date, note}`. `row` must be a row id in an
  exported tree (an `exports` block with `rows`); `state` is `not_started`, `in_progress`, `done` or `blocked`; dates
  run in order; `note` is client-facing (first person singular, plain language, at most 160 characters, no em-dash).
- The newest entry per row wins and earlier ones stay. A row that goes back from `done` shows `reopened DATE`.
- The renderer folds progress into each exported tree: every row with entries gets `status`, phases roll up from their
  gate/task/ms/oh children, and a `progress` summary carries hours done of total, items done, now, blocked, next and
  the latest entry. The myally hub's Step 1 tab draws its "Where things stand" band and row pills from that block.
- Log and publish with `scripts/engagement_progress.py` (`<row> start|done|block|reset "note"`, `--list`, `--ship`).

## Add an engagement

1. Copy `_ARTIFACTS/engagements/myally-ld/` to a new slug; replace the record's values and sources.
2. Edit the templates only where the wording differs for this client.
3. `python3 scripts/engagement_render.py --dir _ARTIFACTS/engagements/<slug>`, read `out/`, commit.

Nothing renders under `public/`, and nothing here sends. Agreements are drafts for a Connecticut lawyer, not legal advice.
