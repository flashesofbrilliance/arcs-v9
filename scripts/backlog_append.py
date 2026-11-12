#!/usr/bin/env python3
"""backlog_append.py: add rows to _QUEUE/induced-backlog.jsonl without rewriting the file. Stdlib, no model calls.

Why: ledger edits done by rewriting the whole file can silently drop lines another session added. This script
only ever appends new lines, in one write, under an exclusive lock, after the batch passes validation.

Each input row must:
  - parse as one JSON object per line (blank lines are skipped)
  - carry a non-empty `id`, `state` and `jtbd`
  - have an id that is not already in the file and not repeated in the batch
  - name only ids in `depends_on` and `unblocks` that exist in the file or in the batch
  - use a `state` from runtime/specs/backlog-status.json (the enum backlog_graph and the pre-commit gate read)
  - not carry the legacy `status` key, and carry claimed_by + claimed_at when RUNNING (backlog_status_check rules)

All or nothing: one failure and nothing is written. After a write (or with --dry-run, against a temporary copy)
it runs scripts/backlog_graph.py --json and prints the findings and waves that mention the new ids.
It never edits, reorders or removes an existing row. Fates stay human (NOTOMATION).

usage:
  backlog_append.py --rows new.jsonl [--file F] [--dry-run] [--today YYYY-MM-DD]
  cat new.jsonl | backlog_append.py [--dry-run]
  backlog_append.py --self-test        fixtures in a temp dir: bad JSON, duplicate id, dangling dependency, happy path
"""
import argparse, fcntl, json, os, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FILE = ROOT / "_QUEUE" / "induced-backlog.jsonl"
SPEC = ROOT / "runtime" / "specs" / "backlog-status.json"
GRAPH = ROOT / "scripts" / "backlog_graph.py"
REQUIRED = ("id", "state", "jtbd")


def states():
    return set(json.loads(SPEC.read_text())["states"])


def ids_of(field):
    """depends_on / unblocks as a list of ids; a bare string is split the way backlog_graph.deps_of splits it."""
    if not field:
        return []
    if isinstance(field, str):
        field = re.split(r"[,\s]+", field)
    return [str(x).strip() for x in field if str(x).strip()]


def existing_ids(text):
    out = set()
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if isinstance(r, dict) and r.get("id"):
            out.add(r["id"])
    return out


def parse_batch(text):
    """Return (rows, errors). Each row is (input line number, dict)."""
    rows, errs = [], []
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except ValueError as e:
            errs.append(f"input line {n}: not valid JSON ({e})")
            continue
        if not isinstance(r, dict):
            errs.append(f"input line {n}: a row must be a JSON object, got {type(r).__name__}")
            continue
        rows.append((n, r))
    return rows, errs


def validate(rows, have, allowed):
    errs, seen = [], set()
    batch = {r.get("id") for _, r in rows if r.get("id")}
    for n, r in rows:
        tag = f"input line {n} {r.get('id') or '<no id>'}"
        for k in REQUIRED:
            if not (isinstance(r.get(k), str) and r.get(k).strip()):
                errs.append(f"{tag}: missing or empty `{k}`")
        rid = r.get("id")
        if rid:
            if rid in have:
                errs.append(f"{tag}: id already in the backlog")
            if rid in seen:
                errs.append(f"{tag}: id repeated in this batch")
            seen.add(rid)
        st = r.get("state")
        if st and st not in allowed:
            errs.append(f"{tag}: state {st!r} not in {sorted(allowed)}")
        if "status" in r:
            errs.append(f"{tag}: legacy `status` key; put prose in `status_note`")
        if st == "RUNNING" and not (r.get("claimed_by") and r.get("claimed_at")):
            errs.append(f"{tag}: RUNNING needs claimed_by and claimed_at")
        for field in ("depends_on", "unblocks"):
            for d in ids_of(r.get(field)):
                if d == rid:
                    errs.append(f"{tag}: {field} names the row itself")
                elif d not in have and d not in batch:
                    errs.append(f"{tag}: {field} id {d!r} is in neither the backlog nor this batch")
    return errs


def render_lines(rows, current):
    """The exact text to append. Keeps the trailing-newline convention: if the file ends without one, the new
    lines are joined on with a leading newline and the last one is left without a trailing newline."""
    body = "\n".join(json.dumps(r) for _, r in rows)
    if current == "" or current.endswith("\n"):
        return body + "\n"
    return "\n" + body


def graph_report(path, new_ids, today=None):
    cmd = [sys.executable, str(GRAPH), "--json", "--file", str(path)]
    if today:
        cmd += ["--today", today]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        return [f"graph: backlog_graph.py exited {p.returncode}: {p.stderr.strip()[-400:]}"], []
    g = json.loads(p.stdout)
    hits = [f"{k}: {line}" for k, v in g["findings"].items() for line in v
            if any(re.search(r"(?<![\w-])" + re.escape(i) + r"(?![\w-])", str(line)) for i in new_ids)]
    nodes = [x for x in g["nodes"] if x["id"] in new_ids]
    return hits, nodes


