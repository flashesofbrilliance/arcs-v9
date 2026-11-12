#!/usr/bin/env python3
"""agent_seed_gate: merge rule for candidate seed agents (stdlib only).

Seed agents (idea-*, chief-*, scenario-*, prospect-*) live in .claude/agents/ and are tested in practice.
runtime/specs/agent-seed-ledger.jsonl holds, per agent: a pre-registered belief, a kill_line, and a
log of real uses. The merge rule is the result of that falsifiability test:
  CANDIDATE  description starts "[CANDIDATE]"; needs belief, kill_line, prior; uses may be empty.
  SURVIVED   needs >= 3 uses, each with ref and verdict (helpful|not_helpful); fewer than 2 not_helpful;
             description must NOT start "[CANDIDATE]".
  KILLED     the spec file must be absent (delete it; the ledger row stays as the record).
A CANDIDATE with 2 or more not_helpful uses is a kill and must be marked KILLED.

  python3 scripts/agent_seed_gate.py --check
  python3 scripts/agent_seed_gate.py --self-test
"""
import json, os, re, sys, tempfile

SEED = re.compile(r"^(idea|chief|scenario|prospect)-")

def _frontmatter_desc(path):
    txt = open(path, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---", txt, re.S)
    d = re.search(r'^description:\s*"?(.*?)"?\s*$', m.group(1), re.M) if m else None
    return (d.group(1) if d else ""), "—" in txt

def check(root="."):
    errs = []
    led_path = os.path.join(root, "runtime/specs/agent-seed-ledger.jsonl")
    rows = {}
    if os.path.exists(led_path):
        for i, ln in enumerate(open(led_path, encoding="utf-8"), 1):
            if ln.strip():
                try: r = json.loads(ln); rows[r["name"]] = r
                except Exception as e: errs.append(f"ledger line {i}: bad JSON ({e})")
    adir = os.path.join(root, ".claude/agents")
    files = {f[:-3] for f in os.listdir(adir) if f.endswith(".md") and SEED.match(f)} if os.path.isdir(adir) else set()
    for n in sorted(files - set(rows)): errs.append(f"{n}: seed agent file has no ledger row")
    for n, r in sorted(rows.items()):
        for k in ("belief", "kill_line"):
            if not str(r.get(k, "")).strip(): errs.append(f"{n}: ledger missing {k}")
        if not isinstance(r.get("prior"), (int, float)): errs.append(f"{n}: ledger missing numeric prior")
        st, uses = r.get("status"), r.get("uses", [])
        bad = [u for u in uses if u.get("verdict") not in ("helpful", "not_helpful") or not str(u.get("ref", "")).strip()]
        if bad: errs.append(f"{n}: {len(bad)} use(s) lack ref or a valid verdict")
        nh = sum(1 for u in uses if u.get("verdict") == "not_helpful")
        exists = n in files
        if st == "KILLED":
            if exists: errs.append(f"{n}: KILLED but spec file still present; delete it")
            continue
        if st not in ("CANDIDATE", "SURVIVED"): errs.append(f"{n}: status must be CANDIDATE, SURVIVED or KILLED"); continue
        if nh >= 2: errs.append(f"{n}: {nh} not_helpful uses trips the kill line; mark KILLED and delete the spec")
        if not exists: errs.append(f"{n}: ledger row is {st} but spec file is missing"); continue
        desc, emdash = _frontmatter_desc(os.path.join(adir, n + ".md"))
        if emdash: errs.append(f"{n}: spec contains an em-dash")
        cand = desc.startswith("[CANDIDATE]")
        if st == "CANDIDATE" and not cand: errs.append(f"{n}: CANDIDATE but description lacks [CANDIDATE]")
        if st == "SURVIVED":
            if cand: errs.append(f"{n}: SURVIVED but description still says [CANDIDATE]")
            if len(uses) < 3: errs.append(f"{n}: SURVIVED needs >= 3 recorded uses, has {len(uses)}")
    return errs

def _plant(root, rows, files):
    os.makedirs(os.path.join(root, ".claude/agents")); os.makedirs(os.path.join(root, "runtime/specs"))
    open(os.path.join(root, "runtime/specs/agent-seed-ledger.jsonl"), "w").write("\n".join(json.dumps(r) for r in rows) + "\n")
    for n, desc in files.items():
        open(os.path.join(root, f".claude/agents/{n}.md"), "w").write(f'---\nname: {n}\ndescription: "{desc}"\ntools: Read\n---\nbody\n')

def self_test():
    base = {"prior": 0.6, "belief": "b", "kill_line": "k"}
    use = lambda v: {"ref": "r", "verdict": v}
    cases = [  # (label, rows, files, expect_fail)
        ("good candidate", [dict(base, name="idea-x", status="CANDIDATE", uses=[])], {"idea-x": "[CANDIDATE] d"}, False),
        ("good survivor", [dict(base, name="idea-x", status="SURVIVED", uses=[use("helpful")] * 3)], {"idea-x": "d"}, False),
        ("killed and deleted", [dict(base, name="idea-x", status="KILLED", uses=[use("not_helpful")] * 2)], {}, False),
        ("no ledger row", [], {"chief-y": "[CANDIDATE] d"}, True),
        ("no kill line", [dict(base, name="idea-x", status="CANDIDATE", kill_line="", uses=[])], {"idea-x": "[CANDIDATE] d"}, True),
        ("survivor under-tested", [dict(base, name="idea-x", status="SURVIVED", uses=[use("helpful")])], {"idea-x": "d"}, True),
        ("tripped kill still candidate", [dict(base, name="idea-x", status="CANDIDATE", uses=[use("not_helpful")] * 2)], {"idea-x": "[CANDIDATE] d"}, True),
        ("killed but file present", [dict(base, name="idea-x", status="KILLED", uses=[])], {"idea-x": "d"}, True),
        ("survivor keeps candidate tag", [dict(base, name="idea-x", status="SURVIVED", uses=[use("helpful")] * 3)], {"idea-x": "[CANDIDATE] d"}, True),
    ]
    ok = True
    for label, rows, files, expect_fail in cases:
        with tempfile.TemporaryDirectory() as d:
            _plant(d, rows, files); failed = bool(check(d))
        good = failed == expect_fail; ok &= good
        print(f"{'PASS' if good else 'FAIL'}  {label}  (gate {'blocked' if failed else 'passed'})")
    return ok

if __name__ == "__main__":
    if "--self-test" in sys.argv: sys.exit(0 if self_test() else 1)
    errs = check()
    for e in errs: print("FAIL", e)
    print("agent_seed_gate:", "BLOCKED" if errs else "OK")
    sys.exit(1 if errs else 0)
