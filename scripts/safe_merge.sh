#!/usr/bin/env bash
# safe_merge.sh: the one way a session merges a PR in arcs-v9.
#
# Tuition (2026-10-20, one day of parallel sessions): a parent merged a child's PR before the
# child's last push; a wait loop exited early and merged while Vercel was still PENDING (PR 1722);
# a pre-commit refusal was hidden behind `| tail` so the next destructive step ran. Frustration
# Gate (AGENTS.md gotcha 15): one helper that fails the whole class instead of three instance fixes.
#
# Usage: scripts/safe_merge.sh <pr> <expected-head-sha> [--timeout SECS] [--interval SECS]
#        scripts/safe_merge.sh --self-test      (offline: fake gh on PATH, merge gates + job/tool derivation)
#   1. refuses unless the PR head equals <expected-head-sha> (full sha or a prefix of 7+)
#   2. waits until every check on that head is final, then refuses unless all are SUCCESS
#      (PENDING past the timeout, FAILURE, CANCELLED, only-SKIPPED checks, or zero checks: refuse; SKIPPED beside a SUCCESS is neutral)
#   3. CONFLICTING mergeable: stop and say so (never rebases)
#   3b. a Hermes PR (branch hermes/*) also needs commit status claude-code-review = success on that
#      exact head (scripts/claude_pr_review.py; Zach 2026-11-12: Claude Code reviews every Hermes PR)
#   4. merges with `gh pr merge --merge --match-head-commit <sha>` (gotcha 17: never squash/rebase)
#   5. prints the merge commit and a decision_receipt INSERT template (never writes to Supabase), with
#      job_id and tool_id filled (Sprint 5 coverage, AGENTS.md "Receipts or it didn't happen"):
#      job_id = a `job:backlog:<id>` named in the PR body or branch, else the one backlog row the diff adds
#      or changes; tool_id = tool:script:<name> of the scripts/ file with the most changed lines. When
#      neither derives, a '<REQUIRED ...>' placeholder is printed: it fails the column CHECK, so it can
#      never land as a silent NULL.
# Env: SAFE_MERGE_TIMEOUT (default 1800), SAFE_MERGE_INTERVAL (default 20),
#      SAFE_MERGE_NOCHECK_GRACE (default 120: zero checks right after a push counts as pending this long).
# Exit: 0 merged · 1 refused · 2 usage. Gating steps are never piped through tail/head/grep.
set -euo pipefail

die() { echo "safe_merge: REFUSE: $*" >&2; exit 1; }

self_test() {
  local here tmp pass=0 fail=0
  here="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
  tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' RETURN
  mkdir -p "$tmp/bin"
  # Fake gh: state lives in $FAKE_DIR. `checks` file holds one JSON array per line; each call
  # to `gh pr checks` consumes the next line (the last line repeats).
  cat > "$tmp/bin/gh" <<'FAKE'
#!/usr/bin/env bash
set -eu
d="$FAKE_DIR"
case "$1 $2" in
  "pr view")
    if [[ "$*" == *mergeCommit* ]]; then echo '{"state":"MERGED","mergeCommit":{"oid":"m3rg3c0mm1t"}}'; exit 0; fi
    if [[ "$*" == *files* ]]; then cat "$d/meta" 2>/dev/null || echo '{"body":"","headRefName":"b","files":[]}'; exit 0; fi
    printf '{"headRefOid":"%s","headRefName":"%s","mergeable":"%s","state":"OPEN","title":"t","url":"u"}\n' "$(cat "$d/head")" "$(cat "$d/branch" 2>/dev/null || echo claude/x)" "$(cat "$d/mergeable")";;
  "api repos/{owner}/{repo}/commits/"*) cat "$d/review" 2>/dev/null || echo missing;;
  "pr checks")
    n=$(cat "$d/n" 2>/dev/null || echo 0); n=$((n+1)); echo $n > "$d/n"
    total=$(wc -l < "$d/checks"); [ $n -gt $total ] && n=$total
    sed -n "${n}p" "$d/checks";;
  "pr merge") echo "$*" > "$d/merged";;
  "auth status") [ "$(cat "$d/head")" = authdown ] && { echo "not logged in" >&2; exit 1; }; exit 0;;
  "pr diff") cat "$d/diff" 2>/dev/null || true;;
  *) echo "fake gh: unexpected $*" >&2; exit 9;;
