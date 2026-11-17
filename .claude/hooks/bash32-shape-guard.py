#!/usr/bin/env python3
"""bash32-shape-guard: PreToolUse hook on Bash for the shapes macOS bash 3.2 refuses.

Why (dreaming pass 5 F1, Zach's go 2026-11-16 "add a guard hook"): the harness refuses some commands
on bash 3.2.57 ("this shell is too old to run it reliably", exit 126). 50+ hits in 30+ sessions in
the scan windows, the largest error cluster. The refusal names no fix, so each hit costs a retry.
This hook catches the two shapes that are unambiguous and says what to do instead.

Deliberately narrow (a guard that blocks working commands is worse than the retry it saves):
  - bash arrays: `name=( ... )`, `${name[...]}`, `declare -a`
  - a `$( ... )` nested inside another `$( ... )`
Backticks and long double-quoted text are NOT matched: they often run fine (this session's own PR
bodies used escaped backticks), so matching them would deny good commands.

Fix it names: write the logic to a script file in the scratchpad and run that file. Memory:
long-inline-shell-goes-in-a-script-file. Fail-open on input it cannot parse.
  bash32-shape-guard.py --self-test
Stdlib only.
"""
import json, re, sys

REASON = ("bash 3.2 shape (array or nested $(...)): the harness refuses these on macOS bash 3.2. "
          "Write the logic to a script file in the scratchpad (python3 or sh) and run the file, or "
          "split it into plain one-level commands. Memory: long-inline-shell-goes-in-a-script-file.")

ARRAY = re.compile(r"(^|[\s;&|(])[A-Za-z_][A-Za-z0-9_]*=\(|\$\{[A-Za-z_][A-Za-z0-9_]*\[|\bdeclare\s+-[aA]\b")


def strip_quoted_heredocs(cmd):
    """Drop the bodies of quoted heredocs (<<'EOF' ... EOF): the shell never parses them."""
    out, skip = [], None
    for line in cmd.split("\n"):
        if skip is not None:
            if line.strip() == skip:
                skip = None
            continue
        out.append(line)
        m = re.search(r"<<-?\s*'([A-Za-z_]+)'", line)
        if m:
            skip = m.group(1)
    return "\n".join(out)


def strip_single_quotes(cmd):
    return re.sub(r"'[^']*'", "''", cmd)


def nested_subst(cmd):
    depth, i = 0, 0
    while i < len(cmd):
        if cmd.startswith("$(", i) and not cmd.startswith("$((", i):
            depth += 1
            if depth >= 2:
                return True
            i += 2
            continue
        if cmd[i] == ")" and depth:
            depth -= 1
        i += 1
    return False


def verdict(command):
    c = strip_single_quotes(strip_quoted_heredocs(command))
    return bool(ARRAY.search(c)) or nested_subst(c)


def self_test():
    cases = [
        ("files=(a b c); echo ${files[0]}", True),
        ("echo \"$(git log -1 --format=%h $(git merge-base HEAD origin/main))\"", True),
        ("declare -a xs", True),
        ("for p in 1 2; do gh pr view $p; done", False),
        ("git commit -m \"$(cat msg.txt)\"", False),
        ("python3 - <<'EOF'\nxs=(1,2)\nprint(f'{xs[0]}')\nEOF", False),
        ("echo 'arr=(1 2) and $(a $(b))'", False),
        ("echo $((1 + 2))", False),
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
