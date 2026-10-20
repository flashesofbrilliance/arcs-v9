# Take-home session postmortem: user turns

Sources: sessions bdc2caab and 619c04b7 (117 user turns, 13-14 Oct) plus arcs-v9 orchestrator 66a03f8a. 38 deduplicated rows in sessions.jsonl.

## Recurring corrections (ranked by count)
1. Cross-session routing and verification (about 25): the user pinged, checked and re-checked sibling sessions and origin/main by hand.
2. Bulk approval gates ("yes, go ahead", "do A through D, then rehearse") (about 12).
3. Look at the real UI (comet tabs, monday boards) rather than inferring (about 10).
4. Sync every mirror: zip, README, monday Welcome Doc, GitHub, PDF, boards page (about 10).
5. Shared styling and nav across all pages, row grids, FOUT, motion polish (about 7).
6. Land the plane, table it (about 8 scope cuts).
7. Liveness: "still running?", "any update?" (about 5).

## Standing rules and preferences
- Follow the brief's literal pass/fail packaging (source/, one PDF, README) and mimic the employer's own bundling style.
- Hiring-manager persona gauntlet and grading panel before release; rehearse after each change.
- Light mode default; dark only on the deck. Calm, crisp motion.
- One-shot commands; copy-paste CLI quick start; first screen must work for reviewers who skip the README.
- Backlog goes to todo.md with unblock criteria; freeze the RC.
- Prove non-technical UX through the monday UI, with screenshots.

## Where the assistant needed steering (blindspots)
- Did not volunteer where the final zip lives, or whether changes reached GitHub, the monday doc and the PDF.
- Did not walk the reviewer journey: public board links, submit permissions, hyperlinks in the PDF.
- Proved things on the backend, not the front end.
- Explanations assumed the user followed the mechanism ("I don't understand how it works on the board").
- Parallel sessions risked clobbering shared files; media ended up in the zip folder.
- Stale artifacts: static build log, outdated Welcome Doc, unbacked deck claims.

## Late-stage scope additions
Currency-conversion test, four document faults, quick-start snippet, pre-populated board, YouTube card, thumbnail and end card, [live] tag, todo.md, name and email on slide 1, public-link shutoff.

## Five operating rules for the next take-home
1. Before building, extract the brief's hard pass/fail rules and a reviewer-journey checklist (zip layout, links, permissions, first screen). Check them at every release candidate.
2. After every change, run one sync checklist and report it: bundle path, README, hosted doc and boards, GitHub, PDF freshness and claim audit.
3. Verify through the reviewer's real path (their UI, one command) with screenshots. Backend success is not proof.
4. Offer lettered options with a recommendation for bulk approval, then execute and rehearse. Park extras in todo.md and keep the RC frozen unless the user asks.
5. Run one session per deliverable with declared file ownership. Report liveness, commit shas and push state without prompting. Never claim delivery without confirmation.
