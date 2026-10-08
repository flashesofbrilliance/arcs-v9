#!/usr/bin/env python3
"""build_proposal_view.py: generate proposal-view.html from 07, 09 and 10 (single source = the markdown).

Run from the repo root:  python3 _ARTIFACTS/sow-scaffold-2026-10-08/build_proposal_view.py

SEND = False keeps the "draft for Zach" strip; set True only when Zach has said yes to sending.
TALLY_FORM_ID: leave empty until a form exists; the page then shows the questions as a read-only preview.
Light theme is the default; the dark theme follows the reader's system setting or the toggle.
"""
import html
import json
import re
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SEND = False
TALLY_FORM_ID = ""
DEFAULT_LEVEL = 3

tokens = (ROOT / "src/ui-kit/recoil-report/_tokens.css").read_text(encoding="utf-8")

LEVELS = [
    (1, "Exec", "The headline, one line per section, and what happens next.", "the short version, the picture, and one line per section"),
    (2, "Strategic", "The stages, what happens in each, and what you get.", "the four stages with what happens and what you get"),
    (3, "Operational", "Who does what, how I would work, and what I need from you.", "who does what, how I would work, and what I need from you"),
    (4, "Tactical", "Checklists, triggers and the questions I would ask, with why.", "checklists, triggers and the questions I would ask"),
    (5, "Surgical", "Every detail, plus the glossary.", "every remaining detail and the glossary"),
]

# heading text -> (level at which the body opens, one-line summary shown while collapsed)
SPEC = {
    "The short version": (2, "Your product already does what you set out to show. Before more gets built, I would help make sure the plan, the money and the build all describe the same product. Four stages, a checkpoint at each, and you can stop at any point with everything in hand."),
    "The whole idea, simply": (2, "Build it like a house: look at the ground first, agree the route, pour the floor, then decide how big it gets."),
    "The four stages": (2, "Look and listen. Agree the plan together. Make it solid. Aim higher, then look back."),
    "For Kelly": (3, "Your plan and the build side by side, cost per family in three cases, and the lists that make the empathy question testable."),
    "For Chelsea": (3, "You stay the builder. The AI provider choice waits for the facts, and Alice comes after the groundwork."),
    "My view on Alice": (3, "I would hold off connecting Alice until three answers are in. A small trial on made-up data is the cheaper way to learn what she costs."),
    "Questions to settle with your lawyers first": (4, "Turn warm-but-never-health-advice into three written lists with your lawyers, then test Alice against sample questions."),
    "How I would approach \"will this work?\"": (4, "Before important work, the owner writes down confidence, a cap on time and money, what worked and failed look like, and what a miss would cost."),
    "A possibility I want to name early: setup that depends on what I find": (4, "Some set-up can only be scoped after I look. It is priced only if it is needed."),
    "The cost, in three buckets": (3, "Fixed, grows with use, and hidden, each as a best, likely and worst case. Nothing is priced yet."),
    "What I need from you, and what you can expect from me": (3, "From you: the NDA, the code, the plan, your cost model and a list of services. From me: dated findings and early notice when anything moves."),
    "What I know, what I think, what I am guessing": (3, "I say which points I know, which I think and which I am guessing."),
    "What happens next": (1, None),
}

# first occurrence of these phrases in the plan links to the codex entry
GLOSS_LINKS = [
    (r"usage meter", "token"),
    (r"AI providers?", "vendor-provider"),
    (r"change tracking", "version-control-branch"),
    (r"who can see what", "role-based-access"),
    (r"audit log", "audit-log"),
    (r"evidence trail", "evidence-trail"),
    (r"NDA", "nda"),
    (r"cost model", "cost-model"),
    (r"made-up", "synthetic-data"),
    (r"look-back", "looking-back"),
]


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", re.sub("<.*?>", "", text).lower()).strip("-")


def md(path):
    text = (HERE / path).read_text(encoding="utf-8")
    text = re.sub(r"^> DRAFT FOR ZACH.*\n", "", text, flags=re.M)
    return markdown.markdown(text, extensions=["tables"])


def shift(h, down):
    """Demote headings by `down` levels so the page keeps one h1 and no skipped levels."""
    for lvl in (3, 2, 1):
        h = re.sub(rf"<(/?)h{lvl}>", lambda m: f"<{m.group(1)}h{lvl + down}>", h)
    return h


def cells(row, tag):
    return re.findall(rf"<{tag}[^>]*>(.*?)</{tag}>", row, flags=re.S)


