# ARCS v9 — Memory Log

> **Versioning convention:** append new entries at top; never delete prior versions.
> Format: `## [vX.Y.Z] YYYY-MM-DD — <what changed>`

---

## [v3.1.0] 2026-06-23 — Engineering governance roadmap (tasks #1-8), RC-OPS-001 landed, BAR/KKL canon collision resolved

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Environment: Claude Code (local), continuation of the same 2026-06-23 session as v3.0.0
- Branch: `claude/dreamy-ardinghelli-56bbfa` + direct commits on `main` via `frosty-kepler-b69f51` worktree

### What landed (commits `7f1df53`..`3474d10`, 10 commits)
| Commit | What |
|---|---|
| `7f1df53` | `_PATTERNS/2026-06-23-governance-roadmap.md` — 7-item dependency graph (parallel/sequential/interlocking/entangled relationships between the backlog items v3.0.0 surfaced) |
| `d079674` | Kintsugi-mapped pathogen taxonomy (`SNAPSHOT_STALE`, `VERSION_DIVERGENCE`, `CREDENTIAL_EXPOSED`, `TOPOLOGY_INVERSION`, `PHANTOM_OPEN_ITEM`, `ORPHANED_ARTIFACT`, `SILENT_SENSOR`, `UNCLOSED_CEREMONY`, `UNENFORCED_CONVENTION`, `ACRONYM_DRIFT`) + fat-tail/long-tail pre-mortem on the roadmap itself |
| `7fff8f6` | **CANON_COLLISION resolved**: `BAR` macro meant two different things in `ADR-020` (Baseline/Asymmetric/Ruin — a risk-tier enum) vs `.claude/arcs-canon.md` (Bayesian/Adversarial/Ruin — the analytical lens). `KKL` meant two unrelated things (Kairos/Kairos Lock/Chronos vs Known-Known/Known-Unknown/Loki). Routed through `/dual-bar-raiser`; Architect ruling applied: arcs-canon.md's BAR wins, ADR-020's risk-tier row relabeled "risk tier," ADR-020's timing triad renamed `KKL`→`KLC`. Both files now cross-reference each other. |
| `a2e32fd` | "5D 5W 5C 5R 5H" S-tier rubric resolved via `/dual-bar-raiser` (5 Dimensions / Who-What-Where-When-Why / Consonance-Confidence-Conviction-Coherence-Cohesion / Risk-Resonance-Reflection-Refraction-Refutation / How at 5 altitudes) — logged as `IMPL_GAP` in `.claude/arcs-canon.md`, not yet a formal ADR |
| `0eca22c` | **`operators/arcs_inchworm_echo.py` landed as `RC-OPS-001`** (ROM Candidate, explicitly NOT yet ROM). Golden Inchworm + Orthogonal Echo Detector, gated behind an Observatory period. This is the **third** implementation pass in-session (v1 → v8.5 → v8.5.1) — each independently executed and verified, not trusted from description: v1 had 4 confirmed bugs (golden-thread noun-extraction bug, needle double-"before", dead `orthogonality_fn` injection, OM/canon mismatch); v8.5 fixed 2, regressed `orthogonality_fn` to non-injectable, added a needle nested-quote bug; v8.5.1 (the landed version) fixes all of it, confirmed via independent execution + an explicit injection test proving the fix is real, not just claimed. A parallel v8.5.1 candidate (two-axis `ExecGrade`/`TriuneState` dataclass design) was reviewed and rejected — its boolean-feature scoring counts `False==False` as a match, letting deliberately-dissimilar domains in its own test suite score as a confident "OM" echo. |
| `227be29`, `19b7a05`, `90aad7b` | `_PATTERNS/2026-06-23-s-tier-execution-plan.md` — per-task plan for #1-7 with Funhouse Optics applied, then a Perplexity-Space-sourced addendum that was **fetched and found not to support its own citation** (URL pointed at unrelated monetization content) — withdrawn same-session rather than left standing. |
| `3474d10` | Cross-referenced Zach's `RECOIL-PROTOCOL.pdf` (the ARCS corpus's own retrospective self-audit) against this session's findings — the corpus's own `Consonance ★★★★☆` self-grade ("funhouse performative residue... flagged in Kairos Shavasana audit") independently converges with this session's repo-level findings (RC-OPS-001's freshness, the BAR/KKL collision). Two audit methods, same finding — named as a genuine Orthogonal Echo. |

### Open backlog — 8 tracked items, NONE built yet (see TaskList, source of truth for status)
1. Build local-only git backup repo for `~/.claude` globals — **S-tier, ready, no dependencies**
2. Rotate/confirm-dead leaked Supabase password in `settings.local.json` — **blocked on Zach**, smallest scope/highest real stakes
3. Consolidate arcs-v9's 3 overlapping narrative logs (`MEMORY.md`/`CLAUDE.md` handoff/`.claude/arcs-session-state.md`) — **S-tier, ready**; sequencing point, must land before #4b/#6b
4. Drift-sensor cadence/severity/display — design done (Y-gate severity via Time-Quality-ROM decay × BAR ruin-risk), **build not started** — the long pole. Blocked by #6 (needs trailers to check ADR-vs-commit consistency) and #7 (needs Observatory for display)
5. Audit prose-rules across `SKILL.md`/`AGENTS.md`/`CLAUDE.md`/`WORLD.md` for enforcement gaps — **S-tier, ready**, scope to `SKILL.md` first
6. Design + retrofit DEWY commit/PR stamp (`ADR-Ref:`/`Y-Gate:` trailers) — **ready conditional on #3+#5 landing first**; forward-only, never rewrite history (highest-irreversibility item in the whole plan if mishandled)
7. Cherry-pick orphaned Observatory commit `35070a3` from stale `/Users/zharris/arcs` clone — **S-tier, ready**; also the shared dependency for #4's display AND RC-OPS-001's own promotion gate
8. Reformat the S-tier plan doc into the corpus's own canonical Section 1-7 format (True North → Kairos Map → Signal Physics → Hyperstition Arc → REQ/SPEC/PLAN → Decision Receipt+NCI Grade → Next Irreversible Step), per `RECOIL-PROTOCOL.pdf` page 9 — deferred for budget this session

