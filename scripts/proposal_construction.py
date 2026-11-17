#!/usr/bin/env python3
"""proposal_construction.py: render a proposal page as its own construction sheet, atom to page.

WHY: a proposal page (built by proposal_build.py) is meant to be assembled from the ui-kit, but its
molecules drift into page-local CSS one polish round at a time, and nothing shows which parts are kit
and which are one-offs. This sheet cuts every tier straight out of the page's own source, so it can
never disagree with the page:

  0 Drift      kit-backed vs page-local classes, kit blocks inlined but unused, template fit
  1 Atoms      the tokens the page reads, the type roles, the single-element parts
  2 Molecules  the smallest reusable groups (a question pair, a labelled row, a trace step ...)
  3 Organisms  the page's sections, whole
  4 Template   the slot skeleton, with each slot's organism and source line
  5 Page       the built page itself, in a frame

Each specimen carries its classes and a verdict: KIT (the class belongs to a numbered kit part) or
LOCAL (the class exists only on this page; a promotion candidate). Fragments are cut from the source
markup and styled by the source's own <style>, so a specimen renders exactly as it does on the page.

  python3 scripts/proposal_construction.py --louisville            writes _ARTIFACTS/louisville-proposal/construction.html
  python3 scripts/proposal_construction.py --source S --page P --out O
Stdlib only. Read-only on the source; the output is a local review page (untracked by default).
"""
import argparse, collections, html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "src/ui-kit/kit-manifest.json")
TEMPLATES = os.path.join(ROOT, "src/ui-kit/templates.json")
PRESETS = {"louisville": dict(source="_ARTIFACTS/louisville-proposal/source.html",
                              page="public/louisville-proposal.html",
                              out="_ARTIFACTS/louisville-proposal/construction.html")}

VOID = {"br", "img", "input", "meta", "link", "hr", "path", "circle", "rect", "line", "polyline"}


def grab(src, opener, nth=0):
    """Return the balanced element whose start tag matches the regex `opener` (nth match)."""
    ms = list(re.finditer(opener, src))
    if len(ms) <= nth:
        raise SystemExit(f"construction: no match #{nth} for {opener!r}; the source changed, update the cut list")
    start = ms[nth].start()
    tag = re.match(r"<([a-zA-Z0-9]+)", src[start:]).group(1)
    depth, i = 0, start
    pat = re.compile(r"<(/?)%s\b[^>]*?(/?)>" % tag)
    for m in pat.finditer(src, start):
        if m.group(1):
            depth -= 1
        elif not m.group(2):
            depth += 1
        if depth == 0:
            return src[start:m.end()]
    raise SystemExit(f"construction: unbalanced <{tag}> at {opener!r}")


def classes_in(fragment):
    out = []
    for c in re.findall(r'class="([^"]+)"', fragment):
        for x in c.split():
            if x not in out:
                out.append(x)
    return out


def kit_owners():
    m = json.load(open(MANIFEST))
    own = collections.defaultdict(list)
    for p in m["parts"]:
        for c in p.get("classes", []):
            own[c].append(f'{p["number"]} {p["name"]}'.strip())
    return own, m


def esc(s):
    return html.escape(s, quote=True)


def chips(cls, own):
    out = []
    for c in cls:
        k = own.get(c)
        tag = "kit" if k else "local"
        tip = ("kit: " + ", ".join(k[:2])) if k else "page-local, no kit part owns it"
        out.append(f'<code class="cx-cls cx-{tag}" title="{esc(tip)}">.{esc(c)}</code>')
    return "".join(out)


def verdict(cls, own):
    if not cls:
        return "cx-na", "ELEMENT"
    kit = [c for c in cls if own.get(c)]
    if len(kit) == len(cls):
        return "cx-v-kit", "KIT"
    if kit:
        return "cx-v-mixed", f"MIXED {len(kit)}/{len(cls)}"
    return "cx-v-local", "LOCAL"


