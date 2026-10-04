#!/usr/bin/env python3
"""press_run: stage the weekly go/no-go digest. Schedules the staging, never the publishing.

Spec: runtime/specs/press-run-v0.md. Seed: seed-pipeline-press-run.

Reads draft manifests in _QUEUE/press/<id>.json, re-runs the honest check (slop_lint +
provenance_lint) on each source, applies the freshness ceiling, and stages:
  _STATE/press-run/<date>.md               one-page go/no-go digest (Zach reads, Zach decides)
  _STATE/press-run/<date>.receipts.jsonl   one DRAFT receipt per item (decision field left open)
  _STATE/press-run/<date>.trail.json       candidate rows for the public honesty trail (not published)
  _STATE/press-run/runs.jsonl              one run receipt, appended even when nothing is ready

It never publishes, posts, deploys, edits public/, or writes to _QUEUE/linkedin/. LinkedIn
candidates are listed in the digest only.

Manifest shape (_QUEUE/press/<id>.json):
  {"id": "...", "title": "...", "source": "public/blog-....html",
   "preview": {"ok": true, "at": "YYYY-MM-DD", "url": "..."},
   "review":  {"by": "Zach", "at": "YYYY-MM-DD", "verdict": "pass"},
   "linkedin": true}          # optional: offer as a next-week LinkedIn source if it passes

Usage:
  python3 scripts/press_run.py stage [--date YYYY-MM-DD] [--ceiling N] [--dry-run]
  python3 scripts/press_run.py --self-test
Exit: 0 staged (or dry-run printed), 1 self-test failure, 2 usage error. Stdlib only.
"""
import argparse, datetime, glob, json, os, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_CEILING = 3  # reviewed drafts older than N runs must be re-reviewed or retired


def honest_check(root, src):
    """Mechanical half only. Returns (passed, notes). A missing file fails."""
    path = os.path.join(root, src)
    if not os.path.isfile(path):
        return False, [f"source missing: {src}"]
    notes, ok = [], True
    for tool in ("slop_lint.py", "provenance_lint.py"):
        p = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", tool), path],
                           capture_output=True, text=True)
        if p.returncode != 0:
            ok = False
            last = ((p.stdout + p.stderr).strip().splitlines() or [""])[-1]
            notes.append(f"{tool}: FAIL ({last[:120]})")
        else:
            notes.append(f"{tool}: pass")
    return ok, notes


def runs_since(runs, day):
    """Count prior press runs dated after `day` (the freshness clock ticks in runs, not days)."""
    return sum(1 for r in runs if r.get("date", "") > day)


def classify(m, honest_ok, age, ceiling):
    prev, rev = m.get("preview") or {}, m.get("review") or {}
    if not prev.get("ok"):
        return "NOT_READY", "no passing preview"
    if rev.get("verdict") != "pass" or not rev.get("at"):
        return "NOT_READY", "no passing review"
    if age > ceiling:
        return "STALE", f"reviewed {age} runs ago (ceiling {ceiling}): re-review or retire"
    if not honest_ok:
        return "HELD", "honest check failed"
    return "READY", "all gates pass; awaiting go/no-go"


def stage(root, date, ceiling, dry_run, out=sys.stdout):
    pdir = os.path.join(root, "_STATE", "press-run")
    runs_path = os.path.join(pdir, "runs.jsonl")
    runs = []
    if os.path.isfile(runs_path):
        runs = [json.loads(l) for l in open(runs_path) if l.strip()]
    items = []
    for f in sorted(glob.glob(os.path.join(root, "_QUEUE", "press", "*.json"))):
        m = json.load(open(f))
        h_ok, h_notes = honest_check(root, m.get("source", ""))
        rev_at = (m.get("review") or {}).get("at", "")
        age = runs_since(runs, rev_at) if rev_at else 0
        status, why = classify(m, h_ok, age, ceiling)
        items.append({"id": m.get("id", os.path.basename(f)[:-5]), "title": m.get("title", ""),
                      "source": m.get("source", ""), "status": status, "why": why,
                      "honest": h_notes, "age_runs": age, "linkedin": bool(m.get("linkedin"))})

    counts = {s: sum(1 for i in items if i["status"] == s)
              for s in ("READY", "HELD", "STALE", "NOT_READY")}
    lines = [f"# Press run {date}", "",
             "Staged, not published. Each READY row needs Zach's go or no-go; nothing ships from this file.",
             "", f"Ready {counts['READY']} · Held {counts['HELD']} · Stale {counts['STALE']} · "
             f"Not ready {counts['NOT_READY']} · freshness ceiling {ceiling} runs", ""]
    if not items:
        lines.append("Nothing in _QUEUE/press/. The run is still receipted.")
    for i in items:
        lines += [f"## [{i['status']}] {i['title'] or i['id']}",
                  f"- source: `{i['source']}` · reviewed {i['age_runs']} runs ago",
                  f"- {i['why']}", f"- honest check: {'; '.join(i['honest'])}",
                  "- go / no-go: ____", ""]
    li = [i["id"] for i in items if i["status"] == "READY" and i["linkedin"]]
    lines += ["## Next week's LinkedIn candidates (listed only, not queued)",
              *(f"- {x}" for x in li or ["none"]), ""]
    digest = "\n".join(lines)

    receipts = [{"receipt_id": f"{date}--press-{i['id']}--DRAFT",
                 "question": f"Publish {i['id']} this week?", "horizon": "this-week",
                 "stakes": "low", "mode": "QUICKMOVE", "decision": None, "status": i["status"],
                 "what_confirmed": [n for n in i["honest"] if n.endswith("pass")],
                 "what_unconfirmed": ["go/no-go not yet given"] + [n for n in i["honest"] if not n.endswith("pass")],
                 "operator": "press_run.py (staging only)", "refs": [i["source"]]} for i in items]
    trail = [{"date": date, "id": i["id"], "title": i["title"], "honest_check": "passed"}
             for i in items if i["status"] == "READY"]
    run = {"date": date, "ceiling": ceiling, "counts": counts, "items": len(items),
           "published": 0, "dry_run": dry_run}

    if dry_run:
        out.write(digest + "\n")
        out.write(f"[dry-run] would write {len(receipts)} draft receipts, {len(trail)} trail rows, "
                  f"1 run receipt under {os.path.relpath(pdir, root)}/. Nothing written.\n")
        return run
    os.makedirs(pdir, exist_ok=True)
    with open(os.path.join(pdir, f"{date}.md"), "w") as fh:
        fh.write(digest + "\n")
    with open(os.path.join(pdir, f"{date}.receipts.jsonl"), "w") as fh:
        fh.writelines(json.dumps(r) + "\n" for r in receipts)
    with open(os.path.join(pdir, f"{date}.trail.json"), "w") as fh:
        json.dump(trail, fh, indent=1)
    with open(runs_path, "a") as fh:
        fh.write(json.dumps(run) + "\n")
    out.write(f"staged {os.path.relpath(pdir, root)}/{date}.md ({counts})\n")
    return run


