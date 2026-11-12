#!/usr/bin/env python3
"""Recoil call service, stage J5: explode the SSOT into an arcs.atlas.v2 knowledge graph (stdlib only).

Backlog row atlas-v2-schema-export (R9). Spec: _PROPOSALS/2026-11-11-recoil-call-service-arc-weld.md
sections 3 (J5 to J8), 4.5 and 6.1. Schema: runtime/specs/arcs-atlas-v2.schema.json.

  python3 scripts/recoil_stage_j5.py --self-test
  python3 scripts/recoil_service.py run --call <ssot> --only J5      # the normal path

Registered into the runner by install(svc), the same plug-in interface J1 to J3 use. J5 owns the
SSOT key `atlas` (pointers and kairos marks) and writes the graph to
runtime/recoil/generated/<report_id>.atlas.json.

What goes in (all from the SSOT, nothing invented):
  tier 0 atoms      call.atoms
  tier 1 people     the speakers of those atoms
  tier 2 claims     claims[] (J3)
  tier 3 beliefs    beliefs[] (priors carried in: t is the call start, 0:00)
  tier 4 decisions  next_steps[]
Edges point from the newer, derived node to the older, source node, and each names the atom ids
that evidence it. An item with no atom to stand on gets a node with t null and no edges, and is
listed in `unanchored`.

J5 also emits the recoil-beats timeline (row recoil-runner-beats; schema runtime/specs/recoil-beats.md,
used as is) so any run plays in the existing recoil player with no new player code. Written under the run
directory, beside the run's other prints:
  runtime/recoil/runs/<stem>/beats.json     a recoil data file: meta, beliefs, beats (one beat per atom time)
  runtime/recoil/runs/<stem>/player.html    src/ui-kit/recoil-report/recoil-player.html with this run's data
  runtime/recoil/runs/<stem>/_player.js and _tokens.css   the template's script and tokens, copied beside it
A belief's move lands on the beat of its earliest evidencing atom (the same rule as x-kairos); a kairos
pin sits on the beat of each atlas kairos mark, its id is that atom's id and its label names the atom.
A belief that moved with no atom keeps its prior in the player and is named in meta.note.

Gates (spec 6.1, plus the row's):
  every edge has evidence, and every evidence id is an atom in the file
  no edge goes backward in time, and the graph is acyclic
  the kairos list matches the SSOT's atlas.kairos, and the rule in x-kairos finds no other move
  render states equal the x-fidelity rule recomputed; v1 tier shape kept; schema valid
  beats: valid under check_beats (scripts/recoil_brief.py); one pin per atlas kairos mark, each on its atom
"""
from __future__ import annotations

import copy
import html
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import recoil_ssot_v2 as v2  # noqa: E402

SCHEMA_PATH = os.path.join(ROOT, "runtime", "specs", "arcs-atlas-v2.schema.json")
SCHEMA_ID = "arcs.atlas.v2"
GENERATED = os.path.join("runtime", "recoil", "generated")
RUNS_DIR = os.path.join("runtime", "recoil", "runs")
VERSION = "2"  # 2: also emits beats.json and player.html (recoil-runner-beats)
TIERS = [("Atoms", "atom"), ("People", "person"), ("Claims", "claim"), ("Beliefs", "belief"), ("Decisions", "decision")]
TIER_OF = {kind: i for i, (_, kind) in enumerate(TIERS)}
WORST = ["A", "B", "C", "D", "E", "NS"]
BRACKET = re.compile(r"\[([^\]]+)\]")
TS = re.compile(r"(?<![\d:])(\d{1,2}:\d{2}(?::\d{2})?)(?![\d:])")
PLAYER_DIR = os.path.join(ROOT, "src", "ui-kit", "recoil-report")
PLAYER_ASSETS = ("_player.js", "_tokens.css")  # the template's relative src and href, copied beside the page
CONVICTION = {"LOW": "LOW", "MED": "MEDIUM", "MEDIUM": "MEDIUM", "HIGH": "HIGH"}
Gate = None  # set by install(); the self-test uses a local stand-in


