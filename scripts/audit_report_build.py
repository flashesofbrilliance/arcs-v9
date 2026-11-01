#!/usr/bin/env python3
"""Build an Agent Receipts Audit report page from one audit data file.

    python3 scripts/audit_report_build.py runtime/audit/cold-1.json   # writes _ARTIFACTS/audit-report/<id>.html
    python3 scripts/audit_report_build.py --check runtime/audit/cold-1.json
    python3 scripts/audit_report_build.py --self-test

The page is never hand-edited. Tokens are inlined verbatim from the kit, and the tile, LED, callout,
fidelity-grain (part 37) and altitude-ladder styles are pulled from their kit files at build time, so the report inherits the kit
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
PRIMS = ["29-tile", "33-led", "31-callout", "37-fidelity-grain"]


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
.grp { max-width: none; font-family: var(--ds-font-mono); color: var(--text); margin: 28px 0 10px; padding-top: 12px; border-top: 1px solid var(--border); }
.lede { max-width: none; margin: 0 0 12px; }
.bottom { max-width: none; margin: 16px 0; font-weight: 500; }
p, li { max-width: var(--measure); }
.mono { font-family: var(--ds-font-mono); font-size: var(--fs-body); color: var(--dimmed); }
.rows { list-style: none; padding: 0; margin: 0; background: var(--surface); border: 1px solid var(--border); border-radius: var(--ds-r-md); }
.rows li { max-width: none; padding: 12px 16px; border-top: 1px solid var(--border); }
.rows li:first-child { border-top: 0; }
.rows .why { color: var(--text-secondary); }
.bar { height: 8px; background: var(--border); border-radius: var(--ds-r-sm); overflow: hidden; margin-top: 8px; }
.bar i { display: block; height: 100%; }
.band-sharp { background: var(--green); } .band-degraded { background: var(--gold); } .band-grain { background: var(--red); }
.alt-body dl { margin: 12px 0 0; }
.alt-body dt { font-family: var(--ds-font-mono); color: var(--text-secondary); margin-top: 10px; }
.alt-body dd { margin: 2px 0 0; }
.alt-body .mono { display: block; margin-top: 12px; }
.caveat { color: var(--text-secondary); margin-top: 12px; }
.fix1 { max-width: none; margin: 0 0 12px; }
ol.fixes { padding-left: 22px; margin: 0; }
ol.fixes li { max-width: none; margin: 0 0 10px; }
.cta { display: inline-block; margin: 12px 0 0; padding: 12px 20px; border: 1px solid var(--cyan); border-radius: var(--ds-r-md); color: var(--cyan); text-decoration: none; font-weight: 600; }
footer { color: var(--dimmed); border-top: 1px solid var(--border); margin-top: 80px; }
@media (max-width: 600px) { :root { --gutter: 16px; } }
"""

BANDS = {"sharp": "well grounded (75 to 100)", "degraded": "partial, record is thin (45 to 74)",
         "grain": "described, not confirmed (under 45)"}
BAND_SHORT = {"sharp": "well grounded", "degraded": "partial", "grain": "described, not confirmed"}


# Loaded after the kit blocks: reading-comfort overrides on display text (leading >= 1.3).
POST_CSS = """.tile .v, .alts .alt-t, .alts .alt-go { line-height: 1.3; }
.callout.fix1, .caveat, footer p { max-width: none; }
.led { text-transform: none; letter-spacing: normal; font-size: var(--fs-body); }
.callout b, .alts .alt-n { font-size: var(--fs-body); }
.alts .alt-n { color: var(--text-secondary); }
.tile .k { text-transform: none; letter-spacing: normal; font-size: var(--fs-body); }"""


