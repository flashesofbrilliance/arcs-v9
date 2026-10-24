#!/usr/bin/env python3
"""One-shot, deterministic migration: induced-backlog `status` prose -> `state` enum + `status_note`.

Lossless: the original prose moves verbatim to `status_note`; nothing else in the row changes.
Only obvious prefixes are classified. Anything else is listed as UNSURE and left untouched
(no `state`), so a human decides; pass --decide id=STATE[,claimed_by=..,claimed_at=..] to apply.

  backlog_status_migrate.py            dry run: per-row verdicts + UNSURE list
  backlog_status_migrate.py --apply    write confident rows (and any --decide rows)
"""
import argparse, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUEUE = ROOT / "_QUEUE" / "induced-backlog.jsonl"

RULES = [  # (regex on the prose, state). First match wins; anchored at the start.
    (r"(DONE|CLOSED)\b", "DONE"),
    (r"COMPOSTED\b", "COMPOSTED"),
    (r"SUPERSEDED\b", "SUPERSEDED"),
    (r"INDUCED\s+—\s+HOLDING until depends_on clear", "HOLDING"),
    (r"(HELD|TABLED)\b.*\bZach\b", "HELD"),
    (r"OPEN\s+—\s+decision with Zach\s*$", "BLOCKED"),
    (r"OPEN\s*$", "OPEN"),
]


def classify(prose: str):
    s = prose.strip()
    for pat, state in RULES:
        if re.match(pat, s, re.I):
            return state
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--decide", action="append", default=[], help="id=STATE[,key=val...]")
    a = ap.parse_args()
    decided = {}
    for d in a.decide:
        rid, rest = d.split("=", 1)
        parts = rest.split(",")
        decided[rid] = {"state": parts[0], **dict(p.split("=", 1) for p in parts[1:])}
    lines = QUEUE.read_text().splitlines()
    out, unsure = [], []
    for line in lines:
        if not line.strip():
            out.append(line); continue
        r = json.loads(line)
        if "id" not in r or "state" in r:
            out.append(line); continue
        prose = str(r.get("status") or "")
        fields = decided.get(r["id"]) or ({"state": classify(prose)} if classify(prose) else None)
        if not fields:
            unsure.append((r["id"], prose)); out.append(line); continue
        new = {}
        for k, v in r.items():  # keep key order; state + status_note take status's slot
            if k == "status":
                new.update(fields); new["status_note"] = v
            else:
                new[k] = v
        if "status" not in r:
            new.update(fields); new["status_note"] = ""
        print(f"{fields['state']:<10} {r['id']}")
        out.append(json.dumps(new, ensure_ascii=False))
    for rid, prose in unsure:
        print(f"UNSURE     {rid}  | {prose[:120]}")
    if a.apply:
        QUEUE.write_text("\n".join(out) + "\n")
    print(f"\n{len(unsure)} unsure; {'written' if a.apply else 'dry run'}", file=sys.stderr)


if __name__ == "__main__":
    main()
