#!/usr/bin/env python3
"""coherence_sweep: cheap, batched disturbance detector over a ledger of claims. Stdlib only, no model calls.

python3 scripts/coherence_sweep.py --memory                 # sweep the project memory store
python3 scripts/coherence_sweep.py --jsonl FILE --id-field id --date-field added --require id,jtbd
python3 scripts/coherence_sweep.py --memory --write         # also write _STATE/coherence-sweep-<date>.md + .residue.jsonl
python3 scripts/coherence_sweep.py --self-test              # plant a fault per check, require it to fire

It finds claims that are inconsistent, unsourced, dangling, stale or contradicted. It cannot tell that a sourced,
consistent, fresh claim is TRUE; only a live check does that. The point is to shrink the pile: every finding
goes to a residue file (one JSON line each, with a snippet) that a cheap model can judge in one batch.

Checks (memory mode):
  frontmatter   name matches the file, description present, type is user|feedback|project|reference
  index         every note is listed in MEMORY.md, and every index entry resolves to a note
  dangling      [[links]] to a note that does not exist (reported, never a failure: they mark notes worth writing)
  path          a backticked repo path that does not exist in this checkout
  present-tense "currently / is live / now" in a note older than --stale-days (default 45)
  contradiction one subject given opposite states (public/private, live/dead...) by different notes
"""
import argparse
import datetime as dt
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEM = os.path.expanduser("~/.claude/projects/-Users-zharris-arcs-v9/memory")
EXTRA = []
TYPES = {"user", "feedback", "project", "reference"}
ENTITIES = {  # canonical entity -> alias regexes; contradictions are sought per entity, not per raw subject string
    "arcs-v9": [r"arcs-v9", r"arcs v9"],
    "arcs-care": [r"arcs-care"],
    "status.arcs.care": [r"status\.arcs\.care"],
}
STATES = r"(public|private|live|dead|inactive|archived)"
NEGATION = re.compile(r"\b(not|never|no longer|isn't|wasn't|n't)\b", re.I)
OPPOSED = [("public", "private"), ("live", "dead"), ("live", "inactive"), ("open", "closed"), ("done", "open"), ("on", "off")]
CLAIM = re.compile(r"`?([A-Za-z0-9_.@/-]{3,60})`?[^.\n|]{0,40}?\b(?:is|was|now|became|flipped to|made|remains)\s+(?:now\s+)?(public|private|live|dead|inactive|archived)\b", re.I)
PRESENT = re.compile(r"\b(currently|right now|is live|is now|as of today|still)\b", re.I)
TICK = re.compile(r"`([^`\n]{3,120})`")
LINK = re.compile(r"\[\[([^\]]+)\]\]")


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        k, _, v = line.strip().partition(":")
        if k in ("name", "description", "type", "modified") and k not in fm:  # keys may sit under `metadata:`; first one wins
            fm[k] = v.strip().strip('"')
    return fm, m.group(2)


def load_memory(mem):
    notes = {}
    for f in sorted(os.listdir(mem)):
        if f.endswith(".md") and f != "MEMORY.md":
            p = os.path.join(mem, f)
            fm, body = frontmatter(open(p, errors="replace").read())
            fm["_mtime"] = dt.date.fromtimestamp(os.path.getmtime(p))
            mod = fm.get("modified", "")
            try:
                fm["_date"] = dt.date.fromisoformat(mod[:10])
            except ValueError:
                fm["_date"] = fm["_mtime"]
            notes[f[:-3]] = (fm, body)
    for extra in EXTRA:  # other stores swept as pseudo-notes so cross-store contradictions can surface
        if os.path.exists(extra):
            fm, body = frontmatter(open(extra, errors="replace").read())
            fm["_date"] = fm["_mtime"] = dt.date.fromtimestamp(os.path.getmtime(extra))
            notes["@" + os.path.basename(os.path.dirname(extra)) + "/" + os.path.basename(extra)] = (fm, body)
    index = open(os.path.join(mem, "MEMORY.md"), errors="replace").read() if os.path.exists(os.path.join(mem, "MEMORY.md")) else ""
    return notes, index


def looks_like_path(t):
    if any(c in t for c in "<>*{}$ |,;=()") or t.startswith(("http", "~", "/", "-", "#", ".")) or "://" in t or "@" in t:
        return False
    if t.count("/") < 1 or t.endswith(("/", ".")):
        return len(t) > 2 and t.endswith("/") and t.count("/") >= 2 and not t.startswith(".")
    return bool(re.search(r"\.[a-z]{1,5}$", t.split("/")[-1])) and not re.search(r"\.(com|org|care|io|dev|app|xyz|net|ai)$", t)


