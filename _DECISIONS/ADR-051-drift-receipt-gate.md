# ADR-051 — Drift receipts: every gate is a detector, every failure a receipt

**Status:** Accepted · 2026-08-11

## Context
Architecture decays by blight/neglect — a forked copy instead of extending the SSOT, an internal name
left on a public page, a dead link no one re-curled. The goal is to *learn* from decay, not just block it.

## Decision
Turn each gate into a drift detector whose failure is a learnable receipt.
- **PR-time:** `scripts/tripwire.sh` greps the diff for names/dead-links/jargon; a hit blocks the merge.
- **Deploy-time:** `tests/family.spec.ts` runs live E2E in `deploy-verify.yml`; failure auto-rolls-back
  and opens a GitHub Issue (the durable receipt).
- **PR body is the receipt** (`pull_request_template.md`); promotion criteria in `docs/PROMOTION.md`.
Recurring receipts promote to ADRs via the ADR/DEWY watcher — the gate teaches the generator.

## Consequences
Drift is caught at the stitch; the blocked diff / rollback Issue is the raw learning material.
