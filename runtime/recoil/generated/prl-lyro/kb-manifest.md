# PRL Lyro knowledge-base manifest (guardrail ledger, SSOT)
_2026-08-07 · The dated record of what goes into Lyro's knowledge and what is deliberately kept out, with the
reason. "The guardrail is what's ABSENT": Lyro answers only from what's loaded, so keeping specs/certs/prices
out is what makes never-fabricate structural. Update this file whenever a source is added or removed._

## LOAD (in Lyro's knowledge)
| Source | Form | Why safe |
|---|---|---|
| `kb-content/kb-content.md` | paste as text / Q&A | Curated, scrubbed application prose. No grade codes, UL codes, numbers, prices. THE primary KB. |
| `conversation-starters.md` openers | widget starters | Market-level, route to specialist. |
| PRL site market/capability pages | URL scrape (≤60 pp) | Only the market/application pages. **Must be spot-checked** — the site also hosts the datasheet PDFs (below); do not let the crawl ingest those. |

## HELD OUT (never load — routes to a human by construction)
| Source | Why held out |
|---|---|
| `prl-product-catalog-2025.json` / `.jsonl` (150 grades) | Per-grade property values → fabrication path. |
| 11 `PRL-<grade>-*.pdf` tech-sheets in `site-datasheets/` | Per-grade spec tables + grade codes. |
| `UL-Jun16.pdf` (UL 94/746 explainer) | Blends with a grade name → fabricated cert claim (gauntlet's most dangerous path). |
| `prl-good-better-best-matrix.pdf`, `PRL-Material-Selection-*.pdf` | Comparative spec tiers = numbers. |
| `PRL-Competitor-Cross-Reference.pdf` | Competitor recognition is **1.3**, not 1.5. |
| UL / NPE press releases | Contain file/listing specifics. |
| Prices, lead times | Not the bot's to state; commercial + volatile. |

## SELL-SHEET SCRUB CHECKLIST (why the sheets are NOT loaded whole)
The 7 market sell sheets are marketing, but a grep confirmed they carry grade codes (ABS-GP1, PC-GP1/2/3,
PPX-FR3), UL rating tokens (UL94, UL746C, F1, 5VA, RTI), and org marks (NEMA, CSA). Loading them whole would
smuggle a spec/cert past the wall. So they are **extract-and-scrubbed into `kb-content/kb-content.md`**, not
uploaded. Before any sell-sheet-derived text is staged, confirm ALL of the following are absent:
- [ ] No PRL grade codes (anything like `PC-GP1`, `PPX-FR3`, `ABS-GP1`, `NY6-...`).
- [ ] No UL/cert codes or ratings (`UL94`, `UL746C`, `V-0/V-1/V-2`, `5VA/5VB`, `RTI`, `F1/F2`, file numbers).
- [ ] No org-specific approval marks tied to a grade (`NEMA`, `CSA` as a per-grade claim).
- [ ] No numeric property values (HDT, tensile, modulus, MFR, specific gravity, temperatures, %).
- [ ] No prices, no lead times, no minimum-order numbers.
- [ ] General capability claims ("has UL-listed grades for electrical use") are OK **only** when they route to
      a specialist for the specific grade/listing — never asserting a specific grade's status.

## POST-LOAD GATE
After loading, run every prompt in `firewall-test-prompts.md` in the Tidio playground. Any value that leaks →
trace it to a source here, remove/scrub, re-test. Only a clean sweep clears the anti-fabrication gate.

## Note on the general "70+ UL-listed grades" style claim
Company-level counts are marketing, not a per-grade cert, so they are lower-risk — but they were still left out
of `kb-content.md` to keep the wall bright-line simple. If Todd wants that credibility line in, add it as a
reviewed exception here first.
