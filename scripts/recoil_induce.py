#!/usr/bin/env python3
"""recoil_induce.py: induce candidate backlog rows from a recoil report or war room. Stdlib only, no model calls.

Five stages. Each reads JSON on stdin (or --in) and writes JSON on stdout, so each runs on its own and they pipe:

  extract  recoil SSOT JSON (or a recoil-close markdown) -> candidates
           sources: an `induced` array, then `next_steps`, then a markdown section titled "Induced backlog"
  snap     each candidate's job -> the existing tool for it, from runtime/specs/tool-catalog.json, checked with
           backlog_graph.resolve_tool. Never invents a tool: no catalog match, or a named tool that does not
           resolve, gives route.tool "NOT-RESOLVED: ..." (backlog_graph labels that NOT-RESOLVED)
  cluster  Operator 20 Folksonomy: its stdlib DBSCAN (operators/arcs_operator20.py) over job word sets
  rank     Operator 19 Accountant: outcome weight from how far the linked beliefs moved, rank-combined with
           its _rank. Operator 21 Librarian (operators/arcs_librarian.py): value = p_load_bearing x
           cost_if_absent(stakes) from its own tier table, and per cluster the prior art it would retrieve
           under a context budget (--no-librarian skips the corpus read)
  rows     candidates -> _QUEUE/induced-backlog.jsonl row shape, as JSONL on stdout

`all` runs the five in order. Nothing here writes the live backlog: filing a row stays a human step (NOTOMATION).
The JSONL feeds `backlog_graph.py --file <rows.jsonl> --json`, which the recoil player's organism 35 renders.

usage:
  recoil_induce.py extract --data F | recoil_induce.py snap | recoil_induce.py cluster | recoil_induce.py rank | recoil_induce.py rows
  recoil_induce.py all --data F [--no-librarian] [--budget 4000]
  recoil_induce.py --self-test
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "operators"))
import backlog_graph as bg  # noqa: E402
from arcs_accountant import _rank  # noqa: E402  Operator 19
from arcs_operator20 import DBSCAN  # noqa: E402  Operator 20

STOP = set("a an the and or of to for in on with by from at as is are be it this that we our you your their them "
           "they he she his her i me my will would can could should into one two not no yes than then so if but "
           "about after before when what which who how up out over per each all any new use using via get".split())
SNAP_MIN = 0.18          # weighted overlap a catalog tool must reach to count as the tool for the job
STAKES = ("low", "medium", "high", "critical")
CIA_FALLBACK = {"low": 1.5, "medium": 3.0, "high": 6.0, "critical": 12.0}


def words(s):
    return {w for w in re.findall(r"[a-z][a-z0-9-]{2,}", str(s).lower()) if w not in STOP}


def slug(s, n=48):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", str(s).lower())).strip("-")[:n].strip("-")


# ---------------------------------------------------------------- extract
def extract(data=None, md=None):
    """-> envelope {meta, beliefs, candidates[]}. Candidates keep their source so a human can trace each one."""
    cands = []
    if data is not None:
        for i, it in enumerate(data.get("induced") or []):
            cands.append({"title": it.get("title") or it.get("jtbd", "")[:60], "jtbd": it.get("jtbd") or it.get("title", ""),
                          "tool_hint": it.get("tool"), "depends_on": list(it.get("depends_on") or []),
                          "beliefs": list(it.get("beliefs") or []), "stakes": it.get("stakes", "medium"),
                          "source": "induced[%d]" % i})
        if not cands:
            for i, it in enumerate(data.get("next_steps") or []):
                text = it.get("text", "") if isinstance(it, dict) else str(it)
                if re.match(r"\s*DONE\b", text):
                    continue
                cands.append({"title": text[:60], "jtbd": text, "tool_hint": None, "depends_on": [], "beliefs": [],
                              "stakes": "medium", "owner": (it or {}).get("owner") if isinstance(it, dict) else None,
                              "source": "next_steps[%d]" % i})
    if md is not None:
        sec = re.search(r"^#{1,4}[^\n]*induced backlog[^\n]*\n(.*?)(?=^#{1,4} |\Z)", md, re.I | re.M | re.S)
        for i, line in enumerate(re.findall(r"^\s*(?:[-*]|\d+[.)])\s+(.+)$", sec.group(1) if sec else "", re.M)):
            tool = re.search(r"`([^`]+)`", line)
            text = re.sub(r"\*\*|`", "", line).strip()
            cands.append({"title": text[:60], "jtbd": text, "tool_hint": tool.group(1) if tool else None,
                          "depends_on": [], "beliefs": [], "stakes": "medium", "source": "md:induced[%d]" % i})
    meta = (data or {}).get("meta", {})
    return {"stage": "extract", "meta": meta, "beliefs": (data or {}).get("beliefs", []), "candidates": cands}


# ---------------------------------------------------------------- snap
def load_catalog():
    try:
        return [t for t in json.loads((ROOT / "runtime/specs/tool-catalog.json").read_text())["tools"]
                if t.get("state", "WIRED") not in ("BROKEN", "RETIRED")]
    except (OSError, KeyError, ValueError):
        return []


def snap(env, catalog=None, names=None, files=None):
    catalog = load_catalog() if catalog is None else catalog
    names = bg.known_tools() if names is None else names
    files = set(bg.repo_files()) if files is None else files
    docs = [(t, words(t.get("name", "")) | words(t.get("jtbd", ""))) for t in catalog]
    df = {}
    for _, ws in docs:
        for w in ws:
            df[w] = df.get(w, 0) + 1
    idf = lambda w: 1.0 / (1 + df.get(w, 0))  # noqa: E731  rare words carry the match
    for c in env["candidates"]:
        if c.get("tool_hint"):
            label, ok, miss, _ = bg.resolve_tool({"route": {"tool": c["tool_hint"]}, "jtbd": ""}, names, files)
            c["route_tool"] = c["tool_hint"] if label == "HAVE" else "NOT-RESOLVED: named %s, not in the repo or catalog" % c["tool_hint"]
            c["snap"] = {"label": "HAVE" if label == "HAVE" else "NOT-RESOLVED", "via": "named", "missing": miss}
            continue
        q = words(c["jtbd"])
        best, score = None, 0.0
        for t, ws in docs:
            hit = q & ws
            s = sum(idf(w) for w in hit) / (sum(idf(w) for w in q) or 1)
            if s > score:
                best, score = t, s
        tool = best and (best.get("path") or best.get("invoke") or best.get("name"))
        label = bg.resolve_tool({"route": {"tool": tool}, "jtbd": ""}, names, files)[0] if tool and score >= SNAP_MIN else None
        if label == "HAVE":
            c["route_tool"] = tool
            c["snap"] = {"label": "HAVE", "via": "catalog", "tool": best.get("name"), "score": round(score, 3),
                         "matched": sorted(q & words(best.get("name", "")) | (q & words(best.get("jtbd", ""))))}
        else:
            c["route_tool"] = "NOT-RESOLVED: no existing tool fits this job yet"
            c["snap"] = {"label": "NOT-RESOLVED", "via": "catalog", "nearest": best and best.get("name"),
                         "score": round(score, 3)}
    env["stage"] = "snap"
    return env


# ---------------------------------------------------------------- cluster (Operator 20)
class _Pt:
    """Duck-typed seed for Operator 20's DBSCAN: it only calls .distance()."""

    def __init__(self, ws):
        self.ws = ws

    def distance(self, other):
        u = self.ws | other.ws
        return 1.0 - (len(self.ws & other.ws) / len(u) if u else 0.0)