def snapshot(d):
    return sorted((p, os.path.getsize(p), os.path.getmtime(p))
                  for p in glob.glob(os.path.join(d, "**"), recursive=True) if os.path.isfile(p))


def self_test():
    fails = []
    with tempfile.TemporaryDirectory() as t:
        os.makedirs(os.path.join(t, "_QUEUE", "press"))
        os.makedirs(os.path.join(t, "public"))
        open(os.path.join(t, "public", "good.html"), "w").write("<p>A plain sentence.</p>")
        open(os.path.join(t, "public", "bad.html"), "w").write("<p>One \u2014 two.</p>")
        ok = {"preview": {"ok": True, "at": "2026-10-01"}, "review": {"by": "Z", "at": "2026-10-01", "verdict": "pass"}}
        mk = lambda i, **kw: json.dump({"id": i, **ok, **kw}, open(os.path.join(t, "_QUEUE", "press", i + ".json"), "w"))
        mk("a-good", source="public/good.html", linkedin=True)
        mk("b-bad", source="public/bad.html")
        mk("c-old", source="public/good.html", review={"by": "Z", "at": "2026-09-01", "verdict": "pass"})
        mk("d-noprev", source="public/good.html", preview={"ok": False})
        os.makedirs(os.path.join(t, "_STATE", "press-run"))
        open(os.path.join(t, "_STATE", "press-run", "runs.jsonl"), "w").write(
            "".join(json.dumps({"date": d}) + "\n" for d in ("2026-09-08", "2026-09-15", "2026-09-22", "2026-09-29")))
        before = snapshot(t)
        import io
        buf = io.StringIO()
        stage(t, "2026-10-06", DEFAULT_CEILING, True, buf)
        if snapshot(t) != before: fails.append("dry-run wrote to disk")
        if "Nothing written" not in buf.getvalue(): fails.append("dry-run did not say so")
        run = stage(t, "2026-10-06", DEFAULT_CEILING, False, io.StringIO())
        want = {"READY": 1, "HELD": 1, "STALE": 1, "NOT_READY": 1}
        if run["counts"] != want: fails.append(f"counts {run['counts']} != {want}")
        if run["published"] != 0: fails.append("a run published something")
        dig = open(os.path.join(t, "_STATE", "press-run", "2026-10-06.md")).read()
        if "\u2014" in dig: fails.append("digest contains an em-dash")
        if "- a-good" not in dig: fails.append("LinkedIn candidate not listed")
        trail = json.load(open(os.path.join(t, "_STATE", "press-run", "2026-10-06.trail.json")))
        if [r["id"] for r in trail] != ["a-good"]: fails.append(f"trail {trail}")
        # empty queue still files a run receipt
        for f in glob.glob(os.path.join(t, "_QUEUE", "press", "*.json")): os.remove(f)
        stage(t, "2026-10-13", DEFAULT_CEILING, False, io.StringIO())
        n = len(open(os.path.join(t, "_STATE", "press-run", "runs.jsonl")).readlines())
        if n != 6: fails.append(f"empty run not receipted ({n} rows)")
    print("press_run self-test: " + ("PASS 8/8" if not fails else "FAIL: " + "; ".join(fails)))
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="press_run", description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("stage", help="stage this week's go/no-go digest")
    s.add_argument("--date", default=datetime.date.today().isoformat())
    s.add_argument("--ceiling", type=int, default=DEFAULT_CEILING)
    s.add_argument("--dry-run", action="store_true", help="print the digest; write nothing")
    a = ap.parse_args(argv)  # argparse exits 2 on any unknown flag: a look never becomes a touch
    if a.self_test:
        return self_test()
    if a.cmd != "stage":
        ap.print_usage(sys.stderr)
        return 2
    try:
        datetime.date.fromisoformat(a.date)
    except ValueError:
        ap.error(f"--date must be YYYY-MM-DD, got {a.date!r}")
    stage(ROOT, a.date, a.ceiling, a.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