def stage_rail(h):
    """The four-stage table becomes a numbered rail; row visibility follows the depth ladder."""
    def table(m):
        t = m.group(0)
        heads = [re.sub("<.*?>", "", c).strip() for c in cells(t, "th")]
        if heads[:1] != ["Stage"]:
            return '<div class="tablewrap" tabindex="0">' + t + "</div>"
        alt = {"What happens, in plain terms": 2, "What you get": 2, "How you will know it worked": 3, "If it does not work": 3}
        order = ["What happens, in plain terms", "What you get", "How you will know it worked", "If it does not work"]
        items = []
        for row in re.findall(r"<tr>\s*(<td.*?)</tr>", t, flags=re.S):
            c = cells(row, "td")
            parts = ""
            for name in order:
                parts += f'<div class="row" data-alt="{alt[name]}"><span class="lbl">{name}</span><p>{c[heads.index(name)]}</p></div>'
            items.append(f'<li class="stage"><h3>{c[0]}</h3>{parts}</li>')
        return '<ol class="rail">' + "".join(items) + "</ol>"
    return re.sub(r"<table>.*?</table>", table, h, flags=re.S)


def gloss(h):
    """Codex tables become definition lists: term, plain meaning, picture, why it matters."""
    def table(m):
        t = m.group(0)
        heads = [re.sub("<.*?>", "", c).strip() for c in cells(t, "th")]
        out = []
        for row in re.findall(r"<tr>\s*(<td.*?)</tr>", t, flags=re.S):
            c = cells(row, "td")
            term = re.sub("<.*?>", "", c[0]).strip()
            mean = c[1]
            pic = c[heads.index("Picture")] if "Picture" in heads else ""
            why = c[-1]
            extra = (f' <span class="pic">Picture: {pic}</span>' if pic else "") + f' <span class="why">Why it matters: {why}</span>'
            out.append(f'<div id="g-{slug(term)}"><dt>{term}</dt><dd>{mean}{extra}</dd></div>')
        return '<dl class="gloss">' + "".join(out) + "</dl>"
    return re.sub(r"<table>.*?</table>", table, h, flags=re.S)


def tables_focusable(h):
    return re.sub(r"<table>(.*?)</table>", r'<div class="tablewrap" tabindex="0"><table>\1</table></div>', h, flags=re.S)


def altitude_wrap(h):
    """Split on <h2>; wrap each section as dek (while collapsed) plus body (when open)."""
    parts = re.split(r"(?=<h2>)", h)
    out = [parts[0]]
    n = 0
    for part in parts[1:]:
        m = re.match(r"<h2>(.*?)</h2>", part, flags=re.S)
        title = re.sub("<.*?>", "", m.group(1)).replace("&quot;", '"')
        alt, dek = SPEC.get(title, (3, None))
        rest = part[m.end():]
        n += 1
        if dek is None:
            out.append(f'<div class="sec" data-body-alt="{alt}">{m.group(0)}{rest}</div>')
        else:
            out.append(
                f'<div class="sec" data-body-alt="{alt}">{m.group(0)}<p class="dek">{dek}</p>'
                f'<div class="body" id="b{n}">{rest}</div>'
                f'<button class="more" type="button" aria-controls="b{n}" aria-expanded="false" hidden>Show detail</button></div>'
            )
        if title == "The four stages":
            pass
        if title == "The whole idea, simply":
            out.append("<!--BAR-->")
    return "".join(out)


def linkify(h):
    """Link the first use of each glossary phrase to its codex entry (text nodes in p, li, td, dd only)."""
    done = set()
    pieces = re.split(r"(<[^>]+>)", h)
    stack = []
    skip = {"h1", "h2", "h3", "h4", "a", "button", "dt", "th", "strong", "code"}
    for i, piece in enumerate(pieces):
        if piece.startswith("<"):
            tag = re.match(r"</?\s*([a-zA-Z0-9]+)", piece)
            if tag:
                name = tag.group(1).lower()
                if piece.startswith("</"):
                    if name in stack:
                        while stack and stack.pop() != name:
                            pass
                elif not piece.endswith("/>") and name not in ("br", "hr", "img", "input"):
                    stack.append(name)
            continue
        if any(s in skip for s in stack):
            continue
        for pat, target in GLOSS_LINKS:
            if target in done:
                continue
            m = re.search(rf"\b({pat})\b", piece)
            if m:
                piece = piece[:m.start()] + f'<a class="gl" href="#g-{target}">{m.group(1)}</a>' + piece[m.end():]
                done.add(target)
        pieces[i] = piece
    return "".join(pieces)


