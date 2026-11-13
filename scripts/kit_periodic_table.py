#!/usr/bin/env python3
"""kit_periodic_table: the visual periodic table of the ARCS ui-kit parts, plus its catalyst ledger.

Not the operator periodic table (operators/docs/PERIODIC-TABLE.md); this one is the UI kit's parts.

Inputs (all generated or append-only, never hand-maintained here):
  src/ui-kit/kit-manifest.json     every part (scripts/kit_pull.py manifest)
  src/ui-kit/templates.json        every template
  src/ui-kit/specimens/*.json      the declared layer of specimen-built parts
  src/ui-kit/kit-catalysts.jsonl   the catalyst ledger (append-only; one event per line)
Output:
  _ARTIFACTS/kit-periodic-table.html   self-contained page, kit tokens inlined verbatim

Axes the page shows:
  Layer (rows, the periods): Atom, Molecule, Organism, Lockup, Template, then Unclassed for any part no source
    declares. Layer comes from, in order: the specimen spec, the @dsCard subtitle's first word, the README
    hierarchy (group Molecules = Molecule; groups Recoil Report and Instrument Lab = Organism). Never guessed.
  Altitude (five sheets, keys 1 to 5, the acetate-plate ladder): Exec (one computed stamp), Strategic (layer by
    family, fidelity by layer), Operational (templates and the parts they compose), Tactical (every element as a
    tile), Surgical (every part's file, classes, twins and pages).
  Earned fidelity per element, pre-registered here before counting, printed with its sample size n = pages:
    grain     n = 0 (no page uses it)
    degraded  n = 1 (one consumer; the kit promotes on the second real case)
    moire     n >= 2 but a rule in it is an exact twin (Jaccard 1.0) of another part's rule: identity contradicts
    sharp     n >= 2 and no exact twin
  The declared fidelity states (what a part can render) show separately as four marks.

Catalyst ledger kinds: phase_shift (a part changes layer or group), new_cut (a new part), echo (a load-bearing
shape recurring: two parts first carrying an identical rule, Jaccard 1.0), insight (counterintuitive; hand-written
only), attraction (a part pulled its second page, so it earned promotion). Each event names a trigger and evidence.

  python3 scripts/kit_periodic_table.py            build the page from the ledger and manifest
  python3 scripts/kit_periodic_table.py --check    exit 1 if the page differs, or the ledger is malformed or rewritten
  python3 scripts/kit_periodic_table.py --sync     append derived events from git history, then build
  python3 scripts/kit_periodic_table.py --behind   print how many manifest commits the ledger has not synced (0 = fresh)
  python3 scripts/kit_periodic_table.py --self-test
Stdlib only.
"""
import html, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = "src/ui-kit/kit-manifest.json"
TEMPLATES = "src/ui-kit/templates.json"
SPECIMENS = "src/ui-kit/specimens"
LEDGER = "src/ui-kit/kit-catalysts.jsonl"
TOKENS = "src/ui-kit/recoil-report/_tokens.css"
GRAIN = "src/ui-kit/recoil-report/37-fidelity-grain.html"
OUT = "_ARTIFACTS/kit-periodic-table.html"
LAYERS = ("Atom", "Molecule", "Organism", "Lockup", "Template", "Unclassed")
KINDS = ("phase_shift", "new_cut", "echo", "insight", "attraction")
KIND_LABEL = {"phase_shift": "Phase shift", "new_cut": "New cut", "echo": "Load-bearing echo",
              "insight": "Counterintuitive insight", "attraction": "Attraction"}
FIDS = ("sharp", "degraded", "grain", "moire")
ALTS = ("Exec", "Strategic", "Operational", "Tactical", "Surgical")
GROUP_LAYER = {"Molecules": "Molecule", "Recoil Report": "Organism", "Instrument Lab": "Organism"}
ECHO_FLOOR = 1.0
REQUIRED = ("id", "date", "kind", "parts", "trigger", "evidence", "status", "source")


def p(rel):
    return os.path.join(ROOT, rel)


def read(rel):
    with open(p(rel), encoding="utf-8") as f:
        return f.read()


def git(*a):
    return subprocess.run(("git",) + a, cwd=ROOT, capture_output=True, text=True).stdout


def e(s):
    return html.escape(str(s), quote=True)


# ---------- inputs ----------

def ledger_lines(text=None):
    text = read(LEDGER) if text is None else text
    return [l for l in text.splitlines() if l.strip()]


def ledger(text=None):
    return [json.loads(l) for l in ledger_lines(text)]


