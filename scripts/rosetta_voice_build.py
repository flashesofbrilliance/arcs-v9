#!/usr/bin/env python3
"""Build public/rosetta-voice.html (served at rosetta-shell.arcs.care/voice).

Sources, so nothing here is hand-copied twice:
  - Kit blocks: taken verbatim from public/rosetta-shell.html (same template,
    tool-getting-started), plus 38-wordmark from src/ui-kit/recoil-report.
  - App script: the <script> of rosetta-shell's web/rosetta-voice.html, passed
    as --app (its lint rules are kept in step with bin/rosetta by that repo's
    web/parity.test.js).

Usage:
  python3 scripts/rosetta_voice_build.py --app ../rosetta-shell/web/rosetta-voice.html
  python3 scripts/rosetta_voice_build.py --app ... --check   # exit 1 if the page is stale
"""
import argparse, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIB = ROOT / "public/rosetta-shell.html"
WM = ROOT / "src/ui-kit/recoil-report/38-wordmark.html"
OUT = ROOT / "public/rosetta-voice.html"


def between(text, start, end, inclusive=True):
    i = text.index(start)
    j = text.index(end, i) + (len(end) if inclusive else 0)
    return text[i:j] if inclusive else text[i + len(start):j]


def build(app_path):
    sib = SIB.read_text()
    app = Path(app_path).read_text()
    # Kit tokens and blocks: everything in the sibling's first <style> up to its page layout.
    kit_css = between(sib, "/* grammar chips */", "/* @prim:end 51-display-preferences */")
    wordmark = between(WM.read_text(), "/* @prim:begin 38-wordmark */", "/* @prim:end 38-wordmark */")
    fonts = between(sib, '<link rel="preload" href="/fonts/', "/* fonts_selfhost:end */\n</style>")
    dp_wire = between(sib, "/* 51 display-preferences wiring", "apply();})();")
    js = between(app, "<script>", "</script>", inclusive=False)
    return TEMPLATE.format(kit_css=kit_css, wordmark=wordmark, fonts=fonts, js=js, dp_wire=dp_wire)


