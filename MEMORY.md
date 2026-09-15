# ARCS v9 — Memory Log

> **Versioning convention (amended 2026-07-19):** append new entries at top; keep only the recent
> window live. Relocate older entries to `_ARCHIVE/memory-archive.md` (never delete — archival honors
> "never delete prior versions" without paying the per-read token tax).
> Format: `## [vX.Y.Z] YYYY-MM-DD — <what changed>`

---

## [v3.62.0] 2026-09-14 — Schriner/Oxenham job-search engagement: full recoil lifecycle + resume correction

- **`schriner.arcs.care`** (recruiter pitch + resume viewer/PDF/ATS) and **`schriner-ext.arcs.care`**
  (safe external recoil twin, air-gap verified) shipped live via normal PR/merge.
- **Resume correction shipped live**: technical-cut resume first sent to Joe had dropped real
  leadership scope; corrected to a three-modes (builder/team-lead/executive-partner) framing and a
  closed 2010-2016 work-history gap (Selectable Media, IBRShop), sourced from real iCloud PDFs.
- **Internal recoil receipt** closed post-call at FORK/DIVERGENT; the CEO-identity gate was resolved
  by independent search after the call, not by the recruiter on it — generalized into
  `inbound-opportunity-three-gate-smoke-test` memory (verify identity BEFORE the call).
- **Global memory**: new project memory `project_joe_schriner_oxenham_autopilot_vico`, new feedback
  memory `technical-cut-resume-must-keep-leadership-scope`, `MEMORY.md` index deduped/tidied.
- **Open**: Joe-facing fit-note drafted, held pending follow-up call; `resume-tailor` skill repo
  itself not yet updated with the lesson (deferred to next session).

## [v3.61.0] 2026-09-13 — Bridge employer index live · Triune Stream A/B/C landed · seed bank clean

- **`scripts/bridge_index_scan.py`** (new, stdlib): curated employer lists → public ATS boards → winnable
  reqs → jobs.arcs.care. 578 rows live as `bridge_scan` UNSCORED across 84 employers; index at
  `_STATE/job-search/employer-index/`. Ingest skips existing jobids (API upsert would reset scores).
- **ADR-078/079/080/081 + 041 on main** — the three 2026-08-03 hold branches renumbered through the
  oracle and merged (#408–#413); `_STATE/worktree-audit-2026-09-11.md` is the patch-id sweep of all 74 worktrees.
- **`scripts/scout_dossier_ingest.py`** (new): Perplexity dossier gate (validate/map/post). Caught real
  drift on first use (Parloa lacks `extraction_risk`).
- **Seed bank**: +4 candidates, 2 orphans receipted, 4 broken locals fixed; drift check OK (41/80).
- **Receipts**: 8 `decision_receipt` rows this session; AGENTS.md now documents the CHECK enums.
- Cross-harness: `_STATE/convergence.json` on `fresh-starts` beat 6; Hermes owns JTBD-004, Perplexity JTBD-007.
- Next: Thread 2 scores the bridge rows; human prune call on 17 worktrees; Workday adapter seed.

## [v3.57.0] 2026-09-07 — Reading Room back-propagation organ (1b gate MET)

- **`scripts/cache_backprop.py`** (new, stdlib): the Metabolic Router's lazy pull-driven repair for a
  DIRTY `(domain, epoch)` cache slice. `plan` (list dirty) → `packet` (assemble a Curator work-packet:
  slice nodes + cited provenance AS-IS at HEAD + rubric) → `apply` (write graded statuses back into the
  digest, stamp only THAT slice fresh). Grading is JUDGMENT and stays external by construction
  (NOTOMATION) — the script never grades.
- **Per-slice grade preservation** (the load-bearing fix in `cache_manifest.py`): `stamp`/`check` now
  carry a prior slice's recorded `graded_at_sha` forward instead of recomputing it from the shared
  digest file's last commit. Without this, re-grading one epoch falsely frees every sibling epoch that
  shares the file. Only a *complete* re-grade advances the sha; `--partial` leaves the slice dirty and
  says so (WITNESS honesty).
- **Gauntlet before commit** (runner + adversarial skeptic, refuter per finding) — 3 real defects found
  and fixed: (1) write-before-validate left a half-graded digest on a bad apply (KINTSUGI: all
  validation now precedes the write); (2) `--partial` falsely stamped the whole slice fresh; (3) a
  cleared note outlived a status change. 5 stdlib tests green (`scripts/tests/test_cache_backprop.py`).
- **1b gate MET**: proved end-to-end — `product/2026-04` dirty → re-graded LIVE → fresh, 19 siblings
  stay dirty; freshness survived a full re-stamp AND 11 commits of base advance. PR #320 → `343b266`.
- **Lesson banked**: when many slices share one provenance/digest file, freshness MUST be tracked
  per-slice in the manifest, never derived from the shared file's git history — the shared file is the
  wrong granularity and silently over-frees.

## [v3.56.0] 2026-09-07 — wrap-lint MODE 5 safeguard, post-4 s-tier pass, Dealroom research, ADR-076 MCP-led growth

- **wrap-lint MODE 5** (`scripts/artifact_wrap_lint.py`, pre-commit wired, PRs #256/#258/#260): gates the
  desktop measure/container-mismatch wrap bug that overflow checks miss. `<style>`-only scan, CSS-comment
  strip, FP-reducer for `max-width:none` overrides, `wrap-lint-allow: measure-mismatch` opt-out for
  intentional two-width designs. Fixed dossier + 3 ledes; marked wing/scott-cut/observatory. AEO
  robots/sitemap reachable on good.arcs.care (proxy + next.config both layers).
- **NFTT post-4 impeccable pass = s-tier, zero edits**; posts 1-3 swept clean. Template gives diamond-cut
  text handling by construction; 4-width JS test method banked.
- **Dealroom talent research** (`_ARTIFACTS/research/2026-09-04-dealroom-talent-report-grammar.md`, PR #273):
  15 report/viz patterns + MCP-led-growth GTM analysis.
- **ADR-076 — MCP-Led Growth: the attribution wedge** (PR #307). DRAFT/YELLOW, demand-probe gated.
  Drafted as ADR-075; renumbered to 076 after a parallel session's DECIDED **ADR-075 Metabolic Router**
  merged first (oracle-first: ratified canon keeps the number, unmerged draft renumbers; audit no-dup).
- Housekeeping: lattice epoch re-pinned e9 (spot-check); iCloud deliverable→Files sync convention; 5 new
  memories banked (MODE-5 tripwire doctrine, MCP-led-growth, dealroom grammar, NFTT provenance/aphorisms).

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
