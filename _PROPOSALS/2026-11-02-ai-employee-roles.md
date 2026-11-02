---
title: AI-employee roles as job reqs (tools for jobs, backlog as jobs to be done)
date: 2026-11-02
status: PROPOSED (no builds until Zach rules)
source: read-only sweep of .claude/agents, .claude/skills, .claude/commands, runtime/specs/tool-catalog.json, _QUEUE/induced-backlog.jsonl at origin/main 05f5d6f6
---

# AI-employee roles as job reqs

Prior art: `cruise-control` agent (CANDIDATE), `/backlog-graph`, `/readiness`, `/loops`, `/catalog`,
the `ai-employees:hire` plugin skill (read, not installed), memories
`every-spawned-session-gets-a-backlog-row-first`, `jtbd-reuse-existing-tool-before-inventing`,
`session-budget-discipline-cap-parallel-molt-long`.

## Short answer

Yes, but mostly by giving existing agents a job req, not by writing new agents. The repo already
has 25 agents, 24 project skills, 18 commands and 260 scripts (378 catalog rows). What it lacks is
an owner per cluster of backlog work: 288 live rows (178 OPEN, 71 HOLDING, 17 READY, 13 RUNNING,
4 BLOCKED, plus 37 HELD) and no role that holds any cluster end to end. Eight roles cover the
clusters. Six reuse an agent that exists; two are thin new seats. None needs a new dependency.

## What a job req contains

Borrowed from the ai-employees kit, mapped onto what this repo already has:

| Kit file | Here | Why keep it |
|---|---|---|
| `CONTRACT.md` (mission, limits) | the agent `.md` front-matter and body | already the place Claude Code loads |
| work board | the backlog rows the role owns (`route.owns` or a new `owner` key) | backlog is the single job store |
| `SCHEDULE.md` | one scheduled task per role, read-only roles only | fire times live in one place |
| `brief-latest.md` (today, waiting on you, blocked) | one line per role in the `/loops` morning note | Zach reads one page, not eight |
| `RELEASES.md` ships empty | the one-way-door list: merge, publish, send, push to main, canon change | nothing irreversible without Zach |
| `## Corrections` at the end of every file | same, appended to each agent `.md` | a dated correction outranks the body on the next run |

Recommendation: borrow the three ideas in the last three rows (one brief, empty releases list,
a Corrections section). Do not install the eight kit employees: their roles (GTM, SEO, ads, sales,
support) do not match this backlog, and each brings its own board, dashboard and schedule, which is
a second job store.

## The roles, ranked by leverage

Unattended means it can run on a schedule with read-only tools and report. Needs go means Zach
approves each run or each output before it leaves the machine or touches main.

### 1. Backlog Steward (reuse `cruise-control`, promote from CANDIDATE)

- **Mission:** keep the job store honest so every other role starts from true state.
- **Owns:** `backlog-fate-triage-2026-10-18` (READY), `pressure-rotting-loops`, the 13 RUNNING
  claims (stale ones flagged after 3 days), the mechanical half of `jtbd-orphan-jobs-groom`
  (163 orphan jobs).
- **Tools:** `scripts/backlog_status_check.py --check --gh`, `scripts/backlog_ripeness.py`,
  `scripts/backlog_freshness.py`, `scripts/open_loops.py`, `scripts/universe_jtbd_adapter.py --check`,
  `/backlog-graph`, `/readiness`, `/catalog`.
- **Gates:** fates stay human (NOTOMATION); it proposes renew, promote, compost or supersede and
  never writes them. Bash guard hook already exists (`cruise-control-bash-guard.py`).
- **Done looks like:** zero STALE RUNNING claims, ripe rows each carry a proposed fate, orphan count
  falls each week, one line in the morning note.
- **Run mode:** unattended (report only). Fates need go.
- **Chain position:** root. Every other role reads its output.

### 2. Receipts Clerk (new thin seat, read-only plus drafts)

- **Mission:** no shipped action without a receipt, and outcomes get closed.
- **Owns:** the Sprint 5 coverage check (at least 70% by **2026-11-03, tomorrow**; else job_id and
  tool_id become mandatory), `universe-outcome-capture` (READY; 2 of 247 receipts closed),
  `accountant-weekly-first-unattended`.
- **Tools:** `scripts/receipt_coverage.py --export`, `scripts/accountant_weekly.py`,
  `operators/arcs_accountant.py`, the receipt template printed by `scripts/safe_merge.sh`.
- **Gates:** the ledger is append-only; the clerk drafts INSERT rows, it never writes. Outcomes are
  supplied by the human, never inferred.
- **Done looks like:** a weekly list of merges with no receipt, each with a drafted row; the
  coverage number in the morning note.
- **Run mode:** unattended for the audit; every ledger write needs go.
- **Chain position:** depends on 1 (receipts cite `job:backlog:<id>`). Feeds 6.

### 3. Line Producer (reuse `brand-line-producer`)

- **Mission:** nothing renders publicly below the repo's own gates.
- **Owns:** the design and render cluster, the largest live cluster (about 54 rows: tokens.css
  migration, font-stack drift, HUD and page passes, NFTT template contrast).
- **Tools:** `scripts/page_gate.py`, `scripts/artifact_wrap_lint.py`, `scripts/voice_gate.py`,
  `/page-gate`, `impeccable` skill and its four agents.
- **Gates:** read-only; returns PASS or BLOCK. Builds go to a session per row.
- **Done looks like:** every public-surface PR carries a PASS line.
- **Run mode:** unattended as a reviewer; the fixes need a build session and go.
- **Chain position:** parallel to 2, after 1.