def load_schema() -> dict:
    with open(SCHEMA_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def secs(t: str) -> int:
    n = [int(x) for x in t.split(":")]
    return n[0] * 60 + n[1] if len(n) == 2 else n[0] * 3600 + n[1] * 60 + n[2]


def fmt(s: int) -> str:
    h, rest = divmod(s, 3600)
    m, sec = divmod(rest, 60)
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "unknown"


def worst(*grades) -> dict:
    gs = [g for g in grades if isinstance(g, dict) and g.get("letter")]
    if not gs:
        return {"letter": "NS", "basis": "no grade on the source item"}
    g = max(gs, key=lambda x: WORST.index(x["letter"]))
    out = {"letter": g["letter"], "basis": g.get("basis") or "graded at the source"}
    if "n" in g:
        out["n"] = g["n"]
    return out


def cited_times(text: str) -> list[int]:
    """Timestamps the prose cites inside [brackets], e.g. [15:49] or [8:44-9:36, 27:48]."""
    out = []
    for b in BRACKET.findall(text or ""):
        out += [secs(t) for t in TS.findall(b)]
    return out


def reads(doc: dict) -> dict:
    return {k: doc.get(k) for k in ("meta", "call", "claims", "beliefs", "next_steps")}


# --------------------------------------------------------------------------- build

def build(doc: dict, ssot_rel: str, prior_kairos: list | None = None, schema: dict | None = None) -> tuple[dict, dict]:
    """Return (atlas file object, SSOT atlas value). Deterministic: same input, same bytes."""
    schema = schema or load_schema()
    rule, kz = schema["x-fidelity"], schema["x-kairos"]
    meta = doc.get("meta") or {}
    report_id = meta.get("report_id") or os.path.splitext(os.path.basename(ssot_rel))[0]
    atoms = [a for a in (doc.get("call") or {}).get("atoms") or [] if isinstance(a, dict) and a.get("id")]
    by_id = {a["id"]: a for a in atoms}
    by_s: dict[int, list[str]] = {}
    for a in atoms:
        by_s.setdefault(secs(a["t"]), []).append(a["id"])
    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    unanchored: list[str] = []

    def node(kind, ref, label, s, grade=None, audience=None):
        nid = f"{kind}:{ref}"
        n = {"id": nid, "tier": TIER_OF[kind], "kind": kind, "t": fmt(s) if s is not None else None,
             "label": (label or ref).strip()[:120] or ref, "ref": ref}
        if s is not None:
            n["s"] = s
        if grade:
            n["grade"] = grade
        if audience:
            n["audience"] = audience
        nodes[nid] = n
        return nid

    def edge(frm, to, kind, evidence, grade):
        ev = sorted(set(evidence), key=lambda x: (secs(by_id[x]["t"]), x))
        s = max([nodes[frm].get("s", 0), nodes[to].get("s", 0)] + [secs(by_id[x]["t"]) for x in ev])
        edges.append({"id": "", "from": frm, "to": to, "kind": kind, "t": fmt(s), "s": s, "evidence": ev,
                      "grade": grade})

    def atoms_for(item: dict, text: str) -> list[str]:
        ids = [x for x in item.get("atoms") or item.get("cites") or [] if x in by_id]
        if ids:
            return ids
        return [aid for s in cited_times(text) for aid in by_s.get(s, [])]

    # tier 0 and 1: atoms and their speakers
    first_said: dict[str, int] = {}
    for a in atoms:
        first_said[a["speaker"]] = min(first_said.get(a["speaker"], 10**9), secs(a["t"]))
    for name, s in sorted(first_said.items(), key=lambda x: (x[1], x[0])):
        n_atoms = sum(1 for a in atoms if a["speaker"] == name)
        node("person", slug(name), name, s, {"letter": "NS", "basis": f"speaker label on {n_atoms} atom(s)", "n": n_atoms})
    for a in atoms:
        node("atom", a["id"], a["text"], secs(a["t"]), a.get("grade"), a.get("audience"))
    for a in atoms:
        edge(f"atom:{a['id']}", f"person:{slug(a['speaker'])}", "said_by", [a["id"]], worst(a.get("grade")))
        if a.get("parent") in by_id:
            p = by_id[a["parent"]]
            edge(f"atom:{a['id']}", f"atom:{p['id']}", "part_of", [a["id"], p["id"]], worst(a.get("grade"), p.get("grade")))

    # tier 3: beliefs (priors carried into the call: t = 0:00)
    belief_atoms: dict[str, list[str]] = {}
    for b in doc.get("beliefs") or []:
        if not isinstance(b, dict) or not b.get("id"):
            continue
        nid = node("belief", b["id"], b.get("claim") or b["id"], 0, b.get("grade"), b.get("audience"))
        ids = atoms_for(b, b.get("evidence") or "")
        belief_atoms[b["id"]] = ids
        for aid in ids:
            edge(f"atom:{aid}", nid, "updates", [aid], worst(by_id[aid].get("grade"), b.get("grade")))

    # tier 2: claims
    for c in doc.get("claims") or []:
        if not isinstance(c, dict) or not c.get("id"):
            continue
        ids = [x for x in (c.get("cites") or []) + [e.get("atom") for e in c.get("evidence") or []] if x in by_id]
        s = max((secs(by_id[x]["t"]) for x in ids), default=None)
        nid = node("claim", c["id"], c.get("said") or c["id"], s, c.get("grade"), c.get("audience"))
        if s is None:
            unanchored.append(f"claim {c['id']}: cites no atom in call.atoms")
            continue
        for aid in sorted(set(ids)):
            edge(nid, f"atom:{aid}", "cites", [aid], worst(c.get("grade"), by_id[aid].get("grade")))
        if c.get("belief") and f"belief:{c['belief']}" in nodes:
            edge(nid, f"belief:{c['belief']}", "moves", ids, worst(c.get("grade")))

    # tier 4: decisions (next_steps)
    for i, st in enumerate(doc.get("next_steps") or [], 1):
        if not isinstance(st, dict):
            continue
        text = st.get("text") or st.get("action") or f"next step {i}"
        ids = atoms_for(st, text)
        s = max((secs(by_id[x]["t"]) for x in ids), default=None)
        nid = node("decision", f"n{i}", text, s, st.get("grade"), st.get("audience"))
        if s is None:
            unanchored.append(f"decision n{i}: no atom or cited timestamp to stand on")
            continue
        g = worst(st.get("grade"), *[by_id[x].get("grade") for x in ids])
        for aid in sorted(set(ids)):
            edge(nid, f"atom:{aid}", "decided_from", [aid], g)
        owner = st.get("owner")
        if owner and f"person:{slug(owner)}" in nodes and nodes[f"person:{slug(owner)}"]["s"] <= s:
            edge(nid, f"person:{slug(owner)}", "owned_by", ids, g)

    edges.sort(key=lambda e: (e["s"], TIER_OF[nodes[e["from"]]["kind"]], e["from"], e["to"], e["kind"]))
    for i, e in enumerate(edges, 1):
        e["id"] = f"e{i:03d}"

    # kairos: pre-registered rule x-kairos; ids stay stable across reruns
    kairos, ssot_kairos = [], []
    prior = {(k.get("belief"), k.get("atom")): k["id"] for k in prior_kairos or [] if k.get("id")}
    used = set(prior.values())
    nxt = 1
    for b in doc.get("beliefs") or []:
        if not isinstance(b, dict) or not b.get("id"):
            continue
        conf = b.get("confidence") or []
        if len(conf) != 2 or not all(isinstance(x, (int, float)) for x in conf):
            continue
        if round(abs(conf[1] - conf[0]), 2) < kz["min_move"]:
            continue
        ids = belief_atoms.get(b["id"]) or []
        if not ids:
            unanchored.append(f"belief {b['id']}: moved {conf[0]} to {conf[1]} but cites no atom in call.atoms")
            continue
        aid = min(ids, key=lambda x: (secs(by_id[x]["t"]), x))
        kid = prior.get((b["id"], aid))
        if not kid:
            while f"k{nxt:02d}" in used:
                nxt += 1
            kid = f"k{nxt:02d}"
            used.add(kid)
        g = worst(by_id[aid].get("grade"), b.get("grade"))
        what = f"{b['id']} {(b.get('claim') or '').strip()[:80]} ({b.get('verdict') or 'moved'})".strip()
        s = secs(by_id[aid]["t"])
        kairos.append({"id": kid, "node": f"belief:{b['id']}", "atom": aid, "t": fmt(s), "s": s, "what": what,
                       "from": conf[0], "to": conf[1], "grade": g})
        ssot_kairos.append({"id": kid, "atom": aid, "belief": b["id"],
                            "note": f"confidence {conf[0]} to {conf[1]}: {what}", "grade": g})
    kairos.sort(key=lambda k: (k["s"], k["id"]))
    ssot_kairos.sort(key=lambda k: k["id"])

    node_list = sorted(nodes.values(), key=lambda n: (n["tier"], n.get("s", 10**9), n["id"]))
    for n in node_list:
        if n["t"] is None and not any(u.startswith(f"{n['kind']} {n['ref']}:") for u in unanchored):
            unanchored.append(f"{n['kind']} {n['ref']}: t null")
    tiers = fidelity(node_list, edges, rule)
    gates = {t["gate"] for t in tiers}
    overall = "RED" if "fail" in gates else "GREEN" if gates == {"pass"} else "YELLOW"
    atlas = {
        "schema": SCHEMA_ID,
        "built": meta.get("date") or "undated",
        "gate": overall,
        "title": f"Recoil atlas: {report_id}",
        "note": "Tiers run base (index 0) to apex: atoms, people, claims, beliefs, decisions. docs is the node count. "
                "Render state per tier follows x-fidelity in runtime/specs/arcs-atlas-v2.schema.json. Internal: "
                "carries the SSOT's audience tags; not counterpart-safe until /recoil-ship.",
        "source": {"ssot": ssot_rel, "report_id": report_id,
                   "input_hash": v2_hash(reads(doc))},
        "tiers": tiers,
        "nodes": node_list,
        "edges": edges,
        "kairos": kairos,
        "fidelity": {k: rule[k] for k in ("countable_letters", "sharp_letters", "degraded_min_edges",
                                          "sharp_min_edges", "sharp_min_share")} | {"min_move": kz["min_move"]},
        "unanchored": unanchored,
    }
    ssot_atlas = {
        "target": SCHEMA_ID,
        "file": os.path.join(GENERATED, f"{report_id}.atlas.json"),
        "exported_at": atlas["built"],
        "refs": [{"node": n["id"], "kind": n["kind"], "ref": n["ref"], "tier": n["tier"],
                  "grade": n.get("grade") or {"letter": "NS", "basis": "no grade on the source item"}}
                 for n in node_list],
        "kairos": ssot_kairos,
    }
    return atlas, ssot_atlas


def v2_hash(obj) -> str:
    import hashlib
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:16]


