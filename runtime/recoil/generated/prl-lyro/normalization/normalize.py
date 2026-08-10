#!/usr/bin/env python3
"""PRL deterministic normalizer + recognizer (1.3 recognition backbone).

NOT an LLM. Pure lookup over the dictionaries in this folder. Given free-text lead input, it
surfaces which PRL grade / material family / competitor-equivalent is being referenced. It never
emits a spec, price, or UL status - recognition only; specifics route to a human (anti-fabrication).

Usage:
    from normalize import norm, recognize, normalize_state
    recognize("we need PA66 for fiber extrusion")   -> [{'type':'family','family':'NY66',...}]
    recognize("what's your equivalent to Lexan 141") -> [{'type':'competitor_equiv','prl_grade':'PC-GP2-D',...}]
Run `python3 normalize.py` for the self-test.
"""
import json, re, os
_D = os.path.dirname(os.path.abspath(__file__))
def _load(n): return json.load(open(os.path.join(_D, n)))
GRADES = _load('grade-dictionary.json')['grades']
MAT    = _load('material-synonyms.json')
COMP   = _load('competitor-to-prl.json')['map']
FIELD  = _load('field-normalization.json')

def norm(s):
    """Canonical form: uppercase, strip trademark marks, standardize / and - separators, collapse ws."""
    s = re.sub(r'[™®©]', '', str(s)).upper().strip()
    s = re.sub(r'\s*/\s*', '/', s)
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'\s*-\s*', '-', s)
    return s.strip()

# ---- build fast lookup indexes (exact alias -> record) ----
_GRADE_IDX = {}
for g in GRADES:
    for a in g['aliases']:
        _GRADE_IDX.setdefault(a, g)
_FAM_IDX = {}
for fam, blk in MAT['families'].items():
    for a in blk['aliases']:
        _FAM_IDX.setdefault(a, fam)

_SENT_PUNCT = '?.!,;:"\'`'          # sentence punctuation (NOT brackets)
_EDGE_PUNCT = _SENT_PUNCT + '()[]{}*'  # everything strippable from token edges

def _grams(text, n_max=3):
    raw = norm(text).replace('/', ' / ').split()
    toks = [t.strip(_EDGE_PUNCT) for t in raw]
    toks = [t for t in toks if t]
    out = []
    for n in range(n_max, 0, -1):
        for i in range(len(toks) - n + 1):
            out.append(' '.join(toks[i:i+n]).replace(' / ', '/'))
    # per-token alternates so a grade code with INTERNAL brackets survives trailing sentence punct:
    # 'ABS-FR-UV(F2)?' -> strip only sentence punct -> 'ABS-FR-UV(F2)' (keeps the parens) matches.
    for r in raw:
        for cand in (r, r.strip(_SENT_PUNCT)):
            if cand and cand not in out:
                out.append(cand)
    return out

def recognize(text):
    """Scan free text; return de-duped list of recognized entities (grade / competitor_equiv / family)."""
    hits, seen = [], set()
    grams = _grams(text)
    # 1) exact PRL grade
    for gm in grams:
        g = _GRADE_IDX.get(gm)
        if g and ('grade', g['grade']) not in seen:
            seen.add(('grade', g['grade']))
            hits.append({'type': 'prl_grade', 'grade': g['grade'], 'family': g['family_code'],
                         'family_name': g['family_name'], 'matched': gm})
    # 2) competitor grade -> PRL equivalent (brand-qualified grams win, but bare also matched)
    for gm in grams:
        if gm in COMP:
            for e in COMP[gm]:
                k = ('comp', e['prl_grade'], gm)
                if k not in seen:
                    seen.add(k)
                    hits.append({'type': 'competitor_equiv', 'prl_grade': e['prl_grade'],
                                 'maker': e['maker'], 'brand': e['brand'], 'matched': gm})
    # 3) material family
    for gm in grams:
        fam = _FAM_IDX.get(gm)
        if fam and ('fam', fam) not in seen:
            seen.add(('fam', fam))
            hits.append({'type': 'family', 'family': fam,
                         'family_name': MAT['product_families'].get(fam, fam), 'matched': gm})
    # 4) bare generic material term -> route to family (ONLY if nothing more specific matched, so
    #    "nylon 6" still pins NY6 but bare "nylon" surfaces both and defers 6-vs-66 to a specialist)
    if not hits:
        GENERIC = {'NYLON': ['NY6', 'NY66'], 'POLYAMIDE': ['NY6', 'NY66']}
        gramset = set(grams)
        for term, fams in GENERIC.items():
            if term in gramset:
                for fam in fams:
                    if ('fam', fam) not in seen:
                        seen.add(('fam', fam))
                        hits.append({'type': 'family', 'family': fam,
                                     'family_name': MAT['product_families'].get(fam, fam),
                                     'matched': term, 'generic': True})
                break
    return hits

# ---- state resolution (canonical FULL name for Sugar location_c + territory routing) ----
# Sugar's live records + the territory map both use FULL names, so we resolve TO full name,
# accepting abbreviations, informal abbrevs, and mixed case/punctuation. Regions and placeholders
# are NOT guessed -> they return status so the flow can re-ask instead of writing garbage.
_FULL = {k: k.title() for k in FIELD['state_fullname_to_abbrev']}                    # CONNECTICUT -> Connecticut
_ABBR = {v: k.title() for k, v in FIELD['state_fullname_to_abbrev'].items()}          # CT -> Connecticut
_INFORMAL = {'CONN': 'CT', 'CALIF': 'CA', 'CALI': 'CA', 'MASS': 'MA', 'PENN': 'PA', 'PENNA': 'PA',
             'FLA': 'FL', 'TEX': 'TX', 'ARIZ': 'AZ', 'COLO': 'CO', 'MICH': 'MI', 'MINN': 'MN',
             'WASH': 'WA', 'ORE': 'OR', 'TENN': 'TN', 'WISC': 'WI', 'WIS': 'WI', 'NEB': 'NE',
             'OKLA': 'OK', 'KAN': 'KS', 'MISS': 'MS', 'IND': 'IN', 'DEL': 'DE'}
