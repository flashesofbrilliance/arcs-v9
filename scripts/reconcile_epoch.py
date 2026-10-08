#!/usr/bin/env python3
"""reconcile_epoch: run the existing drift, stale and debt detectors once, classify every finding, rank them.

Slice 1 of the weekly reconciliation epoch. It READS ONLY: it runs detectors that already exist,
parses their one-line summaries, and writes one ranked report. It fixes nothing, files nothing on
GitHub, and moves nothing. The detectors write receipts under _INBOX/ by design; this script puts
those files back the way it found them (it will not touch a receipt file you had already edited).

Every finding gets a CLASS (stale, drift, tech debt, design debt, architecture debt), a ROUTE
(mechanical: a cheap-model batch could fix it; judgment: a human rules; prune: salvage-check first)
and a DEFAULT answer, so the judgment items can be cleared with "approve defaults".

A detector that crashes, times out or prints something this script cannot parse is reported as
UNPARSED. It is never counted as zero findings.

  python3 scripts/reconcile_epoch.py                       # report to stdout
  python3 scripts/reconcile_epoch.py --out _STATE/reconcile # also write <date>.md and <date>.json
  python3 scripts/reconcile_epoch.py --rows DIR            # also write proposed tracker rows, one JSON
                                                           # per finding, for `backlog_issue_sync.py debt push --rows DIR`
  python3 scripts/reconcile_epoch.py --self-test

Stdlib only.
"""
import argparse, datetime as dt, glob, json, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CLASS_ORDER = ["drift", "stale", "architecture debt", "design debt", "tech debt"]
SEV_RANK = {"P1": 0, "P2": 1, "P3": 2}
GATE_GLOBS = ("_DECISIONS/", "_MEMORY/", "_SPECS/", "_CANON/", "_STATE/", "_SEEDS/", "_PATTERNS/")
ROOT_RECORDS = ("CLAUDE.md", "AGENTS.md", "WORLD.md", "MEMORY.md", "SKILL.md")


def num(rx, text, group=1, default=None, flags=0):
    m = re.search(rx, text, flags)
    return int(m.group(group)) if m else default


def finding(det, cls, sev, count, summary, route, default, sample="", cmd=""):
    return {"detector": det, "class": cls, "severity": sev, "count": count, "summary": summary,
            "route": route, "default": default, "sample": sample[:300], "cmd": cmd}


def unparsed(det, cls, why, cmd):
    return finding(det, cls, "P2", None, f"UNPARSED: {why}. Not counted as zero.", "judgment",
                   "Run the detector by hand and fix the parser or the detector.", "", cmd)


# ---- parsers: (output, returncode) -> finding or None when clean ------------------------------
def p_lattice(out, rc, cmd):
    n = num(r"(\d+) drifted claim", out)
    if n is None:
        return unparsed("lattice-drift", "drift", "no 'N drifted claim(s)' line", cmd)
    if n == 0:
        return None
    return finding("lattice-drift", "drift", "P3", n, f"{n} drifted claim(s) in the knowledge lattice.",
                   "mechanical", "Run `python3 scripts/lattice_drift_check.py --regenerate` for countables; epoch text is human-owned.", out, cmd)


def p_seedbank(out, rc, cmd):
    n = num(r"(\d+) finding", out)
    if n is None:
        return unparsed("seedbank-drift", "drift", "no 'N finding(s)' line", cmd)
    if n == 0:
        return None
    paths = len(re.findall(r"\[broken-local-path\]", out))
    orphans = len(re.findall(r"\[orphan-seed\]", out))
    return finding("seedbank-drift", "drift", "P3", n, f"{n} seedbank finding(s): {paths} broken local path(s), {orphans} orphan seed(s) shown; curation is human-owned.",
                   "judgment", "Re-catalog by hand; broken paths whose targets were archived can be repointed in one batch.", out, cmd)


