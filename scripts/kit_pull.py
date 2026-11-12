#!/usr/bin/env python3
"""kit_pull.py: give the Field OS kit a measurable pull, so parts flock to the pages and jobs they fit.

The boids rules, made countable:
  cohesion   = job fit: the data shapes a part renders, and the backlog rows that name it
  alignment  = shared tokens and gates: links _tokens.css, ships a @prim block a generator can pull
  separation = near-duplicate shapes: rules that are copies of a rule in another part

    python3 scripts/kit_pull.py manifest            write src/ui-kit/kit-manifest.json (generated, never hand-edited)
    python3 scripts/kit_pull.py manifest --check    exit 1 if the kit's own fields (parts, classes, states) drifted
    python3 scripts/kit_pull.py score <data.json> [--job <backlog-id>] [--family kit,chips|all] [--top N] [--json]
    python3 scripts/kit_pull.py harvest             write src/ui-kit/kit-harvest.json (shapes repeated outside the kit)
    python3 scripts/kit_pull.py --self-test

NOTOMATION: score and harvest only propose. Nothing here edits a page; the gates (referee) and the gauntlet
(judge) decide. `manifest` also lists the cards of the local claude.ai/design export (DS_EXPORT, or
--ds-export <dir>) as an out-of-repo section when it exists; --check ignores that section.
Stdlib only.
"""
import hashlib
import json
import math
import os
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
KIT = ROOT / "src/ui-kit/recoil-report"
MANIFEST = ROOT / "src/ui-kit/kit-manifest.json"
HARVEST = ROOT / "src/ui-kit/kit-harvest.json"
BACKLOG = ROOT / "_QUEUE/induced-backlog.jsonl"
TEMPLATES = ROOT / "src/ui-kit/templates.json"
SPECIMENS = ROOT / "src/ui-kit/specimens"
PAGE_DIRS = ["public", "_ARTIFACTS"]
# The claude.ai/design export of the wider design system (cards, ui_kits, React sources). Out of repo,
# so it is listed when present and never gated. /design-sync keeps the remote copy; this is the local one.
DS_EXPORT = "~/Downloads/ARCS OS - Design System"
FIDELITY = ["sharp", "degraded", "grain", "moire"]
SIGNAL_HEX = re.compile(r"#(00F0FF|00FF9D|FFD700|FF4D6D)\b", re.I)
PRIM = re.compile(r"/\* @prim:begin (\S+) \*/(.*?)/\* @prim:end \1 \*/", re.S)
CARD = re.compile(r'<!-- @dsCard ([^>]*)-->')
ATTR = re.compile(r'(\w+)="([^"]*)"')
CLASS_DEF = re.compile(r"\.([a-zA-Z][\w-]*)")
CLASS_USE = re.compile(r'class="([^"]*)"')
# Classes too generic to prove a page assembles from a part (layout words every page uses).
GENERIC = {"row", "rows", "grid", "wrap", "pad", "card", "lede", "mono", "label", "k", "v", "t", "n", "s",
           "on", "off", "active", "open", "hidden", "sr-only", "cyan", "green", "gold", "red", "muted", "dim",
           "title", "head", "body", "main", "note", "tag", "item", "list", "box", "meta", "sub", "small"}

# Specimen-page scaffolding every kit file carries around its demo; not part of the shape.
SCAFFOLD = {"*", "html", "body", "main", "h1", "html, body", "body > main"}

# Data-shape vocabulary. A part carries a tag when its name, subtitle or spec job says so; a data file
# carries a tag when its fields have that shape. The rules live here so the inference is auditable.
SHAPE_WORDS = {
    "scalar": r"\btile\b|readout|gauge|\bstat\b|number",
    "percent": r"probability|percent|confidence|progress|\bbar\b|support|threshold|0 to 100",
    "sequence": r"stepper|\bbeats?\b|stage|ladder|\barc\b|phase|steps|rung|depth|90-day|\bordered\b|cascade",
    "table": r"table|key-value|2-col|\brows?\b|ledger",
    "state": r"\bled\b|status|states?\b|signal|\bchip|badge|verdict|stop-loss|y-state|lock",
    "evidence": r"evidence|cite|source|receipt",
    "note": r"callout|\bnote\b|thesis|owns",
    "graph": r"graph|\bmap\b|relationship|manifold|adjacency",
    "timeline": r"\btime\b|scrub|transport|contact sheet|over the call|in time order|tempo",
    "fidelity": r"fidelity|resolution|\bfog\b|grain|moir|render state",
    "delta": r"delta|change|moved|expected vs actual|before and after",
    "control": r"button|control|segmented|\bpad\b|range|toggle|radio",
    "label": r"section label|index line|header",
}


