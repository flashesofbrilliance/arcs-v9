#!/usr/bin/env python3
"""lattice_drift_check — a drift detector for the orphaned knowledge lattice.

The knowledge lattice (runtime/specs/knowledge-lattice-v1.json) is a hand-authored,
epoch-pinned snapshot with no owner. It drifts by neglect: the deployed artifact
embeds it statically, so a stale claim ships to a prospect surface (e.g. "32 ADRs"
while the repo has 44). This does NOT re-author the lattice — that is human judgment
(NOTOMATION). It checks the MECHANICALLY verifiable claims against repo truth and
emits a drift RECEIPT. The human re-authors; the receipt teaches.

  check     (default) diff claims vs repo, append a receipt to _INBOX/lattice-drift.jsonl
  --regenerate        additionally patch ONLY the mechanical countables in the JSON
                      (e.g. the ADR count) + stamp last_drift_check; never touches
                      node statuses, edges, or prose — those stay human-owned.

Stdlib only. Exit 0 always (hook-safe; a drift is a receipt, not a failure).
"""
import argparse, hashlib, json, glob, re, subprocess, sys, datetime, os

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
LATTICE = os.path.join(ROOT, "runtime/specs/knowledge-lattice-v1.json")
RECEIPTS = os.path.join(ROOT, "_INBOX/lattice-drift.jsonl")


def _pulse_max(name, fallback):
    """Freshness budget in beats(=days). The pulse (_STATE/pulse.json) is the SSOT for
    every subsystem's staleness threshold; this reads it so the constant lives in one place.
    Falls back to the historical value when pulse is absent (air-gapped / another machine)."""
    try:
        return json.load(open(os.path.join(ROOT, "_STATE/pulse.json")))["subsystems"][name]["max_beats"]
    except Exception:
        return fallback


STALE_DAYS = _pulse_max("lattice-drift", 14)  # SSOT: pulse.json subsystems.lattice-drift.max_beats


def repo_adr_count():
    return len(glob.glob(os.path.join(ROOT, "_DECISIONS/ADR-*.md")))


def check(data):
    findings = []

    # 1. ADR count — the "adrs" node label carries a number; compare to disk.
    adrs = next((n for n in data["nodes"] if n["id"] == "adrs"), None)
    if adrs:
        m = re.search(r"(\d+)\s*ADR", adrs.get("label", ""))
        if m:
            claimed, actual = int(m.group(1)), repo_adr_count()
            findings.append({
                "claim": "ADR count (node:adrs)", "lattice": claimed, "repo": actual,
                "drift": claimed != actual,
            })

    # 2. Epoch staleness — parse the last epoch date from epoch_source.
    stale_days = None
    dates = re.findall(r"e\d+\s*=\s*(\d{4}-\d{2}-\d{2})", data.get("epoch_source", ""))
    if dates:
        latest = max(dates)  # the newest epoch, not the first
        try:
            d0 = datetime.date.fromisoformat(latest)
            stale_days = (datetime.date.today() - d0).days
            findings.append({
                "claim": "epoch freshness", "lattice": latest,
                "repo": datetime.date.today().isoformat(), "stale_days": stale_days,
                "drift": stale_days > STALE_DAYS,
            })
        except ValueError:
            pass

    # 3. Unverified surface — how much of the lattice is aspirational ('true') or gated.
    counts = {}
    for n in data["nodes"]:
        counts[n.get("status", "?")] = counts.get(n.get("status", "?"), 0) + 1
    findings.append({
        "claim": "unverified-node share",
        "lattice": f"{counts.get('true', 0)} aspirational + {counts.get('gate', 0)} gated + {counts.get('shore', 0)} shore of {len(data['nodes'])}",
        "repo": "human-owned (not auto-checkable)", "drift": False,
    })

    return findings, stale_days


def _parse_args(argv=None):
    ap = argparse.ArgumentParser(prog="lattice_drift_check.py",
                                 description="Drift detector for the knowledge lattice (receipt-only by default).")
    ap.add_argument("--regenerate", action="store_true",
                    help="also patch ONLY the mechanical countables in the lattice JSON (the only write path)")
    ap.add_argument("--self-test", action="store_true", help="run the CLI guard self-test in a temp dir")
    return ap.parse_args(argv)


def _sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest() if os.path.exists(path) else None


