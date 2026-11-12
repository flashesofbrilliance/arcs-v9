# Host prune list, DRAFT (2026-10-07)

Source: `runtime/specs/surface-catalog.json` (89 hosts, 287 routes) plus a repo-wide reference count per host. **Nothing has been changed.** This is a proposal for Zach to mark up.

**Limits, read first.** (1) There is no traffic data here: Vercel's analytics read path is broken (memory `vercel-web-analytics-not-enabled-arcs-v9`), so 'idle' below means 'old and unreferenced', not 'unvisited'. Age is the last commit touching the host's rows; 15 hosts share 2026-07-24, which looks like a bulk import date, so their true age may be younger. (2) A counterpart may still hold the link. Retire means a redirect or a 410, never a silent 404.

## A. Retire: gated behind the admin session (10 hosts)

These already 404 for everyone except Zach (`gate: admin session`), so they serve no counterpart today. Deleting them removes no visitor access; it only removes dead config. Lowest risk.

| host | title | last touched | days | refs in repo |
|---|---|---|---|---|
| ahmed.arcs.care | Ahmed Elsamadisi / Polyform AI - ARCS Brief | 2026-07-24 | 75 | 0 |
| danny.arcs.care | Danny Quick / Kiko — ARCS Pre-Call Brief | 2026-07-24 | 75 | 0 |
| jalaja.arcs.care | Jalaja Padma / theTrueAI – ARCS Pre-Call Brief | 2026-07-24 | 75 | 0 |
| joe-war.arcs.care | Recoil Report | 2026-07-24 | 75 | 0 |
| kelly-interview.arcs.care | Kelly Mullaney — Juniper Square | 2026-07-24 | 75 | 1 |
| labella.arcs.care | Steve LaBella / Tallin — ARCS Brief | 2026-07-24 | 75 | 0 |
| labelle.arcs.care | Steve LaBella / Tallin — ARCS Brief | 2026-07-24 | 75 | 0 |
| peter.arcs.care | Peter Espersen — ARCS Brief | 2026-07-24 | 75 | 0 |
| yuri-war.arcs.care | Recoil Report | 2026-07-24 | 75 | 0 |
| jeben.arcs.care | Louisville Brands × ARCS – The Thread Book | 2026-07-31 | 68 | 0 |

## B. Collapse or redirect: old counterpart pages (34 hosts in 15 families)

Public product pages for a counterpart engagement, 40+ days since last edit, 8 or fewer references. Proposal: keep each family's single 'one door' host and 301 the satellites to it. A family with no 'one door' host gets a call from you.

**yuri** (9)
- yuri-codex.arcs.care · One call, one belief that flipped, both sides of t · 58d · refs 2
- yuri-demo.arcs.care · Yuri · one door · 58d · refs 0
- yuri-diamond.arcs.care · Yuri · the diamond cut · one call, mapped moment b · 58d · refs 4
- yuri-ext.arcs.care · Yuri · one door · 58d · refs 0
- yuri-profile.arcs.care · Yuri · the profile read · 58d · refs 0
- yuri-receipt.arcs.care · Yuri Kleban · Receipt Close · Before and After · 58d · refs 2
- yuri-recoil.arcs.care · Yuri · one door · 58d · refs 0
- yuri-sample.arcs.care · Yuri · one door · 58d · refs 0
- yuri.arcs.care · Yuri · one door · 58d · refs 7

**scott** (8)
- scott-arcs-demo.arcs.care · ARCS × Parlance · Scott Demo · 47d · refs 1
- scott-attraction.arcs.care · Scott × ARCS – stated vs revealed · 47d · refs 1
- scott-codex.arcs.care · Scott · the recoil · 49d · refs 1
- scott-profile.arcs.care · Scott · the profile read · 49d · refs 3
- scott-receipt.arcs.care · Scott · receipt · 48d · refs 1
- scott-signal.arcs.care · Scott · the signal read · 49d · refs 1
- scott-teardown.arcs.care · Scott (Parlance) × ARCS – a teardown and a map · 47d · refs 1
- scott.arcs.care · Scott · one door · 45d · refs 8

**robin** (4)
- robin-codex.arcs.care · Two calls, one line, both sides of the coin · 61d · refs 3
- robin-profile.arcs.care · Robin · the profile read · 59d · refs 1
- robin-receipt.arcs.care · Robin Daniels · Receipt Close · Call 3 · 59d · refs 1
- robin.arcs.care · Robin · one door · 58d · refs 3

**joe** (2)
- joe-ext.arcs.care · Recoil Report · 75d · refs 0
- joe.arcs.care · HypeLab × ARCS – A Six-Month Decision Map · 75d · refs 2

**ahmed** (1)
- ahmed-ext.arcs.care · Ahmed · one read · 42d · refs 6

**ayesha** (1)
- ayesha.arcs.care · Ayesha × ARCS — good catching up · 75d · refs 0

**daniel** (1)
- daniel.arcs.care · Fractional × ARCS — a teardown and a map · 75d · refs 0

**kam** (1)
- kam-codex.arcs.care · One call, the bet I filed, and the machine that he · 54d · refs 1

**kiko** (1)
- kiko.arcs.care · Kiko × ARCS – a teardown and a map · 75d · refs 0

**louisville** (1)
- louisville.arcs.care · ARCS × Louisville · Home · 67d · refs 5

**omakase** (1)
- omakase.arcs.care · 物の哀れ /// MONO NO AWARE · 67d · refs 4

**rayan** (1)
- rayan.arcs.care · Rayan · one read · 57d · refs 0

**serialized** (1)
- serialized-teardown.arcs.care · Scott (scottwitt.cc) × ARCS – a teardown and a ser · 47d · refs 1

**thetrueai** (1)
- thetrueai.arcs.care · theTrueAI × ARCS – think first, ship true · 75d · refs 0

**vishal** (1)
- vishal.arcs.care · For Vishal Kapadia · Two Close Readings · 75d · refs 0

## C. Keep, no action

45 hosts: edited in the last 40 days, or gated by passcode, or tools/status/products, or referenced widely (resume 60, prl 26, jobs 17, resume-tailor 13, recruithaus 11).

*, app, arcs-field-scan, autopilot, blacksmith, brooks, build, chan, claritai, conduit, forge, forge-cut, fun, germinate, good, growth-ai, honest, jack-rain, jobs, julia, julia-ext, lewoof, lyndon-war, mercury, monolith, monstro, playground, prl, rain, recruithaus, resume, resume-tailor, rosetta-shell, saul, schriner, schriner-ext, scott-cut, sentilink, squad, status, success-academy, surfaces, todd-call, vico, wing

## D. Needs Zach's call before anything moves

- **Active engagements** per memory (Yuri Kleban, Ahmed Elsamadisi, Robin Daniels, Kam Palizban, Julia Trabulski, Joe Schriner, Todd Hotes, Brooks Thomas): do not retire a family while its person is in play. Tell me which are closed.
- **Already marked retired** in the catalog (7): chase-intro, chris-intro, chris, cj-brief, fanatics, growth-intel, token. Confirm each serves a redirect or 410 and not a bare 404.
- **Backlinks:** emails, LinkedIn posts and resumes may still link some of these. Grep covers only this repo.

## Mechanics if approved

1. One PR per tier. Remove the host rule from `next.config.ts`/`src/proxy.ts`, add the redirect, regenerate with `python3 scripts/surface_catalog_emit.py` (its `--check` is a CI gate and will fail on any mismatch).
2. The page files under `public/` move to `_ARCHIVE/` (reversible, in git), not deleted.
3. Vercel: remove the domain alias only after the redirect has been live a week.
4. One decision receipt per PR.
