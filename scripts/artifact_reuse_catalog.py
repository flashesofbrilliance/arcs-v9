#!/usr/bin/env python3
"""artifact_reuse_catalog: a read-only reuse catalog of _ARTIFACTS/, placed four ways.

Why: the repo holds many valuable documents (1,800+ tracked files in _ARTIFACTS/) made to be
reproduced, repurposed and upcycled. This lists every top-level entry once, with four placements
named for the operators that would order them (operators/docs/PERIODIC-TABLE.md):

  Taxonomist (27)  what it IS: family, kind, class (a Dewey-style shelf)
  Librarian  (21)  what it costs to reuse vs what it is worth: read effort (tokens / 8000, the
                   Librarian's own tokens_per_step) against inbound references and recency
  Accountant (19)  whether it got used: a PROXY only (served by a live route / referenced / orphan);
                   there is no per-artifact outcome data, and the catalog says so
  Auditor    (28)  provenance and versions: first and last commit, commit count, draft or evidence marks
  + "reuse as"     template, evidence, copy, design, data or archive candidate (rules below, heuristic)

Nothing is moved, renamed or deleted. Output: runtime/specs/artifact-reuse-catalog.{json,md}.

  python3 scripts/artifact_reuse_catalog.py            # write both files
  python3 scripts/artifact_reuse_catalog.py --self-test

Heuristics are labelled as such in the output. Stdlib only; reads git and the working tree.
"""
import argparse, collections, datetime as dt, json, math, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ART = "_ARTIFACTS"
OUT_JSON = os.path.join(ROOT, "runtime", "specs", "artifact-reuse-catalog.json")
OUT_MD = os.path.join(ROOT, "runtime", "specs", "artifact-reuse-catalog.md")
TOKENS_PER_STEP = 8000          # same constant as runtime/specs/read-friction-tiers.json
STALE_DAYS = 90
SERVE_FILES = ("next.config.ts", "src/proxy.ts", "vercel.json")

# Dewey-style shelves by name prefix. Order matters: first match wins. Everything else is "Unshelved".
SHELVES = [
    ("forge", "300 Counterpart packages (forge)"),
    ("resume", "400 Resume and application sets"),
    ("prl", "500 Client engagements: PRL"),
    ("louisville", "500 Client engagements: Louisville"),
    ("jeben", "500 Client engagements: Jeben"),
    ("brooks", "500 Client engagements: Brooks"),
    ("vico", "500 Client engagements: Vico"),
    ("scott", "500 Client engagements: Scott"),
    ("todd", "500 Client engagements: Todd"),
    ("ahmed", "500 Client engagements: Ahmed"),
    ("recoil", "600 Recoil and calls"),
    ("pitch", "700 Pitch bundles"),
    ("closing", "800 Closing-the-loop series"),
    ("brier", "800 Closing-the-loop series"),
    ("prereg", "800 Closing-the-loop series"),
    ("arcs", "100 ARCS explorers and canon"),
    ("apex", "100 ARCS explorers and canon"),
    ("atlas", "100 ARCS explorers and canon"),
    ("terrain", "100 ARCS explorers and canon"),
    ("vision", "100 ARCS explorers and canon"),
    ("wing", "100 ARCS explorers and canon"),
]


def git(*a):
    return subprocess.run(["git", "-C", ROOT, *a], capture_output=True, text=True).stdout


def shelf(name):
    base = name.lower()
    for pre, label in SHELVES:
        if base.startswith(pre):
            return label
    return "900 Unshelved"


def kind(entry_files, is_dir):
    if is_dir:
        exts = collections.Counter(os.path.splitext(f)[1].lower() for f in entry_files)
        top = exts.most_common(1)[0][0] if exts else ""
        return "bundle (" + (top.lstrip(".") or "mixed") + ")"
    ext = os.path.splitext(entry_files[0])[1].lower()
    return {".html": "page", ".md": "doc", ".json": "data", ".jsonl": "data", ".pdf": "pdf",
            ".png": "image", ".jpg": "image", ".csv": "data"}.get(ext, ext.lstrip(".") or "file")


def reuse_as(name, kind_, files, refs, age_days):
    low = name.lower()
    if refs == 0 and age_days is not None and age_days > STALE_DAYS:
        return "archive candidate"
    if low.startswith("forge") and kind_.startswith("bundle"):
        return "template (swap the counterpart)"
    if low.endswith(".evidence.jsonl") or kind_ == "data":
        return "evidence / data"
    if kind_ == "page" or (kind_.startswith("bundle") and "html" in kind_):
        return "design / layout"
    if kind_ == "doc":
        return "copy"
    return "reference"


def entries():
    tracked = [f for f in git("ls-files", ART).split("\n") if f]
    groups = collections.defaultdict(list)
    for f in tracked:
        rest = f[len(ART) + 1:]
        groups[rest.split("/")[0]].append(f)
    return groups


def inbound(name, own_prefix):
    """Distinct tracked files elsewhere that mention the entry by name (a lineage proxy)."""
    # The full path always counts; the bare name counts only when it is distinctive (has a dot or hyphen),
    # so a common word like "sources" or "blog" does not collect every mention of the word.
    pats = ["-e", f"{ART}/{name}"] + (["-e", name] if ("." in name or "-" in name) else [])
    out = git("grep", "-l", "-F", *pats, "--", ".",
              f":(exclude){own_prefix}", ":(exclude)runtime/specs/artifact-reuse-catalog.md",
              ":(exclude)runtime/specs/artifact-reuse-catalog.json", ":(exclude)_RELEASES").split("\n")
    return [o for o in out if o]


