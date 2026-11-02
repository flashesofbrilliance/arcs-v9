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
        with f.open(errors="replace") as fh:
            for raw in fh:
                if '"user"' not in raw:
                    continue
                try:
                    d = json.loads(raw)
                except ValueError:
                    continue
                if d.get("type") != "user" or d.get("isSidechain"):
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
                t = text_of(content).strip()
                if not t or NOISE.search(t) or len(t) > 600:
                    continue
                if CORRECTION.search(t):
                    corrections.append({"session": sid, "ts": d.get("timestamp"),
                                        "cwd": Path(d.get("cwd", "")).name, "text": t[:400]})
    return n_files, errors, corrections


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--min-sessions", type=int, default=3)
    ap.add_argument("--out", default="_STATE/dream/mine.json")
    a = ap.parse_args()
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
