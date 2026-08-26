// Zapier Code step: "Process State and Name Inputs"
// Paste this whole file into the Zapier Code (JavaScript) step body.
//
// Input Data fields expected (map these in the Zap editor):
//   state      -> raw state text from the Tidio payload
//   full_name  -> raw visitor name from the Tidio payload
//   test_mode  -> (optional) set to "yes", "true", or "1" to run the canned test
//                 suite instead. Any other value (including "no"/"false"/"") is
//                 ignored, so a leftover mapping can never hijack a real lead.
//
// Output contract (DO NOT rename these keys, downstream steps depend on them):
//   state_code          always a valid 2-letter code; falls back to "CA" on parse failure
//   state_parse_failed  "true"/"false" string flag (Zapier filters compare text)
//   state_raw           raw state input, passed through untouched
//   ambiguous           "true"/"false"; true when more than one state was found
//   first_name          first token of full_name ("" if none)
//   last_name           everything after the first token ("" if none)
//   name_raw            raw full_name input, passed through untouched

var FALLBACK_STATE = 'CA';

var STATE_NAMES = {
  'ALABAMA': 'AL', 'ALASKA': 'AK', 'ARIZONA': 'AZ', 'ARKANSAS': 'AR',
  'CALIFORNIA': 'CA', 'COLORADO': 'CO', 'CONNECTICUT': 'CT', 'DELAWARE': 'DE',
  'FLORIDA': 'FL', 'GEORGIA': 'GA', 'HAWAII': 'HI', 'IDAHO': 'ID',
  'ILLINOIS': 'IL', 'INDIANA': 'IN', 'IOWA': 'IA', 'KANSAS': 'KS',
  'KENTUCKY': 'KY', 'LOUISIANA': 'LA', 'MAINE': 'ME', 'MARYLAND': 'MD',
  'MASSACHUSETTS': 'MA', 'MICHIGAN': 'MI', 'MINNESOTA': 'MN', 'MISSISSIPPI': 'MS',
  'MISSOURI': 'MO', 'MONTANA': 'MT', 'NEBRASKA': 'NE', 'NEVADA': 'NV',
  'NEW HAMPSHIRE': 'NH', 'NEW JERSEY': 'NJ', 'NEW MEXICO': 'NM', 'NEW YORK': 'NY',
  'NORTH CAROLINA': 'NC', 'NORTH DAKOTA': 'ND', 'OHIO': 'OH', 'OKLAHOMA': 'OK',
  'OREGON': 'OR', 'PENNSYLVANIA': 'PA', 'RHODE ISLAND': 'RI', 'SOUTH CAROLINA': 'SC',
  'SOUTH DAKOTA': 'SD', 'TENNESSEE': 'TN', 'TEXAS': 'TX', 'UTAH': 'UT',
  'VERMONT': 'VT', 'VIRGINIA': 'VA', 'WASHINGTON': 'WA', 'WEST VIRGINIA': 'WV',
  'WISCONSIN': 'WI', 'WYOMING': 'WY',
  'DISTRICT OF COLUMBIA': 'DC', 'WASHINGTON DC': 'DC', 'WASHINGTON D C': 'DC'
};

var VALID_CODES = {};
(function () {
  var codes = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN',
    'IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ',
    'NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA',
    'WA','WV','WI','WY','DC'];
  for (var i = 0; i < codes.length; i++) { VALID_CODES[codes[i]] = true; }
})();

// Connector words that are ALSO state codes ("or" = OR, "in" = IN, "hi" = HI, "ok" = OK).
// A 2-letter token only counts as a code when it was UPPERCASE in the raw input,
// OR when it is the only thing in the input.
var ENGLISH_WORD_CODES = { 'OR': true, 'IN': true, 'HI': true, 'OK': true, 'ME': true, 'DE': true, 'LA': true, 'PA': true, 'OH': true };

