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

def _grams(text, n_max=3):
    toks = norm(text).replace('/', ' / ').split()
    out = []
    for n in range(n_max, 0, -1):
        for i in range(len(toks) - n + 1):
            out.append(' '.join(toks[i:i+n]).replace(' / ', '/'))
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
    return hits

def normalize_state(value):
    """location_c -> canonical 2-letter. (Write format still gated: existing zaps use FULL names.)"""
    v = norm(value)
    if len(v) == 2 and v in FIELD['state_fullname_to_abbrev'].values():
        return v
    return FIELD['state_fullname_to_abbrev'].get(v, value)

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
    ]
    ok = 0
    for text, expect in tests:
        r = recognize(text)
        got = {h['type'] for h in r}
        passed = (expect in got) if expect else (len(r) == 0)
        ok += passed
        print(f"[{'PASS' if passed else 'FAIL'}] {text!r}\n        -> {r}")
    print(f"\nstate: 'New Jersey' -> {normalize_state('New Jersey')} | 'TX' -> {normalize_state('TX')}")
    print(f"self-test: {ok}/{len(tests)} passed")
