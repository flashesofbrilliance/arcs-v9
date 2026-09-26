#!/usr/bin/env python3
"""gauntlet_log_emit.py — the worked example of the public-projection factory.

Projects the internal adversarial-gauntlet ledger (_STATE/gauntlet-runs.jsonl) to a
SAFE public mirror at public/gauntlet-log.html (served at status.arcs.care/gauntlets).

This is the NEEDLE for scripts/projection_factory.py: a SECOND internal instrument
mirrored publicly through the same base that renders the belief log, proving the
generalization. The whole emitter is one Projection spec because the factory carries
the load / inject / air-gap / --check / --gate machinery.

The air-gap, by construction: the ledger carries subject, finding, outcome, and
counterpart (real names live there, e.g. the counterpart of a pre-send gauntlet).
NONE of those keys are in `public_keys`, so they are never serialized into the
served file. Only the shape crosses the basis change: date, class, agent-count.

    python3 scripts/gauntlet_log_emit.py           # write the mirror
    python3 scripts/gauntlet_log_emit.py --check    # audit only (exit 1 on drift)
    python3 scripts/gauntlet_log_emit.py --gate     # write, then run the 3 air-gap gates

stdlib-only. Deterministic: same ledger -> byte-identical mirror.
"""
from __future__ import annotations

import projection_factory as pf

GAUNTLET = pf.Projection(
    name="gauntlet log",
    ledger=pf.ROOT / "_STATE" / "gauntlet-runs.jsonl",
    template=pf.ROOT / "scripts" / "gauntlet_log_public_template.html",
    out=pf.ROOT / "public" / "gauntlet-log.html",
    # a valid row must carry these; the ledger also holds subject/finding/outcome/
    # counterpart, which are deliberately NOT required here and never embedded.
    required_keys={"run_id", "ts", "kind"},
    # the whitelist — the ONLY keys that reach the served file (the air-gap).
    public_keys=("ts", "kind", "agents"),
    id_key="run_id",
    date_key="ts",
    sort_keys=("ts", "run_id"),
    marker="/*DATA*/",
    # coarsen a precise timestamp down to the date: the public surface shows cadence,
    # never the minute a run happened (finer than shape, and a mild fingerprint).
    transforms={"ts": lambda v: str(v)[:10]},
)

if __name__ == "__main__":
    raise SystemExit(pf.cli(GAUNTLET))
