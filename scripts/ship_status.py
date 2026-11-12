#!/usr/bin/env python3
"""ship_status.py: report every stage from local commit to live URL for one or more branches.

Stages per branch, each YES / NO / PENDING / NOT-CHECKED with the evidence:

  committed   the branch exists as a local ref (sha)
  pushed      the branch exists on the remote (sha, in sync with local or not)
  pr          a pull request has this branch as head (number, state, url)
  checks      check runs and commit statuses on the head sha (each name and conclusion)
  merged      the PR merged (merge commit), or the head is an ancestor of the base branch
  production  the newest successful GitHub deployment in a Production environment
              contains the head (git merge-base --is-ancestor)
  live        each --url answers 2xx (HTTP status and <title>)

The rule this tool exists for: an empty answer from a source that could not be reached is
NOT-CHECKED, never NO. NO is only printed when the source answered and the thing is absent.

Shells out to git, gh and curl only (stdlib Python). Read-only: it never pushes, merges,
deploys or fixes anything, and it always exits 0.

Usage:
  python3 scripts/ship_status.py --branch claude/x [--branch claude/y] [--url https://...] [--json]
  python3 scripts/ship_status.py --repo OWNER/NAME --branch B      # run from that repo's clone

Must run where git and gh hold GitHub credentials and network (a native shell on the Mac,
for example Desktop Commander or a local terminal). A sandbox that cannot reach github.com
will report NOT-CHECKED for every remote stage, which is the correct answer there.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
import tempfile

TIMEOUT = 45
PROD_ENVS = ("Production", "production", "PRODUCTION")
OK_CONCLUSIONS = {"success", "neutral", "skipped"}

YES, NO, PENDING, NOT_CHECKED = "YES", "NO", "PENDING", "NOT-CHECKED"


def run(cmd: list[str], timeout: int = TIMEOUT) -> tuple[int, str, str]:
    """Run a command; return (rc, stdout, stderr). rc 127 = missing tool, 124 = timeout."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except FileNotFoundError:
        return 127, "", f"{cmd[0]}: command not found"
    except subprocess.TimeoutExpired:
        return 124, "", f"timed out after {timeout}s: {' '.join(cmd[:4])}"


def short_err(err: str, out: str = "") -> str:
    text = (err or out or "").strip().splitlines()
    return text[-1][:200] if text else "no output"


def stage(status: str, evidence: str, **data) -> dict:
    return {"status": status, "evidence": evidence, **data}


def gh_json(args: list[str]):
    """Return (ok, parsed_or_None, error). ok False means GitHub was not reached or refused."""
    rc, out, err = run(["gh", *args])
    if rc != 0:
        return False, None, short_err(err, out)
    try:
        return True, json.loads(out) if out.strip() else None, ""
    except json.JSONDecodeError as e:
        return False, None, f"unparseable gh output: {e}"


def gh_api_status(path: str):
    """gh api that distinguishes 404 (source answered: absent) from unreachable."""
    rc, out, err = run(["gh", "api", path])
    if rc == 0:
        try:
            return "ok", json.loads(out)
        except json.JSONDecodeError:
            return "error", "unparseable gh api output"
    msg = short_err(err, out)
    if "HTTP 404" in err or "Not Found" in err:
        return "404", msg
    return "error", msg


def default_repo() -> str | None:
    rc, out, _ = run(["git", "remote", "get-url", "origin"])
    if rc != 0:
        return None
    m = re.search(r"github\.com[:/]([^/]+)/([^/\s]+?)(?:\.git)?/?$", out.strip())
    return f"{m.group(1)}/{m.group(2)}" if m else None


def have_object(sha: str) -> bool:
    return run(["git", "cat-file", "-e", f"{sha}^{{commit}}"])[0] == 0


def ensure_object(sha: str) -> bool:
    if have_object(sha):
        return True
    run(["git", "fetch", "-q", "origin", sha], timeout=90)
    return have_object(sha)


def is_ancestor(a: str, b: str) -> bool | None:
    """True/False if both objects are present locally, None if it cannot be decided."""
    if not (ensure_object(a) and ensure_object(b)):
        return None
    rc, _, _ = run(["git", "merge-base", "--is-ancestor", a, b])
    if rc in (0, 1):
        return rc == 0
    return None


