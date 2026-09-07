#!/usr/bin/env python3
"""
review_pairs.py — CLI reviewer for the audit benchmark pair store.

Loads benchmark pairs from the JSONL store and prints side-by-side
LLM vs operator comparisons for human review.

Usage:
    python review_pairs.py                        # last 20 pairs
    python review_pairs.py --limit 10             # last 10 pairs
    python review_pairs.py --trace-id t2          # single trace
    python review_pairs.py --operator SAGE         # single operator
    python review_pairs.py --fidelity somatic=default axioms=default
    python review_pairs.py --before 2026-08-27T00:00:00Z
    python review_pairs.py --stats                # store stats only

Requires AUDIT_BENCH_FILE (default: benchmark_pairs.jsonl in same dir).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
_BENCH_FILE = Path(__file__).parent / "benchmark_pairs.jsonl"


def load_pairs(
    trace_id: str | None = None,
    operator: str | None = None,
    fidelity_somatic: str | None = None,
    fidelity_axioms: str | None = None,
    before: str | None = None,
    after: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict]:
    """Thin wrapper around persistence.loadBenchmarkPairs for CLI use."""
    sys.path.insert(0, str(_HERE))
    from persistence import loadBenchmarkPairs as _load

    return _load(
        trace_id=trace_id,
        operator=operator,
        fidelity_somatic=fidelity_somatic,
        fidelity_axioms=fidelity_axioms,
        before=before,
        after=after,
        limit=limit,
        offset=offset,
    )


def fmt_field(label: str, value: Any, max_len: int = 80) -> str:
    """Format a field for display, truncating long values."""
    if value is None:
        return f"{label}: null"
    s = str(value)
    if len(s) <= max_len:
        return f"{label}: {s}"
    return f"{label}: {s[:max_len]}…[{len(s) - max_len} more chars]"


def print_pair(pair: dict, index: int) -> None:
    """Print one benchmark pair as a side-by-side review card."""
    tid = pair["traceId"]
    op = pair["operator"]
    ts = pair.get("timestamp", "")
    fidelity = (pair.get("auditResult") or {}).get("fidelity") or {}
    result = pair.get("auditResult") or {}
    primitive = pair.get("primitives") or {}
    llm = pair.get("llmOutput") or {}

    print(f"\n{'═' * 70}")
    print(f"PAIR {index}: traceId={tid}  operator={op}  timestamp={ts}")
    print(f"  fidelity: somatic={fidelity.get('somatic','?')} · hci={fidelity.get('hci','?')} · axioms={fidelity.get('axioms','?')}")
    print(f"  auditResult.ok: {result.get('ok')}  latencyMs: {result.get('latencyMs')}")
    if result.get("failureReason"):
        print(f"  ⚠ failureReason: {result['failureReason']}")

    # Side-by-side: LLM signal vs operator output (varies by operator)
    print(f"\n  ── primitives (what was sent to the operator) ──")
    sig = primitive.get("signal") or {}
    print(f"    signal.label: {sig.get('label','?')}")
    print(f"    signal.phaseId: {sig.get('phaseId','?')}")
    print(f"    signal.signalProxy (12): {sig.get('signalProxy',[])}")
    print(f"    fated.direction: {primitive.get('fated',{}).get('direction','?')}")
    print(f"    axioms: {primitive.get('axioms',{})}")
    print(f"    somatic.source: {primitive.get('somatic',{}).get('source','?')}")
    print(f"    hci_score / hci_source: {primitive.get('hci_score')} / {primitive.get('hci_source','?')}")
    print(f"    pci_score: {primitive.get('pci_score')}")
    print(f"    irreversibility: {primitive.get('irreversibility')}")
    print(f"    signalClassification: {primitive.get('signalClassification','?')}")

    if llm:
        print(f"\n  ── llmOutput (what the LLM produced — sparse in test data) ──")
        if llm.get("coherence_pct") is not None:
            print(f"    coherence_pct: {llm.get('coherence_pct')}")
        if llm.get("nci_score") is not None:
            print(f"    nci_score: {llm.get('nci_score')}")
        if llm.get("true_north"):
            print(f"    true_north: {str(llm.get('true_north'))[:120]}")
        if llm.get("reasoning"):
            r = llm["reasoning"]
            if r.get("fated"):
                print(f"    reasoning.fated.direction: {str(r['fated'].get('direction',''))[:120]}")
            if r.get("court"):
                verdicts = [(c.get("name",""), c.get("verdict","")) for c in r["court"]]
                print(f"    reasoning.court verdicts: {verdicts}")
            if r.get("geometry"):
                print(f"    reasoning.geometry.macros_on: {r['geometry'].get('macros_on',[])}")
        if llm.get("meta"):
            print(f"    meta.macro_tags: {llm['meta'].get('macro_tags',[])}")

    print(f"\n  ── operator output ({op}) ──")
    out = result.get("output") or {}
    if op == "SAGE":
        print(f"    nci_score: {out.get('nci_score')}")
        print(f"    pci_score: {out.get('pci_score')}")
        print(f"    hci_score: {out.get('hci_score')}")
        print(f"    signal_classification: {out.get('signal_classification','?')}")
        print(f"    verdict: {out.get('verdict','?')}")
        print(f"    nci_grade: {out.get('nci_grade','?')}")
        axioms = out.get("axioms") or {}
        print(f"    axioms: {axioms}")
        somatic = out.get("somatic") or {}
        print(f"    somatic.witness_score: {somatic.get('witness_score')}")
    elif op == "LAB":
        print(f"    lab_threat_level: {out.get('lab_threat_level','?')}")
        print(f"    lab_recommendation: {out.get('lab_recommendation','?')}")
        loki = out.get("loki") or {}
        if loki:
            print(f"    loki.challenge_statement: {str(loki.get('challenge_statement',''))[:160]}")
            print(f"    loki.loki_confidence: {loki.get('loki_confidence')}")
            print(f"    loki.threat_score: {loki.get('threat_score')}")
            print(f"    loki.can_be_dismissed: {loki.get('can_be_dismissed')}")
        bayesian = out.get("bayesian") or {}
        if bayesian:
            print(f"    bayesian.prior_confidence: {bayesian.get('prior_confidence')}")
            print(f"    bayesian.posterior_confidence: {bayesian.get('posterior_confidence')}")
            print(f"    bayesian.belief_shift: {bayesian.get('belief_shift')}")
            print(f"    bayesian.proceed_recommended: {bayesian.get('proceed_recommended')}")
        advisors = out.get("advisors") or []
        if advisors:
            print(f"    advisors ({len(advisors)}):")
            for a in advisors[:5]:
                print(f"      - {a.get('advisor_archetype','?')}: {a.get('stance','?')} (conf={a.get('confidence')})")
    elif op == "BAR":
        print(f"    bar_verdict: {out.get('bar_verdict','?')}")
        baseline = out.get("baseline") or {}
        print(f"    baseline.floor_nci: {baseline.get('floor_nci')}")
        print(f"    baseline.floor_is_acceptable: {baseline.get('floor_is_acceptable')}")
        print(f"    baseline.floor_confidence: {baseline.get('floor_confidence')}")
        asym = out.get("asymmetry") or {}
        print(f"    asymmetry.asymmetry_ratio: {asym.get('asymmetry_ratio')}")
        print(f"    asymmetry.bet_quality: {asym.get('bet_quality','?')}")
        print(f"    asymmetry.kelly_fraction: {asym.get('kelly_fraction')}")
        ruin = out.get("ruin") or {}
        print(f"    ruin.ruin_detected: {ruin.get('ruin_detected')}")
        print(f"    ruin.ruin_probability: {ruin.get('ruin_probability')}")
        print(f"    ruin.irreversibility_score: {ruin.get('irreversibility_score')}")
    elif op == "KINTSUGI":
        print(f"    pathogens count: {len(out.get('pathogens') or [])}")
        print(f"    is_healthy: {out.get('is_healthy')}")
        print(f"    repaired: {out.get('repaired')}")
        print(f"    kintsugi_repair_count: {out.get('kintsugi_repair_count')}")
        print(f"    kintsugi_trust_discount: {out.get('kintsugi_trust_discount')}")
        print(f"    nci_score: {out.get('nci_score')} (pre-repair: {out.get('nci_pre_repair')})")
        seams = out.get("golden_seams") or []
        if seams:
            print(f"    golden_seams ({len(seams)}):")
            for s in seams[:5]:
                print(f"      - {s.get('seam_type','?')}: discount={s.get('trust_discount')} · {str(s.get('description',''))[:80]}")
    else:
        print(f"    output: {json.dumps(out, indent=2)[:800]}")


def print_stats() -> None:
    """Print store statistics."""
    sys.path.insert(0, str(_HERE))
    from persistence import audit_store_stats

    stats = audit_store_stats()
    print(f"benchmark_pairs.jsonl: {stats['bench_rows']} rows")
    print(f"audit_traces.jsonl:    {stats['trace_rows']} rows")
    print()
    print("by operator (benchmark):")
    for op, count in sorted(stats["bench_by_operator"].items()):
        print(f"  {op}: {count}")
    print()
    print("by fidelity (benchmark):")
    for key, count in sorted(stats["bench_by_fidelity"].items(), key=lambda x: -x[1]):
        print(f"  {key}: {count}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CLI reviewer for the audit benchmark pair store",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python review_pairs.py                          last 20 pairs
  python review_pairs.py --limit 10               last 10 pairs
  python review_pairs.py --trace-id t2            single trace
  python review_pairs.py --operator SAGE           single operator
  python review_pairs.py --fidelity somatic=default axioms=default
  python review_pairs.py --before 2026-08-27T00:00:00Z
  python review_pairs.py --stats                  store stats only
        """,
    )
    parser.add_argument("--limit", type=int, default=20, help="max pairs to show (default 20)")
    parser.add_argument("--trace-id", type=str, default=None, help="filter by traceId")
    parser.add_argument("--operator", type=str, default=None, help="filter by operator")
    parser.add_argument("--fidelity", type=str, action="append", default=[],
                        help="fidelity filter: key=value (e.g. somatic=default). Repeatable.")
    parser.add_argument("--before", type=str, default=None, help="ISO timestamp upper bound")
    parser.add_argument("--after", type=str, default=None, help="ISO timestamp lower bound")
    parser.add_argument("--stats", action="store_true", help="print store stats only")
    parser.add_argument("--offset", type=int, default=0, help="pagination offset (default 0)")

    args = parser.parse_args()

    fidelity_filters: dict[str, str] = {}
    for f in args.fidelity:
        if "=" not in f:
            print(f"⚠ skipping malformed fidelity filter: {f}", file=sys.stderr)
            continue
        k, v = f.split("=", 1)
        fidelity_filters[k] = v

    if args.stats:
        print_stats()
        return

    pairs = load_pairs(
        trace_id=args.trace_id,
        operator=args.operator,
        fidelity_somatic=fidelity_filters.get("somatic"),
        fidelity_axioms=fidelity_filters.get("axioms"),
        before=args.before,
        after=args.after,
        limit=args.limit,
        offset=args.offset,
    )

    if not pairs:
        print("no pairs found for the given filters")
        return

    print(f"showing {len(pairs)} pair(s)")
    for i, pair in enumerate(pairs, 1):
        print_pair(pair, i)


if __name__ == "__main__":
    main()
