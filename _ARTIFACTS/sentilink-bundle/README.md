# SentiLink pitch-us bundle

A two-surface counterpart micro-site for SentiLink's "New Leader / Pitch Us" role, built on the
reusable pitch-us bundle IA (opportunity surface + operator surface, one SSOT, projected).

## Live (deployed, noindex, unlisted-by-URL)
- **The pitch (opportunity):** https://sentilink.arcs.care/
- **The operator (why Zach):** https://sentilink.arcs.care/operator

Both carry `<meta name="robots" content="noindex, nofollow">` plus a host-level `X-Robots-Tag` noindex
header. They are reachable only by direct link; nothing indexes or links to them.

## The opportunity (what the pitch argues)
SentiLink should stand up a **Government Program Integrity** line: point the synthetic-identity engine it
already owns at the AI-industrialized identity fraud draining federal benefit programs. Same data moat, a
beachhead SentiLink already claimed before Congress (Maimon's July 2026 House Oversight testimony), a
buyer with acute budgeted pain, no fraud-first incumbent. Reframed off the killed "define agentic
identity" framing (that category is already owned by Prove/Socure/the card networks) onto SentiLink's own
onboarding surface plus the government beachhead.

## Files
| File | What it is |
|---|---|
| `pitch.html` | The opportunity surface (wing chassis). Read-at-any-depth + PRESENT mode. |
| `operator.html` | The operator surface (blacksmith fork): the seam, the domain-match, live proof. |
| `pitch-memo.md` | **The SSOT.** The pages project this and add no claims of their own. |

## SSOT and re-projection
`pitch-memo.md` is the single source of truth. The two HTML surfaces are *projections* of it: to change a
claim, edit the memo, then re-stamp the surface (do not hand-edit the page). The operator surface projects
Zach's blacksmith operator record, re-pointed at this role.

## Honesty rails held
- Zach is the **operator who stands up a regulated market**, working with SentiLink's fraud science, never
  the fraud scientist. Grayscale ($7B SEC/FINRA), ARCS (Claude + MCP), HIPAA health do the load-bearing.
- Axon appears only as government-**adjacent** shipped work (public-safety/law-enforcement tech), not as
  fraud or direct government-program experience.

## Before you send it
- **Pin the dollar citations.** The $100B+ program-fraud figures render with a visible amber
  `[citation pending: GAO/IG]` marker. Replace each with one hard, sourced number before the pitch goes to
  a human. This surface is honest about being provisional; a live pitch should not be.
- File the ex-ante receipt (what you predict happens) so the loop can close when they respond.

## To update or take down
- **Update:** edit `pitch-memo.md`, re-stamp `public/sentilink.html` (or `-operator.html`), commit, merge.
- **Unpublish:** remove the four `public/sentilink*.html` files (or the `next.config.ts` sentilink rewrite)
  and merge; the subdomain then falls through to the default page.
