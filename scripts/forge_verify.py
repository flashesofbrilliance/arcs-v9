#!/usr/bin/env python3
"""
forge_verify.py -- gate that must pass BEFORE any counterpart surface deploys.

Runs the deterministic safety checks the blueprint + project rules require, over both the forge
SSOT and the rendered HTML. Exits nonzero on any HARD failure. Soft items are surfaced for a human
(they cannot be proven mechanically) but never block.

HARD checks (fail -> nonzero exit):
  H1  zero em-dashes anywhere in rendered output
  H2  impeccable anti-pattern detector clean (exit 0) on all 4 surfaces
  H3  attribution + labeling: every said.speaker in {zach,counterpart}; every demo read carries a
      clue AND an inference (labeled read, not asserted fact); every reserved-band read has a disclosure
  H4  every surface is noindex; every gated surface has the pw-gate; landing is ungated
  H5  gate password equals the counterpart first name (lowercased)

SOFT (surfaced, not blocking):
  S1  counterpart-attributed quotes listed for a human transcript check (Me=Zach, Them=counterpart)
  S2  role-archetype reminder for named orgs (no fabricated interiority about real people)

Usage:
  python scripts/forge_verify.py --data runtime/recoil/generated/<name>-forge.json [--out-dir public]
"""
import argparse, json, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DETECT_CANDIDATES = [
    os.path.expanduser("~/.claude/skills/impeccable/scripts/detect.mjs"),
    os.path.join(ROOT, ".claude/skills/impeccable/scripts/detect.mjs"),
]
SUFFIX = {"landing": "", "recoil": "-recoil", "codex": "-codex", "demo": "-demo"}
GATED = {"recoil", "codex", "demo"}
EMDASH = ("—", "―")  # em-dash, horizontal bar (en-dash allowed in ranges)


def find_detector():
    return next((p for p in DETECT_CANDIDATES if os.path.exists(p)), None)


def paths_for(data, out_dir):
    name = data["meta"]["name"]
    return {s: os.path.join(out_dir, f"{name}{SUFFIX[s]}.html") for s in SUFFIX}


def main():
    ap = argparse.ArgumentParser(description="Pre-deploy verify gate for the counterpart family.")
    ap.add_argument("--data", required=True)
    ap.add_argument("--out-dir", default=os.path.join(ROOT, "public"))
    a = ap.parse_args()

    with open(a.data) as f:
        data = json.load(f)
    meta = data["meta"]
    files = paths_for(data, a.out_dir)
    fails, warns = [], []

    # all 4 must exist
    missing = [s for s, p in files.items() if not os.path.exists(p)]
    if missing:
        fails.append(f"missing rendered surface(s): {missing}. Run forge_counterpart.py first.")
        _report(fails, warns); sys.exit(1)

    htmls = {s: open(p, encoding="utf-8").read() for s, p in files.items()}

    # H1 em-dash
    for s, html in htmls.items():
        for ch in EMDASH:
            if ch in html:
                fails.append(f"H1 em-dash in {s} surface (U+{ord(ch):04X})")

    # H2 impeccable detector
    det = find_detector()
    if not det:
        warns.append("H2 impeccable detector not found; skipped. Install the impeccable skill to enforce.")
    else:
        for s, p in files.items():
            r = subprocess.run(["node", det, p], capture_output=True, text=True)
            if r.returncode != 0:
                fails.append(f"H2 impeccable found anti-patterns in {s}:\n{r.stdout.strip()}")

    # H3 attribution + labeling (from SSOT)
    for surf in ("recoil", "codex"):
        for sd in data.get(surf, {}).get("said", []):
            if sd.get("speaker") not in ("zach", "counterpart"):
                fails.append(f"H3 said block in {surf} has invalid speaker {sd.get('speaker')!r} "
                             "(must be 'zach' or 'counterpart')")
    for r in data.get("demo", {}).get("reads", []):
        if not r.get("clue") or not r.get("inference"):
            fails.append(f"H3 demo read {r.get('conclusion','?')!r} missing clue/inference "
                         "(unlabeled inference = asserted fact, not a read)")
        if r.get("band") == "res" and not r.get("disclosure"):
            fails.append(f"H3 reserved-band read {r.get('conclusion','?')!r} has no disclosure line")

    # H4 noindex + gate topology
    for s, html in htmls.items():
        if "noindex" not in html:
            fails.append(f"H4 {s} surface missing noindex")
        has_gate = 'id="pw-gate"' in html
        if s in GATED and not has_gate:
            fails.append(f"H4 gated surface {s} missing pw-gate")
        if s == "landing" and has_gate:
            fails.append("H4 landing surface should be ungated (has pw-gate)")

    # H5 password == first name
    pw = (meta.get("gate_password") or meta.get("first_name", "")).lower()
    if pw != meta.get("first_name", "").lower():
        warns.append(f"H5 gate password {pw!r} != first name {meta.get('first_name','').lower()!r} "
                     "(intentional? blueprint says gate = first name)")
    for s in GATED:
        if f"P='{pw}'" not in htmls[s]:
            fails.append(f"H5 {s} gate does not carry password {pw!r}")

    # S1 counterpart quotes for human transcript check
    for surf in ("recoil", "codex"):
        for sd in data.get(surf, {}).get("said", []):
            if sd.get("speaker") == "counterpart":
                warns.append(f'S1 verify against transcript (Them={meta.get("counterpart")}): '
                             f'"{sd.get("quote","")[:80]}"')
    # S2 role-archetype reminder
    warns.append(f"S2 confirm codex altitudes are role-archetypes, not named people, "
                 f"and no fabricated interiority about {meta.get('counterpart')} (fence={meta.get('fence')})")

    _report(fails, warns)
    sys.exit(1 if fails else 0)


def _report(fails, warns):
    if warns:
        print("SOFT (review, non-blocking):")
        for w in warns:
            print(f"  ~ {w}")
    if fails:
        print("\nHARD FAILURES (must fix before deploy):")
        for f in fails:
            print(f"  x {f}")
        print(f"\nforge_verify: {len(fails)} hard failure(s). Deploy blocked.")
    else:
        print("\nforge_verify: all hard checks pass. Clear to deploy.")


if __name__ == "__main__":
    main()
