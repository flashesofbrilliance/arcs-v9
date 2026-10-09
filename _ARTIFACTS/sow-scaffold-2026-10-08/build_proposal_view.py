#!/usr/bin/env python3
"""build_proposal_view.py: generate proposal-view.html from 07, 09 and 10 (single source = the markdown).

Run from the repo root:  python3 _ARTIFACTS/sow-scaffold-2026-10-08/build_proposal_view.py

SEND = False keeps the "draft for Zach" strip; set True only when Zach has said yes to sending.
TALLY_FORM_URL: the published Tally share link (linked out, never embedded). Empty = the checklist says the link is coming.
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
TALLY_FORM_URL = "https://tally.so/r/xXkrP5"
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
    "What is in scope, and what the audit could change": (2, "I cannot know what stage 1 will show, so here are three general cases, best, base and worst, with the steps in scope for each. They are not predictions, and nothing is priced."),
    "For Kelly": (3, "Your plan and the build side by side, cost per family in three cases, and the lists that make the empathy question testable."),
    "For Chelsea": (3, "You stay the builder. The AI provider choice waits for the facts, and Alice comes after the groundwork."),
    "My view on Alice": (3, "I would hold off connecting Alice until three answers are in. A small trial on made-up data is the cheaper way to learn what she costs."),
    "Questions to settle with your lawyers first": (4, "Turn warm-but-never-health-advice into three written lists with your lawyers, then test Alice against sample questions."),
    "How I would approach \"will this work?\"": (4, "Before important work, the owner writes down confidence, a cap on time and money, what worked and failed look like, and what a miss would cost."),
    "A possibility I want to name early: setup that depends on what I find": (4, "Some set-up can only be scoped after I look. It is priced only if it is needed."),
    "The cost, in three buckets": (3, "Fixed, grows with use, and hidden, each as a best, likely and worst case. Nothing is priced yet."),
    "What I need from you, and what you can expect from me": (3, "From you: the NDA, the code, the plan, your cost model and a list of services. From me: dated findings and early notice when anything moves."),
    "What I know, what I think, what I am guessing": (3, "I say which points I know, which I think and which I am guessing."),
    "Two-week rhythm": (3, "A short planning call, three-line check-ins, and a board that shows who is waiting on whom."),
    "Optional: office hours": (3, "A small prepaid block of my time for your team: a thinking partner, help getting unstuck, or learning a way of working. Separate from the audit, and your choice."),
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
    (r"roadmap", "roadmap"),
    (r"checkpoints?", "checkpoint"),
    (r"imagine it failed", "imagine-it-failed-exercise"),
    (r"cap on AI spending|spending cap", "usage-cap"),
    (r"backups?", "backup-and-restore-test"),
    (r"scope", "scope"),
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
            return t
        alt = {"What happens, in plain terms": 2, "What you get": 2, "How you will know it worked": 3, "If it does not work": 3}
        order = ["What happens, in plain terms", "What you get", "How you will know it worked", "If it does not work"]
        items = []
        for row in re.findall(r"<tr>\s*(<td.*?)</tr>", t, flags=re.S):
            c = cells(row, "td")
            parts = ""
            for name in order:
                parts += f'<div class="row" data-alt="{alt[name]}"><span class="lbl">{name}</span><p>{c[heads.index(name)]}</p></div>'
            num = re.match(r"\s*(\d)", re.sub("<.*?>", "", c[0]))
            sid = f' id="stage-{num.group(1)}"' if num else ""
            items.append(f'<li class="stage"{sid}><h3>{c[0]}</h3>{parts}</li>')
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
    """Scrollable tables get a name and keyboard focus; header cells get scope so screen readers announce columns."""
    def wrap(m):
        t = m.group(0)
        heads = [re.sub("<.*?>", "", c).strip() for c in cells(t, "th")]
        label = html.escape("Table: " + ", ".join(heads)) if heads else "Table"
        t = t.replace("<th>", '<th scope="col">').replace("<th ", '<th scope="col" ')
        return f'<div class="tablewrap" tabindex="0" role="region" aria-label="{label}">{t}</div>'
    return re.sub(r"<table>.*?</table>", wrap, h, flags=re.S)



def scope_view(h):
    """The best/base/worst table becomes a case switcher with one anchor per step; without JavaScript all three cases show."""
    def table(m):
        t = m.group(0)
        heads = [re.sub("<.*?>", "", c).strip() for c in cells(t, "th")]
        if heads != ["Step", "Best case", "Base case", "Worst case"]:
            return m.group(0)
        items = []
        for row in re.findall(r"<tr>\s*(<td.*?)</tr>", t, flags=re.S):
            c = cells(row, "td")
            title = re.sub("<.*?>", "", c[0]).strip()
            num = re.match(r"(\d)\.", title)
            top = bool(num)
            target = f"#stage-{num.group(1)}" if num else "#stage-3"
            cases = "".join(
                f'<span class="c c-{k}"><b>{lab}:</b> {c[i + 1]}</span>'
                for i, (k, lab) in enumerate((("best", "Best case"), ("base", "Base case"), ("worst", "Worst case")))
            )
            items.append(f'<li class="{"sstep" if top else "ssub"}"><a href="{target}">{title}</a>{cases}</li>')
        bar = ('<div class="scopebar" role="group" aria-label="Which case to show"><span class="altlabel">If the audit finds the:</span>'
               '<button type="button" data-case="best" aria-pressed="false">Best case</button>'
               '<button type="button" data-case="base" aria-pressed="true">Base case</button>'
               '<button type="button" data-case="worst" aria-pressed="false">Worst case</button></div>')
        return f'<div class="scope" data-case="base">{bar}<p class="vh" id="scopelive" aria-live="polite"></p><ol class="scopelist">{"".join(items)}</ol></div>'
    return re.sub(r"<table>.*?</table>", table, h, flags=re.S)

SECTION_TITLES = {}


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
        sid = "s-" + slug(title)
        SECTION_TITLES[sid] = title
        if dek is None:
            out.append(f'<div class="sec" id="{sid}" data-body-alt="{alt}">{m.group(0)}{rest}</div>')
        else:
            out.append(
                f'<div class="sec" id="{sid}" data-body-alt="{alt}">{m.group(0)}<p class="dek">{dek}</p>'
                f'<div class="body" id="b{n}">{rest}</div>'
                f'<button class="more" type="button" aria-controls="b{n}" aria-expanded="false" hidden>Show detail</button></div>'
            )
        if title == "The four stages":
            pass
        if title == "The whole idea, simply":
            out.append("<!--BAR-->")
    return "".join(out)


def gloss_data(codex_html):
    """slug -> (term, plain meaning, picture) read from the rendered codex, so the popups share one source."""
    data = {}
    for m in re.finditer(r'<div id="g-([a-z0-9-]+)"><dt>(.*?)</dt><dd>(.*?)</dd></div>', codex_html, flags=re.S):
        slug_, term, dd = m.groups()
        mean = re.split(r'\s*<span class="pic">', dd)[0]
        pic = re.search(r'<span class="pic">Picture: (.*?)</span>', dd, flags=re.S)
        data[slug_] = (re.sub("<.*?>", "", term).strip(), mean.strip(), pic.group(1).strip() if pic else "")
    return data


def first_sentence(text):
    plain = re.sub("<.*?>", "", text).strip()
    m = re.match(r"(.+?[.!?])(\s|$)", plain)
    return m.group(1) if m else plain


def linkify(h, data):
    """First use of each glossary phrase in each section becomes a term with a definition popup (hover, focus, tap)."""
    done = set()
    count = [0]
    uses = {}
    cur = [None]
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
                else:
                    if name == "h2":
                        done = set()
                    idm = re.search(r'class="sec" id="(s-[a-z0-9-]+)"', piece)
                    if idm:
                        cur[0] = idm.group(1)
                    if not piece.endswith("/>") and name not in ("br", "hr", "img", "input"):
                        stack.append(name)
            continue
        if any(s in skip for s in stack):
            continue
        for pat, target in GLOSS_LINKS:
            if target in done or target not in data:
                continue
            m = re.search(rf"\b({pat})\b", piece)
            if m:
                term, mean, pic = data[target]
                count[0] += 1
                n = count[0]
                if cur[0]:
                    uses.setdefault(target, []).append(cur[0])
                tip = (
                    f'<span class="tip" id="tip{n}" role="group" aria-label="Definition: {html.escape(term)}" hidden>'
                    f'<b>{html.escape(term)}</b> {html.escape(first_sentence(mean))}'
                    f'<span class="tipbar"><a class="tipgo" href="#g-{target}">Learn more</a>'
                    f'<button type="button" class="tipclose" aria-label="Close definition: {html.escape(term)}">Close</button></span>'
                    f'<span class="tiphint">Click the word to keep this open</span></span>'
                )
                piece = (
                    piece[:m.start()]
                    + f'<span class="termwrap"><a class="gl" href="#g-{target}" aria-describedby="tip{n}" aria-expanded="false">{m.group(1)}</a>{tip}</span>'
                    + piece[m.end():]
                )
                done.add(target)
        pieces[i] = piece
    return "".join(pieces), uses


def intake_section():
    body = md("10-intake-forms-spec.md")
    body = re.sub(r"<h1>.*?</h1>", "", body, count=1)
    body = tables_focusable(shift(body, 1))
    if TALLY_FORM_URL:
        form = f'<a href="{html.escape(TALLY_FORM_URL)}" target="_blank" rel="noopener">Open the intake form (opens in a new tab)</a>'
    else:
        form = "The intake form link arrives with my email once the NDA is in place"
    steps = [
        "Send your NDA. Mutual, please, so it protects both sides.",
        f"{form}. About 10 minutes for the first page; the later pages are optional.",
        "Upload the signed NDA and the build spec on the form's first page, right after your name. No family or child information.",
        "Pick a time to talk it through, Leah included if she is up for it. Rather talk than type? Reply to my email and I will fill the form in for you.",
        "I send a short written proposal with a clear scope and rate, plus an optional block of office hours for your team.",
    ]
    embed = ('<h3 id="next-steps">Five steps</h3><ol class="checklist">'
             + "".join(f"<li>{t}</li>" for t in steps) + "</ol>"
             '<p class="note">The questions below are a preview. Nothing on this page collects or sends anything.</p>')
    return embed + body


plan = md("07-plain-language-bundle.md")
plan = altitude_wrap(tables_focusable(scope_view(stage_rail(plan))))

quick = (
    '<nav class="quicksteps" aria-label="Jump to a step"><span class="altlabel">Jump to a step:</span><ol>'
    '<li><a href="#stage-1">1 Look and listen</a></li><li><a href="#stage-2">2 Agree the plan</a></li>'
    '<li><a href="#stage-3">3 Make it solid</a></li><li><a href="#stage-4">4 Aim higher</a></li></ol></nav>'
)
_anchor = '<div class="sec" id="s-the-short-version"'
assert _anchor in plan, "quick steps anchor missing"
plan = plan.replace(_anchor, quick + _anchor, 1)
codex_pre = gloss(shift(md("09-translation-codex.md"), 1))
plan, term_uses = linkify(plan, gloss_data(codex_pre))
codex = codex_pre
for slug_, secs_ in term_uses.items():
    links = ", ".join(f'<a href="#{s}">{html.escape(SECTION_TITLES[s])}</a>' for s in secs_)
    codex = re.sub(rf'(<div id="g-{slug_}">.*?)(</dd></div>)', lambda m: m.group(1) + f' <span class="uses">Used in this plan: {links}.</span>' + m.group(2), codex, count=1, flags=re.S)
codex = re.sub(r"<h2>The translation codex</h2>", "", codex, count=1)
intake = intake_section()

ticks = "".join(f'<span class="tick" style="--f:{(n - 1) / 4}" aria-hidden="true"></span>' for n, *_ in LEVELS)
names = "".join(
    f'<button type="button" class="tname" data-level="{n}" tabindex="-1" aria-hidden="true"><span class="n">{n}</span><span class="w">. {name}</span></button>'
    for n, name, _, _ in LEVELS
)
descs = {n: {"name": name, "desc": d, "adds": adds} for n, name, d, adds in LEVELS}
bar_html = (
    '<div class="alt" role="group" aria-label="Level of detail">'
    '<span class="altlabel" id="altlabel">Depth: slide to show more or less detail</span>'
    '<div class="slider"><div class="ticks">' + ticks + '</div>'
    '<input type="range" id="depth" min="1" max="5" step="1" value="' + str(DEFAULT_LEVEL) + '" aria-labelledby="altlabel" aria-describedby="altdesc">'
    '<div class="tnames">' + names + '</div></div>'
    '<p id="altdesc" class="altdesc" aria-live="polite"></p></div>'
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
header.top{position:sticky;top:0;z-index:20;background:var(--pg-bg);border-bottom:1px solid var(--pg-line)}
header.top nav{border-bottom:0}
header.top .wrap{padding-bottom:0;max-width:1200px}
.bar{display:flex;align-items:center;flex-wrap:wrap;gap:8px 16px;min-height:56px;padding-top:6px;padding-bottom:6px}
.brand{display:inline-flex;align-items:baseline;gap:0.6em;min-height:44px;align-items:center;text-decoration:none;font-family:var(--font-mono);font-size:0.925rem;text-transform:uppercase;white-space:nowrap}
.wa{color:var(--pg-accent);font-weight:800;letter-spacing:0.22em}.wf{color:var(--pg-dim);letter-spacing:0.14em}
.links{margin-left:auto;display:flex;flex-wrap:wrap;gap:8px}
header.top .pill{flex:none;display:inline-flex;align-items:center;min-height:44px;padding:0 14px;font-family:var(--font-mono);font-size:0.925rem;letter-spacing:0.08em;text-transform:uppercase;color:var(--pg-dim);background:var(--pg-surface);border:1px solid var(--pg-line);border-radius:6px;text-decoration:none;cursor:pointer;white-space:nowrap}
header.top .pill:hover,header.top .pill:focus-visible{color:var(--pg-accent);border-color:var(--pg-accent);text-decoration:none}
header.top .pill.icon{width:44px;padding:0;justify-content:center}
header.top .pill.primary{color:var(--pg-accent);border-color:var(--pg-accent);background:var(--pg-accent-bg)}
nav .wrap{display:flex;flex-wrap:wrap;align-items:center;gap:0 20px;padding-top:0;padding-bottom:0}
nav a,.themebtn{display:inline-flex;align-items:center;justify-content:center;min-height:44px;min-width:44px;color:var(--pg-dim);text-decoration:none;white-space:nowrap}
nav a:hover,nav a:focus-visible{color:var(--pg-accent);text-decoration:underline}
.themebtn{margin-left:auto;font:inherit;background:none;border:0;cursor:pointer;padding:0}
.themebtn:hover{color:var(--pg-accent);text-decoration:underline}
.banner{background:var(--pg-surface2);border:1px solid var(--pg-line);border-radius:6px;padding:10px 14px;margin:20px 0 0;color:var(--pg-dim)}
h1{font-family:var(--font-head);font-size:2.4rem;font-weight:500;line-height:1.2;letter-spacing:-0.02em;margin:32px 0 8px;text-wrap:balance}
h2{font-size:1.15rem;font-weight:600;line-height:1.25;letter-spacing:-0.01em;margin:48px 0 12px;color:var(--pg-accent);text-wrap:balance}
h3{font-size:0.925rem;font-weight:700;line-height:1.3;margin:24px 0 8px}
p,li{max-width:none;text-wrap:pretty}
a{color:var(--pg-accent);text-underline-offset:3px}
code{font-family:var(--font-code);font-size:.9em}
.sec{margin:0}
.dek{margin:4px 0 8px}
.more{font:inherit;color:var(--pg-text);background:var(--pg-surface);border:1px solid var(--pg-edge);border-radius:6px;padding:0 14px;min-height:44px;cursor:pointer;margin:4px 0 0}
.more:hover{border-color:var(--pg-accent);color:var(--pg-accent)}
.alt{position:sticky;top:0;background:var(--pg-bg);border-top:1px solid var(--pg-line);border-bottom:1px solid var(--pg-line);z-index:2;padding:8px 12px 6px;margin:24px 0 8px}
.altlabel{color:var(--pg-muted)}
.slider{position:relative;margin:4px 0 0;height:76px}
.slider input[type=range]{position:absolute;left:calc(10% - 12px);width:calc(80% + 24px);top:-4px;height:44px;margin:0;background:transparent;-webkit-appearance:none;appearance:none;cursor:pointer;z-index:1}
.slider input[type=range]::-webkit-slider-runnable-track{height:4px;border-radius:3px;background:linear-gradient(var(--pg-accent),var(--pg-accent)) 0/var(--fill,50%) 100% no-repeat,var(--pg-edge)}
.slider input[type=range]::-moz-range-track{height:4px;border-radius:3px;background:var(--pg-edge)}
.slider input[type=range]::-moz-range-progress{height:4px;border-radius:3px;background:var(--pg-accent)}
.slider input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;appearance:none;width:24px;height:24px;margin-top:-10px;border-radius:50%;background:var(--pg-accent);border:3px solid var(--pg-bg);box-shadow:0 0 0 1px var(--pg-accent)}
.slider input[type=range]::-moz-range-thumb{width:18px;height:18px;border-radius:50%;background:var(--pg-accent);border:3px solid var(--pg-bg);box-shadow:0 0 0 1px var(--pg-accent)}
.slider input[type=range]:focus-visible{outline:none}
.slider input[type=range]:focus-visible::-webkit-slider-thumb{box-shadow:0 0 0 3px var(--pg-bg),0 0 0 5px var(--pg-accent)}
.slider input[type=range]:focus-visible::-moz-range-thumb{box-shadow:0 0 0 3px var(--pg-bg),0 0 0 5px var(--pg-accent)}
.ticks{position:absolute;left:0;right:0;top:12px;height:12px;pointer-events:none}
.tick{position:absolute;top:0;width:2px;height:12px;margin-left:-1px;background:var(--pg-edge);left:calc(10% + 80% * var(--f))}
.tnames{position:absolute;left:0;right:0;top:30px;display:flex}
.tname{flex:1 1 0;min-width:0;min-height:44px;font:inherit;color:var(--pg-muted);background:none;border:0;padding:6px 2px;cursor:pointer;text-align:center}
.tname:hover{color:var(--pg-accent);text-decoration:underline}
.tname.on{color:var(--pg-accent);font-weight:700}
.altdesc{color:var(--pg-dim);margin:2px 0 0}
.quicksteps{display:flex;flex-wrap:wrap;align-items:center;gap:0 14px;margin:20px 0 0}
.quicksteps ol{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:0 4px}
.quicksteps a{display:inline-flex;align-items:center;min-height:44px;padding:0 10px;border:1px solid var(--pg-edge);border-radius:6px;margin:4px 0;color:var(--pg-text);text-decoration:none;background:var(--pg-surface)}
.quicksteps a:hover{border-color:var(--pg-accent);color:var(--pg-accent)}
.termwrap{position:relative;display:inline}
a.gl{text-decoration:underline dotted;text-underline-offset:3px;cursor:pointer}
a.gl::after{content:"";display:inline-block;width:5px;height:5px;margin:0 2px 2px 5px;border-right:1.5px solid currentColor;border-bottom:1.5px solid currentColor;transform:rotate(45deg);}
a.gl:hover,a.gl[aria-expanded="true"]{background:var(--pg-accent-bg);text-decoration-style:solid}
a.gl[aria-expanded="true"]::after{transform:rotate(-135deg);margin-bottom:-1px}
.tipbar{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:4px}
.tipclose{display:none;font:inherit;color:var(--pg-text);background:none;border:1px solid var(--pg-edge);border-radius:6px;padding:0 10px;min-height:32px;cursor:pointer}
.termwrap.pinned .tipclose{display:inline-block}
.tiphint{display:none;color:var(--pg-muted);margin-top:2px}
@media (hover:hover) and (pointer:fine){.termwrap:not(.pinned) .tiphint{display:block}}
.tip{position:absolute;z-index:3;left:0;top:calc(100% + 6px);width:max-content;max-width:min(280px,calc(100vw - 32px));background:var(--pg-surface);color:var(--pg-text);border:1px solid var(--pg-edge);border-radius:6px;padding:10px 12px;box-shadow:0 2px 8px rgba(0,0,0,.14);text-align:left;font-weight:400;font-style:normal;white-space:normal}
.tip.flip{left:auto;right:0}
.tip b{display:block;margin:0 0 2px}
.tip a.tipgo{display:inline-block;padding:4px 0;min-height:28px;font-weight:600}
.optbtn{margin-left:0}
#themebtn{margin-left:0}
.readfab{position:fixed;right:16px;bottom:16px;z-index:4;width:48px;height:48px;border-radius:999px;border:1px solid var(--pg-edge);background:var(--pg-surface);color:var(--pg-text);font:inherit;font-weight:700;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.14)}
.readfab:hover{border-color:var(--pg-accent);color:var(--pg-accent)}
.readopts{position:fixed;right:16px;bottom:76px;z-index:4;width:min(360px,calc(100vw - 32px));max-height:calc(100vh - 100px);max-height:calc(100dvh - 100px);overflow:auto;background:var(--pg-surface);color:var(--pg-text);border:1px solid var(--pg-edge);border-radius:6px;padding:14px 16px;box-shadow:0 2px 8px rgba(0,0,0,.14)}
.ro-title{margin:0 0 4px;font-weight:700}
.ro-note{margin:0 0 10px;color:var(--pg-dim)}
.ro-group{margin:0 0 12px}
.ro-label{display:block;color:var(--pg-muted);margin:0 0 4px}
.ro-btns{display:flex;flex-wrap:wrap;gap:6px}
.ro-hint{display:block;color:var(--pg-muted);margin-top:4px}
.ro-btns button,.ro-actions button{font:inherit;color:var(--pg-text);background:var(--pg-surface);border:1px solid var(--pg-edge);border-radius:6px;padding:0 14px;min-height:44px;cursor:pointer}
.ro-btns button[aria-pressed="true"]{border-color:var(--pg-accent);color:var(--pg-accent);background:var(--pg-accent-bg);font-weight:700}
.ro-actions{display:flex;gap:8px;justify-content:flex-end;margin-top:4px}
html[data-font="easy"]{--font-body:Verdana,Tahoma,'Trebuchet MS',Arial,sans-serif}
html[data-font="easy"] h1{font-family:var(--font-body);font-weight:700}
html[data-font="easy"] *{font-style:normal !important}
html[data-font="easy"] a.gl{text-decoration:none;background:var(--pg-accent-bg)}
html[data-font="easy"] a,html[data-font="easy"] .scopelist a{text-decoration:none}
html[data-size="l"]{font-size:112.5%;--measure:700px}
html[data-size="xl"]{font-size:125%;--measure:780px}
html[data-space="roomy"] :is(p,li,dd,dt,td,th,.dek,.lbl,.c,.altdesc,.tip){line-height:1.8;letter-spacing:.04em;word-spacing:.14em}
html[data-space="roomy"] :is(p,li){margin-bottom:1.1em}
@media (prefers-color-scheme: light){html[data-tone="warm"]:not([data-theme="dark"]){--pg-bg:#fbf6e9;--pg-surface:#fffdf6;--pg-surface2:#f3ecda}}
html[data-tone="warm"][data-theme="light"]{--pg-bg:#fbf6e9;--pg-surface:#fffdf6;--pg-surface2:#f3ecda}
.pagefoot{padding-top:0;padding-bottom:96px;color:var(--pg-dim)}
[tabindex="-1"]:focus{outline:none}
@media (prefers-contrast:more){:root{--pg-muted:var(--pg-text);--pg-dim:var(--pg-text);--pg-line:var(--pg-edge)}}
@media (forced-colors:active){
  .alt,.tip,.readopts,.readfab,.scopebar button,.step,.more,.quicksteps a{border:1px solid CanvasText}
  .slider input[type=range]::-webkit-slider-thumb{background:Highlight;border:2px solid CanvasText}
  .slider input[type=range]::-moz-range-thumb{background:Highlight;border:2px solid CanvasText}
  .slider input[type=range]::-webkit-slider-runnable-track,.slider input[type=range]::-moz-range-track{background:CanvasText}
  .tick{background:CanvasText}
  a.gl{text-decoration:underline}
  .tname.on,.scopebar button[aria-pressed="true"],.ro-btns button[aria-pressed="true"]{outline:2px solid Highlight}
}
.scope{margin:16px 0}
.scopebar{display:flex;flex-wrap:wrap;align-items:center;gap:6px 8px;margin:0 0 8px}
.scopebar button{font:inherit;color:var(--pg-text);background:var(--pg-surface);border:1px solid var(--pg-edge);border-radius:6px;padding:0 14px;min-height:44px;cursor:pointer}
.scopebar button[aria-pressed="true"]{border-color:var(--pg-accent);color:var(--pg-accent);background:var(--pg-accent-bg);font-weight:700}
.scopelist{list-style:none;margin:0;padding:0}
.scopelist li{padding:10px 0;border-top:1px solid var(--pg-line)}
.scopelist li:last-child{border-bottom:1px solid var(--pg-line)}
.scopelist .sstep a{font-weight:700}
.scopelist .ssub{padding-left:20px}
.scopelist a{display:inline-block;margin:0 0 2px}
.c{display:block;color:var(--pg-dim)}
.c b{display:none}
.scope:not(.js) .c b{display:inline;color:var(--pg-muted);font-weight:600}
.scope.js[data-case="best"] .c-base,.scope.js[data-case="best"] .c-worst,.scope.js[data-case="base"] .c-best,.scope.js[data-case="base"] .c-worst,.scope.js[data-case="worst"] .c-best,.scope.js[data-case="worst"] .c-base{display:none}
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
.gloss .uses{display:block;color:var(--pg-dim);margin-top:4px}
.flash{background:var(--pg-accent-bg);}
.tablewrap{overflow-x:auto;margin:16px 0}
table{border-collapse:collapse;width:100%}
th,td{border:1px solid var(--pg-line);padding:10px 12px;text-align:left;vertical-align:top}
th{background:var(--pg-surface2);color:var(--pg-dim);font-weight:600}
.checklist{margin:0 0 16px;padding-left:1.4em}.checklist li{margin:0 0 8px}
.note{background:var(--pg-surface);border:1px solid var(--pg-line);border-radius:6px;padding:12px 16px;color:var(--pg-dim)}
.sec,section[id],[id^="g-"],[id^="s-"],.stage{scroll-margin-top:calc(var(--sticky-h, 12rem) + 16px)}
.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
[hidden]:not([hidden="until-found"]){display:none !important}
@media (max-width:600px){h1{font-size:1.5rem}header.top .optbtn{display:none}.links{margin-left:0;flex-wrap:nowrap;overflow-x:auto;width:100%;padding-bottom:2px}header.top .pill{padding:0 10px;letter-spacing:0.04em}.gloss>div{grid-template-columns:1fr}.tname .w{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}.slider{height:78px}}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}a.gl::after{transition:transform .15s}.flash{transition:background .4s}}
@media print{:root,:root[data-theme]{%LIGHT_IMP%}[hidden]{display:block !important;content-visibility:visible !important}.alt,.more,.themebtn,nav,header.top,.skip,.scopebar,.quicksteps,.tip,.readfab,.readopts{display:none !important}}
""".replace("%LIGHT_IMP%", block(LIGHT, True)).replace("%LIGHT%", block(LIGHT)).replace("%DARK%", block(DARK))

