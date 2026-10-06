---
version: 0.1.0
date: 2026-10-05
status: PROPOSED (labels await Zach's ruling on the flagged collisions)
module: src/lib/vocabulary.ts
---

# Ahmed-order vocabulary map

One vocabulary for three surfaces: the receipt page (`src/app/receipt/[receiptId]`), the brief page
(`src/app/brief/[receiptId]` + `src/organisms/Brief.tsx`) and the `decision_receipt` ledger
(AGENTS.md "Receipts or it didn't happen"). Order: VERDICT, 3 REASONS, 3 QUESTIONS with answers,
TASKS, EVIDENCE behind the fold. Labels live only in `src/lib/vocabulary.ts`.

Data basis (prod `Receipt`, read-only, 2026-10-05): 267 rows. Y states present: FORK 137, PARADOX 116,
SCRATCH 7, YELLOW 5, DELTA 2. **No GREEN, RED or LOCKED receipt exists**, so no real receipt earns a
SHARP verdict today. 266/267 carry exactly 3 `whyBullets`; 70 carry `atgTributaries`; 266 carry
`paths`; 0 carry `loki`; 176 have a Brief; 3 have a PrepGuide.

## The map

| # | Slot | Label | Page fields | Ledger columns | Glossary | Today on receipt page | Today on brief page | Mismatch |
|---|---|---|---|---|---|---|---|---|
| 0 | Subject | Decision | `decision` / `sharpQuestion` | `question` | none | "Decision" (top) | "Decision" (h1) | Ledger calls it `question`; pages call it Decision. Kept as the subject line, not a slot. |
| 1 | Verdict | Verdict | `trueNorth` + `yState`/`renderResolution`, `mode`, `doorClass`, `stakes` | `question`, `mode`, `stakes` | none ("Decision" is a candidate term only) | "True North" | "True North" | **C1** label: True North vs Verdict. Mode/door/stakes sit in a pill row at the bottom of the receipt and a sidebar on the brief. |
| 2 | Reasons | Reasons | `whyBullets` (schema `why`) | `what_confirmed[]` | none | "Why This" | **not rendered** | Brief drops the reasons entirely. Compass prompt asks for 1 to 3; prod has 3 in 266/267. |
| 3 | Questions | Open questions | `atgTributaries` (meta / challenge / adjacent prompts); brief `situationFraming` ends with one deciding question | `what_unconfirmed[]` | none | not rendered (TribunePanel is a different thing) | at the bottom ("Tributary rounds", ExpandableTributaries) | **No answers exist anywhere.** Tributaries are prompts; only 70/267 rows have them. Writer gap, chip filed. |
| 4 | Tasks | Next moves | `paths` [{title,detail,tag,status}] + `horizon` | `horizon` | none | TerrainPaths, after Fated | TerrainPaths, mid-page | Ledger has no task column; `horizon` is the only shared field. PrepGuide stages are the richer task source but n=3. |
| 5 | Evidence (fold) | Evidence | `fated`, `court`/`courtVerdict`, `nciScore`, `coherencePct`, `macroTags`, `version`, lineage, `createdAt` | `refs[]`, `event_at`, `operator`, `source_repo` | "Dewy Receipt" (captures time, context, confidence) | inline, open | NCI hero number + Court open | Both pages show NCI above the reasons; it belongs behind the fold. |

## Collisions for Zach (escalated, not resolved; `_CANON` untouched)

- **C1 · True North vs Verdict.** WORLD.md and the compass call the output "True North"; the Ahmed order
  calls it Verdict. The module ships `Verdict`. Option: keep "True North" as the label and "Verdict" as
  the slot name. Your call.
- **C2 · "Dewy Receipt" means two things.** Glossary v0.1 defines it as a *meta* receipt for the use of
  ARCS itself; the code's DEWY receipt is the product decision record and the ledger row is a ship event.
  Three objects, one name.
- **C3 · "Decision".** Glossary v0.1 lists Decision as a next candidate term (undefined). Pages use it for
  the subject line; the ledger uses `question`.
- **C4 · Questions need answers.** The Ahmed order wants 3 questions *with answers*. No field holds an
  answer. Fidelity rule applies: render the questions as open, never invent the answer.
- **C5 · `mode` on the ledger** (QUICKMOVE/PLAN/COURT) is the same enum as the receipt, good; but ledger
  `horizon` (`today`/`this-week`/...) and receipt `horizon` (TODAY/WEEK/QUARTER/...) spell it differently.
  Display maps both to one label; no schema change.

## Fidelity rule (WORLD.md)

The order is structure, not resolution. FORK/YELLOW render the verdict DEGRADED, PARADOX MOIRE,
SCRATCH/DELTA GRAIN. A verdict slot with fog says so in its own register; it is never sharpened to fit
the order.