def spec_layers():
    out = {}
    d = p(SPECIMENS)
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if f.endswith(".json"):
            s = json.load(open(os.path.join(d, f), encoding="utf-8"))
            if s.get("number") and s.get("layer"):
                out[str(s["number"])] = s["layer"]
    return out


def layer_of(part, specs):
    if part["family"] == "kit" and part["number"] in specs:
        return specs[part["number"]], "specimen spec"
    first = (part.get("subtitle") or "").split(" ")[0]
    if first in LAYERS[:-1]:
        return first, "dsCard subtitle"
    if part["group"] in GROUP_LAYER:
        return GROUP_LAYER[part["group"]], "README hierarchy"
    return "Unclassed", "no source declares it"


BOILERPLATE = re.compile(r"^(:root|html|body|\*)")  # shared token and reset rules echo by copy, not by shape


def echo_rule(d):
    return d.get("jaccard", 0) >= ECHO_FLOOR and not BOILERPLATE.match(d.get("rule") or "")


def exact_twin(part):
    return any(echo_rule(d) for d in part.get("near_duplicates", []))


def earned(part):
    n = part["reuse"]
    if n == 0:
        return "grain"
    if n == 1:
        return "degraded"
    return "moire" if exact_twin(part) else "sharp"


def symbols(parts):
    out, seen = {}, set()
    for x in parts:
        words = re.findall(r"[A-Za-z0-9]+", x["name"]) or [x["id"]]
        cands = []
        if len(words) > 1:
            cands.append(words[0][0].upper() + words[1][0].lower())
        w = words[0]
        cands += [w[0].upper() + c.lower() for c in w[1:]]
        cands += [w[0].upper() + c for c in "abcdefghijklmnopqrstuvwxyz"]
        sym = next(c for c in cands if c not in seen)
        seen.add(sym)
        out[x["id"]] = sym
    return out


def elements():
    m = json.loads(read(MANIFEST))
    specs = spec_layers()
    parts = m["parts"]
    tmpl = json.loads(read(TEMPLATES)).get("templates", {})
    users = {}
    for x in parts:
        for t in x.get("templates", []):
            users.setdefault(t, []).append(x["id"])
    els = []
    for x in parts:
        layer, why = layer_of(x, specs)
        els.append(dict(x, layer=layer, layer_source=why, earned=earned(x)))
    for name, t in sorted(tmpl.items()):
        n = len(t.get("canonical_examples", []))
        els.append({"id": "template:" + name, "number": "T", "name": name.replace("-", " ").title(), "group": "Templates",
                    "subtitle": t.get("description", ""), "family": "template", "path": TEMPLATES, "data_shape": [],
                    "fidelity": [], "classes": [], "prim_blocks": [], "templates": [], "jobs": [],
                    "pages": t.get("canonical_examples", []), "reuse": n, "near_duplicates": [],
                    "layer": "Template", "layer_source": "templates.json", "earned": "grain" if n == 0 else "degraded" if n == 1 else "sharp",
                    "mode": t.get("mode", ""), "composes": sorted(users.get(name, [])),
                    "min_signatures": t.get("min_signatures"), "signatures": len(t.get("signature_selectors", []))})
    sym = symbols(els)
    for x in els:
        x["symbol"] = sym[x["id"]]
    return m, els


# ---------- ledger checks ----------

def validate(events):
    errs, ids = [], set()
    for i, ev in enumerate(events, 1):
        miss = [k for k in REQUIRED if k not in ev]
        if miss:
            errs.append(f"line {i}: missing {', '.join(miss)}")
            continue
        if ev["kind"] not in KINDS:
            errs.append(f"line {i}: kind {ev['kind']!r} not in {KINDS}")
        if ev["status"] not in ("landed", "pending"):
            errs.append(f"line {i}: status must be landed or pending")
        if ev["source"] not in ("derived", "hand"):
            errs.append(f"line {i}: source must be derived or hand")
        if ev["kind"] == "insight" and ev["source"] != "hand":
            errs.append(f"line {i}: an insight is hand-written, never derived")
        if not ev["evidence"]:
            errs.append(f"line {i}: an event needs evidence")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", ev["date"]):
            errs.append(f"line {i}: date must be YYYY-MM-DD")
        if ev["id"] in ids:
            errs.append(f"line {i}: duplicate id {ev['id']}")
        ids.add(ev["id"])
        if chr(0x2014) in json.dumps(ev, ensure_ascii=False):
            errs.append(f"line {i}: em-dash")
    return errs


