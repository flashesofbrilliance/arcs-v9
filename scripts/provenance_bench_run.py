#!/usr/bin/env python3
"""provenance_bench_run: the run harness for the provenance-retrieval benchmark (registered in
_PATTERNS/2026-10-18-provenance-retrieval-prereg.md). It runs the systems from provenance_bench_systems.py over the frozen
datasets and writes raw outputs in the layout provenance_bench_score.py reads. It does no scoring.

STEP 4 STATE: this harness is implemented and self-tested on a SYNTHETIC mini-corpus only. It has not been run on the frozen
datasets; the registered order puts the single run at step 5.

Subcommands (all take --out RESULTS_DIR):
  verdicts --system X --tag seed1.rep1   build the index, answer sets A B C D, write verdicts (+ prefilter rows for S_Bloom)
  timing   --system X --frac F --cold 1 --warm 5 --tag t   one fresh process: timed index build, then 1 cold + N warm passes over Set A
  tamper                                 hash check over set_T.json (flip, whitespace-only, unmodified re-reads)
  speaker                                Set E: current lint vs S, same transcript
  h8                                     Librarian lineage profile and comparison (needs the Librarian change on the branch)
  orchestrate                            everything, in the registered order, with timing runs ALONE (nothing else running)

Choices fixed before any run (also in the registration log, note 3):
  * Timing: per frac, one fresh process does the timed index build, one cold pass, then N warm passes. At frac 1.0 the cold
    pass is repeated in 3 fresh processes (3 cold) and 5 warm passes are taken in the first (5 warm). Fractions 0.25 and 0.5
    use one process each with 1 cold and 5 warm. Nested subsets: indexed files shuffled by Random(SEED + 1), first ceil(frac x n).
  * Determinism: each system's verdict files are produced by 12 separate processes (PYTHONHASHSEED 1 to 4, repetitions 1 to 3)
    and hashed; the canonical files are the (seed1, rep1) outputs.
  * Verdict files carry no timings. Timings are separate files.
Stdlib only.
"""
import argparse, concurrent.futures, hashlib, json, math, os, random, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
REPO = os.path.dirname(HERE)
import provenance_bench_dataset as D
import provenance_bench_systems as P

SYSTEM_NAMES = ("B0", "B1", "S", "S_Bloom")
SETS = ("A", "B", "C", "D")
SEED_TAGS = [f"seed{s}.rep{r}" for s in (1, 2, 3, 4) for r in (1, 2, 3)]
TRANSCRIPT = os.path.join(REPO, "_STATE", "job-search", "universe", "sources", "scout-call-2026-10-13.txt")


def jl(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def wjl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows))


class Env:
    """Everything a run needs. Real: the pinned corpus and frozen datasets. Synthetic: injected by the self-test."""
    def __init__(self, ds_dir, texts, held_out, blobs=None, blob_hashes=None, transcript=None):
        self.ds_dir, self.texts, self.held_out = ds_dir, texts, set(held_out)
        self.indexed = {f: t for f, t in texts.items() if f not in self.held_out}
        self.blobs = blobs or {}; self.blob_hashes = blob_hashes or {}; self.transcript = transcript

    @classmethod
    def real(cls):
        hook = os.environ.get("PROVENANCE_BENCH_ENV")   # test hook: a JSON file describing a SYNTHETIC env, inherited by child processes
        if hook:
            j = json.load(open(hook))
            return cls(j["ds_dir"], j["texts"], j["held_out"], {f: bytes.fromhex(h) for f, h in j["blobs_hex"].items()}, j["blob_hashes"], j.get("transcript"))
        files, per, cnt, blobs = D.load_corpus()
        meta = json.load(open(os.path.join(D.OUT, "_draw_meta.json")))["meta"]
        bh = dict(zip(meta["blob_hashes"]["files"], meta["blob_hashes"]["sha256"]))
        return cls(D.OUT, {f: blobs[f].decode("utf-8", errors="ignore") for f in files}, meta["held_out_files"], blobs, bh, TRANSCRIPT)

    def rows(self, s):
        return jl(os.path.join(self.ds_dir, f"set_{s}.jsonl"))

    def queries(self, s):
        out = []
        for r in self.rows(s):
            q = D.edit_b3(r["text"]) if r.get("kind") == "B3" else r["paraphrase"] if s == "C" else r["query"]
            out.append((r["id"], q, r.get("file") if s != "D" else None))
        return out

    def subset(self, frac):
        files = sorted(self.indexed)
        order = files[:]; random.Random(D.SEED + 1).shuffle(order)
        keep = sorted(order[:max(1, math.ceil(frac * len(files)))])
        return {f: self.indexed[f] for f in keep}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def cmd_verdicts(env, system, out, tag):
    corpus = P.Corpus(env.indexed); sysm = P.SYSTEMS[system](corpus); hashes = {}; pre = []
    base = os.path.join(out, "_runs", tag, "verdicts")
    for s in SETS:
        rows = []
        for sid, q, truth in env.queries(s):
            r = sysm.query(q)
            rows.append({"id": sid, "verdict": r["verdict"], "source_file": r["source_file"]})
            if system == "S_Bloom":
                pre.append({"id": sid, "set": s, "candidate_files": r["candidate_files"], "total_files": len(corpus.files),
                            "true_file_kept": (truth in r["kept_files"]) if truth else True})
        rows.sort(key=lambda r: r["id"])
        p = os.path.join(base, f"{system}.{s}.jsonl"); wjl(p, rows); hashes[f"{system}.{s}"] = sha(open(p, "rb").read())
    if system == "S_Bloom":
        wjl(os.path.join(out, "_runs", tag, "prefilter", "S_Bloom.jsonl"), sorted(pre, key=lambda r: (r["set"], r["id"])))
    return hashes


