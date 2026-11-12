// Walkthrough video: HTML cards -> Playwright PNGs, macOS `say` narration, ffmpeg.
// Playwright: PLAYWRIGHT_PATH overrides; a worktree has no node_modules, so fall back to the main checkout's.
const { chromium } = require(process.env.PLAYWRIGHT_PATH || '/Users/zharris/arcs-v9/node_modules/playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const OUT = __dirname + '/out';
fs.mkdirSync(OUT, { recursive: true });

const css = `body{margin:0;width:1920px;height:1080px;background:#0d1117;color:#e2e8f0;font-family:-apple-system,Helvetica,sans-serif;display:flex;flex-direction:column;justify-content:center;padding:0 140px;box-sizing:border-box}
h1{font-size:76px;margin:0 0 28px;color:#fff;letter-spacing:-1px}.k{color:#00F0FF;font-size:30px;text-transform:uppercase;letter-spacing:4px;margin-bottom:24px}
p,li{font-size:40px;line-height:1.45;margin:0 0 14px}ul{padding-left:40px;margin:0}pre{font:30px/1.45 Menlo,monospace;background:#020408;border:1px solid #1e293b;border-radius:12px;padding:32px 40px;margin:0;white-space:pre-wrap}
.g{color:#00FF9D}.r{color:#FF4D6D}.y{color:#FFD700}.m{color:#8391a7}table{border-collapse:collapse;font-size:34px}td{padding:14px 28px 14px 0;border-bottom:1px solid #1e293b;vertical-align:top}td:first-child{color:#fff;font-weight:600;white-space:nowrap}`;

const S = [
  { k: 'RFP answering engine', h: 'Clause behind it, or a refusal', b: `<p>Ask a question about a solicitation and its amendments.</p><p>Get an answer with the exact clauses it rests on, <span class="g">or a refusal.</span></p><p class="m">The RFP and amendment are fictional, written for this sample.</p><p class="m">Python standard library only. Nothing to install.</p>`,
    v: 'Ask this engine about an R F P, and it either quotes the exact clause behind its answer, or it refuses. It never guesses. The R F P here is a short fictional one, written for this sample. It is standard library Python, with nothing to install.' },
  { k: 'How it works', h: 'Rules first, model last', b: `<ul><li><b>Parse with rules, not a model.</b> Clauses are numbered; an amendment that revises 7.1 is recorded as superseding it.</li><li><b>Find clauses</b> by keyword search with stemming and a small glossary.</li><li><b>Ask a model</b> to pick clauses and write one sentence, then <span class="g">check it in code</span> before anyone sees it.</li></ul>`,
    v: 'It works in three steps. Documents are split into clauses by rules, not a model, and amendments are recorded as superseding what they change. Search finds the candidate clauses. Only then does a model pick clauses and write one sentence, and code checks that sentence before anyone sees it.' },
  { k: 'Through the MCP server', h: 'What is the bid deposit?', b: `<pre><span class="m">status</span>   <span class="g">answered</span>
<span class="m">answer</span>   the bid deposit is increased from $20,000 to <span class="g">$35,000</span>
<span class="m">cites</span>    RFP §7.1  +  Amendment No. 1 §A1.2
<span class="m">notes</span>    §7.1 is superseded in part by §A1.2; <span class="y">the amended value governs</span>
<span class="m">gate</span>     fast path: verbatim governing text, no model call</pre>`,
    v: 'Here it is through the Claude M C P server. Ask for the bid deposit, and it returns thirty five thousand dollars, citing both the original clause and the amendment that replaced it, with a note that the amended value governs. The gate field says which check decided the outcome.' },
  { k: 'Trust rules, enforced in code', h: 'Refuse rather than bluff', b: `<table><tr><td>No source, no answer</td><td>A cited clause that does not exist is an error</td></tr><tr><td>Figures are quoted</td><td>Every $, date and % must appear word for word in a cited clause</td></tr><tr><td>Amendments win</td><td>Citing a base clause pulls in its replacement</td></tr><tr><td>Not addressed is valid</td><td>Missing appendix? It says so</td></tr><tr><td>No drafting, no bid calls</td><td>Refused before any model call</td></tr><tr><td>Fail closed</td><td>No model means no answer, just the clauses</td></tr></table>`,
    v: 'Six trust rules are enforced in code. No answer without a real source. Figures must appear word for word in a cited clause. An amended value always wins. Not addressed is a valid answer. Drafting and bid decisions are refused. And with no model available, it fails closed.' },
  { k: 'Injected fault', h: 'A model that invents numbers', b: `<pre><span class="m">MOCK_FAULT=invent</span>  model says: "accept $80,000 or 12% less"

<span class="m">status</span>   answered
<span class="m">answer</span>   See the cited text below (the model's summary failed the verbatim check).
<span class="m">gate</span>     <span class="r">verbatim FAILED: ['12%', '$80,000']</span></pre><p class="m" style="margin-top:28px">8 injected faults, all caught: timeout, garbage, fake clause, invented figures, changed figure, superseded figure, drafting, bid verdict.</p>`,
    v: 'To test the checks, the mock model can misbehave on purpose. Here it invents eighty thousand dollars and twelve percent. Neither figure is in the cited clause, so the summary is withheld and only the clause text comes back. Eight injected faults were tried, and every one was caught.' },
  { k: 'Results, measured 2026-10-29', h: 'What was actually run', b: `<ul><li><span class="g">5 of 5</span> deterministic cases pass through the MCP server</li><li>Server output <span class="g">identical</span> to calling the engine directly</li><li><span class="y">3 model-dependent traps not run with a real model</span> (no API key where this was packaged); without one they return <b>unavailable</b>, as designed</li></ul>`,
    v: 'Here is what was measured. Five of five deterministic cases pass through the server, with output identical to calling the engine directly. Three traps need a real model, and those were not run here, because no A P I key was available. Without one, they return unavailable, as designed.' },
  { k: 'Honest gaps', h: 'What it does not do yet', b: `<ul><li>No calibrated confidence score; results are categorical</li><li>Keyword retrieval, no embeddings</li><li>Figures are checked; meaning is not</li><li>Plain text in one numbering style; PDFs need ingest</li><li>Built for RFPs; contract clause types have no special handling</li></ul>`,
    v: 'The gaps, plainly. There is no confidence score. Retrieval is keyword based. Figures are checked, but meaning is not. It reads plain text in one numbering style. And it was built for R F Ps, so contract clause types like indemnity get no special handling yet.' },
  { k: 'Try it', h: 'One command in Claude Code', b: `<pre>claude mcp add rfp-intelligence \\
  -e MODEL_PROVIDER=mock \\
  -- python3 /PATH/TO/dioptra-work-sample/mcp/server.py</pre><p class="m" style="margin-top:28px">Then: “Using rfp-intelligence, what is the bid deposit?” &nbsp;·&nbsp; Setup and checks: mcp/README.md</p>`,
    v: 'To try it, add the server to Claude Code with one command, and ask about the bid deposit. Setup and the checks are in the M C P read me.' },
];

(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  const parts = [];
  for (let i = 0; i < S.length; i++) {
    const s = S[i], n = String(i + 1).padStart(2, '0');
    await pg.setContent(`<html><head><style>${css}</style></head><body><div class="k">${s.k}</div><h1>${s.h}</h1>${s.b}</body></html>`);
    await pg.screenshot({ path: `${OUT}/${n}.png` });
    // Zach's own takes in voice/NN.<ext> win; otherwise fall back to `say`.
    const own = ['m4a', 'wav', 'mp3', 'aiff'].map(e => `${__dirname}/voice/${n}.${e}`).find(f => fs.existsSync(f));
    if (!own) execFileSync('say', ['-v', 'Samantha', '-r', '175', '-o', `${OUT}/${n}.aiff`, s.v]);
    // Card time = take + 0.8 s pad, exactly. (-shortest overshot ~1.9 s of silent picture per card on a looped still.)
    const take = own || `${OUT}/${n}.aiff`;
    const dur = parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', take]).toString()) + 0.8;
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-loop', '1', '-i', `${OUT}/${n}.png`, '-i', take,
      '-af', 'apad=pad_dur=0.8', '-c:v', 'libx264', '-tune', 'stillimage', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-t', dur.toFixed(3), `${OUT}/${n}.mp4`]);
    parts.push(`file '${OUT}/${n}.mp4'`);
  }
  await b.close();
  fs.writeFileSync(`${OUT}/list.txt`, parts.join('\n'));
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', `${OUT}/list.txt`, '-c', 'copy', `${OUT}/walkthrough.mp4`]);
  console.log('ok', `${OUT}/walkthrough.mp4`);
})();
