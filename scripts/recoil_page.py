#!/usr/bin/env python3
"""recoil_page: one recoil SSOT (v2, or six-tab v1 through the adapter) to a single-file HTML page.

The page follows the arc weld anatomy (_PROPOSALS/2026-11-11-recoil-call-service-arc-weld.md 4.1):
header with a Y chip in its own state color and NCI (prior to post, or "not scored" in grain), one
glance ledger of at most five rows with the next move first, folds in the groups Decide, Evidence
(method tabs in lifecycle order), System and Method, then the Deeper Strata appendix.

`plan()` below is the Python twin of src/document/recoil/anatomy.ts, the plan the React screen
renders. tests/unit/recoil-anatomy.test.ts runs `--plan` on the fixtures and fails on any
difference, so both renders come from one plan. Component CSS is copied verbatim from the kit
(src/ui-kit/recoil-report, @prim blocks); kit_primitive_sync.py --check diffs every block.

  python3 scripts/recoil_page.py SSOT.json [-o OUT.html]   # build the page (build output; not committed)
  python3 scripts/recoil_page.py SSOT.json --plan          # the anatomy plan as JSON
  python3 scripts/recoil_page.py --self-test
Stdlib only. Internal pages: every audience renders; meta.gate is never read.
"""
from __future__ import annotations

import html as _html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KIT = os.path.join(ROOT, "src", "ui-kit", "recoil-report")
sys.path.insert(0, HERE)
import recoil_ssot_v2 as v2  # noqa: E402
from recoil_brief import _grad  # noqa: E402  (same central difference as src/document/kinematics.ts)

# --------------------------------------------------------------------------- plan (twin of anatomy.ts)

FID_TONE = {"SHARP": "green", "DEGRADED": "gold", "GRAIN": "steel", "MOIRE": "magenta"}
Y_TONE = {"GREEN": "green", "YELLOW": "gold", "FORK": "gold", "RED": "red", "PARADOX": "magenta"}
METHOD_RANK = {"pre": 1, "exante": 2, "forge": 3, "recoil": 4, "wargame": 5, "defense": 6}
VERBS = ["analyze", "assess", "evaluate", "synthesize", "recapitulate"]
MAX = 120
_SCHEMA = v2.load_schema()


def rec(v):
    return v if isinstance(v, dict) else {}


def arr(v):
    return v if isinstance(v, list) else []


def s(v):
    if isinstance(v, str):
        return v
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


def fidelity(letter=None, y=None):
    return v2.fidelity(letter, y, _SCHEMA)


def grade_chip(g):
    g = rec(g)
    letter = s(g.get("letter")) or "NS"
    f = fidelity(letter)
    n = g.get("n") if isinstance(g.get("n"), int) else 0
    name = "Not scored" if letter == "NS" else f"Grade {letter}"
    return {"tone": FID_TONE[f], "label": f"{name} · n = {n}" if f == "GRAIN" else name}


NAMED = {"rarr": "→", "larr": "←", "ldquo": "“", "rdquo": "”", "lsquo": "‘",
         "rsquo": "’", "le": "≤", "ge": "≥", "ne": "≠", "asymp": "≈", "deg": "°",
         "amp": "&", "lt": "<", "gt": ">", "quot": '"', "apos": "'", "nbsp": " ", "middot": "·",
         "times": "×", "mdash": "—", "ndash": "–", "hellip": "…"}


def plain(h):
    t = s(h)
    t = re.sub(r"<br\s*/?>", " ", t, flags=re.I)
    t = re.sub(r"<[^>]*>", "", t)
    t = re.sub(r"&#x([0-9a-fA-F]+);", lambda m: chr(int(m.group(1), 16)), t)
    t = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), t)
    t = re.sub(r"&([a-zA-Z]+);", lambda m: NAMED.get(m.group(1).lower(), m.group(0)), t)
    return re.sub(r"\s+", " ", t).strip()


def first_sentence(text):
    t = text.strip()
    m = re.match(r"^(.+?[.?!])(\s|$)", t, re.S)
    return clip(m.group(1) if m else t)


def clip(out):
    """Cut at a word to MAX characters."""
    out = out.strip()
    if len(out) > MAX:
        cut = out[:MAX - 1]
        sp = cut.rfind(" ")
        out = re.sub(r"[\s,;:.·-]+$", "", cut[:sp] if sp > 40 else cut) + "…"
    return out


CLOSED = re.compile(r"^\s*(DONE|RESOLVED|CLOSED|SUPERSEDED|DROPPED)\b")  # a step its author marked finished


def step_text(st):
    """Owner and step, without the author's NEXT marker."""
    return plain(st.get("owner")) + ": " + re.sub(r"^NEXT\b:?\s*", "", plain(st.get("text")))


def next_step(open_steps):
    """The step its author marked NEXT leads; otherwise the first open one."""
    return next((x for x in open_steps if re.match(r"^\s*NEXT\b", plain(x.get("text")))), open_steps[0] if open_steps else None)


def is_open(step):
    return not CLOSED.match(plain(step.get("text")))


PLACEHOLDER = re.compile(r"\{\{[^}]*\}\}|^\s*(TBD|TODO|PENDING)\s*$", re.I)


def sentence(t):
    return t + "." if t and not re.search(r"[.?!]$", t) else t


def real(v):
    p = plain(v)
    return p if p and not PLACEHOLDER.search(p) else ""


