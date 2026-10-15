# Perplexity-to-arcs-v9 port: what is here, what is not, keep or kill (PROPOSAL)

Date: 2026-10-15. Status: scouting only. Nothing moved, deleted or ruled. Zach rules; every verdict below is a recommendation.

## What this is built from
- `runtime/specs/arcs-v9-consolidated-design-v1.md` (the v8.5-to-v9 refactor list, cites Perplexity Space files as `[file:N]`).
- `runtime/specs/arcs-v9-engineering-spec-v1.md` (822 lines, a FastAPI / Pydantic / SQLAlchemy design).
- `runtime/specs/ARCS-v9-ROM.md` (84 lines, same citation style).
- A keyword grep of `src/ operators/ scripts/ prisma/` for each named item. **A hit is a signal, not proof of implementation, and a zero is a signal, not proof of absence** (the feature may live under another name). The verification pass below is what turns signals into verdicts.

## Rule for the verdict pass (fixed before the pass runs)
- **KEEP:** a running implementation exists, or a gate or ADR depends on it.
- **PORT:** specified, no implementation, and the job it serves is still live (it can name a trigger for a backlog row).
- **COMPOST:** superseded by a later ADR or by the shipped stack, or contradicted by a canon ruling. History is relocated, never deleted; each compost row names its supersessor.
- **UNKNOWN:** cannot be decided from the tree. Goes to Zach, not guessed.

## A. ROM surface and proposed additions (consolidated design sections 2 and 3)
| Item | Grep signal | Reading | Recommended next |
|---|---|---|---|
| Write-Lock / commitment ordering | 24 files; ROM primitive 7 in CLAUDE.md; ADR-085 | PRESENT | KEEP |
| Decision Receipts | `decision_receipt` table, AGENTS.md | PRESENT | KEEP |
| Kintsugi immune system | `operators/arcs_kintsugi.py` | PRESENT | KEEP |
| 12-derivative kinematic manifold | `operators/arcs_kinematics.py`; memory ruling: two-zone, D5+ are operators not derivatives | PRESENT with a ruling | KEEP; the ruling already narrowed it |
| Source A-F grading, "no n<5 patterns" | literal "A-F" 0 files; `runtime/specs/source-trust.json` exists; "n>=5" 4 files | PRESENT under another name? | verify, then KEEP |
| Constitutional Court | `operators/arcs_constitutional_court.py`; registry marks Immune (18) PARTIAL, no standalone entrypoint | PARTIAL | PORT the entrypoint |
| Clarity Modes SIMPLE / RICH / DEEP + R1-R4 (True North identical across modes) | 15 and 11 files | LIKELY PRESENT | verify, KEEP |
| Drift Sentinel states ONTRACK / USEFUL_TANGENT / DERAILMENT, Land-the-Plane | states in 4 files; "land the plane" in 1 | THIN | verify; PORT if only prose |
| Macros FATED, HCI_PCI, KKL, BAR, LAB, TAD | 57, 7, 14, many, many, 3 files | PRESENT as vocabulary | but three expansions collide (see effort-policy `canon_collisions_found`) |
| CUR and ALC | Curator has an operator file; Alchemist none | PARTIAL | ALC: PORT or COMPOST; Zach decides |
| Kairos vs over-intellectualizing reversibility rule | "over-intellectual" 0 files | SPEC-ONLY signal | the phrase may differ; verify, then PORT |
| Motion families (articulating / reticulating / circulating) | "reticulat" 2 files | THIN | likely vocabulary only; UNKNOWN |
| 6-state spine (READ ... LOSSLESS TRANSLATION) | PHASE-SYNC or LOSSLESS 7 files | PRESENT as vocabulary | UNKNOWN: is it enforced anywhere? |
| TV Guide channels, Top 7 for users | "TV Guide" 0 files | SPEC-ONLY | PORT or COMPOST; product call |
| Time Quality Attribution (Chronos/Kairos/Drift/Shavasana gates + stop-loss) | `runtime/specs/time-quality-attribution-rom.json` exists | SPEC present, evaluator unverified | verify; PORT the runtime evaluator if absent |
| Bias Hygiene (User0 preferences tagged CONFIG, never ROM) | grep too broad to mean anything (48 files) | UNKNOWN | needs a targeted check |
| "Every override logged with a seam marker" | "seam marker" 0 files | SPEC-ONLY | Kintsugi seams exist as practice; PORT as a field or COMPOST |

## B. The engineering spec (FastAPI) versus what shipped (Next.js 16 + Prisma)
The spec's backend is Python 3.12 + FastAPI + SQLAlchemy with services `context_classifier`, `mode_selector`, `macro_engine`, `court_guardrails`, `drift_sentinel`, `synthesis_engine`, `receipt_service`, `brief_service`, `guide_service`. Grep: the first, second, third, fourth and sixth names have 0 files; `drift_sentinel` has 1. The shipped app is a Next.js route handler (`src/app/api/compass/route.ts`) with Prisma. Reading: **the architecture was superseded, the concepts were not necessarily ported.** Recommendation: COMPOST the FastAPI scaffold (relocate, name the supersessor `src/app/api/compass/route.ts`), and run a concept-by-concept pass for the services above to decide which concepts still need a home. Also zero hits for the design principle "stable recommendation".

## C. Source files the design cites that I could not find in the tree by name
Found: `time-quality-attribution-rom.json`, `field-os-init.md` (under `runtime/memory-export/bootstrap/space/`), `ARCS-YellowPaper-v1-2.md`, `ARCS-Vector-Collision-Engine-v1.md`.
Not found by name: the long "based-on-my-tendency-to-speak" thread (the design says most unlisted specs are probably in it: v9.0 header, Porting Roadmap, 5-Book scaffold, Question Compass spec, ATG, Funhouse Optics), the Pilot's Manual positioning thread, the Cleo creative thread (Book III source), the v8.5 initialization / Diamond Protocol thread, the Deep Shavasana thread, the OS-state-primitives / TV Guide / v8.4 firmware thread, `ARCS-v8.3-Canon.md`, `ARCS-STierProtocol-DefaultStack.md`, and the Ripple-BVF equity thread. Some of these concepts are mentioned elsewhere in the tree (for example "Funhouse Optics" in 5 files), so content may have been absorbed under other names. **Names in the source are truncated, so a filename miss is weak evidence.**
**These live in the Perplexity Space. Only you can export them; I cannot read the Space.** That export is the single highest-value input for this reconciliation.

## Proposed next steps (none started)
1. You: export the Space files in C into one folder (any format).
2. One bounded verification pass over tables A and B with the `claims-skeptic` agent (proves or disproves each row against the live tree, read-only) before any verdict is final.
3. A reconciliation print `_STATE/<date>-perplexity-port-ledger.json` in the doc-reconciliation format, each row carrying class, evidence line and a recommended fate.
4. KEEP rows need no work. PORT rows become backlog rows with a trigger and a gate. COMPOST rows are relocated with a supersessor note.
5. Success measure (pre-registered, for the 10X conversation): share of ROM and design items with a verdict and evidence line, and the count of items found to be PORT that no backlog row names today.
