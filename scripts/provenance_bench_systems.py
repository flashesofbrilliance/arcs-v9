#!/usr/bin/env python3
"""provenance_bench_systems: the systems under test for the provenance-retrieval benchmark.

Registered in _PATTERNS/2026-10-18-provenance-retrieval-prereg.md. This library implements B0, B1, S and S+Bloom, the
hash tamper check (H6) and the speaker check (H9). It reads no frozen dataset and writes no results; the run harness
(provenance_bench_run.py) does that. Everything here takes the corpus as a dict {file: text}, so it is testable on a
synthetic mini-corpus without touching the frozen data.

Implementation choices the registration left open, fixed here before any run (also logged as note 3 in the registration):
  * Token = lowercase run of [a-z0-9']; sentence = text split after . ! ? plus whitespace, whitespace collapsed, kept when it
    has 8 or more tokens. Same functions as the dataset generator (imported, not copied).
  * Verdict for B0, B1, S, S+Bloom is CLEAN or UNSOURCED. ANCHORED is not used: the registered rule is a single ratio line.
  * B0 builds one difflib.SequenceMatcher per (query, sentence) pair and takes ratio(), as the lint does. No quick_ratio
    shortcut: the baseline is the current approach, not an optimised one.
  * B1 is exact substring search on whitespace-normalized text (case and punctuation kept), first file in sorted order.
  * S: 5-token shingle posting lists. A query's candidate sentences are ranked by shared-shingle count, ties broken by
    sentence id; the top 3 are verified with the same ratio rule as B0 (best ratio at least 0.80 after verification). A query
    with fewer than 5 tokens has no shingles and is UNSOURCED. No cap on posting-list length.
  * S+Bloom: one Bloom filter per file over its 5-shingles, sized for a 1 percent false-positive rate (m = -n ln p / ln2^2,
    k = round(m/n ln2)), hashed with sha256 double hashing (deterministic, no Python hash()). Keep rule: a file stays if at
    least ONE of the query's 5-shingles is (probably) in its filter; S then runs on sentences of kept files only.
  * Speaker check (H9): S finds candidate turns by shared 5-shingles on each side, then scores them with the lint's own
    scoring functions and the lint's own verdict rule; a quote under 5 tokens falls back to scanning every turn.
Stdlib only.
"""
import difflib, hashlib, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import provenance_bench_dataset as ds  # sentences(), toks(): same functions the datasets were drawn with
import attribution_provenance_lint as apl

K = 5
VERBATIM_T = 0.80
TOP_VERIFY = 3
toks = ds.toks


def shingles(t, k=K):
    return [" ".join(t[i:i + k]) for i in range(len(t) - k + 1)]


def ratio(q, s):
    return difflib.SequenceMatcher(None, q, s).ratio()


def norm_ws(s):
    return re.sub(r"\s+", " ", s)


class Corpus:
    """Sentences of the indexed files in sorted (file, position) order. sid is the position in this list."""
    def __init__(self, texts):
        self.files = sorted(texts)
        self.texts = texts
        self.sent, self.sent_file, self.sent_tok = [], [], []
        for fi, f in enumerate(self.files):
            for s in ds.sentences(texts[f]):
                self.sent.append(s); self.sent_file.append(fi); self.sent_tok.append(toks(s))


class B0:
    name = "B0"
    def __init__(self, corpus):
        self.c = corpus
    def query(self, q):
        qt = toks(q); best, bi = 0.0, None
        for sid, st in enumerate(self.c.sent_tok):
            r = ratio(qt, st)
            if r > best:
                best, bi = r, sid
        if bi is not None and best >= VERBATIM_T:
            return {"verdict": "CLEAN", "source_file": self.c.files[self.c.sent_file[bi]]}
        return {"verdict": "UNSOURCED", "source_file": None}


class B1:
    name = "B1"
    def __init__(self, corpus):
        self.c = corpus; self.norm = {f: norm_ws(corpus.texts[f]) for f in corpus.files}
    def query(self, q):
        qn = norm_ws(q).strip()
        for f in self.c.files:
            if qn and qn in self.norm[f]:
                return {"verdict": "CLEAN", "source_file": f}
        return {"verdict": "UNSOURCED", "source_file": None}


