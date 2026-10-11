#!/usr/bin/env bash
# Package the monday.com take-home: ONE zip under 10 MB with non-empty source/ and presentation/.
# Usage: ./package.sh   (run from takehome-workspace). Builds ../submission.zip and verifies it. Never uploads anything.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd "$HERE"
OUT="$HERE/submission.zip"; LIMIT=$((10*1024*1024))
for d in source presentation; do
  [ -d "$d" ] && [ -n "$(find "$d" -type f ! -name '.DS_Store' | head -1)" ] || { echo "FAIL: $d/ is missing or empty"; exit 1; }
done
rm -f "$OUT"
zip -qr "$OUT" source presentation -x '*/.DS_Store' '*/node_modules/*' '*/.git/*' '*/.env*' '*/*.key' '*/*.pem'
SIZE=$(stat -f%z "$OUT" 2>/dev/null || stat -c%s "$OUT")
echo "zip: $OUT  size: $SIZE bytes (limit $LIMIT)"
[ "$SIZE" -lt "$LIMIT" ] || { echo "FAIL: zip is 10 MB or larger"; exit 1; }
echo "contents:"; unzip -l "$OUT" | sed -n '4,$p' | head -40
if unzip -l "$OUT" | grep -q -i -E '\.env|secret|token|password|\.pem|\.key'; then echo "WARN: a secret-looking filename is inside the zip"; fi
echo "OK: structure and size pass. Now complete every checklist item in the portal before submitting."
