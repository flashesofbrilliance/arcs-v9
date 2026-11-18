#!/usr/bin/env python3
"""gate_taxonomy_emit: the gate system, built bottom-up, each layer derived from the one below (never declared).

Design ladder                                     ARCS ladder
  atom      one verdict line in the hook            primitive  the ROM primitive a template defends (ruled by Zach)
  molecule  a gate script (its atoms)               operator   a periodic-table operator bound to the gate's code
  organism  a stage that runs molecules              protocol   a flow that composes organisms (commit, merge)
            (pre-commit, a CI job)
  template  the reusable shape of a check, read from its invocation (--check, --staged, lint, ...)
  page      a surface that renders the gate system

Evidence rules (mechanical, no judgment):
  primitive  only when the atom's own comment block or message names a ROM primitive or its alias; else UNRULED.
             A template's primitive is set only in runtime/specs/gate-template-primitives.json (Zach's ruling sheet);
             this script never writes that file.
  operator   only when operators/OPERATOR-REGISTRY.json binds a module the gate script is or imports.
  protocol   commit = the pre-commit organism; merge = the CI organisms (safe_merge.sh requires every check SUCCESS).

In:  scripts/git-hooks/pre-commit, .github/workflows/*.yml, runtime/specs/gate-chains.json (molecules, from
     gate_chain_build.py), operators/OPERATOR-REGISTRY.json, runtime/specs/gate-template-primitives.json (if present)
Out: runtime/specs/gate-taxonomy.json (internal: carries script names and hook messages; not served)
     runtime/specs/gate-taxonomy-docs.jsonl (the same nodes as storage documents, the blob and vector sink input)

  python3 scripts/gate_taxonomy_emit.py            write
  python3 scripts/gate_taxonomy_emit.py --check    exit 1 if the file differs from a rebuild
  python3 scripts/gate_taxonomy_emit.py --summary  print the ladder counts
  python3 scripts/gate_taxonomy_emit.py --docs P   also copy the storage documents to P (JSONL)

Storage seam (--docs): every node at every layer has the SAME document shape, so one sink handles all of them:
  {"id": "<layer>:<key>", "layer": "atom|molecule|organism|template|page|primitive|operator|protocol",
   "ladder": "design|arcs", "text": "<plain sentence to embed>", "meta": {flat scalars and string lists},
   "parents": [ids one layer up], "children": [ids one layer down], "content_hash": "sha256 of text+meta"}
  A blob sink puts the JSONL file as is; a vector sink embeds "text", stores "meta", and upserts by "id",
  re-embedding only when "content_hash" changed. Atom ids hash the script and message, not the line number,
  so an atom keeps its id when the hook is edited above it. The sinks themselves are backlog row gate-ladder-storage-sinks.
Stdlib only.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = "scripts/git-hooks/pre-commit"
OUT = "runtime/specs/gate-taxonomy.json"
DOCS = "runtime/specs/gate-taxonomy-docs.jsonl"  # the storage seam: one document per node, any layer
RULING = "runtime/specs/gate-template-primitives.json"
SCRIPT_RE = re.compile(r"scripts/([A-Za-z0-9_]+\.(?:py|sh|mjs))")
# ROM primitives (CLAUDE.md "ROM Primitives") and the aliases the repo uses for them
PRIMITIVES = {
    "NOTOMATION": r"notomation",
    "HYPERSPHERE": r"hypersphere|context manifold",
    "HYPERSTITION": r"hyperstition|loki test",
    "GOLDEN_INCHWORM": r"golden inchworm|inchworm|red thread|golden thread",
    "ORTHOGONAL_ECHO": r"orthogonal echo|echo detector",
    "KINTSUGI": r"kintsugi|immune system",
    "WRITE_LOCK": r"write-lock|write lock|one-way door",
}
TEMPLATES = [  # (name, test on the invocation line), first match wins
    ("self-test", lambda s, ln: "--self-test" in ln),
    ("derived-freshness", lambda s, ln: "--check" in ln),
    ("record-integrity", lambda s, ln: "--staged" in ln),
    ("lint", lambda s, ln: "lint" in s),
    ("gate", lambda s, ln: "gate" in s or "guard" in s),
    ("check", lambda s, ln: True),
]


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def atoms_from_hook(text):
    """Each verdict line (a blocked or a warn echo) is an atom, tied to the nearest script invoked above it inside
    its block, and to that block's leading comment."""
    lines = text.splitlines()
    out = []
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("#"):
            continue  # a comment that says "WARNS" is not a verdict
        kind = "block" if "commit blocked" in ln else "warn" if re.search(r'echo ".{0,3}⚠|WARN', ln) else None
        if not kind:
            continue
        script, call, comment = None, "", []
        j = i - 1
        while j >= 0 and not lines[j].startswith("# ----"):
            m = SCRIPT_RE.search(lines[j])
            if m and script is None and not lines[j].lstrip().startswith("#"):
                script, call = m.group(1), lines[j].strip()
            if lines[j].startswith("#"):
                comment.insert(0, lines[j].lstrip("# ").strip())
            elif comment:
                break  # the comment block above this atom's code is complete
            j -= 1
        m = SCRIPT_RE.search(ln)
        if script is None and m:
            script, call = m.group(1), ln.strip()
        out.append({"line": i + 1, "verdict": kind, "script": script or "(inline shell)",
                    "call": call[:200], "message": ln.strip()[:240], "comment": " ".join(comment)[:400]})
    seen = {a["script"] for a in out}
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("#"):
            continue
        for s in SCRIPT_RE.findall(ln):
            if s in seen:
                continue
            seen.add(s)
            kind = "advisory" if re.search(r"\|\|\s*true|2>/dev/null\s*\|\|", ln) else "exit"
            out.append({"line": i + 1, "verdict": kind, "script": s, "call": ln.strip()[:200],
                        "message": "(the script's own exit code and output)", "comment": ""})
    return sorted(out, key=lambda a: a["line"])


