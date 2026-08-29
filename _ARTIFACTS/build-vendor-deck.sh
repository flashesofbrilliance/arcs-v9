#!/usr/bin/env bash
# Deterministically derive the vendor-safe roadmap from the production deck (SSOT).
# Vendor = production MINUS commercial terms (payment section + its nav link + dollar figures) + team-view marker.
# Re-run after ANY edit to prl-roadmap-deck.html so the two surfaces stay 1-1.
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"; SRC="${SRC:-$DIR/prl-roadmap-deck.html}"; OUT="${OUT:-$DIR/prl-vendor-roadmap.html}"
awk '/<section id="pay">/{skip=1} !skip{print} skip && /<\/section>/{skip=0}' "$SRC" \
  | sed -E 's@<a[^>]*href="#pay"[^>]*>[^<]*</a>@@g' \
  | sed -E 's/\$[0-9],[0-9]{3}/pricing shared with Todd directly/g' \
  | sed -E 's#<div class="kick">[^<]*</div>#<div class="kick">PRL Resins \&middot; Chatbot Program \&middot; working view for your team</div>#' \
  > "$OUT"
echo "built $OUT"
