#!/usr/bin/env python3
"""seedbank_drift_check — an inchworm drift detector for the _SEEDS bank.

The _SEEDS bank (_SEEDS/index.jsonl = alias index over the atomized public repos;
_SEEDS/ledger.jsonl = append-only conformance/drift receipts) is a hand-curated
registry with no owner. It drifts by neglect: a repo gets a local clone deleted, a
seed never gets a ledger receipt, or the whole bank goes stale while the public
repos move underneath it. This does NOT re-author the bank — curation is human
judgment (NOTOMATION). It checks the MECHANICALLY verifiable invariants and emits a
drift RECEIPT. Mirror of scripts/lattice_drift_check.py (ADR-052); enforces ADR-055.

  check     (default) verify invariants, append a receipt to _INBOX/seedbank-drift.jsonl
  --regenerate        additionally stamp last_check into the receipt stream; never
                      edits index.jsonl seed rows or authors ledger judgment — those
                      stay human-owned.

Invariants checked (all stdlib, no network):
  1. index.jsonl and ledger.jsonl are valid JSONL.
  2. Orphan seeds — a seed in index with NO ledger event (never received a receipt).
  3. Broken local paths — a seed whose `local` is set but does not exist on disk.
  4. Staleness — newest ledger event older than STALE_DAYS.
  (Optional, best-effort, guarded: if `gh` is on PATH, compare catalogued repo count
   to the account's public non-fork repo count — a coverage gap signal.)

Stdlib only. Exit 0 always (hook-safe; a drift is a receipt, not a failure).
"""
import argparse, hashlib, json, os, sys, datetime, subprocess, shutil

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
SEEDS = os.path.join(ROOT, "_SEEDS")
INDEX = os.path.join(SEEDS, "index.jsonl")
LEDGER = os.path.join(SEEDS, "ledger.jsonl")
RECEIPTS = os.path.join(ROOT, "_INBOX", "seedbank-drift.jsonl")


def _pulse_max(name, fallback):
    """Freshness budget in beats(=days). The pulse (_STATE/pulse.json) is the SSOT for
    every subsystem's staleness threshold; falls back to the historical value if pulse is
    absent (air-gapped / another machine)."""
    try:
        return json.load(open(os.path.join(ROOT, "_STATE/pulse.json")))["subsystems"][name]["max_beats"]
    except Exception:
        return fallback


STALE_DAYS = _pulse_max("seedbank-drift", 21)  # SSOT: pulse.json subsystems.seedbank-drift.max_beats


