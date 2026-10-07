#!/bin/sh
# merge_train.sh: batch-merge several green PRs into main with ONE CI run instead of one per PR.
#
# Tuition (2026-10-05): this repo is private on a free personal plan, so there is no merge
# queue and no branch protection. Merging N PRs one at a time costs N main builds, and during
# an Actions outage 5 green PRs sat waiting for N separate re-runs. This script stacks the PRs
# as real --no-ff merge commits (GitHub's own message format, so each PR reads MERGED and
# scripts/squash_merge_detector.py accepts them, AGENTS.md gotcha #17), builds the stacked tip
# once (gotcha #4: `npm run build`, never bare `npx next build`), and pushes one fast-forward.
# Push hang-kill + retry matches scripts/ship_docs.sh. It never force-pushes: if main moved
# since the fetch, the push is rejected non-fast-forward and the script tells you to re-run.
#
# Usage: scripts/merge_train.sh [--dry-run] [--yes] [--skip-build] [--lock] PR [PR...]
#        scripts/merge_train.sh --self-test     (offline: local bare repo + stubbed gh)
#   --dry-run     merge + build in a scratch worktree, print the plan, push nothing
#   --yes         skip the "Push N merges to main? [y/N]" prompt
#   --skip-build  skip npm ci / npm run build / npm test (pre-push hooks then still run)
#   --skip-smoke  skip the Playwright smoke run (scripts/merge_train_smoke.sh: Docker postgres + the
#                 same suite fe-smoke ran). Default ON when app code changed; fails closed if Docker is down
#   --lock        hold the ADR-085 main write-lock (scripts/write_lock.py, refs/locks/main on
#                 origin) from before the fetch until exit; refuse if another session holds it.
#                 Renewed after the build and after the prompt; skipped with --dry-run.
#                 Default OFF: without it this script behaves exactly as before.
# Env: MERGE_TRAIN_GH=<cmd>  replaces `gh` (self-test stub)
# Order matters: PRs merge in the order given. Any refusal, conflict, or build failure exits 1
# with nothing pushed. The scratch worktree is always removed (trap EXIT).
# Receipts are PRINTED for the caller to write (AGENTS.md "Receipts or it didn't happen");
# this script never writes to Supabase.
set -u

GH="${MERGE_TRAIN_GH:-gh}"
DRY=0; YES=0; SKIP_BUILD=0; SKIP_SMOKE=0; LOCK=0; LOCKED=0; PRS=""
WRITE_LOCK="$(cd "$(dirname "$0")" && pwd)/write_lock.py"
WT=""; REPO_ROOT=""

die() { echo "merge_train: $*" >&2; exit 1; }

cleanup() {
  if [ $LOCKED -eq 1 ]; then
    python3 "$WRITE_LOCK" --repo "$REPO_ROOT" --session "$LOCK_ID" lock release >/dev/null \
      || echo "merge_train: main write-lock not released (not ours, or remote unreachable); it expires on its TTL" >&2
  fi
  if [ -n "$WT" ] && [ -d "$WT" ]; then
    git -C "$REPO_ROOT" worktree remove --force "$WT" >/dev/null 2>&1 || rm -rf "$WT"
    git -C "$REPO_ROOT" worktree prune >/dev/null 2>&1 || true
  fi
  [ -n "$REPO_ROOT" ] && git -C "$REPO_ROOT" for-each-ref --format='%(refname)' refs/merge-train/ 2>/dev/null |
    while read -r r; do git -C "$REPO_ROOT" update-ref -d "$r"; done
  return 0
}

