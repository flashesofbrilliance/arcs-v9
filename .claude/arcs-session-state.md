# ARCS Session State

**Last updated:** 2026-05-29 (v2.2.0)
**Last commit (arcs-v9):** 695afb3 — chore(adr): ADR-019 receipt-core Python boundary
**Last commit (perplexity-mcp):** de76184 — fix(mcp): add basePath + maxDuration to createMcpHandler options

## Status

- arcs-v9 Vercel: ✅ LIVE — `arcs-zachharris-3439s-projects.vercel.app`
- arcs-care: ✅ LIVE — arcs.care (PLG Phase 1 fully live)
- **perplexity-mcp / mcp.arcs.care: ✅ FULLY OPERATIONAL**
  - `basePath` fix deployed — `/api/mcp` returns 200 + tools list
  - `SUPABASE_SERVICE_KEY` added — `log_arcs_session` persistence live, `degraded: false`
  - MCP initialize handshake verified end-to-end
- Supabase (owdiiyvphyifukygvxhg): 9 tables, RLS ✅ APPLIED
- ADRs: 001–019 in arcs-v9/_DECISIONS/ (ADR-019 = receipt-core Python boundary, NCI:82)
- All repos pushed to GitHub ✅

## P-track status

| Track | Status | Gate |
|---|---|---|
| P0: arcs-v9 → GitHub | ✅ Done | — |
| P2: Perplexity MCP | ✅ FULLY DONE | Live at `mcp.arcs.care`, basePath fixed, key wired |
| P4: arcs-v9 → Vercel | ✅ Done | — |
| P5: arcs-care PLG Phase 1 | ✅ Done | — |
| P7: receipt-core implementation | 🔓 Unblocked | ADR-019 decided, ready to implement |

## Requires human action (priority order)

1. **`~/.claude/mcp.json`** — add `"type": "http"` + update URL to `https://mcp.arcs.care/api/mcp`, restart Claude Code → Perplexity tools live in session
2. **ADR-016 implementation** — wire `src/lib/auth.ts` (Auth.js v5 Resend EmailProvider) + remove compass 401 gate + `/api/receipts/claim`
3. **DMARC enforcement** — `dig TXT _dmarc.arcs.care` — if monitor-only, emails in spam
4. **30-day calendar reminder** — 2026-06-27 (ADR-013 conversion trigger watchdog)
5. **Add `compass_receipt_id` column** to Supabase `waitlist` table
6. **Preview DATABASE_URL (arcs-v9)** — add via Vercel dashboard (CLI v53 bug)

## Phase 7 open code items (priority order)

1. **receipt-core implementation** (ADR-019 scope, UNBLOCKED):
   - `ReceiptStore.write()` → bridge → `ReceiptObject` validate → Supabase upsert
   - `ReceiptStore.seal()` method
   - `tests/test_receipt_bridge_roundtrip.py`
2. **Receipt Book P3** — quality_score pass on 11 unsealed receipts
3. **CLUE integration** — receipt lifecycle events (blocked on receipt-core)
4. **NGI linking** — `receipt_id` on no-go entries (blocked on receipt-core)
5. **CLI commands** — `arcs receipt log/inspect/export`

## Known structural notes

- `arcs_dewy_log.py` (DEWYLog/DEWYEntry) has zero callers — deferred
- Spots badge hardcoded `SPOTS_REMAINING = 10` — update manually or wire Supabase
- Second Vercel Toolbar thread `YyvHp8_-4jXX` ("Is the API working?") — NOT resolved