def intake_section():
    body = md("10-intake-forms-spec.md")
    body = re.sub(r"<h1>.*?</h1>", "", body, count=1)
    body = tables_focusable(shift(body, 1))
    if TALLY_FORM_ID:
        embed = f'<iframe class="tally" src="https://tally.so/embed/{html.escape(TALLY_FORM_ID)}?hideTitle=1&dynamicHeight=1" title="Intake form" loading="lazy"></iframe>'
    else:
        embed = '<p class="note">The intake form opens here once the NDA is signed. Until then this is a preview of the questions, and nothing on this page collects or sends anything.</p>'
    return body + embed


plan = md("07-plain-language-bundle.md")
plan = altitude_wrap(tables_focusable(stage_rail(plan)))
plan = linkify(plan)
codex = gloss(shift(md("09-translation-codex.md"), 1))
codex = re.sub(r"<h2>The translation codex</h2>", "", codex, count=1)
intake = intake_section()

ladder = "".join(
    f'<li><button type="button" data-level="{n}" aria-label="Level {n}, {name}" aria-pressed="false">'
    f'<span class="dot" aria-hidden="true"></span><span class="nm"><span class="n">{n}</span><span class="w">. {name}</span></span></button></li>'
    for n, name, _, _ in LEVELS
)
descs = {n: {"name": name, "desc": d, "adds": adds} for n, name, d, adds in LEVELS}
bar_html = (
    '<div class="alt" role="group" aria-label="Level of detail"><div class="altrow">'
    '<span class="altlabel">Depth: each step adds to the one before</span>'
    '<span class="stepbtns"><button type="button" class="step" data-dir="-1">Less detail</button>'
    '<button type="button" class="step" data-dir="1">More detail</button></span></div>'
    f'<ol class="ladder">{ladder}</ol><p id="altdesc" class="altdesc" aria-live="polite"></p></div>'
)
plan = plan.replace("<!--BAR-->", bar_html)

LIGHT = {
    "--pg-bg": "#f7f8fa", "--pg-surface": "#ffffff", "--pg-surface2": "#eef1f5",
    "--pg-line": "#d5dbe3", "--pg-edge": "#76808d",
    "--pg-text": "#1c2430", "--pg-muted": "#566170", "--pg-dim": "#475262",
    "--pg-accent": "#00606b", "--pg-accent-bg": "rgba(0,96,107,0.09)",
    "--pg-warn-bg": "#fff3c4", "--pg-warn-edge": "#8a6d00",
}
DARK = {
    "--pg-bg": "var(--bg)", "--pg-surface": "var(--surface)", "--pg-surface2": "#111827",
    "--pg-line": "var(--border)", "--pg-edge": "#5f6f87",
    "--pg-text": "var(--text)", "--pg-muted": "var(--muted)", "--pg-dim": "var(--dimmed)",
    "--pg-accent": "var(--cyan)", "--pg-accent-bg": "var(--cyan-bg)",
    "--pg-warn-bg": "var(--gold-bg)", "--pg-warn-edge": "var(--gold)",
}


def block(d, important=False):
    flag = " !important" if important else ""
    return ";".join(f"{k}:{v}{flag}" for k, v in d.items())