def fidelity(nodes: list[dict], edges: list[dict], rule: dict) -> list[dict]:
    """The x-fidelity rule: cross-tier countable edges per tier -> render state and v1 gate."""
    tier_of = {n["id"]: n["tier"] for n in nodes}
    out = []
    for i, (name, kind) in enumerate(TIERS):
        count = sum(1 for n in nodes if n["tier"] == i)
        inc = [e for e in edges if tier_of[e["from"]] != tier_of[e["to"]] and i in (tier_of[e["from"]], tier_of[e["to"]])]
        countable = [e for e in inc if e["grade"]["letter"] in rule["countable_letters"]]
        sharp = [e for e in countable if e["grade"]["letter"] in rule["sharp_letters"]]
        if count == 0:
            render = "FLAT"
        elif len(countable) < rule["degraded_min_edges"]:
            render = "GRAIN"
        elif len(countable) >= rule["sharp_min_edges"] and len(sharp) >= rule["sharp_min_share"] * len(countable):
            render = "SHARP"
        else:
            render = "DEGRADED"
        out.append({"name": name, "kind": kind, "docs": count, "gate": rule["v1_gate"][render], "render": render,
                    "edges": len(countable), "sharp_edges": len(sharp), "n": len(countable)})
    return out


# --------------------------------------------------------------------------- gate

