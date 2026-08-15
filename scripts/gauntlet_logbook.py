#!/usr/bin/env python3
"""gauntlet_logbook.py — render the append-only gauntlet tape into a visual lab-notebook.

SSOT -> render: reads _STATE/gauntlet-runs.jsonl (the experiment tape) and emits a single
self-contained HTML instrument panel. Regenerate whenever a run lands; it never drifts because
it is a pure projection of the tape. The falsification ledger (hypotheses tested & overturned)
is the lab-notebook spine — the honest record of what each experiment BROKE.

ARCS FieldOS design tokens (CLAUDE.md), committed-dark instrument world (WORLD.md).
Stdlib only. Usage: python3 scripts/gauntlet_logbook.py [--out PATH]
"""
import argparse, html, json, os, sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAPE = os.path.join(ROOT, "_STATE", "gauntlet-runs.jsonl")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hypercube_sampler as hs  # for dollars() + list-price table (single source of pricing)

OPUS_BASELINE = 567_370  # the full 7-Opus self-audit gauntlet — the compression baseline
BASELINE_USD = hs.dollars("opus", OPUS_BASELINE)

# The falsification ledger — the repo-wide belief-log, an SSOT file swept from the whole monorepo
# history (commits, ADR self-audits, forensic verdicts, _PATTERNS post-mortems, red-team memory).
# The anti-survivorship record ARCS canon calls for: keep the failed welds. Rendered, not hardcoded.
LEDGER = os.path.join(ROOT, "_STATE", "falsification-ledger.jsonl")
SCOPE_ORDER = ["gauntlet", "canon", "infra", "deploy", "process", "security", "recoil", "other"]
SCOPE_LABEL = {"gauntlet": "the gauntlet engine", "canon": "canon & ADRs", "infra": "infrastructure",
               "deploy": "deploy & preview", "process": "process & controls", "security": "security",
               "recoil": "recoil / client", "other": "other"}


def load_ledger():
    if not os.path.exists(LEDGER):
        return []
    out = []
    for line in open(LEDGER, encoding="utf-8"):
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def load_runs():
    if not os.path.exists(TAPE):
        return []
    out = []
    for line in open(TAPE, encoding="utf-8"):
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def flip_split(row):
    """(up, down, undirected) from flip_detail; up = coarse missed (fine>coarse)."""
    up = down = und = 0
    det = row.get("flip_detail")
    if isinstance(det, list):
        for f in det:
            try:
                d = float(f["fine"]) - float(f["coarse"])
            except Exception:
                und += 1; continue
            if d >= 0.75: up += 1
            elif d <= -0.75: down += 1
    return up, down, und


def tokens_of(row):
    return int(row.get("total_tokens_measured") or row.get("tokens") or row.get("total_tokens") or 0)


def esc(s):
    return html.escape(str(s))


# ---- inline-SVG charts (no external libs) ----------------------------------

