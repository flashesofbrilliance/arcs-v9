#!/usr/bin/env python3
"""claim_diff_probe: does an agent commit that claims tests actually change a test file?

Read-only probe over public GitHub repos, standard library plus the `gh` CLI. It backs the precision step of the
MCP-route test in _PROPOSALS/2026-11-03-first-product-decision.md section 5.

PRE-REGISTERED RULE (written 2026-11-03, before the run):
  - Sample: public repos whose recent commits carry an AI credit line (GitHub commit search), excluding
    flashesofbrilliance/*, up to --repos repos, last 30 commits each, merge commits skipped.
  - Agent commit: message carries an AI co-author or "Generated with Claude" line, or the author is a bot.
  - Test claim: the message says tests were added, pass, or cover the change (TEST_CLAIM below). Bare "verified" is
    NOT a test claim (it matched facts in bios on the first look).
  - Flag: a test-claiming agent commit whose changed files include no test file and no test config.
  - Hand check: the first 30 flags in run order, each labelled REAL (the record does not back the claim) or FALSE
    (the claim word is not a claim about this change, or tests sit at a path the pattern missed).
  - Decision: under 50% REAL among the 30 kills the claim-vs-diff premise. 50% or more lets it proceed to the
    demand test (outreach). The labels live in a JSON file next to the flags so the count is reproducible.

Usage:
  python3 scripts/claim_diff_probe.py --repos 50 --out <dir>      # writes flags.json
  python3 scripts/claim_diff_probe.py --score <dir>/labels.json    # prints REAL share and the decision
"""
import argparse, collections, json, re, subprocess, sys, time
from pathlib import Path

AGENT = re.compile(r"co-authored-by:[^\n]*(claude|copilot|cursor|codex|devin|aider|gemini)|generated with \[?claude", re.I)
TEST_CLAIM = re.compile(
    r"\b(add(ed|s|ing)? (unit |integration |e2e |regression )?tests?"
    r"|(with|includes?|including) (unit |integration )?tests?"
    r"|tests? (added|pass(es|ed|ing)?|green|cover(s|ed)?)"
    r"|all \d* ?tests? pass"
    r"|\d+ (new )?tests?\b"
    r"|test coverage|covered by tests?)", re.I)
TEST_FILE = re.compile(
    r"(^|/)(tests?|__tests__|specs?|e2e|cypress|playwright)/"
    r"|[._-](test|spec)s?\.[a-z0-9]+$|_test\.go$|(^|/)test_[^/]+\.py$|Tests?\.(swift|kt|java|cs)$"
    r"|(^|/)(jest|vitest|playwright|pytest|karma|cypress)\.config\.|(^|/)(pytest\.ini|conftest\.py|tox\.ini)$", re.I)


def gh(*args):
    time.sleep(0.4)  # pace calls; GitHub's secondary rate limit trips on bursts
    r = subprocess.run(["gh", "api", *args], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr.strip()[:200])
    return json.loads(r.stdout)


def sample_repos(n):
    repos = []
    for page in range(1, 6):
        for attempt in range(4):
            try:
                hits = gh("-X", "GET", "search/commits", "-f", 'q="Co-Authored-By: Claude" committer-date:>2026-09-15',
                          "-f", "per_page=100", "-f", f"page={page}")
                break
            except RuntimeError:
                time.sleep(60 * (attempt + 1))  # secondary rate limit: back off, then retry
        else:
            break  # keep the repos found so far
        for it in hits.get("items", []):
            name = it["repository"]["full_name"]
            if name not in repos and not name.lower().startswith("flashesofbrilliance/"):
                repos.append(name)
        if len(repos) >= n:
            break
        time.sleep(4)  # the search API allows few calls per minute
    return repos[:n]


def run(n, out):
    out.mkdir(parents=True, exist_ok=True)
    stats, flags = collections.Counter(), []
    for repo in sample_repos(n):
        try:
            commits = gh(f"repos/{repo}/commits", "-X", "GET", "-f", "per_page=30")
        except RuntimeError:
            stats["repo_errors"] += 1
            continue
        stats["repos"] += 1
        for c in commits:
            if len(c.get("parents", [])) > 1:
                continue
            msg = c["commit"]["message"]
            login = (c.get("author") or {}).get("login") or ""
            if not (AGENT.search(msg) or login.endswith("[bot]")):
                continue
            stats["agent_commits"] += 1
            m = TEST_CLAIM.search(msg)
            if not m:
                continue
            stats["test_claims"] += 1
            try:
                files = [f["filename"] for f in gh(f"repos/{repo}/commits/{c['sha']}").get("files", [])]
            except RuntimeError:
                stats["detail_errors"] += 1
                continue
            if any(TEST_FILE.search(f) for f in files):
                stats["backed"] += 1
                continue
            stats["flagged"] += 1
            flags.append({"repo": repo, "sha": c["sha"][:7], "claim": m.group(0), "message": msg[:1200],
                          "files": files[:40], "n_files": len(files)})
    (out / "flags.json").write_text(json.dumps({"stats": stats, "flags": flags}, indent=1))
    print(json.dumps(stats))
    print(f"wrote {out / 'flags.json'} ({len(flags)} flags)")


def score(labels_path):
    labels = json.loads(Path(labels_path).read_text())[:30]
    real = sum(1 for x in labels if x["label"] == "REAL")
    share = real / len(labels) if labels else 0
    print(f"REAL {real}/{len(labels)} = {share:.0%} -> {'PROCEED to demand test' if share >= 0.5 else 'KILL the premise'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", type=int, default=50)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--score")
    a = ap.parse_args()
    if a.score:
        score(a.score)
    elif a.out:
        run(a.repos, a.out)
    else:
        sys.exit("pass --out <dir> or --score <labels.json>")