def template_of(script, call):
    return next(name for name, test in TEMPLATES if test(script or "", call or ""))


def primitive_evidence(atom):
    text = f"{atom['comment']} {atom['message']}".lower()
    return sorted(p for p, pat in PRIMITIVES.items() if re.search(pat, text))


def organisms_from_ci():
    orgs = []
    for path in sorted(glob.glob(os.path.join(ROOT, ".github/workflows/*.yml"))):
        name, job, scripts, in_jobs = os.path.basename(path), None, {}, False
        for ln in open(path, encoding="utf-8"):
            if re.match(r"^\S", ln):
                in_jobs = ln.startswith("jobs:")  # a job is a 2-space key under jobs:, never under on:
            m = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", ln)
            if m and in_jobs:
                job = m.group(1)
            for s in SCRIPT_RE.findall(ln):
                if job:
                    scripts.setdefault(job, set()).add(s)
        for j, ss in scripts.items():
            orgs.append({"organism": f"ci:{name}/{j}", "molecules": sorted(ss)})
    return orgs


def operator_bindings(molecules):
    reg = json.loads(read("operators/OPERATOR-REGISTRY.json"))
    mods = {}
    for op in reg.get("operators", []):
        mod = (op.get("binding") or {}).get("module")
        if mod:
            mods.setdefault(mod, []).append(f"{op['op']}:{op['name']}")
    out = {}
    for s in molecules:
        p = os.path.join(ROOT, "scripts", s)
        body = open(p, encoding="utf-8", errors="replace").read() if os.path.exists(p) else ""
        imports = set(re.findall(r"^\s*(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))", body, re.M))
        imported = {x for pair in imports for x in pair if x}
        hits = sorted({o for mod, ops in mods.items() for o in ops
                       if mod == f"scripts/{s}" or mod[:-3].replace("/", ".") in imported})
        if hits:
            out[s] = hits
    return out


ADR_RE = re.compile(r"\bADR-0*(\d{1,3})\b")


def hook_blame():
    """line number -> short sha of the commit that last wrote that hook line (one git blame)."""
    import subprocess
    out = subprocess.run(["git", "blame", "--porcelain", HOOK], cwd=ROOT, capture_output=True, text=True).stdout
    sha_of, cur = {}, None
    for ln in out.splitlines():
        m = re.match(r"^([0-9a-f]{40}) \d+ (\d+)", ln)
        if m:
            cur = m.group(1)[:8]
            sha_of[int(m.group(2))] = cur
    return sha_of


def adr_refs(script, wired_sha):
    """ADRs the repo already ties to a gate: cited in the script's header or in the commit that wired it."""
    import subprocess
    p = os.path.join(ROOT, "scripts", script)
    head = "".join(open(p, encoding="utf-8", errors="replace").readlines()[:40]) if os.path.exists(p) else ""
    msg = subprocess.run(["git", "log", "-1", "--format=%B", wired_sha], cwd=ROOT, capture_output=True,
                         text=True).stdout if wired_sha else ""
    return sorted({f"ADR-{int(n):03d}" for n in ADR_RE.findall(head + "\n" + msg)})