def render(d):
    a = d["anchors"]
    unv = d["unverified"]
    secs = d["sections"]
    record = [u for u in unv if u["group"] == "record"]
    run = [u for u in unv if u["group"] == "run"]
    unseen = sum(1 for u in record if u.get("closable") and u["kind"] == "config not committed")
    # the 90% is the source's published figure, never recomputed (it drifted once: 89 vs 90)
    tiles = "".join(
        f'<div class="tile"><div class="v">{v}</div><div class="k">{e(k)}</div></div>'
        for v, k in [(len(record), f"gaps in the repo history (+{len(run)} this run could not check)"),
                     (1 if unseen else 0, "control described, not shown (Fix 1)"),
                     (f'{a["published_pct"]}%', f'rebuilt from repo history alone ({a["reconstructed"]} of {a["total"]} commits and artifacts)')])
    weakest = min(range(len(secs)), key=lambda i: secs[i]["support"])
    ladder = []
    for i, s in enumerate(secs):
        st = y_state(s["support"])
        led = "on" if st == "sharp" else ("" if st == "degraded" else "alert")
        refs = ", ".join(s.get("evidence", []))
        selfr = " · self-reported" if s.get("self_authored") else ""
        cav = f'<p class="caveat">{e(d["self_authored_note"])}</p>' if s.get("self_authored") else ""
        ladder.append(
            f'<details class="alt"{" open" if i == weakest else ""}><summary><span class="alt-n">{i + 1:02d} · {e(s["name"])}</span>'
            f'<span class="alt-t {st}">{e(s["headline"])}</span><span class="alt-go" aria-hidden="true">+</span>'
            f'<span class="alt-s"><span class="led {led}">support {s["support"]}% · {BAND_SHORT[st]}{selfr}</span></span></summary>'
            f'<div class="alt-body"><div class="bar" role="img" aria-label="support {s["support"]} percent">'
            f'<i class="band-{st}" style="width:{s["support"]}%"></i></div>'
            f'<dl><dt>What the repo history shows</dt><dd>{e(s["shows"])}</dd>'
            f'<dt>What it does not show</dt><dd>{e(s["not_shown"])}</dd>'
            f'<dt>What would raise the score</dt><dd>{e(s["raise"])}</dd></dl>{cav}'
            f'<span class="mono">evidence: {e(refs) or "none cited"}</span></div></details>')

    def row(u):
        tone = "moire" if u["kind"] == "record contradicts itself" else ("grain" if u.get("closable") else "")
        led = "led alert" if u.get("closable") else "led"
        return (f'<li><span class="{led}">{e(u["kind"])}</span><div class="{tone}">{e(u["claim"])}</div>'
                f'<div class="why">{e(u["why"])}</div></li>')
    rows_rec = "".join(row(u) for u in record)
    rows_run = "".join(row(u) for u in run)
    corr = "".join(f'<p class="caveat">Correction: {e(c)}</p>' for c in d.get("corrections", []))
    leaks = "".join(f'<li><span class="led">not surfaced</span> <span class="mono">{e(p)}</span></li>'
                    for p in a["leaked_paths"])
    f1, rest = d["fixes"][0], d["fixes"][1:]
    fix1 = f'<div class="callout fix1"><b>Fix 1 · {e(f1["effort"])}</b>{e(f1["fix"])}</div>'
    fixes = "".join(f'<li>{"<b>" if f is f1 else ""}{e(f["fix"])}{"</b>" if f is f1 else ""} <span class="mono">{e(f["effort"])} · closes: {e(", ".join(f["closes"]))}</span></li>'
                    for f in d["fixes"])
    limits = "".join(f"<li>{e(x)}</li>" for x in d["limits"])
    legend = " · ".join(BANDS[k] for k in ("sharp", "degraded", "grain"))
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
<header class="pad"><span class="mono">Agent Receipts Audit · {e(d["repo_alias"])}</span></header>
<main class="pad">
  <h1>{e(d["title"])}</h1>
  <p class="bottom">{e(d["bottom_line"])}</p>
  {fix1}
  <p class="lede">{e(d["subtitle"])} Built from {pk["commits"]} commits and {pk["artifacts"]} artifacts, with no transcript. <a href="#fixes">See all five fixes</a>.</p>

  <h2>The numbers</h2>
  <div class="tiles">{tiles}</div>
  <p class="lede">{e(a["leak_note"])}</p>

  <h2>How far a reader with no memory got</h2>
  <p class="lede">Each section carries a support score: how well the repo history backs the claim, not how well it reads. A section that reads well but is thinly backed scores low on purpose. Bands: {legend}. The weakest section is open; open any other for its evidence.</p>
  <div class="alts">{"".join(ladder)}</div>

  <h2>Claims not verified</h2>
  <p class="lede">Not verified means the repo history does not show it. It does not mean it is false. A red light marks a gap a fix below makes checkable.</p>
  <p class="grp">Gaps in the repo history</p>
  <ul class="rows">{rows_rec}</ul>
  {corr}
  <p class="grp">Limits of this run</p>
  <p class="lede">{e(d["run_note"])}</p>
  <ul class="rows">{rows_run}</ul>

  <h2>Leak map</h2>
  <p class="lede">Commits and artifacts the repo history named but a reader could not surface. This is an observability gap, not a grade.</p>
  <ul class="rows">{leaks}</ul>

  <h2 id="fixes">Five fixes, ranked</h2>
  <p class="lede">Ranked by the auditor from the gaps above. Each names the gap it closes.</p>
  <ol class="fixes">{fixes}</ol>

  <h2>What this audit cannot see</h2>
  <ul>{limits}</ul>

  <h2>Your repo, your worst week</h2>
  <p class="lede">This is what one repo and one window gets you. Pick the week you would least like to explain from memory.</p>
  <a class="cta" href="{e(d["scope_url"])}">Scope an audit (20 min)</a>
  <p>Or have an engineer run the <a href="https://good.arcs.care/audit/check">free repo check</a> first, in about ten seconds.</p>
</main>
<footer class="pad">
  <p>rendered {e(d["generated"])} UTC · v{e(d["version"])} · ARCS · Source: <a href="{e(d["source_url"])}">{e(d["source_label"])}</a>.</p>
  <p>Range {e(d["range"])} · {e(d["repo_shape"])}. {e(d["alias_note"])} {e(d["repo_private_note"])}</p>
  <p>{e(d["self_review_note"])}</p>
</footer>
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
    assert "—" not in body, "em-dash in page body (the kit token header is verbatim and exempt)"
    assert out.count('class="alt"') == len(d["sections"])
    assert f'{d["anchors"]["published_pct"]}%' in body, "headline figure must be the published one"
    assert body.count('class="led alert"') == sum(1 for u in d["unverified"] if u.get("closable")), "red only for closable gaps"
    rec = sum(1 for u in d["unverified"] if u["group"] == "record")
    assert f'<div class="v">{rec}</div><div class="k">gaps in the repo history' in body, "gaps tile must equal the record-group count"
    first = body.split("<h2>", 1)[0]
    assert "Fix 1" in first and "%" not in first, "grug first screen: the fix before any number"
    assert body.count(" open>") == 1, "exactly one section open by default (the weakest)"
    assert "<script" not in out.lower()
    assert ".grain" not in PAGE_CSS and ".grain {" in kit_block("37-fidelity-grain"), "grain and moire come from kit part 37"
    for word in ("Kintsugi", "fruit-guard", "Y-state"):
        assert word not in body, f"internal vocabulary on a buyer surface: {word}"
    print("audit_report_build self-test: 13 checks pass")


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