# ---------------------------------------------------------------- self-test
self_test() {
  SELF=$(cd "$(dirname "$0")" && pwd)/$(basename "$0")
  T=$(mktemp -d "${TMPDIR:-/tmp}/merge_train_selftest.XXXXXX")
  trap 'rm -rf "$T"' EXIT
  FAILS=0
  ok()  { echo "  PASS $*"; }
  bad() { echo "  FAIL $*"; FAILS=$((FAILS+1)); }
  g() { git -c user.name=t -c user.email=t@t -c commit.gpgsign=false "$@"; }

  git init -q --bare -b main "$T/origin.git"
  g clone -q "$T/origin.git" "$T/seed" 2>/dev/null
  ( cd "$T/seed" && echo base > a.txt && echo base > c.txt && g add . && g commit -qm base && g push -q origin main
    g checkout -qb feat/one main && echo one > one.txt && g add . && g commit -qm one && g push -q origin feat/one
    g checkout -qb feat/two main && echo two > two.txt && g add . && g commit -qm two && g push -q origin feat/two
    g checkout -qb feat/clash1 main && echo X > c.txt && g commit -qam x && g push -q origin feat/clash1
    g checkout -qb feat/clash2 main && echo Y > c.txt && g commit -qam y && g push -q origin feat/clash2
    g checkout -qb feat/red main && echo r > r.txt && g add . && g commit -qm r && g push -q origin feat/red )

  # gh stub: PR data from a table; state is MERGED once the head is reachable from origin main.
  cat > "$T/gh" <<EOF
#!/bin/sh
case "\$1 \$2" in
  "auth status") exit 0 ;;
  "repo view") echo "owner/repo"; exit 0 ;;
