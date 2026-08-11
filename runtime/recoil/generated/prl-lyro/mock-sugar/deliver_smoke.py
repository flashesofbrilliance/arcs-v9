#!/usr/bin/env python3
"""Delivery smoke: run representative chatbot leads through the OAuth + Create-Lead loop
against a running mock-sugar (or a real sandbox). Stdlib only.

Payloads mirror the Zapier transform output (name split, phone_work, location_c FULL name,
lead_source=Chatbot, email->email1, description) across the three branches + the failure modes
the flow must survive. Exit 0 if every expectation holds, 1 otherwise.

Env: BASE (default http://localhost:8090)
On the -edda33 branch this can be fed by simulate_lead_e2e.py's payloads instead of the inline set.
"""
import json
import os
import sys
import urllib.request
import urllib.error

BASE = os.environ.get("BASE", "http://localhost:8090").rstrip("/")


def _post(path, body, token=None):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(body).encode(), method="POST",
        headers={"Content-Type": "application/json",
                 **({"Authorization": f"Bearer {token}"} if token else {})},
    )
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


# each case: (label, payload, use_auth, expect_status, expect_warns)
CASES = [
    ("A · knows grade · CT", {"account_name": "Acme Molding", "first_name": "Jane", "last_name": "Doe",
        "phone_work": "2035551212", "lead_source": "Chatbot", "location_c": "Connecticut",
        "email1": "jane@acme.com", "description": "Lexan 141 equivalent"}, True, 201, False),
    ("B · help choose · California (distribution)", {"account_name": "Hunter Ind", "first_name": "Sam",
        "last_name": "Lee", "phone_work": "6195550000", "lead_source": "Chatbot", "location_c": "California",
        "email1": "sam@hunter.com", "description": "outdoor PC, UV stable"}, True, 201, False),
    ("C · spec question · New York (split)", {"account_name": "IMI", "first_name": "Pat", "last_name": "Roe",
        "phone_work": "7185550000", "lead_source": "Chatbot", "location_c": "New York",
        "email1": "pat@imi.com", "description": "flame rating question"}, True, 201, False),
    ("abbreviation location_c (should warn)", {"account_name": "Acme", "first_name": "Jane", "last_name": "Doe",
        "phone_work": "2035551212", "lead_source": "Chatbot", "location_c": "TX", "email1": "j@acme.com"},
        True, 201, True),
    ("email not email1 (should warn)", {"account_name": "Acme", "first_name": "Jane", "last_name": "Doe",
        "phone_work": "2035551212", "lead_source": "Chatbot", "location_c": "Texas", "email": "j@acme.com"},
        True, 201, True),
    ("missing phone_work (should 400)", {"account_name": "Acme", "first_name": "Jane", "last_name": "Doe",
        "lead_source": "Chatbot", "location_c": "Texas"}, True, 400, False),
    ("no auth (should 401)", {"account_name": "Acme", "first_name": "Jane", "last_name": "Doe",
        "phone_work": "2035551212", "lead_source": "Chatbot", "location_c": "Texas"}, False, 401, False),
]


def main():
    st, tok = _post("/oauth2/token", {})
    if st != 200 or "access_token" not in tok:
        print(f"FAIL: token endpoint -> {st} {tok}")
        return 1
    token = tok["access_token"]

    ok = True
    for label, payload, use_auth, exp_status, exp_warn in CASES:
        status, resp = _post("/rest/v11/Leads", payload, token if use_auth else None)
        warns = resp.get("warnings", []) if isinstance(resp, dict) else []
        status_ok = status == exp_status
        warn_ok = (bool(warns) == exp_warn) if exp_status == 201 else True
        passed = status_ok and warn_ok
        ok = ok and passed
        mark = "PASS" if passed else "FAIL"
        detail = f"{status}" + (f" warns={warns}" if warns else "")
        print(f"[{mark}] {label:<44} -> {detail}")

    # --- real recognizer payloads (when normalize.py + simulate_lead_e2e are present, e.g. -edda33) ---
    rows = None
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # prl-lyro/
        import simulate_lead_e2e as SIM
        rows = SIM.build_payloads()
    except Exception as e:  # recognizer/harness not in this checkout -> inline cases only
        print(f"\n[skip] real recognizer payloads unavailable here ({e.__class__.__name__}); ran inline cases only.")
    if rows:
        print(f"\n-- real recognizer payloads ({len(rows)}) --")
        for row in rows:
            status, resp = _post("/rest/v11/Leads", row["payload"], token)
            warns = resp.get("warnings", []) if isinstance(resp, dict) else []
            passed = status == 201
            ok = ok and passed
            mark = "PASS" if passed else "FAIL"
            print(f"[{mark}] REAL {row['scenario'][:42]:<42} -> {status}" + (f" warns={warns}" if warns else ""))

    print("\n" + ("ALL GREEN — delivery loop verified off-cloud." if ok else "SMOKE FAILED — see above."))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
