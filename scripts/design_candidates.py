#!/usr/bin/env python3
"""design_candidates: a trial lane for design-system changes that are not canon yet.

Why (Zach, 2026-11-13): the render gates are right to fail a page that departs from the kit, but a
deliberate trial of a new token, motion value or template fails the same way, and the only way past
was a one-off exemption in a gate or a page-level waiver with no owner and no end date. This file is
the middle lane between drift and canon.

How it works:
  1. A candidate is a row in runtime/specs/design-candidates.json: id, kind, owner, reason, added,
     expires, pages (globs), and the values it trials:
       "tokens":    {"--name": "value"}  CSS custom properties (token_source_gate, motion_policy_gate)
       "templates": {"name": {...}}      same shape as src/ui-kit/templates.json (component_source_gate)
  2. A page opts in by name:  <!-- @arcs-candidate: <id> -->
  3. The gates accept a candidate's values only on a page that declares it, only while it is
     unexpired. Anything not in the registry still fails exactly as before.
  4. Past its expires date a candidate stops counting, so the gate fails again until it graduates
     (values move into _tokens.css / the kit / templates.json, DESIGN.md gets a dated amendment, the
     row and the page markers are removed, in one PR) or is dropped.

Usage:
  python3 scripts/design_candidates.py --check     registry well-formed; every marker names a live
                                                   candidate whose pages glob covers that page (exit 1)
  python3 scripts/design_candidates.py --list      the trial board: what is in trial, where, until when
  python3 scripts/design_candidates.py --self-test
Library: declared(text), tokens_for(text), templates_for(text) for the gates.
"""
import datetime, fnmatch, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.environ.get("ARCS_DESIGN_CANDIDATES") or os.path.join(ROOT, "runtime", "specs", "design-candidates.json")  # env: tests only
MARK_RE = re.compile(r'<!--\s*@arcs-candidate:\s*([a-z0-9-]+)\s*-->', re.I)
KINDS = {"token", "motion", "template", "rule"}
REQUIRED = ("id", "kind", "owner", "reason", "added", "expires", "pages")


def load(path=None):
    path = path or REGISTRY
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh).get("candidates", [])
    except FileNotFoundError:
        return []


def today():
    return datetime.date.today().isoformat()


def live(c, on=None):
    return str(c.get("expires", "")) >= (on or today())


def declared(text, rows=None, on=None):
    """Live candidates this page declares, by marker. Unknown or expired ids are left out."""
    rows = load() if rows is None else rows
    by = {c.get("id"): c for c in rows}
    return [by[i] for i in dict.fromkeys(m.lower() for m in MARK_RE.findall(text)) if i in by and live(by[i], on)]


def tokens_for(text, rows=None, on=None):
    out = {}
    for c in declared(text, rows, on):
        out.update({k: str(v).strip() for k, v in (c.get("tokens") or {}).items()})
    return out


def templates_for(text, rows=None, on=None):
    out = {}
    for c in declared(text, rows, on):
        out.update(c.get("templates") or {})
    return out


def problems(rows, pages, on=None):
    """pages: {relpath: text}. Returns a list of strings; empty means clean."""
    out, seen = [], set()
    on = on or today()
    for c in rows:
        cid = c.get("id", "?")
        miss = [k for k in REQUIRED if not c.get(k)]
        if miss:
            out.append(f"{cid}: missing {', '.join(miss)}")
        if cid in seen:
            out.append(f"{cid}: duplicate id")
        seen.add(cid)
        if c.get("kind") not in KINDS:
            out.append(f"{cid}: kind must be one of {', '.join(sorted(KINDS))}")
        if not (c.get("tokens") or c.get("templates") or c.get("kind") == "rule"):
            out.append(f"{cid}: trials nothing (give tokens or templates)")
        if c.get("expires") and not live(c, on):
            out.append(f"{cid}: EXPIRED {c['expires']}: graduate it into the kit (one PR, DESIGN.md amendment) or drop it")
    by = {c.get("id"): c for c in rows}
    for rel, text in sorted(pages.items()):
        for cid in dict.fromkeys(m.lower() for m in MARK_RE.findall(text)):
            c = by.get(cid)
            if not c:
                out.append(f"{rel}: declares unknown candidate '{cid}'")
            elif not any(fnmatch.fnmatch(rel, g) for g in c.get("pages", [])):
                out.append(f"{rel}: declares '{cid}' but is not in its pages list")
    return out


