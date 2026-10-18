#!/usr/bin/env python3
"""provenance_bench_score: score the provenance-retrieval benchmark against the thresholds REGISTERED in
_PATTERNS/2026-10-18-provenance-retrieval-prereg.md. This file contains no retrieval system. It reads raw outputs that
a system wrote, joins them to the frozen datasets, and applies the registered thresholds. Thresholds live in THRESH
below and are the registration's numbers; changing one needs a new registration, not an edit here.

It refuses to score if the frozen datasets do not match their SHA256SUMS (frozen means frozen).

Results layout (a directory; names use S_Bloom for the S+Bloom system):
  verdicts/<system>.<set>.jsonl       deterministic rows {id, verdict, source_file}; NO timings (byte-identical under H7)
                                      verdict in CLEAN | ANCHORED | UNSOURCED | CONTAMINATED; set in A B C D E
  verdicts/determinism.json           {"<system>.<set>": {"seed1.rep1": "<sha256 of that verdict file>", ...}}
  timings/<system>.A.jsonl            rows {id, phase: cold|warm, run, corpus_frac, latency_s}
  timings/build.json                  {"<system>": {"<corpus_frac>": build_seconds}}
  prefilter/S_Bloom.jsonl             rows {id, set, candidate_files, total_files, true_file_kept}
  tamper.json                         {"mutations": [{"file", "flagged"}], "whitespace_only": [...], "rereads": [...]}
  h8.json                             {"lineage_share": f, "indegree_mismatches": n, "wall_before_s": 5.3, "wall_after_s": x,
                                       "scaling": [{"frac": 0.25, "time_s": t}, ...]}

Definitions fixed here before any run (the registration did not spell these out; they are written before any result exists):
  confident = verdict CLEAN or ANCHORED. UNSOURCED, SKIPPED and CONTAMINATED are not confident.
  correct   = confident and source_file equals the ground-truth file.
  confident-wrong = confident and (source_file differs from the ground truth, or the query has no source at all).
  latency headline = median over warm-run per-query latencies on Set A (cold reported separately). Index build excluded.
  scaling exponent = least-squares slope of log(build + n_queries x median latency) on log(corpus fraction).

  python3 scripts/provenance_bench_score.py --results DIR [--json OUT]
  python3 scripts/provenance_bench_score.py --self-test
Stdlib only.
"""
import argparse, hashlib, json, math, os, statistics, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
DATASET = os.path.join(REPO, "tests", "fixtures", "provenance-bench", "dataset")
CONFIDENT = ("CLEAN", "ANCHORED")
# Registered thresholds (prereg "Hypotheses, thresholds and kill conditions" and "Speed protocol").
THRESH = {
    "H1_pass_x": 10.0, "H1_kill_x": 3.0,
    "H2_pass": 0.99, "H2_kill": 0.97,
    "H3_pass": 0.90, "H3_kill_abs": 0.85, "H3_vs_B0_pts": 0.03,
    "H4_neg_pass": 0.01, "H4_neg_kill": 0.02,
    "H5_reduction_pass": 0.80, "H5_reduction_kill": 0.50,
    "H8_lineage_share_min": 0.50, "H8_wall_max_s": 3.7, "H8_reduction_kill": 0.15, "H8_exponent_max": 1.2,
    "SAFETY_pass": 0.005, "SAFETY_kill": 0.01, "SCALING_linear_max": 1.2,
}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def jl(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()] if os.path.exists(path) else []


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round((c - h) / d, 4), round((c + h) / d, 4))


def prop(k, n):
    return {"k": k, "n": n, "rate": round(k / n, 4) if n else None, "wilson95": wilson(k, n)}


def verify_dataset(ds=DATASET):
    sums = {l.split("  ")[1].strip(): l.split("  ")[0] for l in open(os.path.join(ds, "SHA256SUMS")) if l.strip()}
    bad = [n for n, h in sums.items() if sha(open(os.path.join(ds, n), "rb").read()) != h]
    if bad:
        sys.exit(f"FROZEN DATASET MISMATCH: {bad}. The registration froze these files; stop and file a deviation, do not score.")


