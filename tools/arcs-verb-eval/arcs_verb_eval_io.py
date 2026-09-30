#!/usr/bin/env python3
"""
arcs_verb_eval_io.py - data in and data out for arcs-verb-eval. Stdlib only.

INGEST (data in) turns a source into the artifacts the verbs read:
  ipynb   a Jupyter notebook (TensorFlow, PyTorch, anything: it is only JSON). Every
          markdown sentence that states a number becomes a claim; the claim cites the
          code cell whose output it matches. Match -> verified, number not in any output
          -> gap, notebook saved without outputs -> unresolved.
  table   a CSV or JSONL of claims with columns id,text,src,stakes,verdict,severity.
  Writes: analysis.html, assessment.html, evidence.jsonl (+ manifest.json).
  --mutate N also writes N corrupted copies (source stripped, number drifted) as
  negative fixtures, so a synthetic set tests fails-on-bad as well as passes-on-good.

EXPORT (data out) reads a directory of <verb>.json prints and writes:
  jsonl     one row per gate (for warehouses, notebooks, pandas)
  csv       same rows, spreadsheet-ready
  md        a human report
  junit     JUnit XML, so any CI shows gates as test cases
  receipt   the AGENTS.md decision_receipt form: passed gates -> what_confirmed,
            failed/skipped gates and unscored rubric rows -> what_unconfirmed
"""
from __future__ import annotations

import csv
import html
import io
import json
import random
import re
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

NUM_RE = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(%?)")
SENT_RE = re.compile(r"(?<=[.!?])\s+")
VERBS = ("analysis", "assessment", "evaluation", "synthesis", "recapitulation")


# ---- ingest --------------------------------------------------------------------------
def _cell_text(cell: dict, key: str = "source") -> str:
    v = cell.get(key, "")
    return "".join(v) if isinstance(v, list) else str(v)


def _outputs_text(cell: dict) -> str:
    parts = []
    for o in cell.get("outputs", []):
        if "text" in o:
            parts.append(_cell_text(o, "text"))
        for mime in ("text/plain", "text/markdown"):
            if mime in o.get("data", {}):
                parts.append(_cell_text(o["data"], mime))
    return "\n".join(parts)


def _nums(text: str) -> set[str]:
    out = set()
    for n, _pct in NUM_RE.findall(text):
        out.add(n.rstrip("0").rstrip(".") if "." in n else n)
    return out


def claims_from_ipynb(path: Path) -> list[dict]:
    nb = json.loads(path.read_text())
    cells = nb.get("cells", [])
    code = [(i, _outputs_text(c)) for i, c in enumerate(cells) if c.get("cell_type") == "code"]
    has_outputs = any(t.strip() for _, t in code)
    claims = []
    for i, c in enumerate(cells):
        if c.get("cell_type") != "markdown":
            continue
        for sent in SENT_RE.split(_cell_text(c)):
            sent = " ".join(sent.replace("#", " ").split())
            nums = _nums(sent)
            if not nums or len(sent) < 12:
                continue
            match = next((j for j, out in code if nums & _nums(out)), None)
            src = f"{path.name}#cell-{match}" if match is not None else f"{path.name}#cell-{i}"
            verdict = "verified" if match is not None else ("gap" if has_outputs else "unresolved")
            claims.append({"id": f"c{len(claims) + 1}", "text": sent, "src": [src], "stakes": "normal",
                           "verdict": verdict, "severity": "low" if verdict == "verified" else "medium",
                           "evidence": (dict(code).get(match, "") or "")[:200] if match is not None else ""})
    return claims


def claims_from_table(path: Path) -> list[dict]:
    if path.suffix == ".csv":
        rows = list(csv.DictReader(path.open()))
    else:
        rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    out = []
    for n, r in enumerate(rows, 1):
        src = r.get("src") or ""
        src = src if isinstance(src, list) else [s.strip() for s in str(src).split(",") if s.strip()]
        out.append({"id": r.get("id") or f"c{n}", "text": r.get("text", ""), "src": src,
                    "stakes": r.get("stakes") or "normal", "verdict": r.get("verdict") or "unresolved",
                    "severity": r.get("severity") or "medium", "evidence": r.get("evidence", "")})
    return out


def _span(c: dict, assess: bool) -> str:
    a = f'class="claim" data-id={quoteattr(c["id"])} data-src={quoteattr(",".join(c["src"]))}'
    if c["stakes"] != "normal":
        a += f' data-stakes={quoteattr(c["stakes"])}'
    if assess:
        a += f' data-verdict={quoteattr(c["verdict"])} data-severity={quoteattr(c["severity"])}'
        if c.get("evidence"):
            a += f' data-evidence={quoteattr(" ".join(str(c["evidence"]).split()))}'
    return f"  <li><span {a}>{html.escape(c['text'])}</span></li>"