def block_text(b):
    t = s(b.get("type"))
    cands = []
    if t == "receipt":
        cands += [f"{plain(f.get('label'))}: {plain(f.get('value'))}" for f in arr(b.get("fields")) if isinstance(f, dict)]
    if t == "keyvalue":
        cands += [f"{plain(r.get('k'))}: {plain(r.get('v'))}" for r in arr(b.get("rows")) if isinstance(r, dict)]
    cands.append(b.get("intro"))
    cands += arr(b.get("p"))
    cands += [it.get("html", it.get("text")) for it in arr(b.get("items")) if isinstance(it, dict)]
    for c in cands:
        p = real(c)
        if p and not re.search(r":\s*$", p):
            return p
    return ""


def forge_rulings(blocks):
    for b in blocks:
        if s(b.get("type")) != "table":
            continue
        cols = [plain(c).lower() for c in arr(b.get("columns"))]
        ci = next((i for i, c in enumerate(cols) if "ruling" in c), -1)
        if ci < 0:
            continue
        out = {}
        for r in arr(b.get("rows")):
            r = arr(r)
            v = plain(r[ci] if ci < len(r) else "").upper()
            k = next((x for x in ("GROUNDED", "INFERENCE", "STRUCK") if x in v), "OTHER")
            out[k] = out.get(k, 0) + 1
        return out
    return None


def tab_fold(tid, label, tab, idx, blocks, fc):
    own = [blocks[i] for i in idx]
    verdict = real(tab.get("verdict"))
    chip = grade_chip(tab["grade"]) if isinstance(tab.get("grade"), dict) else {"tone": "steel", "label": "Not graded"}
    if tid == "forge":
        r = forge_rulings(own)
        if r:
            parts = [f"{r[k]} {w}" for k, w in (("GROUNDED", "grounded"), ("INFERENCE", "inference"), ("STRUCK", "struck")) if r.get(k)]
            if not verdict:
                verdict = "Claims on the call: " + ", ".join(parts)
            if not isinstance(tab.get("grade"), dict):
                chip = {"tone": "red", "label": f"{r['STRUCK']} struck"} if r.get("STRUCK") else {"tone": "green", "label": "None struck"}
    if tid == "recoil" and not verdict and fc:
        verdict = f"{sum(1 for f in fc if f['moved'])} of {len(fc)} beliefs moved on the call"
    if not verdict:
        for b in own:
            t = block_text(b)
            if t:
                verdict = t
                break
    return {"id": f"f-{tid}", "title": label, "verdict": first_sentence(verdict or label), "chip": chip, "kind": "blocks", "blocks": idx}


def forecasts(raw):
    out = []
    for b in arr(raw.get("beliefs")):
        if not isinstance(b, dict):
            continue
        c = arr(b.get("confidence"))
        num = lambda v: v if isinstance(v, (int, float)) and not isinstance(v, bool) else None  # noqa: E731
        a = num(c[0]) if c else None
        z = num(c[1] if len(c) > 1 else (c[0] if c else None))
        g = b.get("grade") if isinstance(b.get("grade"), dict) else None
        out.append({"id": s(b.get("id")), "claim": plain(b.get("claim")),
                    "before": "not held" if a is None else s(a), "after": "--" if z is None else s(z),
                    "moved": a is not None and z is not None and a != z,
                    "fidelity": fidelity(s(g.get("letter")) if g else None), "chip": grade_chip(g)})
    return out


