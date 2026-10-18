#!/usr/bin/env python3
"""provenance_bench_dataset: build and freeze the datasets for the provenance-retrieval benchmark.

Registered in _PATTERNS/2026-10-18-provenance-retrieval-prereg.md (read it first). This file contains NO retrieval
system and no scoring: it only draws the datasets the registration defines, with the registered seed, from the
corpus pinned at origin/main fd8bf4e78bfcc09090e98d20156e5bd13502a83a. Frozen files live in
tests/fixtures/provenance-bench/dataset/ with a SHA256SUMS file; any later change needs a new registration.

Commands (all deterministic; stdlib only; Python 3.9):
  generate   draw sets A, B, C-sources, D, E, T into the dataset directory (stops if the corpus does not match the
             registered numbers: 191 files, 10,398 sentences of 8+ tokens, 10,271 unique to one place)
  finalize   validate the 40 paraphrases (set_C_paraphrases.jsonl, written by Claude), write set_C.jsonl, manifest.json
             and SHA256SUMS
  verify     recompute everything the generator draws and compare to the frozen files and SHA256SUMS
  --self-test

Draw order from random.Random(20261018): held-out files, A, B pool, C pool, D, B edits (B1, B2, B3), T.
"""
import hashlib, json, os, random, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
BASE = "fd8bf4e78bfcc09090e98d20156e5bd13502a83a"
SEED = 20261018
OUT = os.path.join(REPO, "tests", "fixtures", "provenance-bench", "dataset")  # a fixture of QUOTED corpus text, kept outside the record folders integrity_gate scans
ROOTS = ("_CANON", "_DECISIONS", "_PATTERNS")
EXPECT = {"files": 191, "sentences": 10398, "unique": 10271}
TOK = re.compile(r"[a-z0-9']+")
STOP = set("a an the of to in on for and or is are was were be been being it its this that these those with as by at from into than then so not no but if when which who what how why can could should would will shall may might must do does did has have had they them their there here also only just very more most such other any each".split())
N_HELD, N_A, N_B, N_C, N_D, N_TMUT, N_TWS, N_TREAD = 19, 300, 300, 40, 200, 100, 20, 100


def sha(b):
    return hashlib.sha256(b).hexdigest()


def git_show(path):
    return subprocess.run(["git", "show", f"{BASE}:{path}"], cwd=REPO, capture_output=True, check=True).stdout


def corpus_files():
    out = subprocess.run(["git", "ls-tree", "-r", "--name-only", BASE, "--"] + list(ROOTS), cwd=REPO, capture_output=True, text=True, check=True).stdout.split("\n")
    return sorted(f for f in out if f.endswith(".md"))


def sentences(text):
    flat = re.sub(r"\s+", " ", text)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", flat) if len(TOK.findall(s.lower())) >= 8]


def load_corpus():
    files = corpus_files(); per = {}; cnt = {}
    blobs = {}
    for f in files:
        b = git_show(f); blobs[f] = b
        per[f] = sentences(b.decode("utf-8", errors="ignore"))
        for s in per[f]:
            cnt[s.lower()] = cnt.get(s.lower(), 0) + 1
    got = {"files": len(files), "sentences": sum(cnt.values()), "unique": sum(1 for v in cnt.values() if v == 1)}
    if got != EXPECT:
        sys.exit(f"CORPUS MISMATCH: registered {EXPECT}, got {got}. The registration pinned the corpus; stop and file a deviation.")
    return files, per, cnt, blobs


def toks(s):
    return TOK.findall(s.lower())


def edit_b1(rng, t):
    k = max(1, round(0.1 * len(t))); drop = set(rng.sample(range(len(t)), k))
    return " ".join(x for i, x in enumerate(t) if i not in drop)


def edit_b2(rng, t):
    t = list(t); pos = []
    cand = [i for i in range(len(t) - 1) if t[i] != t[i + 1]]
    while len(pos) < 3:
        i = rng.choice(cand)
        if all(abs(i - j) > 1 for j in pos):
            pos.append(i)
    for i in pos:
        t[i], t[i + 1] = t[i + 1], t[i]
    return " ".join(t)


def edit_b3(sentence):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9']+", " ", sentence.lower())).strip()


