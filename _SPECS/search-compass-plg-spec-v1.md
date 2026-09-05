---
title: Search Compass · end-to-end spec v1
status: DRAFT for Zach's review · 2026-09-05
supersedes: nothing (first spec; the working tool is jobs.arcs.care, shipped 2026-09-05)
siblings: _SPECS/profile-scan-spec-v1.md · runtime/specs/target-role-scan.json · runtime/specs/forge-triggers.json
---

# Search Compass

> Size the search before you invest. A job search rendered as an instrument, not a job board.

Sibling of the Question Compass: the same promise (an honest instrument that scaffolds your own judgment and never decides for you), pointed at one high-stakes, slow-feedback decision most people make three or four times in a life: where to aim a job search and where to spend the effort. Same PLG posture: free, sober, a mindset filter rather than a lead magnet. The people it serves see the value in sixty seconds; the people who want it to apply to 400 jobs for them bounce, and that is correct.

## 1. What exists today (the seed)

Working, single-tenant, admin-gated at jobs.arcs.care (PRs #283 to #285):

| Piece | State |
|---|---|
| Ingest | LinkedIn alert digests via Gmail, parser committed, scheduled weekday sweep |
| Score | Rubric as data (8 dims, gates, bands, tiers); JD read before scoring; assessment line; ATS class; hiring-manager kind |
| Board | Filters, sort, date range, swipe left/right with why-tags, score anatomy, undo, manual add, cap |
| Instruments | Profile Scan, Target Scan, Role Scan (profile x target on one posting), same HUD grammar |
| Forge | Light tier on a right swipe (resume cut, tailor notes, red-team, hiring-manager, contact, kintsugi, landing page staged); full tier gated on a human reply |
| Rules | forge-triggers.json applied by the swipe route, asserted by an eval (54 checks green) |
| Store | Prisma on Supabase: JobOpportunity, JobSwipe, ForgeRun, JobBoardSetting; pipeline token for writers |

What it is not yet: multi-tenant, self-serve, source-pluggable, metered, or reachable without an admin email.

## 2. Users and the job to be done

- **The seeker** (primary, PLG). Senior enough that the search is expensive and the wrong role is a two-year mistake. Wants to know where to aim and which of forty alerts deserves a real cut. Does not want a bot applying for them.
- **The counterpart** (secondary, per engagement). A recruiter or hiring manager who receives a forge page or a tear sheet. Never a tenant; a reader with a gate.
- **The coach** (later). Runs the instrument for a client. Multi-seat, not in v1.

The job: turn a stream of postings into a ranked, evidenced, honest set of bets, and spend real effort only where the record compounds.

## 3. Onramps

Each onramp is written from the user's side: what they bring, what they get inside sixty seconds, what is stored, what is gated, and where it leads. Every onramp is complete on its own; none requires the next.

### O0 · Paste a posting (anonymous)
- **Bring:** a posting URL, nothing else.
- **Get:** a Role Scan of that posting against a *generic* senior-builder profile, clearly labeled as generic: the rubric ledger, the four threads, the verdict, and one line: "with your record this changes; add it in two minutes."
- **Stored:** the posting and its score, keyed to an anonymous session (same claim-on-sign-in mechanic as the Question Compass receipts).
- **Gated:** nothing. No email, no account.
- **Leads to:** O2 (add the record) or O1 (bring the stream). This is the wedge. It reuses the Role Scan page as-is, with the profile swapped for the default.

### O1 · Bring the stream (email)
- **Bring:** a LinkedIn alert email, forwarded to an ingest address, or a Gmail connection (OAuth, read-only, sender-filtered).
- **Get:** a seeded board within minutes: every job in the digests, deduped, unscored rows listed with an honest "why not scored yet," and the first scoring pass running.
- **Stored:** the opportunity rows under the user's tenant. Never the email body beyond what the parser extracts.
- **Gated:** magic-link sign-in (the forward address issues it; Gmail OAuth requires it).
- **Leads to:** O2, because scores against a generic profile are only half the instrument.

### O2 · Add the record
- **Bring:** a LinkedIn profile URL, a resume PDF, or the LinkedIn data export ZIP (the richest: positions, skills, endorsements, recommendations).
- **Get:** the Profile Scan (who you are, threads, flags lit not smoothed) and a Target Scan seeded from the archetype library, with the rubric weights shown and editable. Every existing score re-runs against the real record.
- **Stored:** the profile as structured fields plus evidence grades; the target spec as the user's own rubric file.
- **Gated:** sign-in. The record is the most personal thing in the system; it is never shown to anyone but the tenant, and the forge air-gaps it.
- **Leads to:** the board becoming the daily surface.

### O3 · Add sources
- **Bring:** company names or board URLs (Ashby, Greenhouse, Lever public boards), other alert senders (Indeed, Wellfound, Otta), or a one-off URL.
- **Get:** the same board, more streams, each row stamped with its source; a source list with poll windows and last-run.
- **Stored:** a Source row per feed; an IngestRequest row per run, so "run a search for last week" is a real action, not a filter.
- **Gated:** sign-in. Public boards are polled from their JSON endpoints, never scraped from HTML behind a login.
- **Leads to:** the board being complete enough to trust.

### O4 · Swipe and forge (the metered edge)
- **Bring:** a right swipe.
- **Get:** a forge run, visible stage by stage, ending in a resume cut graded against the record, tailor notes, a red-team pass, the hiring-manager read, the apply path, and a staged landing page.
- **Stored:** ForgeRun plus artifacts under the tenant.
- **Gated:** free to hold, metered to fire. Holding (board, scans, swipes, the queue) is free. Firing a cut costs a credit; the first N are included so the wedge is never a paywall. The cap is a cost bound the user sets.
- **Leads to:** O5 when a human on the other side responds.

### O5 · The counterpart loop
- **Bring:** a reply from the company, or a recruiter's req.
- **Get:** the full forge (reverse-listen, audience model, persona gauntlet, hosted page, two-tier tear sheet), the pre-call brief, the post-call close that scores the ex-ante bet.
- **Stored:** Counterpart and Reply rows; the recoil ledger.
- **Gated:** a recorded human reply. This is the one rule that never relaxes: no full forge without a human on their side.
- **Leads to:** the closed loop, which is the product's proof.

### Graceful degradation, everywhere
- No profile: score against generic, say so on every row.
- No JD reachable: row stays unscored with the reason; never a guessed score.
- No hiring manager found: kind is unknown, never a name.
- Source down: last-run and error shown on the source, rows untouched.
- Spend limit or cap hit: runs hold their place in requested order, nothing dropped.

## 4. Objects

```
Tenant        one per user; owns everything below
Profile       structured record + evidence grades + flags (from URL, PDF, or export)
TargetSpec    the user's rubric: archetypes, quads, dims+weights, gates, bands, tiers (defaults from the library)
Source        {type: linkedin_email | ashby | greenhouse | lever | indeed_email | wellfound_email | manual, config, poll_window, last_run, last_error}
IngestRequest {sources[], from, to, status, counts}        ← "run a search" is a row
Opportunity   {id, source, url, title, company, location, first_seen, seen_count, salary?}
Score         {opportunity, spec_version, dims, gates, composite, band, tier, assessment, jd_hits, ats, company_type, hm{kind,text}, contact, next_step, scored_at}
Swipe         {opportunity, direction, why?, at}
ForgeRun      {opportunity, status, tier: light|full, artifacts[], cost, notes}
Counterpart   {opportunity, kind: recruiter|hiring_manager|referrer, replied_at}  ← the gate for full tier
Ledger        {run, est_tokens, actual_tokens, credits}
```
Today's JobOpportunity carries Score inline; splitting them lets a re-score keep history and lets O0's anonymous scores claim into a tenant later.

## 5. Pipelines

- **Ingest.** One adapter per source type emitting Opportunity records. Email adapters share the Gmail path with a sender filter and a per-format parser. Board adapters call public JSON. An IngestRequest fans out to every enabled source for the window and records counts.
- **Score.** Reads the JD, scores against the tenant's TargetSpec, quotes JD sentences per differentiator (jd_hits), records ATS, company type, hiring-manager kind, apply path. Deterministic wrapper, one small-model call per row. Re-scores when the spec version changes.
- **Forge.** Light tier from a swipe; full tier from a counterpart reply. Blueprint stages are data too. Landing pages built from the Blacksmith base, staged, deployed only on approval.
- **Meter.** Estimate before, actual after, per run; credits debited on fire, never on hold.

## 6. Surfaces

Board (daily), Role Scan (per posting), Profile Scan (who), Target Scan with a calibration editor (weights, gates, archetypes; the eval re-runs on save), Sources (list, run, history), Forge page (public, air-gapped, human-approved hosting), Recruiter tear sheet (two tiers, passcode). All in the ARCS grammar, inline styles, one design system. Mobile is a first-class surface because swiping happens on a phone.

## 7. Auth, tenancy, safety

- Magic link per tenant (existing Auth.js). Admin allowlist retired in favor of tenant ownership; the pipeline token becomes per-tenant.
- Row-level tenancy in Prisma queries; RLS deny for anon and authenticated stays as the floor.
- Air-gap: the record never appears on a public page; forge pages carry claims graded against it, not the record itself. Scoring vocabulary never leaves the instrument.
- Honesty gates: never fabricate a listing, score, salary, or name; unknown is a valid answer everywhere; self-reported figures carry the grade.
- Sources: only email the user receives and public JSON boards. No login scraping.

## 8. Monetization

Free to hold, metered to fire. Board, scans, swipes, sources, and the queue are free. A forge cut spends a credit; a full forge spends more and needs a counterpart. First credits included. Coach seats later. The cost ledger is the pricing model's evidence, not a guess.

## 9. Phasing

| Phase | Ships | Eval |
|---|---|---|
| P0 (done) | Single-tenant board, three instruments, light forge, trigger spec | trigger eval green |
| P1 | IngestRequest + board button; Ashby/Greenhouse adapters; source registry; jd_hits in scores | a request from the board produces rows from two source types within one run |
| P2 | O0 paste-a-posting with a generic profile; anonymous claim-on-sign-in; per-tenant rows | a stranger gets a Role Scan in under 60 s with no account |
| P3 | O2 profile intake (URL, PDF, export ZIP) with evidence grades; calibration editor | every score re-runs on spec change; profile flags shown |
| P4 | Metering, credits, Stripe; cap as a spend control | ledger actual within 25% of estimate |
| P5 | Counterpart loop: reply recording unlocks full tier; tear sheet; recoil close | no full forge without a reply row |

Each phase carries its own eval before the next starts, and each is usable on its own.

## 10. Non-goals

Auto-applying. Scraping LinkedIn or any login-walled site. Ranking people. Any surface that decides for the user.

## 11. Decisions for Zach

1. **Name.** Search Compass is the working name (it already appears on the Target Scan pill). Confirm or rename.
2. **First onramp to build.** Recommendation: O0 paste-a-posting, because it is the PLG wedge, reuses the Role Scan page, and costs nothing per visitor beyond one score. P1's ingest request is the next most valuable for you personally.
3. **Forge hosting model.** One `forge.arcs.care/<slug>` path versus per-company subdomains. The spec assumes the path.
4. **Tenant model timing.** Whether P2 ships with real tenancy or with the admin gate still on and anonymous claim deferred.