def truth(ds):
    gt = {}
    for s in ("A", "B", "D"):
        for r in jl(os.path.join(ds, f"set_{s}.jsonl")):
            gt[(s, r["id"])] = {"file": r["file"] if s != "D" else None, "kind": r.get("kind", s)}
    for r in jl(os.path.join(ds, "set_C.jsonl")):
        gt[("C", r["id"])] = {"file": r["file"], "valid": r.get("valid", True)}
    for r in jl(os.path.join(ds, "set_E.jsonl")):
        gt[("E", r["id"])] = {"expect": r["expect"]}
    return gt


def score_set(rows, gt, s):
    """rows: verdict rows for set s. Returns counts of correct, confident-wrong, unsourced, missing."""
    got = {r["id"]: r for r in rows}
    ids = [i for (ss, i) in gt if ss == s]
    out = {"n": len(ids), "correct": 0, "confident_wrong": 0, "unsourced": 0, "missing": 0, "correct_ids": [], "wrong_ids": []}
    for i in ids:
        r = got.get(i); g = gt[(s, i)]
        if r is None:
            out["missing"] += 1; continue
        if r["verdict"] in CONFIDENT:
            ok = g.get("file") is not None and r.get("source_file") == g["file"]
            if ok:
                out["correct"] += 1; out["correct_ids"].append(i)
            else:
                out["confident_wrong"] += 1; out["wrong_ids"].append(i)
        else:
            out["unsourced"] += 1
    return out


def status_lt(v, pass_at, kill_at):
    """higher is better: PASS if v >= pass_at, KILL if v < kill_at, else FAIL (not a pass, not a kill)."""
    return "PASS" if v >= pass_at else "KILL" if v < kill_at else "FAIL"


def latencies(rows, phase):
    return [r["latency_s"] for r in rows if r.get("phase") == phase and r.get("corpus_frac", 1.0) == 1.0]


def pct(xs, q):
    xs = sorted(xs); return xs[min(len(xs) - 1, int(math.ceil(q * len(xs))) - 1)] if xs else None


def slope(points):
    pts = [(math.log(x), math.log(y)) for x, y in points if x > 0 and y > 0]
    if len(pts) < 2:
        return None
    mx = sum(p[0] for p in pts) / len(pts); my = sum(p[1] for p in pts) / len(pts)
    den = sum((p[0] - mx) ** 2 for p in pts)
    return round(sum((p[0] - mx) * (p[1] - my) for p in pts) / den, 3) if den else None


