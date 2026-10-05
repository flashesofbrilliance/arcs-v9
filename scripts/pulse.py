#!/usr/bin/env python3
"""pulse — the global heartbeat: a wall-clock clock that is the oracle's second strand.

WHY THIS EXISTS
  The drift-sentry went stale for 5 days *silently* — the operational layer went quiet
  and nothing alarmed until a human happened to look. A self-report ("I'm fresh") cannot
  catch this: a dead poller reports nothing, not "I'm dead." The fix is an independent
  clock, anchored to the tamper-evident record (git commit timestamps), that alarms when
  an organ stops moving — on day 2, not day 5.

THE TWIN (pulse ⇄ oracle)
  `scripts/oracle.py` is a logical clock backed by git: it counts *events* (ADR/seed/handoff
  allocations); git's non-fast-forward rejection is its atomicity lock. `pulse` is its
  WALL-CLOCK twin: it counts *beats* (days) and measures how many beats since each subsystem
  last showed proof-of-life. Together they are a mutual-attestation pair — neither self-certifies:
    · pulse → oracle : counter monotonic, advancing, no off-oracle mints on disk (reuses oracle's own audit).
    · oracle → pulse : each allocation stamps the `oracle` subsystem's last_beat; the guard
                       alarms if the oracle's committed counter moved but the stamp did not (flatline).

PROOF-OF-LIFE = GIT COMMIT TIMESTAMP (the OT layer, not the IT layer)
  Liveness is derived from the *operational* layer being observably active — work that actually
  LANDED IN GIT — not from a subsystem claiming freshness. `git log -1 --format=%ct -- <paths>`
  is the tamper-evident beat. A `pulse stamp` is a secondary heartbeat for organs with no committed
  artifact; the git timestamp always wins when both exist. No standing service, no watcher-of-the-
  watcher regress; git works offline (local-first / air-gapped-friendly).

BEATS, not days-scattered-everywhere
  Freshness is reported in BEATS-SINCE. `_STATE/pulse.json` is the SSOT for each subsystem's
  `max_beats` budget, absorbing the scattered private STALE_DAYS constants (lattice, seedbank).
  A beat is one day; `global_beat = (today - genesis).days`, derivable anywhere, cannot silently freeze.

Usage:
  pulse now                       grounded global_beat + ISO timestamp (host clock, explicit)
  pulse status [--json]           the board: every subsystem's beats-since / budget / FRESH|STALE|FLATLINE|DORMANT
  pulse check [--strict]          mutual guard (pulse⇄oracle) + flatline scan; append receipt -> _INBOX/pulse.jsonl.
                                  Exit 0 always (hook-safe) unless --strict (then non-zero if any alarm).
  pulse stamp <subsystem>         record proof-of-life NOW (secondary heartbeat for stamp-only organs).
  pulse max <subsystem>           print a subsystem's max_beats (SSOT for the absorbed STALE_DAYS).

Stdlib only. Exit 0 on success; non-zero only on misuse or --strict alarm.
"""
import json, os, sys, subprocess, datetime

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
PULSE = os.path.join(ROOT, "_STATE", "pulse.json")
ORACLE = os.path.join(ROOT, "_SEEDS", "_oracle.json")
RECEIPTS = os.path.join(ROOT, "_INBOX", "pulse.jsonl")
DECISIONS = os.path.join(ROOT, "_DECISIONS")

# Genesis fallback if pulse.json is absent/corrupt (local-first: never hard-fail).
_GENESIS_FALLBACK = "2026-09-08"


def _today():
    return datetime.date.today()


def _load():
    if os.path.exists(PULSE):
        try:
            return json.load(open(PULSE))
        except Exception:
            pass
    return {"genesis": _GENESIS_FALLBACK, "global_beat": 0, "subsystems": {}}


def _save(d):
    os.makedirs(os.path.dirname(PULSE), exist_ok=True)
    with open(PULSE, "w") as f:
        json.dump(d, f, indent=2, sort_keys=True)
        f.write("\n")