def check(atlas: dict, doc: dict, schema: dict | None = None) -> tuple[bool, list[str]]:
    schema = schema or load_schema()
    bad: list[str] = []
    rep = v2.Report()
    v2.check(atlas, schema, schema, rep)
    bad += [f"schema: {e}" for e in rep.errors]
    nodes = {n.get("id"): n for n in atlas.get("nodes") or []}
    if len(nodes) != len(atlas.get("nodes") or []):
        bad.append("nodes: duplicate node id")
    tiers = atlas.get("tiers") or []
    if [t.get("name") for t in tiers] != [n for n, _ in TIERS]:
        bad.append(f"tiers: expected {[n for n, _ in TIERS]}, got {[t.get('name') for t in tiers]}")
    for t in tiers:  # the v1 loader contract (ZigguratLoader toZigTiers)
        if not isinstance(t.get("name"), str) or not isinstance(t.get("docs"), int) or t.get("gate") not in ("pass", "warn", "fail"):
            bad.append(f"tiers: {t.get('name')!r} breaks the v1 shape (name str, docs number, gate pass|warn|fail)")
    # 1. every edge has evidence
    no_ev = [e["id"] for e in atlas.get("edges") or [] if not e.get("evidence")]
    if no_ev:
        bad.append(f"evidence: {len(no_ev)} edge(s) with none: {no_ev[:5]}")
    for e in atlas.get("edges") or []:
        for x in e.get("evidence") or []:
            if f"atom:{x}" not in nodes:
                bad.append(f"evidence: {e['id']} cites {x}, not an atom in this atlas")
        if e.get("from") not in nodes or e.get("to") not in nodes:
            bad.append(f"edges: {e.get('id')} joins a missing node ({e.get('from')} to {e.get('to')})")
    if any(b.startswith("edges:") for b in bad):
        return False, bad
    # 2. no edge goes backward in time; acyclic
    for e in atlas.get("edges") or []:
        f, t = nodes[e["from"]], nodes[e["to"]]
        if f.get("t") is None or t.get("t") is None:
            bad.append(f"time: {e['id']} touches a node with t null")
            continue
        ev_s = [nodes[f"atom:{x}"]["s"] for x in e.get("evidence") or [] if f"atom:{x}" in nodes]
        if t["s"] > f["s"]:
            bad.append(f"time: {e['id']} {e['from']} ({f['t']}) points forward to {e['to']} ({t['t']})")
        if e["s"] < max([f["s"], t["s"]] + ev_s) or fmt(e["s"]) != e["t"]:
            bad.append(f"time: {e['id']} cut at {e['t']}, before an endpoint or its evidence")
    adj: dict[str, list[str]] = {}
    for e in atlas.get("edges") or []:
        adj.setdefault(e["from"], []).append(e["to"])
    state: dict[str, int] = {}

    def cyclic(u: str) -> bool:
        state[u] = 1
        for w in adj.get(u, []):
            if state.get(w) == 1 or (state.get(w) is None and cyclic(w)):
                return True
        state[u] = 2
        return False
    if any(state.get(u) is None and cyclic(u) for u in list(adj)):
        bad.append("time: the edge graph has a cycle")
    # 3. kairos list matches the SSOT, and the rule finds no other move
    ssot_k = {(k.get("id"), k.get("atom"), k.get("belief")) for k in ((doc.get("atlas") or {}).get("kairos") or [])}
    file_k = {(k.get("id"), k.get("atom"), k.get("node", "").split(":", 1)[-1]) for k in atlas.get("kairos") or []}
    if ssot_k != file_k:
        bad.append(f"kairos: atlas {sorted(file_k)} != SSOT {sorted(ssot_k)}")
    min_move = schema["x-kairos"]["min_move"]
    marked = {k[2] for k in file_k}
    for b in doc.get("beliefs") or []:
        conf = (b or {}).get("confidence") or []
        if len(conf) == 2 and all(isinstance(x, (int, float)) for x in conf) and round(abs(conf[1] - conf[0]), 2) >= min_move:
            if b["id"] not in marked and not any(u.startswith(f"belief {b['id']}:") for u in atlas.get("unanchored") or []):
                bad.append(f"kairos: belief {b['id']} moved {conf[0]} to {conf[1]} with no mark and no unanchored line")
    # 4. render states follow the pre-registered rule
    want = fidelity(list(nodes.values()), atlas.get("edges") or [], schema["x-fidelity"])
    if [(t["name"], t["render"], t["edges"]) for t in want] != [(t.get("name"), t.get("render"), t.get("edges")) for t in tiers]:
        bad.append("fidelity: tier render states differ from x-fidelity recomputed")
    n_e, n_k = len(atlas.get("edges") or []), len(atlas.get("kairos") or [])
    lines = bad or [f"J5 atlas: {len(nodes)} nodes, {n_e} edges, {n_k} kairos; every edge evidenced; "
                    "time order holds; acyclic; kairos matches the SSOT"]
    if not bad:
        lines.append("J5 tiers: " + "; ".join(f"{t['name']} {t['docs']} nodes {t['render']} (n={t['n']})" for t in tiers))
        lines += [f"J5 unanchored: {u}" for u in atlas.get("unanchored") or []]
    return not bad, lines


# --------------------------------------------------------------------------- beats (recoil-runner-beats)

