<!-- intent:begin -->
## Intent
- **Why:** The canonical ARCS monorepo (Zach, 2026-10-03): the product (compass, DEWY receipts, Y-gate), every arcs.care surface, the operator suite, the session/handoff machinery, and the private content folded in from dormant repos (`runtime/specs/field-os/`, `runtime/memory-export/`, each with an IMPORTED-FROM.md).
- **Done looks like:** See WORLD.md and the backlog in `_QUEUE/induced-backlog.jsonl`; this repo has no single done-state.
- **Not this:** Not one repo for everything: distributable packages with their own registry or marketplace identity (germinate, rosetta-shell, arcs-skills and its plugins) keep their own public repos. Handoff state lives in CLAUDE.md; intent lives here.
- **Status:** live (serves arcs.care, app.arcs.care and ~95 other aliases)
- **Last verified:** 2026-10-03 (Vercel `get_deployment("arcs.care")` returned project `arcs-v9`, READY at `165855f`)
- **Spec:** none at root (engineering specs live in `runtime/specs/`)
<!-- intent:end -->

<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

Loaded together with CLAUDE.md and WORLD.md (CLAUDE.md imports this file; no back-import, to avoid a cycle).

---

# ARCS v9 — Agent & DevOps Handbook

> Read WORLD.md first. It is not documentation — it is the physics of the world you're building in.

---

## What this repo is

**`github.com/flashesofbrilliance/arcs-v9`** — canonical ARCS v9 decision intelligence app.
Stack: Next.js 16 · Prisma 7 + SQLite (dev) / Supabase (prod) · Auth.js v5 · Anthropic SDK.
No Tailwind (removed 2026-07-11; it was an unused Day-1 scaffold remnant). Inline styles only in components (per WORLD.md); the sole stylesheet is `src/app/globals.css` (reset + keyframes + font tokens — things inline styles cannot express).

---

## Environment variables

| Var | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API for compass, jobs and other routes. Model per job lives ONLY in `src/lib/claude-models.ts` (`MODELS.<role>`; Python reads it via `scripts/arcs_models.py`). `model_id_gate.py` (pre-commit) blocks hardcoded ids; `model_drift_check.py` flags newer models at session start |
| `AUTH_SECRET` | Auth.js v5 session signing |
| `AUTH_RESEND_KEY` | Magic link emails via Resend |
| `DATABASE_URL` | Postgres/Supabase (prod only; SQLite used automatically in dev) |
| `RECOIL_PASSWORD` | **Retired.** Was a shared cookie gate for `/recoil*`; removed (it sat disclosed in git history). `/recoil` is now gated per-route by Auth.js session + `ADMIN_EMAILS` (`src/lib/admin.ts`), fail-closed. No code reads this var. |
| `ADMIN_EMAILS` | Comma-separated admin allowlist — interim RBAC for the internal `/recoil` index + reports (`src/lib/admin.ts`). Prod fail-closed if unset; dev passes through |
| `RECRUITHAUS_AMMO_PASSWORD` | Shared passcode for the gated recruiter ammo tier at `recruithaus.arcs.care/ammo` (`src/lib/ammo-gate.ts` + `src/proxy.ts` + `/api/recruithaus/unlock`). Fail-closed if unset; cookie holds a SHA-256 token, never the passcode |

---

## Routes & handlers

| Route | File | Purpose |
|---|---|---|
| `POST /api/compass` | `src/app/api/compass/route.ts` | **Core.** L0–L5 Claude pipeline → DEWY receipt + Y-gate |
| `POST /api/prep` | `src/app/api/prep/route.ts` | Create PrepSession (stakes/horizon/protecting/confidence) |
| `GET /api/brief/[id]` | `src/app/api/brief/[receiptId]/route.ts` | Cartography brief generation |
| `GET /api/guide/[id]` | `src/app/api/guide/[receiptId]/route.ts` | Step-by-step guide surface |
| `GET /api/history` | `src/app/api/history/route.ts` | Receipt history for user |
| Auth | `src/app/api/auth/[...nextauth]/route.ts` | Auth.js v5 magic link |

---

## Core lib

