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


ROWALT = {
    "What happens, in plain terms": ' data-alt="3"',
    "What you get": ' data-alt="2"',
    "How we will know it worked": ' data-alt="3"',
    "If it does not work": ' data-alt="3"',
}

LEVELS = [
    (1, "Exec", "The headline and one line per section."),
    (2, "Strategic", "The stages and what you get from each."),
    (3, "Operational", "Who does what, how I would work, what I need from you."),
    (4, "Tactical", "Checklists, triggers and the questions I would ask."),
    (5, "Surgical", "Every detail, plus the glossary."),
]

# heading text -> (altitude at which the body opens, one-line summary shown while collapsed)
SPEC = {
    "The short version": (1, None),
    "The whole idea, simply": (1, None),
    "The four stages": (2, "Four stages: look and listen, agree the plan together, make it solid, then aim higher and look back. Each ends with a checkpoint you can verify, and you can stop after any of them with everything I made."),
    "My view on Alice": (3, "I would hold off connecting Alice until the groundwork is done. A small trial on made-up data is the cheaper way to learn what she costs."),
    "Questions to settle with your lawyers first": (4, "Turn warm-but-never-health-advice into three written lists with your lawyers, then test Alice against sample questions."),
    "How I would approach \"will this work?\"": (4, "Before important work, the owner writes down confidence, a cap on time and money, what worked and failed look like, and what a miss would cost."),
    "A possibility I want to name early: setup that depends on what I find": (4, "Some set-up can only be scoped after I look. It is priced only if the audit shows it is needed."),
    "The cost, in three buckets": (3, "Fixed, grows with use, and hidden, each as a best, likely and worst case. Nothing is priced yet."),
    "What I need from you, and what you can expect from me": (3, "From you: the NDA, the code, the plan, your cost model and a list of services. From me: dated findings and early notice when anything moves."),
    "For Kelly": (3, "Your plan and the build side by side, cost per family in three cases, and the lists that make the empathy question testable."),
    "For Chelsea": (3, "You stay the builder. The AI provider choice waits for the facts, and Alice comes after the groundwork."),
    "What I know, what I think, what I am guessing": (3, "Every item is tagged so you can tell what is known from what is a guess."),
}


def altitude_wrap(h):
    """Split on <h2>; wrap each section as dek (while collapsed) plus body (when open)."""
    parts = re.split(r"(?=<h2>)", h)
    out = [parts[0]]
    for part in parts[1:]:
        m = re.match(r"<h2>(.*?)</h2>", part, flags=re.S)
        title = re.sub("<.*?>", "", m.group(1)).replace("&quot;", '"')
        alt, dek = SPEC.get(title, (3, None))
        rest = part[m.end():]
        if dek is None:
            out.append(f'<div class="sec" data-body-alt="{alt}">{m.group(0)}{rest}</div>')
        else:
            out.append(f'<div class="sec" data-body-alt="{alt}">{m.group(0)}<p class="dek">{dek}</p><div class="body">{rest}</div><button class="more" type="button" hidden>Show detail</button></div>')
    return "".join(out)


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
            rest = "".join(f'<div{ROWALT.get(re.sub("<.*?>", "", heads[i]).strip(), "")}><dt>{heads[i]}</dt><dd>{c}</dd></div>' for i, c in enumerate(cells) if i)
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
    body = third_col_surgical(cardify(shift(body, 1), 4))
    if TALLY_FORM_ID:
        embed = f'<iframe class="tally" src="https://tally.so/embed/{html.escape(TALLY_FORM_ID)}?hideTitle=1&dynamicHeight=1" title="Intake form" loading="lazy"></iframe>'
    else:
        embed = '<p class="note">The intake form opens here once the NDA is signed. Until then this is a preview of the questions, and nothing on this page collects or sends anything.</p>'
    return body + embed


def third_col_surgical(h):
    """Intake tables: the 'why I ask' column opens at the surgical level."""
    def row(m):
        cells = re.findall(r"<t[hd]>.*?</t[hd]>", m.group(0), flags=re.S)
        if len(cells) == 3:
            cells[2] = cells[2].replace("<th>", '<th data-alt="5">').replace("<td>", '<td data-alt="5">')
            return "<tr>" + "".join(cells) + "</tr>"
        return m.group(0)
    return re.sub(r"<tr>.*?</tr>", row, h, flags=re.S)


plan = altitude_wrap(cardify(md("07-plain-language-bundle.md"), 3))
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
@media (max-width:600px){h1{font-size:1.5rem}}
@media (min-width:900px){.cards{grid-template-columns:1fr 1fr}.card:first-child:nth-last-child(odd){grid-column:1/-1}}

