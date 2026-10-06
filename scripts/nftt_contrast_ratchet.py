#!/usr/bin/env python3
"""nftt_contrast_ratchet: an HONEST low-contrast gate for the NFTT dark-theme pages.

Why this exists (banked 2026-09-26): the impeccable design detector's blanket `low-contrast` exemption
on `public/blog-nftt-*.html` was hiding a MIX — mostly detector artifacts (on dark pages it can't resolve
the #020408 background and falls back to #ffffff, or defaults an unresolved text color to #000000, both
false positives) PLUS a minority of GENUINE sub-4.5:1 debt (e.g. --dimmed #64748b on #161b22 = 3.63:1 on
take-home-trap-dossier). A blanket exemption = the gate can never catch a NEW low-contrast regression
(theater). Un-exempting = the gate goes red on ~240 mostly-artifact findings (also theater).

This ratchet is the honest middle (Zach's call C, 2026-09-26): freeze the CURRENT per-file low-contrast
count as a baseline explicitly labeled a DEFERRAL (not a clean bill), and FAIL only on NEW low-contrast
ABOVE that baseline. The pre-existing mix (artifacts + genuine --dimmed debt) is deferred to a separate
triage task, NOT blessed as correct. Same ratchet shape as slop_lint --pair / token_source_gate --ratchet.

Mechanism: the impeccable config CANNOT do a count baseline (its ignoreValues is all-or-nothing per
antipattern+glob), so this is a wrapper: run the detector, count `low-contrast` findings per file, compare
to the committed baseline (_STATE/nftt-contrast-baseline.json). Runs the detector with --no-config so it sees low-contrast regardless of the standing config
exemption (which stays, keeping the kintsugi total-count ratchet undisturbed).

Usage:
  python3 scripts/nftt_contrast_ratchet.py <file.html> [...]     # exit 1 if any file EXCEEDS its baseline
  python3 scripts/nftt_contrast_ratchet.py --update-baseline     # re-snapshot all blog-nftt-*.html counts
  python3 scripts/nftt_contrast_ratchet.py --self-test           # fail-on-bad + pass-on-good
Detector launcher: $IMPECCABLE or ~/.claude/skills/impeccable/scripts/impeccable; SKIPS (exit 0) if absent
(so machines without it stay committable, mirroring the kintsugi pre-commit block).
"""
import os, sys, json, glob, subprocess

# realpath on both sides of every relpath: under a symlinked checkout (macOS /var -> /private/var)
# abspath(__file__) keeps the link while os.getcwd() resolves it, and the baseline key would miss.
ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
BASELINE = os.path.join(ROOT, "_STATE", "nftt-contrast-baseline.json")
IMP = os.environ.get("IMPECCABLE") or os.path.expanduser("~/.claude/skills/impeccable/scripts/impeccable")

def detector_available():
    return os.path.isfile(IMP) and os.access(IMP, os.X_OK)

def low_contrast_count(path):
    """low-contrast finding count for one file, via the impeccable detector."""
    out = subprocess.run([IMP, "detect", "--no-config", "--json", path], capture_output=True, text=True, cwd=ROOT).stdout
    try:
        d = json.loads(out)
    except Exception:
        return None  # parse failure -> caller treats as unknown, never silently 0
    return sum(1 for x in d if (x.get("antipattern") or x.get("rule")) == "low-contrast")

def load_baseline():
    try:
        return json.load(open(BASELINE)).get("counts", {})
    except OSError:
        return {}

