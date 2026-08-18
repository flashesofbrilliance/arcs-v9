#!/usr/bin/env python3
"""blog_provenance — emit/verify a provenance manifest for a hand-synthesized artifact.

The transform itself (LLM judgment) is NOT reproducible; this tool does not pretend
otherwise. What IS countable gets counted: source inputs (path + commit + sha), params
(the configs/gates the transform ran under), the ordered transform log, and output
hashes. Mechanical layer only — NOTOMATION: the prose stays human/LLM-owned.

Usage:
  python3 scripts/blog_provenance.py emit   <manifest.json>   # re-hash outputs, stamp epoch
  python3 scripts/blog_provenance.py verify <manifest.json>   # check srcs exist + hashes match
"""
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def git(*args) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def emit(mpath: Path) -> int:
    m = json.loads(mpath.read_text())
    m["epoch"] = {"corpus_commit": git("rev-parse", "--short", "HEAD"),
                  "emitted": git("log", "-1", "--format=%cI", "HEAD")}
    for out in m["outputs"]:
        p = ROOT / out["path"]
        out["sha256_16"] = sha(p) if p.exists() else "MISSING"
    for s in m["sources"]:
        if "path" in s:
            p = ROOT / s["path"]
            s["present"] = p.exists()
            if p.exists():
                s["sha256_16"] = sha(p)
    mpath.write_text(json.dumps(m, indent=2) + "\n")
    print(f"emitted {mpath.name} @ {m['epoch']['corpus_commit']}")
    return 0


def verify(mpath: Path) -> int:
    m = json.loads(mpath.read_text())
    bad = 0
    for out in m["outputs"]:
        p = ROOT / out["path"]
        if not p.exists():
            print(f"DRIFT output missing: {out['path']}"); bad += 1
        elif sha(p) != out.get("sha256_16"):
            print(f"DRIFT output edited since emit: {out['path']}"); bad += 1
    for s in m["sources"]:
        if "path" in s and not (ROOT / s["path"]).exists():
            if "recover_via" in s:
                print(f"NOTE source not in worktree (recoverable): {s['path']} <- {s['recover_via']}")
            else:
                print(f"DRIFT source missing: {s['path']}"); bad += 1
        if "commit" in s and not git("cat-file", "-t", s["commit"]):
            print(f"DRIFT commit unknown: {s['commit']}"); bad += 1
    print(f"verify: {'OK' if bad == 0 else f'{bad} DRIFT'} · "
          f"{len(m['sources'])} sources · {len(m['outputs'])} outputs · "
          f"epoch {m.get('epoch', {}).get('corpus_commit', '?')}")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("emit", "verify"):
        print(__doc__); sys.exit(2)
    sys.exit({"emit": emit, "verify": verify}[sys.argv[1]](Path(sys.argv[2])))