HEAD_JS = """(function(){var d=document.documentElement;try{var t=localStorage.getItem('myAllyTheme');if(t==='light'||t==='dark')d.setAttribute('data-theme',t);}catch(e){}try{var r=JSON.parse(localStorage.getItem('myAllyRead')||'{}');var K={font:'data-font',size:'data-size',space:'data-space',tone:'data-tone'};for(var k in K){if(r[k]&&r[k]!=='std')d.setAttribute(K[k],r[k]);}}catch(e){}})();"""

JS = """(function(){try{var t=localStorage.getItem('myAllyTheme');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();"""

JS = """
(function(){
  var DESC=__DESC__;
  var level=__DEFAULT__,over=new Set();
  try{var v=parseInt(localStorage.getItem('myAllyLevel'),10);if(v>=1&&v<=5)level=v;}catch(e){}
  var secs=[].slice.call(document.querySelectorAll('.sec'));
  var slider=document.getElementById('depth');
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
    var cur=DESC[level],nxt=DESC[level+1];
    slider.value=String(level);
    slider.style.setProperty('--fill','calc(12px + (100% - 24px) * '+((level-1)/4)+')');
    slider.setAttribute('aria-valuetext','Level '+level+' of 5, '+cur.name);
    [].forEach.call(document.querySelectorAll('.tname'),function(b){b.className='tname'+(parseInt(b.getAttribute('data-level'),10)===level?' on':'');});
    measure();
    document.getElementById('altdesc').textContent='Level '+level+' of 5, '+cur.name+': '+cur.desc+(nxt?' Moving right adds '+nxt.adds+'.':' This is the full detail.');
  }
  var bar=document.querySelector('.alt');
  function measure(){if(bar)document.documentElement.style.setProperty('--sticky-h',Math.ceil(bar.getBoundingClientRect().height)+'px');}
  if(window.ResizeObserver&&bar)new ResizeObserver(measure).observe(bar);
  window.addEventListener('resize',measure);
  function setLevel(n){level=Math.max(1,Math.min(5,n));over.clear();try{localStorage.setItem('myAllyLevel',String(level));}catch(e){}apply();}
  slider.addEventListener('input',function(){setLevel(parseInt(slider.value,10));});
  [].forEach.call(document.querySelectorAll('.tname'),function(b){b.addEventListener('click',function(){setLevel(parseInt(b.getAttribute('data-level'),10));});});
  secs.forEach(function(sec,i){
    var more=sec.querySelector('.more'),body=sec.querySelector('.body');
    if(more)more.addEventListener('click',function(){if(over.has(i))over.delete(i);else over.add(i);apply();});
    if(body)body.addEventListener('beforematch',function(){over.add(i);apply();});
  });
  function secFor(t){if(!t)return -1;var s=t.classList&&t.classList.contains('sec')?t:(t.querySelector&&t.querySelector('.sec'))||t.closest('.sec');return secs.indexOf(s);}
  function go(id,push){
    var t=document.getElementById(id);if(!t)return false;
    var i=secFor(t);if(i>-1&&!isOpen(i)){over.add(i);apply();}
    setTimeout(function(){t.scrollIntoView();if(!t.hasAttribute('tabindex'))t.setAttribute('tabindex','-1');try{t.focus({preventScroll:true});}catch(e){}t.classList.add('flash');setTimeout(function(){t.classList.remove('flash');},2000);},0);
    if(push&&history.pushState){history.pushState(null,'','#'+id);}
    return true;
  }
  /* definition popups: hover, keyboard focus and tap */
  var pinned=null,quiet=false;
  function refocus(a){quiet=true;a.focus();quiet=false;}
  function tipOf(a){return a.parentNode.querySelector('.tip');}
  function place(t,w){
    t.style.left='0px';t.style.right='auto';
    var vw=document.documentElement.clientWidth,wr=w.getBoundingClientRect(),tw=t.getBoundingClientRect().width,left=wr.left;
    if(left+tw>vw-8)left=vw-8-tw;
    if(left<8)left=8;
    t.style.left=(left-wr.left)+'px';
  }
  function show(a){var t=tipOf(a);if(!t)return;t.hidden=false;place(t,a.parentNode);a.setAttribute('aria-expanded','true');}
  function hide(a){var t=tipOf(a);if(!t)return;t.hidden=true;a.setAttribute('aria-expanded','false');a.parentNode.classList.remove('pinned');}
  function hideAll(){[].forEach.call(document.querySelectorAll('a.gl'),hide);pinned=null;}
  [].forEach.call(document.querySelectorAll('.termwrap'),function(w){
    var a=w.querySelector('a.gl');
    a.setAttribute('role','button');
    a.addEventListener('keydown',function(e){if(e.key===' '){e.preventDefault();a.click();}});
    w.addEventListener('mouseenter',function(){show(a);});
    w.addEventListener('mouseleave',function(){if(pinned!==a)hide(a);});
    a.addEventListener('focus',function(){if(!quiet)show(a);});
    w.addEventListener('focusout',function(e){if(pinned!==a&&!w.contains(e.relatedTarget))hide(a);});
    a.addEventListener('click',function(e){e.preventDefault();e.stopPropagation();if(pinned===a){hideAll();}else{hideAll();pinned=a;w.classList.add('pinned');show(a);}});
    var cb=w.querySelector('.tipclose');if(cb)cb.addEventListener('click',function(e){e.stopPropagation();hideAll();refocus(a);});
  });
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&pinned){var a=pinned;hideAll();refocus(a);}else if(e.key==='Escape'){hideAll();}});
  document.addEventListener('click',function(e){if(pinned&&!e.target.closest('.termwrap'))hideAll();});
  document.addEventListener('click',function(e){
    var a=e.target.closest&&e.target.closest('a[href^="#"]');if(!a||a.classList.contains('gl'))return;
    var id=a.getAttribute('href').slice(1);if(go(id,true)){if(a.classList.contains('tipgo'))hideAll();e.preventDefault();}
  });
  /* scope cases */
  [].forEach.call(document.querySelectorAll('.scope'),function(sc){
    sc.classList.add('js');
    [].forEach.call(sc.querySelectorAll('.scopebar button'),function(b){
      b.addEventListener('click',function(){
        sc.setAttribute('data-case',b.getAttribute('data-case'));
        var lv=sc.querySelector('#scopelive');if(lv)lv.textContent='Showing the '+b.textContent.toLowerCase()+'.';
        [].forEach.call(sc.querySelectorAll('.scopebar button'),function(o){o.setAttribute('aria-pressed',String(o===b));});
      });
    });
  });
  var root=document.documentElement,tb=document.getElementById('themebtn');
  function eff(){var t=root.getAttribute('data-theme');if(t)return t;return window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';}
  var MOON='<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>',SUN='<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';function label(){var d=eff()==='dark';tb.innerHTML=d?SUN:MOON;tb.setAttribute('aria-label',d?'Switch to light mode':'Switch to dark mode');tb.title=d?'Light mode':'Dark mode';}
  tb.addEventListener('click',function(){var n=eff()==='dark'?'light':'dark';root.setAttribute('data-theme',n);try{localStorage.setItem('myAllyTheme',n);}catch(e){}label();});
  /* reading options */
  var RK='myAllyRead',ro=document.getElementById('readopts'),fab=document.getElementById('readfab'),ob=document.getElementById('optbtn');
  var st={};try{st=JSON.parse(localStorage.getItem(RK)||'{}')||{};}catch(e){st={};}
  var KEYS={font:'data-font',size:'data-size',space:'data-space',tone:'data-tone'};
  var opener=fab;
  function applyRead(){
    Object.keys(KEYS).forEach(function(k){var v=st[k];if(v&&v!=='std')root.setAttribute(KEYS[k],v);else root.removeAttribute(KEYS[k]);});
    [].forEach.call(ro.querySelectorAll('button[data-k]'),function(b){b.setAttribute('aria-pressed',String(b.getAttribute('data-v')===(st[b.getAttribute('data-k')]||'std')));});
    measure();
  }
  function saveRead(){try{localStorage.setItem(RK,JSON.stringify(st));}catch(e){}}
  function openRead(open,from){
    ro.hidden=!open;fab.setAttribute('aria-expanded',String(open));ob.setAttribute('aria-expanded',String(open));
    if(open){opener=from||fab;var f=ro.querySelector('button[aria-pressed="true"]')||ro.querySelector('button');f.focus();}
    else{opener.focus();}
  }
  fab.addEventListener('click',function(){openRead(ro.hidden,fab);});
  ob.addEventListener('click',function(){openRead(ro.hidden,ob);});
  ro.querySelector('.ro-close').addEventListener('click',function(){openRead(false);});
  ro.querySelector('.ro-reset').addEventListener('click',function(){st={};saveRead();applyRead();});
  [].forEach.call(ro.querySelectorAll('button[data-k]'),function(b){b.addEventListener('click',function(){st[b.getAttribute('data-k')]=b.getAttribute('data-v');saveRead();applyRead();});});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!ro.hidden)openRead(false);});
  applyRead();
  label();
  apply();
  measure();
  if(location.hash.length>1)go(location.hash.slice(1),false);
})();
""".replace("__DESC__", json.dumps(descs)).replace("__DEFAULT__", str(DEFAULT_LEVEL))