def _load_jsonl(path):
    rows, bad = [], []
    if not os.path.exists(path):
        return rows, [f"missing:{os.path.basename(path)}"]
    for i, line in enumerate(open(path), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception as e:
            bad.append(f"{os.path.basename(path)}:L{i}:{e.__class__.__name__}")
    return rows, bad


def _newest_ledger_date(led):
    dates = []
    for e in led:
        ts = e.get("ts", "")
        try:
            dates.append(datetime.date.fromisoformat(ts[:10]))
        except Exception:
            pass
    return max(dates) if dates else None


def _gh_public_count():
    if not shutil.which("gh"):
        return None
    try:
        out = subprocess.run(
            ["gh", "repo", "list", "flashesofbrilliance", "--limit", "100",
             "--json", "isFork,visibility"],
            capture_output=True, text=True, timeout=15,
        )
        data = json.loads(out.stdout or "[]")
        return sum(1 for r in data if r.get("visibility") == "PUBLIC" and not r.get("isFork"))
    except Exception:
        return None


_PATH_EXT = (".py", ".json", ".jsonl", ".md", ".html", ".sh", ".mjs", ".ts", ".tsx", ".csv", ".yml", ".yaml", ".txt")
_DOMAIN = r"^[\w-]+\.(xyz|com|care|org|io|dev|net|app)(/|$)"


def local_paths(local):
    """Repo paths named in a seed's `local` field. The field often carries prose after the path
    (`runtime/specs/x.json (the analog); canon unbuilt`), so existence is checked per path token,
    never on the whole string. Prose, URLs, slash-commands and domains are not paths."""
    import re
    text = re.sub(r"\([^)]*\)", " ", local or "")
    out = []
    for part in re.split(r"[;+\u00b7]", text):
        for tok in part.split():
            tok = tok.rstrip(",.")
            if not tok or tok.startswith(("/", "http", "~")) or re.match(_DOMAIN, tok):
                continue
            if "/" in tok or tok.lower().endswith(_PATH_EXT):
                out.append(tok)
    return out


def check():
    idx, idx_bad = _load_jsonl(INDEX)
    led, led_bad = _load_jsonl(LEDGER)

    findings = []
    if idx_bad or led_bad:
        findings.append({"claim": "jsonl-valid", "drift": True, "detail": idx_bad + led_bad})

    seeds_in_ledger = {e.get("seed") for e in led}
    # index rows are keyed by alias (ledger `seed` field uses the short alias)
    for row in idx:
        alias = row.get("alias", "").split(" ")[0]  # strip "(proposed repo)" suffixes
        rid = row.get("id", "?")
        if alias and alias not in seeds_in_ledger and row.get("id", "").replace("seed-", "").replace("repo-", "") not in seeds_in_ledger:
            findings.append({"claim": "orphan-seed", "drift": True, "detail": f"{rid} has no ledger receipt"})
        local = row.get("local")
        missing = [q for q in local_paths(local) if not os.path.exists(q)]
        if missing:
            findings.append({"claim": "broken-local-path", "drift": True, "detail": f"{rid}: {', '.join(missing)}"})

    newest = _newest_ledger_date(led)
    stale_days = (datetime.date.today() - newest).days if newest else None
    if stale_days is not None and stale_days > STALE_DAYS:
        findings.append({"claim": "staleness", "drift": True,
                         "detail": f"newest ledger event {stale_days}d old (> {STALE_DAYS})"})

    gh_count = _gh_public_count()
    if gh_count is not None:
        repo_seeds = sum(1 for r in idx if r.get("seed_type") == "repo")
        if gh_count > repo_seeds:
            findings.append({"claim": "coverage-gap", "drift": True,
                             "detail": f"account has {gh_count} public repos; {repo_seeds} catalogued"})

    return idx, led, findings, stale_days


def _parse_args(argv=None):
    ap = argparse.ArgumentParser(prog="seedbank_drift_check.py",
                                 description="Drift detector for the _SEEDS bank (receipt-only).")
    ap.add_argument("--regenerate", action="store_true",
                    help="stamp regenerated=true into the receipt; never edits _SEEDS files")
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
        # empty PATH dir: no `gh`, so the self-test never touches the network
        nobin = os.path.join(tmp, "nobin")
        os.makedirs(nobin)
        env = dict(os.environ, CLAUDE_PROJECT_DIR=tmp, PATH=nobin)
        seeds = os.path.join(tmp, "_SEEDS")
        os.makedirs(seeds)
        idx, led = os.path.join(seeds, "index.jsonl"), os.path.join(seeds, "ledger.jsonl")
        open(idx, "w").write(json.dumps({"id": "seed-a", "alias": "a"}) + "\n")
        open(led, "w").write(json.dumps({"seed": "a", "ts": "2020-01-01"}) + "\n")
        rec = os.path.join(tmp, "_INBOX", "seedbank-drift.jsonl")

        def run(*a):
            return subprocess.run([sys.executable, me, *a], env=env, cwd=tmp, capture_output=True, text=True)

        def check(name, ok):
            nonlocal fails, total
            total += 1
            print(("PASS " if ok else "FAIL ") + name)
            fails += 0 if ok else 1

        h0 = (_sha(idx), _sha(led))
        check("unknown flag exits 2", run("--regenrate").returncode == 2)
        check("extra positional exits 2", run("check").returncode == 2)
        check("rejected args write no receipt", not os.path.exists(rec))
        r = run()
        check("default mode exits 0 and reports DRIFT", r.returncode == 0 and "DRIFT" in r.stdout)
        check("default mode leaves _SEEDS untouched", (_sha(idx), _sha(led)) == h0)
        r = run("--regenerate")
        check("--regenerate leaves _SEEDS untouched", r.returncode == 0 and (_sha(idx), _sha(led)) == h0)
        rows = [json.loads(l) for l in open(rec)] if os.path.exists(rec) else []
        check("receipts appended, regenerated flag stamped",
              len(rows) == 2 and [x["regenerated"] for x in rows] == [False, True])
    total += 4
    ok1 = local_paths("runtime/specs/tool-catalog.json (the tool-analog: /catalog); canon analog unbuilt") == ["runtime/specs/tool-catalog.json"]
    ok2 = local_paths("_ARTIFACTS/a.md (x) \u00b7 _ARTIFACTS/b/ + public/c.html (y)") == ["_ARTIFACTS/a.md", "_ARTIFACTS/b/", "public/c.html"]
    ok3 = local_paths("mirrored public at zachharris.xyz/scan (own static repo)") == []
    ok4 = local_paths(".claude/skills/x/ (y)") == [".claude/skills/x/"] and local_paths(None) == [] and local_paths("AGENTS.md (table) + src/x.ts") == ["AGENTS.md", "src/x.ts"]
    for name, ok in (("annotated path yields only the path", ok1), ("separators split paths", ok2), ("domain and prose are not paths", ok3), ("bare filename and None", ok4)):
        print(("PASS " if ok else "FAIL ") + name)
        fails += 0 if ok else 1
    print(f"seedbank_drift_check self-test: {total - fails}/{total}")
    sys.exit(1 if fails else 0)


def main():
    args = _parse_args()
    if args.self_test:
        self_test()
    regenerate = args.regenerate
    idx, led, findings, stale_days = check()
    drifted = [f for f in findings if f.get("drift")]

    receipt = {
        "ts": datetime.date.today().isoformat(),
        "check": "seedbank-drift",
        "index_rows": len(idx),
        "ledger_rows": len(led),
        "stale_days": stale_days,
        "drifted": len(drifted),
        "findings": findings,
        "regenerated": regenerate,
    }
    os.makedirs(os.path.dirname(RECEIPTS), exist_ok=True)
    with open(RECEIPTS, "a") as f:
        f.write(json.dumps(receipt) + "\n")

    if not os.path.exists(INDEX):
        print("seedbank-drift: no _SEEDS bank yet (skip)")
        return
    if drifted:
        print(f"seedbank-drift: DRIFT · {len(drifted)} finding(s) · stale {stale_days}d · receipt -> _INBOX/seedbank-drift.jsonl")
        for f in drifted[:5]:
            print(f"  DRIFT [{f['claim']}] {f.get('detail','')}")
        print("seedbank-drift: receipt-only (curation stays human-owned; re-catalog by hand)")
    else:
        print(f"seedbank-drift: OK · {len(idx)} seeds · {len(led)} receipts · stale {stale_days}d")


if __name__ == "__main__":
    main()
