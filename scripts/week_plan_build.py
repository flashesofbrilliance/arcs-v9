#!/usr/bin/env python3
"""week_plan_build: render a week plan (runtime/specs/week-plan.schema.json) as kit organism 70 Week Plan.

One tab per week, and inside each tab, stacked top to bottom:
  tab sparkline   each week's tab carries its own small line (three branch ends, the stop-loss); a week nobody has
                  drafted stays a flat dashed line: no data, no line
  week strip      best, base and worst as lanes from day 1 to day 7: orange while time is spent before you know
                  (opportunity cost), a gold mark at the stop-loss, then green or red for the ROI sign; kairos forks
                  as gold dashed lines, on-ramps cyan, off-ramps steel
  cascade         the future perfect, then executive to surgical, one row each, each fork tagged on its altitude
  fork cards      one per kairos fork: a sparkline with keep and kill paths, a keep/kill switch, keep-if, kill-if,
                  on-ramp, off-ramp, and the premises with their falsifiers
  order tree      first to fifth order, in a fold
  de-risk matrix  verb (analyze, assess, evaluate, synthesize, recapitulate) by lens (D W H C R), the same axes as
                  scripts/recoil_hypercube_explorer.py, then the method list

Every item that is a hypothesis carries fog grain (strength --wp-fog, default 0.5) and a Hypothesis chip; text is
never dimmed. Values not set (ROI, probability) draw shape only, and the page says so.

The CSS is the kit's: the @prim block in src/ui-kit/recoil-report/70-week-plan.html (generated from
src/ui-kit/specimens/week-plan.json by kit_specimen.py), pulled at build time. The JS lives here (WP_JS) and is
written into the specimen demo by --specimen.

  python3 scripts/week_plan_build.py DATA.json -o OUT.html      standalone page (kit tokens linked from the kit folder,
                                                                 or --inline-tokens to inline them)
  python3 scripts/week_plan_build.py DATA.json --fragment        print the organism only (section + script), for a host page
  python3 scripts/week_plan_build.py --specimen                  rewrite the specimen demo from the Gravity example, rebuild 70
  python3 scripts/week_plan_build.py --check                     exit 1 if the specimen demo is stale or the example data fails validation
  python3 scripts/week_plan_build.py --validate DATA.json        schema rules, stdlib only
  python3 scripts/week_plan_build.py --self-test
Stdlib only.
"""
import html, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = os.path.join(ROOT, "src/ui-kit/recoil-report")
KIT_PAGE = os.path.join(KIT, "70-week-plan.html")
SPEC = os.path.join(ROOT, "src/ui-kit/specimens/week-plan.json")
EXAMPLE = os.path.join(ROOT, "_ARTIFACTS/week-plan/gravity.json")
EXAMPLE_OUT = os.path.join(ROOT, "_ARTIFACTS/week-plan/gravity.html")  # preview only, not committed: light-palette advisories trip the kintsugi hook
PRIMS = ["28-chip", "56-fold", "70-week-plan"]

ALT = ["executive", "strategic", "operational", "tactical", "surgical"]
ALT_L = {"executive": "L5", "strategic": "L4", "operational": "L3", "tactical": "L2", "surgical": "L1"}
VERBS = ["analyze", "assess", "evaluate", "synthesize", "recapitulate"]
VERB_AB = {"analyze": "AN", "assess": "AS", "evaluate": "EV", "synthesize": "SY", "recapitulate": "RE"}
LENS = ["D", "W", "H", "C", "R"]
LENS_NAME = {"D": "Decision", "W": "Window", "H": "Human", "C": "Coherence", "R": "Risk"}  # recoil_hypercube_explorer.py LENS
CASES = ["best", "base", "worst"]
LENS_KEY = " \u00b7 ".join(f"{l} {n}" for l, n in LENS_NAME.items())
STATUS = {"sourced", "hypothesis", "confirmed"}
BASIS = {"unset", "stated", "measured", "judgment"}


def e(s):
    return html.escape(str(s if s is not None else ""), quote=True)


