#!/usr/bin/env python3
"""
recoil_brief.py -- single-source-of-truth generator for a recoil brief.

Reads one canonical engagement JSON and projects an AUDIENCE view:
  internal  = full (beliefs, next-steps, kinematic derivatives, opportunity NCI)
  external  = redacted (only audience:"both" fields survive)

The redaction is mechanical, not a manual discipline: any field/row tagged
audience:"internal" is dropped for the external projection. Kinematics are
COMPUTED (via operators/arcs_kinematics.py), never hand-typed, so the numbers
are reproducible from source.

Usage:
  python scripts/recoil_brief.py --data runtime/recoil/generated/<id>.json \
      --audience internal|external [--format md|json] [--set key=value ...]

Pass-through:
  --set meta.foo=bar   override any dotted meta key at generation time
"""
import argparse, json, os, sys

OPERATORS = os.path.join(os.path.dirname(__file__), "..", "operators")


def load(path):
    with open(path) as f:
        return json.load(f)


def apply_overrides(data, sets):
    """Pass-through --set key.path=value overrides (best-effort, meta scope)."""
    for kv in sets or []:
        if "=" not in kv:
            continue
        path, val = kv.split("=", 1)
        node = data
        keys = path.split(".")
        for k in keys[:-1]:
            node = node.setdefault(k, {})
        node[keys[-1]] = val
    return data


def visible(item, audience):
    """A field/row is visible if audience is internal, or it is tagged 'both'."""
    if audience == "internal":
        return True
    return item.get("audience") == "both"


def _grad(f, dt=1.0):
    """Central-difference gradient (edge_order=1), the np.gradient behavior, in stdlib."""
    n = len(f)
    if n < 2:
        return [0.0] * n
    g = [0.0] * n
    g[0] = (f[1] - f[0]) / dt
    g[-1] = (f[-1] - f[-2]) / dt
    for i in range(1, n - 1):
        g[i] = (f[i + 1] - f[i - 1]) / (2.0 * dt)
    return g


def _derivatives(pts, dt):
    """D1-D3. Uses the canonical arcs_kinematics.py engine if numpy is present,
    else a pure-stdlib fallback. Both produce identical D1-D3 (same central difference),
    so the tool has ZERO required third-party deps."""
    try:
        import numpy as np  # noqa: F401
        sys.path.insert(0, os.path.abspath(OPERATORS))
        from arcs_kinematics import KinematicManifold
        km = KinematicManifold(np.array(pts, dtype=float), dt=dt)
        v = [float(x) for x in km.velocity()]
        a = [float(x) for x in km.acceleration()]
        j = [float(x) for x in km.jerk()]
        return v, a, j, "arcs_kinematics.py v1.3 (numpy)"
    except Exception:
        v = _grad(pts, dt); a = _grad(v, dt); j = _grad(a, dt)
        return v, a, j, "stdlib finite-difference"


def compute_kinematics(series_block):
    """Compute D1-D3 per series. Reproducible; canonical engine when available, else stdlib."""
    dt = series_block.get("dt", 1.0)
    out = []
    engine = "stdlib finite-difference"
    for s in series_block["series"]:
        pts = [float(x) for x in s["points"]]
        v, a, j, engine = _derivatives(pts, dt)
        out.append({
            "key": s["key"], "label": s["label"], "audience": s.get("audience", "both"),
            "points": s["points"],
            "D1_velocity": {"peak": round(max(abs(x) for x in v), 3), "terminal": round(v[-1], 3)},
            "D2_acceleration": {"terminal": round(a[-1], 3)},
            "D3_jerk": {"terminal": round(j[-1], 3)},
        })
    n = len(series_block["series"][0]["points"]) if series_block["series"] else 0
    note = (f"n={n} points -> D1-D2 valid, D3 marginal, D4+ undersampled. engine={engine}. "
            "D5-D12 = coherence-operator zone (noise past ~D4 per arcs_kinematics.py "
            "header); NOT reported as derivatives.")
    return out, note