def plan(raw):
    meta, opp, page = rec(raw.get("meta")), rec(raw.get("opportunity")), rec(raw.get("page"))
    hd = rec(page.get("header"))
    blocks = [rec(b) for b in arr(page.get("blocks"))]
    fc = forecasts(raw)

    y = s(opp.get("y_state")).strip().upper()
    chips = []
    if y:
        chips.append({"tone": Y_TONE.get(y, "steel"), "label": f"Y · {y}"})
    num = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)  # noqa: E731
    # Both zero is the template default, not a score (Schriner 2026-09-14 carries 0 and 0 on a YELLOW call).
    scored = (num(opp.get("nci_prior")) or num(opp.get("nci_post"))) and not (opp.get("nci_prior") in (0, None) and opp.get("nci_post") in (0, None))
    nv = lambda v: s(v) if num(v) else "--"  # noqa: E731
    chips.append({"tone": "steel", "label": f"NCI {nv(opp.get('nci_prior'))} → {nv(opp.get('nci_post'))}"} if scored
                 else {"tone": "steel", "label": "NCI · not scored · n = 0"})
    header = {
        "eyebrow": plain(hd.get("eyebrow")) or "Recoil",
        "title": plain(hd.get("title")) or " · ".join(x for x in (s(meta.get("counterpart")), s(meta.get("date"))) if x),
        "lede": " ".join(x for x in (sentence(real(hd.get("sub"))), "NCI is the Net Coherence Index.") if x),
        "ref": " · ".join(x for x in (s(meta.get("date")), s(meta.get("counterpart")), s(meta.get("report_id"))) if x),
        "chips": chips, "nciGrain": not scored,
    }

    tabs = [{"id": s(t.get("id")), "label": plain(t.get("label")), "tab": t} for t in arr(page.get("tabs")) if isinstance(t, dict)]
    known = {t["id"] for t in tabs}
    loose = [i for i, b in enumerate(blocks) if s(b.get("tab")) not in known]
    tf = []
    for t in tabs:
        idx = [i for i, b in enumerate(blocks) if s(b.get("tab")) == t["id"]]
        if idx:
            tf.append({"t": t, "both": all(s(blocks[i].get("audience")) == "both" for i in idx),
                       "fold": tab_fold(t["id"], t["label"], t["tab"], idx, blocks, fc)})

    evidence = []
    verbs = rec(raw.get("verbs"))
    for vb in VERBS:
        p = rec(verbs.get(vb))
        if s(p.get("verdict")):
            evidence.append({"id": f"f-verb-{vb}", "title": vb[0].upper() + vb[1:], "verdict": first_sentence(plain(p["verdict"])),
                             "chip": grade_chip(p.get("grade")), "kind": "verb", "verb": vb})
    evidence += [x["fold"] for x in tf if x["both"] and x["t"]["id"] not in METHOD_RANK]
    evidence += [x["fold"] for x in sorted((x for x in tf if x["t"]["id"] in METHOD_RANK), key=lambda x: METHOD_RANK[x["t"]["id"]])]
    system = [x["fold"] for x in tf if not x["both"] and x["t"]["id"] not in METHOD_RANK]
    if loose:
        system.append(tab_fold("unfiled", "Unfiled" if tabs else "Brief", {}, loose, blocks, fc))

    decide = []
    steps = [x for x in arr(raw.get("next_steps")) if isinstance(x, dict)]
    open_steps = [x for x in steps if is_open(x)]
    if real(opp.get("note")) or steps:
        s0 = next_step(open_steps)
        decide.append({"id": "f-next", "title": "Where it stands",
                       "verdict": first_sentence(step_text(s0) if s0 else real(opp.get("note"))),
                       "chip": {"tone": "cyan", "label": f"{len(open_steps)} open of {len(steps)}"} if steps else {"tone": "cyan", "label": "Note"},
                       "kind": "next"})
    if fc:
        graded = sum(1 for f in fc if f["fidelity"] != "GRAIN")
        moved = sum(1 for f in fc if f["moved"])
        decide.append({"id": "f-forecasts", "title": "Forecasts",
                       "verdict": f"{moved} of {len(fc)} beliefs moved; " + (f"{graded} graded" if graded else "none graded, so all render grain"),
                       "chip": {"tone": "steel", "label": f"{graded} of {len(fc)} graded"} if graded else {"tone": "steel", "label": "Not scored · n = 0"},
                       "kind": "forecasts"})

    mig = rec(raw.get("migration"))
    frm = s(mig.get("from")) or ("v2" if s(raw.get("schema")) else "six-tab.v1")
    method = [{"id": "f-glass", "title": "Glass box",
               "verdict": f"Rendered by code from {s(meta.get('report_id')) or 'this SSOT'} ({frm}); fidelity and color set from grade and Y state",
               "chip": {"tone": "steel", "label": "How it was made"}, "kind": "glass"}]

    groups = [g for g in (
        {"name": "Decide", "note": "what to do next", "folds": decide},
        {"name": "Evidence", "note": "what the decision rests on, method in lifecycle order", "folds": evidence},
        {"name": "System", "note": "what else this record holds", "folds": system},
        {"name": "Method", "note": "how this page was made", "folds": method},
    ) if g["folds"]]

    glance = []
    allf = [f for g in groups for f in g["folds"]]
    n0 = next_step(open_steps)
    if n0:
        glance.append({"key": "Next move", "text": clip(step_text(n0)), "href": "#f-next",
                       "chip": {"tone": "cyan", "label": plain(n0.get("owner")) or "Owner"}})
    else:
        glance.append({"key": "Next move", "text": "No open next step in this record.", "href": "", "chip": {"tone": "steel", "label": "None on record"}})
    quote = real(rec(meta.get("provenance")).get("load_bearing_quote"))
    if quote:
        glance.append({"key": "Signal", "text": clip(quote), "href": "#f-strata"})
    elif evidence:
        glance.append({"key": "Signal", "text": evidence[0]["verdict"], "href": f"#{evidence[0]['id']}"})
    if open_steps:
        owners = {}
        for st in open_steps:
            o = plain(st.get("owner")) or "Unowned"
            owners[o] = owners.get(o, 0) + 1
        glance.append({"key": "Owed", "text": ", ".join(f"{o} owes {n}" for o, n in owners.items()), "href": "#f-next"})
    if fc:
        glance.append({"key": "Forecasts", "text": decide[-1]["verdict"], "href": "#f-forecasts", "chip": decide[-1]["chip"]})
    pre = next((f for f in allf if f["id"] == "f-pre"), None)
    glance.append({"key": "Pre-call", "text": pre["verdict"], "href": "#f-pre"} if pre else
                  {"key": "Pre-call", "text": "No pre-call tab in this record.", "href": "", "chip": {"tone": "steel", "label": "None on record"}})

    guard = None
    for b in blocks:
        if s(b.get("tab")) == "exante" and s(b.get("type")) == "receipt":
            for fld in arr(b.get("fields")):
                if isinstance(fld, dict) and re.search(r"falsifier|kill|stop.?loss", plain(fld.get("label")), re.I) and real(fld.get("value")):
                    guard = {"title": plain(fld.get("label")), "text": real(fld.get("value"))}
                    break
        if guard:
            break

    return {"header": header, "glance": glance[:5], "groups": groups, "forecasts": fc, "guard": guard,
            "appendix": {"id": "f-strata", "title": "Deeper Strata", "verdict": "Provenance and every key the folds above do not render, verbatim"}}


def load_v2(path):
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    stem = os.path.splitext(os.path.basename(path))[0]
    return v2.to_v2(doc, stem)


# --------------------------------------------------------------------------- HTML

PRIMS = ["27-section-label", "28-chip", "30-button", "32-evidence-ref", "33-led", "37-fidelity-grain",
         "56-fold", "57-ledger-row", "58-toast", "59-claim-check", "62-attributed-notes"]
