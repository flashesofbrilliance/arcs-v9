#!/usr/bin/env bash
# Vendor-neutral NFTT ship-gate checks. Callable from Claude hooks,
# Hermes hooks, or plain CI. Exit 0 = pass, non-zero = fail.
# Portable: BSD grep (macOS) has no -P, so dash/PII scans use python3.

set -euo pipefail

FILE="${1:?usage: nftt-gates.sh <path-to-html-draft>}"

fail() { echo "GATE FAIL: $1" >&2; exit 1; }

[ -f "$FILE" ] || fail "file not found: $FILE"

# 1. Zero em/en dashes or minus-as-dash (U+2014, U+2013, U+2212)
if python3 -c "
import sys
t = open(sys.argv[1], encoding='utf-8').read()
bad = [c for c in ('\u2014', '\u2013', '\u2212') if c in t]
sys.exit(1 if bad else 0)
" "$FILE"; then :; else
  fail "em-dash/en-dash/minus-as-dash found in $FILE"
fi

# 2. Title suffix + description present
grep -q '<title>.*· NFTT</title>' "$FILE" || fail "title missing '· NFTT' suffix"
grep -q '<meta name="description" content="[^"]\{10,\}"' "$FILE" \
  || fail "description meta missing or too short"

# 3. robots meta present
grep -q '<meta name="robots"' "$FILE" || fail "robots meta missing"

# 4. PII scan (basic — extend as needed)
if python3 -c "
import re, sys
t = open(sys.argv[1], encoding='utf-8').read()
sys.exit(1 if re.search(r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}', t, re.I) else 0)
" "$FILE"; then :; else
  fail "possible email address found in $FILE"
fi

# 5. AI-slop safeguard (single source: scripts/slop_lint.py, on main since PR #509).
#    MECHANICAL half is a HARD FAIL (tier-A cliches + em-dashes, ~zero legit use on a
#    public surface). The metrics half (burstiness + specificity) is ADVISORY, run in
#    --mode essay for these reflective NFTT posts (evidence-aware, 10% floor calibrated
#    to real essays) so it informs without false-failing the genre. Rubric:
#    _PATTERNS/slop-free-rubric.md. Split rationale: mechanical blocks, judgment advises.
if [ -f scripts/slop_lint.py ] && command -v python3 >/dev/null 2>&1; then
  python3 scripts/slop_lint.py "$FILE" || fail "AI-slop mechanical lint (tier-A cliche or em-dash) in $FILE"
  echo "-- slop metrics (advisory, mode=essay) --"
  python3 scripts/slop_lint.py --metrics --mode essay "$FILE" 2>&1 | grep -E 'burstiness|UNDER|specificity' || true
fi

# 6. Visual-slop safeguard: the impeccable design detector, wired as a RATCHET (single
#    source: scripts/nftt_contrast_ratchet.py, on main since PR #528). The brand profile
#    (.impeccable/config.json) already exempts the ARCS house grammar so brand != slop.
#    Low-contrast is NOT config-exempted; instead the ratchet FAILS only on a NEW low-contrast
#    finding above the committed per-file baseline (_STATE/nftt-contrast-baseline.json, a
#    labeled DEFERRAL of the mixed existing findings, not a clean bill). This catches a new
#    contrast regression without turning red on legacy debt. After a deliberate accepted
#    change or a debt fix, re-snapshot: python3 scripts/nftt_contrast_ratchet.py --update-baseline.
if [ -f scripts/nftt_contrast_ratchet.py ] && command -v python3 >/dev/null 2>&1; then
  python3 scripts/nftt_contrast_ratchet.py "$FILE" || fail "NEW low-contrast regression above baseline in $FILE (raise the token, or --update-baseline if deliberate)"
fi

echo "GATE PASS: $FILE"
