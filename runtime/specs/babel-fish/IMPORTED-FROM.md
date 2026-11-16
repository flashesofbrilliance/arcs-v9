# Imported from flashesofbrilliance/arcs-decision-receipts

- **Source:** `flashesofbrilliance/arcs-decision-receipts`
  `field-receipts/instances/_MASTER/adaptive-translation-codex.md` at `148c097` (2026-05-29), copied
  byte for byte.
- **Imported:** 2026-11-16, when Zach chose to build Babel Fish (the lossless translation transceiver)
  as a private artifact and to keep its live codex in arcs-v9. The source repo is archived (the
  Deloitte arc closed), so this copy is the one to maintain.
- **History:** the source repo keeps the commit history; it is archived, not deleted.

## Files here

| File | What it is |
|---|---|
| `adaptive-translation-codex.md` | The Adaptive Translation Codex: register-neutral source concept, six synthetic personas, four translation invariants, drift flags, phase-lock signals. |
| `babel-fish-artifact.html` | Source of the private claude.ai artifact (https://claude.ai/artifact/QQFyyZa3xeUhfuhyMtjKz9): decomposition, recomposition, then a blind transceiver that marks each load-bearing claim kept, weakened or dropped. Republish from this file. |

## Relation to the operators

- `operators/arcs_lte.py` (Lossless Translation Engine) defines the same stages (Intake/Decomp,
  Lossless Codex, Recomp, Transceiver). The artifact adapts its decomposition prompt and its
  IPS >= 0.95 bar, with two deliberate differences: IPS is scored by a blind receiver instead of
  keyword overlap, and there is no recovery pass that pastes dropped claims back on to pass.
- The LTE's archetype registry (QUANT, CONNECTOR, ARCHITECT, INSTITUTIONALIST) does not match the
  codex's six personas. The artifact uses the codex six; reconciling the two is part of backlog row
  `spec-babelfish-reconcile`.