### Honest self-assessment (asked for directly this session, not volunteered) — CORRECTED below
When pressed on whether an "independent" read of `RECOIL-PROTOCOL.pdf` was genuinely uncorrelated: no — this session was already primed to find claimed-vs-verified gaps before reading it. That observation stands and is the actual standing bar (name the priming honestly when asked for an "independent" check). **What does not stand, corrected after Zach pointed it out:** an earlier draft of this assessment used that priming to push back on the deck's `Conviction ★★★★★`/`Coherence ★★★★★` self-grades, treating the BAR/KKL collision and RC-OPS-001's freshness as evidence the corpus overclaims its own coherence. That's a scope error — **arcs-v9 is only ~20% of the ARCS corpus**; the rest lives and compiles in Perplexity Space. Findings about contradictions *in this port* are not valid evidence about the *corpus's* self-grade, which was assessed against the whole thing. The accurate framing: **port lag, not corpus incoherence** — and port lag is exactly what `/dual-bar-raiser`'s Architect/Implementer split exists to catch, which it did, correctly, today. Separately: the priming itself isn't something to apologize for — Zach named it as the same **productive discord** mechanism `RECOIL-PROTOCOL.pdf` itself describes as the corpus's actual generative engine (friction → Loki Test → ROM). The self-check was for him, using this session as the instrument, not a check on the session itself.

### Next session starts at
A dedicated cold-start prompt was written for a fresh, zero-context thread — see `_STATE/cold-start-v3.1.0.md`. Don't re-derive the dependency graph or pathogen catalog; both are written down in `_PATTERNS/2026-06-23-governance-roadmap.md` and `_PATTERNS/2026-06-23-s-tier-execution-plan.md`.

---

## [v3.0.0] 2026-06-23 — S-tier copy rewrite + a11y fix + domain-topology correction

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Environment: Claude Code (local), worktree `claude/dreamy-ardinghelli-56bbfa`
- Branch: `claude/dreamy-ardinghelli-56bbfa` → merged to `main` (commits `60a4f71`, `efb1af7`, `69250b4`)

### Artifacts landed (arcs-v9)
| File | What changed |
|---|---|
| `src/organisms/Home.tsx`, `src/app/page.tsx` | S-tier copy rewrite — retired "boardroom-grade," "render through the fog," internal pipeline jargon from all homepage copy |
| `src/organisms/CompassForm.tsx`, `src/molecules/PipelineTakeover.tsx` | Loading/placeholder/CTA copy aligned to new register; one example decision swapped |
| `src/app/prep/page.tsx` | "When do you decide?" vs "When will you know if it worked?" — disambiguated two previously near-identical horizon fields |
| `src/organisms/Brief.tsx`, `src/app/brief/[receiptId]/page.tsx`, `src/app/brief/[receiptId]/opengraph-image.tsx`, `src/organisms/ResultView.tsx`, `src/molecules/ReceiptPreviewWidget.tsx`, `src/molecules/FatedGrid.tsx` | "Cartography Brief" → "Decision Brief" everywhere; FATED axes color-coded; Brief layout restructured (8 Vercel toolbar threads resolved: conviction placement, FATED placement, sticky share footer, tributaries promoted to "Where to Navigate Next") |
| `src/ui/Field.tsx` | **Accessibility fix** — every input/textarea/select now gets a real `id`/`name` (auto-derived from label) + proper `<label htmlFor>`. Fixes an audit finding across every Field instance app-wide. |
| `src/organisms/ReflectLayer.tsx` | 3 bugs fixed: kernel lost on harden click, meditate collapse/expand state bug, shavasana converted from full-screen modal to inline accordion carousel with working prev/next navigation |
| `src/emails/welcomeEmail.ts`, `src/emails/receiptEmail.ts`, `src/app/layout.tsx`, `src/app/api/compass/route.ts` | Retired-tagline sweep — "render through the fog to earned clarity" → "Your judgment. Sharper." across metadata + email templates |

### Infra
- Vercel CLI upgraded `54.7.1` → `54.14.5` (Homebrew formula `vercel-cli`; a separate `npm i -g` install was shadowed by it — left in place, harmless but redundant)
- `@vercel/config` added as a new dependency; `vercel.json` migrated to typed `vercel.ts` — **see Open gaps, this migration is incomplete and not on main**

### Cross-repo / topology correction (the big one this session)
Discovered and corrected a stale belief — including one I personally asserted mid-session before being corrected by the operator — that `arcs.care` and `app.arcs.care` were separate codebases (the old `arcs-care` PLG repo vs. this one). **They are not.** Confirmed live via `get_deployment`: `arcs.care`, `www.arcs.care`, `app.arcs.care`, `resume.arcs.care` are all aliased to this repo's production deployment. The standalone `arcs-care` Vercel project is `live: false`. Fixed in three places: `~/.claude/CLAUDE.md` (repo table + new standing verification protocol), and two new files under `.claude/projects/-Users-zharris-arcs-v9/memory/` (`arcs-v9-arcs-care-domain-consolidation.md`, `verify-domain-topology-live-not-from-memory.md`).

### Open gaps
- 🔴 **vercel.ts migration incomplete** — current `main`'s `vercel.json` (re-added by other concurrent work) has `experimentalServices` (Python `sage` route) + `crons` that the committed `vercel.ts` branch doesn't represent. Migration attempt aborted mid-merge rather than risk silently dropping those. `vercel.json` remains canonical on `main`; `vercel.ts` only exists on the feature branch, unmerged.
- 🟡 **Observatory recoverable** — stale local clone `/Users/zharris/arcs` (do not use — see CLAUDE.md) has one orphaned, never-pushed commit (`35070a3`) containing a full 1174-line interactive `/observatory` Next.js page. Current `main` only has the static `public/observatory/` demo. Not superseded, not yet cherry-picked.
- 🟡 **Trust contract page** — `_CANON/trust-contract.md` exists on `main` (committed earlier, separately) but isn't surfaced anywhere on the live site. Now confirmed this repo IS the right place for that page (per the domain correction above). Not started.
- 🟡 `_DECISIONS/ADR-026-debrief-calendar-invite-vs-email.md` — untracked draft sitting in the `frosty-kepler-b69f51` worktree, never reviewed or committed.

### Next move
1. `/handoff-pickup` → read `_STATE/snapshot.json` (recaptured this session, was 15 days stale before)
2. Pick one: trust-contract page build, Observatory cherry-pick, or finish the vercel.ts migration
3. Re-verify DATABASE_URL rotation status once Supabase MCP reconnects (was disconnected mid-session)

---

## [v2.6.0] 2026-06-09 — Figma recoil report + resume.arcs.care architecture gates (ADR-024)

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Environment: Claude Code on the web (cloud) — model `claude-sonnet-4-6`
- Branch: `claude/amazing-rubin-z3sv1a` → merged to main

### Artifacts landed

