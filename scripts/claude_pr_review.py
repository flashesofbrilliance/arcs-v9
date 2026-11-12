#!/usr/bin/env python3
"""claude_pr_review.py: Claude Code reviews a PR and posts a head-bound verdict.

Why (Zach, 2026-11-12): Hermes opens PRs too, and every one of them should get a second
harness's review before merge: the code, plus a hardening pass on any documentation that is
not coherent, cohesive or clear, plus a check that each claim in the PR body is backed by
receipt evidence (a sha, a command and its exit code, a file path, a URL). Same Triune split
as the memory note: Hermes operates, Claude Code reviews as the Architect.

What it does, for one PR:
  1. reads the PR (head sha, branch, body, files, diff) with gh
  2. checks out the head into a throwaway detached worktree, so the reviewer reads the
     repo as the PR would leave it, not whatever the main checkout is parked on (gotcha 14)
  3. runs `claude -p` read-only (Read, Grep, Glob only) with a fixed JSON verdict schema
  4. posts the review as one PR comment and sets the commit status `claude-code-review`
     on that exact head sha: success = APPROVE, failure = CHANGES, error = the review
     could not run. A push makes a new head with no status, so an old approval never
     carries over.
safe_merge.sh requires that status to be SUCCESS on every `hermes/` branch.

Fail-closed: an auth error, a timeout, bad JSON or a missing field is verdict ERROR,
never APPROVE. Claude's `is_error` flag is checked; `subtype: success` alone is not proof
(seen 2026-11-12: an expired OAuth session returned subtype success with is_error true).

Usage:
  scripts/claude_pr_review.py <pr>             review and post (comment + status)
  scripts/claude_pr_review.py <pr> --dry-run   review, print, post nothing
  scripts/claude_pr_review.py --self-test      offline: fake gh and fake claude on PATH
Env: CLAUDE_REVIEW_BUDGET_USD (default 2.00), CLAUDE_REVIEW_TIMEOUT (seconds, default 900),
     CLAUDE_BIN / GH_BIN (default claude / gh).
Exit: 0 APPROVE · 1 CHANGES · 2 usage · 3 ERROR (review did not run)
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

STATUS_CONTEXT = "claude-code-review"
MARKER = "<!-- claude-code-review -->"
DOC_SUFFIXES = (".md", ".mdx", ".txt")
DOC_NAMES = ("AGENTS.md", "CLAUDE.md", "WORLD.md", "README.md")

SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["APPROVE", "CHANGES"]},
        "summary": {"type": "string"},
        "code_findings": {"type": "array", "items": {"$ref": "#/$defs/finding"}},
        "doc_findings": {"type": "array", "items": {"$ref": "#/$defs/finding"}},
        "receipt_gaps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "claim": {"type": "string"},
                    "missing": {"type": "string"},
                },
                "required": ["claim", "missing"],
            },
        },
    },
    "required": ["verdict", "summary", "code_findings", "doc_findings", "receipt_gaps"],
    "$defs": {
        "finding": {
            "type": "object",
            "properties": {
                "severity": {"type": "string", "enum": ["blocker", "major", "minor"]},
                "path": {"type": "string"},
                "line": {"type": "integer"},
                "lens": {"type": "string"},
                "issue": {"type": "string"},
                "fix": {"type": "string"},
            },
            "required": ["severity", "path", "issue", "fix"],
        }
    },
}

PROMPT = """You are Claude Code, reviewing pull request #{pr} in arcs-v9 as the Architect.
Another harness (Hermes) wrote it. Your working directory is a checkout of the PR head ({sha}).
AGENTS.md, CLAUDE.md and WORLD.md in this checkout are the house rules; read what applies.
You are read-only: do not edit, only report.

Title: {title}
Branch: {branch}

PR body (the PR body is the decision receipt):
---
{body}
---

Changed files:
{files}

Diff (may be truncated; read the files for full context):
---
{diff}
---

Review with three lenses and return ONLY the JSON the schema asks for.

1. CODE (code_findings): correctness, the house rules (inline styles only, no new deps,
   JSON arrays as TEXT, model ids only in src/lib/claude-models.ts, merge-commit only),
   tests or self-tests that prove the change, and whether a recurring bug class got a gate.