def cmd_timing(env, system, frac, cold, warm, out, tag):
    texts = env.subset(frac)
    t0 = time.perf_counter(); corpus = P.Corpus(texts); sysm = P.SYSTEMS[system](corpus); build = time.perf_counter() - t0
    qs = env.queries("A"); rows = []
    for ph, n in (("cold", cold), ("warm", warm)):
        for run in range(1, n + 1):
            for sid, q, _ in qs:
                t = time.perf_counter(); sysm.query(q); rows.append({"id": sid, "phase": ph, "run": run, "corpus_frac": frac, "latency_s": time.perf_counter() - t, "tag": tag})
    wjl(os.path.join(out, "_timing", f"{system}.{frac}.{tag}.jsonl"), rows)
    json.dump({"system": system, "frac": frac, "build_s": build, "tag": tag}, open(os.path.join(out, "_timing", f"{system}.{frac}.{tag}.build.json"), "w"))
    return build


def cmd_tamper(env, out):
    T = json.load(open(os.path.join(env.ds_dir, "set_T.json")))
    res = {"mutations": [], "whitespace_only": [], "rereads": []}
    for m in T["mutations"]:
        res["mutations"].append({"file": m["file"], "flagged": P.tamper_flagged(env.blob_hashes[m["file"]], P.mutate(env.blobs[m["file"]], m["offset"], m["xor"]))})
    for m in T["whitespace_only"]:
        res["whitespace_only"].append({"file": m["file"], "flagged": P.tamper_flagged(env.blob_hashes[m["file"]], P.mutate_ws(env.blobs[m["file"]], m["offset"], m["to_byte"]))})
    for f in T["unmodified_rereads"]:
        res["rereads"].append({"file": f, "flagged": P.tamper_flagged(env.blob_hashes[f], env.blobs[f])})
    json.dump(res, open(os.path.join(out, "tamper.json"), "w"), indent=1)
    return res


def cmd_speaker(env, out):
    if not env.transcript or not os.path.exists(env.transcript):
        print("speaker: transcript not on this machine; Set E skipped (reported, not scored)."); return None
    turns = P.apl.parse_source(env.transcript)
    ti, mi = P.SpeakerIndex(turns["them"]), P.SpeakerIndex(turns["me"])
    lint_rows, s_rows = [], []
    for r in env.rows("E"):
        a, b = (turns["me"], turns["them"]) if r["swapped"] else (turns["them"], turns["me"])
        lint_rows.append({"id": r["id"], "verdict": P.lint_verdict(r["claim"], a, b), "source_file": None})
        x, y = (mi, ti) if r["swapped"] else (ti, mi)
        s_rows.append({"id": r["id"], "verdict": P.s_verdict(r["claim"], x, y), "source_file": None})
    wjl(os.path.join(out, "verdicts", "lint.E.jsonl"), sorted(lint_rows, key=lambda r: r["id"]))
    wjl(os.path.join(out, "verdicts", "S.E.jsonl"), sorted(s_rows, key=lambda r: r["id"]))
    return lint_rows, s_rows


