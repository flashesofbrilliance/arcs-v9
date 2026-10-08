#!/usr/bin/env python3
"""build_proposal_view.py: generate proposal-view.html from 07, 09 and 10 (single source = the markdown).

Run from the repo root:  python3 _ARTIFACTS/sow-scaffold-2026-10-08/build_proposal_view.py
Tables with four or more columns are rendered as stacked cards so narrow screens never need sideways scrolling.
TALLY_FORM_ID: leave empty until a form exists; the page then shows the questions as a read-only preview.
"""
import html
import re
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
TALLY_FORM_ID = ""

tokens = (ROOT / "src/ui-kit/recoil-report/_tokens.css").read_text(encoding="utf-8")


def md(path):
    text = (HERE / path).read_text(encoding="utf-8")
    text = re.sub(r"^> DRAFT FOR ZACH.*\n", "", text, flags=re.M)
    return markdown.markdown(text, extensions=["tables"])


def cardify(h, level=3):
    def table(m):
        t = m.group(0)
        heads = re.findall(r"<th[^>]*>(.*?)</th>", t, flags=re.S)
        if len(heads) < 4:
            return '<div class="tablewrap">' + t + "</div>"
        cards = []
        for row in re.findall(r"<tr>\s*(<td.*?)</tr>", t, flags=re.S):
            cells = re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.S)
            first = cells[0]
            rest = "".join(f"<div><dt>{heads[i]}</dt><dd>{c}</dd></div>" for i, c in enumerate(cells) if i)
            cards.append(f'<article class="card"><h{level}>{first}</h{level}><dl>{rest}</dl></article>')
        return '<div class="cards">' + "".join(cards) + "</div>"
    return re.sub(r"<table>.*?</table>", table, h, flags=re.S)


def shift(h, down):
    """Demote headings by `down` levels so the page keeps one h1 and no skipped levels."""
    for lvl in (3, 2, 1):
        h = re.sub(rf"<(/?)h{lvl}>", lambda m: f"<{m.group(1)}h{lvl + down}>", h)
    return h


def intake_section():
    body = md("10-intake-forms-spec.md")
    body = re.sub(r"<h1>.*?</h1>", "", body, count=1)
    body = cardify(shift(body, 1), 4)
    if TALLY_FORM_ID:
        embed = f'<iframe class="tally" src="https://tally.so/embed/{html.escape(TALLY_FORM_ID)}?hideTitle=1&dynamicHeight=1" title="Intake form" loading="lazy"></iframe>'
    else:
        embed = '<p class="note">The intake form opens here once the NDA is signed. Until then this is a preview of the questions, and nothing on this page collects or sends anything.</p>'
    return body + embed


plan = cardify(md("07-plain-language-bundle.md"), 3)
codex = cardify(shift(md("09-translation-codex.md"), 1), 4)
intake = intake_section()

css = tokens + """
:root{--measure:760px;--gut:24px;--font-body:system-ui,-apple-system,'Inter',sans-serif;--font-code:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;--font-head:'Iowan Old Style','Palatino Linotype',Palatino,Georgia,serif}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--text);font:0.925rem/1.6 var(--font-body)}
.wrap{max-width:calc(var(--measure) + 2*var(--gut));margin:0 auto;padding:0 var(--gut) 64px}
nav{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--border);z-index:2}
nav .wrap{display:flex;gap:20px;padding-top:12px;padding-bottom:12px;overflow-x:auto}
nav a{color:var(--muted);text-decoration:none;white-space:nowrap;padding:6px 0}
nav a:hover,nav a:focus{color:var(--cyan)}
.banner{background:var(--gold-bg);border:1px solid var(--gold);border-radius:6px;padding:12px 16px;margin:24px 0;color:var(--text)}
h1{font-family:var(--font-head);font-size:2.4rem;font-weight:500;line-height:1.2;letter-spacing:-0.02em;margin:32px 0 8px}
h2{font-size:1.15rem;font-weight:600;line-height:1.25;letter-spacing:-0.01em;margin:48px 0 12px;color:var(--cyan)}
h3{font-size:1.15rem;font-weight:600;line-height:1.25;margin:28px 0 8px}
h4{font-size:0.925rem;font-weight:600;margin:0 0 8px}
p,li{max-width:none}
a{color:var(--cyan)}
code{font-family:var(--font-code);font-size:.9em;color:var(--text-secondary,#94a3b8)}
.cards{display:grid;gap:12px;margin:16px 0}
.card{background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:14px 16px}
.card h3,.card h4{margin:0 0 8px;font-size:0.925rem;font-weight:600;color:var(--green)}
.card dl{margin:0;display:grid;gap:8px}
.card dt{font-size:0.925rem;color:var(--muted)}
.card dd{margin:0}
.tablewrap{overflow-x:auto;margin:16px 0}
table{border-collapse:collapse;width:100%}
th,td{border:1px solid var(--border);padding:10px 12px;text-align:left;vertical-align:top}
th{background:#111827;color:var(--dimmed);font-weight:600}
.note{background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:12px 16px;color:var(--dimmed)}
iframe.tally{width:100%;min-height:640px;border:1px solid var(--border);border-radius:6px;background:var(--surface)}
section{scroll-margin-top:64px}
@media (max-width:600px){h1{font-size:1.5rem}}
@media (min-width:900px){.cards{grid-template-columns:1fr 1fr}.card:first-child:nth-last-child(odd){grid-column:1/-1}}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
"""

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>My Ally LD plan</title>
<style>{css}</style>
</head>
<body>
<nav aria-label="Sections"><div class="wrap"><a href="#plan">The plan</a><a href="#codex">Translation codex</a><a href="#intake">Intake</a></div></nav>
<main class="wrap">
<div class="banner" role="note">Draft for Zach to review. Not sent. No prices appear because none are agreed.</div>
<section id="plan">{plan}</section>
<section id="codex">{codex}</section>
<section id="intake"><h2>Intake</h2>{intake}</section>
</main>
</body>
</html>
"""
out = HERE / "proposal-view.html"
out.write_text(page, encoding="utf-8")
print("wrote", out.relative_to(ROOT), len(page), "bytes")