RULING = {"GROUNDED": ("sharp", "green"), "STRUCK": ("slip", "red"), "INFERENCE": ("grain", "steel")}
ALLOWED = {"strong", "b", "em", "i", "br", "code", "a", "span", "u", "sub", "sup"}
# Kit 28 has no magenta chip yet (adding the rule ripples into every page that copies the chip block,
# so it waits for a kit release); a PARADOX chip renders plain here and magenta in React.
TONE_CLASS = {"cyan": "cyan", "green": "green", "gold": "gold", "red": "red", "magenta": "", "steel": ""}
FID_CLASS = {"SHARP": "sharp", "DEGRADED": "degraded", "GRAIN": "grain", "MOIRE": "moire"}


def esc(t):
    return _html.escape(s(t), quote=True)


def clean(h):
    """Authored HTML fragments from committed SSOTs: keep the inline tags they use, drop the rest.
    Mirrors clean() in src/document/screens/WarRoomReport.tsx."""
    t = re.sub(r"<(script|style|iframe|object)[\s\S]*?</\1\s*>", "", s(h), flags=re.I)

    def tag(m):
        name, attrs = m.group(1).lower(), m.group(2)
        if name not in ALLOWED:
            return ""
        if m.group(0).startswith("</"):
            return f"</{name}>"
        if name == "a":
            href = re.search(r'href\s*=\s*"(https?://[^"]*)"', attrs, re.I)
            return f'<a href="{esc(href.group(1))}" target="_blank" rel="noopener noreferrer">' if href else "<a>"
        return f"<{name}>"
    return re.sub(r"</?([a-zA-Z0-9]+)([^>]*)>", tag, t)


def chip(c):
    cls = TONE_CLASS.get(c["tone"], "")
    return f'<span class="chip{(" " + cls) if cls else ""}">{esc(c["label"])}</span>'


def kit_prim(name):
    for f in sorted(os.listdir(KIT)):
        if re.match(r"\d\d-.*\.html$", f):
            m = re.search(r"/\* @prim:begin %s \*/\n.*?/\* @prim:end %s \*/\n" % (re.escape(name), re.escape(name)),
                          open(os.path.join(KIT, f), encoding="utf-8").read(), re.S)
            if m:
                return f"/* from src/ui-kit/recoil-report/{f} */\n" + m.group(0)
    raise SystemExit(f"kit primitive {name} has no @prim block")


def print_palette():
    """The @media print block of the kit light remap, verbatim: print is light (spec 8 Q2, Zach 2026-11-12)."""
    light = open(os.path.join(KIT, "_tokens-light.css"), encoding="utf-8").read()
    m = re.search(r"^@media print\{.*\}\}$", light, re.M)
    if not m:
        raise SystemExit("_tokens-light.css has no @media print block")
    return "/* Print palette, from src/ui-kit/recoil-report/_tokens-light.css (its @media print block, verbatim) */\n" + m.group(0) + "\n"


PAGE_CSS = """/* Page layer, recoil-skim template: layout, tables and print only. Every component rule above is a kit block. */
:root { --fs-label: 0.75rem; --fs-body: 0.9375rem; --measure: 680px; } /* label 12px, body 15px (spec 4.3); one px measure */
* { box-sizing: border-box; margin: 0; padding: 0; }
html { background: var(--bg); color-scheme: dark; }
body { background: var(--bg); color: var(--text); font-family: var(--ds-font-sans); font-size: var(--fs-body); line-height: 1.6; -webkit-font-smoothing: antialiased; }
a { color: var(--cyan); text-underline-offset: 3px; }
:focus-visible { outline: 2px solid var(--cyan); outline-offset: 3px; }
.wrap { max-width: calc(var(--measure) + 48px); margin: 0 auto; padding: 32px 24px 160px; display: flex; flex-direction: column; gap: 24px; }
.hero { display: flex; flex-direction: column; gap: 12px; }
.hero .section-label { margin-bottom: 0; }
.hero h1 { font-family: var(--ds-font-display); font-size: var(--fs-display); font-weight: 600; line-height: 1.15; text-wrap: balance; }
.hero .lede { max-width: none; font-size: var(--fs-headline); line-height: 1.5; color: var(--text-secondary); }
.controls { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px; }
.controls p { color: var(--text-secondary); }
.lr-body > span > a { display: inline-block; padding: 13px 4px; margin: -13px 0; }
.sub { font-family: var(--ds-font-mono); font-size: var(--fs-label); font-weight: 700; letter-spacing: 0.02em; color: var(--text); }
.fold-body > p { color: var(--text); }
.tbl-wrap { overflow-x: auto; }
.tbl { width: 100%; border-collapse: collapse; }
.tbl th { font-family: var(--ds-font-mono); font-size: var(--fs-label); font-weight: 700; letter-spacing: 0.02em; color: var(--text-secondary); text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--border); vertical-align: bottom; }
.tbl td { padding: 10px; border-bottom: 1px solid var(--border); vertical-align: top; color: var(--text); }
.chart svg { width: 100%; height: auto; display: block; }
.strata { font-family: var(--ds-font-mono); font-size: var(--fs-label); line-height: 1.5; color: var(--text-secondary); white-space: pre-wrap; overflow-wrap: anywhere; }
.ledger-row, .claim, .tbl tr, .chart { break-inside: avoid; }
.fold > summary { break-after: avoid; }
@media (max-width: 760px) { .wrap { padding: 20px 16px 160px; gap: 16px; } }
@page { margin: 14mm 12mm; }
@media print { .wrap { max-width: none; padding: 0; } .controls, [data-copy] { display: none; } details.fold::details-content { content-visibility: visible; display: contents; } .fold { break-inside: auto; } }
"""

