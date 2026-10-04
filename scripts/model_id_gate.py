#!/usr/bin/env python3
"""model_id_gate: block hardcoded Claude model ids outside runtime/specs/models.json.

Callers name a role (src/lib/models.ts, scripts/arcs_models.py); only the registry names an id,
so a model upgrade is a one-line, reviewable change instead of a hunt across ~30 call sites.

    python3 scripts/model_id_gate.py            # scan tracked code in src/ scripts/ operators/
    python3 scripts/model_id_gate.py --staged   # scan staged files only (pre-commit)
    python3 scripts/model_id_gate.py --self-test
Exit 1 on any hit. A line may opt out with the marker `model-id-ok` (e.g. a doc example).
"""
import re, subprocess, sys

ID = re.compile(r"claude-(?:haiku|sonnet|opus|fable)-\d[\w.-]*")
SCOPE = ("src/", "scripts/", "operators/")
EXT = (".ts", ".tsx", ".js", ".mjs", ".py", ".sh")
ALLOW = {"runtime/specs/models.json", "scripts/model_id_gate.py", "scripts/model_drift_check.py"}


def hits(path, text):
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        if "model-id-ok" in line:
            continue
        for m in ID.finditer(line):
            out.append(f"{path}:{n}: {m.group(0)}")
    return out


def files(staged):
    cmd = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"] if staged else ["git", "ls-files"]
    names = subprocess.run(cmd, capture_output=True, text=True).stdout.split()
    return [f for f in names if f.startswith(SCOPE) and f.endswith(EXT) and f not in ALLOW and "node_modules" not in f]


def read(path, staged):
    if staged:
        return subprocess.run(["git", "show", f":{path}"], capture_output=True, text=True).stdout
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def self_test():
    cases = [('model: "claude-sonnet-4-6"', 1), ('model: model("deep")', 0), ('source="claude-fable"', 0),
             ('"claude-opus-4-7" # model-id-ok', 0), ("claude-haiku-4-5-20251001", 1), ("claude-plugin", 0)]
    ok = all(len(hits("t", s)) == want for s, want in cases)
    print(f"model_id_gate self-test: {'PASS' if ok else 'FAIL'} ({len(cases)} cases)")
    return 0 if ok else 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    unknown = [a for a in argv if a not in ("--staged",)]
    if unknown:
        print(f"model_id_gate: unknown argument(s): {' '.join(unknown)}", file=sys.stderr)
        return 2
    staged = "--staged" in argv
    found = [h for f in files(staged) for h in hits(f, read(f, staged))]
    if found:
        print("✖ model_id_gate: hardcoded Claude model id(s). Use model(\"<role>\") from src/lib/models.ts or scripts/arcs_models.py; ids live only in runtime/specs/models.json:", file=sys.stderr)
        print("\n".join("  " + h for h in found), file=sys.stderr)
        return 1
    print("model_id_gate: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
