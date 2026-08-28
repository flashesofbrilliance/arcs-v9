#!/usr/bin/env python3
"""sugar_bulk — build Sugar /rest/v11/bulk payloads and parse saved MCP results.

Tuition (2026-08-26): the 50-state routing sweep planned as ~150 sequential Zapier-MCP
calls collapsed to 11 once /rest/v11/bulk was discovered (12+ sub-requests per call);
the payloads and the result parsing were hand-built in throwaway heredocs four times
in one session. This mechanizes both halves.

The Zapier MCP is the transport (execute_zapier_*_action, selected_api SugarCRMCLIAPI,
action _zap_raw_request). This script only BUILDS the params JSON and PARSES the saved
results — it never talks to the network, so it is safe everywhere.

SANDBOX ONLY by default: emits prlresinstest.sugarondemand.com URLs. Pass --host to
override deliberately; the script refuses the production host without --i-mean-prod.

Usage:
  sugar_bulk.py creates leads.json            # [{fieldmap},...] -> bulk POST params
  sugar_bulk.py deletes ids.txt --module Leads  # one id per line -> bulk DELETE params
  sugar_bulk.py gets ids.txt --module Leads --fields assigned_user_name
  sugar_bulk.py parse result.txt              # saved MCP tool-result -> JSONL records
  sugar_bulk.py parse result.txt --csv f1,f2  # -> CSV on stdout

Output of creates/deletes/gets is the exact JSON for the MCP call's `params` field
(chunked into multiple payloads of --chunk sub-requests, default 12, printed one per line).
"""
import json, sys, argparse

SANDBOX = "https://prlresinstest.sugarondemand.com"
PROD_MARKER = "prlresins.sugarondemand.com"


def _payloads(reqs, host, chunk):
    for i in range(0, len(reqs), chunk):
        body = json.dumps({"requests": reqs[i:i + chunk]})
        yield json.dumps({"url": f"{host}/rest/v11/bulk", "method": "POST",
                          "body": body, "fail_on_errors": "false"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["creates", "deletes", "gets", "parse"])
    ap.add_argument("file")
    ap.add_argument("--module", default="Leads")
    ap.add_argument("--fields", default="id")
    ap.add_argument("--host", default=SANDBOX)
    ap.add_argument("--chunk", type=int, default=12)
    ap.add_argument("--csv", default=None)
    ap.add_argument("--i-mean-prod", action="store_true")
    a = ap.parse_args()

    if PROD_MARKER in a.host and not a.i_mean_prod:
        sys.exit("sugar_bulk: PRODUCTION host refused (pass --i-mean-prod only with explicit authorization)")

    if a.cmd == "creates":
        rows = json.load(open(a.file))
        reqs = [{"url": f"/v11/{a.module}?fields={a.fields}", "method": "POST", "data": r} for r in rows]
    elif a.cmd == "deletes":
        ids = [l.strip() for l in open(a.file) if l.strip()]
        reqs = [{"url": f"/v11/{a.module}/{i}", "method": "DELETE"} for i in ids]
    elif a.cmd == "gets":
        ids = [l.strip() for l in open(a.file) if l.strip()]
        reqs = [{"url": f"/v11/{a.module}/{i}?fields={a.fields}", "method": "GET"} for i in ids]
    else:  # parse: saved MCP tool-result file -> records
        raw = json.load(open(a.file))
        out = []
        for res in raw.get("results", [raw] if "results" not in raw else []):
            body = res.get("body", res)
            if isinstance(body, list):  # bulk response: [{contents: {...}}, ...]
                out.extend(item.get("contents", item) for item in body)
            elif isinstance(body, dict) and "records" in body:  # list response
                out.extend(body["records"])
            elif isinstance(body, dict):
                out.append(body)
        if a.csv:
            import csv as _csv
            cols = a.csv.split(",")
            w = _csv.writer(sys.stdout); w.writerow(cols)
            for r in out: w.writerow([r.get(c, "") for c in cols])
        else:
            for r in out: print(json.dumps(r, ensure_ascii=False))
        return

    for p in _payloads(reqs, a.host, a.chunk):
        print(p)


if __name__ == "__main__":
    main()