esac
FAKE
  chmod +x "$tmp/bin/gh"
  local S='{"name":"Vercel","state":"SUCCESS"}' P='{"name":"Vercel","state":"PENDING"}' F='{"name":"build","state":"FAILURE"}'
  run_case() { # name expect_rc expect_merged head mergeable timeout checks-lines...
    local name="$1" want="$2" want_merged="$3" head="$4" mg="$5" to="$6"; shift 6
    local d="$tmp/$name"; mkdir -p "$d"; echo "$head" > "$d/head"; echo "$mg" > "$d/mergeable"
    printf '%s\n' "$@" > "$d/checks"
    local rc=0
    FAKE_DIR="$d" PATH="$tmp/bin:$PATH" SAFE_MERGE_INTERVAL=0 SAFE_MERGE_NOCHECK_GRACE=0 SAFE_MERGE_TIMEOUT="$to" \
      bash "$here" 42 abc1234def > "$d/out" 2>&1 || rc=$?
    local merged=no; [ -f "$d/merged" ] && merged=yes
    if [ "$rc" = "$want" ] && [ "$merged" = "$want_merged" ]; then
      echo "PASS $name (rc=$rc merged=$merged)"; pass=$((pass+1))
    else
      echo "FAIL $name (rc=$rc want $want, merged=$merged want $want_merged)"; sed 's/^/    /' "$d/out"; fail=$((fail+1))
    fi
    if [ "$merged" = yes ] && ! grep -q -- '--merge --match-head-commit abc1234def' "$d/merged"; then
      echo "FAIL $name: merge args wrong: $(cat "$d/merged")"; fail=$((fail+1))
    fi
  }
  run_case pending-then-success 0 yes abc1234def0000 MERGEABLE 60 "[$P]" "[$P]" "[$S]"
  run_case failure              1 no  abc1234def0000 MERGEABLE 60 "[$S,$F]"
  run_case head-mismatch        1 no  ffff1234def000 MERGEABLE 60 "[$S]"
  run_case conflict             1 no  abc1234def0000 CONFLICTING 60 "[$S]"
  run_case timeout              1 no  abc1234def0000 MERGEABLE 0 "[$P]"
  run_case zero-checks          1 no  abc1234def0000 MERGEABLE 60 "[]"
  K='{"name":"smoke","state":"SKIPPED"}'
  run_case skipped-beside-success 0 yes abc1234def0000 MERGEABLE 60 "[$S,$K]"
  run_case only-skipped         1 no  abc1234def0000 MERGEABLE 60 "[$K]"
  run_case skipped-beside-failure 1 no abc1234def0000 MERGEABLE 60 "[$S,$K,$F]"
  run_case github-down          1 no  authdown       MERGEABLE 60 "[$S]"
  # Hermes PRs need a head-bound claude-code-review success (claude_pr_review.py).
  review_case() { # name review-state expect_rc expect_merged
    local name="$1" d="$tmp/$1"; mkdir -p "$d"; echo abc1234def0000 > "$d/head"; echo MERGEABLE > "$d/mergeable"
    echo hermes/x > "$d/branch"; echo "[$S]" > "$d/checks"; [ -n "$2" ] && echo "$2" > "$d/review"
    local rc=0; FAKE_DIR="$d" PATH="$tmp/bin:$PATH" SAFE_MERGE_INTERVAL=0 SAFE_MERGE_NOCHECK_GRACE=0 bash "$here" 42 abc1234def > "$d/out" 2>&1 || rc=$?
    local merged=no; [ -f "$d/merged" ] && merged=yes
    if [ "$rc" = "$3" ] && [ "$merged" = "$4" ]; then echo "PASS $name (rc=$rc merged=$merged)"; pass=$((pass+1))
    else echo "FAIL $name (rc=$rc want $3, merged=$merged want $4)"; sed 's/^/    /' "$d/out"; fail=$((fail+1)); fi
  }
  review_case hermes-review-success success 0 yes
  review_case hermes-review-failure failure 1 no
  review_case hermes-review-missing ""      1 no
  # Receipt job_id/tool_id derivation (Sprint 5): body ref, backlog-diff row, placeholders.
  derive_case() { # name meta-json diff-text want-job-grep want-tool-grep
    local name="$1" d="$tmp/$1"; mkdir -p "$d"; echo abc1234def0000 > "$d/head"; echo MERGEABLE > "$d/mergeable"
    echo "[$S]" > "$d/checks"; printf '%s\n' "$2" > "$d/meta"; printf '%s\n' "$3" > "$d/diff"
    FAKE_DIR="$d" PATH="$tmp/bin:$PATH" SAFE_MERGE_INTERVAL=0 SAFE_MERGE_NOCHECK_GRACE=0 bash "$here" 42 abc1234def > "$d/out" 2>&1 || true
    if grep -qF -- "$4" "$d/out" && grep -qF -- "$5" "$d/out"; then echo "PASS $name"; pass=$((pass+1))
    else echo "FAIL $name (want '$4' and '$5')"; sed 's/^/    /' "$d/out"; fail=$((fail+1)); fi
  }
  derive_case job-from-body \
    '{"body":"Serves job:backlog:row-a.","headRefName":"claude/x","files":[{"path":"scripts/a.py","additions":9,"deletions":1},{"path":"scripts/b.sh","additions":2,"deletions":0}]}' '' \
    "'job:backlog:row-a'," "'tool:script:a.py'"
  derive_case job-from-backlog-diff \
    '{"body":"","headRefName":"claude/x","files":[{"path":"_QUEUE/induced-backlog.jsonl","additions":1,"deletions":0},{"path":"AGENTS.md","additions":3,"deletions":0}]}' \
    $'diff --git a/_QUEUE/induced-backlog.jsonl b/_QUEUE/induced-backlog.jsonl\n+++ b/_QUEUE/induced-backlog.jsonl\n+{"id": "row-b", "state": "RUNNING"}' \
    "'job:backlog:row-b'," "'<REQUIRED tool:<kind>:<name>"
  derive_case placeholders \
    '{"body":"","headRefName":"claude/x","files":[{"path":"README.md","additions":1,"deletions":0}]}' '' \
    "'<REQUIRED job:backlog:<row-id>" "'<REQUIRED tool:<kind>:<name>"
  echo "self-test: $pass passed, $fail failed"
  [ "$fail" -eq 0 ]
}