function parseState(rawInput) {
  var raw = (rawInput === undefined || rawInput === null) ? '' : String(rawInput);
  var result = {
    state_code: FALLBACK_STATE,
    state_parse_failed: true,
    ambiguous: false,
    state_raw: raw
  };

  // Normalize: remove periods entirely ("N.Y." -> "NY", "D.C." -> "DC"),
  // then turn remaining punctuation into spaces, trim, collapse whitespace.
  var cleaned = raw.replace(/\./g, '')
    .trim().replace(/[,;:!?()\/\\|&+-]+/g, ' ').replace(/\s+/g, ' ').trim();
  if (cleaned === '') { return result; }

  // Any digits present (zip codes, street addresses): refuse to guess. Parse failed, never silently wrong.
  if (/\d/.test(cleaned)) { return result; }

  var upper = cleaned.toUpperCase();

  // 1) Exact whole-string match: valid 2-letter code
  if (upper.length === 2 && VALID_CODES[upper]) {
    result.state_code = upper;
    result.state_parse_failed = false;
    return result;
  }

  // 2) Exact whole-string match: full state name (covers multi-word names like NEW YORK)
  if (STATE_NAMES[upper]) {
    result.state_code = STATE_NAMES[upper];
    result.state_parse_failed = false;
    return result;
  }

  // 3) Scan for embedded matches (multi-state answers, "state of Texas", etc.)
  //    Collect matches in order of position in the string.
  var matches = []; // { pos, code }

  // 3a) Full state names anywhere in the string (word-bounded)
  var name;
  for (name in STATE_NAMES) {
    if (!Object.prototype.hasOwnProperty.call(STATE_NAMES, name)) { continue; }
    var re = new RegExp('(^|\\s)' + name.replace(/\s+/g, '\\s+') + '(\\s|$)');
    var m = re.exec(upper);
    if (m) {
      matches.push({ pos: m.index, code: STATE_NAMES[name], len: name.length });
    }
  }

  // Longer names win overlapping shorter ones at the same position region
  // (e.g. "WEST VIRGINIA" must not also count as "VIRGINIA").
  matches.sort(function (a, b) { return a.pos - b.pos || b.len - a.len; });
  var filtered = [];
  for (var i = 0; i < matches.length; i++) {
    var overlaps = false;
    for (var j = 0; j < filtered.length; j++) {
      var f = filtered[j];
      if (matches[i].pos < f.pos + f.len && f.pos < matches[i].pos + matches[i].len) {
        overlaps = true;
        break;
      }
    }
    if (!overlaps) { filtered.push(matches[i]); }
  }
  matches = filtered;

  // 3b) Standalone 2-letter code tokens. Only trust a token that doubles as an
  //     English word (OR, IN, HI, OK, ME, DE, LA, PA, OH) when it appeared
  //     UPPERCASE in the raw input.
  var rawTokens = cleaned.split(' ');
  var offset = 0;
  for (var t = 0; t < rawTokens.length; t++) {
    var tok = rawTokens[t];
    var tokUpper = tok.toUpperCase();
    if (tok.length === 2 && VALID_CODES[tokUpper]) {
      var trustworthy = !ENGLISH_WORD_CODES[tokUpper] || tok === tokUpper;
      if (trustworthy) {
        var pos = offset;
        var covered = false;
        for (var k = 0; k < matches.length; k++) {
          if (pos >= matches[k].pos && pos < matches[k].pos + matches[k].len) { covered = true; break; }
        }
        if (!covered) { matches.push({ pos: pos, code: tokUpper, len: 2 }); }
      }
    }
    offset += tok.length + 1;
  }

  if (matches.length === 0) {
    // Non-US ("Toronto", "Ontario") or unrecognizable: parse failed, CA fallback, flagged.
    return result;
  }

  matches.sort(function (a, b) { return a.pos - b.pos; });

  // De-duplicate same code found twice ("NY, New York" is not ambiguous)
  var distinct = [];
  var seen = {};
  for (var d = 0; d < matches.length; d++) {
    if (!seen[matches[d].code]) { seen[matches[d].code] = true; distinct.push(matches[d]); }
  }

  result.state_code = distinct[0].code;
  result.state_parse_failed = false;
  result.ambiguous = distinct.length > 1;
  return result;
}

function parseName(rawInput) {
  var raw = (rawInput === undefined || rawInput === null) ? '' : String(rawInput);
  var cleaned = raw.trim().replace(/\s+/g, ' ');
  if (cleaned === '') {
    return { first_name: '', last_name: '', name_raw: raw };
  }
  var parts = cleaned.split(' ');
  var first = parts.shift();
  return {
    first_name: first,
    last_name: parts.join(' '),
    name_raw: raw
  };
}

