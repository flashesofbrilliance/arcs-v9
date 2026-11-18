#!/usr/bin/env python3
"""bash32-shape-guard: PreToolUse hook on Bash for the shapes macOS bash 3.2 refuses.

Why (dreaming pass 5 F1, Zach's go 2026-11-16 "add a guard hook"): the harness refuses some commands
on bash 3.2.57 ("this shell is too old to run it reliably", exit 126). It is the largest error
cluster in the scans, and the refusal names no fix, so each hit costs a retry.

Seam (2026-11-18, dreaming pass 15 ruling, Zach: "retire them"): the first version denied bash arrays
and nested $(...). Measured on the week before it shipped (13,788 Bash calls, 77 refusals), those
rules denied 77 commands that ran fine (mostly ${PIPESTATUS[0]} and array indexing) and caught 2
refusals. They were the wrong shape and are retired. The refusals are heredoc shapes:
  - a heredoc inside $(...) (`--body "$(cat <<'EOF'`) whose body has a `#` line, a backtick, or
    runs past 1500 chars. Fix: write the text to a file and pass it (--body-file F, -F F).
  - a quoted heredoc whose marker line goes on with `;` (`<<'EOF' 2>&1 | tail; git log`) and whose
    terminator is the last line. Fix: end the heredoc, then run the next command on its own line.
On that week these deny 59 calls, 54 of which the harness refused (catching 54 of 77). A guard that
blocks working commands is worse than the retry it saves, so keep it that narrow and re-measure
before adding a shape (the scan scripts are in the pass 15 ruling).

Fail-open on input it cannot parse.
  bash32-shape-guard.py --self-test
Stdlib only.
"""
import json, re, sys

REASON = ("bash 3.2 heredoc shape: the harness refuses a heredoc inside $(...) with a long or "
          "markdown body, and a heredoc whose marker line goes on with ';'. Write the text to a "
          "file in the scratchpad and pass it (gh pr create --body-file F, git commit -F F), or "
          "end the heredoc and put the next command on its own line. "
          "Memory: long-inline-shell-goes-in-a-script-file.")
SUBST_HD = re.compile(r"\$\(\s*cat\s+<<-?\s*(['\"]?)([A-Za-z_]+)\1[^\n]*")
QUOTED_HD = re.compile(r"<<-?\s*(['\"])([A-Za-z_]+)\1([^\n]*)")


def heredoc_body(cmd, m):
    """Body after the marker line, and the lines after the terminator (None if no terminator)."""
    tag, rest, body = m.group(2), cmd[m.end():].split("\n")[1:], []
    for i, line in enumerate(rest):
        if line.strip() == tag:
            return "\n".join(body), rest[i + 1:]
        body.append(line)
    return "\n".join(body), None


def verdict(cmd):
    for m in SUBST_HD.finditer(cmd):
        body, _ = heredoc_body(cmd, m)
        if re.search(r"^\s*#", body, re.M) or "`" in body or len(body) > 1500:
            return True
    for m in QUOTED_HD.finditer(cmd):
        if ";" in m.group(3):
            _, after = heredoc_body(cmd, m)
            if after is None or not "\n".join(after).strip():
                return True
    return False


def self_test():
    cases = [
        # heredoc in $(...) with a markdown body: refused 24 of 28 times in the 2026-11-18 scan
        ("gh pr create --title t --body \"$(cat <<'EOF'\n## Why\nbecause\nEOF\n)\"", True),
        ("gh pr create --title t --body \"$(cat <<'EOF'\nuse `x` here\nEOF\n)\"", True),
        ("gh pr create --title t --body \"$(cat <<'EOF'\nshort plain body\nEOF\n)\"", False),
        # marker line goes on with ';' and the terminator ends the command: 43 of 46
        ("git commit -q -F - <<'EOF' 2>&1 | tail -15; git log --oneline -1\nfeat: x\nEOF", True),
        ("git commit -q -F - <<'EOF' ; echo rc=$?\nfeat: x\nEOF", True),
        # same marker without ';', or with commands after the terminator: ran fine
        ("git commit -q -F - <<'EOF' 2>&1 | tail -1\nfeat: x\nEOF", False),
        ("git commit -q -F - <<'EOF' 2>&1 | tail -1; true\nfeat: x\nEOF\ngit log --oneline -1", False),
        ("python3 - <<'EOF'\nprint(1); print(2)\nEOF", False),
        # retired shapes: these ran fine on bash 3.2 and must not be denied
        ("python3 x.py | tail -25; echo rc=${PIPESTATUS[0]}", False),
        ("files=(a b c); echo ${files[0]}", False),
        ("echo \"$(git log -1 --format=%h $(git merge-base HEAD origin/main))\"", False),
        ("scripts/safe_merge.sh 2313 $(git rev-parse HEAD)", False),
    ]
    bad = [(c, w) for c, w in cases if verdict(c) != w]
    for c, w in bad:
        print("WRONG", repr(c), "want", w)
    print("bash32-shape-guard self-test", "OK" if not bad else "FAILED")
    return not bad


def main():
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test() else 1)
    try:
        payload = json.load(sys.stdin)
        command = (payload.get("tool_input") or {}).get("command", "")
    except Exception:
        return
    if isinstance(command, str) and verdict(command):
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                                 "permissionDecision": "deny",
                                                 "permissionDecisionReason": REASON}}))


if __name__ == "__main__":
    main()
