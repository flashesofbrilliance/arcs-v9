#!/usr/bin/env python3
"""mcp_tool_index_emit: the cached MCP tool index for the JTBD graph (Sprint 6, row jtbd-graph-s6-mcp-tools).

Rules are pre-registered in _PATTERNS/2026-10-20-jtbd-graph-preregistration-amendment-8.md; this file only applies them.
The index holds names and one-liners only (server, tool, fn, purpose, read|write class). It never stores an input
schema: a session loads the few tools a job needs with ToolSearch, by `fn`.

  python3 scripts/mcp_tool_index_emit.py --capture TRANSCRIPT.jsonl -o CAPTURE.json
        # build a capture from a Claude Code session transcript: replay its deferred_tools_delta attachments
        # (the deferred tool names) and take its last session_connectors_status result (server names, kinds, ids)
  python3 scripts/mcp_tool_index_emit.py CAPTURE.json        # write runtime/specs/mcp-tool-index.json
  python3 scripts/mcp_tool_index_emit.py --receipts          # write runtime/specs/mcp-tool-receipts.jsonl from the
        # gitignored receipt export (rows whose tool_id is tool:mcp:*; receipt_id, job_id, tool_id, event_at only)
  python3 scripts/mcp_tool_index_emit.py --check [CAPTURE.json]  # exit 1 when the snapshot is STALE
  python3 scripts/mcp_tool_index_emit.py --self-test
Stdlib only.
"""
import datetime, json, os, re, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
INDEX = "runtime/specs/mcp-tool-index.json"
RECEIPTS = "runtime/specs/mcp-tool-receipts.jsonl"
EXPORT = "_STATE/job-search/universe/sources/decision-receipts.json"
RULES = "_PATTERNS/2026-10-20-jtbd-graph-preregistration-amendment-8.md"
STALE_DAYS = 30
FIELDS = ("kind", "name", "server", "tool", "fn", "purpose", "class")  # the only fields a tool row may carry
READ_VERBS = {"get", "list", "search", "query", "read", "view", "fetch", "count", "inspect"}
WRITE_VERBS = set("""create update delete remove send set add apply deploy execute run merge reset rebase pause unpause
restore publish post write upsert patch put cancel trash untrash forward reply share unshare move rename import upload buy
enable disable sign revoke rotate kill stop start invalidate approve edit label unlabel mark unmark generate copy duplicate
record complete issue assign connect transfer verify confirm save submit respond give provision activate extend stage
replace retry rerequest request accept authorize change resolve spawn convert remix mint initiate test or and""".split())
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
FN_RE = re.compile(r"^mcp__(.+?)__([A-Za-z0-9_-]+)$")
KEY_RE = re.compile(r"^[a-z0-9-]+\.[A-Za-z0-9_-]+$")


class SourceDup(Exception):
    pass


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.split(":")[-1].lower()).strip("-")


def prefix_of(server):
    return server["id"] if server.get("id") else re.sub(r"[^A-Za-z0-9_-]", "_", server["name"])


def classify(tool, label):
    """Rule (c). Read only when the first verb (after the server's own name) is a read verb and no token is a write
    verb; everything else, including anything unparseable, is write."""
    toks = [t for t in re.split(r"[_\-]+", tool.lower()) if t]
    lt = [t for t in label.split("-") if t]
    while toks and lt and toks[0] == lt[0]:
        toks.pop(0); lt.pop(0)
    if not toks or toks[0] not in READ_VERBS or any(t in WRITE_VERBS for t in toks):
        return "write"
    return "read"


def capture_from_transcript(path):
    names, servers, last = set(), None, None
    use_ids = set()
    for line in open(path, encoding="utf-8"):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        a = d.get("attachment") if isinstance(d.get("attachment"), dict) else None
        if a and a.get("type") == "deferred_tools_delta":
            names |= set(a.get("addedNames") or []); names -= set(a.get("removedNames") or [])
            last = d.get("timestamp") or last
        msg = d.get("message") or {}
        for c in msg.get("content") or [] if isinstance(msg.get("content"), list) else []:
            if c.get("type") == "tool_use" and str(c.get("name", "")).endswith("session_connectors_status"):
                use_ids.add(c.get("id"))
            if c.get("type") == "tool_result" and c.get("tool_use_id") in use_ids:
                body = c.get("content")
                body = body[0].get("text") if isinstance(body, list) and body else body
                try:
                    servers = json.loads(body)["servers"]
                except (ValueError, TypeError, KeyError):
                    pass
    if servers is None:
        raise SystemExit("no session_connectors_status result in the transcript; call it in that session first")
    return {"captured_at": (last or "")[:10], "source": "Claude Code session transcript: deferred_tools_delta + "
            "session_connectors_status", "tools": sorted(n for n in names if n.startswith("mcp__")),
            "servers": [{k: s[k] for k in ("name", "id", "kind") if s.get(k)} for s in servers],
            "purposes": {}}


