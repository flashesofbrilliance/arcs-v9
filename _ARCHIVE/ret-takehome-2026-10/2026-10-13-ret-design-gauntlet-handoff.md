# RET take-home: cold handoff for the design gauntlet session (internal, not shipped)

Written 2026-10-13 ~13:00 ET. Repo `/Users/zharris/ret-rfp-intelligence`, main at `175afe2`, pushed. Due Thu 2026-10-15
17:00 ET; Zach plans to submit Thursday morning.

## The deliverable (portal step 05, verbatim)
"Prepare source/, exactly one presentation PDF, and README.md inside one ZIP package." Under 10 MB, read as
10,000,000 bytes (the release check enforces this since K67). Top level of the ZIP is exactly `source/` and
`presentation/`; README is `source/README.md`; one PDF `presentation/RET-RFP-Intelligence.pdf`.

## State
- Last cut: rc35 (3.36 MB, release check exit 0, live e2e from ZIP passed). Files: `dist/submission-rc35.zip`.
  iCloud `RET take-home/` holds rc34; replace with the final rc.
- Since rc35, committed: shared page bar + Evidence group, five-card start page (deck, how we got here, boards, try it
  live, find anything), How-to-use drawer in the start header, theme icon in Grid/Present, verdict-first pages
  (mistakes as expandable rows, boards folded), light/dark everywhere, file viewer abs path + copy, deck opens in present
  on >=900px (grid on phones; `?view=grid`; overflow gate uses it), mistake link table + gate (60 guarded, 7 process),
  freshness step in release_check (boards re-read; video staleness warning), HISTORY.txt replaces history.bundle.
- Phone preview (private): https://claude.ai/artifact/TWik6eh8ZwJUQF7EfuA45J (republish from scratchpad copy with
  ../source links unlinked and the bench link disabled).
- Bench: `cd source && ./rfp serve` then http://127.0.0.1:8765/presentation/index.html. `./rfp status` / `./rfp stop`.

## Waiting on others
- Explainer session (uds:/tmp/cc-socks/88259.sock, "Rebuild explainer as capture of deck present mode") re-rendering
  opener, panel, 5 GIFs, how-i-built-this (Samantha voice). Last told: film from 3779368. The deck has since changed
  (present-mode default, 175afe2): tell it to film from the final head. MANIFEST must say "from ret-rfp-intelligence <hash>".
- Zach: create view-only share links for the four RET boards in monday.com, paste them; then wire them into boards page,
  wiki, README (+ limits line: revoke after review), data file covered by the link check.
- rc36: cut when videos land (Zach's instruction), then live e2e from ZIP, then put in iCloud in place of rc34.

## Decide first: Zach's proposed packaging model (2026-10-13)
"The deck we have is that PDF in the presentation, and the other stuff is the source (build documentation approach
etc), and README.md effectively acts like the how-to-use on Start here." I.e. map the bundle 1:1 to the deliverable's
three parts: `presentation/` = the deck (PDF, plus deck.html as its interactive form); `source/` = the code AND the build
documentation (review pages, evidence, wiki); `source/README.md` = the how-to-use and entry point (what is where, in the
assignment's five stages). Implications to weigh: the review pages (index, wiki, mistakes, boards, build log, how we
got here, proof) would move from presentation/ to e.g. source/docs/site/; every ../source link, the link checker's ZIP
layout, the bench's /presentation/ route, package.py's E8 checks, DEMO.md and README paths change; the start page's
How-to-use drawer content moves into README.md (generated from the same READ_ME data so it cannot drift). Recommendation
from this session: yes, it matches the deliverable's own words and removes the "which index do I open" question; do it
as the first step of the design pass, by script, behind the link check and a cold start from the ZIP.

## The design gauntlet (the job for the new session; run the impeccable skill, critique then one fix batch)
Zach's verdict: "This navigation is confusing." Known issues:
1. Wiki ("Find anything") has two rows of pills (areas, then section pills like "3 Evidence", "3.1 Evals") plus the
   shared page bar on other pages: three navigation systems. Section numbering ("3 Evidence") is internal.
2. Bench tabs (What it does, plan, timeline, beliefs, evidence, evals, test bench, glossary) overlap the wiki and the
   evidence pages. Zach asks: organize the bench's sub-tabs into the wiki and remove them from the bench? Decide the
   taxonomy: one place per kind of information; bench = live instrument only, wiki = reading room.
3. Mistakes page says "generated from KINTSUGI.md" without linking it; every provenance file named on any page should
   link (pattern exists: `linked()` in scripts/home.py for wiki tables; extend to ledes and verdicts).
4. Cold-reader (Ahmed) heuristic audit done 2026-10-13: walls were mistakes (7,747 words) and boards (221 cells); both
   folded. how-we-decided is 5,240 words behind a depth switch. Re-measure after changes.
5. OTel question from Zach: are there OpenTelemetry best practices for organizing the trace/observability view? The
   build has OTel-style spans (flight/recorder.py, flightlog/trace.jsonl). Answer honestly: what matches OTel semantic
   conventions and what does not; do not claim OTel compliance.
Gates for any change: `python3 scripts/build.py` + `--check`, `python3 scripts/home.py --check` (link check incl. ZIP
layout), unit tests `cd source && python3 -m unittest -q tests.test_seams`, `./rfp e2e --provider mock --runs 1`,
phone-width measure (375px, scrollWidth == width), no em-dashes, no internal vocabulary.

## After the design pass ("the fancy monday stuff")
Enterprise access arriving: test plan in `_STATE/2026-10-13-ret-enterprise-test-plan.md` (copy only, separate boards
and token, never change the submitted build). Wiki/governance spec: `_STATE/2026-10-13-ret-wiki-spec.md`.

## Rules in force
Never internal ARCS vocabulary in shipped files; every figure from evidence.jsonl (use {E-id|text}); no em-dashes;
never --no-verify; stage by path; merge with --merge; export ANTHROPIC_API_KEY before release checks; run
release_check.sh detached and read dist/release_check_exit; deletions need Zach's yes; no compliance claims.
Budget: weekly all-models ~65% used (resets Fri); prefer Sonnet scaffolding + Opus verification for bulk work.

## Constraints from the explainer session (2026-10-13)
Its rig frames `details#K27`, `details#K55` on the mistakes page and the boards fold summarized "What reading the boards
cost"; it hides `nav.gnav` in every shot. Keep those ids, that summary text and that element name, or tell it the new
ones. Its trial at 3779368 passed every shot; figures differ from a58e893 only in E-cycle-cost and E-repairs. Send it
the final head after the design pass; it renders all eight videos, then cut rc36.
