#!/usr/bin/env python3
"""jobs_prose_gate: Job Factory slice 7. The NFTT prose factory's gate chain, run on
an application draft (cover letter or answers) before it is shown as ready to send.

Order matters: truth before polish. A draft is READY only if every hard gate passes;
otherwise HELD with the reasons. The system never sends; READY means "Zach may send".

  1. provenance  scripts/provenance_lint.py against the bundle's evidence ledger.
                 STRICT here: no ledger = HELD (its metrics are unchecked), unlike the
                 page-rollout default where an unenrolled file passes with a note.
  2. slop lint   scripts/slop_lint.py (mechanical: em-dashes, cliches).
  3. slop eval   scripts/slop_eval.py --strict (judgment, needs ANTHROPIC_API_KEY;
                 with no key it is recorded SKIPPED, never silently passed as checked).
  4. honest      tools/arcs-verb-eval recapitulation (ADR-068): draft marker, ex-ante
                 receipt, pre-send gauntlet. A missing gauntlet HOLDS unless Zach waives
                 it with --waive-gauntlet "<reason>", which the print records as SKIPPED.

Writes <draft>.gate.json beside the draft. Exit 0 = READY, 1 = HELD, 2 = usage.

  python3 scripts/jobs_prose_gate.py --bundle _ARTIFACTS/forge-x --draft _ARTIFACTS/forge-x/cover-x.md
  python3 scripts/jobs_prose_gate.py ... --ledger path/evidence.jsonl --gauntlet path.json
  python3 scripts/jobs_prose_gate.py ... --waive-gauntlet "cold application, no counterpart yet"
  python3 scripts/jobs_prose_gate.py --self-test
"""
import argparse, json, os, re, subprocess, sys, tempfile
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PY = sys.executable


def run(cmd, env=None):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env=env)
    return p.returncode, (p.stdout + p.stderr).strip()


def find_ledger(bundle, explicit):
    for cand in [explicit, os.path.join(bundle, "evidence.jsonl"), os.environ.get("ARCS_EVIDENCE_LEDGER")]:
        if cand and os.path.isfile(cand):
            return cand
    return None


def gate(bundle, draft, ledger=None, gauntlet=None, waive=None, judge=True):
    out = {"draft": os.path.relpath(draft, ROOT), "at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "gates": []}
    add = lambda gid, status, detail: out["gates"].append({"id": gid, "status": status, "detail": detail[-600:]})

    led = find_ledger(bundle, ledger)
    if not led:
        rc, txt = run([PY, "scripts/provenance_lint.py", draft])
        add("provenance", "HELD", "no evidence ledger for this bundle, so its metrics are unchecked: " + txt)
    else:
        rc, txt = run([PY, "scripts/provenance_lint.py", "--ledger", led, draft])
        add("provenance", "PASS" if rc == 0 else "HELD", txt)

    rc, txt = run([PY, "scripts/slop_lint.py", draft])
    add("slop-lint", "PASS" if rc == 0 else "HELD", txt)

    if judge and os.environ.get("ANTHROPIC_API_KEY"):
        rc, txt = run([PY, "scripts/slop_eval.py", "--strict", draft])
        add("slop-eval", "PASS" if rc == 0 else "HELD", txt)
    else:
        add("slop-eval", "SKIPPED", "judgment tier not run (no ANTHROPIC_API_KEY or --no-judge); not counted as checked")

    # honest: a front-matter copy so the draft file itself stays paste-ready.
    ex_ante = os.path.join(bundle, "ex-ante.json")
    fm = f"status: DRAFT\nex_ante: {os.path.abspath(ex_ante) if os.path.isfile(ex_ante) else 'missing'}\ngauntlet: {os.path.abspath(gauntlet) if gauntlet and os.path.isfile(gauntlet) else 'missing'}\n\n"
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as t:
        t.write(fm + open(draft, encoding="utf-8").read())
        tmp = t.name
    cmd = [PY, "tools/arcs-verb-eval/arcs_verb_eval.py", "recapitulation", tmp, "--json", "--no-slop"]
    if waive:
        cmd[3:3] = ["--skip-gate", "pre-send-gauntlet"]
    rc, txt = run(cmd)
    os.unlink(tmp)
    try:
        rep = json.loads(txt[txt.index("{"):])
        failed = [g["id"] for g in rep.get("gates", []) if g.get("status") in ("FAIL", False) or g.get("ok") is False]
        fate = rep.get("fate", "")
    except (ValueError, KeyError):
        failed, fate = ["unparseable"], ""
    if waive:
        add("pre-send-gauntlet-waiver", "WAIVED", waive)
    add("honest", "PASS" if rc == 0 else "HELD", f"fate {fate or '?'}; failed: {', '.join(failed) or 'none'}")

    held = [g["id"] for g in out["gates"] if g["status"] == "HELD"]
    out["verdict"] = "HELD" if held else "READY"
    out["held_by"] = held
    out["unchecked"] = [g["id"] for g in out["gates"] if g["status"] == "SKIPPED"]
    with open(os.path.splitext(draft)[0] + ".gate.json", "w") as f:
        json.dump(out, f, indent=2)
    return out


def self_test():
    d = tempfile.mkdtemp()
    good = os.path.join(d, "cover-good.md")
    open(good, "w").write("Dear team,\n\nI led a platform that cut review time by 40%. I would like to talk.\n\nZach Harris\n")
    open(os.path.join(d, "evidence.jsonl"), "w").write(json.dumps({"pattern": "40%", "source": "self-reported:test"}) + "\n")
    open(os.path.join(d, "ex-ante.json"), "w").write("{}")
    g = os.path.join(d, "gauntlet.json"); open(g, "w").write("{}")
    ok = gate(d, good, gauntlet=g, judge=False)
    bad = os.path.join(d, "cover-bad.md")
    open(bad, "w").write("Dear team,\n\nI grew revenue 300% — a game-changer.\n\nZach Harris\n")
    no = gate(d, bad, gauntlet=g, judge=False)
    nogauntlet = gate(d, good, judge=False)
    waived = gate(d, good, judge=False, waive="self-test waiver")
    checks = [
        ("good draft is READY", ok["verdict"] == "READY"),
        ("uncovered metric + em-dash is HELD", no["verdict"] == "HELD" and {"provenance", "slop-lint"} <= set(no["held_by"])),
        ("missing gauntlet HOLDS", nogauntlet["verdict"] == "HELD" and "honest" in nogauntlet["held_by"]),
        ("waiver is recorded and lets it pass", waived["verdict"] == "READY" and any(x["id"] == "pre-send-gauntlet-waiver" for x in waived["gates"])),
        ("judgment never counted as checked when skipped", "slop-eval" in ok["unchecked"]),
    ]
    for name, passed in checks:
        print(("ok   " if passed else "FAIL ") + name)
    return 0 if all(p for _, p in checks) else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--bundle"); ap.add_argument("--draft"); ap.add_argument("--ledger")
    ap.add_argument("--gauntlet"); ap.add_argument("--waive-gauntlet", dest="waive")
    ap.add_argument("--no-judge", action="store_true"); ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        sys.exit(self_test())
    if not (a.bundle and a.draft):
        ap.error("--bundle and --draft are required")
    r = gate(a.bundle, a.draft, a.ledger, a.gauntlet, a.waive, judge=not a.no_judge)
    print(f"{r['verdict']}  {r['draft']}" + (f"  held by: {', '.join(r['held_by'])}" if r["held_by"] else "") + (f"  unchecked: {', '.join(r['unchecked'])}" if r["unchecked"] else ""))
    sys.exit(0 if r["verdict"] == "READY" else 1)