| File | Purpose |
|---|---|
| `src/lib/ygate.ts` | Y-gate 12D manifold → polarity × conviction × stability → state |
| `src/lib/db.ts` | Prisma client singleton |
| `src/lib/auth.ts` | Auth.js v5 config (magic link, Resend) |
| `src/lib/env.ts` | Env validation — throws on missing required vars |

---

## DEWY pipeline (compass)

```
question + prep context
  → Claude Sonnet 4.6 (L0–L5 system prompt)
  → JSON: { true_north, why, tributaries[3], nci_score, reasoning, ... }
  → computeYGate(parsed, prep, parent, sessionVersion)
  → prisma.receipt.create({ ...DEWY fields, ...yGate })
  → return receipt_id + full parsed output
```

**Tributaries** — EXACTLY 3, already implemented:
- `[0]` meta: deeper question beneath the stated one
- `[1]` challenge: uncomfortable truth / overlooked constraint
- `[2]` adjacent: cross-domain reframe

**Y-gate states → render resolution:**
`GREEN=SHARP · YELLOW/FORK=DEGRADED · SCRATCH/DELTA/DRIFT=GRAIN · PARADOX=MOIRE · RED=GRAIN`

---

## Prisma / DB

```bash
npx prisma migrate dev --name <description>   # create + apply migration
npx prisma studio                              # inspect data
npx prisma db push                             # push schema, no migration file (dev only)
```

JSON arrays stored as `TEXT` (SQLite compat). Do NOT use `Json` Prisma type until datasource is Postgres.

---

## Dev commands

```bash
npm run dev       # start (port 3000)
npx next build    # typecheck + build (preferred over tsc --noEmit — avoids TS5090 false positive)
```

---

## Agents & workers map

> **Tool discovery:** `/catalog <job>` recommends THE one right existing tool from the full inventory (`runtime/specs/tool-catalog.{json,md}`, regenerated by `python3 scripts/tool_catalog_emit.py`; the count is the `total` field there, never written in prose, so it cannot go stale).
>
> **Surface inventory:** `runtime/specs/surface-catalog.json` is one row per routed host+path (next.config.ts rewrites, src/proxy.ts host blocks, src/app routes), rendered at `surfaces.arcs.care` (`runtime/warroom/surfaces.html`, admin-gated through the `/warroom/[slug]` route). Regenerate with `python3 scripts/surface_catalog_emit.py`; `--check` (pre-commit + CI) fails when a host in next.config.ts is missing from the catalog. Never hand-edit the JSON or the page. Supersedes the July prose map in `_PATTERNS/2026-07-10-atomic-surface-map.md` as the inventory.

> **Moved to a path-scoped rule (2026-10-17):** the live-routes table, backlog table, foundation table, Operators Library table, the file census and the integration status now live in `.claude/rules/operators-and-workers.md`. It loads on its own when you read, write or edit anything in the operators folder or the API route handlers. To see it from anywhere, open that file or run `/prior-art`.

## Gotchas

