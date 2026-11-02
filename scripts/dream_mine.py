#!/usr/bin/env python3
"""dream_mine.py: the deterministic scout half of an out-of-band "dreaming" pass.

Reads Claude Code session transcripts (~/.claude/projects/<arcs-v9 dirs>/*.jsonl)
over a window and clusters two failure signals across sessions:
  1. tool errors (tool_result with is_error), keyed by normalized first line
  2. user corrections (short human turns with correction phrasing)
Each cluster carries a count, the number of distinct sessions, and examples.

It proposes nothing and writes no memory. A judgment pass (a human or an agent)
reads the JSON and drafts memory-edit proposals with evidence; a human accepts.
Pattern after Lamis Mukta, "Context Engineering, Memory Systems, and Dreaming"
(AI Native DevCon London 2026).

Usage: python3 scripts/dream_mine.py [--days 7] [--min-sessions 3] [--out PATH]
"""
import argparse
import json
import re
import time
from collections import defaultdict
from pathlib import Path

PROJECTS = Path.home() / ".claude" / "projects"
CORRECTION = re.compile(
    r"\b(no[,.!]|nope|wrong|that's not|thats not|don't|dont|stop|why did you|"
    r"i said|i told you|not what i|you missed|you forgot|again\?|undo|revert)\b",
    re.I,
)
NOISE = re.compile(r"<(system-reminder|command-name|local-command|task-notification)")


def norm(line: str) -> str:
    s = line.strip()[:200]
    s = re.sub(r"/[\w./~@+-]+", "<path>", s)
    s = re.sub(r"\b[0-9a-f]{7,40}\b", "<sha>", s)
    s = re.sub(r"\d+", "<n>", s)
    return s


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(
            c.get("text", "") if isinstance(c.get("text"), str) else str(c.get("content", ""))
            for c in content if isinstance(c, dict)
        )
    return ""


def mine(days: int):
    cutoff = time.time() - days * 86400
    errors = defaultdict(lambda: {"count": 0, "sessions": set(), "examples": []})
    corrections = []
    n_files = 0
    for f in PROJECTS.glob("-Users-zharris-arcs-v9*/*.jsonl"):
        if f.stat().st_mtime < cutoff:
            continue
        n_files += 1
        sid = f.stem[:8]
        after_reply = False  # was the last main-thread record an assistant turn?
        with f.open(errors="replace") as fh:
            for raw in fh:
                if '"user"' not in raw and '"assistant"' not in raw:
                    continue
                try:
                    d = json.loads(raw)
                except ValueError:
                    continue
                if d.get("isSidechain"):
                    continue
                if d.get("type") == "assistant":
                    after_reply = True
                    continue
                if d.get("type") != "user":
                    continue
                content = (d.get("message") or {}).get("content")
                if isinstance(content, list) and any(
                    isinstance(c, dict) and c.get("type") == "tool_result" for c in content
                ):
                    for c in content:
                        if isinstance(c, dict) and c.get("is_error"):
                            body = text_of(c.get("content")) or str(c.get("content"))
                            lines = [l for l in body.splitlines() if l.strip()]
                            first = lines[0] if lines else ""
                            if first.startswith("Exit code") and len(lines) > 1:
                                # the exit line says nothing; key on the last line (the error itself)
                                first = "Exit code: " + lines[-1]
                            k = norm(first)
                            e = errors[k]
                            e["count"] += 1
                            e["sessions"].add(sid)
                            if len(e["examples"]) < 3:
                                e["examples"].append({"session": sid, "ts": d.get("timestamp"),
                                                      "text": body[:300]})
                    continue
                was_after_reply, after_reply = after_reply, False
                # drop the user's quotes of the assistant ("> ..." lines from reply/attach chips)
                t = "\n".join(l for l in text_of(content).splitlines()
                              if not l.lstrip().startswith((">", "<!--"))).strip()
                # a correction answers a reply and is short; long turns are new instructions
                if not t or not was_after_reply or NOISE.search(t) or len(t) > 200:
                    continue
                if CORRECTION.search(t):
                    corrections.append({"session": sid, "ts": d.get("timestamp"),
                                        "cwd": Path(d.get("cwd", "")).name, "text": t[:400]})
    return n_files, errors, corrections


# --- corpus mode: claims in the docs and memory that went stale with no diff to show it ---

ROOT = Path(__file__).resolve().parent.parent
MEMORY = PROJECTS / "-Users-zharris-arcs-v9" / "memory"
# a backticked repo path: starts at a known top-level folder or file, has no spaces or globs
PATH_CITE = re.compile(r"`((?:scripts|src|runtime|_PATTERNS|_DECISIONS|_PROPOSALS|_QUEUE|_SEEDS|"
                       r"_ARTIFACTS|operators|public|prisma|\.claude|\.github)/[\w./@+-]+)`")