def append_only(head_text, now_text):
    """Every line committed at HEAD must still be there, unchanged and in order, at the top of the file."""
    old, new = ledger_lines(head_text), ledger_lines(now_text)
    return new[:len(old)] == old


# ---------- sync from git ----------

def clean(subj):
    return subj.replace(" \u2014 ", ", ").replace("\u2014", ",")


def manifest_history():
    rows = []
    for line in git("log", "--reverse", "--format=%H|%ad|%s", "--date=short", "--", MANIFEST).splitlines():
        sha, date, subj = line.split("|", 2)
        try:
            rows.append((sha, date, clean(subj), json.loads(git("show", f"{sha}:{MANIFEST}"))))
        except ValueError:
            continue
    return rows


def first_adds(paths):
    out = {}
    for line in git("log", "--reverse", "--diff-filter=A", "--name-only", "--format=@%H|%ad|%s", "--date=short", "--", *paths).splitlines():
        if line.startswith("@"):
            cur = line[1:].split("|", 2)
            cur[2] = clean(cur[2])
        elif line.strip() and line not in out:
            out[line] = cur
    return out


def derive():
    hist = manifest_history()
    if not hist:
        return []
    evs = []
    newest = hist[-1][3]["parts"]
    adds = first_adds(sorted({x["path"] for x in newest}))
    for x in newest:
        if x["path"] in adds:
            sha, date, subj = adds[x["path"]]
            evs.append({"id": f"new_cut:{x['id']}:{sha[:8]}", "date": date, "kind": "new_cut", "parts": [x["id"]],
                        "trigger": f"{x['path']} first committed", "evidence": [{"type": "commit", "ref": sha[:8], "note": subj}],
                        "status": "landed", "source": "derived"})
    prev, echoed = {}, set()
    for sha, date, subj, m in hist:
        cur = {x["id"]: x for x in m.get("parts", [])}
        for pid, x in cur.items():
            old = prev.get(pid)
            if old is None:
                continue
            if old.get("reuse", 0) < 2 <= x.get("reuse", 0):
                gained = sorted(set(x.get("pages", [])) - set(old.get("pages", [])))
                evs.append({"id": f"attraction:{pid}:{sha[:8]}", "date": date, "kind": "attraction", "parts": [pid],
                            "trigger": f"reached its second consumer (n {old.get('reuse', 0)} to {x['reuse']}), the kit's promotion rule",
                            "evidence": [{"type": "commit", "ref": sha[:8], "note": subj}] + [{"type": "page", "ref": g} for g in gained[:3]],
                            "status": "landed", "source": "derived"})
            if old.get("group") != x.get("group"):
                evs.append({"id": f"phase_shift:{pid}:{sha[:8]}", "date": date, "kind": "phase_shift", "parts": [pid],
                            "trigger": f"group {old.get('group')} to {x.get('group')}",
                            "evidence": [{"type": "commit", "ref": sha[:8], "note": subj}], "status": "landed", "source": "derived"})
            had = {d["twin"] for d in old.get("near_duplicates", []) if echo_rule(d)}
            for twin in sorted({d["twin"] for d in x.get("near_duplicates", []) if echo_rule(d)} - had):
                pair = sorted([pid, twin])
                eid = f"echo:{pair[0]}+{pair[1]}"
                if pid != pair[0] or eid in echoed:
                    continue
                echoed.add(eid)
                d = next(d for d in x["near_duplicates"] if d["twin"] == twin and echo_rule(d))
                evs.append({"id": f"{eid}:{sha[:8]}", "date": date, "kind": "echo", "parts": pair,
                            "trigger": f"{d.get('rule')} and {d.get('twin_rule')} carry identical declarations",
                            "evidence": [{"type": "commit", "ref": sha[:8], "note": subj}], "status": "landed", "source": "derived"})
        prev = cur
    return evs


def sync():
    have = {ev["id"] for ev in ledger()}
    new = [ev for ev in derive() if ev["id"] not in have]
    new.sort(key=lambda ev: (ev["date"], ev["id"]))
    if new:
        with open(p(LEDGER), "a", encoding="utf-8") as f:
            for ev in new:
                f.write(json.dumps(ev, ensure_ascii=False) + "\n")
    return len(new)


def behind():
    shas = [l[:8] for l in git("log", "--format=%H", "--", MANIFEST).splitlines()]
    cited = set()
    for ev in ledger():
        for ref in ev["evidence"]:
            cited.add(ref.get("ref", "")[:8])
    synced = next((i for i, s in enumerate(shas) if s in cited), len(shas))
    return synced


# ---------- render ----------

