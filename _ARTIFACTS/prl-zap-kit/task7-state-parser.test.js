// Plain-node test runner for task7-state-parser.js. No dependencies.
// Run: node task7-state-parser.test.js
// Exits nonzero on any failure.

var parser = require('./task7-state-parser.js');
var parseState = parser.parseState;
var parseName = parser.parseName;
var processInputs = parser.processInputs;
var runCannedTests = parser.runCannedTests;

var failures = 0;
var total = 0;

function check(label, actual, expected) {
  total++;
  var a = JSON.stringify(actual);
  var e = JSON.stringify(expected);
  if (a === e) {
    console.log('PASS  ' + label);
  } else {
    failures++;
    console.log('FAIL  ' + label);
    console.log('      expected: ' + e);
    console.log('      actual:   ' + a);
  }
}

function checkState(label, input, code, failed, ambiguous) {
  var got = parseState(input);
  check(label + ' [state="' + input + '"]',
    { code: got.state_code, failed: got.state_parse_failed, ambiguous: got.ambiguous, raw: got.state_raw },
    { code: code, failed: failed, ambiguous: ambiguous, raw: input === null || input === undefined ? '' : String(input) });
}

// --- Clean codes ---
checkState('plain code', 'CA', 'CA', false, false);
checkState('lowercase code', 'ny', 'NY', false, false);
checkState('whitespace around code', '  TX  ', 'TX', false, false);

// --- Punctuation ---
checkState('punctuated N.Y.', 'N.Y.', 'NY', false, false);
checkState('punctuated D.C.', 'D.C.', 'DC', false, false);
checkState('trailing comma', 'CT,', 'CT', false, false);

// --- Full state names (historical data mixes them with codes) ---
checkState('full name', 'California', 'CA', false, false);
checkState('lowercase full name', 'california', 'CA', false, false);
checkState('uppercase full name', 'CONNECTICUT', 'CT', false, false);
checkState('two-word name', 'New York', 'NY', false, false);
checkState('two-word name extra spaces', 'new   york', 'NY', false, false);
checkState('West Virginia not Virginia', 'West Virginia', 'WV', false, false);
checkState('North Carolina', 'North Carolina', 'NC', false, false);
checkState('District of Columbia', 'District of Columbia', 'DC', false, false);
checkState('name embedded in phrase', 'the state of Texas', 'TX', false, false);

// --- Zip codes and digits: extract nothing, fail loudly ---
checkState('bare zip', '06810', 'CA', true, false);
checkState('zip+4', '90210-1234', 'CA', true, false);
checkState('code plus zip still fails', 'CT 06810', 'CA', true, false);

// --- Multi-state: first match wins, ambiguous flag set ---
checkState('multi full names', 'California or Texas', 'CA', false, true);
checkState('multi codes with slash', 'NY / NJ', 'NY', false, true);
checkState('name plus code', 'Texas TX', 'TX', false, false); // same state twice = not ambiguous
checkState('reversed order', 'Texas or California', 'TX', false, true);

// --- Connector-word codes: lowercase "or"/"in" are English, uppercase are codes ---
checkState('lowercase or is not Oregon', 'I live in Oregon', 'OR', false, false);
checkState('bare lowercase or exact-matches Oregon', 'or', 'OR', false, false);
checkState('uppercase OR token counts', 'OR', 'OR', false, false);

// --- Non-US: parse failed, never a silent CA ---
checkState('Toronto', 'Toronto', 'CA', true, false);
checkState('Ontario', 'Ontario', 'CA', true, false);
checkState('UK', 'United Kingdom', 'CA', true, false);

// --- Garbage and empties ---
checkState('empty string', '', 'CA', true, false);
checkState('whitespace only', '   ', 'CA', true, false);
checkState('invalid 2-letter', 'XX', 'CA', true, false);

// null/undefined raw passthrough is '' by contract
(function () {
  var got = parseState(null);
  check('null input', { code: got.state_code, failed: got.state_parse_failed, raw: got.state_raw },
    { code: 'CA', failed: true, raw: '' });
})();

// --- Name splitting ---
check('two-part name', parseName('John Smith'), { first_name: 'John', last_name: 'Smith', name_raw: 'John Smith' });
check('three-part name', parseName('Mary Jane Watson'), { first_name: 'Mary', last_name: 'Jane Watson', name_raw: 'Mary Jane Watson' });
check('single name', parseName('Cher'), { first_name: 'Cher', last_name: '', name_raw: 'Cher' });
check('empty name', parseName(''), { first_name: '', last_name: '', name_raw: '' });
check('padded name', parseName('  Ada   Lovelace '), { first_name: 'Ada', last_name: 'Lovelace', name_raw: '  Ada   Lovelace ' });

// --- Full processInputs contract (Zapier output shape, string flags) ---
(function () {
  var out = processInputs({ state: 'N.Y.', full_name: 'Roger Lamarre' });
  check('processInputs contract keys', out, {
    state_code: 'NY',
    state_parse_failed: 'false',
    ambiguous: 'false',
    state_raw: 'N.Y.',
    first_name: 'Roger',
    last_name: 'Lamarre',
    name_raw: 'Roger Lamarre'
  });
})();

// --- Hostile inputs added in adversarial verify (2026-08-26) ---
checkState('emoji around name', '🌴 California 🌴', 'CA', false, false);
checkState('emoji only', '😀😀', 'CA', true, false);
checkState('USA is not a state', 'USA', 'CA', true, false);
checkState('city implies state', 'new york city', 'NY', false, false);
checkState('numeric 06 refused', '06', 'CA', true, false);
checkState('Mexico is not New Mexico', 'Mexico', 'CA', true, false);
checkState('New Mexico still works', 'New Mexico', 'NM', false, false);
checkState('en-dash plus zip fails loud', 'CT–06810', 'CA', true, false);
checkState('VA and WV both found', 'Virginia and West Virginia', 'VA', false, true);

// --- test_mode guard: only explicit affirmatives run the canned suite ---
(function () {
  var isTestMode = parser.isTestMode;
  check('test_mode "yes"', isTestMode('yes'), true);
  check('test_mode "TRUE"', isTestMode('TRUE'), true);
  check('test_mode "1"', isTestMode('1'), true);
  check('test_mode "no" ignored', isTestMode('no'), false);
  check('test_mode "false" ignored', isTestMode('false'), false);
  check('test_mode empty ignored', isTestMode(''), false);
  check('test_mode undefined ignored', isTestMode(undefined), false);
})();

// --- Canned in-Zap test suite must itself pass ---
(function () {
  var canned = runCannedTests();
  check('canned suite all pass', { all_passed: canned.all_passed, failed: canned.tests_failed },
    { all_passed: 'true', failed: '0' });
  if (canned.all_passed !== 'true') {
    canned.results.forEach(function (r) { if (r.indexOf('FAIL') === 0) { console.log('      ' + r); } });
  }
})();

console.log('');
console.log(total - failures + '/' + total + ' assertions passed');
if (failures > 0) {
  console.log(failures + ' FAILURES');
  process.exit(1);
}
process.exit(0);