def bar_chart_cost(runs):
    """Horizontal token-cost bars vs the 567K Opus baseline."""
    rows = [(r.get("subject", r.get("run_id", "?")), tokens_of(r), r.get("kind", "")) for r in runs]
    rows = [r for r in rows if r[1] > 0]
    W, rowh, pad, labelw = 720, 30, 8, 210
    H = pad * 2 + rowh * (len(rows) + 1)
    maxv = max([OPUS_BASELINE] + [v for _, v, _ in rows])
    bw = W - labelw - 90
    def x(v): return labelw + bw * v / maxv
    parts = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="token cost per run" '
             f'style="width:100%;height:auto;font-family:ui-monospace,monospace">']
    # baseline marker
    bx = x(OPUS_BASELINE)
    parts.append(f'<line x1="{bx:.0f}" y1="{pad}" x2="{bx:.0f}" y2="{H-pad}" stroke="#FF4D6D" '
                 f'stroke-dasharray="3 3" stroke-width="1" opacity="0.7"/>')
    parts.append(f'<text x="{bx-4:.0f}" y="{pad+9}" text-anchor="end" fill="#FF4D6D" font-size="10">'
                 f'567K Opus gauntlet</text>')
    for i, (name, v, kind) in enumerate(rows):
        y = pad + rowh * (i + 1)
        live = kind == "engine-run"
        col = "#00F0FF" if live else "#475569"
        parts.append(f'<text x="{labelw-8}" y="{y+rowh/2+4:.0f}" text-anchor="end" fill="#e2e8f0" '
                     f'font-size="11">{esc(name[:30])}</text>')
        parts.append(f'<rect x="{labelw}" y="{y+5:.0f}" width="{x(v)-labelw:.1f}" height="{rowh-12}" '
                     f'rx="2" fill="{col}" opacity="{0.9 if live else 0.5}"/>')
        parts.append(f'<text x="{x(v)+6:.0f}" y="{y+rowh/2+4:.0f}" fill="{col}" font-size="10">'
                     f'{v//1000}K</text>')
    parts.append("</svg>")
    return "".join(parts)


def flip_chart(engine_runs):
    """Stacked up/down flip bars per engine-run — the recall(up) vs precision(down) split."""
    if not engine_runs:
        return "<p class='muted'>no engine-runs yet</p>"
    W, colw, gap, pad, base = 720, 120, 40, 30, 300
    H = base + 70
    maxp = max(int(r.get("fine_probes", 0)) for r in engine_runs) or 1
    unit = (base - 30) / maxp
    parts = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="flip direction per run" '
             f'style="width:100%;height:auto;font-family:ui-monospace,monospace">']
    x0 = pad
    for r in engine_runs:
        up, down, und = flip_split(r)
        probes = int(r.get("fine_probes", 0))
        clean = probes - up - down - und
        segs = [("clean", clean, "#1e293b"), ("down (healthy)", down, "#00FF9D"),
                ("undirected", und, "#FFD700"), ("up (recall hole)", up, "#FF4D6D")]
        y = base
        for _lbl, n, col in segs:
            h = n * unit
            if h > 0:
                parts.append(f'<rect x="{x0}" y="{y-h:.1f}" width="{colw}" height="{h:.1f}" fill="{col}"/>')
                y -= h
        subj = esc(r.get("subject", "?"))
        parts.append(f'<text x="{x0+colw/2:.0f}" y="{base+18}" text-anchor="middle" fill="#e2e8f0" '
                     f'font-size="10">{subj[:16]}</text>')
        parts.append(f'<text x="{x0+colw/2:.0f}" y="{base+32}" text-anchor="middle" fill="#64748b" '
                     f'font-size="9">{r.get("n_anchors","?")} anchors · {up}up/{down}down</text>')
        x0 += colw + gap
    # legend
    lx = pad
    for lbl, col in [("up = coarse missed (recall hole)", "#FF4D6D"),
                     ("down = fine killed false-positive (healthy)", "#00FF9D"),
                     ("clean", "#1e293b")]:
        parts.append(f'<rect x="{lx}" y="{H-14}" width="10" height="10" fill="{col}"/>')
        parts.append(f'<text x="{lx+14}" y="{H-5}" fill="#94a3b8" font-size="10">{esc(lbl)}</text>')
        lx += len(lbl) * 6.0 + 34
    parts.append("</svg>")
    return "".join(parts)


# ---- page -------------------------------------------------------------------

