# PRL Resins Chatbot — Project Cold Start

> This is a standalone client build for Todd Hotes at PRL Resins (Polymer Resources Ltd),
> a ~$100M specialty resin manufacturer. It was spun out of the ARCS repo into its own folder.
> Read this whole file first. It is the single source of truth for the engagement.

## What this project is

A Phase 1 lead-capture chatbot for prl-resins.com. A visitor lands on the site, the bot
qualifies them (what resin/spec/application they need), captures contact info, and drops a
structured lead into the sales team's CRM plus an email notification. No AI formulation advice
in Phase 1 — it captures and routes to a human fast (Todd targets ~4-hour reply).

**Business context:** Todd has full budget discretion. This is a paid, kicked-off build
($1,552.51 paid July 24, 2026). Todd is a close friend as well as the client, so keep it sharp
and honest, not salesy.

## Tech stack

| Layer | Choice | Notes |
|---|---|---|
| Site | WordPress | Existing prl-resins.com; Josh set up a lower/dev environment |
| Chatbot | Tidio | Free account signed up; will pick a paid tier by volume |
| CRM | SugarCRM | Lead destination; access pending |
| Notifications | Email to sales manager | MVP routes all leads to the SM, who assigns by territory |
| No Zapier, no separate CS layer | | Bot → SugarCRM + email, direct |

## Current state (as of 2026-07-30)

**Done**
- Discovery complete (Todd answered the qualification questions himself, Jul 20)
- Branch-logic map finalized (v1.2) — the full conversation design
- Resin nomenclature integrated — bot can recognize PRL product families + competitor names
  (from PRL's Product Selection Guide 2025)
- Tidio build sheet written (v1) — node-by-node builder instructions
- Payment received

**In motion**
- Building the Tidio flow in the free account against Josh's lower environment
- Waiting on Tidio rep for pricing-tier options (by volume)

**Needed from PRL side**
- SugarCRM login / API access (to wire lead creation + field map)
- GitHub repo + collaborator access (Todd's org account; add Zach's personal account)
- SM to answer 4 open dependencies (below)

## Open dependencies (blocking full build, not the rough-in)

1. **Exact field set** — required vs optional, from the SM's discovery/application form
2. **Territory map** — rep → states/regions, to turn on auto-routing (until then, all → SM)
3. **ICP / poor-fit criteria** — what makes a prospect ideal vs poor, to drive a soft `fit` tag
4. **FAQ content** — for the "something else" branch (optional)

## Files to bring into this folder

- `branch-logic-map-v1.2.md` — the conversation design (what the bot says, how it branches,
  what it captures, where the lead goes). THE spec.
- `tidio-build-sheet-v1.md` — click-by-click Tidio Flow instructions mapping the spec onto
  Tidio's builder primitives.
- `PRL-Product-Selection-Guide-2025.pdf` — resin families, nomenclature grammar, competitor
  cross-reference. Source for the recognition layer.

## Hard rules

- **Credentials never go in the repo or in chat.** Store PRL dev + GitHub + SugarCRM + Tidio
  logins in a password manager. The GitHub password arrived in plaintext email — treat it as
  exposed, change it on first login, and delete the credential emails.
- **Never enter credentials into any field on the user's behalf.** Hand the step to Zach.
- **Do not touch Todd's live WordPress or SugarCRM** until access is granted and the plan is
  confirmed. Build and test in Tidio + the lower environment only.
- **No em-dashes in anything Todd sees.** Short, plain, non-technical language.
- **Local dev is separate from any other project** — its own WordPress instance (LocalWP or
  Docker), its own folder, its own git.

## How to work here

- Keep the branch-logic map as the spec; keep the Tidio build sheet as the executable version
  of it. When one changes, reconcile the other.
- Version specs in the filename (`-v1`, `-v2`) on breaking changes; never overwrite history.
- When you finish a work session, update the "Current state" block above.

## First actions for a fresh session

1. Read the branch-logic map and the Tidio build sheet.
2. Ask Zach where he is: has SugarCRM/GitHub access landed? Is the Tidio flow started?
3. If still pre-access: keep building/testing the Tidio flow with a placeholder email sink.
4. If access landed: wire SugarCRM lead creation + the real notification email.