[ "${1:-}" = "--self-test" ] && { self_test; exit $?; }

PR="${1:-}"; WANT="${2:-}"
[ -n "$PR" ] && [ -n "$WANT" ] || { echo "usage: safe_merge.sh <pr> <expected-head-sha> [--timeout S] [--interval S]" >&2; exit 2; }
shift 2
TIMEOUT="${SAFE_MERGE_TIMEOUT:-1800}"; INTERVAL="${SAFE_MERGE_INTERVAL:-20}"; NOCHECK_GRACE="${SAFE_MERGE_NOCHECK_GRACE:-120}"
while [ $# -gt 0 ]; do
  case "$1" in
    --timeout) TIMEOUT="$2"; shift 2;;
    --interval) INTERVAL="$2"; shift 2;;
    *) echo "safe_merge: unknown arg $1" >&2; exit 2;;
  esac
done
[ "${#WANT}" -ge 7 ] || die "expected sha '$WANT' is shorter than 7 characters"

jget() { python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get(sys.argv[1]) or "")' "$1"; }

# Re-read the head on every poll: a push mid-wait must refuse, not merge the new head.
check_head() {
  local view head
  view="$(gh pr view "$PR" --json headRefOid,headRefName,mergeable,state,title,url)"
  [ "$(printf '%s' "$view" | jget state)" = OPEN ] || die "PR $PR is not OPEN"
  BRANCH="$(printf '%s' "$view" | jget headRefName)"
  head="$(printf '%s' "$view" | jget headRefOid)"
  case "$head" in "$WANT"*) ;; *) die "PR $PR head is $head, expected $WANT (someone pushed; re-confirm the head)";; esac
  HEAD_SHA="$head"
  MERGEABLE="$(printf '%s' "$view" | jget mergeable)"
  TITLE="$(printf '%s' "$view" | jget title)"; URL="$(printf '%s' "$view" | jget url)"
}

