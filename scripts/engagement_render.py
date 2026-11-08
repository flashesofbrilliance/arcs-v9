#!/usr/bin/env python3
"""engagement_render.py: one engagement record -> reply, agreement, Exhibit A, five-altitude page.

One record per client engagement (_ARTIFACTS/engagements/<slug>/engagement.json, schema in
runtime/specs/engagement-record-v0.md). Templates in <slug>/templates/*.md.tpl cite record values
as {{field_id}} or {{field_id|fmt}}; every output lands in <slug>/out/ with render.lock.json.

Idempotent: the same record and templates always give the same bytes (no clock, sorted keys).
Self-updating: render.lock.json stores each output's hash and the value of every field it cites.
--check re-renders in memory and fails when an output on disk is stale, naming the field that
moved, its old and new value, and every output that cites it. A stale field is flagged, never kept.

  python3 scripts/engagement_render.py                 # render every engagement
  python3 scripts/engagement_render.py --dir <slug-dir> # render one
  python3 scripts/engagement_render.py --check         # read-only; exit 1 on stale or invalid
  python3 scripts/engagement_render.py --self-test

Stdlib only. Nothing here sends, publishes or writes outside the engagement folder.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import hashlib
import html
import json
import os
import re
import shutil
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENG_GLOB = os.path.join(ROOT, "_ARTIFACTS", "engagements", "*", "engagement.json")
TOKENS = os.path.join(ROOT, "src", "ui-kit", "recoil-report", "_tokens.css")
SCHEMA = "engagement-record-v0"
SOURCE_KINDS = {"sent", "email", "doc", "decision", "judgment", "call"}
KINDS = {"money", "int", "days", "hours", "date", "text"}
OPS = {"mul", "div", "add_days"}
ALTITUDES = ["exec", "strategic", "operational", "tactical", "surgical"]
CITE = re.compile(r"\{\{([^{}]+)\}\}")
WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
LOCK = "render.lock.json"


class RecordError(Exception):
    pass


# ---------------------------------------------------------------- validate + resolve

def validate(rec: dict) -> list[str]:
    errs = []
    if rec.get("schema") != SCHEMA:
        errs.append(f"schema must be {SCHEMA!r}")
    for key in ("meta", "client", "fields", "terms", "lists", "assumptions", "altitudes", "cold_read"):
        if key not in rec:
            errs.append(f"missing top-level key {key!r}")
    for fid, f in rec.get("fields", {}).items():
        if f.get("kind") not in KINDS:
            errs.append(f"field {fid}: kind must be one of {sorted(KINDS)}")
        if "derive" in f:
            if "value" in f or "source" in f:
                errs.append(f"field {fid}: a derived field has no value or source of its own")
            continue
        if "value" not in f:
            errs.append(f"field {fid}: no value and no derive")
        errs += _check_source(f"field {fid}", f.get("source"))
        if not isinstance(f.get("history"), list):
            errs.append(f"field {fid}: history must be a list (append-only, may be empty)")
        for i, h in enumerate(f.get("history", [])):
            if "value" not in h or not _is_date(h.get("until")):
                errs.append(f"field {fid}: history[{i}] needs value and until (YYYY-MM-DD)")
            errs += _check_source(f"field {fid} history[{i}]", h.get("source"))
    for a in rec.get("assumptions", []):
        if not a.get("test_that_would_decide"):
            errs.append(f"assumption {a.get('id')}: no test_that_would_decide (an assumption with no test is a belief)")
        errs += _check_source(f"assumption {a.get('id')}", a.get("source"))
    for alt in ALTITUDES:
        if alt not in rec.get("altitudes", {}):
            errs.append(f"altitudes: missing {alt}")
    blob = json.dumps(rec, ensure_ascii=False)
    if "—" in blob:
        errs.append("em-dash in the record (client copy rule: none)")
    return errs


def _is_date(s) -> bool:
    try:
        dt.date.fromisoformat(s)
        return True
    except (TypeError, ValueError):
        return False


def _check_source(where, src) -> list[str]:
    if not isinstance(src, dict):
        return [f"{where}: no source"]
    out = []
    if src.get("kind") not in SOURCE_KINDS:
        out.append(f"{where}: source.kind must be one of {sorted(SOURCE_KINDS)}")
    if not src.get("ref"):
        out.append(f"{where}: source.ref is empty")
    if not _is_date(src.get("date")):
        out.append(f"{where}: source.date must be YYYY-MM-DD")
    return out


def resolve(rec: dict) -> dict:
    """field id -> {value, inputs}; inputs is the set of stored fields a value depends on."""
    fields = rec["fields"]
    done: dict = {}

    def arg(a, stack):
        if isinstance(a, list):
            return op(a, stack)
        if isinstance(a, (int, float)):
            return a, set()
        if a in fields:
            r = get(a, stack)
            return r["value"], r["inputs"]
        raise RecordError(f"derive cites unknown field {a!r}")

    def op(expr, stack):
        name, *args = expr
        if name not in OPS:
            raise RecordError(f"unknown derive op {name!r}")
        vals, ins = zip(*(arg(a, stack) for a in args))
        inputs = set().union(*ins)
        if name == "mul":
            v = vals[0]
            for x in vals[1:]:
                v *= x
        elif name == "div":
            v = vals[0] / vals[1]
            v = int(v) if float(v).is_integer() else v
        else:
            v = (dt.date.fromisoformat(vals[0]) + dt.timedelta(days=vals[1])).isoformat()
        return v, inputs

    def get(fid, stack=()):
        if fid in done:
            return done[fid]
        if fid in stack:
            raise RecordError(f"derive cycle through {fid!r}")
        f = fields[fid]
        if "derive" in f:
            v, inputs = op(f["derive"], stack + (fid,))
        else:
            v, inputs = f["value"], {fid}
        done[fid] = {"value": v, "inputs": inputs}
        return done[fid]

    for fid in fields:
        get(fid)
    return done


# ---------------------------------------------------------------- formatting

def fmt(kind: str, value, style: str = "") -> str:
    if kind == "money":
        return f"${value:,.0f}"
    if kind == "date":
        d = dt.date.fromisoformat(value)
        if style == "nda":
            return f"{d.month}.{d.day}.{d.year % 100}"
        base = f"{MONTHS[d.month - 1]} {d.day}"
        if style == "day":
            return f"{DAYS[d.weekday()]} {base}"
        return f"{base}, {d.year}" if style == "long" else base
    if kind == "days" and style == "weeks":
        if value % 7 == 0 and value // 7 < len(WORDS):
            w = value // 7
            return f"{WORDS[w]} week{'s' if w != 1 else ''}"
        return f"{value} days"
    if style in ("word", "Word") and isinstance(value, int) and 0 <= value < len(WORDS):
        w = WORDS[value]
        return w.capitalize() if style == "Word" else w
    return str(value)


class Ctx:
    """Renders text against one record and records every field it cites."""

    def __init__(self, rec, resolved):
        self.rec, self.res = rec, resolved
        self.cites: set[str] = set()

    def sub(self, text: str) -> str:
        return CITE.sub(lambda m: self._one(m.group(1).strip()), text)

    def _one(self, token: str) -> str:
        name, _, style = token.partition("|")
        if name.startswith("client."):
            key = name[len("client."):]
            if key not in self.rec["client"]:
                raise RecordError(f"unknown cite {{{{{token}}}}}")
            return str(self.rec["client"][key])
        if name.startswith("list:"):
            key = name[len("list:"):]
            if key not in self.rec["lists"]:
                raise RecordError(f"unknown list {{{{{token}}}}}")
            return "\n".join("- " + self.sub(i["text"]) for i in self.rec["lists"][key])
        if name == "terms":
            return "\n\n".join(f"{n}. **{t['title']}.** {self.sub(t['body'])}" for n, t in enumerate(self.rec["terms"], 1))
        if name not in self.res:
            raise RecordError(f"unknown cite {{{{{token}}}}}")
        self.cites.add(name)
        return fmt(self.rec["fields"][name]["kind"], self.res[name]["value"], style)


# ---------------------------------------------------------------- change seams

def changes_since_sent(rec, resolved, cites) -> list[dict]:
    """Stored fields (cited directly or through a derive) whose history moved after meta.last_sent."""
    sent = rec["meta"].get("last_sent")
    if not sent:
        return []
    stored = set().union(*(resolved[c]["inputs"] for c in cites)) if cites else set()
    out = []
    for fid in sorted(stored):
        f = rec["fields"][fid]
        for h in f["history"]:
            if h["until"] > sent:
                out.append({"field": fid, "was": fmt(f["kind"], h["value"]), "now": fmt(f["kind"], f["value"]),
                            "changed": h["until"], "source": f["source"]["ref"]})
    return out


def seam_block(changes) -> str:
    if not changes:
        return ""
    lines = ["CHANGED SINCE LAST SENT (review before sending):"]
    lines += [f"- {c['field']}: was {c['was']}, now {c['now']} (changed {c['changed']}; {c['source']})" for c in changes]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- outputs

def cites_digest(rec, resolved, cites) -> dict:
    return {c: resolved[c]["value"] for c in sorted(cites)}


def render_md(rec, resolved, tpl_text, name) -> tuple[str, set]:
    ctx = Ctx(rec, resolved)
    body = ctx.sub(tpl_text).rstrip() + "\n"
    head = (f"<!-- {rec['meta']['internal_note']} -->\n"
            f"<!-- Rendered by scripts/engagement_render.py from engagement.json ({rec['meta']['id']}) + templates/{name}.md.tpl. "
            f"Do not hand-edit: change the record and re-render. -->\n")
    seams = seam_block(changes_since_sent(rec, resolved, ctx.cites))
    if seams:
        head += "<!--\n" + seams + "-->\n"
    return head + "\n" + body, ctx.cites


def _e(s) -> str:
    return html.escape(str(s), quote=True)


CSS = """
* { box-sizing: border-box; }
body { --sans: var(--ds-font-sans); --mono: var(--ds-font-mono);
  background: var(--bg); color: var(--text); font-family: var(--sans); font-size: var(--fs-body); line-height: 1.6; margin: 0; padding: 28px 16px; }