def tracked_pages():
    files = subprocess.run(["git", "-C", ROOT, "grep", "-l", "@arcs-candidate", "--", "*.html"], capture_output=True, text=True).stdout.split()
    out = {}
    for rel in files:
        try:
            text = open(os.path.join(ROOT, rel), encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        if "@arcs-candidate" in text:
            out[rel] = text
    return out


def board(rows, pages):
    if not rows:
        print("design candidates: none in trial")
        return
    for c in sorted(rows, key=lambda r: r.get("expires", "")):
        used = [p for p, t in pages.items() if c.get("id") in [m.lower() for m in MARK_RE.findall(t)]]
        state = "live" if live(c) else "EXPIRED"
        vals = ", ".join(list(c.get("tokens") or {}) + list(c.get("templates") or {}))
        print(f"{c.get('id')}  [{state} until {c.get('expires')}]  owner {c.get('owner')}  kind {c.get('kind')}")
        print(f"   trials: {vals or '(rule)'}")
        print(f"   on: {', '.join(used) or '(no page yet)'}")
        print(f"   why: {c.get('reason')}")


def self_test():
    row = {"id": "t-mast", "kind": "token", "owner": "Zach", "reason": "trial", "added": "2026-11-13",
           "expires": "2026-12-01", "pages": ["public/gravity-*.html"], "tokens": {"--mast-cyan": "#00F0FF"},
           "templates": {"trial-tpl": {"mode": "persuade", "signature_selectors": [".x"], "min_signatures": 1}}}
    old = dict(row, id="t-old", expires="2026-11-01")
    page = "<!-- @arcs-candidate: t-mast -->"
    cases = [
        ("declared live", tokens_for(page, [row], "2026-11-13") == {"--mast-cyan": "#00F0FF"}),
        ("template merged", "trial-tpl" in templates_for(page, [row], "2026-11-13")),
        ("expired ignored", tokens_for("<!-- @arcs-candidate: t-old -->", [old], "2026-11-13") == {}),
        ("undeclared ignored", tokens_for("<p>no marker</p>", [row], "2026-11-13") == {}),
        ("clean registry", problems([row], {"public/gravity-brief.html": page}, "2026-11-13") == []),
        ("expired flagged", any("EXPIRED" in p for p in problems([old], {}, "2026-11-13"))),
        ("unknown id flagged", any("unknown" in p for p in problems([row], {"public/x.html": "<!-- @arcs-candidate: nope -->"}, "2026-11-13"))),
        ("page outside glob flagged", any("not in its pages" in p for p in problems([row], {"public/other.html": page}, "2026-11-13"))),
        ("missing field flagged", any("missing" in p for p in problems([{"id": "bad", "kind": "token", "tokens": {"--a": "1"}}], {}, "2026-11-13"))),
        ("duplicate flagged", any("duplicate" in p for p in problems([row, row], {}, "2026-11-13"))),
    ]
    ok = all(g for _, g in cases)
    for label, g in cases:
        print(f"  [{'ok ' if g else 'XX '}] {label}")
    print("design_candidates self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    rows = load()
    if "--list" in argv:
        board(rows, tracked_pages())
        return 0
    if "--check" in argv:
        bad = problems(rows, tracked_pages())
        for p in bad:
            print(f"✖ design_candidates {p}")
        if not bad:
            print(f"✓ design_candidates: {len(rows)} candidate(s) in trial, registry and markers consistent")
        return 1 if bad else 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