css = tokens + """
:root{--measure:620px;--gut:24px;--font-body:system-ui,-apple-system,'Inter',sans-serif;--font-code:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;--font-head:'Iowan Old Style','Palatino Linotype',Palatino,Georgia,serif;color-scheme:light;%LIGHT%}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){color-scheme:dark;%DARK%}}
:root[data-theme="dark"]{color-scheme:dark;%DARK%}
:root[data-theme="light"]{color-scheme:light;%LIGHT%}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--pg-bg);color:var(--pg-text);font:0.925rem/1.6 var(--font-body)}
::selection{background:var(--pg-accent-bg);color:var(--pg-text)}
.skip{position:absolute;left:-999px;top:0;background:var(--pg-surface);color:var(--pg-text);padding:12px 16px;border:1px solid var(--pg-edge);border-radius:6px;z-index:5}
.skip:focus{left:var(--gut);top:8px}
.wrap{max-width:calc(var(--measure) + 2*var(--gut));margin:0 auto;padding:0 var(--gut) 64px}
nav{border-bottom:1px solid var(--pg-line)}
nav .wrap{display:flex;flex-wrap:wrap;align-items:center;gap:0 20px;padding-top:0;padding-bottom:0}
nav a,.themebtn{display:inline-flex;align-items:center;min-height:44px;color:var(--pg-dim);text-decoration:none;white-space:nowrap}
nav a:hover,nav a:focus-visible{color:var(--pg-accent);text-decoration:underline}
.themebtn{margin-left:auto;font:inherit;background:none;border:0;cursor:pointer;padding:0}
.themebtn:hover{color:var(--pg-accent);text-decoration:underline}
.banner{background:var(--pg-surface2);border:1px solid var(--pg-line);border-radius:6px;padding:10px 14px;margin:20px 0 0;color:var(--pg-dim)}
h1{font-family:var(--font-head);font-size:2.4rem;font-weight:500;line-height:1.2;letter-spacing:-0.02em;margin:32px 0 8px;text-wrap:balance}
h2{font-size:1.15rem;font-weight:600;line-height:1.25;letter-spacing:-0.01em;margin:48px 0 12px;color:var(--pg-accent);text-wrap:balance}
h3{font-size:0.925rem;font-weight:700;line-height:1.3;margin:24px 0 8px}
p,li{max-width:none;text-wrap:pretty}
a{color:var(--pg-accent);text-underline-offset:3px}
a.gl{text-decoration-style:dotted}
code{font-family:var(--font-code);font-size:.9em}
.sec{margin:0}
.dek{margin:4px 0 8px}
.more{font:inherit;color:var(--pg-text);background:var(--pg-surface);border:1px solid var(--pg-edge);border-radius:6px;padding:0 14px;min-height:44px;cursor:pointer;margin:4px 0 0}
.more:hover{border-color:var(--pg-accent);color:var(--pg-accent)}
.alt{position:sticky;top:0;background:var(--pg-bg);border-top:1px solid var(--pg-line);border-bottom:1px solid var(--pg-line);z-index:2;padding:8px 0;margin:24px 0 8px}
.altrow{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:4px 16px}
.altlabel{color:var(--pg-muted)}
.stepbtns{display:flex;gap:6px}
.step{font:inherit;color:var(--pg-text);background:var(--pg-surface);border:1px solid var(--pg-edge);border-radius:6px;padding:0 14px;min-height:44px;cursor:pointer}
.step:hover:not(:disabled){border-color:var(--pg-accent);color:var(--pg-accent)}
.step:disabled{opacity:.45;cursor:default}
.ladder{list-style:none;margin:6px 0 4px;padding:0;display:flex}
.ladder li{flex:1 1 0;min-width:0;position:relative;text-align:center}
.ladder li::before{content:"";position:absolute;top:7px;left:-50%;width:100%;height:2px;background:var(--pg-edge)}
.ladder li:first-child::before{display:none}
.ladder li.on::before{background:var(--pg-accent)}
.ladder button{font:inherit;color:var(--pg-muted);background:none;border:0;padding:0 2px;cursor:pointer;position:relative;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;gap:4px;width:100%;min-height:44px}
.ladder .dot{width:16px;height:16px;border-radius:50%;border:2px solid var(--pg-edge);background:var(--pg-bg)}
.ladder li.on .dot{background:var(--pg-accent);border-color:var(--pg-accent)}
.ladder li.on button{color:var(--pg-text)}
.ladder button[aria-pressed="true"]{color:var(--pg-accent);font-weight:700}
.ladder button[aria-pressed="true"] .dot{box-shadow:0 0 0 3px var(--pg-accent-bg)}
.altdesc{color:var(--pg-dim);margin:2px 0 0}
a:focus-visible,button:focus-visible,.tablewrap:focus-visible{outline:2px solid var(--pg-accent);outline-offset:2px}
.rail{list-style:none;margin:16px 0;padding:0}
.stage{padding:16px 0;border-top:1px solid var(--pg-line)}
.stage:last-child{border-bottom:1px solid var(--pg-line)}
.stage h3{margin:0 0 8px;font-size:1.15rem;font-weight:600;color:var(--pg-text)}
.row{margin:0 0 10px}
.row p{margin:0}
.lbl{display:block;color:var(--pg-muted);margin:0 0 2px}
.gloss{margin:8px 0 24px}
.gloss>div{display:grid;grid-template-columns:11rem 1fr;gap:4px 16px;padding:10px 0;border-top:1px solid var(--pg-line)}
.gloss dt{font-weight:600}
.gloss dd{margin:0}
.gloss .pic{display:block;font-style:italic;color:var(--pg-dim)}
.gloss .why{display:block;color:var(--pg-dim)}
.tablewrap{overflow-x:auto;margin:16px 0}
table{border-collapse:collapse;width:100%}
th,td{border:1px solid var(--pg-line);padding:10px 12px;text-align:left;vertical-align:top}
th{background:var(--pg-surface2);color:var(--pg-dim);font-weight:600}
.note{background:var(--pg-surface);border:1px solid var(--pg-line);border-radius:6px;padding:12px 16px;color:var(--pg-dim)}
iframe.tally{width:100%;min-height:640px;border:1px solid var(--pg-edge);border-radius:6px;background:var(--pg-surface)}
.sec,[id^="g-"]{scroll-margin-top:11rem}
.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
[hidden]:not([hidden="until-found"]){display:none !important}
@media (max-width:600px){h1{font-size:1.5rem}.gloss>div{grid-template-columns:1fr}.ladder .w{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}.altlabel{display:none}.sec,[id^="g-"]{scroll-margin-top:9rem}}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
@media print{:root,:root[data-theme]{%LIGHT_IMP%}[hidden]{display:block !important;content-visibility:visible !important}.alt,.more,.themebtn,nav,.skip{display:none !important}}
""".replace("%LIGHT_IMP%", block(LIGHT, True)).replace("%LIGHT%", block(LIGHT)).replace("%DARK%", block(DARK))

