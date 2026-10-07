@AGENTS.md
@WORLD.md

# Session orientation — read this much, and no more

This file (+ its `@`-imports AGENTS.md and WORLD.md) already loads automatically. That is your
baseline context. **Do not read further to "orient."**

- **To resume work:** read the latest `# Handoff` block below (bottom of this file) — nothing else.
  Or run `/handoff-pickup`, which reads `_STATE/snapshot.json` + the latest handoff only.
- **Progressive handoff (2026-09-04):** a global hook checkpoints git state to
  the handoff-progress ledger (jsonl + md under `_STATE/`, gitignored) every turn-with-change, and asks for a `## Delta` at each compaction. Both are gitignored. `/handoff` folds them
  into the CLAUDE.md block and marks the ledger claimed; the global SessionStart hook flags any
  worktree whose trail was never claimed. Compaction never writes CLAUDE.md anymore.
- **Open work lives in `_QUEUE/induced-backlog.jsonl`** — items carry route/gates/trigger; execute
  from there without replanning. Dense multi-domain sessions: run `/fold` to spawn composed sessions.
- **On-demand only** (do NOT read to orient — open only when the task actually needs them):
  `MEMORY.md`, `SKILL.md`, `_ARCHIVE/handoffs.md`, `_ARCHIVE/memory-archive.md`, `_STATE/*`.
- There is no "read MEMORY→SKILL→WORLD→AGENTS in order" chain anymore. That mandate cost ~40k
  tokens per session and was retired 2026-07-19; open a specific file only when a task points to it.

# Project Map (read this before exploring)

## Stack
- Next.js 16 App Router · Prisma 7 + SQLite (`dev.db`) · Auth.js v5 magic link · Anthropic SDK

## Routes
| Path | File | Purpose |
|------|------|---------| 
| `/` | `src/app/page.tsx` | Home / entry |
| `/dashboard` | `src/app/dashboard/page.tsx` | **Main compass UI** — question input, prep form, result |
| `/compass` | `src/app/compass/page.tsx` | Magic-link login form |
| `/brief/[receiptId]` | `src/app/brief/[receiptId]/page.tsx` | Cartography brief (two-column) |

## API Routes
| Endpoint | File | Purpose |
|----------|------|---------| 
| `POST /api/compass` | `src/app/api/compass/route.ts` | L0–L5 Claude pipeline → Receipt |
| `POST /api/prep` | `src/app/api/prep/route.ts` | Create PrepSession |
| `GET /api/brief/[receiptId]` | `src/app/api/brief/[receiptId]/route.ts` | Generate/fetch Brief |

## Lib
- `src/lib/db.ts` — Prisma client singleton
- `src/lib/auth.ts` — Auth.js v5 config (Resend magic link)
- `src/lib/ygate.ts` — Y gate computation (GREEN/YELLOW/RED/FORK/SCRATCH/DELTA/PARADOX/DRIFT)
- `src/lib/env.ts` — env validation

## Schema (prisma/schema.prisma)
Core models: `User` · `PrepSession` · `Receipt` (DEWY + Y gate + kinematic + lineage) · `Brief` · `Outcome`
All JSON arrays stored as TEXT (SQLite). Enums as plain strings.

## Design tokens (inline style objects, no CSS framework)
```
bg: #020408 | surface: #0d1117 | border: #1e293b
text: #e2e8f0 | muted: #7a8699 | dimmed: #8391a7  (AA on bg; raised 2026-10-04)
cyan: #00F0FF | green: #00FF9D | gold: #FFD700 | red: #FF4D6D
```

## Y states → render resolution
GREEN=SHARP · YELLOW/FORK=DEGRADED · SCRATCH/DELTA/DRIFT=GRAIN · PARADOX=MOIRE · RED=GRAIN

# ARCS v9 Architecture (governing law)