def cluster(env, epsilon=0.8):
    cs = env["candidates"]
    pts = [_Pt(words(c["jtbd"]) | ({"tool:" + c["route_tool"]} if c.get("snap", {}).get("label") == "HAVE" else set()))
           for c in cs]
    labels = DBSCAN(epsilon=epsilon, min_samples=2).fit(pts) if pts else []
    nxt = max([l for l in labels if l >= 0], default=-1) + 1
    for c, lab, p in zip(cs, labels, pts):
        if lab < 0:  # noise is a cluster of one, never dropped
            lab, nxt = nxt, nxt + 1
        c["cluster"] = lab
    names = {}
    for lab in sorted({c["cluster"] for c in cs}):
        members = [words(c["jtbd"]) for c in cs if c["cluster"] == lab]
        common = set.intersection(*members) if len(members) > 1 else set()
        freq = {}
        for m in members:
            for w in m:
                freq[w] = freq.get(w, 0) + 1
        top = sorted(common or freq, key=lambda w: (-freq[w], w))[:3]
        names[lab] = "-".join(top) or "misc"
    for c in cs:
        c["cluster_name"] = names[c["cluster"]]
    env["clusters"] = [{"id": k, "name": v, "size": sum(c["cluster"] == k for c in cs)} for k, v in sorted(names.items())]
    env["stage"] = "cluster"
    return env


