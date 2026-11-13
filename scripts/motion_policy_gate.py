#!/usr/bin/env python3
"""motion_policy_gate: pages that move obey the motion and safety tokens in _tokens.css.

Rule (deterministic, stdlib-only), for each checked HTML file that declares or reads motion tokens
or runs a repeating animation:
  M1  the inlined token block carries every --mo-* token the kit defines, with the kit's values
      (a stale or hand-edited copy fails; edit src/ui-kit/recoil-report/_tokens.css and re-inline).
  M2  no CSS animation repeats faster than --mo-flash-max per second (infinite iteration with a
      duration under 1/--mo-flash-max s), unless it only moves position or scale (transform) and
      is not an opacity or color keyframe set.
  M3  a page that reads the tokens in script (--mo-) must not also hold the policy numbers as
      bare literals next to the words they govern (SHUT shutter 650, hold 180, loop 0.17, pose * 8).
Usage: python3 scripts/motion_policy_gate.py <file.html> [...]   (exit 1 on any FAIL)
"""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design_candidates

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = os.path.join(ROOT, "src/ui-kit/recoil-report/_tokens.css")
MO = re.compile(r'(--mo-[a-z-]+)\s*:\s*([^;]+);')

def tokens(text):
    return {n: v.strip().split("/*")[0].strip() for n, v in MO.findall(text)}

def check(path, kit):
    t = open(path, encoding="utf-8").read()
    fails = []
    have = tokens(t)
    uses = "--mo-" in t
    anim = re.findall(r'animation[^;{}]*infinite[^;{}]*', t)
    if not uses and not anim:
        return "PASS", ["no motion tokens read and no repeating animation (not a motion surface)"]
    if uses:
        trial = design_candidates.tokens_for(t)  # a declared, unexpired candidate may trial a motion value
        for n, v in kit.items():
            if n not in have: fails.append(f"M1 {n} missing from the inlined token block")
            elif have[n] != v and trial.get(n) != have[n]: fails.append(f"M1 {n} is {have[n]} here but {v} in the kit")
    cap = float(kit.get("--mo-flash-max", "3"))
    for a in anim:
        m = re.search(r'(\d*\.?\d+)(ms|s)\b', a)
        if not m: continue
        d = float(m.group(1)) / (1000 if m.group(2) == "ms" else 1)
        if d > 0 and 1 / d > cap and not re.search(r'transform|rotate|translate|scale', a):
            fails.append(f"M2 repeating animation '{a.strip()[:60]}' runs {1/d:.1f} Hz (cap {cap:g})")
    if uses:
        js = t[t.rfind("<script"):]
        for pat, what in [(r'now - SHUT\.trig\) / \d', "shutter ms"), (r'< 180;', "hold min"), (r'Math\.max\(s\.L, 0\.17\)', "loop min"), (r"tsec \|\| 0\) \* 8", "pose rate")]:
            if re.search(pat, js): fails.append(f"M3 literal {what}: read it from the --mo-* token instead")
    return ("FAIL" if fails else "PASS"), (fails or ["motion tokens inherited, no repeating animation over the cap"])

def main(argv):
    kit = tokens(open(KIT, encoding="utf-8").read())
    if not argv: print(__doc__); return 2
    bad = 0
    for f in argv:
        s, msgs = check(f, kit)
        print(("✓" if s == "PASS" else "✖"), f"motion_policy_gate {s} {f}")
        for m in msgs:
            if s == "FAIL": print("   ", m)
        bad += s == "FAIL"
    return 1 if bad else 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
