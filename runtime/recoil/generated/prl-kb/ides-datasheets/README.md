# IDES datasheets — RAW GATHER (hold for 1.3 review)
_Gathered 2026-08-07 · source: catalog.ides.com company id **I=73811** (Polymer Resources). Token-efficient
curl + grep enum, no LLM parsing. **Gathered now to avoid a second crawl later; NOT yet reviewed.**_

## What this is
- `raw/E<id>.html` (+ `.txt` sidecar) — 28 per-grade technical datasheet pages, raw HTML + extracted text.
- `_company-listing-I73811.html` — the IDES company listing (one enumeration source).
- `index.tsv` — E_id → grade code, for all 28 grades.

## The 28 grades (all families covered)
ABS-FR, ABS-FR-AMB, ABS-FR-UV-(f2), ABS-G5, ABS-G5-(color)-3, ABS-G10, ABS-G15, ABS-G20, ABS-G25, ABS-G30,
ABS-GP1, ABS-GP1-(color)-EP, ABS-GP1-(color)-UV, ABS-GP-HH, ABS-GP-IM, ABS/PBT GP1-M, ABS/PC-GP1, ASA-GP1,
NY6-G13, NY66-EX1, NY66-G13, PC/ABS GP1, PC/ASA FR1, PC/TP-FR2, PEI-G10, PPX-EN-FR3, TP-FR2 (+1 unparsed grade
name, content intact).

## Completeness (checked 2026-08-07)
Two-source sweep: (1) the bare company listing `xquery.aspx?I=73811` returned 20 grades, ABS-heavy; (2)
crawling every `prlresins.com/products/*` page for its embedded IDES link added 8 more family representatives
(PC, nylon-6, PBT-blend, PC/ABS, PC/ASA, PC/TP, PEI, PPX, TP). Union = **28**, now covering every family PRL
makes. The full per-family IDES search (`xquery.aspx?I=73811&QM=82152:<N>`) is **JS/session-gated** — curl only
gets a 2KB shell, so a handful of extra per-family variants may exist behind it (browser-render needed to
enumerate). **The authoritative complete grade universe is Todd's 150-grade internal catalog**
(`../prl-product-catalog-2025.json`), already in the repo; these 28 IDES sheets are the public-datasheet
supplement (test values as published on IDES), not the source of truth for which grades exist.

## IMPORTANT — do NOT load into the Lyro KB
These pages contain per-grade **property values and UL/cert data**. Per the anti-fabrication design
(`../../prl-lyro/kb-manifest.md`), specs/certs are **held out** of the Lyro knowledge base — Lyro must route
those to a human, never quote them. This material is for:
- **1.3 (smarter recognition)** — teaching the bot to *recognize* which grade a lead means (not to state specs).
- **Human reference** — the sales team / specialist answers.

## Status: HELD FOR REVIEW
Raw only. No parsing into a unified spec table yet (that is 1.3 work, deliberately deferred). When 1.3 kicks
off: parse `raw/` → structured table, reconcile against `../prl-product-catalog-2025.json`, and use for
recognition only.