def specimen(name, job, frag, own, wrap=("", ""), note="", kitref="", sec=1):
    cls = classes_in(frag)
    vcls, vtxt = verdict(cls, own)
    ref = f'<span class="cx-ref">{esc(kitref)}</span>' if kitref else ""
    nt = f'<p class="cx-note">{esc(note)}</p>' if note else ""
    return (f'<article class="cx-spec"><header class="cx-sh"><p class="cx-name">{esc(name)}</p>'
            f'<span class="cx-verdict {vcls}">{vtxt}</span>{ref}</header>'
            f'<p class="cx-job">{esc(job)}</p>'
            f'<div class="cx-stage" style="counter-reset:sec {sec - 1}">{wrap[0]}{frag}{wrap[1]}</div>'
            f'<div class="cx-classes">{chips(cls, own)}</div>{nt}</article>')


def build(source, page_rel, out):
    src = open(os.path.join(ROOT, source)).read()
    own_all, manifest = kit_owners()
    style = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
    # A class counts as KIT only when the page inlines that kit part's block. A bare name match
    # (.verdict, .sub belong to kit 16, which this page does not carry) is a collision, not reuse.
    carried = set(n.split("-")[0] for n in re.findall(r"/\* @prim:begin (\S+) \*/", style))
    own = collections.defaultdict(list)
    collide = {}
    for c, parts in own_all.items():
        real = [x for x in parts if x.split(" ")[0] in carried]
        if real:
            own[c] = real
        else:
            collide[c] = parts
    body = src[src.find("<body"):]
    body_wo_script = re.sub(r"<script.*?</script>", "", body, flags=re.S)

    # ---- 0 drift, measured
    used = collections.Counter()
    for c in re.findall(r'class="([^"]+)"', body_wo_script):
        for x in c.split():
            used[x] += 1
    kit_cls = sorted(c for c in used if own.get(c))
    local_cls = sorted(c for c in used if not own.get(c))
    dead = []
    for name, blk in re.findall(r"/\* @prim:begin (\S+) \*/\n(.*?)/\* @prim:end \1 \*/", style, re.S):
        bcls = set(re.findall(r"\.([a-zA-Z][\w-]*)", re.sub(r"\{[^}]*\}", "{}", blk)))
        hit = sorted(c for c in bcls if c in used)
        dead.append((name, len(bcls), hit))
    tmpl = re.search(r"@arcs-template:\s*(\S+)", src)
    tmpl = tmpl.group(1) if tmpl else None
    tdef = json.load(open(TEMPLATES))["templates"].get(tmpl or "", {})
    sig = [s for s in tdef.get("signature_selectors", []) if s.lstrip(".") in used or s in src]

    # ---- cuts (each from the source, by its start tag)
    g = lambda pat, n=0: grab(body, pat, n)
    mast = g(r'<div class="mast">')
    named = g(r'<div class="named"')
    header = g(r"<header>")
    q_blk = g(r'<details class="blk" open>')
    offerwrap = g(r'<section class="offerwrap">')
    lockup = grab(offerwrap, r'<div class="lockup">')
    trace = grab(offerwrap, r'<figure class="trace"')
    dec_blk = grab(offerwrap, r'<details class="blk sub fixed"')
    inc_blk = grab(offerwrap, r'<details class="blk sub pbreak"')
    offer = grab(offerwrap, r'<div class="offer">')
    eyebrow = re.search(r'<p class="offer-eyebrow">.*?</p>', offerwrap).group(0)
    footer = g(r"<footer>")
    cover = g(r'<section class="cover"')
    hrow = g(r'<div class="hrow">')
    hheads = re.search(r'<h3 class="hhead">.*?<h3 class="hhead c">.*?</h3>', q_blk, re.S).group(0)
    specrow = g(r'<div class="specrow">')
    pli = re.search(r"<li><span class=\"pn\">01</span>.*?</li>", inc_blk, re.S).group(0)
    ggrow = g(r'<div class="gg-row" role="row">')
    gghead = g(r'<div class="gg-row gg-head"')
    tstep = re.search(r"<li><span class=\"trace-k\">.*?</li>", trace, re.S).group(0)
    tstop = re.search(r'<p class="trace-stop">.*?</p>', trace, re.S).group(0)
    offer_head = grab(offer, r'<div class="offer-head">')
    offer_proof = grab(offer, r'<div class="offer-proof">')
    summary = re.search(r"<summary>.*?</summary>", q_blk, re.S).group(0)
    wordmark = re.search(r'<span class="wordmark".*?</span></span>', mast, re.S).group(0)
    pdfbtn = re.search(r'<a class="pdfbtn".*?</a>', mast, re.S).group(0)
    dprefs = g(r'<div class="dprefs">')
    mastfor = re.search(r'<p class="mast-for">.*?</p>', mast, re.S).group(0)
    whypill = re.search(r'<span class="why-pill">.*?</span>', named).group(0)
    pn = '<span class="pn">01</span>'
    expall = '<div class="blkbar"><button type="button" class="expall">Expand all</button></div>'
    pnote = re.search(r'<p class="pnote">.*?</p>', inc_blk, re.S).group(0)

    # ---- 1 atoms: tokens the page reads (live swatches via var())
    toks = sorted(set(re.findall(r"var\((--[\w-]+)\)", style)))
    color_t = [t for t in toks if re.search(r"(bg|surface|elevated|border|text|secondary|muted|dimmed|cyan|green|gold|red)", t) and "font" not in t]
    type_t = [t for t in toks if t.startswith("--fs-")]
    sp_t = [t for t in toks if t.startswith("--sp-") or t in ("--measure",)]
    font_t = [t for t in toks if "font" in t or t in ("--sans", "--serif", "--mono")]
    sw = "".join(f'<div class="cx-sw"><span class="cx-chipc" style="background:var({t})"></span><code>{t}</code></div>' for t in color_t)
    ty = "".join(f'<div class="cx-ty"><span style="font-size:var({t});line-height:1.2">Aa</span><code>{t}</code></div>' for t in type_t)
    spc = "".join(f'<div class="cx-sp"><span class="cx-bar" style="width:var({t})"></span><code>{t}</code></div>' for t in sp_t if t != "--measure")
    fn = "".join(f'<div class="cx-fn"><span style="font-family:var({t})">The two decisions 01</span><code>{t}</code></div>' for t in font_t)

    roles = [("h1 · display", "<h1 style='margin:0'>A checkup on your AI build</h1>"),
             (".verdict · serif lede", '<p class="verdict" style="margin:0">I\'d answer by following two real decisions.</p>'),
             (".slabel · section title", '<h2 class="slabel">The two decisions</h2>'),
             (".tk · section deck", '<span class="tk">You pick. My suggestions:</span>'),
             (".hhead · column head", '<h3 class="hhead">What you raised</h3>'),
             (".deck · secondary body", '<div class="lockup"><p class="deck">I read your build through what it decides.</p></div>')]
    role_html = "".join(f'<div class="cx-role"><code>{esc(n)}</code><div>{h}</div></div>' for n, h in roles)

    atoms = "".join([
        specimen("Wordmark", "Brand lockup, top left of every client page (kit 13b global header).", wordmark, own, kitref="kit 38"),
        specimen("Display preferences", "Theme switch plus the PDF download, top right.", dprefs, own, kitref="kit 51"),
        specimen("Section numeral", "Mono numeral eyebrow; ties screen sections to the PDF's 01/02/03.", pn, own, wrap=('<div class="punch"><ol class="plist"><li>', "<span>numeral</span></li></ol></div>")),
        specimen("Why pill", "Inline label for the one-line framing note.", whypill, own, wrap=('<div class="named"><p class="named-v">', "</p></div>")),
        specimen("PDF button", "The download control.", pdfbtn, own),
        specimen("Expand all", "One control for every collapsible block.", expall, own),
        specimen("Price figure", "The one number on the page.", '<span class="offer-fig">$5,000</span>', own, wrap=('<div class="offer"><div class="offer-head"><p class="offer-price">', "</p></div></div>"), kitref="kit 41"),
    ])

    molecules = "".join([
        specimen("Question pair", "What they raised, set against the question worth asking. One row of the 01 grid.", hheads + hrow, own, wrap=('<div class="hgrid">', "</div>"), kitref="nearest: kit 04 signal delta table"),
        specimen("Labelled row", "A label and its definition: the two decisions.", specrow, own, wrap=('<dl class="spec">', "</dl>"), kitref="nearest: kit 50 term definition"),
        specimen("Deliverable line", "Numbered deliverable, numeral plus sentence.", pli, own, wrap=('<div class="punch"><ol class="plist">', "</ol></div>")),
        specimen("Give/get row", "One step of the time trade: when, what you give, what you get.", gghead + ggrow, own, wrap=('<div class="gg" role="table">', "</div>"), kitref="nearest: kit 52 plan matrix"),
        specimen("Trace step", "One stage of the method: a key and its mark.", tstep, own, wrap=('<figure class="trace"><ol class="trace-steps">', "</ol></figure>"), kitref="nearest: kit 06 beat stepper (legacy)"),
        specimen("Stop line", "The number agreed before the decision.", tstop, own, wrap=('<figure class="trace">', "</figure>")),
        specimen("Section summary", "A block's head: title plus deck, the click target of a collapsible block.", summary, own, wrap=('<details class="blk" open>', '<div class="bd"></div></details>'), kitref="nearest: kit 48 summary disclosure"),
        specimen("Price head", "Price and the keep line.", offer_head, own, wrap=('<div class="offer">', "</div>"), kitref="kit 41"),
        specimen("Proof line", "One piece of public proof, linked.", offer_proof, own, wrap=('<div class="offer">', "</div>"), kitref="kit 41"),
        specimen("Prepared-for line", "Who the page is for.", mastfor, own, wrap=('<div class="mast">', "</div>")),
        specimen("Time note", "The cost in hours, between hairlines.", pnote, own),
    ])

    organisms = "".join([
        specimen("Masthead", "Global header: wordmark, preferences, prepared-for.", mast, own, kitref="kit 13b header (38 + 51)"),
        specimen("Why note", "One dismissible line of framing above the page.", named, own),
        specimen("Opening", "Title and the two-sentence lede: his question, then the answer.", header, own, note="Lede spans the full lane, matching the heading (standing rule)."),
        specimen("01 Questions", "Collapsible block: the question grid.", q_blk, own),
        specimen("Method lockup", "Bridge into the offer: deck plus the trace diagram.", lockup, own),
        specimen("02 Decisions", "Fixed block: the two decisions, always open.", dec_blk, own, sec=2),
        specimen("03 Included", "Deliverables, time note and the give/get table.", inc_blk, own, sec=3),
        specimen("Offer close", "Eyebrow, price, proof, the one ask.", eyebrow + offer, own, kitref="kit 41 offer close"),
        specimen("Footer", "Review copy and plain-text links.", footer, own),
        specimen("PDF cover (print only)", "First page of the PDF; hidden on screen.", cover.replace('class="cover"', 'class="cover" style="display:flex"'), own, note="Shown here by forcing display; on screen the page hides it."),
    ])

    slots = [("Masthead", "mast", "wordmark · dprefs · mast-for"), ("Why note", "named", "why-pill · why-t · dismiss"),
             ("Opening", "header", "h1 · verdict × 2"), ("Block bar", "blkbar", "expall"),
             ("Section 01", "details.blk", "summary · hgrid of question pairs"),
             ("Method", "lockup + trace", "deck × 2 · trace steps × 3 · stop line"),
             ("Section 02", "details.blk.fixed", "summary · spec rows × 2"),
             ("Section 03", "details.blk.pbreak", "summary · deliverables × 6 · time note · give/get × 3"),
             ("Close", "offer", "eyebrow · price · proof · ask"), ("Footer", "footer", "revline")]
    template = "".join(f'<div class="cx-slot"><span class="cx-slot-n">{i:02d}</span><span class="cx-slot-t">{esc(t)}</span><code>{esc(s)}</code><span class="cx-slot-f">{esc(f)}</span></div>' for i, (t, s, f) in enumerate(slots, 1))

    dead_rows = "".join(
        f'<tr><td><code>{esc(n)}</code></td><td>{k}</td><td>{", ".join(map(esc, h)) or "<b>none</b>"}</td>'
        f'<td>{"dead weight: drop or use" if not h else "in use"}</td></tr>' for n, k, h in dead)
    local_html = " ".join(f'<code class="cx-cls cx-local">.{esc(c)}</code>' for c in local_cls)
    coll_html = " ".join(f'<code class="cx-cls cx-local" title="name also used by {esc(", ".join(collide[c][:2]))}">.{esc(c)}</code>' for c in sorted(c for c in used if c in collide)) or "none"
    kit_html = " ".join(f'<code class="cx-cls cx-kit" title="{esc(", ".join(own[c][:2]))}">.{esc(c)}</code>' for c in kit_cls)
    tfit = (f"Enrolled as <code>{esc(tmpl)}</code> ({esc(tdef.get('kind', '?'))}, mode {esc(tdef.get('mode', '?'))}). "
            f"Signatures met: {len(sig)} of {len(tdef.get('signature_selectors', []))} "
            f"({', '.join(map(esc, sig)) or 'none'}); the gate needs {tdef.get('min_signatures', '?')}. "
            f"{esc(tdef.get('description', ''))}")

    css = CX_CSS
    out_html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Proposal Construction Sheet</title>
