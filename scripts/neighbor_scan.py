#!/usr/bin/env python3
"""neighbor_scan: before a change lands, list who else holds it, and after, who to tell.

Read-only. For each target path (or every file changed vs origin/main) it reports:

  citers     tracked files elsewhere that mention the path or its basename (neighbors)
  offspring  tracked files that share its stem or live under it (derived or generated children)
  open PRs   other open PRs whose diff touches the same file (concurrent edits)

It prints a broadcast list: the citers and offspring that a change should be announced to
(update the cite, regenerate the child, or post a note). It never edits or posts anything.
A bare basename shorter than 6 characters is not searched (too many false hits); the full
path always is.

  python3 scripts/neighbor_scan.py scripts/reconcile_epoch.py     # explicit targets
  python3 scripts/neighbor_scan.py                                # files changed vs origin/main
  python3 scripts/neighbor_scan.py --no-prs ...                   # skip the gh call
  python3 scripts/neighbor_scan.py --self-test
"""
import argparse, json, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NOISE = ("_ARCHIVE/", "_RELEASES/", "_HANDOFFS/fragments/", "runtime/specs/artifact-reuse-catalog.",
         "runtime/specs/tool-catalog.", "runtime/specs/surface-catalog.", "scripts/integrity_baseline.json")


def run(*a):
    return subprocess.run(a, cwd=ROOT, capture_output=True, text=True).stdout


def changed():
    base = run("git", "merge-base", "HEAD", "origin/main").strip() or "origin/main"
    return [f for f in run("git", "diff", "--name-only", "--diff-filter=AM", base).split("\n") if f]


def stem(path):
    return os.path.splitext(os.path.basename(path))[0]


def citers(path):
    pats = ["-e", path]
    base = os.path.basename(path)
    if len(base) >= 6:
        pats += ["-e", base]
    out = run("git", "grep", "-l", "-F", *pats, "--", ".", f":(exclude){path}")
    return sorted(o for o in out.split("\n") if o and not o.startswith(NOISE))


def offspring(path):
    s = stem(path)
    tracked = [f for f in run("git", "ls-files").split("\n") if f]
    kids = [f for f in tracked if f != path and (f.startswith(path.rstrip("/") + "/")
            or (len(s) >= 6 and stem(f).startswith(s) and os.path.dirname(f) == os.path.dirname(path)))]
    return sorted(kids)


def open_prs(path, me):
    raw = run("gh", "pr", "list", "--state", "open", "--limit", "100", "--json", "number,headRefName,files")
    try:
        prs = json.loads(raw or "[]")
    except ValueError:
        return None
    return sorted((p["number"], p["headRefName"]) for p in prs
                  if p["headRefName"] != me and any(f["path"] == path for f in p.get("files", [])))


def scan(paths, want_prs=True):
    me = run("git", "branch", "--show-current").strip()
    report = []
    for p in paths:
        report.append({"path": p, "citers": citers(p), "offspring": offspring(p),
                       "prs": open_prs(p, me) if want_prs else None})
    return report


def render(report):
    L = []
    for r in report:
        L.append(f"== {r['path']}")
        L.append(f"  citers ({len(r['citers'])}): " + (", ".join(r["citers"][:12]) or "none")
                 + (" ..." if len(r["citers"]) > 12 else ""))
        L.append(f"  offspring ({len(r['offspring'])}): " + (", ".join(r["offspring"][:8]) or "none"))
        if r["prs"] is None:
            L.append("  open PRs: not checked")
        else:
            L.append("  open PRs touching it: " + (", ".join(f"#{n} ({b})" for n, b in r["prs"]) or "none"))
    tell = sorted({c for r in report for c in r["citers"] + r["offspring"]})
    L += ["", f"Broadcast list ({len(tell)}): update the cite, regenerate the child, or note the change."]
    L += [f"  - {t}" for t in tell[:40]]
    return "\n".join(L)


def self_test():
    assert stem("scripts/neighbor_scan.py") == "neighbor_scan"
    hits = citers("scripts/integrity_gate.py")
    assert hits, "fail-on-bad: a known-cited script must have citers"
    assert citers("zz/no_such_file_anywhere_xyz.py") == [], "pass-on-good: an uncited path has none"
    assert all(not h.startswith(NOISE) for h in hits)
    print("neighbor_scan self-test: ok")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--no-prs", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    paths = a.paths or changed()
    if not paths:
        print("no targets (nothing changed vs origin/main)")
        return 0
    print(render(scan(paths, not a.no_prs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
