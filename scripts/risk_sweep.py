#!/usr/bin/env python3
"""risk_sweep.py - deterministic breaking / non-idempotent change sweep.

Reads the git diff between two points on origin/main, applies mechanical rules,
and folds the findings into an append-only register. No network, no LLM, stdlib only.

Re-running over the same range writes nothing: a finding's id is a hash of
rule + path + evidence key (never the commit), so a re-detection is a no-op.

Usage:
  python3 scripts/risk_sweep.py                    # cursor..origin/main, writes register + cursor
  python3 scripts/risk_sweep.py --day 2026-10-05   # that day's range, read-only
  python3 scripts/risk_sweep.py --since-sha SHA --dry-run
  python3 scripts/risk_sweep.py --heal             # tier-0 repairs only, uncommitted, one attempt each
  python3 scripts/risk_sweep.py --json

Register: $RISK_REGISTER or /Users/zharris/arcs-v9/_STATE/risk-register.jsonl (gitignored, local).
Self-healing tiers (see HEAL below): 0 regenerate, 1 draft fix, 2 file + notify, 3 one-way door,
never auto-healed (write-lock declaration first).
"""
import argparse, datetime as dt, hashlib, json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip())
REGISTER = Path(os.environ.get("RISK_REGISTER", "/Users/zharris/arcs-v9/_STATE/risk-register.jsonl"))
CURSOR = Path(os.environ.get("RISK_CURSOR", str(REGISTER.parent / "risk-sweep-cursor")))
REVIEW_DAYS = {"high": 7, "medium": 14, "low": 30}

# rule -> (class, severity, heal tier, heal action)
RULES = {
    "schema-removed":    ("breaking", "high",   3, "Declare a write-lock, ship an additive migration first, remove in a later release."),
    "migration-drop":    ("breaking", "high",   3, "One-way door. Declare a write-lock; back up the table before applying."),
    "route-removed":     ("breaking", "high",   2, "Restore the route or add a redirect and a deprecation note; notify consumers."),
    "export-removed":    ("breaking", "high",   1, "Re-export the symbol or update the remaining importers; draft the fix."),
    "deps-changed":      ("breaking", "medium", 2, "Confirm the dependency change was approved (no new deps without asking)."),
    "migration-data":    ("non-idempotent", "medium", 1, "Guard with ON CONFLICT / WHERE NOT EXISTS so a re-run is a no-op."),
    "post-create":       ("non-idempotent", "medium", 1, "Add an idempotency key or upsert so a retried POST cannot double-write."),
    "script-append":     ("non-idempotent", "low",    1, "Dedupe on a key before appending so a re-run does not duplicate rows."),
    "generated-stale":   ("breaking", "medium", 0, "Regenerate with the emit script and review the diff."),
}
PRESENCE_RULES = {"migration-data", "post-create", "script-append", "deps-changed", "migration-drop"}

GENERATED = [
    ("scripts/operator_registry_emit.py", ["--check"], []),
]


def git(*args, check=False):
    p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return p.stdout if p.returncode == 0 or not check else ""


def show(ref, path):
    return git("show", f"{ref}:{path}")


def now():
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def fid(rule, path, key):
    return hashlib.sha1(f"{rule}|{path}|{key}".encode()).hexdigest()[:12]


def patch_lines(base, head, path):
    added, removed = [], []
    for ln in git("diff", "-U0", "-M", base, head, "--", path).splitlines():
        if ln.startswith("+++") or ln.startswith("---"):
            continue
        if ln.startswith("+"):
            added.append(ln[1:])
        elif ln.startswith("-"):
            removed.append(ln[1:])
    return added, removed


def finding(rule, path, key, evidence, sha):
    cls, sev, tier, heal = RULES[rule]
    return {"id": fid(rule, path, key), "rule": rule, "class": cls, "severity": sev, "path": path,
            "key": key, "evidence": evidence[:200], "sha": sha, "tier": tier, "heal": heal}