# ---------- validation (the schema's rules, stdlib only) ----------
def validate(doc):
    errs = []
    def claim(c, where):
        if not isinstance(c, dict) or not c.get("text"):
            errs.append(f"{where}: needs text"); return
        if c.get("status") not in STATUS:
            errs.append(f"{where}: status must be one of {sorted(STATUS)}")
        if c.get("status") == "sourced" and not c.get("source"):
            errs.append(f"{where}: sourced needs a source")
    if doc.get("version") != 1:
        errs.append("version must be 1")
    claim(doc.get("future_perfect"), "future_perfect")
    weeks = doc.get("weeks") or []
    if not weeks:
        errs.append("weeks: at least one")
    seen = set()
    for w in weeks:
        n = w.get("n"); where = f"week {n}"
        if n in seen: errs.append(f"{where}: duplicate n")
        seen.add(n)
        if w.get("draft"):
            continue
        claim(w.get("future_perfect"), where + " future_perfect")
        for a in ALT:
            claim((w.get("cascade") or {}).get(a), f"{where} cascade.{a}")
        for k in w.get("kairos", []):
            kw = f"{where} {k.get('id')}"
            if k.get("status") not in STATUS: errs.append(f"{kw}: status")
            if not 1 <= int(k.get("day", 0)) <= 7: errs.append(f"{kw}: day 1 to 7")
            if k.get("altitude") and k["altitude"] not in ALT: errs.append(f"{kw}: altitude")
            if not k.get("premises"): errs.append(f"{kw}: at least one premise")
            for p in k.get("premises", []):
                claim(p, f"{kw} {p.get('id')}")
                if not p.get("falsifier"): errs.append(f"{kw} {p.get('id')}: falsifier")
            for r in ("onramp", "offramp"):
                if r in k and not 1 <= int(k[r].get("day", 0)) <= 7: errs.append(f"{kw} {r}: day 1 to 7")
        for c in CASES:
            b = (w.get("scenarios") or {}).get(c)
            if not b: errs.append(f"{where} scenarios.{c}: missing"); continue
            if b.get("p_basis") not in BASIS: errs.append(f"{where} {c}: p_basis")
            if b.get("p") is not None and b.get("p_basis") == "unset": errs.append(f"{where} {c}: a set p needs a basis")
            if b.get("p") is None and b.get("p_basis") != "unset": errs.append(f"{where} {c}: basis given but p unset")
            roi = b.get("roi")
            if roi:
                if roi.get("sign") not in ("positive", "negative", "flat", "unset"): errs.append(f"{where} {c}: roi.sign")
                if roi.get("value") is not None and roi.get("basis") == "unset": errs.append(f"{where} {c}: a set roi needs a basis")
            sl = b.get("stop_loss")
            if sl and not 1 <= int(sl.get("day", 0)) <= 7: errs.append(f"{where} {c}: stop_loss.day")
        def node(o, d, path):
            if o.get("order") != d: errs.append(f"{where} orders {path}: order {o.get('order')} at depth {d}")
            if o.get("status") not in STATUS: errs.append(f"{where} orders {path}: status")
            if o.get("status") == "sourced" and not o.get("source"): errs.append(f"{where} orders {path}: source")
            for i, ch in enumerate(o.get("children", [])): node(ch, d + 1, f"{path}.{i}")
        for i, o in enumerate(w.get("orders", [])): node(o, 1, str(i))
        for m in w.get("derisk", []):
            mw = f"{where} {m.get('id')}"
            if m.get("verb") not in VERBS: errs.append(f"{mw}: verb")
            if m.get("lens") not in LENS: errs.append(f"{mw}: lens")
            if m.get("altitude") not in ALT: errs.append(f"{mw}: altitude")
            if m.get("status") not in STATUS: errs.append(f"{mw}: status")
            if m.get("status") == "sourced" and not m.get("source"): errs.append(f"{mw}: source")
    return errs


def leaves(w):
    out = []
    def walk(o):
        if isinstance(o, dict):
            if "status" in o: out.append(o["status"])
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(w)
    return out


# ---------- pieces ----------
def chip(status):
    return {"sourced": '<span class="chip cyan">On the page</span>', "confirmed": '<span class="chip">Confirmed</span>'}.get(status, "")


def hyp(status):
    return " wp-hyp" if status == "hypothesis" else ""


def src(c):
    return f'<span class="wp-src">{e(c["source"])}</span>' if c.get("source") else ""


X0, X1 = 64, 676  # day 1 and day 7 on a 700-wide strip
def dx(day, x0=X0, x1=X1):
    return round(x0 + (int(day) - 1) * (x1 - x0) / 6, 1)


SIGN_CLS = {"positive": "pos", "negative": "neg", "flat": "flat", "unset": "flat"}