HEAD_JS = """(function(){try{var t=localStorage.getItem('myAllyTheme');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();"""

JS = """
(function(){
  var DESC=__DESC__;
  var level=__DEFAULT__,over=new Set();
  try{var v=parseInt(localStorage.getItem('myAllyLevel'),10);if(v>=1&&v<=5)level=v;}catch(e){}
  var secs=[].slice.call(document.querySelectorAll('.sec'));
  function isOpen(i){var s=secs[i];var need=parseInt(s.getAttribute('data-body-alt'),10);return !s.querySelector('.body')||level>=need||over.has(i);}
  function apply(){
    secs.forEach(function(sec,i){
      var need=parseInt(sec.getAttribute('data-body-alt'),10);
      var hasBody=!!sec.querySelector('.body');
      var open=isOpen(i);
      var dek=sec.querySelector('.dek'),body=sec.querySelector('.body'),more=sec.querySelector('.more');
      if(dek)dek.hidden=open&&hasBody;
      if(body){if(open)body.removeAttribute('hidden');else body.setAttribute('hidden','until-found');}
      if(more){more.hidden=level>=need;more.textContent=over.has(i)?'Hide detail':'Show detail';more.setAttribute('aria-expanded',over.has(i)?'true':'false');}
      [].forEach.call(sec.querySelectorAll('[data-alt]'),function(el){
        var a=parseInt(el.getAttribute('data-alt'),10);
        el.hidden=!(over.has(i)?true:level>=a);
      });
    });
    [].forEach.call(document.querySelectorAll('.ladder button'),function(b){
      var n=parseInt(b.getAttribute('data-level'),10);
      b.setAttribute('aria-pressed',String(n===level));
      b.parentNode.className=n<=level?'on':'';
    });
    [].forEach.call(document.querySelectorAll('.step'),function(b){
      var d=parseInt(b.getAttribute('data-dir'),10);
      b.disabled=(d<0&&level<=1)||(d>0&&level>=5);
    });
    var cur=DESC[level],nxt=DESC[level+1];
    document.getElementById('altdesc').textContent='Level '+level+' of 5, '+cur.name+': '+cur.desc+(nxt?' Next step adds '+nxt.adds+'.':' This is the full detail.');
  }
  function setLevel(n){level=Math.max(1,Math.min(5,n));over.clear();try{localStorage.setItem('myAllyLevel',String(level));}catch(e){}apply();}
  [].forEach.call(document.querySelectorAll('.ladder button'),function(b){b.addEventListener('click',function(){setLevel(parseInt(b.getAttribute('data-level'),10));});});
  [].forEach.call(document.querySelectorAll('.step'),function(b){b.addEventListener('click',function(){setLevel(level+parseInt(b.getAttribute('data-dir'),10));});});
  secs.forEach(function(sec,i){
    var more=sec.querySelector('.more'),body=sec.querySelector('.body');
    if(more)more.addEventListener('click',function(){if(over.has(i))over.delete(i);else over.add(i);apply();});
    if(body)body.addEventListener('beforematch',function(){over.add(i);apply();});
  });
  function secFor(t){if(!t)return -1;var s=t.classList&&t.classList.contains('sec')?t:(t.querySelector&&t.querySelector('.sec'))||t.closest('.sec');return secs.indexOf(s);}
  function go(id,push){
    var t=document.getElementById(id);if(!t)return false;
    var i=secFor(t);if(i>-1&&!isOpen(i)){over.add(i);apply();}
    setTimeout(function(){t.scrollIntoView();},0);
    if(push&&history.pushState){history.pushState(null,'','#'+id);}
    return true;
  }
  document.addEventListener('click',function(e){
    var a=e.target.closest&&e.target.closest('a[href^="#"]');if(!a)return;
    var id=a.getAttribute('href').slice(1);if(go(id,true))e.preventDefault();
  });
  var root=document.documentElement,tb=document.getElementById('themebtn');
  function eff(){var t=root.getAttribute('data-theme');if(t)return t;return window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';}
  function label(){tb.textContent=eff()==='dark'?'Light mode':'Dark mode';}
  tb.addEventListener('click',function(){var n=eff()==='dark'?'light':'dark';root.setAttribute('data-theme',n);try{localStorage.setItem('myAllyTheme',n);}catch(e){}label();});
  label();
  apply();
  if(location.hash.length>1)go(location.hash.slice(1),false);
})();
""".replace("__DESC__", json.dumps(descs)).replace("__DEFAULT__", str(DEFAULT_LEVEL))

