#!/usr/bin/env python3
"""build_nda_redlines.py: generate public/myally-mnda-edits.html, Zach's proposed edits to the
Access Consulting mutual NDA (2026-10-09), each with a plain-language "Why" note.

Served at myally.arcs.care/mnda-edits behind the myally passcode (src/proxy.ts). Reuses the hosted
proposal page's <head> so tokens, fonts and theme match. Run from the repo root after
build_proposal_view.py:  python3 _ARTIFACTS/sow-scaffold-2026-10-08/build_nda_redlines.py
Not legal advice: these are requests for Chelsea and Leah's counsel to accept, change or decline.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
src = (ROOT / "public" / "myally.html").read_text(encoding="utf-8")
head = src[: src.index("</head>")]
head = re.sub(r"<title>.*?</title>", "<title>My Ally LD: NDA notes</title>", head, count=1, flags=re.S)
head = re.sub(r'<meta name="description"[^>]*>', '<meta name="description" content="Proposed edits to the mutual NDA, each with a short reason.">', head, count=1)

# (section, title, original text, proposed text, why)
EDITS = [
    ("3.2", "Who each of us may share with",
     "Advisor will not share Company's Confidential Information with any employee, subcontractor or other third party without Company's prior written consent.",
     "Advisor may share Company's Confidential Information with its own legal and financial advisors, and with service providers it uses for the Purpose (for example document storage, form and hosting tools), each bound by confidentiality at least as protective as this Agreement and used consistently with Section 4. Any other sharing needs Company's prior written consent.",
     "Section 3.1 lets your team share my information with your advisors and counsel. This makes it two-way, so I can ask my own lawyer or accountant a question, and so the ordinary tools I work in (like the intake form you will use) are covered rather than technically off-limits."),
    ("8.1(c)", "When materials are returned or destroyed",
     "(c) 60 days after the Effective Date, unless the Parties have signed a services agreement or extended this period in writing.",
     "(c) 90 days after the Effective Date, unless the Parties have signed a services agreement or extended this period in writing.",
     "Sixty days runs out quickly once you add review time, counsel and holidays. Ninety gives the proposal room without either of us having to remember to extend it. Return or destruction on your request still applies at any time."),
    ("8.3", "Copies that cannot be cleanly erased",
     "Copies held in automatic backups that cannot reasonably be deleted may be kept until overwritten in the ordinary course, and remain subject to this Agreement.",
     "Copies held in automatic backups or in version-control history that cannot reasonably be deleted may be kept until overwritten or archived in the ordinary course, and remain subject to this Agreement.",
     "I keep working files under version control, where history cannot always be erased line by line. This keeps any such copy fully covered by the agreement, the same way the clause already treats backups."),
    ("6.2", "Derivative works",
     "The Receiving Party will not reverse engineer, decompile or create derivative works from the Disclosing Party's Confidential Information.",
     "The Receiving Party will not reverse engineer, decompile or create derivative works from the Disclosing Party's Confidential Information, except materials prepared for the Purpose, such as proposals, analyses and notes, which remain subject to this Agreement.",
     "Read literally, a proposal or analysis written about your spec is a derivative work, which the agreement exists to let me prepare. This carves out exactly that, and keeps it confidential."),
    ("6.4 (new)", "My own methods stay usable",
     "(no existing text)",
     "Nothing in this Agreement restricts Advisor's use of ARCS or of Advisor's pre-existing or independently developed systems, methods and concepts, including strengths-based and decision-support methods, provided Advisor does not use Company's Confidential Information in doing so.",
     "Some of my existing work sits near your space (for example strengths-based profiling and decision tools). Section 1.5(d) already allows independent development; this simply says it out loud so neither of us has to argue about it later. It does not loosen anything about your information."),
    ("Recital B", "How my services are described",
     "Advisor provides strategic, technical and compliance advisory services, fractional technology leadership and product development services...",
     "Advisor provides strategic and technical advisory services, fractional technology leadership and product development services...",
     "I do not give legal or compliance advice; your counsel does. Dropping the word keeps the description accurate."),
]


def esc(s):
    return html.escape(s)


items = []
for i, (sec, title, old, new, why) in enumerate(EDITS, 1):
    old_html = '<p class="old"><span class="vh">Original: </span>' + (esc(old) if not old.startswith("(") else '<em>' + esc(old) + '</em>') + "</p>"
    items.append(
        f'<li class="edit" id="e{i}"><div class="ehead"><span class="sec">Section {esc(sec)}</span><h2>{esc(title)}</h2>'
        f'<button type="button" class="why" aria-expanded="false" aria-controls="w{i}">Why?</button></div>'
        f'<div class="why-note" id="w{i}" role="note" hidden><p>{esc(why)}</p></div>'
        f'<div class="pair">{old_html}<p class="new"><span class="vh">Proposed: </span>{esc(new)}</p></div></li>'
    )

# ---- clean copy: the original text with every edit applied, changed passages marked
ORIG = (Path(__file__).resolve().parent / "mnda-original.txt").read_text(encoding="utf-8")
REPL = [  # (edit id, exact original fragment, replacement)
    (6, "Advisor provides strategic, technical and compliance advisory services,", "Advisor provides strategic and technical advisory services,"),
    (1, "3.2 Advisor will not share Company's Confidential Information with any employee, subcontractor or other third party without Company's prior written consent.",
        "3.2 Advisor may share Company's Confidential Information with its own legal and financial advisors, and with service providers it uses for the Purpose (for example document storage, form and hosting tools), each bound by confidentiality at least as protective as this Agreement and used consistently with Section 4. Any other sharing needs Company's prior written consent."),
    (4, "create derivative works from the Disclosing Party's Confidential Information.",
        "create derivative works from the Disclosing Party's Confidential Information, except materials prepared for the Purpose, such as proposals, analyses and notes, which remain subject to this Agreement."),
    (5, "as long as Advisor does not use or disclose Company's Confidential Information in doing so.",
        "as long as Advisor does not use or disclose Company's Confidential Information in doing so. 6.4 Nothing in this Agreement restricts Advisor's use of ARCS or of Advisor's pre-existing or independently developed systems, methods and concepts, including strengths-based and decision-support methods, provided Advisor does not use Company's Confidential Information in doing so."),
    (2, "(c) 60 days after the Effective Date,", "(c) 90 days after the Effective Date,"),
    (3, "Copies held in automatic backups that cannot reasonably be deleted may be kept until overwritten in the ordinary course,",
        "Copies held in automatic backups or in version-control history that cannot reasonably be deleted may be kept until overwritten or archived in the ordinary course,"),
]
clean_txt = html.escape(ORIG.replace(" \u2014 ", ": ").replace("\u2014", ":").replace("\u2013", "-"))
for eid, old, new in REPL:
    o = html.escape(old.replace("\u2014", ":"))
    assert o in clean_txt, f"clean copy anchor missing for edit {eid}: {old[:40]}"
    clean_txt = clean_txt.replace(o, f'<mark class="chg">{html.escape(new)}</mark> <a class="chgref" href="#e{eid}" aria-label="Why this change">why</a>', 1)
# paragraph breaks at clause markers
clean_txt = re.sub(r"\s(?=(?:\d{1,2}\.\d{1,2}\s)|(?:\d{1,2}\.\s[A-Z][a-z])|(?:[A-E]\.\s[A-Z])|(?:\([a-i]\)\s)|(?:Recitals\s)|(?:Signatures\s)|(?:COMPANY:)|(?:ADVISOR:))", "</p><p>", clean_txt)
clean_html = '<section class="clean" id="clean" aria-labelledby="cleanh"><h2 id="cleanh">Clean copy with the edits applied</h2><p class="cnote">The full agreement as it would read with the six edits. Changed passages are shaded; each <em>why</em> link jumps to its reason above.</p><div class="ctext"><p>' + clean_txt + "</p></div></section>"

css = """<style>
.nda{max-width:calc(var(--measure) + 2*var(--gut));margin:0 auto;padding:24px var(--gut) 64px}
.nda .lede{font-size:1.15rem;line-height:1.55;margin:0 0 12px}
.nda .key{display:flex;flex-wrap:wrap;gap:12px;margin:8px 0 24px;color:var(--pg-dim)}
.edits{list-style:none;margin:0;padding:0}
.edit{border-top:1px solid var(--pg-line);padding:20px 0;scroll-margin-top:140px}
#clean,#main{scroll-margin-top:140px}
.ehead{display:flex;flex-wrap:wrap;align-items:center;gap:6px 12px}
.ehead h2{flex:1 1 14rem;margin:0;font-size:1.15rem;font-weight:600;color:var(--pg-text)}
.sec{flex:0 0 100%;color:var(--pg-muted);font-size:0.925rem}
.why{min-height:44px;padding:0 16px;font:inherit;font-weight:600;color:var(--pg-accent);background:var(--pg-accent-bg);border:1px solid var(--pg-accent);border-radius:999px;cursor:pointer}
.why[aria-expanded="true"]{color:var(--pg-surface);background:var(--pg-accent)}
.why:focus-visible{outline:3px solid var(--pg-accent);outline-offset:2px}
.why-note{position:relative;margin:12px 0 4px;padding:12px 16px;background:var(--pg-surface);border:1px solid var(--pg-accent);border-radius:6px}
.why-note::before{content:"";position:absolute;top:-7px;right:44px;width:12px;height:12px;background:var(--pg-surface);border-left:1px solid var(--pg-accent);border-top:1px solid var(--pg-accent);transform:rotate(45deg)}
.why-note p{margin:0}
.pair p{margin:10px 0 0;padding:10px 12px;border-radius:6px}
.old{color:var(--pg-dim);background:var(--pg-surface);text-decoration:line-through;text-decoration-thickness:1px}
.new{color:var(--pg-text);background:var(--pg-accent-bg)}
.sw{display:inline-block;padding:2px 8px;border-radius:6px}
.sw.o{background:var(--pg-surface);text-decoration:line-through;border:1px solid var(--pg-line)}
.sw.n{background:var(--pg-accent-bg)}
.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.clean{margin:48px 0 0;border-top:2px solid var(--pg-line);padding-top:24px}.clean h2{font-size:1.5rem;margin:0 0 8px}.cnote{color:var(--pg-dim);margin:0 0 16px}.ctext p{margin:0 0 10px}mark.chg{background:var(--pg-accent-bg);color:var(--pg-text);padding:0 2px}.chgref{font-size:0.925rem}\n.nda .back{margin:32px 0 0;font-weight:600}
.nfoot{margin:32px 0 0;color:var(--pg-muted)}
@media print{.why{display:none}.why-note[hidden]{display:block !important}}
</style>
"""

body = f"""<body>
<a class="skip" href="#main">Skip to the notes</a>
<header class="top"><nav aria-label="Sections"><div class="wrap bar"><a class="brand" href="/" aria-label="ARCS Field OS. Back to the plan"><span class="wa">ARCS</span><span class="wf">FIELD OS</span></a><span class="links"><a class="pill primary" href="/">Back to the plan</a></span></div></nav></header>
<main class="nda" id="main">
<h1>Mutual NDA: a few small edits</h1>
<p class="lede">Thank you for sending the NDA, and for making it mutual. It is clear and fair. I would like to suggest six small edits before signing. A clean copy with the edits applied is at the bottom. Each one has a short reason: tap <strong>Why?</strong> to read it.</p>
<p class="key"><span><span class="sw o">struck text</span> is the current wording</span><span><span class="sw n">shaded text</span> is what I suggest</span></p>
<ol class="edits">{''.join(items)}</ol>
<p><a href="#clean">Jump to the clean copy</a></p>\n<p class="nfoot">These are requests, not conditions. If your counsel prefers different wording that does the same job, that works for me. Everything else in the agreement I am happy to sign as written. I am not a lawyer, and nothing here is legal advice.</p>
{clean_html}
<p class="back"><a href="/">Back to the plan</a></p>
</main>
<script>
document.addEventListener('click',function(e){{var b=e.target.closest&&e.target.closest('.why');if(!b)return;var n=document.getElementById(b.getAttribute('aria-controls'));var open=b.getAttribute('aria-expanded')!=='true';b.setAttribute('aria-expanded',open?'true':'false');if(open)n.removeAttribute('hidden');else n.setAttribute('hidden','');try{{window.va('event',{{name:'nda_why',data:{{edit:b.closest('.edit').id}}}});}}catch(err){{}}}});
</script>
</body>
</html>
"""

page = head + css + "</head>\n" + body
for bad in ["—", "–", "$", "_PATTERNS", "<!--"]:
    assert bad not in re.sub(r"<(style|script)\b.*?</\1>", "", page, flags=re.S), f"banned in visible copy: {bad!r}"
(ROOT / "public" / "myally-mnda-edits.html").write_text(page, encoding="utf-8")
print("wrote public/myally-mnda-edits.html", len(page), "bytes")