def roi_cls(b):
    """Green or red only once an ROI value is set; until then the lane stays steel (Zach, 2026-11-13: steel until set)."""
    roi = b.get("roi") or {}
    return SIGN_CLS[roi.get("sign", "unset")] if roi.get("value") is not None else "flat"


def tab_spark(w):
    if w.get("draft"):
        return '<svg class="wp-tspark" viewBox="0 0 64 20" aria-hidden="true"><line class="wp-none" x1="2" y1="10" x2="62" y2="10"/></svg>'
    ys = {"best": 4, "base": 10, "worst": 16}
    parts = []
    for c in CASES:
        b = w["scenarios"][c]; sl = (b.get("stop_loss") or {}).get("day", 1)
        sx = round(2 + (sl - 1) * 60 / 6, 1)
        cls = roi_cls(b)
        parts.append(f'<line class="wp-cost" x1="2" y1="{ys[c]}" x2="{sx}" y2="{ys[c]}"/><line class="wp-{cls}" x1="{sx}" y1="{ys[c]}" x2="62" y2="{ys[c]}"/>')
    hy = " wp-hyp" if any(w["scenarios"][c]["status"] == "hypothesis" for c in CASES) else ""
    say = ", ".join(f'{c} {(w["scenarios"][c].get("roi") or {}).get("sign", "unset")}' for c in CASES)
    return (f'<svg class="wp-tspark{hy}" viewBox="0 0 64 20" aria-hidden="true">' + "".join(parts) + "</svg>"
            f'<span class="wp-sr">Branches: {e(say)}.</span>')


def strip(w):
    sc = w["scenarios"]; ys = {"best": 44, "base": 88, "worst": 132}; H = 168
    g = []
    for d in range(1, 8):
        g.append(f'<text class="wp-ax" x="{dx(d)}" y="{H - 4}" text-anchor="middle">D{d}</text>')
    byday = {}
    for k in w.get("kairos", []):
        byday.setdefault(k["day"], []).append(k["id"])
    for day, ids in byday.items():
        for j, i in enumerate(ids):
            g.append(f'<text class="wp-forkl" x="{dx(day) + 4 + j * 26}" y="12">{e(i)}</text>')
    for k in w.get("kairos", []):
        x = dx(k["day"])
        g.append(f'<line class="wp-fork" data-fork="{e(k["id"])}" x1="{x}" y1="14" x2="{x}" y2="{H - 20}"/>')
        for r, cls in (("onramp", "wp-on"), ("offramp", "wp-off")):
            if k.get(r):
                g.append(f'<circle class="{cls}" cx="{dx(k[r]["day"])}" cy="22" r="4"/>')
    for c in CASES:
        b = sc[c]; y = ys[c]; sl = b.get("stop_loss") or {}; sd = sl.get("day", 1)
        sign = SIGN_CLS[(b.get("roi") or {}).get("sign", "unset")]; rc = roi_cls(b)
        g.append(f'<text class="wp-lane wp-{c}" x="0" y="{y + 4}">{c.upper()}</text>')
        g.append(f'<line class="wp-cost" x1="{X0}" y1="{y}" x2="{dx(sd)}" y2="{y}"/>')
        g.append(f'<line class="wp-{rc}" x1="{dx(sd)}" y1="{y}" x2="{X1}" y2="{y}"/>')
        if sl:
            g.append(f'<rect class="wp-stop" x="{dx(sd) - 4}" y="{y - 7}" width="8" height="14"/>')
        g.append(f'<text class="wp-sign wp-{rc}t" x="{X1 + 10}" y="{y + 4}">{ {"pos": "+", "neg": "−", "flat": "0"}[sign] }</text>')
    desc = "; ".join(f"{c}: cost until day {(sc[c].get('stop_loss') or {}).get('day', 1)}, then ROI {(sc[c].get('roi') or {}).get('sign', 'unset')}" for c in CASES)
    svg = (f'<svg class="wp-strip" viewBox="0 0 700 {H}" role="img" aria-labelledby="wp-st-{w["n"]}">'
           f'<title id="wp-st-{w["n"]}">Week {w["n"]} branches, day 1 to day 7. {e(desc)}</title>' + "".join(g) + "</svg>")
    notes = []
    for c in CASES:
        b = sc[c]; roi = b.get("roi") or {}; sl = b.get("stop_loss") or {}
        p = "p unset" if b.get("p") is None else f"p {b['p']} ({b['p_basis']})"
        notes.append(f'<div class="wp-note wp-n-{c}{hyp(b["status"])}"><div class="wp-note-h"><span class="wp-k wp-{c}">{c}</span>'
                     f'<span class="chip">{e(p)}</span>{chip(b["status"])}</div>'
                     f'<p>{e(b["path"])}</p><dl class="wp-dl">'
                     + (f'<dt class="wp-k wp-{roi_cls(b)}t">ROI {e(roi.get("sign", "unset"))}{"" if roi.get("value") is not None else ", no value yet"}</dt><dd>{e(roi.get("text", ""))}</dd>' if roi else "")
                     + (f'<dt class="wp-k wp-costt">Opportunity cost</dt><dd>{e(b["opportunity_cost"])}</dd>' if b.get("opportunity_cost") else "")
                     + (f'<dt class="wp-k wp-stopt">Stop-loss, day {e(sl["day"])}</dt><dd>{e(sl["trigger"])}' + (f' Keeps: {e(sl["keeps"])}' if sl.get("keeps") else "") + "</dd>" if sl else "")
                     + '</dl><details class="wp-pm"><summary>Pre-mortem and post-mortem</summary><ul>'
                     + "".join(f'<li>{e(m["cause"])} <span class="wp-fals">Falsifier: {e(m["falsifier"])}</span></li>' for m in b.get("premortem", []))
                     + f'</ul><p class="wp-pmtext">{e(b["postmortem"])}</p></details></div>')
    unset = all(sc[c].get("p") is None and (sc[c].get("roi") or {}).get("value") is None for c in CASES)
    fid = '<p class="wp-fid">Shape only: no ROI value or probability is set yet (n = 0), so the lines have no scale.</p>' if unset else ""
    return ('<div class="wp-block"><h3 class="section-label">Best, base, worst</h3>'
            '<ul class="wp-legend" aria-label="Line colors"><li><i class="wp-cost"></i>opportunity cost</li><li><i class="wp-stop"></i>stop-loss</li>'
            '<li><i class="wp-flat"></i>ROI not set yet</li><li><i class="wp-pos"></i>keep, ROI + (set)</li><li><i class="wp-neg"></i>kill, ROI − (set)</li><li><i class="wp-on"></i>on-ramp</li><li><i class="wp-off"></i>off-ramp</li><li><i class="wp-forki"></i>kairos fork</li></ul>'
            f'<div class="wp-stripwrap{" wp-hyp" if any(sc[c]["status"] == "hypothesis" for c in CASES) else ""}" tabindex="0" role="region" aria-label="Week {w["n"]} branch strip, scrolls sideways on a narrow screen">{svg}</div>{fid}<div class="wp-notes">{"".join(notes)}</div></div>')


