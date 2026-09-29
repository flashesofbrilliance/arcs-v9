#!/usr/bin/env python3
"""
witness_backfill_scout.py — find witness-shaped moments in past session transcripts.
Stdlib only. The scout is MECHANICAL: it surfaces candidates and never files one.
Filing needs a human `--accept` (NOTOMATION; WORLD.md THE WITNESS).

Honesty contract (ADR-044 aspiration vs attestation; chain-of-custody realtime vs posthoc):
  - A backfilled stub is a DIFFERENT object from a live one and says so:
      backfilled: true · occurred_at (from the transcript) · backfilled_at (today)
      gut: null (the in-the-moment read cannot be reconstructed) · source_transcript
  - The quote and the timestamp are M0 (the transcript is the primary record of what was
    said and when). Nothing else is.

Sources scanned: ~/.claude/projects/*arcs-v9*/**/*.jsonl (Claude Code session transcripts).
Hermes sessions are NOT scanned here (different store; use session_search there).

Triggers (case-insensitive, on the human's own words unless noted):
  naming        "wait, that's it" · "that's it" · "yes exactly" · "exactly" (alone) · "bank that"
                · "I see this as" · "feels like" · "the way I think about" · "call it"
                · "I'm saying the word" · "witness" · "proverb" · "invariant" · "names itself"
                ("seems like" / "this is the X" were dropped 2026-09-27: they fired on mundane requests)
  endorsement   a short human turn ("yes" / "yup" / "yes." / "do it" / "right") that FOLLOWS an
                assistant turn containing "Can I get a witness" — the live offer, accepted
  offer         an assistant turn containing "Can I get a witness" with NO short yes after it
                (offered, not taken; still worth a look)

Usage:
  python3 scripts/witness_backfill_scout.py scan [--since YYYY-MM-DD] [--out PATH]
      -> writes candidates JSONL (default _INBOX/witness-backfill-candidates.jsonl), prints a summary
  python3 scripts/witness_backfill_scout.py review [--kind naming|endorsement|offer] [--limit N]
      -> numbered list for a human to read
  python3 scripts/witness_backfill_scout.py accept 3,7,12 [--y SCRATCH|YELLOW|GREEN]
      -> files ONLY those rows into _STATE/witness/<occurred-date>.jsonl as backfilled stubs
  python3 scripts/witness_backfill_scout.py --self-test
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = Path(os.environ.get("CLAUDE_PROJECTS_DIR", Path.home() / ".claude" / "projects"))
WITNESS_DIR = ROOT / "_STATE" / "witness"
DEFAULT_OUT = ROOT / "_INBOX" / "witness-backfill-candidates.jsonl"

NAMING_RE = re.compile(
    r"(wait,?\s*that'?s\s+it|\bthat'?s\s+it\b|yes,?\s*exactly|^\s*exactly[.!]?\s*$|bank\s+that|"
    r"i\s+see\s+this\s+as|feels\s+like|the\s+way\s+i\s+think\s+about|\bcall\s+it\b|"
    r"i'?m\s+saying\s+the\s+word|\bwitness\b|\bproverb\b|\binvariant\b|\bnames?\s+itself\b)",
    re.I | re.M,
)
OFFER_RE = re.compile(r"can\s+i\s+get\s+a\s+witness", re.I)
SHORT_YES_RE = re.compile(r"^\s*(yes|yup|yeah|yep|right|do it|ok(ay)?|sure|witnessed|attest( it)?)[.!]?\s*$", re.I)
SYSTEM_WRAP_RE = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)
MAX_QUOTE = 600


def _text_of(content) -> str:
    """Human-visible text of a message content (str or block list); tool blocks dropped."""
    if isinstance(content, str):
        return content
    parts = []
    for b in content or []:
        if isinstance(b, dict) and b.get("type") == "text":
            parts.append(b.get("text", ""))
    return "\n".join(parts)


def _clean(s: str) -> str:
    s = SYSTEM_WRAP_RE.sub("", s)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    return s.strip()


def iter_turns(path: Path):
    """Yield (role, text, ts, sid, cwd, branch) for real human/assistant turns, in order."""
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = d.get("type")
            if t not in ("user", "assistant") or d.get("isSidechain"):
                continue
            m = d.get("message") or {}
            txt = _clean(_text_of(m.get("content")))
            if not txt:
                continue
            if t == "user" and (txt.startswith("[Request interrupted") or txt.startswith("<local-command")):
                continue
            yield t, txt, d.get("timestamp", ""), d.get("sessionId", ""), d.get("cwd", ""), d.get("gitBranch", "")


def scan(since: str | None) -> list[dict]:
    files = sorted(glob.glob(str(PROJECTS / "*arcs-v9*" / "*.jsonl")))
    cands: list[dict] = []
    for fp in files:
        p = Path(fp)
        turns = list(iter_turns(p))
        for i, (role, txt, ts, sid, cwd, branch) in enumerate(turns):
            if since and ts[:10] < since:
                continue
            base = {"occurred_at": ts, "session": sid, "worktree": Path(cwd).name if cwd else "", "branch": branch,
                    "source_transcript": str(p), "turn_index": i}
            if role == "user":
                m = NAMING_RE.search(txt)
                if m and 20 <= len(txt) <= 1200:    # long pasted docs and one-word turns are not naming moments
                    prev = turns[i - 1][1] if i > 0 else ""
                    cands.append({**base, "kind": "naming", "trigger": m.group(0).strip(),
                                  "quote": txt[:MAX_QUOTE], "context_prev_assistant": prev[:300]})
                elif SHORT_YES_RE.match(txt) and i > 0 and turns[i - 1][0] == "assistant" and OFFER_RE.search(turns[i - 1][1]):
                    # endorsement of a live offer: the quote is the human's PRIOR turn (what was witnessed)
                    prior_human = next((turns[j][1] for j in range(i - 2, -1, -1) if turns[j][0] == "user"), "")
                    cands.append({**base, "kind": "endorsement", "trigger": txt.strip(),
                                  "quote": prior_human[:MAX_QUOTE], "context_prev_assistant": turns[i - 1][1][:300]})
            else:
                if OFFER_RE.search(txt):
                    nxt = turns[i + 1][1] if i + 1 < len(turns) else ""
                    if not SHORT_YES_RE.match(nxt):
                        prior_human = next((turns[j][1] for j in range(i - 1, -1, -1) if turns[j][0] == "user"), "")
                        cands.append({**base, "kind": "offer", "trigger": "offer not taken",
                                      "quote": prior_human[:MAX_QUOTE], "context_prev_assistant": txt[:300]})
    # dedup against already-filed witness quotes (normalized prefix match)
    filed = set()
    for wf in WITNESS_DIR.glob("*.jsonl"):
        for line in wf.read_text(encoding="utf-8").splitlines():
            try:
                q = json.loads(line).get("quote", "")
            except Exception:
                continue
            filed.add(_norm(q)[:80])
    out = []
    seen = set()
    # when the same quote is both a naming hit and an accepted live offer, the endorsement wins
    # (it carries the stronger evidence: an offer AND a human yes); offers rank last
    rank = {"endorsement": 0, "naming": 1, "offer": 2}
    cands.sort(key=lambda c: rank[c["kind"]])
    for c in cands:
        key = _norm(c["quote"])[:80]
        if not key or key in filed or key in seen:
            continue
        seen.add(key)
        out.append(c)
    out.sort(key=lambda c: c["occurred_at"])
    for n, c in enumerate(out, 1):
        c["n"] = n
    return out


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower()).strip()


def cmd_scan(a) -> int:
    out = scan(a.since)
    path = Path(a.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in out), encoding="utf-8")
    kinds = {}
    for c in out:
        kinds[c["kind"]] = kinds.get(c["kind"], 0) + 1
    span = (out[0]["occurred_at"][:10], out[-1]["occurred_at"][:10]) if out else ("-", "-")
    print(f"scout: {len(out)} candidates {kinds} · {span[0]} → {span[1]} · wrote {path}")
    print("next: python3 scripts/witness_backfill_scout.py review   (then accept N,M,... — human only)")
    return 0


def _load(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"no candidates at {path}; run `scan` first")
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def cmd_review(a) -> int:
    rows = _load(Path(a.out))
    if a.kind:
        rows = [r for r in rows if r["kind"] == a.kind]
    for r in rows[: a.limit]:
        q = r["quote"].replace("\n", " ")
        print(f"[{r['n']:>3}] {r['occurred_at'][:16]} {r['kind']:<11} {r['worktree'][:28]:<28} ({r['trigger'][:22]})")
        print(f"       {q[:220]}")
    print(f"-- {min(len(rows), a.limit)} of {len(rows)} shown")
    return 0


def cmd_accept(a) -> int:
    rows = {r["n"]: r for r in _load(Path(a.out))}
    want = [int(x) for x in a.ids.split(",") if x.strip()]
    today = dt.date.today().isoformat()
    filed = 0
    for n in want:
        r = rows.get(n)
        if not r:
            print(f"  skip {n}: no such candidate", file=sys.stderr)
            continue
        day = r["occurred_at"][:10] or today
        entry = {
            "ts": r["occurred_at"],
            "quote": r["quote"],
            "context": f"backfilled from transcript {Path(r['source_transcript']).name} turn {r['turn_index']} (worktree {r['worktree']}, branch {r['branch']}); trigger: {r['trigger']}",
            "gut": None,
            "y": a.y,
            "promoted": None,
            "backfilled": True,
            "occurred_at": r["occurred_at"],
            "backfilled_at": today,
            "source_transcript": r["source_transcript"],
        }
        WITNESS_DIR.mkdir(parents=True, exist_ok=True)
        with (WITNESS_DIR / f"{day}.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        filed += 1
        print(f"  filed {n} -> _STATE/witness/{day}.jsonl (backfilled, gut=null, y={a.y})")
    print(f"accept: {filed} filed. These are RECONSTRUCTIONS with real quotes; promote only if they prove durable.")
    return 0


def self_test() -> int:
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    proj = tmp / "projects" / "-Users-x-arcs-v9"
    proj.mkdir(parents=True)
    def line(t, content, ts):
        return json.dumps({"type": t, "isSidechain": False, "timestamp": ts, "sessionId": "s1", "cwd": "/w/tree-a",
                           "gitBranch": "b", "message": {"role": t, "content": content}})
    turns = [
        line("user", "<system-reminder>ignore me</system-reminder>\nlet's build the thing", "2026-09-01T10:00:00Z"),
        line("assistant", [{"type": "text", "text": "ok"}], "2026-09-01T10:00:05Z"),
        line("user", "wait, that's it: the shell is the debit side", "2026-09-01T10:01:00Z"),
        line("assistant", [{"type": "text", "text": "Can I get a witness? Should I attest that?"}], "2026-09-01T10:01:10Z"),
        line("user", "yes", "2026-09-01T10:01:20Z"),
        line("user", "I see this as a moiré between four pings", "2026-09-02T09:00:00Z"),
        line("assistant", [{"type": "text", "text": "noted"}], "2026-09-02T09:00:05Z"),
        line("user", "the torch is the chain of custody, obviously", "2026-09-02T09:00:08Z"),
        line("assistant", [{"type": "text", "text": "Can I get a witness?"}], "2026-09-02T09:00:10Z"),
        line("user", "no, move on", "2026-09-02T09:00:20Z"),
        line("user", "already filed: the old one", "2026-09-04T09:00:00Z"),
        line("user", "x" * 1300 + " feels like", "2026-09-03T09:00:00Z"),   # long paste: must NOT fire
    ]
    (proj / "s1.jsonl").write_text("\n".join(turns) + "\n", encoding="utf-8")
    global PROJECTS, WITNESS_DIR
    PROJECTS = tmp / "projects"
    WITNESS_DIR = tmp / "witness"; WITNESS_DIR.mkdir()
    (WITNESS_DIR / "2026-09-04.jsonl").write_text(json.dumps({"quote": "already filed: the old one"}) + "\n")
    out = scan(None)
    kinds = sorted((c["kind"], c["trigger"][:12]) for c in out)
    fails = 0
    def check(label, cond, detail=""):
        nonlocal fails
        print(f"  {'PASS' if cond else 'FAIL'}  {label}  {detail}")
        fails += 0 if cond else 1
    check("already-filed quote is deduped out", not any("already filed" in c["quote"] for c in out), kinds)
    check("endorsement (yes after offer) found, quote = prior human turn", any(c["kind"] == "endorsement" and "debit side" in c["quote"] for c in out))
    check("naming trigger found (moiré)", any(c["kind"] == "naming" and "moir" in c["quote"] for c in out))
    check("offer-not-taken found, quote = prior human turn", any(c["kind"] == "offer" and "torch" in c["quote"] for c in out))
    check("long paste does not fire", not any("xxxx" in c["quote"] for c in out))
    check("system-reminder wrapper stripped", not any("ignore me" in c["quote"] for c in out))
    # accept writes a backfilled row with gut null
    outp = tmp / "cands.jsonl"
    outp.write_text("".join(json.dumps(c) + "\n" for c in out))
    n = next(c["n"] for c in out if c["kind"] == "naming" and "moir" in c["quote"])
    class A: ids = str(n); y = "SCRATCH"; out = str(outp)
    cmd_accept(A)
    row = json.loads((WITNESS_DIR / "2026-09-02.jsonl").read_text().splitlines()[-1])
    check("accepted row is marked backfilled with gut=null and occurred_at", row["backfilled"] is True and row["gut"] is None and row["occurred_at"].startswith("2026-09-02"))
    print(f"self-test: {'OK' if fails == 0 else f'{fails} FAIL'}")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("scan"); s.add_argument("--since"); s.add_argument("--out", default=str(DEFAULT_OUT))
    r = sub.add_parser("review"); r.add_argument("--kind", choices=["naming", "endorsement", "offer"]); r.add_argument("--limit", type=int, default=40); r.add_argument("--out", default=str(DEFAULT_OUT))
    c = sub.add_parser("accept"); c.add_argument("ids"); c.add_argument("--y", default="SCRATCH", choices=["SCRATCH", "YELLOW", "GREEN"]); c.add_argument("--out", default=str(DEFAULT_OUT))
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.cmd == "scan":
        return cmd_scan(a)
    if a.cmd == "review":
        return cmd_review(a)
    if a.cmd == "accept":
        return cmd_accept(a)
    ap.print_help(); return 2


if __name__ == "__main__":
    raise SystemExit(main())
