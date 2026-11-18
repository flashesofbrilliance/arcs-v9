#!/usr/bin/env python3
"""gate_ladder_page: render the gate ladder page (design spec, recommendation, plan) from data, never hand-typed counts.

In:   runtime/specs/gate-taxonomy.json            the ladder (scripts/gate_taxonomy_emit.py)
      _QUEUE/induced-backlog.jsonl                 rows whose id starts with gate- or typesafe-residue (the graph)
      scripts/gate_shadow_eval.py                  eval counts, pinned at the commit that last changed the ladder file
      _ARTIFACTS/gate-taxonomy/body.tpl       hand content (judgment: suggestions, findings) with {{slots}}
      _ARTIFACTS/gate-taxonomy/page.css            layout; colours and type from the kit tokens only
      src/ui-kit/recoil-report/_tokens.css         inlined verbatim
      src/ui-kit/recoil-report/53-cold-read.html   kit primitives 27, 31, 53 cut verbatim from their @prim blocks
      _PATTERNS/arcs-artifact-css-base.css         inlined verbatim
Out:  _ARTIFACTS/gate-taxonomy/index.html          full document (repo gates: page_gate, wrap-lint, token gate)
      --fragment PATH                              the page without its document skeleton, for an Artifact publish
                                                   (the publish adds its own); never committed, it is not a page

  python3 scripts/gate_ladder_page.py                    write index.html
  python3 scripts/gate_ladder_page.py --fragment P       also write the publish fragment to P (e.g. a scratch dir)
  python3 scripts/gate_ladder_page.py --check            exit 1 if index.html differs from a rebuild
Stdlib only. Re-run after gate_taxonomy_emit.py or a change to the gate rows.
"""
import argparse
import html
import importlib.util
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, "_ARTIFACTS", "gate-taxonomy")
TAX = "runtime/specs/gate-taxonomy.json"
PREFIXES = ("gate-", "typesafe-residue")
DOOR_ONE = "one-way"


