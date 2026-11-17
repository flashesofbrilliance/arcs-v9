#!/usr/bin/env python3
"""chrome-tab-guard: PreToolUse hook on the Claude in Chrome tools (mcp__claude-in-chrome__*).

Why (dreaming pass 14 U1, Zach's go 2026-11-17): sessions reused remembered tab ids or acted before
the tab group existed ("Tab <id> is not in Claude's tab group", "No tab available"): 10 session-times
in 14 days. The memory browser-pane-protocol named only the built-in pane, so it did not fire. This
hook makes it mechanical: until tabs_context_mcp has run in this session, every other Chrome tool is
denied with the fix in the reason.

State: one marker file per session id under $TMPDIR. Anything it cannot parse is allowed (fail-open:
a broken hook must not block the browser).
  chrome-tab-guard.py --self-test
Stdlib only.
"""
import json, os, sys, tempfile

CTX = "tabs_context_mcp"
REASON = ("Call mcp__claude-in-chrome__tabs_context_mcp with createIfEmpty: true first, and take tab ids "
          "only from its result (never from a handoff or an earlier session). Memory: browser-pane-protocol rule 5.")


def short(name):
    return (name or "").rsplit("__", 1)[-1]


def marker(sid, base=None):
    safe = "".join(ch for ch in sid if ch.isalnum() or ch in "-_")[:80]
    return os.path.join(base or tempfile.gettempdir(), "chrome-tab-guard-" + safe)


def verdict(payload, base=None):
    """Return True to deny. Marks the session once tabs_context_mcp is called."""
    sid = payload.get("session_id")
    name = short(payload.get("tool_name"))
    if not sid or not name:
        return False
    m = marker(sid, base)
    first = name
    if name == "browser_batch":
        acts = (payload.get("tool_input") or {}).get("actions") or []
        first = short(acts[0].get("name")) if acts and isinstance(acts[0], dict) else ""
    if CTX in (name, first):
        try:
            open(m, "w").close()
        except OSError:
            pass
        return False
    if name in ("list_connected_browsers", "select_browser", "switch_browser"):
        return False
    return not os.path.exists(m)


def self_test():
    base = tempfile.mkdtemp()
    s = lambda t, ti=None: {"session_id": "t1", "tool_name": "mcp__claude-in-chrome__" + t, "tool_input": ti or {}}
    steps = [
        (s("navigate", {"url": "https://x", "tabId": 1}), True),
        (s("browser_batch", {"actions": [{"name": "tabs_create_mcp", "input": {}}]}), True),
        (s("list_connected_browsers"), False),
        (s("tabs_context_mcp", {"createIfEmpty": True}), False),
        (s("navigate", {"url": "https://x", "tabId": 1}), False),
        ({"tool_name": "mcp__claude-in-chrome__navigate", "tool_input": {}}, False),
        ({"session_id": "t2", "tool_name": "mcp__claude-in-chrome__browser_batch",
          "tool_input": {"actions": [{"name": "tabs_context_mcp", "input": {}}, {"name": "navigate", "input": {}}]}}, False),
    ]
    ok = all(verdict(p, base) == want for p, want in steps)
    print("chrome-tab-guard self-test", "OK" if ok else "FAILED")
    return ok


def main():
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test() else 1)
    try:
        payload = json.load(sys.stdin)
        deny = verdict(payload)
    except Exception:
        return
    if deny:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                                 "permissionDecision": "deny",
                                                 "permissionDecisionReason": REASON}}))


if __name__ == "__main__":
    main()