def project(data, audience):
    """Mechanically drop internal-only content for the requested audience."""
    dropped = []
    out = {"meta": data["meta"], "audience": audience}

    # beliefs
    keep_b = [b for b in data.get("beliefs", []) if visible(b, audience)]
    dropped += [f"belief:{b['id']}" for b in data.get("beliefs", []) if not visible(b, audience)]
    if keep_b:
        out["beliefs"] = keep_b

    # opportunity
    if visible(data.get("opportunity", {}), audience):
        out["opportunity"] = data.get("opportunity")
    elif "opportunity" in data:
        dropped.append("opportunity.nci")

    # next steps
    keep_n = [s for s in data.get("next_steps", []) if visible(s, audience)]
    dropped += [f"next_step:{s['owner']}" for s in data.get("next_steps", []) if not visible(s, audience)]
    if keep_n:
        out["next_steps"] = keep_n

    # kinematics: trajectories always cross; derivatives are internal-only
    kin, note = compute_kinematics(data["kinematic_series"])
    if audience == "internal":
        out["kinematics"] = {"series": kin, "note": note}
    else:
        out["kinematics"] = {"series": [{"key": s["key"], "label": s["label"], "points": s["points"]}
                                        for s in kin if s["audience"] == "both"]}
        dropped.append("kinematic derivatives (D1-D3)")

    out["_redaction_report"] = {"audience": audience, "dropped_count": len(dropped), "dropped": dropped}
    return out


def render_md(p):
    L = [f"# Recoil Brief -- {p['meta']['counterpart']} ({p['audience']})", ""]
    if "beliefs" in p:
        L += ["## Belief Log (confidence x conviction)", "",
              "| id | claim | inf | conf | conviction | verdict |",
              "|----|-------|-----|------|------------|---------|"]
        for b in p["beliefs"]:
            c = b["confidence"]
            cs = f"{c[0] if c[0] is not None else '--'}->{c[1]}"
            L.append(f"| {b['id']} | {b['claim']} | {b['inference']} | {cs} | {b['conviction']} | {b['verdict']} |")
        L.append("")
    if "opportunity" in p:
        o = p["opportunity"]
        L += [f"**Opportunity NCI:** {o['nci_prior']} -> {o['nci_post']}  "
              f"({o['y_state']}/{o['topology']})", ""]
    L += ["## Kinematics (measured)", ""]
    for s in p["kinematics"]["series"]:
        if "D1_velocity" in s:
            L.append(f"- **{s['label']}**: D1 peak {s['D1_velocity']['peak']} / "
                     f"term {s['D1_velocity']['terminal']} | D2 term {s['D2_acceleration']['terminal']} | "
                     f"D3 term {s['D3_jerk']['terminal']}")
        else:
            L.append(f"- **{s['label']}**: trajectory {s['points']} (derivatives redacted)")
    if "note" in p["kinematics"]:
        L += ["", f"> {p['kinematics']['note']}"]
    if "next_steps" in p:
        L += ["", "## Next Steps"]
        for s in p["next_steps"]:
            L.append(f"- [{s['owner']}] {s['text']}")
    r = p["_redaction_report"]
    L += ["", f"---", f"_Redaction: {r['dropped_count']} field(s) dropped for '{r['audience']}' -> "
          f"{', '.join(r['dropped']) or 'none'}_"]
    return "\n".join(L)