CSS = """* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); color: var(--text); font-family: var(--ds-font-sans); font-size: var(--fs-body); line-height: 1.6; padding: 32px 16px 64px; }
main { max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; gap: 40px; }
.section-label { font-family: var(--ds-font-mono); font-size: var(--fs-label); letter-spacing: 0.14em; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 12px; font-weight: 600; }
h1 { font-family: var(--ds-font-display); font-size: var(--fs-display); font-weight: 500; line-height: 1.1; letter-spacing: -0.01em; text-wrap: balance; }
h2 { font-family: var(--ds-font-display); font-size: 1.5rem; font-weight: 500; line-height: 1.25; margin-bottom: 12px; }
.lede { font-size: var(--fs-headline); line-height: 1.45; color: var(--text-secondary); max-width: none; text-wrap: pretty; }
.cold { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 260px), 1fr)); gap: 16px; }
.cold div { border-top: 1px solid var(--border); padding-top: 12px; }
.cold p { color: var(--text); }
.alts { display: flex; flex-wrap: wrap; gap: 8px; position: sticky; top: 0; background: var(--bg); padding: 12px 0; z-index: 2; border-bottom: 1px solid var(--border); }
.alts button { font: inherit; font-family: var(--ds-font-mono); font-size: var(--fs-body); letter-spacing: 0.08em; text-transform: uppercase; color: var(--text); background: var(--surface); border: 1px solid var(--border); border-radius: var(--ds-r-sm); padding: 8px 14px; cursor: pointer; min-height: 44px; }
.alts button[aria-pressed="true"] { border-color: var(--cyan); color: var(--cyan); }
.alts button:focus-visible, a:focus-visible, .scroll:focus-visible { outline: 2px solid var(--cyan); outline-offset: 2px; }
.sheet[hidden] { display: none; }
.stamp { border: 1px solid var(--border); border-radius: var(--ds-r-sm); background: var(--surface); padding: 24px; display: flex; flex-direction: column; gap: 12px; }
.stamp .big { font-family: var(--ds-font-display); font-size: var(--fs-display); line-height: 1.1; }
.kv { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 180px), 1fr)); gap: 12px; }
.kv div { border: 1px solid var(--border); border-radius: var(--ds-r-sm); padding: 14px; }
.kv b { display: block; font-family: var(--ds-font-mono); font-size: var(--fs-headline); font-variant-numeric: tabular-nums; }
.kv span { font-family: var(--ds-font-mono); font-size: var(--fs-body); letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-secondary); }
.scroll { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--border); vertical-align: top; }
thead th { font-family: var(--ds-font-mono); font-size: var(--fs-body); letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-secondary); font-weight: 600; white-space: nowrap; }
td.num, th.num { font-family: var(--ds-font-mono); font-variant-numeric: tabular-nums; text-align: right; }
code { font-family: var(--ds-font-mono); font-size: var(--fs-body); }
.period { display: grid; grid-template-columns: 132px 1fr; gap: 16px; padding: 16px 0; border-top: 1px solid var(--border); }
.period h3 { font-family: var(--ds-font-mono); font-size: var(--fs-body); letter-spacing: 0.08em; text-transform: uppercase; font-weight: 600; }
.period h3 small { display: block; font-weight: 400; letter-spacing: 0.04em; color: var(--text-secondary); text-transform: none; }
.tiles { display: grid; grid-template-columns: repeat(auto-fill, minmax(104px, 1fr)); gap: 8px; }
.tile { display: flex; flex-direction: column; gap: 2px; border: 1px solid var(--border); border-radius: var(--ds-r-sm); padding: 8px; min-height: 112px; color: var(--text); text-decoration: none; background-color: var(--surface); }
.tile:hover { border-color: var(--cyan); }
.tile.ghost { border-style: dashed; background-color: var(--bg); }
.tile .no { font-family: var(--ds-font-mono); font-size: var(--fs-body); font-variant-numeric: tabular-nums; display: flex; justify-content: space-between; }
.tile .sym { font-family: var(--ds-font-display); font-size: var(--fs-headline); line-height: 1.1; }
.tile .nm { font-size: var(--fs-body); line-height: 1.3; overflow-wrap: anywhere; }
.marks { display: flex; gap: 3px; margin-top: auto; font-family: var(--ds-font-mono); font-size: var(--fs-body); }
.marks i { font-style: normal; width: 14px; text-align: center; border: 1px solid var(--border); border-radius: var(--ds-r-sm); line-height: 1.3; }
.marks i.on { border-color: var(--text); }
.marks i.off { border-style: dotted; }
.legend { display: flex; flex-wrap: wrap; gap: 8px 20px; font-size: var(--fs-body); }
.legend span { display: inline-flex; gap: 6px; align-items: center; }
.chip { font-family: var(--ds-font-mono); font-size: var(--fs-body); letter-spacing: 0.06em; text-transform: uppercase; border: 1px solid var(--border); border-radius: 999px; padding: 1px 8px; white-space: nowrap; }
.chip.pending { border-style: dashed; }
.ev td:first-child { white-space: nowrap; font-family: var(--ds-font-mono); font-variant-numeric: tabular-nums; }
.ev ul { list-style: none; display: flex; flex-direction: column; gap: 2px; }
.filters { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
.filters button { font: inherit; font-size: var(--fs-body); color: var(--text); background: var(--surface); border: 1px solid var(--border); border-radius: 999px; padding: 4px 12px; cursor: pointer; min-height: 44px; }
.filters button[aria-pressed="true"] { border-color: var(--cyan); color: var(--cyan); }
.note { max-width: none; color: var(--text); }
footer { border-top: 1px solid var(--border); padding-top: 16px; font-size: var(--fs-body); color: var(--text-secondary); }
@media (max-width: 640px) { .period { grid-template-columns: 1fr; gap: 8px; } }
"""

