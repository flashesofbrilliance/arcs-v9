<!--
session: claude-prl-handoff-memory-check-6c5e92
branch: claude/prl-handoff-oct9
head: 1ea21eeb
created_at: 2026-10-09T16:44:40Z
-->
> PRL Phase 1.2 wrap prep for Todd: overview overclaim fixed, go-live checklist folded into the runbook, refresher email drafted; the Oct 9 call moved to Mon Oct 12 10:00 ET.
## Goal
Land PRL Phase 1.2 as a clean go-live Todd can run, without pitching further phases (Todd wants to see the chatbot help the team first).
## Changed
- PR 1108 (merged): prl.arcs.care overview + runbook no longer claim leads carry the conversation (they carry "Chatbot Lead"; Task C unbuilt); update dated Oct 9; "nothing risky" replaced by two named checks (blank-email guard live, Zapier plan hold). Also fixed pre-existing page-gate failures: claude.ai artifact link, scrollspy error, runbook missing doctype.
- PR 1109 (merged): runbook "Go-live, three steps" expanded in place into a per-system checklist (Sugar, Zapier, Tidio, WordPress) plus a live proof chat; prl.arcs.care/go-live 307s to /status/runbook#go-live. A separate checklist page was started and dropped as a duplicate.
- Receipts logged: 2026-10-09--prl-overview-overclaim-fix-pr1108--ZH, 2026-10-09--prl-runbook-go-live-checklist-pr1109--ZH.
## State
- Verified in Gmail: Sep 17 recap was sent (9:16pm), no reply. No Loom from Todd. Oct 5 "Finding time" got no reply.
- Calendar: "Wrapping up Phase 1.2" Mon 2026-10-12 10:00-11:00 ET (Todd not yet accepted); "Coffee" Fri 2026-10-16 10:30.
- Gmail DRAFT (unsent): "Chatbot // go-live checklist for Monday 10am" to todd.hotes@prlresins.com, refresher + what Zach needs + what to work through.
- Redundant private artifact https://claude.ai/artifact/UKGKrsT9ygCUBAARVLqpEy still exists; delete needs Zach (session could not confirm).
## Decisions
- One home for go-live steps: the existing runbook section, not a new page or artifact.
- Frame Monday as a go-live working session; no 1.3 pitch until the team has used it.
## Open
1. Zach: review and send the refresher draft.
2. Zach: delete the redundant artifact.
3. Unknown whether the Sep 17 rough edges (lead marked dead, lagged lead, alert email not landing) were fixed; verify before Monday or say so on the call.
4. Blank-email guard verified only in draft; confirm in the published zap on the call.
## Next
Before Mon 10:00 ET: send the draft, then open prl.arcs.care/go-live and run the checklist live with Todd.
