#!/usr/bin/env python3
"""receipt_outcome_queue: a triage queue and an append-only ledger for outcomes on Zach's decision receipts.

Backlog row universe-outcome-capture. Measured 2026-10-18 before building (so the design fits the data):
  * compass `Receipt` table: 271 rows, 0 tagged real, 3 outcomes (2 test, 1 untagged) -> nothing to capture yet.
  * git-side adjudication is almost always 'held' (612 of 647 cited PRs merged, 0 of 637 cited commits reverted,
    1 revert on main), so it carries little information; scripts/reel_in_scan.py already covers it.
  * decision_receipt: 834 of 854 receipts carry open (unconfirmed) lines, 2101 lines in all, none with a recorded resolution.
So the outcomes worth capturing are the resolutions of the open lines on the receipts that mattered. Default scope:
stakes high or critical, or mode COURT.

Rules (same invariant as scripts/receipt_outcome_resolver.py):
  * A verdict is supplied by a human, never inferred. This script only lists and records.
  * Every row says WHO adjudicated: `self` (the decision-maker grading their own decision = capture, never scored)
    or `external` (a signal from someone or something else; needs an evidence ref that resolves).
  * Append-only. A changed mind is a new row that supersedes the old one; nothing is edited or deleted.

Verdicts: held (the open item turned out as hoped) · reeled (it was wrong, corrected or reversed) · open (reviewed, still
unresolved) · dropped (no longer relevant).

Ledger: _STATE/receipt-outcomes.jsonl (tracked; short human notes only). Source of receipts: the gitignored export written by
scripts/universe_receipts_adapter.py --export. Verdicts are projected into the zach-receipts universe as `outcome` atoms by
that adapter.

  python3 scripts/receipt_outcome_queue.py queue [--all-stakes] [--limit N] [--json]
  python3 scripts/receipt_outcome_queue.py record --receipt ID --line N --verdict held --by self [--note TEXT]
  python3 scripts/receipt_outcome_queue.py record ... --by external --evidence <PR url | commit sha | repo path>
  python3 scripts/receipt_outcome_queue.py status
  python3 scripts/receipt_outcome_queue.py --self-test
Stdlib only.
"""
import argparse, json, os, re, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
EXPORT = os.path.join(REPO, "_STATE", "job-search", "universe", "sources", "decision-receipts.json")
LEDGER = os.path.join(REPO, "_STATE", "receipt-outcomes.jsonl")
VERDICTS = ("held", "reeled", "open", "dropped")
SCOPE_STAKES = ("high", "critical")


def load_receipts(path=EXPORT):
    if not os.path.exists(path):
        sys.exit("no export: run `python3 scripts/universe_receipts_adapter.py --export` first.")
    return {r["receipt_id"]: r for r in json.load(open(path))}


def load_ledger(path=LEDGER):
    """Latest row per (receipt, line); a superseding row wins, the history stays in the file."""
    latest = {}
    if os.path.exists(path):
        for l in open(path, encoding="utf-8"):
            if l.strip():
                r = json.loads(l); latest[(r["receipt_id"], r["line"])] = r
    return latest


def in_scope(r, all_stakes=False):
    return bool(r["what_unconfirmed"]) and (all_stakes or r["stakes"] in SCOPE_STAKES or r["mode"] == "COURT")


def queue(receipts, ledger, all_stakes=False):
    out = []
    for rid, r in sorted(receipts.items(), key=lambda kv: kv[1]["event_at"]):
        if not in_scope(r, all_stakes):
            continue
        for i, text in enumerate(r["what_unconfirmed"]):
            if (rid, i) not in ledger:
                out.append({"receipt_id": rid, "line": i, "event_at": str(r["event_at"])[:10], "stakes": r["stakes"], "mode": r["mode"],
                            "question": r["question"], "open_line": text})
    return out


