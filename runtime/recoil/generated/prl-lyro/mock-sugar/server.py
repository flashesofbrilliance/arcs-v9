#!/usr/bin/env python3
"""Mock SugarCRM REST endpoint for the PRL local dev loop.

Speaks just enough of Sugar's cloud REST shape to build + test the chatbot -> Zapier ->
Create Lead flow WITHOUT touching the cloud sandbox (saves API quota + keeps a fast, free
local iteration loop). Stdlib only -- no pip installs, runs in OrbStack.

Mirrors the field contract found in the live-instance audit (see INTEGRATION-DOSSIER.md):
  required: account_name, first_name, last_name, phone_work, lead_source, location_c
  email    -> written to email1 (Leads have no `email` column)
  location_c -> canonical is the FULL state name (not the 2-letter abbreviation)
  status   -> defaults to "New"

Endpoints (v11-ish, path-tolerant):
  POST /oauth2/token            -> {access_token, refresh_token, expires_in}   (any creds accepted)
  GET  /rest/v11/Leads/schema   -> the required-field contract
  POST /rest/v11/Leads          -> validate + create (Bearer required); 400 on missing required
  GET  /rest/v11/Leads          -> list created leads (dev introspection)
  GET  /healthz                 -> ok

Env:
  PORT        (default 8090)
  RATE_LIMIT  (default 0 = off) -> after N successful writes, return 429 to exercise retry/backoff
"""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

REQUIRED = ["account_name", "first_name", "last_name", "phone_work", "lead_source", "location_c"]
FULL_STATES = {
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut",
    "delaware", "florida", "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa",
    "kansas", "kentucky", "louisiana", "maine", "maryland", "massachusetts", "michigan",
    "minnesota", "mississippi", "missouri", "montana", "nebraska", "nevada", "new hampshire",
    "new jersey", "new mexico", "new york", "north carolina", "north dakota", "ohio",
    "oklahoma", "oregon", "pennsylvania", "rhode island", "south carolina", "south dakota",
    "tennessee", "texas", "utah", "vermont", "virginia", "washington", "west virginia",
    "wisconsin", "wyoming",
}

_LEADS = []          # in-memory store
_WRITES = 0          # successful-write counter (for RATE_LIMIT)
RATE_LIMIT = int(os.environ.get("RATE_LIMIT", "0"))


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, payload):
        body = json.dumps(payload, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length", 0) or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n) or b"{}")
        except json.JSONDecodeError:
            return None

    def _authed(self):
        return self.headers.get("Authorization", "").startswith("Bearer ")

    def do_GET(self):
        if self.path.startswith("/healthz"):
            return self._send(200, {"status": "ok"})
        if self.path.rstrip("/").endswith("/Leads/schema"):
            return self._send(200, {
                "module": "Leads",
                "required_fields": REQUIRED,
                "notes": {
                    "email": "no `email` column; write to `email1`",
                    "location_c": "canonical = full state name",
                    "status_default": "New",
                    "lead_source_new_value": "Chatbot",
                },
            })
        if self.path.rstrip("/").endswith("/Leads"):
            return self._send(200, {"records": _LEADS, "count": len(_LEADS)})
        return self._send(404, {"error": "not found", "path": self.path})

    def do_POST(self):
        global _WRITES
        if self.path.rstrip("/").endswith("/oauth2/token"):
            return self._send(200, {
                "access_token": "mock-access-token",
                "refresh_token": "mock-refresh-token",
                "token_type": "bearer",
                "expires_in": 3600,
            })

        if self.path.rstrip("/").endswith("/Leads"):
            if not self._authed():
                return self._send(401, {"error": "need_login", "message": "Bearer token required"})
            if RATE_LIMIT and _WRITES >= RATE_LIMIT:
                return self._send(429, {"error": "rate_limit", "message": f"exceeded {RATE_LIMIT} writes"})
            data = self._body()
            if data is None:
                return self._send(400, {"error": "bad_json"})

            missing = [f for f in REQUIRED if not str(data.get(f, "")).strip()]
            if missing:
                return self._send(400, {"error": "missing_required", "fields": missing})

            warnings = []
            # location_c should be a full state name (canonical); flag abbreviations/placeholders
            loc = str(data.get("location_c", "")).strip().lower()
            if loc not in FULL_STATES:
                warnings.append(f"location_c '{data.get('location_c')}' is not a canonical full state name")
            # email should land in email1
            if data.get("email") and not data.get("email1"):
                warnings.append("email supplied but not email1; write email -> email1")

            rec = dict(data)
            rec["id"] = f"mock-{len(_LEADS)+1:04d}"
            rec.setdefault("status", "New")
            rec.setdefault("lead_source", "Chatbot")
            _LEADS.append(rec)
            _WRITES += 1
            return self._send(201, {"record": rec, "warnings": warnings})

        return self._send(404, {"error": "not found", "path": self.path})

    def log_message(self, fmt, *args):  # quieter logs
        print(f"[mock-sugar] {self.address_string()} {fmt % args}")


def main():
    port = int(os.environ.get("PORT", "8090"))
    srv = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"[mock-sugar] listening on :{port}  (RATE_LIMIT={RATE_LIMIT or 'off'})")
    srv.serve_forever()


if __name__ == "__main__":
    main()