def update_baseline():
    counts = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "public", "blog-nftt-*.html"))):
        rel = os.path.relpath(p, ROOT)
        n = low_contrast_count(rel)
        if n is not None:
            counts[rel] = n
    doc = {
        "_provenance": (
            "DEFERRAL BASELINE, not a clean bill. These per-file low-contrast counts are FROZEN so the "
            "gate can catch NEW low-contrast regressions above them, without red-flagging the pre-existing "
            "mix. The mix is: (1) detector ARTIFACTS on dark pages -- it falls back to #ffffff bg or #000000 "
            "text when it cannot resolve the real #020408/#161b22 values (verified: no literal color:#000 in "
            "the markup); on the real dark bg those colors pass. (2) GENUINE sub-4.5:1 debt -- e.g. --dimmed "
            "#64748b on #161b22 = 3.63:1, concentrated on take-home-trap-dossier -- filed as its own triage/"
            "fix task; when fixed, drop those files' counts here. Do NOT treat a nonzero baseline as 'this "
            "page passes contrast'. Regenerate with --update-baseline only after a deliberate review."
        ),
        "generated": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True).stdout.strip(),
        "counts": counts,
    }
    os.makedirs(os.path.dirname(BASELINE), exist_ok=True)
    json.dump(doc, open(BASELINE, "w"), indent=2); open(BASELINE, "a").write("\n")
    return counts

def check(files):
    base = load_baseline()
    bad = False
    for f in files:
        rel = os.path.relpath(os.path.realpath(f), ROOT)
        n = low_contrast_count(rel)
        if n is None:
            print(f"[WARN] {rel}: detector output unparseable — verify by hand, NOT passing silently"); bad = True; continue
        b = base.get(rel, 0)
        if n > b:
            print(f"[FAIL] {rel}: low-contrast {n} > baseline {b} — a NEW low-contrast regression. Fix the offending "
                  f"token (raise contrast), or if it is a deliberate accepted change, run --update-baseline after review.")
            bad = True
        else:
            print(f"[pass] {rel}: low-contrast {n} <= baseline {b}")
    return 1 if bad else 0

def self_test():
    # Unit-test the RATCHET LOGIC (fail-when-over-baseline, pass-when-at-or-under) with a stubbed
    # detector count. The detector integration itself is proven end-to-end on the real NFTT posts
    # (un-exempting surfaces 7/9/240; every post passes at its committed baseline). Stubbing isolates
    # the logic this file owns from the external detector, so the self-test is deterministic + offline.
    import tempfile
    global BASELINE, ROOT, low_contrast_count
    d = os.path.realpath(tempfile.mkdtemp()); ROOT = d; BASELINE = os.path.join(d, "baseline.json")
    f = os.path.join(d, "x.html"); open(f, "w").write("<html></html>")
    orig = low_contrast_count
    low_contrast_count = lambda p: 5                                   # pretend the detector sees 5
    json.dump({"counts": {"x.html": 3}}, open(BASELINE, "w")); over = check([f]) == 1    # 5>3 -> FAIL
    json.dump({"counts": {"x.html": 5}}, open(BASELINE, "w")); at = check([f]) == 0      # 5==5 -> pass
    json.dump({"counts": {"x.html": 9}}, open(BASELINE, "w")); under = check([f]) == 0   # 5<9 -> pass
    json.dump({"counts": {}}, open(BASELINE, "w")); newfile = check([f]) == 1            # unbaselined 5>0 -> FAIL
    low_contrast_count = orig
    ok = over and at and under and newfile
    print("SELF-TEST (fail-on-bad + pass-on-good):", "OK" if ok else "BROKEN",
          f"(over->{'FAIL' if over else 'WRONG'}, at->{'pass' if at else 'WRONG'}, "
          f"under->{'pass' if under else 'WRONG'}, new-file->{'FAIL' if newfile else 'WRONG'})")
    return 0 if ok else 1

def _snapshot(paths):
    """sha256 + mtime_ns per file (None if absent)."""
    import hashlib
    return {p: (hashlib.sha256(open(p, "rb").read()).hexdigest(), os.stat(p).st_mtime_ns) if os.path.exists(p) else None
            for p in paths}