def build(today=None):
    today = today or dt.date.today()
    rows = []
    for name, files in sorted(entries().items()):
        is_dir = any("/" in f[len(ART) + 1:] for f in files)
        path = f"{ART}/{name}"
        size = 0
        for f in files:
            p = os.path.join(ROOT, f)
            if os.path.exists(p):
                size += os.path.getsize(p)
        tokens = size / 4.0
        log = [d for d in git("log", "--format=%ad", "--date=short", "--", path).split("\n") if d]
        first, last = (log[-1], log[0]) if log else (None, None)
        age = (today - dt.date.fromisoformat(last)).days if last else None
        refs = inbound(name, path)
        served = [r for r in refs if r in SERVE_FILES]
        n_refs = len(refs)
        if served:
            fate = "served by a live route"
        elif n_refs:
            fate = f"referenced by {n_refs} file(s)"
        else:
            fate = "orphan (no inbound reference)"
        k = kind(files, is_dir)
        effort = tokens / TOKENS_PER_STEP + (1.0 if is_dir else 0.5)
        recency = 1.0 if age is None else max(0.2, 1.0 - age / 365.0)
        rank = round(math.log1p(n_refs) * recency / (1.0 + effort), 4)
        marks = []
        if re.search(r"draft", name, re.I):
            marks.append("draft")
        if ".evidence." in name:
            marks.append("evidence file")
        if re.search(r"v\d+|\d{4}-\d{2}-\d{2}", name):
            marks.append("dated or versioned name")
        rows.append({
            "name": name, "path": path, "shelf": shelf(name), "kind": k, "files": len(files),
            "bytes": size, "read_effort_steps": round(effort, 2),
            "inbound_refs": n_refs, "fate_proxy": fate, "served": bool(served),
            "first_commit": first, "last_commit": last, "commits": len(log), "age_days": age,
            "marks": marks, "reuse_as": reuse_as(name, k, files, n_refs, age), "rank": rank,
        })
    return rows


def render_md(rows, today):
    by_shelf = collections.defaultdict(list)
    for r in rows:
        by_shelf[r["shelf"]].append(r)
    start = sorted(rows, key=lambda r: -r["rank"])[:15]
    L = ["# _ARTIFACTS reuse catalog", "",
         f"Generated {today} by scripts/artifact_reuse_catalog.py. {len(rows)} top-level entries, "
         f"{sum(r['files'] for r in rows)} tracked files. Read-only: nothing was moved or renamed.", "",
         "Four placements per entry: **Taxonomist** (shelf and kind), **Librarian** (read effort in steps of "
         f"{TOKENS_PER_STEP} tokens against inbound references and recency), **Accountant** (usage, a proxy only: "
         "there is no per-artifact outcome data), **Auditor** (first and last commit, commit count, draft or "
         "dated marks). **Reuse as** is a heuristic from name, kind and use. Treat every cell as a lead to check, not a verdict.", "",
         "## Start here (highest reuse rank)", "",
         "| Entry | Shelf | Reuse as | Effort | Refs | Last |", "|---|---|---|---|---|---|"]
    for r in start:
        L.append(f"| `{r['name']}` | {r['shelf']} | {r['reuse_as']} | {r['read_effort_steps']} | {r['inbound_refs']} | {r['last_commit']} |")
    for sh in sorted(by_shelf):
        L += ["", f"## {sh}", "",
              "| Entry | Kind | Files | Effort | Fate (proxy) | First | Last | Commits | Marks | Reuse as |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for r in sorted(by_shelf[sh], key=lambda r: -r["rank"]):
            L.append(f"| `{r['name']}` | {r['kind']} | {r['files']} | {r['read_effort_steps']} | {r['fate_proxy']} | "
                     f"{r['first_commit']} | {r['last_commit']} | {r['commits']} | {', '.join(r['marks']) or '-'} | {r['reuse_as']} |")
    cnt = collections.Counter(r["reuse_as"] for r in rows)
    L += ["", "## Totals by reuse-as", ""] + [f"- {k}: {v}" for k, v in cnt.most_common()]
    L += ["", "## What this does not know", "",
          "- Whether an artifact earned anything (a reply, a close): that lives in receipts and the backlog, not per artifact.",
          "- Inbound references count a name appearing in another tracked file; a bare common word can inflate it.",
          "- Published claude.ai artifacts and the iCloud resume folder are not in this catalog.", ""]
    return "\n".join(L)


def self_test():
    assert shelf("forge-monday-fde") == "300 Counterpart packages (forge)"
    assert shelf("zzz-unknown") == "900 Unshelved"
    assert reuse_as("old-thing.md", "doc", ["x"], 0, 200) == "archive candidate"       # fail-on-bad: stale + unreferenced
    assert reuse_as("old-thing.md", "doc", ["x"], 3, 200) == "copy"                    # pass-on-good: still referenced
    assert reuse_as("forge-x", "bundle (html)", ["a/b.html"], 2, 10) == "template (swap the counterpart)"
    assert reuse_as("a.evidence.jsonl", "data", ["a.evidence.jsonl"], 1, 5) == "evidence / data"
    print("artifact_reuse_catalog self-test: ok")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    today = dt.date.today()
    rows = build(today)
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    json.dump({"generated": today.isoformat(), "stale_days": STALE_DAYS, "entries": rows}, open(OUT_JSON, "w"), indent=1)
    open(OUT_MD, "w").write(render_md(rows, today))
    print(f"{len(rows)} entries -> {os.path.relpath(OUT_MD, ROOT)} and .json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
