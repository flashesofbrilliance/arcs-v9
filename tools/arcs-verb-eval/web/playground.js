(function () {
  var LABEL = { analysis: 'Your work (HTML with marked facts)', assessment: 'Your checked facts (HTML with verdicts)', evaluation: 'Your reviews (JSON)', synthesis: 'Your short version (HTML)', recapitulation: 'Your draft note (text)' };
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
    var html = '<div class="res-head"><strong>' + NAMES[v] + '</strong><span class="big ' + (rep.ok ? 'go' : 'stop') + '">' + (rep.ok ? (v === 'recapitulation' ? 'Ready for a person' : 'Go') : 'Stop') + '</span></div>';
    html += '<ul class="gates">' + rep.gates.map(function (g) {
      return '<li class="g ' + (g.ok ? 'g-pass' : 'g-fail') + (g.cliOnly ? ' g-cli' : '') + '"><span class="dot" aria-hidden="true"></span><span class="gt">' + esc(PLAIN[g.id] || g.id) + '</span><span class="ge">' + esc(g.evidence) + '</span><span class="sr">' + (g.ok ? 'passed' : 'failed') + '</span></li>';
    }).join('') + '</ul>';
    var notes = [];
    if (pv && !up) notes.push('Checked on its own. Check step ' + (AVE.VERBS.indexOf(pv) + 1) + ' first and this step will also test what it inherited.');
    if (v === 'synthesis') notes.push('The writing-filler check runs in the command-line tool only.');
    if (rep.gates.some(function (g) { return g.cliOnly; })) notes.push('Hollow dots: the command-line tool also confirms those files exist.');
    html += notes.map(function (n) { return '<p class="res-note">' + n + '</p>'; }).join('');
    out.innerHTML = html;
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