# ---------------------------------------------------------------- rank (Operators 19 and 21)
def rank(env, librarian=True, budget=4000):
    cs = env["candidates"]
    moved = {}
    for b in env.get("beliefs", []):
        conf = b.get("confidence") or []
        if len(conf) >= 2:
            moved[b.get("id")] = abs(float(conf[-1]) - float(conf[0]))
    cia, lib = dict(CIA_FALLBACK), None
    if librarian:
        from arcs_librarian import Librarian  # Operator 21
        lib = Librarian()
        cia.update(lib.tiers.get("cost_if_absent_by_stakes") or {})
    for c in cs:
        st = c.get("stakes") if c.get("stakes") in STAKES else "medium"
        shifts = [moved[b] for b in c.get("beliefs", []) if b in moved]
        c["outcome_weight"] = round(max(shifts), 3) if shifts else 0.5   # 0.5 = no linked belief, no evidence either way
        c["value"] = round(c["outcome_weight"] * cia[st] / (1 + len(c.get("depends_on", []))), 4)
    ranks = _rank([-c["value"] for c in cs]) if cs else []
    for c, r in zip(cs, ranks):
        c["rank"] = r
    totals = {}
    for c in cs:
        totals[c["cluster"]] = totals.get(c["cluster"], 0) + c["value"]
    cs.sort(key=lambda c: (-totals[c["cluster"]], c["cluster"], c["rank"], c["title"]))
    for i, c in enumerate(cs):
        c["order"] = i + 1
    for cl in env.get("clusters", []):
        cl["value"] = round(totals.get(cl["id"], 0), 4)
        if lib:
            text = " ".join(c["jtbd"] for c in cs if c["cluster"] == cl["id"])
            rec = lib.recommend(text[:600], budget=budget, stakes="medium", n_max=3)
            cl["prior_art"] = [{"id": it.get("id"), "path": it.get("path"), "value": it.get("value")} for it in rec.get("items", [])]
    env["clusters"] = sorted(env.get("clusters", []), key=lambda k: -k["value"])
    env["stage"] = "rank"
    return env


# ---------------------------------------------------------------- rows
def rows(env, today=None):
    meta = env.get("meta", {})
    date = today or meta.get("date") or "1970-01-01"
    who = slug(meta.get("counterpart", "recoil"), 20)
    seen, out = set(), []
    for c in env["candidates"]:
        rid = "induced-%s-%s" % (who, slug(c["title"], 36))
        base, k = rid, 2
        while rid in seen:
            rid, k = "%s-%d" % (base, k), k + 1
        seen.add(rid)
        out.append({
            "id": rid, "jtbd": c["jtbd"], "state": "OPEN", "outlet": "internal",
            "status_note": "Candidate from recoil induce (%s, snap %s). Fate is a human call." % (c["source"], c["snap"]["label"]),
            "route": {"session": "fresh", "tool": c["route_tool"]},
            "gates": ["human fate before filing"], "trigger": "recoil %s %s" % (date, meta.get("counterpart", "")),
            "depends_on": c.get("depends_on", []), "blockers": [], "added": date, "source": "scripts/recoil_induce.py",
            "consent": "human", "order": c.get("order"),
            "induce": {"cluster": c.get("cluster"), "cluster_name": c.get("cluster_name"), "value": c.get("value"),
                       "outcome_weight": c.get("outcome_weight"), "snap": c["snap"]},
        })
    return out


# ---------------------------------------------------------------- CLI
def run_all(data=None, md=None, librarian=True, budget=4000, **kw):
    return rows(rank(cluster(snap(extract(data, md), **kw)), librarian, budget))