SCRIPT = """(function () {
  var folds = document.querySelectorAll('details.fold');
  document.querySelectorAll('[data-all]').forEach(function (b) {
    b.addEventListener('click', function () { var open = b.getAttribute('data-all') === 'open'; folds.forEach(function (d) { d.open = open; }); });
  });
  function openId(id) { var el = id && document.getElementById(id); if (el && el.tagName === 'DETAILS') el.open = true; }
  window.addEventListener('hashchange', function () { openId(location.hash.slice(1)); });
  openId(location.hash.slice(1));
  document.querySelectorAll('a[href^="#"]').forEach(function (a) { a.addEventListener('click', function () { openId(a.getAttribute('href').slice(1)); }); });
  window.addEventListener('beforeprint', function () { folds.forEach(function (d) { d.open = true; }); });
  document.querySelectorAll('[data-copy]').forEach(function (b) {
    b.addEventListener('click', function () {
      var t = b.getAttribute('data-copy'), st = b.parentNode.querySelector('[data-status]');
      try { navigator.clipboard.writeText(t).then(function () { st.textContent = 'Copied. Nothing is sent from this page.'; }); } catch (e) { st.textContent = 'Copy was blocked here; select the text and copy it.'; }
    });
  });
  var toast = document.querySelector('[data-toast]');
  if (toast) {
    var hide = function () { toast.hidden = true; };
    toast.querySelector('[data-toast-close]').addEventListener('click', hide);
    document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') hide(); });
  }
})();"""


def ledger(rows):
    """rows: (key_html, body_html, extra_class)"""
    out = []
    for k, body, cls in rows:
        out.append(f'<div class="ledger-row{(" " + cls) if cls else ""}"><div class="lr-key">{k}</div><div class="lr-body"><span>{body}</span></div></div>')
    return '<div class="ledger">' + "".join(out) + "</div>" if out else ""


def table(head, rows):
    th = "".join(f"<th>{clean(h)}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{clean(c)}</td>" for c in arr(r)) + "</tr>" for r in rows)
    return f'<div class="tbl-wrap"><table class="tbl"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


LEAD = re.compile(r"^\s*<(strong|b)>(.*?)</\1>\s*:?\s*", re.S)
DOT_LED = {"g": "led on", "r": "led alert"}


def list_rows(items):
    rows = []
    for it in items:
        if not isinstance(it, dict):
            continue
        h = s(it.get("html", it.get("text")))
        m = LEAD.match(h)
        key, body = (plain(m.group(2)).rstrip(":"), h[m.end():]) if m else ("", h)
        led = DOT_LED.get(s(it.get("dot")), "led")
        rows.append((f'<span class="{led}" aria-hidden="true"></span> {esc(key) or "Note"}', clean(body), ""))
    return rows


def chart_svg(series):
    W, H, pad = 600, 180, 24
    n = max(len(x["points"]) for x in series)
    xa = lambda i: pad + ((i / (n - 1)) * (W - 2 * pad) if n > 1 else 0)  # noqa: E731
    ya = lambda v: H - pad - max(0.0, min(1.0, v)) * (H - 2 * pad)  # noqa: E731
    grid = "".join(f'<line x1="{pad}" x2="{W - pad}" y1="{ya(g):.1f}" y2="{ya(g):.1f}" stroke="var(--border)"/><text x="4" y="{ya(g) + 3:.1f}" fill="var(--text-secondary)" font-size="12" font-family="monospace">{g}</text>' for g in (0, 0.5, 1))
    lines = "".join(f'<polyline fill="none" stroke="{esc(x["color"])}" stroke-width="2" points="{" ".join(f"{xa(i):.1f},{ya(v):.1f}" for i, v in enumerate(x["points"]))}"/>' for x in series)
    legend = ledger([(f'<span aria-hidden="true" style="display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:8px;background:{esc(x["color"])}"></span>{esc(plain(x["label"]))}', esc(f"“{x['quote']}”") if x["quote"] else "", "") for x in series])
    return f'<div class="chart"><svg viewBox="0 0 {W} {H}" role="img" aria-label="Belief trajectory">{grid}{lines}</svg></div>{legend}'


PALETTE = {"#00F0FF": "var(--cyan)", "#00FF9D": "var(--green)", "#FFD700": "var(--gold)", "#FF4D6D": "var(--red)",
           "#A78BFA": "var(--violet)", "#E879F9": "var(--magenta)", "#FF9D3C": "var(--orange)"}


def palette_color(c):
    """A series color snaps to the nearest palette signal color (SSOTs carry ad hoc hexes)."""
    m = re.fullmatch(r"#?([0-9a-fA-F]{6})", s(c).strip())
    if not m:
        return "var(--cyan)"
    rgb = [int(m.group(1)[i:i + 2], 16) for i in (0, 2, 4)]
    near = min(PALETTE, key=lambda h: sum((int(h[1 + 2 * i:3 + 2 * i], 16) - rgb[i]) ** 2 for i in range(3)))
    return PALETTE[near]


def read_series(raw):
    ks = rec(raw.get("kinematic_series"))
    dt = ks.get("dt") if isinstance(ks.get("dt"), (int, float)) and ks.get("dt") > 0 else 1
    out = []
    for x in arr(ks.get("series")):
        if not isinstance(x, dict):
            continue
        pts = [float(p) for p in arr(x.get("points")) if isinstance(p, (int, float))]
        if pts:
            out.append({"key": s(x.get("key")), "label": s(x.get("label")), "color": palette_color(x.get("color")),
                        "points": pts, "quote": s(x.get("grounding_quote"))})
    return dt, out


def norm_label(t):
    return re.sub(r"^\s*\d+\s*[·.:-]\s*", "", plain(t)).strip().lower()


