#!/usr/bin/env python3
"""universe_snapshot_emit.py: one self-contained snapshot of the whole ARCS populi.

WHY: the field on the home page drew a procedural ziggurat, not the atlas. The universe view
must read field truth: one dated file, stamped with the commit it was built from, that every
surface (the field, status, surfaces, beliefs, the reading room) can project.

BACKBONE: runtime/specs/knowledge-lattice-v1.json (the atlas). Its strata are altitude rings,
its domains are bearings, `zp` (Zero-Point Knowledge, "om") is the null origin. The federation
keys are the lattice's OWN: domains ONTOLOGY / EPISTEMOLOGY / METAPHYSICS ("the physics") /
ETYMOLOGY / LIBRARY, and invariant grades TAUTOLOGY / CONSTITUTIONAL / EMPIRICAL. This script
coins no ontology; a new axis is a canon change, decided by Zach, not here.

EIGHT DIMENSIONS (each global, and per node where a node has a population):
  corpus     files in _ARTIFACTS, _PATTERNS, _STATE, _SEEDS            (git ls-files)
  canon      _CANON files, tao proverbs, ADRs                            (git ls-files + jsonl rows)
  codebase   src, scripts, operators files                               (git ls-files)
  conviction Y-gate spread across receipts                               NO SIGNAL (prod DB; not read here)
  clarity    1 - open shore questions / nodes, and unmapped-file fog     (lattice + node map)
  coherence  hardness = distinct domains among in-edge sources; diamond >= 4 (the lattice's rule)
  cohesion   cross-domain edges / all edges                              (lattice edges)
  consonance invariants by grade + last drift check                      (lattice invariants)

SOURCES: every catalog, index, registry, manifest and ledger tracked in git, plus each reading
room shelf. Rows are counted, never copied: private sources (counterpart catalogs, job search,
recoil) carry a count and a privacy flag, no contents.

NODE POPULATIONS: runtime/specs/universe-node-map-v0.json maps lattice node ids to path
patterns. Explicit rules only; a file no rule claims is counted as fog, never guessed onto a node.

CONTENT vs HISTORY (2026-10-08). Every field is one of two kinds:
  content  nodes, edges, dimensions, populations, systems, sources, resonance. A pure function of
           the tracked tree; --check compares these and only these.
  history  `signature.frequency` (commits on a node's files) plus the stamp `epoch`, `as_of_sha`,
           `as_of_date`. An "as of" reading: every commit that touches a mapped file changes it, so
           a committed copy could never stay current (the staleness recursion seen 2026-10-08: five
           bundles stale hours after merge). Same precedent as surface_catalog_emit.py --check
           ("dates excluded").
  A plain emit NEVER recomputes history: it carries the committed frequency block and stamp
  forward unchanged (a node with no committed reading gets frequency null until the next
  refresh). Only --refresh writes history, serialized by the oracle:
    fetch origin/main -> temp worktree at its head -> `oracle.py next snapshot` (the epoch) ->
    emit with frequency counted by `git log <head sha>` (never wall-clock now) -> ONE commit of
    outputs + _SEEDS/_oracle.json -> push. A non-fast-forward rejection is the lock (as for ADR
    numbers): fetch, reset to origin/main, take the next epoch, regenerate, retry (3 tries).

Usage:
  python3 scripts/universe_snapshot_emit.py             # content emit; history carried forward
  python3 scripts/universe_snapshot_emit.py --check     # exit 1 if content is stale (names files)
  python3 scripts/universe_snapshot_emit.py --refresh   # oracle-serialized history refresh to origin/main
  python3 scripts/universe_snapshot_emit.py --self-test # falsifiable eval in a temp repo
Stdlib only.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(os.environ.get("UNIVERSE_ROOT") or Path(__file__).resolve().parent.parent)
# Self-test only: names a deliberately broken variant so the eval can prove it fails on bad.
BAD = os.environ.get("UNIVERSE_BAD", "")
STAMP = ("epoch", "as_of_sha", "as_of_date")
HISTORY_KEYS = set(STAMP) | {"frequency"}
LATTICE = ROOT / "runtime" / "specs" / "knowledge-lattice-v1.json"
NODEMAP = ROOT / "runtime" / "specs" / "universe-node-map-v0.json"
SHELF = ROOT / "runtime" / "specs" / "reading-room-manifest.json"
OUT = ROOT / "runtime" / "specs" / "universe-snapshot.json"
# The public projection the home field reads: lattice nodes, edges and counts only. No source
# paths, no private rows (counterpart catalog names live in the full snapshot, never here).
FIELD = ROOT / "src" / "data" / "universe-field.json"
# Galaxies: one self-contained bundle per lattice node that has a population. Same idea as the
# snapshot, one level down: sovereign (valid alone), same schema everywhere, and the parent
# lists children by id and signature only. Private paths stay here, never in the projection.
GALAXIES = ROOT / "runtime" / "specs" / "universe"

CORPUS = ("_ARTIFACTS/", "_PATTERNS/", "_STATE/", "_SEEDS/")
CANON = ("_CANON/", "_DECISIONS/")
CODE = ("src/", "scripts/", "operators/")
INDEX_RE = re.compile(r"(catalog|index|registry|inventory|manifest|concordance|ledger)[^/]*\.(json|jsonl)$", re.I)
PRIVATE = ("_STATE/job-search/", "runtime/recoil/", "_QUEUE/linkedin/", "_STATE/handoff-excavation/")
PRIVATE_RE = re.compile(r"_ARTIFACTS/[^/]+-catalog\.json$")  # counterpart catalogs


def git(*a: str) -> str:
    return subprocess.run(["git", *a], capture_output=True, text=True, cwd=ROOT, check=True).stdout


def rows(path: Path) -> int | None:
    try:
        t = path.read_text(encoding="utf-8")
    except Exception:
        return None
    if path.suffix == ".jsonl":
        return sum(1 for l in t.splitlines() if l.strip())
    try:
        d = json.loads(t)
    except Exception:
        return None
    if isinstance(d, list):
        return len(d)
    if isinstance(d, dict):
        lists = [v for v in d.values() if isinstance(v, list)]
        return max((len(v) for v in lists), default=len(d))
    return None


def history(sha: str) -> dict[str, list[str]]:
    """file -> dates of the commits that touched it, newest first, counted only up to `sha`."""
    out: dict[str, list[str]] = {}
    date = ""
    for line in git("log", sha, "--name-only", "--format=%x00%ad", "--date=short").splitlines():
        if line.startswith("\x00"):
            date = line[1:]
        elif line:
            out.setdefault(line, []).append(date)
    return out


def signature(node: dict, fs: list[str], hist: dict[str, list[str]] | None, nbr_domains: list[str], domains: dict) -> dict:
    """altitude = stratum; resonance = domain mix of lattice neighbours; frequency = commits on its files.
    Frequency counts back from the node's own last change, never from today, so the bundle is stable.
    hist None = a content emit: frequency is left None and filled from the committed reading."""
    mix = {k: round(nbr_domains.count(k) / len(nbr_domains), 3) for k in domains} if nbr_domains else {}
    if hist is None:
        return {"altitude": node["st"], "resonance": mix, "frequency": None}
    dates = sorted({d for f in fs for d in hist.get(f, [])}, reverse=True)
    commits = sum(len(hist.get(f, [])) for f in fs)
    last = dates[0] if dates else None
    window = 0
    if last:
        from datetime import date as D, timedelta
        floor = (D.fromisoformat(last) - timedelta(days=28)).isoformat()
        window = sum(1 for f in fs for d in hist.get(f, []) if d > floor)
    return {"altitude": node["st"], "resonance": mix,
            "frequency": {"file_commits": commits, "active_days": len(dates), "last_change": last, "last_28d": window}}


def build(files: list[str], hist: dict[str, list[str]] | None = None) -> dict:
    lat = json.loads(LATTICE.read_text(encoding="utf-8"))
    nodes = lat["nodes"] if isinstance(lat["nodes"], list) else [dict(v, id=k) for k, v in lat["nodes"].items()]
    dom = {n["id"]: n["dom"] for n in nodes}
    edges = [e for e in lat["edges"] if e[0] in dom and e[1] in dom]

    # coherence: the lattice's own hardness rule
    into: dict[str, set[str]] = {}
    for a, b, *_ in edges:
        into.setdefault(b, set()).add(dom[a])
    grade = {}
    inv = lat.get("invariants", {})
    for g in ("tautology", "constitutional", "empirical"):
        for i in inv.get(g, []):
            grade[i] = g

    # populations: explicit rules only
    nmap = json.loads(NODEMAP.read_text(encoding="utf-8"))["rules"]
    pop: dict[str, list[str]] = {n["id"]: [] for n in nodes}
    claimed = set()
    for f in files:
        lf = f.lower()
        for nid, pats in nmap.items():
            if nid in pop and any(fnmatch.fnmatch(lf, p.lower()) for p in pats):
                pop[nid].append(f)
                claimed.add(f)

    nbrs: dict[str, list[str]] = {}
    for a, b, *_ in edges:
        nbrs.setdefault(a, []).append(dom[b]); nbrs.setdefault(b, []).append(dom[a])
    galaxies = {}
    out_nodes = []
    for n in nodes:
        fs = pop[n["id"]]
        sig = signature(n, fs, hist, nbrs.get(n["id"], []), lat["domains"])
        if fs:
            systems: dict[str, int] = {}
            for f in fs:
                systems[f.split("/", 1)[0] if "/" in f else "(root)"] = systems.get(f.split("/", 1)[0] if "/" in f else "(root)", 0) + 1
            galaxies[n["id"]] = {
                "version": "0.1.0", "id": n["id"], "label": n["label"], "parent": "universe", "null_origin": n["id"],
                "signature": sig,
                "dimensions": {"corpus": sum(f.startswith(CORPUS) for f in fs), "canon": sum(f.startswith(CANON) or f == "WORLD.md" for f in fs),
                               "codebase": sum(f.startswith(CODE) for f in fs), "files": len(fs)},
                "systems": dict(sorted(systems.items(), key=lambda kv: -kv[1])),
                "files": sorted(fs),
            }
        out_nodes.append({
            "id": n["id"], "label": n["label"], "stratum": n["st"], "domain": n["dom"], "status": n["status"],
            "shore_open": len(n.get("shore", [])),
            "hardness": len(into.get(n["id"], ())), "diamond": len(into.get(n["id"], ())) >= 4,
            "invariant": grade.get(n["id"]),
            "signature": sig,
            "galaxy": f"runtime/specs/universe/{n['id']}.json" if fs else None,
            "population": {
                "corpus": sum(f.startswith(CORPUS) for f in fs),
                "canon": sum(f.startswith(CANON) or f in ("WORLD.md",) for f in fs),
                "codebase": sum(f.startswith(CODE) for f in fs),
                "files": len(fs),
            },
        })

    tracked = [f for f in files if f.startswith(CORPUS + CANON + CODE)]
    tao = rows(ROOT / "_CANON" / "tao-proverbs.jsonl") or 0
    shore = sum(n["shore_open"] for n in out_nodes)
    cross = sum(1 for a, b, *_ in edges if dom[a] != dom[b])

    sources = []
    for f in files:
        if not INDEX_RE.search(f.rsplit("/", 1)[-1]) or "node_modules" in f:
            continue
        priv = f.startswith(PRIVATE) or bool(PRIVATE_RE.search(f))
        sources.append({"path": f, "kind": INDEX_RE.search(f).group(1).lower(), "rows": rows(ROOT / f), "private": priv})
    shelf = json.loads(SHELF.read_text(encoding="utf-8"))
    rooms = [{"tenant": s["tenant"], "question": s.get("question"), "built": bool(s.get("built")), "render": s.get("render")}
             for s in shelf.get("shelf", [])]

    return {
        "version": "0.1.0",
        "backbone": "runtime/specs/knowledge-lattice-v1.json",
        "lattice_reviewed": lat.get("last_reviewed"),
        "lattice_drift_check": lat.get("last_drift_check"),
        "null_origin": "zp",
        "federation": {
            "domains": {k: v["label"] for k, v in lat["domains"].items()},
            "strata": {k: v["label"] for k, v in lat["strata"].items()},
            "invariant_grades": ["tautology", "constitutional", "empirical"],
        },
        "dimensions": {
            "corpus": sum(f.startswith(CORPUS) for f in files),
            "canon": {"files": sum(f.startswith(CANON) for f in files), "tao_proverbs": tao,
                      "adrs": sum(fnmatch.fnmatch(f, "_DECISIONS/ADR-*.md") for f in files)},
            "codebase": sum(f.startswith(CODE) for f in files),
            "conviction": {"signal": None, "why": "Y-gate spread lives in the prod Receipt table; not read by this script"},
            "clarity": {"nodes_clear": sum(1 for n in out_nodes if n["shore_open"] == 0), "nodes": len(out_nodes),
                        "shore_open": shore, "files_mapped": len(claimed & set(tracked)), "files_fog": len(set(tracked) - claimed)},
            "coherence": {"diamonds": sum(n["diamond"] for n in out_nodes),
                          "mean_hardness": round(sum(n["hardness"] for n in out_nodes) / len(out_nodes), 2)},
            "cohesion": {"cross_domain_edges": cross, "edges": len(edges), "ratio": round(cross / len(edges), 3) if edges else None},
            "consonance": {g: len(inv.get(g, [])) for g in ("tautology", "constitutional", "empirical")},
        },
        "nodes": out_nodes,
        "edges": [[a, b] for a, b, *_ in edges],
        "sources": sources,
        "reading_room": rooms,
        "_galaxies": galaxies,
    }


def project(snap: dict, gal: dict) -> dict:
    keep = ("id", "label", "stratum", "domain", "status", "shore_open", "hardness", "diamond", "invariant")
    # Display copy bans em-dashes; lattice labels use them as separators. Public projection only.
    tidy = lambda v: v.replace(" \u2014 ", " · ").replace("\u2014", "-") if isinstance(v, str) else v
    return {
        "version": snap["version"], "lattice_reviewed": snap["lattice_reviewed"], "null_origin": snap["null_origin"],
        "federation": snap["federation"],
        "dimensions": {k: v for k, v in snap["dimensions"].items()},
        "sources": {"count": len(snap["sources"]), "private": sum(s["private"] for s in snap["sources"])},
        "rooms": [r["tenant"] for r in snap["reading_room"]],
        "nodes": [dict({k: tidy(n[k]) for k in keep}, files=n["population"]["files"], sig=n["signature"],
                       systems=gal[n["id"]]["systems"] if n["id"] in gal else None,
                       **({"galaxy": n["galaxy"]} if BAD == "leak" else {})) for n in snap["nodes"]],
        "edges": snap["edges"],
    }


def _load(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def strip_history(o):
    """The content-only view: drop every history-derived key, at any depth."""
    if isinstance(o, dict):
        return {k: strip_history(v) for k, v in o.items() if k not in HISTORY_KEYS}
    if isinstance(o, list):
        return [strip_history(v) for v in o]
    return o


def head_stamp(sha: str, epoch: int | None) -> dict:
    return {"epoch": epoch, "as_of_sha": sha, "as_of_date": git("log", "-1", "--format=%cs", sha).strip()}


def render(hist_sha: str | None = None, epoch: int | None = None) -> dict[Path, str]:
    """All outputs as {path: body}. hist_sha None = content emit, history carried from the
    committed files; otherwise frequency is counted up to hist_sha and stamped with epoch."""
    files = [f for f in git("ls-files").splitlines() if f]
    if BAD == "livefreq":  # the pre-2026-10-08 behavior: an open-ended reading on every emit
        hist_sha = hist_sha or "HEAD"
    snap = build(files, history(hist_sha) if hist_sha else None)
    gal = snap.pop("_galaxies")
    if hist_sha:
        stamp = head_stamp(hist_sha, epoch)
        if BAD == "wallclock":
            from datetime import datetime
            stamp["as_of_date"] = datetime.now().isoformat()
        freq = None
    else:
        old = _load(OUT) or {}
        stamp = {k: old.get(k) for k in STAMP}
        freq = {n["id"]: (n.get("signature") or {}).get("frequency") for n in old.get("nodes", [])}
    for n in snap["nodes"]:
        if freq is not None:
            n["signature"]["frequency"] = freq.get(n["id"])
        if n["id"] in gal:
            gal[n["id"]]["signature"] = n["signature"]
    snap = {**{k: snap[k] for k in ("version",)}, **stamp, **{k: v for k, v in snap.items() if k != "version"}}
    out = {GALAXIES / f"{k}.json": json.dumps({**{"version": v["version"]}, **stamp, **v}, indent=1, ensure_ascii=False) + "\n"
           for k, v in gal.items()}
    out[OUT] = json.dumps(snap, indent=1, ensure_ascii=False) + "\n"
    proj = project(snap, gal)
    out[FIELD] = json.dumps({"version": proj["version"], **stamp, **proj}, separators=(",", ":"), ensure_ascii=False) + "\n"
    return out


def check() -> list[str]:
    """Content-only staleness, naming each stale file. History fields are excluded."""
    if BAD == "alwayspass":
        return []
    fresh = render()
    problems = []
    for p, body in fresh.items():
        cur = _load(p)
        if cur is None:
            problems.append(f"missing: {p.relative_to(ROOT)}")
        elif (cur if BAD == "livefreq" else strip_history(cur)) != (json.loads(body) if BAD == "livefreq" else strip_history(json.loads(body))):
            problems.append(f"stale: {p.relative_to(ROOT)}")
    if GALAXIES.exists():
        problems += [f"orphan galaxy: {p.relative_to(ROOT)}" for p in sorted(GALAXIES.glob("*.json")) if p not in fresh]
    return problems


def write(out: dict[Path, str]) -> None:
    GALAXIES.mkdir(parents=True, exist_ok=True)
    for p in GALAXIES.glob("*.json"):
        if p not in out:
            p.unlink()
    for p, b in out.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(b, encoding="utf-8")


def refresh(remote: str = "origin", branch: str = "main", tries: int = 3) -> int:
    """Oracle-serialized history refresh, in a temp worktree so the caller's checkout is untouched."""
    def g(*a, cwd, check=True):
        return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, check=check)
    g("fetch", "-q", remote, branch, cwd=ROOT)
    tmp = Path(tempfile.mkdtemp(prefix="universe-refresh-")) / "wt"
    g("worktree", "add", "-q", "--detach", str(tmp), f"{remote}/{branch}", cwd=ROOT)
    hook = os.environ.pop("UNIVERSE_BEFORE_PUSH", None)  # self-test only: run a rival refresh mid-flight (once)
    try:
        for attempt in range(1, tries + 1):
            env = dict(os.environ, CLAUDE_PROJECT_DIR=str(tmp), UNIVERSE_ROOT=str(tmp))
            env.pop("UNIVERSE_BEFORE_PUSH", None)
            ep = subprocess.run([sys.executable, str(tmp / "scripts" / "oracle.py"), "next", "snapshot"],
                                cwd=tmp, env=env, capture_output=True, text=True, check=True).stdout.strip().splitlines()[-1]
            sha = g("rev-parse", "HEAD", cwd=tmp).stdout.strip()
            subprocess.run([sys.executable, str(tmp / "scripts" / "universe_snapshot_emit.py"), "--emit-history", sha, ep],
                           cwd=tmp, env=env, check=True)
            g("add", "-A", "--", "runtime/specs/universe-snapshot.json", "runtime/specs/universe", "src/data/universe-field.json",
              "_SEEDS/_oracle.json", cwd=tmp)
            g("commit", "-q", "--no-verify", "-m", f"chore(universe): refresh history, epoch {ep} as of {sha[:8]} [NCI:SKIP generated]", cwd=tmp)
            if hook and attempt == 1:
                subprocess.run(hook, shell=True, check=True)
            r = g("push", "-q", remote, f"HEAD:{branch}", cwd=tmp, check=False)
            if r.returncode == 0:
                print(f"universe: refreshed epoch {ep} as of {sha[:8]} -> {remote}/{branch}")
                return 0
            print(f"universe: push rejected (epoch {ep} taken or base moved), attempt {attempt}/{tries}", file=sys.stderr)
            if BAD == "noretry":
                return 1
            g("fetch", "-q", remote, branch, cwd=tmp)
            g("reset", "-q", "--hard", f"{remote}/{branch}", cwd=tmp)
        return 1
    finally:
        g("worktree", "remove", "--force", str(tmp), cwd=ROOT, check=False)
        shutil.rmtree(tmp.parent, ignore_errors=True)