# ---------------------------------------------------------------- stages

def st_committed(branch: str) -> dict:
    rc, out, _ = run(["git", "rev-parse", "--verify", "-q", f"refs/heads/{branch}"])
    if rc == 0 and out.strip():
        sha = out.strip()
        return stage(YES, f"local refs/heads/{branch} at {sha[:12]}", sha=sha)
    return stage(NO, f"no local branch {branch} in this clone (it may still exist on the remote)")


def st_pushed(repo: str, branch: str, local_sha: str | None) -> dict:
    rc, out, err = run(["git", "ls-remote", "origin", f"refs/heads/{branch}"], timeout=60)
    remote_sha = None
    if rc == 0:
        line = out.strip().split()
        remote_sha = line[0] if line else None
        source = "git ls-remote origin"
    else:
        # fall back to the API before giving up; an ls-remote failure is not an answer
        kind, data = gh_api_status(f"repos/{repo}/branches/{branch}")
        if kind == "ok":
            remote_sha = data.get("commit", {}).get("sha")
            source = "gh api branches"
        elif kind == "404":
            return stage(NO, f"gh api: branch {branch} not found on {repo} "
                             f"(never pushed, or deleted after merge); ls-remote failed: {short_err(err)}")
        else:
            return stage(NOT_CHECKED, f"remote unreachable: ls-remote: {short_err(err)}; gh api: {data}")
    if not remote_sha:
        return stage(NO, f"{source} answered: no refs/heads/{branch} on origin "
                         "(never pushed, or deleted after merge)")
    sync = ""
    if local_sha:
        if local_sha == remote_sha:
            sync = "; local matches remote"
        else:
            rel = "differs"
            if is_ancestor(local_sha, remote_sha):
                rel = "behind remote"
            elif is_ancestor(remote_sha, local_sha):
                rel = "ahead of remote: unpushed commits"
            sync = f"; local is {local_sha[:12]} ({rel})"
    return stage(YES, f"origin/{branch} at {remote_sha[:12]} ({source}){sync}", sha=remote_sha)


def st_pr(repo: str, branch: str) -> dict:
    ok, data, err = gh_json(["pr", "list", "--repo", repo, "--head", branch, "--state", "all",
                             "--limit", "30", "--json",
                             "number,state,url,headRefOid,mergeCommit,mergedAt,baseRefName,title"])
    if not ok:
        return stage(NOT_CHECKED, f"gh pr list failed: {err}")
    prs = data or []
    if not prs:
        return stage(NO, f"gh pr list answered: no pull request with head {branch} on {repo}")
    order = {"OPEN": 0, "MERGED": 1, "CLOSED": 2}
    prs.sort(key=lambda p: (order.get(p.get("state"), 3), -int(p.get("number", 0))))
    pr = prs[0]
    others = ""
    if len(prs) > 1:
        others = "; also " + ", ".join(f"#{p['number']} {p['state']}" for p in prs[1:])
    return stage(YES, f"PR #{pr['number']} {pr['state']} into {pr.get('baseRefName')}: {pr['url']}{others}",
                 pr=pr, all=[{"number": p["number"], "state": p["state"]} for p in prs])


def st_checks(repo: str, sha: str | None) -> dict:
    if not sha:
        return stage(NOT_CHECKED, "no head sha to look up (branch not found locally, remotely or in a PR)")
    ok, runs, err = gh_json(["api", f"repos/{repo}/commits/{sha}/check-runs?per_page=100"])
    if not ok:
        return stage(NOT_CHECKED, f"gh api check-runs failed: {err}")
    ok2, combined, err2 = gh_json(["api", f"repos/{repo}/commits/{sha}/status"])
    items = []
    for r in (runs or {}).get("check_runs", []):
        concl = r.get("conclusion") or r.get("status")
        items.append({"name": r.get("name"), "result": concl, "kind": "check"})
    if ok2:
        for s in (combined or {}).get("statuses", []):
            items.append({"name": s.get("context"), "result": s.get("state"), "kind": "status"})
    note = "" if ok2 else f" (commit statuses NOT-CHECKED: {err2})"
    if not items:
        return stage(NO, f"GitHub answered: no check runs or statuses on {sha[:12]}{note}", items=[])
    bad = [i for i in items if i["result"] in ("failure", "error", "cancelled", "timed_out",
                                               "action_required", "startup_failure", "stale")]
    pend = [i for i in items if i["result"] in ("queued", "in_progress", "pending", "waiting", "requested")]
    status = NO if bad else PENDING if pend else YES
    summary = ", ".join(f"{i['name']}={i['result']}" for i in items)
    return stage(status, f"{len(items)} on {sha[:12]}: {summary}{note}", items=items)


