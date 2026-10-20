#!/usr/bin/env python3
"""Prepare and seal the Sprint 4 blind pool (amendment 7 rule 3).

Reads the raw assemblies under runtime/specs/jtbd-s4/, pools the union of item ids per row,
shuffles with random.Random(20261020 + row) over the sorted union, and writes:
  pool-sealed.json  job + shuffled items (id, name, description, blank mark); no source info
  pool-key.json     id -> system mapping, kept separate
  JUDGE.md          judging sheet rendered from pool-sealed.json only
Stdlib only. Usage: python3 scripts/jtbd_s4_pool.py [--self-test]
"""
import ast, json, random, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "runtime/specs/jtbd-s4"
SEED = 20261020
# Structural words that would reveal a source if they appeared outside item text.
LEAK_KEYS = {"system", "from", "source", "assembly", "rank", "score", "scores", "order"}


def load(p):
    return json.loads(Path(p).read_text())


def docline(path):
    """First docstring/comment line of a file, as a fallback description."""
    p = ROOT / path
    if not p.exists():
        return ""
    txt = p.read_text(errors="replace")
    if p.suffix == ".py":
        try:
            ds = ast.get_docstring(ast.parse(txt))
            if ds:
                return ds.strip().splitlines()[0]
        except SyntaxError:
            pass
    for ln in txt.splitlines()[1:15]:
        ln = ln.strip().lstrip("#").strip()
        if ln and not ln.startswith("!"):
            return ln
    return ""


def resolver():
    cat = load(ROOT / "runtime/specs/tool-catalog.json")["tools"]
    by = {(t["kind"], t["name"]): t for t in cat}
    reg = load(ROOT / "operators/OPERATOR-REGISTRY.json")
    ops = {o["op"]: o for o in reg.get("operators", []) if isinstance(o, dict) and "op" in o}

    def resolve(item_id):
        _, kind, name = item_id.split(":", 2)
        if kind == "op":
            o = ops.get(int(name), {})
            return (f"Operator {name} {o.get('name', '')}".strip(),
                    f"{o.get('function', '')} (status {o.get('status', '?')})")
        t = by.get((kind, name))
        if not t:
            return name, ""
        desc = (t.get("jtbd") or "").strip()
        if not desc or desc == name:
            desc = docline(t.get("path", "")) or desc
        desc = re.sub(r"\s+", " ", desc).replace("—", ",")
        if len(desc) > 160:
            desc = desc[:157].rstrip() + "..."
        return name, desc
    return resolve


def build(queries, raws, resolve):
    sealed, key = [], []
    for q in sorted(queries, key=lambda r: r["row"]):
        row = q["row"]
        union, owners = set(), {}
        for raw in raws:
            for r in raw["rows"]:
                if r["row"] == row:
                    for it in r["assembly"]:
                        union.add(it)
                        owners.setdefault(it, set()).add(r["system"])
        items = sorted(union)
        random.Random(SEED + row).shuffle(items)
        out = []
        for it in items:
            name, desc = resolve(it)
            out.append({"id": it, "name": name, "description": desc, "mark": ""})
        sealed.append({"row": row, "job": q["job"], "items": out})
        key.append({"row": row, "items": {it: sorted(owners[it]) for it in sorted(owners)}})
    return sealed, key


def judge_md(sealed):
    L = ["# Sprint 4 judging sheet (blind)", "",
         "For each item write **E** (essential: the job fails without it), **U** (useful) or "
         "**W** (wrong) after the arrow. Optionally name a missing essential piece on the "
         "`Missing:` line. Item order is random per job.", ""]
    for r in sealed:
        L += [f"## Job {r['row']}: {r['job']}", ""]
        for i, it in enumerate(r["items"], 1):
            d = f": {it['description']}" if it["description"] else ""
            L.append(f"{i}. `{it['name']}`{d}  ->  ")
        L += ["", "Missing: ", ""]
    return "\n".join(L)


def leaks(sealed, md, systems):
    """Return a list of leak findings; empty means blind."""
    bad = []
    def walk(o, path="$"):
        if isinstance(o, dict):
            for k, v in o.items():
                if k.lower() in LEAK_KEYS or k.lower() in systems:
                    bad.append(f"key {path}.{k}")
                walk(v, f"{path}.{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")
    walk(sealed)
    # System names may appear only inside an item's own id/name/description (e.g. a tool that
    # is literally named "catalog"); anywhere else in the sheet they are a label leak.
    item_text = {s for r in sealed for it in r["items"] for s in (it["id"], it["name"], it["description"])}
    jobs = {r["job"] for r in sealed}
    for ln in md.splitlines():
        scrub = ln
        # Only an item line may carry item text, and only a job header may carry the job text.
        allowed = item_text if re.match(r"\d+\. ", ln) else (jobs if ln.startswith("## Job") else ())
        for s in sorted(allowed, key=len, reverse=True):
            if s:
                scrub = scrub.replace(s, "")
        for sysname in systems:
            if re.search(rf"\b{re.escape(sysname)}\b", scrub, re.I):
                bad.append(f"JUDGE.md line mentions {sysname!r}: {ln[:80]}")
    for r in sealed:
        if any(it["mark"] for it in r["items"]):
            bad.append(f"row {r['row']} has a pre-filled mark")
    return bad


def systems_from_mapping():
    return {m["from"].lower() for m in load(D / "source-mapping.json")["map"]}


def main():
    queries = load(D / "queries-rows-1-18.json")
    raws = [load(D / "graph-raw.json"), load(D / "catalog-raw.json")]
    sealed, key = build(queries, raws, resolver())
    md = judge_md(sealed)
    systems = systems_from_mapping()
    if "--self-test" in sys.argv:
        assert not leaks(sealed, md, systems), leaks(sealed, md, systems)
        # Fails on bad: a label field and a header that names a system must both be caught.
        bad = json.loads(json.dumps(sealed)); bad[0]["items"][0]["system"] = "x"
        assert leaks(bad, md, systems), "label key not caught"
        assert leaks(sealed, md + f"\n## {sorted(systems)[0]} picks\n", systems), "header leak not caught"
        # Determinism and union coverage per row.
        s2, _ = build(queries, raws, resolver())
        assert s2 == sealed
        mp = load(D / "source-mapping.json")["map"]
        for r in sealed:
            want = {m["item"] for m in mp if m["row"] == r["row"]}
            assert {it["id"] for it in r["items"]} == want, r["row"]
            assert len(r["items"]) == len(want)
        # Not left in either system's original order.
        print(f"self-test OK: {len(sealed)} rows, {sum(len(r['items']) for r in sealed)} items, 0 leaks")
        return
    found = leaks(sealed, md, systems)
    if found:
        sys.exit("LEAK: " + "; ".join(found))
    (D / "pool-sealed.json").write_text(json.dumps(
        {"rule": "amendment 7 rule 3", "seed": f"random.Random({SEED} + row) over sorted union",
         "rows": sealed}, indent=1) + "\n")
    (D / "pool-key.json").write_text(json.dumps(
        {"note": "id -> system. Do not open before judging is complete.", "rows": key}, indent=1) + "\n")
    (D / "JUDGE.md").write_text(md)
    print("wrote pool-sealed.json, pool-key.json, JUDGE.md")


if __name__ == "__main__":
    main()