def build():
    hook = read(HOOK)
    atoms = atoms_from_hook(hook)
    blame = hook_blame()
    for a in atoms:
        a["sha"] = blame.get(a["line"], "")
    ci = organisms_from_ci()
    # CI-only gates (run by a job, never by the hook) are molecules too; their one atom is the job step's exit code
    hooked = {a["script"] for a in atoms}
    for o in ci:
        for m in o["molecules"]:
            if m not in hooked:
                hooked.add(m)
                atoms.append({"line": 0, "verdict": "ci-exit", "script": m, "call": o["organism"],
                              "message": f"(exit code of the {o['organism']} step)", "comment": "",
                              "template": template_of(m, ""), "primitive_evidence": [], "sha": ""})
    for a in atoms:
        a["template"] = template_of(a["script"], a["call"])
        a["primitive_evidence"] = primitive_evidence(a)
    chains = json.loads(read("runtime/specs/gate-chains.json"))
    wired = {g[2]: {"added": g[0], "sha": g[1]} for w in chains["weeks"] for g in w["gates"]}
    by_script = {}
    for a in atoms:
        by_script.setdefault(a["script"], []).append(a)
    in_hook = set(SCRIPT_RE.findall(hook))
    molecules = []
    # "(inline shell)" is a real molecule: checks written directly in the hook rather than in a script
    for s in sorted(set(wired) | {a["script"] for a in atoms}):
        ats = by_script.get(s, [])
        w = wired.get(s) or {}
        molecules.append({"molecule": s, "atoms": len(ats), "templates": sorted({a["template"] for a in ats}),
                          "adr": adr_refs(s, w.get("sha", "")),
                          "primitive_evidence": sorted({p for a in ats for p in a["primitive_evidence"]}),
                          "wired": wired.get(s), "in_hook_now": s in in_hook})
    organisms = [{"organism": "pre-commit", "molecules": sorted(in_hook | {"(inline shell)"})}] + ci
    ruling = json.loads(read(RULING)) if os.path.exists(os.path.join(ROOT, RULING)) else {}
    templates = {}
    for a in atoms:
        t = templates.setdefault(a["template"], {"template": a["template"], "atoms": 0, "molecules": set(),
                                                 "primitive_evidence": set()})
        t["atoms"] += 1
        t["molecules"].add(a["script"])
        t["primitive_evidence"] |= set(a["primitive_evidence"])
    tlist = [{"template": t["template"], "atoms": t["atoms"], "molecules": len(t["molecules"]),
              "primitive_evidence": sorted(t["primitive_evidence"]),
              "primitive_ruled": (ruling.get(t["template"]) or {}).get("primitive", "UNRULED")}
             for t in sorted(templates.values(), key=lambda t: -t["atoms"])]
    # the page is rendered by the script that OWNS gate-chains.json (assigns its path to a constant), never by a
    # script that merely mentions or reads it (this one reads it; gate_ladder_page.py names it in prose)
    owns = re.compile(r'^[A-Z_]+\s*=.*["\']runtime/specs/gate-chains\.json', re.M)
    consumers = sorted(p for p in glob.glob(os.path.join(ROOT, "scripts", "*.py"))
                       if owns.search(open(p, encoding="utf-8", errors="replace").read()))
    pages = [{"page": "status.arcs.care/gauntlets (public/gauntlet-log.html)",
              "renders": "molecules by week, reviewed chains", "via": [os.path.relpath(c, ROOT) for c in consumers]}]
    ops = operator_bindings([m["molecule"] for m in molecules])
    protocols = [
        {"protocol": "commit", "organisms": ["pre-commit"], "evidence": "core.hooksPath runs scripts/git-hooks/pre-commit"},
        {"protocol": "merge", "organisms": sorted(o["organism"] for o in organisms if o["organism"].startswith("ci:")),
         "evidence": "scripts/safe_merge.sh refuses unless every check is SUCCESS"},
    ]
    return {
        "generator": "scripts/gate_taxonomy_emit.py",
        "ladder": {"atoms": len(atoms), "molecules": len(molecules), "organisms": len(organisms),
                   "templates": len(tlist), "pages": len(pages),
                   "primitives_with_evidence": sorted({p for a in atoms for p in a["primitive_evidence"]}),
                   "templates_ruled": sum(t["primitive_ruled"] != "UNRULED" for t in tlist),
                   "molecules_with_operator": len(ops), "molecules_with_adr": sum(bool(m["adr"]) for m in molecules),
                   "protocols": len(protocols)},
        "atoms": atoms, "molecules": molecules, "organisms": organisms, "templates": tlist, "pages": pages,
        "operators": ops, "protocols": protocols,
    }


