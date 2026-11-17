#!/usr/bin/env python3
"""pr_brief_check.py: keep design briefs tied to big PRs, and keep their status true.

A design brief is a `_PROPOSALS/*.md` file (design spec, product requirements, implementation
plan) published as a private Artifact page. This check covers the two ways that habit broke:

  MISSING  an open PR at or over the size bar (800 changed lines, or 10 files) has no brief:
           no `_PROPOSALS/` doc names it in `pr:`, and its body cites no `_PROPOSALS/` path.
           Opt out in the PR body with a line `design-brief: skip <reason>` (generated files,
           mechanical sweeps).
  STALE    a brief's `pr:` PR is MERGED or CLOSED but its `status:` does not say so, or says
           "not merged"; or the PR is OPEN and the status claims it merged. (Cause, 2026-11-11:
           the honest-proposals page asked for the merge of PR 2072 two days after it merged.)
  RERENDER a brief's `rendered:` HTML was last committed before the brief itself, so the page
           may still show the old status. Republish the Artifact too.

Read-only. Never edits a brief, a page or a PR.

  python3 scripts/pr_brief_check.py            # report every finding
  python3 scripts/pr_brief_check.py --line     # one line for the session-start hook
  python3 scripts/pr_brief_check.py --check    # exit 1 on any MISSING or STALE finding
  python3 scripts/pr_brief_check.py --self-test

Thresholds (800 lines, 10 files) are a judgment call, not measured; tune here.
Stdlib plus the `gh` CLI. On any gh failure it says so and skips the network checks.
"""
import argparse, json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROPOSALS = ROOT / "_PROPOSALS"
MAX_LINES, MAX_FILES = 800, 10
SKIP_RE = re.compile(r"^\s*design-brief:\s*skip\b", re.I | re.M)
CITE_RE = re.compile(r"_PROPOSALS/[\w.\-]+\.md")
NUM_RE = re.compile(r"\d+")