def rel(p):
    return str(Path(p).resolve().relative_to(ROOT))


def read(p):
    try:
        return Path(p).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def styles(text):
    return "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", text, re.S | re.I))


def split_decls(body):
    """Split on `;` outside parens and quotes (data URIs carry `;utf8,` and `url(%23n)`)."""
    out, cur, depth, q = [], [], 0, ""
    for ch in body:
        if q:
            q = "" if ch == q else q
        elif ch in "'\"":
            q = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif ch == ";" and depth == 0:
            out.append("".join(cur)); cur = []; continue
        cur.append(ch)
    return out + ["".join(cur)]


def rules(css):
    """Innermost `selector { decls }` pairs, comments stripped. @media wrappers fall away."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out = []
    for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        sel = " ".join(sel.split())
        decls = frozenset(" ".join(d.split()).lower().replace(": ", ":") for d in split_decls(body) if ":" in d)
        if sel and decls and not sel.startswith("@"):
            out.append((sel, decls))
    return out


def shape_tags(text):
    t = text.lower()
    return sorted(k for k, rx in SHAPE_WORDS.items() if re.search(rx, t))


# ---------------------------------------------------------------- manifest

def kit_parts():
    parts = []
    for f in sorted(KIT.glob("[0-9][0-9]-*.html")):
        text = read(f)
        m = CARD.search(text.split("\n", 1)[0])
        attrs = dict(ATTR.findall(m.group(1))) if m else {}
        prims = PRIM.findall(text)
        css = "\n".join(b for _, b in prims) if prims else styles(text)
        defined = sorted(set(CLASS_DEF.findall(re.sub(r"url\([^)]*\)", "", css))))
        spec = {}
        for s in SPECIMENS.glob("*.json"):
            d = json.loads(read(s))
            if f.name.startswith(f'{d.get("number")}-'):
                spec = d
        about = " ".join([attrs.get("name", ""), attrs.get("subtitle", ""), spec.get("job", "")])
        stem = f.stem
        parts.append({
            "id": stem,
            "number": stem[:2],
            "name": attrs.get("name", stem),
            "group": attrs.get("group", ""),
            "subtitle": attrs.get("subtitle", ""),
            "family": "kit",
            "path": rel(f),
            "data_shape": shape_tags(about),
            "fidelity": [s for s in FIDELITY if re.search(r"\b%s\b" % s, text, re.I)],
            "classes": defined,
            "prim_blocks": [n for n, _ in prims],
            "alignment": {
                "tokens": "_tokens.css" in text,
                "pullable": bool(prims),
                "no_raw_signal_hex": not SIGNAL_HEX.search(styles(text)),
            },
            "_rules": [r for r in rules(css) if r[0] not in SCAFFOLD],
        })
    return parts


def chips_part():
    f = ROOT / "src/ui-kit/grammar-chips/chips.html"
    text = read(f)
    defined = sorted(set(CLASS_DEF.findall(re.sub(r"url\([^)]*\)", "", styles(text)))))
    return {"id": "grammar-chips", "number": "", "name": "Grammar Chips", "group": "Grammar", "subtitle": "",
            "family": "chips", "path": rel(f), "data_shape": ["control", "state"],
            "fidelity": [s for s in FIDELITY if re.search(r"\b%s\b" % s, text, re.I)], "classes": defined,
            "prim_blocks": [], "alignment": {"tokens": "_tokens.css" in text or "--ds-" in text, "pullable": False,
                                             "no_raw_signal_hex": not SIGNAL_HEX.search(styles(text))},
            "_rules": rules(styles(text))}


def react_parts():
    out = []
    for f in sorted((ROOT / "src/ui").glob("[A-Z]*.tsx")):
        text = read(f)
        out.append({"id": f"ui/{f.stem}", "number": "", "name": f.stem, "group": "React", "subtitle": "",
                    "family": "react", "path": rel(f), "data_shape": shape_tags(f.stem + " " + re.sub(r"(?<!^)([A-Z])", r" \1", f.stem)),
                    "fidelity": [s for s in FIDELITY if re.search(r"\b%s\b" % s, text, re.I)], "classes": [],
                    "prim_blocks": [], "alignment": {"tokens": "tokens" in text, "pullable": True,
                                                     "no_raw_signal_hex": not SIGNAL_HEX.search(text)},
                    "_rules": []})
    return out


def page_files():
    files = []
    for d in PAGE_DIRS:
        files += [p for p in (ROOT / d).rglob("*.html") if "node_modules" not in p.parts]
    return sorted(files)


def generator_files():
    return sorted((ROOT / "scripts").glob("*.py"))


def distinctive(parts):
    owners = {}
    for p in parts:
        for c in p["classes"]:
            owners.setdefault(c, set()).add(p["id"])
    return {p["id"]: [c for c in p["classes"] if len(owners[c]) == 1 and c not in GENERIC] for p in parts}


def usage(parts, pages, gens):
    """pages[] per part: a generator that names the part's file, or a page that uses its distinctive classes."""
    dist = distinctive([p for p in parts if p["family"] != "react"])
    used = {p["id"]: [] for p in parts}
    gen_text = {g: read(g) for g in gens}
    page_classes = {}
    for f in pages:
        cs = set()
        for attr in CLASS_USE.findall(read(f)):
            cs.update(attr.split())
        page_classes[f] = cs
    for p in parts:
        if p["family"] == "kit":
            need = min(2, len(dist[p["id"]]))
            for f, cs in page_classes.items():
                if need and len(cs.intersection(dist[p["id"]])) >= need:
                    used[p["id"]].append(rel(f))
            for g, gt in gen_text.items():
                if p["id"] in gt:
                    used[p["id"]].append(rel(g))
        elif p["family"] == "chips":
            for f, cs in page_classes.items():
                if len(cs.intersection(dist[p["id"]])) >= 3:
                    used[p["id"]].append(rel(f))
        elif p["family"] == "react":
            name = p["name"]
            imp = re.compile(r'from ["\'][@./\w-]*ui/%s["\']' % name)
            for f in (ROOT / "src").rglob("*.tsx"):
                if f != ROOT / p["path"] and imp.search(read(f)):
                    used[p["id"]].append(rel(f))
    return {k: sorted(set(v)) for k, v in used.items()}