1. **No new dependencies without asking.**
2. **Inline styles only in components** — no Tailwind, no CSS modules, no utility classes. Exactly two sanctioned exceptions: next/font variable classes on `<html>` in `layout.tsx` (framework mechanism), and the single `src/app/globals.css` (document reset, `@keyframes`, font tokens, reduced-motion). No other CSS files, no other `className`.
3. **JSON arrays are TEXT strings** — always `JSON.stringify()` before write, `JSON.parse()` after read.
4. **Build with `npm run build`, not bare `npx next build`** — for typecheck (not `tsc --noEmit`; TS5090 false positives on baseUrl) AND because the cloud shell exports `NODE_ENV=development`. A bare `next build` inherits that and crashes prerendering `/_global-error` with `Cannot read properties of null (reading 'useContext')` (React loads dev internals during static export). `npm run build` pins `NODE_ENV=production` so it's reproducible; Vercel already builds in production, which is why deploys were never affected.
5. **SQLite in dev, Postgres in prod** — don't use Prisma `Json` type until datasource is Postgres.
6. **`git worktree list`** before any git operation — active worktree changes between sessions.
7. **Commit style:** `type(scope): imperative [NCI:XX]` + `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`
8. **Deeper environment gotchas** (Supabase MCP blind spot, Prisma-7 adapter, Vercel CLI/env quirks, domain→project verify-live, subdomain hosting, concurrency discipline, HEIC/`sips`): see `_PATTERNS/durable-gotchas.md` — on-demand, open when the task touches that area.
9. **Sugar sandbox via Zapier MCP** (PRL work): raw GET/mutating actions on `SugarCRMCLIAPI` reach `prlresinstest.sugarondemand.com/rest/v11/` directly (connection 65663180 = sandbox; NEVER prod). `/rest/v11/bulk` takes 12+ sub-requests per call — build payloads with `scripts/sugar_bulk.py` (prod host refused by default). Zapier's editor is drivable via claude-in-chrome when Comet is logged in, but the permission classifier blocks *typing* into forms: Claude does structure/clicks/publish, the human types free-text fields.
10. **Session shell helpers**: `scripts/ship_docs.sh` (push→PR→merge, enforced docs-only gate, hang-kill+retry) · `scripts/sync_worktree.sh` (WIP-commit + merge origin/main, hook-state kept as ours, never stash) · `python3 scripts/oracle.py sync <ns>` (reconcile a lagging counter — counters drift when sessions mint off-oracle; audit first).
11. **Teleport to terminal when the work is mechanically scorable.** If a pass/fail can be written as a grep, a set-diff, a schema check, a diff, or an operator-client lambda over an `ls`-enum, do it in the shell — don't fan out agents. Reserve agents/LLM for judgment (reading for meaning, emergent tagging, VARIANT-vs-SUPERSEDED, synthesis). Scout deterministically to build the work-list and kill false positives first, then spend agents only on the residue. See memory `when-to-teleport-to-terminal-vs-agents`.
12. **Oracle-first numbering — NEVER infer an ADR/seed/receipt number.** Parallel sessions across harnesses (Claude Code, Hermes) that guess "highest + 1" collide (ADR-033/067 both doubled this way). Allocate via `python3 scripts/oracle.py next <ns>` and commit `_SEEDS/_oracle.json` — git's non-fast-forward rejection is the atomic lock. A pre-commit hook enforces this: `.claude/hooks/session-start.sh` arms it automatically when `core.hooksPath` is unset (2026-10-04); outside Claude Code, install once with `git config core.hooksPath scripts/git-hooks` (blocks any commit that duplicates an existing ADR number; warns on off-oracle numbers). Run `python3 scripts/oracle.py audit adr` to see collisions/gaps/next-free.
13. **Self-contained artifacts/pages (single-file HTML): ONE px `--measure` for body text, ledes full width, run the repo's own gates before shipping.** Never a per-element `max-width:NNch`; a lede spans the same width as its heading (standing preference, not a bug); run `scripts/artifact_wrap_lint.py` and `scripts/page_gate.py`, sweep 360 to 1440 including 700 to 1000, em-dashes 0. The full rule (tokens from the kit, the ledes exception, the verification list, memory pointers) is in `.claude/rules/self-contained-artifacts.md`, which loads when you touch `_ARTIFACTS/`, `public/` or `src/ui-kit/`.
---

14a. **Cross-harness reconciliation: never trust `~/.hermes/state.db`'s sessions table alone to answer "did Hermes do X."** It does not reliably record `git_repo_root`/`git_branch` for sessions that touched a repo — querying it directly undercounts real work (confirmed 2026-09-13: it showed zero arcs-v9 sessions while `session_search`'s FTS index surfaced real, repo-committing Hermes work from 2026-09-11, e.g. the cross-harness handoff push at commit `6c19ec6f`). Use `session_search` (FTS-backed, ground truth) to verify a harness's history before asserting "never happened" — a SQL-table absence is not proof of absence.

