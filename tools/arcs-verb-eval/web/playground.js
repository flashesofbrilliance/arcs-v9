(function () {
  var LABEL = { analysis: 'Your work (HTML with marked facts)', assessment: 'Your checked facts (HTML with verdicts)', evaluation: 'Your reviews (JSON)', synthesis: 'Your short version (HTML)', recapitulation: 'Your draft note (text)' };
  var TOOL = { analysis: 'Analysis by ARCS', assessment: 'Assessment by ARCS', evaluation: 'Evaluation by ARCS', synthesis: 'Synthesis by ARCS', recapitulation: 'Recapitulation by ARCS' };
  var NAMES = { analysis: 'Find the facts', assessment: 'Check the facts', evaluation: 'Poke holes', synthesis: 'Make it short', recapitulation: 'Write the note' };
  var PLAIN = { 'has-claims': 'Found facts to check', 'every-claim-sourced': 'Every fact says where it came from', 'high-stakes-two-sources': 'Big claims have two separate sources',
    'verdict-and-severity': 'Every fact has a verdict and a size', 'verified-was-sourced': 'A fact marked true was found in step 1', 'verified-numbers-in-evidence': 'True facts match their source numbers',
    'summary-matches-rows': 'The totals match the list', 'min-lenses': 'Enough reviewers ran', 'lens-result-and-reason': 'Each reviewer gave a reason', 'dissent-floor': 'Someone actually disagreed',
    'verdict-follows': 'The result follows from the reviews', 'conditions-cite-claims': 'Required fixes point at real facts', sycophancy: 'Not too agreeable', 'no-new-claims': 'No new facts snuck in',
    'conditions-honored': 'Required fixes were made', 'render-matches-verdict': 'Shaky facts look shaky', 'em-dash-zero': 'No long dashes', noindex: 'Hidden from search until ready',
    'draft-marker': 'Still marked as a draft', 'ex-ante-receipt': 'Our prediction was written down first', 'pre-send-gauntlet': 'The pre-send review is on file', 'note-claims-resolve': 'The note only says what the short version said' };
  var state = { verb: null, text: {}, prints: {} };
  var tabs = document.querySelectorAll('#play-tabs [role=tab]'), ta = document.getElementById('play-text'), out = document.getElementById('play-out');
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;'); }
  function select(v) {
    if (state.verb) state.text[state.verb] = ta.value;
    state.verb = v;
    tabs.forEach(function (t) { var on = t.getAttribute('data-verb') === v; t.setAttribute('aria-selected', on); t.tabIndex = on ? 0 : -1; });
    document.getElementById('play-label').textContent = LABEL[v];
    document.getElementById('play-nb-wrap').hidden = v !== 'analysis';
    ta.value = state.text[v] != null ? state.text[v] : FX.examples.good[v];
    out.innerHTML = '<p class="empty">Press <strong>Check it</strong> to see the stamp.</p>';
  }
  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { select(t.getAttribute('data-verb')); });
    t.addEventListener('keydown', function (e) { if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { var j = (i + (e.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length; tabs[j].click(); tabs[j].focus(); } });
  });
  document.getElementById('play-good').onclick = function () { ta.value = FX.examples.good[state.verb]; };
  document.getElementById('play-bad').onclick = function () { ta.value = FX.examples.bad[state.verb]; };
  document.getElementById('play-nb').onchange = function (e) {
    var f = e.target.files[0]; if (!f) return;
    var rd = new FileReader();
    rd.onload = function () {
      try {
        var r = AVE.fromNotebook(rd.result, f.name);
        if (!r.claims.length) { out.innerHTML = '<p class="err">No sentences with numbers were found in this notebook\'s text cells, so there is nothing to check.</p>'; return; }
        state.text.assessment = r.assessment; ta.value = r.analysis;
        out.innerHTML = '<p class="res-note">Found ' + r.claims.length + ' facts in ' + esc(f.name) + '. Step 2 is filled in too. Press <strong>Check it</strong>.</p>';
      } catch (err) { out.innerHTML = '<p class="err">That file is not a readable notebook: ' + esc(err.message) + '</p>'; }
    };
    rd.readAsText(f);
  };
  function prevVerb(v) { var i = AVE.VERBS.indexOf(v); return i > 0 ? AVE.VERBS[i - 1] : null; }
  document.getElementById('play-run').onclick = function () {
    var v = state.verb, pv = prevVerb(v), up = pv ? state.prints[pv] || null : null, rep;
    try { rep = AVE.evaluate(v, ta.value, up); }
    catch (err) { out.innerHTML = '<p class="err">Could not read this as ' + (v === 'evaluation' ? 'JSON' : 'input') + ': ' + esc(err.message) + '. Try "Load example" to see the expected shape.</p>'; return; }
    state.prints[v] = rep; state.text[v] = ta.value;
    state.json = state.json || {};
    var tr0 = AVE.trace(rep, ta.value, FX.rubric[v]);
    state.json[v] = { verb: v, tool: TOOL[v], fate: rep.fate, ok: rep.ok, failed: rep.failed, upstream: pv && up ? pv : null,
      gates: rep.gates.map(function (g) { return { id: g.id, ok: g.ok, evidence: g.evidence, ms: g.ms, cli_only: g.cliOnly || undefined }; }),
      rubric: FX.rubric[v].map(function (r) { return { row: r.row, label: r.label, score: null, judge: 'pending' }; }),
      sycophancy: rep.sycophancy, claims: rep.claims || [], conditions: rep.conditions || [], trace: tr0,
      source: 'arcs-verb-eval web (browser engine)' };
    var tr = AVE.trace(rep, ta.value, FX.rubric[v]), sum = tr[tr.length - 1];
    var html = '<div class="res-head"><strong>' + NAMES[v] + '</strong><span class="big ' + (rep.ok ? 'go' : 'stop') + '">' + (rep.ok ? (v === 'recapitulation' ? 'Ready for a person' : 'Go') : 'Stop') + '</span></div>';
    html += '<p class="meter-line"><b>' + sum.rules + '</b> checks by rules · <b>0</b> calls to an AI · <b>' + sum.judge_pending + '</b> questions waiting for a judge</p>';
    if (pv && up) var nF = up.claims ? up.claims.length : 0, nC = up.conditions ? up.conditions.length : 0;
    html += '<p class="handoff">Picked up ' + nF + (nF === 1 ? ' fact' : ' facts') + (nC ? ' and ' + nC + (nC === 1 ? ' required fix' : ' required fixes') : '') + ' from step ' + (AVE.VERBS.indexOf(pv) + 1) + '.</p>';
    html += '<div class="lanes"><div class="lane-col"><h4>Decided by rules <span>no AI</span></h4><ul class="gates">' + tr.filter(function (e) { return e.lane === 'rules'; }).map(function (g, i) {
      return '<li class="g lit ' + (g.ok ? 'g-pass' : 'g-fail') + (g.cliOnly ? ' g-cli' : '') + '" style="--i:' + i + '"><span class="dot" aria-hidden="true"></span><span class="gt">' + esc(PLAIN[g.id] || g.id) + '</span><span class="ge">' + esc(g.evidence) + ' · ' + (g.ms < 0.01 ? '<0.01' : g.ms.toFixed(2)) + ' ms</span><span class="sr">' + (g.ok ? 'passed' : 'failed') + '</span></li>';
    }).join('') + '</ul></div>';
    var jud = tr.filter(function (e) { return e.lane === 'judge'; });
    html += '<div class="lane-col"><h4>Waiting for a judge <span>not sent</span></h4>';
    if (jud.length) html += '<details class="shared"><summary>Instructions every question shares (same for all ' + jud.length + ')</summary><pre>' + esc(jud[0].prompt.system) + '</pre></details>';
    html += '<ul class="jcards">' + jud.map(function (j, i) {
      return '<li class="lit" style="--i:' + (i + sum.rules) + '"><span class="jq">' + esc(j.label) + '</span><span class="jmsg">Sent with the shared instructions as: <code>' + esc(j.prompt.user) + '</code></span></li>';
    }).join('') + '</ul><p class="res-note">Scores come from a person, or from Claude with <code>--judge</code> in the command-line tool. They never change the stamp.</p></div></div>';
    var notes = [];
    if (pv && !up) notes.push('Checked on its own. Check step ' + (AVE.VERBS.indexOf(pv) + 1) + ' first and this step will also test what it inherited.');
    if (v === 'synthesis') notes.push('The writing-filler check runs in the command-line tool only.');
    if (rep.gates.some(function (g) { return g.cliOnly; })) notes.push('Hollow dots: the command-line tool also confirms those files exist.');
    html += notes.map(function (n) { return '<p class="res-note">' + n + '</p>'; }).join('');
    var nDone = Object.keys(state.json).length;
    html += '<div class="export"><button type="button" class="btn" data-export="step">Copy this step as JSON</button>' +
      (nDone > 1 ? '<button type="button" class="btn" data-export="run">Copy all ' + nDone + ' checked steps as JSON</button>' : '') +
      '<span class="export-note">Same shape as <code>--out</code> in the command-line tool.</span></div><pre class="export-fallback" hidden></pre>';
    html += '<details class="rawtrace"><summary>Trace (the same JSON lines <code>--trace</code> writes)</summary><pre>' + esc(tr.map(function (e) { var o = Object.assign({}, e); if (o.prompt) o.prompt = '(shown above)'; return JSON.stringify(o); }).join('\n')) + '</pre></details>';
    out.innerHTML = html;
    out.querySelectorAll('[data-export]').forEach(function (b) {
      b.addEventListener('click', function () {
        var data = b.getAttribute('data-export') === 'step' ? state.json[v]
          : { tool: 'arcs-verb-eval', steps: AVE.VERBS.filter(function (k) { return state.json[k]; }).map(function (k) { return state.json[k]; }) };
        var text = JSON.stringify(data, null, 2), label = b.textContent, fb = out.querySelector('.export-fallback');
        var done = function () { b.textContent = 'Copied'; setTimeout(function () { b.textContent = label; }, 1400); };
        var fallback = function () {
          fb.hidden = false; fb.textContent = text;
          var r = document.createRange(); r.selectNodeContents(fb);
          var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(r);
          b.textContent = 'Selected below: press Cmd+C';
        };
        try { navigator.clipboard.writeText(text).then(done, fallback); } catch (e) { fallback(); }
      });
    });
    var card = document.querySelector('.step a[href="#' + v + '"]');
    if (card) {
      var li = card.parentNode, st = card.querySelector('.stamp');
      li.classList.remove('s-go', 's-stop', 's-wait');
      li.classList.add(rep.ok ? (v === 'recapitulation' ? 's-wait' : 's-go') : 's-stop');
      st.textContent = rep.ok ? (v === 'recapitulation' ? 'Ready for a person' : 'Go') : 'Stop';
    }
  };
  select('analysis');
})();