def render_block(b, raw, fold_title, nxt):
    t = s(b.get("type"))
    h2 = f'<h3 class="sub">{clean(b["h2"])}</h3>' if s(b.get("h2")) else ""
    intro = f"<p>{clean(b['intro'])}</p>" if real(b.get("intro")) else ""
    if t == "sec_label":
        lab = norm_label(b.get("text"))
        if lab in (fold_title.lower(), norm_label(rec(nxt).get("h2"))):
            return ""  # the fold title already says it: never print a section label twice
        return f'<h3 class="sub">{clean(b.get("text"))}</h3>'
    if t in ("prose", "pilot"):
        return h2 + "".join(f"<p>{clean(p)}</p>" for p in arr(b.get("p")))
    if t == "list" and s(b.get("tab")) == "pre" and re.search(r"intel", plain(b.get("h2")), re.I):
        lis = []
        for it in arr(b.get("items")):
            if isinstance(it, dict):
                h = s(it.get("html", it.get("text")))
                m = LEAD.match(h)
                lis.append(f"<li><span><b>{clean(m.group(2))}</b> {clean(h[m.end():])}</span></li>" if m else f"<li><span>{clean(h)}</span></li>")
        return (f'<div class="note-panel"><div class="note-head"><h3>{esc(plain(b.get("h2")))}</h3><span class="note-src">Gathered before the call</span></div>'
                f'{intro}<ul class="note-list">{"".join(lis)}</ul></div>')
    if t == "list":
        return h2 + intro + ledger(list_rows(arr(b.get("items"))))
    if t in ("receipt", "keyvalue"):
        rows = ([(f.get("label"), f.get("value")) for f in arr(b.get("fields")) if isinstance(f, dict)] if t == "receipt"
                else [(r.get("k"), r.get("v")) for r in arr(b.get("rows")) if isinstance(r, dict)])
        return h2 + ledger([(esc(plain(k)), clean(v), "") for k, v in rows])
    if t == "table" and s(b.get("tab")) == "forge" and any("ruling" in plain(c).lower() for c in arr(b.get("columns"))):
        cols = [plain(c).lower() for c in arr(b.get("columns"))]
        ri = next(i for i, c in enumerate(cols) if "ruling" in c)
        out = []
        for r in arr(b.get("rows")):
            r = arr(r)
            cell = lambda i: r[i] if i < len(r) else ""  # noqa: E731
            word = next((k for k in RULING if k in plain(cell(ri)).upper()), "")
            cls, tone = RULING.get(word, ("grain", "steel"))
            rest = [cell(i) for i in range(len(r)) if i not in (0, ri)]
            out.append(f'<div class="claim {cls}"><div class="claim-said"><span>{clean(cell(0))}</span></div>'
                       f'{chip({"tone": tone, "label": word.title() or plain(cell(ri))})}<div class="claim-record"><span class="claim-v">{esc(word.title() or plain(cell(ri)))}</span>'
                       + "".join(f'<span class="claim-note">{clean(x)}</span>' for x in rest) + "</div></div>")
        return h2 + intro + '<div class="claims">' + "".join(out) + "</div>"
    if t == "table":
        note = f'<p class="ref">{clean(b["note"])}</p>' if s(b.get("note")) else ""
        return h2 + intro + table(arr(b.get("columns")), arr(b.get("rows"))) + note
    if t == "rosetta":
        return h2 + table([s(b.get("left")) or "Your world", s(b.get("right")) or "This engine"], arr(b.get("rows")))
    if t == "provenance":
        prov = rec(rec(raw.get("meta")).get("provenance"))
        return '<h3 class="sub">Source and provenance</h3>' + ledger([(esc("Captured"), clean(prov.get("captured")), "")]
                                                                   + ([(esc("Load-bearing quote"), "“" + clean(prov["load_bearing_quote"]) + "”", "")] if s(prov.get("load_bearing_quote")) else []))
    if t == "worked_example":
        _, series = read_series(raw)
        close = f"<p>{clean(b['close'])}</p>" if real(b.get("close")) else ""
        return h2 + intro + (chart_svg(series) if series else "") + close
    if t == "insights":
        return h2 + intro + ledger([(esc(plain(i.get("plane"))), f"<b>{clean(i.get('title'))}</b> {clean(i.get('text'))}", "")
                                    for i in arr(raw.get("insights")) if isinstance(i, dict)])
    if t == "belief_log":
        return h2 + '<p class="ref">The belief log is shown once, in the <a href="#f-forecasts">Forecasts</a> fold under Decide.</p>'
    if t == "kinematics_table":
        dt, series = read_series(raw)
        rows = []
        for x in series:
            v = _grad(x["points"], dt)
            a = _grad(v, dt)
            j = _grad(a, dt)
            rows.append([esc(x["label"]), f"{round(max(abs(q) for q in v), 3):g} / {round(v[-1], 3):g}", f"{round(a[-1], 3):g}", f"{round(j[-1], 3):g}"])
        n = len(series[0]["points"]) if series else 0
        return h2 + table(["signal", "D1 peak/term", "D2 term", "D3 term"], rows) + f'<p class="ref">n = {n} points: D1 and D2 valid, D3 marginal, D4 and up undersampled.</p>'
    if t in ("foot", "stamp"):
        return f'<p class="ref">{clean(b.get("text"))}</p>'
    return f'<p class="ref">Unrendered block · {esc(t or "untyped")}. Kept in the SSOT; add a renderer here and in WarRoomReport.tsx.</p>'