# Prints SUCCESS, PENDING, or FAILURE:<names>. `gh pr checks` exits non-zero while checks are
# pending or failed, so its exit code is captured, never trusted; the JSON is the verdict.
check_state() {
  local out rc=0
  out="$(gh pr checks "$PR" --json name,state 2>/dev/null)" || rc=$?
  [ -n "$out" ] || out="[]"
  printf '%s' "$out" | python3 -c '
import json,sys
cs=json.load(sys.stdin)
if not cs: print("NOCHECKS"); sys.exit()
# SKIPPED is neutral (path-filtered jobs skip on docs-only PRs) unless every check skipped.
real=[c for c in cs if c["state"]!="SKIPPED"]
if not real: print("FAILURE:only SKIPPED checks"); sys.exit()
bad=[c["name"]+"="+c["state"] for c in real if c["state"] not in ("SUCCESS","PENDING","QUEUED","IN_PROGRESS","WAITING","REQUESTED","EXPECTED")]
if bad: print("FAILURE:"+",".join(bad)); sys.exit()
print("PENDING" if any(c["state"]!="SUCCESS" for c in real) else "SUCCESS")'
}

# GitHub health probe (jtbd-graph dep:service:github, runtime/specs/jtbd-graph-probes.json): refuse before any read or merge.
gh_probe=$(gh auth status --hostname github.com 2>&1) || die "github.com unreachable or gh not signed in: $gh_probe"
start=$(date +%s)
while :; do
  check_head
  [ "$MERGEABLE" = CONFLICTING ] && die "PR $PR is CONFLICTING with main. Resolve it on the branch (owner session only, gotcha 22); this helper never rebases."
  st="$(check_state)"
  case "$st" in
    SUCCESS) [ "$MERGEABLE" = MERGEABLE ] && break ;;  # UNKNOWN mergeable: keep waiting
    FAILURE:*) die "checks failed on $HEAD_SHA: ${st#FAILURE:}" ;;
    NOCHECKS) if [ $(( $(date +%s) - start )) -ge "$NOCHECK_GRACE" ]; then
                die "no checks reported on $HEAD_SHA after ${NOCHECK_GRACE}s (Vercel always posts one)"; fi ;;
  esac
  [ $(( $(date +%s) - start )) -ge "$TIMEOUT" ] && die "timeout after ${TIMEOUT}s: checks=$st mergeable=$MERGEABLE on $HEAD_SHA"
  echo "safe_merge: waiting (checks=$st mergeable=$MERGEABLE)"
  sleep "$INTERVAL"
done