def render(runs):
    engine = [r for r in runs if r.get("kind") == "engine-run"]
    total_live = sum(tokens_of(r) for r in engine)
    best = min((tokens_of(r) for r in engine), default=0)
    ratio = f"{OPUS_BASELINE / best:.1f}x" if best else "—"

    # capital: priced straight from each engine-run's cost_breakdown on the tape (SSOT).
    priced_runs = [r for r in engine if r.get("total_usd") is not None]
    any_estimate = any(sp.get("priced") == "estimate"
                       for r in priced_runs for sp in (r.get("cost_breakdown") or []))
    est_note = ("An <b>est</b> row was run via the Agent tool, which reports only a token total, so its "
                "input/output split is estimated (~5% output); an API-path run records the exact split "
                "and prices to the cent." if any_estimate else
                "Every row carries an exact input/output split &mdash; priced to the cent.")
    cheapest_usd = min((r["total_usd"] for r in priced_runs), default=0)
    dollar_x = BASELINE_USD / cheapest_usd if cheapest_usd else 0
    first_usd = priced_runs[0]["total_usd"] if priced_runs else 0
    monthly_engine = 1000 * first_usd
    monthly_base = 1000 * BASELINE_USD
    cost_rows = [
        f'<tr class="base"><td>full 7-Opus gauntlet</td>'
        f'<td class="mono num">{OPUS_BASELINE//1000}K</td>'
        f'<td class="mono num">${BASELINE_USD:.2f}</td>'
        f'<td class="mono num">1.0&times;</td><td class="mono num">1.0&times;</td></tr>']
    for r in priced_runs:
        usd = r["total_usd"]; toks = tokens_of(r)
        tiers = "+".join(sp["model"] for sp in (r.get("cost_breakdown") or []))
        exact = all(sp.get("priced") == "exact" for sp in (r.get("cost_breakdown") or []))
        badge = "" if exact else ' <span class="dim">est</span>'
        cost_rows.append(
            f'<tr class="live"><td>{esc(r.get("subject","?"))} '
            f'<span class="dim">{esc(tiers)}</span></td>'
            f'<td class="mono num">{toks//1000}K</td>'
            f'<td class="mono num cyan">${usd:.3f}{badge}</td>'
            f'<td class="mono num">{OPUS_BASELINE/toks:.1f}&times;</td>'
            f'<td class="mono num green">{BASELINE_USD/usd:.1f}&times;</td></tr>')

    # run ledger rows
    run_rows = []
    for r in runs:
        live = r.get("kind") == "engine-run"
        up, down, und = flip_split(r)
        flip = f'<span class="up">{up}&uarr;</span> / <span class="down">{down}&darr;</span>' if live else "—"
        agents = r.get("n_anchors") if live else r.get("agents", "—")
        acol = "anchors" if live else "agents"
        run_rows.append(
            f'<tr class="{"live" if live else "base"}">'
            f'<td class="mono">{esc(r.get("run_id","?"))}</td>'
            f'<td>{esc(r.get("subject","?"))}</td>'
            f'<td><span class="chip">{esc(r.get("kind","?"))}</span></td>'
            f'<td class="mono">{esc(r.get("model","?"))}</td>'
            f'<td class="mono num">{agents} <span class="dim">{acol}</span></td>'
            f'<td class="mono num">{tokens_of(r)//1000}K</td>'
            f'<td class="mono num">{flip}</td>'
            f'</tr>')

    ledger = load_ledger()
    n_canon = sum(1 for f in ledger if f.get("canon"))
    campaign_usd = sum(r["total_usd"] for r in runs if r.get("total_usd") is not None)
    by_scope = {}
    for f in ledger:
        by_scope.setdefault(f.get("scope", "other"), []).append(f)
    fcards = []
    for scope in SCOPE_ORDER:
        items = by_scope.get(scope)
        if not items:
            continue
        fcards.append(
            f'<div class="scopehdr">{esc(SCOPE_LABEL.get(scope, scope))}'
            f'<span class="scopen">{len(items)}</span></div>')
        for f in items:
            conf = f.get("confidence", "")
            refs = f.get("refs") or []
            ref_chips = "".join(
                f'<span class="ref {"ref-canon" if r.startswith(("ADR-","DEWY:","tao-")) else ""}">{esc(r)}</span>'
                for r in refs)
            canon_badge = '<span class="canon-tag">canon</span>' if f.get("canon") else \
                          '<span class="nocanon-tag">patterns/memory</span>'
            fcards.append(
                f'<article class="fcard">'
                f'<div class="fnum">{esc(f.get("id", ""))}</div>'
                f'<div class="fbody">'
                f'<p class="claim"><span class="lbl">believed</span>{esc(f["claim"])}</p>'
                f'<p class="test"><span class="lbl">test</span>{esc(f["test"])}</p>'
                f'<p class="delta"><span class="verdict">{esc(f["verdict"])}</span>{esc(f["delta"])}</p>'
                f'<p class="fix"><span class="lbl">propagated</span>{esc(f["fix"])}</p>'
                f'<p class="fmeta">{esc(f.get("ts",""))} &middot; {esc(conf)} confidence '
                f'{canon_badge} {ref_chips}</p>'
                f'</div></article>')

    return f"""<title>Hypercube Gauntlet &mdash; Experiment Logbook</title>
<style>
:root {{
  --bg:#020408; --surface:#0d1117; --surface2:#0b1220; --border:#1e293b;
  --text:#e2e8f0; --muted:#94a3b8; --dim:#64748b; --faint:#475569;
  --cyan:#00F0FF; --green:#00FF9D; --gold:#FFD700; --red:#FF4D6D;
  --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:
  radial-gradient(1200px 600px at 50% -10%, #071019 0%, var(--bg) 60%);
  color:var(--text); font-family:var(--sans); line-height:1.5;
  -webkit-font-smoothing:antialiased; }}
.wrap {{ max-width:940px; margin:0 auto; padding:48px 24px 80px; }}
.eyebrow {{ font-family:var(--mono); font-size:11px; letter-spacing:.22em; text-transform:uppercase;
  color:var(--cyan); opacity:.85; margin:0 0 14px; }}
h1 {{ font-size:32px; line-height:1.1; margin:0 0 10px; font-weight:650; text-wrap:balance;
  letter-spacing:-.01em; }}
.thesis {{ color:var(--muted); font-size:15px; max-width:62ch; margin:0 0 34px; }}
.thesis b {{ color:var(--text); font-weight:600; }}
.readout {{ display:flex; gap:14px; flex-wrap:wrap; margin:0 0 44px; }}
.stat {{ background:linear-gradient(180deg,var(--surface),var(--surface2));
  border:1px solid var(--border); border-radius:10px; padding:16px 20px; min-width:150px; flex:1; }}
.stat .k {{ font-family:var(--mono); font-size:11px; letter-spacing:.12em; text-transform:uppercase;
  color:var(--dim); margin:0 0 6px; }}
.stat .v {{ font-family:var(--mono); font-size:26px; font-weight:600; font-variant-numeric:tabular-nums; }}
.stat .v.cyan {{ color:var(--cyan); }} .stat .v.green {{ color:var(--green); }}
.stat .sub {{ font-size:11px; color:var(--dim); margin-top:4px; }}
section {{ margin:0 0 46px; }}
h2 {{ font-family:var(--mono); font-size:12px; letter-spacing:.18em; text-transform:uppercase;
  color:var(--muted); border-bottom:1px solid var(--border); padding-bottom:9px; margin:0 0 20px;
  font-weight:600; display:flex; justify-content:space-between; align-items:baseline; }}
h2 .h2note {{ color:var(--dim); letter-spacing:.02em; text-transform:none; font-size:11px; }}
.panel {{ background:var(--surface); border:1px solid var(--border); border-radius:10px;
  padding:20px; overflow-x:auto; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th {{ font-family:var(--mono); font-size:10px; letter-spacing:.12em; text-transform:uppercase;
  color:var(--dim); text-align:left; padding:0 12px 10px; font-weight:500; white-space:nowrap; }}
td {{ padding:9px 12px; border-top:1px solid var(--border); vertical-align:middle; }}
tr.base td {{ color:var(--faint); }}
tr.live td {{ color:var(--text); }}
.mono {{ font-family:var(--mono); }}
.num {{ text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }}
.dim {{ color:var(--dim); font-size:10px; }}
.chip {{ font-family:var(--mono); font-size:10px; padding:2px 7px; border-radius:20px;
  border:1px solid var(--border); color:var(--muted); white-space:nowrap; }}
tr.live .chip {{ border-color:rgba(0,240,255,.35); color:var(--cyan); }}
.up {{ color:var(--red); }} .down {{ color:var(--green); }}
.charts {{ display:grid; gap:20px; }}
.fledger {{ display:grid; gap:14px; }}
.fcard {{ display:flex; gap:16px; background:var(--surface); border:1px solid var(--border);
  border-left:2px solid var(--red); border-radius:10px; padding:18px 20px; }}
.fnum {{ font-family:var(--mono); font-size:13px; font-weight:600; color:var(--red);
  padding-top:1px; }}
.fbody {{ flex:1; }}
.fbody p {{ margin:0 0 7px; font-size:13px; }}
.fbody p:last-child {{ margin-bottom:0; }}
.lbl {{ font-family:var(--mono); font-size:9px; letter-spacing:.14em; text-transform:uppercase;
  color:var(--dim); display:inline-block; width:78px; }}
.claim {{ color:var(--muted); }}
.test {{ color:var(--muted); }}
.delta {{ color:var(--text); }}
.verdict {{ font-family:var(--mono); font-size:10px; letter-spacing:.1em; color:var(--red);
  border:1px solid rgba(255,77,109,.4); border-radius:4px; padding:1px 6px; margin-right:10px; }}
.fix {{ color:var(--green); }} .fix .lbl {{ color:var(--dim); }}
.scopehdr {{ font-family:var(--mono); font-size:11px; letter-spacing:.14em; text-transform:uppercase;
  color:var(--cyan); opacity:.9; margin:22px 0 4px; display:flex; align-items:center; gap:8px; }}
.scopehdr:first-child {{ margin-top:0; }}
.scopen {{ font-size:10px; color:var(--dim); border:1px solid var(--border); border-radius:20px;
  padding:1px 7px; }}
.fmeta {{ font-family:var(--mono); font-size:10px; color:var(--dim); margin-top:10px !important;
  display:flex; flex-wrap:wrap; gap:6px; align-items:center; }}
.canon-tag {{ color:var(--green); border:1px solid rgba(0,255,157,.35); border-radius:4px; padding:0 5px; }}
.nocanon-tag {{ color:var(--dim); border:1px solid var(--border); border-radius:4px; padding:0 5px; }}
.ref {{ color:var(--muted); border:1px solid var(--border); border-radius:4px; padding:0 5px; }}
.ref-canon {{ color:var(--cyan); border-color:rgba(0,240,255,.3); }}
.costnote {{ color:var(--muted); font-size:12.5px; margin:16px 0 0; max-width:70ch; line-height:1.55; }}
.costnote b {{ color:var(--text); font-weight:600; }}
td.cyan {{ color:var(--cyan); }} td.green {{ color:var(--green); }}
footer {{ color:var(--dim); font-size:11px; font-family:var(--mono); border-top:1px solid var(--border);
  padding-top:16px; margin-top:10px; }}
@media (max-width:560px) {{ h1{{font-size:25px}} .lbl{{width:64px}} }}
</style>

<div class="wrap">
  <p class="eyebrow">ARCS &middot; Hypercube Gauntlet</p>
  <h1>Experiment Logbook</h1>
  <p class="thesis">The append-only tape (<span class="mono">_STATE/gauntlet-runs.jsonl</span>),
  rendered. Every row is one gauntlet run; the spine of this notebook is the
  <b>falsification ledger</b> &mdash; the hypotheses each experiment <b>broke</b>. The engine
  earns its keep by finding the same faults as the full 567K Opus gauntlet for a fraction of the
  spend, and by falsifying its own designs on the tape.</p>

  <div class="readout">
    <div class="stat"><p class="k">cost / audit</p><p class="v cyan">${cheapest_usd:.2f}</p>
      <p class="sub">vs ${BASELINE_USD:.2f} for the full 7-Opus gauntlet</p></div>
    <div class="stat"><p class="k">dollar compression</p><p class="v green">{dollar_x:.1f}&times;</p>
      <p class="sub">exceeds {ratio} token compression &mdash; tier-routing</p></div>
    <div class="stat"><p class="k">falsifications logged</p><p class="v">{len(ledger)}</p>
      <p class="sub">{n_canon} canon-linked (ADR/DEWY/Tao) &middot; swept from inception</p></div>
  </div>

  <section>
    <h2>Capital <span class="h2note">real dollars at Anthropic list price, uncached</span></h2>
    <div class="panel"><table>
      <thead><tr><th>run</th><th class="num">tokens</th><th class="num">real $</th>
        <th class="num">token &times;</th><th class="num">dollar &times;</th></tr></thead>
      <tbody>{"".join(cost_rows)}</tbody>
    </table>
    <p class="costnote"><b>Campaign total &mdash; ${campaign_usd:.2f}</b> is the real capital spent across
    <b>all</b> metered runs on the tape (the 3 cost-probe workflows that discovered the cost model +
    the 3 live cheap&rarr;fine cycles). The self-audit alone (the 567K Opus gauntlet) was ${BASELINE_USD:.2f}
    of it &mdash; the rest of the campaign ran for ${campaign_usd - BASELINE_USD:.2f}.</p>
    <p class="costnote">The <b>dollar</b> compression beats the <b>token</b> compression because the
    engine tier-routes &mdash; a cheap Haiku coarse pass ($1/$5 per Mtok) and a Sonnet fine pass
    ($3/$15) against a 7&times;-Opus baseline ($5/$25). At <b>1,000 audits/month</b> that is
    <b>${monthly_engine:,.0f}</b> vs <b>${monthly_base:,.0f}</b>. Spend is input-dominated (the floor
    is system-prompt + tool schemas + subject-read), so prompt-caching the subject-read cuts it
    further. Each row is priced from its own <b>per-spawn cost breakdown on the tape</b> (list price,
    no batch/caching discount). {est_note}</p>
    </div>
  </section>

  <section>
    <h2>Falsification ledger <span class="h2note">what each experiment broke</span></h2>
    <div class="fledger">{"".join(fcards)}</div>
  </section>

  <section>
    <h2>Run ledger <span class="h2note">the tape, newest concepts last</span></h2>
    <div class="panel"><table>
      <thead><tr><th>run</th><th>subject</th><th>kind</th><th>model</th><th>scale</th>
        <th class="num">tokens</th><th class="num">flips &uarr;/&darr;</th></tr></thead>
      <tbody>{"".join(run_rows)}</tbody>
    </table></div>
  </section>

  <section>
    <h2>Cost <span class="h2note">measured tokens vs the Opus baseline</span></h2>
    <div class="panel charts">{bar_chart_cost(runs)}</div>
  </section>

  <section>
    <h2>Flip direction <span class="h2note">recall holes (up) vs precision filtering (down)</span></h2>
    <div class="panel charts">{flip_chart(engine)}</div>
  </section>

  <footer>Rendered from the tape by scripts/gauntlet_logbook.py · SSOT&rarr;render, regenerates on
  every run · committed-dark per WORLD.md instrument world</footer>
</div>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "_ARTIFACTS", "gauntlet-logbook.html"))
    a = ap.parse_args()
    runs = load_runs()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(render(runs))
    print(f"rendered {len(runs)} runs -> {a.out}")


if __name__ == "__main__":
    main()
