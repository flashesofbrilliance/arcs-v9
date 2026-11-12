#!/usr/bin/env python3
"""Share-control gate (Frustration Gate, AGENTS.md gotcha 15; 2026-11-12).

Bug class: a share control on a gated page copies the page's own URL, so every
outside reader hits a sign-in wall or a 404. Seen four times: war-room hosts
(pruned 2026-10-07), jobs.arcs.care (2026-09-07), the brief reflect page
(owner-only since e5267871), and the war room "COPY LINK" emailed to a
counterpart (2026-11-11).

Rule, per file under src/ that has a share control (clipboard write, sms:,
x.com/intent, navigator.share):
  1. no line may use window.location.href, unless it carries the marker
     "share-gate: internal" (a deliberately internal, labelled copy);
  2. no sms:/x.com/intent line may build a raw /brief/${...}, /recoil/${...}
     or /scan/${...} path (those routes are owner- or admin-only).
Shares go through a minted path instead (src/lib/briefShare.ts, ADR-037, or a
recoil external twin).

  python3 scripts/share_control_gate.py            # scan src/, exit 1 on a hit
  python3 scripts/share_control_gate.py --self-test
"""
import pathlib, re, sys, tempfile

SHARE = re.compile(r"clipboard\.writeText|sms:\?body|x\.com/intent|navigator\.share\(")
HREF = re.compile(r"window\.location\.href")
OUTBOUND = re.compile(r"sms:\?body|x\.com/intent")
GATED = re.compile(r"/(brief|recoil|scan)/\$\{")
MARK = "share-gate: internal"


def scan_text(path, text):
    hits = []
    if not SHARE.search(text):
        return hits
    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        if HREF.search(line) and MARK not in line:
            hits.append(f"{path}:{i}: share control copies window.location.href (mint a share path, or mark '{MARK}' and label it internal)")
        if OUTBOUND.search(line) and GATED.search(line):
            hits.append(f"{path}:{i}: outbound share builds a gated /brief|/recoil|/scan path (mint a share path)")
    # helper like `const briefUrl = () => `${origin}/brief/${id}`` fed to sms/x
    for i, line in enumerate(lines, 1):
        m = re.match(r"\s*const (\w+)\s*=\s*\(\)\s*=>.*" + GATED.pattern, line)
        if m and any(OUTBOUND.search(l) and m.group(1) + "(" in l for l in lines):
            hits.append(f"{path}:{i}: '{m.group(1)}' builds a gated path and feeds an outbound share")
    return hits


def scan(root):
    hits = []
    for p in sorted(pathlib.Path(root).rglob("*")):
        if p.suffix in (".ts", ".tsx") and "node_modules" not in p.parts:
            hits += scan_text(p, p.read_text(errors="ignore"))
    return hits


def self_test():
    bad = [
        'await navigator.clipboard.writeText(window.location.href)',
        'const briefUrl = () => `${window.location.origin}/brief/${receiptId}`\nwindow.open(`sms:?body=${briefUrl()}`)',
        'window.open(`https://x.com/intent/tweet?url=${origin}/recoil/${id}`)',
    ]
    good = [
        'const url = await getShareUrl()\nawait navigator.clipboard.writeText(url)',
        f'const url = x ? share : window.location.href // {MARK}\nawait navigator.clipboard.writeText(url)',
        'const here = window.location.href  // no share control in this file',
    ]
    ok = all(scan_text("bad", b) for b in bad) and not any(scan_text("good", g) for g in good)
    print("share_control_gate self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    root = pathlib.Path(__file__).resolve().parent.parent / "src"
    hits = scan(root)
    for h in hits:
        print(h, file=sys.stderr)
    print(f"share_control_gate: {len(hits)} hit(s)")
    sys.exit(1 if hits else 0)