def sweep(base, head):
    out = []
    sha = git("rev-parse", "--short", head).strip()
    for row in git("diff", "--name-status", "-M", base, head).splitlines():
        parts = row.split("\t")
        status, path = parts[0][0], parts[-1]
        old = parts[1] if len(parts) > 2 else path
        if re.match(r"src/app/api/.+/route\.ts$", old) and status in "DR" and (status == "D" or old != path):
            f = finding("route-removed", old, old, f"{'deleted' if status == 'D' else 'renamed to ' + path}", sha)
            subj = git("log", "-1", "--format=%s", f"{base}..{head}", "--", old).strip()
            if re.search(r"\b(retire|deprecat|sunset|remove|drop)", subj, re.I):
                f["severity"] = "low"
                f["evidence"] += f" (intentional per commit: {subj[:70]})"
            out.append(f)
        if path == "prisma/schema.prisma" or re.match(r"prisma/migrations/.+\.sql$", path):
            added, removed = patch_lines(base, head, path)
            if path == "prisma/schema.prisma":
                kept = {m.group(1) for ln in added if (m := re.match(r"\s*(\w+)\s+\S+", ln))}
                for ln in removed:
                    m = re.match(r"\s*(model\s+\w+|\w+)\s*(\S*)", ln)
                    if m and not ln.strip().startswith(("//", "@@", "}", "{")) and m.group(1).split()[-1] not in kept:
                        out.append(finding("schema-removed", path, m.group(1), ln.strip(), sha))
            else:
                text = "\n".join(added)
                for m in re.finditer(r"DROP\s+(TABLE|COLUMN|INDEX|CONSTRAINT)[^;]*;|RENAME\s+(TO|COLUMN)[^;]*;", text, re.I):
                    out.append(finding("migration-drop", path, m.group(0)[:80], m.group(0), sha))
                for m in re.finditer(r"^\s*(INSERT\s+INTO|UPDATE|DELETE\s+FROM)\b[^;]*;", text, re.I | re.M):
                    if not re.search(r"ON\s+CONFLICT|WHERE\s+NOT\s+EXISTS", m.group(0), re.I):
                        out.append(finding("migration-data", path, m.group(0)[:80], m.group(0), sha))
        if path == "package.json":
            added, removed = patch_lines(base, head, path)
            dep = re.compile(r'^\s+"([@\w/.-]+)":\s+"[\^~]?\d')
            names = {m.group(1) for ln in added + removed if (m := dep.match(ln))}
            for n in sorted(names):
                out.append(finding("deps-changed", path, n, f"{n} added, removed or bumped", sha))
        if re.match(r"src/lib/.+\.tsx?$", path) and status != "D":
            added, removed = patch_lines(base, head, path)
            exp = re.compile(r"export\s+(?:async\s+)?(?:function|const|class|type|interface|enum)\s+(\w+)")
            kept = {m.group(1) for ln in added if (m := exp.search(ln))}
            for ln in removed:
                m = exp.search(ln)
                if m and m.group(1) not in kept:
                    name = m.group(1)
                    users = [f for f in git("grep", "-lw", name, head, "--", "src").splitlines() if not f.endswith(path)]
                    if users:
                        out.append(finding("export-removed", path, name, f"{name} removed, still referenced in {len(users)} file(s)", sha))
        if re.match(r"src/app/api/.+/route\.ts$", path) and status != "D":
            added, _ = patch_lines(base, head, path)
            body = show(head, path)
            if "export async function POST" in body and re.search(r"\.create(Many)?\(", "\n".join(added)) \
                    and not re.search(r"idempoten|upsert|P2002|dedup", body, re.I):
                out.append(finding("post-create", path, "POST+create", "POST handler creates rows with no idempotency key or upsert", sha))
        if re.match(r"scripts/.+\.(sh|py)$", path) and status != "D":
            added, _ = patch_lines(base, head, path)
            body = show(head, path)
            if any(re.search(r"(?<!>)>>\s*\S|open\([^)]*['\"]a['\"]", ln) for ln in added) \
                    and not re.search(r"already|dedup|idempoten|\bseen\b|grep -q|exists", body, re.I):
                out.append(finding("script-append", path, "append", "appends to a file with no dedupe or exists check", sha))
    uniq = {f["id"]: f for f in out}
    return list(uniq.values())


