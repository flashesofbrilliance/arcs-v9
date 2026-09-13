# Handoff — 2026-09-11 · Forge queue runbook (resume-tailors thread)

> Pickup for draining the jobs-board forge queue. Self-contained. Verified against live
> git + jobs.arcs.care at 2026-09-11 ~22:45 ET. This session's parent handoff:
> `_STATE/handoff-2026-09-10.md` (its job-search trunk items 1–2 are now DONE — see below).

## What this session closed (all committed + pushed to `resume-tailors`)

| Item | Proof |
|---|---|
| Merged origin/main into `resume-tailors` (was 398 behind; 0-conflict forecast held except append-only hook logs → exact-line union, nothing dropped) | `62620ca0` |
| Job-search harness inputs committed (role packets, alerts, scored ledger, applied-Google PDF, `nftt-gates.sh`) | `1e50f42f`, `af3d7fe1` |
| snapshot.json refreshed (was 2026-08-27) | `f2c0ee02` |
| **Scan→score: DONE board-side, zero residue.** Local mirror resynced 54→205 rows, rubric v1.3, bands 104 PURSUE / 46 CONSIDER / 55 PASS | `9c42bbe6` |
| **Proof-of-run: Tenex Associate FDE built end-to-end** (edit-from-seed of Charlie Health, 2pp, air-gap clean, mirrored) + seed-leak sweep across 71 bundles (6 fixed, incl. accenture←Basis title leak, amex/deshaw←Listen Labs, avepoint←Camunda, elev8 jobid artifact) | `d9e48193` |

## Key facts the next session needs

1. **The board is the SSOT, not the repo.** `jobs.arcs.care` (arcs-v9 prod alias) holds 205
   scored rows; `runtime/job-search/*.jsonl` is a mirror — resync from `/api/jobs`, don't trust it.
2. **Token:** `set -a; . /Users/zharris/.arcs/jobs-pipeline.env; set +a`.
   The Vercel copy is **Sensitive** — `vercel env pull` returns an 11-char placeholder that 401s.
   Real token is 64 chars. This cost this session ~20 minutes; banked to memory 2026-09-11.
3. **Tailoring = forge queue**, not a repo script cycle. `swipe right → queued → built` via
   `scripts/forge_edit_from_seed.mjs` (cheap, resume-only, ~1/3 tokens) or full forge for advancing roles.
4. **Tiers** (rubric in `runtime/specs/target-role-scan.json`): t1 ≥0.8, t2 ≥0.7, t3 ≥0.52.
   t1/t2 = auto-cut; **t3 = confirm with Zach before spending a cut.**

## The queue as of 2026-09-11T22:45 ET — 34 runs

- 13 × t1 (auto) · 10 × t2 (auto) · 11 × t3 (confirm first: Distyl, Hopper, Citi×2, RapidSOS,
  EVERSANA, Brex, Radar, Instagram, Rippling, Bloomberg)
- Clusters: PM 11 · Other 11 · FDE 7 · Product-Eng 3 · Applied-AI 2. All five clusters have a
  seed on the board (verified vs forge-bundles.json): FDE=tenex, Applied-AI=listen-labs,
  PM=mercury, Product-Eng=morgan-stanley, **Other=sentilink "New Leader - Pitch Us"** — that
  Other seed is shape-dubious (CEO-adjacent exec cut) for sales/strategist roles; per-row judgment, ask Zach.

## Drain procedure (repeat until empty or out of steam)

```bash
cd /Users/zharris/arcs-v9
set -a; . /Users/zharris/.arcs/jobs-pipeline.env; set +a

# 1) pick the top queued row in a SEEDED cluster (prints target + seed, no model spend):
node scripts/forge_edit_from_seed.mjs --auto --dry-run

# 2) build it (fetches JD via LinkedIn guest API locally — needs residential IP, this machine):
node scripts/forge_edit_from_seed.mjs --jobid <id>

# 3) QC (see pitfalls below) — then it's auto: registered in runtime/specs/forge-bundles.json,
#    board PATCHed to built, mirrored to iCloud, ledger line appended.
```

