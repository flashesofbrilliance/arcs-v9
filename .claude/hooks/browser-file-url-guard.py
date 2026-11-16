#!/usr/bin/env python3
"""browser-file-url-guard: PreToolUse hook on the built-in browser's navigate, preview_start and browser_batch.

Why (dreaming pass 11 N1, Zach's go 2026-11-16): a file:// tab blocks the page tools ("This tab shows
a local file, not a web page"). The memory preview-file-tab-page-tools-dont-act existed and still did
not fire in 11 sessions. This hook makes the memory mechanical: it denies a file:// url before the
browser opens it.

Protocol: read the tool call as JSON on stdin; to refuse, print a PreToolUse deny and exit 0.
Anything it cannot parse is allowed (fail-open: this runs on the main session, and a broken hook must
not block the browser).
  browser-file-url-guard.py --self-test
Stdlib only.
"""
import json, sys

REASON = ("file:// tabs block the page tools. Serve the folder instead: python3 -m http.server <port> "
          "from its directory (run in the background), then navigate to http://127.0.0.1:<port>/<file>; "
          "or Read the file. Memory: preview-file-tab-page-tools-dont-act.")


def urls(tool_input):
    out = [tool_input.get("url", "")]
    for a in tool_input.get("actions", []) or []:
        if isinstance(a, dict):
            out.append((a.get("input") or {}).get("url", ""))
    return [u for u in out if isinstance(u, str)]


def verdict(payload):
    ti = payload.get("tool_input") or {}
    return any(u.strip().lower().startswith("file:") for u in urls(ti))


def self_test():
    cases = [
        ({"tool_input": {"url": "file:///private/tmp/x.html"}}, True),
        ({"tool_input": {"url": "http://127.0.0.1:8000/x.html"}}, False),
        ({"tool_input": {"actions": [{"name": "navigate", "input": {"url": "FILE:///a.html"}}]}}, True),
        ({"tool_input": {"actions": [{"name": "computer", "input": {"action": "screenshot"}}]}}, False),
        ({"tool_input": {"url": "back"}}, False),
    ]
    ok = all(verdict(p) == want for p, want in cases)
    print("browser-file-url-guard self-test", "OK" if ok else "FAILED")
    return ok


def main():
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test() else 1)
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    if verdict(payload):
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                                 "permissionDecision": "deny",
                                                 "permissionDecisionReason": REASON}}))


if __name__ == "__main__":
    main()