def frontmatter(text):
    """Flat `key: value` pairs from a leading --- block. Enough for these docs; no YAML dep."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    out = {}
    for line in text[3:end].splitlines():
        m = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if m:
            out[m.group(1).lower()] = m.group(2).strip()
    return out


def load_briefs():
    briefs = []
    for p in sorted(PROPOSALS.glob("*.md")):
        fm = frontmatter(p.read_text(errors="replace"))
        prs = [int(n) for n in NUM_RE.findall(fm.get("pr", ""))]
        briefs.append({"path": str(p.relative_to(ROOT)), "status": fm.get("status", ""),
                       "prs": prs, "rendered": fm.get("rendered", "")})
    return briefs


def status_drift(status, state):
    """Return a reason string if `status` contradicts the PR `state`, else None."""
    s = status.lower()
    says_not_merged = bool(re.search(r"\bnot (yet )?merged\b|\bunmerged\b|\bawaiting (the )?merge\b", s))
    says_merged = bool(re.search(r"\bmerged\b|\bshipped\b|\bdone\b", s)) and not says_not_merged
    if state == "MERGED" and not says_merged:
        return "PR merged; status does not say merged" + (" (it says not merged)" if says_not_merged else "")
    if state == "CLOSED" and not re.search(r"\bclosed\b|\babandoned\b|\bsuperseded\b|\bcomposted\b", s):
        return "PR closed unmerged; status does not say closed"
    if state == "OPEN" and says_merged and "merged" in s:
        return "PR still open; status says merged"
    return None


def find_missing(open_prs, briefs):
    cited = {n for b in briefs for n in b["prs"]}
    out = []
    for pr in open_prs:
        lines = pr.get("additions", 0) + pr.get("deletions", 0)
        files = pr.get("changedFiles", 0)
        if lines < MAX_LINES and files < MAX_FILES:
            continue
        body = pr.get("body") or ""
        if pr["number"] in cited or CITE_RE.search(body) or SKIP_RE.search(body):
            continue
        out.append(("MISSING", f"PR {pr['number']} ({lines} lines, {files} files) has no design brief: "
                               f"{pr.get('title', '')[:70]}"))
    return out


def find_stale(briefs, pr_state):
    out = []
    for b in briefs:
        for n in b["prs"]:
            state = pr_state.get(n)
            if not state:
                continue
            why = status_drift(b["status"], state)
            if why:
                out.append(("STALE", f"{b['path']}: PR {n} {why}"))
    return out


def _commit_time(path):
    r = subprocess.run(["git", "-C", str(ROOT), "log", "-1", "--format=%ct", "--", path],
                       capture_output=True, text=True)
    return int(r.stdout.strip() or 0)


def find_rerender(briefs, ctime=_commit_time):
    out = []
    for b in briefs:
        if not b["prs"] or not b["rendered"]:
            continue
        rendered = b["rendered"].split()[0]
        r, m = ctime(rendered), ctime(b["path"])
        if r and m and r < m:
            out.append(("RERENDER", f"{b['path']}: {rendered} is older than the brief; re-render and republish"))
    return out


def _gh(args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=20, cwd=ROOT)
    if r.returncode:
        raise RuntimeError(r.stderr.strip()[:200])
    return json.loads(r.stdout)


def run():
    briefs = load_briefs()
    findings, notes = [], []
    try:
        open_prs = _gh(["pr", "list", "--state", "open", "--limit", "100",
                        "--json", "number,title,additions,deletions,changedFiles,body"])
        findings += find_missing(open_prs, briefs)
        pr_state = {}
        for n in sorted({n for b in briefs for n in b["prs"]}):
            pr_state[n] = _gh(["pr", "view", str(n), "--json", "state"])["state"]
        findings += find_stale(briefs, pr_state)
    except (RuntimeError, subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError) as e:
        notes.append(f"gh unavailable, MISSING and STALE skipped ({e})")
    findings += find_rerender(briefs)
    return briefs, findings, notes


def self_test():
    ok = True
    def expect(name, cond):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + name)
        ok &= bool(cond)

    fm = frontmatter("---\ntitle: X\npr: 2072, 2080\nstatus: APPROVED\n---\nbody")
    expect("frontmatter parses pr list", [int(n) for n in NUM_RE.findall(fm["pr"])] == [2072, 2080])
    # The real case: approved, built, PR merged, status silent on the merge.
    expect("merged PR + silent status is stale",
           status_drift('APPROVED 2026-11-08; v0.1 built privately, see PR', "MERGED"))
    expect("merged PR + 'not merged' is stale", status_drift("built, not merged", "MERGED"))
    expect("merged PR + 'MERGED 2026-11-09' is fresh", status_drift("MERGED 2026-11-09 (PR 2072)", "MERGED") is None)
    expect("open PR + 'not merged' is fresh", status_drift("built, not merged", "OPEN") is None)
    expect("open PR + 'merged' is stale", status_drift("MERGED", "OPEN"))
    expect("closed PR + silent status is stale", status_drift("APPROVED", "CLOSED"))
    expect("closed PR + 'superseded' is fresh", status_drift("SUPERSEDED by 2100", "CLOSED") is None)

    briefs = [{"path": "_PROPOSALS/a.md", "status": "APPROVED", "prs": [1], "rendered": "r.html"}]
    big = {"number": 9, "title": "big", "additions": 900, "deletions": 0, "changedFiles": 3, "body": ""}
    expect("big uncited PR is missing", len(find_missing([big], briefs)) == 1)
    expect("small PR is not missing", not find_missing([dict(big, additions=10)], briefs))
    expect("10 files counts as big", len(find_missing([dict(big, additions=10, changedFiles=10)], briefs)) == 1)
    expect("brief citing the PR clears it", not find_missing([dict(big, number=1)], briefs))
    expect("body citing a brief clears it",
           not find_missing([dict(big, body="Design brief: _PROPOSALS/2026-11-11-x-design.md")], briefs))
    expect("skip line clears it", not find_missing([dict(big, body="design-brief: skip generated data")], briefs))
    expect("stale finding names the brief", find_stale(briefs, {1: "MERGED"})[0][1].startswith("_PROPOSALS/a.md"))
    times = {"r.html": 100, "_PROPOSALS/a.md": 200}
    expect("older render is flagged", len(find_rerender(briefs, times.get)) == 1)
    times["r.html"] = 300
    expect("newer render is clean", not find_rerender(briefs, times.get))
    print("self-test", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--line", action="store_true", help="one summary line (session-start hook)")
    ap.add_argument("--check", action="store_true", help="exit 1 on MISSING or STALE")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    briefs, findings, notes = run()
    linked = sum(1 for b in briefs if b["prs"])
    if a.line:
        if findings or notes:
            kinds = {}
            for k, _ in findings:
                kinds[k] = kinds.get(k, 0) + 1
            parts = [f"{v} {k.lower()}" for k, v in sorted(kinds.items())] + notes
            first = findings[0][1] if findings else ""
            print(f"pr-briefs: {', '.join(parts)} (run python3 scripts/pr_brief_check.py)"
                  + (f"\npr-briefs:   {first}" if first else ""))
        return 0
    print(f"pr-briefs: {len(briefs)} briefs, {linked} linked to a PR, {len(findings)} finding(s)")
    for k, msg in findings:
        print(f"  {k:8} {msg}")
    for n in notes:
        print(f"  NOTE     {n}")
    return 1 if a.check and any(k in ("MISSING", "STALE") for k, _ in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