banner = "" if SEND else '<div class="banner" role="note">Draft for Zach to review. Not sent. No prices appear because none are agreed.</div>'

page = f"""<!doctype html>
<!-- KINTSUGI SEAMS (booked in _PATTERNS/kintsugi-visual-grammar-seams.md, 2026-10-08)
 1. First build was dark-only, card-walled, with two stacked sticky bars and sub-44px targets: repaired to a light-default theme with a dark toggle, a stage rail and glossary list, one sticky bar, 44px targets.
 2. Light theme colours sit outside DESIGN.md (dark-only): scoped design-system-color exemption for this file only.
-->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="robots" content="noindex">
<title>My Ally LD plan</title>
<script>{HEAD_JS}</script>
<noscript><style>.alt,.more,.themebtn{{display:none}}.dek{{display:none}}</style></noscript>
<style>{css}</style>
</head>
<body>
<a class="skip" href="#main">Skip to the plan</a>
<nav aria-label="Sections"><div class="wrap"><a href="#plan">The plan</a><a href="#codex">Translation codex</a><a href="#intake">Intake</a><button type="button" class="themebtn" id="themebtn">Dark mode</button></div></nav>
<main class="wrap" id="main">
{banner}
<section id="plan">{plan}</section>
<section id="codex"><div class="sec" data-body-alt="5"><h2>Translation codex</h2><p class="dek">A legend for the technical words, each with a plain meaning, a picture and why it matters to you.</p><div class="body" id="bcodex">{codex}</div><button class="more" type="button" aria-controls="bcodex" aria-expanded="false" hidden>Show detail</button></div></section>
<section id="intake"><div class="sec" data-body-alt="4"><h2>Intake</h2><p class="dek">Four short sets of questions about what I would like to see: links and descriptions only, once the NDA is signed.</p><div class="body" id="bintake">{intake}</div><button class="more" type="button" aria-controls="bintake" aria-expanded="false" hidden>Show detail</button></div></section>
</main>
<script>{JS}</script>
</body>
</html>
"""

# Guard (kintsugi seam, 2026-10-08): the build fails if internal-only or house-banned strings reach visible copy.
_vis = re.sub(r"<(style|script)\b.*?</\1>", "", page, flags=re.S)
_vis = re.sub(r"<!--.*?-->", "", _vis, flags=re.S)
_vis = re.sub(r"<[^>]+>", " ", _vis)
_banned = [".md", "asm-", "ADR-", "P0.", "GRAIN", "DEGRADED", "TBD", "\u2014", "\u2013", "$"]
_hits = [b for b in _banned if b in _vis]
if SEND and "Draft for Zach" in _vis:
    _hits.append("Draft for Zach")
if _hits:
    raise SystemExit(f"build_proposal_view: banned strings in visible copy: {_hits}")
out = HERE / "proposal-view.html"
out.write_text(page, encoding="utf-8")
print("wrote", out.relative_to(ROOT), len(page), "bytes")