JS = """(function(){
var bs=[].slice.call(document.querySelectorAll('.alts button')),ss=[].slice.call(document.querySelectorAll('.sheet'));
function show(n){bs.forEach(function(b){b.setAttribute('aria-pressed',b.dataset.alt===n?'true':'false');});ss.forEach(function(s){s.hidden=s.dataset.alt!==n;});try{localStorage.setItem('kitTableAlt',n);}catch(_){}}
bs.forEach(function(b){b.addEventListener('click',function(){show(b.dataset.alt);});});
document.addEventListener('keydown',function(ev){if(ev.target.closest&&ev.target.closest('input,textarea,select'))return;if(/^[1-5]$/.test(ev.key))show(ev.key);});
var s='4';try{s=localStorage.getItem('kitTableAlt')||'4';}catch(_){}
show(s);
var fs=[].slice.call(document.querySelectorAll('.filters button')),rows=[].slice.call(document.querySelectorAll('.ev tbody tr'));
fs.forEach(function(f){f.addEventListener('click',function(){var k=f.dataset.kind;fs.forEach(function(o){o.setAttribute('aria-pressed',o===f?'true':'false');});rows.forEach(function(r){r.hidden=!(k==='all'||r.dataset.kind===k);});});});
})();"""


def grain_block():
    t = read(GRAIN)
    a = t.index("/* @prim:begin 37-fidelity-grain */")
    b = t.index("/* @prim:end 37-fidelity-grain */") + len("/* @prim:end 37-fidelity-grain */")
    return t[a:b]


def marks(x):
    out = []
    for f, ch in zip(FIDS, "SDGM"):
        on = f in x.get("fidelity", [])
        out.append(f'<i class="{"on" if on else "off"}" title="{f}{"" if on else " (not declared)"}">{ch}</i>')
    return f'<span class="marks" aria-hidden="true">{"".join(out)}</span>'


def tile(x):
    label = f"{x['number']} {x['name']}, {x['layer']}, earned {x['earned']}, n = {x['reuse']}"
    return (f'<a class="tile {x["earned"]}" href="#s-{e(slug(x["id"]))}" aria-label="{e(label)}">'
            f'<span class="no"><span>{e(x["number"])}</span><span>n {x["reuse"]}</span></span>'
            f'<span class="sym">{e(x["symbol"])}</span><span class="nm">{e(x["name"])}</span>{marks(x)}</a>')


def ghost(pid, layer):
    num, _, rest = pid.partition("-")
    name = rest.replace("-", " ").capitalize()
    return (f'<span class="tile ghost grain" role="img" aria-label="{e(num + " " + name + ", " + layer + ", pending, not yet on main")}">'
            f'<span class="no"><span>{e(num)}</span><span>pending</span></span><span class="sym">?</span><span class="nm">{e(name)}</span></span>')


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def ev_row(ev, known):
    parts = ", ".join(ev["parts"])
    status = ev["status"]
    if status == "pending" and ev["parts"] and all(pid in known for pid in ev["parts"]):
        status = "landed since"
    refs = "".join(f'<li><code>{e(r.get("type", ""))}:{e(r.get("ref", ""))}</code>{" " + e(r["note"]) if r.get("note") else ""}</li>' for r in ev["evidence"])
    return (f'<tr data-kind="{e(ev["kind"])}"><td>{e(ev["date"])}</td><td>{e(KIND_LABEL[ev["kind"]])}</td>'
            f'<td><code>{e(parts)}</code></td><td>{e(ev["trigger"])}</td><td><ul>{refs}</ul></td>'
            f'<td><span class="chip{" pending" if status == "pending" else ""}">{e(status)}</span> <span class="chip">{e(ev["source"])}</span></td></tr>')


