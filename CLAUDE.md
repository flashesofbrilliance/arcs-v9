@AGENTS.md
@WORLD.md

# Session orientation — read this much, and no more

This file (+ its `@`-imports AGENTS.md and WORLD.md) already loads automatically. That is your
baseline context. **Do not read further to "orient."**

- **To resume work:** read the latest `# Handoff` block below (bottom of this file) — nothing else.
  Or run `/handoff-pickup`, which reads `_STATE/snapshot.json` + the latest handoff only.
- **Progressive handoff (2026-09-04):** a global hook checkpoints git state to
  `_STATE/handoff-progress.jsonl` every turn-with-change, and asks for a `## Delta` in
  `_STATE/handoff-progress.md` at each compaction. Both are gitignored. `/handoff` folds them
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
  this file to hand off: `/handoff` writes a fragment (`_HANDOFFS/fragments/`, one file per session) and
  `scripts/handoff_fold.py fold` assigns versions, prepends the blocks here and moves the oldest to
  `_ARCHIVE/handoffs.md` (ADR-085 part (d), 2026-10-06). Unfolded fragments are newer than any block below.
- **History is relocated, never deleted.** Older handoffs live in `_ARCHIVE/handoffs.md` and in git.
  "Never delete prior versions" is honored by archival, not by unbounded append into the hot path.
- `MEMORY.md` — keep recent entries live; relocate dead history to `_ARCHIVE/memory-archive.md`.
  New entries still go at top.
- Spec files — version field in front-matter; `*-v2` only on breaking schema change.
- Python scripts — never overwrite; create `*_v2.py` for breaking changes.


---

---

# Handoff — v3.111.0 (2026-10-06)

> **Security-review gate stops failing re-runs red; a real API error still fails.** #909 (`6a29d549`), merged with
> `--merge` on Zach's yes. Receipt `2026-10-06--security-gate-dedupe-skip-pr909--ZH`.

## Shipped
- **#909:** `scripts/security_review_gate.sh` reads the action's `results-file` output (its scan step sets it first,
  so empty = scan never started) plus the cache-restored `.claudecode-marker/marker.json`. Empty + marker for this PR
  = `::notice` "already scanned at <sha>" and pass; empty + no marker = fail; scan ran = all #881 checks unchanged.
  Live proof: run 37474229559 (fresh, outcome=success, passed) and 37476233291 (skipped, notice, passed).
- The scan on #909 found 2 real bugs in the first draft, both fixed: a committed marker.json could fake a pass (now
  only an untracked marker whose `pr_number` matches), and marker fields went into a workflow command (now hex/digits only).

## Open (next session)
1. Broken-key path not run live (secret untouched); covered by the action code plus run 37400262799.
2. The `security-review` label never rescans (cache key is per PR): chip task_d4f6708c is running in its own session
   (`run-every-commit` on labeled; costs API budget, needs Zach's yes).

## Lessons
- Read a composite action's outputs for the signal: an output set on the first line of a step is a step-ran flag.
- Run the security scan on a change to the security gate: it caught the bypass in this one.

> Folded from `_HANDOFFS/fragments/20261006T140855Z--claude-handoff-security-gate.md` (branch `claude/handoff-security-gate`, head `6a29d549`).

# Handoff — v3.110.0 (2026-10-06)

> **CI repair + PR triage session: page gate fixed, billing-blocked runs re-run, two ledger items closed, stale PRs cleared.**
> Receipts (all `--ZH`): `2026-10-05--page-gate-merge-base-pr831`, `--security-review-scope-pr832`,
> `--secreview-skip-dependabot-pr868`, `--linkedin-queue-scheduled-pr661`, `2026-10-06--sess-013-close-pr896`,
> `--pl-011-purpose-guard-pr897`, `--eslint10-hold-tweaks-refs-pr903`, `--nftt-claim-batch-pr912`.

## Shipped (all `--merge`)
- **#831** fe-smoke page gate diffs `base...head` (merge-base) with fetch-depth 0. Proof: #802's pre-sync head gave 92 pages two-dot, none three-dot; a real page edit still gated.
- **#832** security review scoped to security paths (another session's PR, merged on Zach's go).
- **#868** skip claude-security-review when actor is dependabot (no secrets there). `@dependabot rebase` sent to #864 #720 #677 #557.
- **#661** LinkedIn queue: main merged in, the 2 conflicts kept the PR's scheduled text (Zach's call).
- **#896** SESS-013 closed: Zach dropped the anon INSERT **and** anon SELECT policies on legacy `public.sessions` in the SQL editor (tool call was declined twice); pg_policies verified only service_role SELECT remains.
- **#897** PL-011 closed: `scripts/purpose_guard.py` hard gate. No non-Anthropic model SDK or third-party analytics in `src/`; `track()` keys allowlisted. 5 planted violations each fail. The ledger's "aggregate anonymized only" wording was never on a page; the guard binds the live claims. Merged with the security review red from the API usage limit (Zach's go).
- **#903** tweaks-panel.jsx refs-in-render fixed; dependabot ignores eslint majors (eslint 10 crashes eslint-plugin-react 7.37.5, peer ^9.7).
- **#912** `scripts/nftt_claim_batch.py`, recovered from preserve commit 71169923 that sat on #715's branch. `build` offline verified; API paths not run.
- Closed: #799 (archived handoff), #134 and #556 (superseded / blocked upstream). #715 was already closed by Zach as superseded by #882. Local preserve commit 71169923 deleted (branch `claude/model-registry-drift-gate` reset to its own merge-of-main tip, never merged: its PR #715 closed without merge, content superseded by #882, merged as d97dc35f).

## Open (next session)
1. **#644** (Jarrod Wolf SSOT) not synced: its branch is checked out in worktree `zen-pasteur-85c635`.
2. 8 `react-hooks/refs` errors in `src/app` (observatory, JobsBoard, ChampionsBoard): own session running (chip task_7afcd523).
3. Dependabot PRs #864 #720 #677 #557: confirm the rebases ran and are green; #677 also had stale smoke failures.
4. Post-merge CI on main for the merges above never observed (in every receipt's unconfirmed list).

## Lessons
- A billing block can hit one job in an otherwise-running workflow: scan per JOB for 0 steps, not per run.
- `gh run rerun` replays the old workflow file and merge ref; to pick up a workflow fix on a dependabot PR, ask dependabot to rebase.
- Check a PR is still open and not rebuilt elsewhere before acting on it (#715 was closed and rebuilt as #882 hours earlier).
- A lint "fix" request can rest on a misread log: #556's real blocker was a plugin crash, not the refs error (that came from #557's log).

> Folded from `_HANDOFFS/fragments/20261006T140722Z--claude-handoff-v3-85.md` (branch `claude/handoff-v3.85`, head `9bf8ca27`).
