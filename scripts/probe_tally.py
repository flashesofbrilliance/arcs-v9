#!/usr/bin/env python3
"""probe_tally: read the owned demand-probe counts and let the backlog row move with them.

Reads GET https://good.arcs.care/api/probe?probe=<probe> (our DemandSignal table, not Vercel),
writes _STATE/demand-probes.json (append-only history + latest), and updates the matching
row in _QUEUE/induced-backlog.jsonl: `tally` (latest counts) and `priority` by band.

Bands (distinct visitors who clicked "I'd use this"; Zach can retune in the backlog row's
`bands` field, the script reads them from there so the rule lives with the item):
  seed       < 10   P3   keep the probe up, no build
  directional 10..24 P2   scope the MCP wrapper, no hosted build
  powered    >= 25  P1   build (the ADR-076 Y validation is met)
Zach's own judgment can pin `priority_pin` on the row; the tally never lowers a pinned priority.

Usage: python3 scripts/probe_tally.py [--probe mcp-connector] [--base https://good.arcs.care]
stdlib only; exit 0 always (a readout, not a gate).
"""
import json, sys, os, urllib.request, datetime

def main():
    args = sys.argv[1:]
    probe = args[args.index("--probe") + 1] if "--probe" in args else "mcp-connector"
    base = args[args.index("--base") + 1] if "--base" in args else "https://good.arcs.care"
    url = f"{base}/api/probe?probe={probe}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "arcs-probe-tally"}), timeout=15) as r:
            data = json.load(r)
    except Exception as e:
        print(f"⚠ probe_tally: could not read {url} ({e}). Route not deployed yet, or table missing in prod.")
        data = None

    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    state_p = "_STATE/demand-probes.json"
    state = json.load(open(state_p)) if os.path.exists(state_p) else {"history": []}
    if data:
        state["latest"] = {**data, "read_at": now}
        state["history"].append({"read_at": now, "views": data["views"], "interest": data["interest"], "interestVisitors": data["interestVisitors"]})
        state["history"] = state["history"][-200:]
        json.dump(state, open(state_p, "w"), indent=1); open(state_p, "a").write("\n")

    q = "_QUEUE/induced-backlog.jsonl"
    rows = [json.loads(l) for l in open(q) if l.strip()]
    hit = None
    for row in rows:
        if row.get("probe") == probe:
            hit = row
            if data:
                v = data["interestVisitors"]
                bands = row.get("bands", {"P3": 0, "P2": 10, "P1": 25})
                band = "P3"
                if v >= bands.get("P2", 10): band = "P2"
                if v >= bands.get("P1", 25): band = "P1"
                pin = row.get("priority_pin")
                row["tally"] = {"views": data["views"], "interest": data["interest"], "interestVisitors": v, "read_at": now, "band": band}
                row["priority"] = min(pin, band) if pin else band  # "P1" < "P2" lexically: min = higher priority
    if hit:
        with open(q, "w") as f:
            for row in rows: f.write(json.dumps(row) + "\n")
    if data:
        print(f"✓ probe_tally {probe}: views={data['views']} interest={data['interest']} distinct visitors={data['interestVisitors']}"
              + (f" → backlog {hit['id']} priority={hit['priority']} (band {hit['tally']['band']}" + (f", pinned {hit['priority_pin']}" if hit.get('priority_pin') else "") + ")" if hit else " (no backlog row carries this probe)"))
    return 0

if __name__ == "__main__":
    sys.exit(main())
