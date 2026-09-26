#!/usr/bin/env node
/*
 * slop-gate - npm bin wrapper.
 *
 * The four checks are stdlib-only PYTHON (proven, self-tested, zero pip deps).
 * This wrapper does not re-implement them; it shells to python3 and forwards
 * argv, so the npm package is a thin, cross-platform launcher over the same
 * scripts the repo pre-commit runs. python3 (>= 3.8) is a runtime prerequisite
 * (documented in README + package.json engines note).
 *
 * Script resolution mirrors the bash runner: prefer vendored ./lib (populated
 * by build.sh at pack time), else the in-repo ../../scripts SSOT.
 */
'use strict';
const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const here = __dirname; // tools/slop-gate/bin
const vendored = path.join(here, '..', 'lib');
const inRepo = path.join(here, '..', '..', '..', 'scripts');
const LIB = fs.existsSync(path.join(vendored, 'slop_lint.py')) ? vendored
          : fs.existsSync(path.join(inRepo, 'slop_lint.py')) ? inRepo
          : null;
if (!LIB) {
  console.error('slop-gate: cannot locate the linters (looked in ./lib and ../../scripts)');
  process.exit(2);
}
const PY = process.env.PYTHON || 'python3';

const [cmd, ...rest] = process.argv.slice(2);
const S = (f, pre = []) => run(path.join(LIB, f), [...pre, ...rest]);
function run(script, args) {
  const r = spawnSync(PY, [script, ...args], { stdio: 'inherit' });
  if (r.error) { console.error('slop-gate: failed to run python3 (' + r.error.message + ')'); process.exit(2); }
  return r.status || 0;
}

switch (cmd) {
  case 'lint':        process.exit(S('slop_lint.py')); break;
  case 'metrics':     process.exit(S('slop_lint.py', ['--metrics'])); break;
  case 'eval':        process.exit(S('slop_eval.py')); break;
  case 'provenance':  process.exit(S('provenance_lint.py')); break;
  case 'self-test': {
    const a = run(path.join(LIB, 'slop_lint.py'), ['--self-test']);
    const b = run(path.join(LIB, 'provenance_lint.py'), ['--self-test']);
    process.exit(a || b); break;
  }
  default:
    console.log('slop-gate <lint|metrics|eval|provenance|self-test> [args]');
    console.log('  see README.md for the four layers and flags. python3 required.');
    process.exit(cmd ? 2 : 0);
}