def jobs(parts):
    rows = [json.loads(l) for l in read(BACKLOG).splitlines() if l.strip()]
    out = {p["id"]: [] for p in parts}
    for r in rows:
        blob = json.dumps(r).lower()
        for p in parts:
            keys = [p["id"].lower()]
            slug = p["id"][3:] if p["family"] == "kit" else ""
            if "-" in slug:
                keys.append(slug)
            if p["family"] == "kit":
                keys.append(f"part {int(p['number'])}")
            if any(re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(k), blob) for k in keys):
                out[p["id"]].append(r["id"])
    return out


def templates_for(parts):
    reg = json.loads(read(TEMPLATES)).get("templates", {})
    out = {p["id"]: [] for p in parts}
    for name, t in reg.items():
        sigs = [s.lstrip(".").rstrip("-") for s in t.get("signature_selectors", [])]
        for p in parts:
            if any(c == s or (s and c.startswith(s) and t["signature_selectors"][sigs.index(s)].endswith("-"))
                   for s in sigs for c in p["classes"]):
                out[p["id"]].append(name)
    return out


def jaccard(a, b):
    return len(a & b) / len(a | b)


def separation(parts, floor=0.8, min_decls=4):
    """Rules in one part that copy (or nearly copy) a rule in another part."""
    flags = {p["id"]: [] for p in parts}
    seen = set()
    for i, p in enumerate(parts):
        for q in parts[i + 1:]:
            for sa, da in p["_rules"]:
                if len(da) < min_decls:
                    continue
                for sb, db in q["_rules"]:
                    if len(db) >= min_decls and jaccard(da, db) >= floor:
                        key = (p["id"], sa, q["id"], sb)
                        if key in seen:
                            continue
                        seen.add(key)
                        j = round(jaccard(da, db), 2)
                        flags[p["id"]].append({"rule": sa, "twin": q["id"], "twin_rule": sb, "jaccard": j})
                        flags[q["id"]].append({"rule": sb, "twin": p["id"], "twin_rule": sa, "jaccard": j})
    return flags