<style>{style}
{css}</style></head>
<body class="cx-body">
<main class="cx">
<header class="cx-hero">
  <p class="cx-eyebrow">Construction sheet · generated from {esc(source)}</p>
  <h1>The proposal, atom to page</h1>
  <p class="cx-lede">Every specimen below is cut from the page's own source and styled by its own stylesheet, so it renders exactly as it does on the page. Each one is marked <span class="cx-verdict cx-v-kit">KIT</span> when a numbered kit part owns its classes, or <span class="cx-verdict cx-v-local">LOCAL</span> when the class lives only on this page.</p>
  <nav class="cx-toc"><a href="#drift">0 Drift</a><a href="#atoms">1 Atoms</a><a href="#molecules">2 Molecules</a><a href="#organisms">3 Organisms</a><a href="#template">4 Template</a><a href="#page">5 Page</a></nav>
</header>

<section id="drift" class="cx-tier"><p class="cx-tl">0</p><h2 class="cx-th">Drift, measured</h2>
  <div class="cx-stats"><div><b>{len(kit_cls)}</b><span>kit-backed classes</span></div><div><b>{len(local_cls)}</b><span>page-local classes</span></div><div><b>{sum(1 for _, _, h in dead if not h)}</b><span>kit blocks inlined, unused</span></div></div>
  <p class="cx-p"><b>Template fit.</b> {tfit}</p>
  <table class="cx-table"><thead><tr><th>Inlined kit block</th><th>Classes</th><th>Used in markup</th><th>Read</th></tr></thead><tbody>{dead_rows}</tbody></table>
  <p class="cx-p"><b>Kit-backed</b> {kit_html}</p>
  <p class="cx-p"><b>Page-local</b> {local_html}</p>
  <p class="cx-p"><b>Name collisions</b> (page-local classes whose names a kit part also uses, without the page carrying that part): {coll_html}</p>
