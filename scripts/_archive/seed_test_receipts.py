#!/usr/bin/env python3
"""
Seed test receipts via POST /question-compass for /guide[receiptId] fixtures.

Generates 5 deliberately varied scenarios across horizon, stakes, and mode.
Captures request + response JSON locally for reproducibility.
Prints compact ledger of decision_receipt_ids for fixture wiring.
"""

import json
import requests
from datetime import datetime
from pathlib import Path

# FastAPI backend endpoint
API_BASE = "http://127.0.0.1:8765"
COMPASS_ENDPOINT = f"{API_BASE}/question-compass"

# Output directory for fixtures
FIXTURES_DIR = Path(__file__).parent / "test_fixtures" / "receipts"
FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

# Five scenarios with deliberate variation
# Horizon values: TODAY | THIS_WEEK | THIS_QUARTER | THIS_YEAR | LONG_ARC
SCENARIOS = [
    {
        "name": "Resume vs apply now",
        "question": "Should I finalize my resume and apply to roles now, or wait until I have one more project shipped?",
        "horizon": "TODAY",
        "stakes": "LOW",
    },
    {
        "name": "Pilot prep vs outbound",
        "question": "Should we spend this week on pilot prep with existing prospects or start fresh outbound with new targets?",
        "horizon": "THIS_WEEK",
        "stakes": "MEDIUM",
    },
    {
        "name": "Full-time role vs keep building",
        "question": "Accept full-time role offer or continue building ARCS independently for 12+ months?",
        "horizon": "LONG_ARC",
        "stakes": "HIGH",
    },
    {
        "name": "Team/process decision",
        "question": "Should we hire a part-time ops person or redistribute tasks across current team?",
        "horizon": "THIS_QUARTER",
        "stakes": "MEDIUM",
    },
    {
        "name": "High-stakes SIMPLE clarity",
        "question": "Pivot product positioning to regulatory/compliance angle (high stakes) but keep public brief simple?",
        "horizon": "LONG_ARC",
        "stakes": "HIGH",
    },
]


def seed_receipt(scenario: dict) -> dict:
    """POST a scenario to /question-compass, capture full request/response."""
    payload = {
        "question": scenario["question"],
        "horizon": scenario["horizon"],
        "stakes": scenario["stakes"],
    }

    try:
        response = requests.post(COMPASS_ENDPOINT, json=payload, timeout=10)
        response.raise_for_status()
        receipt = response.json()

        # Save fixture: request + response
        fixture = {
            "scenario": scenario["name"],
            "timestamp": datetime.utcnow().isoformat(),
            "request": payload,
            "response": receipt,
        }

        # Write to file named by receipt_id
        receipt_id = receipt.get("receipt_id", "unknown")
        fixture_file = FIXTURES_DIR / f"{receipt_id}.json"
        with open(fixture_file, "w") as f:
            json.dump(fixture, f, indent=2)

        return {
            "scenario": scenario["name"],
            "receipt_id": receipt_id,
            "mode": receipt.get("decision_mode"),
            "clarity_mode": receipt.get("clarity_mode", "SIMPLE"),
            "true_north": receipt.get("true_north", ""),
        }
    except requests.RequestException as e:
        print(f"❌ {scenario['name']}: {e}")
        return None


def main():
    """Seed all scenarios and print ledger."""
    print("🌱 Seeding 5 test receipts...\n")

    results = []
    for scenario in SCENARIOS:
        result = seed_receipt(scenario)
        if result:
            results.append(result)
            print(f"✅ {result['scenario']}")
            print(f"   ID: {result['receipt_id']}")
            print(f"   Mode: {result['mode']} | Clarity: {result['clarity_mode']}")
            print()

    # Print compact ledger
    print("\n📋 Fixture Ledger (for /guide/[receiptId] wiring):\n")
    print("| Scenario | Receipt ID | Mode | Clarity |")
    print("|----------|------------|------|---------|")
    for r in results:
        if r['receipt_id'] != "unknown":
            mode = r['mode'] or "?"
            print(
                f"| {r['scenario'][:30]:<30} | {r['receipt_id'][:16]:<16} | {mode:<6} | {r['clarity_mode']:<7} |"
            )

    print(f"\n✅ {len(results)} receipts seeded.")
    print(f"📁 Fixtures saved to: {FIXTURES_DIR}")


if __name__ == "__main__":
    main()