def fold_body(f, raw, p):
    k = f["kind"]
    if k == "blocks":
        blocks = [rec(b) for b in arr(rec(raw.get("page")).get("blocks"))]
        own = [blocks[i] for i in f["blocks"]]
        return "".join(render_block(b, raw, f["title"], own[j + 1] if j + 1 < len(own) else None) for j, b in enumerate(own))
    if k == "next":
        opp = rec(raw.get("opportunity"))
        out = f"<p>{clean(opp['note'])}</p>" if real(opp.get("note")) else ""
        facts = [(esc(lab), clean(opp.get(key)) + (f'<br><span class="ref">{clean(opp.get(key + "_basis"))}</span>' if s(opp.get(key + "_basis")) else ""), "")
                 for key, lab in (("engagement_type", "Engagement"), ("topology", "Topology"), ("req_reality", "Req reality (0 to 3)")) if s(opp.get(key))]
        steps = [(esc(plain(x.get("owner")) or "Unowned"), clean(x.get("text")), "") for x in arr(raw.get("next_steps")) if isinstance(x, dict)]
        return out + ledger(facts) + ('<h3 class="sub">Next steps</h3>' + ledger(steps) if steps else "")
    if k == "forecasts":
        rows = []
        for fc in p["forecasts"]:
            rows.append(f'<div class="claim {FID_CLASS[fc["fidelity"]]}"><div class="claim-said"><span class="claim-k">{esc(fc["id"])}</span><span>{esc(fc["claim"])}</span></div>'
                        f'{chip(fc["chip"])}<div class="claim-record"><span class="claim-v">{esc(fc["before"])} → {esc(fc["after"])}</span>'
                        f'<span class="claim-note">{"Moved on the call" if fc["moved"] else "Held"}</span></div></div>')
        return ('<p class="ref">Confidence before and after the call, 0 to 1. A forecast with no grade is not scored, so it renders grain with its sample size.</p>'
                '<div class="claims">' + "".join(rows) + "</div>")
    if k == "verb":
        vp = rec(rec(raw.get("verbs")).get(f["verb"]))
        cites = ", ".join(esc(c) for c in arr(vp.get("cites")))
        return "".join(f"<p>{clean(x)}</p>" for x in arr(vp.get("body"))) + (f'<p class="ref">Cites {cites}</p>' if cites else "")
    if k == "glass":
        mig = rec(raw.get("migration"))
        rule = _SCHEMA["x-fidelity"]
        return ledger([
            (esc("Source"), esc(f"runtime/recoil/generated/{s(rec(raw.get('meta')).get('report_id'))}.json, shape {s(mig.get('from')) or 'v2'}"
                                 + (f", adapted by {s(mig.get('adapter'))}" if s(mig.get("adapter")) else "")), ""),
            (esc("Plan"), esc("scripts/recoil_page.py plan(), the twin of src/document/recoil/anatomy.ts; a unit test fails if they differ"), ""),
            (esc("Fidelity"), esc(", ".join(f"{g} {r}" for g, r in rule["by_grade"].items()) + "; Y PARADOX overrides to MOIRE"), ""),
            (esc("Color"), esc("red a failed check, gold a limit, green proven, cyan an action, plain chip unknown; paradox is magenta in the React render and plain here until kit 28 has a magenta chip"), ""),
            (esc("Components"), esc("kit " + ", ".join(PRIMS)), ""),
        ])
    return ""


def strata(raw, p):
    used = {"page", "beliefs", "kinematic_series", "insights", "next_steps", "opportunity", "schema", "call", "verbs"}
    meta = {k: v for k, v in rec(raw.get("meta")).items() if k != "gate"}
    out = ['<p class="ref">Verbatim, except that template text written with an em-dash shows a comma (house style, em-dashes 0).</p>',
           f'<h3 class="sub">meta</h3><pre class="strata">{esc(json.dumps(meta, indent=1, ensure_ascii=False))}</pre>']
    for k, v in raw.items():
        if k in used or k == "meta" or v in (None, {}, []):
            continue
        body = v if isinstance(v, str) else json.dumps(v, indent=1, ensure_ascii=False)
        out.append(f'<h3 class="sub">{esc(k)}</h3><pre class="strata">{esc(body)}</pre>')
    return re.sub(r"\s*\u2014\s*", ", ", "".join(out))


def fold_html(f, body):
    return (f'<details class="fold" id="{esc(f["id"])}"><summary><div class="fold-title"><h2>{esc(f["title"])}</h2>'
            f'<span class="fold-verdict">{esc(f["verdict"])}</span></div>{chip(f["chip"])}</summary>'
            f'<div class="fold-body">{body}</div></details>')


def guard_html(g):
    """Kit 58 toast, gold: the standing limit from the Ex-Ante receipt (its falsifier)."""
    if not g:
        return ""
    return ('<div class="toast gold" role="status" data-toast><span class="toast-title">' + esc(g["title"]) + '</span>'
            '<button class="toast-close" type="button" aria-label="Dismiss" data-toast-close><svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true">'
            '<path d="M2 2l8 8M10 2l-8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></button>'
            '<p class="toast-msg">' + esc(g["text"]) + '</p><span class="toast-meta">Set before the call, in the Ex-Ante receipt</span></div>')


