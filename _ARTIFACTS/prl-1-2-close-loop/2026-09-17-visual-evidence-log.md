# PRL lead-flow — visual evidence log (2026-09-17)

_Live screenshots captured this session via claude-in-chrome against Todd's Zapier + the Sugar sandbox (prlresinstest). Read-only, sandbox only, prod never touched. Note: in this setup the browser screenshots render inline in the session but do not export to standalone image files, so this log is the durable written record; re-capture with a taller window when files are needed._

| # | Surface (URL) | What it showed | Backs the finding | Time |
|---|---|---|---|---|
| 1 | Zapier Zaps list (`/app/zaps`, owner TH) | Toggle states: **"Tidio leads to SugarCRM (Deduplicate + Append)" ON**; **old "Tidio leads to SugarCRM" OFF**; "Stale leads SLA check (4h+)" OFF; "Send PRL website chatbot lead emails to Gmail" OFF | Live Zapier state matches intended; old zap OFF = no double-leads | ~16:00 |
| 2 | Zapier Zap History (`/app/history`) | **"Tidio leads to SugarCRM (Deduplicate + Append)" — Successful, Sep 01 02:41pm, 7 tasks**; a **Sep 17 02:40pm run "Delayed" (6 tasks)**; header banner **"1 held Zap run, held until November 12, 2026"** | 9/1 lead flowed end-to-end; today's lead stuck; account task-limited | ~16:05 |
| 3 | Zapier run detail (dedup zap 376827315, 9/17 run) | Step 1 "Tidio - Contact Sent From Bot" fired (2026-09-17 14:40:18); Step 2 "Code - Process State and Name" ran; delay on a downstream step | The 9/17 run started but stalled downstream (never reached Sugar) | ~16:08 |
| 4 | Sugar sandbox lead (`#Leads/db056406...`) | Lead "sales rep", Location CT, Office Phone 5555555555, **Assigned to Lynn Winston**, Unconverted | Routing/assignment works: the 9/1 lead got a real rep | ~16:12 |

## Cross-check against the API (definitive, text-evidence)
- `GET /rest/v11/Leads?filter[lead_source]=Chatbot` returned ONLY the 9/1 lead (id `db056406-a634-11f1-a2ed-02309379545d`), `assigned_user_name: "Lynn Winston"`, status New, **`description: "Chatbot Lead"`** (NOT a transcript), date_entered 2026-09-01. No 9/17 lead exists -> the Delayed run never delivered.

## Still needs a visual "after" (gated)
The transcript-populated lead + the full end-to-end flow (fresh chat -> zap -> Sugar within seconds) require Task C built + the Zapier plan upgraded (real-time). Capture protocol: taller window, before/after of the lead's `description`/Notes, saved when the tooling exports files.