def _h(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def documents(d):
    """One storage document per node, the same shape at every layer (see the module docstring)."""
    out = []

    def doc(layer, ladder, key, text, meta, parents=(), children=()):
        body = json.dumps({"text": text, "meta": meta}, sort_keys=True)
        out.append({"id": f"{layer}:{key}", "layer": layer, "ladder": ladder, "text": text, "meta": meta,
                    "parents": sorted(set(parents)), "children": sorted(set(children)), "content_hash": _h(body)})
    aid = lambda a: f'{a["script"]}#{_h(a["script"] + "|" + a["message"])[:10]}'
    org_of = {}
    for o in d["organisms"]:
        for m in o["molecules"]:
            org_of.setdefault(m, []).append("organism:" + o["organism"])
    for a in d["atoms"]:
        doc("atom", "design", aid(a),
            f'{a["verdict"]} verdict from {a["script"]}: {a["message"]} {a["comment"]}'.strip(),
            {"verdict": a["verdict"], "script": a["script"], "template": a["template"], "line": a["line"], "sha": a["sha"],
             "primitive_evidence": a["primitive_evidence"]},
            parents=["molecule:" + a["script"]])
    atoms_by = {}
    for a in d["atoms"]:
        atoms_by.setdefault(a["script"], []).append("atom:" + aid(a))
    for m in d["molecules"]:
        doc("molecule", "design", m["molecule"],
            f'gate script {m["molecule"]} with {m["atoms"]} verdicts, templates {", ".join(m["templates"]) or "none"}',
            {"templates": m["templates"], "primitive_evidence": m["primitive_evidence"], "in_hook_now": m["in_hook_now"],
             "wired_sha": (m["wired"] or {}).get("sha", ""), "wired_date": (m["wired"] or {}).get("added", ""),
             "operators": d["operators"].get(m["molecule"], []), "adr": m["adr"]},
            parents=org_of.get(m["molecule"], []) + ["template:" + t for t in m["templates"]],
            children=atoms_by.get(m["molecule"], []))
    for o in d["organisms"]:
        doc("organism", "design", o["organism"], f'stage {o["organism"]} runs {len(o["molecules"])} gate scripts',
            {"molecules": len(o["molecules"])}, children=["molecule:" + m for m in o["molecules"]],
            parents=["protocol:" + p["protocol"] for p in d["protocols"] if o["organism"] in p["organisms"]])
    for t in d["templates"]:
        doc("template", "design", t["template"],
            f'check shape {t["template"]}: {t["atoms"]} verdicts across {t["molecules"]} scripts',
            {"atoms": t["atoms"], "molecules": t["molecules"], "primitive_evidence": t["primitive_evidence"],
             "primitive_ruled": t["primitive_ruled"]},
            parents=[] if t["primitive_ruled"] == "UNRULED" else ["primitive:" + t["primitive_ruled"]])
    for p in d["pages"]:
        doc("page", "design", p["page"], f'surface {p["page"]} renders {p["renders"]}', {"via": p["via"]})
    for name in PRIMITIVES:
        doc("primitive", "arcs", name, f'ROM primitive {name.replace("_", " ").lower()}',
            {"evidence_atoms": sum(name in a["primitive_evidence"] for a in d["atoms"])},
            children=["template:" + t["template"] for t in d["templates"] if t["primitive_ruled"] == name])
    for p in d["protocols"]:
        doc("protocol", "arcs", p["protocol"], f'protocol {p["protocol"]}: {p["evidence"]}', {"evidence": p["evidence"]},
            children=["organism:" + o for o in p["organisms"]])
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--docs", metavar="PATH", help="also write the storage documents as JSONL")
    a = ap.parse_args()
    built = build()
    data = json.dumps(built, indent=1, sort_keys=False) + "\n"
    docs = "".join(json.dumps(x, sort_keys=True) + "\n" for x in documents(built))
    if a.docs:
        open(a.docs, "w", encoding="utf-8").write(docs)
        print(f"gate_taxonomy: {docs.count(chr(10))} documents -> {a.docs}")
    outs = {OUT: data, DOCS: docs}
    if a.check:
        stale = [k for k, v in outs.items() if not os.path.exists(os.path.join(ROOT, k))
                 or open(os.path.join(ROOT, k), encoding="utf-8").read() != v]
        print("gate_taxonomy: fresh" if not stale else f"gate_taxonomy: stale {stale}; run python3 scripts/gate_taxonomy_emit.py")
        return 1 if stale else 0
    if not a.summary:
        for k, v in outs.items():
            open(os.path.join(ROOT, k), "w", encoding="utf-8").write(v)
    lad = json.loads(data)["ladder"]
    print("gate_taxonomy: " + " · ".join(f"{k} {v}" for k, v in lad.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
