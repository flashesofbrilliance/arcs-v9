#!/usr/bin/env python3
"""Recoil call service stages J1 decompose, J2 verbs, J3 deconstruct (stdlib only). Backlog row
recoil-decompose-verbs (R7). Spec: _PROPOSALS/2026-11-11-recoil-call-service-arc-weld.md §3 J1 to J3, §5, §6.

Plugged into scripts/recoil_service.py with install(svc); not run on its own.
Tests live in `python3 scripts/recoil_service.py --self-test`.

J1 decompose (deterministic, owns `call`).
  Source 1, a transcript: runtime/recoil/transcripts/*.txt whose text carries the call's Granola id,
  in the Granola get_meeting_transcript shape with include_timestamps ("[m:ss] Speaker: text").
  Each timed turn is an utterance atom. A turn with no timestamp is dropped and counted.
  Source 2, the SSOT itself: every quote that sits next to a [m:ss] timestamp in the SSOT's own text
  becomes an utterance atom. The speaker is the nearest person named before the quote in the same
  string (or table row); a quote with no named person before it is dropped and counted, never guessed.
  These atoms are graded C: quoted in the SSOT prose, not read from the transcript.
  Both sources then add child atoms: number (a figure with a unit) and promise (a first-person future
  cue), each a verbatim substring of its parent. Ids are stable: an atom already in call.atoms keeps
  its id, and a rerun only appends.

J2 verbs (owns `verbs`) and J3 deconstruct (owns `claims`) need judgment. The code builds the packet,
calls the `deep` role from src/lib/claude-models.ts (read through scripts/arcs_models.py), and then
checks the answer: unknown atom ids are dropped, grades are set by code from what was cited.
J3's skeleton is deterministic: each Forge claim-adjudication row gives `said`, the ruling, and its
evidence (the atoms at the row's timestamps, quoted whole). Only premise and mechanism come from the model.
The model is never called on --dry-run, without ANTHROPIC_API_KEY, or when the ceiling estimate passes
--budget-usd: the stage then reports NOT RUN with the reason and writes nothing into the SSOT.
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request

TRANSCRIPTS = os.path.join("runtime", "recoil", "transcripts")
ME = "Zach"  # the Granola recorder ("Me") is the operator
EM = chr(0x2014)

TS = r"(\d{1,2}:\d{2}(?::\d{2})?)"
BRACKET = re.compile(r"\[" + TS + r"[^\]]*\]")
QUOTE_THEN_T = re.compile(r'"([^"]{3,400})"[\s,:)]{0,3}\[' + TS + r"[^\]]*\]")
T_THEN_QUOTE = re.compile(r"\[" + TS + r'[^\]]*\][\s:,(]{0,3}"([^"]{3,400})"')
TURN = re.compile(r"^\[" + TS + r"\]\s*([^:\[\]]{1,60}):\s*(.+)$")
UNTIMED_TURN = re.compile(r"^([A-Z][^:\[\]]{0,59}):\s*\S")
GRANOLA_ID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
NUMBER = re.compile(r"(\$)?(\d+(?:\.\d+)?)\s?(%|percent\b|hours?\b|days?\b|weeks?\b|months?\b|years?\b|people\b|k\b|K\b|M\b|B\b)?")
PROMISE = re.compile(r"\b(I'll|I will|we'll|we will|I'm going to|we're going to|I'd schedule|let me|let's)\b", re.I)
TAGS = re.compile(r"<[^>]+>")
VERBS = ("analyze", "assess", "evaluate", "synthesize", "recapitulate")

# Ceiling estimate for the budget gate only, not a bill: dollars per million tokens for the deep role.
EST_IN, EST_OUT, MAX_OUT = 3.0, 15.0, 4000


class NotRun(Exception):
    """The stage did not run its judgment step. The runner prints NOT RUN and the reason; no SSOT write."""

    def __init__(self, reason: str, lines: list[str] | None = None):
        super().__init__(reason)
        self.lines = lines or []


def secs(t: str) -> int:
    n = [int(x) for x in t.split(":")]
    return n[0] * 60 + n[1] if len(n) == 2 else n[0] * 3600 + n[1] * 60 + n[2]


# --------------------------------------------------------------------------- J1 decompose

def people(doc: dict) -> dict:
    """First name -> full name of the people on the call, from the SSOT's own metadata. The operator is
    always present. When meta.closed_call.with names who was on the recorded call, only that person joins
    (the counterpart may not have been on it); otherwise meta.counterpart does."""
    meta = doc.get("meta") or {}
    names = [ME]
    on_call = (meta.get("closed_call") or {}).get("with")
    for raw in ([on_call] if isinstance(on_call, str) and on_call.strip() else [meta.get("counterpart")]):
        if isinstance(raw, str) and raw.strip():
            names.append(re.split(r"[(,]", raw)[0].strip())
    out = {}
    for n in names:
        first = n.split()[0] if n.split() else ""
        if first and first[0].isupper():
            out.setdefault(first, n)
    return out


def granola_id(doc: dict) -> str | None:
    src = ((doc.get("call") or {}).get("source") or {}).get("granola_id")
    if src:
        return src
    meta = doc.get("meta") or {}
    for v in ((meta.get("closed_call") or {}).get("source"), (meta.get("provenance") or {}).get("captured")):
        m = GRANOLA_ID.search(v or "") if isinstance(v, str) and "ranola" in v else None
        if m:
            return m.group(0)
    return None


def find_transcript(root: str, gid: str | None) -> str | None:
    d = os.path.join(root, TRANSCRIPTS)
    if not gid or not os.path.isdir(d):
        return None
    for f in sorted(os.listdir(d)):
        p = os.path.join(d, f)
        if f.endswith(".txt") and gid in open(p, encoding="utf-8", errors="replace").read(4000):
            return os.path.join(TRANSCRIPTS, f)
    return None


def from_transcript(text: str, names: dict) -> tuple[list[dict], dict]:
    atoms, dropped = [], {"untimed turn": 0}
    for ln in text.splitlines():
        m = TURN.match(ln.strip())
        if m:
            spk = m.group(2).strip()
            spk = ME if spk == "Me" else names.get(spk.split()[0], spk)
            atoms.append({"t": m.group(1), "speaker": spk, "kind": "utterance", "text": m.group(3).strip(),
                          "grade": {"letter": "B", "basis": "read from the cached Granola transcript"}})
        elif UNTIMED_TURN.match(ln.strip()):
            dropped["untimed turn"] += 1
    return atoms, dropped


def contexts(node, audience=None):
    """Yield (text, audience) for every string leaf; a table row is one context, cells joined."""
    if isinstance(node, dict):
        aud = node.get("audience", audience)
        for k, v in node.items():
            if not k.startswith("_") and k not in ("call", "verbs", "claims", "cells", "atlas", "migration"):
                yield from contexts(v, aud)
    elif isinstance(node, list):
        if node and all(isinstance(x, str) for x in node) and any(BRACKET.search(x) for x in node) and len(node) <= 8:
            yield " | ".join(node), audience
        else:
            for x in node:
                yield from contexts(x, audience)
    elif isinstance(node, str):
        yield node, audience


def from_ssot(doc: dict, names: dict) -> tuple[list[dict], dict]:
    seen: dict = {}
    dropped = {"no named speaker before the quote": 0}
    name_re = re.compile(r"\b(" + "|".join(map(re.escape, names)) + r")\b") if names else None
    for raw, aud in contexts(doc):
        text = TAGS.sub("", raw)
        hits = [(m.start(), m.group(1), m.group(2)) for m in QUOTE_THEN_T.finditer(text)]
        hits += [(m.start(), m.group(2), m.group(1)) for m in T_THEN_QUOTE.finditer(text)]
        for pos, quote, t in sorted(hits):
            before = [m.group(1) for m in name_re.finditer(text[:pos])] if name_re else []
            if not before:
                dropped["no named speaker before the quote"] += 1
                continue
            key = (t, quote.strip())
            spk = names[before[-1]]
            seen.setdefault(key, {"speakers": [], "aud": aud})["speakers"].append(spk)
    atoms = []
    for (t, quote), v in sorted(seen.items(), key=lambda kv: (secs(kv[0][0]), kv[0][1])):
        spk = max(sorted(set(v["speakers"])), key=v["speakers"].count)
        a = {"t": t, "speaker": spk, "kind": "utterance", "text": quote,
             "grade": {"letter": "C", "basis": "quoted beside a timestamp in the SSOT prose; speaker is the nearest "
                                                "person named before the quote; not read from the transcript",
                       "n": len(v["speakers"])}}
        if v["aud"] in ("internal", "both"):
            a["audience"] = v["aud"]
        atoms.append(a)
    return atoms, dropped


def children(parent: dict) -> list[dict]:
    out = []
    for m in NUMBER.finditer(parent["text"]):
        if not (m.group(1) or m.group(3)):
            continue
        a = {"t": parent["t"], "speaker": parent["speaker"], "kind": "number", "text": m.group(0).strip(),
             "value": float(m.group(2)), "unit": "USD" if m.group(1) else m.group(3)}
        out.append(a)
    for sent in re.split(r"(?<=[.?!])\s+", parent["text"]):
        if PROMISE.search(sent):
            out.append({"t": parent["t"], "speaker": parent["speaker"], "kind": "promise", "text": sent.strip(),
                        "owner": parent["speaker"]})
    for a in out:
        if "audience" in parent:
            a["audience"] = parent["audience"]
    return out


def akey(a: dict, parent_text: str = "") -> tuple:
    return (a["kind"], a["t"], a["speaker"], a["text"], parent_text)


def merge(old: list[dict], fresh: list[tuple[dict, list[dict]]]) -> list[dict]:
    """Old atoms keep their ids and place; fresh atoms not already present are appended in order."""
    by_id = {a["id"]: a for a in old}
    known = {akey(a, by_id.get(a.get("parent"), {}).get("text", "")): a["id"] for a in old}
    nxt = max([int(a["id"][1:]) for a in old] or [0]) + 1
    out = [dict(a) for a in old]
    for parent, kids in fresh:
        pk = akey(parent)
        if pk not in known:
            known[pk] = f"a{nxt:03d}"
            nxt += 1
            out.append({"id": known[pk], **parent})
        for k in kids:
            ck = akey(k, parent["text"])
            if ck not in known:
                known[ck] = f"a{nxt:03d}"
                nxt += 1
                out.append({"id": known[ck], **k, "parent": known[pk]})
    return out


def j1_reads(doc: dict) -> dict:
    return {k: v for k, v in doc.items() if k not in ("call", "verbs", "claims", "cells", "atlas")}


def j1_run(ctx, doc: dict) -> dict:
    names = people(doc)
    call = dict(doc.get("call") or {})
    source = dict(call.get("source") or {})
    gid = granola_id(doc)
    tpath = source.get("transcript") or find_transcript(ctx.root, gid)
    if tpath and os.path.isfile(os.path.join(ctx.root, tpath)):
        parents, dropped = from_transcript(open(os.path.join(ctx.root, tpath), encoding="utf-8").read(), names)
        origin = f"transcript {tpath}"
        source["transcript"] = tpath
    else:
        parents, dropped = from_ssot(doc, names)
        origin = "SSOT quotes beside timestamps (no cached transcript" + (f" carries Granola {gid})" if gid else ")")
    if gid:
        source["granola_id"] = gid
    atoms = merge(call.get("atoms") or [], [(p, children(p)) for p in parents])
    ctx.j1 = {"origin": origin, "dropped": dropped, "read": len(parents)}
    call["atoms"] = atoms
    if source:
        call["source"] = source
    return {"call": {k: call[k] for k in ("source", "atoms") if k in call}}


def j1_gate(ctx, doc: dict) -> Gate:
    atoms = (doc.get("call") or {}).get("atoms") or []
    info = getattr(ctx, "j1", {})
    lines = [f"J1 source: {info.get('origin', '?')}",
             "J1 atoms: %d (%s)" % (len(atoms), ", ".join("%s %d" % (k, sum(a["kind"] == k for a in atoms))
                                                        for k in ("utterance", "number", "promise")))]
    lines += [f"J1 dropped: {n} {why}" for why, n in (info.get("dropped") or {}).items() if n]
    bad = [a.get("id", "?") for a in atoms
           if not re.fullmatch(r"([0-9]+:)?[0-9]{1,2}:[0-9]{2}", a.get("t") or "")
           or not (a.get("speaker") or "").strip() or a.get("speaker", "").lower() in ("unknown", "?", "speaker")]
    ids = [a.get("id") for a in atoms]
    ok = bool(atoms) and not bad and len(ids) == len(set(ids))
    if not atoms:
        lines.append("J1 gate: no atom with a timestamp and a named speaker; cache the transcript with Granola "
                     f"get_meeting_transcript (include_timestamps) under {TRANSCRIPTS}/")
    if bad:
        lines.append(f"J1 gate: atoms missing a timestamp or speaker: {bad[:10]}")
    if len(ids) != len(set(ids)):
        lines.append("J1 gate: duplicate atom ids")
    if ok:
        lines.append("J1 gate: every atom has a timestamp and a speaker; ids unique")
    return Gate(ok, lines)


# --------------------------------------------------------------------------- the judgment door

def _anthropic(model_id: str, system: str, user: str) -> str:
    body = json.dumps({"model": model_id, "max_tokens": MAX_OUT, "system": system,
                       "messages": [{"role": "user", "content": user}]}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, headers={
        "x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01",
        "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        out = json.load(r)
    return "".join(b.get("text", "") for b in out.get("content", []))


CALLER = _anthropic  # the self-test swaps this for a fake; nothing else does


def judge(ctx, stage: str, system: str, user: str) -> dict:
    """One model call through ctx.act('paid_call'). Raises NotRun when it must not or cannot run."""
    import arcs_models
    model_id = arcs_models.model("deep")
    est = (len(system) + len(user)) / 4 / 1e6 * EST_IN + MAX_OUT / 1e6 * EST_OUT
    if ctx.dry_run:
        raise NotRun(f"dry run: the {stage} model call (role deep, {model_id}) was not made")
    if CALLER is _anthropic and not os.environ.get("ANTHROPIC_API_KEY"):
        raise NotRun(f"no ANTHROPIC_API_KEY: the {stage} model call (role deep) was not made")
    left = ctx.budget_usd - ctx.spent_usd
    if est > left:
        raise NotRun(f"{stage} needs about ${est:.2f} (ceiling estimate, role deep) and the run budget has "
                     f"${left:.2f}; rerun with --budget-usd on Zach's go")
    try:
        text = ctx.act("paid_call", f"{stage} role deep {model_id}", fn=lambda: CALLER(model_id, system, user),
                       cost_usd=est)
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        raise NotRun(f"{stage} model call failed: {e}")
    m = re.search(r"\{.*\}", text or "", re.S)
    try:
        return json.loads(m.group(0)) if m else {}
    except ValueError:
        return {}


def atom_packet(doc: dict) -> str:
    rows = [f"{a['id']} [{a['t']}] {a['speaker']} ({a['kind']}): {a['text']}"
            for a in (doc.get("call") or {}).get("atoms") or []]
    return "\n".join(rows)


def code_grade(doc: dict, cited: list[str], what: str) -> dict:
    atoms = {a["id"]: a for a in (doc.get("call") or {}).get("atoms") or []}
    letters = [(atoms[i].get("grade") or {}).get("letter", "C") for i in cited if i in atoms]
    n = len(set(cited))
    worst = max(letters or ["C"], key="ABCDE".index)
    letter = "D" if n < 2 else ("B" if worst <= "B" else "C")
    src = "transcript" if worst <= "B" else "SSOT prose"
    return {"letter": letter, "basis": f"{what} cites {n} atom(s) read from the {src}; grade set by code", "n": n}


def clean_cites(doc: dict, ids) -> list[str]:
    known = {a["id"] for a in (doc.get("call") or {}).get("atoms") or []}
    out = []
    for i in ids or []:
        if isinstance(i, str) and i in known and i not in out:
            out.append(i)
    return out


# --------------------------------------------------------------------------- J2 verbs

J2_SYSTEM = (
    "You read one recorded call as numbered atoms and write the five-verb read of it. "
    "analyze: what was actually said, taken apart. assess: how it moves the priors given. "
    "evaluate: judged against the ask and the next steps. synthesize: what it adds up to. "
    "recapitulate: the one line to carry into the next move. Use only facts in the atoms; "
    "if the atoms cannot support a verb, say so in its verdict. Every verdict cites at least one atom id. "
    "Plain words, no em-dashes. Reply with JSON only: "
    '{"analyze": {"verdict": "...", "body": ["..."], "cites": ["a001"]}, "assess": {...}, '
    '"evaluate": {...}, "synthesize": {...}, "recapitulate": {...}}')


def j2_reads(doc: dict) -> dict:
    return {k: v for k, v in doc.items() if k not in ("verbs", "claims", "cells", "atlas")}


def j2_user(doc: dict, extra: str = "") -> str:
    ctx_rows = {"opportunity": {k: (doc.get("opportunity") or {}).get(k) for k in ("y_state", "nci_prior", "nci_post", "note")},
                "beliefs": [{k: b.get(k) for k in ("id", "claim", "verdict")} for b in doc.get("beliefs") or []],
                "next_steps": [{k: s.get(k) for k in ("owner", "text")} for s in doc.get("next_steps") or []]}
    return ("ATOMS\n" + atom_packet(doc) + "\n\nCONTEXT (priors and asks, not evidence)\n"
            + json.dumps(ctx_rows, ensure_ascii=False) + (f"\n\nFIX THESE GATE FAILURES\n{extra}" if extra else ""))


def _verbs_from(doc: dict, raw: dict) -> dict:
    out = {}
    for v in VERBS:
        r = raw.get(v) if isinstance(raw.get(v), dict) else {}
        cites = clean_cites(doc, r.get("cites"))
        p = {"verdict": str(r.get("verdict") or "").strip(), "cites": cites,
             "grade": code_grade(doc, cites, f"the {v} verdict")}
        body = [str(x) for x in r.get("body") or [] if str(x).strip()]
        if body:
            p["body"] = body
        out[v] = p
    return out


def j2_run(ctx, doc: dict) -> dict:
    if not (doc.get("call") or {}).get("atoms"):
        raise NotRun("J2 has no atoms to cite (J1 did not pass)")
    return {"verbs": _verbs_from(doc, judge(ctx, "J2", J2_SYSTEM, j2_user(doc)))}


def j2_gate(ctx, doc: dict) -> Gate:
    verbs = doc.get("verbs") or {}
    lines, ok = [], True
    for v in VERBS:
        p = verbs.get(v) or {}
        if not p.get("verdict"):
            ok = False
            lines.append(f"J2 gate: {v} has no verdict")
        elif not p.get("cites"):
            ok = False
            lines.append(f"J2 gate: {v} verdict cites no known atom")
        elif EM in p["verdict"] + "".join(p.get("body") or []):
            ok = False
            lines.append(f"J2 gate: {v} has an em-dash")
        else:
            lines.append(f"J2 {v}: cites {', '.join(p['cites'])}; grade {p['grade']['letter']}")
    if ok:
        lines.append("J2 gate: every verdict cites at least one atom id")
    return Gate(ok, lines)


def j2_repair(ctx, doc: dict, failed: Gate) -> dict:
    return {"verbs": _verbs_from(doc, judge(ctx, "J2 repair", J2_SYSTEM, j2_user(doc, "\n".join(failed.lines))))}


# --------------------------------------------------------------------------- J3 deconstruct

J3_SYSTEM = (
    "You take claims apart. For each claim id you get the claim as said, its ruling and its evidence atoms. "
    "Write premise (what must already be true for the claim to hold) and mechanism (why the claim would "
    "follow from the evidence), one plain sentence each, using only the atoms given. Do not change rulings. "
    "No em-dashes. Reply with JSON only: {\"c001\": {\"premise\": \"...\", \"mechanism\": \"...\"}, ...}")


def j3_reads(doc: dict) -> dict:
    return {k: v for k, v in doc.items() if k not in ("verbs", "claims", "cells", "atlas")}


def forge_rows(doc: dict) -> list[list[str]]:
    rows = []
    for b in (doc.get("page") or {}).get("blocks") or []:
        cols = [str(c).lower() for c in b.get("columns") or []]
        if b.get("type") == "table" and "claim" in cols and "ruling" in cols:
            ci, ri = cols.index("claim"), cols.index("ruling")
            for r in b.get("rows") or []:
                if len(r) > max(ci, ri):
                    rows.append([TAGS.sub("", str(r[ci])), str(r[ri]),
                                 " | ".join(TAGS.sub("", str(x)) for i, x in enumerate(r) if i not in (ci, ri))])
    return rows


def skeletons(doc: dict) -> tuple[list[dict], list[str]]:
    atoms = (doc.get("call") or {}).get("atoms") or []
    utt = [a for a in atoms if a["kind"] == "utterance"]
    old = {c["said"]: c["id"] for c in doc.get("claims") or []}
    nxt = max([int(c["id"][1:]) for c in doc.get("claims") or []] or [0]) + 1
    out, notes = [], []
    for said, ruling_raw, force in forge_rows(doc):
        ts = BRACKET.findall(force)
        quoted = re.findall(r'"([^"]{3,400})"', force)
        ev = [a for a in utt if a["t"] in ts or a["text"] in quoted]
        if not ev:
            notes.append(f"J3 dropped: \"{said[:60]}\" ({ruling_raw}) cites no atom")
            continue
        ruling = ruling_raw.split()[0].upper() if ruling_raw.split() else ""
        note = force
        if ruling not in ("GROUNDED", "INFERENCE", "STRUCK"):
            notes.append(f"J3 dropped: \"{said[:60]}\" has ruling {ruling_raw!r} outside the Forge vocabulary")
            continue
        if ruling_raw.strip().upper() != ruling:
            note = f"{ruling_raw.strip()}; {force}"
        cid = old.get(said)
        if not cid:
            cid = f"c{nxt:03d}"
            nxt += 1
        out.append({"id": cid, "said": said, "ruling": ruling, "ruling_note": note,
                    "evidence": [{"atom": a["id"], "quote": a["text"]} for a in ev],
                    "cites": [a["id"] for a in ev], **({"audience": ev[0]["audience"]} if "audience" in ev[0] else {})})
    return out, notes


def _claims_from(doc: dict, sk: list[dict], raw: dict) -> list[dict]:
    out = []
    for s in sk:
        r = raw.get(s["id"]) if isinstance(raw.get(s["id"]), dict) else {}
        c = {"id": s["id"], "said": s["said"], "premise": str(r.get("premise") or "").strip(),
             "mechanism": str(r.get("mechanism") or "").strip(), "evidence": s["evidence"], "ruling": s["ruling"],
             "ruling_note": s["ruling_note"], "cites": s["cites"]}
        if "audience" in s:
            c["audience"] = s["audience"]
        g = code_grade(doc, s["cites"], f"a {s['ruling']} claim")
        if s["ruling"] != "GROUNDED":
            g = {"letter": "D" if s["ruling"] == "INFERENCE" else "E",
                 "basis": f"{s['ruling']} in the Forge: the evidence does not force it; grade set by code", "n": g["n"]}
        c["grade"] = g
        out.append(c)
    return out


def j3_user(sk: list[dict], extra: str = "") -> str:
    rows = [{"id": s["id"], "said": s["said"], "ruling": s["ruling"],
             "evidence": [f"{e['atom']}: {e['quote']}" for e in s["evidence"]]} for s in sk]
    return json.dumps(rows, ensure_ascii=False) + (f"\n\nFIX THESE GATE FAILURES\n{extra}" if extra else "")


def j3_run(ctx, doc: dict) -> dict:
    sk, notes = skeletons(doc)
    ctx.j3 = notes
    if not sk:
        raise NotRun("J3 found no Forge claim with an atom to cite", notes)
    lines = notes + [f"J3 skeleton {s['id']} {s['ruling']}: {s['said'][:70]} <- {', '.join(s['cites'])}" for s in sk]
    try:
        raw = judge(ctx, "J3", J3_SYSTEM, j3_user(sk))
    except NotRun as e:
        raise NotRun(str(e), lines)
    ctx.j3 = lines
    return {"claims": _claims_from(doc, sk, raw)}


def j3_gate(ctx, doc: dict) -> Gate:
    claims = doc.get("claims") or []
    atoms = {a["id"]: a["text"] for a in (doc.get("call") or {}).get("atoms") or []}
    lines, ok = list(getattr(ctx, "j3", [])), True
    for c in claims:
        if not c.get("premise") or not c.get("mechanism"):
            ok = False
            lines.append(f"J3 gate: {c['id']} has no premise or mechanism")
        if not c.get("cites"):
            ok = False
            lines.append(f"J3 gate: {c['id']} cites no atom")
        if c["ruling"] == "GROUNDED" and not any(e["quote"] in atoms.get(e["atom"], "") for e in c.get("evidence") or []):
            ok = False
            lines.append(f"J3 gate: GROUNDED {c['id']} quotes no atom verbatim")
        if EM in c.get("premise", "") + c.get("mechanism", ""):
            ok = False
            lines.append(f"J3 gate: {c['id']} has an em-dash")
    if ok:
        lines.append(f"J3 gate: {len(claims)} claims; every GROUNDED claim quotes an atom verbatim")
    return Gate(ok and bool(claims), lines)


def j3_repair(ctx, doc: dict, failed: Gate) -> dict:
    sk, _ = skeletons(doc)
    return {"claims": _claims_from(doc, sk, judge(ctx, "J3 repair", J3_SYSTEM, j3_user(sk, "\n".join(failed.lines))))}


# --------------------------------------------------------------------------- install into the runner

Gate = None  # bound by install()


def install(svc) -> None:
    global Gate
    Gate = svc.Gate
    row = "recoil-decompose-verbs (R7)"
    svc.register(svc.Stage("J1", ("call",), j1_run, j1_gate, version="1", print_name="decompose", builder=row, reads=j1_reads))
    svc.register(svc.Stage("J2", ("verbs",), j2_run, j2_gate, repair=j2_repair, version="1", print_name="verbs",
                           builder=row, reads=j2_reads))
    svc.register(svc.Stage("J3", ("claims",), j3_run, j3_gate, repair=j3_repair, version="1", print_name="deconstruct",
                           builder=row, reads=j3_reads))


# --------------------------------------------------------------------------- self-test (called by recoil_service --self-test)

def _fake(answers: list):
    """A stand-in model: returns the queued JSON answers in order and counts calls."""
    calls = {"n": 0}

    def f(model_id, system, user):
        calls["n"] += 1
        return json.dumps(answers[min(calls["n"], len(answers)) - 1])
    return f, calls


def self_test(svc, check, snap) -> None:
    global CALLER
    import shutil
    import tempfile
    real = CALLER
    try:
        with tempfile.TemporaryDirectory() as td:
            os.makedirs(os.path.join(td, svc.GENERATED))
            os.makedirs(os.path.join(td, TRANSCRIPTS))
            # J1 from SSOT prose: speaker from the nearest named participant; no name, no atom
            doc = {"schema": svc.v2.SCHEMA_ID, "meta": {"report_id": "2026-11-01-t", "date": "2026-11-01",
                   "counterpart": "Ada Lovelace"},
                   "beliefs": [{"id": "P1", "claim": "x", "inference": "OBS", "confidence": [0.5, 0.6],
                                "conviction": "MED", "verdict": "HOLDS",
                                "evidence": 'Ada said "we will hire 2 people by March" [3:10]'}],
                   "next_steps": [{"owner": "Zach", "text": 'check "nobody said this" [4:00]'}],
                   "page": {"header": {}, "blocks": [{"type": "table", "columns": ["Claim", "Ruling", "Source"],
                            "rows": [["Ada plans to hire", "GROUNDED", "[3:10] verbatim"],
                                     ["Nothing backs this", "GROUNDED", "[9:99] none"]]}]},
                   "call": {"atoms": []}}
            rel = os.path.join(svc.GENERATED, "2026-11-01-t.json")
            open(os.path.join(td, rel), "w").write(svc.dump(doc))
            rc, out = svc.run(rel, until="J1", root=td)
            d1 = json.load(open(os.path.join(td, rel)))
            atoms = d1["call"]["atoms"]
            utt = [a for a in atoms if a["kind"] == "utterance"]
            check(rc == 0 and len(utt) == 1 and utt[0]["speaker"] == "Ada Lovelace" and utt[0]["t"] == "3:10",
                  "J1: a quote beside a timestamp becomes an atom with the named speaker")
            check(any(a["kind"] == "number" and a["value"] == 2.0 and a["unit"] == "people" for a in atoms)
                  and any(a["kind"] == "promise" and a.get("parent") == utt[0]["id"] for a in atoms),
                  "J1: number and promise child atoms point at their utterance")
            pr = json.load(open(os.path.join(td, svc.RUNS, "2026-11-01-t", "prints", "J1.json")))
            check(any("dropped: 1 no named speaker" in ln for ln in pr["gate"]),
                  "J1: a quote with no named speaker before it is dropped and counted, not guessed")
            # stable ids: an edit that adds a quote appends; existing ids do not move
            doc["beliefs"][0]["evidence"] = 'Ada: "first new thing" [1:00]; ' + doc["beliefs"][0]["evidence"]
            d1["beliefs"] = doc["beliefs"]
            open(os.path.join(td, rel), "w").write(svc.dump(d1))
            svc.run(rel, until="J1", root=td)
            d2 = json.load(open(os.path.join(td, rel)))
            old = {a["id"]: a["text"] for a in atoms}
            new = {a["id"]: a["text"] for a in d2["call"]["atoms"]}
            check(all(new[k] == v for k, v in old.items()) and len(new) == len(old) + 1
                  and new[max(new)] == "first new thing", "J1: ids are stable; a rerun appends, never renumbers")

            # J2 and J3 offline: budget 0 means NOT RUN, nothing written into the SSOT
            CALLER, calls = _fake([{}])
            rc, out = svc.run(rel, root=td, until="J3")
            d3 = json.load(open(os.path.join(td, rel)))
            check(rc == 0 and calls["n"] == 0 and "verbs" not in d3 and "claims" not in d3
                  and any("J2 verbs: NOT RUN" in ln and "budget" in ln for ln in out),
                  "J2/J3: past the run budget the model is not called and the SSOT is unchanged")
            # J2 with a model: unknown cites are dropped; a verdict left with none fails, the repair fixes it
            ids = [a["id"] for a in d3["call"]["atoms"]]
            bad = {v: {"verdict": f"{v} read", "cites": ["a999"]} for v in VERBS}
            good = {v: {"verdict": f"{v} read", "cites": [ids[0], "a999"]} for v in VERBS}
            CALLER, calls = _fake([bad, good])
            rc, out = svc.run(rel, root=td, only="J2", budget_usd=1.0)
            d4 = json.load(open(os.path.join(td, rel)))
            check(rc == 0 and calls["n"] == 2 and all(d4["verbs"][v]["cites"] == [ids[0]] for v in VERBS)
                  and any("PASS after 1 molt" in ln for ln in out),
                  "J2: unknown atom ids are dropped; a verdict with no cite fails and the repair passes")
            check(d4["verbs"]["analyze"]["grade"]["letter"] == "D", "J2: grade is set by code (one cite = D)")
            # J3: the Forge row with an atom is GROUNDED and quotes it; the row with no atom is dropped
            ucid = [a for a in d4["call"]["atoms"] if a["t"] == "3:10" and a["kind"] == "utterance"][0]
            CALLER, calls = _fake([{"c001": {"premise": "Ada can hire", "mechanism": "she said the number"}}])
            rc, out = svc.run(rel, root=td, only="J3", budget_usd=1.0)
            d5 = json.load(open(os.path.join(td, rel)))
            cl = d5.get("claims") or []
            check(rc == 0 and len(cl) == 1 and cl[0]["ruling"] == "GROUNDED"
                  and cl[0]["evidence"][0] == {"atom": ucid["id"], "quote": ucid["text"]},
                  "J3: a GROUNDED Forge claim quotes its atom verbatim; premise and mechanism from the model")
            pr = json.load(open(os.path.join(td, svc.RUNS, "2026-11-01-t", "prints", "J3.json")))
            check(any("Nothing backs this" in ln and "cites no atom" in ln for ln in pr["gate"]),
                  "J3: a Forge claim with no atom is dropped and listed in the print")
            CALLER, calls = _fake([{"c001": {"premise": "", "mechanism": "x"}}])
            STATE = os.path.join(td, svc.RUNS, "2026-11-01-t", "state.json")
            st = json.load(open(STATE)); st.pop("J3"); open(STATE, "w").write(svc.dump(st))
            rc, out = svc.run(rel, root=td, only="J3", budget_usd=1.0)
            check(rc == 2 and calls["n"] == 4 and any("no premise or mechanism" in ln for ln in out),
                  "J3: an empty premise fails the gate; three repairs, then the verbatim gate")

            # a new Granola id with a cached transcript: J1 scaffolds the SSOT and reads timed turns
            gid = "0123abcd-0000-4000-8000-00000000beef"
            open(os.path.join(td, TRANSCRIPTS, "t.txt"), "w").write(
                f"[Granola {gid} . \"Ada x Zach\" . Nov 3 2026 2:00 PM]\n\n[0:05] Me: Hi Ada.\n"
                "[0:09] Ada Lovelace: We grew 40% last quarter. I'll send the deck.\nUntimed: dropped line\n")
            rc, out = svc.run(gid, until="J1", root=td)
            new_rel = os.path.join(svc.GENERATED, "2026-11-03-granola-0123abcd.json")
            ok = os.path.exists(os.path.join(td, new_rel))
            d6 = json.load(open(os.path.join(td, new_rel))) if ok else {}
            at = (d6.get("call") or {}).get("atoms") or []
            check(rc == 0 and ok and [a["speaker"] for a in at if a["kind"] == "utterance"] == ["Zach", "Ada Lovelace"]
                  and any(a["kind"] == "number" and a["unit"] == "%" for a in at),
                  "J1: a Granola id with a cached transcript scaffolds a v2 SSOT of timed turns")
            rc, out = svc.run(gid, until="J1", root=td)
            check(any("J1 decompose: UNCHANGED" in ln for ln in out), "J1: the same id resolves to its SSOT on rerun")

            # Gasmi, for real (not dry): a rerun with no new input changes nothing, model calls included
            g_rel = os.path.join(svc.GENERATED, "2026-10-29-gasmi.json")
            shutil.copy(os.path.join(svc.ROOT, g_rel), os.path.join(td, g_rel))
            rc, out = svc.run(g_rel, until="J3", root=td)
            s1 = snap(td)
            rc2, out2 = svc.run(g_rel, until="J3", root=td)
            check(rc == rc2 == 0 and snap(td) == s1, "Gasmi offline: a rerun with no new input changes nothing")
            g = json.load(open(os.path.join(td, svc.RUNS, "2026-10-29-gasmi", "ssot.v2.json")))
            gids = [a["id"] for a in g["call"]["atoms"]]
            CALLER, calls = _fake([{v: {"verdict": f"{v} read", "cites": gids[:2]} for v in VERBS},
                                   {c["id"]: {"premise": "p", "mechanism": "m"} for c in skeletons(g)[0]}])
            rc, out = svc.run(g_rel, until="J3", root=td, budget_usd=1.0)
            s2 = snap(td)
            n_calls = calls["n"]
            rc2, out2 = svc.run(g_rel, until="J3", root=td, budget_usd=1.0)
            check(rc == rc2 == 0 and n_calls == 2 and calls["n"] == 2 and snap(td) == s2
                  and sum("UNCHANGED" in ln for ln in out2) == 3,
                  "Gasmi with a model: J1 to J3 PASS, then a rerun is UNCHANGED with no new model call")
            check(open(os.path.join(td, g_rel), "rb").read() == open(os.path.join(svc.ROOT, g_rel), "rb").read(),
                  "Gasmi v1 source file is never rewritten")
    finally:
        CALLER = real
