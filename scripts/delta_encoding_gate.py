#!/usr/bin/env python3
"""delta_encoding_gate: a belief change is never shown by colour alone.

Class it blocks (2026-10-27): a change rendered as a red or green number with no sign and no arrow, which a
colour-blind reader cannot read (Zach is partly colour-blind). The recoil player routes every change through one
helper, pts(), that returns {d, dir, text}: dir picks the colour and arrow, text carries the sign ("+40 pts",
"−40 pts", "no change"). This gate checks that the routing holds.

Rules (static, stdlib only), for each JS file or inline <script>:
  R1  If a file defines pts(), it emits a "+" sign, the true minus U+2212 (escaped or literal) and "no change".
  R2  Every place that sets a class from X.dir also sets text from X.text within 8 lines (same object X).
  R3  No hyphen-minus used as a change sign: a string literal "-" next to "pts" is refused.
Usage:
  python3 scripts/delta_encoding_gate.py <file.js|file.html> [...]   exit 1 on any finding
  python3 scripts/delta_encoding_gate.py --self-test                 known-bad and known-good fixtures
"""
import re, sys

DIR_SET = re.compile(r'className\s*=\s*[^;\n]*?\b(\w+)\.dir\b')
PTS_DEF = re.compile(r'function\s+pts\s*\(')


def scripts_of(path, text):
    if path.endswith(".js"):
        return [text]
    return re.findall(r"<script[^>]*>(.*?)</script>", text, re.S)


def check_js(src):
    out = []
    lines = src.split("\n")
    if PTS_DEF.search(src):
        body = src[PTS_DEF.search(src).start():][:600]
        if '"+"' not in body:
            out.append("R1: pts() does not emit a + sign")
        if "\\u2212" not in body and "−" not in body:
            out.append("R1: pts() does not emit the true minus sign U+2212")
        if "no change" not in body:
            out.append('R1: pts() does not say "no change" for a zero change')
    for i, line in enumerate(lines):
        for m in DIR_SET.finditer(line):
            obj = m.group(1)
            window = "\n".join(lines[max(0, i - 8): i + 9])
            if not re.search(r'\b' + re.escape(obj) + r'\.text\b', window):
                out.append(f"R2: line {i + 1}: class set from {obj}.dir with no {obj}.text nearby (colour without sign)")
        if re.search(r'"-"\s*\)?\s*\+[^;\n]*pts|"-\d+ pts"', line):
            out.append(f"R3: line {i + 1}: hyphen-minus used as a change sign")
    return out


def check_file(path):
    text = open(path, encoding="utf-8").read()
    found = []
    for src in scripts_of(path, text):
        found += check_js(src)
    return found


def self_test():
    good = '''function pts(a, b) { var d = 1; return { d: d, dir: "up", text: d === 0 ? "no change" : (d > 0 ? "+" : "\\u2212") + d + " pts" }; }
var ch = pts(0, 1); el.className = "pl-delta " + ch.dir; b.textContent = ch.text;'''
    cases = [
        ("known-good passes", check_js(good) == []),
        ("colour without sign is refused", any("R2" in f for f in check_js('var ch = pts(0,1);\nel.className = "x " + ch.dir;\nel.textContent = Math.round(v) + "%";'))),
        ("pts without minus is refused", any("U+2212" in f for f in check_js('function pts(a,b){ return { text: (d > 0 ? "+" : "-") + d + " pts, no change" }; }'))),
        ("hyphen sign is refused", any("R3" in f for f in check_js('t.textContent = "-40 pts";'))),
    ]
    for name, ok in cases:
        print(("PASS " if ok else "FAIL ") + name)
    return 0 if all(ok for _, ok in cases) else 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    bad = 0
    for p in argv:
        f = check_file(p)
        if f:
            bad += 1
            print(f"✖ delta-encoding: {p}")
            for x in f:
                print("    " + x)
        else:
            print(f"✓ delta-encoding: {p}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
