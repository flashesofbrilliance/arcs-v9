# ARCS Session State

**Last updated:** 2026-07-20 (v3.11.0)
**Environment:** Claude Code (local, interactive), worktree `nice-lalande-653c79`, committed via main worktree `frosty-kepler-b69f51`
**Branch:** `main`, pushed to `origin/main`
**Last commits (this thread):** `403d109` (PR #121) · `8429f2e` · `cfbc483` (+ handoff commit)

## v3.11.0 delta — see MEMORY.md [v3.11.0] for full detail

First interactive/local session after a run of cloud sessions (which couldn't deploy). Live to `app.arcs.care`.

- **Anon-share "Sign in to keep" persist fix** (PR #121, `403d109`) — closes the core of the
  v3.9.0 honesty flag. Shared bearing recomposed one-time but sign-in kept nothing; onramp now
  writes `arcs_pending_save`, `ClaimAnonymousReceipts` claims it post-auth → `/receipt/<id>`.
- **Design-system glow tuning, two passes** (`8429f2e`, `cfbc483`) — operator: too hot. Halved
  `signalGlow()` intensity, cut bloom blur ~33% then eased the gauge back, reduced accent-card
  glow, gave `TrueNorthPanel` real glassmorphism (backdrop-blur + translucent blue), left
  Field/select alone. Verified via live computed styles, not by eye.
- **Deploy discipline:** merge-to-main + git-push kept all 29 subdomain aliases intact.

## Open items (operator-approved, not started)

1. **Ledger management** — archive + reset-reflection FIRST, hard-delete last. (WORLD.md: receipts
   are frozen positions; soft-retire preserves Observatory/lineage, erasure is the escalation.)
2. **Authenticated `/recoil` index** — ledger of internal recoil/precall briefs behind OAuth.
   Index existing brief documents FIRST (data in `snapshot.json → ui_artifacts`), DB-backed later.

## Standby (needs operator go)

- **Production auth-loop test** via Gmail connector → fully close v3.9.0 (confirm `zach.harris@gmail.com`;
  authenticates a session + writes one `EPHEMERAL_SAVE` test receipt).
- **Glow strays** — sweep hardcoded glows the tokens missed (neutral ∞ gauge, observatory, receipt widget).

## Prior open items — carried, not re-verified this thread

v3.10.0 sweep backlog (52 open riskFlags), ADR-032 duplicate, epistemic/etymology-sequencer
enforcement; plus standing Sentinel rebuild, SageTrace RLS, B2 cadence/HOLD-gate. Owners hold these — this file is not their ledger.

## Blocking

NONE

## Next session starts at

`/handoff-pickup` → ledger-management (archive/reset) or authenticated `/recoil` index; or run the standby auth-loop test.
