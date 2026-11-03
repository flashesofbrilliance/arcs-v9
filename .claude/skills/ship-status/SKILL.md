---
name: ship-status
description: Answer "did it ship?" for any branch in one run - committed locally, pushed, PR (number, state), checks (each name and conclusion), merged (merge commit), production deployment contains the commit, live URL serves it. Use for every "did we commit / push / merge / deploy", "is it live", "was it merged", "is the PR green" question, before answering from memory or from a single git command. Wraps scripts/ship_status.py.
---

# /ship-status: every stage from commit to live URL

On 2026-10-31 the question "did we actually commit, merge, deploy?" took about 15 tool calls
and produced two wrong answers on the way: a `git ls-remote 'refs/pull/*'` run in a sandbox
that could not reach GitHub came back empty and was read as "no PR", and pushes were said to
need Zach's Terminal when a native shell tool could do them. This skill is one command that
answers every stage and says NOT-CHECKED, never "none", when a source cannot be reached.

## Run it

```bash
python3 scripts/ship_status.py --branch claude/x                          # one branch
python3 scripts/ship_status.py --branch claude/x --branch claude/y        # several
python3 scripts/ship_status.py --branch claude/x --url https://good.arcs.care/page   # plus live probe
python3 scripts/ship_status.py --repo OWNER/NAME --branch B                # run from that repo's clone
python3 scripts/ship_status.py --branch claude/x --json                   # machine-readable
```

`--repo` defaults to the `origin` remote of the current directory. Git stages (committed,
pushed, merged, ancestor tests) describe the clone you run it from, so run it from the clone
of the repo you ask about. It always exits 0: it reports, it never pushes, merges or fixes.

## Where it must run

It needs git and `gh` with GitHub credentials and network. Those live on Zach's Mac.

| Place | Works | Why |
|---|---|---|
| Desktop Commander `start_process` (native macOS shell), with `export PATH=/opt/homebrew/bin:/usr/local/bin:$PATH;` | yes | `gh` is logged in with repo scope; git uses the Mac's credential helper |
| A local terminal on the Mac | yes | same credentials |
| Cloud `Bash` tool | no | cannot reach github.com |
| `device_bash` (the Cowork Linux VM) | no | cannot reach github.com |

Pushing works from the same native shell. Do not tell Zach a push needs his Terminal.

## What each stage means

| Stage | YES means | Source |
|---|---|---|
| committed | `refs/heads/<branch>` exists in this clone | `git rev-parse` |
| pushed | the branch exists on origin; says whether local matches, is behind, or is ahead (unpushed) | `git ls-remote`, then `gh api branches` |
| pr | a PR has this branch as head; open first, then merged, then closed; lists the others | `gh pr list --state all` |
| checks | every check run and commit status on the head sha passed; PENDING while any is running; NO if any failed | `gh api commits/<sha>/check-runs` and `/status` |
| merged | the PR is MERGED (merge commit shown), or the head is an ancestor of the base branch | `gh`, `git merge-base --is-ancestor` |
| production | the newest deployment in environment Production / production / PRODUCTION whose latest status is success contains the head or the merge commit | `gh api deployments`, `deployments/<id>/statuses` |
| live | each `--url` answers 2xx; shows HTTP status, final URL after redirects, and `<title>` | `curl -L -m 20` |

## NOT-CHECKED is not NO

- **NO**: the source answered and the thing is absent ("gh pr list answered: no pull request").
- **NOT-CHECKED**: the source could not be reached or refused (network, auth, timeout, a missing
  object). The evidence line carries the error. Say "unverified", never "none" or "not merged".
- **The rule**: an empty result from a tool that cannot reach the source is NOT-CHECKED. If every
  remote stage reads NOT-CHECKED, you are in the wrong shell; move to one in the table above.
- `pushed` NO with a merged PR is normal: the branch was deleted after merge.
- `merged` is judged against the PR's own base. A PR stacked on another branch can be merged
  there and still be absent from main; the `production` line settles that.
- `production` YES is about GitHub deployment records (Vercel posts them). The `live` stage is the
  only proof the URL serves the page; give `--url` whenever a page is the point.

## Rules

1. Answer any shipped / merged / live question from this script's output, quoting the stage
   lines. Do not stitch the answer together from separate git and gh calls.
2. Copy shas, PR numbers and counts from the output; never type them from memory.
3. A new false-answer class (a stage that said NO or YES when it should have said NOT-CHECKED)
   goes into `ship_status.py` with a proof run, not into this prose.
