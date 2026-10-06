<!--
branch: claude/handoff-anthropic-key-audit
head: b04f43d5
created_at: 2026-10-06T14:33:43Z
-->
> **Old Anthropic org key audit (read-only): 8 places still use the capped account; Zach moves and revokes.** Receipt
> `2026-10-06--old-anthropic-key-caller-audit--ZH`. Docs Reconciliation row `old-anthropic-account` set to v3, status decision, owner Zach.

## Shipped
- Compared key fingerprints (sha256 prefix, never values) against the new key and sent a 1-token probe (capped org answers "usage limit" for free).
- On the new key: arcs-v9 `.env.local`, Vercel arcs-v9, GitHub arcs-v9 secret. Morning jobs task goes through the site, so also new.
- On the old capped org (probed): `arcs-v9/.env` (scripts that load `.env` still spend there), `~/.hermes/.env`, `arcs-care-local/.env.local` + `~/.vercel/.env.preview.local`.
- Old by date (set May 2026, not probed): Vercel arcs-care, arcs, arcs-decision-receipts; GitHub arcs-care secret.
- None in scheduled tasks, `~/.arcs/jobs-pipeline.env`, or shell rc; no local n8n.

## Open (next session)
1. Zach: move or delete the old-org keys above, then revoke the old keys in the old org console.
2. question-compass and the stale `~/arcs` clone hold working keys that are not the new key; org unknown (check in console).
3. Cloud n8n not checked; `~/.bash_history` holds 2 capped-org keys in plain text (harmless once revoked).

## Lessons
- `arcs-v9/.env` and `.env.local` held different keys: Next reads `.env.local` first, so the site looked fixed while scripts kept the old key.
- A capped-org probe costs nothing and names the org; a fingerprint match only proves "same as new key".