def cascade(w):
    forks = {}
    for k in w.get("kairos", []):
        forks.setdefault(k.get("altitude"), []).append(k["id"])
    rows = []
    for a in ALT:
        c = w["cascade"][a]
        tags = "".join(f'<a class="wp-ftag" href="#wp-{w["n"]}-{e(i)}">{e(i)}</a>' for i in forks.get(a, []))
        rows.append(f'<div class="wp-crow wp-a-{a}{hyp(c["status"])}"><dt><span class="wp-l">{ALT_L[a]}</span> {a.capitalize()}</dt>'
                    f'<dd><span>{e(c["text"])}</span>{src(c)}<span class="wp-crow-tags">{tags}{chip(c["status"])}</span></dd></div>')
    return '<div class="wp-block"><h3 class="section-label">Executive to surgical</h3><dl class="wp-cascade">' + "".join(rows) + "</dl></div>"


def fork_spark(k):
    fx = 24 + (k["day"] - 1) * 252 / 6
    def X(d): return round(24 + (d - 1) * 252 / 6, 1)
    on = k.get("onramp"); off = k.get("offramp")
    g = [f'<line class="wp-base" x1="24" y1="34" x2="276" y2="34"/>',
         f'<line class="wp-stopl" x1="24" y1="50" x2="276" y2="50"/>',
         f'<polyline class="wp-on" points="24,34 {fx},28"/>',
         f'<polyline class="wp-keep wp-pos" points="{fx},28 276,10"/>',
         f'<polyline class="wp-kill wp-neg" points="{fx},28 {min(fx + 40, 270)},50"/>',
         f'<polyline class="wp-kill wp-off" points="{min(fx + 40, 270)},50 276,50"/>',
         f'<circle class="wp-forkc" cx="{fx}" cy="28" r="5"/>']
    if on: g.append(f'<rect class="wp-ontick" x="{X(on["day"]) - 1.5}" y="38" width="3" height="8"/>')
    lab = f'Day 1 to 7. Fork on day {k["day"]}.' + (f' On-ramp day {on["day"]}.' if on else "") + (f' Off-ramp day {off["day"]}.' if off else "")
    return f'<svg class="wp-fspark" viewBox="0 0 300 60" role="img" aria-label="{e(lab)}">' + "".join(g) + "</svg>"


