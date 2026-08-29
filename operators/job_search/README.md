# Job-search front door — LinkedIn alert catcher

Turns LinkedIn job-alert emails into normalized, deduped **opportunity records** that the
target-role rubric (`_ARTIFACTS/target-role-scan-hud.html`) can score. This is the missing
"front door" of the pipeline: **ingest → [score] → size (recoil) → tailor → prep.**

## What's actually true (verified 2026-08-28 against the live inbox)

- There is **no custom Gmail label / committed scraper**. LinkedIn alerts simply arrive in the
  **inbox** from **`jobalerts-noreply@linkedin.com`** (~201 in the last 45 days). The "catcher" is
  that sender query, nothing more.
- Each email is a **digest** (`email_job_alert_digest`) carrying **multiple jobs** — the *subject*
  names only the top one (sometimes with salary), the *body* lists them all.
- The PLAIN_TEXT body is regular and parseable:
  ```
  Your job alert for <SAVED SEARCH> in <LOCATION>
  New jobs match your preferences.

  <Title>
  <Company>
  <Location>
  <N connections | This company is actively hiring>
  View job: https://www.linkedin.com/comm/jobs/view/<JOBID>/?<tracking…>
  ----------------------------------------
  <next job…>
  See all jobs on LinkedIn: …
  ```
  The `<JOBID>` in each `View job:` URL is the stable **dedupe key**.

## The flow (in-session, repeatable)

1. **Fetch** (Gmail MCP — the only non-committable step):
   - `search_threads` with query `from:jobalerts-noreply@linkedin.com newer_than:14d`
   - `get_message` for each hit with `messageFormat: PLAIN_TEXT`
   - dump to a JSON array → `_INBOX/linkedin-alerts-raw.json`:
     ```json
     [{"id":"<msgId>","date":"<iso>","subject":"<subj>","plaintextBody":"<body>"}, …]
     ```
2. **Normalize** (deterministic, committed):
   ```bash
   python operators/job_search/linkedin_alert_parser.py \
       _INBOX/linkedin-alerts-raw.json --out runtime/job-search/opportunities.jsonl
   ```
   → one opportunity record per unique job:
   `{jobid, title, company, location, url, alert_query, alert_location, source, first_seen_msg_id, first_seen_date, seen_count}`
3. **Score** (next build): run each record through the target-role rubric (hard gates → weighted
   dimensions → composite → band) → ranked **PURSUE / CONSIDER / PASS** shortlist. The `alert_query`
   field also tells you *which saved search* surfaced it — a signal to prune noisy alerts at the source.

## Test

```bash
python operators/job_search/linkedin_alert_parser.py --selftest   # validates the real digest format
```

## Making it standing (optional, later)

The in-session Gmail-MCP fetch is fine for batch runs. To make it autonomous, replace **step 1**
with either a **Gmail API cron** or a **Zapier zap** (the repo already uses Zapier for the PRL client)
that emits the same `_INBOX/linkedin-alerts-raw.json` shape — steps 2–3 stay identical.

> Placement note: this lives under `operators/job_search/`. It was authored on a website-design
> worktree branch; move it to `main` (or a dedicated job-search branch) to make it canonical.
