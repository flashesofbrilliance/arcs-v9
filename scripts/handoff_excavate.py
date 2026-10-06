#!/usr/bin/env python3
"""handoff_excavate — mechanical index of every handoff block ever committed (no LLM).

Walks every commit (all refs) that touched CLAUDE.md, _ARCHIVE/handoffs.md or _HANDOFFS/fragments/,
splits each file version into `# Handoff — vX` blocks (fragments: one block per file), dedupes by
normalized body hash, and emits one JSONL row per unique block: version, date, branch, PRs,
receipt ids, headings, first-seen commit/path, body. Stdlib only.

  handoff_excavate.py [--out _STATE/handoff-excavation/<date>.jsonl]
"""
import datetime, hashlib, json, os, re, subprocess, sys

PATHS = ["CLAUDE.md", "_ARCHIVE/handoffs.md", "_HANDOFFS"]
TITLE = re.compile(r"^# Handoff\b[^\n]*$", re.M)
VER = re.compile(r"v(\d+\.\d+(?:\.\d+)?)")
DATE = re.compile(r"\((\d{4}-\d{2}-\d{2})\)")
PR = re.compile(r"(?<![\w/])#(\d{2,4})\b")
RCPT = re.compile(r"\b\d{4}-\d{2}-\d{2}--[\w.-]+--[A-Z]{2,}\b")
BRANCH = re.compile(r"\bclaude/[\w./-]+[\w]")


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, errors="replace").stdout


def blocks(path, text):
    if path.startswith("_HANDOFFS/fragments/"):
        yield text.strip()
        return
    starts = [m.start() for m in TITLE.finditer(text)]
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else len(text)
        b = text[s:e]
        # a block ends at the next top-level non-handoff heading
        m = re.search(r"^# (?!Handoff)", b[1:], re.M)
        if m:
            b = b[:m.start() + 1]
        yield b.strip().rstrip("-").strip()


def main():
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else \
        f"_STATE/handoff-excavation/{datetime.date.today()}.jsonl"
    log = git("log", "--all", "--reverse", "--format=%H %cI", "--", *PATHS).split("\n")
    seen, rows = {}, []
    for line in filter(None, log):
        sha, when = line.split(" ", 1)
        files = git("show", "--name-only", "--format=", sha, "--", *PATHS).split()
        for f in files:
            if not (f in ("CLAUDE.md", "_ARCHIVE/handoffs.md") or f.startswith("_HANDOFFS/fragments/")):
                continue
            text = git("show", f"{sha}:{f}")
            for b in blocks(f, text):
                if len(b) < 40:
                    continue
                h = hashlib.sha1(re.sub(r"\s+", " ", b).encode()).hexdigest()[:16]
                if h in seen:
                    seen[h]["seen_in"] += 1
                    continue
                head = b.split("\n", 1)[0]
                v, d = VER.search(head), DATE.search(head)
                fm = re.search(r"^branch:\s*(\S+)", b, re.M)
                r = {"hash": h, "version": v.group(1) if v else None,
                     "date": d.group(1) if d else (re.search(r"(\d{4})(\d{2})(\d{2})T", f) and
                                                   "-".join(re.search(r"(\d{4})(\d{2})(\d{2})T", f).groups())),
                     "title": head[:160], "source": f, "first_commit": sha[:10], "first_seen": when,
                     "branch": fm.group(1) if fm else (BRANCH.search(b).group(0) if BRANCH.search(b) else None),
                     "prs": sorted({int(x) for x in PR.findall(b)}), "receipts": sorted(set(RCPT.findall(b))),
                     "headings": re.findall(r"^#{2,3} (.+)$", b, re.M), "seen_in": 1, "body": b}
                seen[h] = r
                rows.append(r)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    vers = {r["version"] for r in rows if r["version"]}
    print(f"{len(rows)} unique blocks ({len(vers)} distinct versions) from {len(log)-1} commits -> {out}")


if __name__ == "__main__":
    main()