14. **Run repo scripts from YOUR worktree, never by the main-checkout absolute path.** `/Users/zharris/arcs-v9/scripts/*.py` is whatever branch the main checkout is parked on — often another session's dirty branch with a STALE copy. On 2026-09-08 I linted with the main-checkout `artifact_wrap_lint.py` (a 138-line copy with no MODE 5) while origin/main's is 296 lines and catches the exact narrow-lede-in-wide-container bug; every "wrap-lint clean" was a false pass and the bug shipped repeatedly. Use `./scripts/…` relative to your own worktree (which is cut from origin/main), or verify with `git show origin/main:scripts/<x>` before trusting a result. Same caution for any tool invoked by an `/Users/zharris/arcs-v9/…` absolute path. See memory `run-repo-tools-from-worktree-not-stale-main-checkout`. **Skills and slash commands too (2026-10-10):** Claude Code loads project skills and slash commands (under .claude/) from the MAIN checkout, not the worktree (verified: the skill list hot-reloaded when the main checkout moved). Keep the main checkout detached at origin/main; a session-start check (project skills drift script in scripts/) warns when it drifts.

15. **Frustration Gate (design pattern, default not favor).** When a bug class is recurring or high-frustration, don't just fix the instance — in the same change add the cheapest mechanical check that FAILS the build on the whole class (grep < static lint < headless assert), prove it fails-on-bad AND passes-on-good, and wire it into the always-run path (`npm test` / pre-commit). A symptom that survives multiple green-gated fixes means the gate is blind or you're solving the wrong problem — that should fire on round 2, not round 15. Full pattern + worked example: `_PATTERNS/2026-09-08-frustration-gate-pattern.md`.

16. **Operator numbering is the periodic table, nothing else.** `operators/docs/PERIODIC-TABLE.md` is the only enumeration (1-15 atoms · 16-21 boardroom · 22-25 chorus · 26-28 super-admin; Folksonomy=20, Librarian=21). An external "audit" (2026-09-27) invented a 1-19 map and bound it to files that do not implement those operators (`kryptonite_scorer.py` as Accountant, `audit_service/` as Librarian, `core/governance.py` as Immune). Never hand-write an operator→file map: regenerate `operators/OPERATOR-REGISTRY.json` with `python3 scripts/operator_registry_emit.py` (refuses to emit any binding whose symbol it cannot grep; `--probe` import-tests with `operators/.venv`; `--check` is on pre-commit). `core/governance.py` + `core/operators.py` import `loguru`/`pandas` that are not declared anywhere: they are dead until someone owns that dep decision.

17. **Merge with `scripts/safe_merge.sh <pr> <expected-head-sha>` (2026-10-20), which runs `gh pr merge --merge --match-head-commit`; never `--squash` or `--rebase`.** It refuses on a head mismatch, any non-SUCCESS or still-pending check (it waits, then times out), CONFLICTING, or a PR touching kit inputs while main has kit commits it lacks (generated kit files would merge stale; rebase and regenerate, 2026-11-13), and prints the merge commit plus a decision_receipt INSERT template; `--self-test` covers each refusal. A merge commit keeps the branch's own commits and the per-PR boundary that decision receipts cite; a squash or rebase lands as a 1-parent commit and erases both. Enforced since 2026-10-06 by the repo's merge-method setting (works on any plan, unlike branch protection): `allow_squash_merge` and `allow_rebase_merge` are `false`, so GitHub refuses a squash or rebase in the UI and the API (check: `gh api repos/flashesofbrilliance/arcs-v9 --jq '{squash:.allow_squash_merge,rebase:.allow_rebase_merge}'`). As a backstop, `scripts/squash_merge_detector.py` still checks daily (`.github/workflows/no-squash.yml`, fails red on any merged PR without a merge commit). `scripts/ship_docs.sh` already uses `--merge`.

18. **Capture inbox rule (Zach, 2026-10-04).** Any idea that surfaces mid-turn becomes a `spawn_task` chip or a `/witness` stub inside the same turn; nothing lives only in chat. The single read over every open-loop store is `/loops` (`scripts/open_loops.py`, read-only); same-day captures show under "Captured today, not filed", and a weekday 8:00 spoken digest lands as an Apple Note (scheduled task `arcs-open-loops-morning-note`). Memory `fork-mid-turn-prompts-into-sessions`.