def write_artifacts(claims: list[dict], outdir: Path, title: str) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)
    counts = "/".join(str(sum(c["verdict"] == v for c in claims)) for v in ("verified", "gap", "unresolved"))
    head = f"<!doctype html><meta charset=utf-8><title>{html.escape(title)}</title>\n"
    (outdir / "analysis.html").write_text(head + "<ul>\n" + "\n".join(_span(c, False) for c in claims) + "\n</ul>\n")
    (outdir / "assessment.html").write_text(head + f'<ul data-summary="{counts}">\n' + "\n".join(_span(c, True) for c in claims) + "\n</ul>\n")
    with (outdir / "evidence.jsonl").open("w") as fh:
        for s in sorted({s for c in claims for s in c["src"]}):
            fh.write(json.dumps({"source": s}) + "\n")
    manifest = {"title": title, "claims": len(claims), "summary_verified_gap_unresolved": counts,
                "files": ["analysis.html", "assessment.html", "evidence.jsonl"]}
    (outdir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def mutate(claims: list[dict], n: int, seed: int = 7) -> list[tuple[str, list[dict]]]:
    rng, out = random.Random(seed), []
    for k in range(n):
        cs = [dict(c, src=list(c["src"])) for c in claims]
        if not cs:
            break
        victim = rng.choice(cs)
        if k % 2 == 0:
            victim["src"], kind = [], "unsourced"
        else:
            victim["text"] = NUM_RE.sub(lambda m: str(int(float(m.group(1))) + 1) + m.group(2), victim["text"], count=1)
            kind = "number-drift"
        out.append((f"{kind}-{victim['id']}", cs))
    return out


def ingest(src: str, outdir: str, fmt: str | None = None, mutations: int = 0) -> dict:
    p, out = Path(src), Path(outdir)
    fmt = fmt or ("ipynb" if p.suffix == ".ipynb" else "table")
    claims = claims_from_ipynb(p) if fmt == "ipynb" else claims_from_table(p)
    man = write_artifacts(claims, out, p.name)
    man["negatives"] = []
    for name, cs in mutate(claims, mutations):
        write_artifacts(cs, out / "negatives" / name, f"{p.name} [{name}]")
        man["negatives"].append(name)
    (out / "manifest.json").write_text(json.dumps(man, indent=2) + "\n")
    return man


# ---- export --------------------------------------------------------------------------
def load_prints(d: str) -> list[dict]:
    return [json.loads((Path(d) / f"{v}.json").read_text()) for v in VERBS if (Path(d) / f"{v}.json").exists()]


def gate_rows(prints: list[dict]) -> list[dict]:
    return [{"verb": p["verb"], "fate": p["fate"], "gate": g["id"],
             "status": "skipped" if g.get("skipped") else ("pass" if g["ok"] else "fail"),
             "evidence": g["evidence"], "artifact": p.get("artifact")} for p in prints for g in p["gates"]]


def export(prints_dir: str, fmt: str, question: str = "", operator: str = "arcs-verb-eval") -> str:
    prints = load_prints(prints_dir)
    rows = gate_rows(prints)
    if fmt == "jsonl":
        return "".join(json.dumps(r) + "\n" for r in rows)
    if fmt == "csv":
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=list(rows[0]) if rows else ["verb"])
        w.writeheader()
        w.writerows(rows)
        return buf.getvalue()
    if fmt == "md":
        lines = ["# arcs-verb-eval report", "", "| Verb | Fate | Failed gates |", "|---|---|---|"]
        lines += [f"| {p['verb']} | {p['fate']} | {', '.join(p['failed']) or 'none'} |" for p in prints]
        lines += ["", "## Gates", "", "| Verb | Gate | Status | Evidence |", "|---|---|---|---|"]
        lines += [f"| {r['verb']} | {r['gate']} | {r['status']} | {r['evidence'].replace('|', '/')} |" for r in rows]
        return "\n".join(lines) + "\n"
    if fmt == "junit":
        fails = sum(r["status"] == "fail" for r in rows)
        out = [f'<?xml version="1.0" encoding="UTF-8"?>\n<testsuites name="arcs-verb-eval" tests="{len(rows)}" failures="{fails}">']
        for p in prints:
            prs = [r for r in rows if r["verb"] == p["verb"]]
            out.append(f'  <testsuite name={quoteattr(p["verb"])} tests="{len(prs)}" failures="{sum(r["status"] == "fail" for r in prs)}">')
            for r in prs:
                inner = f'<failure message={quoteattr(r["evidence"])}/>' if r["status"] == "fail" else ("<skipped/>" if r["status"] == "skipped" else "")
                out.append(f'    <testcase classname={quoteattr(p["verb"])} name={quoteattr(r["gate"])}>{inner}</testcase>')
            out.append("  </testsuite>")
        return "\n".join(out + ["</testsuites>"]) + "\n"
    if fmt == "receipt":
        confirmed = [f"{r['verb']}:{r['gate']} pass ({r['evidence']})" for r in rows if r["status"] == "pass"]
        unconfirmed = [f"{r['verb']}:{r['gate']} {r['status']} ({r['evidence']})" for r in rows if r["status"] != "pass"]
        unconfirmed += [f"{p['verb']}:rubric:{x['row']} unscored" for p in prints for x in p["rubric"] if x["score"] is None]
        return json.dumps({"question": question or "Did the artifact family clear the five-verb print schedule?",
                           "horizon": "today", "stakes": "medium", "mode": "PLAN",
                           "what_confirmed": confirmed, "what_unconfirmed": unconfirmed, "operator": operator,
                           "refs": [p.get("artifact") for p in prints],
                           "_note": "draft row for public.decision_receipt; event_at is set at insert time"}, indent=2) + "\n"
    raise ValueError(f"unknown export format {fmt!r}")


