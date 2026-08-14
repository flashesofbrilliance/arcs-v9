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
import json, os, sys, datetime, subprocess, shutil

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
SEEDS = os.path.join(ROOT, "_SEEDS")
INDEX = os.path.join(SEEDS, "index.jsonl")
LEDGER = os.path.join(SEEDS, "ledger.jsonl")
RECEIPTS = os.path.join(ROOT, "_INBOX", "seedbank-drift.jsonl")
STALE_DAYS = 21


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
        if local and not os.path.exists(local):
            findings.append({"claim": "broken-local-path", "drift": True, "detail": f"{rid}: {local}"})

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


def main():
    regenerate = "--regenerate" in sys.argv
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