def append(path, text, dry_run=False, today=None, graph=True, out=print):
    """Validate the batch in `text` against `path`; append it unless dry_run. Returns an exit code."""
    path = Path(path)
    rows, errs = parse_batch(text)
    if not rows and not errs:
        out("nothing to append: the input has no rows")
        return 1
    fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        with open(str(path), "r", encoding="utf-8") as fh:
            current = fh.read()
        errs += validate(rows, existing_ids(current), states())
        if errs:
            for e in errs:
                out("FAIL " + e)
            out(f"refused: {len(errs)} problem(s); nothing written")
            return 1
        chunk = render_lines(rows, current)
        new_ids = [r["id"] for _, r in rows]
        if dry_run:
            tmp = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
            tmp.write(current + chunk)
            tmp.close()
            target = tmp.name
        else:
            data = chunk.encode("utf-8")
            os.lseek(fd, 0, os.SEEK_END)
            if os.write(fd, data) != len(data):
                out("FAIL short write; check the file tail by hand")
                return 1
            os.fsync(fd)
            target = str(path)
    finally:
        os.close(fd)
    out(("dry run: would append " if dry_run else "appended ") + f"{len(rows)} row(s) to {path}")
    for i in new_ids:
        out("  + " + i)
    if graph:
        hits, nodes = graph_report(target, set(new_ids), today)
        out(f"graph findings naming the new ids: {len(hits)}")
        for h in hits:
            out("  " + h)
        for x in nodes:
            out(f"  wave {x['wave']}  {x['state']:<8} ready_now={x['ready_now']}  {x['id']}")
        terminal = len(new_ids) - len(nodes)
        if terminal:
            out(f"  ({terminal} new row(s) are in a terminal state and have no wave)")
        if dry_run:
            os.unlink(target)
    return 0


def self_test():
    base = ('{"id": "a", "state": "OPEN", "jtbd": "first"}\n'
            '{"id": "b", "state": "HOLDING", "jtbd": "second", "depends_on": ["a"]}\n')
    cases = [
        ("bad JSON is refused", '{"id": "c", "state": "OPEN", "jtbd": "x"\n', 1, "not valid JSON"),
        ("a duplicate id against the file is refused", '{"id": "a", "state": "OPEN", "jtbd": "x"}\n', 1, "already in the backlog"),
        ("a duplicate id within the batch is refused",
         '{"id": "c", "state": "OPEN", "jtbd": "x"}\n{"id": "c", "state": "OPEN", "jtbd": "y"}\n', 1, "repeated in this batch"),
        ("a dangling depends_on is refused", '{"id": "c", "state": "OPEN", "jtbd": "x", "depends_on": ["ghost"]}\n', 1, "'ghost'"),
        ("a dangling unblocks is refused", '{"id": "c", "state": "OPEN", "jtbd": "x", "unblocks": "ghost"}\n', 1, "'ghost'"),
        ("a state outside the enum is refused", '{"id": "c", "state": "MAYBE", "jtbd": "x"}\n', 1, "not in"),
        ("a missing jtbd is refused", '{"id": "c", "state": "OPEN"}\n', 1, "`jtbd`"),
        ("RUNNING without a claim is refused", '{"id": "c", "state": "RUNNING", "jtbd": "x"}\n', 1, "claimed_by"),
        ("one bad row refuses the whole batch",
         '{"id": "c", "state": "OPEN", "jtbd": "x"}\n{"id": "d", "state": "OPEN", "jtbd": "y", "depends_on": ["nope"]}\n', 1, "'nope'"),
    ]
    checks = []
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "q.jsonl"
        for name, rows, want_rc, want_msg in cases:
            f.write_text(base)
            msgs = []
            rc = append(f, rows, graph=False, out=msgs.append)
            checks.append((name, rc == want_rc and any(want_msg in m for m in msgs) and f.read_text() == base))
        f.write_text(base)
        good = ('{"id": "c", "state": "OPEN", "jtbd": "third", "depends_on": ["b", "d"]}\n'
                '{"id": "d", "state": "DONE", "jtbd": "fourth", "unblocks": ["c"]}\n')
        msgs = []
        rc = append(f, good, dry_run=True, graph=False, out=msgs.append)
        checks.append(("dry run validates and writes nothing", rc == 0 and f.read_text() == base))
        rc = append(f, good, graph=False, out=msgs.append)
        after = f.read_text()
        checks.append(("happy path: forward reference inside the batch is accepted and both rows land", rc == 0 and existing_ids(after) == {"a", "b", "c", "d"}))
        checks.append(("existing lines are byte-identical; new lines only appended", after.startswith(base) and after.count("\n") == 4 and after.endswith("\n")))
        f.write_text(base.rstrip("\n"))
        rc = append(f, '{"id": "e", "state": "OPEN", "jtbd": "x"}\n', graph=False, out=msgs.append)
        t = f.read_text()
        checks.append(("no-trailing-newline file keeps its convention and the last old row is not glued to the new one",
                       rc == 0 and t.startswith(base.rstrip("\n") + "\n{") and not t.endswith("\n") and existing_ids(t) == {"a", "b", "e"}))
        checks.append(("output has no em-dash", all(chr(0x2014) not in m for m in msgs)))
    ok = True
    for name, passed in checks:
        print(("PASS " if passed else "FAIL ") + name)
        ok = ok and passed
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=str(DEFAULT_FILE))
    ap.add_argument("--rows", help="JSONL file of new rows (default: stdin)")
    ap.add_argument("--dry-run", action="store_true", help="validate and show graph findings; write nothing")
    ap.add_argument("--today", default=None, help="YYYY-MM-DD passed through to backlog_graph.py")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    text = Path(a.rows).read_text(encoding="utf-8") if a.rows else sys.stdin.read()
    return append(a.file, text, dry_run=a.dry_run, today=a.today)


if __name__ == "__main__":
    sys.exit(main())