def self_test() -> int:
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="arcs-verb-eval-io-"))
    nb = {"cells": [
        {"cell_type": "markdown", "source": ["# Results\n", "The model reaches 94.2% accuracy on the test split. Training took 12 epochs."]},
        {"cell_type": "code", "source": ["model.evaluate(x, y)"], "outputs": [{"output_type": "stream", "text": ["accuracy: 94.2\n"]}]},
        {"cell_type": "markdown", "source": ["Latency is 3 ms per batch on a laptop."]}]}
    (tmp / "nb.ipynb").write_text(json.dumps(nb))
    man = ingest(str(tmp / "nb.ipynb"), str(tmp / "out"), mutations=2)
    ok = []
    cl = claims_from_ipynb(tmp / "nb.ipynb")
    ok.append(("notebook claims extracted", len(cl) == 3))
    ok.append(("matching output -> verified", cl[0]["verdict"] == "verified"))
    ok.append(("unmatched number -> gap", cl[1]["verdict"] == "gap" and cl[2]["verdict"] == "gap"))
    ok.append(("negatives written", len(man["negatives"]) == 2))
    import arcs_verb_eval as core
    good = core.evaluate("analysis", (tmp / "out/analysis.html").read_text())
    ok.append(("ingested analysis passes", good["ok"]))
    bad = core.evaluate("analysis", (tmp / "out/negatives" / man["negatives"][0] / "analysis.html").read_text())
    ok.append(("unsourced negative fails", "every-claim-sourced" in bad["failed"]))
    drift = next(n for n in man["negatives"] if n.startswith("number-drift"))
    up = core.evaluate("analysis", (tmp / "out/negatives" / drift / "analysis.html").read_text())
    dr = core.evaluate("assessment", (tmp / "out/negatives" / drift / "assessment.html").read_text(), upstream=up)
    ok.append(("number-drift negative fails assessment", "verified-numbers-in-evidence" in dr["failed"]))
    ok.append(("clean ingest passes assessment", core.evaluate("assessment", (tmp / "out/assessment.html").read_text(), upstream=good)["ok"]))
    (tmp / "prints").mkdir()
    (tmp / "prints/analysis.json").write_text(json.dumps(bad))
    j = export(str(tmp / "prints"), "junit")
    ok.append(("junit carries the failure", "<failure" in j))
    r = json.loads(export(str(tmp / "prints"), "receipt"))
    ok.append(("receipt: failed gate lands in what_unconfirmed only", any("every-claim-sourced" in x for x in r["what_unconfirmed"]) and not any("every-claim-sourced" in x for x in r["what_confirmed"])))
    ok.append(("csv has a header and rows", export(str(tmp / "prints"), "csv").count("\n") >= 2))
    for name, cond in ok:
        print(f"  {'ok  ' if cond else 'FAIL'}  {name}")
    failed = sum(not c for _, c in ok)
    print(f"\n{len(ok) - failed} passed, {failed} failed")
    return 1 if failed else 0