esac
N=\$3; ALL="\$*"
line=\$(grep "^\$N " "$T/prs.tsv") || { echo "no PR \$N" >&2; exit 1; }
set -- \$line
sha=\$(git -C "$T/origin.git" rev-parse "refs/heads/\$2")
if git -C "$T/origin.git" merge-base --is-ancestor "\$sha" main; then st=MERGED; else st=OPEN; fi
case "\$ALL" in *--jq\ .state) echo "\$st"; exit 0 ;; esac
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "\$st" "\$2" "\$sha" main false "\$3" 0 "title \$N"
EOF
  chmod +x "$T/gh"
  printf '11 feat/one 0\n12 feat/two 0\n21 feat/clash1 0\n22 feat/clash2 0\n31 feat/red 1\n' > "$T/prs.tsv"
  export MERGE_TRAIN_GH="$T/gh" GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t

  fresh() { rm -rf "$T/work"; g clone -q "$T/origin.git" "$T/work" 2>/dev/null; }
  tip() { git -C "$T/origin.git" rev-parse main; }

  echo "(a) two clean PRs -> two --no-ff merge commits, GitHub message format"
  fresh; before=$(tip)
  ( cd "$T/work" && sh "$SELF" --yes --skip-build 11 12 ) > "$T/a.log" 2>&1; rc=$?
  [ $rc -eq 0 ] && ok "exit 0" || { bad "exit $rc"; sed 's/^/    /' "$T/a.log"; }
  subj=$(git -C "$T/origin.git" log --first-parent --format=%s "$before..main")
  [ "$subj" = "$(printf 'Merge pull request #12 from owner/feat/two\nMerge pull request #11 from owner/feat/one')" ] \
    && ok "merge subjects match GitHub format" || bad "subjects: $subj"
  np=$(git -C "$T/origin.git" log --first-parent --min-parents=2 --format=%H "$before..main" | wc -l | tr -d ' ')
  [ "$np" = 2 ] && ok "2 merge commits (2 parents each)" || bad "merge commits=$np"
  grep -q "MERGED" "$T/a.log" && ok "post-push verify saw MERGED" || bad "no MERGED in verify table"
  grep -q -- "--pr11-merge-train--ZH" "$T/a.log" && ok "receipt row printed" || bad "no receipt row"
  [ -z "$(git -C "$T/work" worktree list --porcelain | grep -c '^worktree' | grep -v '^1$')" ] \
    && ok "scratch worktree removed" || bad "scratch worktree left behind"

  echo "(b) conflicting PR -> exit 1, nothing pushed"
  fresh; before=$(tip)
  ( cd "$T/work" && sh "$SELF" --yes --skip-build 21 22 ) > "$T/b.log" 2>&1; rc=$?
  [ $rc -eq 1 ] && ok "exit 1" || bad "exit $rc"
  [ "$(tip)" = "$before" ] && ok "origin main unchanged" || bad "main moved"
  grep -q "conflict.*#22" "$T/b.log" && grep -q "c.txt" "$T/b.log" && ok "names PR #22 and c.txt" || bad "conflict report missing"

  echo "(c) main moves before push -> non-fast-forward, exit 1, no force"
  printf '41 feat/one 0\n' >> "$T/prs.tsv"
  git -C "$T/origin.git" update-ref refs/heads/main "$(git -C "$T/origin.git" rev-list --max-parents=0 main)"   # rewind to base so feat/one is OPEN again
  fresh; before=$(tip)
  ( cd "$T/work" && MERGE_TRAIN_TEST_BEFORE_PUSH="cd '$T/seed' && git checkout -q main && git reset -q --hard '$before' && echo moved > m.txt && git add m.txt && git -c user.name=t -c user.email=t@t commit -qm moved && git push -qf origin main" \
      sh "$SELF" --yes --skip-build 41 ) > "$T/c.log" 2>&1; rc=$?
  [ $rc -eq 1 ] && ok "exit 1" || { bad "exit $rc"; sed 's/^/    /' "$T/c.log"; }
  grep -q "main moved; re-run" "$T/c.log" && ok "prints 'main moved; re-run'" || bad "message missing"
  [ "$(git -C "$T/origin.git" log -1 --format=%s main)" = moved ] && ok "the other push survived (no force)" || bad "main clobbered"

  echo "(d) PR with a FAILURE check -> refused"
  fresh; before=$(tip)
  ( cd "$T/work" && sh "$SELF" --yes --skip-build 31 ) > "$T/d.log" 2>&1; rc=$?
  [ $rc -eq 1 ] && grep -q "#31.*failed check" "$T/d.log" && [ "$(tip)" = "$before" ] \
    && ok "refused, nothing pushed" || bad "rc=$rc"

  echo "(e) --dry-run -> plan printed, nothing pushed"
  fresh; before=$(tip)
  ( cd "$T/work" && sh "$SELF" --dry-run --skip-build 11 ) > "$T/e.log" 2>&1; rc=$?
  [ $rc -eq 0 ] && [ "$(tip)" = "$before" ] && grep -q "DRY RUN" "$T/e.log" && ok "dry run clean" || bad "rc=$rc"

  echo "(f) --lock while another session holds the main write-lock -> refused, nothing pushed"
  git -C "$T/origin.git" update-ref refs/heads/main "$(git -C "$T/origin.git" rev-list --max-parents=0 main)"
  printf '51 feat/two 0\n' >> "$T/prs.tsv"
  fresh; before=$(tip)
  WRITE_LOCK_SESSION=other python3 "$WRITE_LOCK" --repo "$T/work" lock acquire --ttl 600 >/dev/null 2>&1
  ( cd "$T/work" && WRITE_LOCK_SESSION=train sh "$SELF" --lock --yes --skip-build 51 ) > "$T/f.log" 2>&1; rc=$?
  [ $rc -eq 1 ] && [ "$(tip)" = "$before" ] && grep -q "held by other" "$T/f.log" \
    && ok "refused while held, main unchanged" || { bad "rc=$rc"; sed 's/^/    /' "$T/f.log"; }
  WRITE_LOCK_SESSION=other python3 "$WRITE_LOCK" --repo "$T/work" lock release >/dev/null 2>&1

  echo "(g) --lock when free -> merges, pushes, and releases the lock on exit"
  fresh; before=$(tip)
  ( cd "$T/work" && WRITE_LOCK_SESSION=train sh "$SELF" --lock --yes --skip-build 51 ) > "$T/g.log" 2>&1; rc=$?
  [ $rc -eq 0 ] && [ "$(tip)" != "$before" ] && ok "pushed under the lock" || { bad "rc=$rc"; sed 's/^/    /' "$T/g.log"; }
  python3 "$WRITE_LOCK" --repo "$T/work" lock status > "$T/g2.log" 2>&1
  grep -q "free (last holder train)" "$T/g2.log" && ok "lock released on exit" || bad "lock not released: $(cat "$T/g2.log")"

  [ $FAILS -eq 0 ] && { echo "self-test: ALL PASS"; exit 0; } || { echo "self-test: $FAILS FAIL"; exit 1; }
}