| Action | Detail |
|---|---|
| Created | `runtime/recoil/2026-06-08-figma-recruiter-screen.md` — ARCS Recoil Report for Jun 8 Figma recruiter screen. NCI 72→58 (Δ-14). Y: YELLOW/MEDIUM/WATCH. HOLD verdict. Recruiter: Hayden. HM: unconfirmed. |
| Created | `src/app/recoil/page.tsx` — Document UIKit FE page (sidebar-nav + scrollable body). Signal delta table, ex-ante receipt, confidence bars, survivable next steps, recoil analysis, drift sentinel. |
| Created | `_DECISIONS/ADR-024-resume-arcs-care-architecture-gates.md` — DECIDED. Two gates resolved: (1) Scan = input/routing page, auto-runs on load when opportunityId in URL; (2) Single Vercel deployment, (userId, opportunityId) composite RLS. Full OpportunityScanOutput schema. Build sequence steps 1–10. |
| Amended | ADR-024 amended post-/dual-bar-raiser audit: scan trigger corrected to auto-run; table renamed to `opportunity_scans`; enum field types for recruiter_altitude + rhetorical_resonance; added fit_breakdown/silence_map/raw_jd_text; added Open Questions section. |

### Key architectural decisions (ADR-024)
- **Scan layer = input/routing page, not document destination.** Scan output pre-fills compass; full artifact lives at `/brief`.
- **Single Vercel deployment.** All opportunities scoped by `(userId, opportunityId)` composite key. API route layer is primary enforcement (Prisma bypasses RLS).
- **Auto-trigger:** `/scan/[opportunityId]` runs scan on mount if opportunityId in URL; paste-first if not.
- **OpportunityScanOutput table:** `opportunity_scans` — fit_score (0–100), recruiter_altitude (low/mid/high), rhetorical_resonance (analytical/relational/executional/visionary), north_star_signal, fit_breakdown (jsonb), silence_map (jsonb), raw_jd_text.
- **Signal Brief:** collapsible accordion (collapsed by default) at top of `/compass`; sidebar drawer at ≥1024px.

### Pending build sequence (ADR-024 steps 1–10)
1. New repo: `arcs-resume` (Next.js 16 · Prisma 7 · Supabase · Auth.js v5)
2. ADR-025: Supabase migration — `opportunity_scans` table
3. Input surface: `/` (paste resume + JD + alternatives → mint opportunityId → redirect)
4. Scan API: `POST /api/scan` → Claude → write OpportunityScanOutput → redirect to `/compass/[id]`
5. Compass surface: pre-fill contract, Signal Brief panel, editable question
6. Brief surface: UIKit sidebar-nav Profile Scan layout
7. Prep, receipt, recoil surfaces (port from arcs-v9)

### Cross-repo notes
- `arcs-v9`: ADR-024 committed to `_DECISIONS/`. No other arcs-v9 changes required.
- `resume.arcs.care`: new repo — ADR-024 governs all build decisions downstream.

---

## [v2.5.0] 2026-06-05 — ADR-023 superionic goal lattice + Observatory wired (branch: observability-milestone-mapping)

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Environment: Claude Code on the web (cloud) — model `claude-opus-4-8` (undercover; configured id)
- Branch: `claude/observability-milestone-mapping-345ho` — **NOT merged to main**
- Session goal: crystallize the goal-lattice observability model as a decision record; ship a clean Observatory demo

### Artifacts landed (10 commits ahead of main, `9f669fa..bbeb8a8`)

| Action | Detail |
|---|---|
| Created | `_DECISIONS/ADR-023-observability-goal-lattice.md` — DECIDED. Observability = inferred weighted folksonomy DAG over receipts, held in a "superionic" phase band by three governed counter-forces. Includes FMEA + Conductor-loop forward arch. |
| Created | `runtime/specs/lattice-pressure-rom.json` — ROM v0.1.0. Pins edge-decay (L2) / contrarian-injection (L4) / calcification-guard (L3) + phase_band; L7-governed constants, self-tuning FORBIDDEN. |
| Created | `scripts/lattice_sim.py` — structural load-test harness (anterior + posterior modes). |
| Created | `public/observatory/*` + `scripts/build_observatory.py` — repo-agnostic timeline generator; `--attribution show|hide` (hide = strip-to-subject, drops bodies where Co-Authored-By / session URLs live). Deployed `data.jsx` regenerated clean for Deloitte-facing demo. |
| Fixed | `next.config.ts` turbopack.root pin; absolute asset paths (actual blank-page render fix). |

### Key architectural decisions (ADR-023)
- **Lattice over tree, folksonomy over taxonomy** — multi-parent goals = DAG; inferred from receipt trail, never declared (declaring = NOTOMATION breach).
- **Observation moves nodes→edges** — watch edge-weight tightening, not node-state; the superordinate goal *precipitates* out of the high-weight attractor.
- **Three counter-forces = one phase-control loop**, each guarding a different L-level. Calcification (preferential attachment) is the failure mode; the buttresses bracket it.
- **Adversarial grounding (5-agent deep research, 2026-06-05):** 4 over-claims corrected — irreducibility does NOT bar declaration; no monotone-complexity theorem; rising regular-language complexity = enrichment not calcification (LOW-complexity is the calcified pole); DAG is well-motivated, not computationally required. Calcification backing = preferential-attachment dynamics, NOT the CA-complexity result.
- **PR/build gate:** L6 — blocked until real-corpus Zipf baseline measurable at 100+ receipts (same gate as ADR-020). ADR records the model; build is deferred.

### Crosswalk / sync state (the reason this consolidation matters)
- The cloud setup script fetches `_STATE/snapshot.json` **from main**. This branch's snapshot will not reach the next cloud session until merge → **sync gap recorded in snapshot `_sync_gap_warning`.**
- This branch touched ZERO infra: no Vercel/env/DB/migration changes. Deploy + DB facts carried forward unchanged.
- `/arcs-handoff` (local slash command) does not exist in cloud; `/handoff` skill is the equivalent.

### Cross-repo serialization decision (2026-06-06) — DO NOT RE-IMPLEMENT HERE
- The branch-serialization / "deep write lock" protocol is **canonically owned by the Perplexity-space ARCS instance.** A parallel implementation was started in arcs-v9 this session (protocol doc + `write-lock.json` + `arcs_write_lock.py`) and **discarded before commit** — building a second copy is the exact cross-instance drift the protocol exists to prevent (dual-bar-raiser: Architect-routed, forking flag raised, user routed DISCARD).
- **Chosen design = per-branch state files:** each branch owns `_STATE/branch-<slug>.json`, never overwrites the shared snapshot/session-state; `main` reconciles on merge (conflict-free by construction). arcs-v9 ADOPTS this convention for `/handoff`; it does NOT host the lock-manager. Future sessions: do not rebuild the engine here — pull from the Perplexity instance if arcs-v9 ever needs it.
- `/dual-bar-raiser` has no cloud-skill equivalent; applied manually this session.