def render(m, els, events):
    known = {x["id"] for x in els}
    by_layer = {l: [x for x in els if x["layer"] == l] for l in LAYERS}
    ghosts = {}
    for ev in events:
        if ev["status"] == "pending":
            for pid in ev["parts"]:
                if pid not in known and not pid.startswith("template:"):
                    ghosts[pid] = ev.get("layer", "Unclassed")
    parts_only = [x for x in els if x["family"] != "template"]
    n = len(parts_only)
    fid_ct = {f: sum(1 for x in parts_only if x["earned"] == f) for f in FIDS}
    kind_ct = {k: sum(1 for ev in events if ev["kind"] == k) for k in KINDS}
    pending = sum(1 for ev in events if ev["status"] == "pending")
    last = max((ev["date"] for ev in events), default="none")
    unclassed = len(by_layer["Unclassed"])

    # Exec
    exec_ = (f'<div class="stamp"><span class="section-label">Exec stamp, computed</span>'
             f'<span class="big">{fid_ct["sharp"]} of {n} parts sharp</span>'
             f'<p>{fid_ct["sharp"]} parts have two or more pages and no exact twin. {fid_ct["degraded"]} have one consumer, '
             f'{fid_ct["grain"]} have none, and {fid_ct["moire"]} carry a rule identical to another part\'s. '
             f'{unclassed} parts have no declared layer. The ledger holds {len(events)} catalyst events, {pending} pending; the newest is dated {e(last)}.</p></div>'
             '<div class="kv">' + "".join(f'<div><b>{fid_ct[f]}</b><span>{f}</span></div>' for f in FIDS) +
             "".join(f'<div><b>{kind_ct[k]}</b><span>{e(KIND_LABEL[k])}</span></div>' for k in KINDS) + '</div>')

    # Strategic
    fams = sorted({x["family"] for x in els})
    head = "".join(f'<th class="num">{e(f)}</th>' for f in fams) + "".join(f'<th class="num">{f}</th>' for f in FIDS)
    rows = ""
    for l in LAYERS:
        xs = by_layer[l]
        rows += (f'<tr><th scope="row">{l}</th>' + "".join(f'<td class="num">{sum(1 for x in xs if x["family"] == f)}</td>' for f in fams)
                 + "".join(f'<td class="num">{sum(1 for x in xs if x["earned"] == f)}</td>' for f in FIDS) + '</tr>')
    leaders = sorted(parts_only, key=lambda x: (-x["reuse"], x["id"]))[:8]
    strat = (f'<div class="scroll" tabindex="0" role="region" aria-label="Layer by family and earned fidelity"><table><thead><tr><th>Layer</th>{head}</tr></thead><tbody>{rows}</tbody></table></div>'
             '<h2>Strongest attraction</h2><p class="note">The parts the most pages pull toward, by page count n. Attraction events in the ledger mark the commit where a part reached its second page.</p>'
             '<div class="scroll" tabindex="0" role="region" aria-label="Strongest attraction"><table><thead><tr><th>Part</th><th>Layer</th><th class="num">n</th></tr></thead><tbody>'
             + "".join(f'<tr><td><a href="#s-{e(slug(x["id"]))}">{e(x["number"])} {e(x["name"])}</a></td><td>{e(x["layer"])}</td><td class="num">{x["reuse"]}</td></tr>' for x in leaders)
             + '</tbody></table></div>')

    # Operational
    trows = ""
    for t in by_layer["Template"]:
        comp = ", ".join(t["composes"]) or "none recorded"
        trows += (f'<tr id="s-{e(slug(t["id"]))}"><td>{e(t["name"])}</td><td><code>{e(t["mode"])}</code></td><td class="num">{t["reuse"]}</td>'
                  f'<td class="num">{len(t["composes"])}</td><td><code>{e(comp)}</code></td></tr>')
    oper = ('<p class="note">Each template is a composition a page declares once. The parts listed are the ones the manifest says use it.</p>'
            '<div class="scroll" tabindex="0" role="region" aria-label="Templates and the parts they compose"><table><thead><tr><th>Template</th><th>Mode</th><th class="num">Examples</th><th class="num">Parts</th><th>Composes</th></tr></thead>'
            f'<tbody>{trows}</tbody></table></div>')

    # Tactical
    legend = ('<div class="legend"><span><b>Tile texture</b> is earned fidelity:</span><span class="sharp">sharp, n 2+ and distinct</span>'
              '<span class="degraded">degraded, n 1</span><span class="grain">grain, n 0</span><span class="moire">moire, exact twin</span>'
              '<span><b>S D G M</b> marks: the states a part declares it can render (solid = declared).</span><span>Dashed tile: pending, named by a ledger event, not yet on main.</span></div>')
    periods = ""
    for l in LAYERS:
        xs = [x for x in by_layer[l] if x["family"] != "template"] if l != "Template" else by_layer[l]
        gs = [ghost(pid, lay) for pid, lay in sorted(ghosts.items()) if lay == l]
        if not xs and not gs:
            continue
        src = sorted({x["layer_source"] for x in xs})
        periods += (f'<section class="period" aria-label="{l}"><h3>{l}<small>{len(xs)} element{"s" if len(xs) != 1 else ""}'
                    f'{"; " + ", ".join(src) if src else ""}</small></h3><div class="tiles">{"".join(tile(x) for x in xs)}{"".join(gs)}</div></section>')
    tact = legend + periods

    # Surgical
    srows = ""
    for x in parts_only:
        twins = "; ".join(f'{d["rule"]} = {d["twin"]} {d["twin_rule"]} ({d["jaccard"]:.2f})' for d in x["near_duplicates"]) or "none"
        pages = ", ".join(x["pages"][:4]) + (f" and {len(x['pages']) - 4} more" if len(x["pages"]) > 4 else "") if x["pages"] else "none"
        srows += (f'<tr id="s-{e(slug(x["id"]))}"><td>{e(x["number"])}</td><td>{e(x["name"])}<br><code>{e(x["path"])}</code></td>'
                  f'<td>{e(x["layer"])}<br><small>{e(x["layer_source"])}</small></td><td><span class="chip">{e(x["earned"])}</span></td>'
                  f'<td class="num">{len(x["classes"])}</td><td>{e(twins)}</td><td>{e(pages)}</td></tr>')
    surg = ('<div class="scroll" tabindex="0" role="region" aria-label="Every part, file level"><table><thead><tr><th>No</th><th>Part and file</th><th>Layer</th><th>Earned</th>'
            f'<th class="num">Classes</th><th>Near twins (Jaccard)</th><th>Pages</th></tr></thead><tbody>{srows}</tbody></table></div>')

    sheets = [exec_, strat, oper, tact, surg]
    sheet_html = "".join(f'<section class="sheet" data-alt="{i + 1}" aria-label="{ALTS[i]} sheet"><h2>{i + 1} {ALTS[i]}</h2>{s}</section>'
                         for i, s in enumerate(sheets))
    evs = sorted(events, key=lambda ev: (ev["date"], ev["id"]), reverse=True)
    filters = '<div class="filters" role="group" aria-label="Filter events by kind"><button type="button" data-kind="all" aria-pressed="true">All ' + str(len(events)) + '</button>' + \
        "".join(f'<button type="button" data-kind="{k}" aria-pressed="false">{e(KIND_LABEL[k])} {kind_ct[k]}</button>' for k in KINDS) + '</div>'
    ledger_html = ('<section aria-labelledby="led"><h2 id="led">Catalyst ledger</h2>'
                   '<p class="note">Every event that changed the table, newest first. Derived events come from the git history of the manifest; '
                   'insights are hand-written. The file is append-only: a correction is a new line, never an edit.</p>'
                   f'{filters}<div class="scroll ev" tabindex="0" role="region" aria-label="Catalyst events"><table><thead><tr><th>Date</th><th>Kind</th><th>Parts</th><th>Trigger</th><th>Evidence</th><th>Status</th></tr></thead>'
                   f'<tbody>{"".join(ev_row(ev, known) for ev in evs)}</tbody></table></div></section>')
    cold = ('<div class="cold">'
            '<div><span class="section-label">Why</span><p>Kit parts drift: pages hand-roll shapes the kit already has, and parts sit unused. A table shows which parts have earned their place.</p></div>'
            '<div><span class="section-label">What</span><p>Every ui-kit part (atom, molecule, organism, lockup, template) as an element, rendered at the fidelity its use has earned, with a ledger of the events that changed it.</p></div>'
            '<div><span class="section-label">Why now</span><p>On 2026-11-13 four molecules were cut from the Louisville proposal into the kit. That is the first event this ledger records by hand.</p></div>'
            '<div><span class="section-label">How</span><p>Before: kit_pull.py writes the manifest. During: this page is built from it and the ledger. After: a kit commit is blocked until the page is rebuilt, and session start warns when the ledger lags git.</p></div>'
            '</div>')
    alts = '<nav class="alts" aria-label="Altitude">' + "".join(f'<button type="button" data-alt="{i + 1}" aria-pressed="false">{i + 1} {a}</button>' for i, a in enumerate(ALTS)) + '</nav>'
    tokens = read(TOKENS)
    return f"""<!DOCTYPE html>
<!-- generated by scripts/kit_periodic_table.py from {MANIFEST}, {TEMPLATES} and {LEDGER}; never hand-edit -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kit periodic table</title>
<style>
{tokens}
{grain_block()}
{CSS}</style>
</head>
<body>
<main>
<header style="display:flex;flex-direction:column;gap:12px">
<span class="section-label">ARCS ui-kit</span>
<h1>Kit periodic table</h1>
<p class="lede">{n} parts and {len(by_layer["Template"])} templates, laid out by layer, read at five altitudes. A tile's texture is the fidelity its use has earned; n is the number of pages that use it.</p>
</header>
{cold}
<p class="note"><b>How to read this:</b> pick an altitude with the bar or keys 1 to 5. Exec is one computed stamp; Surgical is every file. The catalyst ledger sits below every sheet.</p>
{alts}
{sheet_html}
{ledger_html}
<footer>Generated from <code>{MANIFEST}</code> and <code>{LEDGER}</code>. Rebuild with <code>python3 scripts/kit_periodic_table.py</code>. Earned-fidelity rules are pre-registered in the script's header.</footer>
</main>
<script>{JS}</script>
</body>
</html>
"""