def p_canon(out, rc, cmd):
    n = num(r"(\d+) drifted pair", out)
    if n is None:
        return unparsed("canon-propagation", "drift", "no 'N drifted pair(s)' line", cmd)
    if n == 0:
        return None
    mech = num(r"(\d+) mechanical", out, default=0)
    jud = num(r"(\d+) judgment", out, default=0)
    return finding("canon-propagation", "drift", "P2", n, f"{n} canon pair(s) drifted: {mech} mechanical, {jud} judgment.",
                   "judgment" if jud else "mechanical", "Rule on the judgment pair; apply mechanical ones in a batch.", out, cmd)


def p_ripeness(out, rc, cmd):
    sd = num(r"SECRETLY-DONE (\d+)", out)
    if sd is None:
        return unparsed("backlog-ripeness", "stale", "no 'SECRETLY-DONE N' line", cmd)
    blocked = num(r"BLOCKED (\d+)", out, default=0)
    ripe = num(r"RIPE (\d+)", out, default=0)
    n = sd + blocked
    if n == 0:
        return None
    return finding("backlog-ripeness", "stale", "P3", n,
                   f"{sd} backlog row(s) already done by a merged PR, {blocked} blocked on a dead dependency ({ripe} ripe to start).",
                   "mechanical", "Close the done rows: `python3 scripts/backlog_ripeness.py --apply-closes`; rule on the blocked row.", out, cmd)


def p_orphans(out, rc, cmd):
    unused = num(r"(\d+) unused", out)
    if unused is None:
        return unparsed("tool-orphans", "tech debt", "no 'N unused' line", cmd)
    dup = num(r"(\d+) duplicate", out, default=0)
    broken = num(r"(\d+) broken", out, default=0)
    n = unused + dup + broken
    if n == 0:
        return None
    return finding("tool-orphans", "tech debt", "P3", n, f"{unused} unused, {dup} duplicate, {broken} broken tool(s).",
                   "judgment", "Archive the dead (git mv, history kept); wire or keep the rest. Check callers and tests first.", out, cmd)


def p_registry(out, rc, cmd):
    if re.search(r"registry OK", out):
        return None
    if rc != 0:
        return finding("operator-registry", "architecture debt", "P2", 1, "Operator registry does not match the periodic table.",
                       "mechanical", "Regenerate: `python3 scripts/operator_registry_emit.py`.", out, cmd)
    return unparsed("operator-registry", "architecture debt", "no 'registry OK' and rc 0", cmd)


def p_floor(out, rc, cmd):
    if re.search(r"status floor current", out):
        return None
    if rc != 0:
        return finding("status-floor", "drift", "P3", 1, "The no-JS status page floor is stale or inconsistent.",
                       "mechanical", "Restamp: `python3 scripts/status_floor_emit.py`.", out, cmd)
    return unparsed("status-floor", "drift", "no 'status floor current' and rc 0", cmd)


def p_adrcite(out, rc, cmd):
    n = num(r"(\d+) suspect cite", out)
    if n is None:
        return unparsed("adr-cite-lint", "architecture debt", "no 'N suspect cite(s)' line", cmd)
    if n == 0:
        return None
    return finding("adr-cite-lint", "architecture debt", "P3", n,
                   f"{n} ADR cite(s) whose line shares no words with the ADR (heuristic; many are correct provenance cites).",
                   "judgment", "Review the list as an aid; do not bulk-edit.", out, cmd)


def p_wrap(out, rc, cmd):
    n = num(r"(\d+) wrap-class violation", out)
    if n is None:
        if re.search(r"clean", out) and rc == 0:
            return None
        return unparsed("wrap-lint", "design debt", "no 'N wrap-class violation(s)' line", cmd)
    files = len(set(re.findall(r"✗ wrap-lint: (\S+)", out)))
    return finding("wrap-lint", "design debt", "P2", n, f"{n} wrap-class violation(s) across public/*.html" + (f" ({files} file(s))" if files else "") + ".",
                   "mechanical", "Em-dashes and per-element ch caps: a cheap-model batch can fix them; gate with `artifact_wrap_lint.py` before merging.", out, cmd)


