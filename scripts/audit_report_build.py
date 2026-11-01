#!/usr/bin/env python3
"""Build an Agent Receipts Audit report page from one audit data file.

    python3 scripts/audit_report_build.py runtime/audit/cold-1.json   # writes _ARTIFACTS/audit-report/<id>.html
    python3 scripts/audit_report_build.py --check runtime/audit/cold-1.json
    python3 scripts/audit_report_build.py --self-test

The page is never hand-edited. Tokens are inlined verbatim from the kit, and the tile, LED, callout and
altitude-ladder styles are pulled from their kit files at build time, so the report inherits the kit
instead of copying it. Every claim renders at earned fidelity: record support sets the Y-state.
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KIT = ROOT / "src/ui-kit/recoil-report"
OUT = ROOT / "_ARTIFACTS/audit-report"
PRIMS = ["29-tile", "33-led", "31-callout"]


def y_state(support):
    """Record support (0-100) to render resolution, per the WORLD.md render scale."""
    if support >= 75:
        return "sharp"
    if support >= 45:
        return "degraded"
    return "grain"


def kit_block(name):
    text = (KIT / f"{name}.html").read_text()
    m = re.search(r"/\* @prim:begin %s \*/(.*?)/\* @prim:end %s \*/" % (name, name), text, re.S)
    if not m:
        raise SystemExit(f"kit primitive {name} has no @prim block")
    return m.group(1).strip()


def ladder_block():
    text = (KIT / "17-altitude-ladder.html").read_text()
    css = re.search(r"<style>(.*?)</style>", text, re.S).group(1)
    keep = [l for l in css.splitlines() if l.startswith((".alts", "details.alt", ".alt-", "details[open]", "@media"))]
    return "\n".join(keep)


def e(s):
    return html.escape(str(s), quote=True)


PAGE_CSS = """
:root { --measure: 680px; --lane: 1040px; --gutter: 40px; }
* { box-sizing: border-box; }
html, body { margin: 0; background: var(--bg); color: var(--text); }
body { font-family: var(--ds-font-sans); font-size: var(--fs-body); line-height: 1.6; overflow-wrap: break-word; }
a { color: var(--cyan); text-underline-offset: 3px; }
.pad { max-width: var(--lane); margin: 0 auto; padding: 0 var(--gutter); }
header.pad, footer.pad { padding-top: 28px; padding-bottom: 28px; }
h1 { font-family: var(--ds-font-display); font-size: var(--fs-display); line-height: 1.3; margin: 40px 0 12px; }
h2 { font-family: var(--ds-font-display); font-size: var(--fs-headline); line-height: 1.3; margin: 56px 0 14px; }
.lede { max-width: none; margin: 0 0 12px; }
p, li { max-width: var(--measure); }
.mono { font-family: var(--ds-font-mono); font-size: var(--fs-body); color: var(--dimmed); }
.sharp { font-weight: 500; letter-spacing: normal; }
.degraded { font-weight: 400; letter-spacing: 0.01em; }
.grain { font-weight: 300; letter-spacing: 0.02em; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='120' height='120' filter='url(%23n)' opacity='0.06'/%3E%3C/svg%3E"); }
.moire { font-weight: 300; letter-spacing: 0.03em; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='turbulence' baseFrequency='0.02 0.6' numOctaves='1'/%3E%3C/filter%3E%3Crect width='120' height='120' filter='url(%23n)' opacity='0.08'/%3E%3C/svg%3E"); }
.rows { list-style: none; padding: 0; margin: 0; background: var(--surface); border: 1px solid var(--border); border-radius: var(--ds-r-md); }
.rows li { max-width: none; padding: 12px 16px; border-top: 1px solid var(--border); }
.rows li:first-child { border-top: 0; }
.rows .why { color: var(--text-secondary); }
.fixes .callout { max-width: none; margin: 0 0 10px; }
.bar { height: 8px; background: var(--border); border-radius: var(--ds-r-sm); overflow: hidden; margin-top: 8px; }
.bar i { display: block; height: 100%; background: var(--cyan); }
.alt-body .mono { display: block; margin-top: 12px; }
footer { color: var(--dimmed); border-top: 1px solid var(--border); margin-top: 80px; }
@media (max-width: 600px) { :root { --gutter: 16px; } }
"""


# Loaded after the kit blocks: reading-comfort overrides on display text (leading >= 1.3).
POST_CSS = ".tile .v, .alts .alt-t, .alts .alt-go { line-height: 1.3; }"


def render(d):
    a = d["anchors"]
    pct = round(100 * a["reconstructed"] / a["total"])
    unv = d["unverified"]
    secs = d["sections"]
    tiles = "".join(
        f'<div class="tile"><div class="v{c}">{v}</div><div class="k">{e(k)}</div></div>'
        for v, k, c in [(f"{pct}%", "record rebuilt cold", " cyan"),
                        (f'{a["reconstructed"]}/{a["total"]}', "anchors reconstructed", ""),
                        (len(unv), "claims it could not verify", ""),
                        (a["leaked"], "anchors leaked", "")])
    ladder = []
    for i, s in enumerate(secs, 1):
        st = y_state(s["support"])
        led = "on" if st == "sharp" else ("" if st == "degraded" else "alert")
        refs = ", ".join(s.get("evidence", []))
        ladder.append(
            f'<details class="alt"><summary><span class="alt-n">{i:02d} · {e(s["name"])}</span>'
            f'<span class="alt-t {st}">{e(s["headline"])}</span><span class="alt-go" aria-hidden="true">+</span>'
            f'<span class="alt-s"><span class="led {led}">record support {s["support"]}% · {st}</span></span></summary>'
            f'<div class="alt-body"><div class="bar" role="img" aria-label="record support {s["support"]} percent">'
            f'<i style="width:{s["support"]}%"></i></div><span class="mono">evidence: {e(refs) or "none cited"}</span></div></details>')
    rows = "".join(
        f'<li class="{"moire" if u["kind"] == "record contradicts itself" else "grain"}">'
        f'<span class="led alert">{e(u["kind"])}</span><div>{e(u["claim"])}</div><div class="why">{e(u["why"])}</div></li>'
        for u in unv)
    leaks = "".join(f'<li class="grain"><span class="led alert">leaked</span> <span class="mono">{e(p)}</span></li>'
                    for p in a["leaked_paths"])
    fixes = "".join(f'<div class="callout"><b>Fix {f["rank"]}</b>{e(f["fix"])} <span class="mono">closes: {e(", ".join(f["closes"]))}</span></div>'
                    for f in d["fixes"])
    limits = "".join(f"<li>{e(x)}</li>" for x in d["limits"])
    tokens = (KIT / "_tokens.css").read_text()
    css = "\n".join([tokens, PAGE_CSS] + [kit_block(p) for p in PRIMS] + [ladder_block(), POST_CSS])
    pk = d["pack"]
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Audit Report · {e(d["title"])} · ARCS</title>
<meta name="robots" content="noindex">
<!-- Generated by scripts/audit_report_build.py from runtime/audit/{e(d["id"])}.json. Do not hand-edit. -->
<style>
{css}
</style>
</head>
<body>
<header class="pad"><span class="mono">Agent Receipts Audit · sample report · {e(d["repo"])} · {e(d["range"])}</span></header>
<main class="pad">
  <h1>{e(d["title"])}</h1>
  <p class="lede">{e(d["subtitle"])} A reader with no memory of the work rebuilt it from {pk["commits"]} commits and {pk["artifacts"]} artifacts, with no transcript. Each claim below renders as sharp as the record behind it.</p>
  <div class="tiles">{tiles}</div>

  <h2>How far a cold reader got</h2>
  <p class="lede">Sharp text is backed by the record. Grain is described but not confirmed. Open a row for its evidence.</p>
  <div class="alts">{"".join(ladder)}</div>

  <h2>Claims the record cannot back</h2>
  <ul class="rows">{rows}</ul>

  <h2>Leak map</h2>
  <p class="lede">Anchors the record named but a cold reader could not surface. This is an observability gap, not a grade.</p>
  <ul class="rows">{leaks}</ul>

  <h2>Five fixes, ranked</h2>
  <div class="fixes">{fixes}</div>

  <h2>What this audit cannot see</h2>
  <ul>{limits}</ul>
</main>
<footer class="pad"><p>Source: {e(d["source"])}.</p></footer>
</body>
</html>
"""


def self_test():
    assert y_state(85) == "sharp" and y_state(75) == "sharp"
    assert y_state(60) == "degraded" and y_state(45) == "degraded"
    assert y_state(44) == "grain" and y_state(0) == "grain"
    d = json.loads((ROOT / "runtime/audit/cold-1.json").read_text())
    out = render(d)
    body = out.split("</style>", 1)[1]
    assert "\u2014" not in body, "em-dash in page body (the kit token header is verbatim and exempt)"
    assert out.count('class="alt"') == len(d["sections"])
    assert out.count('class="moire"') == 1, "the one self-contradiction should render MOIRE"
    assert "<script" not in out.lower()
    print("audit_report_build self-test: 7 checks pass")


def main(argv):
    if argv == ["--self-test"]:
        return self_test()
    check = "--check" in argv
    paths = [p for p in argv if not p.startswith("--")]
    if not paths:
        raise SystemExit(__doc__)
    bad = 0
    for p in paths:
        d = json.loads(Path(p).read_text())
        out = render(d)
        dest = OUT / f'{d["id"]}.html'
        if check:
            if not dest.exists() or dest.read_text() != out:
                print(f"STALE {dest.relative_to(ROOT)}: rerun scripts/audit_report_build.py {p}")
                bad = 1
        else:
            OUT.mkdir(parents=True, exist_ok=True)
            dest.write_text(out)
            print(f"wrote {dest.relative_to(ROOT)} ({len(out):,} bytes)")
    sys.exit(bad)


if __name__ == "__main__":
    main(sys.argv[1:])
