#!/usr/bin/env python3
"""recoil_stage_j4: stage J4 of the recoil call service, the ADR-060 hypercube index (backlog row
recoil-hypercube-index, R8). Stdlib only. Registered in scripts/recoil_service.py by one PLUGINS line.

J4 reads an SSOT v2 record (call.atoms, J2 verbs, J3 claims) and writes `cells[]`: filled coordinates on
the ADR-060 penteract, five axes of five values (3,125 coordinates):

    lens        D Decision, W Window, H Human, C Coherence, R Risk
    resolution  Exec, Strategic, Operational, Tactical, Surgical
    operator    LAB, KKL, BAR, COURT, FUNHOUSE
    verb        analyze, assess, evaluate, synthesize, recapitulate
    l           L1 to L5

How a cell comes to exist (never invented):
  1. Code builds one SOCKET per source item: each J2 verb pass, and each J3 claim no verb pass lists.
     A socket carries the atoms and claims it cites, plus the axes code can fix mechanically:
       verb      fixed from the J2 key (a verb pass is that verb).
     Every other axis (lens, resolution, operator, L, and verb for a claim no verb pass lists) is
     judgment. Operator was fixed from the J3 ruling in version 1; that table was dropped in version 2
     (Zach's go, 2026-11-12) because a ruling says how well a claim is backed and the operator axis says
     which adversary engages it, two of the axes ADR-060 section 1 keeps orthogonal.
  2. One model call (role deep, through recoil_decompose.judge: dry run, missing key or budget make it
     NOT RUN) places each socket on those free axes and writes a one-line note.
  3. Code keeps only enum values, overrides any fixed axis the model changed, keeps only atoms and
     claims the socket already cites (falling back to the socket's own), grades by code, and merges
     sockets that land on one coordinate.
So every cell cites atoms its source item cites; a socket with no atom yields no cell.

Gate: every cell id is its coordinate, every cite exists in call.atoms and in some J2/J3 source, every
claim exists, no em-dashes. Print: runtime/recoil/runs/<stem>/prints/J4.json.

Explorer: _ARTIFACTS/recoil-hypercube-explorer.html loads the SSOT v2 working copy and renders a 2D slice
over any two axes plus the filled-cell list; empty data renders grain with n=0.

Usage: python3 scripts/recoil_service.py run <call> --only J4 [--dry-run] [--budget-usd N]
       python3 scripts/recoil_service.py --self-test   (runs this module's self-test too)
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hypercube_sampler  # noqa: E402  (ADR-060 section 1 axes; one source for the five value lists)
import recoil_decompose as decompose  # noqa: E402  (judge, NotRun, code_grade, clean_cites)

AXES = {"lens": hypercube_sampler.AXES["lens"], "resolution": hypercube_sampler.AXES["resolution"],
        "operator": hypercube_sampler.AXES["operator"], "verb": hypercube_sampler.AXES["verb"],
        "l": hypercube_sampler.AXES["lstack"]}
ORDER = ("lens", "resolution", "operator", "verb", "l")
EM = chr(0x2014)
VERSION = "2"
# What each operator value means, bound only to operators/docs/PERIODIC-TABLE.md and the generated
# operators/OPERATOR-REGISTRY.json (AGENTS.md gotcha 16). The self-test fails if a cited entry drifts.
# BAR and FUNHOUSE have no periodic-table entry; their glosses come from ADR-060 section 4.
OPERATOR_GLOSS = {
    "LAB": ("registry op 17 Detective (binding LABOperator)", "challenge via adversarial reasoning"),
    "KKL": ("periodic table force Kai (Kairos)", "timing: which window is open or closed"),
    "BAR": ("ADR-060 section 4; registry names only a BAR RUIN_RISK verdict", "ruin: what could not be undone"),
    "COURT": ("registry op 18 Immune (binding ConstitutionalCourt)", "an axiom or rule the item must hold to"),
    "FUNHOUSE": ("ADR-060 section 4; no periodic-table entry", "the mirror: a distortion that reads like support"),
}

SYSTEM = (
    "You place items from one recorded call on the ADR-060 penteract. Axes: "
    "lens (D Decision: what is being chosen; W Window: timing and the kairos of it; H Human: who and how "
    "they move; C Coherence: whether the parts hold; R Risk: what could ruin it), "
    "resolution (Exec, Strategic, Operational, Tactical, Surgical: how big the move is), "
    "operator, which adversary engages the item (" + "; ".join(f"{k}: {v[1]}" for k, v in OPERATOR_GLOSS.items())
    + "), "
    "verb (analyze, assess, evaluate, synthesize, recapitulate), "
    "l (L1 coherence of one signal, L2 the path survives, L3 the immune check, L4 holds across domains, "
    "L5 global coherence). Each socket lists its fixed axes; do not change them. Fill only the free axes, "
    "write one plain sentence on why the item works at that coordinate, and cite only atom ids the socket "
    "lists. If the atoms cannot support a placement, skip the socket. No em-dashes. Reply with JSON only: "
    '{"s01": {"lens": "D", "resolution": "Tactical", "operator": "LAB", "l": "L2", "note": "...", "cites": ["a001"]}, ...}')


# --------------------------------------------------------------------------- sockets (code only)

def reads(doc: dict) -> dict:
    return {"atoms": (doc.get("call") or {}).get("atoms"), "verbs": doc.get("verbs"), "claims": doc.get("claims")}


def sockets(doc: dict) -> tuple[list[dict], list[str]]:
    """One socket per J2 verb pass and per J3 claim no verb pass lists. Returns (sockets, notes)."""
    claims = {c["id"]: c for c in doc.get("claims") or []}
    out, notes, listed = [], [], set()
    for v in AXES["verb"]:
        p = (doc.get("verbs") or {}).get(v)
        if not p:
            continue
        cites = decompose.clean_cites(doc, p.get("cites"))
        cl = [c for c in p.get("claims") or [] if c in claims]
        listed.update(cl)
        if not cites:
            notes.append(f"J4 dropped verb:{v}: cites no known atom")
            continue
        fixed = {"verb": v}
        out.append({"src": f"verb:{v}", "fixed": fixed, "cites": cites, "claims": cl,
                    "text": p.get("verdict", "")})
    for cid, c in claims.items():
        if cid in listed:
            continue
        cites = decompose.clean_cites(doc, c.get("cites"))
        if not cites:
            notes.append(f"J4 dropped claim:{cid}: cites no known atom")
            continue
        out.append({"src": f"claim:{cid}", "fixed": {},
                    "cites": cites, "claims": [cid], "text": c.get("said", "")})
    for i, s in enumerate(out, 1):
        s["id"] = f"s{i:02d}"
    return out, notes


def socket_lines(sk: list[dict]) -> list[str]:
    return [f"J4 socket {s['id']} {s['src']} fixed {', '.join(f'{k}={v}' for k, v in s['fixed'].items()) or 'none'}; "
            f"free {', '.join(a for a in ORDER if a not in s['fixed'])}; cites {', '.join(s['cites'])}" for s in sk]


def user_packet(doc: dict, sk: list[dict], extra: str = "") -> str:
    rows = [{"socket": s["id"], "source": s["src"], "text": s["text"], "fixed": s["fixed"],
             "atoms": s["cites"], "claims": s["claims"]} for s in sk]
    return ("ATOMS\n" + decompose.atom_packet(doc) + "\n\nSOCKETS\n" + json.dumps(rows, ensure_ascii=False)
            + (f"\n\nFIX THESE GATE FAILURES\n{extra}" if extra else ""))


# --------------------------------------------------------------------------- cells (code checks the judgment)

def cells_from(doc: dict, sk: list[dict], raw: dict) -> tuple[list[dict], list[str]]:
    by: dict[str, dict] = {}
    notes = []
    for s in sk:
        r = raw.get(s["id"]) if isinstance(raw.get(s["id"]), dict) else None
        if r is None:
            notes.append(f"J4 {s['id']} {s['src']}: not placed by the model (no cell)")
            continue
        coord = {}
        for a in ORDER:
            val = s["fixed"].get(a, r.get(a))
            if a in s["fixed"] and r.get(a) not in (None, s["fixed"][a]):
                notes.append(f"J4 {s['id']}: model changed fixed {a} to {r.get(a)}; kept {s['fixed'][a]}")
            coord[a] = val
        bad = [a for a in ORDER if coord[a] not in AXES[a]]
        note = " ".join(str(r.get("note") or "").replace(EM, ",").split())
        if bad or not note:
            notes.append(f"J4 {s['id']} {s['src']}: dropped, {'bad ' + ', '.join(bad) if bad else 'no note'}")
            continue
        cites = [c for c in decompose.clean_cites(doc, r.get("cites")) if c in s["cites"]] or list(s["cites"])
        cid = ".".join(coord[a] for a in ORDER)
        cell = by.get(cid)
        if cell is None:
            by[cid] = {"id": cid, **coord, "cites": cites, "note": note, "claims": list(s["claims"]),
                       "_src": [s["src"]]}
        else:
            cell["cites"] += [c for c in cites if c not in cell["cites"]]
            cell["claims"] += [c for c in s["claims"] if c not in cell["claims"]]
            cell["note"] += " " + note
            cell["_src"].append(s["src"])
    cells = []
    for cid in sorted(by):
        c = by[cid]
        notes.append(f"J4 cell {cid} <- {', '.join(c.pop('_src'))}; cites {', '.join(c['cites'])}")
        if not c["claims"]:
            c.pop("claims")
        c["grade"] = decompose.code_grade(doc, c["cites"], "the cell")
        cells.append(c)
    return cells, notes


def run(ctx, doc: dict) -> dict:
    sk, notes = sockets(doc)
    lines = notes + socket_lines(sk)
    if not sk:
        n_v, n_c = len(doc.get("verbs") or {}), len(doc.get("claims") or [])
        raise decompose.NotRun(f"J4 has no sockets: {n_v} verb passes and {n_c} claims carry an atom (n=0)", lines)
    try:
        raw = decompose.judge(ctx, "J4", SYSTEM, user_packet(doc, sk))
    except decompose.NotRun as e:
        raise decompose.NotRun(f"{e}; {len(sk)} socket(s) wait, mechanical axes fixed", lines)
    cells, more = cells_from(doc, sk, raw)
    ctx.j4 = lines + more
    return {"cells": cells}


def gate(ctx, doc: dict):
    atoms = {a["id"] for a in (doc.get("call") or {}).get("atoms") or []}
    claims = {c["id"] for c in doc.get("claims") or []}
    sourced = set()
    for p in (doc.get("verbs") or {}).values():
        sourced.update(p.get("cites") or [])
    for c in doc.get("claims") or []:
        sourced.update(c.get("cites") or [])
    cells = doc.get("cells") or []
    lines, ok, seen = list(getattr(ctx, "j4", [])), True, set()
    for c in cells:
        cid = ".".join(str(c.get(a)) for a in ORDER)
        problems = []
        if c.get("id") != cid:
            problems.append(f"id {c.get('id')} is not its coordinate {cid}")
        if c.get("id") in seen:
            problems.append("duplicate coordinate")
        seen.add(c.get("id"))
        if not c.get("cites"):
            problems.append("cites no atom")
        for a in c.get("cites") or []:
            if a not in atoms:
                problems.append(f"cites unknown atom {a}")
            elif a not in sourced:
                problems.append(f"atom {a} is cited by no verb pass or claim (invented)")
        for k in c.get("claims") or []:
            if k not in claims:
                problems.append(f"cites unknown claim {k}")
        if EM in c.get("note", ""):
            problems.append("note has an em-dash")
        if problems:
            ok = False
            lines.append(f"J4 gate: {c.get('id')}: " + "; ".join(problems))
    if ok:
        lines.append(f"J4 gate: {len(cells)} cell(s) of 3,125; every cell cites atoms its J2/J3 source cites")
    return Gate(ok and bool(cells), lines)


def repair(ctx, doc: dict, failed) -> dict:
    sk, _ = sockets(doc)
    cells, more = cells_from(doc, sk, decompose.judge(ctx, "J4 repair", SYSTEM,
                                                       user_packet(doc, sk, "\n".join(failed.lines))))
    ctx.j4 = socket_lines(sk) + more
    return {"cells": cells}


# --------------------------------------------------------------------------- install into the runner

Gate = None  # bound by install()


def install(svc):
    global Gate
    Gate = svc.Gate
    svc.register(svc.Stage("J4", ("cells",), run, gate, repair=repair, version=VERSION, print_name="hypercube",
                           builder="recoil-hypercube-index (R8)", reads=reads))
    return sys.modules[__name__]


# --------------------------------------------------------------------------- self-test (called by recoil_service --self-test)

def self_test(svc, check, snap) -> None:
    import tempfile
    real = decompose.CALLER
    try:
        with tempfile.TemporaryDirectory() as td:
            os.makedirs(os.path.join(td, svc.GENERATED))
            g = lambda letter="B": {"letter": letter, "basis": "fixture", "n": 1}  # noqa: E731
            atoms = [{"id": f"a00{i}", "t": f"0:{10 * i:02d}", "speaker": "Ada", "kind": "utterance",
                      "text": f"atom {i} text", "grade": g()} for i in range(1, 6)]
            base = {"schema": svc.v2.SCHEMA_ID, "meta": {"report_id": "2026-11-02-h", "date": "2026-11-02"},
                    "call": {"atoms": atoms}}
            rel = os.path.join(svc.GENERATED, "2026-11-02-h.json")

            # empty: atoms but no verbs or claims -> NOT RUN, n=0, no cells, model never called
            open(os.path.join(td, rel), "w").write(svc.dump(base))
            decompose.CALLER, calls = decompose._fake([{}])
            rc, out = svc.run(rel, root=td, only="J4", budget_usd=1.0)
            d = json.load(open(os.path.join(td, rel)))
            check(rc == 0 and calls["n"] == 0 and "cells" not in d and any("J4 hypercube: NOT RUN" in ln
                  and "n=0" in ln for ln in out), "J4: no verbs or claims means NOT RUN with n=0, no cell written")

            doc = dict(base)
            doc["verbs"] = {v: {"verdict": f"{v} read", "cites": ["a001", "a002"], "grade": g("C")}
                            for v in AXES["verb"]}
            doc["verbs"]["analyze"]["claims"] = ["c001"]
            doc["claims"] = [
                {"id": "c001", "said": "s1", "premise": "p", "mechanism": "m", "ruling": "GROUNDED",
                 "evidence": [{"atom": "a001", "quote": "atom 1 text"}], "cites": ["a001"], "grade": g()},
                {"id": "c002", "said": "s2", "premise": "p", "mechanism": "m", "ruling": "STRUCK",
                 "evidence": [], "cites": ["a004"], "grade": g()}]
            sk, _ = sockets(doc)
            check([s["src"] for s in sk] == [f"verb:{v}" for v in AXES["verb"]] + ["claim:c002"]
                  and sk[0]["fixed"] == {"verb": "analyze"} and sk[1]["fixed"] == {"verb": "assess"}
                  and sk[-1]["fixed"] == {},
                  "J4 sockets: verb fixed from J2; operator is judgment, never set from a J3 ruling")

            # dry run: sockets print, nothing written, no model call
            open(os.path.join(td, rel), "w").write(svc.dump(doc))
            before = snap(td)
            rc, out = svc.run(rel, root=td, only="J4", dry_run=True, budget_usd=1.0)
            check(rc == 0 and snap(td) == before and calls["n"] == 0
                  and any("J4 hypercube: NOT RUN (dry run" in ln and "6 socket" in ln for ln in out),
                  "J4 dry run: NOT RUN, sockets counted, nothing written")

            # with a model: invented atom dropped, fixed axis kept, bad enum dropped, same coordinate merged
            ans = {"s01": {"lens": "D", "resolution": "Tactical", "l": "L2", "note": "it holds",
                           "cites": ["a001", "a999", "a005"], "operator": "BAR"},
                   "s02": {"lens": "D", "resolution": "Tactical", "operator": "LAB", "l": "L2", "note": "same spot",
                           "verb": "evaluate"},
                   "s04": {"lens": "C", "resolution": "Exec", "l": "L1", "note": "no operator given"},
                   "s03": {"lens": "Q", "resolution": "Tactical", "operator": "LAB", "l": "L2", "note": "bad lens"},
                   "s06": {"lens": "R", "resolution": "Surgical", "operator": "FUNHOUSE", "verb": "evaluate", "l": "L3",
                           "note": "a false path", "cites": ["a004"]}}
            decompose.CALLER, calls = decompose._fake([ans])
            rc, out = svc.run(rel, root=td, only="J4", budget_usd=1.0)
            d = json.load(open(os.path.join(td, rel)))
            cells = {c["id"]: c for c in d.get("cells") or []}
            a = cells.get("D.Tactical.BAR.analyze.L2", {})
            check(rc == 0 and calls["n"] == 1 and a.get("cites") == ["a001"] and a.get("claims") == ["c001"],
                  "J4: an invented or foreign atom id is dropped; the cell keeps only its source's atoms")
            check("D.Tactical.LAB.evaluate.L2" not in cells and "D.Tactical.LAB.assess.L2" in cells,
                  "J4: a model change to a fixed axis (verb) is overridden by code")
            check(not any(k.startswith(("Q.", "C.Exec.")) for k in cells) and len(cells) == 3
                  and "R.Surgical.FUNHOUSE.evaluate.L3" in cells,
                  "J4: an off-axis value or a missing operator drops the cell; nothing is defaulted")
            pr = json.load(open(os.path.join(td, svc.RUNS, "2026-11-02-h", "prints", "J4.json")))
            check(pr["status"] == "PASS" and any("not placed by the model" in ln for ln in pr["gate"]),
                  "J4 print: unplaced sockets are listed, not filled")
            rc, out = svc.run(rel, root=td, only="J4", budget_usd=1.0)
            check(calls["n"] == 1 and any("J4 hypercube: UNCHANGED" in ln for ln in out),
                  "J4: a rerun with no new input is UNCHANGED with no new model call")

            # gate refuses an invented cell written by hand
            bad = json.load(open(os.path.join(td, rel)))
            bad["cells"].append({"id": "H.Exec.COURT.synthesize.L5", "lens": "H", "resolution": "Exec",
                                 "operator": "COURT", "verb": "synthesize", "l": "L5", "cites": ["a003"],
                                 "note": "made up", "grade": g()})
            gt = gate(type("C", (), {})(), bad)
            check(not gt.ok and any("invented" in ln for ln in gt.lines),
                  "J4 gate: a cell citing an atom no verb or claim cites is refused")

            # merge: two sockets landing on one coordinate become one cell with both sources
            m = {"s01": {"lens": "C", "resolution": "Exec", "operator": "LAB", "l": "L1", "note": "one"},
                 "s06": {"lens": "C", "resolution": "Exec", "operator": "LAB", "verb": "analyze", "l": "L1", "note": "two"}}
            m_doc = json.loads(json.dumps(doc))
            sk2, _ = sockets(m_doc)
            cs, _ = cells_from(m_doc, sk2, m)
            check(len(cs) == 1 and cs[0]["cites"] == ["a001", "a002", "a004"] and cs[0]["claims"] == ["c001", "c002"],
                  "J4: two sockets on one coordinate merge into one cell; cites and claims are unioned")

        # operator glosses stay bound to the periodic table and the generated registry (gotcha 16)
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        reg = json.load(open(os.path.join(root, "operators", "OPERATOR-REGISTRY.json"), encoding="utf-8"))
        ops = reg if isinstance(reg, list) else reg.get("operators", list(reg.values()))
        by = {o.get("op"): o for o in ops if isinstance(o, dict)}
        table = open(os.path.join(root, "operators", "docs", "PERIODIC-TABLE.md"), encoding="utf-8").read()
        check(list(OPERATOR_GLOSS) == AXES["operator"]
              and (by.get(17) or {}).get("name") == "Detective"
              and ((by.get(17) or {}).get("binding") or {}).get("symbol") == "LABOperator"
              and (by.get(18) or {}).get("name") == "Immune"
              and ((by.get(18) or {}).get("binding") or {}).get("symbol") == "ConstitutionalCourt"
              and "| **Kai** | Kairos |" in table,
              "J4: operator glosses cover the five values and their cited registry and table entries still exist")
    finally:
        decompose.CALLER = real