def build_beats(doc: dict, atlas: dict) -> dict:
    """A recoil-beats data file from the SSOT and its atlas. Deterministic; nothing invented."""
    meta = doc.get("meta") or {}
    atoms = sorted((a for a in (doc.get("call") or {}).get("atoms") or [] if isinstance(a, dict) and a.get("id")),
                   key=lambda a: (secs(a["t"]), a["id"]))
    groups: list[list[dict]] = []
    for a in atoms:
        if groups and secs(groups[-1][0]["t"]) == secs(a["t"]):
            groups[-1].append(a)
        else:
            groups.append([a])
    beat_of = {a["id"]: i for i, g in enumerate(groups) for a in g}
    anchors: dict[str, list[str]] = {}
    for e in atlas.get("edges") or []:
        if e["kind"] == "updates":
            anchors.setdefault(e["to"].split(":", 1)[1], []).extend(e["evidence"])
    beats = []
    for i, g in enumerate(groups):
        s = secs(g[0]["t"])
        speakers = list(dict.fromkeys(a["speaker"] for a in g))
        quote = " / ".join(a["text"] for a in g)
        b = {"id": g[0]["id"], "t_start": s, "t_end": secs(groups[i + 1][0]["t"]) if i + 1 < len(groups) else s,
             "speaker": " and ".join(speakers), "summary": f"Says \"{quote}\".",
             "evidence": quote}
        auds = {a.get("audience") for a in g}
        if auds == {"both"}:
            b["audience"] = "both"
        elif auds - {None, "both"}:
            b["audience"] = sorted(auds - {None, "both"})[0]
        beats.append(b)
    beliefs, unanchored = [], []
    for bl in doc.get("beliefs") or []:
        if not isinstance(bl, dict) or not bl.get("id"):
            continue
        conf = bl.get("confidence") or []
        out = {"id": bl["id"], "claim": bl.get("claim") or bl["id"]}
        for k in ("audience",):
            if bl.get(k):
                out[k] = bl[k]
        if conf:
            out["confidence"] = conf
        if CONVICTION.get(str(bl.get("conviction") or "").upper()):
            out["conviction"] = CONVICTION[str(bl["conviction"]).upper()]
        beliefs.append(out)
        if len(conf) != 2 or conf[0] == conf[1]:
            continue
        ids = [x for x in anchors.get(bl["id"]) or [] if x in beat_of]
        if not ids:
            unanchored.append(f"{bl['id']} moved {conf[0]} to {conf[1]} but cites no atom; the player shows its prior")
            continue
        aid = min(ids, key=lambda x: (beat_of[x], x))
        beats[beat_of[aid]].setdefault("belief_deltas", []).append({"belief": bl["id"], "to": conf[1]})
    for k in atlas.get("kairos") or []:
        b = beats[beat_of[k["atom"]]]
        label = f"{k['id']} at atom {k['atom']} ({k['t']}): {k['node'].split(':', 1)[1]} {k['from']} to {k['to']}"
        b["kairos"] = {"label": label if "kairos" not in b else b["kairos"]["label"] + "; " + label, "lock": "open"}
    note = (f"Generated by stage J5 from {atlas['source']['ssot']} (atlas {atlas['source'].get('input_hash')}). "
            "One beat per atom time; each beat id is its atom id. Internal: carries the SSOT's audience tags.")
    if unanchored:
        note += " Unanchored: " + "; ".join(unanchored) + "."
    return {"meta": {k: meta[k] for k in ("report_id", "counterpart", "company", "date") if meta.get(k)} | {"note": note},
            "beliefs": beliefs, "beats": beats}


def player_page(beats_doc: dict) -> str:
    """The recoil player template with this run's data swapped in for the demo's two data lines."""
    import recoil_brief as rb
    import backlog_graph as bg
    errs = rb.check_beats(beats_doc)
    if errs:
        raise ValueError("beats invalid: " + "; ".join(errs))
    proj = rb.project_player(beats_doc, "internal")
    rows = [{"id": f"n{i}-" + slug(" ".join((st.get("text") or "").split()[:4]))[:32], "jtbd": (st.get("text") or "")[:200], "state": "OPEN", "depends_on": [],
             "route": {"tool": "NOT-RESOLVED"}} for i, st in enumerate(beats_doc.get("_next_steps") or [], 1)]
    os.environ.setdefault("BACKLOG_RIPENESS_GH_STUB", "{}")
    import datetime as _dt
    day = beats_doc["meta"].get("date") or "2026-01-01"
    graph = bg.build(rows, _dt.date.fromisoformat(day)) if rows else {"today": day, "rows": 0, "active": 0, "nodes": []}
    tpl = open(os.path.join(PLAYER_DIR, "recoil-player.html"), encoding="utf-8").read().split("\n")
    p_lines = [i for i, ln in enumerate(tpl) if ln.startswith("var P=")]
    g_lines = [i for i, ln in enumerate(tpl) if ln.startswith("var G=")]
    if len(p_lines) != 1 or len(g_lines) != 1:
        raise ValueError("player template: expected exactly one 'var P=' and one 'var G=' line")
    heads = [i for i, ln in enumerate(tpl) if ln.startswith('<header class="pl-head">')]
    if len(heads) != 1 or not (tpl[heads[0] + 1].startswith("<p>") and tpl[heads[0] + 1].endswith("</p></header>")):
        raise ValueError("player template: expected the header lede on the line after <header class=\"pl-head\">")
    m = beats_doc["meta"]
    moved = [b for b in beats_doc["beliefs"] if len(b.get("confidence") or []) == 2
             and b["confidence"][0] != b["confidence"][1]]
    placed = {d["belief"] for bt in beats_doc["beats"] for d in bt.get("belief_deltas") or []}
    who = ", ".join(x for x in (m.get("counterpart"), m.get("company"), m.get("date")) if x) or m.get("report_id", "")
    lede = (f"{who}. {len(moved)} of {len(beats_doc['beliefs'])} beliefs moved; {len(placed)} land on a moment in the "
            "call, the rest keep their prior here. Each card is what I heard, in the order I heard it, and how far it "
            "moved the belief. Built by stage J5 from the recoil run. Internal.")
    tpl[heads[0] + 1] = "<p>" + html.escape(lede) + "</p></header>"
    js = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")  # noqa: E731
    tpl[p_lines[0]] = "var P=" + js(proj) + ";"
    tpl[g_lines[0]] = "var G=" + js(graph) + ";"
    return "\n".join(tpl)