### P-track / next
| Track | Status |
|---|---|
| ADR-023 model | ✅ DECIDED — build gated at 100+ receipts |
| Observatory demo | ✅ Clean `data.jsx` deployed (attribution hidden) |
| Merge to main | 🔴 OPEN — closes the cloud snapshot sync gap |
| Panel/Chip (ADR-009) | 🟡 READY |
| ADR-006 branching | 🟡 READY (first-external-user gate triggered) |

---

## [v1.4.0] 2026-05-27 — RLS live on all 9 Supabase tables; ADR-008

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Session goal: Enable RLS on Supabase before first external user

### Artifacts landed

| Action | Detail |
|---|---|
| Applied | RLS enabled on all 9 tables via Supabase MCP `apply_migration` |
| Created | `scripts/rls-policies.sql` — deny-all for `anon` + `authenticated` roles |
| Created | `_DECISIONS/ADR-008` — documents why `auth.uid()` policies are wrong for Auth.js v5 + Prisma superuser architecture |
| Committed | `9970c3f` |

### Key architectural decision (ADR-008)
- Prisma connects as `postgres` superuser → bypasses RLS unconditionally
- `auth.uid()` is always NULL (Auth.js v5 ≠ Supabase Auth JWT)
- Correct pattern: deny-all for `anon`/`authenticated`; user isolation stays at app layer (ADR-001)
- Future migration path documented: switch to Supabase Auth → then row-level policies become viable

### P-track status
| Track | Status |
|---|---|
| P0: arcs-v9 → GitHub | ✅ Done |
| P2: Perplexity MCP | ✅ Done |
| P4: arcs-v9 → Vercel | ✅ Done — READY deploy live |
| RLS gate | ✅ Done — this session |
| P3: arcs-care PLG funnel | 🟡 Specced, Phase 1 not started |

---

## [v0.9.0] 2026-05-27 — ADR framework, _QUEUE bus, GitHub Action, COCD weave, deployment audit

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Working environment: FleetView / Claude Code
- Session goals: Build Perplexity↔Claude Code decision bus; run meta-prompt (sync + critique + COCD weave)

### Artifacts landed

| Action | Detail |
|---|---|
| Created | `_DECISIONS/` — ADR framework with DEWY-native template |
| Created | `_DECISIONS/ADR-001` — Auth gate: app-level only, no Supabase RLS |
| Created | `_DECISIONS/ADR-002` — DB split: SQLite dev / Supabase prod + P4 unblock checklist |
| Created | `_DECISIONS/ADR-003` — arcs.care COCD weave: NCI 52/100 audit, 3 pathogens, COCD as hero frame |
| Created | `_DECISIONS/ADR-004` — mcp.arcs.care DNS fix: domain not wired to perplexity-mcp (404) |
| Created | `_QUEUE/` — implementation queue (PENDING.md + per-ADR pickup notes) |
| Created | `.github/workflows/adr-queue.yml` — GitHub Action: auto-processes new ADRs → _QUEUE/ on push |
| Created | `~/.claude/commands/arcs-research.md` — `/arcs-research` slash command (Perplexity → ADR → commit) |
| Updated | `arcs-rom-manifest.md` — Tier 2 table: arcs-care READY + deployment ID, perplexity-mcp updated, mcp.arcs.care 404 flagged, arcs-v9 registered |

### Deployment audit findings (2026-05-27)

| Surface | Status | Deployment ID |
|---------|--------|---------------|
| arcs.care | ✅ READY | `dpl_4TBqvWxUbuXZ6cNT53TiqJyxaCRE` |
| perplexity-mcp-kohl.vercel.app | ✅ READY | `dpl_6JUGdNvCEhDPvz9pDmXYBcQnW62b` |
| mcp.arcs.care | ❌ 404 | DNS not wired — ADR-004 is the fix |
| arcs-rcs | ❌ ERROR | Root cause unknown — needs triage |

### arcs.care design critique (NCI: 52/100)

- **Top pathogen 1:** "10x lighter" — unverifiable, AI-noise, no receipt grounding
- **Top pathogen 2:** Unsequenced dual CTA (Compass vs. Lab compete without flow logic)
- **Top pathogen 3:** No ARCS-native vocabulary above the fold — site reads as generic AI decision tool
- **True North:** Replace hero with COCD frame. Sequence CTAs as phases 1+2 (Calibrate/Orient) and 3+4 (Chart/Detect).

### COCD mapping (translation layer, not new doctrine)

| Phase | L-stack | ARCS artifact |
|-------|---------|---------------|
| Calibrate | L0–L1 | PrepSession |
| Orient | L2–L3 | Receipt + Y-gate |
| Chart | L4 | Decision Receipt + Brief |
| Detect | L5 + Drift Sentinel | Outcome + Observatory (not yet built) |

### Open items

- ADR-004: wire `mcp.arcs.care` DNS (10-min Vercel dashboard task)
- ADR-003: implement COCD weave in `arcs-care` repo (P1, this quarter)
- ADR-002: P4 deploy still blocked on Supabase creds
- ADR-001: userId filter audit on all API routes (READY, no blocker)

---

## [v0.8.0] 2026-05-27 — Housekeeping: stale Part IV draft deleted, exports/ gitignored, GitHub Projects board created

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Working environment: FleetView / Claude Code
- Session goal: Clean repo state, scaffold GitHub Projects board

### Artifacts landed

| Action | Detail |
|---|---|
| Deleted | `_CANON/book-ii/part-iv-sessions-api.md` — stale DO NOT COMMIT draft; canonical Part IV already exists |
| Updated | `.gitignore` — added `exports/` to suppress scan output files |
| Created | GitHub Projects board — `https://github.com/users/flashesofbrilliance/projects/1` |

### GitHub Projects board structure
- **Title:** ARCS v9 — Canon & Product
- **Stage field:** Not Started → Research → Receipt → Build → Refine → QA → Done
- **Issues linked:** #1–#5 (all Done)
- **Book II Part cards:** Parts I–VI (all Done)
- **Use:** Add new sprint issues/cards and move them forward as work progresses; `/handoff` can update card stages

### No blocking question

---

## [v0.7.0] 2026-05-27 — Book II Parts V & VI promoted to CANONICAL; Issue #5 COMPLETE; dual-bar-raiser skill registered

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Working environment: Claude Code (`arcs-v9` main) — drift detection / memory repair session
- Session goal: Reconcile MEMORY.md drift (v0.5.0 → v0.7.0); close Issue #5