# Cross-harness review (Zach, 2026-11-12): a PR Hermes opened (branch hermes/*) merges only with a
# Claude Code APPROVE bound to this exact head: commit status `claude-code-review` = success, set by
# scripts/claude_pr_review.py. A push makes a new head with no status, so an old approval never carries.
case "$BRANCH" in
  hermes/*)
    rv="$(gh api "repos/{owner}/{repo}/commits/$HEAD_SHA/status" --jq '[.statuses[]|select(.context=="claude-code-review")][0].state // "missing"' 2>/dev/null || echo unreadable)"
    [ "$rv" = success ] || die "PR $PR is a Hermes PR ($BRANCH) and claude-code-review on $HEAD_SHA is '$rv', not success. Run: scripts/claude_pr_review.py $PR"
    echo "safe_merge: claude-code-review success on $HEAD_SHA (Hermes PR)" ;;
esac

echo "safe_merge: head $HEAD_SHA verified, all checks SUCCESS, MERGEABLE. Merging PR $PR."
gh pr merge "$PR" --merge --match-head-commit "$HEAD_SHA"
MERGE_SHA="$(gh pr view "$PR" --json state,mergeCommit | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["state"]=="MERGED", d; print(d["mergeCommit"]["oid"])')"
echo "MERGED: PR $PR head $HEAD_SHA merge commit $MERGE_SHA"
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
# job_id / tool_id for the receipt. Best effort: a lookup failure yields the REQUIRED placeholder, never NULL.
JOB_TOOL="$( { gh pr view "$PR" --json body,headRefName,files 2>/dev/null || echo '{}'; echo '#--DIFF--'; gh pr diff "$PR" 2>/dev/null || true; } | python3 -c '
import json,re,sys
meta,_,diff=sys.stdin.read().partition("#--DIFF--")
try: m=json.loads(meta)
except ValueError: m={}
J=re.compile(r"job:backlog:([a-z0-9][a-z0-9._-]*[a-z0-9])")
jobs=sorted(set(J.findall((m.get("body") or "")+" "+(m.get("headRefName") or ""))))
if not jobs:
    infile=False
    for l in diff.splitlines():
        if l.startswith("diff --git"): infile=l.endswith("_QUEUE/induced-backlog.jsonl")
        elif infile and l.startswith("+{"):
            try: jobs.append(json.loads(l[1:])["id"])
            except (ValueError,KeyError,TypeError): pass
    jobs=sorted(set(jobs))
job="job:backlog:"+jobs[0] if len(jobs)==1 else "<REQUIRED job:backlog:<row-id>"+(" one of "+",".join(jobs) if jobs else "")+">"
sc=[(f.get("additions",0)+f.get("deletions",0),f["path"]) for f in m.get("files") or [] if f.get("path","").startswith("scripts/") and "/git-hooks/" not in f["path"]]
tool="tool:script:"+max(sc)[1].rsplit("/",1)[-1] if sc else "<REQUIRED tool:<kind>:<name>>"
print(job.replace(chr(39),"")+"\t"+tool.replace(chr(39),""))')"
JOB_ID="${JOB_TOOL%%$'\t'*}"; TOOL_ID="${JOB_TOOL#*$'\t'}"
q_title="${TITLE//\'/\'\'}"
cat <<SQL

-- decision_receipt template (fill the <...> fields, including any <REQUIRED ...> job_id/tool_id; run via Supabase execute_sql). Not written by this script.
INSERT INTO public.decision_receipt
  (receipt_id, question, horizon, stakes, mode, what_confirmed, what_unconfirmed, operator, event_at, source_repo, refs, job_id, tool_id)
VALUES (
  '$(date -u +%Y-%m-%d)--<slug>-pr${PR}--ZH',
  'Merge PR ${PR}: ${q_title}?',
  'today',            -- today | this-week | this-quarter | 1-3y
  '<low|medium|high|critical>',
  'QUICKMOVE',        -- QUICKMOVE | PLAN | COURT
  ARRAY['PR ${PR} head ${HEAD_SHA} matched expected', 'all checks SUCCESS on ${HEAD_SHA}', 'merged with --merge --match-head-commit, merge commit ${MERGE_SHA}'],
  ARRAY['<anything not verified, e.g. production deploy Ready>'],
  '<operator>',
  '${NOW}',
  'flashesofbrilliance/arcs-v9',
  ARRAY['${URL}', '${MERGE_SHA}'],
  '${JOB_ID}',  -- job_id: the backlog row this served (Sprint 5 coverage; never NULL)
  '${TOOL_ID}'  -- tool_id: the tool used (tool:<kind>:<name>); check it, the derivation is a default
);
SQL