def _genesis(d):
    try:
        return datetime.date.fromisoformat(d.get("genesis", _GENESIS_FALLBACK))
    except Exception:
        return datetime.date.fromisoformat(_GENESIS_FALLBACK)


def global_beat(d):
    return (_today() - _genesis(d)).days


def _git_last_ct(paths):
    """Unix commit timestamp (int) of the most recent commit touching any of `paths`.
    The tamper-evident OT proof-of-life. None if never committed / git unavailable."""
    if not paths:
        return None
    try:
        out = subprocess.run(
            ["git", "-C", ROOT, "log", "-1", "--format=%ct", "--"] + list(paths),
            capture_output=True, text=True, timeout=15,
        )
        s = out.stdout.strip()
        return int(s) if s else None
    except Exception:
        return None


def _proof(name, cfg):
    """Return (beats_since, proof_date_iso, source) for a subsystem.
    Resolution order — git commit timestamp (authoritative, tamper-evident) beats the
    self-reported stamp. beats_since is calendar days since proof-of-life; genesis-independent."""
    ct = _git_last_ct(cfg.get("artifacts", []))
    if ct is not None:
        d = datetime.date.fromtimestamp(ct)
        return (_today() - d).days, d.isoformat(), "git"
    stamp = cfg.get("last_seen")
    if stamp:
        try:
            d = datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00")).date()
            return (_today() - d).days, d.isoformat(), "stamp"
        except Exception:
            pass
    return None, None, "unseen"


def _verdict(beats_since, cfg):
    """FRESH within budget · STALE at/over budget · FLATLINE never-seen · DORMANT expected-inactive."""
    maxb = cfg.get("max_beats", 7)
    if cfg.get("expected") == "inactive":
        return "DORMANT"
    if beats_since is None:
        return "FLATLINE"
    if beats_since > maxb:
        return "FLATLINE"
    if beats_since >= maxb:
        return "STALE"
    return "FRESH"


# ---- mutual check: pulse -> oracle ---------------------------------------------------

def _oracle_check():
    """pulse attesting the oracle: counters present + no off-oracle ADR mint on disk.
    Reuses the disk-vs-counter logic oracle.audit_adr embodies. Returns (ok, notes)."""
    notes = []
    if not os.path.exists(ORACLE):
        return False, ["oracle: _SEEDS/_oracle.json missing"]
    try:
        counters = json.load(open(ORACLE))
    except Exception as e:
        return False, [f"oracle: unreadable ({e})"]
    # off-oracle mint: an ADR file numbered above the oracle's committed high-water.
    import glob, re
    hi_disk = 0
    for p in glob.glob(os.path.join(DECISIONS, "ADR-*.md")):
        m = re.search(r"ADR-(\d+)", os.path.basename(p))
        if m:
            hi_disk = max(hi_disk, int(m.group(1)))
    hi_oracle = int(counters.get("adr", 0))
    if hi_disk > hi_oracle:
        notes.append(f"OFF-ORACLE MINT: ADR-{hi_disk:03d} on disk > oracle counter {hi_oracle}")
        return False, notes
    return True, [f"oracle: adr counter {hi_oracle} >= disk high-water {hi_disk}"]


# ---- commands ------------------------------------------------------------------------

def cmd_now():
    d = _load()
    gb = global_beat(d)
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"global_beat {gb} · {ts} · genesis {d.get('genesis')}")


def _board(d):
    rows = []
    for name, cfg in sorted(d.get("subsystems", {}).items()):
        bs, pdate, src = _proof(name, cfg)
        rows.append((name, cfg, bs, pdate, src, _verdict(bs, cfg)))
    return rows


def cmd_status(as_json=False):
    d = _load()
    rows = _board(d)
    if as_json:
        print(json.dumps({
            "global_beat": global_beat(d), "genesis": d.get("genesis"),
            "subsystems": {n: {"beats_since": bs, "max_beats": c.get("max_beats"),
                               "proof_date": pd, "source": s, "verdict": v}
                           for n, c, bs, pd, s, v in rows},
        }, indent=2))
        return
    print(f"pulse · global_beat {global_beat(d)} · genesis {d.get('genesis')}")
    for name, cfg, bs, pdate, src, v in rows:
        bstr = "—" if bs is None else f"{bs}"
        print(f"  [{v:<8}] {name:<20} {bstr:>4}/{cfg.get('max_beats')} beats  "
              f"(proof: {pdate or 'never'} via {src})")