# ---------------------------------------------------------------------------
# HTML renderer -- generates the full styled page FROM the SSOT (audience-projected)
# ---------------------------------------------------------------------------
CSS = """:root{--bg:#020408;--surface:#0d1117;--surface2:#0a0f16;--border:#1e293b;--text:#e2e8f0;--muted:#94a3b8;--dimmed:#64748b;--cyan:#00F0FF;--green:#00FF9D;--gold:#FFD700;--red:#FF4D6D;--mono:ui-monospace,'SF Mono','Fira Code','Courier New',monospace;--sans:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--text);font-family:var(--sans);padding:48px 24px 96px;line-height:1.62;}
.page{max-width:660px;margin:0 auto;display:flex;flex-direction:column;gap:22px;}
.eyebrow{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;color:var(--dimmed);}
h1{font-size:26px;font-weight:700;letter-spacing:-0.02em;margin-top:8px;}
.sub{font-size:14px;color:var(--muted);margin-top:6px;}
.rule{height:1px;background:linear-gradient(90deg,transparent,var(--cyan),transparent);opacity:0.3;margin:4px 0;}
.sec-label{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;color:var(--dimmed);margin:10px 2px -6px;}
.card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px 22px;}
.card h2{font-size:12px;font-family:var(--mono);font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--cyan);margin-bottom:12px;}
.card p{font-size:14.5px;color:var(--text);margin-bottom:10px;}
.card p:last-child{margin-bottom:0;}
.card strong{font-weight:600;}
ul.plain{list-style:none;display:flex;flex-direction:column;gap:13px;}
ul.plain li{display:flex;gap:11px;align-items:flex-start;font-size:14px;line-height:1.55;}
.dot{width:6px;height:6px;border-radius:50%;background:var(--green);flex-shrink:0;margin-top:7px;}
.dot.c{background:var(--cyan);}.dot.g{background:var(--gold);}
.tbl{width:100%;border-collapse:collapse;font-size:13px;}
.tbl td,.tbl th{padding:10px 12px;border-bottom:1px solid rgba(30,41,59,0.6);vertical-align:top;line-height:1.45;text-align:left;}
.tbl tr:last-child td{border-bottom:none;}
.tbl th{font-family:var(--mono);font-size:9px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:var(--dimmed);}
.tbl .yours{color:var(--muted);width:46%;}.tbl .mine{color:var(--text);}
.arrow{color:var(--cyan);font-family:var(--mono);}
.chart-wrap{overflow-x:auto;}
.legend{display:flex;gap:18px;margin-top:10px;font-size:11px;color:var(--muted);font-family:var(--mono);flex-wrap:wrap;}
.legend span{display:inline-flex;align-items:center;gap:6px;}
.swatch{width:14px;height:3px;border-radius:2px;display:inline-block;}
.pilot{border-color:rgba(0,240,255,0.35);background:rgba(0,240,255,0.04);}
.foot{font-size:13px;color:var(--muted);text-align:center;padding-top:6px;line-height:1.6;}
.stamp{text-align:center;margin-top:8px;font-family:var(--mono);font-size:10px;letter-spacing:0.06em;color:var(--dimmed);}"""


def _chart_svg(series):
    n = len(series[0]["points"])
    def x(i): return 40 + i * (275.0 / (n - 1))
    def y(v): return 95 - v * 80
    lines = []
    worst = (0.0, None, None)  # (delta, xend, yend)
    for s in series:
        pts = s["points"]
        poly = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(pts))
        lines.append(f'<polyline points="{poly}" fill="none" stroke="{s["color"]}" stroke-width="2"/>')
        lines.append(f'<circle cx="{x(n-1):.1f}" cy="{y(pts[-1]):.1f}" r="3" fill="{s["color"]}"/>')
        for i in range(1, n):
            d = pts[i] - pts[i-1]
            if d < worst[0]:
                worst = (d, x(i), y(pts[i]))
    marker = ""
    if worst[1] is not None:
        marker = (f'<circle cx="{worst[1]:.1f}" cy="{worst[2]:.1f}" r="4" fill="#FF4D6D"/>'
                  f'<text x="{worst[1]:.1f}" y="{worst[2]+17:.1f}" fill="#FF4D6D" font-size="8.5" text-anchor="middle">correction</text>')
    leg = " ".join(f'<span><span class="swatch" style="background:{s["color"]};"></span> "{s["label"]}" &nbsp;{s["points"][0]} &#8594; {s["points"][-1]}</span>' for s in series)
    return (f'<div class="chart-wrap"><svg viewBox="0 0 360 150" width="100%" style="max-width:420px;display:block;margin:6px auto 0;" font-family="ui-monospace,monospace">'
            f'<line x1="40" y1="15" x2="340" y2="15" stroke="#1e293b"/><line x1="40" y1="55" x2="340" y2="55" stroke="#1e293b" stroke-dasharray="2 3"/><line x1="40" y1="95" x2="340" y2="95" stroke="#1e293b"/>'
            f'<text x="32" y="18" fill="#64748b" font-size="9" text-anchor="end">1.0</text><text x="32" y="58" fill="#64748b" font-size="9" text-anchor="end">0.5</text><text x="32" y="98" fill="#64748b" font-size="9" text-anchor="end">0.0</text>'
            f'<text x="190" y="128" fill="#94a3b8" font-size="9" text-anchor="middle">call time</text>'
            + "".join(lines) + marker + f'</svg></div><div class="legend">{leg}</div>')


