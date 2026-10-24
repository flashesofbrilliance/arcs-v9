# Phosphor: 25 outcomes for child sessions (2026-10-24)

**What "outcome" means here.** An outcome is what happened to a person after we changed something, written as a claim that can later be marked true, false or unknown. It is not a feature and not a metric. A receipt records what we decided and what we checked; an outcome is the later result, supplied by a person or by a local log, never by the build.

**Evidence status, stated first because it limits everything below.** Phosphor sends nothing anywhere, so there is no usage data. The only revealed behaviour on record is one child, reported by Zach in chat on 2026-10-23. Two outcomes are OBSERVED (n=1, an anecdote, not a measurement). Every other row is a HYPOTHESIS or SHIPPED with its measure named; none is measured. "Measure" says how it could be measured: LOG means the opt-in local play log (Play log button in Parent mode, kept on the device), WATCH means a person watches a real session and writes it down, REPORT means a parent says it after the fact.

Version control for an outcome: each row has an id, a status, and when it changes status the change is a new line (v1, v2) citing the receipt or the person, so the history of what we believed stays readable.

| # | Outcome (child sessions) | Measure | Status |
|---|---|---|---|
| 1 | He begins without being asked | WATCH + LOG (begin event) | HYPOTHESIS. Row phosphor-first-minute-ritual; slice 1 shipped, not measured |
| 2 | He discovers that his keys change the picture and loves it | WATCH | OBSERVED n=1 (Zach, 2026-10-23) |
| 3 | Seconds from page open to first sound | LOG | SHIPPED, not measured (the begin event records it) |
| 4 | Whether he begins with a key or a tap | LOG | SHIPPED, not measured |
| 5 | He comes back another day without a reminder | REPORT | NOT MEASURABLE by design: nothing is stored, no reminders, so only a parent can say |
| 6 | Length of a play session | LOG | SHIPPED, not measured |
| 7 | Number of different controls touched in the first minute | LOG | SHIPPED, not measured |
| 8 | Accidental pauses per session fall after the Space change | WATCH + LOG | OBSERVED n=1 for the problem (many accidental pauses); the fix shipped in release 7, effect not measured |
| 9 | Deliberate stops (a 0.6 s hold) outnumber accidental ones | LOG | HYPOTHESIS |
| 10 | He does not leave within the first 60 seconds | LOG | HYPOTHESIS |
| 11 | He finds the dry cut (Space tap) without being told | WATCH | HYPOTHESIS |
| 12 | He finds the pads without being told | WATCH | HYPOTHESIS |
| 13 | He tries the Glitch presets and has a favourite | LOG | HYPOTHESIS |
| 14 | He starts and stops the music with a hold without help | WATCH | HYPOTHESIS |
| 15 | He goes back to the same preset on purpose | LOG | HYPOTHESIS |
| 16 | He makes a loop he wants to keep | WATCH | NOT BUILT: needs the my loops shelf (row phosphor-my-loops-shelf) |
| 17 | He chops a song into pads and plays them | LOG + WATCH | SHIPPED, not measured |
| 18 | A parent grabs a gesture and replays it | WATCH | SHIPPED, not measured |
| 19 | A parent shares a recipe link and the other person loads it | REPORT | SHIPPED, not measured |
| 20 | He asks someone else to try it, or copies what they do | WATCH | HYPOTHESIS (row phosphor-copy-me-game) |
| 21 | He never leaves Kid mode by accident (Eject needs a 3 s hold) | WATCH | SHIPPED; real-iPad proof still owed |
| 22 | The volume stays under the ceiling during play | guard check | SHIPPED, checked in tests, not on headphones |
| 23 | No flashing above the safe rate during play | guard check | SHIPPED, checked in tests |
| 24 | A parent understands what is stored (nothing leaves the device) | REPORT | HYPOTHESIS |
| 25 | A parent can pause and restart in one deliberate hold without help | WATCH | HYPOTHESIS |

**Reading the table.** 2 of 25 are observed, both one child. 11 are shipped features whose effect nobody has measured. 1 cannot be measured by design and 1 needs a feature that does not exist. The honest summary is that Phosphor has built the means to measure outcomes 1, 3, 4, 6, 7, 9 and 10 (the local play log) and has not yet run a real session with it on.

**Not claimed.** No row here says a child learned anything. No row is evidence for ARCS itself; they are claims about Phosphor.

**Sources.** Receipts 2026-10-23--phosphor-first-minute-ritual-pr1804--ZH and 2026-10-23--phosphor-release-7-pr1806--ZH (decision_receipt table, project xbbpiryokswwvcrcutge); amendments 68 and 69 in _PATTERNS/2026-10-15-phosphor-visualizer-prereg.md; _PATTERNS/2026-10-17-phosphor-journey-and-hardening.md for the earlier statement that no child had used the build. The two observed rows rest on Zach's chat messages of 2026-10-23, which are not stored anywhere else; that is UNCONFIRMED beyond his word.
