---
name: scrum
description: The scrum master ritual, an exoskeleton for cadence. `/scrum` (or `/scrum standup`) is the 2-minute daily check; `/scrum groom` is the 25-minute weekly groom (fate old rows, commit at most 5, revisit one rule). Use at the start of a work day, when the session-start hook says the groom is overdue, or when Zach says he is spinning, sprawling or doesn't know what to do next.
---

# /scrum [standup|groom]

Zach asked for this so he keeps the cadence without having to remember it. The script does the counting
(`scripts/scrum.py`, deterministic, so the same state always gives the same board). You hold the timebox,
make the call on defaults, and keep it short. Facilitate it like a scrum master: the board is a mirror, not a lecture.

The point of the groom is to take things away. Closing a row, cutting a rule or letting a report go is a win. Adding
a row, a tool or a scheduled task during a groom needs a reason said out loud.

## Standup (default, 2 minutes)

1. `python3 scripts/scrum.py standup`. Read the four lines back in plain words. Add nothing else.
2. Ask one question: "Is today's one thing still the one thing?" A yes ends it. A no gets one sentence on what
   replaces it. Keep the sprint, don't replan.
3. `python3 scripts/scrum.py log --ritual standup` (it records the habit and nothing else).
4. If the script says the groom is overdue, offer to run it now or name a time today. Don't nag about it twice.

## Groom (weekly, 25 minutes; say the clock out loud at the start)

`python3 scripts/scrum.py board`, then take the sections in order. Batch the questions: one AskUserQuestion with
at most four questions, multiSelect where it fits (memory `prefers-interactive-multipicker-decompose-and-rerender`).

1. **Said vs did (3 min).** Read section 2. Don't explain a miss away. Ask what made it slip once, then move on.
   A row that slipped twice gets cut from the sprint by default.
2. **WIP (3 min).** Anything over cap: name what has to finish or stop before anything new starts. Open PRs over cap:
   run `python3 scripts/approvals_ledger.py` and list the ones Zach can merge or close right now. He does the merge.
3. **Fate (8 min).** Section 5's ten rows. Show each with its default; Zach answers "approve defaults" or names the
   exceptions. Apply them with `python3 scripts/scrum.py fate --compost a,b --note "<why>"`
   (`--renew x --review-by YYYY-MM-DD` for a renew). Compost keeps what was learned in status_note, so nothing is
   lost. Re-running a fate is a no-op, so a groom that gets interrupted can just be run again.
4. **Debt, if time allows (4 min).** If `_STATE/reconcile/` has this week's report (the Monday JTBD task writes it),
   take its top 3 **mechanical** items as candidate rows for the sprint. Judgment items wait for next week.
5. **One rule (4 min).** Section 6 names the next rule nobody has reviewed. The bias is toward trust: models are
   better now, and a rule that spells out *method* (how to read, how to plan, what order to check things in) usually
   holds back judgment more than it prevents mistakes. A rule that guards a **one-way door** (merge, send, publish,
   money, canon, secrets, deleting data) stays unless Zach says otherwise. Propose a verdict with one line of reason:
   - `cut`: no incident in 30 days that it would have prevented, and a careful engineer would do it unprompted.
   - `loosen`: keep the outcome, drop the steps.
   - `move`: it only matters for some files, so it goes into a path-scoped `.claude/rules/` file.
   - `keep`: it guards a door, or it caught something recently (cite it).
   The edit itself is a separate small PR with the rule's own receipt. Global `~/.claude/CLAUDE.md` edits are
   Zach's to approve line by line. Record the verdict even when the answer is keep.
6. **Commit (3 min).** At most 5 rows, from READY and `python3 scripts/backlog_graph.py --top 5`, plus one sprint-goal
   sentence. The script refuses a sixth row. Then:
   `python3 scripts/scrum.py log --ritual groom --commit a,b,c --rule <ID> --verdict <v> --minutes <N> --note "<goal>"`
7. **Scheduled reports (only on the first groom of the month).** `list_scheduled_tasks`: any enabled task that hasn't
   run in 14 days, or whose purpose is past, gets a disable proposal. Fewer reports that get read beat more that don't.

End with one line: the goal, the 5 rows, what got cut. No summary essay.

## Commit the ledger

`_STATE/scrum/ledger.jsonl` and the backlog fates go in a docs-only PR (`scripts/ship_docs.sh`). The fates touch
`_QUEUE/`, so run `python3 scripts/backlog_status_check.py --check` before shipping.

## Never

- Merge, send, publish or delete for Zach. Fates on backlog rows are the only writes, and only after he says yes.
- Re-derive what the script already printed, or pad the board with your own extra checks.
- Shame. A missed groom shows up as a date, not a judgment. Pick up from where things are.