</section>

<section id="atoms" class="cx-tier"><p class="cx-tl">1</p><h2 class="cx-th">Atoms</h2>
  <h3 class="cx-h3">Color tokens the page reads</h3><div class="cx-grid-sw">{sw}</div>
  <h3 class="cx-h3">Type ramp</h3><div class="cx-row">{ty}</div>
  <h3 class="cx-h3">Font stacks</h3><div class="cx-col">{fn}</div>
  <h3 class="cx-h3">Spacing</h3><div class="cx-col">{spc}</div>
  <h3 class="cx-h3">Type roles</h3><div class="cx-col">{role_html}</div>
  <h3 class="cx-h3">Single-element parts</h3><div class="cx-specs">{atoms}</div>
</section>

<section id="molecules" class="cx-tier"><p class="cx-tl">2</p><h2 class="cx-th">Molecules</h2><div class="cx-specs">{molecules}</div></section>

<section id="organisms" class="cx-tier"><p class="cx-tl">3</p><h2 class="cx-th">Organisms</h2><div class="cx-specs cx-wide">{organisms}</div></section>

<section id="template" class="cx-tier"><p class="cx-tl">4</p><h2 class="cx-th">Template</h2>
  <p class="cx-p">The page's slot order, top to bottom. Each slot names its container and what fills it.</p>
  <div class="cx-slots">{template}</div></section>