TEMPLATE = r"""<!DOCTYPE html>
<!-- @arcs-template: tool-getting-started -->
<!-- @arcs-mode: read -->
<!-- Built from kit parts: grammar chips, 27 section-label, 30 button, 45 fact-tile, 37 fidelity-grain, 39 theme-toggle,
     51 display-preferences, 38 wordmark. Marked blocks are verbatim; scripts/kit_primitive_sync.py --check fails on drift. -->
<html lang="en" data-jtbd="rosetta-shell-public-good">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rosetta Voice · rosetta-shell</title>
<meta name="description" content="Say a shell construct that breaks between bash 3.2, zsh and POSIX sh. Hear the portable rosetta-shell fix and see which shells break. Free, MIT, part of ARCS public goods.">
<script>(function(){{var d=document.documentElement;try{{var r=JSON.parse(localStorage.getItem('arcsGoodRead')||'{{}}')||{{}};var K={{font:'data-font',size:'data-size',space:'data-space',theme:'data-theme'}};for(var k in K){{if(r[k]&&r[k]!=='std')d.setAttribute(K[k],r[k]);}}}}catch(e){{}}}})();</script>
<style>
{kit_css}
{wordmark}

/* Page layout. Kit tokens only; no signal hex below this line except the tool swatch. */
:root{{--measure:720px}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--g-bg);color:var(--g-text);font-family:var(--ds-font-sans);font-size:var(--fs-body);line-height:1.6;padding:20px 16px 72px}}
.topbar,main{{max-width:var(--measure);margin:0 auto}}
.topbar{{display:flex;align-items:center;gap:12px;margin-bottom:28px}}
.topbar .wordmark{{font-size:var(--fs-label);margin:0}}
h1,h2,h3{{text-wrap:balance;margin:0}}
h1{{font-family:var(--ds-font-sans);font-weight:600;font-size:var(--fs-display);line-height:1.2;margin-bottom:12px}}
h2.section-label{{margin:36px 0 12px}}
p,li{{text-wrap:pretty;margin:0 0 10px}}
.eyebrow{{font-family:var(--ds-font-mono);font-size:var(--fs-label);letter-spacing:.14em;text-transform:uppercase;color:var(--g-text-2);margin-bottom:8px}}
.lede{{color:var(--g-text-2);max-width:none}}
a{{color:var(--g-text);text-decoration:underline;text-underline-offset:3px;text-decoration-color:var(--tool-accent)}}
a:focus-visible{{outline:2px solid var(--g-focus);outline-offset:2px}}
code{{font:400 0.925em var(--ds-font-mono)}}
ul{{margin:0 0 10px;padding-left:22px}}
.chips{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:0 0 20px}}
.chips .g-chip{{justify-content:flex-start}}
@media (max-width:760px){{.chips{{grid-template-columns:1fr}}}}
.panel{{background:var(--g-panel);border:1px solid var(--g-border);border-radius:var(--ds-r-sm);padding:16px 18px;margin:0 0 12px}}
.console{{display:grid;gap:14px;background-image:linear-gradient(var(--tool-accent),var(--tool-accent));background-size:100% 3px;background-repeat:no-repeat}}
.console .row{{align-items:center;gap:12px}}
.mic{{width:64px;height:64px;border-radius:50%;flex:none;cursor:pointer;border:1px solid var(--cyan);background:var(--g-elevated);color:var(--cyan);display:grid;place-items:center}}
.mic svg{{width:26px;height:26px}}
.mic:focus-visible{{outline:2px solid var(--g-focus);outline-offset:3px}}
.mic[data-state="listening"]{{background:var(--cyan);color:var(--g-bg)}}
.status{{min-width:0;flex:1;display:grid;gap:2px}}
.status b{{font-weight:600}}
.status span{{color:var(--g-text-2);font-size:var(--fs-body)}}
form.type{{display:flex;gap:8px;flex-wrap:wrap}}
form.type input{{flex:1 1 220px;min-width:0;min-height:44px;background:var(--g-bg);color:var(--g-text);border:1px solid var(--g-border);border-radius:var(--ds-r-sm);padding:0 12px;font:var(--fs-body) var(--ds-font-mono)}}
form.type input:focus-visible{{outline:2px solid var(--g-focus);outline-offset:2px}}
#chips{{display:flex;flex-wrap:wrap;gap:6px}}
.chip{{min-height:44px;background:transparent;color:var(--g-text-2);border:1px dashed var(--g-border);border-radius:var(--ds-r-pill);padding:0 12px;font:inherit;font-size:var(--fs-body);cursor:pointer}}
.chip:hover{{color:var(--g-text);border-color:var(--g-text-2)}}
.chip:focus-visible{{outline:2px solid var(--g-focus);outline-offset:2px}}
.tape{{border-left:2px solid var(--gold);padding:4px 0 4px 12px;display:grid;gap:4px}}
.tape q{{font:var(--fs-body)/1.5 var(--ds-font-mono);quotes:none;overflow-wrap:anywhere}}
.tape small{{color:var(--g-text-2);font-size:var(--fs-label)}}
.tape small b{{color:var(--gold)}}
#out{{display:grid;gap:12px;margin-top:12px}}
.card{{background:var(--g-panel);border:1px solid var(--g-border);border-radius:var(--ds-r-sm);padding:16px 18px;display:grid;gap:12px;min-width:0}}
.card header{{display:flex;justify-content:space-between;gap:10px;align-items:baseline;flex-wrap:wrap}}
.card h3{{font-size:var(--fs-headline);font-weight:600}}
.tag{{font:700 var(--fs-label)/1 var(--ds-font-mono);letter-spacing:.1em;text-transform:uppercase;padding:5px 8px;border-radius:var(--ds-r-xs);border:1px solid}}
.tag.lint{{color:var(--green)}} .tag.voice{{color:var(--cyan)}} .tag.eg{{color:var(--gold)}}
.why{{margin:0;color:var(--g-text-2)}}
.pair{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:10px}}
.code{{min-width:0;display:grid;gap:5px}}
.code label{{font:700 var(--fs-label)/1 var(--ds-font-mono);letter-spacing:.1em;text-transform:uppercase}}
.code.before label{{color:var(--red)}} .code.after label{{color:var(--green)}}
pre{{margin:0;font-family:var(--ds-font-mono);font-size:var(--fs-body);line-height:1.55;background:var(--g-bg);border:1px solid var(--g-border);border-radius:var(--ds-r-sm);padding:10px 12px;overflow-x:auto}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,120px),1fr));gap:6px}}
.cell{{border:1px solid var(--g-border);border-radius:var(--ds-r-sm);padding:7px 9px;display:grid;gap:2px}}
.cell span{{font:var(--fs-label) var(--ds-font-mono);color:var(--g-text-2)}}
.cell b{{font-weight:600}}
.cell.yes b{{color:var(--green)}} .cell.no b{{color:var(--red)}} .cell.vary b{{color:var(--gold)}}
.fix{{font:var(--fs-body) var(--ds-font-mono)}}
.fix i{{color:var(--g-text-2);font-style:normal}}
.miss{{background:var(--g-panel);border:1px dashed var(--red);border-radius:var(--ds-r-sm);padding:16px 18px;display:grid;gap:6px}}
.miss b{{color:var(--red)}}
.tbl{{overflow-x:auto;padding:4px;border:1px solid var(--g-border);border-radius:var(--ds-r-sm)}}
table{{width:100%;border-collapse:collapse;font-size:var(--fs-body)}}
th,td{{text-align:left;padding:9px 12px;border-bottom:1px solid var(--g-border);vertical-align:top}}
th{{font:700 var(--fs-label) var(--ds-font-mono);letter-spacing:.1em;text-transform:uppercase;color:var(--g-text-2);background:var(--g-panel)}}
tr:last-child td{{border-bottom:0}}
td code{{color:var(--cyan);white-space:nowrap}}
tr[data-hit="1"] td{{background:var(--cyan-bg)}}
.foot{{color:var(--g-text-2)}}
:root{{--tool-accent:#4f5fa0}}
main::before{{content:"";display:block;width:48px;height:3px;background:var(--tool-accent);margin:0 0 14px}}
</style>
{fonts}
<script defer src="/_vercel/insights/script.js"></script>
</head>
<body>
<div class="topbar">
<p class="wordmark" aria-label="ARCS Field OS"><span class="wa">ARCS</span><span class="wf">Field OS</span></p>
<div class="dprefs"><button type="button" class="dprefs-theme" aria-pressed="false" aria-label="Dark mode"><svg viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="10" cy="10" r="3.6"/><path d="M10 1.8v2M10 16.2v2M1.8 10h2M16.2 10h2M4.2 4.2l1.4 1.4M14.4 14.4l1.4 1.4M4.2 15.8l1.4-1.4M14.4 5.6l1.4-1.4"/></svg><span class="dprefs-ttl">Dark mode</span><span class="dprefs-trk" aria-hidden="true"></span></button><button type="button" class="dprefs-aa" aria-expanded="false" aria-controls="dp" aria-label="Reading options"><span aria-hidden="true">Aa</span></button></div>
</div>
<section id="dp" class="dprefs-panel" role="dialog" aria-modal="false" aria-labelledby="dp-h" hidden><p id="dp-h" class="dprefs-title">Reading options</p><div class="dprefs-group" role="group" aria-labelledby="dp-font"><span id="dp-font" class="dprefs-label">Font</span><span class="dprefs-btns"><button type="button" data-k="font" data-v="std" aria-pressed="true">Standard</button><button type="button" data-k="font" data-v="easy" aria-pressed="false">Easy-read</button></span></div><div class="dprefs-group" role="group" aria-labelledby="dp-size"><span id="dp-size" class="dprefs-label">Text size</span><span class="dprefs-btns"><button type="button" data-k="size" data-v="std" aria-pressed="true">Standard</button><button type="button" data-k="size" data-v="l" aria-pressed="false">Larger</button><button type="button" data-k="size" data-v="xl" aria-pressed="false">Largest</button></span></div><div class="dprefs-group" role="group" aria-labelledby="dp-space"><span id="dp-space" class="dprefs-label">Spacing</span><span class="dprefs-btns"><button type="button" data-k="space" data-v="std" aria-pressed="true">Standard</button><button type="button" data-k="space" data-v="roomy" aria-pressed="false">Roomy</button></span></div><div class="dprefs-actions"><button type="button" data-reset>Reset</button><button type="button" data-close>Close</button></div></section>
<main>
<div class="eyebrow">ARCS public goods · rosetta-shell</div>
<h1>Say the bashism. Hear the portable line.</h1>
<p class="lede">Speak a shell construct that breaks when a script moves between bash 3.2, bash 4+, zsh and POSIX sh. Rosetta Voice answers with the fix from rosetta-shell, shows which shells break, and reads it back. What it heard is shown word for word, so you can check every step.</p>
<div class="chips">
<span class="g-chip" data-tone="show"><span class="g-glyph">●</span><span class="g-tag">Proven</span><span class="g-body">rules match the CLI byte for byte</span></span>
<span class="g-chip" data-tone="say"><span class="g-glyph">◆</span><span class="g-tag">Shows</span><span class="g-body">what it heard; never guesses</span></span>
<span class="g-chip" data-tone="limit"><span class="g-glyph">▲</span><span class="g-tag">Six</span><span class="g-body">constructs, the ones lint knows</span></span>
</div>

<section class="panel console" aria-label="Voice console">
<div class="row">
<button class="mic" id="mic" type="button" aria-label="Start listening" data-state="idle"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/></svg></button>
<div class="status" aria-live="polite"><b id="stateLine">Tap the mic and say a construct</b><span id="stateHint">For example: "how do I lowercase a variable" or "declare dash A".</span></div>
<button class="btn" id="speakBtn" type="button" hidden>Read it again</button>
</div>
<form class="type" id="typeForm" autocomplete="off">
<input id="typeIn" type="text" placeholder="Or type a line of shell, or a question" aria-label="Shell line or question">
<button class="btn" type="submit">Translate</button>
</form>
<div id="chips" aria-label="Phrases to try"></div>
<div class="tape" id="tape">
<small><b>Heard, verbatim</b> (example input; nothing has been spoken yet)</small>
<q id="heard">echo -e "lowered: &#36;{{name,,}}"</q>
<small id="how">Matched by the lint rules in bin/rosetta: 2 findings.</small>
</div>
</section>
<section id="out" aria-label="Translation" aria-live="polite"></section>

<h2 class="section-label">The phrasebook: every construct rosetta lint knows</h2>
<div class="tbl"><table>
<thead><tr><th>Construct</th><th>Breaks in</th><th>Portable fix</th></tr></thead>
<tbody id="book"></tbody>
</table></div>

<h2 class="section-label">Your voice and privacy</h2>
<ul>
<li>This page receives only the words, never the sound.</li>
<li>Speech recognition is done by your browser. In Chrome and Edge that sends your audio to the browser maker's speech service (Google or Microsoft); Safari uses Apple's. ARCS stores nothing. If you prefer, type instead: it works the same.</li>
<li>Read-aloud uses your device's built-in voices.</li>
</ul>

<h2 class="section-label">Not proven yet</h2>
<ul>
<li>It knows the six constructs <code>rosetta lint</code> flags. A clean answer is not proof a script is portable; <code>rosetta crossrun</code> is.</li>
<li>Spoken matching uses keywords. When it is unsure it says so and shows what it heard.</li>
<li>Voice input needs a browser that offers speech recognition: Safari (on iPhone, with Siri and Dictation on) or Google Chrome. Comet, Firefox and other iPhone browsers get typing only for now.</li>
</ul>

<h2 class="section-label">For agents</h2>
<p>MIT and public. The rules on this page are a copy of <code>bin/rosetta</code> lint, checked byte for byte by <code>web/parity.test.js</code> in <a href="https://github.com/flashesofbrilliance/rosetta-shell">github.com/flashesofbrilliance/rosetta-shell</a>.</p>
<p class="foot"><a href="/">rosetta-shell home</a></p>
</main>
<script>{js}</script>
<script>
{dp_wire}
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", required=True, help="path to rosetta-shell web/rosetta-voice.html")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    page = build(a.app)
    if a.check:
        ok = OUT.exists() and OUT.read_text() == page
        print("rosetta_voice_build: up to date" if ok else "rosetta_voice_build: STALE, rebuild")
        sys.exit(0 if ok else 1)
    OUT.write_text(page)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(page):,} bytes)")


if __name__ == "__main__":
    main()
