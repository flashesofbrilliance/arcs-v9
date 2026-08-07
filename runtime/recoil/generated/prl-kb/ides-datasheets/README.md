# IDES datasheets — RAW GATHER (hold for 1.3 review)
_Gathered 2026-08-07 · source: catalog.ides.com company id **I=73811** (Polymer Resources). Token-efficient
curl + grep enum, no LLM parsing. **Gathered now to avoid a second crawl later; NOT yet reviewed.**_

## What this is
- `raw/E<id>.html` — 20 per-grade technical datasheet pages, raw HTML, one per PRL grade listed on IDES.
- `_company-listing-I73811.html` — the IDES company listing (the full enumeration source).
- `index.tsv` — E_id → grade code → material, for the 20 grades (see below).

## The 20 grades (mostly ABS, plus NY66 + ASA)
ABS-FR, ABS-FR-AMB, ABS-FR-UV-(f2), ABS-G5, ABS-G10, ABS-G15, ABS-G20, ABS-G25, ABS-G30, ABS-GP1,
ABS-GP1-(color)-EP, ABS-GP1-(color)-UV, ABS-GP-HH, ABS-GP-IM, ABS-G5-(color)-3, ABS/PBT GP1-M, ABS/PC-GP1,
ASA-GP1, NY66-EX1, NY66-G13. (This is PRL's **public IDES listing** — a subset of the 150-grade internal
catalog in `../prl-product-catalog-2025.json`, not the whole thing.)

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
