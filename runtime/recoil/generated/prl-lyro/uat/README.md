# PRL UAT / e2e QA automation — harness skeleton (authored 2026-08-18, not yet run)

Two Playwright scripts, zero LLM tokens in any run (dollar-compression: author once, run free).
First run WILL need selector debugging — the `// TODO(selector)` marks are honest placeholders,
not working values. Budget one short session (or a local human run) to green them.

## Setup (one-time, local)
```bash
cd runtime/recoil/generated/prl-lyro/uat
npm init -y && npm i -D playwright && npx playwright install chromium
```
No repo-level dependency added (lives in its own package.json here) — honors the
"no new deps without asking" rule by keeping this a standalone tool dir. ASK before
promoting it into the main package.json.

## Script 1 — `layer1_playground.mjs` (Lyro eval automation)
Drives Tidio -> Lyro -> Playground with the 80-case eval set x3 runs, writes `responses.json`
for the existing scorer. Playground does NOT burn the 50/mo Lyro quota (per TEST-PLAN).
- Needs a logged-in Tidio session: run once with `--login` to open a headed browser, log in
  manually, session saved to `auth-state.json` (gitignored — never commit it).
- Then: `node layer1_playground.mjs` -> paste/collect loop -> `python3 ../prl_lyro_eval.py --score responses.json`

## Script 2 — `staging_chat_e2e.mjs` (capture-flow UAT)
Opens the staging site (wfaprlredev26.wpenginepowered.com), waits for the Tidio widget,
runs a scripted conversation (name/email/phone/company/state from a fixtures file), then
polls Sugar sandbox via REST for the resulting lead and asserts fields (name split, location_c,
lead_source=Chatbot, dedup on second run with same email).
- QUOTA WARNING: each run burns a real flow execution + ~8 Zapier tasks + a ZoomInfo credit.
  This is an ACCEPTANCE script, not a CI loop — run deliberately, never on a schedule.
- Sugar check needs an API token: script reads SUGAR_URL/SUGAR_USER/SUGAR_PASS from env
  (sandbox zapier.chatbot user), uses /rest/v11_5/oauth2/token then /Leads?filter — same
  endpoints proven all day via the Zapier MCP.

## Fixtures
`fixtures.json` — one entry per acceptance case (the 4 planned: new-lead, dedup-repeat,
extra state CA, extra state NY). Edit data there, never inline in scripts.

## Definition of green
- Script 1: responses.json for 240 runs, scorer reports zero critical, no flaky.
- Script 2: all 4 fixtures pass field asserts; dedup case asserts record COUNT unchanged.
