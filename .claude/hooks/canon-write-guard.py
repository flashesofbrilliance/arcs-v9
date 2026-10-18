#!/usr/bin/env python3
"""canon-write-guard: a PreToolUse hook for Claude's Edit, Write and MultiEdit tools. PROPOSAL (draft PR).

Why: canon is changed by a declared, receipted decision (ROM primitive 7, write-lock), not by a stray
edit. The rules live in runtime/specs/canon-paths.json, each citing where the repo says so. Four classes:
  deny         block the edit
  ask          ask Zach to confirm, with the reason
  insert_only  allow only edits that keep every existing byte (append or insert); deny rewrites
  mint_only    an existing file is denied (mint a new file); a new file asks

Protocol (Claude Code hooks): read the tool call as JSON on stdin; to decide, print one JSON object
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny|ask", "permissionDecisionReason": "..."}}
and exit 0. Printing nothing and exiting 0 leaves the normal permission flow alone. Fail-open: any
internal error, unreadable manifest or malformed input exits 0 with a note on stderr, so a bug here
can never stop unrelated work. CANON_GUARD=off in the launching environment disables it.

Limits (stated, not hidden): it sees only Claude's Edit, Write and MultiEdit tools, not Python or shell
writes; and the hooks docs do not say how bypass permission modes treat a hook's deny.

  canon-write-guard.py --self-test    synthetic project in a temp dir; touches nothing else
Stdlib only.
"""
import fnmatch, json, os, re, sys, tempfile

MANIFEST_REL = os.path.join("runtime", "specs", "canon-paths.json")


def project_root():
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def to_regex(glob):
    """** crosses folders, * does not."""
    out, i = "", 0
    while i < len(glob):
        if glob.startswith("**", i):
            out += ".*"; i += 2
        elif glob[i] == "*":
            out += "[^/]*"; i += 1
        elif glob[i] == "?":
            out += "[^/]"; i += 1
        else:
            out += re.escape(glob[i]); i += 1
    return re.compile("^" + out + "$")


def relpath(root, p):
    if not p:
        return None
    ap = os.path.abspath(p if os.path.isabs(p) else os.path.join(root, p))
    root = os.path.abspath(root)
    if ap != root and not ap.startswith(root + os.sep):
        return None
    return os.path.relpath(ap, root).replace(os.sep, "/")


def match_rule(rules, rel):
    for r in rules:
        if to_regex(r["glob"]).match(rel) and not any(to_regex(e).match(rel) for e in r.get("except", [])):
            return r
    return None


def decide(rule, tool, ti, exists, current):
    """-> (decision, reason) or None. `current` is the existing file text (or None)."""
    c, why = rule["class"], rule["why"]
    if c == "deny":
        return "deny", f"Canon file, edit refused. {why} Propose the change in a draft PR or ask Zach; do not edit it in place."
    if c == "ask":
        return "ask", f"Canon file. {why} Confirm this edit was decided; record its receipt id."
    if c == "mint_only":
        if exists:
            return "deny", f"Mint-only canon. {why} Create a new file for a new version instead of editing this one."
        return "ask", f"New canon artifact. {why}"
    if c == "insert_only":
        if not exists:
            return None
        if tool == "Write":
            new = ti.get("content", "")
            return None if (current or "") in new else (
                "deny", f"Append-only record. {why} This Write would remove or rewrite existing text; only insertions are allowed.")
        edits = ti.get("edits") if tool == "MultiEdit" else [ti]
        for e in edits or []:
            old, new = e.get("old_string", ""), e.get("new_string", "")
            if old and old not in new:
                return "deny", f"Append-only record. {why} This edit replaces existing text; keep it and add after or before it."
        return None
    return None


def run(stdin_text, root, env):
    if env.get("CANON_GUARD", "").lower() == "off":
        return None
    try:
        call = json.loads(stdin_text)
    except ValueError:
        return None
    tool = call.get("tool_name")
    if tool not in ("Edit", "Write", "MultiEdit"):
        return None
    ti = call.get("tool_input") or {}
    rel = relpath(root, ti.get("file_path"))
    if rel is None:
        return None
    try:
        rules = json.load(open(os.path.join(root, MANIFEST_REL)))["rules"]
    except (OSError, ValueError, KeyError):
        sys.stderr.write("canon-write-guard: manifest unreadable, allowing\n")
        return None
    rule = match_rule(rules, rel)
    if not rule:
        return None
    fp = os.path.join(root, rel)
    exists = os.path.exists(fp)
    current = None
    if exists and rule["class"] == "insert_only":
        try:
            current = open(fp, encoding="utf-8", errors="replace").read()
        except OSError:
            return None
    return decide(rule, tool, ti, exists, current)


def emit(result):
    if not result:
        return
    d, reason = result
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": d,
                                             "permissionDecisionReason": reason}}))


