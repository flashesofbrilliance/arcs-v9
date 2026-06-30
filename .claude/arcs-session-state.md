# ARCS Session State

**Last updated:** 2026-06-23 (v3.2.0)
**Environment:** Claude Code (local), worktree `busy-chaplygin-22139c`
**Branch:** `observatory-cherry-pick` (pushed to origin, no PR opened yet — deliberate, Zach's choice)
**Last commit (arcs-v9):** e888cc4 — chore: fold in lockfile normalization + RLS doc project-ref fix

## v3.2.0 delta (this update) — see MEMORY.md [v3.2.0] for full detail

- **Critical production fix, live, independent of git/merge state**: Supabase project
  `xbbpiryokswwvcrcutge` (ARCS_v9) had `public.SageTrace` fully exposed — RLS disabled
  entirely, anon read/write/delete via PostgREST. Found via a real Supabase alert email,
  verified live with `supabase db advisors --linked` (the Supabase **MCP connection in this
  session cannot see this project at all** — wrong account/org; the Supabase **CLI** on this
  machine is correctly linked — use the CLI for arcs-v9 Supabase work going forward). Fixed
  with the ADR-008 deny-all pattern, re-verified 0 ERRORs after. Follow-up pass cleared 27 of
  31 remaining WARNs (perf-only `auth_rls_initplan` fixes + 1 redundant policy). 4 WARNs left
  deliberately unfixed — see Open items #13.
- **Task #5 (prose-rule audit) DONE**: `_PATTERNS/2026-06-23-prose-rule-enforcement-audit.md`.
  Zero of 6 in-scope `SKILL.md` rules have any real enforcement mechanism. Headline finding,
  independently re-verified: "inline styles only, no Tailwind, no className" has been violated
  at `src/app/layout.tsx` (the app root) since the first commit.
- **Task #7 (Observatory cherry-pick) DONE** — with a process catch worth repeating: the
  actual page (`src/app/observatory/page.tsx`) was **already on this branch** before this
  session started (this branch is literally named `observatory-cherry-pick`). A subagent was
  dispatched to redo it from scratch before that was checked — caught when the cherry-pick
  came back empty. The one genuinely-missing piece (removing the now-dead `/observatory`
  static rewrite from `next.config.ts`) is done and build-verified.
- **Trust contract v1.0 → v1.1**: `_CANON/trust-contract.md` §8 added, answering Zak's
  residual "how will you catch people at the fork" question. Zach's explicit call: new
  canonical section. Honest about current state — no proactive fork-detection exists yet.
- **Process findings, recorded as durable memory** (`~/.claude/projects/-Users-zharris-arcs-v9/memory/`):
  two delegated subagents hit the account's spend limit mid-task (finished by hand); one
  agent's doc citation could not have been a live read (no `node_modules` in its sandbox) —
  conclusion held on independent re-check, but the claimed verification method wasn't real;
  an absolute-path edit landed in the wrong checkout (`/Users/zharris/arcs-v9` main, a
  *different* branch with its own unrelated in-progress work) due to this repo's many parallel
  worktrees — reverted there, redone correctly in this worktree.

## Status

- arcs-v9 Vercel: ✅ LIVE — production unaffected this session. Pushing `observatory-cherry-pick`
  likely auto-triggered a Vercel preview build (confirmed via `vercel ls`: a Preview deploy
  exists, separate from Production) — non-destructive, doesn't touch `app.arcs.care`.
- arcs-v9 Auth: unchanged, still fully wired (see v3.0.0).
- arcs-v9 DB: `xbbpiryokswwvcrcutge` — **RLS gap closed this session** (see delta above).
  Several tables present in this project (`meeting_cards`/`risks`/`raci`/`dependencies`/
  `drift_signals`/`immune_sessions`/`immune_turns`/`pathogen_log`) have **no owning app found
  anywhere on disk** (checked arcs-v9, arcs-care-local, full home-dir grep) — all 0 rows,
  real open question for Zach, not yet resolved.
- **Two distinct password concerns — don't conflate them:**
  1. `settings.local.json` has a literal plaintext Supabase DB password baked into a
     `Bash(...)` permission-allow string — for project `owdiiyvphyifukygvxhg` (the OTHER,
     inactive project). This is governance-roadmap backlog item **#2, blocked on Zach**.
  2. The live `xbbpiryokswwvcrcutge` `DATABASE_URL` rotation risk (ADR-005 amendment,
     manually-set, not integration-managed) is a **separate, older, still-open** item — see
     Open items #8 below. Different project, different password, both real.

## ⚠️ Domain correction (read this first if picking up cold)

Unchanged from v3.0.0/v3.1.0 — `arcs.care` is not a separate site from `app.arcs.care`. See
`~/.claude/CLAUDE.md` and project memory `arcs-v9-arcs-care-domain-consolidation.md`.

## Open items (re-verified 2026-06-23, v3.2.0)

```
1.  ADR-016 auth.ts wiring                                   RESOLVED (carried, unchanged)
2.  settings.local.json leaked password (owdiiyvphyifukygvxhg) BLOCKED ON ZACH — confirm dead
                                                               or rotate; not this session's to fix
3.  vercel.ts migration                                      🔴 INCOMPLETE — carried, unchanged
4.  Trust contract page (route that renders trust-contract.md) NOT STARTED — different/older task
                                                               than the v1.1 content amendment done
                                                               this session; don't conflate the two
5.  DATABASE_URL rotation risk, xbbpiryokswwvcrcutge (ADR-005) OPEN — carried, still not
                                                               re-verified (separate password from #2)
6.  Validate SAGE NCI against real with-SAGE Outcomes        OPEN — carried, still no data
7.  Panel/Chip design system components (ADR-009)            READY — carried, untouched
8.  ADR-006 branching strategy (first-external-user gate)    READY — carried, untouched
9.  arcs-care: flip NEXT_PUBLIC_CASE_STUDY_APPROVED          WAITING on Dan Pascone — carried
10. Governance backlog #3 — consolidate 3 narrative logs     READY — unblocked, untouched
11. Governance backlog #4 — drift-sensor cadence/severity    Design done, build not started —
                                                               the long pole; blocked on #6/#7below
12. Governance backlog #6 — DEWY commit/PR trailer stamp     Ready after #3+#5 (✅#5 now done) —
                                                               forward-only, NEVER rewrite history
13. Orphaned Supabase tables, no owning app found            OPEN, NEW this session — see Status
14. 4 remaining Supabase advisor WARNs (deliberately unfixed) OPEN — 3 on the orphaned tables
                                                               above (unconfirmed ownership), 1 on
                                                               `sessions`' public INSERT (confirmed
                                                               intentional, arcs-care's compass widget)
```

Resolved this session, removed from the list: governance backlog **#5** (prose audit) and
**#7** (Observatory cherry-pick) — both DONE, see delta above.

## Key infra facts (for next session)

- **Supabase MCP is scoped to the wrong account/org for arcs-v9** — `list_projects` only shows
  `owdiiyvphyifukygvxhg` and `monomath-compiler`, both inactive, never `xbbpiryokswwvcrcutge`.
  Use the `supabase` CLI instead (`supabase link --project-ref xbbpiryokswwvcrcutge`,
  `supabase db advisors --linked`, `supabase db query --linked` — none need Docker; `db dump`/
  `push` do and will fail clearly if Docker isn't running).
- **This repo has 15+ active git worktrees** (`git worktree list`) — an absolute path like
  `/Users/zharris/arcs-v9/<file>` can silently resolve to the bare/main checkout instead of
  your session's own worktree, even mid-session, with no error. Confirm `pwd`/`git branch
  --show-current` before editing by absolute path if there's any doubt.
- All facts from v3.0.0/v3.1.0 (DB connection details, Vercel project IDs, CLI install
  location, `next.config.ts` turbopack root requirement) — unchanged, not repeated here.

## Prior session highlights (compressed — full detail in MEMORY.md history)

- v3.1.0: CANON_COLLISION (`BAR`/`KKL`) resolved via `/dual-bar-raiser`; `RC-OPS-001`
  (`arcs_inchworm_echo.py`) landed as a ROM Candidate, not yet ROM; 8-item governance
  roadmap + pathogen taxonomy written; a withdrawn citation caught same-session;
  `RECOIL-PROTOCOL.pdf` cross-referenced, independent convergence found.
- v3.0.0: S-tier copy rewrite; `Field.tsx` accessibility fix app-wide; 3 `ReflectLayer.tsx`
  bugs fixed; domain-topology correction (`arcs.care`/`app.arcs.care` are one deployment).
- 2026-06-19→21: SAGE efficacy infra shipped; NCI self-grade rubric wired; a real
  `decision_mode`/`door_class` spread-order bug found and fixed; `arcs_readonly` role +
  `BYPASSRLS` gotcha documented.

## Next session

`/handoff-pickup` → governance backlog #3 (consolidate 3 logs, sequencing point for #4/#6) or
#7-adjacent cleanup (orphaned Supabase tables question, item #13) are the most startable-cold
options. #2 and #5(DATABASE_URL rotation) both need Zach directly, not actionable solo.
