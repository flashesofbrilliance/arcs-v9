# RET take-home: handoff after the design pass (internal, not shipped)

Updated 2026-10-14 ~00:10 ET. Branch `claude/brave-elion-c5e1fc` in worktree
`/Users/zharris/ret-rfp-intelligence/.claude/worktrees/brave-elion-c5e1fc`, head **d84aba6**. NOT merged to main,
NOT pushed, rc36 NOT cut. Zach submits Thursday morning; due Thu 2026-10-15 17:00 ET.

## Next session: land the plane (in this order)
0. **Dress rehearsal on d84aba6** (not yet run after the last three commits: slide 4 screenshots, PDF stamp,
   bench single-column faults and landing scroll). Export keys, then `python3 scripts/rehearse.py --live`; commit
   its run records after `scripts/proof.py` + `scripts/build.py` (the commit gate refuses stale figures). Also
   check in the browser that http://127.0.0.1:8765/#bench lands with the three figures just under the nav
   (code is after `await refresh()` in ui.html; not yet seen working because Zach was using the pane).
1. **Done: deck slide 4 screenshots** swapped (05d841d); the PDF stamp now hashes the deck's images too.
2. **Public board links.** Zach opens each board in monday.com; sharing is under the board's ⋯ menu / Share
   (Share view or Create shareable link). The free plan may not offer it; if not, the boards page (read back
   through the API) is the fallback and says so. If links exist: add them to the boards page, Read and README,
   with "revoke after review", and to the link check.
3. **Merge and push.** Merge the branch into main with `--merge`, push. Until the merge, commits in this worktree
   must use `git -c core.hooksPath=hooks commit` (the main checkout's hooks/ is still the old one).
4. **Explainer videos.** Tell the explainer session (uds:/tmp/cc-socks/88259.sock) to film from the final hash;
   MANIFEST must say "from ret-rfp-intelligence <hash>". Every page and the deck changed look (light-only Vibe,
   present-only deck, shared nav, bench header).
5. **rc36.** After the videos: export ANTHROPIC_API_KEY (from /Users/zharris/arcs-v9/.env.local), run
   `scripts/release_check.sh` detached, read `dist/release_check_exit`, live e2e from the ZIP, put the ZIP in
   iCloud `RET take-home/` in place of rc34.
6. **Portal.** Only then click Mark complete on step 05 and upload. Package structure on the portal: exactly
   `source/` and `presentation/` (README is source/README.md; presentation/ holds only the PDF). package.py gates it.

## What changed this session (all committed)
- Layout: presentation/ = the PDF only; review pages + deck.html in source/docs/site/; README in source/.
- Nav: one 4-item bar (Start, Deck, Read, Try it live) from home.py GNAV_STYLE, written into deck.html and
  ui.html between gnav markers and gated by home.py --check. Deck keeps a PDF | theme pill.
- Look: Vibe light tokens everywhere; dark switch on the deck only (Vibe dark, charcoal background); no HUD
  frame; sentence case; audit fixes (contrast #0060b9 text, 40px controls, radius 8, type scale, aligned tables).
- Bench: live instrument only; CLI snippet with copy; busy run answers 409 at once; three outcome chips (main set).
- Engine: superseded figure alone fails the verbatim gate (K69); fast path anchored; Windows-1252/BOM/UTF-16
  reading (K68); four new document faults; regression gate blocks new failing cases and runs all three sets (K70).
- Boards: 14 "[sample]" questions answered live (`./rfp samples`); State label colors synced (sink.color_states).
- Release: rehearse.py fixed for the layout and starts cold; canary fixed; link crawl 150/150; README rewritten
  (decisions first, keys table, configuration).

## Open, lower priority
- Persona gauntlet ledger: scratchpad gauntlet/findings-ledger.jsonl (99 findings, 58 fixed at the time).
  Open themes: local fallback 15/19; mock answers off-topic with a clause; no refusal for "contact the ISO" /
  "submit" / legal advice; amendment intake path undocumented.
- ~290 synthetic entries from an offline timing test sit in flightlog/bench_runs.jsonl (removal needs Zach's yes).
- README "about $0.75" is hand-written; slide 7 now computes $0.76.
- Rules in force: no internal vocabulary, figures from evidence.jsonl, no em-dashes, no --no-verify, stage by
  path, deletions need Zach's yes, measure 375px.

## Since the first version of this handoff
- 05d841d: fresh board screenshots on slide 4; build.py's PDF stamp covers deck images; bench lands on its figures.
- d84aba6: bench fault rows single column; "from the source folder" wording removed from the bench.
- Earlier tonight: deck present-only with the shared nav and a PDF | theme pill; light everywhere (dark switch on
  the deck only); Vibe audit batch (contrast #0060b9, 40px controls, radius 8, aligned tables); bench header
  (19 of 19 from the main set via dashboard.evals); link crawl 150/150; scrollbar always shown.
- Explainer session: film from the final hash after step 0 is green (every page, the deck and the bench changed).

## Kickoff prompt for the next session
"Continue the RET take-home. Read the cold handoff in full first:
/Users/zharris/arcs-v9/.claude/worktrees/mystifying-neumann-91d534/_STATE/2026-10-13-ret-design-pass-handoff.md.
Work in /Users/zharris/ret-rfp-intelligence/.claude/worktrees/brave-elion-c5e1fc (branch claude/brave-elion-c5e1fc,
head d84aba6). Do the finish line in order: step 0 dress rehearsal, then board links if Zach has them, then merge
and push on Zach's yes, hand the final hash to the explainer session, then rc36 after the videos. Rules: no
internal vocabulary, figures from evidence.jsonl, no em-dashes, never --no-verify, stage by path, commit with
-c core.hooksPath=hooks until merged, release_check.sh detached. Keep token use low: Sonnet subagents for
mechanical work."
