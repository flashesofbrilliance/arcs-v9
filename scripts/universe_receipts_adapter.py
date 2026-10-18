#!/usr/bin/env python3
"""universe_receipts_adapter: project one person's decision receipts into a personal universe of atoms + a link graph.

Backlog row universe-receipts-as-atoms. The first person is Zach: every decision_receipt row ends in --ZH (854 rows,
checked 2026-10-18; the 89 `operator` values are sessions and harnesses, not other people).

Source (read-only): public.decision_receipt, exported to _STATE/job-search/universe/sources/decision-receipts.json
(gitignored; --export runs `supabase db query --linked`). The database stays the SSOT; the atoms are an induced projection
(ADR-065), so the generated files are gitignored too and rebuilt on any machine.

Atoms (universe `zach-receipts`, tier `personal`, ALWAYS audience internal):
  <rid>        entity receipt      type claim       the question, with mode/stakes/horizon as tags
  <rid>#cN     entity confirmed    type claim       one what_confirmed line (grade B: asserted by the operator, backed by refs)
  <rid>#uN     entity unconfirmed  type hypothesis  one what_unconfirmed line
Bridges: an atom that names a registered counterpart universe gets `bridges: [universe]` (declared, never inferred from
anything but a name match). The sweep treats a declared bridge as an edge, not a leak; a bridged atom can never be projected public.
Edges (zach-receipts.edges.jsonl): receipt -> PR, commit, file, ADR, other receipt, taken only from the receipt's own refs.
The Librarian (Operator 21) loader is the follow-up row; this file only produces the atoms it would read.

  python3 scripts/universe_receipts_adapter.py --export      # refresh the local export from the database
  python3 scripts/universe_receipts_adapter.py               # build atoms + edges from the export
  python3 scripts/universe_receipts_adapter.py --self-test
Stdlib only.
"""
import collections, json, os, re, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import universe_ask as ua

PERSON = "zach-receipts"
RID_RE = re.compile(r"^\d{4}-\d{2}-\d{2}--.+--[A-Z]{2}$")
PR_RE = re.compile(r"github\.com/([^/]+/[^/]+)/pull/(\d+)")
SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
ADR_RE = re.compile(r"\bADR-(\d{3})\b")


def classify_ref(ref, ids):
    m = PR_RE.search(ref)
    if m:
        return "pr", f"pr:{m.group(1)}#{m.group(2)}"
    if ref in ids or RID_RE.match(ref):
        return "receipt", ref
    if SHA_RE.match(ref):
        return "commit", f"commit:{ref[:7]}"
    m = ADR_RE.search(ref)
    if m and "/" in ref or m and ref.startswith("ADR-"):
        return "adr", f"ADR-{m.group(1)}"
    if "/" in ref and "." in ref.rsplit("/", 1)[-1]:
        return "file", f"file:{ref}"
    return "other", ref


def build(rows, reg, person=PERSON):
    others = {u: d.get("names", []) for u, d in reg["universes"].items() if u != person and d.get("tier") == "counterpart"}
    extra = reg.get("canon_denied_names_extra", [])
    ids = {r["receipt_id"] for r in rows}
    atoms, edges, stats = [], [], collections.Counter()
    for r in rows:
        rid = r["receipt_id"]; day = str(r["event_at"])[:10]
        src = f"decision_receipt:{rid}"
        def atom(suffix, entity, typ, text, grade):
            a = {"id": f"{person}/{rid}{suffix}", "entity": entity, "type": typ, "claim": text, "source": src, "grade": grade,
                 "verified_at": day, "ttl_days": 3650, "audience": "internal",
                 "tags": ["receipt", r["mode"].lower(), r["stakes"], r["horizon"], day[:7]]}
            br = sorted(u for u, ns in others.items() if ua.find_names(text, ns))
            if br:
                a["bridges"] = br; stats["bridged_atoms"] += 1
            if ua.find_names(text, extra):
                stats["mentions_unregistered_counterpart"] += 1
            atoms.append(a)
        atom("", "receipt", "claim", r["question"], "B")
        for i, t in enumerate(r["what_confirmed"] or []):
            atom(f"#c{i}", "confirmed", "claim", t, "B")
        for i, t in enumerate(r["what_unconfirmed"] or []):
            atom(f"#u{i}", "unconfirmed", "hypothesis", t, "hypothesis")
        for ref in r["refs"] or []:
            kind, node = classify_ref(ref, ids)
            edges.append({"from": rid, "to": node, "kind": kind}); stats[f"edge_{kind}"] += 1
    stats["receipts"] = len(rows); stats["atoms"] = len(atoms); stats["edges"] = len(edges)
    indeg = collections.Counter(e["to"] for e in edges)
    stats["most_cited"] = [(n, c) for n, c in indeg.most_common(5)]
    return atoms, edges, stats


