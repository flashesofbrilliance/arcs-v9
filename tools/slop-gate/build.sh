#!/usr/bin/env bash
#
# build.sh - vendor the three linters + the rubric into ./lib for a self-contained
# distribution tarball. The single source of truth stays in the repo's scripts/;
# this copies them at pack time so nothing is duplicated in version control.
#
# Run from tools/slop-gate/. Idempotent. Does NOT publish anything.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$DIR/../../scripts"
PATTERNS="$DIR/../../_PATTERNS"

mkdir -p "$DIR/lib"
for f in slop_lint.py slop_eval.py provenance_lint.py; do
  cp "$SRC/$f" "$DIR/lib/$f"
  echo "vendored lib/$f"
done
cp "$PATTERNS/slop-free-rubric.md" "$DIR/lib/slop-free-rubric.md"
echo "vendored lib/slop-free-rubric.md"

# slop_eval.py resolves the rubric as ../_PATTERNS/slop-free-rubric.md relative to
# its own file. In the vendored layout there is no _PATTERNS sibling, so point it
# at the co-vendored copy. This is the only source edit the vendor step makes.
sed -i.bak 's#"..", "_PATTERNS", "slop-free-rubric.md"#"slop-free-rubric.md"#' "$DIR/lib/slop_eval.py"
rm -f "$DIR/lib/slop_eval.py.bak"

echo "build complete. lib/ is self-contained; the package can now be packed."
echo "NOTE: this does not run 'npm publish' or push a Homebrew tap - those are the user's call."
