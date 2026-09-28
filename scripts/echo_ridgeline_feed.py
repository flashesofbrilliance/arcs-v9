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
    default orthogonality is a function of the domain NAMES. Nothing here upgrades that. The feed
    measures what the existing detector does on real inputs; it does not tune it.
  - "Survival under dither" is a stability proxy, not a truth test. K-blind hindsight confirmation
    (criterion 3 proper) still needs a human to say an echo was real.
  - FP proxy: matches that fire on SCRAMBLED controls (the same words, shuffled across domains)
    cannot be real structure; their rate is reported as the adversarial false-positive proxy.
  - Nothing is written to operators/RC-REGISTRY.json. criteria_status is judgment.

Output: _INBOX/echo-ridgeline-<date>.json + .md (gitignored derived cache) and a stdout summary.
Usage:
  operators/.venv/bin/python scripts/echo_ridgeline_feed.py [--dithers 12] [--keep 0.85] [--k 8]
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


def key(m) -> tuple:
    return (m.domain_a, m.domain_b, m.pattern_name)


def run(dithers: int, keep: float, k: int, seed: int = 27) -> dict:
    from arcs_inchworm_echo import OrthogonalEchoDetector
    today = dt.date.today().isoformat()
    texts = gather(today)
    det = OrthogonalEchoDetector()
    rng = random.Random(seed)
    if len(texts) < 2:
        return {"date": today, "domains": list(texts), "note": "fewer than 2 ridgeline-shaped texts; nothing to echo", "baseline": [], "survivors": [], "aliasing": [], "fp_proxy": None}
    base = det.run(texts)
    baseline = {key(m): m for m in base.matches}
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
    fp_hits, fp_runs = 0, 5
    for _ in range(fp_runs):
        s = det.run(scramble(texts, rng))
        fp_hits += len(s.matches)
    fp_proxy = round(fp_hits / max(1, fp_runs * max(1, len(base.matches))), 3)
    result = {"date": today, "domains": list(texts), "detector": "OrthogonalEchoDetector defaults (keyword signature, name-based orthogonality)",
              "params": {"dithers": dithers, "keep": keep, "k": k, "seed": seed},
              "baseline_matches": len(base.matches), "baseline_status": str(base.status),
              "survivors": sorted(survivors, key=lambda s: -(s["similarity"] or 0)), "aliasing": aliasing,
              "fp_proxy": fp_proxy, "fp_proxy_defn": "matches on word-scrambled controls / (runs x baseline matches); RC-OPS-001 criterion 2 wants adv-FP <= 0.10 at recall >= 0.80 on LABELED echoes, which this is not"}
    out = ROOT / "_INBOX" / f"echo-ridgeline-{today}.json"
    out.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    md = [f"# Echo feed — {today}", "", f"domains: {', '.join(texts)}", f"baseline matches: {len(base.matches)} · survivors (>= {k}/{dithers} dithers): {len(survivors)} · aliasing: {len(aliasing)} · FP proxy on scrambled controls: {fp_proxy}", ""]
    for s in result["survivors"]:
        md.append(f"- SURVIVES {s['survived']} · {s['pattern']} · {s['domains'][0]} ↔ {s['domains'][1]} · sim {s['similarity']}\n    {s['insight']}")
    for a in aliasing:
        md.append(f"- aliasing {a['survived']} · {a['pattern']} · {a['domains'][0]} ↔ {a['domains'][1]}")
    (ROOT / "_INBOX" / f"echo-ridgeline-{today}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return result


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
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        raise SystemExit(self_test())
    res = run(a.dithers, a.keep, a.k)
    print(json.dumps({k_: v for k_, v in res.items() if k_ not in ("survivors", "aliasing")}, indent=1))
    for s in res.get("survivors", []):
        print(f"  SURVIVES {s['survived']}  {s['pattern']:<28} {s['domains'][0]} ↔ {s['domains'][1]}  sim={s['similarity']}")
    for a_ in res.get("aliasing", []):
        print(f"  aliasing {a_['survived']}  {a_['pattern']:<28} {a_['domains'][0]} ↔ {a_['domains'][1]}")