def self_test():
    cat = [{"name": "backlog-graph", "path": "scripts/backlog_graph.py",
            "jtbd": "induced backlog as a graph: dependencies, order, what can start now"},
           {"name": "page-gate", "path": "scripts/page_gate.py", "jtbd": "gate a single-file html page for wrapping and contrast"}]
    names = {"scripts/backlog_graph.py", "backlog_graph.py", "scripts/page_gate.py", "page_gate.py", "backlog-graph", "page-gate"}
    files = {"scripts/backlog_graph.py", "scripts/page_gate.py"}
    data = {"meta": {"counterpart": "Test Person (made-up)", "date": "2026-01-02"},
            "beliefs": [{"id": "B1", "confidence": [0.2, 0.9]}, {"id": "B2", "confidence": [0.5, 0.5]}],
            "induced": [
                {"title": "Graph the backlog", "jtbd": "Show the induced backlog graph with dependencies and order", "beliefs": ["B1"]},
                {"title": "Graph backlog waves", "jtbd": "Show backlog graph order and what can start now", "stakes": "high"},
                {"title": "Gate the page", "jtbd": "Gate the html page for wrapping and contrast", "beliefs": ["B2"]},
                {"title": "Invented tool", "jtbd": "Do a thing", "tool": "scripts/does_not_exist.py"},
                {"title": "Unmatched job", "jtbd": "Negotiate the orchard lease with the landlord"},
                {"title": "Weak overlap", "jtbd": "Order fence posts, gravel, lumber and nails for the landlord"}]}
    md = "# Close\n## 7. Induced backlog\n- Gate the page with `scripts/page_gate.py`\n- Plant tulips\n## 8. Next\n- not this\n"
    out = run_all(data, librarian=False, catalog=cat, names=names, files=files)
    by = {r["jtbd"][:12]: r for r in out}
    mdc = extract(md=md)["candidates"]
    ok = True
    checks = [
        ("known-good: catalog job snaps to the catalog tool", by["Show the ind"]["route"]["tool"] == "scripts/backlog_graph.py"),
        ("known-good: html job snaps to page_gate", by["Gate the htm"]["route"]["tool"] == "scripts/page_gate.py"),
        ("known-bad: invented named tool is NOT-RESOLVED", by["Do a thing"]["route"]["tool"].startswith("NOT-RESOLVED")),
        ("known-bad: job with no tool is NOT-RESOLVED, nothing guessed", by["Negotiate th"]["route"]["tool"].startswith("NOT-RESOLVED")),
        ("known-bad: one incidental shared word does not snap a tool", by["Order fence "]["route"]["tool"].startswith("NOT-RESOLVED")),
        ("Folksonomy: the two backlog-graph jobs share a cluster",
         by["Show the ind"]["induce"]["cluster"] == by["Show backlog"]["induce"]["cluster"]),
        ("Folksonomy: unrelated jobs do not join it", by["Gate the htm"]["induce"]["cluster"] != by["Show the ind"]["induce"]["cluster"]),
        ("Accountant: a moved belief outweighs a flat one",
         by["Show the ind"]["induce"]["outcome_weight"] > by["Gate the htm"]["induce"]["outcome_weight"]),
        ("rows: every row is OPEN, human consent, unique id",
         all(r["state"] == "OPEN" and r["consent"] == "human" for r in out) and len({r["id"] for r in out}) == len(out)),
        ("rows: order is 1..n", sorted(r["order"] for r in out) == list(range(1, len(out) + 1))),
        ("backlog_graph reads the rows and agrees on NOT-RESOLVED",
         {n["id"]: n["tool"] for n in bg.build(out, __import__("datetime").date(2026, 1, 3), catalog=names, files=files)["nodes"]}
         [by["Do a thing"]["id"]] == "NOT-RESOLVED"),
        ("extract: markdown section 7 only, tool hint kept", [c["tool_hint"] for c in mdc] == ["scripts/page_gate.py", None]),
        ("extract: next_steps fallback skips DONE", [c["jtbd"] for c in extract(
            {"next_steps": [{"text": "DONE 1-1: x"}, {"text": "Send the note"}]})["candidates"]] == ["Send the note"]),
    ]
    for label, cond in checks:
        print(("PASS " if cond else "FAIL ") + label)
        ok &= bool(cond)
    print("self-test: %s (%d checks)" % ("OK" if ok else "FAILED", len(checks)))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", nargs="?", choices=["extract", "snap", "cluster", "rank", "rows", "all"])
    ap.add_argument("--data", help="recoil SSOT JSON or recoil-close markdown (extract, all)")
    ap.add_argument("--in", dest="inp", help="stage input JSON (default stdin)")
    ap.add_argument("--no-librarian", action="store_true", help="skip Operator 21 prior-art retrieval")
    ap.add_argument("--budget", type=int, default=4000, help="Librarian context budget in bytes")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.stage:
        ap.print_help()
        return 2
    if a.stage in ("extract", "all"):
        if not a.data:
            ap.error("--data is required for %s" % a.stage)
        text = Path(a.data).read_text()
        src = {"md": text} if a.data.endswith(".md") else {"data": json.loads(text)}
        if a.stage == "extract":
            print(json.dumps(extract(**src), indent=1, ensure_ascii=False))
        else:
            for r in run_all(librarian=not a.no_librarian, budget=a.budget, **src):
                print(json.dumps(r, ensure_ascii=False))
        return 0
    env = json.loads(Path(a.inp).read_text() if a.inp else sys.stdin.read())
    if a.stage == "rows":
        for r in rows(env):
            print(json.dumps(r, ensure_ascii=False))
        return 0
    fn = {"snap": snap, "cluster": cluster, "rank": lambda e: rank(e, not a.no_librarian, a.budget)}[a.stage]
    print(json.dumps(fn(env), indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