banner = "" if SEND else '<div class="banner" role="note">Draft for Zach to review. Not sent. No prices appear because none are agreed.</div>'

PANEL = '''
<button type="button" class="readfab" id="readfab" aria-expanded="false" aria-controls="readopts" aria-label="Reading options"><span aria-hidden="true">Aa</span></button>
<section id="readopts" class="readopts" role="dialog" aria-modal="false" aria-labelledby="roh" hidden>
<p id="roh" class="ro-title">Reading options</p>
<p class="ro-note">Comfort settings: pick whatever reads best for you. They stay on this device and are not sent anywhere.</p>
<div class="ro-group" role="group" aria-labelledby="ro-f"><span id="ro-f" class="ro-label">Font</span><span class="ro-btns"><button type="button" data-k="font" data-v="std" aria-pressed="true">Standard</button><button type="button" data-k="font" data-v="easy" aria-pressed="false">Easy-read</button></span><span class="ro-hint">Easy-read is a plain, wide font with no italics and no underlines.</span></div>
<div class="ro-group" role="group" aria-labelledby="ro-s"><span id="ro-s" class="ro-label">Text size</span><span class="ro-btns"><button type="button" data-k="size" data-v="std" aria-pressed="true">Standard</button><button type="button" data-k="size" data-v="l" aria-pressed="false">Larger</button><button type="button" data-k="size" data-v="xl" aria-pressed="false">Largest</button></span></div>
<div class="ro-group" role="group" aria-labelledby="ro-p"><span id="ro-p" class="ro-label">Spacing</span><span class="ro-btns"><button type="button" data-k="space" data-v="std" aria-pressed="true">Standard</button><button type="button" data-k="space" data-v="roomy" aria-pressed="false">Roomy</button></span><span class="ro-hint">Roomy adds space between letters, words and lines.</span></div>
<div class="ro-group" role="group" aria-labelledby="ro-t"><span id="ro-t" class="ro-label">Background</span><span class="ro-btns"><button type="button" data-k="tone" data-v="std" aria-pressed="true">Standard</button><button type="button" data-k="tone" data-v="warm" aria-pressed="false">Warm paper</button></span></div>
<div class="ro-actions"><button type="button" class="ro-reset">Reset</button><button type="button" class="ro-close">Close</button></div>
</section>
'''
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
<meta name="description" content="A plain-language plan for My Ally LD: four stages, what is in scope under best, base and worst cases, a glossary and an intake preview.">
<title>My Ally LD plan</title>
<script>{HEAD_JS}</script>
<noscript><style>.alt,.more,.themebtn{{display:none}}.dek{{display:none}}</style></noscript>
<style>{css}</style>
</head>
<body>
<a class="skip" href="#main">Skip to the plan</a>
<header class="top"><nav aria-label="Sections"><div class="wrap bar"><a class="brand" href="#plan" aria-label="ARCS Field OS. Go to the top of the plan"><span class="wa">ARCS</span><span class="wf">FIELD OS</span></a><span class="links"><a class="pill" href="#plan">The plan</a><a class="pill" href="#codex">Word guide</a><a class="pill primary" href="#intake">Next steps</a><button type="button" class="pill optbtn" id="optbtn" aria-expanded="false" aria-controls="readopts">Reading options</button><button type="button" class="pill icon" id="themebtn" aria-label="Switch to dark mode"><svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg></button></span></div></nav></header>
<main class="wrap" id="main">
{banner}
<section id="plan">{plan}</section>
<section id="codex"><div class="sec" data-body-alt="5"><h2>Word guide</h2><p class="dek">A legend for the technical words, each with a plain meaning, a picture and why it matters to you.</p><div class="body" id="bcodex">{codex}</div><button class="more" type="button" aria-controls="bcodex" aria-expanded="false" hidden>Show detail</button></div></section>
<section id="intake"><div class="sec" data-body-alt="4"><h2>Next steps</h2><p class="dek">Four short sets of questions about what I would like to see: links and descriptions only, once the NDA is signed.</p><div class="body" id="bintake">{intake}</div><button class="more" type="button" aria-controls="bintake" aria-expanded="false" hidden>Show detail</button></div></section>
</main>
<footer class="wrap pagefoot"><p>Prepared by Zach at manana. This page is a view, not an agreement. Reading options and your depth setting stay on this device.</p></footer>
{PANEL}
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
# Hosted copy, served only through the myally passcode gate (src/proxy.ts).
# HTML comments (internal seam notes) are stripped: page source is visible to the counterpart.
(ROOT / "public" / "myally.html").write_text(re.sub(r"<!--.*?-->\n?", "", page, flags=re.S).replace("</head>", '<script defer src="/_vercel/insights/script.js"></script>\n</head>', 1), encoding="utf-8")
print("wrote", out.relative_to(ROOT), len(page), "bytes")
