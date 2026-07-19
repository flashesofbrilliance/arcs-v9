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

Chronos-sequencer discipline (runtime/specs/recoil-modes-v1.md): ledger files
are append-don't-overwrite — later passes correct earlier strata without
deleting them. This reader therefore takes current state ONLY from `cover`
(maintained in-place, always current) and `recapitulation`, honors each
report's `readOrder` directive, and skips any risk flag carrying a superseded
marker. It never serializes base-pass strata (callWalk/statedVsRevealed/
signalThreads) — those are provenance, not state.

Inductive-overfit discipline (same spec, sibling section): an advisory
stripped of its bounds is how an anecdote gets treaded as law. The Read
therefore carries its n and a sample-size regime classification (anecdote /
directional prior / central-mass — thresholds per ADR-023's 100-receipt
precedent), and any banked counterpart model's `validityBounds` is surfaced
alongside the conclusion, never silently dropped.

Open-loop-decay discipline (same spec §Open-loop decay; family registry in
ADR-033): riskFlags carry a `status` field (OPEN/DONE/WAIVED, dated). Closure
is an explicit write, never silence — DONE/WAIVED flags leave the live
aggregation, legacy flags without a status are implicitly OPEN, and `--sweep`
enumerates every open obligation across the whole ledger, aged, oldest first.
The sweeper reads state, not text.

Usage:
    python3 scripts/receipt_lookup.py "<name or email fragment>"
    python3 scripts/receipt_lookup.py --all          # dump every counterpart on file
    python3 scripts/receipt_lookup.py --sweep        # every OPEN obligation, ledger-wide, aged

