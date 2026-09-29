#!/usr/bin/env python3
"""projection_factory.py — the reusable public-projection factory for ARCS.

WORLD.md §Field Geometry names the law this makes real: "every projection factory
is a lawful transform; the lossless invariants are what must survive every change
of basis." PR #205 proved it once, for the belief log. This is the generalization:
any internal instrument can project a SAFE public mirror through the same base.

────────────────────────────────────────────────────────────────────────────────
THE CONTRACT (the minimal, whole thing — the RED THREAD)

A public projection is defined by exactly FOUR things, no more:

  1. source ledger   — an internal, append-only JSONL file. The SSOT ("one field").
                       Each line is one row; blank lines ignored.
  2. whitelist keys  — the ONLY keys copied into the served file. This is the
                       sovereign zero: the change of basis that keeps only what may
                       cross the internal↔external air-gap.
  3. template        — a self-contained HTML file carrying a DATA_MARKER token where
                       the whitelisted rows are injected as one JSON blob.
  4. the guarantee   — AIR-GAP BY CONSTRUCTION. Internal prose is never in the
                       whitelist, so it structurally cannot reach the served file —
                       not by policy, by construction. And every embedded value is
                       `<`-escaped, so no field value can break out of the <script>.

A projection is a PURE FUNCTION of (ledger, whitelist, template): the same inputs
render byte-identical output. `--check` re-renders and compares to the committed
file without writing, so a stale mirror fails CI instead of shipping silently.

The invariant that must survive every change of basis: the served file contains
the SHAPE of the record (cadence, counts, categories) and never its content.

────────────────────────────────────────────────────────────────────────────────
HOW TO USE IT (the GOLDEN THREAD — import this, don't re-derive it)

  import projection_factory as pf

  P = pf.Projection(
      name="gauntlet log",
      ledger=ROOT / "_STATE" / "gauntlet-runs.jsonl",
      template=ROOT / "scripts" / "gauntlet_log_public_template.html",
      out=ROOT / "public" / "gauntlet-log.html",
      required_keys={"run_id", "ts", "kind"},   # what a valid row must carry
      public_keys=("ts", "kind", "agents"),      # what the mirror may embed
      id_key="run_id",                           # dup-detection key
      sort_keys=("ts", "run_id"),                # deterministic order
  )
  raise SystemExit(pf.cli(P))   # gives --check / --gate / (default) write

Low-level users (e.g. belief_log_emit.py, which has more than one view) can call
`pf.load(...)` and `pf.inject(...)` directly and keep their own orchestration.

stdlib-only (foundation rule). No third-party imports, ever.
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import pathlib
import subprocess
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# The default injection token. A template marks the one spot the data blob goes
# with this literal string inside its <script type="application/json"> tag.
# (belief_log_emit.py predates this module and uses "/*BELIEF_DATA*/"; it passes
# its own marker so its output stays byte-identical — see `marker=` below.)
DATA_MARKER = "/*DATA*/"

# The three air-gap gates every served public/*.html must pass. Kept here so a new
# instrument runs the SAME gates the belief log passes, not an ad-hoc sweep.
GATES = (
    ("leak-check", ["bash", "scripts/leak_check.sh"]),        # whole-tree, glob-scanned
    ("tripwire", ["bash", "scripts/tripwire.sh"]),            # + the target file
    ("wrap-lint", ["python3", "scripts/artifact_wrap_lint.py"]),  # + the target file
)


def load(path: pathlib.Path, required_keys, *, id_key: str = "id", date_key: str | None = "ts") -> list[dict]:
    """Read a JSONL ledger into rows, validating the row contract.

    Fails closed (exit 1) on: invalid JSON, a row missing any required key, a
    malformed `date_key`, or a duplicate `id_key`. A silent bad row would poison
    every downstream projection, so a bad ledger is never a partial pass.
    """
    rows: list[dict] = []
    required = set(required_keys)
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError as e:
            sys.exit(f"AUDIT FAIL: line {n} is not valid JSON: {e}")
        missing = required - d.keys()
        if missing:
            sys.exit(f"AUDIT FAIL: entry {d.get(id_key, '?')} (line {n}) missing keys: {sorted(missing)}")
        if date_key:
            v = d[date_key]
            try:
                dt.date.fromisoformat(v)            # bare YYYY-MM-DD
            except ValueError:
                try:
                    # full timestamp; normalize Z and +HHMM so py3.9 parses what py3.11+ does
                    iso = re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", v[:-1] + "+00:00" if v.endswith("Z") else v)
                    dt.datetime.fromisoformat(iso)
                except ValueError:
                    sys.exit(f"AUDIT FAIL: entry {d.get(id_key, '?')} (line {n}) has malformed {date_key}: {v!r}")
        rows.append(d)
    if id_key:
        ids = [r[id_key] for r in rows]
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        if dupes:
            sys.exit(f"AUDIT FAIL: duplicate ledger ids: {dupes}")
    return rows


def inject(template_path: pathlib.Path, rows: list[dict], keys, *,
           marker: str = DATA_MARKER, sort_keys=("ts", "id"), transforms=None) -> str:
    """Inject a keyed projection of the ledger into a template.

    This is the lawful transform: rows are ordered deterministically by `sort_keys`
    (which need NOT be in the embed set), then projected down to `keys` only — so a
    field that is not whitelisted is never serialized. `transforms` is an optional
    {key: fn} map applied to a whitelisted value before it is embedded, for lossy
    coarsening toward the shape-only invariant (e.g. a full timestamp -> a date).
    `<` is escaped so no value can break out of the <script> tag. Missing marker
    fails closed.
    """
    transforms = transforms or {}
    ordered = sorted(rows, key=lambda r: tuple(r[k] for k in sort_keys))
    # a whitelisted key absent from a row embeds as null (optional shape field),
    # never a crash and never a reach into a non-whitelisted key.
    data = [{k: (transforms[k](r.get(k)) if k in transforms else r.get(k)) for k in keys} for r in ordered]
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    template = template_path.read_text(encoding="utf-8")
    if marker not in template:
        sys.exit(f"AUDIT FAIL: {template_path.name} is missing the {marker} injection marker.")
    return template.replace(marker, blob)


def run_gates(target: pathlib.Path, *, root: pathlib.Path = ROOT) -> int:
    """Run the three air-gap gates against a freshly-emitted public surface.

    leak-check globs the whole public/ tree; tripwire and wrap-lint also take the
    specific target so a brand-new mirror is checked by name. Returns 0 iff all pass.
    """
    rel = target.relative_to(root).as_posix()
    failed = []
    for label, cmd in GATES:
        full = cmd + ([rel] if label in ("tripwire", "wrap-lint") else [])
        print(f"── {label}: {' '.join(full)}")
        proc = subprocess.run(full, cwd=root)
        if proc.returncode != 0:
            failed.append(label)
    if failed:
        print(f"\n✘ gates FAILED: {', '.join(failed)} — fix before shipping {rel}.")
        return 1
    print(f"\n✔ all three air-gap gates green on {rel}.")
    return 0


@dataclasses.dataclass(frozen=True)
class Projection:
    """A public projection spec: the four contract pieces, tied to one output.

    render() is the pure function; emit()/check() are the deterministic write and
    the CI audit; gate() runs the air-gap gates. `cli()` wires them to argv.
    """
    name: str
    ledger: pathlib.Path
    template: pathlib.Path
    out: pathlib.Path
    required_keys: set
    public_keys: tuple
    id_key: str = "id"
    date_key: str | None = "ts"
    sort_keys: tuple = ("ts", "id")
    marker: str = DATA_MARKER
    transforms: dict = dataclasses.field(default_factory=dict)

    def render(self) -> str:
        rows = load(self.ledger, self.required_keys, id_key=self.id_key, date_key=self.date_key)
        return inject(self.template, rows, self.public_keys, marker=self.marker,
                      sort_keys=self.sort_keys, transforms=self.transforms)

    def count(self) -> int:
        return len(load(self.ledger, self.required_keys, id_key=self.id_key, date_key=self.date_key))

    def emit(self) -> int:
        self.out.write_text(self.render(), encoding="utf-8")
        print(f"wrote {self.out.relative_to(ROOT).as_posix()} — {self.count()} rows ({self.name}, audit clean).")
        return 0

    def check(self) -> int:
        current = self.out.read_text(encoding="utf-8") if self.out.exists() else ""
        if current != self.render():
            print(f"DRIFT: {self.out.relative_to(ROOT).as_posix()} stale — regenerate the {self.name}.")
            return 1
        print(f"OK — {self.out.relative_to(ROOT).as_posix()} current ({self.count()} rows).")
        return 0

    def gate(self) -> int:
        self.emit()
        return run_gates(self.out)


def cli(projection: Projection, argv: list[str] | None = None) -> int:
    """Standard emitter CLI for a single-projection instrument."""
    ap = argparse.ArgumentParser(description=f"Emit the {projection.name} public mirror.")
    ap.add_argument("--check", action="store_true", help="audit only; exit 1 if the mirror is stale")
    ap.add_argument("--gate", action="store_true", help="emit, then run the three air-gap gates")
    args = ap.parse_args(argv)
    if args.check:
        return projection.check()
    if args.gate:
        return projection.gate()
    return projection.emit()
