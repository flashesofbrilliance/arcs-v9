/* eslint-disable @typescript-eslint/no-require-imports -- standalone Node script, not app code */
// Runs parity cases through web/arcs-verb-eval.js in node (no DOMParser, so the engine's parseLite
// path is used). stdin: JSON [{verb, text, up}], where up names an earlier case index or null.
// stdout: JSON [[failed gate ids], ...]. Driven by test_arcs_verb_eval.py.
const vm = require('vm'), fs = require('fs'), path = require('path');
const ctx = { performance, URL, Set, console };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(__dirname, '..', 'web', 'arcs-verb-eval.js'), 'utf8') + ';this.AVE=AVE;', ctx);
const cases = JSON.parse(fs.readFileSync(0, 'utf8'));
const reps = [];
const out = cases.map((c) => {
  const r = ctx.AVE.evaluate(c.verb, c.text, c.up == null ? null : reps[c.up]);
  reps.push(r);
  return r.failed;
});
process.stdout.write(JSON.stringify(out));
