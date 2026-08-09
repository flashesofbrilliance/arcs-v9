# ARCS session state — sprint snapshot

_Updated 2026-08-09 (handoff v3.27.0). Machine head: origin/main `519219f`. All Yuri + Robin
surfaces live. Content + honesty fully healed; the server-side gate is the one open build._

## Shipped this sprint
- **counterpart-forge CLI** — `scripts/forge_counterpart.py --surface {receipt|profile|codex|onedoor}`,
  one canonical token source, inline verify/honesty/craft-floor gates. Every counterpart surface is
  SSOT→generator. + `gen_receipt_close.py`, `provision_studio_tenant.mjs`, `/forge` skill.
- **Receipt Studio** — `/api/receipts/studio/[tenant]` registry route + `robin_app`/`yuri_app` RLS
  roles (prod, isolated, CISO/SRE-reviewed). `ROBIN_/YURI_DATABASE_URL` on Production.
- **Transcript-grounded Yuri heal (2026-08-09)** — pulled the real Jul 23 Granola transcript + ran a
  counterpart-vantage pre-mortem (role-play as Yuri). Caught a **consent/data-ethics fabrication** the
  detector AND the register gauntlet both passed clean (the tape has Yuri disowning it: "I could care
  less", "I trust the people I speak with"). Reframed to an honest self-correction + a "clean by
  design, not precious" read that keeps the real Agentum least-exposure signal. Also: profile → "the
  before" not "step one"; one-door leads with the before/after he named; codex flip beats → I BET /
  YOU SAID; Sundar restored consistently; receipt labels plain-languaged (Robin-safe `meta.labels`
  override); `.close` links gold not UA-blue. All deployed.

## Open (next session) — ONE item
1. **Server-side gate (the send-blocker, family-wide incl Robin's LIVE pages).** Counterpart HTML is
   world-readable in `public/` (curl-by-filename returns full content behind the client overlay).
   Move robin+yuri surfaces to `runtime/counterpart/` + serve via a new `/counterpart/[slug]` route
   with a signed-cookie password gate (HMAC over `AUTH_SECRET`, timing-safe); rewrite the domains to
   the route; preserve the `/api` negative-lookahead (Studio fetch); add a forge `--server-gated`
   flag to drop the redundant client gate. **Dev-server test + ciso-review before the live cutover.**
   One product decision: how Yuri gets the password (first name, or a stronger token in the email).

## Blocking
NONE internally. The gate is the one build gating the send to Yuri.

## Pickup
`/handoff-pickup` → `_STATE/snapshot.json` + the v3.27.0 handoff in `CLAUDE.md`. Forge detail:
`_PATTERNS/forge-pipeline-handoff.md`. Deploy content-only from `main-wt2` with `--no-verify`; the
gate needs a real build (server routes), so deploy it through the normal Vercel build.