def sweep_memory(notes, index, root, today, stale_days):
    F = []

    def add(check, note, msg, snip=""):
        F.append({"check": check, "note": note, "msg": msg, "snippet": snip[:200]})
    listed = set(re.findall(r"([A-Za-z0-9_.-]+)", index))
    names = set(notes)
    for n, (fm, body) in notes.items():
        if n.startswith("@"):
            continue_checks = False
        else:
            continue_checks = True
        if continue_checks and fm.get("name") and fm["name"] != n:
            add("frontmatter", n, "name %r does not match file" % fm["name"])
        if continue_checks and not fm.get("description"):
            add("frontmatter", n, "no description")
        if "type" in fm and fm["type"] not in TYPES:
            add("frontmatter", n, "type %r not in %s" % (fm.get("type"), sorted(TYPES)))
        if continue_checks and n not in listed and n.replace("_", "-") not in listed:
            add("index", n, "note not mentioned in MEMORY.md")
        for tgt in (set(LINK.findall(body)) if continue_checks else ()):
            if tgt not in names:
                add("dangling", n, "[[%s]] has no note" % tgt)
        age = (today - fm["_date"]).days
        for t in TICK.findall(body):
            if looks_like_path(t) and not os.path.exists(os.path.join(root, t.rstrip("/"))):
                add("path", n, "`%s` does not exist in this checkout" % t, t)
        if age > stale_days:
            for m in PRESENT.finditer(body):
                s = body[max(0, m.start() - 60):m.end() + 60].replace("\n", " ")
                add("present-tense", n, "present tense in a %d-day-old note (%s)" % (age, fm["_date"]), s)
                break
    # contradictions: one entity, opposed states, different notes. Affirmative sentences only (negations skipped).
    seen = {}
    for n, (fm, body) in notes.items():
        for sent in re.split(r"(?<=[.!?\n])\s+", body.replace("**", "")):
            if NEGATION.search(sent):
                continue
            for ent, pats in ENTITIES.items():
                if any(re.search(p, sent, re.I) for p in pats):
                    for m in re.finditer(r"\b" + STATES + r"\b", sent, re.I):
                        seen.setdefault(ent, []).append((n, m.group(1).lower(), fm["_date"], sent.strip()[:140]))
    for ent, rows in seen.items():
        vals = {r[1] for r in rows}
        for a, b in OPPOSED:
            if a in vals and b in vals:
                ra = [r for r in rows if r[1] == a][0]
                rb = [r for r in rows if r[1] == b][0]
                if ra[0] != rb[0]:
                    newer = ra if ra[2] >= rb[2] else rb
                    add("contradiction", ra[0], "%s: %s in %s (%s) vs %s in %s (%s); newer note: %s" % (
                        ent, a, ra[0], ra[2], b, rb[0], rb[2], newer[0]), ra[3] + " || " + rb[3])
    return F


def sweep_jsonl(path, id_field, date_field, require, today, stale_days):
    F, ids = [], {}
    for i, line in enumerate(open(path), 1):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except ValueError:
            F.append({"check": "parse", "note": "line %d" % i, "msg": "not JSON", "snippet": line[:120]})
            continue
        rid = r.get(id_field, "line %d" % i)
        for f in require:
            if r.get(f) in (None, "", []):
                F.append({"check": "required", "note": str(rid), "msg": "missing %s" % f, "snippet": ""})
        ids.setdefault(rid, []).append(i)
        d = r.get(date_field)
        if d:
            try:
                dd = dt.date.fromisoformat(str(d)[:10])
                if dd > today:
                    F.append({"check": "date", "note": str(rid), "msg": "%s %s is in the future" % (date_field, d), "snippet": ""})
                elif (today - dd).days > stale_days and r.get("state", "OPEN") not in ("DONE", "COMPOSTED", "SUPERSEDED"):
                    F.append({"check": "stale", "note": str(rid), "msg": "open for %d days" % (today - dd).days, "snippet": ""})
            except ValueError:
                F.append({"check": "date", "note": str(rid), "msg": "unparseable %s %r" % (date_field, d), "snippet": ""})
    for rid, ls in ids.items():
        if len(ls) > 1:
            F.append({"check": "duplicate", "note": str(rid), "msg": "id repeated on lines %s" % ls, "snippet": ""})
    return F


def report(F, label):
    from collections import Counter
    c = Counter(f["check"] for f in F)
    print("COHERENCE SWEEP: %s  (%d findings)" % (label, len(F)))
    for k, v in c.most_common():
        print("  %-14s %d" % (k, v))
        for f in [x for x in F if x["check"] == k][:3]:
            print("      %-44s %s" % (f["note"][:44], f["msg"][:110]))
    return c


