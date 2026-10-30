#!/usr/bin/env python3
"""Design check for the recoil-report renderer (stdlib only).

Renders the bundled sample with recoil_report.py and fails on the class of debt that
blocked every rendered report at commit time (backlog row recoil-renderer-design-debt):
  - any em-dash in the output (title separator, renderer copy, or sample data)
  - any font-size below the 11px floor (px values, or rem values under 0.6875rem)
  - letter-spacing above 0.05em on an element that is not an uppercase label

Usage: python3 tools/recoil-report/design_check.py [path/to/recoil_report.py]
Exit 0 clean, 1 on findings. Wired into scripts/git-hooks/pre-commit for staged
changes under tools/recoil-report/.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def check(html):
    errs = []
    if "—" in html:
        errs.append(f"{html.count(chr(0x2014))} em-dash(es) in rendered output")
    for m in re.finditer(r'style="([^"]*)"', html):
        st = m.group(1)
        fs = re.search(r"font-size:\s*([\d.]+)(px|rem)", st)
        if fs:
            px = float(fs.group(1)) * (16 if fs.group(2) == "rem" else 1)
            if px < 11:
                errs.append(f"font-size {fs.group(0)} below the 11px floor")
        ls = re.search(r"letter-spacing:\s*([\d.]+)em", st)
        if ls and float(ls.group(1)) > 0.05 and "text-transform:uppercase" not in st:
            errs.append(f"letter-spacing {ls.group(1)}em on non-label text")
    return errs


def main():
    renderer = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "recoil_report.py")
    sample = os.path.join(HERE, "sample", "sample-report.json")
    out = subprocess.run([sys.executable, renderer, "render", sample],
                         capture_output=True, text=True)
    if out.returncode != 0:
        print(f"design_check: render failed: {out.stderr.strip()}", file=sys.stderr)
        return 1
    errs = check(out.stdout)
    for e in errs:
        print(f"design_check: {e}", file=sys.stderr)
    if errs:
        print(f"design_check: FAIL, {len(errs)} finding(s)", file=sys.stderr)
        return 1
    print("design_check: OK, rendered sample is clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
