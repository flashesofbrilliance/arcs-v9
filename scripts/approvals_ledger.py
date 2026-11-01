#!/usr/bin/env python3
"""approvals_ledger: every open PR, its owner, its check state, and whether a merge approval exists and how it arrived.

Stdlib, read-only. It proposes; it never merges, pushes, comments or writes a receipt. The human releases
the one-way door (NOTOMATION); this is the sheet handed to Zach at that door
(_PATTERNS/2026-11-01-harness-flight-manual.md, "Before each one-way door").

Tuition (2026-10-31 to 2026-11-01, one coordinating session, about a dozen PRs): a PR merged while its
session reported it had not; a child acted on an approval the parent could not trace to Zach; three PRs
were merged before a planned batch reached them; a fe-smoke check sat pending with 0s run time.

Sources, in order:
  1. open PRs: `gh pr list --state open --json ...` (body, commits, statusCheckRollup, head sha)
  2. receipts: the local export of public.decision_receipt (what_confirmed), refreshed with
     `python3 scripts/universe_receipts_adapter.py --export`; a missing export is reported, never guessed
  3. owner: a `local_<id>` session id in the PR body or commits, else the worktree that has the branch
     checked out (`git worktree list --porcelain`), else the branch name

Approval convention (the manual states it; this script reads it):
  firsthand:  Zach, 2026-11-01, verbatim: "merge 1917"
  relayed:    relayed via local_<id>: Zach, 2026-11-01, verbatim: "merge 1917"
A line counts as a merge approval only when it attributes a quoted phrase to Zach AND names merge, ship
or land. A line saying Zach approved with no verbatim quote is UNQUOTED (fog, not a release). A quote
that pins a head sha other than the current head is STALE_HEAD.

  python3 scripts/approvals_ledger.py [--json] [--receipts PATH] [--fixture FILE]
  python3 scripts/approvals_ledger.py --self-test
Exit: 0 report printed · 1 gh unavailable · 2 self-test failed.
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
RECEIPTS = os.path.join(REPO, "_STATE", "job-search", "universe", "sources", "decision-receipts.json")
PR_FIELDS = "number,title,headRefName,headRefOid,body,statusCheckRollup,mergeable,isDraft"  # commits per PR: the list query hits the GraphQL node cap
STUCK_MIN = 15  # a check queued/in progress this long with no start time reads as stuck (0s run time)

SESSION_RE = re.compile(r"\blocal_[0-9a-f]{8}(?:-[0-9a-f]{4}){0,4}(?:-[0-9a-f]{12})?\b")
QUOTE_RE = re.compile(r"[\"“]([^\"”]{2,200})[\"”]")
ZACH_RE = re.compile(r"\bZach\b")
MERGE_RE = re.compile(r"(?i)\b(merge|merging|ship|land)\b")
APPROVE_WORDS = re.compile(r"(?i)\b(approv\w*|go-ahead|his go|zach'?s go|zach'?s yes|released by zach)\b")
RELAY_RE = re.compile(r"(?i)\b(relay\w*|forwarded|via local_|per (the )?parent|from the parent)\b")
CONDITION_RE = re.compile(r"(?i)\b(only on|only after|wait(s|ing)? (for|on)|awaiting|needs|until|pending|ask(s)? for)\b")
SHA_RE = re.compile(r"\b[0-9a-f]{7,40}\b")


def sh(args):
    return subprocess.run(args, capture_output=True, text=True, cwd=REPO)


def lines_of(pr):
    """(source, text) for every line of the PR body and every commit message."""
    out = [("body", ln) for ln in (pr.get("body") or "").splitlines()]
    for c in pr.get("commits") or []:
        sha = (c.get("oid") or "")[:8]
        for ln in ((c.get("messageHeadline") or "") + "\n" + (c.get("messageBody") or "")).splitlines():
            out.append(("commit " + sha if sha else "commit", ln))
    return out


def classify_line(text, head):
    """One approval verdict for a line, or None when the line says nothing about a merge approval."""
    has_zach = bool(ZACH_RE.search(text))
    if not has_zach:
        return None
    quotes = QUOTE_RE.findall(text)
    merge_quote = [q for q in quotes if MERGE_RE.search(q)]
    relayed = bool(RELAY_RE.search(text))
    if merge_quote:
        q = merge_quote[0]
        shas = SHA_RE.findall(q)
        if shas and head and not any(head.startswith(s) or s.startswith(head[:len(s)]) for s in shas):
            return {"kind": "STALE_HEAD", "arrival": "relayed" if relayed else "firsthand", "quote": q}
        return {"kind": "RELAYED_QUOTED" if relayed else "FIRSTHAND_QUOTED",
                "arrival": "relayed" if relayed else "firsthand", "quote": q}
    if MERGE_RE.search(text) and APPROVE_WORDS.search(text) and not CONDITION_RE.search(text):
        return {"kind": "UNQUOTED", "arrival": "relayed" if relayed else "unknown", "quote": None}
    return None


def receipt_lines(receipts, number):
    """what_confirmed lines from receipts that name this PR (refs, receipt_id, or the line itself)."""
    out = []
    tag = re.compile(r"(?i)(\bpr[ -#]?%d\b|#%d\b|/pull/%d\b)" % (number, number, number))
    for r in receipts:
        hay = " ".join([r.get("receipt_id") or ""] + list(r.get("refs") or []))
        for ln in r.get("what_confirmed") or []:
            if tag.search(hay) or tag.search(ln):
                out.append(("receipt " + (r.get("receipt_id") or "?"), ln))
    return out


def check_state(rollup, now):
    if not rollup:
        return "NONE", []
    bad, pending, stuck = [], [], []
    for c in rollup:
        name = c.get("name") or c.get("context") or "?"
        if c.get("__typename") == "StatusContext":
            st = c.get("state")
            if st in ("FAILURE", "ERROR"):
                bad.append(name)
            elif st in ("PENDING", "EXPECTED"):
                pending.append(name)
            continue
        if c.get("status") != "COMPLETED":
            started = c.get("startedAt") or ""
            if not started or started.startswith("0001"):
                stuck.append(name)
            else:
                try:
                    t = dt.datetime.fromisoformat(started.replace("Z", "+00:00"))
                    (stuck if (now - t).total_seconds() > STUCK_MIN * 60 and c.get("status") == "QUEUED" else pending).append(name)
                except ValueError:
                    pending.append(name)
        elif c.get("conclusion") not in ("SUCCESS", "SKIPPED", "NEUTRAL"):
            bad.append(name)
    if bad:
        return "FAILING", bad
    if stuck:
        return "STUCK_0S", stuck
    if pending:
        return "PENDING", pending
    return "GREEN", []


def worktree_branches():
    r = sh(["git", "worktree", "list", "--porcelain"])
    out, path = {}, None
    for ln in r.stdout.splitlines():
        if ln.startswith("worktree "):
            path = ln[9:]
        elif ln.startswith("branch refs/heads/") and path:
            out[ln[len("branch refs/heads/"):]] = path
    return out


def ledger_row(pr, receipts, worktrees, now):
    head = pr.get("headRefOid") or ""
    lines = lines_of(pr) + receipt_lines(receipts, pr["number"])
    found = []
    for src, text in lines:
        v = classify_line(text, head)
        if v:
            v["source"] = src
            found.append(v)
    sessions = sorted(set(SESSION_RE.findall(" ".join(t for _, t in lines_of(pr)))))
    branch = pr.get("headRefName") or ""
    owner = ("session " + ", ".join(sessions)) if sessions else (
        "worktree " + os.path.basename(worktrees[branch]) if branch in worktrees else "no session id in PR")
    checks, names = check_state(pr.get("statusCheckRollup"), now)
    order = ["FIRSTHAND_QUOTED", "RELAYED_QUOTED", "STALE_HEAD", "UNQUOTED"]
    best = min(found, key=lambda v: order.index(v["kind"])) if found else None
    approval = best["kind"] if best else "NONE"
    blockers = []
    if pr.get("isDraft"):
        blockers.append("draft")
    if checks != "GREEN":
        blockers.append("checks " + checks + (" (" + ", ".join(names) + ")" if names else ""))
    if pr.get("mergeable") == "CONFLICTING":
        blockers.append("conflicting")
    if approval not in ("FIRSTHAND_QUOTED", "RELAYED_QUOTED"):
        blockers.append("no traceable approval" if approval == "NONE" else "approval " + approval)
    if blockers:
        proposal = "HOLD: " + "; ".join(blockers)
    else:
        proposal = "READY FOR ZACH'S RELEASE: scripts/safe_merge.sh %d %s" % (pr["number"], head[:12])
        if approval == "RELAYED_QUOTED":
            proposal += " (approval is relayed: confirm with Zach firsthand before running)"
    return {"number": pr["number"], "title": (pr.get("title") or "")[:70], "branch": branch, "head": head[:12],
            "owner": owner, "checks": checks, "check_names": names, "mergeable": pr.get("mergeable"),
            "approval": approval, "approval_quote": best["quote"] if best else None,
            "approval_source": best["source"] if best else None, "all_approval_lines": found, "proposal": proposal}


def load_receipts(path):
    if not os.path.exists(path):
        return [], "no local receipts export at %s (refresh: python3 scripts/universe_receipts_adapter.py --export)" % os.path.relpath(path, REPO)
    d = json.load(open(path))
    rows = d if isinstance(d, list) else d.get("rows") or d.get("receipts") or []
    return rows, "%d receipts from %s" % (len(rows), os.path.relpath(path, REPO))


def render(rows, note):
    print("approvals ledger (read-only; proposes, never merges) · %d open PR(s) · %s" % (len(rows), note))
    for r in rows:
        print("\n#%d  %s" % (r["number"], r["title"]))
        print("  owner     %s  (branch %s @ %s)" % (r["owner"], r["branch"], r["head"]))
        print("  checks    %s%s · mergeable %s" % (r["checks"], (" " + ", ".join(r["check_names"])) if r["check_names"] else "", r["mergeable"]))
        q = (' "%s" [%s]' % (r["approval_quote"], r["approval_source"])) if r["approval_quote"] else (
            " [%s]" % r["approval_source"] if r["approval_source"] else "")
        print("  approval  %s%s" % (r["approval"], q))
        print("  proposal  %s" % r["proposal"])
    ready = [r["number"] for r in rows if r["proposal"].startswith("READY")]
    print("\nready for release: %s · every release is Zach's, one PR at a time, then a decision receipt" % (ready or "none"))


# ---------------------------------------------------------------- self-test
NOW = dt.datetime(2026, 11, 1, 12, 0, tzinfo=dt.timezone.utc)
GREEN = [{"__typename": "CheckRun", "name": "gates", "status": "COMPLETED", "conclusion": "SUCCESS", "startedAt": "2026-11-01T11:00:00Z"}]
STUCK = GREEN + [{"__typename": "CheckRun", "name": "fe-smoke", "status": "QUEUED", "conclusion": None, "startedAt": None}]
HEAD = "abc1234def5678900000000000000000000000ff"


def fx(n, body="", commits=(), checks=GREEN, mergeable="MERGEABLE", head=HEAD):
    return {"number": n, "title": "t%d" % n, "headRefName": "claude/b%d" % n, "headRefOid": head, "body": body,
            "commits": [{"oid": "c0ffee%02d" % i, "messageHeadline": "x", "messageBody": m} for i, m in enumerate(commits)],
            "statusCheckRollup": checks, "mergeable": mergeable, "isDraft": False}


CASES = [
    # (name, pr, receipts, want_approval, want_checks, want_ready)
    ("good firsthand quote in body", fx(1, 'Zach, 2026-11-01, verbatim: "merge 1"'), [], "FIRSTHAND_QUOTED", "GREEN", True),
    ("good relayed quote, labelled", fx(2, 'relayed via local_7a42a368: Zach, 2026-11-01, verbatim: "merge it"'), [], "RELAYED_QUOTED", "GREEN", True),
    ("good approval from a receipt", fx(3), [{"receipt_id": "2026-11-01--x-pr3--ZH", "refs": ["pr3"],
        "what_confirmed": ['Zach, verbatim: "merge 3 now"']}], "FIRSTHAND_QUOTED", "GREEN", True),
    ("good approval pinned to current head", fx(4, commits=['Zach, verbatim: "merge at abc1234"']), [], "FIRSTHAND_QUOTED", "GREEN", True),
    ("bad: no approval at all", fx(5, "Builds row x. Tests pass."), [], "NONE", "GREEN", False),
    ("bad: claimed approval, no quote", fx(6, "Merge approved by Zach in the parent session."), [], "UNQUOTED", "GREEN", False),
    ("bad: quote pins an older head", fx(7, 'Zach, verbatim: "merge 7 at 9999999"'), [], "STALE_HEAD", "GREEN", False),
    ("bad: design quote is not a merge approval", fx(8, 'Zach, 2026-11-01: "go ahead on the design rulings"'), [], "NONE", "GREEN", False),
    ("gate statement is not an approval", fx(13, "Merge only on Zach's go, via scripts/safe_merge.sh."), [], "NONE", "GREEN", False),
    ("bad: receipt for another PR does not count", fx(9), [{"receipt_id": "2026-11-01--y-pr19--ZH", "refs": ["pr19"],
        "what_confirmed": ['Zach, verbatim: "merge 19"']}], "NONE", "GREEN", False),
    ("bad: green approval but fe-smoke stuck at 0s", fx(10, 'Zach, verbatim: "merge 10"', checks=STUCK), [], "FIRSTHAND_QUOTED", "STUCK_0S", False),
    ("bad: approval but conflicting", fx(11, 'Zach, verbatim: "merge 11"', mergeable="CONFLICTING"), [], "FIRSTHAND_QUOTED", "GREEN", False),
    ("bad: zero checks", fx(12, 'Zach, verbatim: "merge 12"', checks=[]), [], "FIRSTHAND_QUOTED", "NONE", False),
]


def self_test():
    ok = 0
    for name, pr, rc, want_a, want_c, want_ready in CASES:
        r = ledger_row(pr, rc, {}, NOW)
        got = (r["approval"], r["checks"], r["proposal"].startswith("READY"))
        good = got == (want_a, want_c, want_ready)
        ok += good
        print(("PASS " if good else "FAIL ") + name + ("" if good else "  got %s want %s" % (got, (want_a, want_c, want_ready))))
    # relayed approvals must say so in the proposal
    r2 = ledger_row(CASES[1][1], [], {}, NOW)
    flag = "relayed" in r2["proposal"]
    print(("PASS " if flag else "FAIL ") + "relayed approval is labelled in the proposal")
    # the script has no merge, push or write path
    src = open(os.path.abspath(__file__)).read()
    forbidden = ["pr " + "merge", "git " + "push", "pr " + "comment", "execute" + "_sql", "INSERT " + "INTO"]
    clean = not any(f in src for f in forbidden)
    print(("PASS " if clean else "FAIL ") + "no merge, push, comment or write path in this script")
    total = len(CASES) + 2
    passed = ok + flag + clean
    print("self-test: %d/%d" % (passed, total))
    return passed == total


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--receipts", default=RECEIPTS)
    ap.add_argument("--fixture", help="JSON list of PRs in gh's shape, instead of calling gh")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        sys.exit(0 if self_test() else 2)
    if a.fixture:
        prs = json.load(open(a.fixture))
    else:
        r = sh(["gh", "pr", "list", "--state", "open", "--limit", "100", "--json", PR_FIELDS])
        if r.returncode != 0:
            print("approvals_ledger: gh unavailable: " + r.stderr.strip(), file=sys.stderr)
            sys.exit(1)
        prs = json.loads(r.stdout)
        for p in prs:
            c = sh(["gh", "pr", "view", str(p["number"]), "--json", "commits"])
            p["commits"] = json.loads(c.stdout).get("commits", []) if c.returncode == 0 else []
    receipts, note = load_receipts(a.receipts)
    now = dt.datetime.now(dt.timezone.utc)
    wt = worktree_branches()
    rows = [ledger_row(p, receipts, wt, now) for p in sorted(prs, key=lambda p: -p["number"])]
    if a.json:
        print(json.dumps({"receipts": note, "prs": rows}, indent=2))
    else:
        render(rows, note)


if __name__ == "__main__":
    main()