### 4. Librarian of Claims (reuse `claims-skeptic` + `claim-index-sme`; add `dream-scout` once PR 1946 merges)

- **Mission:** what the repo says about itself stays true: claims, memory, lattice and seedbank.
- **Owns:** the drift findings the session-start sentries print (lattice epoch 27 days stale,
  seedbank missing `rfp-engine`, universe snapshot 9 days stale, findings past their due beat),
  `claims-atom-seed-gate`, `freshness-zeno-ceiling`.
- **Tools:** `scripts/dream_mine.py`, `scripts/prior_art.py`, `scripts/operator_registry_emit.py --check`,
  `scripts/surface_catalog_emit.py --check`, `scripts/tool_catalog_emit.py`.
- **Gates:** reports drift, never rewords a page or a canon file (canon collisions escalate, never
  resolve under write-lock).
- **Done looks like:** each sentry finding has a fate or a row within one beat.
- **Run mode:** unattended.
- **Chain position:** parallel; its findings become rows that 1 grooms.

### 5. Chief of Staff, job search (reuse the `recoil-*` and `forge` skills; no new agent)

- **Mission:** move the monday.com offer and the warm-path pipeline; prep before, close after.
- **Owns:** `monday-leadership-call`, `monday-offer-terms`, `req-reality-dim-board-and-champion`
  (READY), `warm-path-campaign-v0`.
- **Tools:** `/recoil-prep`, `/recoil-close`, `/recoil-ship`, `/precall-brief`, `/forge`,
  `counterpart-gauntlet` workflow, `scripts/voice_gate.py`.
- **Gates:** draft first; Zach sends every message; ex-ante receipt before any counterpart send;
  never attribute an unconfirmed identity.
- **Done looks like:** each call has an ex-ante receipt before and a recoil close after.
- **Run mode:** needs go for everything outward. Highest stakes, lowest autonomy.
- **Chain position:** depends on 2 (ex-ante receipts). Top goal in `_STATE/intentions.jsonl`.

### 6. Filing Paralegal (new thin seat)

- **Mission:** keep the patent filing chain moving without a new disclosure.
- **Owns:** 27 `filing-*` rows. Seven are READY and every one is a Zach (human) step: audit log,
  off-repo channels, conception evidence, prior filings, counsel, who saw it, anonymize detail.
- **Tools:** `scripts/filing_workback.py` and its ledger.
- **Gates:** three write-lock rows (`filing-wl-file`, `-preprint`, `-outreach`) are one-way doors;
  it never touches a public surface (`filing-public-surface-decision` is Zach's).
- **Done looks like:** a one-page packet per READY step so Zach's part takes minutes, and the
  ledger shows each date VERIFIED or open with an owner.
- **Run mode:** needs go. Its value is prep, since the blockers are human.
- **Chain position:** independent chain; `filing-select-counsel` gates the rest.

### 7. Platform Steward (reuse `claude-code-config-auditor` + `platform-standards-auditor`)

- **Mission:** the harness itself stays cheap and correct.
- **Owns:** main-checkout drift (session start today: main at 0cc8d65f, origin/main at 05f5d6f6, so
  new agents do not load), `anthropic-spend-monitor` (BLOCKED on a Zach console step),
  `revoke-old-anthropic-keys`, `ci-orbstack-linux-vm-runners` (READY).
- **Tools:** `scripts/model_drift_check.py`, `scripts/squash_merge_detector.py`, the skills-drift
  session-start check.
- **Gates:** never touches keys, settings or security config; reports only.
- **Run mode:** unattended for audits; any fix needs go.
- **Chain position:** parallel; unblocks every role, since agents load from the main checkout.

### 8. Phosphor Producer (formalize the existing owner session; no new agent)

- **Mission:** ship the Phosphor rows through the release checkpoint.
- **Owns:** about 42 `phosphor-*` rows.
- **Tools:** `scripts/phosphor_build.py` (`--check`, `--release`), `runtime/specs/phosphor-release-holds.json`.
- **Gates:** `--release` only at a checkpoint and never over a hold without Zach's go.
- **Run mode:** needs go for releases. Ranked last because it does not serve the current goal.

## Not proposed

- New review agents: `ciso-review`, `sre-review`, `privacy-review` stay as reviewers the roles
  call, not owners.
- The Staff of Chiefs and idea-* candidates: they are thinking tools for one prompt, not job
  owners. Leave them CANDIDATE.
- A role per operator: operator numbering lives only in `operators/docs/PERIODIC-TABLE.md` and the
  generated registry; this proposal binds no operator to a file.

## Goal-based chain

```
goal: monday offer (intentions.jsonl)
  5 Chief of Staff  <- 2 Receipts Clerk  <- 1 Backlog Steward (root)
  3 Line Producer, 4 Librarian, 7 Platform Steward  <- 1   (parallel)
  6 Filing Paralegal  (own chain, gated by filing-select-counsel)
  8 Phosphor Producer (own chain, release holds)
```

7 is the hidden prerequisite for all of them: until the main checkout tracks origin/main, any
new or promoted agent does not load.

## Rulings needed from Zach

1. Promote `cruise-control` to Backlog Steward (unattended, report only)? Recommended first.
2. Receipts Clerk as a new read-only seat, run before tomorrow's 70% check?
3. Add an `owner` key to backlog rows (schema change to `runtime/specs/backlog-status.json`), or
   keep ownership in this file only?
4. Borrow the Corrections section and the one-line brief from the ai-employees kit; do not install
   the kit. Agree?
5. Which, if any, of 6 and 8 to staff now, given the 4-session budget?

## Corrections