def render(raw):
    p = plan(raw)
    h = p["header"]
    css = "".join(kit_prim(n) + "\n" for n in PRIMS)
    tokens = open(os.path.join(KIT, "_tokens.css"), encoding="utf-8").read()
    tokens += print_palette()
    glance = []
    for i, g in enumerate(p["glance"]):
        key = esc(g["key"])
        link = f' <a href="{esc(g["href"])}">Open</a>' if g["href"] else ""
        chips = f'<div class="lr-chips">{chip(g["chip"])}</div>' if g.get("chip") else ""
        copy = (f'<div class="row"><button class="btn" type="button" data-copy="{esc(g["text"])}">Copy</button>'
                f'<span class="ref" data-status aria-live="polite">Nothing is sent from this page.</span></div>') if i == 0 and g["key"] == "Next move" else ""
        glance.append(f'<div class="ledger-row"><div class="lr-key">{key}</div><div class="lr-body">{chips}<span>{esc(g["text"])}{link}</span>{copy}</div></div>')
    nfold = sum(len(g["folds"]) for g in p["groups"])
    groups = []
    for g in p["groups"]:
        groups.append(f'<div class="fold-group"><span class="fold-group-name">{esc(g["name"])}</span><span class="fold-group-note">{esc(g["note"])}</span></div>')
        groups += [fold_html(f, fold_body(f, raw, p)) for f in g["folds"]]
    ap = p["appendix"]
    appendix = fold_html({**ap, "chip": {"tone": "steel", "label": "Provenance"}}, strata(raw, p))
    hero_chips = "".join(chip(c).replace('class="chip', 'class="chip grain', 1) if c["label"].startswith("NCI") and h["nciGrain"] else chip(c) for c in h["chips"])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- @arcs-template: recoil-skim -->
<!-- @arcs-mode: operate -->
<!-- generated by scripts/recoil_page.py from the SSOT; edit the SSOT or the generator, not this page -->
<title>Recoil: {esc(h["title"])}</title>
<meta name="robots" content="noindex, nofollow">
<style>
{tokens}</style>
<style>
/* Kit primitives, copied from src/ui-kit/recoil-report; kit_primitive_sync.py --check diffs each block against its kit file. */
{css}</style>
<style>
{PAGE_CSS}</style>
</head>
<body>
<main class="wrap">
<header class="hero">
  <p class="section-label">{esc(h["eyebrow"])}</p>
  <h1>{esc(h["title"])}</h1>
  <p class="ref">{esc(h["ref"])}</p>
  <p class="lede">{esc(h["lede"])}</p>
  <div class="row">{hero_chips}</div>
</header>
<section aria-labelledby="g">
  <h2 class="section-label" id="g">At a glance</h2>
  <div class="ledger">{"".join(glance)}</div>
</section>
<div class="controls">
  <p>{nfold} folds in {len(p["groups"])} groups, then the Deeper Strata. Each summary states its verdict.</p>
  <div class="row"><button class="btn" type="button" data-all="open">Open all</button><button class="btn" type="button" data-all="close">Close all</button></div>
</div>
<div class="folds">
{chr(10).join(groups)}
</div>
<footer>
{appendix}
</footer>
{guard_html(p.get("guard"))}
</main>
<script>
{SCRIPT}
</script>
</body>
</html>
"""


# --------------------------------------------------------------------------- CLI

def self_test():
    ok = True

    def expect(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  [{'ok ' if cond else 'XX '}] {name}")
    expect("grade D renders grain with n", grade_chip({"letter": "D", "basis": "x", "n": 3}) == {"tone": "steel", "label": "Grade D · n = 3"})
    expect("not scored is grain, never red", grade_chip(None)["tone"] == "steel" and "n = 0" in grade_chip(None)["label"])
    expect("grade A is green", grade_chip({"letter": "A", "basis": "x"})["tone"] == "green")
    expect("PARADOX overrides to MOIRE", fidelity("A", "PARADOX") == "MOIRE")
    raw = {"meta": {"report_id": "t", "date": "2026-01-01"}, "opportunity": {"y_state": "RED"},
           "next_steps": [{"owner": "Zach", "text": "Send it."}],
           "beliefs": [{"id": "P1", "claim": "c", "inference": "OBS", "confidence": [0.5, 0.7], "conviction": "LOW", "verdict": "v"}],
           "page": {"header": {}, "tabs": [{"id": "forge", "label": "Forge"}, {"id": "pre", "label": "Pre-Call"}],
                    "blocks": [{"type": "table", "tab": "forge", "columns": ["claim", "ruling"], "rows": [["a", "STRUCK"], ["b", "GROUNDED"]]},
                               {"type": "sec_label", "tab": "pre", "text": "01 · Pre-Call"}, {"type": "prose", "tab": "pre", "p": ["Bearing. More."]}]}}
    p = plan(raw)
    expect("Y RED chip is red", p["header"]["chips"][0] == {"tone": "red", "label": "Y · RED"})
    expect("NCI not scored renders grain", p["header"]["nciGrain"] and "not scored" in p["header"]["chips"][1]["label"])
    expect("glance row one is the next move", p["glance"][0]["key"] == "Next move" and len(p["glance"]) <= 5)
    expect("method tabs in lifecycle order", [f["id"] for f in p["groups"][1]["folds"]] == ["f-pre", "f-forge"])
    forge = p["groups"][1]["folds"][1]
    expect("a struck claim is red, a failed check", forge["chip"] == {"tone": "red", "label": "1 struck"})
    page = render(raw)
    expect("section label never printed twice", page.count("01 · Pre-Call") == 0)
    expect("no em-dash in the body", "—" not in page.split("</style>")[-1])
    pr = page[page.find("Print palette, from"):]
    expect("print is light: the kit print block is inlined", "@media print{:root{--bg:#f7f8fa;" in pr and "--magenta:#a21caf" in pr)
    print("recoil_page self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "--self-test":
        return self_test()
    path = argv[0]
    raw = load_v2(path)
    if "--plan" in argv:
        print(json.dumps(plan(raw), ensure_ascii=False, indent=1))
        return 0
    out = argv[argv.index("-o") + 1] if "-o" in argv else None
    page = render(raw)
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(page)
        print(f"wrote {out} ({len(page):,} bytes)")
    else:
        sys.stdout.write(page)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
