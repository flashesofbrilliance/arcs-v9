#!/usr/bin/env python3
"""memory_index_sync.py — self-cataloging inchworm for the memory index.

The inversion that makes the index progressively self-catalog: each memory file's
frontmatter `description:` IS the SSOT for its index line. A file on disk that is
missing from MEMORY.md is mechanically appendable — rendered from its own
frontmatter into an "## Uncurated (auto-catalogued)" band at the bottom.
Curation (grouping into real sections, merging, retiring) stays human/judgment-
owned per canon (ADR-051/052 drift-receipt doctrine): this script never moves,
rewrites, or deletes a curated line. It only detects, and (in --append) adds.

Modes:
  --check    receipt-only: orphans, dead links, byte size vs budget. Exit 1 on drift.
  --append   auto-catalog orphans into the Uncurated band (mechanical countable),
             then print the receipt. Dead links + size stay receipt-only (judgment).

Stdlib-only. Filenames may contain dots (e.g. *-v0.2-*.md) — the historical
session-start.sh regex `[a-zA-Z0-9_-]+\\.md` missed those and false-positived.
"""
import argparse, os, re, sys

MEMDIR = os.path.expanduser("~/.claude/projects/-Users-zharris-arcs-v9/memory")
INDEX = os.path.join(MEMDIR, "MEMORY.md")
BUDGET = 24 * 1024  # soft byte budget for the always-loaded index. Harness loads only the first 25,000 CHARS of MEMORY.md (measured 2026-09-27; memory-index-load-cap-observed); bytes >= chars so 24576B is safe. Keep in sync with MEM_BUDGET in ~/.claude/hooks/global-session-start.sh
AUTO_HEADER = "## Uncurated (auto-catalogued — move into a real section when curating)"

# link targets: anything inside ](...) ending in .md, dots allowed in the name
LINK_RE = re.compile(r"\]\(([A-Za-z0-9._-]+\.md)\)")
DESC_RE = re.compile(r"^description:\s*(.+)$", re.M)


def frontmatter_desc(path):
    try:
        head = open(path, encoding="utf-8").read(2000)
    except OSError:
        return None
    m = DESC_RE.search(head)
    if not m:
        return None
    return m.group(1).strip().strip('"').strip("'")


def scan():
    idx = open(INDEX, encoding="utf-8").read()
    linked = set(LINK_RE.findall(idx))
    on_disk = {f for f in os.listdir(MEMDIR) if f.endswith(".md") and f != "MEMORY.md"}
    orphans = sorted(on_disk - linked)
    dead = sorted(f for f in linked if not os.path.exists(os.path.join(MEMDIR, f)))
    size = len(idx.encode("utf-8"))
    return idx, orphans, dead, size


def receipt(orphans, dead, size, appended=None):
    drift = bool(orphans or dead or size > BUDGET)
    if appended:
        print(f"memory-sync: AUTO-CATALOGUED {len(appended)} -> " + " ".join(appended))
    if orphans:
        print(f"memory-sync: ORPHANS ({len(orphans)}) -> " + " ".join(orphans))
    if dead:
        print(f"memory-sync: DEAD LINKS ({len(dead)}) -> " + " ".join(dead))
    if size > BUDGET:
        print(f"memory-sync: INDEX OVER BUDGET {size}B > {BUDGET}B — run /consolidate-memory (judgment stays human-owned)")
    if not drift and not appended:
        print("memory-sync: 1-1 OK")
    return drift


def append_orphans(idx, orphans):
    lines = []
    for f in orphans:
        desc = frontmatter_desc(os.path.join(MEMDIR, f)) or "(no frontmatter description — write one; it IS the index line)"
        if len(desc) > 140:
            desc = desc[:137] + "..."
        title = os.path.splitext(f)[0].replace("-", " ")
        lines.append(f"- [{title}]({f}) — {desc}")
    block = "\n".join(lines)
    if AUTO_HEADER in idx:
        idx = idx.replace(AUTO_HEADER, AUTO_HEADER + "\n" + block, 1)
    else:
        idx = idx.rstrip("\n") + f"\n{AUTO_HEADER}\n{block}\n"
    open(INDEX, "w", encoding="utf-8").write(idx)
    return [os.path.splitext(f)[0] for f in orphans]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--append", action="store_true")
    a = ap.parse_args()
    if not os.path.isfile(INDEX):
        print("memory-sync: no MEMORY.md — skipping")
        return 0
    idx, orphans, dead, size = scan()
    appended = None
    if a.append and orphans:
        appended = append_orphans(idx, orphans)
        idx, orphans, dead, size = scan()  # re-scan post-append
    drift = receipt(orphans, dead, size, appended)
    return 1 if (a.check and drift) else 0


if __name__ == "__main__":
    sys.exit(main())
