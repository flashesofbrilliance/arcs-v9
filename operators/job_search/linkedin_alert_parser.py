#!/usr/bin/env python3
"""
linkedin_alert_parser — the front door of the ARCS job-search pipeline.

Turns LinkedIn "job alert" digest emails (from jobalerts-noreply@linkedin.com) into normalized,
deduplicated *opportunity records* that the target-role rubric can score.

DELIBERATE SCOPE: this is the committable, deterministic, offline-testable core. It does NOT touch
Gmail. The one non-committable step — pulling the emails — is done in-session via the Gmail MCP
(search `from:jobalerts-noreply@linkedin.com`, get each message as PLAIN_TEXT) and dumped to a JSON
array; everything downstream is this pure function. (There is no committed "catcher" beyond this;
the alerts simply arrive in the inbox from that sender — no custom Gmail label exists.)

INPUT  (a JSON array, one object per alert email):
    [{"id": "<gmail msg id>", "date": "2026-08-27T20:53:09Z",
      "subject": "<subject>", "plaintextBody": "<PLAIN_TEXT body>"}, ...]
OUTPUT (JSONL, one opportunity record per line, deduped by LinkedIn job id):
    {"jobid","title","company","location","url","alert_query","alert_location",
     "source","first_seen_msg_id","first_seen_date","seen_count"}

USAGE:
    python linkedin_alert_parser.py alerts-raw.json --out opportunities.jsonl
    python linkedin_alert_parser.py alerts-raw.json           # prints JSONL to stdout
    python -m pytest linkedin_alert_parser.py                 # (self-test via --selftest)
    python linkedin_alert_parser.py --selftest
"""
from __future__ import annotations
import json
import re
import sys

_DASH = re.compile(r"^-{8,}$")
_VIEW = re.compile(r"View job:\s*(\S+)", re.I)
_JOBID = re.compile(r"/jobs/view/(\d+)")
_ALERT_FOR = re.compile(r"Your job alert for\s+(.*?)\s+in\s+(.+)$", re.I)
_SKIP = re.compile(r"^(This company is actively hiring|\d+\s+connection|View job:|New jobs match|Actively recruiting)", re.I)
_STOP = ("See all jobs on LinkedIn", "Stand out and let hirers", "This email was intended", "See jobs on LinkedIn")


def canonical_url(u: str) -> str:
    """Strip LinkedIn's tracking querystring down to the stable /jobs/view/<id>/ canonical URL."""
    m = _JOBID.search(u)
    if m:
        return f"https://www.linkedin.com/jobs/view/{m.group(1)}/"
    return u.split("?", 1)[0]


def parse_alert_email(subject: str | None, body: str, msg_id: str | None = None, date: str | None = None) -> list[dict]:
    """Parse ONE LinkedIn job-alert digest email's plaintext body into a list of job records."""
    lines = [ln.rstrip() for ln in (body or "").splitlines()]

    alert_query = alert_location = None
    for ln in lines[:8]:
        m = _ALERT_FOR.search(ln)
        if m:
            alert_query, alert_location = m.group(1).strip(), m.group(2).strip()
            break

    # Isolate the jobs region: after "New jobs match…" (fallback: after the alert-for line) → first stop marker.
    start = 0
    for i, ln in enumerate(lines):
        if ln.lower().lstrip().startswith("new jobs match"):
            start = i + 1
            break
    end = len(lines)
    for i in range(start, len(lines)):
        if any(mk in lines[i] for mk in _STOP):
            end = i
            break
    region = lines[start:end]

    # Split the region into blocks on dashed separators.
    blocks: list[list[str]] = []
    cur: list[str] = []
    for ln in region:
        if _DASH.match(ln.strip()):
            if cur:
                blocks.append(cur)
                cur = []
        else:
            cur.append(ln)
    if cur:
        blocks.append(cur)

    jobs: list[dict] = []
    for b in blocks:
        url = None
        for ln in b:
            m = _VIEW.search(ln)
            if m:
                url = m.group(1)
                break
        if not url:
            continue  # not a job card (preamble/footer fragment)
        # Content = the non-empty, non-boilerplate lines BEFORE the "View job:" line → [title, company, location].
        content: list[str] = []
        for ln in b:
            s = ln.strip()
            if not s:
                continue
            if _VIEW.search(ln):
                break
            if _SKIP.match(s):
                continue
            content.append(s)
        if len(content) < 2:
            continue  # need at least title + company
        title, company = content[0], content[1]
        location = content[2] if len(content) > 2 else (alert_location or None)
        jid = _JOBID.search(url)
        jobs.append({
            "jobid": jid.group(1) if jid else None,
            "title": title,
            "company": company,
            "location": location,
            "url": canonical_url(url),
            "alert_query": alert_query,
            "alert_location": alert_location,
            "source": "linkedin-alert",
            "source_msg_id": msg_id,
            "source_date": date,
        })
    return jobs


