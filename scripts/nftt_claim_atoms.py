#!/usr/bin/env python3
"""Measure the diff atom behind each repo-backed claim in an NFTT claim ledger.

Reads a claims JSON (see _ARTIFACTS/nftt-drafts/lagging-indicator.claims.json) and writes
<name>.atoms.json beside it. For every claim with a `file`:
  atom      the smallest commit that introduced the behaviour (git pickaxe on `find`,
            or the commit that added the file when `find` is empty): sha, date, subject,
            lines added/removed in that file, files touched, and the PR that merged it.
  excerpt   up to 8 lines around the first `excerpt_grep` match, baked in so readers
            never need access to the private repo. Each excerpt passes a redaction check.
  selftest  the claim's self-test command, run now: PASS or FAIL.
Claims with `measure` get that command's output. Stdlib only; read-only on git.

usage: python3 scripts/nftt_claim_atoms.py <claims.json> [--check]
  --check   exit 1 if any excerpt fails redaction or any self-test fails
"""
import json, re, subprocess, sys
from pathlib import Path

REDACT = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+|sk-ant-|xbbpiryok|password\s*=|AUTH_SECRET=|DATABASE_URL=", re.I)


def sh(cmd, check=False):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and r.returncode:
        raise SystemExit(f"failed: {cmd}\n{r.stderr}")
    return r


def atom(path, find):
    flag = f"-S{json.dumps(find)}" if find else "--diff-filter=A"
    sha = sh(f"git log --reverse --format=%H {flag} -- {path} | head -1").stdout.strip()
    if not sha:
        return None
    meta = sh(f"git show -s --format='%h%x09%ad%x09%s' --date=short {sha}").stdout.strip().split("\t")
    num = sh(f"git show --numstat --format= {sha} -- {path}").stdout.split()
    files = len([l for l in sh(f"git show --numstat --format= {sha}").stdout.splitlines() if l.strip()])
    merge = sh(f"git log --merges --ancestry-path --reverse --format=%s {sha}..HEAD | grep -m1 -o 'pull request #[0-9]*'").stdout.strip()
    return {"sha": meta[0], "date": meta[1], "subject": meta[2].replace("\u2014", "--").replace("\u2013", "-"),
            "added": int(num[0]) if num and num[0].isdigit() else None,
            "removed": int(num[1]) if len(num) > 1 and num[1].isdigit() else None,
            "files_touched": files, "pr": merge.replace("pull request ", "") or None}


def excerpt(path, pat):
    lines = Path(path).read_text(errors="replace").splitlines()
    hit = next((i for i, l in enumerate(lines) if pat in l), None)
    if hit is None:
        return None
    lo = max(0, hit - 2)
    raw = lines[lo:lo + 8]
    clean = [l.replace("\u2014", "--").replace("\u2013", "-") for l in raw]
    return {"start": lo + 1, "lines": clean, "dashes_normalized": clean != raw}


def main(argv):
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    src = Path(argv[0])
    data = json.loads(src.read_text())
    problems = []
    for c in data["claims"]:
        if c.get("measure"):
            c["measured"] = sh(c["measure"]).stdout.strip()
        if c.get("file"):
            c["atom"] = atom(c["file"], c.get("find", ""))
            if c.get("applied_by"):
                a = sh(f"git show -s --format='%h%x09%ad%x09%s' --date=short {c['applied_by']}").stdout.strip().split("\t")
                c["applied"] = {"sha": a[0], "date": a[1], "subject": a[2]}
            ex = excerpt(c["file"], c.get("excerpt_grep", "")) if c.get("excerpt_grep") else None
            if ex and any(REDACT.search(l) for l in ex["lines"]):
                problems.append(f"{c['id']}: excerpt fails redaction, dropped")
                ex = None
            c["excerpt"] = ex
        if c.get("selftest"):
            r = sh(c["selftest"])
            c["selftest_result"] = "PASS" if r.returncode == 0 else "FAIL"
            if r.returncode:
                problems.append(f"{c['id']}: self-test FAIL ({c['selftest']})")
    out = src.with_name(src.name.replace(".claims.json", ".atoms.json"))
    out.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    for c in data["claims"]:
        a = c.get("atom") or {}
        print(f"{c['id']:4} {c['type']:9} {a.get('sha','-'):9} {str(a.get('added','')):>4}+/{str(a.get('removed','')):<4} "
              f"{a.get('pr') or '':6} {c.get('selftest_result','')}")
    for p in problems:
        print("PROBLEM", p)
    print(f"wrote {out}")
    return 1 if ("--check" in argv and problems) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
