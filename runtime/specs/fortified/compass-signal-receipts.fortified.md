# Question Compass, Signal and Receipts (fortified)

## 1. Front matter

```
spec_id:        arcs-question-compass-signal-receipts
version:        2.0.0-fortified
original:       /Users/zharris/Downloads/ARCS_Question_Compass_Signal_Receipts_Spec.md
                (byte-identical copy: runtime/specs/ARCS_Question_Compass_Signal_Receipts_Spec.md)
original_sha256_prefix: 979ee0e2547909c6
original_file_date:     2026-04-21
fortified:      2026-11-12 by Claude Opus 5.5
from_ledger:    runtime/specs/fortified/ledgers/compass.json (28 claims, 36 facets)
stance:         the live build is the source of truth; the original is a facet checklist
status:         DRAFT for Zach's review
```

## 2. Cold read

- **Why this spec exists:** it was the April handoff that defined the compass as the front door: one question in, one next move out, with a receipt.
- **What it is now:** a checklist. The build at `src/app/dashboard`, `src/app/api/compass/route.ts`, `src/lib/ygate.ts` and `src/app/receipt` has moved past it and is the contract.
- **Why now:** the pressure test found 13 of 28 claims false against today's repo, mostly names and endpoints that were never built, and three facets the build dropped that its own primitives still need.
- **How to use it:** before building, read section 7 and pick from it. During, take names and enums from the code cited in section 4, never from the original. After, re-run the greps in section 7 to confirm the gap closed.
- **How to read this page:** sections 4 and 5 tell you what to trust; section 6 is unproven; section 7 is the work; section 8 is how the original misled.

## 3. Verdict

Nobody should build from the original's contracts today. Its endpoints (`/api/question-compass`, `/deepen`, `/api/receipts` list), its `CompassResponse` shape, its `QUICK_MOVE` spelling and its status enum do not exist, and following them would fork the contract. Its product principles (simple by default, depth on demand, receipts over rhetoric, agency preservation) still hold, and the build honours all but the last. The useful part is a short list of facets the build overlooked: a declared override path, a drift prompt the user can actually see, Cmd/Ctrl+Enter submit, and real control semantics on the horizon and stakes inputs. Build from the code and from section 7.

## 4. What holds

Verified against the repo on 2026-11-12. Line numbers are today's.

**Principles that survive (original lines 75 to 79).** Simple by default, depth on demand, trust through transparency, receipts over rhetoric, agency preservation. The build follows the first four. The fifth is half built (section 7, item 1).

**Facets present as specified.**

| Facet | Evidence |
|---|---|
| Free-text question intake, `?q=` prefill | `src/organisms/CompassForm.tsx:70-73` |
| Horizon: four values | `src/molecules/HorizonStakesRow.tsx` (Picker); values match original line 243 |
| Stakes: LOW / MEDIUM / HIGH | `src/molecules/HorizonStakesRow.tsx` (SegmentedSlider) |
| Visible submit, disabled when empty | `CompassForm.tsx:80` `disabled={running \|\| !question.trim()}` |
| Loading state announced | PipelineTakeover `role=status aria-live=polite` (ledger: `CompassForm.tsx:95`) |
| Three modes, auto-selected | `selectMode` at `src/app/api/compass/route.ts:36-41`; enum `QUICKMOVE \| PLAN \| COURT` at `prisma/schema.prisma:122` |
| Receipt on every signed-in run | `prisma.receipt.create` at `route.ts:539`; anonymous runs ephemeral by trust contract |
| Outcome capture and debrief | `model Outcome` at `schema.prisma:443`; `src/app/api/receipts/[receiptId]/outcome/route.ts`; `src/app/debrief/[receiptId]` |
| History and reopen by id | `src/app/history`, `/api/history`, `src/app/receipt/[receiptId]/page.tsx` |
| Error with retry | ledger: `CompassError(message,onRetry)` in dashboard; `src/lib/compass-response.ts` |
| `clarityMode` defaults to SIMPLE | ledger C13: `route.ts` default and `schema.prisma` |

**Wins over the original (BETTER-IN-BUILD).** These are the build's choices, and each one beats what the spec asked for.

1. **Reversibility is inferred, not asked.** `doorClass()` at `route.ts:52-56` sets ONE_WAY or TWO_WAY from horizon and stakes. One fewer field on the front door, which is the original's own "simple by default".
2. **Example tiles instead of placeholder rotation.** Tappable examples while the question is empty (ledger: `CompassForm.tsx:98-107`). They teach and survive focus; a rotating placeholder vanishes on focus.
3. **A richer answer.** True North, why bullets, exactly three tributaries, Loki, BAR, NCI, Y state and path cards, rendered at earned fidelity by Y state. The original's move / why / signal / mode / receipt is a subset.
4. **Signal as Y-gate conditions, not three-level weights.** `ygate.ts` emits conditions with severity, and NCI is scored per lens (`nciByLens`). The original's `weightedFactors` would have been coarser.
5. **Status plus calibration.** `OPEN | LOGGED | EXPIRED` (`schema.prisma:202`) plus `Outcome.matched` and `regretScore`. That gives a calibration signal; the original's four states did not.
6. **Refine through lineage.** Tributary follow-ups re-run with `?parent=&tributary=` and keep the session thread (`route.ts:261` sets `sessionVersion` from the parent). Better than edit-in-place, because the earlier receipt stays.
7. **Depth escalates on its own.** Mode picks the model and depth; Court, Brief and Guide are a click away. No separate deepen endpoint is needed, which is the original's line 76 principle.
8. **Transport-failure recovery.** The dashboard polls `/api/history` for a receipt written after a client fetch failed (ledger: proven in prod 2026-09-24). The original has no recovery story at all.