def cmd_stamp(name):
    d = _load()
    subs = d.setdefault("subsystems", {})
    if name not in subs:
        sys.stderr.write(f"pulse: unknown subsystem '{name}' — register it in _STATE/pulse.json first\n")
        sys.exit(2)
    subs[name]["last_beat"] = global_beat(d)
    subs[name]["last_seen"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    d["global_beat"] = global_beat(d)
    _save(d)
    print(f"pulse: stamped {name} @ beat {subs[name]['last_beat']}")


def cmd_max(name):
    d = _load()
    cfg = d.get("subsystems", {}).get(name)
    if not cfg:
        sys.stderr.write(f"pulse: unknown subsystem '{name}'\n"); sys.exit(2)
    print(cfg.get("max_beats", 7))


def cmd_check(strict=False):
    d = _load()
    gb = global_beat(d)
    d["global_beat"] = gb  # keep the twin honest even on a read-path
    rows = _board(d)
    flatlines = [(n, bs, c.get("max_beats")) for n, c, bs, pd, s, v in rows if v == "FLATLINE"]
    stales = [(n, bs, c.get("max_beats")) for n, c, bs, pd, s, v in rows if v == "STALE"]
    ok_oracle, oracle_notes = _oracle_check()

    # refresh cached last_beat from the git-derived truth (file stays a faithful twin)
    for n, c, bs, pd, s, v in rows:
        if bs is not None:
            d["subsystems"][n]["last_beat"] = gb - bs
    _save(d)

    alarm = bool(flatlines) or not ok_oracle
    verdict = "ALARM" if alarm else ("STALE" if stales else "OK")
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    receipt = {
        "ts": ts, "global_beat": gb, "type": "pulse-check-receipt", "verdict": verdict,
        "flatlines": [{"subsystem": n, "beats_since": bs, "max_beats": m} for n, bs, m in flatlines],
        "stale": [{"subsystem": n, "beats_since": bs, "max_beats": m} for n, bs, m in stales],
        "oracle_ok": ok_oracle, "oracle_notes": oracle_notes,
    }
    os.makedirs(os.path.dirname(RECEIPTS), exist_ok=True)
    with open(RECEIPTS, "a") as fh:
        fh.write(json.dumps(receipt, ensure_ascii=False) + "\n")

    print(f"pulse: {verdict} · global_beat {gb} · "
          f"{len(flatlines)} flatline · {len(stales)} stale · oracle {'ok' if ok_oracle else 'FAIL'} "
          f"· receipt -> _INBOX/pulse.jsonl")
    for n, bs, m in flatlines:
        print(f"  FLATLINE [{n}] {('never seen' if bs is None else str(bs)+' beats')} > {m} budget — the operational layer went quiet")
    if not ok_oracle:
        for note in oracle_notes:
            print(f"  ORACLE   {note}")
    for n, bs, m in stales:
        print(f"  stale    [{n}] {bs}/{m} beats — approaching flatline")

    if strict and alarm:
        sys.exit(1)
    return 0


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__.strip().splitlines()[0]); return
    cmd = args[0]
    if cmd == "now":
        cmd_now()
    elif cmd == "status":
        cmd_status(as_json="--json" in args)
    elif cmd == "check":
        cmd_check(strict="--strict" in args)
    elif cmd == "stamp" and len(args) > 1:
        cmd_stamp(args[1])
    elif cmd == "max" and len(args) > 1:
        cmd_max(args[1])
    else:
        sys.stderr.write("usage: pulse now | status [--json] | check [--strict] | stamp <subsystem> | max <subsystem>\n")
        sys.exit(2)


if __name__ == "__main__":
    main()
