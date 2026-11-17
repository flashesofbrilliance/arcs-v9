#!/usr/bin/env python3
"""drift_fp_sample: how many "broken path" findings in the docs are real? Measure, draw a seeded sample, score labels.

The Docs Reconciliation page counts backticked paths in tracked markdown that do not exist ("drift").
Its headline is an upper bound with false positives, and that rate was unmeasured. This is the
re-runnable measurement. It READS git only and writes a file only when you pass --tsv.

The rule ("V2", a close rebuild of the 2026-10-06 per-file pass, not an exact copy: on that pass's base
commit 735b6afd it gives 2,292 cited paths / 178 broken / 81 files against the original 2,108 / 166 / 83):
  in every tracked *.md at REV, take each backticked token that looks like a repo path (letters, digits,
  . _ @ [ ] - with at least one slash; not a URL, not starting with ~ or /), whose first segment is a
  top-level directory of the tree and whose last segment has an extension. It is BROKEN when it is neither
  a tracked file nor a directory of the tree, and not gitignored.

Classes of the population (mechanical, by where the cite sits or what it names):
  fragment   a cite of _HANDOFFS/fragments/... (a molt deletes the fragment on purpose)
  audit      a cite inside _PATTERNS/drift-audits/ (dated audits that say a path is absent)
  archive    a cite inside _ARCHIVE/ (other)
  other      everything else

Labels for a sampled cite (assigned by a reader from the surrounding lines and git history):
  R real stale cite (a live doc points at a path that should exist or be redirected)
  H historical or intentional (a dated record that names a path as it was, or says it is absent)
  G generated or ephemeral by design (deleted on purpose, for example molted fragments)
  T template, example, planned or runtime-generated path (not a path that ever had to exist yet)
  U undecided
False positive = anything but R. U is reported separately and counted as not-R only in the upper bound.

  python3 scripts/drift_fp_sample.py --measure [--rev REV]
  python3 scripts/drift_fp_sample.py --sample 20 --seed 1018 [--rev REV] [--tsv OUT.tsv]
  python3 scripts/drift_fp_sample.py --score LABELED.tsv
  python3 scripts/drift_fp_sample.py --self-test
REV defaults to origin/main. A sample is reproducible only at the same REV and seed: record both.
Stdlib only.
"""
from __future__ import annotations

import csv
import math
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TICK = re.compile(r"`([^`\n]+)`")
PATH = re.compile(r"^[A-Za-z0-9_.@\[\]\-]+(?:/[A-Za-z0-9_.@\[\]\-]+)+/?$")
LABELS = ("R", "H", "G", "T", "U")


def git(root: Path, *a: str, stdin: str | None = None) -> str:
    return subprocess.run(["git", "-C", str(root), *a], capture_output=True, text=True, input=stdin).stdout


def population(root: Path, rev: str) -> tuple[list[tuple[str, int, str]], int, int]:
    """(sorted broken cites as (file, line, ref), md file count, cited path count)."""
    tree = set(git(root, "ls-tree", "-r", "--name-only", rev).splitlines())
    dirs = {"/".join(p.split("/")[:i]) for p in tree for i in range(1, len(p.split("/")))}
    tops = {p.split("/")[0] for p in tree if "/" in p}
    mds = sorted(p for p in tree if p.endswith(".md"))
    refs = []
    for f in mds:
        for n, line in enumerate(git(root, "show", f"{rev}:{f}").splitlines(), 1):
            for m in TICK.finditer(line):
                t = m.group(1).strip()
                if t.startswith(("http", "~", "/")) or "://" in t or not PATH.match(t):
                    continue
                t = t.rstrip("/")
                if t.split("/")[0] in tops and "." in t.split("/")[-1]:
                    refs.append((f, n, t))
    cand = [r for r in refs if not (r[2] in tree or r[2] in dirs)]
    ignored = set()
    if cand:
        out = git(root, "check-ignore", "--stdin", "-z", stdin="\0".join({t for _, _, t in cand}) + "\0")
        ignored = {x for x in out.split("\0") if x}
    return sorted(r for r in cand if r[2] not in ignored), len(mds), len(refs)