def beats_files(doc: dict, atlas: dict, run_dir: str) -> dict:
    """{repo-relative path: text} for the three player files of this run."""
    bd = build_beats(doc, atlas)
    page = player_page(bd | {"_next_steps": doc.get("next_steps") or []})
    return {os.path.join(run_dir, "beats.json"): dump(bd),
            os.path.join(run_dir, "player.html"): page,
            **{os.path.join(run_dir, f): open(os.path.join(PLAYER_DIR, f), encoding="utf-8").read() for f in PLAYER_ASSETS}}


def check_beats_export(bd: dict, atlas: dict) -> tuple[bool, list[str]]:
    import recoil_brief as rb
    bad = [f"beats: {e}" for e in rb.check_beats(bd)]
    atoms = {n["ref"] for n in atlas.get("nodes") or [] if n["kind"] == "atom"}
    pins = [b for b in bd.get("beats") or [] if b.get("kairos")]
    for b in bd.get("beats") or []:
        if b["id"] not in atoms:
            bad.append(f"beats: {b['id']} is not an atom in the atlas")
    for b in pins:
        if f"atom {b['id']}" not in b["kairos"]["label"]:
            bad.append(f"beats: kairos pin on {b['id']} does not name its atom")
    want = sorted({k["atom"] for k in atlas.get("kairos") or []})
    if sorted(b["id"] for b in pins) != want:
        bad.append(f"beats: pins on {sorted(b['id'] for b in pins)}, atlas kairos atoms {want}")
    n = len(bd.get("beats") or [])
    return not bad, bad or [f"J5 beats: {n} beats, {len(pins)} kairos pin(s), each on its atom; check_beats OK"]


# --------------------------------------------------------------------------- stage hooks

def dump(obj: dict) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def j5_run(ctx, doc: dict) -> dict:
    ssot_rel = (ctx.source or {}).get("path") or os.path.join(GENERATED, f"{ctx.stem}.json")
    atlas, ssot_atlas = build(doc, ssot_rel, prior_kairos=(doc.get("atlas") or {}).get("kairos"))
    ctx.atlas_v2 = (ssot_atlas["file"], atlas)
    ctx.write(ssot_atlas["file"], dump(atlas))
    ctx.beats_v1 = beats_files(doc, atlas, ctx.run_dir)
    for rel, text in ctx.beats_v1.items():
        ctx.write(rel, text)
    return {"atlas": ssot_atlas}


def j5_gate(ctx, doc: dict):
    got = getattr(ctx, "atlas_v2", None)
    if not got:
        return Gate(False, ["J5 atlas: export did not run"])
    rel, atlas = got
    ok, lines = check(atlas, doc)
    full = os.path.join(ctx.root, rel)
    if ok and not ctx.dry_run:
        on_disk = open(full, encoding="utf-8").read() if os.path.exists(full) else ""
        if on_disk != dump(atlas):
            ok, lines = False, lines + [f"J5 atlas: {rel} on disk differs from the export"]
    files = getattr(ctx, "beats_v1", None) or {}
    bd = json.loads(next((t for r, t in files.items() if r.endswith("beats.json")), "{}"))
    b_ok, b_lines = check_beats_export(bd, atlas)
    ok, lines = ok and b_ok, lines + b_lines
    if ok and not ctx.dry_run:
        for r, t in files.items():
            f = os.path.join(ctx.root, r)
            if not os.path.exists(f) or open(f, encoding="utf-8").read() != t:
                ok, lines = False, lines + [f"J5 beats: {r} on disk differs from the export"]
    lines.append(f"J5 file: {rel}" + (" (dry run: not written)" if ctx.dry_run else ""))
    lines += [f"J5 file: {r}" for r in files if os.path.basename(r) not in PLAYER_ASSETS]
    return Gate(ok, lines)


def install(svc) -> None:
    global Gate
    Gate = svc.Gate
    svc.register(svc.Stage("J5", ("atlas",), j5_run, j5_gate, version=VERSION, print_name="atlas",
                           builder="atlas-v2-schema-export (R9)", reads=reads))


# --------------------------------------------------------------------------- self-test

