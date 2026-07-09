---
name: ARCS × GIGI Substrate
description: GIGI is the local-first fiber-bundle substrate for ARCS; P1–P4 complete; arcs-v9 seam not yet wired
type: project
originSessionId: 70b644f9-1698-4cbd-8b92-51aa13374dca
---

**Last verified:** 2026-05-18 (P1–P4 complete). No new work since then.

## What GIGI is

`github.com/flashesofbrilliance/gigi` — Rust-native local-first fiber-bundle database. Holds Decision Receipts, ARCS macro templates, gap logs, and structural priors locally. LLMs act as stateless compute only.

**Naming rule (hard):** ARCS owns semantics; GIGI is persistence + retrieval. Say "ARCS corpus, persisted via GIGI" — never "GIGI's templates."

## Status

| Phase | Status |
|---|---|
| P1 (repo gardening + CI) | ✅ COMPLETE 2026-05-18 |
| P2 (GIGI schema + BAR seed templates) | ✅ COMPLETE 2026-05-18 |
| P3 (seam swap) | ✅ COMPLETE 2026-05-18 — Python layer wired |
| P4 (CI gates) | ✅ COMPLETE 2026-05-18 |
| arcs-v9 seam (`compass/route.ts`) | 🔴 NOT YET WIRED |

## Key files

- `arcs_substrate.py` — GIGI seam for arcs-v9
- `arcs_init_bundles.py`, `arcs_seed_bar.py` — BAR seed templates
- Local clone: `/Users/zharris/Repositories/forks/gigi`

## Blocking gate for arcs-v9 seam

GIGI wiring in `compass/route.ts` is P3 on the product roadmap. Not blocking any current sprint. Resume when arcs-v9 has real users (post-ADR-016 auth wiring).
