#!/usr/bin/env python3
"""
echo_ridgeline_feed.py — feed ridgeline-shaped texts to the Orthogonal Echo Detector and run the
DITHER test: an echo that survives small perturbations of the input is a candidate; one that
vanishes was aliasing (moiré artifact). This is RC-OPS-001 graduation criterion 3 run as sonar.

Inputs (domain -> text):
  a. unfold stone drafts   _INBOX/unfold-<date>-<domain>.md   (ridgeline-shaped; today's only source)
  b. fold-receipt ridgelines in _QUEUE/induced-backlog.jsonl  (field `ridgeline`; none exist yet,
     the field was added 2026-09-27 — the feed picks them up automatically when they appear)

Honesty notes:
  - The detector's default signature is keyword matching against a fixed pattern library and its
    default orthogonality is a function of the domain NAMES. `--signature embedding` swaps in the
    pair from operators/arcs_echo_embedding.py (text embeddings via the same local model
    operators/arcs_api.py serves at /api/embed; orthogonality = 1 - cosine of the domain TEXT
    vectors). The feed measures; it does not tune either detector on the stones.
  - `--compare PATH` runs keyword then embedding on the same texts with the same seed and writes
    one before/after JSON (RC-OPS-001 criterion 2 evidence; criteria_status stays untouched).
  - "Survival under dither" is a stability proxy, not a truth test. K-blind hindsight confirmation
    (criterion 3 proper) still needs a human to say an echo was real.
  - FP proxy: matches that fire on SCRAMBLED controls (the same words, shuffled across domains)
    cannot be real structure; their rate is reported as the adversarial false-positive proxy.
  - TEMPLATE control (added 2026-09-27, pre-registered before its first run): the unfold stones share
    boilerplate lines verbatim (headings, the "every path below was checked" line). A match whose
    evidence is a line present in >= 2 domains is an echo of the TEMPLATE, not of domain motion, and
    the scramble control cannot see it (the line is real prose, just repeated). The control drops
    every line that appears verbatim in >= 2 domains and re-runs; `real_echoes_after_template_control`
    is what survives. This is the number a human should read before calling anything an echo.
  - Nothing is written to operators/RC-REGISTRY.json. criteria_status is judgment.

Output: _INBOX/echo-ridgeline-<date>.json + .md (gitignored derived cache) and a stdout summary.
Usage:
  operators/.venv/bin/python scripts/echo_ridgeline_feed.py [--dithers 12] [--keep 0.85] [--k 8] [--signature keyword|embedding]
  operators/.venv/bin/python scripts/echo_ridgeline_feed.py --compare _STATE/<date>-echo-signature-before-after.json
  operators/.venv/bin/python scripts/echo_ridgeline_feed.py --self-test
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "operators"))


def gather(today: str) -> dict[str, str]:
    texts: dict[str, str] = {}
    for f in sorted(glob.glob(str(ROOT / "_INBOX" / f"unfold-*-*.md"))):
        p = Path(f); dom = p.stem.split("-", 4)[-1]
        if dom and not dom.startswith("unfold") and not dom.isdigit():   # skip the bench summary unfold-<date>.md
            texts[f"stone:{dom}"] = p.read_text(encoding="utf-8", errors="replace")
    bl = ROOT / "_QUEUE" / "induced-backlog.jsonl"
    if bl.exists():
        for l in bl.read_text(encoding="utf-8").splitlines():
            if not l.strip():
                continue
            r = json.loads(l)
            rl = r.get("ridgeline")
            if rl:
                for chip in rl.get("chips", []):
                    texts[f"ridgeline:{chip.get('domain', r['id'])}"] = json.dumps(chip)
    return texts


def dither(text: str, keep: float, rng: random.Random) -> str:
    lines = [l for l in text.splitlines() if l.strip()]
    rng.shuffle(lines)
    k = max(2, int(len(lines) * keep))
    return "\n".join(lines[:k])


def scramble(texts: dict[str, str], rng: random.Random) -> dict[str, str]:
    """Adversarial control: pool every word across domains, deal them back at random.
    Any echo the detector finds here is structure it invented."""
    words = [w for t in texts.values() for w in t.split()]
    rng.shuffle(words)
    out, i = {}, 0
    for d, t in texts.items():
        n = len(t.split()); out[d] = " ".join(words[i:i + n]); i += n
    return out


def template_control(texts: dict[str, str]) -> tuple[dict[str, str], int]:
    """Drop every line that appears verbatim (stripped) in >= 2 domains. Returns (texts, n_dropped)."""
    from collections import Counter
    cnt = Counter(l.strip() for t in texts.values() for l in set(t.splitlines()) if l.strip())
    shared = {l for l, c in cnt.items() if c >= 2}
    out = {d: "\n".join(l for l in t.splitlines() if l.strip() not in shared) for d, t in texts.items()}
    return out, len(shared)


def key(m) -> tuple:
    return (m.domain_a, m.domain_b, m.pattern_name)



def make_detector(signature: str):
    from arcs_inchworm_echo import OrthogonalEchoDetector
    if signature == "keyword":
        return OrthogonalEchoDetector(), "OrthogonalEchoDetector defaults (keyword signature, name-based orthogonality)"
    if signature == "embedding":
        from arcs_echo_embedding import EMBED_MODEL_NAME, KEYWORD_TAU, build_embedding_detector
        return build_embedding_detector(), f"arcs_echo_embedding (segment embeddings via {EMBED_MODEL_NAME}, keyword_tau={KEYWORD_TAU}; orthogonality = 1 - cosine of domain text vectors)"
    raise SystemExit(f"unknown --signature {signature!r}")


def run(dithers: int, keep: float, k: int, seed: int = 27, signature: str = "keyword", write: bool = True) -> dict:
    today = dt.date.today().isoformat()
    texts = gather(today)
    det, det_label = make_detector(signature)
    rng = random.Random(seed)
    if len(texts) < 2:
        return {"date": today, "domains": list(texts), "signature": signature, "note": "fewer than 2 ridgeline-shaped texts; nothing to echo", "baseline": [], "survivors": [], "aliasing": [], "fp_proxy": None}
    base = det.run(texts)
    baseline = {key(m): m for m in base.matches}
    # evidence segments (embedding signature only): rebuild each signature once, read keyword -> segment
    seg_of: dict = {}
    echo = getattr(det, "_echo", None)
    if echo is not None and base.matches:
        for dom, t in texts.items():
            sig = echo.signature(dom, t)
            seg_of[dom] = {k: v[1] for k, v in getattr(sig, "keyword_evidence", {}).items()}
    counts: dict[tuple, int] = defaultdict(int)
    for _ in range(dithers):
        d = det.run({dom: dither(t, keep, rng) for dom, t in texts.items()})
        for m in d.matches:
            counts[key(m)] += 1
    survivors = [{"domains": [a, b], "pattern": p, "similarity": round(baseline[(a, b, p)].similarity, 3) if (a, b, p) in baseline else None,
                  "survived": f"{c}/{dithers}", "insight": baseline[(a, b, p)].named_insight if (a, b, p) in baseline else None}
                 for (a, b, p), c in counts.items() if c >= k]
    aliasing = [{"domains": [a, b], "pattern": p, "survived": f"{counts.get((a, b, p), 0)}/{dithers}"} for (a, b, p) in baseline if counts.get((a, b, p), 0) < k]
    # adversarial FP proxy: how many of the baseline pattern-firings also fire on scrambled text
    tc_texts, tc_dropped = template_control(texts)
    tc = det.run(tc_texts)
    fp_hits, fp_runs, fp_per_run = 0, 5, []
    for _ in range(fp_runs):
        s = det.run(scramble(texts, rng))
        fp_hits += len(s.matches); fp_per_run.append(len(s.matches))
    # NB: with 0 baseline matches the denominator floors at 1, so the proxy degenerates to
    # hits/runs (0.8 on 2026-09-27 = 4 scrambled hits in 5 runs against 0 real). The raw counts
    # are reported alongside so before/after is comparable even when the baseline is empty.
    fp_proxy = round(fp_hits / max(1, fp_runs * max(1, len(base.matches))), 3)
    result = {"date": today, "domains": list(texts), "signature": signature, "detector": det_label,
              "params": {"dithers": dithers, "keep": keep, "k": k, "seed": seed},
              "baseline_matches": len(base.matches), "baseline_status": str(base.status),
              "baseline": [{"domains": [m.domain_a, m.domain_b], "pattern": m.pattern_name, "similarity": round(m.similarity, 3),
                            "evidence_a": m.evidence_a[:6], "evidence_b": m.evidence_b[:6],
                            "segments_a": [seg_of.get(m.domain_a, {}).get(k, "")[:160] for k in m.evidence_a[:6]],
                            "segments_b": [seg_of.get(m.domain_b, {}).get(k, "")[:160] for k in m.evidence_b[:6]]} for m in base.matches],
              "template_control": {"shared_lines_dropped": tc_dropped, "matches": len(tc.matches),
                                   "patterns": sorted({m.pattern_name for m in tc.matches}),
                                   "pairs": [[m.domain_a, m.domain_b, m.pattern_name, round(m.similarity, 3)] for m in tc.matches]},
              "real_echoes_after_template_control": len(tc.matches),
              "survivors": sorted(survivors, key=lambda s: -(s["similarity"] or 0)), "aliasing": aliasing,
              "fp_proxy": fp_proxy, "fp_scrambled_hits": fp_hits, "fp_scrambled_runs": fp_runs, "fp_scrambled_per_run": fp_per_run,
              "fp_proxy_defn": "matches on word-scrambled controls / (runs x max(1, baseline matches)); RC-OPS-001 criterion 2 wants adv-FP <= 0.10 at recall >= 0.80 on LABELED echoes, which this is not"}
    if not write:
        return result
    suffix = "" if signature == "keyword" else f"-{signature}"
    out = ROOT / "_INBOX" / f"echo-ridgeline-{today}{suffix}.json"
    out.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    md = [f"# Echo feed — {today} ({signature} signature)", "", f"domains: {', '.join(texts)}", f"baseline matches: {len(base.matches)} · survivors (>= {k}/{dithers} dithers): {len(survivors)} · aliasing: {len(aliasing)} · FP proxy on scrambled controls: {fp_proxy} ({fp_hits} hits / {fp_runs} runs)", ""]
    for s in result["survivors"]:
        md.append(f"- SURVIVES {s['survived']} · {s['pattern']} · {s['domains'][0]} ↔ {s['domains'][1]} · sim {s['similarity']}\n    {s['insight']}")
    for a in aliasing:
        md.append(f"- aliasing {a['survived']} · {a['pattern']} · {a['domains'][0]} ↔ {a['domains'][1]}")
    (ROOT / "_INBOX" / f"echo-ridgeline-{today}{suffix}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return result


def compare(out: Path, dithers: int, keep: float, k: int, seed: int) -> dict:
    """Before/after on the same texts, same seed: keyword (before) then embedding (after)."""
    before = run(dithers, keep, k, seed, "keyword", write=False)
    after = run(dithers, keep, k, seed, "embedding", write=False)
    def _n(r, key): return len(r.get(key) or [])
    fp_improved = (after.get("fp_proxy") is not None and before.get("fp_proxy") is not None
                   and after["fp_proxy"] < before["fp_proxy"])
    verdict = "fp-proxy-improved" if fp_improved else "no-improvement-recorded"
    real_after = after.get("real_echoes_after_template_control", 0)
    report = {"date": before["date"], "seed": seed, "params": {"dithers": dithers, "keep": keep, "k": k},
              "inputs": before["domains"],
              "before": before, "after": after,
              "delta": {"baseline_matches": _n(after, "baseline") - _n(before, "baseline"),
                        "survivors": _n(after, "survivors") - _n(before, "survivors"),
                        "fp_proxy": (None if before.get("fp_proxy") is None or after.get("fp_proxy") is None
                                     else round(after["fp_proxy"] - before["fp_proxy"], 3)),
                        "fp_scrambled_hits": after.get("fp_scrambled_hits", 0) - before.get("fp_scrambled_hits", 0),
                        "real_echoes_after_template_control": real_after - before.get("real_echoes_after_template_control", 0)},
              "fate": verdict,
              "jtbd": {"fp_proxy_below_keyword_baseline": bool(fp_improved),
                       "baseline_finds_real_echoes": bool(real_after > 0),
                       "note": "the row's JTBD has two halves; both are reported, the fate names only the mechanical one"},
              "note": "fate is the backlog row's own vocabulary (echo-detector-embedding-signature). This file is evidence for RC-OPS-001 criterion 2; criteria_status in operators/RC-REGISTRY.json is a human ruling and is not written here."}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def self_test() -> int:
    from arcs_inchworm_echo import OrthogonalEchoDetector
    det = OrthogonalEchoDetector()
    rng = random.Random(1)
    t = "a\nb\nc\nd\ne\nf\ng\nh\ni\nj"
    d = dither(t, 0.8, rng)
    fails = 0
    def check(label, cond, detail=""):
        nonlocal fails
        print(f"  {'PASS' if cond else 'FAIL'}  {label}  {detail}")
        fails += 0 if cond else 1
    check("dither keeps ~keep fraction of lines, shuffled", len(d.splitlines()) == 8 and set(d.splitlines()) <= set(t.splitlines()))
    s = scramble({"x": "one two three", "y": "four five six"}, rng)
    check("scramble preserves word counts per domain", len(s["x"].split()) == 3 and len(s["y"].split()) == 3, s)
    r = det.run({"only": "text"})
    check("detector on 1 domain returns NULL, not a match", str(r.status).endswith("NULL") and not r.matches, r.status)
    print(f"self-test: {'OK' if fails == 0 else f'{fails} FAIL'}")
    return 1 if fails else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dithers", type=int, default=12)
    ap.add_argument("--keep", type=float, default=0.85)
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--seed", type=int, default=27)
    ap.add_argument("--signature", choices=["keyword", "embedding"], default="keyword")
    ap.add_argument("--compare", metavar="OUT_JSON", help="run keyword then embedding on the same texts/seed; write one before/after report")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        raise SystemExit(self_test())
    if a.compare:
        rep = compare(Path(a.compare), a.dithers, a.keep, a.k, a.seed)
        for tag in ("before", "after"):
            r = rep[tag]
            print(f"{tag:>6}: {r['signature']:<9} baseline={r.get('baseline_matches', 0)} survivors={len(r.get('survivors') or [])} fp_proxy={r.get('fp_proxy')} scrambled_hits={r.get('fp_scrambled_hits')}/{r.get('fp_scrambled_runs')} after_template_control={r.get('real_echoes_after_template_control')}")
        print(f" delta: {rep['delta']}\n  jtbd: {rep['jtbd']}\n  fate: {rep['fate']}\n  wrote {a.compare}")
        raise SystemExit(0)
    res = run(a.dithers, a.keep, a.k, a.seed, a.signature)
    print(json.dumps({k_: v for k_, v in res.items() if k_ not in ("survivors", "aliasing")}, indent=1))
    for s in res.get("survivors", []):
        print(f"  SURVIVES {s['survived']}  {s['pattern']:<28} {s['domains'][0]} ↔ {s['domains'][1]}  sim={s['similarity']}")
    for a_ in res.get("aliasing", []):
        print(f"  aliasing {a_['survived']}  {a_['pattern']:<28} {a_['domains'][0]} ↔ {a_['domains'][1]}")
