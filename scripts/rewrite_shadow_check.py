#!/usr/bin/env python3
"""rewrite_shadow_check: fail when a host's catch-all rewrite would swallow one of that host's own pages.

Next.js rewrites chain: after `/voice -> /rosetta-voice.html` matches, later rules still see the new
path. A host catch-all like `/:path((?!fonts/).*) -> /rosetta-shell.html` then rewrites
`rosetta-voice.html` again, and the page is unreachable. That shipped on 2026-11-14 (rosetta-shell
/voice served the landing page) and is why good.arcs.care's catch-all lists its good-* pages.

Rule: for every host, every specific rewrite listed before that host's catch-all must have a
destination the catch-all pattern does not match (unless it is the catch-all's own destination).
A `:name(a|b)` parameter is expanded, so `/:seg(x|y) -> /pf-:seg.html` checks pf-x.html and pf-y.html.

Scope: next.config.ts only. src/proxy.ts runs first for some hosts and can route a path before any
rewrite sees it (resume.arcs.care is one); this check does not read it.

KNOWN lists shadowed routes found when the check was added (2026-11-15), each awaiting Zach's call on
whether the page should be reachable. They print as warnings; anything not listed fails.

Usage:
  python3 scripts/rewrite_shadow_check.py              # check next.config.ts; exit 1 on a shadowed page
  python3 scripts/rewrite_shadow_check.py --self-test  # replays the 2026-11-14 bug: must flag it, must pass the fix
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULE = re.compile(
    r'\{\s*source:\s*"((?:[^"\\]|\\.)*)",\s*destination:\s*"((?:[^"\\]|\\.)*)",\s*'
    r'has:\s*\[\s*\{\s*type:\s*"host",\s*value:\s*"([^"]+)"\s*\}\s*\]', re.S)
CATCH_ALL = re.compile(r'^/:path\((.*)\)$', re.S)
PARAM = re.compile(r':(\w+)\(([^()]*)\)')
# (host, destination) -> why it is held. Remove an entry when its route is fixed or retired.
KNOWN = {
    ("scott-profile.arcs.care", "/scott-signal.html"):
        "live 2026-11-15: /signal serves scott-profile.html; the profile page links to it; restore or retire is Zach's call",
    ("resume.arcs.care", "/resume-google-gtm.html"):
        "live 2026-11-15: /google serves resume.html (src/proxy.ts resume map, added 2026-10-30, routes first); restore or retire is Zach's call",
}


def expand(src, dst):
    """Concrete destinations for a source with a :name(a|b) parameter."""
    m = PARAM.search(src)
    if not m or f":{m.group(1)}" not in dst:
        return [dst]
    return [dst.replace(f":{m.group(1)}", alt) for alt in m.group(2).split("|")]


def rules(text):
    # TS string literal -> regex source: "\\." in the file is the regex \.
    return [(m.group(1).replace("\\\\", "\\"), m.group(2), m.group(3)) for m in RULE.finditer(text)]


def shadowed(text):
    found, seen = [], {}
    for src, dst, host in rules(text):
        m = CATCH_ALL.match(src)
        if not m:
            seen.setdefault(host, []).append((src, dst))
            continue
        try:
            pat = re.compile(r"^(?:" + m.group(1) + r")$")
        except re.error as e:
            found.append((host, src, f"catch-all pattern does not compile: {e}"))
            continue
        for s, d in seen.get(host, []):
            for real in expand(s, d):
                path = real.lstrip("/")
                if real != dst and pat.match(path):
                    found.append((host, s, real, f"destination {real} is re-rewritten to {dst} by the catch-all; "
                                                 f"add {re.escape(path)}$ to its negative lookahead"))
    return found


BUG = '''
{ source: "/voice", destination: "/rosetta-voice.html", has: [{ type: "host", value: "rosetta-shell.arcs.care" }] },
{ source: "/:path((?!fonts/|voice$).*)", destination: "/rosetta-shell.html", has: [{ type: "host", value: "rosetta-shell.arcs.care" }] },
'''
FIXED = BUG.replace("voice$).*)", "voice$|rosetta-voice\\\\.html$).*)")
# A parameterised route whose catch-all excludes every expanded destination: must not be flagged.
PARAM_OK = '''
{ source: "/:seg(teardown|logictree)", destination: "/todd-:seg.html", has: [{ type: "host", value: "t.example" }] },
{ source: "/:path((?!.*teardown|.*logictree).*)", destination: "/todd-call.html", has: [{ type: "host", value: "t.example" }] },
'''
PARAM_BAD = PARAM_OK.replace("|.*logictree).*)", ").*)")


def self_test():
    bad, good = shadowed(BUG), shadowed(FIXED)
    pok, pbad = shadowed(PARAM_OK), shadowed(PARAM_BAD)
    ok = len(bad) == 1 and not good and not pok and len(pbad) == 1
    print(f"self-test: bug flagged {len(bad)} (want 1), fix {len(good)} (want 0), "
          f"param ok {len(pok)} (want 0), param missing {len(pbad)} (want 1): {'PASS' if ok else 'FAIL'}")
    return ok


def main():
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test() else 1)
    text = (ROOT / "next.config.ts").read_text()
    n = len(rules(text))
    new, held, hit = [], [], set()
    for host, src, real, why in shadowed(text):
        key = (host, real)
        (held if key in KNOWN else new).append((host, src, real, why))
        hit.add(key)
    for host, src, real, why in held:
        print(f"⚠ held {host}: rewrite {src}: {KNOWN[(host, real)]}")
    for key in sorted(set(KNOWN) - hit):
        print(f"✖ stale KNOWN entry {key}: no longer shadowed; remove it from KNOWN")
    for host, src, real, why in new:
        print(f"✖ {host}: rewrite {src}: {why}")
    if new or set(KNOWN) - hit:
        sys.exit(1)
    print(f"✓ rewrite-shadow: {n} host rewrites, no new page swallowed by its host's catch-all ({len(held)} held)")


if __name__ == "__main__":
    main()