def forks(w):
    cards = []
    for k in w.get("kairos", []):
        fid = f'wp-{w["n"]}-{k["id"]}'
        prem = "".join(f'<li class="{hyp(p["status"]).strip()}"><span>{e(p["text"])}</span> {chip(p["status"])}<span class="wp-fals">Falsifier: {e(p["falsifier"])}</span></li>' for p in k["premises"])
        ramps = ""
        for r, cls, lab in (("keep_if", "wp-post", "Keep if"), ("kill_if", "wp-negt", "Kill if")):
            if k.get(r): ramps += f'<dt class="wp-k {cls}">{lab}</dt><dd>{e(k[r])}</dd>'
        for r, cls, lab in (("onramp", "wp-ont", "On-ramp"), ("offramp", "wp-offt", "Off-ramp")):
            if k.get(r): ramps += f'<dt class="wp-k {cls}">{lab}, day {e(k[r]["day"])}</dt><dd>{e(k[r]["text"])}</dd>'
        alt = f' · {e(k["altitude"].capitalize())}' if k.get("altitude") else ""
        cards.append(f'<article class="wp-fork-card{hyp(k["status"])}{" is-kill" if k.get("decision") == "kill" else ""}" id="{fid}" data-fork="{e(k["id"])}">'
                     f'<div class="wp-fork-h"><span class="wp-k wp-forkt">{e(k["id"])} · Day {e(k["day"])}{alt}</span>'
                     f'<span class="wp-sw" role="group" aria-label="{e(k["id"])} keep or kill"><button type="button" class="wp-swb" data-v="keep" aria-pressed="{"true" if k.get("decision") == "keep" else "false"}">Keep</button>'
                     f'<button type="button" class="wp-swb" data-v="kill" aria-pressed="{"true" if k.get("decision") == "kill" else "false"}">Kill</button></span></div>'
                     f'<h4 class="wp-fork-q">{e(k["fork"])} {chip(k["status"])}</h4>{src(k)}{fork_spark(k)}'
                     f'<dl class="wp-dl">{ramps}<dt class="wp-k wp-post">If true</dt><dd>{e(k["if_true"])}</dd><dt class="wp-k wp-negt">If false</dt><dd>{e(k["if_false"])}</dd></dl>'
                     f'<details class="wp-pm"><summary>What must be true ({len(k["premises"])})</summary><ul class="wp-prem">{prem}</ul></details>'
                     f'<p class="wp-live" aria-live="polite"></p></article>')
    return '<div class="wp-block"><h3 class="section-label">Kairos forks</h3><div class="wp-forks">' + "".join(cards) + "</div></div>"


def orders(w):
    def node(o):
        kids = "".join(node(c) for c in o.get("children", []))
        mark = chip(o["status"]) if o["status"] != "hypothesis" else ""
        return (f'<li class="{hyp(o["status"]).strip()}"><span class="wp-ord">{o["order"]}</span><span>{e(o["text"])}</span> {mark}'
                + (f"<ol>{kids}</ol>" if kids else "") + "</li>")
    body = "".join(f'<ol class="wp-tree">{node(o)}</ol>' for o in w.get("orders", []))
    n = sum(1 for _ in w.get("orders", []))
    st = leaves({"o": w.get("orders", [])}); nt = len(st); ns = nt - st.count("hypothesis")
    return (f'<details class="fold wp-fold"><summary><div class="fold-title"><h2>First to fifth order</h2>'
            f'<span class="fold-verdict">{n} chains, five effects deep; {ns} of {nt} steps sourced, every unmarked step is a hypothesis</span></div></summary><div class="fold-body">{body}</div></details>')


