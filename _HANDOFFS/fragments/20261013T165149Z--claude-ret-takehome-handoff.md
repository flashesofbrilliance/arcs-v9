<!--
session: claude-ret-takehome-handoff
branch: claude/ret-takehome-handoff
head: e83abaed
created_at: 2026-10-13T16:51:49Z
-->
> RET take-home session (2026-10-10 to 2026-10-13): built and hardened Zach's monday.com FDE take-home in the separate
> repo ret-rfp-intelligence (rc23 to rc35), rehearsed the panel in four rounds, and handed the navigation redesign to a
> fresh session. Work product lives in that repo; this fragment banks the internal notes in _STATE.

### Shavasana — handoff pause, 2026-10-13 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/ret-takehome-handoff), receipts in digest: no digest file.
- **Inhale** (what came in): 0 falsification rows today, 0 dissent markers, 0 unconfirmed markers in the day's records.
- **Breath balance**: breathing (both directions).
- **Sycophancy check**: agreement 1 / dissent 0 (ratio 1.0) → OK: dissent present.
- **Cold re-read (canary on the draft fragment.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._
- Attachment release: every claim in Changed and State was re-checked this session against git tags, the release log and the live run; none downgraded.
- Somatic: not asked.
- Disposition: release.

## Goal
Submit the take-home Thursday 2026-10-15 morning: one ZIP under 10,000,000 bytes with source/, exactly one presentation
PDF, and README.md, that a cold reviewer can run and navigate.

## Changed
- ret-rfp-intelligence main 175afe2 (pushed), release candidate rc35 (tag rc35-2026-10-13, 3.36 MB, release check exit 0,
  live end-to-end run from the ZIP passed). Not an arcs-v9 PR; that repo is the deliverable.
- Size gate fixed: rc25 to rc33 exceeded 10 MB on the decimal reading (K67); history.bundle replaced by HISTORY.txt (D-HISTORY).
- Hardening found in rehearsal: K60 (bench from ZIP), K61 (runaway pollers; one poller per computer), K62 (borderline
  eval, temperature 0 reverted), K63 to K66 (file viewer, evidence loop, column ids, poller write order), K67 (size).
- Mistake link table with a build gate (60 of 67 guarded, 7 process lessons); wiki, controls map, FAQ, cases.
- Internal notes added under _STATE (panel audit, question tree, lightning FAQ, enterprise test plan, design handoff).

## State
- rc35 is the latest verified release; main 175afe2 carries the newer page work (five-card start page, page bar,
  verdict-first pages, light/dark, deck opens in present mode on laptops).
- A design-gauntlet session is offered as a task chip; its handoff is _STATE/2026-10-13-ret-design-gauntlet-handoff.md.
- The explainer session is holding the video re-render until the design pass ends.

## Decisions
- Ship HISTORY.txt instead of the git bundle: the bundle was 8.7 of 10.4 MB; cited hashes stay findable.
- Submit from the free monday.com plan the brief prescribes; enterprise access is tested in a copy only.
- Deck first, then How we got here; proof, mistakes and build log become Evidence one level down.
- Zach's packaging model (presentation/ = deck, source/ = code and documentation, README = front door) goes to the
  design session, with a show-the-tree-first gate before any file move.

## Open
1. Zach: create view-only share links for the four RET boards, then wire them in.
2. Design gauntlet session: packaging model, one navigation system, link every provenance file, OTel answer.
3. Explainer videos re-render from the final head; then cut rc36 and run the live test from its ZIP.

## Next action
Start the "Run the RET design gauntlet" task chip.

## Cold-start
Read _STATE/2026-10-13-ret-design-gauntlet-handoff.md; repo /Users/zharris/ret-rfp-intelligence; `cd source && ./rfp serve`
then http://127.0.0.1:8765/presentation/index.html; `./rfp status`; releases via `./scripts/release_check.sh` (detached,
read dist/release_check_exit). Debt tracker: https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm (debt collection).