def ds_export(d):
    d = Path(d).expanduser()
    m = json.loads(read(d / "_ds_manifest.json") or "{}")
    cards = []
    for c in m.get("cards", []):
        cards.append({"name": c.get("name"), "group": c.get("group"), "subtitle": c.get("subtitle", ""),
                      "path": c.get("path"), "present": (d / c.get("path", "")).exists(),
                      "data_shape": shape_tags(f'{c.get("name")} {c.get("subtitle", "")}')})
    comps = [{"name": c["name"], "source": c["sourcePath"], "in_repo": (ROOT / c["sourcePath"]).exists()}
             for c in m.get("components", [])]
    return {"dir": str(d).replace(str(Path.home()), "~"), "namespace": m.get("namespace"), "cards": cards, "components": comps}


INTRINSIC = ["id", "name", "group", "family", "path", "data_shape", "fidelity", "classes", "prim_blocks", "alignment"]


def build_manifest(ds=None):
    parts = kit_parts() + [chips_part()] + react_parts()
    used = usage(parts, page_files(), generator_files())
    jb = jobs(parts)
    tp = templates_for(parts)
    sep = separation([p for p in parts if p["family"] != "react"])
    out = []
    for p in parts:
        row = {k: p[k] for k in ["id", "number", "name", "group", "subtitle", "family", "path", "data_shape",
                                 "fidelity", "classes", "prim_blocks", "alignment"]}
        row["templates"] = tp[p["id"]]
        row["jobs"] = jb[p["id"]]
        row["pages"] = used[p["id"]]
        row["reuse"] = len(used[p["id"]])
        row["near_duplicates"] = sep.get(p["id"], [])
        out.append(row)
    m = {"_comment": "GENERATED by scripts/kit_pull.py manifest. Never hand-edit; rerun the generator.",
         "fidelity_states": FIDELITY, "shape_vocabulary": sorted(SHAPE_WORDS), "parts": out}
    if ds:
        m["ds_export"] = ds_export(ds)
    return m


def dump(obj):
    return json.dumps(obj, indent=1, ensure_ascii=False) + "\n"


def check_manifest():
    if not MANIFEST.exists():
        print(f"✖ {rel(MANIFEST)} missing: run python3 scripts/kit_pull.py manifest")
        return 1
    have = {p["id"]: p for p in json.loads(read(MANIFEST))["parts"]}
    want = {p["id"]: p for p in build_manifest()["parts"]}
    bad = sorted(set(want) ^ set(have))
    for k in set(want) & set(have):
        if any(want[k][f] != have[k][f] for f in INTRINSIC):
            bad.append(k)
    if bad:
        print(f"✖ kit-manifest drifted for {len(bad)} part(s): {', '.join(sorted(bad)[:8])}. "
              "Rerun python3 scripts/kit_pull.py manifest (never hand-edit).")
        return 1
    print(f"✓ kit-manifest: {len(want)} parts, kit fields match the kit files")
    return 0


# ---------------------------------------------------------------- score

def data_features(d):
    """Shape tags a data file needs rendered, read from its field names and value types."""
    feats, why = set(), {}

    def add(tag, path):
        feats.add(tag)
        why.setdefault(tag, path)

    def walk(x, path, key=""):
        k = key.lower()
        if isinstance(x, bool):
            add("state", path)
        elif isinstance(x, (int, float)):
            if re.search(r"support|percent|pct|confidence|probab|score", k) and 0 <= x <= 100:
                add("percent", path)
                add("fidelity", path)
            else:
                add("scalar", path)
        elif isinstance(x, str):
            if re.search(r"^(kind|state|status|verdict|y|signal)$", k):
                add("state", path)
            if re.search(r"evidence|source|sha|refs?$|closes|path", k) or re.fullmatch(r"[0-9a-f]{7,40}", x):
                add("evidence", path)
            if re.search(r"^(before|after|from|to|delta)$", k):
                add("delta", path)
            if re.search(r"^(t|time|at|date|timestamp|event_at)$", k):
                add("timeline", path)
        elif isinstance(x, dict):
            if {"nodes", "edges"} & set(x) or "depends_on" in x:
                add("graph", path)
            for kk, v in x.items():
                walk(v, f"{path}.{kk}", kk)
        elif isinstance(x, list) and x:
            if all(isinstance(i, dict) for i in x):
                keys = set().union(*x)
                if len(x) >= 2:
                    add("sequence" if {"rank", "step", "order", "stage", "n"} & keys or k in ("sections", "beats", "steps", "stages") else "table", path)
                if "claim" in keys or "fix" in keys:
                    add("note", path)
            elif all(isinstance(i, str) for i in x) and k not in ("evidence", "closes", "refs"):
                add("note", path)
            for i, v in enumerate(x[:50]):
                walk(v, f"{path}[{i}]", key if not isinstance(v, dict) else "")
    walk(d, "$")
    return feats, why


