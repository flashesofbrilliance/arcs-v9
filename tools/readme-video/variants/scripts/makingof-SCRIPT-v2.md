# Making of v2: compound engineering (DRAFT, not recorded)

Lens: each piece of work leaves something that makes the next piece cheaper. Same kit and voice (Zach Harris clone)
as the walkthrough. Narration is in spoken form (no digits or symbols). Frame text <= 45 words. Every step cites a
real artifact; sources are listed under each section and are not spoken.

## 01

Every fix today left something behind. A rule, a check, a reviewer, a tool, or a task for the next session. That is compound engineering: each piece of work makes the next one cheaper.

Chip: `Each fix leaves a tool`
Frame: the chain as six linked boxes, empty, lighting left to right as the video goes.
Sources: this session's work, 2026-10-30.

## 02

Here is one chain from today. A line of copy sounded wrong. It became a written rule, then a check that runs on every script, then a reviewer that gates every render, then shared tooling, and finally a task in the backlog.

Chip: `Correction to rule to gate to judge to tool to task`
Frame: the six boxes labelled (correction, rule, check, judge, tooling, backlog row).
Sources: the chain steps cited in 03 to 05.

## 03

It started with one rule's wording. "No answer without a real source" sounded strange out loud. The rewrite became part of the video rules, and a punctuation check now reads every script before it is recorded.

Chip: `One wording fix, one standing check`
Frame: before and after line; arrow to the rules doc and to check R11.
Sources: card 04 copy change (Zach, 2026-10-30); video kit spec and typography rules on PR 1877; readme_video_check R11 punctuation lint (commit 298ddbb2, on PR 1877, merged 2026-10-30).

## 04

Then a reviewer. The brand line producer checks every frame before it renders. It blocked these videos twice, on margins, type and density. The music tool, with its splice and voice ride, is now shared by both videos.

Chip: `Blocked twice, fixed, passed`
Frame: the gate as a checkpoint with two red stamps then green; mix.sh feeding two video strips.
Sources: brand-line-producer agent, PR 1875 (merged 2026-10-30); gate reports in this session; mix.sh with splice and spans ride (scratch folder, used by both videos).

## 05

The last link is the backlog. Findings become rows, each with a route, its gates, a trigger and what it depends on. A graph orders about four hundred rows into thirteen waves, and lists what is ready to start now.

Chip: `About 400 rows, 13 waves`
Frame: the graph as waves left to right; one row card lit: arcs-mini-adopt-design-md-motion, READY, with its route and gates.
Sources: _QUEUE/induced-backlog.jsonl; scripts/backlog_graph.py run 2026-10-30 (394 rows, 13 waves deep, in this checkout; main has 409 rows); row arcs-mini-adopt-design-md-motion (state READY, from PR 1877, merged 2026-10-30).

## 06

Some of it broke on the way. A timing bug put reveals on estimates instead of the voice. The reviewer caught frames twice too dense for the rules. The timing was fixed in the tool, so it stays fixed. Density was trimmed by hand.

Chip: `Timing in the tool, density by hand`
Frame: three breaks, each with its seam and the tool that now holds the fix.
Sources: fluid-card.cjs snap fix; brand gate density block; kit.cjs refit (this session).

## 07

Some of it is not built yet. The checks for type size and density still live in the reviewer's judgment, not in a script. Many backlog rows name no tool the graph can find. And the music tool is not in the repository yet.

Chip: `3 gaps, stated`
Frame: dashed boxes for each gap.
Sources: video kit spec ("Not built yet: the ramp and density checks"); backlog_graph.py (172 rows NOT-RESOLVED in this checkout); mix.sh lives in the scratch folder.

## 08

To see it yourself, run the backlog graph. It shows what is ready now, and the next session can start from the top row without replanning.

Chip: `Run /backlog-graph`
Frame: terminal callout with `/backlog-graph`, arrow to the "ready now" list.
Sources: .claude/commands/backlog-graph.md.