## ROM Primitives — constitutional, never violate
1. **NOTOMATION** — scaffold/sequence cognition only; never compress/replace/overrule revealed preference
2. **HYPERSPHERE CONTEXT MANIFOLD** — What / Who / Where-When / Why / Flow-State
3. **HYPERSTITION PIPELINE** — Ethereal → Loki Test → Receipt Evaluation → ROM
4. **GOLDEN INCHWORM** — Red Thread → Golden Thread → Needle (3-pass, non-blocking)
5. **ORTHOGONAL ECHO DETECTOR** — surface cross-domain kinematic isomorphisms
6. **KINTSUGI IMMUNE SYSTEM** — repair seams visibly; no silent patching of integrity failures; show the break and the gold
7. **WRITE-LOCK** — one-way-door decisions require explicit write-lock declaration before commit; irreversibility is declared, not assumed

## L0–L7 Stack (current impl: L0–L5 only)
L0=atomic signal · L1=coherence · L2=path survivability · L3=cascade · L4=cross-domain · L5=global coherence · L6=ecosystem · L7=meta-governance

## ATG — next major feature (backlog)
Every compass response should include 2–4 tributaries: meta-question · need-to-hear branch · unnamed adjacent primitive

## What's NOT built yet
ATG · Kairos detection · Blockchain registry · L6–L7 engine · Python Vector Collision microservice
Observatory/replay: a **static demo** exists (`public/observatory/`, served via a `next.config.ts`
rewrite). The full interactive Next.js page IS committed on main at `src/app/observatory/page.tsx`
(landed 2026-06-23, ~1.2k LOC); the old "never pushed" note was stale (Atlas audit 2026-09-03).
Confirm the `/observatory` route vs the static-demo rewrite before relying on either.

# Token-saving rules
- **Invoke the `token-savings-bank` skill** (user-level, `~/.claude/skills/token-savings-bank`) before any
  fan-out (subagents, chips, parallel sessions), bulk edit, or long resumable task, and whenever you notice
  waste (top-tier model on mechanical work, a subagent for a one-grep question, re-deriving state). It governs
  Claude Code session tokens, which count against the subscription limit (the weekly cap stalled the morning
  jobs task 2026-09-30/10-01). API spend is separate: prompt caching, Batch API, and Haiku roles in
  `src/lib/claude-models.ts`.
