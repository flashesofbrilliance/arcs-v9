#!/usr/bin/env python3
"""warroom_board.py — sovereign projection service: the instrument board.

Second instance of the sovereign-projection-services pattern (pilot: honest-resume
ladder). Contract per the seed:
  - independently invokable (stdlib only, no network, one command)
  - owns its SSOT slice read-only (each source is an ADAPTER; adding an
    instrument = one adapter entry — services snap together, nothing entangles)
  - emits a typed print: the gated HTML room + a .print.json sidecar carrying
    the SPARK PLUG (germination block: what this print enables next)

Usage:  python3 scripts/warroom_board.py            # writes runtime/warroom/gauntlet.html
        python3 scripts/warroom_board.py --out X    # override output path
Served at /warroom/gauntlet (Auth.js + ADMIN_EMAILS, prod fail-closed, noindex).
"""
import json, re, sys, html, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "runtime/warroom/gauntlet.html"

# ---------------------------------------------------------------- adapters ---
# Each adapter: name, path, parse(rows)->dict of typed fields. Read-only.
# To snap a new instrument onto the board, append one adapter and one section
# renderer keyed by its name. Nothing else changes.

def _load(path):
    p = ROOT / path
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]

SEV_RE = re.compile(r"(\d+)\s+pathogen[^,]*,\s*(\d+)\s+crack[^,]*,\s*(\d+)\s+nit", re.I)
REJ_RE = re.compile(r"(\d+)\s+over-?flags?\s+rejected", re.I)

def adapt_gauntlet(rows):
    runs = []
    for r in rows:
        finding = r.get("finding") or ""
        m = SEV_RE.search(finding)
        rej = REJ_RE.search(finding)
        runs.append({
            "ts": r.get("ts", ""), "kind": r.get("kind", ""), "subject": r.get("subject", ""),
            "agents": r.get("agents"), "tokens": r.get("tokens"),
            "sev": {"pathogen": int(m.group(1)), "crack": int(m.group(2)), "nit": int(m.group(3))} if m else None,
            "rejected": int(rej.group(1)) if rej else None,
            "finding": finding, "gates": r.get("gates") or "", "outcome": r.get("outcome") or "",
        })
    runs.sort(key=lambda r: r["ts"], reverse=True)
    return runs

def adapt_falsifications(rows):
    rows = sorted(rows, key=lambda r: r["ts"])
    return rows

SOURCES = [
    {"name": "gauntlet-runs", "path": "_STATE/gauntlet-runs.jsonl", "adapt": adapt_gauntlet},
    {"name": "falsification-ledger", "path": "_STATE/falsification-ledger.jsonl", "adapt": adapt_falsifications},
]

# ---------------------------------------------------------------- renderers --
E = html.escape
SCOPE_COLORS = {"canon": "#00F0FF", "infra": "#e3c65a", "process": "#e2e8f0", "gauntlet": "#FF4D6D",
                "deploy": "#3fb950", "security": "#d0546b", "recoil": "#C9A227"}

def strip_bar(sev, rejected):
    total = sum(sev.values()) or 1
    seg = lambda n, c: (f'<span style="flex:{n};background:{c}"></span>' if n else "")
    rej = f'<span class="rej">{rejected} over-flags rejected by the verifier</span>' if rejected else ""
    return (f'<div class="sevrow"><div class="sevbar">'
            f'{seg(sev["pathogen"], "#FF4D6D")}{seg(sev["crack"], "#C9A227")}{seg(sev["nit"], "#475569")}'
            f'</div><span class="sevlab">{sev["pathogen"]} pathogen &middot; {sev["crack"]} crack &middot; {sev["nit"]} nit</span>{rej}</div>')

def render_runs(runs):
    cards = []
    for r in runs:
        meta = " &middot; ".join(x for x in [E(r["ts"]), E(r["kind"]),
                f'{r["agents"]} agents' if r["agents"] else "", f'{r["tokens"]:,} tok' if r["tokens"] else ""] if x)
        body = strip_bar(r["sev"], r["rejected"]) if r["sev"] else ""
        finding = E(r["finding"][:260]) + ("&hellip;" if len(r["finding"]) > 260 else "")
        cards.append(f'''<div class="card">
  <div class="cm">{meta}</div>
  <div class="ct">{E(r["subject"])}</div>
  {body}
  <div class="cf">{finding}</div>
</div>''')
    return "\n".join(cards)

