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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
        rel = os.path.relpath(os.path.abspath(f), ROOT)
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
    d = tempfile.mkdtemp(); ROOT = d; BASELINE = os.path.join(d, "baseline.json")
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

def main(argv):
    if "--self-test" in argv:
        return self_test()
    if not detector_available():
        print(f"[skip] impeccable detector not found ({IMP}) — nftt contrast ratchet not enforced here"); return 0
    if "--update-baseline" in argv:
        c = update_baseline(); print(f"baseline written: {len(c)} NFTT files -> {BASELINE}"); return 0
    files = [a for a in argv if not a.startswith("--")]
    if not files:
        print("usage: nftt_contrast_ratchet.py <file> [...] | --update-baseline | --self-test"); return 2
    return check(files)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
