#!/usr/bin/env python3
"""disclosure_sweep: retro sweep for the earliest dated trace of each mechanism across every local clone.

python3 scripts/disclosure_sweep.py                 # prints the table; writes nothing
python3 scripts/disclosure_sweep.py --write         # also writes _STATE/disclosure-retro-sweep-<today>.md
python3 scripts/disclosure_sweep.py --self-test     # prove it finds a planted term and reports a miss

Read-only over git and `gh`. Standard library only. Mechanical: a term list, `git log --reverse -i -G`,
and the remote's visibility from `gh api`. It reports commit dates, which are conception or authorship
evidence, NOT proof of public disclosure: a commit in a private repo discloses nothing by itself. Judgement
about what a date means is left to counsel. Nothing here contacts anyone.
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = os.path.expanduser("~")
REPOS = [ROOT, HOME + "/arcs-care-local", HOME + "/arcs-decision-receipts"]  # ~/arcs is a stale second clone of arcs-v9 and only repeats it
TERMS = {
    "ARCS Law (S_min)": r"S_min|\(S *- *S_min\)",
    "Y-gate": r"y-gate|ygate|yellow gate",
    "Decision receipt predicted vs actual": r"regretScore|predicted.{0,30}actual",
    "Kintsugi": r"kintsugi",
    "Orthogonal echo": r"orthogonal echo",
    "Write-lock": r"write-lock",
    "Hypersphere manifold": r"hypersphere",
    "Golden inchworm": r"inchworm",
    "Notomation": r"notomation",
}


def git(repo, *a):
    return subprocess.run(["git", "-C", repo] + list(a), capture_output=True, text=True, timeout=300).stdout.strip()


def visibility(repo):
    url = git(repo, "remote", "get-url", "origin")
    m = re.search(r"github\.com[:/]([^/]+/[^/.]+?)(?:\.git)?$", url)
    if not m:
        return "no GitHub remote", ""
    r = subprocess.run(["gh", "api", "repos/" + m.group(1), "--jq", "[.visibility,.created_at]|@tsv"], capture_output=True, text=True)
    if r.returncode:
        return "unknown (gh failed)", m.group(1)
    v, c = r.stdout.strip().split("\t")
    return "%s, created %s" % (v, c[:10]), m.group(1)


def earliest(repo, pattern):
    out = git(repo, "log", "--all", "--reverse", "-i", "-G", pattern, "--format=%h %ad", "--date=short")
    return out.splitlines()[0] if out else None


def sweep(repos=REPOS, terms=TERMS):
    res = []
    for repo in repos:
        if not os.path.isdir(os.path.join(repo, ".git")) and not os.path.isfile(os.path.join(repo, ".git")):
            res.append({"repo": repo, "missing": True})
            continue
        vis, slug = visibility(repo)
        first = git(repo, "log", "--all", "--reverse", "--format=%h %ad", "--date=short").splitlines()[:1]
        res.append({"repo": repo, "slug": slug, "vis": vis, "first_commit": first[0] if first else None,
                    "hits": {t: earliest(repo, p) for t, p in terms.items()}})
    return res


def render(res, today):
    L = ["# Retro sweep: earliest dated trace per mechanism, all local clones", "",
         "Generated %s by `scripts/disclosure_sweep.py` (read-only; `git log --all --reverse -i -G`)." % today, "",
         "Commit dates are authorship/conception evidence. A commit in a private repo is not a disclosure by itself; "
         "counsel decides what each date means. Term hits are LEADS: they match substrings and other meanings (S_min in a test name, a mathematical hypersphere, database write-locks), so read the matching text before relying on a cell. A blank cell means no commit touched that term in that clone, "
         "NOT that the idea did not exist (clones may be partial, history was rewritten once on 2026-06-03 in arcs-v9).", ""]
    names = list(TERMS)
    L.append("| Clone | GitHub remote today | First commit | " + " | ".join(names) + " |")
    L.append("|" + "---|" * (3 + len(names)))
    for r in res:
        if r.get("missing"):
            L.append("| %s | not found | | " % r["repo"] + " | ".join([""] * len(names)) + " |")
            continue
        label = r["slug"].split("/")[-1] if r.get("slug") else os.path.basename(r["repo"].rstrip("/"))
        L.append("| %s | %s %s | %s | " % (label, r["slug"], r["vis"], r["first_commit"] or "-") +
                 " | ".join((r["hits"][n] or "-") for n in names) + " |")
    allhits = [(h.split()[1], h.split()[0], r["repo"], n) for r in res if not r.get("missing") for n, h in r["hits"].items() if h]
    if allhits:
        d, sha, repo, n = min(allhits)
        L += ["", "Earliest hit of any term in any clone: **%s** (`%s`, %s, term: %s)." % (d, sha, os.path.basename(repo), n)]
    L += ["", "Gaps this sweep cannot close (ask Zach): notes apps, Drive/Dropbox, email, transcripts outside git, "
          "clones not on this machine, GitHub repos with no local clone (gigi, arcs-field-scan, arcs-canon, arcs-field-os, arcs-immune-system)."]
    return "\n".join(L) + "\n"


def self_test():
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["git", "-C", d, "init", "-q"], check=True)
        open(os.path.join(d, "a.txt"), "w").write("the ARCS Law uses S_min\n")
        env = dict(os.environ, GIT_AUTHOR_DATE="2025-01-02T10:00:00", GIT_COMMITTER_DATE="2025-01-02T10:00:00",
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        subprocess.run(["git", "-C", d, "add", "."], check=True, env=env)
        subprocess.run(["git", "-C", d, "commit", "-qm", "x"], check=True, env=env)
        hit = earliest(d, TERMS["ARCS Law (S_min)"])
        miss = earliest(d, TERMS["Kintsugi"])
        assert hit and hit.endswith("2025-01-02"), "planted term not found: %r" % hit
        assert miss is None, "false hit on absent term: %r" % miss
    print("self-test OK: finds the planted term at its commit date, reports None for an absent term")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    today = dt.date.today()
    text = render(sweep(), today)
    print(text)
    if a.write:
        p = os.path.join(ROOT, "_STATE", "disclosure-retro-sweep-%s.md" % today)
        open(p, "w").write(text)
        print("wrote " + os.path.relpath(p, ROOT))


if __name__ == "__main__":
    main()