def st_merged(repo: str, pr_stage: dict, head: str | None, base: str) -> dict:
    pr = pr_stage.get("pr")
    if pr and pr.get("state") == "MERGED":
        mc = (pr.get("mergeCommit") or {}).get("oid")
        return stage(YES, f"PR #{pr['number']} merged {pr.get('mergedAt')} as {mc[:12] if mc else '?'}",
                     merge_commit=mc)
    if not head:
        return stage(NOT_CHECKED, "no head sha to test against the base branch")
    rc, _, err = run(["git", "fetch", "-q", "origin", base], timeout=90)
    if rc != 0:
        return stage(NOT_CHECKED, f"git fetch origin {base} failed: {short_err(err)}")
    anc = is_ancestor(head, f"origin/{base}")
    if anc is None:
        return stage(NOT_CHECKED, f"could not compare {head[:12]} with origin/{base} (object missing)")
    if anc:
        return stage(YES, f"{head[:12]} is an ancestor of origin/{base} (merged without a merged PR)",
                     merge_commit=None)
    why = f"PR #{pr['number']} is {pr['state']}" if pr else "no PR"
    if pr_stage["status"] == NOT_CHECKED:
        why = "PR state not checked"
    return stage(NO, f"{why}; {head[:12]} is not in origin/{base}")


def list_prod_deployments(repo: str):
    seen, deps, errors, answered = set(), [], [], False
    for env in PROD_ENVS:
        ok, data, err = gh_json(["api", f"repos/{repo}/deployments?environment={env}&per_page=30"])
        if not ok:
            errors.append(f"{env}: {err}")
            continue
        answered = True
        for d in data or []:
            if d["id"] not in seen:
                seen.add(d["id"])
                deps.append(d)
    deps.sort(key=lambda d: d.get("created_at", ""), reverse=True)
    return answered, deps, errors


def st_production(repo: str, targets: list[str]) -> dict:
    """targets: shas whose presence in production we test (head, then merge commit)."""
    answered, deps, errors = list_prod_deployments(repo)
    if not answered:
        return stage(NOT_CHECKED, "gh api deployments failed: " + "; ".join(errors))
    if not deps:
        return stage(NO, f"GitHub answered: no deployments in environments {', '.join(PROD_ENVS)} on {repo}")
    if not targets:
        return stage(NOT_CHECKED, "no sha to look for in production")
    latest_ok = None
    for d in deps:
        ok, statuses, err = gh_json(["api", f"repos/{repo}/deployments/{d['id']}/statuses?per_page=10"])
        if not ok:
            continue
        state = statuses[0]["state"] if statuses else "none"
        if state == "success":
            latest_ok = (d, statuses[0])
            break
    if not latest_ok:
        return stage(NO, f"{len(deps)} production deployments found, none with a latest status of success")
    d, s = latest_ok
    dep_sha = d["sha"]
    info = (f"deployment {d['id']} env {d['environment']} sha {dep_sha[:12]} "
            f"created {d.get('created_at')} status {s['state']} {s.get('environment_url') or ''}").strip()
    data = {"deployment_id": d["id"], "environment": d["environment"], "deployed_sha": dep_sha,
            "environment_url": s.get("environment_url")}
    undecided = []
    for t in targets:
        anc = is_ancestor(t, dep_sha)
        if anc:
            return stage(YES, f"{t[:12]} is in the newest successful {info}", **data)
        if anc is None:
            undecided.append(t[:12])
    if undecided and len(undecided) == len(targets):
        return stage(NOT_CHECKED, f"could not compare {', '.join(undecided)} with {dep_sha[:12]} "
                                  f"(object missing locally); {info}", **data)
    return stage(NO, f"{', '.join(t[:12] for t in targets)} not in the newest successful {info}", **data)


