#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# ONE-SHOT v2 — works around the 'main' worktree lock.
# Builds in a throwaway worktree/branch, pushes straight onto origin/main
# (fast-forward), no PR, never touches your existing worktrees.
#
# Run from anywhere:
#   bash ship-scott-loop-v2.sh
# ============================================================================

REPO_DIR="/Users/zharris/arcs-v9"

cd "$REPO_DIR"
echo "== [1/9] repo root: $(pwd) =="
echo "Existing worktrees:"
git worktree list

echo
echo "== [2/9] fetch + create throwaway worktree off origin/main =="
git fetch origin main
STAMP="$(date +%s)"
BRANCH="scott-loop-tmp-$STAMP"
WT="/tmp/arcs-v9-scott-loop-$STAMP"
git worktree add -b "$BRANCH" "$WT" origin/main
cd "$WT"
echo "Working in: $(pwd)  (branch: $BRANCH, based on origin/main)"

cleanup() {
  cd "$REPO_DIR" 2>/dev/null || true
  git worktree remove "$WT" --force 2>/dev/null || true
  git branch -D "$BRANCH" 2>/dev/null || true
}
trap cleanup EXIT

echo
echo "== [3/9] applying the three edits (exact-anchor replace, atomic) =="
python3 - <<'PYEOF'
import io, sys

def replace_once(path, old, new, label):
    with io.open(path, "r", encoding="utf-8") as f:
        content = f.read()
    n = content.count(old)
    if n != 1:
        print(f"[{label}] FAIL: anchor found {n} time(s) in {path} (expected 1). No files written.", file=sys.stderr)
        sys.exit(1)
    content = content.replace(old, new, 1)
    with io.open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[{label}] OK: {path}")

nc_old = ('        { source: "/:path*", destination: "/scott-receipt.html", '
          'has: [{ type: "host", value: "scott-receipt.arcs.care" }] },\n')
nc_new = (nc_old +
    '        { source: "/:path*", destination: "/scott-teardown.html", '
    'has: [{ type: "host", value: "scott-teardown.arcs.care" }] },\n'
    '        { source: "/:path*", destination: "/scottwitt-cc-teardown.html", '
    'has: [{ type: "host", value: "serialized-teardown.arcs.care" }] },\n'
    '        { source: "/:path*", destination: "/scott-attraction-field.html", '
    'has: [{ type: "host", value: "scott-attraction.arcs.care" }] },\n'
)
replace_once("next.config.ts", nc_old, nc_new, "next.config.ts")

em = "\u2014"; arrow = "\u2192"; rsq = "\u2019"

sub_line = ('<p class="sub">Not a pitch ' + em + ' a mirror. I ran ARCS reverse-listening '
            '(end to start) and a deep-recall pass on both of our recorded calls. '
            'Everything below is serialized straight from the transcripts, no embellishment. '
            'Move at your own pace.</p>')
ask_block = (
    '\n<div class="ask">\n'
    '  <b>It' + rsq + 's an instrument reading ' + arrow + ' not a diagnosis. '
    'Tell me what' + rsq + 's wrong to recalibrate.</b><br>\n'
    '  Every claim across these artifacts traces to verbatim transcripts and the public record. '
    'Where I' + rsq + 've connected two points into a pattern, I' + rsq + 've said so plainly. '
    'Correct anything that' + rsq + 's off; the point of the mirror is to adjust expectations '
    'and sharpen the instrument, not hand down a verdict.\n'
    '</div>'
)
replace_once("public/scott.html", sub_line, sub_line + ask_block, "scott.html body")

keyframes_line = ("@keyframes shake{0%,100%{transform:translateX(0)}20%,60%{transform:translateX(-6px)}"
                   "40%,80%{transform:translateX(6px)}}")
ask_css = ("\n.ask{border:1px solid rgba(255,215,0,.3);border-radius:12px;background:rgba(255,215,0,.05);"
           "padding:16px 18px;font-size:14px;color:var(--text);margin-top:20px}\n"
           ".ask b{color:var(--gold)}")
replace_once("public/scott.html", keyframes_line, keyframes_line + ask_css, "scott.html CSS")

rows = [
    ('AI-displacement <span class="lpct up">75%</span>',
     'AI-displacement&nbsp;<span class="lpct up">75%</span>'),
    ('short-polite otherwise <span class="lpct up">80%</span>',
     'short-polite otherwise&nbsp;<span class="lpct up">80%</span>'),
    ('signals a hard no <span class="lpct up">70%</span>',
     'signals a hard no&nbsp;<span class="lpct up">70%</span>'),
    ('loop is his to close <span class="lpct up">100%</span>',
     'loop is his to close&nbsp;<span class="lpct up">100%</span>'),
]
for i, (old, new) in enumerate(rows, 1):
    replace_once("public/scott-receipt.html", old, new, f"scott-receipt.html row {i}")

print("\nAll three files edited successfully.")
PYEOF

echo
echo "== [4/9] git diff --check =="
git diff --check

echo
echo "== [4/9] focused diff =="
git diff -- next.config.ts public/scott.html public/scott-receipt.html

echo
echo "== [5/9] npm ci && npm run build =="
npm ci
npm run build

echo
echo "== [6/9] commit (on throwaway branch) =="
git add next.config.ts public/scott.html public/scott-receipt.html
git commit -m "feat(scott): wire artifact hosts, clarify instrument, fix receipt wrapping"

echo
echo "== [7/9] rebase onto latest origin/main, then push straight to main (fast-forward, no PR) =="
git fetch origin main
git rebase origin/main
git push origin HEAD:main

COMMIT_SHA="$(git rev-parse HEAD)"
echo "Pushed directly to origin/main. Commit: $COMMIT_SHA"

echo
echo "== [8/9] watching Vercel production deployment =="
DEPLOY_OK=0
for i in $(seq 1 30); do
  STATE="$(vercel ls arcs-v9 --prod 2>/dev/null | grep -m1 "${COMMIT_SHA:0:7}" || true)"
  echo "  [$i/30] $STATE"
  if echo "$STATE" | grep -qi "Ready"; then DEPLOY_OK=1; break; fi
  if echo "$STATE" | grep -qi "Error"; then
    echo "Deployment errored. Run: vercel inspect <deployment-url> --logs" >&2
    exit 1
  fi
  sleep 10
done
if [ "$DEPLOY_OK" -ne 1 ]; then
  echo "Timed out waiting for READY — check 'vercel ls arcs-v9 --prod' manually." >&2
fi

echo
echo "== [9/9] verifying all five hosts =="
for host in scott.arcs.care scott-receipt.arcs.care scott-teardown.arcs.care serialized-teardown.arcs.care scott-attraction.arcs.care; do
  echo "--- https://$host ---"
  curl -sI "https://$host" | head -n 1
done

echo
echo "DONE. Commit $COMMIT_SHA pushed to main. Throwaway worktree/branch cleaned up automatically."
