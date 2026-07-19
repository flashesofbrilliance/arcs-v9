#!/usr/bin/env python3
"""Enforcement-parity ledger gate (ADR-034).

Fails (exit 1) when any finding in _PATTERNS/ledger.json is delinquent:
  - exit.type == "open" and older than its severity SLA, or
  - exit.type == "waiver" with a past 'expires' date or missing fields, or
  - malformed entries (unknown severity/exit type, missing id/filed).

Stdlib only. Run from repo root: python3 scripts/ledger_check.py
"""
import json
import sys
from datetime import date
from pathlib import Path

LEDGER = Path(__file__).resolve().parent.parent / "_PATTERNS" / "ledger.json"
VALID_EXITS = {"test", "ci", "guard", "waiver", "open"}


def main() -> int:
    data = json.loads(LEDGER.read_text())
    slas = data["slas_days"]
    today = date.today()
    problems = []
    open_ok = []

    for f in data["findings"]:
        fid = f.get("id", "<missing id>")
        sev = f.get("severity")
        exit_ = f.get("exit", {})
        etype = exit_.get("type")

        if sev not in slas or etype not in VALID_EXITS or "filed" not in f:
            problems.append(f"{fid}: malformed entry (severity={sev}, exit={etype})")
            continue

        if etype == "open":
            age = (today - date.fromisoformat(f["filed"])).days
            sla = slas[sev]
            if age > sla:
                problems.append(
                    f"{fid} [{sev}]: OPEN {age}d, SLA {sla}d — {f['summary']}"
                )
            else:
                open_ok.append(f"{fid} [{sev}]: open {age}d of {sla}d — {f['summary']}")
        elif etype == "waiver":
            if not exit_.get("reason") or not exit_.get("expires"):
                problems.append(f"{fid}: waiver missing reason/expires")
            elif date.fromisoformat(exit_["expires"]) < today:
                problems.append(
                    f"{fid} [{sev}]: waiver EXPIRED {exit_['expires']} — {f['summary']}"
                )

    if open_ok:
        print("Open findings within SLA:")
        for line in open_ok:
            print(f"  ⏳ {line}")
    if problems:
        print("\nDELINQUENT — close with a mechanism (test/ci/guard) or a dated waiver:")
        for line in problems:
            print(f"  ✗ {line}")
        return 1
    print("\nLedger clean: no delinquent findings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