def build(cap):
    """Capture -> index rows. Raises SourceDup on an unresolvable label collision."""
    by_prefix = {prefix_of(s): s for s in cap["servers"]}
    used, dropped = {}, []
    for fn in cap["tools"]:
        m = FN_RE.match(fn)
        s = by_prefix.get(m.group(1)) if m else None
        if not s:
            dropped.append(fn); continue
        used.setdefault(prefix_of(s), (s, []))[1].append(m.group(2))
    labels = {}
    for p, (s, _) in used.items():
        labels.setdefault(slug(s["name"]), []).append((p, s))
    final = {}
    for lab, group in labels.items():
        if len(group) == 1:
            final[group[0][0]] = lab; continue
        own = [p for p, s in group if not UUID_RE.match(p)]
        conn = [p for p, s in group if UUID_RE.match(p)]
        if len(own) > 1 or len(conn) > 1:
            raise SourceDup(f"SOURCE-DUP label {lab!r}: {[s['name'] for _, s in group]}")
        for p in own:
            final[p] = lab
        for p in conn:
            final[p] = lab + "-claudeai"
    rows, keys = [], set()
    for p, (s, tools) in sorted(used.items(), key=lambda kv: final[kv[0]]):
        lab = final[p]
        if not re.fullmatch(r"[a-z0-9-]+", lab) or UUID_RE.match(lab):
            raise SourceDup(f"label {lab!r} for {s['name']!r} is not a stable name")
        for t in sorted(tools):
            key = f"{lab}.{t}"
            if key in keys or not KEY_RE.fullmatch(key):
                raise SourceDup(f"SOURCE-DUP or bad key {key!r}")
            keys.add(key)
            pur = (cap.get("purposes") or {}).get(f"mcp__{p}__{t}")
            pur = pur.split("\n")[0][:120] if pur else re.sub(r"[_\-]+", " ", t) + " (from name)"
            rows.append({"kind": "mcp", "name": key, "server": lab, "tool": t, "fn": f"mcp__{p}__{t}",
                         "purpose": pur, "class": classify(t, lab)})
    return rows, dropped