def score(results, ds=DATASET, verify=True):
    if verify:
        verify_dataset(ds)
    gt = truth(ds)
    V = lambda sysn, s: jl(os.path.join(results, "verdicts", f"{sysn}.{s}.jsonl"))
    T = lambda sysn: jl(os.path.join(results, "timings", f"{sysn}.A.jsonl"))
    R = {"hypotheses": {}, "primary_safety": {}, "decisions": {}}
    H = R["hypotheses"]
    present = lambda sysn: any(os.path.exists(os.path.join(results, "verdicts", f"{sysn}.{s}.jsonl")) for s in "ABCD")
    systems = [x for x in ("B0", "B1", "S", "S_Bloom") if present(x)]
    R["systems_present"] = systems
    sc = {x: {s: score_set(V(x, s), gt, s) for s in "ABCD"} for x in systems}
    R["counts"] = {x: {s: {k: v for k, v in sc[x][s].items() if not k.endswith("_ids")} for s in "ABCD"} for x in systems}
    # H1 speed
    if "S" in systems and "B0" in systems:
        warm = {x: latencies(T(x), "warm") for x in ("B0", "S")}
        if warm["B0"] and warm["S"]:
            ratio = statistics.median(warm["B0"]) / max(statistics.median(warm["S"]), 1e-12)
            st = "PASS" if ratio >= THRESH["H1_pass_x"] else "KILL" if ratio < THRESH["H1_kill_x"] else "WEAK"
            build = json.load(open(os.path.join(results, "timings", "build.json"))) if os.path.exists(os.path.join(results, "timings", "build.json")) else {}
            b = (build.get("S") or {}).get("1.0")
            saving = statistics.median(warm["B0"]) - statistics.median(warm["S"])
            H["H1"] = {"status": st, "speedup_median": round(ratio, 2), "B0_median_s": statistics.median(warm["B0"]), "S_median_s": statistics.median(warm["S"]),
                       "B0_p95_s": pct(warm["B0"], .95), "S_p95_s": pct(warm["S"], .95), "S_build_s": b,
                       "break_even_queries": round(b / saving, 1) if b and saving > 0 else None,
                       "cold_median_s": {x: (statistics.median(latencies(T(x), "cold")) if latencies(T(x), "cold") else None) for x in ("B0", "S")}}
    # H2 verbatim accuracy
    if "S" in systems:
        a = sc["S"]["A"]; acc = a["correct"] / a["n"]; st = status_lt(acc, THRESH["H2_pass"], THRESH["H2_kill"])
        if "B1" in systems and st == "PASS" and acc < sc["B1"]["A"]["correct"] / sc["B1"]["A"]["n"]:
            st = "FAIL"
        H["H2"] = {"status": st, "S_accuracy": prop(a["correct"], a["n"]), "B1_accuracy": prop(sc["B1"]["A"]["correct"], sc["B1"]["A"]["n"]) if "B1" in systems else None}
        # H3 edited recall
        b = sc["S"]["B"]; rec = b["correct"] / b["n"]
        b0 = (sc["B0"]["B"]["correct"] / sc["B0"]["B"]["n"]) if "B0" in systems else None
        kill = rec < THRESH["H3_kill_abs"] or (b0 is not None and rec < b0 - THRESH["H3_vs_B0_pts"])
        passed = rec >= THRESH["H3_pass"] and (b0 is None or rec >= b0 - THRESH["H3_vs_B0_pts"])
        per = {}
        for k in ("B1", "B2", "B3"):
            ids = [i for (ss, i), g in gt.items() if ss == "B" and g["kind"] == k]
            ok = set(sc["S"]["B"]["correct_ids"])
            per[k] = prop(sum(1 for i in ids if i in ok), len(ids))
        H["H3"] = {"status": "KILL" if kill else "PASS" if passed else "FAIL", "S_recall": prop(b["correct"], b["n"]),
                   "B0_recall": prop(sc["B0"]["B"]["correct"], sc["B0"]["B"]["n"]) if "B0" in systems else None, "S_per_kind": per}
        # H4 fail safe
        d = sc["S"]["D"]; fp = d["confident_wrong"] / d["n"]
        c = sc["S"]["C"]; cids = [i for (ss, i) in gt if ss == "C"]; vset = {i for i in cids if gt[("C", i)]["valid"]}
        cw_c = c["confident_wrong"]
        st = "KILL" if (fp > THRESH["H4_neg_kill"] or cw_c > 0) else "PASS" if fp <= THRESH["H4_neg_pass"] else "FAIL"
        H["H4"] = {"status": st, "S_negatives_confident": prop(d["confident_wrong"], d["n"]), "S_setC_confident_wrong": cw_c,
                   "S_setC_recall_all40": prop(c["correct"], c["n"]), "S_setC_recall_valid": prop(sum(1 for i in vset if i in set(c["correct_ids"])), len(vset)), "descriptive_only": True}
        # primary safety over A, B, D
        n = sum(sc["S"][s]["n"] for s in "ABD"); k = sum(sc["S"][s]["confident_wrong"] for s in "ABD")
        k0 = sum(sc["B0"][s]["confident_wrong"] for s in "ABD") if "B0" in systems else None
        st = "KILL" if k / n > THRESH["SAFETY_kill"] else ("PASS" if (k / n <= THRESH["SAFETY_pass"] and (k0 is None or k <= k0)) else "WARN")
        R["primary_safety"] = {"status": st, "S_confident_wrong": prop(k, n), "B0_confident_wrong_count": k0}
    # H5 bloom
    pf = jl(os.path.join(results, "prefilter", "S_Bloom.jsonl"))
    if pf:
        ab = [r for r in pf if r["set"] in ("A", "B")]
        fn = sum(1 for r in ab if not r["true_file_kept"])
        red = 1 - statistics.mean(r["candidate_files"] / r["total_files"] for r in pf)
        st = "KILL" if (fn > 0 or red < THRESH["H5_reduction_kill"]) else "PASS" if red >= THRESH["H5_reduction_pass"] else "FAIL"
        H["H5"] = {"status": st, "false_negatives": fn, "n_checked": len(ab), "candidate_reduction": round(red, 4)}
    # H6 tamper
    tp = os.path.join(results, "tamper.json")
    if os.path.exists(tp):
        t = json.load(open(tp))
        miss = sum(1 for r in t["mutations"] if not r["flagged"]); fa = sum(1 for r in t["rereads"] if r["flagged"])
        H["H6"] = {"status": "PASS" if (miss == 0 and fa == 0) else "KILL", "mutations_missed": miss, "mutations": len(t["mutations"]), "false_alarms": fa, "rereads": len(t["rereads"]),
                   "whitespace_only_flagged": sum(1 for r in t.get("whitespace_only", []) if r["flagged"]), "whitespace_only": len(t.get("whitespace_only", []))}
    # H7 determinism
    dp = os.path.join(results, "verdicts", "determinism.json")
    if os.path.exists(dp):
        det = json.load(open(dp)); bad = {k: sorted(set(v.values())) for k, v in det.items() if len(set(v.values())) > 1}
        H["H7"] = {"status": "PASS" if not bad else "KILL", "groups": len(det), "differing_groups": sorted(bad)}
    # H8 librarian lineage
    hp = os.path.join(results, "h8.json")
    if os.path.exists(hp):
        h = json.load(open(hp))
        if h["lineage_share"] < THRESH["H8_lineage_share_min"]:
            H["H8"] = {"status": "DROPPED", "why": "the profile does not support the inference (lineage under half of the time)", "lineage_share": h["lineage_share"]}
        else:
            red = 1 - h["wall_after_s"] / h["wall_before_s"]
            ex = slope([(p["frac"], p["time_s"]) for p in h.get("scaling", [])])
            if h["indegree_mismatches"] > 0 or red < THRESH["H8_reduction_kill"]:
                st = "KILL"
            elif h["wall_after_s"] <= THRESH["H8_wall_max_s"] and ex is not None and ex <= THRESH["H8_exponent_max"]:
                st = "PASS"
            else:
                st = "FAIL"
            H["H8"] = {"status": st, "lineage_share": h["lineage_share"], "indegree_mismatches": h["indegree_mismatches"], "wall_reduction": round(red, 3), "exponent": ex}
    # H9 speaker attribution (S against the expectation, and against the current lint)
    if "S" in systems and os.path.exists(os.path.join(results, "verdicts", "lint.E.jsonl")):
        s9 = {r["id"]: r["verdict"] for r in V("S", "E")}; l9 = {r["id"]: r["verdict"] for r in jl(os.path.join(results, "verdicts", "lint.E.jsonl"))}
        exp = {i: g["expect"] for (ss, i), g in gt.items() if ss == "E"}
        meets = lambda v, e: (v in CONFIDENT) if e == "CLEAN_OR_ANCHORED" else v == e
        wrong = [i for i in exp if not meets(s9.get(i), exp[i])]; differ = [i for i in exp if s9.get(i) != l9.get(i)]
        H["H9"] = {"status": "PASS" if (not wrong and not differ) else "KILL", "expectation_misses": len(wrong), "differs_from_current_lint": len(differ), "n": len(exp)}
    # scaling exponent (speed protocol)
    for x in ("B0", "S"):
        rows = T(x)
        fr = sorted({r["corpus_frac"] for r in rows})
        if len(fr) >= 3 and os.path.exists(os.path.join(results, "timings", "build.json")):
            build = json.load(open(os.path.join(results, "timings", "build.json"))).get(x, {})
            pts = [(f, float(build.get(str(f), 0)) + 300 * statistics.median([r["latency_s"] for r in rows if r["corpus_frac"] == f and r["phase"] == "warm"])) for f in fr]
            e = slope(pts)
            R.setdefault("scaling", {})[x] = {"exponent": e, "claim_linear_allowed": e is not None and e <= THRESH["SCALING_linear_max"]}
    # decisions, exactly as registered
    g = lambda k: H.get(k, {}).get("status")
    if all(g(k) for k in ("H1", "H2", "H3", "H4", "H7")):
        others = all(g(k) == "PASS" for k in ("H2", "H3", "H4", "H7"))
        l4 = "ADOPT" if g("H1") == "PASS" and others else "PARTIAL" if g("H1") == "WEAK" and others else "DROP" if "KILL" in (g(k) for k in ("H1", "H2", "H3", "H4", "H7")) else "NOT ADOPTED (no kill, a pass condition missed)"
    else:
        l4 = "UNDETERMINED (not all of H1, H2, H3, H4, H7 have results)"
    R["decisions"] = {"layer4_shingle_index": l4,
                      "layer5_bloom": ("ADOPT" if (g("H5") == "PASS" and l4 == "ADOPT") else "NOT ADOPTED" if g("H5") else "UNDETERMINED"),
                      "layer2_hash_verification": {"PASS": "SUPPORTED", "KILL": "NOT SUPPORTED"}.get(g("H6"), "UNDETERMINED"),
                      "librarian_lineage_change": {"PASS": "ADOPT", "FAIL": "NOT ADOPTED", "KILL": "LEAVE LIBRARIAN UNTOUCHED", "DROPPED": "HYPOTHESIS DROPPED"}.get(g("H8"), "UNDETERMINED"),
                      "speaker_attribution_unchanged": {"PASS": "SUPPORTED", "KILL": "NOT SUPPORTED"}.get(g("H9"), "UNDETERMINED")}
    return R


