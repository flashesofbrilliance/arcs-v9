#!/usr/bin/env python3
"""render_prep_v2 — render a counterpart brief in the ADR-075 grammar (verdict+instance → 3 reasons →
3 Q/A → tasks → evidence behind disclosures, one figure per block, takeaway → figure → takeaway → record).
The renderer owns the order; the data owns the words. Passes scripts/cold_reader_gate.py by construction
if the data fits the shape. Stdlib only. No em-dashes are emitted; input is checked too.

Data shape: see _SPECS/cold-start-metaprompt.md Component 2.
Usage: python3 scripts/render_prep_v2.py --data <json> --out <html>
"""
import argparse, html as H, json, sys

CSS = """
:root{--paper:#F6F7F9;--ink:#15181E;--muted:#5A6170;--line:#DEE1E6;--well:#EEF0F3;--accent:#0E6B75;--strong:#0F7A4A;--partial:#B54708;--gap:#B42318;--measure:680px}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 "Source Serif 4",Georgia,serif}
.page{max-width:var(--measure);margin:0 auto;padding:40px 22px 72px}
h1,h2,h3,summary,.eyebrow,.k{font-family:"Instrument Sans",system-ui,sans-serif}
.eyebrow{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:0 0 10px}
h1{font-size:30px;line-height:1.15;margin:0 0 18px;font-weight:600;text-wrap:balance}
h2{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:34px 0 10px;font-weight:600}
.verdict{border:1.5px solid var(--ink);border-radius:6px;padding:16px 18px;margin:0}
.verdict .inst{font-style:italic;color:var(--muted);font-size:15.5px;margin:0 0 8px}
.verdict .line{font-size:20px;line-height:1.4;font-weight:600;font-family:"Instrument Sans",sans-serif;margin:0 0 8px}
.verdict .next{margin:0;font-size:15.5px}
.reasons{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.reasons div{background:var(--well);border-radius:6px;padding:13px 14px;font-size:15.5px}
.reasons b{display:block;font-family:"Instrument Sans",sans-serif;font-size:13px;letter-spacing:.03em;text-transform:uppercase;color:var(--accent);margin-bottom:6px}
dl{margin:0}dt{font-family:"Instrument Sans",sans-serif;font-weight:600;margin:14px 0 4px}dd{margin:0}
ol.tasks{list-style:none;padding:0;margin:0;counter-reset:t}
ol.tasks li{position:relative;padding:10px 0 10px 40px;border-top:1px solid var(--line)}ol.tasks li:last-child{border-bottom:1px solid var(--line)}
ol.tasks li::before{counter-increment:t;content:counter(t);position:absolute;left:0;top:9px;width:26px;height:26px;border-radius:50%;background:var(--ink);color:var(--paper);font:600 13px/26px "Instrument Sans",sans-serif;text-align:center}
details{border:1px solid var(--line);border-radius:6px;margin:0 0 10px}summary{cursor:pointer;padding:12px 16px;font-weight:600;font-size:15.5px}
summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px}details>div{padding:0 16px 16px}
.take{font-size:15px;color:var(--muted);margin:8px 0}
table{width:100%;border-collapse:collapse;font-size:15px;margin:8px 0}th,td{text-align:left;padding:8px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-family:"Instrument Sans",sans-serif;font-size:12px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted)}
td.fit-strong{color:var(--strong);font-weight:600}td.fit-partial{color:var(--partial);font-weight:600}td.fit-gap{color:var(--gap);font-weight:600}td.fit-your-call{color:var(--muted);font-weight:600}
.cards{display:grid;gap:10px;margin:8px 0}.card{border:1px solid var(--line);border-radius:6px;padding:12px 14px}.card h3{margin:0 0 8px;font-size:16px}
.card .k{display:inline-block;min-width:64px;font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}.card p{margin:4px 0;font-size:15px}
.triple{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:8px 0}.triple h3{font-size:13px;letter-spacing:.06em;text-transform:uppercase;margin:0 0 6px}
.triple ul{margin:0;padding-left:18px;font-size:15px}.triple li{margin:4px 0}
ul.plain{padding-left:20px;font-size:15.5px}ul.plain li{margin:6px 0}
.close{border-top:1px solid var(--line);margin-top:30px;padding-top:14px}.foot{font-size:13.5px;color:var(--muted)}.foot a{color:var(--accent)}
@media (max-width:600px){body{font-size:16px}.verdict .line{font-size:18px}}
"""

