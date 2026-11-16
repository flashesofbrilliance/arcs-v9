#!/usr/bin/env python3
"""jobs_board_mcp.py: a local stdio MCP server over the jobs.arcs.care board API.

One interface for every session and every role source (Fonzi, Jack & Jill,
LinkedIn alerts, HN, ATS bridges) instead of hand-rolled curl through
scripts/jobs_wt.sh. It reads and writes ONLY through the existing routes, with
the pipeline token (x-jobs-token from ~/.arcs/jobs-pipeline.env):

  GET    /api/jobs              all rows (filtered here, client side)
  POST   /api/jobs              array upsert (used for add_job, new manual-* id only)
  PATCH  /api/jobs/lane         laneStage + laneStatus (outcome refused here AND by the API)
  GET    /api/jobs/lane         sources + recent ingest requests
  DELETE /api/jobs?jobid=       self-test cleanup only (API allows manual-*/eval-* only)

Never exposed: swipes (admin session only, a revealed preference) and outcome
writes (human only). Every move writes a provenance line into laneStatus:
"<status> · via <source> <date> (<session>)", which the board already renders.

Stdlib only (newline-delimited JSON-RPC 2.0 over stdio), so no npm dependency.

  python3 scripts/jobs_board_mcp.py              # serve (Claude Code starts this)
  python3 scripts/jobs_board_mcp.py --self-test  # round-trip on a scratch manual-* row, then delete it
  claude mcp add --scope user jobs-board -- python3 <repo>/scripts/jobs_board_mcp.py
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = os.environ.get("JOBS_BASE", "https://jobs.arcs.care")
ENV_FILE = Path.home() / ".arcs" / "jobs-pipeline.env"
MOVABLE = ("research", "qualify", "apply", "interview")  # outcome is human-only
CACHE_TTL = 60.0
PROTOCOL = "2025-06-18"
_cache: dict = {"at": 0.0, "rows": None}


def _token() -> str:
    tok = os.environ.get("JOBS_PIPELINE_TOKEN", "")
    if not tok and ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            m = re.match(r"\s*(?:export\s+)?JOBS_PIPELINE_TOKEN=(.*)$", line)
            if m:
                tok = m.group(1).strip().strip("'\"")
    if not tok:
        raise RuntimeError(f"JOBS_PIPELINE_TOKEN not set (env or {ENV_FILE})")
    return tok


def api(method: str, path: str, body=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("x-jobs-token", _token())
    req.add_header("user-agent", "arcs-jobs-board-mcp/1")
    if data is not None:
        req.add_header("content-type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        txt = e.read().decode(errors="replace")[:300]
        raise RuntimeError(f"{method} {path} -> HTTP {e.code}: {txt}") from None


def rows(fresh: bool = False) -> list[dict]:
    if fresh or _cache["rows"] is None or time.time() - _cache["at"] > CACHE_TTL:
        _cache["rows"] = api("GET", "/api/jobs")["rows"]
        _cache["at"] = time.time()
    return _cache["rows"]


def _session() -> str:
    return (os.environ.get("CLAUDE_CODE_SESSION_ID") or "mcp")[:8]


def _today() -> str:
    return _dt.date.today().isoformat()


def _brief(r: dict) -> dict:
    return {k: r.get(k) for k in ("jobid", "title", "company", "source", "composite", "band",
                                  "laneStage", "laneStatus", "url", "firstSeen")}


def _find_one(jobid: str, fresh: bool = False) -> dict:
    for r in rows(fresh):
        if r["jobid"] == jobid:
            return r
    raise RuntimeError(f"no such job: {jobid}")


# ---------------------------------------------------------------- tools

def find_jobs(query: str = "", stage: str | None = None, source: str | None = None, limit: int = 25):
    terms = [t for t in query.lower().split() if t]
    out = []
    for r in rows():
        hay = f"{r.get('company','')} {r.get('title','')} {r.get('source','')}".lower()
        if terms and not all(t in hay for t in terms):
            continue
        if stage is not None:
            want = None if stage in ("", "none") else stage
            if r.get("laneStage") != want:
                continue
        if source and r.get("source") != source:
            continue
        out.append(_brief(r))
    return {"count": len(out), "rows": out[: max(1, min(int(limit), 200))]}


def get_job(jobid: str):
    r = dict(_find_one(jobid))
    r.pop("swipe", None)  # swipe is admin-only state; this tool does not surface or write it
    return r


def score_check(jobid: str):
    r = _find_one(jobid)
    parse = lambda v: json.loads(v) if isinstance(v, str) and v[:1] in "[{" else v
    return {"jobid": jobid, "composite": r.get("composite"), "band": r.get("band"),
            "scoredAt": r.get("scoredAt"), "unscoredWhy": r.get("unscoredWhy"),
            "dims": parse(r.get("dims")), "gates": parse(r.get("gates")),
            "assessment": r.get("assessment"), "scored": r.get("composite") is not None}


def add_job(url: str, title: str, company: str, source: str = "manual"):
    if not re.match(r"^https?://", url or ""):
        raise RuntimeError("url must start with http(s)://")
    if not re.match(r"^[a-z0-9_-]{2,40}$", source or ""):
        raise RuntimeError("source must be a short slug, e.g. fonzi, jackandjill_match, hn_whoishiring")
    for r in rows(fresh=True):
        if r.get("url") == url:
            return {"created": False, "note": "url already on the board", "row": _brief(r)}
    jobid = f"manual-{int(time.time() * 1000)}"
    api("POST", "/api/jobs", [{
        "jobid": jobid, "title": title, "company": company, "url": url, "source": source,
        "alertQuery": "manual", "band": "UNSCORED", "unscoredWhy": "added by hand, not yet scored",
        "atsClass": "unk", "atsName": "unverified", "contactType": "unverified",
        "contactDetail": "resolves on swipe",
        "nextStep": f"Added via jobs-board MCP {_today()} ({_session()}). Resolve ATS and hiring manager on swipe.",
    }])
    return {"created": True, "row": _brief(_find_one(jobid, fresh=True))}


def move_job(jobid: str, stage: str, status: str = "", via: str = "mcp"):
    if stage == "outcome":
        raise RuntimeError("outcomes are human-only: close the row on jobs.arcs.care while signed in")
    if stage not in MOVABLE and stage != "none":
        raise RuntimeError(f"stage must be one of {', '.join(MOVABLE)} or none")
    note = f"{status.strip() + ' · ' if status.strip() else ''}via {via} {_today()} ({_session()})"
    res = api("PATCH", "/api/jobs/lane", {"jobid": jobid, "laneStage": None if stage == "none" else stage,
                                          "laneStatus": note[:300]})
    _cache["rows"] = None
    return res


def list_sources():
    d = api("GET", "/api/jobs/lane")
    counts: dict[str, int] = {}
    for r in rows():
        counts[r.get("source") or "?"] = counts.get(r.get("source") or "?", 0) + 1
    srcs = [{k: s.get(k) for k in ("key", "label", "status", "lastRunAt", "lastError")} for s in d["sources"]]
    return {"registered": srcs, "row_counts_by_source": dict(sorted(counts.items(), key=lambda kv: -kv[1]))}


S = lambda **p: {"type": "object", "properties": p, "additionalProperties": False}
STR = {"type": "string"}
TOOLS = {
    "find_jobs": (find_jobs, "Search board rows by words in company/title/source (all must match). "
                  "Optional stage (research|qualify|apply|interview|outcome|none) and exact source filter.",
                  {**S(query=STR, stage=STR, source=STR, limit={"type": "integer"})}),
    "get_job": (get_job, "Full row for one jobid (swipe state omitted).", {**S(jobid=STR), "required": ["jobid"]}),
    "score_check": (score_check, "Score state for one jobid: composite, band, dims, gates, why unscored.",
                    {**S(jobid=STR), "required": ["jobid"]}),
    "add_job": (add_job, "Add a posting by hand as a new manual-* row with its source slug "
                "(e.g. fonzi, jackandjill_match, hn_whoishiring). Dedupes on url.",
                {**S(url=STR, title=STR, company=STR, source=STR), "required": ["url", "title", "company"]}),
    "move_job": (move_job, "Move a row to research|qualify|apply|interview (or none to clear). "
                 "status is a short note; provenance (via, date, session) is appended. Outcome is refused: human-only.",
                 {**S(jobid=STR, stage=STR, status=STR, via=STR), "required": ["jobid", "stage"]}),
    "list_sources": (list_sources, "Registered sources plus row counts by source value.", S()),
}


# ---------------------------------------------------------------- stdio JSON-RPC

def handle(msg: dict):
    mid, method = msg.get("id"), msg.get("method")
    if mid is None:  # notification (e.g. notifications/initialized)
        return None
    ok = lambda result: {"jsonrpc": "2.0", "id": mid, "result": result}
    if method == "initialize":
        return ok({"protocolVersion": (msg.get("params") or {}).get("protocolVersion", PROTOCOL),
                   "capabilities": {"tools": {}}, "serverInfo": {"name": "jobs-board", "version": "1.0.0"}})
    if method == "ping":
        return ok({})
    if method == "tools/list":
        return ok({"tools": [{"name": n, "description": d, "inputSchema": s} for n, (_, d, s) in TOOLS.items()]})
    if method == "tools/call":
        p = msg.get("params") or {}
        name, args = p.get("name"), p.get("arguments") or {}
        if name not in TOOLS:
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32602, "message": f"unknown tool {name}"}}
        try:
            out = TOOLS[name][0](**args)
            return ok({"content": [{"type": "text", "text": json.dumps(out, indent=1, default=str)}]})
        except Exception as e:  # tool errors go back to the model, not as protocol errors
            return ok({"content": [{"type": "text", "text": f"error: {e}"}], "isError": True})
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"method not found: {method}"}}


def serve():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            resp = handle(json.loads(line))
        except json.JSONDecodeError:
            resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


def self_test() -> int:
    """Protocol smoke over a real subprocess, then a live round-trip on a scratch row, then delete it."""
    fails = 0
    def check(cond, label):
        nonlocal fails
        print(("PASS " if cond else "FAIL ") + label)
        fails += 0 if cond else 1

    p = subprocess.run([sys.executable, __file__], capture_output=True, text=True, timeout=30, input="\n".join(json.dumps(m) for m in [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": PROTOCOL}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "move_job", "arguments": {"jobid": "x", "stage": "outcome"}}},
    ]) + "\n")
    resp = [json.loads(l) for l in p.stdout.splitlines() if l.strip()]
    check(len(resp) == 3 and resp[0]["result"]["serverInfo"]["name"] == "jobs-board", "initialize answers, notification gets no reply")
    check({t["name"] for t in resp[1]["result"]["tools"]} == set(TOOLS), "tools/list names all six tools")
    check(resp[2]["result"].get("isError") and "human-only" in resp[2]["result"]["content"][0]["text"], "move to outcome refused locally")
    check(not any("swipe" in n for n in TOOLS), "no swipe tool exposed")

    url = f"https://example.invalid/jobs-board-mcp-selftest-{int(time.time())}"
    jobid = None
    try:
        a = add_job(url, "MCP self-test (delete me)", "zz-selftest", "manual")
        jobid = a["row"]["jobid"]
        check(a["created"] and jobid.startswith("manual-"), f"add_job created {jobid}")
        check(not add_job(url, "dup", "zz-selftest")["created"], "add_job dedupes on url")
        f = find_jobs("zz-selftest self-test")
        check(any(r["jobid"] == jobid for r in f["rows"]), "find_jobs finds the scratch row")
        m = move_job(jobid, "research", "self-test", via="self-test")
        check(m.get("ok") and m.get("laneStage") == "research", "move_job -> research")
        g = get_job(jobid)
        check(g["laneStage"] == "research" and "via self-test" in (g["laneStatus"] or ""), "provenance line on laneStatus")
        check("swipe" not in g, "get_job omits swipe")
        check(score_check(jobid)["band"] == "UNSCORED", "score_check reports UNSCORED")
        check(any(s["key"] == "manual" for s in list_sources()["registered"]), "list_sources lists manual")
    finally:
        if jobid:
            d = api("DELETE", f"/api/jobs?jobid={urllib.parse.quote(jobid)}")
            check(d.get("deleted") == 1, f"scratch row {jobid} deleted")
            check(not any(r["jobid"] == jobid for r in rows(fresh=True)), "scratch row gone from the board")
    print(f"{'OK' if not fails else 'FAILED'}: {fails} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    serve()
