# Staged backlog rows

Rows induced in the 2026-10-14..16 Scout/Wonderful session, held here so PR #1442 does not conflict
with the heavily edited `_QUEUE/induced-backlog.jsonl` on main. They are valid backlog rows (14, all
state OPEN, append-only, no row removed or edited).

After #1442 merges, append them to the real backlog, skipping any id already present, then run the checker:

    python3 - <<'PY'
    import json
    P="_QUEUE/induced-backlog.jsonl"
    have={json.loads(l).get("id") for l in open(P) if l.strip()}
    new=[l for l in open("_QUEUE/staged-rows/2026-10-17-scout-session-rows.jsonl") if l.strip() and json.loads(l)["id"] not in have]
    open(P,"a").write("".join(new)); print("appended",len(new))
    PY
    python3 scripts/backlog_status_check.py --check

Then delete this folder in the same commit.
