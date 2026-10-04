#!/usr/bin/env python3
"""blog_provenance — emit/verify a provenance manifest for a hand-synthesized artifact.

The transform itself (LLM judgment) is NOT reproducible; this tool does not pretend
otherwise. What IS countable gets counted: source inputs (path + commit + sha), params
(the configs/gates the transform ran under), the ordered transform log, and output
hashes. Mechanical layer only — NOTOMATION: the prose stays human/LLM-owned.

Usage:
  python3 scripts/blog_provenance.py emit   <manifest.json>   # re-hash outputs, stamp epoch
  python3 scripts/blog_provenance.py emit   <manifest.json> --dry-run   # print, write nothing
  python3 scripts/blog_provenance.py verify <manifest.json>   # check srcs exist + hashes match
  python3 scripts/blog_provenance.py --self-test
`verify` and `emit --dry-run` are read-only.
"""
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def git(*args) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def emit(mpath: Path, dry_run: bool = False) -> int:
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
    if dry_run:
        print(json.dumps(m, indent=2))
        print(f"would emit {mpath.name} @ {m['epoch']['corpus_commit']} (dry run, nothing written)")
        return 0
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


def build_parser():
    import argparse
    ap = argparse.ArgumentParser(prog="blog_provenance.py",
                                 description="Emit/verify a provenance manifest for a hand-synthesized artifact.")
    ap.add_argument("--self-test", action="store_true", help="argv contract in a temp repo")
    sub = ap.add_subparsers(dest="cmd")
    e = sub.add_parser("emit", help="re-hash outputs + sources, stamp epoch (writes the manifest)")
    e.add_argument("manifest", type=Path)
    e.add_argument("--dry-run", action="store_true", help="print the stamped manifest, write nothing")
    v = sub.add_parser("verify", help="check sources exist + output hashes match (read-only)")
    v.add_argument("manifest", type=Path)
    return ap


def main(argv) -> int:
    ap = build_parser()
    a = ap.parse_args(argv)
    if a.self_test:
        if a.cmd: ap.error("--self-test takes no subcommand")
        return self_test()
    if a.cmd == "emit": return emit(a.manifest, a.dry_run)
    if a.cmd == "verify": return verify(a.manifest)
    ap.print_help(); return 2


def _snapshot(root: Path) -> dict:
    import hashlib
    return {str(p): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
            for p in sorted(root.rglob("*")) if p.is_file()}


def self_test() -> int:
    """Copy this script into a repo-shaped temp dir (ROOT resolves from the script path)."""
    import shutil, sys as _s, tempfile
    tmp = Path(tempfile.mkdtemp(prefix="blog-provenance-selftest-")).resolve()
    fails = total = 0

    def ok(name, cond):
        nonlocal fails, total
        total += 1; fails += 0 if cond else 1
        print(("  PASS  " if cond else "  FAIL  ") + name)

    try:
        (tmp / "scripts").mkdir()
        me = tmp / "scripts" / "blog_provenance.py"
        shutil.copy2(Path(__file__).resolve(), me)
        (tmp / "out.html").write_text("<p>out</p>\n")
        (tmp / "src.md").write_text("source\n")
        man = tmp / "m.json"
        man.write_text(json.dumps({"sources": [{"path": "src.md"}], "outputs": [{"path": "out.html"}]}) + "\n")

        def run(*a):
            return subprocess.run([_s.executable, str(me), *a], capture_output=True, text=True, cwd=tmp)

        before = _snapshot(tmp)
        ok("no command exits 2", run().returncode == 2)
        ok("unknown flag exits 2", run("--bogus").returncode == 2)
        ok("unknown subcommand exits 2", run("emitt", "m.json").returncode == 2)
        ok("verify extra positional exits 2", run("verify", "m.json", "extra").returncode == 2)
        ok("emit extra positional exits 2", run("emit", "m.json", "extra").returncode == 2)
        ok("verify unknown flag exits 2", run("verify", "m.json", "--dry-run").returncode == 2)
        ok("emit unknown flag exits 2", run("emit", "m.json", "--dryrun").returncode == 2)
        ok("verify without manifest exits 2", run("verify").returncode == 2)
        ok("--self-test with a subcommand exits 2", run("--self-test", "verify", "m.json").returncode == 2)
        r = run("verify", "m.json")
        ok("verify flags an un-emitted output as DRIFT (exit 1)", r.returncode == 1 and "DRIFT output edited" in r.stdout)
        r = run("emit", "--dry-run", "m.json")
        ok("emit --dry-run previews", r.returncode == 0 and "would emit m.json" in r.stdout)
        ok("read-only modes and bad argv write nothing", _snapshot(tmp) == before)
        r = run("emit", "m.json")
        ok("emit writes the hashes", r.returncode == 0 and json.loads(man.read_text())["outputs"][0].get("sha256_16"))
        r = run("verify", "m.json")
        ok("verify OK after emit", r.returncode == 0 and "verify: OK" in r.stdout)
        (tmp / "out.html").write_text("<p>edited</p>\n")
        ok("verify catches an edited output", run("verify", "m.json").returncode == 1)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"blog_provenance self-test: {total - fails}/{total}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
