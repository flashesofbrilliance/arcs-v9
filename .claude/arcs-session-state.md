# ARCS Session State

**Last updated:** 2026-07-20 (v3.12.0)
**Environment:** Claude Code (local, interactive), worktree `todd-call-proposal-clarity-1a9ed2`, committed via main worktree `frosty-kepler-b69f51`
**Branch:** `main`, pushed to `origin/main`
**Last commits (this thread):** `57ae693`..`11830d8` (Todd Hotes chatbot proposal, cherry-picked to main) + `e79f641` (handoff)

## v3.12.0 delta — see MEMORY.md [v3.12.0] and `project_todd_hotes_prl_resins.md` for full detail

Todd Hotes / PRL Resins Phase 1 chatbot proposal build-out. Todd verbally agreed ($1,500) and
answered discovery questions himself. This thread built the proposal page out for his internal
buy-in — Discovery section (his answers folded in), How It Works section, live Stripe buy
button, branch-logic-tree v1 spec (git + Claude Artifact). **Explicit hold:** don't touch his
WordPress/SugarCRM or start the Tidio build until his go + payment — page updates are NOT held.
See CLAUDE.md Handoff v3.12.0 for full detail.

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
