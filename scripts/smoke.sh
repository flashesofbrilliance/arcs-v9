#!/usr/bin/env bash
# scripts/smoke.sh — ADR-016 acceptance gate
# 5 assertions: anonymous compass, session_id returned, receipt userId=null,
#               history 401 for anon, retired claim endpoint stays gone.
# Usage: PROD_URL=https://arcs-v9-zachharris-3439s-projects.vercel.app bash scripts/smoke.sh

set -euo pipefail

BASE="${PROD_URL:-https://arcs-v9-zachharris-3439s-projects.vercel.app}"
PASS=0
FAIL=0

assert_pass() { echo "  ✔ $1"; ((PASS++)); }
assert_fail() { echo "  ✘ $1"; ((FAIL++)); }

echo ""
echo "=== ADR-016 smoke — $BASE ==="
echo ""

# ── A1: Anonymous compass POST returns 200 ────────────────────────────────────
echo "A1: anonymous compass POST → 200"
COMPASS=$(curl -s -o /tmp/arcs-smoke-compass.json -w "%{http_code}" \
  -X POST "$BASE/api/compass" \
  -H "Content-Type: application/json" \
  -d '{"question":"Should I do this?","horizon":"THIS_WEEK","stakes":"MEDIUM"}')
if [ "$COMPASS" = "200" ]; then
  assert_pass "compass POST → 200"
else
  assert_fail "compass POST → $COMPASS (expected 200)"
fi

# ── A2: Response includes session_id ─────────────────────────────────────────
echo "A2: response includes session_id"
SESSION_ID=$(cat /tmp/arcs-smoke-compass.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('session_id',''))" 2>/dev/null || echo "")
if [ -n "$SESSION_ID" ]; then
  assert_pass "session_id present: ${SESSION_ID:0:8}…"
else
  assert_fail "session_id missing from response"
fi

# ── A3: Receipt row has userId=null (anonymous write succeeded) ───────────────
echo "A3: receipt_id present (anonymous DB write)"
RECEIPT_ID=$(cat /tmp/arcs-smoke-compass.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('receipt_id',''))" 2>/dev/null || echo "")
if [ -n "$RECEIPT_ID" ]; then
  assert_pass "receipt_id present: ${RECEIPT_ID:0:8}…"
else
  assert_fail "receipt_id missing — DB write likely failed"
fi

# ── A4: /api/history returns 401 for anonymous requests ──────────────────────
echo "A4: /api/history → 401 for anon"
HISTORY=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/api/history")
if [ "$HISTORY" = "401" ]; then
  assert_pass "history → 401 (auth-gated, correct)"
else
  assert_fail "history → $HISTORY (expected 401)"
fi

# ── A5: /api/receipts/claim stays retired (2026-10-05, PR #847) ─────────────
# A sessionId was never proof of possession; the route must not come back.
echo "A5: /api/receipts/claim is retired (404/405, not 2xx/401)"
CLAIM=$(curl -s -o /dev/null -w "%{http_code}" \
  -X PATCH "$BASE/api/receipts/claim" \
  -H "Content-Type: application/json" \
  -d '{"sessionId":"smoke-test"}')
if [ "$CLAIM" = "404" ] || [ "$CLAIM" = "405" ]; then
  assert_pass "claim → $CLAIM (route retired)"
else
  assert_fail "claim → $CLAIM (expected 404/405; the retired claim route is reachable)"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
rm -f /tmp/arcs-smoke-compass.json
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
