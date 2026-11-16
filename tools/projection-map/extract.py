#!/usr/bin/env python3
"""Pull Granola transcripts verbatim out of a subagent's JSONL log (tool_result text), write raw/<id>.txt.
Prints only counts. Usage: extract.py <agent.jsonl> <outdir>"""
import json, sys, re
from pathlib import Path
log, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(exist_ok=True)
calls, got = {}, {}
for ln in log.read_text().splitlines():
    try: e = json.loads(ln)
    except Exception: continue
    for c in (e.get("message") or {}).get("content") or []:
        if not isinstance(c, dict): continue
        if c.get("type") == "tool_use" and "get_meeting_transcript" in c.get("name", ""):
            calls[c["id"]] = c["input"]
        if c.get("type") == "tool_result" and c.get("tool_use_id") in calls:
            body = c["content"]; body = "".join(x.get("text", "") for x in body) if isinstance(body, list) else body
            try: d = json.loads(body)
            except Exception: print("non-JSON result for", calls[c["tool_use_id"]]); continue
            items = d.get("meetings") or [d]
            for m in items:
                mid = m.get("meeting_id") or m.get("id") or calls[c["tool_use_id"]].get("meeting_id") or (calls[c["tool_use_id"]].get("meeting_ids") or [None])[0]
                if not m.get("transcript"): continue  # skip error / rate-limited attempts
                off = calls[c["tool_use_id"]].get("offset") or 0
                got.setdefault(mid, []).append((off, m.get("transcript") or "", m.get("total_chars"), m.get("truncated")))
for mid, parts in got.items():
    parts = list({p[0]: p for p in parts}.values())  # one copy per offset (duplicate fetches)
    parts.sort(key=lambda p: p[0]); txt = "".join(p[1] for p in parts)
    (out / f"{mid}.txt").write_text(txt)
    print(mid, "pages", len(parts), "chars", len(txt), "tool_total", parts[0][2], "last_truncated", parts[-1][3], "MATCH" if len(txt) == parts[0][2] else "MISMATCH", "offsets", [p[0] for p in parts])
