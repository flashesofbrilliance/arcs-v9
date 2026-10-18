#!/usr/bin/env python3
"""canon_claims_report: REPORT-ONLY list of quantified claims in _CANON/**/*.md and in
operators/arcs_primitives.py docstrings that no evidence ledger covers.

Reuses provenance_lint's METRIC and ledger format (sibling evidence.jsonl, nearest ancestor wins).
Writes nothing but the report you redirect it to; never edits canon text.

  python3 scripts/canon_claims_report.py              # markdown table to stdout
  python3 scripts/canon_claims_report.py --self-test  # known-bad + known-good fixtures
"""
import ast, os, re, subprocess, sys, tempfile, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import provenance_lint as pl

# statistical forms provenance_lint's METRIC does not cover (additive here; the gate itself is untouched)
EXTRA = re.compile(r"\b[rR]\s?=\s?-?\d?\.\d+|\bp\s?[<=]\s?0?\.\d+|\bBrier[^.\n]{0,40}?\d\.\d+(?:\s?(?:to|->|→)\s?\d\.\d+)?|\bchi-?square\b", re.I)

def nearest_ledger(path, stop):
    d = os.path.dirname(os.path.abspath(path))
    stop = os.path.abspath(stop)
    per_file = os.path.splitext(path)[0] + ".evidence.jsonl"
    if os.path.exists(per_file):
        return per_file
    while True:
        cand = os.path.join(d, "evidence.jsonl")
        if os.path.exists(cand):
            return cand
        if d == stop or d == os.path.dirname(d):
            return None
        d = os.path.dirname(d)

def docstring_lines(src):
    """1-indexed line numbers that belong to module/class/function docstrings."""
    lines = set()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
               and isinstance(body[0].value.value, str):
                lines.update(range(body[0].lineno, body[0].end_lineno + 1))
    return lines

def scan(path, ledger_root, only_lines=None):
    text = open(path, encoding="utf-8", errors="replace").read()
    ledger = nearest_ledger(path, ledger_root)
    pats = pl.load_ledger(ledger) if ledger else []
    unval = pl.load_unvalidated(ledger) if ledger else []
    proj = pl.load_projection(ledger) if ledger else []
    rows = []
    for i, line in enumerate(text.splitlines(), 1):
        if only_lines is not None and i not in only_lines:
            continue
        for m in list(pl.METRIC.finditer(line)) + list(EXTRA.finditer(line)):
            tok = m.group(0).strip()
            if pl.YEAR.match(tok):
                continue
            covered = any(rx.search(line) and any(cm.start() <= m.start() and m.end() <= cm.end()
                          for cm in rx.finditer(line)) for rx, _ in pats)
            if not covered:
                marked = any(any(c.start() <= m.start() and m.end() <= c.end() for c in rx.finditer(line))
                             for rx, _ in unval)
                planned = any(any(c.start() <= m.start() and m.end() <= c.end() for c in rx.finditer(line))
                              for rx, _ in proj)
                rows.append((path, i, tok, line.strip()[:140],
                             "UNVALIDATED" if marked else "PROJECTION" if planned else "UNCOVERED"))
    return rows

def run(canon="_CANON", prim="operators/arcs_primitives.py"):
    rows = []
    for dp, _, fs in os.walk(canon):
        for fn in sorted(fs):
            if fn.endswith(".md"):
                rows += scan(os.path.join(dp, fn), canon)
    if os.path.exists(prim):
        src = open(prim, encoding="utf-8").read()
        rows += scan(prim, os.path.dirname(prim), docstring_lines(src))
    return rows

def render(rows):
    out = ["| file:line | claim token | state | line (truncated) |", "|---|---|---|---|"]
    for path, ln, tok, line, state in sorted(rows):
        out.append(f"| {path}:{ln} | `{tok}` | {state} | {line.replace('|', '/').replace('_DECISIONS/', '')} |")
    return "\n".join(out)

def self_test():
    ok = True
    with tempfile.TemporaryDirectory() as t:
        os.makedirs(os.path.join(t, "c"))
        open(os.path.join(t, "c", "evidence.jsonl"), "w").write(json.dumps({"pattern": r"87%", "source": "x"}) + "\n")
        open(os.path.join(t, "c", "good.md"), "w").write("87% held. Year 2026.\n")
        open(os.path.join(t, "c", "bad.md"), "w").write("87% held and 76% accuracy.\n")
        g = scan(os.path.join(t, "c", "good.md"), t)
        b = scan(os.path.join(t, "c", "bad.md"), t)
        open(os.path.join(t, "c", "u.md"), "w").write("87% held and 76% accuracy.\n")
        open(os.path.join(t, "c", "u.evidence.jsonl"), "w").write(
            json.dumps({"pattern": "87%", "status": "unvalidated", "source": "audit:x"}) + "\n")
        u = scan(os.path.join(t, "c", "u.md"), t)
        open(os.path.join(t, "c", "p.md"), "w").write("Priced at $7.5M and 87% held.\n")
        open(os.path.join(t, "c", "p.evidence.jsonl"), "w").write(
            json.dumps({"pattern": r"\$7\.5M", "status": "projection", "source": "plan:x"}) + "\n")
        pj = scan(os.path.join(t, "c", "p.md"), t)
        for name, cond in (("good fixture: no uncovered claims", g == []),
                           ("bad fixture: 76% flagged, 87% covered", [r[2] for r in b] == ["76%"]),
                           ("unvalidated fixture: 87% UNVALIDATED, 76% UNCOVERED",
                            sorted((r[2], r[4]) for r in u) == [("76%", "UNCOVERED"), ("87%", "UNVALIDATED")]),
                           ("projection fixture: $7.5M PROJECTION, 87% UNCOVERED",
                            sorted((r[2], r[4]) for r in pj) == [("$7.5M", "PROJECTION"), ("87%", "UNCOVERED")])):
            print(("PASS " if cond else "FAIL ") + name); ok &= cond
    return 0 if ok else 1

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    print(render(run()))