def render_ledger(rows):
    ticks = "".join(
        f'<span class="tick" style="background:{SCOPE_COLORS.get(r["scope"], "#64748b")}" title="{E(r["id"])} {E(r["ts"])} [{E(r["scope"])}] {E(r["claim"][:120])}"></span>'
        for r in rows)
    legend = " ".join(f'<span class="lg"><span class="dot" style="background:{c}"></span>{s}</span>'
                      for s, c in SCOPE_COLORS.items())
    latest = "\n".join(
        f'<div class="frow"><span class="fid">{E(r["id"])}</span><span class="fts">{E(r["ts"])}</span>'
        f'<span class="fsc" style="color:{SCOPE_COLORS.get(r["scope"], "#64748b")}">{E(r["scope"])}</span>'
        f'<span class="fcl">{E(r["claim"][:150])}</span></div>' for r in rows[::-1][:8])
    return ticks, legend, latest

def main():
    out = OUT
    if "--out" in sys.argv:
        out = pathlib.Path(sys.argv[sys.argv.index("--out") + 1])
    data = {s["name"]: s["adapt"](_load(s["path"])) for s in SOURCES}
    runs, ledger = data["gauntlet-runs"], data["falsification-ledger"]
    now = datetime.date.today().isoformat()

    n_sev = [r for r in runs if r["sev"]]
    tot_agents = sum(r["agents"] or 0 for r in runs)
    tot_tokens = sum(r["tokens"] or 0 for r in runs)
    ticks, legend, latest = render_ledger(ledger)
    srcrows = "\n".join(
        f'<div class="frow"><span class="fid">{E(s["name"])}</span><span class="fcl mono">{E(s["path"])}</span>'
        f'<span class="fts">{len(data[s["name"]])} rows</span></div>' for s in SOURCES)

    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow"><title>Instrument Board</title>
<style>
  :root{{color-scheme:dark;--bg:#020408;--surface:#0d1117;--surface2:#0a0f16;--border:#1e293b;
    --text:#e2e8f0;--muted:#64748b;--dimmed:#475569;--cyan:#00F0FF;--gold:#C9A227;--red:#FF4D6D;
    --sans:"Inter",system-ui,-apple-system,sans-serif;--mono:ui-monospace,"SF Mono",Menlo,monospace}}
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{background:var(--bg);color:var(--text);font-family:var(--sans);line-height:1.5;padding:56px 24px 72px;-webkit-font-smoothing:antialiased}}
  .wrap{{max-width:760px;margin:0 auto}}
  .ey{{font-family:var(--mono);font-size:10.5px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--dimmed)}}
  h1{{font-weight:800;letter-spacing:-.02em;font-size:34px;margin:12px 0 6px}}
  .sub{{color:var(--muted);font-size:14px;margin-bottom:24px}}
  .stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:9px;margin-bottom:28px}}
  .st{{border:1px solid var(--border);border-radius:11px;background:var(--surface);padding:12px 15px}}
  .st .v{{font-size:22px;font-weight:800}}
  .st .l{{font-family:var(--mono);font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--dimmed);margin-top:2px}}
  h2{{font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--dimmed);margin:30px 0 12px}}
  .card{{border:1px solid var(--border);border-radius:11px;background:var(--surface);padding:14px 17px;margin-bottom:10px}}
  .cm{{font-family:var(--mono);font-size:10.5px;color:var(--dimmed);letter-spacing:.04em}}
  .ct{{font-weight:650;font-size:15.5px;margin:3px 0 8px}}
  .sevrow{{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:8px}}
  .sevbar{{display:flex;gap:2px;height:8px;flex:1 1 180px;min-width:140px;border-radius:4px;overflow:hidden;background:rgba(255,255,255,.05)}}
  .sevbar span{{display:block;border-radius:2px}}
  .sevlab{{font-family:var(--mono);font-size:10.5px;color:var(--muted);white-space:nowrap}}
  .rej{{font-family:var(--mono);font-size:10.5px;color:var(--cyan);white-space:nowrap}}
  .cf{{color:var(--muted);font-size:13px;line-height:1.55}}
  .ticks{{display:flex;gap:3px;flex-wrap:wrap;margin:4px 0 10px}}
  .tick{{width:9px;height:22px;border-radius:2px;display:block;opacity:.9}}
  .legend{{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:14px}}
  .lg{{font-family:var(--mono);font-size:10px;color:var(--muted);display:flex;align-items:center;gap:5px}}
  .lg .dot{{width:8px;height:8px;border-radius:2px;display:inline-block}}
  .frow{{display:flex;gap:12px;align-items:baseline;padding:7px 0;border-top:1px solid rgba(255,255,255,.05);font-size:12.5px}}
  .fid{{font-family:var(--mono);font-weight:700;color:var(--text);min-width:34px}}
  .fts{{font-family:var(--mono);color:var(--dimmed);white-space:nowrap}}
  .fsc{{font-family:var(--mono);min-width:64px}}
  .fcl{{color:var(--muted);flex:1}}
  .mono{{font-family:var(--mono);font-size:11.5px}}
  .foot{{margin-top:30px;font-family:var(--mono);font-size:10px;letter-spacing:.06em;color:var(--dimmed)}}
