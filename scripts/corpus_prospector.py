#!/usr/bin/env python3
"""corpus_prospector.py — index the addressable corpus and find dormant ore.

Deterministic, stdlib-only. Loop 1 of the harvest cycle (index → catalog → organize → bundle),
see `_CANON/flora-and-fauna.md` §IX. Two commands:

  python3 scripts/corpus_prospector.py index   [--out FILE.jsonl]   # every addressable file, classed + graded
  python3 scripts/corpus_prospector.py orphans [--out FILE.jsonl]   # files with zero inbound references

What "addressable" means here: any tracked file (plus untracked files inside the artifact/state
folders, flagged tracked=false) that belongs to one of the ARCS artifact classes below. Source code
under src/ and node_modules/ is not corpus and is skipped.

Grading is a *training-reuse* heuristic, not a judgment of worth. Four signals, one point each:
  dated        — an ISO date in the path or the first 4KB
  provenance   — a provenance / source / witnessed / commit marker in the first 4KB, or front-matter
  referenced   — at least one other file mentions this file's name (inbound_refs > 0).
                 Index/landmark basenames (README, index.*, ledgers) and stems under 6 chars are
                 NOT scanned: ref_scanned=false, inbound_refs=null, and they are never orphans.
  well_formed  — JSON/JSONL parses; markdown has a top-level heading or front-matter
Grade A = 4, B = 3, C = 2, D = 0–1. A `secret_risk` hit caps the grade at D regardless
(Kintsugi: the break is shown, never silently patched; nothing is deleted by this script).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import subprocess
import sys
from collections import defaultdict

# ---------------------------------------------------------------- classification
# Order matters: first match wins. (regex on the repo-relative path)
CLASS_RULES = [
    ("ADR",       r"^_DECISIONS/ADR-\d+"),
    ("COLLISION", r"^_DECISIONS/CANON-COLLISION"),
    ("DECISION",  r"^_DECISIONS/"),
    ("DEWY",      r"\.dewy\.json$|session-decisions"),
    ("APEX",      r"^_CANON/apex-"),
    ("PROVERB",   r"^_CANON/tao-proverbs\.jsonl$"),
    ("MOMENT",    r"^_CANON/great-moments\.jsonl$"),
    ("CANON",     r"^_CANON/"),
    ("WITNESS",   r"^_STATE/witness/"),
    ("KINTSUGI",  r"kintsugi"),
    ("HANDOFF",   r"^_ARCHIVE/handoffs\.md$|^_STATE/handoff-|^CLAUDE\.md$"),
    ("MEMORY",    r"^_MEMORY/|^MEMORY\.md$|^_ARCHIVE/memory-archive\.md$"),
    ("SEED",      r"^_SEEDS/"),
    ("PATTERN",   r"^_PATTERNS/"),
    ("QUEUE",     r"^_QUEUE/"),
    ("SCRATCH",   r"^_INBOX/|/tmp/|/scratch/|-backup-|DRAFT|\.tmp$|~$"),
    ("RECOIL",    r"^runtime/recoil/"),
    ("WARROOM",   r"^runtime/warroom/"),
    ("SPEC",      r"^runtime/specs/|^_SPECS/|^runtime/flows/"),
    ("RUNTIME",   r"^runtime/"),
    ("ARTIFACT",  r"^_ARTIFACTS/|^analysis/|^archive/|^docs/"),
    ("STATE",     r"^_STATE/"),
    ("SKILL",     r"^\.claude/skills/"),
    ("COMMAND",   r"^\.claude/commands/"),
    ("AGENT",     r"^\.claude/agents/"),
    ("SCRIPT",    r"^scripts/"),
    ("OPERATOR",  r"^operators/"),
    ("WORLD",     r"^WORLD\.md$|^AGENTS\.md$|^\.claude/arcs-canon\.md$"),
]
CORPUS_CLASSES = {c for c, _ in CLASS_RULES}
# classes that are instruments, not corpus — indexed for the roster, never graded as training data
INSTRUMENT_CLASSES = {"SKILL", "COMMAND", "AGENT", "SCRIPT", "OPERATOR"}

TEXT_EXT = {".md", ".json", ".jsonl", ".txt", ".yaml", ".yml", ".py", ".ts", ".tsx", ".js", ".mjs",
            ".html", ".css", ".csv", ".sh", ".sql", ".toml", ".cfg", ".ini", ".mdx", ".plist"}
BINARY_EXT = {".png", ".jpg", ".jpeg", ".pdf", ".gif", ".webp", ".heic", ".mov", ".mp4", ".zip"}
INDEX_BASENAMES = {"README.md", "index.md", "index.json", "index.jsonl", "ledger.json",
                   "ledger.jsonl", "_oracle.json", "registry-artifacts.jsonl"}
UNTRACKED_SCAN_DIRS = ("_ARTIFACTS/", "_STATE/", "_INBOX/", "_QUEUE/", "_PATTERNS/", "runtime/")

SELF_OUTPUT_RE = re.compile(r"corpus-index|ore-ledger|orphan-ore|prospecting-survey")
DATE_RE = re.compile(r"20\d{2}-\d{2}-\d{2}")
PROV_RE = re.compile(r"provenance|witnessed|source[:_ ]|commit[:_ ]|minted|generated[- ]by|\bsha\b", re.I)
SECRET_RE = re.compile(
    r"(sk-ant-[A-Za-z0-9\-_]{20,}|sk-[A-Za-z0-9]{32,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}"
    r"|xox[abp]-[A-Za-z0-9\-]{20,}|-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----"
    r"|(?:password|passwd|secret|api[_-]?key)\s*[=:]\s*['\"][^'\"\s]{8,}['\"])", re.I)


def classify(path: str) -> str | None:
    for cls, rx in CLASS_RULES:
        if re.search(rx, path):
            return cls
    return None


# ---------------------------------------------------------------- git helpers
def sh(*args: str) -> str:
    return subprocess.check_output(list(args), text=True, errors="ignore")


def repo_root() -> str:
    return sh("git", "rev-parse", "--show-toplevel").strip()


def is_shallow() -> bool:
    return os.path.exists(os.path.join(".git", "shallow"))


def last_commit_dates(paths_prefixes) -> dict[str, str]:
    """path -> last commit date, from one git log walk (fast). Unreliable on a shallow clone."""
    dates: dict[str, str] = {}
    log = sh("git", "log", "--format=%cs", "--name-only", "--", *paths_prefixes)
    cur = None
    for line in log.split("\n"):
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", line):
            cur = line
        elif line and cur and line not in dates:
            dates[line] = cur
    return dates


# ---------------------------------------------------------------- core
def build_index(compute_refs: bool = True) -> tuple[list[dict], dict]:
    tracked = [f for f in sh("git", "ls-files").split("\n") if f and not f.startswith("node_modules/")]
    untracked = [f for f in sh("git", "ls-files", "--others", "--exclude-standard").split("\n")
                 if f and f.startswith(UNTRACKED_SCAN_DIRS)]
    files = [(f, True) for f in tracked] + [(f, False) for f in untracked]

    # corpus text for inbound-ref search (tracked text files only; capped read)
    corpus: dict[str, str] = {}
    for f, _ in files:
        # this script's own outputs list every path — they must never count as citations
        if SELF_OUTPUT_RE.search(f):
            continue
        if os.path.splitext(f)[1].lower() in TEXT_EXT and os.path.isfile(f):
            try:
                with open(f, "r", errors="ignore") as fh:
                    corpus[f] = fh.read(2_000_000)
            except OSError:
                pass

    shallow = is_shallow()
    dates = last_commit_dates(["."])
    today = _dt.date.today()

    rows: list[dict] = []
    for f, is_tracked in files:
        cls = classify(f)
        if cls is None or not os.path.isfile(f):
            continue
        base = os.path.basename(f)
        stem, ext = os.path.splitext(base)
        ext = ext.lower()
        size = os.path.getsize(f)
        head = corpus.get(f, "")[:4096]

        # --- inbound references (skip index-y basenames and instruments; too noisy / not the point)
        refs: list[str] = []
        # Triune rule: a file we never scanned for citations is UNDEFINED, not NULL — it must not be
        # reported as an orphan. Index/landmark basenames and very short stems are never scanned.
        ref_scanned = compute_refs and base not in INDEX_BASENAMES and len(stem) >= 6 and cls not in INSTRUMENT_CLASSES
        if ref_scanned:
            for g, text in corpus.items():
                if g == f:
                    continue
                if base in text or (len(stem) >= 10 and stem in text):
                    refs.append(g)

        # --- quality signals
        dated = bool(DATE_RE.search(f) or DATE_RE.search(head))
        frontmatter = head.startswith("---") or head.startswith("{") or "**Status:**" in head[:800]
        provenance = bool(PROV_RE.search(head)) or frontmatter
        well_formed = True
        if ext in (".json",):
            try:
                json.loads(corpus.get(f, "") or "null")
            except Exception:
                well_formed = False
        elif ext == ".jsonl":
            try:
                for line in (corpus.get(f, "") or "").split("\n"):
                    if line.strip():
                        json.loads(line)
            except Exception:
                well_formed = False
        elif ext == ".md":
            well_formed = head.lstrip().startswith("#") or head.startswith("---")
        elif ext in BINARY_EXT:
            well_formed = True
        secret_risk = bool(SECRET_RE.search(corpus.get(f, "")[:200_000])) if f in corpus else False

        referenced = (len(refs) > 0) if ref_scanned else True  # unscanned landmarks get the benefit of the doubt
        score = int(dated) + int(provenance) + int(referenced) + int(well_formed)
        grade = {4: "A", 3: "B", 2: "C"}.get(score, "D")
        if secret_risk:
            grade = "D"
        if cls in INSTRUMENT_CLASSES:
            grade = None  # instruments are rostered, not graded

        last = dates.get(f)
        rows.append({
            "path": f, "class": cls, "tracked": is_tracked, "bytes": size, "ext": ext or None,
            "binary": ext in BINARY_EXT,
            "last_commit": last, "age_days": (today - _dt.date.fromisoformat(last)).days if last else None,
            "ref_scanned": ref_scanned, "inbound_refs": len(refs) if ref_scanned else None, "referenced_by": refs[:5],
            "dated": dated, "provenance": provenance, "well_formed": well_formed,
            "secret_risk": secret_risk, "score": score, "grade": grade,
        })

    meta = {"generated": today.isoformat(), "shallow_clone": shallow,
            "age_caveat": "git history is shallow; age_days/last_commit are lower bounds only" if shallow else None,
            "files_indexed": len(rows)}
    return rows, meta


def summarize(rows: list[dict]) -> dict:
    by = defaultdict(lambda: {"n": 0, "bytes": 0, "orphans": 0, "untracked": 0, "secret_risk": 0,
                              "grades": {"A": 0, "B": 0, "C": 0, "D": 0}})
    for r in rows:
        b = by[r["class"]]
        b["n"] += 1
        b["bytes"] += r["bytes"]
        if r["ref_scanned"] and r["inbound_refs"] == 0:
            b["orphans"] += 1
        if not r["tracked"]:
            b["untracked"] += 1
        if r["secret_risk"]:
            b["secret_risk"] += 1
        if r["grade"]:
            b["grades"][r["grade"]] += 1
    return dict(sorted(by.items(), key=lambda kv: -kv[1]["n"]))


def print_summary(rows: list[dict], meta: dict) -> None:
    s = summarize(rows)
    print(f"indexed={meta['files_indexed']}  shallow_clone={meta['shallow_clone']}")
    if meta.get("age_caveat"):
        print(f"caveat: {meta['age_caveat']}")
    print(f"\n{'class':<11}{'n':>6}{'KB':>9}{'orphan':>8}{'untrk':>7}{'A':>5}{'B':>5}{'C':>5}{'D':>5}{'secret':>8}")
    for cls, b in s.items():
        g = b["grades"]
        print(f"{cls:<11}{b['n']:>6}{b['bytes']//1024:>9}{b['orphans']:>8}{b['untracked']:>7}"
              f"{g['A']:>5}{g['B']:>5}{g['C']:>5}{g['D']:>5}{b['secret_risk']:>8}")
    graded = [r for r in rows if r["grade"]]
    if graded:
        dist = defaultdict(int)
        for r in graded:
            dist[r["grade"]] += 1
        tot = len(graded)
        print(f"\ncorpus files graded={tot}  " + "  ".join(f"{k}={dist[k]} ({100*dist[k]//tot}%)" for k in "ABCD"))
        print(f"training-grade (A+B)={dist['A']+dist['B']} ({100*(dist['A']+dist['B'])//tot}%)")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["index", "orphans"])
    ap.add_argument("--out", help="write JSONL rows here (one file per line)")
    ap.add_argument("--top", type=int, default=30, help="orphans: how many rows to print")
    a = ap.parse_args(argv)

    os.chdir(repo_root())
    rows, meta = build_index()

    if a.command == "index":
        out_rows = rows
        print_summary(rows, meta)
    else:
        out_rows = [r for r in rows if r["ref_scanned"] and r["inbound_refs"] == 0]
        print(f"orphans={len(out_rows)} of {len(rows)} indexed  bytes={sum(r['bytes'] for r in out_rows)}"
              f"  shallow_clone={meta['shallow_clone']}")
        for r in sorted(out_rows, key=lambda r: -r["bytes"])[:a.top]:
            print(f"{r['bytes']//1024:>6}KB  {r['class']:<9} {r['grade'] or '-'}  {r['path']}")

    if a.out:
        with open(a.out, "w") as fh:
            fh.write(json.dumps({"_meta": meta}) + "\n")
            for r in out_rows:
                fh.write(json.dumps(r) + "\n")
        print(f"\nwrote {len(out_rows)} rows → {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
