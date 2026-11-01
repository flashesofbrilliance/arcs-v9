#!/usr/bin/env python3
"""cruise-control-bash-guard: a PreToolUse hook on Bash, scoped to the cruise-control agent.

Why: the agent's "never merge, publish, send, push or write" rule was only described in its prompt,
and a control owned by the agent it polices is captured (memory `control-integrity-described-vs-wired`,
manual _PATTERNS/2026-11-01-harness-flight-manual.md). This hook is the not-the-agent owner: it denies
the one-way-door commands and file writes before Bash runs them.

Protocol (Claude Code hooks): read the tool call as JSON on stdin; to refuse, print
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "..."}}
and exit 0. Allowed commands print nothing. Fail-closed: input it cannot parse is denied, because this
hook runs only inside the cruise-control agent, never on the main session.

Limits (stated, not hidden): it reads the command text, so an obfuscated command (base64, eval of a
variable) can slip past; a deny-list is a tripwire, not a sandbox. The read-only allow path is the
agent prompt's command list.

  cruise-control-bash-guard.py --self-test
Stdlib only.
"""
import json, re, sys

# (pattern, reason). Matched against each shell segment split on ; && || | and newlines.
DENY = [
    (r"\bgh\s+pr\s+(merge|comment|review|close|edit|ready|create)\b", "gh pr write (merge, comment, review, close, edit, create) is a one-way door"),
    (r"\bgh\s+(workflow\s+run|run\s+(rerun|cancel)|release|issue\s+(create|comment|close|edit)|repo\s+edit|api\b.*-X\s*(POST|PATCH|PUT|DELETE))", "gh write to GitHub"),
    (r"\bgit\s+(push|commit|merge|rebase|reset|stash|checkout|switch|cherry-pick|revert|tag|am|apply|clean|rm|mv|restore|worktree\s+(add|remove|prune)|branch\s+-[dDmM])\b", "git write to a ref, index or working tree"),
    (r"\bscripts/safe_merge\.sh\b(?!\s+--self-test\b)", "safe_merge.sh merges; only --self-test is allowed here"),
    (r"\bscripts/(merge_train|ship_docs|sync_worktree)\.sh\b", "merge or push helper"),
    (r"\b(phosphor_build\.py\s+--release|handoff_fold\.py\s+molt|oracle\.py\s+next|backlog_append\.py)\b", "writes a release, handoff, counter or backlog row"),
    (r"\b(pulse|lattice_drift_check)\.py\b", "appends a receipt under _INBOX/"),
    (r"--(write|regenerate|release|export|fix|apply)\b", "a writing flag"),
    (r"\b(supabase|psql|vercel|curl\s+.*-X\s*(POST|PATCH|PUT|DELETE)|npm\s+(publish|install|i)\b)", "a write to an external service or the dependency tree"),
    (r"(^|[^<>&0-9])>>?\s*(?!/dev/null\b|&)", "a shell redirect writes a file"),
    (r"\b(tee|rm|mv|cp|mkdir|touch|chmod|ln|dd|truncate)\b", "a file-writing command"),
    (r"\bsed\s+(-[a-zA-Z]*i|--in-place)", "sed -i edits in place"),
    (r"\b(python3?|node|perl|ruby)\s+-(c|e)\b", "inline interpreter code can write anything"),
]
DENY = [(re.compile(p), why) for p, why in DENY]


def check(cmd):
    """-> reason string when the command must be refused, else None."""
    for seg in re.split(r"\n|;|&&|\|\|", cmd):
        seg = seg.strip()
        if not seg:
            continue
        for rx, why in DENY:
            if rx.search(seg):
                return f"cruise-control is read-only: {why} (`{seg[:80]}`). Disengage and hand Zach the approvals ledger."
    return None


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                             "permissionDecision": "deny", "permissionDecisionReason": reason}}))


def self_test():
    bad = ["gh pr merge 1919 --merge", "git push origin main", "git commit -am x", "scripts/safe_merge.sh 1919 abc1234",
           "scripts/merge_train.sh --lock 1 2", "python3 scripts/pulse.py", "python3 scripts/oracle.py next adr",
           "echo hi > notes.md", "git status && git push", "python3 scripts/tool_catalog_emit.py --write",
           "supabase db query --linked 'select 1'", "sed -i '' s/a/b/ f", "python3 -c 'open(\"x\",\"w\")'",
           "gh run rerun 123", "gh api repos/o/r/pulls/1/merge -X PUT", "cat a | tee b", "rm -rf _STATE"]
    good = ["git fetch -q origin main", "git worktree list", "git log origin/main --oneline --since='48 hours ago'",
            "python3 scripts/approvals_ledger.py", "python3 scripts/backlog_status_check.py --check --gh",
            "python3 scripts/backlog_graph.py --top 5", "python3 scripts/readiness_packet.py some-row",
            "python3 scripts/open_loops.py --summary", "scripts/project_skills_drift.sh", "scripts/safe_merge.sh --self-test",
            "gh pr list --state open --json number", "gh pr view 1919 --json state", "git diff --stat origin/main",
            "python3 scripts/approvals_ledger.py 2>/dev/null", "ls _PATTERNS", "grep -n x file 2>&1 | head"]
    ok = 0
    for c in bad:
        hit = check(c) is not None
        ok += hit
        print(("PASS deny  " if hit else "FAIL allow ") + c)
    for c in good:
        hit = check(c) is None
        ok += hit
        print(("PASS allow " if hit else "FAIL deny  ") + c + ("" if hit else "  <- " + check(c)))
    total = len(bad) + len(good)
    print(f"self-test: {ok}/{total}")
    return ok == total


def main():
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test() else 1)
    try:
        data = json.load(sys.stdin)
        cmd = (data.get("tool_input") or {}).get("command")
        if not isinstance(cmd, str):
            raise ValueError("no command")
    except Exception as e:  # fail-closed: this hook only runs inside the read-only agent
        deny(f"cruise-control bash guard could not read the tool call ({e}); refused.")
        return
    reason = check(cmd)
    if reason:
        deny(reason)


if __name__ == "__main__":
    main()
