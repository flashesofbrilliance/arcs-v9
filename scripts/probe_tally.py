#!/usr/bin/env python3
"""probe_tally: read the owned demand-probe counts and let the backlog row move with them.

Reads GET https://good.arcs.care/api/probe?probe=<probe> (our DemandSignal table, not Vercel),
writes _STATE/demand-probes.json (append-only history + latest), and updates the matching
row in _QUEUE/induced-backlog.jsonl: `tally` (latest counts) and `priority` by band.

Bands (distinct visitors who clicked "I'd use this"; Zach can retune in the backlog row's
`bands` field, the script reads them from there so the rule lives with the item):
  seed       < 10   P3   keep the probe up, no build
  directional 10..24 P2   scope the MCP wrapper, no hosted build
  powered    >= 25  P1   build (the ADR-076 Y validation is met)
Zach's own judgment can pin `priority_pin` on the row; the tally never lowers a pinned priority.

Usage: python3 scripts/probe_tally.py [--probe mcp-connector] [--base https://good.arcs.care] [--dry-run]
       python3 scripts/probe_tally.py --self-test
--dry-run reads the probe and prints the would-be tally and priority; writes nothing.
Paths are relative to the current directory (run from the repo root).
stdlib only; exit 0 always (a readout, not a gate).
"""
import argparse, datetime, hashlib, json, os, sys, urllib.request


def fetch(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "arcs-probe-tally"}), timeout=15) as r:
            return json.load(r)
    except Exception as e:
        print(f"⚠ probe_tally: could not read {url} ({e}). Route not deployed yet, or table missing in prod.")
        return None


def run(probe, base, dry_run=False):
    url = f"{base}/api/probe?probe={probe}"
    data = fetch(url)

    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    state_p = "_STATE/demand-probes.json"
    state = json.load(open(state_p)) if os.path.exists(state_p) else {"history": []}
    if data:
        state["latest"] = {**data, "read_at": now}
        state.setdefault("history", []).append({"read_at": now, "views": data["views"], "interest": data["interest"], "interestVisitors": data["interestVisitors"]})
        state["history"] = state["history"][-200:]
        if not dry_run:
            with open(state_p, "w") as f:
                json.dump(state, f, indent=1); f.write("\n")

    q = "_QUEUE/induced-backlog.jsonl"
    lines = open(q).readlines() if os.path.exists(q) else []
    hit = hit_i = None
    for i, l in enumerate(lines):
        if not l.strip():
            continue
        row = json.loads(l)
        if row.get("probe") == probe:
            hit, hit_i = row, i
            if data:
                v = data["interestVisitors"]
                bands = row.get("bands", {"P3": 0, "P2": 10, "P1": 25})
                band = "P3"
                if v >= bands.get("P2", 10): band = "P2"
                if v >= bands.get("P1", 25): band = "P1"
                pin = row.get("priority_pin")
                row["tally"] = {"views": data["views"], "interest": data["interest"], "interestVisitors": v, "read_at": now, "band": band}
                row["priority"] = min(pin, band) if pin else band  # "P1" < "P2" lexically: min = higher priority
                lines[i] = json.dumps(row) + "\n"
    # Rewrite only when a row changed, and only that row: the other lines stay byte-for-byte.
    if hit and data and not dry_run:
        with open(q, "w") as f:
            f.writelines(lines)
    if data:
        print(("[dry-run] " if dry_run else "") + f"✓ probe_tally {probe}: views={data['views']} interest={data['interest']} distinct visitors={data['interestVisitors']}"
              + (f" → backlog {hit['id']} priority={hit['priority']} (band {hit['tally']['band']}" + (f", pinned {hit['priority_pin']}" if hit.get('priority_pin') else "") + ")" if hit else " (no backlog row carries this probe)"))
    return 0


def _snapshot(root):
    out = {}
    for d, _, fs in os.walk(root):
        for n in fs:
            p = os.path.join(d, n)
            out[p] = (hashlib.sha256(open(p, "rb").read()).hexdigest(), os.stat(p).st_mtime_ns)
    return out


def self_test():
    """Subprocess the script in a temp cwd against a local stub HTTP server (no real network)."""
    import http.server, shutil, subprocess, tempfile, threading

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            body = json.dumps({"views": 40, "interest": 13, "interestVisitors": 12}).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
            self.wfile.write(body)
        def log_message(self, *a): pass

    srv = http.server.HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    tmp = tempfile.mkdtemp(prefix="probe-tally-selftest-")
    fails = total = 0

    def ok(name, cond):
        nonlocal fails, total
        total += 1
        print(("  PASS  " if cond else "  FAIL  ") + name)
        fails += 0 if cond else 1

    try:
        me = os.path.join(tmp, "probe_tally.py")
        shutil.copy2(os.path.abspath(__file__), me)
        work = os.path.join(tmp, "repo")
        os.makedirs(os.path.join(work, "_STATE")); os.makedirs(os.path.join(work, "_QUEUE"))
        other = '{"id": "keep-me", "note": "caf\u00e9",  "spacing":"odd"}\n'
        with open(os.path.join(work, "_QUEUE/induced-backlog.jsonl"), "w") as f:
            f.write(other + json.dumps({"id": "probe-row", "probe": "mcp-connector", "priority": "P3"}) + "\n")

        def run_(*a):
            return subprocess.run([sys.executable, me, *a], capture_output=True, text=True, cwd=work)

        before = _snapshot(work)
        ok("unknown flag exits 2", run_("--bogus").returncode == 2)
        ok("extra positional exits 2", run_("extra").returncode == 2)
        ok("--probe without value exits 2", run_("--probe").returncode == 2)
        r = run_("--dry-run", "--base", base)
        ok("--dry-run exits 0 and reports band", r.returncode == 0 and "[dry-run]" in r.stdout and "priority=P2" in r.stdout)
        ok("--dry-run writes nothing", _snapshot(work) == before)
        r = run_("--base", base)
        ok("write mode exits 0", r.returncode == 0)
        rows = open(os.path.join(work, "_QUEUE/induced-backlog.jsonl")).readlines()
        ok("write mode updates the probe row", json.loads(rows[1]).get("priority") == "P2")
        ok("write mode keeps other rows byte-for-byte", rows[0] == other)
        ok("write mode appends state history", len(json.load(open(os.path.join(work, "_STATE/demand-probes.json")))["history"]) == 1)
    finally:
        srv.shutdown()
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"probe_tally self-test: {total - fails}/{total}")
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="probe_tally.py", description="Read demand-probe counts and move the backlog row with them.",
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--probe", default="mcp-connector", help="probe name (default: mcp-connector)")
    ap.add_argument("--base", default="https://good.arcs.care", help="API base URL (default: https://good.arcs.care)")
    ap.add_argument("--dry-run", action="store_true", help="read and report; write nothing")
    ap.add_argument("--self-test", action="store_true", help="assert the argv contract on synthetic input")
    args = ap.parse_args(sys.argv[1:] if argv is None else argv)
    if args.self_test:
        return self_test()
    return run(args.probe, args.base, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
