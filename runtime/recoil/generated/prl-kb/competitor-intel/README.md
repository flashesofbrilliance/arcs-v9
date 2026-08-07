# Competitor intel — cross-reference map + scrape findings
_2026-08-07 · Value-added enrichment for phases 1.2 / 1.3 (internal only; NOT for the Lyro KB)._

## DELIVERED: `cross-reference-map.csv` (the backbone)
335 rows flattened from PRL's own `competitive_cross_reference` (in `../prl-product-catalog-2025.json`):
`family, prl_grade, competitor, brand, competitor_grade`. Every PRL grade mapped to its named competitor
equivalents across **9 makers**: SABIC 140, Covestro 52, Trinseo 50, Asahi 34, Celanese 19, DSM 12, Ascend 12,
Ineos 11, BASF 5. Brands: Lexan/Cycolac/Cycoloy/Noryl/Geloy/Valox/Xenoy/Ultem (SABIC), Calibre/Magnum/
Emerge/Pulse (Trinseo), Makrolon/Bayblend/Makroblend (Covestro), Lustran/Luran (Ineos), Xyron (Asahi),
Celenex/Zytel (Celanese), Ultradur (BASF), Vydyne (Ascend), Akulon (DSM).

**This is immediately useful:** a rep who hears "we currently run Lexan 141" can look up → PRL **PC-GP2-D**. It
is a queryable, structured version of PRL's own positioning. No external data needed.

## BLOCKED: automated pull of competitor SPEC VALUES
Getting each competitor grade's actual property table (to put real numbers side-by-side) is **not scrapable**:
- **ulprospector.com** (the current host) is behind **Cloudflare bot protection** — curl returns HTTP 403, and
  an automated browser is held at "Performing security verification." Confirmed 2026-08-07 on the Lexan-141
  datasheet page.
- **catalog.ides.com** (the older host) *does* serve a direct `Datasheet.aspx?I=<company>&E=<sheet>` (that is
  how PRL's own I=73811 sheets were pulled), BUT mapping a competitor **grade name → E= id** needs the site
  search, which is JS/session-gated. Bare company listings are truncated (SABIC I=34794 returns only 12).
- Full spec tables on ulprospector also appear to require a **free Prospector account** (login-gated) even
  past the bot wall.

## Realistic options for competitor spec values (pick per need)
1. **Map-only (done)** — strongest value/effort ratio; pair with PRL's own specs (28 IDES sheets + 150-grade
   catalog) for a PRL-side spec column, competitor = equivalent grade name.
2. **Ask Todd** — PRL *built* this cross-reference, so the comparison spec basis likely already exists in their
   internal files. Cheapest path to real competitor numbers.
3. **Licensed UL Prospector / IDES account** — the legitimate, ToS-clean way to pull competitor specs at scale
   (it is a paid data service). A human with a login, or a data license/API.
4. **Selective manual** — for a short priority list, a person opens the ulprospector page interactively (passes
   the challenge) and copies specs. Not automatable, fine for a handful.

## Recommendation
Ship the map now as 1.2/1.3 enrichment. For real competitor numbers, source from PRL internally (option 2) or a
licensed account (option 3) rather than scraping — scraping is both blocked and ToS-risky. Do NOT put any of
this in the customer-facing Lyro KB (competitor specs are not ours to state; same anti-fabrication rule).