def matrix(w):
    ms = w.get("derisk", [])
    cnt = {}
    for m in ms: cnt[(m["verb"], m["lens"])] = cnt.get((m["verb"], m["lens"]), 0) + 1
    head = "".join(f'<th scope="col"><abbr title="{LENS_NAME[l]}">{l}</abbr></th>' for l in LENS)
    body = ""
    for v in VERBS:
        cells = "".join((f'<td class="wp-lit">{cnt[(v, l)]}</td>' if cnt.get((v, l)) else '<td><span class="wp-sr">0</span></td>') for l in LENS)
        body += f'<tr><th scope="row">{v.capitalize()}</th>{cells}</tr>'
    lst = "".join(f'<li class="{hyp(m["status"]).strip()}"><span>{e(m["method"])}</span><span class="wp-mtags"><span class="chip cyan">{e(m["verb"])}</span>'
                  f'<span class="wp-mmeta">{e(m["lens"])} {e(LENS_NAME[m["lens"]])} \u00b7 {e(m["altitude"])}</span>{chip(m["status"])}</span>'
                  + (f'<span class="wp-fals">Tests {e(m["kills"])}</span>' if m.get("kills") else "") + "</li>" for m in ms)
    return (f'<div class="wp-block"><h3 class="section-label">De-risk: {len(ms)} methods, verb by lens</h3>'
            f'<div class="wp-mx-wrap"><div><table class="wp-mx"><caption class="wp-sr">Count of de-risk methods by verb and lens</caption><thead><tr><td></td>{head}</tr></thead><tbody>{body}</tbody></table>'
            f'<p class="wp-mx-key">{LENS_KEY}</p></div>'
            f'<ul class="wp-methods">{lst}</ul></div></div>')


def week_panel(w):
    if w.get("draft"):
        return f'<p class="wp-fid">Week {w["n"]} has no plan yet, so its tab and this panel draw nothing.</p>'
    fp = w["future_perfect"]
    ls = leaves(w); nh = ls.count("hypothesis")
    pills = (f'<ul class="wp-pills"><li><span>Hypotheses</span><b>{nh} / {len(ls)}</b></li><li><span>Forks</span><b>{len(w.get("kairos", []))}</b></li>'
             f'<li><span>Methods</span><b>{len(w.get("derisk", []))}</b></li></ul>')
    return (f'{pills}<p class="wp-fp{hyp(fp["status"])}"><span>{e(fp["text"])}</span> {chip(fp["status"])}</p>{src(fp)}'
            + strip(w) + cascade(w) + forks(w) + matrix(w) + orders(w))


NOTAB = ' tabindex="-1"'


def render(doc, uid="wp"):
    weeks = sorted(doc["weeks"], key=lambda w: w["n"])
    tabs, panels = [], []
    for i, w in enumerate(weeks):
        tid, pid = f"{uid}-t{w['n']}", f"{uid}-p{w['n']}"
        state = "Not drafted" if w.get("draft") else f"{len(w.get('kairos', []))} forks"
        tabs.append(f'<button type="button" role="tab" class="wp-tab" id="{tid}" aria-controls="{pid}" aria-selected="{"true" if i == 0 else "false"}"'
                    f'{"" if i == 0 else NOTAB}><span class="wp-tab-n">Week {w["n"]}</span>{tab_spark(w)}<span class="wp-tab-s">{state}</span></button>')
        panels.append(f'<div role="tabpanel" class="wp-panel" id="{pid}" aria-labelledby="{tid}" tabindex="0"{"" if i == 0 else " hidden"}><h2 class="wp-wh">Week {w["n"]}{"" if w["title"].lower().startswith("week") or w.get("draft") else ": " + e(w["title"])}</h2>{week_panel(w)}</div>')
    fp = doc["future_perfect"]
    return (f'<section class="wp" id="{uid}" aria-label="{e(doc["subject"])}">'
            f'<p class="wp-fp wp-fp-top{hyp(fp["status"])}"><span class="wp-k">By the end</span> <span>{e(fp["text"])}</span> {chip(fp["status"])}</p>'
            '<p class="wp-key"><span class="wp-keyg wp-hyp" aria-hidden="true"></span>Dot grain marks a hypothesis, not yet confirmed. <span class="chip cyan">On the page</span> marks a line quoted from this page.</p>'
            f'<div class="wp-tabs" role="tablist" aria-label="Weeks">{"".join(tabs)}</div>{"".join(panels)}</section>')