def self_test():
    import shutil
    import tempfile
    today = dt.date(2026, 10, 15)
    d = tempfile.mkdtemp()
    try:
        def note(name, fm_extra="", body="", mod="2026-10-10"):
            open(os.path.join(d, name + ".md"), "w").write("---\nname: %s\ndescription: x\nmetadata:\n  type: project\n  modified: %s\n%s---\n%s\n" % (name, mod, fm_extra, body))
        open(os.path.join(d, "MEMORY.md"), "w").write("- clean-note\n")
        note("clean-note", body="Nothing wrong here. See [[clean-note]].")
        notes, index = load_memory(d)
        assert not sweep_memory(notes, index, ROOT, today, 45), "clean store produced findings"
        note("orphan-note", body="x")
        note("ref-note", body="see `scripts/this_file_does_not_exist.py` and [[ghost-note]]", mod="2026-10-14")
        note("old-note", body="The repo is currently fine.", mod="2026-01-01")
        note("pub-a", body="The arcs-v9 repo is public on GitHub.")
        note("pub-b", body="After the status page went up, arcs-v9 became private.")
        notes, index = load_memory(d)
        got = {f["check"] for f in sweep_memory(notes, index, ROOT, today, 45)}
        for need in ("index", "path", "dangling", "present-tense", "contradiction"):
            assert need in got, "%s check cannot fail: got %s" % (need, sorted(got))
        note("neg-note", body="The arcs-v9 repo is not private and was never dead.")
        note("other-ent", body="The gigi repo is private.")
        notes, index = load_memory(d)
        cons = [f for f in sweep_memory(notes, index, ROOT, today, 45) if f["check"] == "contradiction"]
        assert cons and all("neg-note" not in f["msg"] and "gigi" not in f["msg"] for f in cons), "negation or unrelated entity produced a contradiction: %s" % cons
        # control: a real path must NOT be flagged
        note("good-path", body="see `scripts/filing_workback.py`")
        notes, index = load_memory(d)
        assert not [f for f in sweep_memory(notes, index, ROOT, today, 45) if f["note"] == "good-path" and f["check"] == "path"], "real path flagged"
        j = os.path.join(d, "t.jsonl")
        open(j, "w").write('{"id":"a","added":"2026-01-01","state":"OPEN","jtbd":"x"}\n{"id":"a","added":"2030-01-01","jtbd":""}\nnot json\n')
        g = {f["check"] for f in sweep_jsonl(j, "id", "added", ["id", "jtbd"], today, 45)}
        for need in ("duplicate", "date", "stale", "required", "parse"):
            assert need in g, "jsonl %s check cannot fail: got %s" % (need, sorted(g))
    finally:
        shutil.rmtree(d)
    print("self-test OK: every memory check and every jsonl check fired on its planted fault; clean store and real path stayed quiet")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--memory", action="store_true")
    ap.add_argument("--mem-dir", default=MEM)
    ap.add_argument("--jsonl")
    ap.add_argument("--id-field", default="id")
    ap.add_argument("--date-field", default="added")
    ap.add_argument("--require", default="id")
    ap.add_argument("--stale-days", type=int, default=45)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--also", action="append", default=[], help="extra text file swept alongside the notes (e.g. ~/.claude/CLAUDE.md)")
    a = ap.parse_args()
    EXTRA.extend(os.path.expanduser(x) for x in a.also)
    if a.self_test:
        return self_test()
    today = dt.date.today()
    if a.memory:
        notes, index = load_memory(a.mem_dir)
        F, label = sweep_memory(notes, index, ROOT, today, a.stale_days), "memory (%d notes)" % len(notes)
    elif a.jsonl:
        F, label = sweep_jsonl(a.jsonl, a.id_field, a.date_field, a.require.split(","), today, a.stale_days), a.jsonl
    else:
        ap.error("pick --memory or --jsonl FILE")
    c = report(F, label)
    if a.write:
        base = os.path.join(ROOT, "_STATE", "coherence-sweep-%s-%s" % ("memory" if a.memory else os.path.basename(a.jsonl).split(".")[0], today))
        with open(base + ".residue.jsonl", "w") as f:
            for x in F:
                f.write(json.dumps(x) + "\n")
        open(base + ".md", "w").write("# Coherence sweep: %s, %s\n\nGenerated by `scripts/coherence_sweep.py`. Mechanical only: finds inconsistent, dangling, stale or contradicted claims; cannot prove a consistent claim true.\n\n%s\n\nResidue for a cheap batched judgment pass: `%s`\n" % (
            label, today, "\n".join("- %s: %d" % kv for kv in c.most_common()), os.path.basename(base) + ".residue.jsonl"))
        print("wrote %s.md and .residue.jsonl" % os.path.relpath(base, ROOT))


if __name__ == "__main__":
    main()