<section id="page" class="cx-tier"><p class="cx-tl">5</p><h2 class="cx-th">Page</h2>
  <p class="cx-p">The built page (<code>{esc(page_rel)}</code>), framed.</p>
  <iframe class="cx-frame" src="{esc(os.path.relpath(os.path.join(ROOT, page_rel), os.path.dirname(os.path.join(ROOT, out))))}" title="The built proposal page"></iframe></section>
</main>
</body></html>
"""
    with open(os.path.join(ROOT, out), "w") as f:
        f.write(out_html)
    print(f"construction: wrote {out} · kit {len(kit_cls)} · local {len(local_cls)} · unused kit blocks {sum(1 for _, _, h in dead if not h)}")


CX_CSS = """
/* construction-sheet chrome: tokens only, every class prefixed cx- so the page's own CSS is untouched */
body.cx-body{padding:var(--sp-4) 16px 96px;}
.cx{max-width:1120px;margin:0 auto;display:flex;flex-direction:column;gap:var(--sp-5);}
.cx-hero{display:flex;flex-direction:column;gap:var(--sp-2);}
.cx-eyebrow,.cx-tl{font-family:var(--mono);font-size:var(--fs-label);letter-spacing:0.12em;text-transform:uppercase;color:var(--text-secondary);}
.cx-lede{font-family:var(--serif);font-size:var(--fs-step);line-height:1.45;max-width:none;}
.cx-toc{display:flex;flex-wrap:wrap;gap:var(--sp-1) var(--sp-3);font-family:var(--mono);font-size:var(--fs-label);}
.cx-toc a{color:var(--cyan);text-decoration:none;}
.cx-tier{display:flex;flex-direction:column;gap:var(--sp-2);border-top:2px solid var(--text);padding-top:var(--sp-2);}
.cx-th{font-size:var(--fs-display);font-weight:700;letter-spacing:-0.02em;line-height:1.2;}
.cx-h3{font-family:var(--mono);font-size:var(--fs-label);letter-spacing:0.1em;text-transform:uppercase;color:var(--text-secondary);margin-top:var(--sp-3);}
.cx-p{color:var(--text);}
.cx-stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:var(--sp-2);}
.cx-stats div{border:1px solid var(--border);border-radius:8px;padding:var(--sp-2);background:var(--surface);display:flex;flex-direction:column;}
.cx-stats b{font-size:var(--fs-display);font-family:var(--mono);}
.cx-stats span{color:var(--text-secondary);font-size:var(--fs-label);}
.cx-table{width:100%;border-collapse:collapse;font-size:var(--fs-label);}
.cx-table th,.cx-table td{border-top:1px solid var(--border);padding:var(--sp-1);text-align:left;vertical-align:top;}
.cx-table th{font-family:var(--mono);letter-spacing:0.08em;text-transform:uppercase;color:var(--text-secondary);font-weight:600;}
.cx-cls{display:inline-block;font-family:var(--mono);font-size:12px;padding:1px 6px;border-radius:4px;margin:2px 4px 2px 0;border:1px solid var(--border);}
.cx-kit{color:var(--green);background:var(--green-bg);border-color:var(--green);}
.cx-local{color:var(--gold);background:var(--gold-bg);border-color:var(--gold);}
.cx-verdict{font-family:var(--mono);font-size:11px;letter-spacing:0.08em;padding:2px 8px;border-radius:999px;border:1px solid currentColor;white-space:nowrap;}
.cx-v-kit{color:var(--green);} .cx-v-local{color:var(--gold);} .cx-v-mixed{color:var(--cyan);} .cx-na{color:var(--text-secondary);}
.cx-grid-sw{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:var(--sp-1);}
.cx-sw{display:flex;align-items:center;gap:var(--sp-1);font-size:12px;}
.cx-chipc{width:28px;height:28px;border-radius:6px;border:1px solid var(--border);flex:none;}
.cx-row{display:flex;flex-wrap:wrap;gap:var(--sp-3);align-items:flex-end;}
.cx-ty,.cx-fn,.cx-sp,.cx-role{display:flex;align-items:baseline;gap:var(--sp-2);flex-wrap:wrap;}
.cx-ty{flex-direction:column;align-items:flex-start;gap:4px;}
.cx-col{display:flex;flex-direction:column;gap:var(--sp-1);}
.cx-bar{display:inline-block;height:12px;background:var(--cyan);border-radius:2px;}
.cx code{font-family:var(--mono);font-size:12px;color:var(--text-secondary);}
.cx-role{border-top:1px solid var(--border);padding-top:var(--sp-1);}
.cx-role > code{min-width:200px;}
.cx-specs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:var(--sp-3);}
.cx-specs.cx-wide{grid-template-columns:minmax(0,1fr);}
.cx-spec{border:1px solid var(--border);border-radius:10px;background:var(--surface);display:flex;flex-direction:column;overflow:hidden;}
.cx-sh{display:flex;align-items:center;gap:var(--sp-1);flex-wrap:wrap;padding:var(--sp-2) var(--sp-2) 0;}
.cx-name{font-weight:600;}
.cx-ref{font-family:var(--mono);font-size:11px;color:var(--text-secondary);}
.cx-job{color:var(--text-secondary);font-size:var(--fs-label);padding:4px var(--sp-2) var(--sp-2);}
.cx-stage{padding:var(--sp-3) var(--sp-2);background:var(--bg);border-top:1px dashed var(--border);border-bottom:1px dashed var(--border);display:flex;flex-direction:column;gap:var(--sp-2);min-width:0;}
.cx-classes{padding:var(--sp-1) var(--sp-2);}
.cx-note{padding:0 var(--sp-2) var(--sp-2);font-size:var(--fs-label);color:var(--text-secondary);}
.cx-slots{display:flex;flex-direction:column;border:1px solid var(--border);border-radius:10px;overflow:hidden;}
.cx-slot{display:grid;grid-template-columns:40px 160px 200px minmax(0,1fr);gap:var(--sp-2);padding:var(--sp-1) var(--sp-2);border-top:1px solid var(--border);align-items:baseline;}
.cx-slot:first-child{border-top:0;}
.cx-slot-n{font-family:var(--mono);color:var(--text-secondary);}
.cx-slot-t{font-weight:600;}
.cx-slot-f{color:var(--text-secondary);font-size:var(--fs-label);}
.cx-frame{width:100%;height:1400px;border:1px solid var(--border);border-radius:10px;background:var(--bg);}
@media (max-width:760px){.cx-specs{grid-template-columns:minmax(0,1fr);}.cx-stats{grid-template-columns:minmax(0,1fr);}.cx-slot{grid-template-columns:32px minmax(0,1fr);}.cx-slot code,.cx-slot-f{grid-column:2;}}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--louisville", action="store_true")
    ap.add_argument("--source"); ap.add_argument("--page"); ap.add_argument("--out")
    a = ap.parse_args()
    cfg = PRESETS["louisville"] if a.louisville else dict(source=a.source, page=a.page, out=a.out)
    if not all(cfg.values()):
        ap.error("pass --louisville, or --source, --page and --out")
    build(cfg["source"], cfg["page"], cfg["out"])


if __name__ == "__main__":
    main()