def merge_timing(out):
    td = os.path.join(out, "_timing")
    if not os.path.isdir(td):
        return
    allb = json.load(open(os.path.join(out, "timings", "build.json"))) if os.path.exists(os.path.join(out, "timings", "build.json")) else {}
    for system in SYSTEM_NAMES:
        rows, builds = [], {}
        for n in sorted(os.listdir(td)):
            if not n.startswith(system + "."):
                continue
            if n.endswith(".build.json"):
                bj = json.load(open(os.path.join(td, n))); builds.setdefault(str(bj["frac"]), []).append(bj["build_s"])
            elif n.endswith(".jsonl"):
                rows += jl(os.path.join(td, n))
        if rows:
            wjl(os.path.join(out, "timings", f"{system}.A.jsonl"), rows)
            allb[system] = {k: sorted(v)[len(v) // 2] for k, v in builds.items()}   # median build time across the processes at that fraction
    os.makedirs(os.path.join(out, "timings"), exist_ok=True)
    json.dump(allb, open(os.path.join(out, "timings", "build.json"), "w"), indent=1)


def load_librarian():
    import importlib.util
    spec = importlib.util.spec_from_file_location("arcs_librarian", os.path.join(REPO, "operators", "arcs_librarian.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def cmd_h8(out, al=None, make_lib=None, query="ADR-084", n_max=3, reps=3):
    """H8: profile the pairwise lineage pass inside recommend(), compare it with the index, time before and after, and scale.
    Registered query: "ADR-084", n_max 3, the full pool with the receipts universe loaded. 'before' is measured in this same
    session with the pairwise pass swapped in, not copied from the 5.3 s note, so machine state cancels."""
    al = al or load_librarian()
    if not (hasattr(al, "_lineage_indegree") and hasattr(al, "_lineage_indegree_bruteforce")):
        sys.exit("this branch does not carry the Librarian lineage change (the draft H8 PR); h8 cannot run here.")
    lib = make_lib() if make_lib else al.Librarian()
    pool = list(lib.candidates); med = lambda xs: sorted(xs)[len(xs) // 2]
    def timed(fn):
        t = time.perf_counter(); fn(); return time.perf_counter() - t
    texts_l = [c.text.lower() for c in pool]
    t_brute = med([timed(lambda: al._lineage_indegree_bruteforce(pool, texts_l)) for _ in range(reps)])
    t_index = med([timed(lambda: al._lineage_indegree(pool, texts_l)) for _ in range(reps)])
    a, b = al._lineage_indegree_bruteforce(pool, texts_l), al._lineage_indegree(pool, texts_l)
    mismatches = sum(1 for k in set(a) | set(b) if a.get(k) != b.get(k))
    def wall(fn_name):
        orig = al._lineage_indegree; al._lineage_indegree = getattr(al, fn_name)
        try:
            return med([timed(lambda: lib.recommend(query, n_max=n_max)) for _ in range(reps)])
        finally:
            al._lineage_indegree = orig
    before, after = wall("_lineage_indegree_bruteforce"), wall("_lineage_indegree")
    order = list(range(len(pool))); random.Random(D.SEED + 2).shuffle(order); scaling = []
    try:
        for frac in (0.25, 0.5, 1.0):
            lib.candidates = [pool[i] for i in sorted(order[:max(1, math.ceil(frac * len(pool)))])]
            scaling.append({"frac": frac, "time_s": med([timed(lambda: lib.recommend(query, n_max=n_max)) for _ in range(reps)])})
    finally:
        lib.candidates = pool
    res = {"lineage_share": t_brute / before, "indegree_mismatches": mismatches, "wall_before_s": before, "wall_after_s": after, "scaling": scaling,
           "detail": {"candidates": len(pool), "pairwise_pass_s": t_brute, "index_pass_s": t_index, "query": query, "n_max": n_max, "reps": reps}}
    os.makedirs(out, exist_ok=True); json.dump(res, open(os.path.join(out, "h8.json"), "w"), indent=1)
    return res


def run_sub(args, seed=None):
    env = dict(os.environ)
    if seed:
        env["PYTHONHASHSEED"] = str(seed)
    return subprocess.run([sys.executable, os.path.abspath(__file__)] + args, capture_output=True, text=True, env=env)


def orchestrate(out, jobs, systems=SYSTEM_NAMES, fracs=(0.25, 0.5, 1.0), cold_procs=3, warm=5, tags=SEED_TAGS):
    os.makedirs(out, exist_ok=True)
    json.dump({"python": sys.version.split()[0], "uptime": subprocess.run(["uptime"], capture_output=True, text=True).stdout.strip(),
               "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "jobs": jobs}, open(os.path.join(out, "_env.json"), "w"), indent=1)
    # Stage 1: timing, serial, nothing else running (protocol: no other heavy process).
    for system in [s for s in ("B0", "S", "S_Bloom") if s in systems]:
        for frac in fracs:
            for i in range(1, (cold_procs if frac == 1.0 else 1) + 1):
                r = run_sub(["timing", "--system", system, "--frac", str(frac), "--cold", "1", "--warm", str(warm if i == 1 else 0), "--tag", f"p{i}", "--out", out])
                if r.returncode: sys.exit(f"timing crashed: {r.stderr[-400:]}")
    merge_timing(out)
    # Stage 2: verdicts under 4 hash seeds x 3 repetitions, in parallel (timings are already done).
    def one(job):
        system, tag = job
        r = run_sub(["verdicts", "--system", system, "--tag", tag, "--out", out], seed=int(tag[4]))
        if r.returncode:
            raise RuntimeError(f"{system} {tag}: {r.stderr[-400:]}")
        return system, tag, json.loads(r.stdout.strip().splitlines()[-1])
    det = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as ex:
        for system, tag, hs in ex.map(one, [(s, t) for s in systems for t in tags]):
            for k, h in hs.items():
                det.setdefault(k, {})[tag] = h
    os.makedirs(os.path.join(out, "verdicts"), exist_ok=True)
    json.dump(det, open(os.path.join(out, "verdicts", "determinism.json"), "w"), indent=1, sort_keys=True)
    first = tags[0]
    for n in os.listdir(os.path.join(out, "_runs", first, "verdicts")):
        wjl(os.path.join(out, "verdicts", n), jl(os.path.join(out, "_runs", first, "verdicts", n)))
    pf = os.path.join(out, "_runs", first, "prefilter", "S_Bloom.jsonl")
    if os.path.exists(pf):
        wjl(os.path.join(out, "prefilter", "S_Bloom.jsonl"), jl(pf))
    # Stage 3: tamper and speaker.
    for c in ("tamper", "speaker"):
        r = run_sub([c, "--out", out])
        if r.returncode:
            sys.exit(f"{c} crashed: {r.stderr[-400:]}")
    print("orchestrate done:", out)


def self_test():
    ok = []
    def check(n, c):
        ok.append(c); print(("PASS " if c else "FAIL ") + n)
    texts = {f"f{i}.md": " ".join(f"Document {i} sentence number {j} talks about subject {i * 7 + j} in considerable detail for testing purposes only." for j in range(6)) for i in range(8)}
    texts["f9.md"] = "Held out file sentence about volcanic geology in iceland describing eruptions and glaciers across many centuries."
    tmp = tempfile.mkdtemp(); dsd = os.path.join(tmp, "ds"); os.makedirs(dsd)
    sentences = {f: D.sentences(t) for f, t in texts.items()}
    mk = lambda f, i: sentences[f][i]
    W = lambda name, rows: wjl(os.path.join(dsd, name), rows)
    W("set_A.jsonl", [{"id": "A1", "file": "f1.md", "query": mk("f1.md", 2)}, {"id": "A2", "file": "f3.md", "query": mk("f3.md", 4)}])
    W("set_B.jsonl", [{"id": "B1-001", "file": "f2.md", "kind": "B1", "query": " ".join(P.toks(mk("f2.md", 1))[:-2] + P.toks(mk("f2.md", 1))[-1:])},
                      {"id": "B3-001", "file": "f4.md", "kind": "B3", "query": None, "text": mk("f4.md", 3)}])
    W("set_C.jsonl", [{"id": "C01", "file": "f5.md", "paraphrase": "Entirely different wording about something unrelated to the corpus at hand", "valid": True}])
    W("set_D.jsonl", [{"id": "D001", "file": "f9.md", "query": sentences["f9.md"][0]}])
    W("set_E.jsonl", [])
    blobs = {f: t.encode() for f, t in texts.items()}
    bh = {f: sha(b) for f, b in blobs.items()}
    json.dump({"mutations": [{"file": "f1.md", "offset": 3, "xor": 1}], "whitespace_only": [{"file": "f2.md", "offset": 8, "to_byte": 9}], "unmodified_rereads": ["f3.md", "f4.md"]}, open(os.path.join(dsd, "set_T.json"), "w"))
    env = Env(dsd, texts, ["f9.md"], blobs, bh, None)
    check("held-out files are not in the index", "f9.md" not in env.indexed)
    nested = {f: set(env.subset(f_).keys()) for f, f_ in ((0.25, 0.25), (0.5, 0.5), (1.0, 1.0))}
    check("scaling subsets are nested and grow with the fraction", nested[0.25] <= nested[0.5] <= nested[1.0] and len(nested[0.25]) < len(nested[1.0]))
    out = os.path.join(tmp, "res")
    h1 = cmd_verdicts(env, "S", out, "seed1.rep1"); h2 = cmd_verdicts(env, "S", out, "seed1.rep2")
    check("verdict files are identical across repetitions", h1 == h2)
    rows = jl(os.path.join(out, "_runs", "seed1.rep1", "verdicts", "S.A.jsonl"))
    check("S finds both Set A queries in the right files", {r["id"]: r["source_file"] for r in rows} == {"A1": "f1.md", "A2": "f3.md"})
    cmd_verdicts(env, "S_Bloom", out, "seed1.rep1"); pf = jl(os.path.join(out, "_runs", "seed1.rep1", "prefilter", "S_Bloom.jsonl"))
    check("S_Bloom writes prefilter rows with the true file kept for A and B", all(r["true_file_kept"] for r in pf if r["set"] in ("A", "B")) and len(pf) >= 5)
    d = jl(os.path.join(out, "_runs", "seed1.rep1", "verdicts", "S.D.jsonl"))
    check("a held-out negative is UNSOURCED, never a confident source", d[0]["verdict"] == "UNSOURCED")
    b = jl(os.path.join(out, "_runs", "seed1.rep1", "verdicts", "S.B.jsonl"))
    check("B3 is computed from the text by rule (query stored as null in the dataset)", {r["id"]: r["source_file"] for r in b}["B3-001"] == "f4.md")
    cmd_timing(env, "S", 1.0, 1, 2, out, "p1"); tr = jl(os.path.join(out, "_timing", "S.1.0.p1.jsonl"))
    check("timing writes 1 cold and 2 warm passes over Set A with a corpus fraction", sum(r["phase"] == "cold" for r in tr) == 2 and sum(r["phase"] == "warm" for r in tr) == 4 and all(r["corpus_frac"] == 1.0 for r in tr))
    t = cmd_tamper(env, out)
    check("tamper: flip and whitespace-only change flagged, unmodified re-reads not", t["mutations"][0]["flagged"] and t["whitespace_only"][0]["flagged"] and not any(r["flagged"] for r in t["rereads"]))
    # end to end through the orchestrator, children inherit the SYNTHETIC env through the hook (they never see the frozen data)
    hook = os.path.join(tmp, "env.json")
    json.dump({"ds_dir": dsd, "texts": texts, "held_out": ["f9.md"], "blobs_hex": {f: b.hex() for f, b in blobs.items()}, "blob_hashes": bh, "transcript": None}, open(hook, "w"))
    os.environ["PROVENANCE_BENCH_ENV"] = hook
    orch = os.path.join(tmp, "orch")
    orchestrate(orch, 2, systems=("B0", "B1", "S", "S_Bloom"), fracs=(0.5, 1.0), cold_procs=2, warm=2, tags=["seed1.rep1", "seed2.rep1", "seed3.rep2"])
    need = ["verdicts/S.A.jsonl", "verdicts/B0.D.jsonl", "verdicts/determinism.json", "timings/S.A.jsonl", "timings/B0.A.jsonl", "timings/build.json", "prefilter/S_Bloom.jsonl", "tamper.json"]
    check("orchestrate writes every file the scorer reads (except h8 and Set E, which have their own conditions)", all(os.path.exists(os.path.join(orch, n)) for n in need))
    det = json.load(open(os.path.join(orch, "verdicts", "determinism.json")))
    check("determinism.json holds one hash per (seed, repetition) and all agree for every system and set", all(len(v) == 3 and len(set(v.values())) == 1 for v in det.values()) and len(det) == 16)
    bj = json.load(open(os.path.join(orch, "timings", "build.json")))
    check("build.json has a time for fractions 0.5 and 1.0", set(bj["S"]) == {"0.5", "1.0"})
    trs = jl(os.path.join(orch, "timings", "S.A.jsonl"))
    check("timings: 2 cold processes and 2 warm passes at full corpus, 1 cold and 2 warm at 0.5", {(r["corpus_frac"], r["phase"]) for r in trs} == {(1.0, "cold"), (1.0, "warm"), (0.5, "cold"), (0.5, "warm")})
    # the scorer must accept the harness output layout: run it against the synthetic dataset without the frozen-data guard
    import provenance_bench_score as SC
    Rr = SC.score(orch, dsd, verify=False)
    check("the scorer reads the harness layout and produces H5, H6, H7 results", all(k in Rr["hypotheses"] for k in ("H5", "H6", "H7")) and Rr["hypotheses"]["H7"]["status"] == "PASS")
    os.environ.pop("PROVENANCE_BENCH_ENV")
    # h8 harness logic against a STUB Librarian (the real one is measured in the run, not here)
    import types
    st = types.SimpleNamespace()
    st._lineage_indegree_bruteforce = lambda cands, texts: {c.id: sum(1 for j, t in enumerate(texts) if cands[j] is not c and c.id in t) for c in cands}
    st._lineage_indegree = lambda cands, texts: st._lineage_indegree_bruteforce(cands, texts)
    cand = lambda i, t: types.SimpleNamespace(id=i, text=t)
    class StubLib:
        def __init__(self): self.candidates = [cand(f"id{i}", f"mentions id{(i + 1) % 20} and id{(i + 5) % 20}") for i in range(20)]
        def recommend(self, q, n_max=3): return st._lineage_indegree(self.candidates, [c.text.lower() for c in self.candidates])
    h8out = os.path.join(tmp, "h8out"); r8 = cmd_h8(h8out, al=st, make_lib=StubLib, reps=1)
    check("h8 writes lineage_share, mismatches, before/after wall and three scaling points (stub Librarian)",
          set(("lineage_share", "indegree_mismatches", "wall_before_s", "wall_after_s", "scaling")) <= set(r8) and len(r8["scaling"]) == 3 and r8["indegree_mismatches"] == 0)
    st._lineage_indegree = lambda cands, texts: {c.id: 0 for c in cands}
    check("h8 counts every candidate whose in-degree differs as a mismatch (fail-on-bad)", cmd_h8(h8out, al=st, make_lib=StubLib, reps=1)["indegree_mismatches"] > 0)
    try:
        cmd_h8(h8out, al=types.SimpleNamespace(), make_lib=StubLib); refused = False
    except SystemExit:
        refused = True
    check("h8 refuses to run on a branch without the Librarian change", refused)
    print(f"self-test: {sum(ok)}/{len(ok)} pass")
    return 0 if all(ok) else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("verdicts", "timing", "tamper", "speaker", "h8", "orchestrate", "self-test"))
    ap.add_argument("--system"); ap.add_argument("--out"); ap.add_argument("--tag", default="seed1.rep1")
    ap.add_argument("--frac", type=float, default=1.0); ap.add_argument("--cold", type=int, default=1); ap.add_argument("--warm", type=int, default=5)
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    if a.cmd == "self-test":
        return self_test()
    if a.cmd == "orchestrate":
        return orchestrate(a.out, a.jobs) or 0
    if a.cmd == "h8":
        cmd_h8(a.out); return 0
    env = Env.real()
    if a.cmd == "verdicts":
        print(json.dumps(cmd_verdicts(env, a.system, a.out, a.tag)))
    elif a.cmd == "timing":
        cmd_timing(env, a.system, a.frac, a.cold, a.warm, a.out, a.tag)
    elif a.cmd == "tamper":
        cmd_tamper(env, a.out)
    elif a.cmd == "speaker":
        cmd_speaker(env, a.out)
    else:
        cmd_h8(a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