**Dropped on purpose, and right to stay dropped.**

- Inline answer on the dashboard. The dashboard routes to `/receipt/<id>` (`src/app/dashboard/page.tsx:223`; comment at line 162). Commit `730e332d` removed the preview carousel on Zach's call.
- Zoetrope nav. The original itself put it outside MVP; no Zoetrope surface exists in `src/app`.

## 5. Corrected

| Original (line) | Correction | Evidence |
|---|---|---|
| "lacks ... first-class receipt layer" (11) | A full receipt layer exists: DEWY fields, Y gate, lineage, outcomes. | `model Receipt` at `schema.prisma:75`; `route.ts:539` |
| "does not receive a visible, structured answer on the same surface" (39) | The answer is visible and structured on `/receipt/<id>`, one navigation away, by decision. | `dashboard/page.tsx:223`; commit `730e332d` |
| "keyboard shortcut-only behavior breaks the primary action path" (43) | There is no shortcut at all; a full-width button submits. | `CompassForm.tsx:80`; no `metaKey`/`ctrlKey` in `CompassForm.tsx` |
| "feel?: clear\|murky\|stuck\|torn ; reversibility?" (241) | Intake is horizon and stakes only. Reversibility is inferred; feel is not collected. | `HorizonStakesRow.tsx`; `route.ts:52-56` |
| "mode: QUICK_MOVE \| PLAN \| COURT" (256) | `QUICKMOVE`, no underscore, here and in the `decision_receipt` CHECK. | `schema.prisma:122`; `route.ts:36` |
| "weightedFactors, guardrailStatus, ... relatedReceipts" (260) | The contract is the SYSTEM prompt JSON in `route.ts`. None of these keys exist. `compass-response.ts` is an 18-line failure helper. | `wc -l src/lib/compass-response.ts`; grep finds no such keys in `src` |
| "status: OPEN \| ACTED \| REVIEWED \| SUPERSEDED" (288) | `OPEN \| LOGGED \| EXPIRED`, plus an Outcome row. | `schema.prisma:202` |
| "POST /api/question-compass" (299) | `POST /api/compass`. | `ls src/app/api/question-compass` fails |
| "/api/receipts GET list, /api/receipts/:id GET" (351) | `src/app/api/receipts` holds only `[receiptId]`, `ripe`, `save`, `studio`. List is `/api/history`. | `ls src/app/api/receipts` |
| "/api/question-compass/deepen POST" (354) | No deepen route. Depth comes from mode, tributaries, Brief and Guide. | `ls src/app/api` |
| "COURT: high stakes, low reversibility" (379) | HIGH stakes is COURT; THIS_QUARTER or longer is COURT at any stakes; TODAY with LOW is QUICKMOVE; else PLAN. | `route.ts:36-41` |
| "ARCS local-hosted brief" (6) | arcs-v9 is Vercel-hosted. | AGENTS.md Intent block |
| "/apps/arcs-web/src/pages" (638) | No `/apps`. Next.js App Router under `src/app`; orchestration is inline in `route.ts`. | repo tree |

**Internally contradicted.** Line 138 adds DriftSentinelNotice as a new component, yet the phase plan defers it. Line 59 names three surfaces, yet the nav lists four including Zoetrope, which line 96 puts out of scope.

**Where I differ from the ledger.** The `yOverride` columns sit at `schema.prisma:167-169`, not 171-173. They are not only defaulted: `src/app/api/geometry/route.ts:86` and `:207` read `yOverride`. The ledger also marks the drift facet PRESENT. I would mark it half present: `ygate.ts:134-137` adds the "land the plane" condition, but no `.tsx` file renders `yConditions` (grep), and `src/app/api/geometry/route.ts:185` only counts them. The user never sees the prompt.

## 6. Hypotheses, not facts

| Claim | What would verify or kill it |
|---|---|
| "S-tier" design spec (3) | Self-grade with no rubric. Stripped. |
| One trustworthy move "in under two minutes" (27) | Unmeasured. Log submit-to-receipt-render per run; the ledger notes a COURT model median near 17s, which excludes typing and reading. |
| Loading visible "within 100ms of submit" (522) | Not measured. A Playwright trace on `/dashboard` would settle it. |
| An explicit finite state machine improves the form (388) | The build uses plain booleans and works. Keep as hypothesis until a state bug appears that booleans caused. |
| A "feel" qualifier sharpens conviction (241) | Untested. Prep already asks how certain you are. Kill it if Y-gate conviction does not differ between runs with and without prep. |
| ReceiptLinker, topical related receipts (371) | Worth it only with volume. Count receipts per signed-in user first. |
| About 150 `[cite:N]` tags | No bibliography in the file. Not traceable; treated as no source. |