def write_index(cap, root=REPO):
    rows, dropped = build(cap)
    doc = {"note": f"Generated by scripts/mcp_tool_index_emit.py; never hand-edit. Rules: {RULES}. Names and one-liners "
                   "only, no input schemas. Load a tool's schema on demand with ToolSearch select:<fn>.",
           "captured_at": cap["captured_at"], "source": cap.get("source", ""), "stale_after_days": STALE_DAYS,
           "counts": {"tools": len(rows), "servers": len({r["server"] for r in rows}),
                      "write": sum(r["class"] == "write" for r in rows), "dropped_unlisted_prefix": len(dropped)},
           "tools": rows}
    with open(os.path.join(root, INDEX), "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False); f.write("\n")
    return doc, dropped


def load_index(root=REPO):
    try:
        return json.load(open(os.path.join(root, INDEX), encoding="utf-8"))
    except (OSError, ValueError):
        return None


def staleness(doc, today=None, newer=None):
    """[] when fresh; else reasons. Rule (a): older than STALE_DAYS, or a newer capture lists a tool the index lacks."""
    today = today or datetime.date.today()
    out = []
    try:
        age = (today - datetime.date.fromisoformat(doc["captured_at"])).days
        if age > STALE_DAYS:
            out.append(f"STALE: captured_at {doc['captured_at']} is {age} days old (> {STALE_DAYS})")
    except (KeyError, TypeError, ValueError):
        out.append("STALE: captured_at missing or not a date")
    if newer:
        have = {r["fn"] for r in doc.get("tools", [])}
        rows, _ = build(newer)
        miss = sorted(r["fn"] for r in rows if r["fn"] not in have)
        if miss:
            out.append(f"STALE: a newer capture lists {len(miss)} tool(s) the index lacks, e.g. {miss[:3]}")
    return out


def leaks(doc):
    """Field names outside FIELDS on any row, or schema-shaped values: the index must never cache a schema."""
    bad = []
    for r in doc.get("tools", []):
        extra = set(r) - set(FIELDS)
        if extra:
            bad.append((r.get("name"), sorted(extra)))
        if any(isinstance(v, (dict, list)) for v in r.values()) or len(str(r.get("purpose", ""))) > 120:
            bad.append((r.get("name"), "structured or long value"))
    return bad


def write_receipts(root=REPO):
    rows = json.load(open(os.path.join(root, EXPORT), encoding="utf-8"))
    out = sorted(({"receipt_id": r["receipt_id"], "job_id": r.get("job_id"), "tool_id": r["tool_id"],
                   "event_at": str(r.get("event_at", ""))[:19]}
                  for r in rows if str(r.get("tool_id") or "").startswith("tool:mcp:")),
                 key=lambda r: (r["event_at"], r["receipt_id"]))
    with open(os.path.join(root, RECEIPTS), "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return out


def self_test():
    ok = True

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond); print(("PASS " if cond else "FAIL ") + name)
    U = "19ba8754-b4f4-48bf-af48-1a5034789808"
    cap = {"captured_at": "2026-10-20", "source": "fixture", "purposes": {}, "servers": [
        {"name": "supabase", "kind": "project"}, {"name": "Supabase", "id": U, "kind": "connector"},
        {"name": "Notion", "id": "4c7edfae-9c05-4fc5-9d32-8fdad213afdc", "kind": "connector"},
        {"name": "plugin:resend:resend", "kind": "plugin"}],
        "tools": ["mcp__supabase__apply_migration", "mcp__supabase__list_tables", f"mcp__{U}__execute_sql",
                  "mcp__4c7edfae-9c05-4fc5-9d32-8fdad213afdc__notion-search",
                  "mcp__4c7edfae-9c05-4fc5-9d32-8fdad213afdc__notion-create-pages",
                  "mcp__plugin_resend_resend__get-email", "mcp__ccd_session__start_session"]}
    rows, dropped = build(cap)
    by = {r["name"]: r for r in rows}
    check("labels: own-name server keeps 'supabase', connector gets 'supabase-claudeai', no UUID in any id",
          "supabase.apply_migration" in by and "supabase-claudeai.execute_sql" in by
          and not any(UUID_RE.search(k.split(".")[0]) for k in by))
    check("unlisted prefix dropped and counted, never guessed", dropped == ["mcp__ccd_session__start_session"])
    check("server-name tokens stripped: notion-search is read, notion-create-pages is write",
          by["notion.notion-search"]["class"] == "read" and by["notion.notion-create-pages"]["class"] == "write")
    # a write tool is never classed read: every write verb, alone and hidden behind a read verb, and junk names
    trap = [v for v in sorted(WRITE_VERBS)] + [f"get_or_{v}" for v in sorted(WRITE_VERBS)] + \
           [f"list_and_{v}_items" for v in sorted(WRITE_VERBS)] + ["", "_", "do_thing", "execute_read_action",
                                                                  "get", "fetchall", "readwrite", "search-and-destroy"]
    wrong = [t for t in trap if classify(t, "x") == "read" and t not in ("get",)]
    check(f"write class: {len(trap)} trap names, none classed read except bare 'get' ({wrong[:3]})", not wrong)
    check("read verbs classify read", all(classify(f"{v}_items", "x") == "read" for v in READ_VERBS))
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "runtime/specs"))
        doc, _ = write_index(cap, tmp)
        check("no schema field leaks into the snapshot", not leaks(doc) and all(set(r) == set(FIELDS) for r in doc["tools"]))
        bad = json.loads(json.dumps(doc)); bad["tools"][0]["inputSchema"] = {"type": "object"}
        check("a leaked schema field is detected", bool(leaks(bad)))
        check("fresh snapshot is not stale", not staleness(doc, datetime.date(2026, 10, 25)))
        check("stale snapshot flagged (> 30 days)", bool(staleness(doc, datetime.date(2026, 11, 25))))
        newer = json.loads(json.dumps(cap)); newer["tools"].append("mcp__supabase__get_logs")
        check("stale snapshot flagged (newer capture has a tool the index lacks)",
              any("lacks" in x for x in staleness(doc, datetime.date(2026, 10, 21), newer)))
    dup = json.loads(json.dumps(cap)); dup["servers"].append({"name": "Supabase", "kind": "desktop"})
    dup["tools"].append("mcp__Supabase__x")
    try:
        build(dup); check("two own-name servers with one label is SOURCE-DUP", False)
    except SourceDup:
        check("two own-name servers with one label is SOURCE-DUP", True)
    print("mcp_tool_index_emit self-test: " + ("PASS" if ok else "FAIL"))
    return ok


def main(argv):
    if "--self-test" in argv:
        return 0 if self_test() else 1
    if "--capture" in argv:
        cap = capture_from_transcript(argv[argv.index("--capture") + 1])
        out = argv[argv.index("-o") + 1] if "-o" in argv else None
        s = json.dumps(cap, indent=1)
        open(out, "w").write(s) if out else print(s)
        print(f"capture: {len(cap['tools'])} mcp tool names, {len(cap['servers'])} servers, captured_at {cap['captured_at']}",
              file=sys.stderr)
        return 0
    if "--receipts" in argv:
        out = write_receipts()
        print(f"wrote {RECEIPTS}: {len(out)} receipt(s) naming an MCP tool"); return 0
    if "--check" in argv:
        doc = load_index()
        if doc is None:
            print(f"mcp-index: {INDEX} missing"); return 1
        rest = [a for a in argv[1:] if a != "--check"]
        newer = json.load(open(rest[0])) if rest else None
        probs = staleness(doc, newer=newer) + [f"LEAK {x}" for x in leaks(doc)]
        for p in probs:
            print(p)
        print(f"mcp-index: {doc['counts']['tools']} tools, {doc['counts']['servers']} servers, captured {doc['captured_at']}: "
              + ("FAIL" if probs else "OK"))
        return 1 if probs else 0
    if len(argv) == 2 and os.path.isfile(argv[1]):
        try:
            doc, dropped = write_index(json.load(open(argv[1])))
        except SourceDup as e:
            print(e); return 1
        c = doc["counts"]
        print(f"wrote {INDEX}: {c['tools']} tools on {c['servers']} servers ({c['write']} write), "
              f"{c['dropped_unlisted_prefix']} dropped (prefix not a listed server)")
        return 0
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
