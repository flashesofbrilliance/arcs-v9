"""
Bootstrap ARCS bundle schemas in GIGI.
Run once after starting gigi-stream:

  python A.R.C.S/arcs_init_bundles.py

Idempotent — if bundles already exist, GQL returns ok without clearing data.
DB managed by gigi-stream at ~/gigi/arcs.db (port 3142).
"""

import urllib.request
import urllib.error
import json
import sys

GIGI_BASE = "http://localhost:3142"


def post(path: str, body: dict) -> dict:
    url = f"{GIGI_BASE}{path}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def main():
    # Health check
    try:
        req = urllib.request.Request(f"{GIGI_BASE}/v1/health", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            health = json.loads(resp.read())
        print(f"gigi-stream healthy — {health.get('bundles', 0)} bundles")
    except Exception as e:
        print(f"ERROR: gigi-stream not reachable at {GIGI_BASE}: {e}")
        print("Start it first:  GIGI_DATA_DIR=~/gigi ~/Repositories/forks/gigi/target/debug/gigi-stream &")
        sys.exit(1)

    # arcs_templates — ARCS macro template library, persisted via GIGI
    r = post("/v1/bundles", {
        "name": "arcs_templates",
        "schema": {
            "fields": {
                "template_id": "text", "macro_family": "text",
                "stakes": "text", "horizon": "text", "mode": "text",
                "skeleton": "text", "source": "text",
                "version": "numeric", "created_at": "timestamp",
            },
            "keys": ["template_id"],
            "indexed": ["macro_family", "stakes", "horizon", "mode"],
            "defaults": {"source": "canonical", "version": 1},
        },
    })
    print(f"arcs_templates: {r}")

    # arcs_gap_log — ARCS gap log (typed misses), persisted via GIGI
    r = post("/v1/bundles", {
        "name": "arcs_gap_log",
        "schema": {
            "fields": {
                "gap_id": "text", "macro_family_attempted": "text",
                "stakes": "text", "horizon": "text", "mode": "text",
                "nearest_template_id": "text", "holonomy_distance": "numeric",
                "fallback_used": "text", "gap_signal_type": "text",
                "instrumentation_needed": "numeric", "incoherence_flag": "numeric",
                "outcome": "text", "delta": "text", "ts": "timestamp",
            },
            "keys": ["gap_id"],
            "indexed": ["macro_family_attempted", "stakes", "horizon", "gap_signal_type"],
            "defaults": {"outcome": "pending", "delta": "", "instrumentation_needed": 0, "incoherence_flag": 0},
        },
    })
    print(f"arcs_gap_log: {r}")

    # Verify
    req = urllib.request.Request(f"{GIGI_BASE}/v1/bundles", method="GET")
    with urllib.request.urlopen(req, timeout=5) as resp:
        bundles = json.loads(resp.read())
    names = [b["name"] for b in bundles]
    assert "arcs_templates" in names, "arcs_templates missing"
    assert "arcs_gap_log" in names, "arcs_gap_log missing"
    print(f"\nVerified: {names}")
    print("Bundle schemas ready. Run arcs_seed_bar.py to load templates.")


if __name__ == "__main__":
    main()