[hidden]{display:none !important}
.alt{position:sticky;top:46px;background:var(--bg);border-bottom:1px solid var(--border);z-index:1}
.alt .wrap{display:flex;flex-wrap:wrap;align-items:center;gap:8px 16px;padding-top:10px;padding-bottom:10px}
.altlabel{color:var(--muted)}
.altbtns{display:flex;flex-wrap:wrap;gap:6px}
.altbtns button,.more{font:inherit;color:var(--text);background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:6px 12px;cursor:pointer}
.altbtns button[aria-pressed="true"]{border-color:var(--cyan);color:var(--cyan);background:var(--cyan-bg)}
.altbtns button:focus-visible,.more:focus-visible{outline:2px solid var(--cyan);outline-offset:2px}
.altdesc{color:var(--dimmed)}
.dek{margin:4px 0 8px;color:var(--text)}
.more{margin:4px 0 0}
.sec{margin:0}
section{scroll-margin-top:110px}
@media print{[hidden]{display:block !important}.alt,.more{display:none !important}}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
"""

buttons = "".join(f'<button type="button" data-level="{n}" aria-pressed="false">{name}</button>' for n, name, _ in LEVELS)
descs = {n: d for n, _, d in LEVELS}
import json as _json
js = """
(function(){
  var DESC=__DESC__;
  var level=2,over=new Set();
  try{var v=parseInt(localStorage.getItem('altLevel'),10);if(v>=1&&v<=5)level=v;}catch(e){}
  var secs=[].slice.call(document.querySelectorAll('.sec'));
  function apply(){
    secs.forEach(function(sec,i){
      var need=parseInt(sec.getAttribute('data-body-alt'),10);
      var hasBody=!!sec.querySelector('.body');
      var open=!hasBody||level>=need||over.has(i);
      var dek=sec.querySelector('.dek'),body=sec.querySelector('.body'),more=sec.querySelector('.more');
      if(dek)dek.hidden=open&&hasBody;
      if(body)body.hidden=!open;
      if(more){more.hidden=level>=need;more.textContent=over.has(i)?'Hide detail':'Show detail';more.setAttribute('aria-expanded',over.has(i)?'true':'false');}
      [].forEach.call(sec.querySelectorAll('[data-alt]'),function(el){
        var a=parseInt(el.getAttribute('data-alt'),10);
        el.hidden=!(over.has(i)?true:level>=a);
      });
    });
    [].forEach.call(document.querySelectorAll('.altbtns button'),function(b){
      b.setAttribute('aria-pressed',String(parseInt(b.getAttribute('data-level'),10)===level));
    });
    document.getElementById('altdesc').textContent=DESC[level];
  }
  [].forEach.call(document.querySelectorAll('.altbtns button'),function(b){
    b.addEventListener('click',function(){level=parseInt(b.getAttribute('data-level'),10);over.clear();try{localStorage.setItem('altLevel',String(level));}catch(e){}apply();});
  });
  secs.forEach(function(sec,i){
    var more=sec.querySelector('.more');
    if(more)more.addEventListener('click',function(){if(over.has(i))over.delete(i);else over.add(i);apply();});
  });
  apply();
})();
""".replace("__DESC__", _json.dumps(descs))

bar_html = '''<div class="alt" role="group" aria-label="Level of detail"><div class="wrap"><span class="altlabel">Level of detail</span><span class="altbtns">{buttons}</span><span id="altdesc" class="altdesc" aria-live="polite"></span></div></div>'''.replace("{buttons}", buttons)
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
{bar_html}
<main class="wrap">
<div class="banner" role="note">Draft for Zach to review. Not sent. No prices appear because none are agreed.</div>
<section id="plan">{plan}</section>
<section id="codex"><div class="sec" data-body-alt="5"><h2>Translation codex</h2><p class="dek">A legend for every technical word, each with a plain meaning, a picture and why it matters to you.</p><div class="body">{codex}</div><button class="more" type="button" hidden>Show detail</button></div></section>
<section id="intake"><div class="sec" data-body-alt="4"><h2>Intake</h2><p class="dek">Four short sets of questions about what I would like to see: links and descriptions only, once the NDA is signed.</p><div class="body">{intake}</div><button class="more" type="button" hidden>Show detail</button></div></section>
</main>
<script>{js}</script>
</body>
</html>
"""
out = HERE / "proposal-view.html"
out.write_text(page, encoding="utf-8")
print("wrote", out.relative_to(ROOT), len(page), "bytes")