def render(R):
    print("systems with results:", ", ".join(R["systems_present"]) or "none")
    for k, v in sorted(R["hypotheses"].items()):
        body = {a: b for a, b in v.items() if a != "status"}
        print(f"{k:3} {v['status']:8} {json.dumps(body, default=str)[:230]}")
    if R["primary_safety"]:
        print(f"PRIMARY SAFETY (confident-wrong, S over A+B+D): {R['primary_safety']['status']} {json.dumps(R['primary_safety']['S_confident_wrong'])}")
    for k, v in R.get("scaling", {}).items():
        print(f"scaling {k}: exponent {v['exponent']} (linear claim allowed: {v['claim_linear_allowed']})")
    print("decisions:", json.dumps(R["decisions"], indent=1))


def self_test():
    """Synthetic data in a temp dir: every threshold is exercised on both sides (fail-on-bad, pass-on-good)."""
    ok = []
    def check(name, cond):
        ok.append((name, cond)); print(("PASS " if cond else "FAIL ") + name)
    ds = tempfile.mkdtemp(); rs = tempfile.mkdtemp()
    for d in ("verdicts", "timings", "prefilter"):
        os.makedirs(os.path.join(rs, d))
    W = lambda p, rows: open(p, "w").write("".join(json.dumps(r) + "\n" for r in rows))
    W(os.path.join(ds, "set_A.jsonl"), [{"id": f"A{i}", "file": f"f{i % 5}.md"} for i in range(200)])
    W(os.path.join(ds, "set_B.jsonl"), [{"id": f"B{i}", "file": f"f{i % 5}.md", "kind": ["B1", "B2", "B3"][i % 3]} for i in range(60)])
    W(os.path.join(ds, "set_C.jsonl"), [{"id": f"C{i}", "file": f"f{i % 5}.md", "valid": i < 8} for i in range(10)])
    W(os.path.join(ds, "set_D.jsonl"), [{"id": f"D{i}", "file": f"h{i}.md"} for i in range(100)])
    W(os.path.join(ds, "set_E.jsonl"), [{"id": "E1", "expect": "CLEAN_OR_ANCHORED"}, {"id": "E1~swapped", "expect": "CONTAMINATED"}])
    def vrow(s, n, wrong=0, unsourced=0, neg=False):
        rows = []
        for i in range(n):
            if i < wrong:
                rows.append({"id": f"{s}{i}", "verdict": "CLEAN", "source_file": "zzz.md"})
            elif i < wrong + unsourced:
                rows.append({"id": f"{s}{i}", "verdict": "UNSOURCED", "source_file": None})
            else:
                rows.append({"id": f"{s}{i}", "verdict": "CLEAN", "source_file": None if neg else f"f{i % 5}.md"})
        return rows
    def setup(S_wrong=0, B0_wrong=0, s_med=0.001, b0_med=0.05, d_neg_conf=0):
        for sysn, w, med in (("S", S_wrong, s_med), ("B0", B0_wrong, b0_med), ("B1", 0, 0.01)):
            W(os.path.join(rs, "verdicts", f"{sysn}.A.jsonl"), vrow("A", 200, wrong=w))
            W(os.path.join(rs, "verdicts", f"{sysn}.B.jsonl"), vrow("B", 60))
            W(os.path.join(rs, "verdicts", f"{sysn}.C.jsonl"), vrow("C", 10, unsourced=10))
            W(os.path.join(rs, "verdicts", f"{sysn}.D.jsonl"), [{"id": f"D{i}", "verdict": "CLEAN" if i < (d_neg_conf if sysn == "S" else 0) else "UNSOURCED", "source_file": "x.md" if i < (d_neg_conf if sysn == "S" else 0) else None} for i in range(100)])
            W(os.path.join(rs, "timings", f"{sysn}.A.jsonl"), [{"id": f"A{i}", "phase": "warm", "run": 1, "corpus_frac": 1.0, "latency_s": med} for i in range(200)])
    setup()
    R = score(rs, ds, verify=False); H = R["hypotheses"]
    check("good input: H1 PASS at a 50x speedup, H2 PASS, H3 PASS, H4 PASS, primary safety PASS", H["H1"]["status"] == "PASS" and H["H2"]["status"] == "PASS" and H["H3"]["status"] == "PASS" and H["H4"]["status"] == "PASS" and R["primary_safety"]["status"] == "PASS")
    setup(s_med=0.012); R = score(rs, ds, verify=False)
    check("H1 WEAK between 3x and 10x (about 4.2x)", R["hypotheses"]["H1"]["status"] == "WEAK")
    setup(s_med=0.03); R = score(rs, ds, verify=False)
    check("H1 KILL under 3x (about 1.7x)", R["hypotheses"]["H1"]["status"] == "KILL")
    setup(S_wrong=1); R = score(rs, ds, verify=False)
    check("H2 FAIL (not a kill) at 99.5 percent because it is below B1's 100 percent; safety WARN (0.3 percent but above B0's 0 wrong)", R["hypotheses"]["H2"]["status"] == "FAIL" and R["primary_safety"]["status"] == "WARN")
    setup(S_wrong=1, B0_wrong=1); R = score(rs, ds, verify=False)
    check("primary safety PASS when S has 1 confident-wrong of 360 (0.3 percent) and B0 has the same", R["primary_safety"]["status"] == "PASS")
    setup(S_wrong=4); R = score(rs, ds, verify=False)
    check("H2 FAIL at 98 percent (between the 97 kill and 99 pass lines)", R["hypotheses"]["H2"]["status"] == "FAIL")
    setup(S_wrong=8); R = score(rs, ds, verify=False)
    check("H2 KILL at 96 percent and primary safety KILL (8 of 360 is over the 1 percent line)", R["hypotheses"]["H2"]["status"] == "KILL" and R["primary_safety"]["status"] == "KILL")
    setup(d_neg_conf=3); R = score(rs, ds, verify=False)
    check("H4 KILL when 3 percent of negatives get a confident source", R["hypotheses"]["H4"]["status"] == "KILL")
    setup(d_neg_conf=1); R = score(rs, ds, verify=False)
    check("H4 PASS at exactly 1 percent of negatives", R["hypotheses"]["H4"]["status"] == "PASS")
    W(os.path.join(rs, "verdicts", "S.C.jsonl"), [{"id": "C0", "verdict": "ANCHORED", "source_file": "zzz.md"}] + vrow("C", 10, unsourced=10)[1:])
    R = score(rs, ds, verify=False)
    check("H4 KILL on a single confident-wrong source on Set C", R["hypotheses"]["H4"]["status"] == "KILL")
    setup()
    W(os.path.join(rs, "prefilter", "S_Bloom.jsonl"), [{"id": f"A{i}", "set": "A", "candidate_files": 10, "total_files": 172, "true_file_kept": True} for i in range(50)])
    R = score(rs, ds, verify=False); check("H5 PASS: no false negatives and 94 percent removed", R["hypotheses"]["H5"]["status"] == "PASS")
    W(os.path.join(rs, "prefilter", "S_Bloom.jsonl"), [{"id": "A1", "set": "A", "candidate_files": 10, "total_files": 172, "true_file_kept": False}])
    R = score(rs, ds, verify=False); check("H5 KILL on one false negative", R["hypotheses"]["H5"]["status"] == "KILL")
    json.dump({"mutations": [{"file": "a", "flagged": True}] * 100, "whitespace_only": [{"file": "b", "flagged": True}] * 20, "rereads": [{"file": "c", "flagged": False}] * 100}, open(os.path.join(rs, "tamper.json"), "w"))
    R = score(rs, ds, verify=False); check("H6 PASS: 100 of 100 flagged, 0 of 100 false alarms", R["hypotheses"]["H6"]["status"] == "PASS")
    json.dump({"mutations": [{"file": "a", "flagged": True}] * 99 + [{"file": "a", "flagged": False}], "rereads": []}, open(os.path.join(rs, "tamper.json"), "w"))
    R = score(rs, ds, verify=False); check("H6 KILL on a single missed mutation", R["hypotheses"]["H6"]["status"] == "KILL")
    json.dump({"S.A": {"seed1.rep1": "aa", "seed2.rep1": "aa"}}, open(os.path.join(rs, "verdicts", "determinism.json"), "w"))
    R = score(rs, ds, verify=False); check("H7 PASS on identical hashes", R["hypotheses"]["H7"]["status"] == "PASS")
    json.dump({"S.A": {"seed1.rep1": "aa", "seed2.rep1": "ab"}}, open(os.path.join(rs, "verdicts", "determinism.json"), "w"))
    R = score(rs, ds, verify=False); check("H7 KILL on one differing hash", R["hypotheses"]["H7"]["status"] == "KILL")
    sc = [{"frac": 0.25, "time_s": 1.0}, {"frac": 0.5, "time_s": 2.0}, {"frac": 1.0, "time_s": 4.1}]
    json.dump({"lineage_share": 0.6, "indegree_mismatches": 0, "wall_before_s": 5.3, "wall_after_s": 3.0, "scaling": sc}, open(os.path.join(rs, "h8.json"), "w"))
    R = score(rs, ds, verify=False); check("H8 PASS: lineage 60 percent of time, no mismatch, 3.0 s, exponent about 1", R["hypotheses"]["H8"]["status"] == "PASS")
    json.dump({"lineage_share": 0.4, "indegree_mismatches": 0, "wall_before_s": 5.3, "wall_after_s": 3.0, "scaling": sc}, open(os.path.join(rs, "h8.json"), "w"))
    R = score(rs, ds, verify=False); check("H8 DROPPED when the profile falsifies the inference (40 percent)", R["hypotheses"]["H8"]["status"] == "DROPPED")
    json.dump({"lineage_share": 0.6, "indegree_mismatches": 1, "wall_before_s": 5.3, "wall_after_s": 3.0, "scaling": sc}, open(os.path.join(rs, "h8.json"), "w"))
    R = score(rs, ds, verify=False); check("H8 KILL on a single in-degree mismatch", R["hypotheses"]["H8"]["status"] == "KILL")
    W(os.path.join(rs, "verdicts", "lint.E.jsonl"), [{"id": "E1", "verdict": "CLEAN"}, {"id": "E1~swapped", "verdict": "CONTAMINATED"}])
    W(os.path.join(rs, "verdicts", "S.E.jsonl"), [{"id": "E1", "verdict": "ANCHORED"}, {"id": "E1~swapped", "verdict": "CONTAMINATED"}])
    R = score(rs, ds, verify=False); check("H9 KILL when S differs from the current lint even though it meets the expectation", R["hypotheses"]["H9"]["status"] == "KILL")
    W(os.path.join(rs, "verdicts", "S.E.jsonl"), [{"id": "E1", "verdict": "CLEAN"}, {"id": "E1~swapped", "verdict": "CONTAMINATED"}])
    R = score(rs, ds, verify=False); check("H9 PASS when S matches the lint and the expectation", R["hypotheses"]["H9"]["status"] == "PASS")
    setup(); os.remove(os.path.join(rs, "verdicts", "S.E.jsonl")); R = score(rs, ds, verify=False)
    check("decisions stay UNDETERMINED until H1, H2, H3, H4 and H7 all exist", R["decisions"]["layer4_shingle_index"].startswith("UNDETERMINED") or R["decisions"]["layer4_shingle_index"] in ("ADOPT", "PARTIAL", "DROP"))
    check("wilson interval is sane", wilson(50, 100)[0] < 0.5 < wilson(50, 100)[1] and wilson(0, 0) == (None, None))
    check("scaling slope recovers exponent 1 and 2", abs(slope([(0.25, 1), (0.5, 2), (1, 4)]) - 1.0) < 0.01 and abs(slope([(0.25, 1), (0.5, 4), (1, 16)]) - 2.0) < 0.01)
    # frozen-dataset guard: a modified file must stop scoring
    try:
        bad = tempfile.mkdtemp(); open(os.path.join(bad, "set_A.jsonl"), "w").write("x\n"); open(os.path.join(bad, "SHA256SUMS"), "w").write("0" * 64 + "  set_A.jsonl\n")
        verify_dataset(bad); stopped = False
    except SystemExit:
        stopped = True
    check("a dataset file that does not match SHA256SUMS stops the scorer", stopped)
    n = sum(1 for _, c in ok if c)
    print(f"self-test: {n}/{len(ok)} pass")
    return 0 if n == len(ok) else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results"); ap.add_argument("--json"); ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.results:
        verify_dataset(); print("frozen datasets match SHA256SUMS; pass --results DIR to score."); return 0
    R = score(a.results)
    render(R)
    if a.json:
        json.dump(R, open(a.json, "w"), indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
