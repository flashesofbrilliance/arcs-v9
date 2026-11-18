#!/usr/bin/env python3
"""commit-push-chain-nudge: PostToolUse / PostToolUseFailure hook on Bash, after an unchecked commit.

Why (dreaming pass 15 V3, Zach 2026-11-18): a commit refused by pre-commit was piped (`| grep`) or
followed by `;` into `git push` and `gh pr create` in the same call, so the push sent nothing and gh
failed with "No commits between main and claude/...". 3 calls in 2 sessions; memory
pipe-to-tail-hides-failed-step-in-and-chain states the rule and fired in none of them.

Not a deny (Zach's ruling on the measurement): that shape is common and almost always fine. A deny
would have blocked 981 Bash calls in the week scanned to save the 3. So this runs after the call and
speaks only when the command has the shape AND its output shows the commit failed. Then it tells the
model the push or PR carried nothing and to fix the commit first.

The shape: a `git commit` followed later by `git push` or `gh pr create`, where the push can run after
a failed commit (a `;`, newline or `||` between them, or a pipe on the commit without
`set -o pipefail`). Quoted text and heredoc bodies are ignored. Fail-open.
  commit-push-chain-nudge.py --self-test
Stdlib only.
"""
import json, re, sys

NOTE = ("The commit in this command failed (see the output), but the push or PR step ran anyway "
        "because a ';', newline or pipe sat between them, so it carried nothing. Fix and re-run the "
        "commit, check it landed (git log -1), then push. Chain commit, push and PR with &&. "
        "Memory: pipe-to-tail-hides-failed-step-in-and-chain.")
FAILED = re.compile(r"No commits between|✖|pre-commit.*(fail|block)|hook.*(failed|blocked)", re.I)
HD = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_]+)\1")
COMMIT = re.compile(r"\bgit\s+(?:-C\s+\S+\s+)?commit\b")
PUSH = re.compile(r"\bgit\s+(?:-C\s+\S+\s+)?push\b|\bgh\s+pr\s+create\b")


def strip(cmd):
    """Drop heredoc bodies and terminators, then the contents of quoted strings."""
    out, skip = [], None
    for line in cmd.split("\n"):
        if skip is not None:
            if line.strip() == skip:
                skip = None
            continue
        out.append(line)
        m = HD.search(line)
        if m:
            skip = m.group(2)
    s, res, q, i = "\n".join(out), [], None, 0
    while i < len(s):
        ch = s[i]
        if q is None:
            if ch in "'\"":
                q = ch
            res.append(ch)
        elif ch == "\\" and q == '"':
            i += 1
        elif ch == q:
            q = None
            res.append(ch)
        i += 1
    return "".join(res)


def verdict(command):
    s = strip(command)
    c = COMMIT.search(s)
    if not c:
        return False
    p = PUSH.search(s, c.end())
    if not p:
        return False
    between = s[c.end():p.start()]
    if re.search(r";|\n|\|\|", between):
        return True
    own_pipeline = between.split("&&", 1)[0]
    if re.search(r"(?<!\|)\|(?![|&])", own_pipeline) and "pipefail" not in s[:c.start()]:
        return True
    return False


def self_test():
    cases = [
        ("git commit -q -m x | grep FAIL; git push -q; gh pr create --fill", True),
        ("git commit -q -m x > log; echo $?; git push origin HEAD", True),
        ("git commit -q -F - <<'EOF'\nfeat: x\nEOF\ngit push -q -u origin HEAD", True),
        ("git commit -q -m x || true && git push", True),
        ("git add -A && git commit -q -m x && git push -q -u origin HEAD && gh pr create --fill", False),
        ("git commit -q -F - <<'EOF' && git push -q\nfeat: x; mention gh pr create\nEOF", False),
        ("set -o pipefail; git commit -q -m x 2>&1 | tail -2 && git push", False),
        ("git commit -q -m 'docs: run git push; then gh pr create'", False),
        ("git commit -q -m x 2>&1 && git push", False),
        ("git push -q; git commit -m x", False),
        ("git log --oneline -1; git push", False),
    ]
    bad = [(c, w) for c, w in cases if verdict(c) != w]
    shape = "git commit -q -m x 2>&1 | grep FAIL; git push -q; gh pr create --fill"
    out_cases = [
        ({"hook_event_name": "PostToolUseFailure", "tool_input": {"command": shape},
          "error": "Exit code 1\n✖ gate failed\npull request create failed: No commits between main and x"}, True),
        ({"hook_event_name": "PostToolUse", "tool_input": {"command": shape},
          "tool_response": {"stdout": "[x 1a2b3c] feat\n", "stderr": ""}}, False),
        ({"hook_event_name": "PostToolUseFailure", "tool_input": {"command": "git log; git push"},
          "error": "No commits between main and x"}, False),
    ]
    for p, want in out_cases:
        if (note_for(p) is not None) != want:
            bad.append((p["tool_input"]["command"] + " / " + p["hook_event_name"], want))
    for c, w in bad:
        print("WRONG", repr(c), "want", w)
    print("commit-push-chain-nudge self-test", "OK" if not bad else "FAILED")
    return not bad


def note_for(payload):
    """The note to add, or None. Speaks only on the shape plus a sign the commit failed."""
    command = (payload.get("tool_input") or {}).get("command", "")
    if not isinstance(command, str) or not verdict(command):
        return None
    resp = payload.get("tool_response")
    text = str(payload.get("error") or "")
    if isinstance(resp, dict):
        text += "\n" + str(resp.get("stdout") or "") + "\n" + str(resp.get("stderr") or "")
    elif resp:
        text += "\n" + str(resp)
    return NOTE if FAILED.search(text) else None


def main():
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test() else 1)
    try:
        payload = json.load(sys.stdin)
        note = note_for(payload)
    except Exception:
        return
    if note:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": payload.get("hook_event_name") or "PostToolUse",
            "additionalContext": note}}))


if __name__ == "__main__":
    main()
