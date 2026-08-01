# ARCS v9 — Memory Log

> **Versioning convention (amended 2026-07-19):** append new entries at top; keep only the recent
> window live. Relocate older entries to `_ARCHIVE/memory-archive.md` (never delete — archival honors
> "never delete prior versions" without paying the per-read token tax).
> Format: `## [vX.Y.Z] YYYY-MM-DD — <what changed>`

---
## [v3.22.0] 2026-08-01 — The ARCS "house" architecture + brand, one marathon thread

From a Logo-origin question to a formalized brand system and a compounding proverb engine. All
committed on `claude/decision-geometry-logo-81fb56` (`3c8bee5`→`fdc1fcf`); ADRs RC-PROPOSED.

- **Build spine:** ADR-039 (instance→class) + `tool-forge` → `tools/recoil-report/` (first CLI cast)
  → `forge-kit` (macro construction: food/experience/tuned-explanation/gift + intake + fish-finder).
- **Decision amplifier:** ADR-040 — Kairos detector = condenser + recoil(gain/resistor/breaker) +
  blower; Tesla-discharge at peak; recipe→receipt; overfit+gain-staging+custody rods. Due a molt-pass.
- **Honesty+growth:** ADR-041 — GAAP/non-GAAP (tilde/custody/gain-staging) + considered molt +
  recapitulate=deep-kairos + the 5×5 proverb grid (D/R/W/C/H × 5 verbs, anti-padding).
- **Brand:** DESIGN.md + .impeccable/design.json via /impeccable — North Star "Render Through the
  Fog", mark = tilde extruded → Möbius/fog/horizon, named rules, render-scale signature.
- **Oral history + engine:** Tao (`_ARTIFACTS/arcs-tao.html`, 32 verses) → `tao-mint` skill +
  `runtime/tao/proverbs.json` SSOT → first mint: 25 net-new ADR-040 proverbs (full grid). SSOT=40.
- Next: Phase 2 (render proverbs → visual cards via DESIGN.md); mint ADR-039/041 grids; ratify ADRs.

---
## [v3.21.0] 2026-08-01 — Positioning spine + Shannon recoil (strategy session, no code)

A Logo-origin question ("did learning Logo seed the decision-geometry frame?") became a coherent
GTM spine, then got field-tested by a real call.

- **Positioning:** "ARCS = Logo for the AI Era" (recognition line) + "you learn the terrain by
  moving through it and leaving a trace" (public promise). ICP = high-agency, 20+yr-career,
  golden-handcuff escapees seeking self-sovereignty; the felt Logo / legible-machine cohort
  (Oregon Trail / Pong / HyperCard nostalgia = legibility restored). Small-batch specificity is the
  moat. 3 auto-memories banked (in `~/.claude/projects/.../memory/`, not this repo).
- **ICP is a STATE, not a segment:** same person unreachable in-the-fire (horizon=0, files you as
  "vendor") vs receptive in caught-breath; in survival mode remove noise, don't add horizon;
  catching the window is a **Kairos problem** (the unbuilt ARCS primitive).
- **Shannon recoil:** `/recoil-report` on the Jul 31 10:30 Shannon (Usersnap) catch-up →
  `runtime/recoil/generated/2026-07-31-shannon.json` (`b6cc871`). YELLOW/DEGRADED, NCI 60 — clean
  soft-no, timing miss not fit miss; the grounding case for the ICP-state memory. Stopped before
  Gamma/deploy/email per cost.
- On branch `claude/decision-geometry-logo-81fb56` (not main). Next: do NOT pursue Shannon (active-
  listening alarm); take her LinkedIn-repost offer; re-approach ~Sept. Sit with the Kairos thread.

---
## [v3.11.0] 2026-07-20 — Anon-share persist fix + design-system glow tuning (live)

