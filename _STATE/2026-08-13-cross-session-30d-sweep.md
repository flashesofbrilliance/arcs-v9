# Cross-session 30-day sweep — fan the seed-bank discipline backward

**Status:** RECEIPT + reconciliation · 2026-08-13 · token-efficient (git inventory + 1 distiller, no transcripts)

> Goal (user): "spread and ripple and fan this out token-efficiently cross-session for the past 30 days."
> Method: lean on the cheap residue — the git inventory + ADR/script titles — not raw session transcripts.
> (night-moves ran only once in 30d, so that shortcut was mostly unavailable.)

## The headline finding: the ADR namespace is broken, and now has an authority

Parallel sessions guessed ADR numbers and collided. **On main, ADR-024/025/031/032 are each doubled;**
across branches: 033×3, 039×3, 055×2 (incl. this session's). Root cause: no serialization authority for a
shared namespace. Fix shipped: **ADR-057 — the sequence oracle** (`scripts/oracle.py`), a git-serialized
id+time authority. Going forward every number is drawn from `oracle next adr`; git's non-ff rejection is
the atomic gate. New collisions are prevented by construction.

## Existing collisions — remap PROPOSAL (human-ratify, NOT auto-applied)
`_INBOX/adr-collision-remap.jsonl`. References say only "ADR-0NN" and do not disambiguate *which* of two
files they mean, and some collided ADRs are governing (032 zero-trust). So renumbering is a human act per
pair — the oracle detects; the human disambiguates. Recommended keeps/moves + inbound-ref load are in the
proposal. Movers draw a new number from the oracle, preferring best-fit gap stubs.

## Gaps — stubbed only where TRULY free
The oracle's main-only gap audit listed [21,41,42,43,47,48,49]. **But most are occupied on unmerged
branches** (21,41,42,43,47) — stubbing them would recreate collisions. Only **048, 049** are free
everywhere; both stubbed `RESERVED` with best-fit hints (`_DECISIONS/ADR-048-RESERVED.md`, `-049-`). Fill
convention: replace the stub (keep the number) with a best-fit decision or a ratified collision-mover.
The unreliability of computing this by hand *is* the argument for the oracle.

## Artifact catalog — the 30d tools/commands/hooks, now in the bank
`_SEEDS/registry-artifacts.jsonl` (30 rows: 18 tools · 10 commands · 2 hooks). Mechanization gaps found:
- **Orphan tools** (substantial, no command/skill surface): `idea_montecarlo.py`, `provision_studio_tenant.mjs`.
- **Inchworm family** (`lattice`/`seedbank`/`state_sync` drift checks) share one pattern; confirm
  `state_sync_check.py` is hook-wired like the other two.
- **Overlap to confirm:** `tripwire.sh` vs `leak_check.sh` (both grep `public/*.html` for leaks).

## What this session added to the durable substrate
- **ADR-057** (oracle) + **ADR-055/056** (conformance + connector) + **ADR-053/054** (Tao + pricing) — 5 ADRs.
- **`/faq-eval`** skill · **`seedbank_drift_check.py`** inchworm (hook-wired) · **`oracle.py`** authority.
- `_SEEDS/` bank: repo index + ledger (28 receipts) + artifact registry + oracle counter.

## Next (routed, not done here)
- Ratify the 4 ADR collision remaps (human) → apply via oracle.
- Wire `state_sync_check.py` to a hook if it isn't; resolve tripwire/leak_check overlap; surface the 2 orphan tools.
- The branch-side collisions (033×3, 039×3, 055-hypercube) reconcile when those branches merge — the oracle should gate that merge.
