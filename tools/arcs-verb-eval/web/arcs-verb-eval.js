/* arcs-verb-eval, browser port of the machine checks. Mirrors arcs_verb_eval.py gate for gate.
   Two checks need the file system or a repo script, so they run in the CLI only:
   slop-lint (synthesis) and ex-ante / pre-send-gauntlet file existence (recapitulation). */
var AVE = (function () {
  var VERBS = ['analysis', 'assessment', 'evaluation', 'synthesis', 'recapitulation'];
  var VERDICTS = ['verified', 'gap', 'unresolved'], SEV = ['low', 'medium', 'high'];
  var DISSENT = /\b(FALSIFIED|falsif|blocked|STOP:|refused|corrected|premise correction|deceipt|retract|red X|does not exist|not evidence|wrong|dissent|fail(ed|s)?)\b/gi;
  var UNCONF = /\b(unconfirmed|not verified|not checked|unverified|unresolved|assum(e|ed|ption))\b/gi;
  var AGREE = /\b(merged|shipped|done|complete|green|verified|confirmed|landed|agree[sd]?|pass(ed|es)?)\b/gi;
  function count(re, t) { return (t.match(re) || []).length; }
  function syco(t, blocking) {
    var a = count(AGREE, t), d = count(DISSENT, t) + count(UNCONF, t), r = a / (d + 1);
    return { agreement: a, dissent: d, ratio: Math.round(r * 100) / 100, verdict: a >= 5 && d === 0 ? 'RETURN' : r > 4 ? 'THIN' : 'OK', blocking: blocking };
  }
  function host(s) { try { return new URL(s).host || s; } catch (e) { return s; } }
  /* parseLite: a small tag scanner used only where DOMParser does not exist (node, for the CI
     parity test). It mirrors arcs_verb_eval.py's _ClaimParser: claim spans by class, nested tags
     counted by depth, data-summary, meta robots, text without script/style. */
  var ENT = { amp: '&', lt: '<', gt: '>', quot: '"', '#39': "'", apos: "'" };
  function unent(s) { return s.replace(/&(amp|lt|gt|quot|#39|apos);/g, function (_, k) { return ENT[k]; }).replace(/&#x([0-9a-f]+);/gi, function (_, h) { return String.fromCharCode(parseInt(h, 16)); }).replace(/&#(\d+);/g, function (_, d) { return String.fromCharCode(+d); }); }
  function attrs(s) { var a = {}, m, re = /([\w-]+)\s*=\s*("([^"]*)"|'([^']*)'|([^\s>]+))/g; while ((m = re.exec(s))) a[m[1].toLowerCase()] = unent(m[3] != null ? m[3] : m[4] != null ? m[4] : m[5]); return a; }
  function parseLite(html) {
    html = html.replace(/<(script|style)\b[\s\S]*?<\/\1>/gi, ' ');
    var claims = [], stack = [], summary = null, noindex = false, text = [], re = /<(\/?)([a-zA-Z0-9]+)([^>]*)>|([^<]+)/g, m;
    while ((m = re.exec(html))) {
      if (m[4] != null) { var t = unent(m[4]); text.push(t); stack.forEach(function (s) { s.text.push(t); }); continue; }
      var close = m[1] === '/', tag = m[2].toLowerCase(), a = close ? {} : attrs(m[3]);
      if (!close) {
        if (a['data-summary'] != null && summary === null) summary = a['data-summary'];
        if (tag === 'meta' && a.name === 'robots' && /noindex/.test(a.content || '')) noindex = true;
        var voidTag = /^(meta|br|img|input|link|hr)$/.test(tag) || /\/\s*$/.test(m[3]);
        if ((' ' + (a['class'] || '') + ' ').indexOf(' claim ') >= 0) stack.push({ a: a, text: [], depth: 0 });
        else if (stack.length && !voidTag) stack[stack.length - 1].depth++;
      } else if (stack.length) {
        var top = stack[stack.length - 1];
        if (top.depth) top.depth--; else { stack.pop(); var c = top.a, i = claims.length;
          claims.push({ id: c['data-id'] || 'auto' + (i + 1), text: top.text.join('').replace(/\s+/g, ' ').trim(),
            src: (c['data-src'] || '').split(',').map(function (s) { return s.trim(); }).filter(Boolean), stakes: c['data-stakes'] || 'normal',
            verdict: c['data-verdict'] == null ? null : c['data-verdict'], severity: c['data-severity'] == null ? null : c['data-severity'],
            render: c['data-render'] == null ? null : c['data-render'], evidence: c['data-evidence'] == null ? null : c['data-evidence'] }); }
      }
    }
    return { claims: claims, summary: summary, noindex: noindex, text: text.join('') };
  }
  function parse(html) {
    if (typeof DOMParser === 'undefined') return parseLite(html);
    var doc = new DOMParser().parseFromString(html, 'text/html');
    var claims = [].map.call(doc.querySelectorAll('.claim'), function (el, i) {
      return { id: el.getAttribute('data-id') || 'auto' + (i + 1), text: el.textContent.replace(/\s+/g, ' ').trim(),
        src: (el.getAttribute('data-src') || '').split(',').map(function (s) { return s.trim(); }).filter(Boolean),
        stakes: el.getAttribute('data-stakes') || 'normal', verdict: el.getAttribute('data-verdict'),
        severity: el.getAttribute('data-severity'), render: el.getAttribute('data-render'), evidence: el.getAttribute('data-evidence') };
    });
    var sum = doc.querySelector('[data-summary]');
    var robots = [].some.call(doc.querySelectorAll('meta[name=robots]'), function (m) { return /noindex/.test(m.getAttribute('content') || ''); });
    [].forEach.call(doc.querySelectorAll('script,style'), function (n) { n.remove(); });
    return { claims: claims, summary: sum ? sum.getAttribute('data-summary') : null, noindex: robots, text: doc.documentElement.textContent };
  }
  function now() { return (typeof performance !== 'undefined' ? performance.now() : Date.now()); }
  function Run() { this.gates = []; this._t = now(); }
  Run.prototype.gate = function (id, ok, ev, cliOnly) { var t = now(); this.gates.push({ id: id, ok: !!ok, evidence: ev, cliOnly: !!cliOnly, ms: Math.round((t - this._t) * 1000) / 1000 }); this._t = t; };
  Run.prototype.ok = function () { return this.gates.every(function (g) { return g.ok; }); };
  Run.prototype.failed = function () { return this.gates.filter(function (g) { return !g.ok; }).map(function (g) { return g.id; }); };
  function ids(a) { return a.join(', '); }

  var V = {};
  V.analysis = function (t) {
    var r = new Run(), p = parse(t), cl = p.claims;
    r.gate('has-claims', cl.length > 0, cl.length + ' claim spans');
    var un = cl.filter(function (c) { return !c.src.length; }).map(function (c) { return c.id; });
    r.gate('every-claim-sourced', !un.length, (cl.length - un.length) + '/' + cl.length + ' sourced' + (un.length ? '; unsourced: ' + ids(un) : ''));
    var thin = cl.filter(function (c) { return c.stakes === 'high' && new Set(c.src.map(host)).size < 2; }).map(function (c) { return c.id; });
    r.gate('high-stakes-two-sources', !thin.length, cl.filter(function (c) { return c.stakes === 'high'; }).length + ' high-stakes' + (thin.length ? '; under 2 hosts: ' + ids(thin) : ''));
    return [r, { fate: r.ok() ? 'sourced' : 'unsourced', claims: cl }, p.text];
  };
  V.assessment = function (t, up) {
    var r = new Run(), p = parse(t), cl = p.claims;
    r.gate('has-claims', cl.length > 0, cl.length + ' claim spans');
    var bad = cl.filter(function (c) { return VERDICTS.indexOf(c.verdict) < 0 || SEV.indexOf(c.severity) < 0; }).map(function (c) { return c.id; });
    r.gate('verdict-and-severity', !bad.length, (cl.length - bad.length) + '/' + cl.length + ' rows complete' + (bad.length ? '; incomplete: ' + ids(bad) : ''));
    if (up) {
      var src = new Set(up.claims.filter(function (c) { return c.src && c.src.length; }).map(function (c) { return c.id; }));
      var ver = cl.filter(function (c) { return c.verdict === 'verified'; });
      var rogue = ver.filter(function (c) { return !src.has(c.id); }).map(function (c) { return c.id; });
      r.gate('verified-was-sourced', !rogue.length, (ver.length - rogue.length) + ' verified resolve upstream' + (rogue.length ? '; not sourced upstream: ' + ids(rogue) : ''));
    }
    var ev = cl.filter(function (c) { return c.verdict === 'verified' && c.evidence; });
    if (ev.length) {
      var num = /(?<![\w.])\d+(?:\.\d+)?/g;
      var drift = ev.filter(function (c) { var a = new Set(c.text.match(num) || []); return !(c.evidence.match(num) || []).some(function (n) { return a.has(n); }); }).map(function (c) { return c.id; });
      r.gate('verified-numbers-in-evidence', !drift.length, (ev.length - drift.length) + '/' + ev.length + ' verified claims share a number with their evidence' + (drift.length ? '; drifted: ' + ids(drift) : ''));
    }
    var counts = VERDICTS.map(function (v) { return cl.filter(function (c) { return c.verdict === v; }).length; }).join('/');
    r.gate('summary-matches-rows', p.summary === counts, 'header ' + (p.summary || 'missing') + ' vs rows ' + counts);
    return [r, { fate: r.ok() ? 'pass' : 'fail', claims: cl }, p.text];
  };
  V.evaluation = function (t, up, o) {
    var r = new Run(), g = JSON.parse(t), L = g.lenses || [], min = (o && o.min_lenses) || 4;
    r.gate('min-lenses', L.length >= min, L.length + ' lenses (min ' + min + '): ' + L.map(function (l) { return l.name || '?'; }).join(', '));
    var inc = L.filter(function (l) { return ['pass', 'fail', 'dissent'].indexOf(l.result) < 0 || !(l.reason || '').trim(); }).map(function (l) { return l.name || '?'; });
    r.gate('lens-result-and-reason', !inc.length, (L.length - inc.length) + '/' + L.length + ' complete' + (inc.length ? '; incomplete: ' + ids(inc) : ''));
    var dis = L.filter(function (l) { return l.result === 'fail' || l.result === 'dissent'; }).map(function (l) { return l.name || '?'; });
    r.gate('dissent-floor', dis.length > 0, dis.length ? dis.length + ' dissent: ' + ids(dis) : 'no lens dissented; a gauntlet nothing could fail is not a gauntlet');
    var v = g.verdict, C = g.conditions || [], fails = L.filter(function (l) { return l.result === 'fail'; }).length;
    var cons = v === 'fail' || (v === 'conditional pass' && C.length > 0) || (v === 'pass' && !fails && !C.length);
    r.gate('verdict-follows', ['pass', 'conditional pass', 'fail'].indexOf(v) >= 0 && cons, 'verdict "' + v + '" · ' + fails + ' fail lenses · ' + C.length + ' conditions');
    if (up) {
      var known = new Set(up.claims.map(function (c) { return c.id; }));
      var dang = C.filter(function (c) { return c.claim && !known.has(c.claim); }).map(function (c) { return c.id || '?'; });
      r.gate('conditions-cite-claims', !dang.length, C.length + ' conditions' + (dang.length ? '; dangling: ' + ids(dang) : ''));
    }
    var s = syco(L.map(function (l) { return (l.result || '') + ' ' + (l.reason || ''); }).join(' '), true);
    r.gate('sycophancy', s.verdict !== 'RETURN', s.verdict + ' · agreement ' + s.agreement + ' · dissent ' + s.dissent);
    return [r, { fate: r.ok() ? v : 'fail', conditions: C, claims: up ? up.claims : [], syco: s }, ''];
  };
  V.synthesis = function (t, up, o) {
    var r = new Run(), p = parse(t), cl = p.claims;
    if (up) {
      var U = {}; up.claims.forEach(function (c) { U[c.id] = c; });
      var nw = cl.filter(function (c) { return !U[c.id]; }).map(function (c) { return c.id; });
      r.gate('no-new-claims', !nw.length, (cl.length - nw.length) + '/' + cl.length + ' resolve upstream' + (nw.length ? '; new: ' + ids(nw) : ''));
      var P = {}; cl.forEach(function (c) { P[c.id] = c; });
      var open = (up.conditions || []).filter(function (k) { var c = P[k.claim]; return c && (k.action === 'drop' || (k.action === 'degrade' && (!c.render || c.render === 'sharp'))); })
        .map(function (k) { return (k.id || '?') + ' (' + k.action + ' ' + k.claim + ')'; });
      r.gate('conditions-honored', !open.length, open.length ? 'open: ' + ids(open) : 'all closed');
      var sharp = cl.filter(function (c) { return U[c.id] && (U[c.id].verdict === 'gap' || U[c.id].verdict === 'unresolved') && (!c.render || c.render === 'sharp'); }).map(function (c) { return c.id; });
      r.gate('render-matches-verdict', !sharp.length, sharp.length ? 'gap/unresolved rendered sharp: ' + ids(sharp) : 'earned fidelity holds');
    }
    var dashes = p.text.split(String.fromCharCode(8212)).length - 1;
    r.gate('em-dash-zero', dashes === 0, dashes + ' em-dashes in visible text');
    if (!(o && o.public)) r.gate('noindex', p.noindex, p.noindex ? 'robots noindex present' : 'missing <meta name=robots content=noindex>');
    return [r, { fate: r.ok() ? 'ship' : 'hold', claims: cl.filter(function (c) { return !up || up.claims.some(function (u) { return u.id === c.id; }); }) }, p.text];
  };
  V.recapitulation = function (t, up) {
    var r = new Run(), fm = {};
    t.replace(/^(status|ex_ante|gauntlet)\s*:\s*(.+?)\s*$/gim, function (_, k, v) { fm[k.toLowerCase()] = v; });
    r.gate('draft-marker', (fm.status || '').toUpperCase() === 'DRAFT', 'status: ' + (fm.status || 'missing'));
    r.gate('ex-ante-receipt', !!fm.ex_ante, fm.ex_ante ? fm.ex_ante + ' named (the CLI also checks the file exists)' : 'ex_ante: missing', true);
    r.gate('pre-send-gauntlet', !!fm.gauntlet, fm.gauntlet ? fm.gauntlet + ' named (the CLI also checks the file exists)' : 'gauntlet: missing', true);
    var cites = (t.match(/\[claim:([\w.-]+)\]/g) || []).map(function (m) { return m.slice(7, -1); });
    if (up) {
      var known = new Set(up.claims.map(function (c) { return c.id; }));
      var rogue = cites.filter(function (c) { return !known.has(c); });
      r.gate('note-claims-resolve', !rogue.length, (cites.length - rogue.length) + '/' + cites.length + ' resolve to synthesis' + (rogue.length ? '; unknown: ' + ids(rogue) : ''));
    }
    var s = syco(t, true);
    r.gate('sycophancy', s.verdict !== 'RETURN', s.verdict + ' · agreement ' + s.agreement + ' · dissent ' + s.dissent);
    return [r, { fate: r.ok() ? 'parked' : 'blocked', claims: [], syco: s }, t];
  };
  function evaluate(verb, text, up, opts) {
    var out = V[verb](text, up, opts || {}), r = out[0], c = out[1];
    var s = c.syco || syco(out[2], false);
    return { verb: verb, fate: c.fate, ok: r.ok(), failed: r.failed(), gates: r.gates, sycophancy: s, claims: c.claims, conditions: c.conditions };
  }
  /* notebook ingest, mirrors arcs_verb_eval_io.claims_from_ipynb */
  function fromNotebook(json, name) {
    var nb = JSON.parse(json), cells = nb.cells || [];
    var j = function (v) { return Array.isArray(v) ? v.join('') : String(v || ''); };
    var nums = function (t) { var s = new Set(); (t.match(/(?<![\w.])(\d+(?:\.\d+)?)%?/g) || []).forEach(function (m) { m = m.replace('%', ''); s.add(m.indexOf('.') >= 0 ? m.replace(/0+$/, '').replace(/\.$/, '') : m); }); return s; };
    var code = [];
    cells.forEach(function (c, i) { if (c.cell_type === 'code') { var o = (c.outputs || []).map(function (x) { return j(x.text) + (x.data ? j(x.data['text/plain']) : ''); }).join('\n'); code.push([i, o]); } });
    var has = code.some(function (c) { return c[1].trim(); }), claims = [];
    cells.forEach(function (c, i) {
      if (c.cell_type !== 'markdown') return;
      j(c.source).split(/(?<=[.!?])\s+/).forEach(function (s) {
        s = s.replace(/#/g, ' ').replace(/\s+/g, ' ').trim();
        var n = nums(s); if (!n.size || s.length < 12) return;
        var m = code.find(function (cc) { var o = nums(cc[1]); return [].some.call(Array.from(n), function (x) { return o.has(x); }); });
        var verdict = m ? 'verified' : has ? 'gap' : 'unresolved';
        claims.push({ id: 'c' + (claims.length + 1), text: s, src: [name + '#cell-' + (m ? m[0] : i)], verdict: verdict, severity: verdict === 'verified' ? 'low' : 'medium', evidence: m ? m[1].slice(0, 200) : '' });
      });
    });
    var esc = function (s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;'); };
    var span = function (c, a) { return '  <li><span class="claim" data-id="' + c.id + '" data-src="' + esc(c.src.join(',')) + '"' + (a ? ' data-verdict="' + c.verdict + '" data-severity="' + c.severity + '"' + (c.evidence ? ' data-evidence="' + esc(c.evidence.replace(/\s+/g, ' ').trim()) + '"' : '') : '') + '>' + esc(c.text) + '</span></li>'; };
    var counts = VERDICTS.map(function (v) { return claims.filter(function (c) { return c.verdict === v; }).length; }).join('/');
    return { claims: claims, analysis: '<ul>\n' + claims.map(function (c) { return span(c, false); }).join('\n') + '\n</ul>', assessment: '<ul data-summary="' + counts + '">\n' + claims.map(function (c) { return span(c, true); }).join('\n') + '\n</ul>' };
  }
  /* the judge lane: same prompt text as arcs_verb_eval_judge.py; the page never sends it */
  var TOOLS = { analysis: 'Analysis by ARCS', assessment: 'Assessment by ARCS', evaluation: 'Evaluation by ARCS', synthesis: 'Synthesis by ARCS', recapitulation: 'Recapitulation by ARCS' };
  function judgePrompt(rep, text, row) {
    var ev = rep.gates.map(function (g) { return '- ' + g.id + ': ' + (g.ok ? 'pass' : 'fail') + ' (' + g.evidence + ')'; }).join('\n');
    var system = 'You score one rubric row at a time for ' + TOOLS[rep.verb] + ', one step of a five-step check that runs before anything is said to someone.\n' +
      'Score 0 (no), 1 (partly) or 2 (yes). Judge only the artifact below. Machine checks already decided go or stop; your score informs a person and changes nothing else.\n' +
      'Be strict: a 2 means a skeptical reader would agree without argument.\n\nMachine-check results:\n' + ev + '\n\n<artifact>\n' + text + '\n</artifact>';
    return { system: system, user: 'Rubric question: ' + row.label };
  }
  function trace(rep, text, rubric) {
    var ev = rep.gates.map(function (g) { return { lane: 'rules', verb: rep.verb, id: g.id, ok: g.ok, ms: g.ms, evidence: g.evidence, cliOnly: g.cliOnly }; });
    (rubric || []).forEach(function (r) { ev.push({ lane: 'judge', verb: rep.verb, id: r.row, label: r.label, sent: false, score: null, prompt: judgePrompt(rep, text, r) }); });
    ev.push({ lane: 'summary', verb: rep.verb, rules: rep.gates.length, llm_calls: 0, judge_pending: (rubric || []).length, fate: rep.fate, decided_by: 'rules' });
    return ev;
  }
  return { VERBS: VERBS, evaluate: evaluate, fromNotebook: fromNotebook, trace: trace, _parseLite: parseLite };
})();