def p_integrity(out, rc, cmd):
    m = re.search(r"integrity_gate: (\d+) file\(s\) against \S+ → (OK|WARN|FAIL)", out)
    if not m:
        return unparsed("integrity-gate", "architecture debt", "no summary line", cmd)
    new_fail = len(re.findall(r"^✖ ", out, re.M))
    base = num(r"(\d+) baselined failure", out, default=0)
    if new_fail == 0 and base == 0:
        return None
    sev = "P1" if new_fail else "P3"
    return finding("integrity-gate", "architecture debt", sev, new_fail + base,
                   f"{new_fail} record(s) with NEW failing cites (these block commits), {base} grandfathered cite(s) in the baseline.",
                   "mechanical" if new_fail else "judgment",
                   "Fix new cites now. Shrink the baseline by qualifying old cites in live records; never grow it.", out, cmd)


def detectors():
    recs = []
    for f in subprocess.run(["git", "-C", ROOT, "ls-files"] + [g.rstrip("/") for g in GATE_GLOBS] + list(ROOT_RECORDS),
                            capture_output=True, text=True).stdout.split("\n"):
        if f and f.endswith((".md", ".json", ".jsonl")):
            recs.append(f)
    wrap_files = sorted(glob.glob(os.path.join(ROOT, "public", "*.html")))
    wrap_files = [os.path.relpath(f, ROOT) for f in wrap_files]
    return [
        ("lattice-drift", ["python3", "scripts/lattice_drift_check.py"], p_lattice),
        ("seedbank-drift", ["python3", "scripts/seedbank_drift_check.py"], p_seedbank),
        ("canon-propagation", ["python3", "scripts/canon_propagation_check.py", "--dry-run"], p_canon),
        ("status-floor", ["python3", "scripts/status_floor_emit.py", "--check"], p_floor),
        ("operator-registry", ["python3", "scripts/operator_registry_emit.py", "--check"], p_registry),
        ("integrity-gate", ["python3", "scripts/integrity_gate.py", "-q"] + recs, p_integrity),
        ("adr-cite-lint", ["python3", "scripts/adr_cite_lint.py"], p_adrcite),
        ("backlog-ripeness", ["python3", "scripts/backlog_ripeness.py"], p_ripeness),
        ("tool-orphans", ["python3", "scripts/tool_orphan_audit.py"], p_orphans),
        ("wrap-lint", ["python3", "scripts/artifact_wrap_lint.py"] + wrap_files, p_wrap),
    ]


def dirty_inbox():
    out = subprocess.run(["git", "-C", ROOT, "status", "--porcelain", "--", "_INBOX"], capture_output=True, text=True).stdout
    return {l[3:] for l in out.split("\n") if l}


def run_all(timeout=150):
    before = dirty_inbox()
    found, ran = [], []
    for det, cmd, parser in detectors():
        label = " ".join(cmd[:3]) + (" ..." if len(cmd) > 3 else "")
        try:
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
            out = r.stdout + r.stderr
            f = parser(out, r.returncode, label)
        except subprocess.TimeoutExpired:
            f = unparsed(det, "drift", f"timed out after {timeout}s", label)
        except Exception as e:  # a crashing parser must still surface
            f = unparsed(det, "drift", f"{type(e).__name__}: {e}", label)
        ran.append(det)
        if f:
            found.append(f)
    after = dirty_inbox()
    restore = sorted(after - before)
    if restore:
        subprocess.run(["git", "-C", ROOT, "checkout", "--"] + restore, capture_output=True)
    return found, ran, restore


def rank(found):
    def key(f):
        cls = CLASS_ORDER.index(f["class"]) if f["class"] in CLASS_ORDER else 9
        return (SEV_RANK.get(f["severity"], 3), cls, -(f["count"] or 0))
    return sorted(found, key=key)


