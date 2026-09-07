# ARCS v9 — Memory Log

> **Versioning convention (amended 2026-07-19):** append new entries at top; keep only the recent
> window live. Relocate older entries to `_ARCHIVE/memory-archive.md` (never delete — archival honors
> "never delete prior versions" without paying the per-read token tax).
> Format: `## [vX.Y.Z] YYYY-MM-DD — <what changed>`

---

## [v3.53.0] 2026-09-04 — The Reading Room: the Almanac, ADR-075 the Metabolic Router, locked build plan

- **Almanac** (`scripts/research_render.py`): 264 full-temporal epoch-tagged nodes read at 3 altitudes
  (Skim/Scan/Trenches); two-shelf Required Reading (Foundational by canon + Load-bearing by in-degree);
  per-row export. Local-only. Library taxonomy: Alexandria index / Atlas map / Almanac dated state.
- **ADR-075** minted through the oracle from a live witness: mechanical fan-out automatable, judgment
  never; integrity gate = cites exist on origin/main (caught 5 memories describing never-merged gates).
- **Locked plan** `_SPECS/reading-room-build-plan-v1.md`: spine (Desk+Reader+cache) first, tenants
  cheap; token-savings-bank levers; CBA ledger. Loop: Desk -> Almanac -> Concordance -> Chronicle -> Lexicon.
- growth-ai.arcs.care family live; recruithaus `/ammo` gated live; Blacksmith polish; drift swept.

## [v3.46.0] 2026-08-27 — First closed client receipt + instrument board

- **ADR-069 minted** (oracle audit pending): first ex-ante->ex-post receipt closed in a paying
  engagement (PRL 1.2, RED on estimate, cap held). Expectation management is now precedent-shaped:
  forward claims cite banked receipts; losing receipts are publishable; variance priced as
  preconditions. Witness stub 2026-08-26 + DEWY receipt.
- **prl.arcs.care/status/receipt** live: the close-loop as data-story (band chart, tiles, honest
  method). Passed fact-check-vs-CSV + full counterpart-gauntlet (14 findings fixed, incl. 2
  pathogens on the four-hour row). Receipt pill now on all 8 family pages + homepage gold jumplink.
- **Instrument Board** (`scripts/warroom_board.py` -> /warroom/gauntlet, admin-gated): second
  sovereign projection service; adapters snap on per JSONL ledger; typed print + spark-plug sidecar.
  Care rule: new gauntlet-runs rows must state "N pathogen, N crack, N nit" + "N over-flags rejected".
- Gotchas re-proven: handoff version collision across parallel sessions (renumber, keep both);
  squash-merged branch = reset to main, never rebase-replay; tripwire flags on touched-but-unchanged
  content get adjudicated in the commit message, not silently bypassed.

## [v3.43.0] 2026-08-26 — ADR-068 germination + the genesis-riff arc (PR #167 merged)

Verb-matrix pattern PROMOTED to **ADR-068** (print/gate/fate per verb-cut, altitude orthogonal)
and **wired as blocking steps into 7 skills** (ex-ante-before-send, pre-send gauntlet, close-loop
obligation); `_DECISIONS/index.json` backfilled 066/067; both oracle counters reconciled. Banked
**4 seeds with ledger receipts**: projection-family-registry, extraction-prospecting,
sovereign-projection-services, pollinate. Witness file 2026-08-23 carries the 8-stub spine:
inheritance capstone → **tikkun olam origin** (absent from _CANON until witnessed) → molt
(polyform survey → buddhist convergence) → tree-fall koan closed → **frame-geometry PROMOTED**:
Tao v1.1.0 §V "one field, sovereign zeros, lawful transforms, preserved invariants" + tao-250/251
+ genesis root-cluster (adam·adamah·adom·dam) + **Eve = chava == anima = the vox animus**.
Overdue: PRL close-loop/prospecting pass (was Aug-24); Sean window ends Aug-30.

## [v3.35.0] 2026-08-17 — Comet Technical PMM application + resume-tailor skill v0.2 (ATG-in-the-wild)

Tailored Zach's résumé + cover letter + ATS-plain to Comet's **Technical Product Marketing Manager**
role (VP Marketing Hannah Klemme) in `_ARTIFACTS/resume-comet/` — honesty-graded, voice-tuned from his
LinkedIn export, and gauntlet-hardened via a 4-facet adversarial panel (recruiter/ATS · hiring-manager
· technical-peer · reference-check; verdicts **TAKE THE CALL / DEFENSIBLE-WITH-FIXES**). Centerpiece:
an **orthogonal echo** (his OSS `token-savings-bank` ↔ Opik's AI Spend Tracker, reframed to
reduction-vs-observability after the gauntlet caught the category error). **ATG offshoots:**
resume-tailor skill → **v0.2 PUSHED** to `flashesofbrilliance/resume-tailor-skill` main
(components/params/eval+rubric/exemplar; `resume-tailor@arcs` installs it); the 4-facet gauntlet
harness; voice-extract + orthogonal-echo memories; blog "NOTOMATION powering gradient ascent" forked
to its own session. Titles reconciled to the export (Grayscale = Product Lead; Squat = Head of Product
Innovation & Tech Lead). Open: **ARCS not on Zach's LinkedIn** (reference-check gap). No arcs-v9 code touched.
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
ADR-049. Rejected the server-token alternative precisely because it would have.

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

## Older entries (v3.3.1 and back)

v3.0.0–v3.3.1 relocated to `_ARCHIVE/memory-archive.md` on 2026-09-06; v2.6.0 and back on 2026-07-19.
Open that file to read pre-v3.7.0 history.