Per-batch: commit `runtime/specs/forge-bundles.json` + `_STATE/job-search/forge-cost-ledger.jsonl`
+ any `_ARTIFACTS/forge-*` changes (they're tracked here) with `fix|feat(forge): ... [NCI:SKIP]`.
Pre-commit hooks (wrap-lint, integrity-gate) run and pass on clean bundles.

## QC after EVERY build — the tenet the script does NOT enforce

The script's air-gap greps cover em-dash + scoring vocab only. **Seed-identity leaks pass it.**
After each build, run:

```bash
S=<slug>; grep -oE '<title>[^<]*</title>|Tailored ·[^<]*' _ARTIFACTS/forge-$S/resume-$S.html
# footer + title must name THIS target; also:
grep -ic "$(python3 -c "import json;print((json.load(open('_ARTIFACTS/forge-$S/cost.json')).get('seed') or 'zzz').split('-')[0].title())")" _ARTIFACTS/forge-$S/resume-$S.html
# ^ nonzero = seed's company leaked; also grep for 'jobid ' artifacts in footers
```

If leaked: fix HTML → re-render `chrome --headless=new --print-to-pdf` → `pdfinfo` Pages=2 →
`pdftoppm` PNGs → regenerate `-ats.txt` → re-copy to `~/Library/Mobile Documents/com~apple~CloudDocs/ARCS/resumes/$S/`.

## Known-open governance items (found this session, NOT fixed)

- **Invariant↔script drift:** `jobs_trigger_eval.mjs` FAILs `built-has-no-url` ×69 — it asserts
  built rows have NO url, but `forge_edit_from_seed.mjs`/`forge_finalize.sh` set url at `built` by
  design. One side is stale doctrine. Decide which, then patch the other.
- **`forge_finalize.sh` assumes full-forge layout** (`page.html`, `-ats.pdf` naming) — the
  edit-from-seed bundles don't match it; `forge_edit_from_seed.mjs` does its own finalize inline.
  Don't run forge_finalize on edit-from-seed bundles.
- **Integrity gate (non-blocking)** flags snapshot cites of ~20 paths not on origin/main —
  mostly the untracked loose docs (below); they need a home.
- **Loose docs still untracked** (from 2026-09-10 handoff, unchanged): `release-state-audit-2026-09-10.md`,
  `audit-translator-validation.md`, `docs/audit-service-hosting-scope.md`,
  `docs/decision-memo-creative-tim-template-audit.md`, `docs/frontend-theming-curated-bases.md`,
  `docs/mui-theme-reference-memo.md`, `_STATE/verify-three-loose-ends.md`, plus orphan scripts
  (`_patch_handoff_bugs.py`, `ship-scott-loop-v2.sh`, `public/static-serve.py`, `scripts/gen_tailor_icons.py`)
  — keep-or-kill decision.
- **Ledger worktree** `.claude/worktrees/nftt-ledger-not-story` clean+merged — `git worktree remove`
  + delete branch (other sessions' worktrees also accumulating — ~60 parked).
- **PRL** still blocked on Todd. **OSS queue** empty. Unchanged from 2026-09-10.

## Not-doing / hold

- **Receipt:** `2026-09-10--forge-resync-proof-run--ZH` in `decision_receipt` (this session's
  merge/commit/build/sweep, confirmed/unconfirmed split). Hosted viewer confirmed auth-gated
  (agent browser → 307 magic-link); local page PNGs visually verified clean + Tenex-identified.
- **11 "Other"-cluster queued rows** (Perplexity AI Strategist, Edra AI Strategist, sales-engineer
  shapes): the only Other seed is SentiLink's exec cut — shape-mismatched for these. Options: a
  fresh full forge (expensive), or fold into FDE/Product-Eng if the shape truly fits — judgment
  call per role, ask Zach.
- Somatic/HCI collection: HELD (memory).

## Reading sequence for the fresh thread

1. SUBSTRATE: `WORLD.md` → `CLAUDE.md` → this runbook.
2. STRUCTURAL MAP: `AGENTS.md` + `_STATE/snapshot.json` (head d9e48193+).
3. COMPONENTS: `scripts/forge_edit_from_seed.mjs` (the worker, 127 lines) →
   `runtime/specs/forge-triggers.json` (what fires when) → `scripts/forge_finalize.sh` (full-forge sibling) →
   `src/app/api/jobs/edit-from-seed/route.ts` (the model call) → `runtime/specs/forge-bundles.json` (registry).
4. SYNTHESIZE: queue state via `/api/jobs` (fact 1) → drain t1/t2, confirm t3 list with Zach,
   settle the invariant-drift item.

## Insights register

- *Self-diagnosis —* "score the 36 unscored" from the 2026-09-10 handoff was solving a stale
  mirror. The board had been re-scored to v1.3 with the queue drained to built. Read from SSOT first.
- *Hard evidence —* seed-leak class: edit-from-seed's model patch can drop a footer/title edit;
  5 of 70 pre-existing bundles shipped with foreign-company footers or a leaked `jobid` string.
  The air-gap greps can't see it. Fixed sweep `d9e48193`.
- *User-framing —* "ship minimal, get paid": one proof-of-run + runbook beats 34 blind builds tonight.
