# Cold-start meta prompt: counterpart surface through the two-ended gate (ADR-075)

> Paste into a NEW session to test the updated global configs (recoil-prep Step 1.5, recoil-ship render
> gate, cold_reader_gate R0 to R7, pre_prep_gate P0 to P7, the cold-reader rubric). Fill the {{params}}.
> Every step names the file it reads or writes, so a session that has never seen this repo can run it and a
> reviewer can score it from the receipts alone. Components are independent: run one, several, or all.

## Parameters
| param | meaning | example |
|---|---|---|
| {{COUNTERPART}} | reader's name and role | Saul Miller, VP Data Ops candidate |
| {{SSOT}} | account SSOT json (create with /recoil-new if absent) | runtime/recoil/generated/2026-09-01-saul.json |
| {{DATA}} | surface data json for the renderer | runtime/recoil/generated/saul-prep-data.json |
| {{TRANSCRIPTS}} | Granola ids or file paths, raw transcripts only | 363c13a2 |
| {{STAGE}} | Receipt Loop stage of the reader | before · during · after · share · compounds |
| {{SURFACE}} | renderer + output | render_prep_v2.py → public/{{slug}}-v2.html |
| {{ACCEPTANCE}} | who reads it and the pass condition | Ahmed states what/why/do inside 2 minutes |
| {{BUDGET_MIN}} | build minutes allowed (read budget = this/10) | 60 |

## Session contract (read first, then do not re-orient)
1. Read only CLAUDE.md's latest `# Handoff` block and `_SPECS/cold-reader-rubric-v1.md`. Nothing else to orient.
2. Cost line before starting: est. human time · est. actual · ~Nx. State it, then proceed.
3. No em-dashes. Inline styles only. No new deps. Oracle for any ADR/seed number. Commit on the working branch.

## Component 1: input gate (pre_prep_gate, P0 to P7)
- Pull {{TRANSCRIPTS}} with `get_meeting_transcript` (never a summary tool). Save to disk under `_ARTIFACTS/transcripts/`.
- Write the `pre_prep` block into {{SSOT}}: filed date · raw_sources (verbatim, on disk) · asks (verbatim quotes, source, answered_by) · reader {who, stage={{STAGE}}} · subject {about, same_as_reader, reader_asked_for_it} · format_spec (their words or none_found) · arriving_state {state, quote} · budget {build_minutes={{BUDGET_MIN}}, read_minutes}.
- Run: `python3 scripts/pre_prep_gate.py {{SSOT}}`. STOP on FAIL. Fix the block from the sources, not by loosening the gate.

## Component 2: render in the grammar
- Data shape for `scripts/render_prep_v2.py`: verdict {instance, line, next_step} · reasons[3] · questions[3]{q,a} · tasks[] · blocks[]{title, takeaway_open, figure (one table|number|list), takeaway_close} · record_links[] · read_minutes.
- Run: `python3 scripts/render_prep_v2.py --data {{DATA}} --out public/{{slug}}-v2.html`.
- The renderer emits the order; do not reorder by hand. If the data lacks a field, fix the data.

## Component 3: output gate (cold_reader_gate, R0 to R7)
- Run: `python3 scripts/cold_reader_gate.py public/{{slug}}-v2.html`. STOP on FAIL. Fix content order or disclosure, never the gate. If the gate contradicts a counterpart's stated verdict, amend the calibration set in ADR-075 instead.
- Then the judgment half: `/counterpart-gauntlet {{COUNTERPART}} --facet cold-reader` (from the first screen only: what is this, why should I care, what do I do). Any "not sure" fails.
- Then the existing chain: `scripts/leak_check.sh`, em-dash grep, `scripts/artifact_wrap_lint.py`.

## Component 4: ship and score
- `/recoil-ship` (it now runs the render gate). Deploy only the `-v2` path; leave the incumbent live for the A/B.
- Draft the note (never send). Two links, one ask: "which one can you act on in two minutes?"
- File the ex-ante in {{SSOT}}: P(acceptance passes) with a number. On reply, `/recoil-close` scores it.

## Component 5: receipts (what a reviewer checks)
- `pre_prep` block present and PASS · `-v2` page PASS on R0 to R7 · gauntlet facet output · ex-ante number · commit hashes.
- Failure that counts as success: the gate stopped a page that would have shipped. Log it in the DEWY as a miss kept.

## Known traps for a cold session
- Live pages render from a JS object; the gate refuses script-rendered sources (R0). Score the rendered DOM or the `-v2` static render.
- Granola rate-limits under parallel readers. One reader, paced; never fan out transcript fetches.
- `public/` is world-readable; passcode gates are theater. Route gated content via /warroom/[slug].
- Do not infer ADR numbers. `python3 scripts/oracle.py next adr`.
