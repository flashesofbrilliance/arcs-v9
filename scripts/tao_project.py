#!/usr/bin/env python3
"""
tao_project.py — project the Tao canon into the rendered runtime book (Option A, 2026-09-27).

Ruling (_DECISIONS/CANON-COLLISION-tao-two-books.md): `_CANON/tao-proverbs.jsonl` is the Tao's
single source of truth (oracle-numbered, append-only). `runtime/tao/proverbs.json` is a DERIVED
projection (ADR-065: corpus = SSOT, derived = cache) that this script rebuilds. The renderers
(`scripts/gen_tao_corpus.py`, `gen_tao_views.py`, `gen_tao_alchemist.py`) keep reading the runtime
file and never notice.

Execution finding (2026-09-27, set-diff over normalized text): 241 of the 242 grid rows in the
runtime book were the SAME proverbs as canon rows tao-001..tao-241, under a different id scheme
and with lowercased text. The books were disjoint by id, not by content. So absorption LINKS
(each canon row gains `grid_id` + a `grid` custody object) instead of appending 242 duplicates.
One grid row (`field-2026-08-01-R-assess`) had no canon twin and was minted through the oracle.

A canon row is projected iff it carries `grid_id`. Its `grid` object holds the ADR-041 custody as
the grid book recorded it: {seq, aspect, verb, source, minted, text, movement[, gloss]}. `text`
is stored because the grid book kept the cased form and canon the lowercased one; the projection
must be byte-faithful to what the renderers were given. `seq` is the reading order of the grid
book at absorption. Nothing here reads or writes the oracle: new rows are minted by /tao-mint.

Usage:
  python3 scripts/tao_project.py                 # rebuild runtime/tao/proverbs.json from canon
  python3 scripts/tao_project.py --check         # exit 1 if the runtime book is stale (pre-commit)
  python3 scripts/tao_project.py --self-test     # zero rows lost + renderer HTML identical
  python3 scripts/tao_project.py --absorb        # link unlinked runtime rows to canon by text;
                                                 #   refuses to invent ids (mint via the oracle)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANON = ROOT / "_CANON" / "tao-proverbs.jsonl"
RUNTIME = ROOT / "runtime" / "tao" / "proverbs.json"
RENDERERS = ["gen_tao_corpus.py", "gen_tao_views.py", "gen_tao_alchemist.py"]
ARTIFACTS = ["arcs-tao-corpus.html", "arcs-tao-views.html", "arcs-tao-alchemist.html"]
CUSTODY_KEYS = ("aspect", "verb", "source", "minted", "text", "movement", "gloss")

META = {
    "title": "The Tao of ARCS — rendered book (derived projection)",
    "ssot": "_CANON/tao-proverbs.jsonl",
    "generated_by": "scripts/tao_project.py (do not edit by hand; edit canon, then regenerate)",
    "ruling": "_DECISIONS/CANON-COLLISION-tao-two-books.md (Option A, 2026-09-27)",
    "north_star": "Render Through the Fog",
    "governed_by": "ADR-041 (5x5 grid, recapitulate = deep-kairos distill, anti-padding)",
    "minted_by": ".claude/skills/tao-mint (writes canon through the oracle, then runs this script)",
    "renders_to": ["_ARTIFACTS/arcs-tao-corpus.html", "_ARTIFACTS/arcs-tao-views.html", "_ARTIFACTS/arcs-tao-alchemist.html"],
    "aspects": {"D": "Decision", "R": "Risk/Ruin", "W": "Window", "C": "Clarity", "H": "Horizon"},
    "verbs": ["analyze", "assess", "evaluate", "synthesize", "recapitulate"],
    "note": "Founding batch (source 'founding-v1') predates the 5x5 grid and carries movement only; aspect/verb are ~ (unassigned) for these. A canon row appears here iff it carries grid_id; canon rows without grid custody are canon-only until /tao-mint assigns a cell.",
}


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def load_canon() -> list[dict]:
    return [json.loads(l) for l in CANON.read_text(encoding="utf-8").splitlines() if l.strip()]


def write_canon(rows: list[dict]) -> None:
    CANON.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def project_rows(canon: list[dict]) -> list[dict]:
    linked = [c for c in canon if "grid_id" in c]
    linked.sort(key=lambda c: (c.get("grid", {}).get("seq", 10**9), c["id"]))
    out = []
    seen = set()
    for c in linked:
        g = c.get("grid", {})
        gid = c["grid_id"]
        if gid in seen:
            raise SystemExit(f"tao_project: duplicate grid_id {gid} in canon")
        seen.add(gid)
        row = {
            "id": gid,
            "movement": g.get("movement"),
            "aspect": g.get("aspect", c.get("aspect", "~")),
            "verb": g.get("verb", c.get("verb", "~")),
            "source": g.get("source", c.get("source_adr", "")),
            "minted": g.get("minted", c.get("minted", "")),
            "text": g.get("text", c["text"]),
        }
        if g.get("gloss") is not None:
            row["gloss"] = g["gloss"]
        row["canon_ref"] = f"_CANON/tao-proverbs.jsonl#{c['id']}"
        out.append(row)
    return out


def project() -> dict:
    return {"_meta": META, "proverbs": project_rows(load_canon())}


def dump(d: dict) -> str:
    return json.dumps(d, indent=2, ensure_ascii=False) + "\n"


def read_runtime() -> dict:
    return json.load(RUNTIME.open(encoding="utf-8"))


def render_with(runtime_json: str, tag: str) -> dict[str, str]:
    """Run the three renderers in a scratch ROOT that holds only the given runtime book."""
    tmp = Path(tempfile.mkdtemp(prefix=f"tao-{tag}-"))
    (tmp / "scripts").mkdir()
    (tmp / "runtime" / "tao").mkdir(parents=True)
    (tmp / "_ARTIFACTS").mkdir()
    (tmp / "runtime" / "tao" / "proverbs.json").write_text(runtime_json, encoding="utf-8")
    out = {}
    for r, a in zip(RENDERERS, ARTIFACTS):
        shutil.copy(ROOT / "scripts" / r, tmp / "scripts" / r)
        subprocess.run([sys.executable, str(tmp / "scripts" / r)], check=True, capture_output=True, cwd=tmp)
        out[a] = (tmp / "_ARTIFACTS" / a).read_text(encoding="utf-8")
    shutil.rmtree(tmp, ignore_errors=True)
    return out


def self_test() -> int:
    before = read_runtime()
    after = project()
    b_ids = [r["id"] for r in before["proverbs"]]
    a_ids = [r["id"] for r in after["proverbs"]]
    lost = sorted(set(b_ids) - set(a_ids))
    gained = sorted(set(a_ids) - set(b_ids))
    print(f"rows: runtime={len(b_ids)} projected={len(a_ids)} lost={lost or 0} gained={gained or 0}")
    ok = not lost and not gained and b_ids == a_ids
    if b_ids != a_ids and not lost and not gained:
        print("✖ same id set but different order (renderers are order-sensitive)")
    b_html = render_with(RUNTIME.read_text(encoding="utf-8"), "before")
    a_html = render_with(dump(after), "after")
    for a in ARTIFACTS:
        same = b_html[a] == a_html[a]
        ok = ok and same
        print(f"render {a}: {'identical' if same else 'DIFFERS'}")
    print("self-test: PASS" if ok else "self-test: FAIL")
    return 0 if ok else 1


def check() -> int:
    if not RUNTIME.exists():
        print("✖ tao_project --check: runtime/tao/proverbs.json missing; run python3 scripts/tao_project.py", file=sys.stderr)
        return 1
    if read_runtime() != project():
        print("✖ tao_project --check: runtime/tao/proverbs.json is stale vs _CANON/tao-proverbs.jsonl. fix: python3 scripts/tao_project.py && git add runtime/tao/proverbs.json", file=sys.stderr)
        return 1
    print("tao_project --check: runtime book matches canon")
    return 0


def absorb() -> int:
    """Link every runtime row to its canon twin by normalized text. Never invents ids."""
    canon = load_canon()
    runtime = read_runtime()["proverbs"]
    by_text = {}
    for c in canon:
        by_text.setdefault(norm(c["text"]), []).append(c)
    linked_gids = {c["grid_id"] for c in canon if "grid_id" in c}
    orphans, linked = [], 0
    for seq, r in enumerate(runtime):
        if r["id"] in linked_gids:
            continue
        twins = by_text.get(norm(r["text"]), [])
        if len(twins) != 1:
            orphans.append((r["id"], len(twins)))
            continue
        c = twins[0]
        if "grid_id" in c:
            orphans.append((r["id"], f"twin {c['id']} already linked to {c['grid_id']}"))
            continue
        c["grid_id"] = r["id"]
        g = {"seq": seq}
        for k in CUSTODY_KEYS:
            if k in r:
                g[k] = r[k]
        c["grid"] = g
        linked += 1
    write_canon(canon)
    print(f"absorb: linked {linked} runtime rows to canon by text; {len(orphans)} orphan(s)")
    for o in orphans:
        print(f"   orphan {o[0]}: {o[1]} canon twin(s). Mint it through the oracle (python3 scripts/oracle.py next tao), then re-run --absorb.")
    return 1 if orphans else 0


def _snapshot(paths: list[Path]) -> dict:
    """sha256 + mtime_ns of every file an emit or --absorb would write."""
    out = {}
    for p in paths:
        out[str(p)] = (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns) if p.exists() else None
    return out


def argv_self_test() -> int:
    """Run the CLI as a subprocess and assert the argv contract: bad args exit 2, --check writes nothing."""
    me = str(Path(__file__).resolve())
    watched = [RUNTIME, CANON]
    fails, total = 0, 0

    def run(*a):
        return subprocess.run([sys.executable, me, *a], capture_output=True, text=True, cwd=ROOT)

    def ok(name, cond):
        nonlocal fails, total
        total += 1
        print(("PASS " if cond else "FAIL ") + name)
        fails += 0 if cond else 1

    before = _snapshot(watched)
    ok("unknown flag exits 2", run("--chek").returncode == 2)
    ok("unknown flag writes nothing", _snapshot(watched) == before)
    ok("extra positional exits 2", run("extra").returncode == 2)
    ok("extra positional with --check exits 2", run("--check", "extra").returncode == 2)
    ok("extra positional writes nothing", _snapshot(watched) == before)
    r = run("--check")
    ok("--check exits 0 or 1", r.returncode in (0, 1))
    ok("--check writes nothing (hash + mtime)", _snapshot(watched) == before)
    print(f"tao_project self-test: {total - fails}/{total}")
    return 1 if fails else 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        prog="tao_project.py",
        description="Project _CANON/tao-proverbs.jsonl into runtime/tao/proverbs.json. No flag: rebuild (writes).",
    )
    # Independent flags, resolved in the original priority order: --self-test > --check > --absorb.
    ap.add_argument("--self-test", action="store_true", help="argv contract + zero rows lost + renderer HTML identical (writes nothing in the repo)")
    ap.add_argument("--check", action="store_true", help="exit 1 if the runtime book is stale (read-only)")
    ap.add_argument("--absorb", action="store_true", help="link unlinked runtime rows to canon by text (writes canon)")
    return ap.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.self_test:
        rc_argv = argv_self_test()
        rc_rows = self_test()
        return 1 if (rc_argv or rc_rows) else 0
    if args.check:
        return check()
    if args.absorb:
        return absorb()
    RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    d = project()
    RUNTIME.write_text(dump(d), encoding="utf-8")
    print(f"tao_project: wrote {RUNTIME.relative_to(ROOT)} with {len(d['proverbs'])} rows from canon")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