def _fixture() -> dict:
    g = lambda L: {"letter": L, "basis": "self-test"}  # noqa: E731
    atoms = [
        {"id": "a001", "t": "0:10", "speaker": "Ana", "kind": "utterance", "text": "we ship in March", "grade": g("B")},
        {"id": "a002", "t": "1:05", "speaker": "Zach", "kind": "utterance", "text": "budget is 40k", "grade": g("A")},
        {"id": "a003", "t": "1:05", "speaker": "Zach", "kind": "number", "text": "40k", "parent": "a002", "value": 40000, "grade": g("A")},
        {"id": "a004", "t": "2:30", "speaker": "Ana", "kind": "promise", "text": "I'll send the SOW", "grade": g("C")},
    ]
    return {
        "schema": "arcs.recoil.ssot.v2", "meta": {"report_id": "2026-11-12-selftest", "date": "2026-11-12"},
        "call": {"atoms": atoms},
        "beliefs": [
            {"id": "P1", "claim": "Budget exists", "evidence": "said so [1:05]", "inference": "OBS",
             "confidence": [0.4, 0.9], "conviction": "HIGH", "verdict": "HOLDS"},
            {"id": "P2", "claim": "Timeline is firm", "evidence": "no timestamp here", "inference": "IMP",
             "confidence": [0.5, 0.8], "conviction": "MED", "verdict": "NEW"},
            {"id": "P3", "claim": "Small drift", "evidence": "[0:10]", "inference": "IMP",
             "confidence": [0.5, 0.55], "conviction": "LOW", "verdict": "UNTESTED"},
        ],
        "claims": [
            {"id": "c001", "said": "budget is 40k", "premise": "p", "mechanism": "m", "ruling": "GROUNDED",
             "evidence": [{"atom": "a002", "quote": "budget is 40k"}], "cites": ["a002", "a003"], "belief": "P1", "grade": g("A")},
        ],
        "next_steps": [{"owner": "Ana", "text": "Send the SOW [2:30]"}, {"owner": "Zach", "text": "Review it"}],
    }


