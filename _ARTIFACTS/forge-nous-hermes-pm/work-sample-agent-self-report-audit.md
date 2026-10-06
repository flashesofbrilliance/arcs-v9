# When an agent says "done": a user's audit of Hermes Agent self-reports

Zach Harris · written for the Nous Research Hermes Agent PM application · small sample, older release, treat as a hypothesis generator

## What I did
On 2026-08-30 I ran Hermes (the `~/.hermes` runtime, v0.20.6 at the time) as one leg of a two-harness build: Hermes generated, Claude Code verified, and git was the single source of truth. Every factual statement Hermes made about its own work was checked against the committed tree.

## What I found
| Hermes said | The committed tree showed |
| --- | --- |
| A file was 653 and 232 lines | 655 and 685 lines |
| "diff exit 0, already in parent" | It had committed the wrong 273-line file |
| "36 of 36 pass, record_coverage wired" | False on the committed tree |
| "verified working on disk" | True of its working copy, false of git, three separate times |
| One conformance report | True, but only provable after I ran an execution test; the table alone could not show it |

The work itself was real and often useful. The problem was narrower: a true "done" and a confabulated "done" looked identical from outside.

## What I changed in my own process
- The agent generates; an independent check, written by someone else, runs against the committed tree.
- "Verified" is a claim until a command's output backs it.
- Nothing merges on an agent's say-so.

## Product hypotheses for Hermes Agent (to test, not to assert)
1. **A completion receipt.** When the agent reports done, attach the command run, its exit code, and the diff it refers to, so the claim carries its own evidence.
2. **Claimed vs. verified in the UI.** Show the two states differently, so a user learns when to trust the summary.
3. **Check-before-done.** Let a user attach a test or hook that must pass before the agent may use the word "done."
4. **Measure it.** Track the share of "done" reports a user later reverts or corrects. That is an activation and trust metric you can trend by release.

## Limits
One thread, one user, one day, an older release, my own configuration. I would rerun this on the current release before drawing any conclusion about today's Hermes. Source notes are in a private repository and can be shown on request.