def generated_stale(head_sha):
    """Only meaningful when the working tree is the swept head."""
    if git("rev-parse", "HEAD").strip() != git("rev-parse", head_sha).strip():
        return [], "generated-artifact check skipped (working tree is not the swept head)"
    out = []
    for script, args, _ in GENERATED:
        if not (ROOT / script).exists():
            continue
        r = subprocess.run(["python3", script, *args], cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            out.append(finding("generated-stale", script, script, (r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else "stale", git("rev-parse", "--short", "HEAD").strip()))
    return out, None


def load():
    rows = {}
    if REGISTER.exists():
        for ln in REGISTER.read_text().splitlines():
            if ln.strip():
                e = json.loads(ln)
                rows.setdefault(e["id"], {}).update(e)
    return rows


def append(events):
    if not events:
        return
    REGISTER.parent.mkdir(parents=True, exist_ok=True)
    with REGISTER.open("a") as f:
        for e in events:
            f.write(json.dumps(e, sort_keys=True) + "\n")


def reconcile(rows, head):
    """Git-derived moot: a finding that is no longer true at head resolves to moot."""
    events = []
    for r in rows.values():
        if r.get("status") != "open":
            continue
        rule, path, key = r["rule"], r["path"], r["key"]
        present = bool(git("cat-file", "-e", f"{head}:{path}", check=True) == "" and subprocess.run(["git", "cat-file", "-e", f"{head}:{path}"], cwd=ROOT, capture_output=True).returncode == 0)
        moot = None
        if rule == "route-removed" and present:
            moot = "route restored"
        elif rule in PRESENCE_RULES and not present:
            moot = "file no longer exists"
        elif rule == "export-removed" and present and re.search(rf"export\s+(?:async\s+)?(?:function|const|class|type|interface|enum)\s+{re.escape(key)}\b", show(head, path)):
            moot = "symbol exported again"
        elif rule == "schema-removed" and present and re.search(rf"\b{re.escape(key.split()[-1])}\b", show(head, path)):
            moot = "field or model present again"
        if moot:
            events.append({"id": r["id"], "event": "moot", "status": "moot", "at": now(), "why": moot})
    return events


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since-sha")
    ap.add_argument("--day")
    ap.add_argument("--head", default="origin/main")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--heal", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    git("fetch", "--quiet", "origin", "main")
    head = a.head
    if a.day:
        base = git("rev-list", "-1", f"--before={a.day} 00:00", head).strip()
        head = git("rev-list", "-1", f"--before={a.day} 23:59:59", head).strip() or head
        a.dry_run = True
    elif a.since_sha:
        base = a.since_sha
    elif CURSOR.exists():
        base = CURSOR.read_text().strip()
    else:
        base = git("rev-list", "-1", "--before=24 hours ago", head).strip()
    if not base:
        print("risk_sweep: no base commit found", file=sys.stderr)
        return 0
    head_sha = git("rev-parse", head).strip()
    rows = load()
    found = sweep(base, head)
    note = None
    if not a.day:
        gen, note = generated_stale(head_sha)
        found += gen
    new = [f for f in found if f["id"] not in rows]
    events = [{**f, "event": "open", "status": "open", "first_seen": now(), "at": now(),
               "review_by": (dt.date.today() + dt.timedelta(days=REVIEW_DAYS[f["severity"]])).isoformat()} for f in new]
    for f in found:  # a re-detection of a moot row reopens it
        r = rows.get(f["id"])
        if r and r.get("status") == "moot":
            events.append({"id": f["id"], "event": "reopen", "status": "open", "at": now()})
    if not a.dry_run:
        merged = {**rows, **{e["id"]: {**rows.get(e["id"], {}), **e} for e in events}}
        events += reconcile(merged, head)
        if a.heal:
            for r in merged.values():
                if r.get("status") == "open" and r["rule"] == "generated-stale" and r.get("heal_attempts", 0) < 1:
                    cmd = ["python3", r["path"]]
                    subprocess.run(cmd, cwd=ROOT, capture_output=True)
                    ok = subprocess.run(["python3", r["path"], "--check"], cwd=ROOT, capture_output=True).returncode == 0
                    events.append({"id": r["id"], "event": "heal", "at": now(), "heal_attempts": 1,
                                   "status": "healed-pending-review" if ok else "open",
                                   "healed_by": " ".join(cmd) if ok else None})
        append(events)
        CURSOR.parent.mkdir(parents=True, exist_ok=True)
        CURSOR.write_text(head_sha + "\n")
    rows = load() if not a.dry_run else rows
    view = {f["id"]: f for f in new}
    open_rows = [r for r in rows.values() if r.get("status") == "open"]
    stale = [r for r in open_rows if r.get("review_by", "9999") < dt.date.today().isoformat()]
    if a.json:
        print(json.dumps({"range": [base[:8], head_sha[:8]], "new": list(view.values()), "open": len(open_rows), "stale_open": len(stale)}, indent=1))
        return 0
    print(f"## RISK REGISTER DELTA  {base[:8]}..{head_sha[:8]}" + ("  (read-only)" if a.dry_run else ""))
    print(f"new {len(new)} | open {len(open_rows)} | past review date {len(stale)}" + (f" | {note}" if note else ""))
    order = {"high": 0, "medium": 1, "low": 2}
    for f in sorted(view.values(), key=lambda x: order[x["severity"]]):
        print(f"- [{f['severity']}/{f['class']}/tier{f['tier']}] {f['rule']} {f['path']}: {f['evidence']}")
        print(f"    heal: {f['heal']}")
    if not new:
        print("(no new findings)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