WP_JS = r"""(function(){
document.querySelectorAll('.wp').forEach(function(root){
  var tabs=[].slice.call(root.querySelectorAll('.wp-tab')),panels=tabs.map(function(t){return document.getElementById(t.getAttribute('aria-controls'));});
  function show(i,focus){tabs.forEach(function(t,j){var on=j===i;t.setAttribute('aria-selected',on?'true':'false');t.tabIndex=on?0:-1;panels[j].hidden=!on;});if(focus)tabs[i].focus();}
  root.classList.add('wp-js');
  tabs.forEach(function(t,i){t.addEventListener('click',function(){show(i);});t.addEventListener('keydown',function(ev){var k=ev.key,n=tabs.length,j=null;
    if(k==='ArrowRight')j=(i+1)%n;else if(k==='ArrowLeft')j=(i+n-1)%n;else if(k==='Home')j=0;else if(k==='End')j=n-1;if(j!==null){ev.preventDefault();show(j,true);}});});
  show(0);
  root.querySelectorAll('.wp-fork-card').forEach(function(card){
    var id=card.getAttribute('data-fork'),panel=card.closest('.wp-panel'),live=card.querySelector('.wp-live');
    card.querySelectorAll('.wp-swb').forEach(function(b){b.addEventListener('click',function(){
      var kill=b.getAttribute('data-v')==='kill';
      card.querySelectorAll('.wp-swb').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false');});
      card.classList.toggle('is-kill',kill);
      if(panel)panel.querySelectorAll('.wp-fork[data-fork="'+id+'"]').forEach(function(l){l.classList.toggle('is-kill',kill);});
      var off=card.querySelector('.wp-offt'),dd=off&&off.nextElementSibling;
      live.textContent=kill?(id+' set to kill.'+(dd?' Off-ramp: '+dd.textContent:'')):(id+' set to keep.');
    });});
  });
});
})();"""


def prim(name):
    text = open(os.path.join(KIT, name + ".html"), encoding="utf-8").read()
    m = re.search(r"/\* @prim:begin %s \*/\n.*?/\* @prim:end %s \*/\n" % (name, name), text, re.S)
    if not m:
        raise SystemExit(f"kit primitive {name} has no @prim block")
    return m.group(0)


def page(doc, inline_tokens=False):
    css = "".join(prim(p) for p in PRIMS)
    if inline_tokens:
        tok = open(os.path.join(KIT, "_tokens.css"), encoding="utf-8").read() + open(os.path.join(KIT, "_tokens-light.css"), encoding="utf-8").read()
        head = f"<style>\n{tok}\n</style>\n"
    else:
        rel = os.path.relpath(KIT, os.path.dirname(EXAMPLE_OUT))
        head = f'<link rel="stylesheet" href="{rel}/_tokens.css">\n<link rel="stylesheet" href="{rel}/_tokens-light.css">\n'
    return f"""<!DOCTYPE html>
<!-- generated by scripts/week_plan_build.py from a week-plan JSON; edit the data or the kit, not this page -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(doc['subject'])}</title>
{head}<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: var(--bg); color: var(--text); font-family: var(--ds-font-sans); font-size: var(--fs-body); line-height: 1.6; }}
h1.wp-page-h {{ font-family: var(--ds-font-display); font-size: var(--fs-display); font-weight: 500; line-height: 1.15; margin-bottom: 24px; text-wrap: balance; }}
main {{ --measure: 60rem; max-width: var(--measure); margin: 0 auto; padding: 32px 16px 96px; }}
{css}</style>
</head>
<body>
<main>
<h1 class="wp-page-h">{e(doc['subject'])}</h1>
{render(doc)}
</main>
<script>
{WP_JS}
</script>
</body>
</html>
"""


# ---------- specimen ----------
def demo_doc():
    doc = json.load(open(EXAMPLE, encoding="utf-8"))
    have = {w["n"] for w in doc["weeks"]}
    for n in range(1, 8):
        if n not in have:
            doc["weeks"].append({"n": n, "title": "Not drafted", "draft": True})
    return doc


