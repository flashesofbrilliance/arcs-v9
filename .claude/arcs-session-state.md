# ARCS Session State

**Last updated:** 2026-07-08 (v3.7.0)
**Environment:** Claude Code (local), worktree `unruffled-chatelet-26794f`
**Branch:** `claude/uikits-templates-artifacts-87c0ca`
**Last commit (arcs-v9 main):** b7883fb — chore(consolidation): bar-raiser corrections [NCI:SKIP]

## v3.7.0 delta (this update)

- **Consolidation audit COMPLETE** — arcs-decision-receipts unique content ported to arcs-v9 in two commits:
  - `cf8b084`: field-os specs → `runtime/specs/field-os/`; fanatics+token routes in `next.config.ts`; canonical template `public/templates/call-brief-template.html`; `ui_artifacts` section in `_STATE/snapshot.json`
  - `b7883fb`: bar-raiser corrections — `kryptonite_scorer.py`+`waveform_optimizer.py` → `operators/`; 4 canon docs → `_CANON/living/`; 5 memory shards → `_MEMORY/` (git-tracked, replaces `~/.claude/projects/` which is machine-local)
- **`_MEMORY/` directory established** — git-tracked product intelligence now visible to cloud sessions; 5 shards committed
- **`_CANON/living/` directory established** — primary doctrine docs (v9-canon-operational, codex-v8.5, positioning, technical-overview) promoted from `arcs-v9-additional/`
- **Canonical call-brief template** — `public/templates/call-brief-template.html` with `{{PLACEHOLDERS}}` and authoring workflow comment
- **Snapshot coverage** — `_STATE/snapshot.json` now has `ui_artifacts` + `memory_shards` sections for cloud session bootstrap
- **Pending Architect decisions**: monomath-compiler + gold-coast → standalone repos (not arcs-v9); index.html + deep-activate.html → audit provenance before porting
- **`_STATE/snapshot.json` is 6d stale** — run `/init-state-sync` to refresh NCI counter and active brief roster

## v3.6.0 delta (prior)

- **fanatics.arcs.care LED placement fixed** — `.beat-led` converted from `position: absolute; top: 14px; left: 14px` (overlapping beat number) to `flex-shrink: 0` inline flex item, moved to first child inside `.beat-head`. Mirrors the diamond `◆` position: inline before the beat number on all 5 beats. [NCI:212]
- **Stray `</div>` removed** — removing beat-06 in prior session left an orphaned closing div that closed `.page` container before the CTA block, causing it to render full-width outside the 680px max-width container. Fixed by removing the extra div. [NCI:212]
- **CTA padding updated** — `margin-top: 32px → 40px`, `padding: 20px 22px → 24px` for consistent spacing with rest of page. [NCI:212]
- **Committed + deployed** — commit `971f95e`, deploying to production via `deploy-prod.sh`.

## v3.5.0 delta (prior)

- **fanatics.arcs.care LED refactor COMPLETE** — pulsing LEDs moved from vertical left-rail to horizontal SVG waveform circles (5 `filter: drop-shadow()` animations, color-matched per beat, staggered timing). Vertical `signal-wire` element and `beat-node` dots removed. Beat card `.beat-led` dots restored (6px dot, top-left, color-coded via `--nc` CSS var) for visual differentiation between cards. [NCI:207–209]
- **padding-left regression fixed + deployed** — `signal-sequence` `padding-left: 44px` was orphaned after removing the vertical rail. Set to `0` to align provenance beat cards with all other page sections. Commit `0246df6`, deployed to production. [NCI:210]
- **Subdomain QA COMPLETE** — all 13 deployed subdomains confirmed 200 OK (curl + visual). Zero 404s.
- **Fanatics security constraints re-confirmed**: fanatics.arcs.care, chris.arcs.care, cj-debrief.arcs.care, chase-intro.arcs.care, token.arcs.care, kelly-interview.arcs.care, todd-call.arcs.care — all ungated, no password protection.
- **Drift sentinel fired** — this session state update + CLAUDE.md Handoff v3.5.0 written per pre-compaction protocol.

## Status

- arcs-v9 Vercel: ✅ LIVE — `dpl_4ANhwAxWA3cG6gHVF5MBh3LXBR2k` READY, aliased to `app.arcs.care`
- fanatics.arcs.care: ✅ Beat LED dots + SVG timeline pulse + flush page layout — all live
- All prior open items from v3.2.0: unchanged (carried forward — see prior session state below)

## Open items (carried from v3.2.0, unresolved)

```
2.  settings.local.json leaked password (owdiiyvphyifukygvxhg)  BLOCKED ON ZACH
3.  vercel.ts migration                                          🔴 INCOMPLETE
4.  Trust contract page (route)                                  NOT STARTED
5.  DATABASE_URL rotation risk, xbbpiryokswwvcrcutge (ADR-005)  OPEN
6.  Validate SAGE NCI against real Outcomes                      OPEN
7.  Panel/Chip design system components (ADR-009)               READY
8.  ADR-006 branching strategy                                   READY
9.  arcs-care: flip NEXT_PUBLIC_CASE_STUDY_APPROVED             WAITING on Dan Pascone
10. Governance backlog #3 — consolidate 3 narrative logs        READY
11. Governance backlog #4 — drift-sensor                        Design done, build not started
12. Governance backlog #6 — DEWY commit/PR trailer stamp        Ready after #3
13. Orphaned Supabase tables                                     OPEN — needs Zach's input
14. 4 remaining Supabase advisor WARNs                          OPEN (deliberate)
```

## Next session

`/handoff-pickup` → julia.arcs.care drill feature (pre-call checklist → verbal drills for voice call practice; clarify: drill interaction model + who are Jack, Jill, Boardy) OR governance backlog #3 (log consolidation).

**Pending clarifications for julia.arcs.care drill feature:**
1. Drill interaction model — inline flip/reveal, modal, or sidebar?
2. Who are Jack, Jill, and Boardy? (referenced in julia.arcs.care pre-call checklist)

---

<!-- PRIOR SESSION STATE (v3.2.0) PRESERVED BELOW -->

**[v3.2.0 — 2026-06-23]**
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
