---
title: Compass Lane · execution plan v1 (cost per outcome)
status: DRAFT · 2026-09-05 · companion to compass-lane-spec-v2.md §12 (implementation order)
rules applied: model-tier routing (locked 2026-08-11) · dollar compression over token compression · terminal before agents · right cook temp · cost leaks are a ruin vector · human-vs-actual leverage spelled out
---

# Execution plan: highest-quality outcome, lowest dollars per outcome

The unit is **dollars per accepted outcome**, not tokens. Every step below names the job class first, because the class decides the tier, and the tier decides most of the cost. Three job classes:

- **Mechanical.** A grep, a schema check, a set-diff, a migration, a render. Terminal or a script. No model.
- **Structured.** Implement-to-spec, wire, refactor, port with a contract. One small model in the main session, or Sonnet-class when it must reason over code.
- **Judgment.** Read for meaning, grade evidence, write in a voice, decide what to cut. The only class that earns a large model, and never in parallel beyond two.

What the last week taught, banked as rules here: four large-model agents fanned out at once hit the monthly spend limit and lost three partial runs; the resumed runs cost 95K to 240K tokens each, largely re-fetching and re-deriving inputs the caller already had. The single biggest lever is **handing every agent its inputs up front** and never letting it fetch what the orchestrator already holds.

## 1. The plan, step by step

| Step (spec §12) | Job class | Runs where | Tier | Batch | Est. cost | Human-equiv → actual |
|---|---|---|---|---|---|---|
| 1. Weight guardrail fix | Mechanical + one judgment | Zach picks the fix; a script rewrites the JSON, the eval re-runs | none / Haiku for the changelog line | one PR | < $0.10 | 30 min → 3 min |
| 2. Migration + rename + backfill | Mechanical | Prisma migration written by hand from the spec's object list; applied through the Supabase MCP; backfill is SQL, not a model | none | one PR, one apply | $0 model; one Vercel build | 3 h → 25 min |
| 3. Lane schema + lane eval | Structured | JSON schema in the terminal; eval extends `jobs_trigger_eval.mjs` | none | one PR | $0 | 2 h → 15 min |
| 4. Size + Decide against Score | Structured (wiring) + Judgment (the scorer prompt) | Wiring in the main session at Sonnet-class; scorer prompt authored once, then runs as a batch | Sonnet for wiring; **Haiku-class at temperature 0 for scoring** | see §2 | wiring ~$2; scoring ~$0.01 per row | 1 day → 1.5 h |
| 5. Flip lane to bound | Mechanical | one field, one PR, eval green as the gate | none | — | $0 | — |
| 6. Second lane (Todd / PRL) | Judgment for the lane file's labels; Mechanical for everything else | one drafting pass by the main session from the Granola transcript and the PRL status pages; no agent | Sonnet-class draft, Zach edits | one PR | ~$1 | 4 h → 40 min |
| Ongoing: forge runs | Judgment, tiered | one agent per row, **max 2 concurrent**, inputs pre-staged (§3) | light tier: Sonnet-class; full tier: Opus-class, floored, because it is sent to a human and irreversible | per swipe | light ~$1.50, full ~$8 (estimate; ledger meters actual) | 3 h per cut → 12 min |
| Ongoing: daily sweep | Mechanical + batch scoring | scheduled task; fetch and parse are scripts; scoring is the §2 batch | Haiku-class at 0 | one run per weekday | ~$0.50/day at 40 new rows | 45 min → 0 |

Totals for the build itself (steps 1 to 6): well under $20 in model spend and one production build per PR. The recurring cost is the sweep and the forges, which is where the levers below matter.

## 2. The scorer: prompt engineering that pays

The scorer is the only recurring model call that runs on every row, so it gets the most care.

1. **Stable prefix, cached.** The rubric (`target-role-scan.json`), the scoring instructions, and the output schema go first and never change between calls. The posting text goes last. This puts the invariant part in the prompt cache; only the JD is new tokens.
2. **Temperature 0.** Scoring against anchors is a deterministic job. Right cook temp.
3. **Batch by JD, not by row.** Ten postings per call in one JSON array in, one array out, each element keyed by jobid. A malformed element fails that row only.
4. **Pre-fetch, pre-clean.** The task fetches and strips each JD to plain text before the call. The model never sees HTML, never fetches, never guesses at a page it could not load; those rows are marked unscored with the reason, by the script.
5. **Schema-bound output.** One JSON object per row: dims 0 to 3, gates, assessment ≤ 25 words, evidence quotes per differentiator (verbatim, ≤ 2 each), hiring-manager kind, contact type. Validated by the script; a row that fails validation is retried once, then unscored with the reason.
6. **No re-scoring on read.** A row is scored once per target version. A weight change re-sizes with arithmetic, not a model call; only a change to anchors or gates triggers a re-score.
7. **Evidence grades from the script, not the model.** Whether a claim is documented or self-reported comes from matching against the record of record; the model does not opine on it.

Expected: about 1,200 cached prefix tokens, 800 to 1,500 new tokens per JD, 250 output tokens per row. At Haiku-class prices that is on the order of a cent a row.

## 3. Forge agents: the contract that stops the re-derivation

Each forge agent receives, in its first message, everything it would otherwise fetch:

- the JD as text (`jd-full.txt`), already saved
- the record of record as text, already extracted from resume.arcs.care (it serves HTML)
- the row's Score with evidence quotes
- the lane file, the trigger spec, and the two design rules (Blacksmith base; headline names the archetype)
- the reference bundle path and the exact output file list
- the four-width check command (Playwright from the main clone; headless Chrome cannot do 375)

And it is told what **not** to do: no gathering the JD, no re-grading the record, no design-system exploration, no screenshots beyond the four widths, no tool calls to the database. The agent's job is the judgment residue: the tailor mapping, the red-team, the page copy. Everything else was mechanical and was done before it started.

Concurrency cap: 2, until the ledger shows real per-run cost. Cap lives in the lane file, not in a prompt.

## 4. Where the tokens are not spent

- **Ingest and dedupe.** Python only, forever.
- **ATS and hiring-manager lookups.** One probe per company, cached in the Source and Candidate rows; never repeated by an agent.
- **Rendering and verification.** Scripts, screenshots read once, Playwright checks with pass/fail output.
- **Evals.** Scripts that read the API and assert. Zero model.
- **The board, the scans, the Role Scan.** Server-rendered from data. Zero model per view.
- **Docs commits.** Skipped by the Vercel ignore step (verified twice this week; `.gitignore` added to the safe list after PR #279 slipped through).

## 5. Metering: the ledger is the pricing model

Every model call in the sweep and every forge run writes `{date, target, stage, est, actual, tier}` to the cost ledger. Two rules:

- **Estimate before, actual after.** An estimate without an actual is a wish. The forge watcher already does this; the scorer batch does the same per run.
- **Dollars, not tokens.** Each ledger line carries the tier's list price and the dollar total; the weekly digest reports dollars per accepted outcome (per built forge, per scored row, later per interview).

The end-of-run usage report (`anthropic-skills:explain-usage`) is the second reading of the same number.

## 6. What a bar-raiser should try to break

- That Haiku-class scoring at temperature 0 holds the same bands as the Sonnet-class scoring that produced the first 19 rows. Test: re-score those 19 with the batch prompt and diff the bands. Any flip is a calibration finding, not a routing decision.
- That two concurrent forges is the right cap. Test: the ledger after five runs.
- That the cached prefix actually caches. Test: the usage report's cache-read tokens on the second batch call.