### Artifacts landed (not previously logged)

| Commit SHA | File | What it is |
|---|---|---|
| `087ef22` | `_CANON/book-ii/part-v-the-accumulation-protocol.md` | CONDITIONAL CLEAR applied — 10 upstream audit findings addressed (§5.1–§5.6); three-state receipt taxonomy, constitutional range formally defined, mandatory debrief scoped to lineage-citing sessions |
| `087ef22` | `_CANON/book-ii/part-vi-the-shared-court.md` | CONDITIONAL CLEAR applied — 9 findings addressed (§6.1–§6.5); L5 presence rule for co-signing, gate-refusal→HOLD→Arbitration routing, formal declaration mechanism |
| `b6e59e4` | Both Part V + VI | **Promoted to CANONICAL v1.0.0** — Architect ratification received 2026-05-26; no further structural changes required |
| `05312cb` | `.claude/arcs-dual-bar-raiser.md` | Dual-bar-raiser skill — two-agent workflow (Claude Code owns edits/commits; Architect/Bar-Raiser owns canon structure + upstream audits) |

### Sprint closure

| Issue | Status |
|---|---|
| #2 DEWY Receipt Schema | ✅ DONE |
| #3 Time ROM | ✅ DONE |
| #4 Compass → DEWY Flow | ✅ DONE |
| #5 Book II Canon | ✅ DONE — All 6 Parts CANONICAL |

**Issue #1 (P0 Backlog Sprint 1) — COMPLETE.** All sub-issues resolved.

### Book II canon final status

| Part | Title | Status |
|---|---|---|
| I | From Firehose to Compass | ✅ CANONICAL |
| II | Core ROM Axioms | ✅ CANONICAL |
| III | Constitutional Court & Agency | ✅ CANONICAL |
| IV | (held — see v0.4.0) | ✅ CONDITIONAL CLEAR → CANONICAL |
| V | The Accumulation Protocol | ✅ CANONICAL v1.0.0 |
| VI | The Shared Court | ✅ CANONICAL v1.0.0 |

### Open gaps (carry forward)

```
globals.css                     🟡 DECISION NEEDED — Tailwind import vs. WORLD.md inline-styles-only rule
.env.example                    🟡 LOW — stale FastAPI/Railway refs (ARCS_API_URL, ARCS_API_KEY)
P4: arcs-v9 → Vercel preview    🟡 IN PROGRESS — blocked on DATABASE_URL + Supabase keys
NCI progressive grading         📋 BACKLOG — cross-session tracking not yet implemented
```

### Next move for next session
1. Decide next sprint: P4 Vercel deploy unblock OR new canon/feature sprint
2. If deploy: Supabase dashboard → Settings → Database → Connection strings → set on Vercel → `prisma db push` → `vercel deploy`
3. If canon: new sprint scoping needed (Book III? Observatory? ATG?)

---

## [v0.6.0] 2026-05-26 — Book II Part VI drafted (The Shared Court); dual-bar-raiser workflow established

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Working environment: Claude Code (`arcs-v9` main)
- Session goal: Draft Book II Part VI; establish two-agent workflow protocol

### Artifacts landed this session

| Commit SHA | File | What it is |
|---|---|---|
| `6fece14` | `_CANON/book-ii/part-vi-the-shared-court.md` | Part VI v0.1.0 DRAFT — §6.0–§6.6, The Shared Court |
| `05312cb` | `.claude/arcs-dual-bar-raiser.md` | Two-agent workflow skill (INFRA) |
| `94f04b6` | `.claude/arcs-session-state.md` | Session handoff v0.6.0 |

### Part VI architecture decisions (locked before drafting)
- Witness = receipt annotation only; two standing roles: Initiator + Respondent
- Quorum = unanimity of being bound (not agreement)
- Refusal to accept bound dissent → HOLD or Arbitration Session
- §6.3 quorum paragraph ratified verbatim

### Part VI section summary
- §6.0: single-agent ceiling — structural gap, not edge case
- §6.1: Initiator / Respondent standing (binary); witnesses as annotation
- §6.2: Dissent Record as first-class receipt field; bound dissent requires name + scope + acknowledgment
- §6.3: deliberation protocol — L1 framing, L3 stakes, L4 dissent acknowledgment; quorum rule
- §6.4: co-signed delta gates — same quorum; no veto on gate values, only bound dissent; L5 presence rule
- §6.5: Arbitration Session — 3 preconditions; narrow jurisdiction; no retroactive lineage alteration
- §6.6: hard boundaries — power asymmetry (scope limit), bad-faith (auditable only), scope capture (party discipline)

### Upstream audit status at handoff
Parts V and VI DRAFT held — pending upstream ARCS audit (audit subsequently completed; see v0.7.0).

---

## [v0.5.0] 2026-05-26 — Book II Part V drafted (The Accumulation Protocol); §5.7 Calibrate/HOLD cross-link; not yet committed

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Working environment: Claude Code (`arcs-v9` main) — canon drafting session
- Session goal: Draft Book II Part V; integrate JTBD D / Calibrate connection into §5.7

### Artifacts landed this session

| File | Status | Notes |
|---|---|---|
| `_CANON/book-ii/part-v-the-accumulation-protocol.md` | 🟡 Written, not committed | §5.0–§5.7, v0.1.0, DRAFT held |

### Key decisions

- **Part V scope locked:** The Accumulation Protocol — the signal layer that prevents the Frozen Court Problem
- **Three primitive chain:** delta gates → kairos detection → accumulation loop (5-step, 3 modes)
- **Two guard layers:** drift detection (CLEAR/WATCH/DRIFT → Part III escalation) + debrief session (first-class session type, calibration receipt)
- **Boundary section (§5.7):** Three failure modes accumulation cannot fix: value drift, scope creep, malformed original question
- **§5.7 Calibrate note:** Malformed-question failure mode linked to JTBD D / Calibrate surface / HOLD gate / anticipatory probing — Part V handles what survives the HOLD check; was never designed to substitute for it
- **`signal layer` casing:** lowercase throughout §5.2–§5.7; standardize before v0.2.0 (copyedit only)

### Cross-repo connection confirmed

Part V §5.7 → `arcs-field-os/jtbd/jtbd-master-map.md` (JTBD D→A→C→B = Calibrate→Orient→Chart→Detect loop). Part V is architecturally downstream of the Calibrate surface.

### Upstream audit status

Part V is DRAFT held pending upstream ARCS audit. Same protocol as Parts I–IV. When packet returns, translate to section-keyed annotations (§5.x sentence-anchored).