</style></head><body>
<div class="wrap">
  <div class="ey">ARCS &middot; private &middot; sovereign projection</div>
  <h1>Instrument Board</h1>
  <p class="sub">Every adversarial pass the shop has run, projected from its own ledgers. Regenerate: <span class="mono">python3 scripts/warroom_board.py</span></p>

  <div class="stats">
    <div class="st"><div class="v">{len(runs)}</div><div class="l">gauntlet runs</div></div>
    <div class="st"><div class="v">{tot_agents}</div><div class="l">agents fielded</div></div>
    <div class="st"><div class="v">{tot_tokens/1e6:.1f}M</div><div class="l">tokens burned</div></div>
    <div class="st"><div class="v">{len(ledger)}</div><div class="l">claims falsified</div></div>
  </div>

  <h2>Gauntlet runs &middot; newest first</h2>
  {render_runs(runs)}

  <h2>Falsification ledger &middot; {len(ledger)} claims killed, one tick each</h2>
  <div class="ticks">{ticks}</div>
  <div class="legend">{legend}</div>
  {latest}

  <h2>Snapped-on sources</h2>
  {srcrows}

  <div class="foot">generated {now} &middot; runtime/warroom/gauntlet.html &middot; admin-gated &middot; noindex &middot; severity strips parse only structured findings; prose-only runs show text</div>
</div>
</body></html>'''
    out.write_text(page)

    # The spark plug: typed print sidecar (germination block, seed-bank schema).
    print_json = {
        "print": "instrument-board", "service": "scripts/warroom_board.py", "ts": now,
        "output": str(out.relative_to(ROOT)), "route": "/warroom/gauntlet",
        "sources": [{"name": s["name"], "path": s["path"], "rows": len(data[s["name"]])} for s in SOURCES],
        "germination": {
            "soil": ["any new adversarial instrument that writes a JSONL ledger"],
            "triggers": ["a third instrument ledger appears -> add one adapter, re-run",
                          "gauntlet-runs grows structured severity fields -> retire the prose regex",
                          "a second tenant wants a board -> extract adapters, pollinate the class"],
            "care": ["re-run after every gauntlet; the board is stateless and cheap",
                      "keep findings machine-parseable: state 'N pathogen, N crack, N nit' and 'N over-flags rejected' in every new run row"],
        },
    }
    out.with_suffix(".print.json").write_text(json.dumps(print_json, indent=1))
    print(f"wrote {out.relative_to(ROOT)} + sidecar ({len(runs)} runs, {len(ledger)} falsifications)")

if __name__ == "__main__":
    main()