def probe_url(url: str) -> dict:
    with tempfile.NamedTemporaryFile(suffix=".html") as tmp:
        rc, out, err = run(["curl", "-sS", "-L", "-m", "20", "-o", tmp.name,
                            "-w", "%{http_code} %{url_effective}", url], timeout=30)
        if rc != 0:
            return stage(NOT_CHECKED, f"{url}: curl could not connect: {short_err(err)}", url=url)
        code, _, final = out.strip().partition(" ")
        body = open(tmp.name, "rb").read(400_000).decode("utf-8", "replace")
    m = re.search(r"<title[^>]*>(.*?)</title>", body, re.I | re.S)
    title = html.unescape(re.sub(r"\s+", " ", m.group(1)).strip()) if m else None
    status = YES if code.startswith("2") else NO
    moved = f" -> {final}" if final and final != url else ""
    return stage(status, f"{url}{moved}: HTTP {code}, title {title!r}", url=url, http=code, title=title)


# ---------------------------------------------------------------- report

def report_branch(repo: str, branch: str, base: str, live: list[dict]) -> dict:
    s = {}
    s["committed"] = st_committed(branch)
    s["pushed"] = st_pushed(repo, branch, s["committed"].get("sha"))
    s["pr"] = st_pr(repo, branch)
    pr = s["pr"].get("pr") or {}
    head = s["pushed"].get("sha") or pr.get("headRefOid") or s["committed"].get("sha")
    s["checks"] = st_checks(repo, head)
    s["merged"] = st_merged(repo, s["pr"], head, pr.get("baseRefName") or base)
    targets = [t for t in (head, s["merged"].get("merge_commit")) if t]
    s["production"] = st_production(repo, targets)
    s["live"] = live
    return {"repo": repo, "branch": branch, "head": head, "stages": s}


def print_text(rep: dict) -> None:
    print(f"ship-status  {rep['repo']}  {rep['branch']}  head {rep['head'][:12] if rep['head'] else '?'}")
    for name in ("committed", "pushed", "pr", "checks", "merged", "production"):
        st = rep["stages"][name]
        print(f"  {name:<11} {st['status']:<12} {st['evidence']}")
    if not rep["stages"]["live"]:
        print(f"  {'live':<11} {NOT_CHECKED:<12} no --url given")
    for st in rep["stages"]["live"]:
        print(f"  {'live':<11} {st['status']:<12} {st['evidence']}")
    print()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--repo", help="OWNER/NAME (default: parsed from git remote origin)")
    ap.add_argument("--branch", action="append", required=True, help="branch name (repeatable)")
    ap.add_argument("--url", action="append", default=[], help="live URL to probe (repeatable)")
    ap.add_argument("--base", default=None, help="base branch for the ancestor test (default: repo default)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    a = ap.parse_args()

    origin = default_repo()
    repo = a.repo or origin
    notes = []
    if not repo:
        print("ship-status: no --repo and no GitHub origin in this directory; nothing checked")
        return 0
    if a.repo and origin and origin.lower() != a.repo.lower():
        notes.append(f"warning: --repo {a.repo} but this clone's origin is {origin}; "
                     "git stages (committed, pushed, merged, ancestor tests) describe this clone")
    base = a.base
    if not base:
        ok, data, _ = gh_json(["repo", "view", repo, "--json", "defaultBranchRef"])
        base = (data or {}).get("defaultBranchRef", {}).get("name") if ok else None
        if not base:
            base = "main"
            notes.append("default branch NOT-CHECKED (gh repo view failed); assuming main")

    live = [probe_url(u) for u in a.url]
    reports = [report_branch(repo, b, base, live) for b in a.branch]
    if a.json:
        print(json.dumps({"notes": notes, "base": base, "reports": reports}, indent=2))
    else:
        for n in notes:
            print(n)
        for r in reports:
            print_text(r)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # report, never crash with a nonzero code
        print(f"ship-status: internal error, nothing further checked: {e!r}")
        sys.exit(0)
