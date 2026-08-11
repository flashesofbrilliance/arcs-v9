#!/usr/bin/env python3
"""
deploy_lab.py — the ORCHESTRATION step of the lab factory.

Deploys every surface under _ARTIFACTS/lab/ to the isolated Vercel project
'arcs-experiments' (serves lab.arcs.care) via the REST API, then writes a
serializable state record to _ARTIFACTS/lab/STATE.json.

Why REST, not `vercel deploy`: the CLI (54.x) injects a deprecated
`experimentalServices` field that fails new-project deploys. REST is the
reliable path and never touches the protected arcs-v9 / arcs.care projects.

Isolation invariant (do NOT change): PID below is 'arcs-experiments'. Never
point this at prj_aKmLj1UvT2oaDSH4KIAqEPaULqx9 (arcs-v9) or the arcs.care project.

Usage:
    python3 .claude/skills/lab-mint/deploy_lab.py            # deploy + update STATE.json
    python3 .claude/skills/lab-mint/deploy_lab.py --dry-run  # list what would deploy
"""
import json, os, sys, hashlib, urllib.request, subprocess

TEAM = "team_narCbxUgS4eiieJKRv1QMfff"          # arcs-care team
PID  = "prj_2hKOq2uqRXualTM4zsbbOXHpuAXm"        # arcs-experiments  (ISOLATED — do not change)
DOMAIN = "lab.arcs.care"
ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "_ARTIFACTS", "lab")
ROOT = os.path.abspath(ROOT)
STATE = os.path.join(ROOT, "STATE.json")

def token():
    p = os.path.expanduser("~/Library/Application Support/com.vercel.cli/auth.json")
    return json.load(open(p))["token"]

def surfaces():
    out = []
    for dirpath, _, files in os.walk(ROOT):
        for f in files:
            if f.endswith(".html"):
                full = os.path.join(dirpath, f)
                rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
                out.append((rel, full))
    return sorted(out)

def git_head():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT).decode().strip()
    except Exception:
        return None

def main():
    dry = "--dry-run" in sys.argv
    files_on_disk = surfaces()
    if not files_on_disk:
        print("no *.html under", ROOT); sys.exit(1)
    print("Surfaces (%d):" % len(files_on_disk))
    for rel, _ in files_on_disk:
        route = "/" if rel == "index.html" else "/" + rel[:-len("index.html")]
        print("  %-32s https://%s%s" % (rel, DOMAIN, route))
    if dry:
        return

    tok = token()
    payload = []
    for rel, full in files_on_disk:
        raw = open(full, "rb").read()
        sha = hashlib.sha1(raw).hexdigest()
        up = urllib.request.Request(
            "https://api.vercel.com/v2/files?teamId=%s" % TEAM, data=raw, method="POST",
            headers={"Authorization": "Bearer %s" % tok, "Content-Type": "application/octet-stream",
                     "x-vercel-digest": sha, "x-now-size": str(len(raw))})
        urllib.request.urlopen(up)
        payload.append({"file": rel, "sha": sha, "size": len(raw)})

    body = {"name": "arcs-experiments", "project": PID, "target": "production", "files": payload,
            "projectSettings": {"framework": None, "buildCommand": None, "outputDirectory": None, "installCommand": None}}
    req = urllib.request.Request("https://api.vercel.com/v13/deployments?teamId=%s" % TEAM,
        data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": "Bearer %s" % tok, "Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req))
    print("DEPLOY", d.get("readyState"), d.get("id"))

    state = {
        "project": "arcs-experiments", "domain": DOMAIN, "source": "_ARTIFACTS/lab/",
        "git_head": git_head(),
        "deploy_id": d.get("id"), "deploy_url": d.get("url"), "ready": d.get("readyState"),
        "surfaces": [{"route": ("/" if r == "index.html" else "/" + r[:-len("index.html")]),
                      "file": r, "sha": next(p["sha"] for p in payload if p["file"] == r)}
                     for r, _ in files_on_disk],
    }
    json.dump(state, open(STATE, "w"), indent=2)
    print("state →", STATE)
    print("live  → https://%s/" % DOMAIN)

if __name__ == "__main__":
    main()