def evidence_ok(ev, repo=REPO):
    if re.search(r"github\.com/[^/]+/[^/]+/(pull|issues|commit)/\w+", ev):
        return True
    if re.fullmatch(r"[0-9a-f]{7,40}", ev):
        return subprocess.run(["git", "cat-file", "-e", ev + "^{commit}"], cwd=repo, capture_output=True).returncode == 0
    return os.path.exists(os.path.join(repo, ev))


def record(receipts, rid, line, verdict, by, evidence=None, note=None, path=LEDGER, repo=REPO, supersede=False):
    r = receipts.get(rid)
    if not r:
        sys.exit(f"unknown receipt {rid}.")
    if not (0 <= line < len(r["what_unconfirmed"])):
        sys.exit(f"{rid} has {len(r['what_unconfirmed'])} open line(s); line {line} does not exist.")
    if verdict not in VERDICTS:
        sys.exit(f"verdict must be one of {VERDICTS}.")
    if by not in ("self", "external"):
        sys.exit("--by must be self or external.")
    if by == "external" and not (evidence and evidence_ok(evidence, repo)):
        sys.exit("an external verdict needs an evidence ref that resolves (PR/issue/commit URL, a commit sha in this repo, or a repo path).")
    prior = load_ledger(path).get((rid, line))
    if prior and not supersede:
        sys.exit(f"{rid} line {line} already has a verdict ({prior['verdict']}, {prior['by']}); pass --supersede to append a new one.")
    row = {"receipt_id": rid, "line": line, "verdict": verdict, "by": by, "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "open_line": r["what_unconfirmed"][line][:160]}
    if evidence:
        row["evidence"] = evidence
    if note:
        row["note"] = note[:240]
    if prior:
        row["supersedes"] = prior["ts"]
    open(path, "a", encoding="utf-8").write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def status(receipts, ledger):
    scope = [(rid, i) for rid, r in receipts.items() if in_scope(r) for i in range(len(r["what_unconfirmed"]))]
    done = [k for k in scope if k in ledger]
    allrows = list(ledger.values())
    by = {"self": sum(1 for r in allrows if r["by"] == "self"), "external": sum(1 for r in allrows if r["by"] == "external")}
    vc = {v: sum(1 for r in allrows if r["verdict"] == v) for v in VERDICTS}
    return {"receipts_in_scope": len({rid for rid, _ in scope}), "open_lines_in_scope": len(scope), "resolved_in_scope": len(done),
            "capture_rate_in_scope": round(len(done) / len(scope), 3) if scope else None, "verdicts": vc, "adjudicated_by": by,
            "scored_by_resolver": by["external"]}


def self_test():
    tmp = tempfile.mkdtemp(); led = os.path.join(tmp, "l.jsonl")
    R = {"a--ZH": {"receipt_id": "a--ZH", "stakes": "high", "mode": "PLAN", "event_at": "2026-10-01", "question": "q", "what_unconfirmed": ["x", "y"]},
         "b--ZH": {"receipt_id": "b--ZH", "stakes": "low", "mode": "QUICKMOVE", "event_at": "2026-10-02", "question": "q", "what_unconfirmed": ["z"]},
         "c--ZH": {"receipt_id": "c--ZH", "stakes": "low", "mode": "COURT", "event_at": "2026-10-03", "question": "q", "what_unconfirmed": ["w"]},
         "d--ZH": {"receipt_id": "d--ZH", "stakes": "critical", "mode": "PLAN", "event_at": "2026-10-04", "question": "q", "what_unconfirmed": []}}
    ok = []
    def fails(fn, *a, **k):
        try:
            fn(*a, **k); return False
        except SystemExit:
            return True
    ok.append(("scope: high/critical or COURT with open lines (a x2, c x1); low-stakes and empty excluded", [(q["receipt_id"], q["line"]) for q in queue(R, {})] == [("a--ZH", 0), ("a--ZH", 1), ("c--ZH", 0)]))
    ok.append(("--all-stakes widens scope to include b", any(q["receipt_id"] == "b--ZH" for q in queue(R, {}, True))))
    row = record(R, "a--ZH", 0, "held", "self", note="n", path=led, repo=tmp)
    ok.append(("a self verdict is recorded and marked self", row["by"] == "self" and load_ledger(led)[("a--ZH", 0)]["verdict"] == "held"))
    ok.append(("a resolved line leaves the queue", ("a--ZH", 0) not in [(q["receipt_id"], q["line"]) for q in queue(R, load_ledger(led))]))
    ok.append(("an external verdict without evidence is refused", fails(record, R, "a--ZH", 1, "reeled", "external", path=led, repo=tmp)))
    ok.append(("an external verdict with an unresolvable ref is refused", fails(record, R, "a--ZH", 1, "reeled", "external", evidence="nope/missing.md", path=led, repo=tmp)))
    open(os.path.join(tmp, "real.md"), "w").write("x")
    ok.append(("an external verdict with a resolvable path is accepted", record(R, "a--ZH", 1, "reeled", "external", evidence="real.md", path=led, repo=tmp)["by"] == "external"))
    ok.append(("a second verdict on the same line needs --supersede", fails(record, R, "a--ZH", 0, "reeled", "self", path=led, repo=tmp)))
    sup = record(R, "a--ZH", 0, "reeled", "self", path=led, repo=tmp, supersede=True)
    ok.append(("supersede appends (never edits): 3 rows in the file, latest wins", sum(1 for _ in open(led)) == 3 and "supersedes" in sup and load_ledger(led)[("a--ZH", 0)]["verdict"] == "reeled"))
    ok.append(("bad line index and bad verdict are refused", fails(record, R, "a--ZH", 9, "held", "self", path=led, repo=tmp) and fails(record, R, "a--ZH", 0, "maybe", "self", path=led, repo=tmp)))
    st = status(R, load_ledger(led))
    ok.append(("status: external verdicts counted separately; self never counts as scored", st["adjudicated_by"] == {"self": 1, "external": 1} and st["scored_by_resolver"] == 1))
    for n, p in ok:
        print(("PASS " if p else "FAIL ") + n)
    print(f"self-test: {sum(p for _, p in ok)}/{len(ok)} pass")
    return 0 if all(p for _, p in ok) else 1


def main():
    if "--self-test" in sys.argv:
        return self_test()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("queue"); q.add_argument("--all-stakes", action="store_true"); q.add_argument("--limit", type=int, default=15); q.add_argument("--json", action="store_true")
    rc = sub.add_parser("record")
    rc.add_argument("--receipt", required=True); rc.add_argument("--line", type=int, required=True); rc.add_argument("--verdict", required=True)
    rc.add_argument("--by", required=True); rc.add_argument("--evidence"); rc.add_argument("--note"); rc.add_argument("--supersede", action="store_true")
    sub.add_parser("status")
    a = ap.parse_args()
    receipts = load_receipts()
    if a.cmd == "queue":
        items = queue(receipts, load_ledger(), a.all_stakes)
        if a.json:
            print(json.dumps(items[: a.limit], indent=1, ensure_ascii=False)); return 0
        print(f"{len(items)} open line(s) waiting; showing {min(a.limit, len(items))}, oldest first")
        for it in items[: a.limit]:
            print(f"- {it['receipt_id']} line {it['line']} [{it['stakes']}/{it['mode']}] {it['event_at']}\n    Q: {it['question'][:140]}\n    open: {it['open_line'][:200]}")
        return 0
    if a.cmd == "record":
        print(json.dumps(record(receipts, a.receipt, a.line, a.verdict, a.by, a.evidence, a.note, supersede=a.supersede), ensure_ascii=False)); return 0
    print(json.dumps(status(receipts, load_ledger()), indent=1)); return 0


if __name__ == "__main__":
    sys.exit(main())