def specimen_demo():
    doc = demo_doc()
    w1 = [w for w in doc["weeks"] if w["n"] == 1][0]
    drafted = render(doc, "wp-stage")
    undrafted = render(dict(doc, weeks=[{"n": 2, "title": "Not drafted", "draft": True}]), "wp-s1")
    phone = render(dict(doc, weeks=[w1]), "wp-s2")
    return ("var WP_STAGE=" + json.dumps(drafted) + ";\nvar WP_STATES=" + json.dumps([render(dict(doc, weeks=[w1]), "wp-s0"), undrafted, phone]) + ";\n"
            "document.querySelector('[data-stage]').innerHTML=WP_STAGE;\n"
            "STATES.forEach(function(s,i){var h=document.querySelector('[data-state=\"'+i+'\"]');h.style.maxWidth=s[1];h.innerHTML=WP_STATES[i];});\n"
            + WP_JS)


def specimen_write():
    spec = json.load(open(SPEC, encoding="utf-8"))
    spec["demo"] = specimen_demo()
    with open(SPEC, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=1, ensure_ascii=False); f.write("\n")
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts/kit_specimen.py"), SPEC], check=True)


def check():
    bad = []
    spec = json.load(open(SPEC, encoding="utf-8"))
    if spec.get("demo") != specimen_demo(): bad.append("specimen demo is stale: run --specimen")
    doc = json.load(open(EXAMPLE, encoding="utf-8"))
    errs = validate(doc)
    if errs: bad += ["example: " + x for x in errs]
    for b in bad: print("week_plan_build:", b, file=sys.stderr)
    return 1 if bad else 0


def self_test():
    doc = demo_doc()
    assert not validate(doc), validate(doc)
    bad = json.loads(json.dumps(doc)); w = bad["weeks"][0]
    w["cascade"]["executive"]["status"] = "sourced"; w["cascade"]["executive"].pop("source", None)
    w["scenarios"]["best"]["p"] = 0.4
    w["derisk"][0]["lens"] = "Z"
    errs = validate(bad)
    for want in ("cascade.executive: sourced needs a source", "best: a set p needs a basis", "M1: lens"):
        assert any(want in x for x in errs), (want, errs)
    out = render(doc)
    assert out.count('role="tab"') == 7 and "wp-none" in out, "seven tabs, undrafted weeks flat"
    assert "Shape only" in out, "unset values must say shape only"
    strips = re.findall(r'<svg class="wp-strip".*?</svg>', out, re.S) + re.findall(r'<svg class="wp-tspark.*?</svg>', out, re.S)
    assert strips and not any('class="wp-pos"' in s or 'class="wp-neg"' in s for s in strips), "ROI color drawn before a value is set"
    assert "\u2014" not in out, "em-dash in output"
    css = json.load(open(SPEC, encoding="utf-8"))["css"]
    assert ".wp-panel[hidden] { display: none; }" in css, "a display rule on .wp-panel must not override [hidden]"
    assert out.count('class="wp-fork-card') == len(doc["weeks"][0]["kairos"])
    from html.parser import HTMLParser
    class Bal(HTMLParser):
        def __init__(s): super().__init__(); s.st = []
        def handle_starttag(s, t, a):
            if t not in ("circle", "line", "rect", "polyline"): s.st.append(t)
        def handle_endtag(s, t):
            if t in ("circle", "line", "rect", "polyline"): return
            assert s.st and s.st[-1] == t, f"unbalanced </{t}> at {s.getpos()}"
            s.st.pop()
    b = Bal(); b.feed(out); assert not b.st, f"unclosed {b.st}"
    print("week_plan_build self-test: ok")
    return 0


def main(a):
    if "--self-test" in a: return self_test()
    if "--check" in a: return check()
    if "--specimen" in a: specimen_write(); return 0
    if "--validate" in a:
        errs = validate(json.load(open(a[a.index("--validate") + 1], encoding="utf-8")))
        for x in errs: print(x, file=sys.stderr)
        return 1 if errs else 0
    files = [x for x in a if not x.startswith("-")]
    if not files:
        print(__doc__); return 2
    doc = json.load(open(files[0], encoding="utf-8"))
    errs = validate(doc)
    if errs:
        for x in errs: print(x, file=sys.stderr)
        return 1
    if os.path.abspath(files[0]) == EXAMPLE: doc = demo_doc()
    if "--fragment" in a:
        sys.stdout.write(render(doc) + "\n<script>\n" + WP_JS + "\n</script>\n"); return 0
    out = a[a.index("-o") + 1] if "-o" in a else None
    text = page(doc, "--inline-tokens" in a)
    if out:
        open(out, "w", encoding="utf-8").write(text); print("wrote", os.path.relpath(out, ROOT))
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
