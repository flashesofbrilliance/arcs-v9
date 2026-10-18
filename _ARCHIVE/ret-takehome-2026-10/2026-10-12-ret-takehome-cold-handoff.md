# Cold handoff: RET take-home, 2026-10-12 evening

Not shipped (not in package.py SOURCE_PARTS). Read this, then `DEMO.md` (run of show). Nothing else is needed to start.

## Deadline and state

- **Due Thu 2026-10-15 17:00 ET.** Upload: `dist/submission-rcN.zip` (one ZIP: README.md at top, source/, exactly one PDF)
  plus an explainer video beside it.
- **Head:** `69485cf` on main, pushed. **Latest RC:** rc22 at `59b7c08` (9.43 MB of the 10 MB cap). **13 commits are
  not in any RC yet** (lean deck, `./rfp start`, boards page, run of show, ranked outcomes, re-grades, K59). Cut rc23 first.
- Each RC adds ~0.1 MB of history: about 5 cuts left. Batch fixes.
- GitHub Actions is billing-blocked: `scripts/release_check.sh` (detached, key exported) is the gate (D-RC14-GATE).

## Fold 1: the product (done, verified today)

- Live path works end to end: Key Facts (14 facts), Questions (answered live 7 times today), Solicitations, Pilot Scorecard.
- `./rfp start [--reset]` runs pre-flight, the bench and the poller in one terminal (no idle stop until Ctrl-C).
- Clean install from the rc22 ZIP verified (doctor reads the key from `.env`; Claude and local answer union labor
  "not addressed"); `./rfp verify-proof` ok; 31/31 unit tests; e2e 5/5.
- Real defects found late by testing like a user, all fixed: K55 (new amendment needed code), K56 (no paging past 100),
  K57 (Claude key not read from .env), K58 (poller could die mid-demo), K59 (lean deck overflowed in grid reflow).

## Fold 2: the presentation (deck frozen)

- Lean deck at `040c42f` + `0bc4f4b` + `69485cf`: ~675 words (from 1,358); one headline + one organism per slide;
  slide 3 is a ranked friction grid (four voices, three pains each); slide 4 names which pains each board relieves and
  carries the amended deadline (E-deadline, A).
- DEMO.md: full 60-minute run of show mapped to the brief's three parts and five proposal sections, timings, the
  "trace one answer" beat (`./rfp ask --json`, `./rfp verify-proof`), prepared answers, rehearsal checklist.
- monday.com Welcome Doc: intro, boards, "How we grade ourselves" checklist (33 of 36, dated, honest gaps), "Try it
  yourself". Video file block present (Zach uploaded); press play once to confirm.

## Fold 3: open decisions (Zach)

1. Cut rc23 now? (recommended yes, so the ZIP matches the rehearsal)
2. Board links labelled "needs an invitation" on boards.html and DEMO pre-flight? Invite panelists as viewers?
3. Extend the width sweep to the other generated pages (index, how-we-decided, boards, mistakes)? ~15 min.
4. Which video ships beside the ZIP: v4 (43 s), the long cut, or the cards-style render (next fold)?

## Fold 4: videos (owned by the explainer session, 88259.sock)

- Storyboard: `~/ret-rfp-explainer-rig/storyboard.md`: opener (A1-A7, ~90 s), long video as three Q&A rounds
  (C1-C12, ~2 min), five step GIFs (B). Cards style approved by Zach; canonical rig copy `~/ret-rfp-explainer-rig/cards-rig/`.
- Final render waits for Zach to say rehearsal 2 is done. Outputs ship beside the ZIP, never in it.

## Fold 5: rehearsal (Zach)

- Part 1 rehearsed once on the old deck; re-rehearse on the lean deck (target 15-20 min).
- Part 2 rehearsed partly; the trace beat is new. Part 3: the 12-question drill is in this session's last turns and
  mirrored in the storyboard C1-C12; the live panel drill stopped at Doug's question 1 (Amendment Two worded
  differently). Resume there.

## Fold 6: design-led audit backlog (for a fresh session, after rehearsal 2)

Run with the `impeccable` skill, bounded: per surface one `critique` pass, one batch of `distill` (cut words and
elements), one batch of `polish`, one confirm pass. Stop there. Rules that bind every pass: every figure from
`evidence/evidence.jsonl` (never typed); claims gate wording; no em-dashes; deck stays 10 slides and passes
`scripts/overflow_gate.py` (1280 real/fallback fonts + grid 390/820); `scripts/home.py --check` link check; one-writer rule.

| # | Surface | File | Panel sees it? | Audit focus | Priority |
|---|---|---|---|---|---|
| D1 | Deck (frozen; only defects) | `presentation/deck.html` | yes, Part 1 | type scale consistency across the new organisms; chips legibility at present size; slide 9 table density | high (defects only) |
| D2 | Start page | `scripts/home.py` → `index.html` | maybe | 7 tiles: distill copy to one line each; order by run of show | medium |
| D3 | How we got here | `scripts/home.py` → `how-we-decided.html` | if asked | eight sections: is each earning its place at Executive depth; empty Tactical cells in gaps/inputs/held | medium |
| D4 | What the boards hold | `boards.html` | if asked | wide tables on phones; long governing text truncation with expand | medium |
| D5 | Mistakes log | `mistakes.html` | if asked | 59 rows: group by kind; table on phones | low |
| D6 | Test bench | `source/harness/ui.html` | backup only | mock default label; header tiles; duplicate `/api/outcomes` call on load | low |
| D7 | monday.com boards | live boards | yes, Part 2 | column order and widths for the demo; "AI unavailable" label colour is green (set once by monday; fix in UI) | high |
| D8 | Welcome Doc | monday doc 18434979636 | yes | the order: video, checklist, try it; confirm video plays | high |

## Fold 7: harvest for the ARCS side (after Thursday, not in this repo)

Skill and workflow candidates (each proved here):
- **brief line-by-line trace** (requirements x shipped ZIP, MET/PARTIAL/MISSING/CONTRADICTED): found K55/K56.
- **claims ledger audit** (every sentence vs brief/logs/code, then a gate on false phrasings): found 4 false claims.
- **cold install from the shipped artifact** with a fresh `.env`: confirms what a reviewer gets.
- **CTO-in-a-box pulse check** and **outside-view research** (bounded searches): both flagged process-over-product drift.
- **friction audit** (per stakeholder, three ranked pains from their own words, then features mapped to pains).
- **`./rfp start`-style ignition command** for any client pipeline.
- **width-sweep reflow probe** (headless Chrome, no deps) for single-file decks.

Seed candidates: lane-timeline pattern (already chipped), 5x5 decision-geometry explorer (chipped, running separately),
persona UAT + definition-of-done skill, "What usage will teach us" pre-registered adoption plan, OKR level on ranked
outcomes, reusable delivery harness as an FDE team standard (evidence grades, claims gate, rubric, mistakes log).

## Cross-session protocol (unchanged)

One writer to `~/ret-rfp-intelligence` at a time; start only after an explicit "handed back at <sha>". Stage by path;
never `git add -A`; never `--no-verify`; merge with `--merge`; let the pre-commit hook finish; export
ANTHROPIC_API_KEY before any eval or release check; stop servers with `kill $(lsof -ti tcp:<port>)`.