def klass(f: str, ref: str) -> str:
    if ref.startswith("_HANDOFFS/fragments/"):
        return "fragment"
    if f.startswith("_PATTERNS/drift-audits/"):
        return "audit"
    if f.startswith("_ARCHIVE/"):
        return "archive"
    return "other"


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def draw(pop: list, k: int, seed: int) -> list:
    return random.Random(seed).sample(pop, min(k, len(pop)))


def score(rows: list[dict]) -> dict:
    lab = [r["label"].strip().upper() for r in rows if r.get("label", "").strip()]
    bad = [x for x in lab if x not in LABELS]
    if bad:
        raise ValueError(f"unknown label(s): {sorted(set(bad))}")
    n = len(lab)
    real = lab.count("R")
    u = lab.count("U")
    fp, fp_hi = n - real - u, n - real          # U excluded from the point estimate, included in the upper bound
    lo, hi = wilson(n - real - u, n - u) if n - u else (0.0, 1.0)
    return {"n": n, "R": real, "H": lab.count("H"), "G": lab.count("G"), "T": lab.count("T"), "U": u,
            "fp_rate": (fp / (n - u)) if n - u else None, "ci95": (lo, hi), "fp_upper_bound": fp_hi / n if n else None}


def cmd_measure(root: Path, rev: str) -> None:
    pop, md, refs = population(root, rev)
    cls: dict[str, int] = {}
    for f, _, t in pop:
        cls[klass(f, t)] = cls.get(klass(f, t), 0) + 1
    print(f"drift_fp_sample --measure @ {rev} ({git(root, 'rev-parse', '--short', rev).strip()})")
    print(f"  md files {md} | cited paths {refs} | broken {len(pop)} | distinct broken targets {len({t for _, _, t in pop})}")
    for k in ("fragment", "audit", "archive", "other"):
        print(f"  {k:9} {cls.get(k, 0):4}")
    print(f"  after the three mechanical classes: {cls.get('other', 0)}")


