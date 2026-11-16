# Ship to good.arcs.care: published 2026-11-16 (Zach approved)

Staged 2026-11-16 after the build-index audit (PR 2290). Nothing here is public. Each package is scrubbed of counterpart names and ARCS-local paths and still needs Zach's go to become a public repo, a seed-bank row, an arcs-skills marketplace entry and a card on good.arcs.care/instruments.

| Package | Status | Notes |
|---|---|---|
| cruft-sweep-skill | PUBLISHED | github.com/flashesofbrilliance/cruft-sweep-skill; self-test passes; in arcs-skills PR 2. |
| claims-skeptic-skill | PUBLISHED | github.com/flashesofbrilliance/claims-skeptic-skill; in arcs-skills PR 2. |
| decision-receipt-cli | NOT STAGED | Seed row says candidate; `scripts/receipt.py` does not exist (receipts are hand-written SQL). Nothing to ship until it is built. |

## Publish steps, each needs a go
1. Create public repos `cruft-sweep-skill` and `claims-skeptic-skill` under flashesofbrilliance, MIT licence, plugin manifest, README with install line.
2. Add both to `flashesofbrilliance/arcs-skills` `.claude-plugin/marketplace.json` and its README table.
3. Add seed-bank rows (status published) in `_SEEDS/index.jsonl` via the usual path; run `python3 scripts/sync_family_roster.py --check`.
4. Card on `public/good-instruments.html` (and `good.html` if the roster gate asks), then `page_gate`.