VERIFIED = re.compile(r"\b(?:verified|confirmed|as of|re-verified|last verified)\b[^.\n]{0,40}?"
                      r"(\d{4}-\d{2}-\d{2})", re.I)
# skipped: history by design, generated state, and build output
SKIP_DIRS = ("_ARCHIVE/", "_STATE/", "node_modules/", "_HANDOFFS/fragments/", "runtime/memory-export/")


def corpus_docs():
    import subprocess
    tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True,
                             text=True).stdout.split("\n")
    known = set(tracked)
    docs = [(p, ROOT / p) for p in tracked if p.endswith(".md") and not p.startswith(SKIP_DIRS)]
    docs += [("memory/" + f.name, f) for f in sorted(MEMORY.glob("*.md"))]
    return known, docs


def corpus(stale_days):
    known = corpus_docs()[0]
    dirs = {str(Path(p).parent) for p in known}
    by_stem = {}  # a dead cite whose file still exists under another path or extension was moved
    generic = {"index", "route", "page", "layout", "README", "package", "SKILL", "VERSION"}
    for p in known:
        if Path(p).stem not in generic:
            by_stem.setdefault(Path(p).stem, []).append(p)
    today = time.time()
    dead, stale, descs = [], [], []
    _, docs = corpus_docs()
    for name, path in docs:
        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for m in PATH_CITE.finditer(line):
                cite = m.group(1).rstrip("./")
                if cite in known or cite in dirs or (ROOT / cite).exists():
                    continue
                # a cite next to "retired/moved/renamed" is history, not a live claim
                if re.search(r"retir|moved|renam|archiv|deleted|was |old |former", line, re.I):
                    continue
                dead.append({"doc": name, "line": i, "cite": cite, "text": line.strip()[:200],
                             "moved_to": [p for p in by_stem.get(Path(cite).stem, [])
                                          if p.split("/")[0] == cite.split("/")[0]][:2]})
            for m in VERIFIED.finditer(line):
                try:
                    age = (today - time.mktime(time.strptime(m.group(1), "%Y-%m-%d"))) / 86400
                except ValueError:
                    continue
                if age > stale_days:
                    stale.append({"doc": name, "line": i, "date": m.group(1), "age_days": int(age),
                                  "text": line.strip()[:200]})
        if name.startswith("memory/"):
            d = re.search(r"^description:\s*(.+)$", text, re.M)
            if d:
                descs.append((name, set(re.findall(r"[a-z]{4,}", d.group(1).lower()))))
    dupes = []
    for i in range(len(descs)):
        for j in range(i + 1, len(descs)):
            a, b = descs[i][1], descs[j][1]
            if len(a) >= 5 and len(b) >= 5:
                jac = len(a & b) / len(a | b)
                if jac >= 0.45:
                    dupes.append({"a": descs[i][0], "b": descs[j][0], "jaccard": round(jac, 2)})
    return len(docs), dead, stale, sorted(dupes, key=lambda d: -d["jaccard"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--min-sessions", type=int, default=3)
    ap.add_argument("--corpus", action="store_true",
                    help="scan repo docs + project memory for dead cites, stale verifications, near-duplicate memories")
    ap.add_argument("--stale-days", type=int, default=45)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if a.corpus:
        n, dead, stale, dupes = corpus(a.stale_days)
        p = Path(a.out or "_STATE/dream/corpus.json")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"docs": n, "dead_cites": dead, "stale_verified": stale,
                                 "near_duplicate_memories": dupes}, indent=1))
        print(f"dream_mine --corpus: {n} docs, {len(dead)} dead cites, {len(stale)} verifications "
              f"older than {a.stale_days}d, {len(dupes)} near-duplicate memory pairs -> {p}")
        return
    a.out = a.out or "_STATE/dream/mine.json"
    n, errors, corrections = mine(a.days)
    clusters = sorted(
        ({"pattern": k, "count": v["count"], "sessions": len(v["sessions"]),
          "examples": v["examples"]} for k, v in errors.items()
         if len(v["sessions"]) >= a.min_sessions),
        key=lambda c: (-c["sessions"], -c["count"]),
    )
    # forked sessions replay the parent's turns; keep the first copy of each correction
    seen, uniq = set(), []
    for c in sorted(corrections, key=lambda c: c["ts"] or ""):
        if c["text"] not in seen:
            seen.add(c["text"])
            uniq.append(c)
    corrections = uniq
    out = {"window_days": a.days, "transcripts": n, "tool_error_clusters": clusters,
           "user_corrections": corrections}
    p = Path(a.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=1))
    print(f"dream_mine: {n} transcripts, {len(clusters)} error clusters "
          f"(>= {a.min_sessions} sessions), {len(corrections)} corrections -> {p}")


if __name__ == "__main__":
    main()