class Bloom:
    def __init__(self, n, p=0.01):
        n = max(1, n)
        self.m = max(64, int(math.ceil(-n * math.log(p) / (math.log(2) ** 2)))); self.k = max(1, round(self.m / n * math.log(2)))
        self.bits = bytearray((self.m + 7) // 8)
    def _idx(self, item):
        d = hashlib.sha256(item.encode("utf-8")).digest()
        h1, h2 = int.from_bytes(d[:8], "big"), int.from_bytes(d[8:16], "big") | 1
        return [(h1 + i * h2) % self.m for i in range(self.k)]
    def add(self, item):
        for i in self._idx(item):
            self.bits[i >> 3] |= 1 << (i & 7)
    def __contains__(self, item):
        return all(self.bits[i >> 3] & (1 << (i & 7)) for i in self._idx(item))


class S:
    name = "S"
    def __init__(self, corpus, bloom=False):
        self.c = corpus; self.post = {}; self.bloom = {} if bloom else None
        per_file = {}
        for sid, t in enumerate(corpus.sent_tok):
            for sh in set(shingles(t)):
                self.post.setdefault(sh, []).append(sid)
            if bloom:
                per_file.setdefault(corpus.sent_file[sid], set()).update(shingles(t))
        if bloom:
            for fi, shs in per_file.items():
                b = Bloom(len(shs))
                for sh in sorted(shs):
                    b.add(sh)
                self.bloom[fi] = b
    def candidates(self, qsh):
        keep = None
        if self.bloom is not None:
            keep = {fi for fi, b in self.bloom.items() if any(sh in b for sh in qsh)}
        cnt = {}
        for sh in qsh:
            for sid in self.post.get(sh, ()):
                if keep is None or self.c.sent_file[sid] in keep:
                    cnt[sid] = cnt.get(sid, 0) + 1
        return keep, cnt
    def query(self, q):
        qt = toks(q); qsh = sorted(set(shingles(qt)))
        keep, cnt = self.candidates(qsh)
        out = {"verdict": "UNSOURCED", "source_file": None}
        if self.bloom is not None:
            out["candidate_files"] = len(keep) if keep is not None else len(self.c.files); out["kept_files"] = sorted(self.c.files[i] for i in (keep or ()))
        if not qsh or not cnt:
            return out
        top = sorted(cnt, key=lambda s: (-cnt[s], s))[:TOP_VERIFY]
        best, bi = 0.0, None
        for sid in top:
            r = ratio(qt, self.c.sent_tok[sid])
            if r > best:
                best, bi = r, sid
        if bi is not None and best >= VERBATIM_T:
            out.update({"verdict": "CLEAN", "source_file": self.c.files[self.c.sent_file[bi]]})
        return out


def S_Bloom(corpus):
    s = S(corpus, bloom=True); s.name = "S_Bloom"; return s


SYSTEMS = {"B0": B0, "B1": B1, "S": S, "S_Bloom": S_Bloom}


# ---- H6: hash verification (tamper) --------------------------------------------------------------------------------
def blob_hash(b):
    return hashlib.sha256(b).hexdigest()


def tamper_flagged(expected_sha, current_bytes):
    """Flagged when the current bytes no longer hash to the recorded value."""
    return blob_hash(current_bytes) != expected_sha


def mutate(blob, offset, xor=1):
    b = bytearray(blob); b[offset] ^= xor; return bytes(b)


def mutate_ws(blob, offset, to_byte=9):
    b = bytearray(blob); b[offset] = to_byte; return bytes(b)


# ---- H9: speaker attribution -----------------------------------------------------------------------------------------
def lint_verdict(quote, them_turns, me_turns):
    return apl.judge(quote, them_turns, me_turns)["verdict"]


class SpeakerIndex:
    """Shingle index over turns of one side, for S's candidate generation."""
    def __init__(self, turns):
        self.turns = turns; self.post = {}
        for i, t in enumerate(turns):
            for sh in set(shingles(apl._tokens(t))):
                self.post.setdefault(sh, set()).add(i)
    def candidates(self, quote):
        qt = apl._tokens(quote)
        if len(qt) < K:
            return list(range(len(self.turns)))      # fewer than 5 tokens: no shingles, scan every turn
        out = set()
        for sh in set(shingles(qt)):
            out |= self.post.get(sh, set())
        return sorted(out)


def s_verdict(quote, them_idx, me_idx):
    """The lint's rule, but scores only the candidate turns S's index proposes."""
    def side(ix):
        cand = ix.candidates(quote); sub = [ix.turns[i] for i in cand]
        return apl.best_side_score(quote, sub) if sub else (0.0, 0.0, -1)
    tr, tc, _ = side(them_idx); mr, mc, _ = side(me_idx)
    them_hit = tr >= apl.VERBATIM_T or tc >= apl.COVERAGE_T
    me_hit = mr >= apl.VERBATIM_T or mc >= apl.COVERAGE_T
    if them_hit:
        return "CLEAN" if tr >= apl.VERBATIM_T else "ANCHORED"
    return "CONTAMINATED" if me_hit else "UNSOURCED"


def self_test():
    import json, subprocess, tempfile
    ok = []
    def check(n, c):
        ok.append(c); print(("PASS " if c else "FAIL ") + n)
    texts = {
        "a.md": "The quick brown fox jumps over the lazy dog near the river bank today. Another sentence about harvest festivals in the northern valley during autumn.",
        "b.md": "Quarterly planning requires clear ownership of every deliverable across all teams involved. The committee reviewed the budget proposal and approved funding for next year projects.",
        "c.md": "Distributed systems fail in surprising ways when clocks drift between the machines that coordinate them.",
        "d.md": "Boats drift slowly down the winding channel while herons wait patiently along the muddy shoreline each morning.",
    }
    corp = Corpus(texts)
    q_exact = "The committee reviewed the budget proposal and approved funding for next year projects."
    q_edit = "the committee reviewed budget proposal and approved funding for next year projects"          # one token deleted
    q_para = "Members examined the spending plan then signed off money for the coming twelve months."
    q_neg = "Photosynthesis converts sunlight and carbon dioxide into sugars inside green leaves every single day."
    sy = {n: f(corp) for n, f in SYSTEMS.items()}
    check("B0, S, S_Bloom and B1 all find an exact sentence in the right file", all(sy[n].query(q_exact)["source_file"] == "b.md" and sy[n].query(q_exact)["verdict"] == "CLEAN" for n in sy))
    check("B1 misses an edited sentence (by design: exact substring)", sy["B1"].query(q_edit)["verdict"] == "UNSOURCED")
    check("B0, S and S_Bloom still find a lightly edited sentence", all(sy[n].query(q_edit)["source_file"] == "b.md" for n in ("B0", "S", "S_Bloom")))
    check("a paraphrase is UNSOURCED, never a confident wrong source, in every system", all(sy[n].query(q_para)["verdict"] == "UNSOURCED" for n in sy))
    check("an unrelated sentence is UNSOURCED in every system", all(sy[n].query(q_neg)["verdict"] == "UNSOURCED" for n in sy))
    r = sy["S_Bloom"].query(q_exact)
    check("Bloom keeps the true file and removes most others for a verbatim query", "b.md" in r["kept_files"] and r["candidate_files"] < len(texts))
    b = Bloom(200)
    for i in range(200):
        b.add(f"item-{i}")
    check("Bloom filter has no false negatives and a false-positive rate near 1 percent", all(f"item-{i}" in b for i in range(200)) and sum(f"other-{i}" in b for i in range(5000)) / 5000 < 0.03)
    check("S and B0 agree on every query in the mini set", all(sy["S"].query(q) == {k: v for k, v in sy["B0"].query(q).items()} for q in (q_exact, q_edit, q_para, q_neg)))
    blob = b"alpha beta gamma delta\n" * 20
    h = blob_hash(blob)
    check("tamper: a one-byte flip and a whitespace-only change are flagged, an unmodified re-read is not", tamper_flagged(h, mutate(blob, 5)) and tamper_flagged(h, mutate_ws(blob, 5)) and not tamper_flagged(h, blob))
    them = ["we are hiring about ten engineers this quarter across the whole region", "the process takes five stages and moves quickly"]
    me = ["i ship code every single day and i love it", "we have run similar projects before in finance"]
    qs = [("we are hiring about ten engineers this quarter across the whole region", them, me, "CLEAN"),
          ("i ship code every single day and i love it", them, me, "CONTAMINATED"),
          ("completely unrelated statement about volcanic geology in iceland today", them, me, "UNSOURCED")]
    ti, mi = SpeakerIndex(them), SpeakerIndex(me)
    check("speaker: S and the lint give the same verdict as the rule (CLEAN / CONTAMINATED / UNSOURCED)",
          all(s_verdict(q, ti, mi) == lint_verdict(q, t, m) == exp for q, t, m, exp in qs))
    check("speaker: a quote under 5 tokens falls back to a full scan and still agrees with the lint", s_verdict("ship code daily", ti, mi) == lint_verdict("ship code daily", them, me))
    # determinism: the same queries under two hash seeds give byte-identical output
    code = ("import sys,json; sys.path.insert(0,%r); import provenance_bench_systems as p; "
            "t=%r; c=p.Corpus(t); out=[]\nfor n in ('B0','B1','S','S_Bloom'):\n  s=p.SYSTEMS[n](c)\n  out.append([s.query(q) for q in %r])\nprint(json.dumps(out,sort_keys=True))") % (HERE, texts, [q_exact, q_edit, q_para, q_neg])
    outs = {sd: subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env={**os.environ, "PYTHONHASHSEED": sd}).stdout for sd in ("1", "2", "3", "4")}
    check("deterministic: byte-identical output from all four systems under four hash seeds", len(set(outs.values())) == 1 and outs["1"].strip() != "")
    print(f"self-test: {sum(ok)}/{len(ok)} pass")
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(self_test() if "--self-test" in sys.argv else sys.exit(__doc__))
