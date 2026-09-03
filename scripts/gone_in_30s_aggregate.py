#!/usr/bin/env python3
"""gone_in_30s_aggregate — score the pre-registered corpus test.

Reads _STATE/gone-in-30s/batch-*.jsonl (one JSON line per call, coded by a reader against
_STATE/2026-09-03-gone-in-30s-preregistration.md), applies the pre-registered decision rule, and
emits a markdown report with every hit line verbatim. Stdlib only; no judgment here, only counting.

Usage: python3 scripts/gone_in_30s_aggregate.py [--out _STATE/2026-09-03-gone-in-30s-report.md]
"""
import glob, json, sys, collections, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN = os.path.join(ROOT, "_STATE", "gone-in-30s")
OUT = os.path.join(ROOT, "_STATE", "2026-09-03-gone-in-30s-report.md")
TAGS = {"C1": "legibility complaint", "C2": "verdict-first demand", "C3": "depth-on-pull",
        "C4": "receptivity-as-state", "C5": "mirror preference", "M1": "consumed depth unprompted",
        "M2": "asked for more detail up front"}


def main():
    out = OUT
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
    rows = []
    for f in sorted(glob.glob(os.path.join(IN, "batch-*.jsonl"))) + sorted(glob.glob(os.path.join(IN, "retry-*.jsonl"))):
        for line in open(f, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"skip bad line in {f}: {e}", file=sys.stderr)
    seen = {}
    for r in rows:
        seen[r["id"]] = r  # last write wins on duplicates
    rows = list(seen.values())
    ok = [r for r in rows if r.get("transcript_ok", True)]
    failed = [r for r in rows if not r.get("transcript_ok", True)]
    in_scope = [r for r in ok if r.get("in_scope")]
    hit_calls = [r for r in in_scope if r.get("hits")]
    unprompted_calls = [r for r in in_scope if any(not h.get("prompted") for h in r.get("hits", []))]
    oos_hits = [r for r in ok if not r.get("in_scope") and r.get("hits")]
    miss_calls = [r for r in in_scope if r.get("misses")]
    tagc = collections.Counter(h["tag"] for r in in_scope for h in r.get("hits", []))
    missc = collections.Counter(m["tag"] for r in in_scope for m in r.get("misses", []))
    rate = len(hit_calls) / len(in_scope) if in_scope else 0.0
    verdict = "H1 SUPPORTED (>= 0.50)" if rate >= 0.5 else ("H0 (< 0.25)" if rate < 0.25 else "INCONCLUSIVE (0.25 to 0.50)")

    L = []
    a = L.append
    a("# Does 'gone in 30 seconds' hold across all calls? Corpus test, scored")
    a("")
    a("Rule pre-registered in `_STATE/2026-09-03-gone-in-30s-preregistration.md` before reading. Counting only; every hit below is a verbatim counterpart line.")
    a("")
    a("| Measure | Value |")
    a("|---|---|")
    a(f"| Calls coded | {len(rows)} |")
    a(f"| Transcript fetch failed | {len(failed)} |")
    a(f"| In scope (artifact or ARCS explained) | {len(in_scope)} |")
    a(f"| In-scope calls with >= 1 hit | {len(hit_calls)} |")
    a(f"| Hit rate (hit calls / in scope) | {rate:.2f} |")
    a(f"| In-scope calls with an UNPROMPTED hit | {len(unprompted_calls)} |")
    a(f"| In-scope calls with a miss (M1/M2) | {len(miss_calls)} |")
    a(f"| Out-of-scope calls that still produced a hit | {len(oos_hits)} |")
    a(f"| **Pre-registered verdict** | **{verdict}** |")
    a("")
    a("## Tag distribution (in scope)")
    a("")
    a("| Tag | Meaning | Count |")
    a("|---|---|---|")
    for t in ["C1", "C2", "C3", "C4", "C5"]:
        a(f"| {t} | {TAGS[t]} | {tagc.get(t, 0)} |")
    for t in ["M1", "M2"]:
        a(f"| {t} | {TAGS[t]} | {missc.get(t, 0)} |")
    a("")
    a("## Every hit, verbatim (in scope)")
    a("")
    for r in sorted(in_scope, key=lambda r: r.get("date", "")):
        if not r.get("hits"):
            continue
        a(f"### {r.get('date','')} · {r.get('title','')}")
        if r.get("artifact_presented"):
            a(f"_Artifact: {r['artifact_presented']}_")
        for h in r["hits"]:
            p = "prompted" if h.get("prompted") else "unprompted"
            a(f"- **{h['tag']}** ({p}): \"{h['quote']}\"")
        for m in r.get("misses", []):
            a(f"- MISS **{m['tag']}**: \"{m['quote']}\"")
        a("")
    a("## In-scope calls with NO hit")
    a("")
    for r in sorted(in_scope, key=lambda r: r.get("date", "")):
        if r.get("hits"):
            continue
        ms = "; ".join(f"{m['tag']}: \"{m['quote']}\"" for m in r.get("misses", []))
        a(f"- {r.get('date','')} · {r.get('title','')} · {r.get('artifact_presented') or ''} {('· ' + ms) if ms else ''}")
    a("")
    a("## Out-of-scope calls that still produced a hit (observations, not in denominator)")
    a("")
    for r in sorted(oos_hits, key=lambda r: r.get("date", "")):
        for h in r["hits"]:
            a(f"- {r.get('date','')} · {r.get('title','')} · **{h['tag']}**: \"{h['quote']}\"")
    a("")
    a("## Zach-side lines (the mechanism, said about his own material)")
    a("")
    for r in sorted(ok, key=lambda r: r.get("date", "")):
        for z in r.get("zside", []) or []:
            a(f"- {r.get('date','')} · {r.get('title','')}: \"{z}\"")
    a("")
    if failed:
        a("## Fetch failures")
        a("")
        for r in failed:
            a(f"- {r.get('date','')} · {r.get('title','')} · {r.get('id','')}")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print(f"gone_in_30s: {len(rows)} coded · {len(in_scope)} in scope · {len(hit_calls)} hit · rate {rate:.2f} · {verdict} -> {os.path.relpath(out, ROOT)}")


if __name__ == "__main__":
    main()