def main():
    argv = sys.argv[1:]
    if "--self-test" in argv:
        return self_test()
    root = ua.ROOT; src = os.path.join(root, "sources", "decision-receipts.json")
    if "--export" in argv:
        r = subprocess.run(["supabase", "db", "query", "--linked", "--project-ref", "xbbpiryokswwvcrcutge", "--output-format", "json",
                            "select receipt_id, question, horizon, stakes, mode, what_confirmed, what_unconfirmed, operator, event_at, source_repo, refs "
                            "from public.decision_receipt order by event_at"], capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit("export failed: " + r.stderr[-300:])
        json.dump(json.loads(r.stdout)["rows"], open(src, "w"))  # rows are data; the wrapper's boundary/warning keys are dropped
        print(f"exported -> {src}")
    if not os.path.exists(src):
        sys.exit("no export: run with --export first (needs the supabase CLI linked to ARCS_v9).")
    rows = json.load(open(src))
    reg = ua.load_registry(root)
    atoms, edges, stats = build(rows, reg)
    w = lambda name, rs: open(os.path.join(root, name), "w", encoding="utf-8").write("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rs))
    w(f"{PERSON}.claims.jsonl", atoms); w(f"{PERSON}.edges.jsonl", edges)
    print(f"{PERSON}: {stats['receipts']} receipts -> {stats['atoms']} atoms, {stats['edges']} edges "
          f"(pr {stats['edge_pr']}, commit {stats['edge_commit']}, file {stats['edge_file']}, adr {stats['edge_adr']}, receipt {stats['edge_receipt']}, other {stats['edge_other']})")
    print(f"  declared bridges to counterpart universes: {stats['bridged_atoms']} atoms · naming an unregistered counterpart: {stats['mentions_unregistered_counterpart']}")
    print(f"  most cited: {stats['most_cited']}")
    open(os.path.join(REPO, "_INBOX", "universe-drift.jsonl"), "a", encoding="utf-8").write(json.dumps(
        {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "type": "receipts-adapter-receipt", "universe": PERSON, **{k: v for k, v in stats.items() if k != "most_cited"}}) + "\n")
    return 0


def self_test():
    reg = {"canon_denied_names_extra": ["zed corp"], "universes": {
        "acme": {"tier": "counterpart", "names": ["acme"], "entities": ["acme"], "anti_aliases": []},
        PERSON: {"tier": "personal", "entities": ["receipt", "confirmed", "unconfirmed"], "names": [], "anti_aliases": []}}}
    rows = [{"receipt_id": "2026-10-01--first--ZH", "question": "Ship the Acme brief?", "horizon": "today", "stakes": "low", "mode": "QUICKMOVE",
             "event_at": "2026-10-01 10:00:00+00", "what_confirmed": ["merged as abc1234"], "what_unconfirmed": ["Zed Corp reply pending", "tone not tested"],
             "refs": ["https://github.com/o/r/pull/12", "abc1234", "_DECISIONS/ADR-033-x.md", "src/a.ts", "plain-word"]},
            {"receipt_id": "2026-10-02--second--ZH", "question": "Follow up", "horizon": "today", "stakes": "low", "mode": "PLAN",
             "event_at": "2026-10-02 10:00:00+00", "what_confirmed": [], "what_unconfirmed": [], "refs": ["2026-10-01--first--ZH"]}]
    atoms, edges, st = build(rows, reg)
    ok = []
    ok.append(("5 atoms: 2 receipts + 1 confirmed + 2 unconfirmed", len(atoms) == 5))
    ok.append(("unconfirmed lines become hypotheses, never claims", [a["type"] for a in atoms if a["entity"] == "unconfirmed"] == ["hypothesis", "hypothesis"]))
    ok.append(("a name match declares a bridge to the counterpart universe", atoms[0].get("bridges") == ["acme"] and "bridges" not in atoms[1]))
    ok.append(("an unregistered counterpart is counted, not guessed into a bridge", st["mentions_unregistered_counterpart"] == 1))
    ok.append(("refs classified into pr, commit, adr, file, receipt, other", sorted(e["kind"] for e in edges) == sorted(["pr", "commit", "adr", "file", "other", "receipt"])))
    ok.append(("every atom is internal", all(a["audience"] == "internal" for a in atoms)))
    ok.append(("receipt-to-receipt edge targets the real receipt id", {"from": "2026-10-02--second--ZH", "to": "2026-10-01--first--ZH", "kind": "receipt"} in edges))
    tmp = tempfile.mkdtemp()
    try:
        json.dump({"universes": {PERSON: {"tier": "personal", "entities": ["receipt", "confirmed", "unconfirmed"], "names": [], "anti_aliases": []}}}, open(os.path.join(tmp, "_registry.json"), "w"))
        bad = [dict(atoms[0], audience="external")]
        open(os.path.join(tmp, f"{PERSON}.claims.jsonl"), "w").write(json.dumps(bad[0]) + "\n")
        r = subprocess.run([sys.executable, os.path.join(HERE, "universe_ask.py"), "--universe", PERSON, "x"], capture_output=True, text=True, env={**os.environ, "UNIVERSE_ROOT": tmp})
        ok.append(("personal tier refuses an external atom at load (AIR-GAP)", r.returncode != 0 and "AIR-GAP" in r.stderr))
        open(os.path.join(tmp, f"{PERSON}.claims.jsonl"), "w").write(json.dumps(atoms[0]) + "\n")
        r = subprocess.run([sys.executable, os.path.join(HERE, "universe_ask.py"), "--universe", PERSON, "--project", "public"], capture_output=True, text=True, env={**os.environ, "UNIVERSE_ROOT": tmp})
        ok.append(("personal tier can never be projected public", r.returncode != 0 and "personal" in r.stderr))
    finally:
        import shutil; shutil.rmtree(tmp, ignore_errors=True)
    for n, p in ok:
        print(("PASS " if p else "FAIL ") + n)
    print(f"self-test: {sum(p for _, p in ok)}/{len(ok)} pass")
    return 0 if all(p for _, p in ok) else 1


if __name__ == "__main__":
    sys.exit(main())