def normalize(emails: list[dict]) -> list[dict]:
    """Parse many alert emails → deduped opportunity records (first-seen wins; seen_count tracked)."""
    by_id: dict[str, dict] = {}
    order: list[str] = []
    for em in emails:
        jobs = parse_alert_email(em.get("subject"), em.get("plaintextBody") or em.get("plaintext_body") or "",
                                 msg_id=em.get("id"), date=em.get("date"))
        for j in jobs:
            key = j["jobid"] or f'{j["company"]}::{j["title"]}'.lower()
            if key in by_id:
                by_id[key]["seen_count"] += 1
                continue
            rec = {
                "jobid": j["jobid"], "title": j["title"], "company": j["company"], "location": j["location"],
                "url": j["url"], "alert_query": j["alert_query"], "alert_location": j["alert_location"],
                "source": j["source"], "first_seen_msg_id": j["source_msg_id"], "first_seen_date": j["source_date"],
                "seen_count": 1,
            }
            by_id[key] = rec
            order.append(key)
    return [by_id[k] for k in order]


# ── self-test against the real 2026-08-27 digest format ───────────────────────
_SAMPLE = {
    "id": "test1", "date": "2026-08-27T20:53:09Z",
    "subject": "Wealth Management - AI Product Owner at JPMorgan - XML: up to $155K/year",
    "plaintextBody": (
        "Your job alert for chief of staff product OR ceo OR cpo fintech OR crypto in New York City Metropolitan Area\n\n"
        "New jobs match your preferences.\n\n"
        "Wealth Management - AI Product Owner, Financial Insights - Senior Associate\nJPMorganChase\nJersey City, NJ\n\n"
        "11 connections\nView job: https://www.linkedin.com/comm/jobs/view/4449436844/?trackingId=abc&trk=eml\n\n"
        "------------------------------------------------\n\n"
        "Sr Product Mgr - Consumer Lending\nBank of America\nNew York, NY\n\n"
        "4 connections\nView job: https://www.linkedin.com/comm/jobs/view/4459391668/?trackingId=def\n\n"
        "------------------------------------------------\n\n"
        "Senior Associate, Product Manager-Small Business Bank\nCapital One\nNew York, NY\n\n"
        "This company is actively hiring\nView job: https://www.linkedin.com/comm/jobs/view/4449454168/?x=1\n\n"
        "------------------------------------------------\n\n"
        "See all jobs on LinkedIn: https://www.linkedin.com/comm/jobs/search-results/?keywords=x\n"
        "This email was intended for Zach Harris\n"
    ),
}


def _selftest() -> int:
    jobs = parse_alert_email(_SAMPLE["subject"], _SAMPLE["plaintextBody"], _SAMPLE["id"], _SAMPLE["date"])
    fails = []
    if len(jobs) != 3:
        fails.append(f"expected 3 jobs, got {len(jobs)}: {[j['title'] for j in jobs]}")
    if jobs and jobs[0]["company"] != "JPMorganChase":
        fails.append(f"job0 company = {jobs[0]['company']!r}")
    if jobs and jobs[0]["jobid"] != "4449436844":
        fails.append(f"job0 jobid = {jobs[0]['jobid']!r}")
    if jobs and jobs[0]["url"] != "https://www.linkedin.com/jobs/view/4449436844/":
        fails.append(f"job0 url not canonical: {jobs[0]['url']!r}")
    if jobs and jobs[2]["company"] != "Capital One":
        fails.append(f"job2 company = {jobs[2]['company']!r} (skip-line handling)")
    if jobs and jobs[0]["alert_query"] != "chief of staff product OR ceo OR cpo fintech OR crypto":
        fails.append(f"alert_query = {jobs[0]['alert_query']!r}")
    # dedupe: same email twice → still 3
    if len(normalize([_SAMPLE, _SAMPLE])) != 3:
        fails.append("dedupe failed across duplicate emails")
    if fails:
        print("SELFTEST FAIL:")
        for f in fails:
            print("  -", f)
        return 1
    print(f"SELFTEST PASS ✓  parsed {len(jobs)} jobs, dedupe ok, urls canonical")
    return 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return _selftest()
    args = [a for a in argv if not a.startswith("--")]
    out = None
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
    if not args:
        print(__doc__)
        return 2
    with open(args[0], encoding="utf-8") as fh:
        emails = json.load(fh)
    recs = normalize(emails if isinstance(emails, list) else [emails])
    lines = "\n".join(json.dumps(r, ensure_ascii=False) for r in recs)
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(lines + "\n")
        print(f"wrote {len(recs)} opportunity records → {out}")
    else:
        print(lines)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