def _ground_quotes(series):
    out = []
    for s in series:
        gq = s.get("grounding_quote")
        if gq:
            out.append(f'<div style="padding:11px 14px;border-left:2px solid {s["color"]};background:var(--surface2);border-radius:0 8px 8px 0;">'
                       f'<div style="font-family:var(--mono);font-size:9px;letter-spacing:0.1em;text-transform:uppercase;color:var(--dimmed);margin-bottom:4px;">grounded in &#183; your words</div>'
                       f'<div style="font-size:13.5px;line-height:1.5;color:var(--text);font-style:italic;">"{gq}"</div></div>')
    return '<div style="margin-top:14px;display:flex;flex-direction:column;gap:10px;">' + "".join(out) + "</div>"


def render_html(data, audience):
    series = [s for s in data["kinematic_series"]["series"] if visible(s, audience)]
    insights = [i for i in data.get("insights", []) if visible(i, audience)]
    prov = data["meta"].get("provenance", {})
    hdr = data["page"]["header"]
    out = [f'<!DOCTYPE html><!-- generated by recoil_brief.py from SSOT; do not hand-edit -->',
           f'<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">',
           f'<meta name="robots" content="noindex, nofollow"><title>Recoil Report</title><style>{CSS}</style></head><body><div class="page">',
           f'<div><div class="eyebrow">{hdr["eyebrow"]}</div><h1>{hdr["title"]}</h1><div class="sub">{hdr["sub"]}</div></div><div class="rule"></div>']
    for b in data["page"]["blocks"]:
        if not visible(b, audience):
            continue
        t = b["type"]
        if t == "sec_label":
            out.append(f'<div class="sec-label">{b["text"]}</div>')
        elif t == "prose":
            ps = "".join(f"<p>{p}</p>" for p in b["p"])
            out.append(f'<div class="card"><h2>{b["h2"]}</h2>{ps}</div>')
        elif t == "pilot":
            ps = "".join(f"<p>{p}</p>" for p in b["p"])
            out.append(f'<div class="card pilot"><h2>{b["h2"]}</h2>{ps}</div>')
        elif t == "list":
            items = "".join(f'<li><span class="dot {i.get("dot","")}"></span><div>{i["html"]}</div></li>' for i in b["items"])
            out.append(f'<div class="card"><h2>{b["h2"]}</h2><p style="margin-bottom:14px;">{b["intro"]}</p><ul class="plain">{items}</ul></div>')
        elif t == "rosetta":
            rows = "".join(f'<tr><td class="yours">{a}</td><td class="mine"><span class="arrow">&#8594;</span> {c}</td></tr>' for a, c in b["rows"])
            out.append(f'<div class="card"><h2>{b["h2"]}</h2><div class="chart-wrap"><table class="tbl"><tr><th>Your world</th><th>This engine</th></tr>{rows}</table></div></div>')
        elif t == "provenance":
            out.append(f'<div class="card" style="border-color:rgba(255,215,0,0.28);"><h2 style="color:var(--gold);">Source &amp; provenance</h2>'
                       f'<p>Everything here traces to {prov.get("captured","our call")}. Each read is anchored to a line you said, cleaned of filler but never paraphrased. <strong>If it is in quotes, it is your words. If it is my read, it is labeled as mine.</strong></p>'
                       f'<div style="margin-top:14px;padding:14px 16px;border-left:2px solid var(--gold);background:var(--surface2);border-radius:0 8px 8px 0;">'
                       f'<div style="font-family:var(--mono);font-size:9px;letter-spacing:0.14em;text-transform:uppercase;color:var(--dimmed);margin-bottom:6px;">Load-bearing line &#183; your words</div>'
                       f'<div style="font-size:15px;line-height:1.5;color:var(--text);font-style:italic;">"{prov.get("load_bearing_quote","")}"</div></div>'
                       f'<div style="margin-top:12px;font-family:var(--mono);font-size:10px;letter-spacing:0.06em;color:var(--dimmed);">PROVENANCE &#183; call {data["meta"]["date"]} &#183; {data["meta"]["segments"]} segments &#183; verbatim-anchored</div></div>')
        elif t == "worked_example":
            out.append(f'<div class="card"><h2>{b["h2"]}</h2><p>{b["intro"]}</p>{_chart_svg(series)}<p style="margin-top:16px;">{b["close"]}</p>{_ground_quotes(series)}</div>')
        elif t == "insights":
            items = "".join(f'<li><span class="dot {["c","","g",""][k%4]}"></span><div><strong>{i["title"]}.</strong> {i["text"]}</div></li>' for k, i in enumerate(insights))
            out.append(f'<div class="card"><h2>{b["h2"]}</h2><p style="margin-bottom:14px;">{b["intro"]}</p><ul class="plain">{items}</ul></div>')
        elif t == "belief_log":
            rows = ""
            for be in [x for x in data.get("beliefs", []) if visible(x, audience)]:
                c = be["confidence"]; cs = f'{c[0] if c[0] is not None else "--"}&#8594;{c[1]}'
                rows += f'<tr><td>{be["id"]}</td><td>{be["claim"]}</td><td>{be["inference"]}</td><td>{cs}</td><td>{be["conviction"]}</td><td>{be["verdict"]}</td></tr>'
            out.append(f'<div class="card"><h2>{b["h2"]}</h2><div class="chart-wrap"><table class="tbl"><tr><th>id</th><th>claim</th><th>inf</th><th>conf</th><th>conviction</th><th>verdict</th></tr>{rows}</table></div></div>')
        elif t == "kinematics_table":
            kin, note = compute_kinematics(data["kinematic_series"])
            rows = "".join(f'<tr><td>{k["label"]}</td><td>{k["D1_velocity"]["peak"]} / {k["D1_velocity"]["terminal"]}</td><td>{k["D2_acceleration"]["terminal"]}</td><td>{k["D3_jerk"]["terminal"]}</td></tr>' for k in kin)
            out.append(f'<div class="card"><h2>{b["h2"]}</h2><div class="chart-wrap"><table class="tbl"><tr><th>signal</th><th>D1 peak/term</th><th>D2 term</th><th>D3 term</th></tr>{rows}</table></div><p style="font-size:11px;color:var(--dimmed);margin-top:10px;">{note}</p></div>')
        elif t == "foot":
            out.append(f'<div class="foot">{b["text"]}</div>')
        elif t == "stamp":
            out.append(f'<div class="stamp">{b["text"]}</div>')
    out.append("</div></body></html>")
    return "".join(out)


def main():
    ap = argparse.ArgumentParser(description="Single-source recoil brief generator.")
    ap.add_argument("--data", required=True)
    ap.add_argument("--audience", choices=["internal", "external"], default="internal")
    ap.add_argument("--format", choices=["md", "json", "html"], default="md")
    ap.add_argument("--set", action="append", default=[], help="pass-through override key.path=value")
    a = ap.parse_args()

    data = apply_overrides(load(a.data), a.set)
    if a.format == "html":
        print(render_html(data, a.audience))
    else:
        proj = project(data, a.audience)
        print(render_md(proj) if a.format == "md" else json.dumps(proj, indent=2))


if __name__ == "__main__":
    main()
