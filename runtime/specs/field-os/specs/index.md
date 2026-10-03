# ARCS Field OS — Product Spec Index

> **Version:** v0.1.0
> **Date:** 2026-05-26
> **Status:** SCAFFOLD — stubs only; each linked spec is the next authoring target

---

## Governing frame

All specs in this directory derive from the canonical JTBD ordering defined in [`jtbd/jtbd-master-map.md`](../jtbd/jtbd-master-map.md):

```
Calibrate (D) → Orient (A) → Chart Course (C) → Detect (B)
```

Each surface gets a PRD. Each PRD cross-links to the `arcs-v9` sprint issue that implements the underlying engine.

---

## Spec registry

| Surface | Verb | Spec file | Linked arcs-v9 issues | Status |
|---|---|---|---|---|
| Calibrate | D | `specs/calibrate-prd.md` | ATG backlog (no issue yet) | 🔴 Not started |
| Orient | A | `specs/orient-prd.md` | [#2](https://github.com/flashesofbrilliance/arcs-v9/issues/2) [#3](https://github.com/flashesofbrilliance/arcs-v9/issues/3) [#4](https://github.com/flashesofbrilliance/arcs-v9/issues/4) | 🔴 Not started |
| Chart Course | C | `specs/chart-course-prd.md` | Scan suite (shipped) | 🔴 Not started |
| Detect | B | `specs/detect-prd.md` | [#5](https://github.com/flashesofbrilliance/arcs-v9/issues/5) + Observatory backlog | 🔴 Not started |
| Design system | — | `specs/design-system.md` | All surfaces | 🔴 Not started |
| HOLD/REJECT gate | — | `specs/hold-reject-gate.md` | Validation layer (all surfaces) | 🔴 Not started |

---

## Authoring priority

Write PRDs in this order (mirrors JTBD sequence + dependency chain):

1. `specs/orient-prd.md` — primary shipped surface; unblocks arcs-v9 Issues #2–#4
2. `specs/chart-course-prd.md` — scan suite is shipped; needs product framing
3. `specs/hold-reject-gate.md` — validation layer applies to all surfaces
4. `specs/calibrate-prd.md` — ATG feature gate; write before building ATG
5. `specs/design-system.md` — design language + token map across all surfaces
6. `specs/detect-prd.md` — Observatory; write when receipt body is large enough

---

## Changelog

| Version | Date | Change |
|---|---|---|
| v0.1.0 | 2026-05-26 | Initial scaffold — spec registry created from Perplexity ARCS session |