def self_test() -> int:
    global Gate
    fails: list[str] = []

    def ok(cond: bool, label: str):
        print(("ok   " if cond else "FAIL ") + label)
        if not cond:
            fails.append(label)

    import recoil_service as svc  # the real runner and registry
    schema = load_schema()
    for k in ("x-fidelity", "x-kairos"):
        ok(k in schema, f"schema carries the pre-registered {k} thresholds")
    doc = _fixture()
    atlas, sa = build(doc, "runtime/recoil/generated/2026-11-12-selftest.json", schema=schema)
    doc["atlas"] = sa
    good, lines = check(atlas, doc, schema)
    ok(good, "fixture atlas passes every J5 gate: " + lines[0])
    kinds = sorted({e["kind"] for e in atlas["edges"]})
    ok(kinds == ["cites", "decided_from", "moves", "owned_by", "part_of", "said_by", "updates"],
       f"fixture cuts every edge kind: {kinds}")
    ok([k["node"] for k in atlas["kairos"]] == ["belief:P1"], "kairos: P1 moved 0.4 to 0.9 and is marked at its atom")
    ok(any(u.startswith("belief P2:") for u in atlas["unanchored"]), "kairos: P2 moved with no atom, listed unanchored")
    ok(not any("P3" in k["node"] for k in atlas["kairos"]), "kairos: P3 moved 0.05, under min_move, not marked")
    ok(any(u.startswith("decision n2:") for u in atlas["unanchored"]), "a decision with no atom is listed unanchored")
    ok(atlas["nodes"][0]["kind"] == "atom" and [t["name"] for t in atlas["tiers"]] == [n for n, _ in TIERS],
       "tiers run atoms, people, claims, beliefs, decisions")
    a2, _ = build(doc, "runtime/recoil/generated/2026-11-12-selftest.json", prior_kairos=sa["kairos"], schema=schema)
    ok(dump(a2) == dump(atlas), "build is deterministic (same input, same bytes)")

    # each gate fails on a bad atlas
    def broken(mut, label, needle):
        a = copy.deepcopy(atlas)
        d = copy.deepcopy(doc)
        mut(a, d)
        g2, ln = check(a, d, schema)
        ok(not g2 and any(needle in x for x in ln), f"gate refuses {label}: " + next((x for x in ln if needle in x), "no line"))
    broken(lambda a, d: a["edges"][0].update(evidence=[]), "an edge with no evidence", "evidence:")
    broken(lambda a, d: a["edges"][0].update(evidence=["a999"]), "evidence that is not an atom", "evidence:")
    up = next(e for e in atlas["edges"] if e["kind"] == "updates")
    broken(lambda a, d: a["edges"].append({**up, "id": "e999", "from": up["to"], "to": up["from"]}),
           "an edge pointing forward in time", "time:")
    broken(lambda a, d: a["edges"][-1].update(s=0, t="0:00"), "an edge cut before its evidence", "time:")
    cyc = lambda a, d: a["edges"].append({**[e for e in a["edges"] if e["kind"] == "part_of"][0], "id": "e998",  # noqa: E731
                                          "from": "atom:a002", "to": "atom:a003"})
    broken(cyc, "a cycle", "cycle")
    broken(lambda a, d: d["atlas"].update(kairos=[]), "a kairos list that differs from the SSOT", "kairos:")
    broken(lambda a, d: (a["kairos"].clear(), d["atlas"].update(kairos=[])), "a belief move with no mark", "kairos: belief P1")
    broken(lambda a, d: a["tiers"][0].update(render="FLAT"), "a hand-set render state", "fidelity:")
    broken(lambda a, d: a["tiers"][0].update(docs="many"), "a tier that breaks the v1 shape", "v1 shape")

    # the pre-registered fidelity thresholds, at their edges
    rule = schema["x-fidelity"]

    def state(letters):
        ns = [{"id": "atom:x", "tier": 0}, {"id": "person:y", "tier": 1}]
        es = [{"from": "atom:x", "to": "person:y", "grade": {"letter": L}} for L in letters]
        return fidelity(ns, es, rule)[0]["render"]
    ok(fidelity([], [], rule)[0]["render"] == "FLAT", "an empty tier renders FLAT (v1 gate fail)")
    ok(state("CC") == "GRAIN", "2 countable edges: GRAIN")
    ok(state("CCC") == "DEGRADED", "3 countable edges: DEGRADED")
    ok(state("AAAACCCC") == "SHARP", "8 edges, half A or B: SHARP")
    ok(state("AAACCCCC") == "DEGRADED", "8 edges, under half A or B: DEGRADED")
    ok(state("DDDDDDDDDD") == "GRAIN", "D, E and NS edges do not count")

    # through the real runner in a temp repo: register, run --only J5, rerun UNCHANGED
    saved = dict(svc.STAGES)
    try:
        install(svc)
        with tempfile.TemporaryDirectory() as td:
            os.makedirs(os.path.join(td, GENERATED))
            rel = os.path.join(GENERATED, "2026-11-12-selftest.json")
            fx = _fixture()
            fx.pop("claims")  # J3 claims carry fields the SSOT validator checks against atoms; keep J5 isolated
            with open(os.path.join(td, rel), "w", encoding="utf-8") as fh:
                fh.write(dump(fx))
            rc, out = svc.run(rel, only="J5", root=td)
            ok(rc == 0 and any(x.startswith("J5 atlas: PASS") for x in out), "runner: J5 PASS on a v2 SSOT (" +
               next((x for x in out if x.startswith("J5")), "no J5 line") + ")")
            apath = os.path.join(td, GENERATED, "2026-11-12-selftest.atlas.json")
            ok(os.path.exists(apath), "runner: writes runtime/recoil/generated/<id>.atlas.json")
            ssot = json.load(open(os.path.join(td, rel), encoding="utf-8"))
            ok((ssot.get("atlas") or {}).get("file", "").endswith(".atlas.json") and ssot["atlas"]["kairos"],
               "runner: the SSOT carries the atlas pointer and its kairos marks")
            before = open(apath, encoding="utf-8").read()
            rc, out = svc.run(rel, only="J5", root=td)
            ok(rc == 0 and any("UNCHANGED" in x for x in out) and open(apath, encoding="utf-8").read() == before,
               "runner: a rerun with no new input is UNCHANGED")
            rd = os.path.join(td, RUNS_DIR, "2026-11-12-selftest")
            ok(all(os.path.exists(os.path.join(rd, f)) for f in ("beats.json", "player.html") + PLAYER_ASSETS),
               "runner: beats.json, player.html and its assets land under runtime/recoil/runs/<stem>/")
    finally:
        svc.STAGES.clear()
        svc.STAGES.update(saved)

    # the Gasmi fixture through the real registry, dry run: J5 builds and gates, writes nothing
    rc, out = svc.run(os.path.join(GENERATED, "2026-10-29-gasmi.json"), until="J5", dry_run=True)
    j5 = [x for x in out if x.startswith("J5")]
    ok(any(x.startswith(("J5 atlas: PASS", "J5 atlas: UNCHANGED")) for x in j5),
       "Gasmi: J5 PASS on a dry run, UNCHANGED when a local run already did (" + (j5[0] if j5 else "no J5") + ")")
    # beats (recoil-runner-beats): the existing player's schema, fed from the same atlas
    import recoil_brief as rb
    bd = build_beats(doc, atlas)
    ok(rb.check_beats(bd) == [], "beats: the export passes check_beats (schema used as is)")
    ok([b["id"] for b in bd["beats"]] == ["a001", "a002", "a004"], "beats: one beat per atom time, id = first atom")
    ok(bd["beats"][1]["evidence"] == "budget is 40k / 40k", "beats: atoms at one time share a beat, quotes joined")
    ok(bd["beats"][1].get("belief_deltas") == [{"belief": "P1", "to": 0.9}], "beats: P1 moves on its anchor atom a002")
    ok("atom a002" in bd["beats"][1]["kairos"]["label"] and bd["beats"][1]["kairos"]["lock"] == "open",
       "beats: the kairos pin names its atom")
    ok(bd["beats"][0].get("belief_deltas") == [{"belief": "P3", "to": 0.55}] and "kairos" not in bd["beats"][0],
       "beats: P3's sub-threshold move lands on its atom with no pin")
    ok("P2 moved 0.5 to 0.8 but cites no atom" in bd["meta"]["note"], "beats: an unanchored move is named in meta.note")
    ok(check_beats_export(bd, atlas)[0], "beats: export gate passes")
    bad = copy.deepcopy(bd)
    bad["beats"][1]["kairos"]["label"] = "k01 somewhere"
    ok(not check_beats_export(bad, atlas)[0], "beats gate refuses a pin that does not name its atom")
    bad = copy.deepcopy(bd)
    del bad["beats"][1]["kairos"]
    ok(not check_beats_export(bad, atlas)[0], "beats gate refuses a missing pin for an atlas kairos mark")
    page = player_page(bd | {"_next_steps": doc["next_steps"]})
    ok(page.count("\nvar P=") == 1 and "Rowan" not in page and "made-up" not in page and "a002" in page,
       "player page: the demo data and lede are replaced by this run's")
    ok(rb.check_beats({"beliefs": [], "beats": [{"id": "x"}]}) != [], "check_beats is live (refuses a bad beat)")

    print(f"\nself-test: {'PASS' if not fails else 'FAIL'} ({len(fails)} failing)")
    return 1 if fails else 0


if __name__ == "__main__":
    if sys.argv[1:2] == ["--self-test"]:
        sys.exit(self_test())
    print(__doc__)
    sys.exit(0)
