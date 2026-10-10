<!--
session: lab-assessment-experiment-wrapper (relay, read-only on the take-home since 13:13 ET)
branch: claude/lab-assessment-experiment-wrapper-dd51d3
head: f9f18b99
created_at: 2026-10-10T22:04:32Z
-->
## Changed
- monday FDE take-home: built the core (morning), then handed it off at 13:13 ET to the single writer "Continue monday take-home from HANDOFF.md". From then on this session was read-only on `~/ret-rfp-intelligence` and relayed ~30 approved asks by message.
- #1143 merged (54b1539a): write-locked `_ARTIFACTS/forge-monday-fde/takehome/CHRONICLE.md` (first prompt incl. pre-work to 15:00 ET; 8 phases, 10 turning points, SSOT map), an `atlas.json` (arcs.atlas.v1 ziggurat, 12 tiers, YELLOW) and a `MANIFEST.json` of hashes. Receipt `2026-10-10--monday-takehome-chronicle-atlas-pr1143--ZH`.
- Amendment 1 to the chronicle (f9f18b99): usage and allocation readout from Zach's usage panels.
- Private kanban of the take-home plan: https://claude.ai/artifact/9zS9Md9E8mwZXLELVYtQ7B (generated from plan.json by a scratchpad script; tabs per workstream, a Cut lane).
- `_ARTIFACTS/forge-monday-fde/takehome/HANDOFF-making-of.md`: spec for the optional "making-of" easter egg (fork the blacksmith observatory + the status/beliefs pages, scrubbed; Suno bed optional).
- Memory: new `relay-scope-check-against-brief-before-forwarding`; `session-budget-discipline-cap-parallel-molt-long` lowered to fold at 80k, molt at 100k or 4 h, with the 2026-10-10 spike post-mortem.

## State
- Take-home at ~18:00 ET: e2e dry run green (mock 7/7, from the ZIP 7/7, live 3/3); deck and front page frozen; CI green; K1-K46; D-SCOPE and D-SUBTRACT in force. Last relays (onboarding docs, "as of" label on the build cost) are queued to the writer, unread at handoff.
- This session ran far past the new molt threshold. Retire it.

## Decisions
- D-SCOPE confirmed by Zach ("focus on rehearsal"); the over-build seam was mine (relaying without a brief check).
- Making-of video OK as an optional easter egg, after rehearsal, in a fresh session, built from records, no new dependencies.
- Build cost stays on the deck, labelled API-equivalent compute on a subscription, with an "as of" time.

## Open
1. Writer: ONBOARDING.md + docs/using-the-boards.md (doc-as-test from the ZIP, cold-reader pass); the "as of" label.
2. Zach: dress rehearsal following ONBOARDING.md, then submit by Thu 2026-10-15 17:00 ET.
3. Fresh session: the making-of, per HANDOFF-making-of.md, after rehearsal.
4. Optional: a code-tour drill for Zach's weak spot (navigating code and diffs); it can fold into the making-of drill mode.
5. Optional: wire the fold/molt thresholds into a hook (memory-only today).

## Next action
Zach runs the dress rehearsal once the writer lands ONBOARDING.md.