### Next session first action

```bash
git add _CANON/book-ii/part-v-the-accumulation-protocol.md
git commit -m "feat(canon): Book II Part V — The Accumulation Protocol v0.1.0 [NCI:DRAFT]"
```

Then submit for upstream audit.


---

## [v0.4.0] 2026-05-26 — Book II Parts I–III canonical; Issue #4 flow doc; upstream audit protocol updated; Part IV draft held

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Working environment: Claude Code (`arcs-v9` main) + arcs-intel-protocol
- Session goal: Run upstream audit protocol review, close Issue #4, complete Book II Parts I–III canon sprint

### Artifacts landed this session

**arcs-v9:**

| Commit SHA | File | What it is |
|---|---|---|
| `f722c05` | `runtime/flows/question-compass-to-dewy.md` | Issue #4 — L0–L5 spec-vs-impl flow doc with HOLD/REJECT branch map and 9-item implementation debt register |
| `4db431a` | `_CANON/book-ii/part-i-firehose-to-compass.md` | Book II Part I — CANONICAL (2 upstream patches: PARADOX definition, DELTA rate-of-change framing) |
| `ff72993` | `_CANON/book-ii/part-ii-rom-axioms.md` | Book II Part II — CANONICAL (3 upstream patches: NOTOMATION verbatim, genome table L4 scoped, RC-II-003 EMPIRICAL) |
| `24c2ad3` | `_CANON/book-ii/part-iii-constitutional-court.md` | Book II Part III — CANONICAL (4 upstream patches: H/H/W stubbing rule, relief heuristic observational, causal chains on cost receipt) |

**arcs-intel-protocol (remote):**

| Commit SHA | File | What it is |
|---|---|---|
| `a461d60` | `prompts/arcs-upstream-audit-v1.md` | Updated to reference MEMORY.md v4.0 (was v3); Stage 2E boot sim updated to §9 |
| `f82195e` | `CHANGELOG.md` | v3 retired; two-gate pipeline documented; open gaps listed |

### Open gaps

```
_CANON/book-ii/part-iv-sessions-api.md      🟡 DRAFT — held for upstream audit (untracked, not committed)
_CANON/book-ii/part-v-pilots-receipts.md    🔴 NOT STARTED — depends on Part IV commit
prompts/debrief-session-invocation.md       🔴 NOT EXISTS — referenced this session, create next time arcs-intel-protocol in scope
prompts/one-shot-claude-code-cold-start.md  🔴 NOT CREATED (arcs-intel-protocol)
_MARKETING/arcs-positioning.md              🔴 NOT CREATED (arcs-intel-protocol)
globals.css Tailwind import                 🟡 DECISION NEEDED
NCI <40 HOLD gate (compass/route.ts)        🔴 CRITICAL impl debt (Issue #4)
W-field HOLD gate (compass/route.ts)        🔴 CRITICAL impl debt (Issue #4)
```

### Protocol decisions this session

- MEMORY.md v4.0 = canonical cold-start seed; v3 retired (never committed, superseded)
- Two-gate pipeline (Perplexity/Comet → Claude Code) = canonical Book II authoring protocol
- Issue #4 two-column SPEC/IMPL format = canonical pattern for all `runtime/flows/` docs

