#!/usr/bin/env python3
"""milestone_render — inject a data JSON into the fixed milestone template.

The layout is pre-verified and frozen in _ARTIFACTS/milestones/_template.html; only
the DATA changes per run. This keeps headless (cron) renders from ever reintroducing
a layout bug — there is no layout to break, only data to fill.

  milestone_render.py <data.json> <out.html> [--dry-run]
  milestone_render.py --self-test
  milestone_render.py <data.json> [<out.html>] --tune TUNED.html      internal copy with the live editor (refuses public/)
  milestone_render.py <data.json> [<out.html>] --apply EXPORT [...]   text edits back to data.json, then rebuild
  (the template declares no tuner tokens, so slider moves are refused by name)

The data JSON must match window.MILESTONE_DATA (schema documented in the template head).
Stdlib only.
"""
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
TEMPLATE = os.path.join(ROOT, "_ARTIFACTS/milestones/_template.html")
MARKER = "__MILESTONE_DATA__"



def _pt():
    """page_tune, imported only for --tune/--apply (the self-test runs a lone copy of this script, without it)."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import page_tune
    return page_tune

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="milestone_render.py",
                                 description="Inject a data JSON into the frozen milestone template.")
    ap.add_argument("data", nargs="?", help="data JSON (window.MILESTONE_DATA shape)")
    ap.add_argument("out", nargs="?", help="output HTML path")
    ap.add_argument("--dry-run", action="store_true",
                    help="render in memory and report; write nothing")
    ap.add_argument("--self-test", action="store_true", help="run the argv contract self-test")
    ap.add_argument("--tune", metavar="OUT.html", help="internal copy with the live editor inlined; refuses public/")
    ap.add_argument("--apply", nargs="+", metavar="EXPORT", help="write the editor's exports back to the source, then rebuild")
    ap.add_argument("--version", type=int, help="with --apply on an Export versions file: that version, not the latest")
    return ap


def render(data_path: str) -> tuple[dict, str]:
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)                           # validates JSON
    with open(TEMPLATE, encoding="utf-8") as f:
        tmpl = f.read()
    if MARKER not in tmpl:
        sys.stderr.write(f"template missing {MARKER} marker\n")
        sys.exit(1)
    # inject as a JS literal (json.dumps is valid JS). Replace ALL occurrences so a
    # stray marker in a comment can't shadow the real one in the script.
    return data, tmpl.replace(MARKER, json.dumps(data, ensure_ascii=False))


def _snap(root: str) -> dict:
    out = {}
    for d, _, fs in os.walk(root):
        for n in fs:
            fp = os.path.join(d, n)
            with open(fp, "rb") as f:
                out[fp] = (hashlib.sha256(f.read()).hexdigest(), os.stat(fp).st_mtime_ns)
    return out


def self_test() -> int:
    """Copy this script into a temp project and assert the argv contract via subprocess."""
    tmp = tempfile.mkdtemp(prefix="milestone-selftest-")
    fails = total = 0
    try:
        os.makedirs(os.path.join(tmp, "scripts"))
        os.makedirs(os.path.join(tmp, "_ARTIFACTS", "milestones"))
        me = os.path.join(tmp, "scripts", "milestone_render.py")
        shutil.copy2(os.path.abspath(__file__), me)
        with open(os.path.join(tmp, "_ARTIFACTS", "milestones", "_template.html"), "w", encoding="utf-8") as f:
            f.write("<script>window.MILESTONE_DATA = __MILESTONE_DATA__;</script>\n")
        with open(os.path.join(tmp, "d.json"), "w", encoding="utf-8") as f:
            json.dump({"clusters": [1, 2], "trace": [1]}, f)
        env = dict(os.environ, CLAUDE_PROJECT_DIR=tmp)

        def run(*a):
            return subprocess.run([sys.executable, me, *a], capture_output=True, text=True, cwd=tmp, env=env)

        def ok(name, cond):
            nonlocal fails, total
            total += 1
            print(("  PASS  " if cond else "  FAIL  ") + name)
            fails += 0 if cond else 1

        before = _snap(tmp)
        ok("unknown flag exits 2", run("d.json", "o.html", "--bogus").returncode == 2)
        ok("extra positional exits 2", run("d.json", "o.html", "x").returncode == 2)
        ok("missing positional exits 2", run("d.json").returncode == 2)
        ok("no args exits 2", run().returncode == 2)
        r = run("d.json", "o.html", "--dry-run")
        ok("--dry-run exits 0 and reports", r.returncode == 0 and "2 clusters, 1 trace points" in r.stdout)
        ok("--dry-run and failures wrote nothing", _snap(tmp) == before)
        r = run("d.json", "o.html")
        out = os.path.join(tmp, "o.html")
        ok("render writes output", r.returncode == 0 and os.path.exists(out)
           and '"clusters": [1, 2]' in open(out, encoding="utf-8").read())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"milestone_render self-test: {total - fails}/{total}")
    return 1 if fails else 0


def main(argv=None) -> int:
    ap = build_parser()
    a = ap.parse_args(argv)
    if a.self_test:
        if a.data or a.out or a.dry_run:
            ap.error("--self-test takes no other arguments")
        return self_test()
    if a.data and a.tune:
        _pt().tune_write(render(a.data)[1], a.tune)
        return 0
    if a.data and a.apply:
        _pt().apply(a.apply, [("json", a.data)], version=a.version)
        if not a.out:
            return 0
    if not a.data or not a.out:
        ap.error("usage: milestone_render.py <data.json> <out.html>")
    data, html = render(a.data)
    if a.dry_run:
        print(f"dry-run: would render {a.out} ({len(data.get('clusters',[]))} clusters, {len(data.get('trace',[]))} trace points, {len(html)} chars)")
        return 0
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"rendered {a.out} ({len(data.get('clusters',[]))} clusters, {len(data.get('trace',[]))} trace points)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
