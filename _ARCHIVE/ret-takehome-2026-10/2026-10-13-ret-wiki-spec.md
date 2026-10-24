# RET RFP Intelligence: reconciled wiki, controls map and monday.com governance surface

Design spec, product requirements and implementation plan. Internal working document, 2026-10-13. Not shipped.
Status: proposal for Zach's decision. Submission due Thu 2026-10-15 17:00 ET; the ZIP is at 9.86 of 10 MB.

## 1. Problem

The build is complete but hard to navigate:
- `source/` opens on 13 top-level Markdown files plus 15 folders, and the code itself sits one level down in
  `source/source/`, which reads as a mistake.
- Governance evidence is real but scattered: decisions (DECISIONS.md), mistakes and repairs (KINTSUGI.md), constraints
  (CONSTRAINTS.md), release gates (scripts/package.py, release_check.sh, hooks/), change history (git, build log),
  evals (source/eval/, flightlog/eval_runs.jsonl), evidence rows (evidence/). Nothing says which file proves which control.
- IDs (K27, Q7, W4, D-SCOPE) are cited everywhere and explained in one place, far down the page.

A reviewer, an RET admin, or Nina should find "what proves X" in one click, not by reading the tree.

## 2. Principles

1. **Map, don't move (before submission).** 66 mistake rows, 26 decisions, every test and every page cite today's
   paths. Moving files now breaks citations the panel may click. The wiki is a generated layer over the files as they are.
2. **One record per file.** Every shipped file is classified once, in a manifest; every page is generated from it.
   Nothing about the structure is typed twice.
3. **Every control points at evidence that runs.** A control is listed only with the test or gate that checks it and
   the log that shows it ran. No control is claimed on description alone; no certification is claimed at all.
4. **monday.com is the operating surface, the repo is the source of truth.** Boards show status; files and git prove it.
5. **Same gates as everything else:** link check, cold start from the ZIP, size cap, no internal vocabulary.

## 3. Information architecture (nested)

```
1 Product            what it does, for whom            README, ONBOARDING, docs/using-the-boards, install.sh, FAQ (new)
  1.1 Run it         start, status, stop, troubleshoot TROUBLESHOOT, rfp launcher, start.py
2 Architecture       how it works                      README architecture, source/rfp/*, sync_boards, live_questions, harness/
  2.1 Data model     tables, boards, ids                rfp/store.py, rfp/sink.py, .rfp-boards.json (local)
  2.2 Integrations   monday.com, model providers        rfp/monday.py, rfp/provider.py, docs/monday-platform.md
3 Evidence           what is true, graded               evidence/evidence.jsonl, evidence/blind, proof-of-one-answer
  3.1 Evals          test sets and every run            source/eval/*.json, flightlog/eval_runs.jsonl, sim/
4 Governance         why, and what went wrong           DECISIONS, KINTSUGI (mistakes log), CONSTRAINTS, HYPOTHESES
  4.1 Controls map   control -> test -> log (new)       section 5 below, generated page
  4.2 Change control commits, releases, gates           git history (history.bundle), hooks/, release_check.sh, package.py
5 Presentation       for the panel                      deck.html, PDF, index, how-we-decided, mistakes, boards, build-log
6 Build history      how it was made                    JOURNEY, RCA, plan.json, flightlog/*, turning points
```

Every node lists its files from the manifest, each opening through the bench's file viewer (K63).

## 4. Product requirements

| # | Requirement | Who | Acceptance test |
|---|---|---|---|
| R1 | Every shipped file appears exactly once in the manifest with a section, a one-line purpose and an owner | reviewer, admin | build fails if a shipped file is missing from the manifest or listed twice |
| R2 | A wiki page renders the tree in section 3 from the manifest; every entry opens the file | reviewer | link check: 0 broken, from the repo and from the unzipped ZIP |
| R3 | Every ID (K, Q/W/T/X, D-) has a tooltip on hover, focus and tap, and a Glossary tab lists them all | everyone | IDs that exist get a tooltip; strings that only look like IDs ("Q4 2026") do not |
| R4 | A controls map lists each control with the gate or test that checks it and the log that shows it ran | Nina, Sam | build fails if a control names a test or file that does not exist |
| R5 | A stakeholder FAQ answers the panel's likely questions with figures from evidence ids and a source per answer | RET staff | provenance lint passes; every answer has a source that resolves |
| R6 | No file moves before submission | Zach | `git diff --name-status` shows no renames in the submission range |
| R7 | (post-submission) monday.com boards mirror control status, releases and eval runs | RET admin, Elena | one sync creates the boards; a re-run creates nothing; free-plan call budget respected |

Non-goals: compliance certification; a hosted wiki; editing documents in monday.com; moving code before submission.