def cmd_sample(root: Path, rev: str, k: int, seed: int, tsv: str | None) -> None:
    pop, _, _ = population(root, rev)
    pick = draw(pop, k, seed)
    sha = git(root, "rev-parse", rev).strip()
    print(f"# sample of {len(pick)} from {len(pop)} broken cites @ {sha[:8]}, seed {seed}")
    rows = []
    for i, (f, n, t) in enumerate(pick, 1):
        text = ""
        for j, line in enumerate(git(root, "show", f"{rev}:{f}").splitlines(), 1):
            if j == n:
                text = line.strip()[:220]
                break
        base = t.split("/")[-1]
        elsewhere = [q for q in git(root, "ls-tree", "-r", "--name-only", rev).splitlines() if q.endswith("/" + base) and q != t][:2]
        deleted = git(root, "log", rev, "--diff-filter=D", "--format=%h %ad", "--date=short", "-1", "--", t).strip()
        rows.append({"i": i, "class": klass(f, t), "file": f, "line": n, "ref": t, "text": text,
                     "same_basename_elsewhere": ";".join(elsewhere), "last_deleted": deleted, "label": "", "reason": ""})
        print(f"\n[{i}] {klass(f, t)} | {f}:{n} | ref {t}\n    {text}\n    elsewhere: {elsewhere or '-'} | deleted: {deleted or '-'}")
    if tsv:
        with open(tsv, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        print(f"\nwrote {tsv} (fill the label and reason columns, then --score)")


def cmd_score(path: str) -> int:
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    s = score(rows)
    print(f"labeled {s['n']} | R {s['R']} H {s['H']} G {s['G']} T {s['T']} U {s['U']}")
    if s["fp_rate"] is None:
        print("no decided labels")
        return 1
    lo, hi = s["ci95"]
    print(f"false-positive rate {s['fp_rate']:.0%} of decided (95% Wilson interval {lo:.0%} to {hi:.0%}); upper bound counting U as false positive {s['fp_upper_bound']:.0%}")
    return 0


def self_test() -> int:
    import os as _os  # a pre-commit hook exports GIT_DIR / GIT_INDEX_FILE; left set, the scratch git below writes to the REAL repo
    for _k in [k for k in _os.environ if k.startswith("GIT_")]:
        del _os.environ[_k]
    fails = 0

    def ok(label: str, cond: bool, detail=""):
        nonlocal fails
        print(f"  {'PASS' if cond else 'FAIL'}  {label} {'' if cond else detail}")
        fails += 0 if cond else 1

    r = Path(tempfile.mkdtemp())
    def run(*a): subprocess.run(["git", "-C", str(r), *a], capture_output=True, text=True, check=True)
    run("init", "-q"); run("config", "user.email", "t@t"); run("config", "user.name", "t"); run("config", "commit.gpgsign", "false")
    for rel, body in (("scripts/real.py", "x\n"),
                      ("docs/a.md", "ok `scripts/real.py` dir `scripts/` gone `scripts/gone.py` ign `build/out.txt` url `https://x.io/a/b.html` bare `README`\n"),
                      ("_HANDOFFS/fragments/f0.md", "x\n"),
                      ("_ARCHIVE/h.md", "Molted from `_HANDOFFS/fragments/f1.md` and `scripts/old.py`\n"),
                      ("_PATTERNS/drift-audits/d.md", "`scripts/missing.py` still does not exist\n"),
                      (".gitignore", "build/\n")):
        p = r / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(body)
    run("add", "-A", "-f"); run("commit", "-q", "-m", "init")
    pop, md, refs = population(r, "HEAD")
    broken = {t for _, _, t in pop}
    ok("an existing file and a directory are not broken", "scripts/real.py" not in broken and "scripts" not in broken, broken)
    ok("a missing file is broken", "scripts/gone.py" in broken, broken)
    ok("a gitignored path is excluded", "build/out.txt" not in broken, broken)
    ok("a URL and a bare word are not cited paths", not any("x.io" in t or t == "README" for t in broken), broken)
    ok("classes: fragment, audit, archive, other", {klass(f, t) for f, _, t in pop} == {"fragment", "audit", "archive", "other"}, [(f, t, klass(f, t)) for f, _, t in pop])
    ok("the same seed draws the same sample", draw(pop, 2, 7) == draw(pop, 2, 7) and len(draw(pop, 2, 7)) == 2)
    lo, hi = wilson(19, 20)
    ok("Wilson interval for 19 of 20 is about 76% to 99%", abs(lo - 0.764) < 0.005 and abs(hi - 0.991) < 0.005, (lo, hi))
    s = score([{"label": x} for x in ["H"] * 8 + ["G"] * 6 + ["T"] * 5 + ["R"]])
    ok("score: 19 false positives of 20", s["n"] == 20 and s["R"] == 1 and abs(s["fp_rate"] - 0.95) < 1e-9, s)
    s2 = score([{"label": x} for x in ["R", "U", "H", "H"]])
    ok("score: U is excluded from the rate but kept in the upper bound", s2["fp_rate"] == 2 / 3 and s2["fp_upper_bound"] == 0.75, s2)
    try:
        score([{"label": "Z"}])
        ok("an unknown label is refused", False)
    except ValueError:
        ok("an unknown label is refused", True)
    print("drift_fp_sample self-test: ok" if not fails else f"drift_fp_sample self-test: {fails} failed")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    def opt(name: str, default=None):
        return argv[argv.index(name) + 1] if name in argv else default
    rev = opt("--rev", "origin/main")
    if argv == ["--self-test"]:
        return self_test()
    if "--measure" in argv:
        cmd_measure(ROOT, rev)
        return 0
    if "--sample" in argv:
        cmd_sample(ROOT, rev, int(opt("--sample")), int(opt("--seed", "1018")), opt("--tsv"))
        return 0
    if "--score" in argv:
        return cmd_score(opt("--score"))
    print(__doc__.split("\n\n")[0] + "\nusage: --measure | --sample K [--seed N] [--tsv OUT] | --score FILE | --self-test (+ --rev REV)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
