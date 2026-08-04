# Phase 1.3 — Smarter lead recognition
_Todd-safe · LATER · 2026-08-04._

## Where this sits
**LATER.** Its data-gathering is mostly inside your own CRM, so we can prepare it in parallel with
earlier phases at no extra cost.

## Scope / what "done" looks like
The bot recognizes the resins and competitor grades you actually sell, so it knows a real buying signal
when it sees one and routes it right. It never guesses a spec, a certification, or a price. Correctness
is proven with a test set before it ever goes live.

## Best / Base / Worst
| | Effort | Time | What drives it |
|---|---|---|---|
| **Best** | ~10 hrs | ~few days | Recognition data pulls cleanly from your CRM (product catalog + tagged deals). |
| **Base** | ~18 hrs | ~1 wk | Normal build + the test set + a short session with your SM for the unwritten know-how. |
| **Worst** | ~28 hrs | ~1.5 wks | The competitor cross-reference needs manual clean-up, or the know-how session takes more rounds. |

## Dependencies & what could delay it
- **Blocking:** read access to the CRM product catalog + the competitor-tagged deals (largely already
  there). A machine-readable competitor list from you would make it cleaner but is not required.
- **Coordination overhead:** a short interview with your SM (or a senior rep) to capture the judgment
  calls that are not written down anywhere.
- **Calendar risk:** the rep interview depends on their availability; a busy stretch or trip shifts it.
- **Out-of-scope:** building a full product recommendation engine (that is a later, separate project).

## Payment
- **Base price: $4,000** (fixed). **Paid before kickoff.**
- **Range:** best case ships sooner at the same price. Worst case stays $4,000 unless a named change
  order applies.

## Contingency
- **Min-cost path:** start with family + competitor-name recognition (covers most real leads); add full
  grade-code precision as a fast-follow only if the volume justifies it.
- **Where it could bubble:** if you want the bot to recommend specific grades (not just recognize them),
  that is a bigger, separate scope with its own quote.
- **Capital note:** no new tool spend here; this runs on data you already own.

## Appendix
- Recognition sources, edge cases, the tacit-knowledge layer: `2026-08-04-todd-phase-map-1.1-to-1.5.md`
  (1.3) + `2026-08-04-todd-crm-deep-dive-scope.md` (Product Catalog + Competitors field, internal).