# ---------------------------------------------------------------- args
for a in "$@"; do
  case "$a" in
    --self-test) self_test ;;
    --dry-run) DRY=1 ;;
    --yes) YES=1 ;;
    --skip-build) SKIP_BUILD=1 ;;
    --skip-smoke) SKIP_SMOKE=1 ;;
    --lock) LOCK=1 ;;
    -h|--help) sed -n '2,27p' "$0"; exit 0 ;;
    *[!0-9]*|"") die "bad argument: $a (PR numbers only)" ;;
    *) PRS="$PRS $a" ;;
  esac
done
[ -z "$PRS" ] && { echo "usage: merge_train.sh [--dry-run] [--yes] [--skip-build] [--skip-smoke] PR [PR...]" >&2; exit 2; }
NPR=$(echo $PRS | wc -w | tr -d ' ')

# ---------------------------------------------------------------- 1. preflight
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || die "not in a git repo"
trap cleanup EXIT
trap 'exit 130' INT TERM
DIRTY=$(git status --porcelain --untracked-files=no | grep -vE '_INBOX/|_STATE/snapshot.json|public/family-roster.json' || true)
[ -n "$DIRTY" ] && { echo "merge_train: dirty tree, commit first:" >&2; echo "$DIRTY" >&2; exit 1; }
$GH auth status >/dev/null 2>&1 || die "gh not authenticated (gh auth login)"
OWNER_REPO=$($GH repo view --json nameWithOwner -q .nameWithOwner) || die "gh repo view failed"
OWNER=${OWNER_REPO%%/*}
# One identity per train run (pid), so two trains from the same checkout never share a lock.
LOCK_ID="${WRITE_LOCK_SESSION:-merge-train@$(hostname -s 2>/dev/null || hostname):$$:$REPO_ROOT}"
lock_renew() {   # re-entrant acquire = extend; fails if someone took it over (ADR-085)
  [ $LOCKED -eq 1 ] || return 0
  python3 "$WRITE_LOCK" --repo "$REPO_ROOT" --session "$LOCK_ID" lock acquire --ttl 1800 --reason "merge train:$PRS" \
    || die "main write-lock lost before $1; nothing pushed"
}
if [ $LOCK -eq 1 ] && [ $DRY -eq 1 ]; then
  echo "merge_train: --dry-run pushes nothing, so --lock is skipped"
elif [ $LOCK -eq 1 ]; then
  LOCKED=1   # set BEFORE acquire: an interrupt mid-acquire still releases (release of a free lock is a no-op)
  python3 "$WRITE_LOCK" --repo "$REPO_ROOT" --session "$LOCK_ID" lock acquire --ttl 1800 --reason "merge train:$PRS" \
    || { LOCKED=0; die "main write-lock not acquired (see above); nothing merged"; }
fi
GIT_TERMINAL_PROMPT=0 git fetch -q origin main || die "fetch origin main failed"
BASE=$(git rev-parse origin/main)

JQ='[.statusCheckRollup[]? | (.conclusion // .state // "")] as $c
| [.state, .headRefName, .headRefOid, .baseRefName, (.isDraft|tostring),
   ($c | map(select(. == "FAILURE" or . == "CANCELLED" or . == "TIMED_OUT" or . == "ERROR" or . == "STARTUP_FAILURE")) | length | tostring),
   ($c | map(select(. == "" or . == "PENDING" or . == "EXPECTED" or . == "QUEUED" or . == "IN_PROGRESS")) | length | tostring),
   .title] | @tsv'

INFO=""; REFUSE=0; TAB=$(printf '\t')
for N in $PRS; do
  L=$($GH pr view "$N" --json state,headRefName,headRefOid,baseRefName,title,isDraft,statusCheckRollup --jq "$JQ") \
    || { echo "  #$N: gh pr view failed" >&2; REFUSE=1; continue; }
  IFS="$TAB" read -r ST HEAD OID BASEREF DRAFT NBAD NPEND TITLE <<EOF
$L
EOF
  [ "$ST" = OPEN ] || { echo "  #$N: state $ST (need OPEN)" >&2; REFUSE=1; }
  [ "$DRAFT" = false ] || { echo "  #$N: draft" >&2; REFUSE=1; }
  [ "$BASEREF" = main ] || { echo "  #$N: base is $BASEREF, not main" >&2; REFUSE=1; }
  [ "$NBAD" = 0 ] || { echo "  #$N: $NBAD failed check(s) (FAILURE/CANCELLED/TIMED_OUT)" >&2; REFUSE=1; }
  [ "$NPEND" = 0 ] || echo "  #$N: WARNING $NPEND check(s) still pending"
  if GIT_TERMINAL_PROMPT=0 git fetch -q origin "+refs/heads/$HEAD:refs/merge-train/pr$N" 2>/dev/null \
     || GIT_TERMINAL_PROMPT=0 git fetch -q origin "+refs/pull/$N/head:refs/merge-train/pr$N" 2>/dev/null; then
    GOT=$(git rev-parse "refs/merge-train/pr$N")
    [ "$GOT" = "$OID" ] || { echo "  #$N: fetched $GOT but PR head is $OID (pushed mid-run?)" >&2; REFUSE=1; }
  else
    echo "  #$N: could not fetch head $HEAD" >&2; REFUSE=1
  fi
  INFO="$INFO$N$TAB$HEAD$TAB$OID$TAB$TITLE
"
done
[ $REFUSE -eq 0 ] || die "refusing: fix the PRs above (nothing merged)"

# ---------------------------------------------------------------- 2. merge in scratch worktree
WT=$(mktemp -d "${TMPDIR:-/tmp}/merge_train.XXXXXX")
rmdir "$WT"
git worktree add -q --detach "$WT" "$BASE" || die "worktree add failed"
MERGES=""
echo "$INFO" | while IFS="$TAB" read -r N HEAD OID TITLE; do
  [ -z "$N" ] && continue
  if ! git -C "$WT" merge --no-ff --no-edit -m "Merge pull request #$N from $OWNER/$HEAD" -m "$TITLE" "$OID" >/dev/null 2>&1; then
    echo "merge_train: conflict merging PR #$N ($HEAD); conflicting files:" >&2
    git -C "$WT" diff --name-only --diff-filter=U | sed 's/^/  /' >&2
    git -C "$WT" merge --abort >/dev/null 2>&1
    exit 1
  fi
  echo "$N$TAB$(git -C "$WT" rev-parse HEAD)"
done > "$WT/.merge-train-map" || die "aborted; nothing pushed"
MAP=$(cat "$WT/.merge-train-map"); rm -f "$WT/.merge-train-map"
TIP=$(git -C "$WT" rev-parse HEAD)

# ---------------------------------------------------------------- 3. build once
if [ $SKIP_BUILD -eq 0 ]; then
  MAIN_CO=$(git worktree list --porcelain | sed -n '1s/^worktree //p')
  if [ -d "$MAIN_CO/node_modules" ] && cmp -s "$MAIN_CO/package-lock.json" "$WT/package-lock.json"; then
    echo "merge_train: package-lock.json byte-identical to $MAIN_CO, symlinking its node_modules"
    ln -s "$MAIN_CO/node_modules" "$WT/node_modules"
  else
    echo "merge_train: package-lock.json differs from main checkout (or no node_modules), running npm ci"
    ( cd "$WT" && npm ci --no-audit --no-fund ) || die "npm ci failed; nothing pushed"
  fi
  ( cd "$WT" && npm run build ) || die "npm run build failed on the stacked tip; nothing pushed"
  if ( cd "$WT" && node -e 'process.exit(require("./package.json").scripts?.test ? 0 : 1)' ); then
    ( cd "$WT" && npm test ) || die "npm test failed; nothing pushed"
  else
    echo "merge_train: no test script in package.json, skipping npm test"
  fi
  if [ $SKIP_SMOKE -eq 0 ]; then
    sh "$(dirname "$0")/merge_train_smoke.sh" "$WT" "$BASE" || die "smoke failed (or Docker is down; --skip-smoke overrides); nothing pushed"
  else
    echo "merge_train: --skip-smoke, Playwright smoke not run"
  fi
  rm -f "$WT/node_modules" 2>/dev/null || true
fi

lock_renew "the plan/prompt"

# ---------------------------------------------------------------- 4. plan
echo
echo "== merge train: $NPR PR(s) onto origin/main $BASE"
echo "$MAP" | while IFS="$TAB" read -r N S; do echo "  #$N -> merge $S"; done
echo "  tip: $TIP"
git -C "$WT" log --oneline --first-parent "$BASE..HEAD" | sed 's/^/  /'
[ $DRY -eq 1 ] && { echo "DRY RUN: nothing pushed"; exit 0; }
if [ $YES -eq 0 ]; then
  printf 'Push %s merges to main? [y/N] ' "$NPR"
  read -r ans </dev/tty || ans=""
  case "$ans" in y|Y|yes) ;; *) echo "merge_train: not pushed"; exit 1 ;; esac
fi

lock_renew "the push"

# ---------------------------------------------------------------- 5. push (fast-forward only, never force)
[ -n "${MERGE_TRAIN_TEST_BEFORE_PUSH:-}" ] && sh -c "$MERGE_TRAIN_TEST_BEFORE_PUSH" >/dev/null 2>&1
# Hang-kill scoped to THIS run (a global `pkill -f "git push"` would kill parallel sessions' pushes).
pkill -f "git -C $WT push" 2>/dev/null && sleep 1 || true
# Built tip already passed npm run build; with --skip-build, let the pre-push hook run.
NOVERIFY=""; [ $SKIP_BUILD -eq 0 ] && NOVERIFY="--no-verify"
push() { GIT_TERMINAL_PROMPT=0 git -C "$WT" push $NOVERIFY origin HEAD:refs/heads/main 2>&1; }
OUT=$(push); RC=$?
if [ $RC -ne 0 ]; then
  echo "$OUT" | grep -qE 'non-fast-forward|fetch first|\[rejected\]' && { echo "$OUT" >&2; die "main moved; re-run"; }
  echo "merge_train: push failed once, retrying in 5s..."; sleep 5
  pkill -f "git -C $WT push" 2>/dev/null || true
  OUT=$(push); RC=$?
  [ $RC -ne 0 ] && { echo "$OUT" >&2; echo "$OUT" | grep -qE 'non-fast-forward|fetch first|\[rejected\]' && die "main moved; re-run"; die "push failed"; }
fi
echo "merge_train: pushed $TIP to main"

# ---------------------------------------------------------------- 6. verify + receipts
DATE=$(date +%Y-%m-%d); NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo
printf '%-6s %-42s %s\n' PR "merge sha" state
echo "$MAP" | while IFS="$TAB" read -r N S; do
  st=""; i=0
  while [ $i -lt 12 ]; do
    st=$($GH pr view "$N" --json state --jq .state 2>/dev/null)
    [ "$st" = MERGED ] && break
    i=$((i+1)); sleep 5
  done
  printf '#%-5s %-42s %s\n' "$N" "$S" "${st:-UNKNOWN}"
done
echo
echo "Receipts to write (public.decision_receipt; one per PR; not written by this script):"
echo "$MAP" | while IFS="$TAB" read -r N S; do
  echo "  receipt_id=${DATE}--pr${N}-merge-train--ZH | question='Merge PR #$N to main via merge train?' | horizon=today | stakes=<low|medium|high> | mode=QUICKMOVE | what_confirmed={merge commit $S on main, tip $TIP pushed fast-forward, gh state per table above} | what_unconfirmed={Vercel deploy READY, CI run on $TIP} | operator=<who> | event_at=$NOW | source_repo=$OWNER_REPO | refs={PR #$N,$S}"
done
exit 0