## 7. Gaps and open questions

This is the main section. Each item is a facet the build overlooked that still earns a place, with the check that proves it closed.

**1. Declared override has a column and no door.** `Receipt.yOverride`, `yOverrideAt` and `yOverrideNote` exist (`schema.prisma:167-169`) and geometry reads them (`src/app/api/geometry/route.ts:86,207`). Nothing writes them: grep for `yOverride` in `src` shows only the geometry read and a comment at `ygate.ts:51`. The original's agency principle (line 79) and the ROM Write-Lock primitive both need a person to say "I see the RED or FORK and I proceed anyway", with a note and a timestamp. Today that cannot happen, and geometry counts a value that is always false.
- Smallest door: a POST on `src/app/api/receipts/[receiptId]/` that sets all three fields for the owner, and one button with a required note on the receipt page when Y is RED or FORK.
- Done when: grep shows a write path, and a test receipt has `yOverride=true` with a non-empty note.
- Decision for Zach: wire the door, or drop the columns. Leaving them half built is the worst option, because geometry presents a field that can never be true.

**2. The drift prompt is computed and never shown.** `ygate.ts:134-137` adds "Session v5+, land the plane or keep exploring?" and `ygate.ts:190-195` sets `driftState=DRIFTING`. No page renders `yConditions`. The only drift text a user can meet is `DRIFT <state>` inside TribunePanel (`TribunePanel.tsx:127`), from a separate tribune row. WORLD.md names this prompt as the defence against "entropy masquerading as motion". `LANDED` is only set by an outcome (`outcome/route.ts:122`), so a user cannot land a session at the moment they choose to.
- Smallest door: on `/receipt/<id>`, when `driftState=DRIFTING`, show the line with two actions: land (log the decision now) or keep exploring (follow a tributary).
- Done when: a v5 session receipt shows the prompt at 375 and 1280 widths.

**3. Cmd/Ctrl+Enter submit.** Still missing (grep: no `metaKey` or `ctrlKey` in `CompassForm.tsx` or `ui/Field.tsx`; the only Cmd+Enter in the app is `ReflectLayer.tsx:1049` for annotations). One keydown handler on the textarea; plain Enter keeps inserting a newline.
- Done when: Cmd+Enter in the question box submits on desktop and the button path is unchanged.

**4. Control semantics on Picker and SegmentedSlider.** Both use native `<button>` elements (`src/ui/Picker.tsx:36,50`, `src/ui/SegmentedSlider.tsx:52`), so they are reachable by keyboard. Neither has any `aria-` or `role` attribute (grep). A screen reader hears unlabelled buttons with no selected state. Picker needs `aria-expanded` and a listbox or radio pattern; SegmentedSlider needs `role=radiogroup` and `aria-checked` on each segment.
- Done when: `scripts/page_gate.py --matrix full` on `/dashboard` passes axe with no control-name or state findings. Not run in this pass.

**5. Inputs stay editable while a run is in flight.** Only the button disables (`CompassForm.tsx:80`). The run reads state at submit, so edits mid-run are silently ignored and mislead. Low cost to disable or visibly lock the fields. Lower priority than 1 to 4.

**6. Nothing measures the job the spec names.** "Under two minutes" is the stated job, and no event measures it. One event pair (submit, receipt rendered) would turn section 6's first row into a fact.

**Open decisions only Zach can make.**
- Override (item 1): wire the door or drop the columns.
- Drift (item 2): is landing a session a receipt event of its own, or only a nudge toward the debrief?
- Feel qualifier: test it, or close it since prep covers certainty?
- Should the original's file at `runtime/specs/` carry a pointer to this page, so the next reader does not build from its endpoints? This doc does not edit it.

## 8. Kintsugi seam

1. **It described a build that was never made.** The endpoints, the response type, the folder layout and the enums read as a contract, but none matched the code even near the time of writing. A builder following them would have forked the API. The seam: names come from code, never from a spec.
2. **Its central complaint went stale and stayed in the file.** "No receipt layer, no answer surface" was the premise for most of the plan. Receipts, outcomes, history, lineage and recovery all shipped, and the inline answer was removed on purpose. The real gaps were smaller and different: an override nobody can declare, and a drift prompt nobody can see.
3. **It looked sourced and was not.** About 150 `[cite:N]` tags with no bibliography gave every line the look of evidence. None can be traced. Two self-grades ("S-tier", "under two minutes") rode along as facts.

Grounds: ledger runtime/specs/fortified/ledgers/compass.json (claims marked FALSE, facets array); the endpoint and enum mismatches against src/app/api/compass/route.ts and src/lib/compass-response.ts; the inline answer surface removed on purpose in commit 730e332d; the untraceable `[cite:N]` tags in runtime/specs/ARCS_Question_Compass_Signal_Receipts_Spec.md (no bibliography in the file).