First **interactive/local** deploy session after a run of cloud sessions (which couldn't deploy).

- **Anon-share "Sign in to keep" persist fix** (PR #121, `403d109`) — closes the v3.9.0 honesty
  flag's core gap: the shared bearing recomposed one-time but sign-in kept nothing. Onramp now
  writes `arcs_pending_save`; `ClaimAnonymousReceipts` claims it post-auth → `/receipt/<id>`.
- **Glow tuning, two passes** (`8429f2e`, `cfbc483`) — operator: too hot across the board.
  `signalGlow()` alphas halved (~.28), bloom blur cut ~33% then eased back on the gauge; accent
  card glow reduced; `TrueNorthPanel` given real glassmorphism (backdrop-blur(14px) + translucent
  blue); Field/select untouched (confirmed correct). All verified via **live computed styles**, not
  by eye — extends the "verify render, don't claim it" discipline to the design system.
- **Deploy discipline receipt:** merged to main + git-push (NOT `vercel --prod` from a worktree) →
  all **29 subdomain aliases intact** (app/arcs.care + every brief). The long INITIALIZING was
  queue time; build itself ~46s.
- **Operator-approved, not started:** ledger management (archive/reset before hard-delete);
  authenticated `/recoil` index (index documents first, DB-backed later). Standby: production
  auth-loop test (Gmail connector) to fully close v3.9.0; sweep stray hardcoded glows.

---
## [v3.10.0] 2026-07-19 — Serialization pathogen family: ADR-033 ratified + Detective --sweep

> Tracker note: mid-session, CLAUDE.md's handoff chain read v3.8.0 while this file was at
> v3.9.0 (two concurrent sessions, one tracker each — the exact chronos-sequencer receipt
> ADR-033 cites). The v3.9.0 session healed it concurrently by appending its own CLAUDE.md
> handoff; recorded here as a live family receipt, observed and closed same-day.

**The family, discovered serially 2026-07-17→19 and unified under one axiom** (`_DECISIONS/
ADR-033-serialization-pathogen-family.md`, **DECIDED — Zach ratified GREEN/HIGH/REVISIT**):
a serialized belief is a tuple (claim, time, scope, warrant, obligations, dictionary); every
member is one coordinate silently dropped at write/read time. time→chronos-sequencer ·
scope→inductive-overfit · obligation→open-loop decay · warrant→epistemic-sequencer ·
dictionary→etymology-sequencer. Admission gate (all 4): distinct coordinate + distinct
mechanism + ≥1 in-repo receipt + named enforcement point.

- `runtime/specs/recoil-modes-v1.md` v0.1.0→**v0.4.0**: §chronos-sequencer (readOrder
  directive near file head, in-place `[SUPERSEDED — see X]` markers, cover always-current);
  §inductive-overfit (banked models MUST carry validityBounds {n, conditions, stationarity};
  n-aware regime ladder anecdote→directional→central-mass, ADR-023's 100-receipt gate as the
  threshold; tails/edges excepted at ANY n — BAR jurisdiction); §open-loop decay (riskFlags
  MUST carry `status` OPEN/DONE/WAIVED dated; closure is an explicit write, never silence).
- `runtime/specs/call-brief-hooks-v1.md` v1.0.0→**v1.1.0**: Task A/B read
  readOrder/recapitulation-designated current state FIRST; never quote a stratum without a
  superseded-marker check.
- `scripts/receipt_lookup.py` (Detective): superseded-marker skip (marker syntax, not bare
  word — live flags may *mention* supersession), n-aware regime read, validityBounds
  surfaced verbatim, latest-Y-gate no longer masked by empty pre-call-stub covers, and
  **`--sweep`** — every OPEN obligation ledger-wide, aged, oldest first. First live run:
  **52 open obligations across 20 reports, zero ever closed**, incl. a 10-day-old HIGH whose
  owed action was "send within 48 hours." QED.
- **First documented closure:** the enforcement-parity ledger, stranded on an unmerged
  branch 2026-07-16→19 (memory had serialized it as live CI-gated law — double receipt:
  open-loop + epistemic), merged as **ADR-034** (PR #63) renumbered per ADR-033's own rule.
  Jurisdictions: ADR-034 `_PATTERNS/ledger.json` = repo/audit findings; `--sweep` = call-
  ledger obligations. Worked example for the whole family:
  `runtime/recoil/generated/2026-07-17-chan-suh.json` (readOrder + validityBounds).

Commits: `9748048` `15d71d8` `9ce0dfc` `09bb14b` `5f181fc`. Open from this thread: act on
the 52-flag sweep backlog; dedupe the two ADR-032 files; epistemic/etymology members have
partial mechanisms only (no dedicated enforcement built yet — registered honestly as such).

## [v3.9.0] 2026-07-19 — Stateless anonymous brief sharing (ADR-037) + trust-contract v1.3

Anonymous bearings are never persisted (trust contract). Made them shareable **without a server write** by
encoding the bearing in the URL **fragment** (`/brief/share#<payload>`) — browsers never send it to the
server, so the recipient recomposes client-side. Preserves "nothing stored / no write path"; does NOT reverse
ADR-032. Rejected the server-token alternative precisely because it would have.

- `src/lib/shareLink.ts` (encode/decode; **decodeShare sanitizes every field** incl. `reasoning.paths` — the
  `#payload` is attacker-controllable), `src/app/brief/share/page.tsx` (recipient view, one-view localStorage
  gate → `/compass?shared=1`, never reads hash into analytics), receipt-page "Share ↗" (ephemeral only),
  compass `?shared=1` banner.
- **Governance:** amended the CANONICAL `_CANON/trust-contract.md` → v1.3 (§1 share carve-out + amendment log),
  then the derived pages (`/trust` v1.3, `/privacy` v1.1). Caught by the `privacy-review` agent, which flagged
  that the first pass updated only the derived pages — fixed before merge.
- Branch `claude/anon-share-stateless` (NOT merged). ADR-037 (037 claimed via live `ls`; 035=commit-nci,
  036=concurrent session's repo-split — no collision). Build+typecheck pass; not yet driven live.

---
## [v3.8.0] 2026-07-19 — Token-efficiency audit + downstream fixes (branch `claude/token-efficiency-audit-ip3l3x`, 17 commits, NOT merged)

**Audit:** re-ranked the prior "Sentinel connector strip = #1" recommendation. Measured this repo: CLAUDE.md
(@-imports AGENTS+WORLD) auto-loaded ~24.6k tok/session and the orientation chain pulled MEMORY.md for ~39k
tok before any work — unbounded by the append-only handoff policy (28 handoff sections). That per-session tax
was the true #1; the Sentinel fix is real but ~10× smaller.

**Fix #1 (context split):** CLAUDE.md 19.8k→3.6k tok, MEMORY.md 14.8k→5.8k. Dead handoffs/memory → `_ARCHIVE/`.
Amended the append-only policy: CLAUDE.md/MEMORY.md are lean working files, history relocated (never deleted).
**Fix #2:** replaced the ~40k-tok orientation-chain mandate with a lean one. **Archive safety-scan** (subagent)
confirmed the cut dropped nothing (open work lives in PENDING.md, not handoff prose). Banked `_PATTERNS/
durable-gotchas.md`.

**ADR-035:** ratified the real Commit-NCI rubric (5 lenses = 100; the `[NCI:XX]` tag had no rubric + was all
SKIP). Distinct from the product `nci_score`. Wired `nci-scoring` skill + `/nci-commit` + `/drift-check` to it.
Added `/rca` (triage-gated root-cause command).

**Tech-debt batch** (backgrounded via subagents): A1 console cleanup [NCI:94]; A5/A6 doc+index fixes; B1
react-hooks diagnosed clean; A2/A3/A4 triaged out honestly. **B4:** `npx next build` failed on `/_global-error`
prerender — root-caused to shell `NODE_ENV=development`; fixed by pinning `NODE_ENV=production` in the build
script + AGENTS.md gotcha (Vercel always built prod → deploys never affected). Added branded `global-error.tsx`.

**B2:** implemented the spec 5-lens `nci_by_lens` + `nci_grade` (schema columns existed, impl never populated),
additive/backward-compatible (composite semantics unchanged); surfaced the weak-lens grade in `DebriefCard`;
added a `stop_reason` truncation guard.

**Security:** threat assessment of the model-downgrade trade-offs (`_PATTERNS/2026-07-19-threat-assessment.md`).
HIGH = the Haiku Sentinel (lethal trifecta → could poison CLAUDE.md). Then hardened the **recursive cascade**
(`src/lib/sanitize.ts`, unit-tested 8/8): trust boundary at every rung — ingress framing, persist-boundary
clamps (`clampText`/`clampInt`), tributary-prompt clamp (recursive edge), brief-writer framing. Structural
defense (delimiter defang), not phrase-matching.

**Honesty note:** compass changes are build+typecheck+unit-tested but NOT driven via a live compass call
(no `ANTHROPIC_API_KEY` in session). **Next:** merge to main; then out-of-band items in `_QUEUE/PENDING.md`.

## [v3.7.0] 2026-07-17 — chan.arcs.care built end-to-end + status.arcs.care fork; two real mobile bugs found via device photos and fixed

**Realignment note:** this file was last updated 2026-07-02 (v3.3.1) while `CLAUDE.md` had advanced to v3.6.0 across other sessions in between. Versioning here jumps to v3.7.0 to follow `CLAUDE.md` as the more current tracker, per the same realignment `CLAUDE.md`'s own v3.0.0 entry performed. Full narrative detail lives in `.claude/arcs-session-state.md`, not duplicated here.

**chan.arcs.care** — built as a Prophet/Mike Lemon/Chan Suh (CDO) discovery-call artifact, iterated across ~20 commits in one long session:
- Player/Coach/Pacecar identity frame, prior-terrain (pre-ARCS) résumé receipts, era-split visual separation
- Instrument-panel section: 12 design principles (traceability, anti-hallucination, anti-sycophancy, etc.) each tied to where it's enforced, plus a hand-authored SVG of the actual compounding architecture loop (question → L0–L5 pipeline → receipt → outcome → calibration)
- Conductor-lane telemetry: real git-trailer data showing which Claude model authored each week's commits, tabbed against commit-cadence, with click-to-unlock narrative cards (the 5 quiet design weeks; the model-rotation "building at the edge" story)
- Presentation mode: 16 slides in a SEEN/HEARD/VIBE-CHECK discovery structure, provenance-graded per slide (glow=confidence per the canonical `--glow-*` tokens), Maya Lin-inspired pointer-terraformed moiré topography, 2.5D isometric floor (perspective scaled to `70vh`, not a fixed px, after it broke on ultrawide/zoom), a left-edge "fathom" progress rail, chrome that auto-hides after 2.6s idle, right-click escape-hatch on the closing slide back to slide 1
- Full design-system conformance pass: pulled the canonical token file (`colors_and_type.css`) live from the "ARCS OS - Design System" Claude Design project via `DesignSync`, then migrated all 81 freehand font-sizes onto the canonical 8-step `--text-*` scale, swapped fonts to Inter + JetBrains Mono (the only two the project's own adherence linter permits), tokenized radii
- Progressive disclosure: FOCUS-mode-by-default (only section 1 open, rest collapsed to a headline + one-line TL;DR), EXPAND ALL as the alternate mode
- PII removed (email + phone from both footers); confirmed `noindex, nofollow` already present, no `robots.txt` override exists

**status.arcs.care** — forked from `chan.html` with the Prophet-specific content and the entire presentation deck surgically removed (anchor-based excision, not hand-editing): echo-map, Player/Coach/Pacecar frame, prior-terrain creds, ~250 lines of presentation JS/DOM/CSS. Routed via `next.config.ts`; domain had to be attached to the Vercel project directly via API (the deploy script's pre-flight falsely reported it already assigned).

**Two real mobile bugs, found only from actual device photos (HEIC — converted via `sips` since the Read tool can't render HEIC directly), not simulator resizing:**
1. `.echo-mid`'s mobile styling used `transform: rotate(90deg)` on a full-width flex box to turn "↔" into "↕" — CSS transforms repaint an element in place but don't change its layout footprint, so the rotated glyph + its border lines visually overflowed above/below their own grid cell, reading as a disconnected floating icon. Fixed by dropping the rotation and swapping the glyph via `font-size:0` + `::after` instead.
2. The architecture-loop SVG is legitimately wider than a phone screen and horizontally scrollable, but mobile Safari hides scrollbars until an active drag — the truncated edge read as broken content. Added a right-edge fade mask + explicit "SWIPE FOR THE FULL LOOP" hint, mobile-only.

Also fixed in the same pass: presentation chrome (top/bottom bars) was drifting left/right slide-to-slide because `flex; justify-content: space-between` centers content *relative to flanking-element width*, not true viewport center — converted to CSS grid (`1fr auto 1fr`) with explicit `grid-column` pins (needed because mobile hides some children via `display:none`, and grid auto-placement would otherwise misplace the survivors).

**Last confirmed commit:** `c536792` — merged to `main`, pushed to `origin/main`, deployed, and verified live via direct curl against both chan.arcs.care and status.arcs.care (not just "deploy succeeded" — actual served content checked for each specific fix).

---

## [v3.3.1] 2026-07-02 — kelly-interview brief built + deployed, Todd Phase 1 proposal verified

### Session context
Post-interview brief for Kelly Mullaney (VP Applied AI, Juniper Square) built from scratch and shipped to `kelly-interview.arcs.care`. Four-tab layout: Pre-Call / Post-Call / Build / The Ask. Key work: host-based routing fix in `next.config.ts` (was missing from beforeFiles — page was serving Next.js root instead of HTML); read times on tab buttons; bullet scan copy throughout; mental model row (stated vs revealed preference); 5 unsubstantiated claims dropped after fact-check audit (GP/LP customer base claim, 7-day lag specific number, Jay Farber quote attribution, 80% signal coverage figure, "one sentence" commission framing). Email sent to Kelly 3:50pm. Brief confirmed live via curl (`x-matched-path: /kelly-interview.html`). Todd Hotes / PRL Resins Phase 1 proposal also verified live at `todd-call.arcs.care`.

### Decisions
- host-based subdomain rewrites MUST live in `next.config.ts` `beforeFiles` with `has: [{type: "host"}]` — `vercel.json` rewrites are intercepted by Next.js App Router before they fire
- NCI counter at 191 end of session
- Kelly follow-up cadence: let breathe until Wed Jul 8, then one-line check-in "any movement on your end?" — do not go around Kelly to Alex or Nushi directly

### Open loops
- Kelly Mullaney / Juniper Square — waiting on Kelly to loop back with Nushi re alternative assessment
- Todd Hotes / PRL Resins — waiting on yes/no re Phase 1 ($1,500, 3 sessions this week)
- Compass Kit Phase 2 ADR — not started, no blocker

---

## [v3.2.0] 2026-06-23 — Critical Supabase RLS fix, tasks #5/#7 closed, trust-contract §8 added

### Session context
- Operator: Zach Harris, branch `observatory-cherry-pick` (worktree `busy-chaplygin-22139c`)
- Continuation of the same 2026-06-23 thread as v3.1.0/v3.2.0's backlog

### Critical fix — live production exposure (not part of the 8-item backlog)
A Supabase security alert ("Table publicly accessible") for project `xbbpiryokswwvcrcutge`
(ARCS_v9) was verified live via `supabase db advisors --linked` (the Supabase MCP
connection in this session is scoped to the wrong account/org and could not see this
project at all — the CLI, separately logged in, could). Confirmed real: `public.SageTrace`
(11 rows, Prisma-managed) had RLS disabled entirely — fully open anon read/write/delete via
PostgREST. Fixed with the same deny-all pattern as ADR-008 (Prisma bypasses RLS as the
`postgres` superuser regardless; RLS exists only to block public PostgREST access). Re-verified
post-fix: 0 ERRORs. A follow-up pass cleared 27 of 31 remaining WARN-level advisories
(`auth_rls_initplan` perf fixes across `meeting_cards`/`risks`/`raci`/`dependencies`/
`drift_signals`/`receipts`/`immune_sessions`/`immune_turns`/`pathogen_log`, plus a redundant
permissive policy dropped on `sessions`). 4 WARNs left deliberately unfixed: 3 on
`immune_sessions`/`immune_turns`/`pathogen_log` (zero rows, zero references anywhere on
disk — unconfirmed ownership, not safe to guess-tighten) and 1 on `sessions` (confirmed
intentional — backs `arcs-care-local`'s public `/receipts` page). `scripts/rls-policies.sql`'s
stale header (said `owdiiyvphyifukygvxhg`, the wrong/inactive project) corrected to the real
live ref. Open question for Zach: what are `immune_sessions`/`meeting_cards`/`risks`/`raci`/
`dependencies`/`drift_signals` — no owning app found in any local repo.

### Task #5 — prose-rule enforcement audit (`_PATTERNS/2026-06-23-prose-rule-enforcement-audit.md`)
Scoped to `SKILL.md` per the plan. Zero of six in-scope rules have any real enforcement
mechanism. Highest-value finding, independently re-verified (not just trusted from the
writeup): "inline styles only — no Tailwind, no className" — stated as a hard constraint in
three files — has been violated at the application root (`src/app/layout.tsx`,
`className="...bg-obsidian-950..."`, `tailwindcss` a real dependency) since the first commit.
Two out-of-scope findings also surfaced: CI's actual typecheck gate does the thing `AGENTS.md`
says not to do (`tsc --noEmit` vs. the documented `npx next build`), and SKILL.md
self-contradicts on the commit-trailer file count (5 vs. 3).

### Task #7 — Observatory cherry-pick (`35070a3`)
Turned out to be already-landed before this session started (this branch's HEAD already had
the full 1174-line `src/app/observatory/page.tsx` — missed checking this before delegating
to a subagent to redo it from scratch). The one genuinely-missing piece — removing the now-dead
`/observatory` static rewrite from `next.config.ts`, which the real App Router page route now
shadows — is done and build-verified (`npx next build` passes, `○ /observatory` registers as
a real prerendered route).

### Trust contract v1.1 — `_CANON/trust-contract.md` §8 added
Zak's feedback checklist (6 items) was already fully covered §1–§6, verified against his
literal wording, not assumed from topic match. The one open framing question — "how will you
catch people at the fork the system is solving for" — had no home. Zach's call: add it as a
new canonical §8 rather than route it to product copy or park it. Written honestly: ARCS does
not proactively detect a forming decision today (deliberate boundary against ambient
surveillance, *and* a genuine gap — consent-based `Kairos detection` is unbuilt backlog).
Version bumped 1.0 → 1.1 per the doc's own amendment rule.

### Process note
Both background-delegated subagents (for #5 and #7) hit the account's monthly spend limit
mid-task and were finished by hand. One agent (#7) cited a Next.js doc file from a sandbox
that had no `node_modules` installed — it could not have read it live as instructed. The
underlying technical claim (rewrite-vs-page-route precedence) held up when independently
re-checked against the real file in a working environment, but the agent's stated verification
method was not real. Distinguish "conclusion happened to be correct" from "conclusion was
actually verified" — this session's standing discipline, applied to its own delegated work
this time, not just to external claims.

### Next session starts at
Backlog items remaining: #1 (done, see v3.1.0 follow-up), #2 (blocked on Zach), #3, #4, #6, #8.
Two small uncommitted items from this session not yet folded into a branch: confirm with Zach
whether to consolidate.

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

## Older entries (v2.6.0 and back)

Relocated to `_ARCHIVE/memory-archive.md` on 2026-07-19. Open that file to read pre-v3.0.0 history.
