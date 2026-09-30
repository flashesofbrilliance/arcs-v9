import json, html
sn = json.load(open("snippets.json"))
E = html.escape

STEPS = [
 dict(v="analysis", n=1, name="Find the facts", kid="When you need to know what's true before building on it.", tool="Analysis by ARCS", stamp="go",
      gates=[("pass","Every fact says where it came from","41 of 41"),("pass","Big claims have two separate sources","6 big claims, all with 2+"),("pass","Every source is on the evidence list","0 missing")],
      rubric=[("Did we look in the obvious places?",None),("Did we use the original, not a summary?",None),("Did we keep the question open?",None),("Did we log the weird stuff?",None)], extra=""),
 dict(v="assessment", n=2, name="Check the facts", kid="When you need to tell a solid fact from a shaky one.", tool="Assessment by ARCS", stamp="go",
      gates=[("pass","Every fact has a verdict and a size","41 of 41"),("pass","A fact marked true was found in step 1","36 of 36"),("pass","The totals match the list","36 true, 2 gaps, 3 unsure")],
      rubric=[("Is each problem sized right?",2),("Are the gaps said as plainly as the wins?",1),("No hedging to sound safe?",2),("Are the objections written down?",2)],
      extra='''<div class="fid"><p class="fid-row sharp"><span class="tag t-go">true</span>Setup takes under 10 minutes on the demo.</p><p class="fid-row degraded"><span class="tag t-warn">gap</span>The deck says 40 customers. The case page lists 12.</p><p class="fid-row grain"><span class="tag t-unsure">unsure</span>No security report (SOC 2) was found.</p><p class="note">Shaky facts look shaky. Only true facts render sharp.</p></div>'''),
 dict(v="evaluation", n=3, name="Poke holes", kid="When you need to find the weak spot before someone else does.", tool="Evaluation by ARCS", stamp="go",
      gates=[("pass","At least 4 reviewers ran","6 ran"),("pass","Each reviewer gave a reason","6 of 6"),("pass","Someone actually disagreed","2 disagreed: the risk reviewer and the skeptic"),("pass","The result follows from the reviews","pass, with 2 fixes required")],
      rubric=[("Was the best objection a real one?",2),("Did we argue the product works?",2),("Did we argue we can prove it?",1),("Are the required fixes concrete?",2)],
      extra='''<div class="meter"><p><strong>Too-agreeable check:</strong> fine. 9 agreements, 5 disagreements.</p><div class="bar" role="img" aria-label="Agreement ratio 1.5, limit 4"><i style="width:36%" class="b-go"></i><span class="lim" style="left:80%"></span></div><p class="note">If reviewers only agree, this step stops. A test nothing could fail is not a test.</p></div>'''),
 dict(v="synthesis", n=4, name="Make it short", kid="When you need it short without adding anything unchecked.", tool="Synthesis by ARCS", stamp="stop",
      gates=[("fail","No new facts snuck in",'"Trusted by 50+ teams" was never checked'),("fail","Required fixes were made","the 40-customer number still looks certain"),("pass","Writing has no filler","clean"),("pass","No long dashes","0"),("pass","Hidden from search until ready","yes")],
      rubric=[("Plain words?",2),("Clear structure?",1),("Easy rhythm?",2),("Specific, not vague?",2),("About five times shorter?",2)], extra=""),
 dict(v="recapitulation", n=5, name="Write the note", kid="When you need a note that's ready for a person to send.", tool="Recapitulation by ARCS", stamp="wait",
      gates=[("pass","Still marked as a draft","DRAFT"),("pass","Our prediction was written down first","filed before the draft"),("pass","The note says nothing the short version didn't","5 of 5"),("pass","Not too agreeable","borderline: 13 agreements, 2 disagreements")],
      rubric=[("Does it sound right for this person?",2),("Honest about what we dropped and kept?",1),("Is the ask clear?",2),("Did we note to follow up?",2)], extra=""),
]
STAMP = {"go": ("Go", "s-go"), "stop": ("Stop", "s-stop"), "wait": ("Ready for a person", "s-wait")}