def self_test():
    """Run the CLI in a throwaway project dir and assert the guard holds. Never touches ROOT."""
    import tempfile
    me = os.path.abspath(__file__)
    fails = total = 0
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ, CLAUDE_PROJECT_DIR=tmp)
        lat = os.path.join(tmp, "runtime/specs/knowledge-lattice-v1.json")
        os.makedirs(os.path.dirname(lat))
        os.makedirs(os.path.join(tmp, "_DECISIONS"))
        for i in (1, 2, 3):
            open(os.path.join(tmp, f"_DECISIONS/ADR-00{i}.md"), "w").write("x\n")
        json.dump({"epoch_source": "e1 = 2020-01-01",
                   "nodes": [{"id": "adrs", "label": "1 ADRs", "status": "true"}]},
                  open(lat, "w"))

        def run(*a):
            return subprocess.run([sys.executable, me, *a], env=env, cwd=tmp, capture_output=True, text=True)

        def check(name, ok):
            nonlocal fails, total
            total += 1
            print(("PASS " if ok else "FAIL ") + name)
            fails += 0 if ok else 1

        h0 = _sha(lat)
        check("unknown flag exits 2", run("--regenrate").returncode == 2)
        check("extra positional exits 2", run("check").returncode == 2)
        check("rejected args leave lattice untouched", _sha(lat) == h0)
        r = run()
        check("default mode exits 0 and reports DRIFT", r.returncode == 0 and "DRIFT" in r.stdout)
        check("default mode leaves lattice untouched", _sha(lat) == h0)
        r = run("--regenerate")
        check("--regenerate patches the ADR count",
              r.returncode == 0 and json.load(open(lat))["nodes"][0]["label"] == "3 ADRs")
    print(f"lattice_drift_check self-test: {total - fails}/{total}")
    sys.exit(1 if fails else 0)


def main():
    args = _parse_args()
    if args.self_test:
        self_test()
    regen = args.regenerate
    if not os.path.exists(LATTICE):
        print(f"lattice-drift: no lattice at {LATTICE} — skipping")
        return 0
    data = json.load(open(LATTICE))
    findings, stale_days = check(data)
    drifted = [f for f in findings if f.get("drift")]

    # NOTE: no Date.now() taboo here — this is Python at runtime, real clock is correct.
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    receipt = {
        "ts": ts, "artifact": "runtime/specs/knowledge-lattice-v1.json",
        "type": "lattice-drift-receipt", "stale_days": stale_days,
        "drift_count": len(drifted), "findings": findings,
        "verdict": "DRIFT" if drifted else "fresh",
    }
    os.makedirs(os.path.dirname(RECEIPTS), exist_ok=True)
    with open(RECEIPTS, "a") as fh:
        fh.write(json.dumps(receipt, ensure_ascii=False) + "\n")

    print(f"lattice-drift: {receipt['verdict']} · {len(drifted)} drifted claim(s) · stale {stale_days}d · receipt -> _INBOX/lattice-drift.jsonl")
    for f in drifted:
        print(f"  DRIFT [{f['claim']}] lattice={f['lattice']} repo={f['repo']}")

    if regen:
        # Patch ONLY mechanical countables. Never statuses/edges/prose (NOTOMATION).
        # Idempotent: writes the file ONLY when a countable actually changed, so
        # "advance at close" never churns an already-fresh lattice.
        patched = []
        adrs = next((n for n in data["nodes"] if n["id"] == "adrs"), None)
        actual = repo_adr_count()
        if adrs:
            m = re.search(r"(\d+)(\s*ADRs?)", adrs.get("label", ""))
            if m and int(m.group(1)) != actual:
                adrs["label"] = re.sub(r"\d+(\s*ADRs?)", f"{actual}\\1", adrs["label"])
                patched.append(f"ADR count {m.group(1)} -> {actual}")
        if patched:
            data["last_drift_check"] = ts
            data["_note"] = "Countables auto-refreshed by lattice_drift_check; node statuses/edges/prose remain human-authored (NOTOMATION). Re-author the judgment layer manually."
            json.dump(data, open(LATTICE, "w"), ensure_ascii=False, indent=0)
            print(f"lattice-drift: --regenerate advanced -> {'; '.join(patched)} (judgment layer left for human)")
        else:
            print("lattice-drift: --regenerate no-op (countables already fresh; judgment-layer drift stays a receipt)")
    elif drifted:
        print("lattice-drift: receipt-only (run with --regenerate to patch countables; the judgment layer stays human-owned)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
