---
title: Widen jobs.arcs.care sourcing beyond LinkedIn alerts
date: 2026-11-03
status: PARTLY BUILT (path 3 for existing lists; paths 1 and 2 wait on Zach's alerts)
---

# Widen jobs.arcs.care sourcing

**Goal.** Bring more fitting roles onto jobs.arcs.care (forward-deployed, applied AI, deployment strategist, product engineer, AI product) in NYC metro, remote US and local CT, including family-friendly employers. Every source must be ToS-safe.

**Three intake paths, cheapest first.**
1. **Email alert.** The site emails Zach a digest. The morning run reads it from Gmail and hands rows to `node scripts/jobs_sources.mjs --import <rows.json> --source <key>` (the path Fonzi uses). Claude never fetches the site.
2. **Public API or feed.** Only where the site offers one and robots allows it.
3. **Company list to ATS boards.** A published list of employers is read by a person or a permitted fetch. `scripts/bridge_index_scan.py probe` + `verify` resolves names to public Greenhouse, Lever or Ashby boards, which the existing adapters then poll every morning.

## Per source

Robots files were checked on 2026-11-03 with a plain fetch.

| Source | Path | Why |
|---|---|---|
| Indeed | 1, email alert | The public RSS feeds were retired and the ToS forbids automated access. robots allows some search pages, but the ToS still governs. Alert emails from `alert@indeed.com` (sender to confirm on the first digest). |
| ZipRecruiter | 1, email alert | Its partner API is for publishers only and the ToS forbids scraping. Alert emails from ZipRecruiter. |
| Wellfound | 1, email alert | It blocks fetches (bot wall), so no fetch, ever. Its job-match emails list role, company and link. |
| Lenny's Newsletter job board (lennysjobs.com) | 1, email alert; 3 by hand | robots.txt disallows `anthropic-ai`, ChatGPT-User, PerplexityBot and Google-Extended, so Claude must not fetch it at all. Zach subscribes to its alerts, or pastes company names he sees into a list file for path 3. |
| Techmeme jobs | 3 by hand | The jobs box on techmeme.com is a short sponsored list (about 10 employers, mostly media). Its outbound `/r2/` links are disallowed in robots. Low yield: add a name to a list file when one fits. |
| Mediagazer jobs | skip | Same box, almost all newsroom roles. `/jobs` returns 404. |
| Fortune / GPTW Best Workplaces for Parents | 3, **done** | `lists/gptw-parents.json` (2025 edition, 100 names) is already resolved. Re-run when the 2026 edition is published. |
| Fortune 100 Best Companies | 3, **done** | `lists/fortune-100-best.json`, complete. |
| Seramount 100 Best | 3, **partial** | Only 7 names are published openly (Top 10 press release). The full list is gated, so it stays partial rather than padded. |
| Comparably Best Companies for Parents, Best for Work-Life Balance | 3 by hand | comparably.com returns 403 to automated fetches, so no fetch. Zach copies the names into `lists/comparably-parents-<yr>.txt` and `lists/comparably-wlb-<yr>.txt`; Claude probes them. |
| Best Places to Work in Connecticut (Hartford Business Journal) | 3 by hand | Not fetched. Zach copies the winner names into `lists/ct-best-places-<yr>.txt`. Many CT winners use Workday or iCIMS, which have no public JSON board, so expect few hits (see Limits). |

## What was built (path 3 wired into the daily run)

The employer index (`_STATE/job-search/employer-index/index.json`, 133 verified boards from six best-workplaces lists, built 2026-09-11) was ingested once and never polled again. `scripts/jobs_sources.mjs` now also polls every board in that index whose `verify` is `ok`, through the same title, location and dedupe filters as the spec boards. The spec field `employer_index` in `runtime/specs/job-sources.json` names the file.

- Board count: Greenhouse 34 to 101, Lever 4 to 13, Ashby 33 to 70.
- Dry run on 2026-11-03: **52 new matching rows**, at least 33 of them from boards only the index lists (Abridge FDE, BetterUp Staff/Principal PM Forward Deployment, Clay deployment strategist and applied AI in NYC, Aledade, Datadog, Braze, Upstart, and others). Nothing was posted. The morning run (Step 3b) posts them, unchanged.
- Three index boards now return 404 (Bombora, Invoca, Philo) and are marked `verify: gone`, so they stop logging errors.

**Adding a list later:** save names one per line under `_STATE/job-search/employer-index/lists/`, then run
`python3 scripts/bridge_index_scan.py probe <file>` and `verify`, review any REVIEW or MISMATCH by eye, and merge the hits into `index.json` with a `lists` tag. The next morning run polls them.

## Not built yet (waits on Zach's alerts)

**Path 1, a general Gmail digest step.** Once the first Indeed, ZipRecruiter, Wellfound and Lenny's alert emails arrive, add one step to the "Jobs 8/31 - Autorun" task. For each sender, run `search_threads from:<sender> after:<watermark>`, write the rows to `forge-inputs/<source>-rows.json`, then `--import ... --source <key>`. That also needs a `SOURCE_KEY` entry per source in `jobs_sources.mjs`. Formats are not guessed here: the parser is written against a real digest, as the LinkedIn one was.

## Limits

- Path 3 only reaches employers on Greenhouse, Lever or Ashby. 256 list names (mostly Workday, SuccessFactors or iCIMS corporates) are unresolved. Workday's public `/wday/cxs/` endpoint is the next adapter if CT and Fortune corporates matter.
- Index boards are polled with the target-role filter, which is narrower than the bridge-lane filter they were built for. This is on purpose.

## Hardening rules (learned building this, 2026-11-03)

1. **Read the whole robots.txt, AI-agent groups included.** `User-agent: *  Allow: /` is not permission. lennysjobs.com allows `*` but disallows `anthropic-ai`, and a grep for the `*` group alone missed that. Check with `curl -s <host>/robots.txt | grep -inE -A3 'anthropic|claude|gpt|perplexity|google-extended|^user-agent: \*'`.
2. **A 403, a bot wall or a ToS ban means no fetch**, whatever robots says. Route the source to an email alert or a pasted list.
3. **Wire every resolved list into the recurring run.** The September index was ingested once and polled never. In 7 weeks, 3 of 133 boards went 404 and nobody noticed. New lists merge into `index.json`, which the morning run already polls, never into a one-shot pull.
4. **Mark dead boards, never drop them silently.** When the morning report shows the same board `ERR` on two runs, a session sets `verify: gone` and a dated `verify_note` (by hand: nothing automates this yet). `bridge_index_scan.py verify` re-checks the whole index. Run it when a list is added, and monthly.
5. **Write each parser against a real digest.** No email format is guessed. The Gmail step for a source is built only after its first alert email arrives.
6. **Route backlog rows through a catalogued tool.** The tool catalog does not index `scripts/*.mjs`, so a row whose `route.tool` names a `.mjs` file fails the JTBD graph gate. Name the wrapper that runs it (`scripts/jobs_wt.sh node ./scripts/<x>.mjs`) until the catalog learns `.mjs`.

## Zach's steps (Claude must not create accounts or enter passwords)

1. **Indeed:** sign in or create an account at indeed.com. Set job alerts for "forward deployed engineer", "applied AI engineer", "product engineer" and "AI product manager", each for New York, NY and for Remote. Choose daily email.
2. **ZipRecruiter:** create an account and set the same four alerts (New York, NY within 25 miles, plus Remote), daily email.
3. **Wellfound:** sign in, set role preferences (Product Engineer, Forward Deployed / Solutions, Product Manager, AI) and locations (NYC, Remote US), and turn on job-match emails.
4. **Lenny's job board:** at lennysjobs.com, subscribe to job alerts for Product and Engineering, NYC or remote.
5. **Comparably and CT Best Places:** open each current list in your browser and paste the company names, one per line, into the files named in the table above. Then tell a session "probe the new lists".
6. Make sure the alert emails land in the Gmail account the Gmail connector reads, and are not filtered out of the inbox.
7. When the first digest from each arrives, tell a session "build the Gmail digest step for <source>". It writes the parser against that real email.