def score(data, manifest, job=None, families=("kit", "chips")):
    """fit = 0.6 x share of the part's shapes the data has + 0.4 x share of the data's needs the part covers."""
    feats, why = data_features(data)
    pool = [p for p in manifest["parts"] if p["family"] in families]
    max_reuse = max([p["reuse"] for p in pool] + [1])
    ranked = []
    for p in pool:
        tags = set(p["data_shape"])
        hit = sorted(tags & feats)
        fit = (0.6 * len(hit) / len(tags) + 0.4 * len(hit) / len(feats)) if tags and feats else 0.0
        reuse = math.log2(1 + p["reuse"]) / math.log2(1 + max_reuse)
        a = p["alignment"]
        gate = (a["tokens"] + a["pullable"] + a["no_raw_signal_hex"]) / 3 - (0.1 if p["near_duplicates"] else 0)
        jobm = 1.0 if job and job in p["jobs"] else 0.0
        pull = round(0.55 * fit + 0.2 * reuse + 0.15 * gate + 0.1 * jobm, 3)
        ranked.append({"id": p["id"], "family": p["family"], "pull": pull, "fit": round(fit, 2), "reuse": p["reuse"],
                       "gate": round(gate, 2), "job": bool(jobm), "matched": hit,
                       "evidence": {t: why[t] for t in hit}})
    ranked.sort(key=lambda r: (-r["pull"], r["id"]))
    return feats, ranked


def cmd_score(argv):
    path = next(a for a in argv if not a.startswith("--"))
    job = argv[argv.index("--job") + 1] if "--job" in argv else None
    top = int(argv[argv.index("--top") + 1]) if "--top" in argv else 10
    fams = tuple(argv[argv.index("--family") + 1].split(",")) if "--family" in argv else ("kit", "chips")
    if fams == ("all",):
        fams = ("kit", "chips", "react")
    manifest = json.loads(read(MANIFEST)) if MANIFEST.exists() else build_manifest()
    feats, ranked = score(json.loads(read(path)), manifest, job, fams)
    if "--json" in argv:
        print(dump({"data": path, "needs": sorted(feats), "ranked": ranked[:top]}))
        return 0
    print(f"{path} needs: {', '.join(sorted(feats))}" + (f"  (job {job})" if job else ""))
    print(f"{'pull':>5}  {'fit':>4}  {'reuse':>5}  {'gate':>4}  part · matched")
    for r in ranked[:top]:
        print(f"{r['pull']:5.3f}  {r['fit']:4.2f}  {r['reuse']:5d}  {r['gate']:4.2f}  {r['id']} · {', '.join(r['matched']) or '-'}")
    print("Proposal only: nothing was written. The page's generator and its gates decide.")
    return 0


# ---------------------------------------------------------------- harvest

def norm_value(d):
    """Shape of a declaration: numbers and colors erased, data-URI SVGs reduced to their element names."""
    prop, _, val = d.partition(":")
    if "data:image/svg" in val:
        svg = unquote(val)
        els = sorted(set(re.findall(r"<(fe\w+|filter|rect|circle|path|pattern|line)\b", svg)))
        kinds = sorted(set(re.findall(r"type=\\?['\"](\w+)", svg)))
        return f"{prop}:url(svg:{'+'.join(els)}:{'+'.join(kinds)})"
    val = re.sub(r"#[0-9a-f]{3,8}\b", "C", val)
    val = re.sub(r"-?\d*\.?\d+(px|rem|em|%|ms|s|deg|vh|vw|ch|fr)?", "N", val)
    return f"{prop}:{val}"


def family_of(f, text):
    """Pages poured from one mold count once: its generator, its template marker, else its name stem."""
    m = re.search(r"(?:Generated|GENERATED) by (scripts/[\w./-]+)", text) or re.search(r"@arcs-template: ([\w-]+)", text)
    if m:
        return m.group(1)
    r = rel(f)
    d, stem = os.path.dirname(r), Path(r).stem
    return f"{d}/{'-'.join(re.split(r'[-_.]', stem)[:2])}"


