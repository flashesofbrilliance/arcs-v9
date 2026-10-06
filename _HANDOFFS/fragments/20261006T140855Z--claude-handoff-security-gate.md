<!--
branch: claude/handoff-security-gate
head: 6a29d549
created_at: 2026-10-06T14:08:55Z
-->
> **Security-review gate stops failing re-runs red; a real API error still fails.** #909 (`6a29d549`), merged with
> `--merge` on Zach's yes. Receipt `2026-10-06--security-gate-dedupe-skip-pr909--ZH`.

## Shipped
- **#909:** `scripts/security_review_gate.sh` reads the action's `results-file` output (its scan step sets it first,
  so empty = scan never started) plus the cache-restored `.claudecode-marker/marker.json`. Empty + marker for this PR
  = `::notice` "already scanned at <sha>" and pass; empty + no marker = fail; scan ran = all #881 checks unchanged.
  Live proof: run 37474229559 (fresh, outcome=success, passed) and 37476233291 (skipped, notice, passed).
- The scan on #909 found 2 real bugs in the first draft, both fixed: a committed marker.json could fake a pass (now
  only an untracked marker whose `pr_number` matches), and marker fields went into a workflow command (now hex/digits only).

## Open (next session)
1. Broken-key path not run live (secret untouched); covered by the action code plus run 37400262799.
2. The `security-review` label never rescans (cache key is per PR): chip task_d4f6708c is running in its own session
   (`run-every-commit` on labeled; costs API budget, needs Zach's yes).

## Lessons
- Read a composite action's outputs for the signal: an output set on the first line of a step is a step-ran flag.
- Run the security scan on a change to the security gate: it caught the bypass in this one.
