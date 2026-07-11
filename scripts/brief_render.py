#!/usr/bin/env python3
"""
brief_render.py — parameterized call-brief renderer (ADR-032)
==============================================================
Renders public/<slug>.html from a params JSON + the canonical template.

Self-sovereign: stdlib only, Python 3.8+. Deterministic: same params + same
template => byte-identical output, so the embedded provenance is provable —
anyone with the repo can re-run the printed command and diff.

    python3 scripts/brief_render.py --params briefs/demo.params.json
    python3 scripts/brief_render.py --params briefs/demo.params.json --check

─────────────────────────────────────────────────────────────
PARAMS CONTRACT (briefs/<name>.params.json):
─────────────────────────────────────────────────────────────
{
  "name":          "demo",              # lowercase first name; gate password + sessionStorage key
  "slug":          "demo-brief",        # output file stem (default: name) -> public/<slug>.html
  "full_name":     "First Last",
  "company":       "Company / context label",
  "date_label":    "JUL 10, 2026 · PRE-CALL",
  "date_display":  "Jul 10, 2026",
  "next_date_tab": "Jul 24 Agenda",     # label for the 4th tab
  "ygate":         "YELLOW / MEDIUM / REVISIT",
  "true_north":    "One sentence.",
  "provenance":    "receipt",           # "full" (internal: visible CLI card)
                                        # "receipt" (client-facing: one mono line, no command surface)
  "tabs": { "pre": [card, ...], "recoil": [...], "post": [...], "agenda": [...] }
}

Card types (text values are trusted HTML fragments — author-controlled, never user input):
  {"type":"text",      "title":"True North", "text":"..."}
  {"type":"conf",      "title":"Context",  "rows":[{"key":"Date","val":"..."} | {"key":"Y-Gate","badge":"GREEN / ..."}]}
  {"type":"intel",     "title":"Intel",    "rows":[{"color":"cyan","text":"<strong>Fact</strong> — detail"}]}
  {"type":"questions", "title":"Questions to Ask", "rows":[{"text":"...","look_for":"..."}]}   # numbered automatically
  {"type":"next",      "title":"Next Steps","rows":[{"owner":"Zach","color":"cyan","text":"..."}]}
  {"type":"html",      "title":"Anything", "html":"<raw fragment>"}   # escape hatch for bespoke sections

Colors: cyan | green | gold | red | muted | dimmed  ->  var(--<color>)
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TEMPLATE = "public/templates/call-brief-template.html"
TABS = ("pre", "recoil", "post", "agenda")
COLORS = {"cyan", "green", "gold", "red", "muted", "dimmed"}
REQUIRED = ("name", "full_name", "company", "date_label", "date_display",
            "next_date_tab", "ygate", "true_north", "tabs")


def die(msg):
    print(f"brief_render: error: {msg}", file=sys.stderr)
    sys.exit(1)


def sha12(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:12]


def color_var(name):
    if name not in COLORS:
        die(f"unknown color {name!r} (allowed: {', '.join(sorted(COLORS))})")
    return f"var(--{name})"


def card_shell(title, body, margin):
    header = (f'<div class="card-header"><div class="card-title">{title}</div></div>'
              if title else "")
    return (f'      <div class="card" style="margin:{margin};">\n'
            f'        {header}\n{body}\n      </div>')


def build_card(card, margin):
    ctype = card.get("type")
    title = card.get("title", "")
    if ctype == "text":
        body = (f'        <div style="padding:16px 20px;font-size:14px;line-height:1.6;'
                f'color:var(--text);">{card["text"]}</div>')
    elif ctype == "conf":
        rows = []
        for r in card["rows"]:
            if "badge" in r:
                val = (f'<div class="ygate-badge"><div class="ygate-dot"></div>{r["badge"]}</div>')
            else:
                val = r["val"]
            rows.append(f'          <div class="conf-row"><div class="conf-key">{r["key"]}</div>'
                        f'<div class="conf-val">{val}</div></div>')
        body = '        <div class="conf-rows">\n' + "\n".join(rows) + "\n        </div>"
    elif ctype == "intel":
        rows = [f'          <div class="intel-row"><div class="intel-dot" '
                f'style="background:{color_var(r.get("color", "cyan"))};"></div>'
                f'<div class="intel-text">{r["text"]}</div></div>'
                for r in card["rows"]]
        body = '        <div class="intel-rows">\n' + "\n".join(rows) + "\n        </div>"
    elif ctype == "questions":
        rows = []
        for i, r in enumerate(card["rows"], 1):
            look = (f'\n            <div class="q-look">Look for: {r["look_for"]}</div>'
                    if r.get("look_for") else "")
            rows.append(f'          <div class="q-row">\n'
                        f'            <div class="q-top"><div class="q-n">{i}</div>'
                        f'<div class="q-text">{r["text"]}</div></div>{look}\n'
                        f'          </div>')
        body = '        <div class="q-rows">\n' + "\n".join(rows) + "\n        </div>"
    elif ctype == "next":
        rows = [f'          <div class="next-row"><div class="next-owner" '
                f'style="color:{color_var(r.get("color", "cyan"))};">{r["owner"]}</div>'
                f'<div class="next-text">{r["text"]}</div></div>'
                for r in card["rows"]]
        body = '        <div class="next-rows">\n' + "\n".join(rows) + "\n        </div>"
    elif ctype == "html":
        body = "        " + card["html"]
    else:
        die(f"unknown card type {ctype!r}")
    return card_shell(title, body, margin)


def build_tab(cards, tab):
    if not cards:
        die(f"tabs.{tab} is empty — every tab needs at least one card")
    out = []
    last = len(cards) - 1
    for i, card in enumerate(cards):
        top = "16px" if i == 0 else "0"
        bottom = "16px" if i == last else "0"
        out.append(build_card(card, f"{top} 16px {bottom}"))
    return "\n".join(out)


def provenance_block(tier, params_rel, params_sha, tmpl_sha, tmpl_ver, date_display):
    stamp = f"call-brief-template v{tmpl_ver} · params {params_sha}"
    if tier == "receipt":
        return (f'  <div style="font-family:var(--mono);font-size:9px;color:var(--dimmed);'
                f'letter-spacing:0.08em;text-align:center;padding-top:8px;">'
                f'ARCS · {stamp} · {date_display}</div>')
    cmd = f"python3 scripts/brief_render.py --params {params_rel}"
    return f"""  <div class="card">
    <div class="card-header"><div class="card-title">Provenance — Reproducible Render</div></div>
    <div style="padding:14px 20px;font-family:var(--mono);font-size:10px;line-height:2;color:var(--dimmed);letter-spacing:0.03em;">
      <div style="color:var(--cyan);">$ {cmd}</div>
      <div>template&nbsp;&nbsp;public/templates/call-brief-template.html · v{tmpl_ver} · sha256 {tmpl_sha}</div>
      <div>params&nbsp;&nbsp;&nbsp;&nbsp;{params_rel} · sha256 {params_sha}</div>
      <div>Re-running the command from the repo root reproduces this file byte-for-byte.</div>
    </div>
  </div>"""


def render(params_path: Path, template_path: Path):
    try:
        params = json.loads(params_path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        die(f"cannot read params {params_path}: {e}")
    for key in REQUIRED:
        if key not in params:
            die(f"params missing required field {key!r}")
    tier = params.get("provenance", "receipt")
    if tier not in ("full", "receipt"):
        die(f'provenance must be "full" or "receipt", got {tier!r}')

    tmpl_bytes = template_path.read_bytes()
    html = tmpl_bytes.decode()
    m = re.search(r"TEMPLATE_VERSION:\s*(\S+)", html)
    tmpl_ver = m.group(1) if m else "unversioned"

    # Strip the authoring-instructions comment block — it documents {{PLACEHOLDERS}},
    # which would trip the unresolved-placeholder check (and is noise in output).
    html = re.sub(r"<!--\n  ARCS CALL BRIEF — CANONICAL TEMPLATE.*?-->\n", "", html,
                  count=1, flags=re.S)

    for tab in TABS:
        cards = params["tabs"].get(tab)
        if cards is None:
            die(f"params.tabs missing tab {tab!r}")
        pattern = re.compile(
            rf'(<div id="tab-{tab}" class="tab-pane[^"]*">).*?(</div><!-- /tab-{tab} -->)',
            re.S)
        if not pattern.search(html):
            die(f"template has no region markers for tab {tab!r}")
        content = build_tab(cards, tab)
        html = pattern.sub(lambda mo: f"{mo.group(1)}\n\n{content}\n\n    {mo.group(2)}", html)

    fields = {
        "NAME": params["name"], "FULL_NAME": params["full_name"],
        "COMPANY": params["company"], "DATE_LABEL": params["date_label"],
        "DATE_DISPLAY": params["date_display"], "NEXT_DATE_TAB": params["next_date_tab"],
        "YGATE": params["ygate"], "TRUE_NORTH": params["true_north"],
    }
    for key, val in fields.items():
        html = html.replace("{{" + key + "}}", val)

    leftover = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", html)))
    if leftover:
        die(f"unresolved placeholders after render: {', '.join(leftover)}")

    try:
        params_rel = params_path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        params_rel = params_path.as_posix()  # params outside the repo — show as given
    prov = provenance_block(tier, params_rel, sha12(params_path.read_bytes()),
                            sha12(tmpl_bytes), tmpl_ver, params["date_display"])
    html = html.replace("</div><!-- /page -->", f"\n{prov}\n</div><!-- /page -->")
    html += (f"<!-- arcs:brief-render template_version={tmpl_ver} "
             f"template_sha256={sha12(tmpl_bytes)} params_sha256={sha12(params_path.read_bytes())} -->\n")
    return params, html


def main():
    ap = argparse.ArgumentParser(description="Render a call brief from params JSON (ADR-032)")
    ap.add_argument("--params", required=True, help="briefs/<name>.params.json")
    ap.add_argument("--template", default=str(REPO_ROOT / DEFAULT_TEMPLATE))
    ap.add_argument("--out", help="output path (default: public/<slug>.html)")
    ap.add_argument("--check", action="store_true",
                    help="verify the existing output matches a fresh render (drift check); writes nothing")
    args = ap.parse_args()

    params, html = render(Path(args.params), Path(args.template))
    slug = params.get("slug", params["name"])
    out = Path(args.out) if args.out else REPO_ROOT / "public" / f"{slug}.html"

    try:
        out_disp = out.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        out_disp = out.as_posix()

    if args.check:
        if not out.exists():
            die(f"--check: {out} does not exist")
        if out.read_text() != html:
            die(f"--check: {out} has drifted from its params — re-render or fix the params")
        print(f"OK — {out_disp} matches its params (no drift)")
        return

    out.write_text(html)
    print(f"rendered {out_disp} "
          f"({len(html)} bytes, provenance={params.get('provenance', 'receipt')})")


if __name__ == "__main__":
    main()