def render(found, ran, today):
    L = [f"# Reconciliation epoch {today}", "",
         f"{len(ran)} detectors run, {len(found)} with findings. Read-only: nothing was fixed, filed or moved.", "",
         "| # | Severity | Class | Detector | Count | Route | Finding |", "|---|---|---|---|---|---|---|"]
    for i, f in enumerate(found, 1):
        L.append(f"| {i} | {f['severity']} | {f['class']} | {f['detector']} | {f['count'] if f['count'] is not None else 'n/a'} | {f['route']} | {f['summary']} |")
    clean = sorted(set(ran) - {f["detector"] for f in found})
    L += ["", "## Defaults (reply 'approve defaults' to act on the judgment rows)", ""]
    for i, f in enumerate(found, 1):
        L.append(f"{i}. **{f['detector']}** ({f['route']}): {f['default']}")
    L += ["", f"Clean: {', '.join(clean) or 'none'}.", "",
          "UNPARSED rows mean a detector crashed, timed out or changed its output; they are not zero findings.", ""]
    return "\n".join(L)


def rows_for(found, today):
    rows = {}
    for f in found:
        doc = "reconcile-" + f["detector"]
        rows[doc] = {"title": f"Reconcile: {f['detector']} ({f['class']})", "severity": f["severity"],
                     "status": "decision" if f["route"] == "judgment" else "open", "owner": "Zach" if f["route"] == "judgment" else "Chip: needed",
                     "filed": today, "detail": f["summary"], "next": f["default"], "ref": "scripts/reconcile_epoch.py"}
    return rows


def self_test():
    cmd = "x"
    assert p_lattice("lattice-drift: fresh · 0 drifted claim(s) · stale 0d", 0, cmd) is None            # clean parses to none
    f = p_lattice("lattice-drift: DRIFT · 2 drifted claim(s)", 0, cmd); assert f and f["count"] == 2
    g = p_lattice("traceback: boom", 1, cmd); assert g and g["summary"].startswith("UNPARSED")         # fail-on-bad: garbage is never zero
    assert p_seedbank("seedbank-drift: DRIFT · 47 finding(s)\n [broken-local-path] a\n [orphan-seed] b", 0, cmd)["count"] == 47
    c = p_canon("canon-propagation: DRIFT · 1 drifted pair(s) · 0 mechanical / 1 judgment", 0, cmd); assert c["route"] == "judgment"
    r = p_ripeness("backlog ripeness: SECRETLY-DONE 7 · RIPE 3 · BLOCKED 1 · WAITING 24", 0, cmd); assert r["count"] == 8
    assert p_registry("registry OK (28 rows)", 0, cmd) is None and p_registry("mismatch", 1, cmd)["class"] == "architecture debt"
    w = p_wrap("✗ wrap-lint: public/a.html x\n✗ 639 wrap-class violation(s). Fixes", 1, cmd); assert w["count"] == 639
    i = p_integrity("✖ _DECISIONS/ADR-1.md  — FAIL\nintegrity_gate: 5 file(s) against origin/main → FAIL\nintegrity_gate: 648 baselined failure(s) reported as WARN", 1, cmd)
    assert i["severity"] == "P1" and i["count"] == 649
    ok = p_integrity("integrity_gate: 5 file(s) against origin/main → OK", 0, cmd); assert ok is None
    ranked = rank([finding("a", "tech debt", "P3", 9, "", "m", ""), finding("b", "drift", "P1", 1, "", "m", "")])
    assert ranked[0]["detector"] == "b"                                                                   # severity first
    assert "reconcile-a" in rows_for(ranked, "2026-10-07")
    print("reconcile_epoch self-test: ok")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--rows")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    today = dt.date.today().isoformat()
    found, ran, restored = run_all()
    found = rank(found)
    md = render(found, ran, today)
    print(md)
    if restored:
        print(f"(restored detector receipts: {', '.join(restored)})", file=sys.stderr)
    if a.out:
        d = os.path.join(ROOT, a.out)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, f"{today}.md"), "w").write(md)
        json.dump({"date": today, "ran": ran, "findings": found}, open(os.path.join(d, f"{today}.json"), "w"), indent=1)
    if a.rows:
        d = os.path.join(ROOT, a.rows)
        os.makedirs(d, exist_ok=True)
        for doc, row in rows_for(found, today).items():
            json.dump(row, open(os.path.join(d, doc + ".json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