def rd(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def git(*a):
    return subprocess.run(("git",) + a, cwd=ROOT, capture_output=True, text=True).stdout.strip()


def esc(s):
    return html.escape(str(s), quote=False)


def pinned():
    """(sha, date) of the last commit that changed the ladder file; HEAD when it is not committed yet."""
    out = git("log", "-1", "--format=%H %cs", "--", TAX) or git("log", "-1", "--format=%H %cs")
    sha, date = out.split()
    return sha, date


def eval_counts(rev):
    spec = importlib.util.spec_from_file_location("gse", os.path.join(ROOT, "scripts", "gate_shadow_eval.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.main_run(rev, "")["counts"]


def gate_rows():
    rows = [json.loads(l) for l in rd("_QUEUE/induced-backlog.jsonl").splitlines() if l.strip()]
    return [r for r in rows if r["id"].startswith(PREFIXES)]


def waves(rows):
    ids = {r["id"] for r in rows}
    by = {r["id"]: r for r in rows}
    memo = {}

    def depth(i, seen=()):
        if i in memo:
            return memo[i]
        deps = [d for d in by[i].get("depends_on", []) if d in ids and d not in seen]
        memo[i] = 0 if not deps else 1 + max(depth(d, seen + (i,)) for d in deps)
        return memo[i]
    return {r["id"]: depth(r["id"]) for r in rows}


def downstream(rows, root):
    kids = {}
    for r in rows:
        for d in r.get("depends_on", []):
            kids.setdefault(d, set()).add(r["id"])
    seen, stack = set(), [root]
    while stack:
        for k in kids.get(stack.pop(), ()):
            if k not in seen:
                seen.add(k)
                stack.append(k)
    return len(seen)


def ladder_html(lad, tax):
    v = {}
    for a in tax["atoms"]:
        v[a["verdict"]] = v.get(a["verdict"], 0) + 1
    verdicts = ", ".join(f"{n} {k}" for k, n in sorted(v.items(), key=lambda x: -x[1]))
    cis = len([o for o in tax["organisms"] if o["organism"].startswith("ci:")])
    design = [
        ("Pages", lad["pages"], "from the readers of gate-chains.json: " + "; ".join(p["page"] for p in tax["pages"])),
        ("Templates", lad["templates"], "the invocation shape of each atom"),
        ("Organisms", lad["organisms"], f"pre-commit plus {cis} CI jobs, from the hook and workflows"),
        ("Molecules", lad["molecules"], "gate scripts, from the hook's git history"),
        ("Atoms", lad["atoms"], f"verdict lines: {verdicts}"),
    ]
    prims = lad["primitives_with_evidence"]
    arcs = [
        ("Protocols", lad["protocols"], ", ".join(p["protocol"] for p in tax["protocols"]) + " (each names its organisms)", False),
        ("Operators", f"{lad['molecules_with_operator']} of {lad['molecules']}",
         "no gate script imports a periodic-table operator" if not lad["molecules_with_operator"] else "gate scripts that import an operator", not lad["molecules_with_operator"]),
        ("ADRs", f"{lad['molecules_with_adr']} of {lad['molecules']}",
         "gate scripts whose header or wiring commit cites an ADR; every atom carries the sha that wrote it", True),
        ("Primitives", f"{len(prims)} of 7",
         f"named in the hook: {', '.join(p.title().replace('_', ' ') for p in prims) or 'none'}; templates ruled {lad['templates_ruled']} of {lad['templates']}", len(prims) < 7),
    ]

    def li(rung, n, frm, warn=False):
        return (f'<li><span class="rung">{rung}</span><span class="n{" warn" if warn else ""}">{esc(n)}</span>'
                f'<span class="from">{esc(frm)}</span></li>')
    d = "".join(li(*x) for x in design)
    a = "".join(li(*x) for x in arcs)
    return (f'<figure class="ladder" aria-label="Design ladder"><figcaption class="section-label">Design ladder</figcaption><ol>{d}</ol></figure>',
            f'<figure class="ladder" aria-label="ARCS ladder"><figcaption class="section-label">ARCS ladder</figcaption><ol>{a}</ol></figure>')


READ_FROM = {"check": "none of the shapes below", "derived-freshness": "<code>--check</code>", "gate": "name has gate or guard",
             "lint": "name has lint", "self-test": "<code>--self-test</code>", "record-integrity": "<code>--staged</code>"}


def template_rows(tax):
    out = []
    for t in tax["templates"]:
        ev = ", ".join(p.title().replace("_", " ") for p in t["primitive_evidence"]) or "none"
        out.append(f'<tr><td>{esc(t["template"])}</td><td class="num">{t["atoms"]}</td><td class="num">{t["molecules"]}</td>'
                   f'<td>{READ_FROM.get(t["template"], "")}</td><td>{esc(ev)}</td></tr>')
    return "<tbody>" + "".join(out) + "</tbody>"


def state_class(r):
    return {"DONE": "done", "HELD": "held", "BLOCKED": "held"}.get(r["state"], "open")


def graph(rows, wv):
    cols = {}
    for r in sorted(rows, key=lambda r: (wv[r["id"]], r["id"])):
        cols.setdefault(wv[r["id"]], []).append(r)
    ncol = max(cols) + 1
    # node width fits the longest id in mono at body size (about 0.6em per glyph at 14.8px), so no label overflows
    NW = 28 + int(max(len(r["id"]) for r in rows) * 0.6 * 14.8)
    NH, GAP, TOP, CG = 52, 22, 40, 48
    W = 40 + ncol * NW + (ncol - 1) * CG
    colx = [20 + i * (NW + CG) for i in range(ncol)]
    pos = {}
    for c, rs in cols.items():
        for k, r in enumerate(rs):
            pos[r["id"]] = (colx[c], TOP + k * (NH + GAP))
    H = TOP + max(len(rs) for rs in cols.values()) * (NH + GAP) + 10
    labels = "".join(f'<text x="{colx[c]}" y="24">Wave {c}</text>' for c in range(ncol))
    edges = []
    for r in rows:
        for d in r.get("depends_on", []):
            if d in pos:
                x1, y1 = pos[d][0] + NW, pos[d][1] + NH // 2
                x2, y2 = pos[r["id"]][0], pos[r["id"]][1] + NH // 2
                mx = (x1 + x2) // 2
                edges.append(f'<path d="M{x1} {y1} C {mx} {y1}, {mx} {y2}, {x2} {y2}"/>')
    nodes = []
    for r in rows:
        x, y = pos[r["id"]]
        door = r.get("door", "two-way")
        sub = f'{r["state"]} · {door}' + (" (held on Zach)" if r["state"] == "HELD" and "Zach" in r.get("status_note", "") else "")
        nodes.append(f'<g class="node {state_class(r)}"><rect x="{x}" y="{y}" width="{NW}" height="{NH}" rx="6"/>'
                     f'<text x="{x + 14}" y="{y + 22}">{esc(r["id"])}</text><text class="s" x="{x + 14}" y="{y + 40}">{esc(sub)}</text></g>')
    desc = "; ".join(f'{r["id"]} ({r["state"]}, wave {wv[r["id"]]})' for r in rows)
    return (f'<svg class="graph" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Backlog graph: {esc(desc)}">'
            f'<g class="col-label">{labels}</g><g class="edges">{"".join(edges)}</g>{"".join(nodes)}</svg>')


def row_rows(rows, wv):
    out = []
    for r in sorted(rows, key=lambda r: (wv[r["id"]], r["id"])):
        first = r["jtbd"].split(": ")[0].split(". ")[0]
        done = (r.get("gates") or ["(none)"])[0]
        out.append(f'<tr><td>{esc(r["id"])}</td><td>{esc(r["state"])}</td><td>{esc(first)}</td><td><code>{esc(done)}</code></td></tr>')
    return ("<thead><tr><th>Row</th><th>State</th><th>Delivers</th><th>Done when</th></tr></thead><tbody>" + "".join(out) + "</tbody>")


PRIMS = ("27-section-label", "31-callout", "53-cold-read")  # kit primitives this page is assembled from
PRIM_SRC = "src/ui-kit/recoil-report/53-cold-read.html"     # carries all three between @prim markers


def kit_prims():
    """The kit's own CSS for each primitive, cut verbatim from its @prim:begin/@prim:end block (never copied by hand)."""
    src, out = rd(PRIM_SRC), []
    for name in PRIMS:
        a, b = f"/* @prim:begin {name} */", f"/* @prim:end {name} */"
        i, j = src.index(a), src.index(b) + len(b)
        out.append(src[i:j])
    return "\n".join(out)


def build():
    tax = json.loads(rd(TAX))
    lad = tax["ladder"]
    sha, date = pinned()
    counts = eval_counts(sha)
    rows = gate_rows()
    wv = waves(rows)
    dl, al = ladder_html(lad, tax)
    body = rd("_ARTIFACTS/gate-taxonomy/body.tpl")
    # the rows table template carries its own thead; swap the hand thead for the generated one
    i = body.index("<thead><tr><th>Row</th>")
    j = body.index("{{ROW_ROWS}}")
    body = body[:i] + body[j:]
    slots = {
        "DESIGN_LADDER": dl, "ARCS_LADDER": al, "TEMPLATE_ROWS": template_rows(tax), "GRAPH": graph(rows, wv),
        "ROW_ROWS": row_rows(rows, wv), "atoms": lad["atoms"], "molecules": lad["molecules"], "templates_n": lad["templates"],
        "fix_followed": counts.get("fix-followed", 0), "unrevealed": f'{counts.get("unrevealed", 0):,}',
        "rows_n": len(rows), "waves_n": max(wv.values()) + 1,
        "ruling_downstream": downstream(rows, "gate-template-primitive-ruling"),
        "generated_at": f"{date} (ladder commit {sha[:8]})",
        "check_atoms": next((t["atoms"] for t in tax["templates"] if t["template"] == "check"), 0),
        "check_molecules": next((t["molecules"] for t in tax["templates"] if t["template"] == "check"), 0),
    }
    for k, v in slots.items():
        body = body.replace("{{" + k + "}}", str(v))
    assert "{{" not in body, body[body.index("{{"):body.index("{{") + 40]
    tok, base, page = rd("src/ui-kit/recoil-report/_tokens.css"), rd("_PATTERNS/arcs-artifact-css-base.css"), rd("_ARTIFACTS/gate-taxonomy/page.css")
    prims = kit_prims()
    head = ('<title>The Gate Ladder</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
            f'<style>\n{tok}\n{base}\n{prims}\n{page}\n</style>\n')
    frag = head + body
    full = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + head + "</head>\n<body>\n" + body + "</body>\n</html>\n")
    return {"index.html": full, "artifact.html": frag}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--fragment", metavar="PATH")
    a = ap.parse_args()
    built = build()
    if a.fragment:
        open(a.fragment, "w", encoding="utf-8").write(built.pop("artifact.html"))
        print(f"gate_ladder_page: fragment -> {a.fragment}")
    out = {"index.html": built["index.html"]}
    if a.check:
        stale = [n for n, t in out.items()
                 if not os.path.exists(os.path.join(DIR, n)) or open(os.path.join(DIR, n), encoding="utf-8").read() != t]
        print("gate_ladder_page: fresh" if not stale else f"gate_ladder_page: stale {stale}; run python3 scripts/gate_ladder_page.py")
        return 1 if stale else 0
    for n, t in out.items():
        open(os.path.join(DIR, n), "w", encoding="utf-8").write(t)
    print("gate_ladder_page: wrote " + ", ".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
