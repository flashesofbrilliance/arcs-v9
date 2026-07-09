#!/usr/bin/env python3
"""
receipt_lookup.py — the Detective query over the internal recoil ledger.

Scans runtime/recoil/generated/*.json (git-tracked, auth-gated via
/recoil/[reportId] — NOT the public/*.html taste pages) for prior calls
with a given counterpart, and prints a pattern digest: NCI trend, Y-gate
history, aggregated risk flags, and a plain-language conversion read.

This is the piece that was missing when the LaBella recoil ran on 2026-07-09:
nothing queried prior outcomes before spending call time. Run this BEFORE
scoping a pre-call brief, not after.

Usage:
    python3 scripts/receipt_lookup.py "<name or email fragment>"
    python3 scripts/receipt_lookup.py --all          # dump every counterpart on file

Stdlib only, per repo convention (see AGENTS.md — Foundation section).
"""
import json
import sys
import glob
import os

LEDGER_DIR = os.path.join(os.path.dirname(__file__), "..", "runtime", "recoil", "generated")


def load_all():
    records = []
    for path in sorted(glob.glob(os.path.join(LEDGER_DIR, "*.json"))):
        if os.path.basename(path) == "demo.json":
            continue
        try:
            with open(path) as f:
                data = json.load(f)
            data["_file"] = os.path.basename(path)
            records.append(data)
        except (json.JSONDecodeError, OSError):
            continue
    return records


def matches(record, query):
    q = query.lower()
    meta = record.get("meta", {})
    haystack = " ".join([
        meta.get("counterpart", ""),
        meta.get("counterpartRole", ""),
        meta.get("callTitle", ""),
    ]).lower()
    return q in haystack


def digest(records, query):
    hits = [r for r in load_all() if matches(r, query)]
    if not hits:
        print(f"NO PRIOR HISTORY for '{query}' — {len(records)} total records on file, none match.")
        print("This is a cold call in the ledger. No pattern signal available; proceed on stated context only.")
        return

    hits.sort(key=lambda r: r.get("meta", {}).get("callDate", ""))

    print(f"=== RECEIPT BANK — {len(hits)} prior call(s) for '{query}' ===\n")

    nci_trend = []
    ygate_trend = []
    all_risk_flags = []
    all_belief_shifts = []

    for r in hits:
        meta = r.get("meta", {})
        cover = r.get("cover", {})
        nci_trend.append((meta.get("callDate"), cover.get("nci")))
        ygate_trend.append((meta.get("callDate"), cover.get("yGate")))
        for rf in r.get("riskFlags", []):
            all_risk_flags.append((meta.get("callDate"), rf.get("severity"), rf.get("label")))
        print(f"[{meta.get('callDate')}] {meta.get('callTitle')} — {meta.get('counterpartRole', '')}")
        print(f"  Y: {cover.get('yGate')}/{cover.get('conviction')} · NCI {cover.get('nci')} · {cover.get('headline', '')}")
        print()

    print("--- NCI trend ---")
    print("  " + " -> ".join(f"{d}:{n}" for d, n in nci_trend))

    print("\n--- Y-gate trend ---")
    print("  " + " -> ".join(f"{d}:{y}" for d, y in ygate_trend))

    high_risks = [f for f in all_risk_flags if f[1] in ("HIGH", "HIGH_IF_TRIGGERED")]
    if high_risks:
        print("\n--- Unresolved HIGH risk flags across history ---")
        for d, sev, label in high_risks:
            print(f"  [{d}] {sev} — {label}")

    # crude conversion read: trending NCI direction + most recent Y-gate
    numeric_nci = [n for _, n in nci_trend if isinstance(n, (int, float))]
    trend_word = "flat"
    if len(numeric_nci) >= 2:
        trend_word = "declining" if numeric_nci[-1] < numeric_nci[0] else (
            "improving" if numeric_nci[-1] > numeric_nci[0] else "flat")
    latest_gate = ygate_trend[-1][1] if ygate_trend else "UNKNOWN"

    print(f"\n--- Read ---")
    print(f"  NCI trend: {trend_word} ({numeric_nci[0] if numeric_nci else '?'} -> {numeric_nci[-1] if numeric_nci else '?'})")
    print(f"  Latest Y-gate: {latest_gate}")
    if latest_gate in ("FORK", "RED") or trend_word == "declining":
        print("  ADVISORY: prior call(s) show a structural blocker or declining conviction.")
        print("  Check riskFlags above before allocating more call time — confirm the blocker has changed, don't assume it.")
    elif latest_gate == "GREEN":
        print("  ADVISORY: prior call trended positive — normal prep applies.")
    else:
        print("  ADVISORY: mixed/early signal — normal prep applies, watch for repeat of flagged risk items.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    if sys.argv[1] == "--all":
        recs = load_all()
        seen = set()
        for r in recs:
            c = r.get("meta", {}).get("counterpart")
            if c and c not in seen:
                seen.add(c)
                print(c)
        sys.exit(0)
    query = " ".join(sys.argv[1:])
    digest(load_all(), query)