def self_test():
    ok = True

    def check(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok = ok and cond

    with tempfile.TemporaryDirectory() as d:
        w = lambda p, t: (os.makedirs(os.path.dirname(os.path.join(d, p)), exist_ok=True), open(os.path.join(d, p), "w").write(t))
        real = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", MANIFEST_REL)))
        w(MANIFEST_REL, json.dumps(real))
        for p in ("_CANON/ordinals/ARCS-Glossary-v0.1.md", "_CANON/ordinals/README.md", "_CANON/ARCS-Canon-v2-0-Complete.md",
                  "_CANON/Tao-of-ARCS.md", "_CANON/index.md", "WORLD.md", "CLAUDE.md", "AGENTS.md", "src/app/page.tsx"):
            w(p, "line one\nline two\n")
        w("_SEEDS/ledger.jsonl", '{"a":1}\n{"b":2}\n')
        D = lambda tool, **ti: run(json.dumps({"tool_name": tool, "tool_input": ti}), d, {})
        dec = lambda r: r[0] if r else None
        P = lambda p: os.path.join(d, p)

        check("an ordinary file is untouched", D("Edit", file_path=P("src/app/page.tsx"), old_string="one", new_string="1") is None)
        check("CLAUDE.md and AGENTS.md are not canon here", D("Edit", file_path=P("CLAUDE.md"), old_string="one", new_string="1") is None
              and D("Write", file_path=P("AGENTS.md"), content="x") is None)
        check("frozen canon v2.0 is denied", dec(D("Edit", file_path=P("_CANON/ARCS-Canon-v2-0-Complete.md"), old_string="one", new_string="1")) == "deny")
        check("CANONICAL doctrine asks", dec(D("Edit", file_path=P("_CANON/Tao-of-ARCS.md"), old_string="one", new_string="1")) == "ask")
        check("the canon index is exempt", D("Edit", file_path=P("_CANON/index.md"), old_string="one", new_string="1") is None)
        check("WORLD.md asks", dec(D("Write", file_path=P("WORLD.md"), content="new")) == "ask")
        check("existing ordinal is denied (mint, do not edit)", dec(D("Edit", file_path=P("_CANON/ordinals/ARCS-Glossary-v0.1.md"), old_string="one", new_string="1")) == "deny")
        check("new ordinal asks", dec(D("Write", file_path=P("_CANON/ordinals/ARCS-Glossary-v0.2.md"), content="x")) == "ask")
        check("ordinals README is exempt", D("Edit", file_path=P("_CANON/ordinals/README.md"), old_string="one", new_string="1") is None)
        check("append to an insert-only ledger via Write is allowed", D("Write", file_path=P("_SEEDS/ledger.jsonl"), content='{"a":1}\n{"b":2}\n{"c":3}\n') is None)
        check("rewriting the ledger via Write is denied", dec(D("Write", file_path=P("_SEEDS/ledger.jsonl"), content='{"a":9}\n')) == "deny")
        check("an Edit that keeps the old text is allowed", D("Edit", file_path=P("_SEEDS/ledger.jsonl"), old_string='{"b":2}\n', new_string='{"b":2}\n{"c":3}\n') is None)
        check("an Edit that replaces old text is denied", dec(D("Edit", file_path=P("_SEEDS/ledger.jsonl"), old_string='{"b":2}', new_string='{"b":3}')) == "deny")
        check("MultiEdit with one replacing edit is denied", dec(D("MultiEdit", file_path=P("_SEEDS/ledger.jsonl"), edits=[
            {"old_string": '{"a":1}\n', "new_string": '{"a":1}\n{"z":0}\n'}, {"old_string": '{"b":2}', "new_string": "X"}])) == "deny")
        check("creating a new insert-only file is allowed", D("Write", file_path=P("_STATE/falsification-ledger.jsonl"), content="x\n") is None)
        check("a path outside the project is ignored", D("Edit", file_path="/etc/hosts", old_string="a", new_string="b") is None)
        check("a non-edit tool is ignored", run(json.dumps({"tool_name": "Bash", "tool_input": {"command": "echo hi"}}), d, {}) is None)
        check("CANON_GUARD=off disables it", run(json.dumps({"tool_name": "Edit", "tool_input": {"file_path": P("WORLD.md"), "old_string": "a", "new_string": "b"}}), d, {"CANON_GUARD": "off"}) is None)
        check("malformed stdin fails open", run("{not json", d, {}) is None)
        os.remove(os.path.join(d, MANIFEST_REL))
        check("a missing manifest fails open", D("Edit", file_path=P("WORLD.md"), old_string="a", new_string="b") is None)
    print("canon-write-guard self-test:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    try:
        emit(run(sys.stdin.read(), project_root(), os.environ))
    except Exception as e:  # fail-open: never let a bug here stop unrelated work
        sys.stderr.write(f"canon-write-guard: internal error, allowing: {e}\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
