# Session handoff — 2026-08-11 (watcher family · grammar · ATG · cost)

Marathon Opus session (context hit 686k). Pickup: `/handoff-pickup`. Branch: `claude/todd-work-continuation-1698a8` (yuri worktree). Infra landed here should reconcile to `main`.

## Shipped / committed (this branch)
- **Watcher family** (NOTOMATION-safe, candidates-only, wired into hooks):
  - `scripts/adr_dewy_watch.py` — decision-candidate detector (`--sessions N` sweep, scored `--top`). Ledger `_INBOX/adr-dewy-candidates.jsonl` (517). Curated `_INBOX/adr-dewy-gems.md` (8 gems). Design `_PATTERNS/adr-dewy-candidate-watcher.md`.
  - `scripts/surface_watch.py` — surface-candidate detector ranked by "static charge." Ledger `_INBOX/surface-candidates.jsonl` (1577).
  - Hooks: `pre-compact.sh` (harvest `--sessions 1`) + `session-start.sh` (`--list`) = first activated ARCS listeners.
- **ADR-044 + DEWY receipt** — ATG demonstrated in the wild (instance #1; build held for instance #2, ADR-039). Arc-weld proverb-candidate in the ledger.
- **ADR-045** — model-tier routing by reversibility × value (cost containment).
- **PRL staging forms** — spam layers (honeypot + speed check + Akismet) + form-factor field + Send-To flipped to `info@prlresins.com` on both lead forms (#7, #6). Verified.

## Artifacts (claude.ai; private unless shared)
- PRL Visual Grammar `6cd19221` · Conviction Ledger `d1c787e8` · E2E Forms Test `0aac50f4` · Sugar agenda `b98f7dfc` (updated) · notification-email preview `9fc693fd`.

## Gmail drafts (NOT sent — user action)
1. Todd — design (`r-5781646197188524823`). **Share grammar artifact first, then send.**
2. Todd — staging test (`r-1108636442972750201`). Link public; ready.
3. Jorge — Mailgun/DMARC (`r-5123930822007034803`). **Add his address, then send.**

## Owed by Todd / team
Written sandbox approval (Long call) · negative-keyword + garbage-lead examples · territory map (Bill) · ZoomInfo contact · Jorge's email address.

## Open / resumable
- **Vercel experiment-spinner pilot** — re-skin Conviction Ledger to FieldOS grammar (DesignSync `be620c0c`) + deploy once. Paused on monthly spend limit; agent `a6f5f7140d68c5455`; nothing deployed. Fanned out (see task).
- **Model-tier router** — ADR-045; fanned out (see task).
- **Invariant-polyform fork** `task_b3dbc0ac` — schema + artifact registry + ATG skill + Tao SSOT back-prop. Separate session.
- **Memory hygiene** — SessionStart flags ~19 orphan memory files not in MEMORY.md; run `/consolidate-memory` when convenient.
- **PRL forms E2E** — grab #7/#6 field IDs → ship clickable email-B + Divi CSS pass + Tidio ceiling verify (need real Tidio docs).

## Cost note
Weekly usage 52% mid-week from Opus-on-everything + 686k marathon context. Lever order: end long sessions > route model (Haiku routine / Sonnet default / Opus judgment, ADR-045) > fewer tool calls.

## Next session starts at
`/handoff-pickup`. Either send the 3 drafts (after the 2 prep actions), or resume the fork / model-router / Vercel-spinner when spend resets.