def harvest(min_families=2, min_decls=4):
    kit_rules = []
    for p in kit_parts() + [chips_part()]:
        kit_rules += [(p["id"], s, d) for s, d in p["_rules"]]
    kit_exact = {d for _, _, d in kit_rules}
    tokens = read(KIT / "_tokens.css")
    groups, textures = {}, {}
    for f in page_files():
        css = styles(read(f))
        if not css:
            continue
        fam = family_of(f, read(f))
        for sel, decls in rules(css.replace(tokens, "")):
            for dd in decls:
                if "data:image/svg" in dd:
                    t = textures.setdefault(norm_value(dd), {"families": {}, "selectors": set()})
                    t["families"].setdefault(fam, set()).add(rel(f))
                    t["selectors"].add(sel)
            if len(decls) < min_decls or decls in kit_exact or sel.startswith(":root") or sel in ("*", "html", "body", "html, body"):
                continue
            shape = frozenset(norm_value(d) for d in decls)
            g = groups.setdefault(shape, {"selectors": set(), "families": {}, "decls": decls})
            g["selectors"].add(sel)
            g["families"].setdefault(fam, set()).add(rel(f))
    cands = []
    for shape, g in groups.items():
        if len(g["families"]) < min_families:
            continue
        files = sorted(set().union(*g["families"].values()))
        near = max(((jaccard(g["decls"], d), pid, s) for pid, s, d in kit_rules if len(d) >= min_decls),
                   default=(0, None, None))
        cands.append({
            "shape": sorted(shape),
            "example": [d[:100] for d in sorted(g["decls"])],
            "selectors": sorted(g["selectors"])[:12],
            "families": len(g["families"]),
            "files": len(files),
            "evidence": [sorted(v)[0] for v in g["families"].values()][:8],
            "nearest_kit": {"part": near[1], "rule": near[2], "jaccard": round(near[0], 2)} if near[0] >= 0.5 else None,
            "verdict": "drifted copy of a kit rule: pull the kit part" if near[0] >= 0.8 else "promotion candidate",
        })
    cands.sort(key=lambda c: (-c["families"], -len(c["shape"]), c["selectors"][0]))
    # A flock: shapes that always travel with the same set of page families are one component.
    flocks = {}
    for i, c in enumerate(cands):
        flocks.setdefault(tuple(c["evidence"]), []).append(i)
    clusters = [{"families": cands[ix[0]]["families"], "rules": len(ix),
                 "selectors": [cands[i]["selectors"][0] for i in ix][:10], "evidence": list(k)}
                for k, ix in flocks.items()]
    clusters.sort(key=lambda c: (-c["families"] * c["rules"], c["selectors"][0]))
    kit_tex = {norm_value(dd): pid for pid, _, d in kit_rules for dd in d if "data:image/svg" in dd}
    tex = [{"texture": k, "families": len(v["families"]), "selectors": sorted(v["selectors"])[:10],
            "kit_part": kit_tex.get(k), "evidence": [sorted(x)[0] for x in v["families"].values()]}
           for k, v in textures.items() if len(v["families"]) >= min_families]
    tex.sort(key=lambda t: (-t["families"], t["texture"]))
    return {"_comment": "GENERATED by scripts/kit_pull.py harvest. A one-off earns no mold; promote on the second "
                        "real case. families = distinct page style sheets (pages sharing one generator count once).",
            "min_families": min_families, "min_decls": min_decls, "total_candidates": len(cands), "total_flocks": len(clusters),
            "textures": tex, "clusters": clusters[:150],
            "candidates": [{k: v for k, v in c.items() if k != "shape"} for c in cands[:150]]}


def cmd_harvest(argv):
    h = harvest()
    HARVEST.write_text(dump(h))
    print(f"wrote {rel(HARVEST)}: {h['total_candidates']} rule shapes in {h['total_flocks']} flocks, "
          f"{len(h['textures'])} textures, each across >= {h['min_families']} page families")
    for c in h["clusters"][:12]:
        print(f"  flock {c['families']:3d} fam x {c['rules']:3d} rules  {', '.join(c['selectors'][:4])[:70]}")
    for t in h["textures"][:6]:
        print(f"  texture {t['families']:3d} fam  {t['texture'][:60]}  e.g. {t['evidence'][0]}")
    return 0


# ---------------------------------------------------------------- self-test