19. **Neighbor scan before a merge, broadcast after (Zach, 2026-10-08).** Before changing or merging a file others cite, run `python3 scripts/neighbor_scan.py <path>` (no args: every file changed vs origin/main). It is read-only and lists citers, offspring (same-stem or child files) and other open PRs touching the same file. After the change lands, update each cite, regenerate each child, or post a note to the owning session; name the broadcast list in the receipt. Moves and deletes are gated: `scripts/archive_move_gate.py` (pre-commit) blocks a staged rename or delete while a live file still cites the old path (2026-10-18, after four scripts were archived with their citers unfixed); re-point the cite in the same commit. Memory `look-out-before-look-in-scan-concurrent-sessions-first`.

20. **Backlog rows carry a `state` enum (2026-10-10).** Every `_QUEUE/induced-backlog.jsonl` row has `state` from `runtime/specs/backlog-status.json` (OPEN READY HOLDING HELD RUNNING BLOCKED DONE COMPOSTED SUPERSEDED) and its prose in `status_note`; never write a `status` key. A claimed row is `RUNNING` with `claimed_by` + `claimed_at`. `scripts/backlog_status_check.py --check` gates it in pre-commit and CI; add `--gh` to flag rows citing a merged or closed PR, and RUNNING claims older than 3 days print as STALE.

21. **Phosphor is built from sources (2026-10-17).** Edit `_ARTIFACTS/phosphor-src/` (`page.tpl`, `style.css`, `app.js`), then run `python3 scripts/phosphor_build.py` to write `_ARTIFACTS/phosphor.html`; never hand-edit the built file (pre-commit runs `--check` and blocks a mismatch). The build only strips indentation from the script, so the kit tokens in the stylesheet stay verbatim: never trim anything inside the token sentinel block. Page cap 400,000 bytes applies to the built file (raised from 280,000 to 320,000 on 2026-10-17, amendment 43, and to 400,000 on 2026-10-18, amendment 57, both by Zach). The public copy (public/dj.html, served at dj.arcs.care) is written only by `python3 scripts/phosphor_build.py --release` at a release checkpoint (about every five shipped rows, after the full suite and a browser pass), so a merge does not change what the public sees. **Release holds (2026-10-24):** a feature Zach said to build but not release is listed in `runtime/specs/phosphor-release-holds.json`; `--release` refuses while its id is in the built page, and an override (`--allow-hold <id>`) is used only after his explicit go, with the entry removed in the same change.

22. **One owner per PR branch (Zach, 2026-10-20).** Only the session that opened a PR pushes to its branch. Any other session that wants a change sends the owner a message (SendMessage with its session id) and waits, or takes the branch over only on Zach's explicit go, building on the current remote head. Git rejecting a push because the branch moved means another writer is active: stop and ask, never force. Cause: on 2026-10-20 two sessions pushed rewordings to PR 1671 within 30 seconds of each other. For merging several PRs at once, use `scripts/merge_train.sh --lock` (ADR-085, still PROPOSED).

23. **Coding discipline (Zach, 2026-11-03).** Grug first, then the Karpathy guidelines: think before coding, simplicity first, surgical changes, goal-driven execution with a check before the code. Full text in `.claude/rules/coding-discipline.md`, which loads when you touch code.

24. **Design system SSOT and the kit wire (2026-11-16).** The kit's source of truth is `src/ui-kit/recoil-report/` (the numbered parts) plus `DESIGN.md` (rules) and `src/ui-kit/templates.json` (page templates). `src/ui-kit/kit-manifest.json` is GENERATED from them by `python3 scripts/kit_pull.py manifest`; its `parts` list is the live part count, so do not hardcode a count in prose. The wire tools, all read-only advisors that never edit a page: `scripts/kit_attract.py <backlog row | text>` (nearest parts for a job), `scripts/kit_rank.py` (three options as JSON), `scripts/kit_gate_results.py` (stored static page_gate results per part, regenerate on demand), `scripts/kit_optionboard.py` (the internal option board). `scripts/kit_job_ratchet.py` fails if the parts that name a backlog job fall below `runtime/specs/kit-job-coverage-floor.json`; raise it with `--bump` when coverage rises. After merging main into a branch, regenerate the tool catalog before pushing, or CI's `gates` job fails on the script count; a red `gates` can also be main's own time-decayed `source-trust.json` (merge main).