_REGIONS = {'NORTHEAST', 'NORTH EAST', 'NEW ENGLAND', 'MIDWEST', 'MID WEST', 'SOUTH', 'SOUTHEAST',
            'SOUTH EAST', 'SOUTHWEST', 'SOUTH WEST', 'WEST', 'WEST COAST', 'EAST COAST', 'PNW',
            'PACIFIC NORTHWEST', 'MID ATLANTIC', 'MID-ATLANTIC', 'TRI STATE', 'TRISTATE',
            'TRI-STATE', 'GREAT LAKES', 'SUN BELT', 'ROCKIES', 'NEW ENGLAND AREA', 'CENTRAL',
            'THE SOUTH', 'THE MIDWEST', 'THE NORTHEAST', 'THE NORTH EAST', 'THE WEST', 'THE EAST',
            'THE SOUTHEAST', 'THE SOUTHWEST', 'THE NORTHWEST'}
_PLACEHOLDER = {'', 'N/A', 'NA', 'N A', 'NONE', 'NULL', 'NIL', 'TBD', 'TBA', 'X', 'XX', 'XXX',
                'ASDF', 'TEST', 'USA', 'US', 'UNITED STATES', 'U S', 'U.S.', 'U S A'}

def resolve_state(value):
    """Return {'value': canonical full name or None, 'status': ok|region|placeholder|unknown}."""
    v = norm(value).rstrip('.').strip()
    v = re.sub(r'[?!.,]', '', v).strip()
    if not any(ch.isalnum() for ch in v):  return {'value': None, 'status': 'placeholder'}  # '', '-', '--'
    if v in _PLACEHOLDER:               return {'value': None, 'status': 'placeholder'}
    if v in _REGIONS:                   return {'value': None, 'status': 'region'}
    if v in _FULL:                      return {'value': _FULL[v], 'status': 'ok'}
    if len(v) == 2 and v in _ABBR:      return {'value': _ABBR[v], 'status': 'ok'}
    if v in _INFORMAL:                  return {'value': _ABBR[_INFORMAL[v]], 'status': 'ok'}
    return {'value': None, 'status': 'unknown'}

def normalize_state(value):
    """location_c -> canonical FULL state name (Sugar + routing). Returns the original value when
    unresolved so nothing is silently dropped; callers should branch on resolve_state()['status']
    (region/placeholder/unknown -> re-ask the visitor, never write it as a real state)."""
    r = resolve_state(value)
    return r['value'] if r['value'] else value

if __name__ == '__main__':
    tests = [
        ("PC-GP1-D",                       'prl_grade'),
        ("pc gp1",                         'prl_grade'),
        ("we are looking for PA66 for fiber extrusion application", 'family'),
        ("interested in ABS & ABA resin",  'family'),
        ("what is your equivalent to Lexan 141", 'competitor_equiv'),
        ("Makrolon 3105 replacement",      'competitor_equiv'),
        ("need Ultem 1000",                'competitor_equiv'),
        ("do you have polycarbonate",      'family'),
        ("nylon 6/6 glass filled",         'family'),
        ("random unrelated question",      None),
        # --- regression cases from the 2026-08-09 end-to-end sim (punctuation + bare family) ---
        ("Do you have an equivalent to Lexan 141? Need a quote.", 'competitor_equiv'),  # trailing '?'
        ("Makrolon 3105, please",          'competitor_equiv'),   # trailing ','
        ("(Ultem 1000)",                   'competitor_equiv'),   # wrapping parens
        ("glass-filled nylon",             'family'),             # bare generic family
        ("we need nylon",                  'family'),             # bare generic family
    ]
    ok = 0
    for text, expect in tests:
        r = recognize(text)
        got = {h['type'] for h in r}
        passed = (expect in got) if expect else (len(r) == 0)
        ok += passed
        print(f"[{'PASS' if passed else 'FAIL'}] {text!r}\n        -> {r}")
    # --- state resolution edge cases (canonical FULL name for Sugar + routing) ---
    state_tests = [
        ("CT", "Connecticut", "ok"), ("ct", "Connecticut", "ok"),
        ("Connecticut", "Connecticut", "ok"), ("Texas", "Texas", "ok"), ("TX", "Texas", "ok"),
        ("Conn.", "Connecticut", "ok"), ("Calif", "California", "ok"), ("New Jersey", "New Jersey", "ok"),
        ("North East", None, "region"), ("New England", None, "region"), ("Midwest", None, "region"),
        ("N/A", None, "placeholder"), ("none", None, "placeholder"), ("-", None, "placeholder"),
        ("", None, "placeholder"), ("USA", None, "placeholder"), ("XX", None, "placeholder"),
        ("Ontario", None, "unknown"), ("asdf", None, "placeholder"),
    ]
    sok = 0
    for inp, exp_val, exp_status in state_tests:
        r = resolve_state(inp)
        passed = (r["value"] == exp_val and r["status"] == exp_status)
        sok += passed
        print(f"[{'PASS' if passed else 'FAIL'}] state {inp!r:16} -> {r}")
    ok += sok
    total = len(tests) + len(state_tests)
    print(f"\nself-test: recognizer {ok - sok}/{len(tests)} + state {sok}/{len(state_tests)} = {ok}/{total} passed")