main { --measure: 860px; max-width: var(--measure); margin: 0 auto; display: flex; flex-direction: column; gap: 22px; }
h1 { font-family: var(--sans); font-size: var(--fs-display); font-weight: 600; line-height: 1.2; margin: 0; text-wrap: balance; }
.lede { max-width: none; margin: 0; }
.note { color: var(--muted); margin: 0; }
h2.label { font-family: var(--mono); font-size: var(--fs-label); font-weight: 700; letter-spacing: .02em; color: var(--muted); margin: 0 0 6px; line-height: 1.4; }
.panel { background: var(--surface); border: 1px solid var(--border); border-radius: var(--ds-r-sm); padding: 20px 22px; }
.panel p { margin: 0 0 8px; }
.beats { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
.beat { background: var(--elevated); border: 1px solid var(--border); border-radius: var(--ds-r-sm); padding: 12px; min-width: 0; }
.beat b { display: block; font-family: var(--mono); font-size: var(--fs-body); letter-spacing: .02em; color: var(--cyan); margin-bottom: 4px; }
details { background: var(--surface); border: 1px solid var(--border); border-radius: var(--ds-r-sm); padding: 14px 18px; }
summary { cursor: pointer; font-weight: 600; }
summary span { font-family: var(--mono); font-size: var(--fs-body); color: var(--muted); letter-spacing: .02em; margin-right: 10px; }
.tw { overflow-x: auto; margin-top: 10px; }
table { border-collapse: collapse; width: 100%; font-size: var(--fs-body); }
th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--border); vertical-align: top; overflow-wrap: anywhere; }
th { font-family: var(--mono); font-size: var(--fs-body); letter-spacing: .02em; color: var(--muted); font-weight: 700; }
code { font-family: var(--mono); }
.seam { color: var(--gold); font-family: var(--mono); font-size: var(--fs-body); }
.callout { border: 1px solid var(--gold); background: var(--elevated); padding: 12px 16px; border-radius: var(--ds-r-sm); margin: 0; }
"""


def render_html(rec, resolved) -> tuple[str, set]:
    ctx = Ctx(rec, resolved)
    s = ctx.sub
    cr = rec["cold_read"]
    a = []
    a.append(f"<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
             f"<title>{_e(rec['meta']['title'])}</title><style>\n{open(TOKENS, encoding='utf-8').read()}\n{CSS}</style></head><body><main>")
    a.append(f"<h1>{_e(rec['meta']['title'])}</h1>")
    a.append(f"<p class=\"note\">Internal draft. Not for the client. Rendered from engagement.json ({_e(rec['meta']['id'])}).</p>")
    a.append(f"<p class=\"lede\">{_e(s(rec['altitudes']['exec']))}</p>")
    a.append("<section class=\"panel\">")
    for key, lab in (("why", "Why"), ("what", "What"), ("why_now", "Why now")):
        a.append(f"<h2 class=\"label\">{lab}</h2><p>{_e(s(cr[key]))}</p>")
    a.append("<h2 class=\"label\">How</h2><div class=\"beats\">")
    for key, lab in (("before", "Before"), ("during", "During"), ("after", "After")):
        a.append(f"<div class=\"beat\"><b>{lab}</b>{_e(s(cr[key]))}</div>")
    a.append("</div></section>")
    a.append("<p class=\"callout\">How to read this: five levels, Exec to Surgical. Each opens one level deeper; Surgical lists every value with its source.</p>")

    def table(head, rows):
        t = "<div class=\"tw\"><table><thead><tr>" + "".join(f"<th>{_e(h)}</th>" for h in head) + "</tr></thead><tbody>"
        t += "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
        return t + "</tbody></table></div>"

    def level(n, alt, title, inner, open_=False):
        a.append(f"<details{' open' if open_ else ''}><summary><span>{n} {alt}</span>{_e(title)}</summary>"
                 f"<p>{_e(s(rec['altitudes'][alt.lower()]))}</p>{inner}</details>")

    level(1, "Exec", "The headline", "", open_=True)
    level(2, "Strategic", "Best, base, worst", table(
        ["Case", "What happens", "I earn", "Signal to watch", "Guard"],
        [[_e(x["id"]), _e(s(x["what"])), _e(s(x["earn"])), _e(x["watch"]), _e(x["guard"])] for x in rec["scenarios"]]))
    level(3, "Operational", "Steps and timing", table(
        ["Step", "Question", "Fee", "Status"],
        [[_e(p["name"]), _e(p["question"]), _e(s(p["fee"])), _e(p["status"])] for p in rec["phases"]]))
    level(4, "Tactical", "Chelsea's asks, each with its answer", table(
        ["Ask", "From", "What they asked", "Answered by"],
        [[_e(x["short"]), _e(x["source"]["ref"]), _e(x["text"]), _e(", ".join(x["answered_by"]))] for x in rec["asks"]]))
    changes = {c["field"]: c for c in changes_since_sent(rec, resolved, set(rec["fields"]))}
    rows = []
    for fid in sorted(rec["fields"]):
        f = rec["fields"][fid]
        ctx.cites.add(fid)
        val = _e(fmt(f["kind"], resolved[fid]["value"], "long" if f["kind"] == "date" else ""))
        if fid in changes:
            c = changes[fid]
            val += f"<br><span class=\"seam\">changed {_e(c['changed'])}, was {_e(c['was'])}</span>"
        if "derive" in f:
            src = "derived from " + ", ".join(sorted(resolved[fid]["inputs"]))
        else:
            src = f"{f['source']['kind']}: {f['source']['ref']} ({f['source']['date']})"
        note = f" Note: {f['note']}" if f.get("note") else ""
        rows.append([f"<code>{_e(fid)}</code>", _e(f["label"]), val, _e(src + note)])
    asm = [[f"<code>{_e(x['id'])}</code>", _e(s(x["text"])), _e(x["test_that_would_decide"]), _e(x["status"])] for x in rec["assumptions"]]
    level(5, "Surgical", "Every value and where it came from",
          table(["Field", "What", "Value", "Source"], rows) + "<h2 class=\"label\">Assumptions</h2>"
          + table(["Id", "Assumption", "Test that would decide it", "Status"], asm))
    a.append(f"<h2 class=\"label\">Counsel notes</h2><p>{_e(rec.get('counsel_notes', ''))}</p>")
    a.append("</main></body></html>\n")
    return "".join(a), ctx.cites


def build(eng_dir: str) -> dict:
    """Return {relative output name: (bytes, cites digest)} plus the lock text, all in memory."""
    with open(os.path.join(eng_dir, "engagement.json"), encoding="utf-8") as fh:
        rec = json.load(fh)
    errs = validate(rec)
    if errs:
        raise RecordError("; ".join(errs))
    res = resolve(rec)
    outs = {}
    for tpl in sorted(glob.glob(os.path.join(eng_dir, "templates", "*.md.tpl"))):
        name = os.path.basename(tpl)[:-len(".md.tpl")]
        with open(tpl, encoding="utf-8") as fh:
            text, cites = render_md(rec, res, fh.read(), name)
        if "—" in text:
            raise RecordError(f"em-dash in rendered {name}.md")
        outs[f"{name}.md"] = (text, cites_digest(rec, res, cites))
    page, cites = render_html(rec, res)
    outs["proposal.html"] = (page, cites_digest(rec, res, cites))
    for name in rec.get("exports", []):
        # A structured block (e.g. a tab's rows) exported as JSON, every string cite-substituted.
        if name not in rec:
            raise RecordError(f"exports names {name!r}, which the record does not have")
        ctx = Ctx(rec, res)
        def walk(v):
            if isinstance(v, str):
                return ctx.sub(v)
            if isinstance(v, list):
                return [walk(x) for x in v]
            if isinstance(v, dict):
                return {k: walk(x) for k, x in v.items()}
            return v
        text = json.dumps(walk(rec[name]), indent=1, ensure_ascii=False, sort_keys=True) + "\n"
        if "\u2014" in text:
            raise RecordError(f"em-dash in exported {name}.json")
        outs[f"{name}.json"] = (text, cites_digest(rec, res, ctx.cites))
    lock = {"record": rec["meta"]["id"], "outputs": {
        n: {"sha256": hashlib.sha256(t.encode()).hexdigest(), "cites": c} for n, (t, c) in sorted(outs.items())}}
    return {"outputs": outs, "lock": json.dumps(lock, indent=2, sort_keys=True) + "\n"}


def write(eng_dir: str) -> list[str]:
    b = build(eng_dir)
    out_dir = os.path.join(eng_dir, "out")
    os.makedirs(out_dir, exist_ok=True)
    written = []
    for n, (t, _) in b["outputs"].items():
        with open(os.path.join(out_dir, n), "w", encoding="utf-8") as fh:
            fh.write(t)
        written.append(n)
    with open(os.path.join(out_dir, LOCK), "w", encoding="utf-8") as fh:
        fh.write(b["lock"])
    return written


def check(eng_dir: str) -> list[str]:
    """Read-only. Every problem as one line; empty list means fresh."""
    rel = os.path.relpath(eng_dir, ROOT)
    try:
        b = build(eng_dir)
    except (RecordError, json.JSONDecodeError, KeyError) as exc:
        return [f"{rel}: invalid record: {exc}"]
    out_dir = os.path.join(eng_dir, "out")
    try:
        with open(os.path.join(out_dir, LOCK), encoding="utf-8") as fh:
            old_lock = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return [f"{rel}: no {LOCK}; run python3 scripts/engagement_render.py --dir {rel}"]
    probs = []
    moved: dict[str, tuple] = {}
    for n, (text, cites) in b["outputs"].items():
        path = os.path.join(out_dir, n)
        try:
            on_disk = open(path, encoding="utf-8").read()
        except OSError:
            probs.append(f"{rel}/out/{n}: missing")
            continue
        if on_disk == text:
            continue
        old = old_lock.get("outputs", {}).get(n, {}).get("cites", {})
        diff = [k for k in sorted(set(old) | set(cites)) if old.get(k) != cites.get(k)]
        for k in diff:
            moved.setdefault(k, (old.get(k), cites.get(k), []))[2].append(n)
        if not diff:
            probs.append(f"{rel}/out/{n}: differs from a fresh render with no cited value moved (record text, template, or a hand edit changed)")
    for k, (was, now, names) in sorted(moved.items()):
        probs.append(f"{rel}: STALE field {k}: was {was!r}, now {now!r}; not regenerated in {', '.join(names)}")
    if not probs:
        with open(os.path.join(out_dir, LOCK), encoding="utf-8") as fh:
            if fh.read() != b["lock"]:
                probs.append(f"{rel}/out/{LOCK}: stale")
    if probs:
        probs.append(f"  fix: python3 scripts/engagement_render.py --dir {rel}, review the diff, re-stage")
    return probs


# ---------------------------------------------------------------- self-test

def self_test() -> int:
    src = os.path.join(ROOT, "_ARTIFACTS", "engagements", "myally-ld")
    tmp = tempfile.mkdtemp(prefix="engagement-selftest-")
    eng = os.path.join(tmp, "eng")
    try:
        shutil.copytree(os.path.join(src, "templates"), os.path.join(eng, "templates"))
        shutil.copy(os.path.join(src, "engagement.json"), eng)
        recp = os.path.join(eng, "engagement.json")

        def edit(fn):
            rec = json.load(open(recp, encoding="utf-8"))
            fn(rec)
            json.dump(rec, open(recp, "w", encoding="utf-8"), indent=2)

        write(eng)
        assert check(eng) == [], f"fresh render must pass: {check(eng)}"
        first = {n: open(os.path.join(eng, "out", n), encoding="utf-8").read() for n in os.listdir(os.path.join(eng, "out"))}
        write(eng)
        again = {n: open(os.path.join(eng, "out", n), encoding="utf-8").read() for n in os.listdir(os.path.join(eng, "out"))}
        assert first == again, "render must be idempotent"
        assert "fixed $1,500" in first["agreement.md"], "agreement must cite the Step 1 fee"

        edit(lambda r: r["fields"]["rate_ff"].update(value=150))
        p = check(eng)
        assert any("STALE field fee_step1" in x and "agreement.md" in x for x in p), p
        assert any("STALE field rate_ff" in x for x in p), p
        write(eng)
        assert check(eng) == [] and "fixed $1,800" in open(os.path.join(eng, "out", "agreement.md")).read()

        with open(os.path.join(eng, "out", "reply.md"), "a", encoding="utf-8") as fh:
            fh.write("hand edit\n")
        assert any("hand edit" in x for x in check(eng)), "hand edit must fail"
        write(eng)

        def moved(r):
            r["meta"]["last_sent"] = "2026-11-07"
            f = r["fields"]["access_by"]
            f["value"], f["history"] = "2026-11-13", []  # fixed start, so record edits never break this test
            f["history"].append({"value": f["value"], "until": "2026-11-10", "source": f["source"]})
            f["value"] = "2026-11-20"
        edit(moved)
        write(eng)
        reply = open(os.path.join(eng, "out", "reply.md"), encoding="utf-8").read()
        assert "CHANGED SINCE LAST SENT" in reply and "access_by: was Nov 13, now Nov 20" in reply, reply[:600]
        import datetime as _dt
        _days = json.load(open(recp, encoding="utf-8"))["fields"]["duration_days"]["value"]
        _want = _dt.date(2026, 11, 20) + _dt.timedelta(days=_days)
        assert _want.strftime("%b ") + str(_want.day) in reply, "deliver_by must follow access_by"
        assert "changed 2026-11-10, was Nov 13" in open(os.path.join(eng, "out", "proposal.html")).read()

        for bad, want in (
            (lambda r: r["terms"].append({"id": "TX", "title": "x", "body": "{{nope}}"}), "unknown cite"),
            (lambda r: r["fields"]["rate_ff"].pop("source"), "no source"),
            (lambda r: r["assumptions"][0].update(test_that_would_decide=""), "no test"),
            (lambda r: r["fields"].update(loop={"kind": "int", "label": "x", "derive": ["mul", "loop", 2]}), "cycle"),
        ):
            shutil.copy(os.path.join(src, "engagement.json"), recp)
            edit(bad)
            p = check(eng)
            assert p and want in p[0], (want, p)
        print("engagement_render self-test: OK (fresh passes, idempotent, stale field named, hand edit caught, seam shown, 4 invalid records refused)")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dir", help="one engagement folder (default: every _ARTIFACTS/engagements/*)")
    ap.add_argument("--check", action="store_true", help="read-only; exit 1 when any output is stale or the record invalid")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    dirs = [os.path.abspath(args.dir)] if args.dir else sorted(os.path.dirname(p) for p in glob.glob(ENG_GLOB))
    if args.check:
        probs = [p for d in dirs for p in check(d)]
        for p in probs:
            print(p, file=sys.stderr)
        if not probs:
            print(f"engagement_render --check: {len(dirs)} engagement(s) fresh")
        return 1 if probs else 0
    for d in dirs:
        try:
            names = write(d)
        except RecordError as exc:
            print(f"{os.path.relpath(d, ROOT)}: {exc}", file=sys.stderr)
            return 1
        print(f"{os.path.relpath(d, ROOT)}/out: {', '.join(names)}, {LOCK}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