## Receipts or it didn't happen

Every merge, deploy, or publish action MUST end with exactly one Decision Receipt row in the
`decision_receipt` table (Supabase project `xbbpiryokswwvcrcutge`, ARCS_v9), in the fixed form:
`question, horizon, stakes, mode, what_confirmed[], what_unconfirmed[], operator, event_at, job_id, tool_id`
(+ `source_repo`, `refs[]`). `job_id` = the backlog row the work served (`job:backlog:<id>`); `tool_id` = the tool
used (`tool:<kind>:<name>`, e.g. `tool:script:safe_merge.sh`). `scripts/safe_merge.sh` prints both in its template
(derived from the PR, else a `<REQUIRED ...>` placeholder that fails the column CHECK). A receipt without them counts
against Sprint 5's coverage check (at least 70% by 2026-11-03, else they become mandatory;
`_PATTERNS/2026-10-20-jtbd-s5-preregistration.md`); check it with `python3 scripts/receipt_coverage.py --export`. Matched by any verifier against real git/GitHub/Vercel state —
anything not verifiable goes in `what_unconfirmed`, never `what_confirmed`. Do not invent field values.

**The ledger is append-only (2026-10-20).** A database trigger refuses UPDATE and DELETE on `decision_receipt`. To correct a receipt, insert a new row whose `supersedes` names the old `receipt_id`; the old row stays. See `runtime/specs/decision-receipt/2026-10-20-append-only.sql`.

An action without a logged receipt is not considered complete, regardless of whether the underlying
merge/deploy/publish succeeded. This applies to every harness (Claude Code, Hermes, or future) equally.

> **Column constraints (verified 2026-09-11 via `pg_constraint`):** `horizon` ∈ {`today`, `this-week`,
> `this-quarter`, `1-3y`} · `stakes` ∈ {`low`, `medium`, `high`, `critical`} · `mode` ∈ {`QUICKMOVE`,
> `PLAN`, `COURT`}. Anything else is rejected by a CHECK constraint (`QUARTER`/`MEDIUM` failed once).
> `what_confirmed`, `what_unconfirmed`, `refs` are `text[]`; `event_at` is timestamptz.
> Nullable in the schema since 2026-10-20 (`runtime/specs/decision-receipt/2026-10-20-job-tool-ids.sql`), required by the form above: `job_id`
> (`job:<source>:<key>`) and `tool_id` (`tool:<kind>:<name>`), the JTBD graph atoms the action served and used;
> CHECK-enforced prefixes. NULL is legal only for rows written before the form required them.
>
> Write paths (verified 2026-09-10): Supabase MCP `execute_sql` against `public.decision_receipt`,
> or the `log_arcs_session` MCP tool **only once** its `arcs_session_log` schema is extended to carry
> the receipt form — the tool as-shipped grades *sessions* (jtbd/effort/NCI), not ship events, and its
> table was never applied. The first two receipts (rubric v1.3 ship, NFTT PR #394) landed 2026-09-11
> with `receipt_id`s `2026-09-10--rubric-v1.3-ship--ZH` and `2026-09-10--nftt-ledger-pr--ZH`.

---

## Connected systems

| System | Repo | Role |
|---|---|---|
| Perplexity MCP | `flashesofbrilliance/perplexity-mcp` | Claude Code search tool (search/reason/chat) |
| arcs-care (dormant) | `flashesofbrilliance/arcs-care` | The original arcs.care site + PLG funnel. NOT live: every arcs.care domain is served by this repo's `arcs-v9` Vercel project (verified 2026-10-03). See its AGENTS.md intent block |
| GIGI substrate | `flashesofbrilliance/gigi` | Local-first fiber-bundle DB — seam at compass/route.ts (TBD P3) |
| arcs-canon | `flashesofbrilliance/arcs-canon` | Dewey YAML knowledge library |
| arcs-hq | `flashesofbrilliance/arcs-hq` | TS skills runtime — being archived (P1) |