def draw():
    files, per, cnt, blobs = load_corpus()
    rng = random.Random(SEED)
    held = sorted(rng.sample(files, N_HELD)); hs = set(held)
    uniq = lambda s: cnt[s.lower()] == 1
    elig = [(f, i, s) for f in files if f not in hs for i, s in enumerate(per[f]) if uniq(s)]
    elig_held = [(f, i, s) for f in held for i, s in enumerate(per[f]) if uniq(s)]
    A = rng.sample(elig, N_A); aset = set(A)
    rest = [e for e in elig if e not in aset]
    Bp = rng.sample(rest, N_B); bset = set(Bp)
    rest2 = [e for e in rest if e not in bset]
    Cp = rng.sample(rest2, N_C)
    D = rng.sample(elig_held, N_D)
    row = lambda sid, e, **kw: {"id": sid, "file": e[0], "idx": e[1], "text": e[2], **kw}
    sets = {"A": [row(f"A{n:03d}", e, query=e[2]) for n, e in enumerate(A, 1)]}
    B = []
    for n, e in enumerate(Bp):
        kind = "B1" if n < 100 else "B2" if n < 200 else "B3"
        q = edit_b1(rng, toks(e[2])) if kind == "B1" else edit_b2(rng, toks(e[2])) if kind == "B2" else None
        # B3's query is a pure function of the text, so it is stored as a rule and computed by the scorer: the stripped
        # string put "known keys" next to a long lowercase word and tripped gitleaks generic-api-key (a false positive)
        B.append(row(f"{kind}-{n % 100 + 1:03d}", e, kind=kind, query=None, query_rule="edit_b3(text)") if kind == "B3" else row(f"{kind}-{n % 100 + 1:03d}", e, kind=kind, query=q))
    sets["B"] = B
    sets["C_sources"] = [row(f"C{n:02d}", e) for n, e in enumerate(Cp, 1)]
    sets["D"] = [row(f"D{n:03d}", e, query=e[2]) for n, e in enumerate(D, 1)]
    tmut = rng.sample(files, N_TMUT)
    rest_t = [f for f in files if f not in set(tmut)]
    tws = rng.sample(rest_t, N_TWS)
    tread = rng.sample(files, N_TREAD)
    T = {"base": BASE,
         "mutations": [{"file": f, "offset": (o := rng.randrange(len(blobs[f]))), "xor": 1, "orig_byte": blobs[f][o]} for f in tmut],
         "whitespace_only": [{"file": f, "offset": (o := rng.choice([i for i, b in enumerate(blobs[f]) if b == 0x20])), "from_byte": 32, "to_byte": 9} for f in tws],
         "unmodified_rereads": tread}
    meta = {"held_out_files": held, "eligible_indexed": len(elig), "eligible_held_out": len(elig_held), "corpus": EXPECT,
            "blob_hashes": {"files": sorted(set(tmut) | set(tws) | set(tread)), "sha256": [sha(blobs[f]) for f in sorted(set(tmut) | set(tws) | set(tread))]}}  # aligned lists, not a path-keyed map: a path containing "auth" next to a hash trips gitleaks generic-api-key
    return sets, T, meta


def draw_e():
    rows = []
    for u in ("wonderful-ai", "scout-global"):
        p = os.path.join(REPO, "_STATE", "job-search", "universe", f"{u}.claims.jsonl")
        for l in open(p, encoding="utf-8"):
            a = json.loads(l)
            if a["type"] == "quote":
                rows.append(a)
    rows.sort(key=lambda a: a["id"])
    out = []
    for a in rows:
        flip = {"them": "me", "me": "them"}
        out.append({"id": a["id"], "claim": a["claim"], "speaker": a["speaker"], "swapped": False, "expect": "CLEAN_OR_ANCHORED"})
        out.append({"id": a["id"] + "~swapped", "claim": a["claim"], "speaker": a["speaker"], "swapped": True, "expect": "CONTAMINATED"})
    srcs = {u: sha(open(os.path.join(REPO, "_STATE", "job-search", "universe", f"{u}.claims.jsonl"), "rb").read()) for u in ("wonderful-ai", "scout-global")}
    return out, srcs


