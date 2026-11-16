# Ship to good.arcs.care: staged, not published

Staged 2026-11-16 after the build-index audit (PR 2290). Nothing here is public. Each package is scrubbed of counterpart names and ARCS-local paths and still needs Zach's go to become a public repo, a seed-bank row, an arcs-skills marketplace entry and a card on good.arcs.care/instruments.

| Package | Status | Notes |
|---|---|---|
| cruft-sweep-skill | staged | Skill plus `scripts/cruft_sweep.py` (stdlib Python, parses and prints help). Hard-coded memory dir, bundle dir and hook-state paths replaced by flags and env vars. Not yet tested outside this repo: run its own self-test in a scratch repo before publishing. |
| claims-skeptic-skill | staged | One agent file; repo-specific lines generalised. Cites no tooling. |
| decision-receipt-cli | NOT STAGED | Seed row says candidate; `scripts/receipt.py` does not exist (receipts are hand-written SQL). Nothing to ship until it is built. |

## Publish steps, each needs a go
1. Create public repos `cruft-sweep-skill` and `claims-skeptic-skill` under flashesofbrilliance, MIT licence, plugin manifest, README with install line.
2. Add both to `flashesofbrilliance/arcs-skills` `.claude-plugin/marketplace.json` and its README table.
3. Add seed-bank rows (status published) in `_SEEDS/index.jsonl` via the usual path; run `python3 scripts/sync_family_roster.py --check`.
4. Card on `public/good-instruments.html` (and `good.html` if the roster gate asks), then `page_gate`.