e = H.escape

def fig(f):
    t = f["type"]
    if t == "table":
        head = "".join(f"<th>{e(h)}</th>" for h in f["head"])
        rows = []
        for r in f["rows"]:
            cells = []
            for i, c in enumerate(r):
                cls = f' class="fit-{e(str(c)).lower().replace(" ", "-")}"' if i == 1 and str(c).lower() in ("strong", "partial", "gap", "your call") else ""
                cells.append(f"<td{cls}>{e(str(c))}</td>")
            rows.append("<tr>" + "".join(cells) + "</tr>")
        return f'<div style="overflow-x:auto"><table><tr>{head}</tr>{"".join(rows)}</table></div>'
    if t == "cards":
        out = []
        for it in f["items"]:
            rows = "".join(f'<p><span class="k">{e(k)}</span> {e(v)}</p>' for k, v in it["rows"])
            out.append(f'<div class="card"><h3>{e(it["h"])}</h3>{rows}</div>')
        return f'<div class="cards">{"".join(out)}</div>'
    if t == "triple":
        cols = "".join(f'<div><h3>{e(h)}</h3><ul>{"".join(f"<li>{e(x)}</li>" for x in items)}</ul></div>' for h, items in f["cols"])
        return f'<div class="triple">{cols}</div>'
    if t == "list":
        return '<ul class="plain">' + "".join(f"<li>{e(x)}</li>" for x in f["items"]) + "</ul>"
    if t == "number":
        return f'<p style="font:600 34px/1.1 Instrument Sans,sans-serif;margin:8px 0">{e(f["value"])} <span style="font-size:15px;color:var(--muted);font-weight:400">{e(f.get("label",""))}</span></p>'
    raise SystemExit(f"unknown figure type {t}")

def render(d):
    m, v = d["meta"], d["verdict"]
    assert len(d["reasons"]) == 3 and len(d["questions"]) == 3, "grammar requires exactly 3 reasons and 3 questions"
    parts = [f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(m["who"])} × {e(m["org"])}</title>',
             '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@500;600&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap">',
             f"<style>{CSS}</style></head><body><div class=\"page\">",
             f'<p class="eyebrow">{e(m["who"])} · {e(m["role"])} · {e(m["org"])} · read time: {int(m["read_minutes"])} minutes · {e(m["for"])}</p>',
             f'<h1>{e(v["line"])}</h1>',
             f'<div class="verdict"><p class="inst">{e(v["instance"])}</p><p class="line">If you read one thing: {e(v["line"])}</p><p class="next">Next step: {e(v["next_step"])}</p></div>',
             '<h2>Three reasons this seat is yours to lose</h2><div class="reasons">' + "".join(f'<div><b>{e(r["h"])}</b>{e(r["t"])}</div>' for r in d["reasons"]) + "</div>",
             '<h2>The three questions you will get</h2><dl>' + "".join(f'<dt>{e(q["q"])}</dt><dd>{e(q["a"])}</dd>' for q in d["questions"]) + "</dl>",
             '<h2>Before the call</h2><ol class="tasks">' + "".join(f"<li>{e(t)}</li>" for t in d["tasks"]) + "</ol>",
             '<h2>The record, if you want it</h2>']
    for b in d["blocks"]:
        parts.append(f'<details><summary>{e(b["title"])}</summary><div><p class="take">{e(b["open"])}</p>{fig(b["figure"])}<p class="take">{e(b["close"])}</p></div></details>')
    links = " · ".join(f'<a href="{e(l["href"])}">{e(l["label"])}</a>' for l in d.get("record_links", []))
    parts.append(f'<div class="close"><p>{e(d["close"])}</p><p class="foot">sources: {e(m["sources"])}{(" · " + links) if links else ""}</p></div>')
    parts.append("</div></body></html>")
    out = "".join(parts)
    if "—" in out:
        raise SystemExit("em-dash in output; fix the data")
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    d = json.load(open(a.data, encoding="utf-8"))
    html = render(d)
    open(a.out, "w", encoding="utf-8").write(html)
    print(f"render_prep_v2: {a.out} ({len(html)} bytes)")

if __name__ == "__main__":
    main()
