"""
ARCS battery routing — three operating modes.

FULL         AC power or battery > 50%: all GIGI queries, full synthesis
LITE_DEFERRED battery 20–50%: L1+L2 queries run, ALC deferred
LOW_POWER_SAFE battery < 20%: skip GIGI reads, L5 floor only; receipts always write

Receipts and gap log writes are never deferred regardless of mode.
"""

from __future__ import annotations

import re
import subprocess
from typing import Literal

BatteryMode = Literal["FULL", "LITE_DEFERRED", "LOW_POWER_SAFE"]


def get_battery_mode() -> BatteryMode:
    """Read live battery state from pmset and return ARCS routing mode."""
    try:
        out = subprocess.run(
            ["pmset", "-g", "batt"], capture_output=True, text=True, timeout=3
        ).stdout
    except Exception:
        return "FULL"  # fail open — don't restrict on tool error

    if "AC Power" in out:
        return "FULL"

    pct_match = re.search(r"(\d+)%", out)
    if not pct_match:
        return "FULL"

    pct = int(pct_match.group(1))
    if pct > 50:
        return "FULL"
    if pct >= 20:
        return "LITE_DEFERRED"
    return "LOW_POWER_SAFE"