def build():
    m, els = elements()
    return render(m, els, ledger())


def check():
    errs = validate(ledger())
    head = subprocess.run(("git", "show", f"HEAD:{LEDGER}"), cwd=ROOT, capture_output=True, text=True)
    if head.returncode == 0 and not append_only(head.stdout, read(LEDGER)):
        errs.append(f"{LEDGER} rewrote or reordered a committed line; the ledger is append-only (add a correcting line instead)")
    if not os.path.exists(p(OUT)) or read(OUT) != build():
        errs.append(f"{OUT} differs from what the manifest and ledger produce; run python3 scripts/kit_periodic_table.py")
    for x in errs:
        print("kit_periodic_table:", x, file=sys.stderr)
    return 1 if errs else 0


def self_test():
    good = {"id": "a", "date": "2026-11-13", "kind": "insight", "parts": [], "trigger": "t", "evidence": [{"type": "note", "ref": "x"}], "status": "landed", "source": "hand"}
    assert validate([good]) == []
    assert validate([dict(good, kind="insight", source="derived")])
    assert validate([dict(good, kind="boom")])
    assert validate([dict(good, evidence=[])])
    assert validate([good, good])
    a = json.dumps(good)
    assert append_only(a + "\n", a + "\n" + a.replace('"a"', '"b"') + "\n")
    assert not append_only(a + "\n", a.replace('"t"', '"u"') + "\n")
    assert earned({"reuse": 0}) == "grain" and earned({"reuse": 1}) == "degraded"
    assert earned({"reuse": 3, "near_duplicates": [{"jaccard": 1.0}]}) == "moire"
    assert earned({"reuse": 3, "near_duplicates": [{"jaccard": 0.9}]}) == "sharp"
    assert layer_of({"family": "kit", "number": "99", "subtitle": "Organism 99 x", "group": "Specimens"}, {}) == ("Organism", "dsCard subtitle")
    assert layer_of({"family": "react", "number": "", "subtitle": "", "group": "React"}, {})[0] == "Unclassed"
    s = symbols([{"id": "1", "name": "Fold"}, {"id": "2", "name": "Fold"}])
    assert len(set(s.values())) == 2
    page = build()
    assert chr(0x2014) not in page.replace(read(TOKENS), "")  # the inlined token file is verbatim kit text
    print("kit_periodic_table self-test: 12 checks pass")
    return 0


def main(argv):
    if argv and argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if "--self-test" in argv:
        return self_test()
    if "--check" in argv:
        return check()
    if "--behind" in argv:
        print(behind())
        return 0
    if "--sync" in argv:
        print(f"appended {sync()} derived events to {LEDGER}")
    with open(p(OUT), "w", encoding="utf-8") as f:
        f.write(build())
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