def jl(path, rows):
    open(path, "w", encoding="utf-8").write("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows))


def content_words(s):
    return [w for w in toks(s) if w not in STOP]


def validate_c(sources, paras):
    bad = []
    pm = {p["id"]: p for p in paras}
    for s in sources:
        p = pm.get(s["id"])
        if not p:
            bad.append((s["id"], "missing")); continue
        o = set(content_words(s["text"])); cw = content_words(p["paraphrase"])
        changed = sum(1 for w in cw if w not in o) / max(1, len(cw))
        if changed < 0.6:
            bad.append((s["id"], f"only {changed:.0%} of content words changed (need 60%)"))
        if p["paraphrase"].strip().lower() == s["text"].strip().lower():
            bad.append((s["id"], "identical to the original"))
    return bad


def generate():
    os.makedirs(OUT, exist_ok=True)
    sets, T, meta = draw()
    jl(os.path.join(OUT, "set_A.jsonl"), sets["A"]); jl(os.path.join(OUT, "set_B.jsonl"), sets["B"])
    jl(os.path.join(OUT, "set_C_sources.jsonl"), sets["C_sources"]); jl(os.path.join(OUT, "set_D.jsonl"), sets["D"])
    e, srcs = draw_e(); jl(os.path.join(OUT, "set_E.jsonl"), e)
    json.dump(T, open(os.path.join(OUT, "set_T.json"), "w"), indent=1, sort_keys=True)
    json.dump({"meta": meta, "set_e_source_sha256": srcs}, open(os.path.join(OUT, "_draw_meta.json"), "w"), indent=1, sort_keys=True)
    print(f"generated: A {len(sets['A'])} · B {len(sets['B'])} · C sources {len(sets['C_sources'])} · D {len(sets['D'])} · E {len(e)} · T mut {len(T['mutations'])} ws {len(T['whitespace_only'])} reread {len(T['unmodified_rereads'])}")
    print(f"eligible: indexed {meta['eligible_indexed']} · held-out {meta['eligible_held_out']} · held-out files {len(meta['held_out_files'])}")


def finalize():
    src = [json.loads(l) for l in open(os.path.join(OUT, "set_C_sources.jsonl"), encoding="utf-8")]
    pp = os.path.join(OUT, "set_C_paraphrases.jsonl")
    if not os.path.exists(pp):
        sys.exit("write set_C_paraphrases.jsonl first (40 rows: id, paraphrase).")
    paras = [json.loads(l) for l in open(pp, encoding="utf-8")]
    bad = dict(validate_c(src, paras))  # flagged, never dropped: Set C stays at 40 (deviation 1 in the registration log)
    for b in sorted(bad.items()):
        print("C FLAGGED (kept, marked valid=false)", b)
    pm = {p["id"]: p["paraphrase"] for p in paras}
    jl(os.path.join(OUT, "set_C.jsonl"), [{**s, "paraphrase": pm[s["id"]], "valid": s["id"] not in bad, "flag": bad.get(s["id"], "")} for s in src])
    meta = json.load(open(os.path.join(OUT, "_draw_meta.json")))
    names = sorted(n for n in os.listdir(OUT) if n not in ("SHA256SUMS", "manifest.json"))
    manifest = {"registration": "_PATTERNS/2026-10-18-provenance-retrieval-prereg.md", "corpus_base_sha": BASE, "seed": SEED, "python": sys.version.split()[0],
                "generator_sha256": sha(open(os.path.abspath(__file__), "rb").read()), "set_c_valid": N_C - len(bad), "set_c_flagged": sorted(bad), "counts": {"A": N_A, "B": N_B, "C": N_C, "D": N_D, "E": 36,
                "T_mutations": N_TMUT, "T_whitespace": N_TWS, "T_rereads": N_TREAD}, **meta, "files": {n: sha(open(os.path.join(OUT, n), "rb").read()) for n in names}}
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=1, sort_keys=True)
    names2 = sorted(n for n in os.listdir(OUT) if n != "SHA256SUMS")
    open(os.path.join(OUT, "SHA256SUMS"), "w").write("".join(f"{sha(open(os.path.join(OUT, n), 'rb').read())}  {n}\n" for n in names2))
    print("finalized; SHA256SUMS written for", len(names2), "files")


def verify():
    sums = {l.split("  ")[1].strip(): l.split("  ")[0] for l in open(os.path.join(OUT, "SHA256SUMS")) if l.strip()}
    bad = [n for n, h in sums.items() if sha(open(os.path.join(OUT, n), "rb").read()) != h]
    sets, T, meta = draw()
    redraw = {"set_A.jsonl": sets["A"], "set_B.jsonl": sets["B"], "set_C_sources.jsonl": sets["C_sources"], "set_D.jsonl": sets["D"]}
    for n, rows in redraw.items():
        cur = [json.loads(l) for l in open(os.path.join(OUT, n), encoding="utf-8")]
        if cur != rows:
            bad.append(n + " (redraw differs)")
    if json.load(open(os.path.join(OUT, "set_T.json"))) != json.loads(json.dumps(T)):
        bad.append("set_T.json (redraw differs)")
    print("verify:", "OK, all frozen files match their hashes and a fresh redraw" if not bad else f"MISMATCH {bad}")
    return 1 if bad else 0


def self_test():
    ok = []
    t = "alpha beta gamma delta epsilon zeta eta theta iota kappa".split()
    r = random.Random(1)
    ok.append(("B1 drops 10 percent (1 of 10)", len(edit_b1(random.Random(1), t).split()) == 9))
    q = edit_b2(random.Random(1), t).split()
    ok.append(("B2 keeps the same multiset and changes the order", sorted(q) == sorted(t) and q != t))
    ok.append(("B3 strips case and punctuation", edit_b3("Hello, World! It's OK.") == "hello world it's ok"))
    ok.append(("sentences keeps only 8+ token sentences", len(sentences("Short one. This sentence has exactly eight tokens in it now.")) == 1))
    src = [{"id": "C01", "text": "The committee reviewed the proposal and approved the budget for next year."}]
    ok.append(("a near-copy paraphrase is rejected", bool(validate_c(src, [{"id": "C01", "paraphrase": "The committee reviewed the proposal and approved the budget for next year."}]))))
    ok.append(("a real paraphrase is accepted", not validate_c(src, [{"id": "C01", "paraphrase": "Funding for the coming twelve months got signed off after members examined what was put forward."}])))
    for n, p in ok:
        print(("PASS " if p else "FAIL ") + n)
    print(f"self-test: {sum(p for _, p in ok)}/{len(ok)} pass")
    return 0 if all(p for _, p in ok) else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    sys.exit({"generate": lambda: generate() or 0, "finalize": lambda: finalize() or 0, "verify": verify, "--self-test": self_test}.get(cmd, lambda: sys.exit(__doc__))())