function processInputs(input) {
  var state = parseState(input.state);
  var name = parseName(input.full_name);
  return {
    state_code: state.state_code,
    state_parse_failed: state.state_parse_failed ? 'true' : 'false',
    ambiguous: state.ambiguous ? 'true' : 'false',
    state_raw: state.state_raw,
    first_name: name.first_name,
    last_name: name.last_name,
    name_raw: name.name_raw
  };
}

// ---------------------------------------------------------------------------
// test_mode: canned cases run inside Zapier itself (set input test_mode = yes)
// ---------------------------------------------------------------------------

var CANNED_CASES = [
  // [input state, expected code, expected parse_failed, expected ambiguous, label]
  ['CA',                 'CA', false, false, 'plain valid code'],
  ['ca',                 'CA', false, false, 'lowercase code'],
  ['  TX  ',             'TX', false, false, 'whitespace around code'],
  ['N.Y.',               'NY', false, false, 'punctuated code'],
  ['D.C.',               'DC', false, false, 'punctuated DC'],
  ['California',         'CA', false, false, 'full state name'],
  ['california',         'CA', false, false, 'lowercase full name'],
  ['New York',           'NY', false, false, 'two-word full name'],
  ['new  york',          'NY', false, false, 'extra internal whitespace'],
  ['West Virginia',      'WV', false, false, 'name containing another name'],
  ['District of Columbia','DC', false, false, 'DC long form'],
  ['06810',              'CA', true,  false, 'zip code: parse failed, never guessed'],
  ['CT 06810',           'CA', true,  false, 'code plus zip: digits force parse failed'],
  ['California or Texas','CA', false, true,  'multi-state: first match plus ambiguous'],
  ['NY / NJ',            'NY', false, true,  'multi-code: first plus ambiguous'],
  ['Toronto',            'CA', true,  false, 'non-US city: parse failed, not silent CA'],
  ['Ontario',            'CA', true,  false, 'non-US province: parse failed'],
  ['',                   'CA', true,  false, 'empty input: parse failed'],
  ['the state of Texas', 'TX', false, false, 'name embedded in phrase'],
  ['I live in Oregon',   'OR', false, false, 'lowercase "in" not read as Indiana'],
  ['or',                 'OR', false, false, 'bare 2-letter exact match still honored'],
  ['XX',                 'CA', true,  false, 'invalid 2-letter code: parse failed']
];

function runCannedTests() {
  var results = [];
  var passed = 0;
  for (var i = 0; i < CANNED_CASES.length; i++) {
    var c = CANNED_CASES[i];
    var got = parseState(c[0]);
    var ok = got.state_code === c[1] &&
             got.state_parse_failed === c[2] &&
             got.ambiguous === c[3];
    if (ok) { passed++; }
    results.push(
      (ok ? 'PASS' : 'FAIL') + ' | ' + c[4] + ' | input="' + c[0] +
      '" expected=' + c[1] + '/' + (c[2] ? 'failed' : 'ok') + '/' + (c[3] ? 'ambiguous' : 'unambiguous') +
      ' got=' + got.state_code + '/' + (got.state_parse_failed ? 'failed' : 'ok') + '/' + (got.ambiguous ? 'ambiguous' : 'unambiguous')
    );
  }
  return {
    test_mode: 'true',
    tests_total: String(CANNED_CASES.length),
    tests_passed: String(passed),
    tests_failed: String(CANNED_CASES.length - passed),
    all_passed: passed === CANNED_CASES.length ? 'true' : 'false',
    results: results
  };
}

// ---------------------------------------------------------------------------
// Entry point: Zapier provides inputData; plain node (tests) provides nothing.
// ---------------------------------------------------------------------------

function isTestMode(v) {
  // Zapier passes every field as a string; only explicit affirmatives count.
  var s = String(v === undefined || v === null ? '' : v).trim().toLowerCase();
  return s === 'yes' || s === 'true' || s === '1';
}

if (typeof inputData !== 'undefined') {
  if (isTestMode(inputData.test_mode)) {
    output = runCannedTests();
  } else {
    output = processInputs(inputData);
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    parseState: parseState,
    parseName: parseName,
    processInputs: processInputs,
    runCannedTests: runCannedTests,
    isTestMode: isTestMode,
    CANNED_CASES: CANNED_CASES
  };
}