def self_test():
    n = 0
    m = build_manifest()
    parts = {p["id"]: p for p in m["parts"]}
    kit = [p for p in m["parts"] if p["family"] == "kit"]
    assert len(kit) == len(list(KIT.glob("[0-9][0-9]-*.html"))); n += 1
    assert all(p["data_shape"] for p in kit), [p["id"] for p in kit if not p["data_shape"]]; n += 1
    assert "scripts/audit_report_build.py" in parts["29-tile"]["pages"], "generator pull of 29-tile not seen"; n += 1
    assert set(parts["29-tile"]["data_shape"]) >= {"scalar"} and set(parts["07-probability-bar"]["data_shape"]) >= {"percent"}; n += 1
    # separation: two parts carrying the same rule are flagged as twins
    fake = [{"id": "a", "_rules": [(".x", frozenset("abcd"))]}, {"id": "b", "_rules": [(".y", frozenset("abcd"))]}]
    assert separation(fake)["a"][0]["twin"] == "b"; n += 1
    assert not separation([{"id": "a", "_rules": [(".x", frozenset("abcd"))]}, {"id": "b", "_rules": [(".y", frozenset("wxyz"))]}])["a"]; n += 1
    # score: the audit data pulls the parts its generator already uses; a graph pulls the graph parts
    cold = json.loads(read(ROOT / "runtime/audit/cold-1.json"))
    feats, ranked = score(cold, m)
    assert {"percent", "fidelity", "scalar", "evidence", "sequence"} <= feats, feats; n += 1
    top = [r["id"] for r in ranked[:12]]
    assert sum(x in top for x in ["29-tile", "17-altitude-ladder", "33-led", "31-callout"]) >= 3, top; n += 1
    g = {"nodes": [{"id": "a"}, {"id": "b"}], "edges": [{"from": "a", "to": "b"}]}
    _, gr = score(g, m)
    assert gr[0]["matched"] and "graph" in gr[0]["matched"], gr[:3]; n += 1
    assert score({}, m)[1][0]["fit"] == 0; n += 1
    # job match lifts a part
    row = parts["35-backlog-graph"]["jobs"][:1]
    if row:
        a = next(r for r in score(g, m)[1] if r["id"] == "35-backlog-graph")["pull"]
        b = next(r for r in score(g, m, row[0])[1] if r["id"] == "35-backlog-graph")["pull"]
        assert b > a; n += 1
    # harvest normalizes sizes and colors, so two noise overlays at different sizes are one shape
    u1 = "background-image:url(\"data:image/svg+xml,%3Csvg width='120'%3E%3Cfilter%3E%3CfeTurbulence type='fractalNoise'/%3E\")"
    u2 = "background-image:url(\"data:image/svg+xml,%3Csvg width='160'%3E%3Cfilter%3E%3CfeTurbulence type='fractalNoise'/%3E\")"
    assert norm_value(u1) == norm_value(u2) and norm_value("color:#00f0ff") == norm_value("color:#ff4d6d"); n += 1
    # read-only: score and harvest's scan touch no page
    before = {p: p.stat().st_mtime_ns for p in page_files()[:50]}
    score(cold, m)
    assert before == {p: p.stat().st_mtime_ns for p in before}; n += 1
    # check fails on a hand edit and passes on the generated file
    global MANIFEST
    real = MANIFEST
    with tempfile.TemporaryDirectory() as td:
        MANIFEST = Path(td) / "m.json"
        MANIFEST.write_text(dump(m))
        ok = check_manifest()
        bad = json.loads(read(MANIFEST)); bad["parts"][0]["classes"].append("hand-edit")
        MANIFEST.write_text(dump(bad))
        failed = check_manifest()
    MANIFEST = real
    assert ok == 0 and failed == 1; n += 1
    print(f"kit_pull self-test: {n} checks pass")
    return 0


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "--self-test":
        return self_test()
    if argv[0] == "manifest":
        if "--check" in argv:
            return check_manifest()
        ds = argv[argv.index("--ds-export") + 1] if "--ds-export" in argv else DS_EXPORT
        if not (Path(ds).expanduser() / "_ds_manifest.json").exists():
            ds = None
        m = build_manifest(ds)
        MANIFEST.write_text(dump(m))
        print(f"wrote {rel(MANIFEST)}: {len(m['parts'])} parts")
        return 0
    if argv[0] == "score":
        return cmd_score(argv[1:])
    if argv[0] == "harvest":
        return cmd_harvest(argv[1:])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