- Do NOT read files you already know from this map.
- Do NOT explore node_modules unless looking up a specific API.
- Before writing Next.js/Prisma code, check `node_modules/next/dist/docs/` for breaking changes.
- Inline styles only in components — no Tailwind, no utility classes. Sanctioned exceptions (only these): next/font classes on `<html>`, and the single `src/app/globals.css` (reset + keyframes + font tokens). Tailwind was removed 2026-07-11.
- No new dependencies without asking.
- **Self-contained artifact/page CSS: one shared px `--measure` for BODY/card reading text — NEVER `max-width:NNch` per element** (font-dependent → misaligned right edges that read as broken wrapping). **But LEDES are the exception: a hero/section lede spans the full lane width matching its heading (`max-width:none`), never the narrow body measure — a lede narrower than its heading reads as a broken/abridged block with a dead right gutter (EXCEPTION, 2026-09-29: text INDEX pages such as good.arcs.care/series/* put lede, rows and footer rule on the 680px measure) (`design-full-width-lede-matches-heading`; Zach's standing preference, do NOT "fix" it back to `--measure`).** The "too narrow" symptom is invisible to overflow/clip gates — eyeball lede-vs-heading edges at ~1280px too. Bordered callouts carry the measure on the box, not the inner text. Before shipping any single-file HTML, run the repo's own gate (`scripts/artifact_wrap_lint.py`; `npm test` for `zachharris-xyz`) and sweep 360–1440 incl. the 700–1000 band. Em-dashes 0. Canon: `_PATTERNS/arcs-artifact-css-base.css`; AGENTS.md gotcha #13.


# Versioning & handoff policy (amended 2026-07-19)

> Supersedes the prior "CLAUDE.md — append new sections only; never overwrite" rule, which had grown
> this file to 28 handoff sections / ~19.8k tokens loaded on **every** session. Rationale + measurements:
> `_PATTERNS/2026-07-19-token-efficiency-audit.md`.

- **CLAUDE.md is a working file, kept lean — not an archive.** It holds durable facts (Project Map,
  ROM primitives, token-saving rules) plus **only the latest 1–2 handoff sections**. Sessions no longer edit
  this file to hand off: `/handoff` writes a fragment (`_HANDOFFS/fragments/`, one file per session, raw
  material) and `scripts/handoff_fold.py molt` synthesizes ALL fragments into ONE arc block (Goal, What
  changed, State, Decisions, Open, ONE Next action, Cold-start recipe), versioned by
  `scripts/oracle.py next handoff`, refusing bookends; overflow moves to `_ARCHIVE/handoffs.md` by version
  (ADR-085 part (d) + 2026-10-06 amendment). Unmolted fragments are newer than any block below.
- **History is relocated, never deleted.** Older handoffs live in `_ARCHIVE/handoffs.md` and in git.
  "Never delete prior versions" is honored by archival, not by unbounded append into the hot path.
- `MEMORY.md` — keep recent entries live; relocate dead history to `_ARCHIVE/memory-archive.md`.
  New entries still go at top.
- Spec files — version field in front-matter; `*-v2` only on breaking schema change.
- Python scripts — never overwrite; create `*_v2.py` for breaking changes.


---

---

# Handoff — v3.118.0 (2026-10-07)

## Goal / true north
Land the day's open PRs safely and keep the decision-geometry explorer honest (no private text in the public feed), without burning the 5-hour limit on long Fable contexts.

## What changed
- Merged with --merge and receipts: #1070 (672a797a), #1064 (8ee8ff3b), #1065 (cc85c8b4, owner-set provenance tag; CI security review failed on "Credit balance is too low", local diff review found nothing blocking). #1073 (9 unrouted public pages deleted) was merged by another session; no repo link to them, 8 of 9 return 404 live, lewoof.html is deliberately routed to the gate.
- #1068 and #1069 merged by their own sessions. #1069's catalog was then served through the admin-gated warroom route (c220eb8b), which answers the counterpart-hostname disclosure question.
- Local security review of #1068 found the public /api/geometry feed leaked free-text `protecting` (up to 8 x 200 chars) in the shared base object. Fix e6413821 (gate `prot` on text fidelity, add non-text `protN`, client reads `protN`) landed AFTER #1068 merged, so it is on main only once PR 1082 merges.
- Worktrees: 16 stale ones pruned with bundles (cruft_sweep); live ones, zen-pasteur-85c635 (907 behind, 2 dirty) and pensive-hopper-b6feb8 (1 unmerged commit, 3 salvage claims) kept.

## Current state
- Specs are DRAFT: `runtime/specs/dopeness-eval-v0.md`, `runtime/specs/decision-geometry-cells-v0.json`, `_STATE/2026-10-07-tool-cluster-jtbd-map.json`. The adversarial verifier workflow (14 agents) recorded corrections that are NOT yet folded into the specs. Every refuted and unverifiable verdict plus the critic's missing, unverified and contradiction lists are committed at `_ARTIFACTS/decision-geometry-verify-2026-10-07/verifier-corrections-w7oi2kc36.md` (the full 357 KB JSON lives only on this Mac at `/private/tmp/claude-501/-Users-zharris-arcs-v9--claude-worktrees-compass-dopeness-audit-963f43/2a998756-827f-4413-8e5c-521f02be10e7/tasks/w7oi2kc36.output`, under `result.cells.verify`, `result.clusters.verify`, `result.critic`). Summary:
  - Cells: 12 of 46 claims refuted, 3 unverifiable. Key refutations: DELTA has two triggers (parent nci band shift as well as hasRed, `ygate.ts:170-180`); sessionVersion is parent.version + 1, not a count of session rows; driftState DRIFTING is outcome-driven (matched false) not version-driven; PrepSession.stakes/horizon equal Receipt.stakes/window by assignment so they carry no independent evidence; confidence = 1 is a ygate input so independence holds only for 2 to 5; inline prep can leave prepId null on a calibrated receipt; `observatory/page.tsx:30-36` already defines an L1 to L5 altitude rung map (off by one from the model's); the contract altitude sample uses a U+2013 en-dash so the `L(\d)-L(\d)` parse returns lo=hi=1 on the contract's own sample; "5R: no field" is false (ScanSignal.networkResonance exists, still unmappable to a receipt cell); D1 coverage L2 must read ~267 since coherencePct presence was not measured; the "0 of 267 by code path" for six columns rests on a route grep, not SQL.
  - Clusters: 4 of 16 spot checks refuted: `arcs_no_go_inventory.py` and `arcs_seed_bar.py` are not decision-lens members (post-hoc failure catalog; BAR there means Belief-Action-Rationale templates); `sugar_bulk.py` is a PRL CRM payload builder, not counterpart-facing; `fates.py` is the fate registry, not page authoring. The map also double-books 11 tools as both members and orphans.
  - Critic: `src/app/api/tribune/route.ts:205` writes batonId (so "no write path" is wrong for that column); `provenance` is client-settable by any signed-in caller; the founder userId is unrecorded so the founder cohort split is assumed; COURT and ONE_WAY are one predicate in `compass/route.ts` (same 96 rows by construction); the shipped `parseKairos` differs from the cell model's parse; ladder tier A's GREEN clause is not SHARP (CONTESTED renders DEGRADED); ladder fields use pseudo-paths not prisma names; the day-counting unit differs between tier D (sessionId) and tier B (userId).
- Admin fidelity shows no banner by design (only public and owner set one); the fidelity statement lives in the stats line.

## Decisions made
- Merge handled by the originating session; this session verified only and did not merge.
- Receipt logged in the fixed form with the JS-dispatched drawer open listed as unconfirmed rather than claimed as a click.

## Open decisions (waiting on Zach)
None.

## Open (other)
1. Merge PR 1082 (the prot fix). Until then the leak is live on main.
2. claude-security-review fails on every PR until the CI Anthropic key's org has credit (human).
3. GEOMETRY_PUBLIC defaults to on (open to anonymous callers); decide whether to default it off.
4. scripts/dependency_sweep.py is named in the night-moves skill but is absent on main.

## Next action
Fold the verifier corrections into `runtime/specs/dopeness-eval-v0.md` and `decision-geometry-cells-v0.json` (start with batonId write path and client-settable provenance), then mark them past DRAFT.

## Cold-start recipe
- Page: `public/pf-decision-geometry.html`; feed: `src/app/api/geometry/route.ts`; rewrites: `next.config.ts` lines 92 to 96 (playground) and 205 to 208 (app).
- Gate: `SMOKE_BASE_URL=https://playground.arcs.care npx playwright test tests/decision-geometry.spec.ts --reporter=line`.
- Feed shape check: `curl -s https://playground.arcs.care/api/geometry | head -c 600` must show no `"q":` and only `"t":"YYYY-MM-DD"`.
- Receipt: `2026-10-07--decision-geometry-explorer-verify-pr1068--ZH`.

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

### Notes: Lessons
- Claude in Chrome clicks on a canvas can land on neighbouring controls; prove a pick by dispatching the page's own pointer events and reading the drawer state, and record it as a dispatch, not a click.

> Molted from `_HANDOFFS/fragments/20261007T180720Z--claude-keen-hermann-e14d76.md` (branch `claude/keen-hermann-e14d76`, head `cc85c8b4`).

# Handoff — v3.117.1 (2026-10-07)

## Goal / true north
One generated inventory of every arcs.care surface, gated so a routed host can never again be missing from it.

## What changed
- #1066 merged (`4e4972a7`, `--merge`): server-side satoshi base-rate gate (`src/lib/satoshi.ts`), prompt anchor "fewer than 1 in 50" built from the same constants, same gate on the EPHEMERAL_SAVE path, 9 unit tests incl. the real `/api/compass` handler against the stubs. Receipts `2026-10-06--satoshi-base-rate-gate-pr1066--ZH` (PR open) and `2026-10-07--satoshi-base-rate-gate-merge-pr1066--ZH` (merge).
- **#1069** (open, branch `claude/vigorous-tu-599264`, not merged by request): `scripts/surface_catalog_emit.py` (stdlib) parses next.config.ts, src/proxy.ts and the src/app tree; emits `runtime/specs/surface-catalog.json` (286 rows, 88 hosts) and renders `runtime/warroom/surfaces.html`, served admin-gated at surfaces.arcs.care via /warroom/surfaces (domain added via `vercel domains add`, resolving). `--check` fails on a missing next.config host, a stale catalog (dates excluded) or a hand-edited page; wired into pre-commit and the CI gates job. Page is noindex + X-Robots-Tag.
- Kintsugi: first commit blocked at 23 detector findings; repaired in the emitter to 0 plus one scoped Inter exemption; seam booked in `_PATTERNS/kintsugi-visual-grammar-seams.md` (DESIGN.md label size 10px sits under the detector's 11px floor).
- AGENTS.md pointer; `_PATTERNS/2026-07-10-atomic-surface-map.md` marked superseded as the inventory.
- Handoff collision: this session's first molt took v3.116.0 at the same time as another session's; reset, merged main, molted again (the documented recovery).

## Current state
- PR #1069 open, merged with main, CI pending at handoff. Catalog findings: `prl.arcs.care/status/wp` routes to a missing file; 13 unrouted public pages. Two chips spawned and started by Zach as separate sessions.

## Decisions made
- Enforce the compass meaning of satoshi (rare, category-defining) in a deterministic server gate rather than a prompt-only rewording; the prompt line is derived from the gate's constants so they cannot drift.
- Merged on Zach's yes with the security-review check red for a credit error, not a finding.
- Zach: hold off on passcode-gating surfaces.arcs.care; it stays unlisted-but-readable for now.

## Open decisions (waiting on Zach)
1. Zach: Anthropic credit on the org behind the `ANTHROPIC_API_KEY` repo secret; re-run the security review on `4e4972a7`.
2. Zach: merge #1069 with `--merge` after CI, then confirm `curl -sI https://surfaces.arcs.care` returns the page with X-Robots-Tag.

## Open (other)
1. Canon collision, escalated not resolved: `operators/arcs_rom.py` SATOSHI_CRITERIA (nci >= 50, irreversibility <= 0.5, most receipts qualify) vs the compass rare-move meaning now enforced. Zach decides which definition the word keeps.
2. EX-ANTE to score: after 50 new receipts, re-run the audit aggregates (flagged vs unflagged by stakes, mode, doorClass, nci bucket) and check the rate is under 1 in 50.
3. The two chip sessions (prl status mismatch; unrouted public pages audit) land their own PRs.
4. Kit-wide: resolve the DESIGN.md label-size vs detector-floor contradiction (ledger 2026-10-07 seam 3).

## Next action
Merge #1069 with --merge once CI is green, then verify surfaces.arcs.care live.

## Cold-start recipe
- `python3 scripts/surface_catalog_emit.py` (emit) · `--check` (gate) · `--self-test`.
- Memory `subdomain-html-hosting-workflow` (domain add via CLI; MCP add_project_domain is 403).

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

### Notes: Lessons
- A red `claude-security-review` with "Credit balance is too low" is billing, not a finding; the other CI jobs use a placeholder key and stay green (memory `anthropic-api-budget-shared-cap-ci-drain` updated).
- Pull aggregates before touching a model flag: the inflation lived entirely in one mode/model/stakes cell, which made a two-condition bar sufficient.

### Notes: Lessons
- The Vercel MCP cannot add project domains (403); `vercel domains add <host> arcs-v9 --scope arcs-care` works before the route is even on main.
- The impeccable detector and DESIGN.md disagree on label size; for a new page use body size for labels.
- A molt deletes fragments before anything is committed: on an oracle collision the fragment body is gone, so keep the body in the scratchpad until the molt commit lands.

> Molted from `_HANDOFFS/fragments/20261007T174054Z--claude-mystifying-tesla-6bc6f3.md` (branch `claude/mystifying-tesla-6bc6f3`, head `90fcea9c`); `_HANDOFFS/fragments/20261007T174439Z--claude-vigorous-tu-599264.md` (branch `claude/vigorous-tu-599264`, head `1d8bd4dd`).