def pips(sc):
    if sc is None:
        return '<span class="pips" aria-label="not scored yet"><i class="pend"></i><i class="pend"></i></span>'
    return f'<span class="pips" aria-label="{sc} of 2">' + "".join(f'<i class="{"on" if k < sc else ""}"></i>' for k in range(2)) + "</span>"

def snip(v):
    tabs = list(sn[v].keys())
    b = "".join(f'<button type="button" role="tab" id="t-{v}-{i}" aria-selected="{str(i==0).lower()}" aria-controls="p-{v}-{i}">{k}</button>' for i, k in enumerate(tabs))
    p = "".join(f'<div class="code" role="tabpanel" id="p-{v}-{i}" aria-labelledby="t-{v}-{i}"{"" if i==0 else " hidden"}><button type="button" class="copy">Copy</button><pre><code>{E(sn[v][k])}</code></pre></div>' for i, k in enumerate(tabs))
    return f'<div class="snip"><div class="tabs" role="tablist" aria-label="Code type">{b}</div>{p}</div>'

def step_card(s):
    lab, cls = STAMP[s["stamp"]]
    return f'<li class="step {cls}"><a href="#{s["v"]}"><span class="num">{s["n"]}</span><strong>{s["name"]}</strong><span class="kid">{s["kid"]}</span><span class="foot"><code class="tool">{s["v"]}-by-arcs</code><span class="checks">{len(s["gates"])} checks, all visible</span></span><span class="stamp">{lab}</span></a></li>'

def detail(s):
    lab, cls = STAMP[s["stamp"]]
    g = "".join(f'<li class="g g-{st}"><span class="dot" aria-hidden="true"></span><span class="gt">{E(t)}</span><span class="ge">{E(ev)}</span><span class="sr">{"passed" if st=="pass" else "failed"}</span></li>' for st, t, ev in s["gates"])
    r = "".join(f'<li><span>{E(t)}</span>{pips(sc)}</li>' for t, sc in s["rubric"])
    return f'''<details class="deep {cls}" id="{s["v"]}"{" open" if s["stamp"]=="stop" else ""}>
  <summary><span class="num">{s["n"]}</span><span class="st-name">{s["name"]}</span><span class="st-tool">{s["tool"]}</span><span class="stamp">{lab}</span><svg class="chev" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 6l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></summary>
  <div class="deep-body">
    <div class="half"><h3>Machine checks</h3><p class="note">Any one of these fails, the step says stop.</p><ul class="gates">{g}</ul>{s["extra"] if s["v"]!="assessment" else ""}</div>
    <div class="half"><h3>Person checks</h3><p class="note">Scored 0 to 2 by a person. The tool never scores these itself.</p><ul class="rubric">{r}</ul>{s["extra"] if s["v"]=="assessment" else ""}</div>
    <div class="full"><h3>Copy it</h3>{snip(s["v"])}</div>
  </div>
</details>'''