Stdlib only, per repo convention (see AGENTS.md — Foundation section).
"""
import json
import sys
import glob
import os
from datetime import date

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


# Marker forms mandated by recoil-modes-v1.md §Chronos-sequencer risk. Match
# the marker syntax, not the bare word — a live flag may legitimately *mention*
# a superseded sub-strategy without itself being overturned.
SUPERSEDED_MARKERS = ("[SUPERSEDED", "⚠ SUPERSEDED", "SUPERSEDED —", "SUPERSEDED --")


def is_superseded(flag):
    text = " ".join(str(flag.get(k, "")) for k in ("label", "description", "action")).upper()
    return any(m in text for m in SUPERSEDED_MARKERS)


def flag_state(flag):
    # Open-loop-decay mandate (recoil-modes-v1.md §Open-loop decay): `status`
    # is a string beginning with OPEN, DONE, or WAIVED. Legacy flags without
    # one are implicitly OPEN — closure is an explicit write, never silence.
    # Prose in description ("RESOLVED IN PART…") does NOT close a flag.
    status = str(flag.get("status", "")).strip().upper()
    for state in ("DONE", "WAIVED", "OPEN"):
        if status.startswith(state):
            return state
    return "OPEN"


def flag_age_days(call_date):
    try:
        return (date.today() - date.fromisoformat(str(call_date)[:10])).days
    except (ValueError, TypeError):
        return None


def sweep(records):
    """Enumerate every OPEN obligation ledger-wide, aged, oldest first.

    The enforcement point for open-loop decay: an obligation that never
    appears here was written as prose (spec violation); one that appears
    forever is a decision waiting to be made.
    """
    open_flags = []
    closed = 0
    superseded = 0
    prose_items = 0
    for r in records:
        meta = r.get("meta", {})
        call_date = meta.get("callDate")
        counterpart = meta.get("counterpart", "?").split("—")[0].split(",")[0].strip()
        for rf in r.get("riskFlags", []):
            if is_superseded(rf):
                superseded += 1
                continue
            if flag_state(rf) in ("DONE", "WAIVED"):
                closed += 1
                continue
            open_flags.append({
                "age": flag_age_days(call_date),
                "date": call_date,
                "file": r.get("_file", "?"),
                "counterpart": counterpart,
                "severity": rf.get("severity", "?"),
                "id": rf.get("id", "?"),
                "label": rf.get("label", ""),
                "action": rf.get("action", ""),
            })
        recap = r.get("recapitulation")
        if isinstance(recap, dict):
            oi = recap.get("openItems")
            if isinstance(oi, list):
                prose_items += len(oi)

    open_flags.sort(key=lambda f: (-(f["age"] if f["age"] is not None else -1), f["date"] or ""))

    print(f"=== OPEN-LOOP SWEEP — {len(open_flags)} open obligation(s) across {len(records)} report(s) ===")
    print(f"(closed by explicit status: {closed} · superseded: {superseded})\n")
    for f in open_flags:
        age = f"{f['age']}d" if f["age"] is not None else "?d"
        print(f"[{age:>4} open] {f['severity']:<4} {f['counterpart']} — {f['label']}")
        print(f"           {f['file']} · {f['id']}")
        if f["action"]:
            print(f"           owed: {f['action']}")
        print()
    if prose_items:
        print(f"⚠ {prose_items} prose item(s) in recapitulation.openItems across the ledger are NOT")
        print("  sweepable — prose is write-only. Obligations that must survive the session")
        print("  belong in riskFlags with a status field (recoil-modes-v1.md §Open-loop decay).")


def regime(n):
    # Sample-size regime ladder, recoil-modes-v1.md §Inductive-overfit risk.
    # Central-mass threshold reuses ADR-023's 100-receipt gate rather than
    # inventing a new one. Tails/edges are excepted at ANY n (BAR jurisdiction)
    # — that exception is the reader's job, not this classifier's.
    if n >= 100:
        return "central-mass (n>=100, ADR-023 gate) — legitimate default IF conditions are stationary"
    if n >= 10:
        return "directional prior — condition-bounded lean, not a load-bearing assumption"
    return "anecdote — no transfer warrant; re-verify per round, prep the branch distribution"


def find_validity_bounds(record):
    # Banked counterpart models live under recapitulation.<modelKey>.validityBounds
    # (key name varies per counterpart, e.g. chanModel). Surface every one found.
    recap = record.get("recapitulation")
    found = []
    if isinstance(recap, dict):
        for key, val in recap.items():
            if isinstance(val, dict) and "validityBounds" in val:
                found.append((key, str(val["validityBounds"])))
    return found


def digest(records, query):
    hits = [r for r in records if matches(r, query)]
    if not hits:
        print(f"NO PRIOR HISTORY for '{query}' — {len(records)} total records on file, none match.")
        print("This is a cold call in the ledger. No pattern signal available; proceed on stated context only.")
        return

    hits.sort(key=lambda r: r.get("meta", {}).get("callDate", ""))

    print(f"=== RECEIPT BANK — {len(hits)} prior call(s) for '{query}' ===\n")

    nci_trend = []
    ygate_trend = []
    all_risk_flags = []
    superseded_skipped = 0
    closed_skipped = 0

    for r in hits:
        meta = r.get("meta", {})
        # NCI / Y-gate come from cover ONLY — it is maintained in-place and
        # always current; strata may hold overturned reads of the same call.
        cover = r.get("cover", {})
        nci_trend.append((meta.get("callDate"), cover.get("nci")))
        ygate_trend.append((meta.get("callDate"), cover.get("yGate")))
        for rf in r.get("riskFlags", []):
            if is_superseded(rf):
                superseded_skipped += 1
                continue
            if flag_state(rf) in ("DONE", "WAIVED"):
                closed_skipped += 1
                continue
            all_risk_flags.append((meta.get("callDate"), rf.get("severity"), rf.get("label")))
        print(f"[{meta.get('callDate')}] {meta.get('callTitle')} — {meta.get('counterpartRole', '')}")
        print(f"  Y: {cover.get('yGate')}/{cover.get('conviction')} · NCI {cover.get('nci')} · {cover.get('headline', '')}")
        recap = r.get("recapitulation")
        if isinstance(recap, dict):
            as_of = recap.get("asOf", "undated")
            print(f"  recapitulation present (asOf {as_of}) — consolidated current state; read it before any stratum.")
        for model_key, bounds in find_validity_bounds(r):
            excerpt = bounds if len(bounds) <= 300 else bounds[:300] + " […]"
            print(f"  banked model '{model_key}' carries validityBounds — read them before treading it as law:")
            print(f"    {excerpt}")
        print()

    if superseded_skipped or closed_skipped:
        print(f"({superseded_skipped} superseded flag(s) skipped — provenance; "
              f"{closed_skipped} closed by explicit DONE/WAIVED status)\n")

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
    # Latest = latest record that actually carries a cover gate. Pre-call
    # stubs have an empty cover; letting one mask the last real read is the
    # chronos-sequencer pathogen in cross-file form.
    gates = [y for _, y in ygate_trend if y]
    latest_gate = gates[-1] if gates else "UNKNOWN"

    # n for the regime read = scored calls only (records with a real cover
    # gate) — pre-call stubs are not observations.
    n_scored = len(gates)
    print(f"\n--- Read (n={n_scored} scored call(s) — {regime(n_scored)}) ---")
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
    if sys.argv[1] == "--sweep":
        sweep(load_all())
        sys.exit(0)
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
