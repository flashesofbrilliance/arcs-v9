# mock-sugar — local SugarCRM REST stub (dev loop)

A stdlib-only mock of Sugar's cloud REST, so we build + test the chatbot → Zapier → **Create Lead** flow
locally in OrbStack **without touching the cloud sandbox** (saves API quota + rate limits, keeps a fast/free
loop). Cost note: this is local compute, not LLM tokens — the token lever is keeping deterministic work in
code + the git SSOT, not this container.

## Run (OrbStack)
```
cd runtime/recoil/generated/prl-lyro/mock-sugar
docker compose up --build          # -> http://localhost:8090
```
Or without Docker: `python3 server.py` (needs nothing but Python 3).

## One-command smoke (no Docker needed)
```
./dev-smoke.sh
```
Boots the mock, runs `deliver_smoke.py` (OAuth + Create-Lead across branches A/B/C + the failure modes:
missing-required → 400, abbreviation/email → warnings, no-auth → 401), tears down, exits non-zero on any fail.
Run it before wiring the real sandbox — it proves the whole delivery loop off-cloud.

## What it enforces (mirrors the live-instance audit)
- Required: `account_name`, `first_name`, `last_name`, `phone_work`, `lead_source`, `location_c` → **400** if any missing.
- `email` supplied without `email1` → warned (Leads have no `email` column; write to `email1`).
- `location_c` not a full state name → warned (canonical = full names, not abbreviations).
- `status` defaults to `New`; `lead_source` defaults to `Chatbot`.

## Endpoints
| Method | Path | Purpose |
|---|---|---|
| POST | `/oauth2/token` | returns a mock access/refresh token (any creds) |
| GET | `/rest/v11/Leads/schema` | the required-field contract |
| POST | `/rest/v11/Leads` | validate + create (Bearer required) |
| GET | `/rest/v11/Leads` | list created leads |
| GET | `/healthz` | ok |

## Example
```
TOKEN=$(curl -s -XPOST localhost:8090/oauth2/token -d '{}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')

# good lead
curl -s -XPOST localhost:8090/rest/v11/Leads -H "Authorization: Bearer $TOKEN" -d '{
  "account_name":"Acme Molding","first_name":"Jane","last_name":"Doe",
  "phone_work":"203-555-1212","lead_source":"Chatbot","location_c":"Connecticut",
  "email1":"jane@acme.com","description":"needs a Lexan 141 equivalent"}'

# missing required -> 400
curl -s -XPOST localhost:8090/rest/v11/Leads -H "Authorization: Bearer $TOKEN" -d '{"first_name":"Jane"}'
```

## Where it plugs in
Point the **Zapier Catch Hook** (or the Tidio flow API-call node) at `http://localhost:8090/rest/v11/Leads`
during development. When the real scoped sandbox key lands, swap the base URL to the cloud sandbox — the field
contract is identical, so the transform doesn't change. Use `RATE_LIMIT` (compose env) to force 429s and prove
the retry/backoff path.