ENGINE = open("engine.js").read()
FIXTURES = open("fixtures.json").read().replace("</", "<\\/")
CONTROLLER = open("controller.js").read()
page = f'''<title>Five Verbs by ARCS</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
/* ARCS Recoil Report — Design Tokens */
/* inlined verbatim from src/ui-kit/recoil-report/_tokens.css; single dark world by choice */
:root {{
  --bg:        #020408;
  --surface:   #0d1117;
  --surface-2: #121820;
  --border:    #1e293b;
  --text:      #e2e8f0;
  --muted:     #475569;
  --dimmed:    #64748b;
  --cyan:      #00F0FF;
  --green:     #00FF9D;
  --gold:      #FFD700;
  --red:       #FF4D6D;
  --cyan-bg:   rgba(0, 240, 255, 0.07);
  --green-bg:  rgba(0, 255, 157, 0.07);
  --gold-bg:   rgba(255, 215,   0, 0.07);
  --red-bg:    rgba(255,  77, 109, 0.07);
  --cyan-glow:  0 0 5px rgba(0,240,255,0.22);
  --green-glow: 0 0 5px rgba(0,255,157,0.22);
  --red-glow:   0 0 5px rgba(255,77,109,0.22);
  --r-sm: 4px;
  --r-md: 8px;
  --r-lg: 12px;
  --font-mono:  'GeistMono', 'JetBrains Mono', 'IBM Plex Mono', monospace;
  --font-sans:  'InstrumentSans', 'Instrument Sans', 'Work Sans', system-ui, sans-serif;
  --font-display: 'BricolageGrotesque', 'Bricolage Grotesque', 'Work Sans', system-ui, sans-serif;
}}
/* page layer: one readable secondary text tone (the kit's --dimmed is 3.9:1 on surface, under 4.5) */
/* layout: verdict, the five steps as one flowing strip, three reasons, three answers, try it, then the evidence behind a click */
:root {{ --soft: #9aa7b8; --lane: 1080px; --measure: 640px; color-scheme: dark; }}
* {{ box-sizing: border-box; }}
html {{ scrollbar-color: var(--border) var(--bg); }}
::selection {{ background: rgba(0,240,255,0.28); color: var(--text); }}
body {{ margin: 0; background: var(--bg); color: var(--text); font: 400 16px/1.6 var(--font-sans); padding-inline: 16px; padding-block: 0 72px; caret-color: var(--cyan); }}
.lane {{ max-width: var(--lane); margin: 0 auto; }}
h1, h2, h3 {{ font-family: var(--font-display); text-wrap: balance; margin: 0; letter-spacing: -0.015em; }}
p {{ margin: 0; }}
a {{ color: var(--cyan); text-underline-offset: 3px; }}
:focus-visible {{ outline: 2px solid var(--cyan); outline-offset: 3px; border-radius: var(--r-sm); }}
.note {{ color: var(--soft); font-size: 14px; }}
section {{ margin-top: 72px; }}
section > h2 {{ font-size: clamp(24px, 3vw, 30px); font-weight: 700; margin-bottom: 20px; }}

/* verdict */
.verdict {{ padding-block: 72px 36px; display: grid; gap: 18px; }}
.verdict h1 {{ font-size: clamp(40px, 7vw, 76px); font-weight: 700; line-height: 1; letter-spacing: -0.03em; }}
.verdict h1 span {{ color: var(--cyan); }}
.verdict .lede {{ font-size: clamp(18px, 2vw, 21px); color: var(--text); opacity: 0.88; max-width: none; }}

/* the five steps: one strip, the current runs through it and stops at the red stamp */
.strip {{ list-style: none; margin: 8px 0 0; padding: 0; display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; position: relative; }}
.strip::before {{ content: ""; position: absolute; left: 24px; right: 24px; top: 31px; height: 2px; background: var(--border); }}
.strip::after {{ content: ""; position: absolute; left: 24px; top: 31px; height: 2px; width: calc(75% - 12px); background: linear-gradient(90deg, var(--cyan), var(--green) 60%, var(--red)); transform-origin: left; animation: run 1.4s cubic-bezier(.16,1,.3,1) both; }}
@keyframes run {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
.step a {{ position: relative; z-index: 1; display: flex; flex-direction: column; gap: 6px; height: 100%; padding: 16px; background: var(--surface); border: 1px solid var(--border); border-radius: var(--r-lg); color: var(--text); text-decoration: none; transition: border-color .2s, transform .2s cubic-bezier(.16,1,.3,1); }}
.step a:hover {{ border-color: var(--soft); transform: translateY(-2px); }}
.num {{ display: inline-grid; place-items: center; width: 30px; height: 30px; border-radius: 50%; font: 500 13px var(--font-mono); background: var(--bg); border: 2px solid currentColor; }}
.step strong {{ font: 600 18px/1.25 var(--font-display); }}
.step .kid {{ color: var(--soft); font-size: 15px; }}
.stamp {{ justify-self: start; margin-top: 4px; font: 600 12px var(--font-sans); letter-spacing: 0.04em; padding: 3px 10px; border-radius: 999px; border: 1px solid currentColor; }}
.s-go .stamp {{ color: var(--green); }} .s-stop .stamp {{ color: var(--red); }} .s-wait .stamp {{ color: var(--cyan); }}
.s-go .num {{ color: var(--green); }} .s-stop .num {{ color: var(--red); }} .s-wait .num {{ color: var(--cyan); }}
.s-go .num {{ border-color: var(--green); }} .s-stop .num {{ border-color: var(--red); }} .s-wait .num {{ border-color: var(--cyan); }}
.step.s-stop a {{ border-color: rgba(255,77,109,0.55); background: linear-gradient(var(--red-bg), var(--red-bg)), var(--surface); }}
.step.s-wait a {{ border-style: dashed; }}
.foot {{ display: grid; gap: 2px; margin-top: auto; padding-top: 10px; border-top: 1px solid var(--border); }}
.tool {{ font: 500 12px var(--font-mono); color: var(--cyan); }}
.checks {{ font-size: 13px; color: var(--soft); }}
.example {{ margin-top: 18px; font-size: 17px; }}
.example strong {{ color: var(--red); font-weight: 600; }}
.example .tag-ex {{ color: var(--soft); font-size: 14px; }}

/* three reasons */
.reasons {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 32px; }}
.reasons h3 {{ font-size: 19px; font-weight: 600; margin-bottom: 6px; }}
.reasons p {{ color: var(--soft); }}

/* three answers */
.qa {{ display: grid; gap: 0; border-top: 1px solid var(--border); }}
.qa div {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.4fr); gap: 24px; padding-block: 18px; border-bottom: 1px solid var(--border); }}
.qa dt {{ font: 600 18px/1.35 var(--font-display); }}
.qa dd {{ margin: 0; color: var(--soft); }}
.qa dd strong {{ color: var(--text); font-weight: 600; }}

/* try it */
.try {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }}
.try .code pre {{ font-size: 14px; }}
.try p {{ margin-bottom: 8px; }}

/* code */
.code {{ position: relative; min-width: 0; }}
.code pre {{ margin: 0; background: var(--bg); border: 1px solid var(--border); border-radius: var(--r-md); padding: 16px 16px 16px; padding-right: 76px; overflow-x: auto; font: 400 13px/1.6 var(--font-mono); color: var(--text); }}
.copy {{ position: absolute; top: 10px; right: 10px; font: 500 12px var(--font-sans); color: var(--text); background: var(--surface-2); border: 1px solid var(--border); border-radius: var(--r-sm); padding: 5px 10px; cursor: pointer; }}
.copy:hover {{ border-color: var(--cyan); color: var(--cyan); }}
.tabs {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }}
.tabs button {{ font: 500 13px var(--font-sans); color: var(--soft); background: transparent; border: 1px solid var(--border); border-radius: 999px; padding: 5px 12px; cursor: pointer; }}
.tabs button:hover {{ color: var(--text); }}
.tabs button[aria-selected="true"] {{ color: var(--bg); background: var(--cyan); border-color: var(--cyan); }}

/* evidence behind a click */
.deep {{ border: 1px solid var(--border); border-radius: var(--r-lg); background: var(--surface); scroll-margin-top: 24px; }}
.deep + .deep {{ margin-top: 10px; }}
.deep.s-stop {{ border-color: rgba(255,77,109,0.55); }}
summary {{ list-style: none; cursor: pointer; display: grid; grid-template-columns: auto minmax(0, 1fr) auto auto auto; gap: 14px; align-items: center; padding: 16px 18px; }}
summary::-webkit-details-marker {{ display: none; }}
.st-name {{ font: 600 18px var(--font-display); color: var(--text); }}
.st-tool {{ color: var(--soft); font-size: 14px; }}
summary .stamp {{ margin: 0; }}
.chev {{ width: 18px; height: 18px; color: var(--soft); transition: transform .25s cubic-bezier(.16,1,.3,1); }}
details[open] .chev {{ transform: rotate(180deg); }}
.deep-body {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 28px; padding: 6px 18px 22px; border-top: 1px solid var(--border); padding-top: 20px; }}
.deep-body .full {{ grid-column: 1 / -1; }}
.half, .full {{ display: grid; grid-template-columns: minmax(0, 1fr); gap: 10px; align-content: start; min-width: 0; }}
.deep h3 {{ font-size: 16px; font-weight: 600; }}
.gates, .rubric {{ list-style: none; margin: 0; padding: 0; display: grid; gap: 0; }}
.g {{ display: grid; grid-template-columns: 14px minmax(0, 1fr); column-gap: 10px; padding-block: 10px; border-bottom: 1px solid var(--border); }}
.g .dot {{ width: 10px; height: 10px; border-radius: 50%; margin-top: 7px; grid-row: span 2; }}
.g-pass .dot {{ background: var(--green); }} .g-fail .dot {{ background: var(--red); box-shadow: 0 0 0 3px var(--red-bg); }}
.gt {{ font-weight: 500; }} .g-fail .gt {{ color: var(--red); }}
.ge {{ color: var(--soft); font-size: 14px; }}
.sr {{ position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }}
.rubric li {{ display: flex; justify-content: space-between; gap: 16px; align-items: center; padding-block: 10px; border-bottom: 1px solid var(--border); }}
.pips {{ display: inline-flex; gap: 4px; flex: none; }}
.pips i {{ width: 18px; height: 6px; border-radius: 3px; background: var(--border); }}
.pips i.on {{ background: var(--cyan); }}
.pips i.pend {{ background: repeating-linear-gradient(90deg, var(--muted) 0 2px, transparent 2px 4px); }}
.fid, .meter {{ display: grid; gap: 8px; padding: 14px; border: 1px solid var(--border); border-radius: var(--r-md); background: var(--bg); margin-top: 6px; }}
.fid-row {{ display: grid; grid-template-columns: 64px minmax(0, 1fr); gap: 10px; align-items: baseline; font-size: 15px; }}
.sharp {{ opacity: 1; font-weight: 500; }} .degraded {{ opacity: 0.85; }} .grain {{ opacity: 0.7; font-weight: 300; letter-spacing: 0.02em; }}
.tag {{ font: 600 11px var(--font-sans); text-align: center; padding: 2px 6px; border-radius: var(--r-sm); border: 1px solid currentColor; }}
.t-go {{ color: var(--green); }} .t-warn {{ color: var(--gold); }} .t-unsure {{ color: var(--soft); }}
.bar {{ position: relative; height: 8px; border-radius: 4px; background: var(--surface-2); }}
.bar i {{ position: absolute; inset: 0 auto 0 0; border-radius: 4px; }} .b-go {{ background: var(--green); }}
.lim {{ position: absolute; top: -4px; bottom: -4px; width: 2px; background: var(--gold); }}

/* playground */
.play {{ border: 1px solid var(--border); border-radius: var(--r-lg); background: var(--surface); padding: 18px; display: grid; gap: 16px; }}
.play-grid {{ display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr); gap: 20px; }}
.play-in {{ display: grid; gap: 10px; min-width: 0; align-content: start; }}
.play-in label {{ font-weight: 500; }}
textarea {{ width: 100%; min-height: 260px; resize: vertical; background: var(--bg); color: var(--text); border: 1px solid var(--border); border-radius: var(--r-md); padding: 14px; font: 400 13px/1.55 var(--font-mono); }}
textarea:focus {{ outline: none; border-color: var(--cyan); }}
.play-actions {{ display: flex; flex-wrap: wrap; gap: 8px; }}
.btn {{ font: 500 14px var(--font-sans); color: var(--text); background: var(--surface-2); border: 1px solid var(--border); border-radius: var(--r-md); padding: 9px 14px; cursor: pointer; }}
.btn:hover {{ border-color: var(--soft); }}
.btn.primary {{ background: var(--cyan); color: var(--bg); border-color: var(--cyan); font-weight: 600; }}
.btn.primary:hover {{ filter: brightness(1.08); }}
.btn.file {{ position: relative; overflow: hidden; }}
.btn.file input {{ position: absolute; inset: 0; opacity: 0; cursor: pointer; }}
.btn.file:focus-within {{ outline: 2px solid var(--cyan); outline-offset: 3px; }}
.play-out {{ min-width: 0; border: 1px solid var(--border); border-radius: var(--r-md); background: var(--bg); padding: 16px; display: grid; gap: 12px; align-content: start; }}
.play-out .empty {{ color: var(--soft); }}
.res-head {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }}
.res-head strong {{ font: 700 22px var(--font-display); }}
.big {{ font: 700 15px var(--font-sans); padding: 6px 14px; border-radius: 999px; border: 1.5px solid currentColor; }}
.big.go {{ color: var(--green); background: var(--green-bg); }} .big.stop {{ color: var(--red); background: var(--red-bg); }}
.g-cli .dot {{ background: transparent; border: 1.5px solid var(--soft); }}
.res-note {{ color: var(--soft); font-size: 14px; }}
.err {{ color: var(--red); }}

/* depth last */
.depth {{ display: grid; gap: 10px; }}
footer {{ margin-top: 72px; color: var(--soft); font-size: 14px; display: grid; gap: 4px; }}

@media (max-width: 900px) {{
  .strip {{ grid-template-columns: minmax(0, 1fr); gap: 8px; }}
  .strip::before, .strip::after {{ display: none; }}
  .step a {{ display: grid; grid-template-columns: auto minmax(0, 1fr) auto; column-gap: 12px; align-items: center; }}
  .step .kid {{ grid-column: 2; }}
  .step .stamp {{ grid-column: 3; grid-row: 1 / span 3; margin: 0; }}
  .step .foot {{ grid-column: 2; }}
  .reasons, .try {{ grid-template-columns: minmax(0, 1fr); gap: 20px; }}
  .qa div {{ grid-template-columns: minmax(0, 1fr); gap: 4px; }}
  .deep-body, .play-grid {{ grid-template-columns: minmax(0, 1fr); }}
  summary {{ grid-template-columns: auto minmax(0, 1fr) auto auto; }}
  .st-tool {{ display: none; }}
}}
@media (prefers-reduced-motion: reduce) {{ .strip::after {{ animation: none; }} .step a, .chev {{ transition: none; }} }}
</style>

<main class="lane">
  <header class="verdict">
    <h1>Check it <span>before you say it.</span></h1>
    <p class="lede">Five steps between an idea and a message. Each step gets a stamp: go or stop. If any step says stop, you fix it before anyone hears it.</p>
  </header>

  <ol class="strip" aria-label="The five steps">
    {"".join(step_card(s) for s in STEPS)}
  </ol>
  <p class="example"><span class="tag-ex">Example run:</span> steps 1 to 3 said go. Step 4 said <strong>stop</strong>, because the short version added "trusted by 50+ teams" and nobody had checked it.</p>

  <section aria-labelledby="why">
    <h2 id="why">Why bother</h2>
    <div class="reasons">
      <div><h3>Nothing sneaks in</h3><p>Each step can only use what the step before it approved. A fact that skipped a check gets caught.</p></div>
      <div><h3>No yes-men</h3><p>If every reviewer just agrees, the check fails. Someone has to have tried to break it.</p></div>
      <div><h3>A person hits send</h3><p>The last step can only say "ready." It never sends anything for you.</p></div>
    </div>
  </section>

  <section aria-labelledby="qa">
    <h2 id="qa">Three questions</h2>
    <dl class="qa">
      <div><dt>Is this the AI's chain of thought?</dt><dd><strong>No.</strong> It checks the finished work, not the thinking. Each step saves a file you can open later.</dd></div>
      <div><dt>What do I need to run it?</dt><dd><strong>Just Python.</strong> Nothing to install. It runs in a terminal, in code, in GitHub, or before each commit.</dd></div>
      <div><dt>Who decides the parts a machine can't?</dt><dd><strong>A person.</strong> Each step has a short scorecard. The tool leaves it blank for you.</dd></div>
    </dl>
  </section>

  <section aria-labelledby="try">
    <h2 id="try">Try it on your own work</h2>
    <p class="note" style="margin:-8px 0 18px">Pick a step, paste your work, press Check it. It runs in this page. Nothing is uploaded.</p>
    <div class="play">
      <div class="tabs" role="tablist" aria-label="Step to check" id="play-tabs">{"".join(f'<button type="button" role="tab" data-verb="{s["v"]}" aria-selected="{str(i==0).lower()}">{s["n"]}. {s["name"]}</button>' for i, s in enumerate(STEPS))}</div>
      <div class="play-grid">
        <div class="play-in">
          <label for="play-text" id="play-label">Your work (HTML with marked facts)</label>
          <textarea id="play-text" spellcheck="false" rows="12"></textarea>
          <div class="play-actions">
            <button type="button" class="btn primary" id="play-run">Check it</button>
            <button type="button" class="btn" id="play-good">Load example</button>
            <button type="button" class="btn" id="play-bad">Load a broken one</button>
            <label class="btn file" id="play-nb-wrap">Use a notebook (.ipynb)<input type="file" id="play-nb" accept=".ipynb,application/json"></label>
          </div>
        </div>
        <div class="play-out" id="play-out" aria-live="polite">
          <p class="empty">Press <strong>Check it</strong> to see the stamp. Start with "Load a broken one" to watch a check catch it.</p>
        </div>
      </div>
    </div>
  </section>

  <section aria-labelledby="inside">
    <h2 id="inside">Inside each step</h2>
    <p class="note" style="margin:-8px 0 16px">Open a step to see its checks and copy its code. Step 4 is open because that's where the example stopped.</p>
    {"".join(detail(s) for s in STEPS)}
  </section>

  <section aria-labelledby="builders">
    <h2 id="builders">For builders</h2>
    <div class="depth">
      <div class="try"><div><p>Prove every check catches a bad example:</p><div class="code"><button type="button" class="copy">Copy</button><pre><code>make test</code></pre></div></div><div><p>Run all five steps on the sample:</p><div class="code"><button type="button" class="copy">Copy</button><pre><code>make demo</code></pre></div></div></div>
      <details class="deep"><summary><span class="st-name">All five steps as one GitHub workflow</span><span></span><span></span><span></span><svg class="chev" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 6l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></summary><div class="deep-body"><div class="full"><div class="code"><button type="button" class="copy">Copy</button><pre><code>{E(sn["_full"])}</code></pre></div></div></div></details>
      <details class="deep"><summary><span class="st-name">What each step saves</span><span></span><span></span><span></span><svg class="chev" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 6l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></summary><div class="deep-body"><div class="full"><p class="note">One format for all five. The next step reads it.</p><div class="code"><button type="button" class="copy">Copy</button><pre><code>{E(json.dumps({"verb":"synthesis","fate":"hold","upstream":"evaluation.json#sha256:9f1c","gates":[{"id":"no-new-claims","ok":False,"evidence":"line 212"}],"rubric":[{"row":"D-specificity","score":2,"judge":"human"}],"sycophancy":{"agreement":4,"dissent":3,"verdict":"OK","blocking":False}}, indent=2))}</code></pre></div></div></div></details>
    </div>
  </section>

  <footer>
    <p>Example data from a made-up review, not a real run.</p>
    <p>arcs-verb-eval · Python standard library only · tokens from the ARCS recoil-report kit.</p>
  </footer>
</main>

<script>
{ENGINE}
var FX = {FIXTURES};
{CONTROLLER}
document.querySelectorAll('[role=tablist]:not(#play-tabs)').forEach(function (list) {{
  var tabs = list.querySelectorAll('[role=tab]');
  tabs.forEach(function (t, i) {{
    t.addEventListener('click', function () {{ pick(i); }});
    t.addEventListener('keydown', function (e) {{
      if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {{
        var j = (i + (e.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length;
        pick(j); tabs[j].focus();
      }}
    }});
  }});
  function pick(k) {{
    tabs.forEach(function (o, i) {{
      o.setAttribute('aria-selected', i === k);
      o.tabIndex = i === k ? 0 : -1;
      document.getElementById(o.getAttribute('aria-controls')).hidden = i !== k;
    }});
  }}
  pick(0);
}});
document.querySelectorAll('.copy').forEach(function (b) {{
  b.addEventListener('click', function () {{
    var code = b.parentNode.querySelector('code');
    var done = function () {{ b.textContent = 'Copied'; setTimeout(function () {{ b.textContent = 'Copy'; }}, 1400); }};
    var fallback = function () {{
      var r = document.createRange(); r.selectNodeContents(code);
      var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(r);
      b.textContent = 'Selected: press Cmd+C';
    }};
    try {{ navigator.clipboard.writeText(code.textContent).then(done, fallback); }} catch (e) {{ fallback(); }}
  }});
}});
document.querySelectorAll('.step a').forEach(function (a) {{
  a.addEventListener('click', function () {{
    var d = document.querySelector(a.getAttribute('href'));
    if (d && d.tagName === 'DETAILS') d.open = true;
  }});
}});
</script>
'''
open("verb-eval-mockups.html", "w").write(page)