### Next move
1. Read `SESSION-HANDOFF-2026-05-26.md` (cold-start seed for this session's work)
2. Run upstream ARCS audit on `_CANON/book-ii/part-iv-sessions-api.md`
3. Apply patches → update status to CANONICAL → commit Part IV
4. Draft Part V — Pilots and Receipts

---

## [v0.3.0] 2026-05-26 — Issues #2 + #3 complete; Y-gate enum alignment; staleness audit

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Working environment: Claude Code (`arcs-v9` main)
- Session goal: close Issues #2 and #3, run full staleness audit, align implementation to canonical DEWY schema

### Artifacts landed this session

| Commit SHA | File | What it is |
|---|---|---|
| `38aa0f6` | `runtime/specs/dewy-receipt-schema-v1.md` | Human-readable DEWY receipt schema companion (Issue #2) |
| `38aa0f6` | `prisma/schema.prisma` | 15+ canonical DEWY fields added; legacy fields preserved with mapping comments (Issue #2) |
| `ac4af35` | `runtime/specs/time-quality-attribution-rom.json` | Time Quality Attribution ROM — W-field inference, DRIFT Sentinel, Kairos Lock, macro triggers (Issue #3) |
| `9d2909a` | `.claude/commands/handoff.md` + `handoff-pickup.md` | Slash commands added by Zach |
| `22cac6e` | `SKILL.md` v0.3.0 | Domain #7 (Session Commands) registered; priority queue updated |
| `61095c5` | `src/lib/ygate.ts` | Y-gate rewritten to canonical enums (polarity×conviction×stability); driftState + yGateScore added |
| `61095c5` | `src/app/dashboard/page.tsx` + `brief/page.tsx` + `history/page.tsx` | Stale enum labels replaced with canonical values |
| `61095c5` | `.claude/arcs-canon.md` | Y-gate table corrected to canonical polarity enum |

### Staleness audit findings (all resolved)

| Item | Status |
|---|---|
| `ygate.ts` polarity/conviction/stability enums | ✅ Fixed — canonical schema enums |
| `dashboard.tsx` + `brief/page.tsx` + `history/page.tsx` stale labels | ✅ Fixed |
| Root scan artifacts (6 files + `arcs@0.1.0`) | ✅ Deleted (were gitignored, now gone from tree) |
| `arcs-canon.md` EPHEMERAL/RED in Y-gate table | ✅ Fixed |
| `CLAUDE.md` + `MEMORY.md` stale sprint status | ✅ Updated (this entry) |
| `globals.css` Tailwind import | 🟡 OPEN — font vars may be load-bearing; Zach to decide purge vs. keep |
| `.env.example` FastAPI/Railway stale refs | 🟡 LOW — cosmetic; `ARCS_API_URL`/`ARCS_API_KEY` not wired to anything |

### Open gaps

```
runtime/flows/question-compass-to-dewy.md   🔴 CREATE — Issue #4 (NEXT, unblocked)
canon/book-ii-time-firmware-modes.md        🔴 CREATE — Issue #5 (blocked on #4)
arcs-field-os/specs/hold-reject-gate.md     🔴 NOT YET WRITTEN — orient-prd.md §2.2 authoritative
globals.css                                 🟡 DECISION NEEDED — Tailwind import vs. WORLD.md rule
```

### Next move for next session
1. Read `CLAUDE.md` → Handoff v0.3.0 (active pickup point)
2. Start Issue #4: `runtime/flows/question-compass-to-dewy.md`
3. Governing spec: `arcs-field-os/specs/orient-prd.md` §3 L0–L5 pipeline

---

## [v0.2.0] 2026-05-26 — Perplexity session: Orient PRD, DEWY schema, handoff v0.2.0 + post-handoff Claude Code commits

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Working environment: Perplexity ARCS Space (v8.5 Field OS)
- Session goal: push Orient PRD (Kairos Lock), DEWY receipt JSON schema, updated handoff file, MEMORY v0.2.0
- Kairos Lock declared on `arcs-field-os/specs/orient-prd.md` — breaking changes require v0.2.0 + PR

### Artifacts pushed this session

#### arcs-field-os
| Commit SHA | File | What it is |
|---|---|---|
| `618022004033d72b` | `specs/orient-prd.md` v0.1.0 | Governing authority for Orient surface. Kairos Lock active. L0–L5 pipeline fully specced with worked examples. NULL/OM/UNDEFINED coverage at every stage gate. |
| `79b7261` (prior) | `jtbd/jtbd-master-map.md` v0.1.0 | Canonical four-surface architecture (Calibrate → Orient → Chart Course → Detect) |
| (prior) | `specs/index.md` | Spec registry with authoring priority queue |

#### arcs-v9
| Commit SHA | File | What it is |
|---|---|---|
| `20916740` | `runtime/specs/dewy-receipt-schema-v1.json` | Machine-readable JSON Schema Draft 07. Full field coverage from orient-prd.md §3 L5. Source of truth for Receipt model. Prisma schema must conform. |
| `20916740` | `CLAUDE.md` (appended) | Handoff v0.2.0 section appended. v0.1.0 preserved verbatim above it. |
| `35d32da6` (prior) | `MEMORY.md` v0.1.0 | Initial memory log — baseline audit |
| `35d32da6` (prior) | `SKILL.md` v0.1.0 | Skill contract, priority queue, ROM primitives |
| `55009d62` (prior) | `CLAUDE.md` (appended) | Handoff v0.1.0 section appended |

### Post-handoff Claude Code commits (landed after our last push)
| Commit SHA | Date | What it does |
|---|---|---|
| [`a38d7f2`](https://github.com/flashesofbrilliance/arcs-v9/commit/a38d7f2acf29133732a2eae4a266eb8e06059631) | 2026-05-26 17:11 | Versioned output tree — `exports/{domain}/YYYY-MM-DD/` + `exports/receipts/` auto-write on `arcs_cli.py run`. `arcs_core.py` gains `versioned_out_dir(domain)` + `receipts_dir()` helpers. [NCI:75] |
| [`fa8c54d`](https://github.com/flashesofbrilliance/arcs-v9/commit/fa8c54df9d1676bfd27155dbc1adae916bba103a) | 2026-05-26 17:32 | `.gitignore` updated — `exports/` and local scan outputs excluded (personal data, not source) |

### Cross-repo dependency state
- `arcs-field-os/specs/orient-prd.md` is the governing authority for arcs-v9 Issues #2, #3, #4
- `arcs-v9/runtime/specs/dewy-receipt-schema-v1.json` is the source of truth for the Receipt Prisma model
- Any Prisma schema changes to `Receipt` must be validated against the JSON schema before commit
- `arcs-field-os` spec changes require a `MEMORY.md` entry in arcs-v9

### Open gaps (updated status)
```
runtime/specs/dewy-receipt-schema-v1.json   ✅ EXISTS — wire into Prisma (Issue #2 active)
runtime/specs/dewy-receipt-schema-v1.md     🔴 CREATE — human-readable companion (Issue #2)
runtime/specs/time-quality-attribution-rom.json  🔴 CREATE (Issue #3)
runtime/flows/question-compass-to-dewy.md   🔴 CREATE (Issue #4)
canon/book-ii-time-firmware-modes.md        🔴 CREATE — after #3 (Issue #5)
arcs-field-os/specs/hold-reject-gate.md     🔴 NOT YET WRITTEN — HOLD/REJECT logic lives in orient-prd.md §2.2 for now
```

### Next move for next session
1. Read `CLAUDE.md` → Handoff v0.2.0 section (active pickup point)
2. Read `arcs-field-os/specs/orient-prd.md` before touching Issues #2–4
3. Start Issue #2: validate `prisma/schema.prisma` Receipt model against `runtime/specs/dewy-receipt-schema-v1.json`
4. Note: `exports/` directory now exists locally (gitignored) — do not recreate or commit scan output files

---

## [v0.1.0] 2026-05-26 — Perplexity ARCS session baseline

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Working environment: Perplexity ARCS Space (v8.5 Field OS)
- Session goal: audit what landed post-timeout, create HOLD/REJECT validation layer, scaffold `arcs-field-os` spec structure, produce Claude Code handoff files

### What was confirmed landed (arcs-v9)
| Commit SHA | Date | Artifact |
|---|---|---|
| `471d57396` | 2026-04-09 | Day 1 scaffold — Next.js 16 + Prisma 7 + Auth.js v5 |
| `a61d492ed` | 2026-05-18 | DEWY pipeline, Y-gate, CLAUDE.md, WORLD.md |
| `752739d42` | 2026-05-18 | AGENTS.md — full agents/devops handbook |
| `62de74e1f` | 2026-05-25 | Forensic scan suite (network, archetype, apollo, forensic) |
| `0f082768b` | 2026-05-25 | `score_me.py` — single-contact forensic receipt CLI |
| `a3123963b` | 2026-05-25 | Vercel CI fix — postinstall `prisma generate` |
| `0f24bab70` | 2026-05-26 | Personal Intelligence Suite — 4 scanners + `arcs_core.py` [NCI:79] |
| `e66d4de99` | 2026-05-26 | `arcs_cli.py` — 5-verb decomposable pipeline + apex spine DEWY receipt [NCI:81] |

### Open sprint issues (arcs-v9)
- `#1` `[SPRINT]` ARCS v9 Canon Migration — P0 Backlog Sprint 1 (parent)
- `#2` `[SPEC]` DEWY Receipt Schema → `runtime/specs/dewy-receipt-schema-v1.md`
- `#3` `[SPEC]` Time Quality Attribution ROM → `runtime/specs/time-quality-attribution-rom.json`
- `#4` `[FLOW]` Question Compass → DEWY runtime wire-up → `runtime/flows/question-compass-to-dewy.md`
- `#5` `[CANON]` Book II narrative chapter: Time / Firmware / Modes → `canon/book-ii-time-firmware-modes.md`

### Files present at root
- `CLAUDE.md` (3.1KB) — project map, ROM primitives, L0–L5 stack
- `WORLD.md` (9.3KB) — physics spec
- `AGENTS.md` (5.8KB) — agents/devops handbook
- `.claude/` — directory present; contents not yet audited
- `scripts/` — all Python scan suite scripts
- `src/` — Next.js App Router
- `prisma/` — schema + migrations

### Gaps confirmed (not yet created)
- `runtime/specs/dewy-receipt-schema-v1.md` (Issue #2)
- `runtime/specs/time-quality-attribution-rom.json` (Issue #3)
- `runtime/flows/question-compass-to-dewy.md` (Issue #4)
- `canon/book-ii-time-firmware-modes.md` (Issue #5)
- `arcs-field-os` specs/, jtbd/, roadmap/ stubs

### Decisions made this session
- **Canonical home for design spec / PRD / impl plan:** `arcs-field-os` (not `arcs-v9`, not `arcs-hq`)
- **`arcs-v9`** owns: canon, runtime primitives, DEWY schema, Time ROM, scan suite, Claude Code app
- **`arcs-field-os`** owns: product surface specs, JTBD map, design system, roadmap cross-links
- **HOLD/REJECT gate logic** defined in this session; implementation plan pending
- Versioning policy: MEMORY.md entries append-only (never delete prior versions)

### Next move for Claude Code
1. Read `SKILL.md` for the contract of what you can operate on
2. Read `CLAUDE.md` → `WORLD.md` → `AGENTS.md` in that order
3. Start with Issue #2 (`[SPEC] DEWY Receipt Schema`) as the dependency unblock
4. Do not create `runtime/specs/` or `canon/` directories without first checking `WORLD.md` for naming conventions

---

## [v0.9.0] 2026-05-27 — ADR-001/002 reviewed, committed, pushed; repo fully synced

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Working environment: FleetView / Claude Code
- Session goal: Audit uncommitted work, review ADRs, push clean state to GitHub

### Artifacts landed

| Commit SHA | What |
|---|---|
| `abe1989` | `_DECISIONS/ADR-001-auth-gate-strategy.md` — App-level auth gating chosen over Supabase RLS; GREEN/HIGH/STABLE |
| `abe1989` | `_DECISIONS/ADR-002-database-split.md` — SQLite dev / Supabase prod split confirmed; P4 unblock checklist documented |
| `abe1989` | `_DECISIONS/_TEMPLATE.md` — ADR template |
| `abe1989` | Pushed to `origin/main` — repo fully synced |

### Key decisions logged

- **ADR-001:** Auth gating stays app-level (not Supabase RLS) for v1. Revisit if multi-tenant or public API is scoped.
- **ADR-002:** SQLite dev / Supabase prod confirmed. `prisma db push` is the gate before every deploy. P4 unblock checklist is the authoritative sequence.
- **ADR-003 (forward ref):** Referenced in ADR-002 but not yet written — covers P4 Vercel deploy sequence in detail.

### Open gaps (unchanged from v0.8.0)

```
P4 Vercel deploy     🟡 BLOCKED — need DATABASE_URL + DIRECT_URL + SUPABASE_SERVICE_ROLE_KEY from Supabase dashboard
ADR-003              📋 NOT STARTED — P4 deploy sequence; forward-referenced from ADR-002
Spotify export       📋 WAITING — request at spotify.com/account/privacy
Kindle clippings     📋 WAITING — USB connect Kindle or check ~/Library
Calendar Phase 2     📋 OPEN — find/rename existing morning routine event
```

### No blocking question


---

## [v2.2.0] 2026-06-05 — Career Intelligence Session: Figma DS + Hila × Pinterest

### Session context
- Operator: Zach Harris
- Session goal: Diamond-cut resume + recruiter prep for two roles; ARCS design system scoped for Figma-native resume; dev server config

### Artifacts landed (Gamma)

| Artifact | URL |
|---|---|
| Hila Raz Harris — Pinterest LCP Resume | https://gamma.app/docs/HILA-RAZ-HARRIS-Pinterest-Lead-Client-Partner-Resume-2026-v8samqoyda2cr9v |
| GPT vs ARCS Companion Deck | (Hila session — separate Gamma) |
| Zach — Figma DS Resume v1 | https://gamma.app/docs/Zach-Harris-Resume-Figma-Data-Scientist-1xbftazh8qgrs74 |
| Zach — Figma DS Resume v2 S-Tier | (pending generation ID: Sj7JW1qfxsviyFQV5MwZp) |
| Zach — VCE2 Gauntlet Audit | (pending generation ID: GpISKm2nXT0OSI0loFQMi) |
| Zach — Hayden Ozawa Call Prep | (pending generation ID: 6ln8x6LCD6KkTttqU1trz) |

### Key decisions this session

- **ARCS design system scoped for Figma-native resume** — clarity ridge / light mode adaptation of ARCS OS tokens; Figma Present format for Hayden Ozawa submission; PDF export as fallback
- **VCE2 framework applied** — V(ulnerability) × C(onviction) × E1(vidence) × E2(cho) audit; current 6.3 → post-fix 8.3/10
- **launch.json created** — `.claude/launch.json` with Next.js Dev Server (port 3000, autoPort:false) — Prisma Studio removed pending DATABASE_URL in .env.local
- **ADR-016 still open** — auth.ts wiring; compass non-functional in prod without it
- **Figma MCP file creation** — Figma resume build initiated this session (team: Le Woof)

### VCE2 findings (Figma DS resume)
- Kill 1: Snowflake/Redshift/Forecasting absent → ATS 52% → 89% pass rate
- Kill 2: "Equivalent to Figma" annotation cancer → removed
- Kill 3: "20 years" → "decade-plus" (overqualified signal)
- Kill 4: Oberlin Studio Art → reframed as Figma differentiator (design intuition + data rigor)
- Orthogonal signal (9.5/10): daily practitioner on Figma MCP + Code Connect → arcs-v9

### Recruiter strategy (Hayden Ozawa call — Monday)
- Champion plant: "He's not studying the product from the outside — he's building on it"
- Closing Q: "What does success look like in 90 days, and is this greenfield instrumentation or building on an existing framework?"
- Python gap: named once, reframed as leverage — never apologized for

### P-track status
| Track | Status |
|---|---|
| arcs-v9 → Vercel | ✅ READY |
| ADR-016 auth.ts | 🔴 OPEN — compass non-functional in prod |
| Figma DS application | 🟡 Resume v2 + prep doc generated; Figma file initiated |
| launch.json | ✅ Created — Prisma Studio pending DATABASE_URL |