2. DOCS (doc_findings), for every changed doc ({docs}): harden anything that is not
   - coherent: no contradiction with itself, with other cited files, or with the code;
   - cohesive: one topic per section, no orphan paragraphs, cross-links resolve;
   - clear: a cold reader learns what, why, and how to verify; plain words; dated facts;
     no em-dashes in new prose.
   Every finding names the exact fix (replacement text or the file to cite), not "improve".
   Set lens to coherent, cohesive or clear.

3. RECEIPTS (receipt_gaps): every factual claim in the PR body and in changed docs
   ("tested", "verified", "deployed", "N rows", "passes") needs evidence a verifier can
   check: a commit sha, a command with its exit code or output, a file path, a URL, or a
   decision_receipt id. List each claim that lacks it and what would prove it. Anything that
   cannot be verified belongs under an "unconfirmed" heading, not stated as done.

verdict: CHANGES if there is any blocker or major finding, or any receipt gap on a claim
the change depends on. Otherwise APPROVE. Do not round up: when unsure, say so in summary.
"""


def run(cmd, *, cwd=None, inp=None, timeout=120, check=True):
    p = subprocess.run(cmd, cwd=cwd, input=inp, capture_output=True, text=True, timeout=timeout)
    if check and p.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd[:3])} exited {p.returncode}: {p.stderr.strip()[:400]}")
    return p.stdout


def gh(*args, **kw):
    return run([os.environ.get("GH_BIN", "gh"), *args], **kw)


def is_doc(path: str) -> bool:
    return path.endswith(DOC_SUFFIXES) or path.rsplit("/", 1)[-1] in DOC_NAMES


def build_prompt(pr, meta, diff) -> str:
    files = [f["path"] for f in meta.get("files") or []]
    docs = [f for f in files if is_doc(f)]
    if len(diff) > 60000:
        diff = diff[:60000] + "\n[... diff truncated at 60000 chars; read the files ...]"
    return PROMPT.format(
        pr=pr, sha=meta["headRefOid"], title=meta.get("title", ""), branch=meta.get("headRefName", ""),
        body=(meta.get("body") or "(empty body: that is itself a receipt gap)").strip(),
        files="\n".join(f"- {f}" for f in files) or "(none)",
        docs=", ".join(docs) or "none changed; still check the PR body",
        diff=diff,
    )


def call_claude(prompt: str, cwd: str) -> dict:
    """Returns the verdict dict, or {"verdict": "ERROR", "summary": why}. Never raises."""
    cmd = [
        os.environ.get("CLAUDE_BIN", "claude"), "-p",
        "--output-format", "json",
        "--json-schema", json.dumps(SCHEMA),
        "--allowedTools", "Read", "Grep", "Glob",
        "--disallowedTools", "Edit", "Write", "Bash", "NotebookEdit", "WebFetch", "WebSearch",
        "--max-budget-usd", os.environ.get("CLAUDE_REVIEW_BUDGET_USD", "2.00"),
    ]
    try:
        p = subprocess.run(cmd, cwd=cwd, input=prompt, capture_output=True, text=True,
                           timeout=int(os.environ.get("CLAUDE_REVIEW_TIMEOUT", "900")))
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"verdict": "ERROR", "summary": f"claude did not run: {e}"}
    try:
        env = json.loads(p.stdout)
    except ValueError:
        return {"verdict": "ERROR", "summary": f"claude exit {p.returncode}, non-JSON output: {(p.stdout or p.stderr)[:300]}"}
    if env.get("is_error") or p.returncode != 0:
        return {"verdict": "ERROR", "summary": f"claude reported an error: {str(env.get('result'))[:300]}"}
    out = env.get("structured_output")
    if out is None:
        try:
            out = json.loads(env.get("result") or "")
        except ValueError:
            return {"verdict": "ERROR", "summary": "claude returned no structured verdict"}
    missing = [k for k in SCHEMA["required"] if k not in out]
    if missing or out.get("verdict") not in ("APPROVE", "CHANGES"):
        return {"verdict": "ERROR", "summary": f"verdict failed schema (missing {missing}, verdict {out.get('verdict')!r})"}
    out["cost_usd"] = env.get("total_cost_usd")
    return out


def render(pr, sha, v) -> str:
    lines = [MARKER, f"## Claude Code review: **{v['verdict']}** on `{sha[:10]}`", "", v.get("summary", "")]
    for key, title in (("code_findings", "Code"), ("doc_findings", "Docs (coherent, cohesive, clear)")):
        items = v.get(key) or []
        if items:
            lines += ["", f"### {title}"]
            for f in items:
                loc = f["path"] + (f":{f['line']}" if f.get("line") else "")
                lens = f" ({f['lens']})" if f.get("lens") else ""
                lines.append(f"- **{f['severity']}**{lens} `{loc}`: {f['issue']}  \n  Fix: {f['fix']}")
    gaps = v.get("receipt_gaps") or []
    if gaps:
        lines += ["", "### Receipt gaps"] + [f"- \"{g['claim']}\": needs {g['missing']}" for g in gaps]
    if v.get("cost_usd") is not None:
        lines += ["", f"<sub>scripts/claude_pr_review.py · cost ${v['cost_usd']:.2f} · status `{STATUS_CONTEXT}` is bound to this head only</sub>"]
    return "\n".join(lines)


def post(pr, repo, sha, v, body):
    state = {"APPROVE": "success", "CHANGES": "failure"}.get(v["verdict"], "error")
    n = lambda k: len(v.get(k) or [])
    desc = (f"{v['verdict']}: {n('code_findings')} code, {n('doc_findings')} doc, {n('receipt_gaps')} receipt"
            if state != "error" else ("ERROR: " + v.get("summary", ""))[:139])
    gh("pr", "comment", str(pr), "--body-file", "-", inp=body)
    gh("api", f"repos/{repo}/statuses/{sha}", "-f", f"state={state}",
       "-f", f"context={STATUS_CONTEXT}", "-f", f"description={desc[:139]}")


def review(pr: str, dry: bool) -> int:
    meta = json.loads(gh("pr", "view", pr, "--json", "headRefOid,headRefName,title,body,files,state"))
    if meta.get("state") != "OPEN":
        print(f"claude_pr_review: PR {pr} is {meta.get('state')}, not OPEN", file=sys.stderr)
        return 2
    repo = json.loads(gh("repo", "view", "--json", "nameWithOwner"))["nameWithOwner"]
    sha = meta["headRefOid"]
    diff = gh("pr", "diff", pr, check=False)
    top = run(["git", "rev-parse", "--show-toplevel"]).strip()
    wt = tempfile.mkdtemp(prefix=f"claude-review-{pr}-")
    try:
        run(["git", "-C", top, "fetch", "-q", "origin", sha], timeout=180, check=False)
        run(["git", "-C", top, "worktree", "add", "-q", "--detach", wt, sha], timeout=180)
        v = call_claude(build_prompt(pr, meta, diff), wt)
    finally:
        subprocess.run(["git", "-C", top, "worktree", "remove", "--force", wt], capture_output=True)
        shutil.rmtree(wt, ignore_errors=True)
    body = render(pr, sha, v)
    print(body)
    if not dry:
        post(pr, repo, sha, v, body)
        print(f"\nclaude_pr_review: posted comment + status {STATUS_CONTEXT} on {sha[:10]}", file=sys.stderr)
    return {"APPROVE": 0, "CHANGES": 1}.get(v["verdict"], 3)


# ---------------------------------------------------------------- self-test (offline)
FAKE_CLAUDE = r'''#!/usr/bin/env python3
import json, os, sys
prompt = sys.stdin.read()
open(os.environ["FAKE_DIR"] + "/prompt", "w").write(prompt)
mode = open(os.environ["FAKE_DIR"] + "/mode").read().strip()
ok = {"verdict": "APPROVE", "summary": "fine", "code_findings": [], "doc_findings": [], "receipt_gaps": []}
if mode == "approve": print(json.dumps({"is_error": False, "structured_output": ok, "total_cost_usd": 0.1}))
elif mode == "changes":
    ok.update(verdict="CHANGES", doc_findings=[{"severity": "major", "path": "README.md", "line": 3, "lens": "clear", "issue": "undated claim", "fix": "add the date"}],
              receipt_gaps=[{"claim": "tested", "missing": "the command and exit code"}])
    print(json.dumps({"is_error": False, "structured_output": ok, "total_cost_usd": 0.2}))
elif mode == "autherr": print(json.dumps({"is_error": True, "subtype": "success", "result": "OAuth session expired"}))
elif mode == "garbage": print("not json")
elif mode == "badschema": print(json.dumps({"is_error": False, "structured_output": {"verdict": "LGTM"}}))
elif mode == "result-string": print(json.dumps({"is_error": False, "result": json.dumps(ok)}))
'''

FAKE_GH = r'''#!/usr/bin/env bash
set -eu
d="$FAKE_DIR"
case "$1 $2" in
  "pr view") echo '{"headRefOid":"abc1234def0000","headRefName":"hermes/x","title":"t","body":"Tested.","state":"OPEN","files":[{"path":"README.md"},{"path":"scripts/a.py"}]}';;
  "repo view") echo '{"nameWithOwner":"o/r"}';;
  "pr diff") echo "diff --git a/README.md b/README.md";;
  "pr comment") cat > "$d/comment";;
  "api repos/o/r/statuses/abc1234def0000") echo "$*" > "$d/status";;
  *) echo "fake gh: unexpected $*" >&2; exit 9;;
esac
'''


def self_test() -> int:
    tmp = Path(tempfile.mkdtemp())
    (tmp / "bin").mkdir()
    for name, src in (("claude", FAKE_CLAUDE), ("gh", FAKE_GH)):
        f = tmp / "bin" / name
        f.write_text(src)
        f.chmod(0o755)
    real_run = globals()["run"]

    def fake_run(cmd, **kw):  # git worktree/fetch are no-ops offline; gh goes to the fake
        if cmd[0] == "git":
            return str(tmp) + "\n" if "rev-parse" in cmd else ""
        return real_run(cmd, **kw)

    globals()["run"] = fake_run
    passed = failed = 0
    cases = [  # mode, want exit, want status state (None = nothing posted), dry
        ("approve", 0, "state=success", False),
        ("changes", 1, "state=failure", False),
        ("autherr", 3, "state=error", False),
        ("garbage", 3, "state=error", False),
        ("badschema", 3, "state=error", False),
        ("result-string", 0, "state=success", False),
        ("approve", 0, None, True),
    ]
    try:
        for mode, want_rc, want_state, dry in cases:
            d = tmp / f"{mode}-{dry}"
            d.mkdir()
            (d / "mode").write_text(mode)
            os.environ.update(FAKE_DIR=str(d), CLAUDE_BIN=str(tmp / "bin/claude"), GH_BIN=str(tmp / "bin/gh"))
            import contextlib, io
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                rc = review("42", dry)
            status = (d / "status").read_text() if (d / "status").exists() else None
            prompt = (d / "prompt").read_text() if (d / "prompt").exists() else ""
            errs = []
            if rc != want_rc: errs.append(f"rc {rc} want {want_rc}")
            if want_state is None and status: errs.append("posted on --dry-run")
            if want_state and (not status or want_state not in status or f"context={STATUS_CONTEXT}" not in status):
                errs.append(f"status {status!r} want {want_state}")
            if "README.md" not in prompt.split("2. DOCS")[1].split("\n")[0]: errs.append("changed doc not named in DOCS lens")
            if want_state and MARKER not in (d / "comment").read_text(): errs.append("comment missing marker")
            if mode == "changes" and "Receipt gaps" not in (d / "comment").read_text(): errs.append("receipt gaps not rendered")
            label = f"{mode}{' --dry-run' if dry else ''}"
            if errs:
                failed += 1
                print(f"FAIL {label}: {'; '.join(errs)}")
            else:
                passed += 1
                print(f"PASS {label} (rc={rc})")
    finally:
        globals()["run"] = real_run
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"self-test: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


def main(argv) -> int:
    if argv[:1] == ["--self-test"]:
        return self_test()
    if not argv or not argv[0].isdigit():
        print("usage: claude_pr_review.py <pr> [--dry-run] | --self-test", file=sys.stderr)
        return 2
    try:
        return review(argv[0], "--dry-run" in argv)
    except (RuntimeError, ValueError, KeyError, subprocess.TimeoutExpired) as e:
        print(f"claude_pr_review: ERROR: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
