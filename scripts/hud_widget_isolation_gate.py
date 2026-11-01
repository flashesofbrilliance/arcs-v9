#!/usr/bin/env python3
"""Isolation gate for HUD widgets (row hud-widget-views-admin-mount).

A widget file in src/organisms/hud/ may import only: tokens and atoms (@/ui/...), react, and its own
read file, the shared face, reading types and snap. Importing another widget fails.
Widgets: fidelity conviction clarity coherence consonance (.tsx and .read.ts).
Usage: hud_widget_isolation_gate.py [--check] [--self-test]
"""
import re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / "src/organisms/hud"
W = ["fidelity", "conviction", "clarity", "coherence", "consonance"]
IMP = re.compile(r"""(?:from|import)\s*['"]([^'"]+)['"]""")

def violations(name: str, src: str):
    own = name.split(".")[0]
    out = []
    for spec in IMP.findall(src):
        base = spec.rsplit("/", 1)[-1].split(".")[0]
        if spec.startswith(("./", "../")) and base in W and base != own:
            out.append(f"{name} imports another widget: {spec}")
        if "organisms/hud/" in spec and base in W and base != own:
            out.append(f"{name} imports another widget: {spec}")
    return out

def check():
    bad = []
    for f in sorted(D.glob("*")):
        if f.suffix in (".ts", ".tsx") and f.name.split(".")[0] in W:
            bad += violations(f.name, f.read_text())
    return bad

def self_test():
    assert violations("clarity.tsx", "import { x } from './fidelity'"), "known-bad must fail"
    assert violations("clarity.tsx", "import { x } from '@/organisms/hud/coherence.read'"), "known-bad (alias) must fail"
    assert not violations("clarity.tsx", "import { x } from './clarity.read'\nimport { Gauge } from '@/ui/Gauge'\nimport { y } from './WidgetFace'"), "known-good must pass"
    print("self-test ok")

if __name__ == "__main__":
    if "--self-test" in sys.argv: self_test()
    bad = check()
    for b in bad: print("FAIL", b)
    print(f"{len(bad)} violation(s)")
    sys.exit(1 if bad else 0)