def argv_self_test():
    """Copy this script into a temp repo with a stub detector; assert the argv contract via subprocess."""
    import shutil, tempfile
    tmp = os.path.realpath(tempfile.mkdtemp(prefix="nftt-ratchet-selftest-"))  # /var -> /private/var: ROOT and cwd must agree
    fails = total = 0
    try:
        os.makedirs(os.path.join(tmp, "scripts")); os.makedirs(os.path.join(tmp, "public")); os.makedirs(os.path.join(tmp, "_STATE"))
        me = os.path.join(tmp, "scripts", "nftt_contrast_ratchet.py")
        shutil.copy2(os.path.abspath(__file__), me)
        stub = os.path.join(tmp, "impeccable-stub")
        open(stub, "w").write("#!/bin/sh\necho '[{\"antipattern\":\"low-contrast\"},{\"antipattern\":\"low-contrast\"}]'\n")
        os.chmod(stub, 0o755)
        page = os.path.join(tmp, "public", "blog-nftt-x.html"); open(page, "w").write("<html></html>")
        base = os.path.join(tmp, "_STATE", "nftt-contrast-baseline.json")
        json.dump({"counts": {"public/blog-nftt-x.html": 2}}, open(base, "w"))
        watched = [page, base]
        env = dict(os.environ, IMPECCABLE=stub)

        def run(*a):
            return subprocess.run([sys.executable, me, *a], capture_output=True, text=True, cwd=tmp, env=env)

        def ok(name, cond):
            nonlocal fails, total
            total += 1; fails += 0 if cond else 1
            print(("  PASS  " if cond else "  FAIL  ") + name)

        before = _snapshot(watched)
        ok("unknown flag exits 2", run("--updat-baseline").returncode == 2)
        ok("unknown flag beside a file exits 2", run("public/blog-nftt-x.html", "--chek").returncode == 2)
        ok("--update-baseline with a file arg exits 2", run("--update-baseline", "public/blog-nftt-x.html").returncode == 2)
        ok("no args exits 2", run().returncode == 2)
        r = run("public/blog-nftt-x.html")
        ok("check at baseline passes", r.returncode == 0 and "[pass]" in r.stdout)
        ok("check mode writes nothing", _snapshot(watched) == before)
        json.dump({"counts": {"public/blog-nftt-x.html": 1}}, open(base, "w"))
        ok("check over baseline fails 1", run("public/blog-nftt-x.html").returncode == 1)
        r = run("--update-baseline")
        ok("--update-baseline rewrites baseline", r.returncode == 0 and json.load(open(base))["counts"] == {"public/blog-nftt-x.html": 2})
        link = tmp + "-link"; os.symlink(tmp, link)
        try:
            r = subprocess.run([sys.executable, os.path.join(link, "scripts", "nftt_contrast_ratchet.py"), "public/blog-nftt-x.html"],
                               capture_output=True, text=True, cwd=link, env=env)
            ok("symlinked repo path still hits its baseline key", r.returncode == 0 and "[pass] public/blog-nftt-x.html" in r.stdout)
        finally:
            os.unlink(link)
        env["IMPECCABLE"] = os.path.join(tmp, "absent")
        ok("absent detector skips with 0", run("public/blog-nftt-x.html").returncode == 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return fails, total


def full_self_test():
    rc = self_test()
    fails, total = argv_self_test()
    total += 1; fails += 1 if rc else 0
    print(f"nftt_contrast_ratchet self-test: {total - fails}/{total}")
    return 1 if fails else 0


def build_parser():
    import argparse
    ap = argparse.ArgumentParser(prog="nftt_contrast_ratchet.py",
                                 description="Fail only on NEW low-contrast findings above the committed baseline.")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--update-baseline", action="store_true", help="re-snapshot all blog-nftt-*.html counts (writes)")
    mode.add_argument("--self-test", action="store_true", help="logic + argv contract tests in a temp repo")
    ap.add_argument("files", nargs="*", help="HTML files to check against the baseline (read-only)")
    return ap


def main(argv):
    ap = build_parser()
    a = ap.parse_args(argv)
    if (a.update_baseline or a.self_test) and a.files:
        ap.error("--update-baseline / --self-test take no file arguments")
    if a.self_test:
        return full_self_test()
    if not a.update_baseline and not a.files:
        ap.error("give one or more files, --update-baseline, or --self-test")
    if not detector_available():
        print(f"[skip] impeccable detector not found ({IMP}) — nftt contrast ratchet not enforced here"); return 0
    if a.update_baseline:
        c = update_baseline(); print(f"baseline written: {len(c)} NFTT files -> {BASELINE}"); return 0
    return check(a.files)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