## 5. Controls map (first draft; every row must point at something that runs)

| Control | What it guards | Checked by | Shown in |
|---|---|---|---|
| Change control | no unreviewed change ships | pre-commit hook (hooks/pre-commit): provenance, secrets, leak, security, tests, evals on engine change | git history in history.bundle; every commit 1-1 with a build span |
| Release gate | only a passing build is packaged | scripts/release_check.sh, package.py (E1-E11) | rcN tags; dist/release_check.log |
| Figure provenance | every number traces to evidence | scripts/provenance_lint.py, build.py --check | evidence.jsonl; grades A-D on every figure |
| Claim accuracy | no false sentence on the slides | build.py --check refused phrasings (K54) | D-CLAIMS |
| Answer integrity | figures word for word or withheld | answer.py figure check; eval sets wave 1-3 | flightlog/eval_runs.jsonl |
| Amendment handling | the governing value wins; unreadable wording is flagged | resolve.py rules; test_unreadable_amendment... | Key Facts State column |
| Data egress | only what is stated leaves RET | glossary.json what_leaves, build.py check | flightlog/model_calls.jsonl |
| Write scope | only four boards can be written | sink.py ALLOWED_BOARDS; war-game attacks | sim/wargame.py runs |
| Secrets | keys never in git or logs | pre-commit secret scan; doctor.py .env check | doctor output |
| Operational safety | one poller, call reserve, safe stop | runlock.py; K61 tests | ./rfp status |
| Schema stability | board renames harmless, deletions loud | sink.py recorded ids; K65 test | .rfp-boards.json |
| Honest limits | gaps named, not hidden | README "Limits and disclaimers", "not tested" table | README |
| Mistake handling | every own error logged with its repair and test | KINTSUGI.md; turning points | mistakes.html, timeline |

Known gaps to list as "not yet controlled": call-log retention and access (README), local-model fingerprint (round 4).

## 6. monday.com as the governance surface (post-submission, phase 2)

Three boards, written by the same sink (added to ALLOWED_BOARDS in review), idempotent by Key, within the free plan:
- **RET · Controls**: one item per row of section 5; status from the last release check (Passing / Failing / Not yet
  controlled), link to the evidence file. Written at each release, about 15 calls.
- **RET · Releases**: one item per rcN tag: date, size, gates passed, commit. About 3 calls per release.
- **RET · Eval runs**: one item per eval run: set, model, score, worst case. Already logged locally; mirrored at release.
Why not live: the call budget (1,000 a day, K61) and the rule that the repo, not the board, is the source of truth.
Enterprise would add an automation (Controls item turns Failing -> notify Nina), untested (D-PLAN).

## 7. Implementation plan

**Phase 0, before submission (about 2.5 h, no file moves, no deck change, a few KB):**
1. `docs/catalog.json`: the manifest (R1), generated first from `git ls-files`, then each row given a section and purpose.
   Gate: build fails on an unlisted shipped file.
2. `presentation/wiki.html` from the manifest (R2), an eighth card on the index ("Find any file"). Link check covers it.
3. Bench tooltips and a Glossary tab (R3); the mistakes legend moves into the Glossary.
4. `evidence/faq.json` and `presentation/faq.html` (R5), a ninth card, or a section of the wiki page to keep the index at eight.
5. Controls map (R4) as a section of the wiki page, generated from `evidence/controls.json`; build fails on a dead reference.
6. Model fingerprint in `./rfp doctor` (closes a section-5 gap).
7. Gates: unit tests, mock e2e, link check from the ZIP, one live e2e from the final ZIP, release check. Cut the final rc.

**Phase 1, pilot week 1 (after the interview):** physical restructure, done once with the manifest as the map:
`source/source/` becomes `source/app/`; top-level docs move under `source/docs/{product,governance,history}/`; a
script rewrites every citation from the manifest and the link check proves nothing broke; old paths listed in a
redirect table in the wiki.

**Phase 2, pilot weeks 2-3:** the three monday.com boards in section 6, behind the release check.

## 8. Risks and decisions for Zach

| Risk | Mitigation |
|---|---|
| New surface three days out (D-SUBTRACT) | phase 0 is generation over existing files; no moves; every page behind the same link check |
| ZIP size (0.14 MB left) | phase 0 adds HTML and JSON only, estimated under 40 KB; measured at release |
| The manifest drifts | the build fails on any unlisted or duplicated file |
| A restructure breaks citations | deferred to phase 1, done by script from the manifest, verified by the link check |

Decisions needed: (a) approve phase 0 tonight; (b) FAQ as its own card or inside the wiki page; (c) phases 1-2 as the
"what's next" answer in the interview, not built before it.