# ---------------------------------------------------------------------------- self-test

def self_test() -> int:
    """Falsifiable eval in a throwaway repo: each assertion passes on good AND fails on its bad variant."""
    import os as _os  # a pre-commit hook exports GIT_DIR / GIT_INDEX_FILE; left set, the scratch git below writes to the REAL repo
    for _k in [k for k in _os.environ if k.startswith("GIT_")]:
        del _os.environ[_k]
    me = Path(__file__).resolve()
    oracle = me.parent / "oracle.py"
    results = []

    def sh(cmd, cwd, env=None, check=True):
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check,
                              env=dict(os.environ, **(env or {}), GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                                       GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t"))

    def fixture(d: Path) -> Path:
        r = d / "repo"
        (r / "scripts").mkdir(parents=True)
        shutil.copy(me, r / "scripts" / me.name)
        shutil.copy(oracle, r / "scripts" / "oracle.py")
        spec = r / "runtime" / "specs"
        spec.mkdir(parents=True)
        lat = {"domains": {"ont": {"label": "Ontology"}, "epi": {"label": "Epistemology"}},
               "strata": {"s0": {"label": "Ground"}, "s1": {"label": "Ridge"}},
               "invariants": {"tautology": ["a"]},
               "nodes": [{"id": "a", "label": "Alpha — one", "st": "s0", "dom": "ont", "status": "live"},
                         {"id": "b", "label": "Beta", "st": "s1", "dom": "epi", "status": "live", "shore": ["q"]},
                         {"id": "c", "label": "Gamma", "st": "s1", "dom": "epi", "status": "live"}],
               "edges": [["a", "b"]]}
        (spec / "knowledge-lattice-v1.json").write_text(json.dumps(lat))
        (spec / "universe-node-map-v0.json").write_text(json.dumps({"rules": {"a": ["src/a/*"], "b": ["_patterns/b*"]}}))
        (spec / "reading-room-manifest.json").write_text(json.dumps({"shelf": [{"tenant": "t1", "built": True}]}))
        for f, t in {"src/a/one.ts": "1\n", "src/a/two.ts": "2\n", "_PATTERNS/b1.md": "b\n", "_SEEDS/_oracle.json": "{}\n",
                     "_CANON/tao-proverbs.jsonl": "{}\n", "_ARTIFACTS/free.md": "x\n", "_STATE/x-ledger.jsonl": "{}\n{}\n"}.items():
            (r / f).parent.mkdir(parents=True, exist_ok=True)
            (r / f).write_text(t)
        sh(["git", "init", "-q", "-b", "main"], r)
        sh(["git", "add", "-A"], r); sh(["git", "commit", "-qm", "base"], r)
        return r

    def emit(r, bad="", *a):
        return sh([sys.executable, "scripts/" + me.name, *a], r, {"UNIVERSE_BAD": bad, "UNIVERSE_ROOT": str(r)}, check=False)

    def outputs(r):
        return {str(p.relative_to(r)): p.read_bytes() for p in sorted((r / "runtime" / "specs").rglob("*.json")) + [r / "src/data/universe-field.json"]
                if "universe" in p.name or "universe" in str(p.parent.name)}

    def commit_all(r, msg):
        sh(["git", "add", "-A"], r); sh(["git", "commit", "-qm", msg, "--allow-empty"], r)

    def seeded(d, bad=""):
        r = fixture(d)
        # twice: the outputs are tracked files themselves, so the first commit changes the tree they count
        for _ in range(2):
            emit(r, bad, "--emit-history", "HEAD", "1"); commit_all(r, "seed")
        return r

    def t_idempotent(bad):
        with tempfile.TemporaryDirectory() as d:
            r = fixture(Path(d))
            emit(r, bad, "--emit-history", "HEAD", "1"); a = outputs(r)
            emit(r, bad, "--emit-history", "HEAD", "1"); b = outputs(r)
            emit(r, bad); c = outputs(r)
            emit(r, bad); e = outputs(r)
            return a == b and c == e and bool(a)

    def t_history_insensitive(bad):
        with tempfile.TemporaryDirectory() as d:
            r = seeded(Path(d), bad)
            sh(["git", "commit", "-q", "--allow-empty", "-m", "empty"], r)
            (r / "src/a/one.ts").write_text("1\nmore\n"); commit_all(r, "touch a mapped file")
            (r / "README.md").write_text("unmapped\n"); commit_all(r, "unrelated file")
            res = emit(r, bad, "--check")
            if os.environ.get("UNIVERSE_DEBUG"): print(res.stdout, res.stderr)
            return res.returncode == 0

    def t_content_sensitive(bad):
        ok = True
        for mut, want in (("edge", "universe-snapshot.json"), ("rule", "c.json")):
            with tempfile.TemporaryDirectory() as d:
                r = seeded(Path(d), bad)
                if mut == "edge":
                    p = r / "runtime/specs/knowledge-lattice-v1.json"; j = json.loads(p.read_text()); j["edges"].append(["b", "c"])
                else:
                    p = r / "runtime/specs/universe-node-map-v0.json"; j = json.loads(p.read_text()); j["rules"]["c"] = ["_artifacts/free*"]
                p.write_text(json.dumps(j))
                res = emit(r, bad, "--check")
                ok = ok and res.returncode == 1 and want in res.stdout
        return ok

    def t_no_leak(bad):
        with tempfile.TemporaryDirectory() as d:
            r = seeded(Path(d), bad)
            pub = json.loads((r / "src/data/universe-field.json").read_text())
            strs = []
            def walk(o):
                if isinstance(o, dict): [walk(v) for v in o.values()]
                elif isinstance(o, list): [walk(v) for v in o]
                elif isinstance(o, str): strs.append(o)
            walk(pub)
            pathy = [s for s in strs if re.search(r"[\w.-]+/[\w./-]+\.\w+$", s) or s.startswith(("src/", "runtime/", "_"))]
            return not pathy and "—" not in (r / "src/data/universe-field.json").read_text()

    def t_race(bad):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            r = seeded(d, bad)
            bare = d / "remote.git"
            sh(["git", "clone", "-q", "--bare", str(r), str(bare)], d)
            A, B = d / "A", d / "B"
            for c in (A, B):
                sh(["git", "clone", "-q", str(bare), str(c)], d)
            # distinct committers: two refreshes of the same base in the same second are otherwise the same SHA
            rival = f"cd {A} && env -u UNIVERSE_BEFORE_PUSH GIT_COMMITTER_NAME=rival UNIVERSE_ROOT={A} UNIVERSE_BAD={bad} {sys.executable} scripts/{me.name} --refresh"
            rb = sh([sys.executable, "scripts/" + me.name, "--refresh"], B,
                    {"UNIVERSE_BAD": bad, "UNIVERSE_ROOT": str(B), "UNIVERSE_BEFORE_PUSH": rival}, check=False)
            log = sh(["git", "log", "--format=%s", "main"], bare).stdout.splitlines()
            if os.environ.get("UNIVERSE_DEBUG"): print(rb.stdout, rb.stderr, log)
            eps = [int(m.group(1)) for s in reversed(log) if (m := re.search(r"epoch (\d+) as of", s))]
            final = json.loads(sh(["git", "show", "main:_SEEDS/_oracle.json"], bare).stdout)
            return (rb.returncode == 0 and len(eps) == 2 and eps == sorted(set(eps)) and final.get("snapshot") == eps[-1]
                    and json.loads(sh(["git", "show", "main:runtime/specs/universe-snapshot.json"], bare).stdout)["epoch"] == eps[-1])

    cases = [("idempotent", t_idempotent, "wallclock"), ("history-insensitive", t_history_insensitive, "livefreq"),
             ("content-sensitive", t_content_sensitive, "alwayspass"), ("no-path-leak", t_no_leak, "leak"),
             ("race-serialized", t_race, "noretry")]
    fail = 0
    for name, fn, bad in cases:
        good, badres = fn(""), fn(bad)
        ok = good and not badres
        fail += not ok
        print(f"{'✓' if ok else '✖'} {name}: good={'pass' if good else 'FAIL'} · bad[{bad}]={'caught' if not badres else 'NOT caught'}")
    print(f"universe self-test: {len(cases) - fail}/{len(cases)}")
    return 1 if fail else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="ARCS universe snapshot: emit, check, refresh, self-test")
    ap.add_argument("--check", action="store_true", help="exit 1 if content-derived fields are stale (history excluded)")
    ap.add_argument("--refresh", action="store_true", help="oracle-serialized history refresh pushed to origin/main")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--emit-history", nargs=2, metavar=("SHA", "EPOCH"), help=argparse.SUPPRESS)  # used by --refresh
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.refresh:
        return refresh()
    if a.check:
        problems = check()
        for p in problems:
            print(f"  {p}")
        if problems:
            print(f"✖ universe-snapshot --check: {len(problems)} stale file(s); run python3 scripts/universe_snapshot_emit.py")
            return 1
        print("✓ universe-snapshot content current (history fields are an as-of reading, not gated)")
        return 0
    if a.emit_history:
        sha = git("rev-parse", a.emit_history[0]).strip()
        out = render(sha, int(a.emit_history[1]))
    else:
        out = render()
    write(out)
    snap = json.loads(out[OUT])
    d = snap["dimensions"]
    print(f"universe: {len(snap['nodes'])} nodes · {len(snap['edges'])} edges · {len(snap['sources'])} sources · "
          f"{len(out) - 2} galaxies · mapped {d['clarity']['files_mapped']} / fog {d['clarity']['files_fog']} · "
          f"history epoch {snap.get('epoch')} as of {snap.get('as_of_date')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
