# Mercury pitch-us bundle

A two-surface counterpart micro-site for Mercury's "Open Call for Founders / Founding Teams" role, built
on the reusable pitch-us bundle IA (opportunity surface + operator surface, one SSOT, projected).

## Live (deployed, noindex, unlisted-by-URL)
- **The pitch (opportunity):** https://mercury.arcs.care/
- **The operator (why Zach):** https://mercury.arcs.care/operator

Both carry `<meta name="robots" content="noindex, nofollow">` plus a host-level `X-Robots-Tag` noindex
header. Reachable only by direct link.

## The opportunity (what the pitch argues)
Mercury already holds the money and just shipped the agent that acts on it (Command). The next layer is an
**Opportunity-Cost Engine on Command**: a human-approved intelligence layer that prices the cost of every
idle dollar in real time, computes runway under scenarios as a first-class output, and opens the untouched
spend-timing surface, monetized by moving deposits into Mercury Treasury. Reframed off the killed
"autonomous CFO / investment bank" framing (Command already auto-sweeps to yield, and that framing is
regulatory-infeasible under a partner-bank model) onto the genuinely unbuilt intelligence residue. The
pitch's own meta-proof: it was built by running that exact opportunity-cost discipline on its own creation.

## Files
| File | What it is |
|---|---|
| `pitch.html` | The opportunity surface (wing chassis). Read-at-any-depth + PRESENT mode. |
| `operator.html` | The operator surface (blacksmith fork): the seam, the domain-match, live proof. |
| `pitch-memo.md` | **The SSOT.** The pages project this and add no claims of their own. Now enriched with the sourced record (§11–§12). |

## SSOT and re-projection
`pitch-memo.md` is the single source of truth. The surfaces are projections; edit the memo, then re-stamp.
The operator surface projects Zach's blacksmith operator record re-pointed at Mercury's Command/MCP world.

## Honesty rails held
- Zach is the **operator-builder with regulated-capital fluency**, not a career treasurer. ARCS on Claude
  + a custom MCP server is exactly Mercury's Command/CLI/MCP ask; Grayscale ($7B SEC/FINRA) is why yield
  claims survive compliance.
- The pitch credits, up front, that Command already auto-sweeps and rebalances Treasury; it pitches only
  the unbuilt intelligence on top.

## Before you send it  ⚠️ action needed
- **Three `[citation pending]` markers are live on the pitch page** (§06 evidence base): the $5.2B Series D,
  the OCC conditional charter, and the four-years-GAAP-profit figures. These are real and now sourced in
  the memo (§11), but the deployed page was stamped before the enrichment. **Re-stamp `public/mercury.html`
  from the enriched `pitch-memo.md`** to clear the markers before this goes to a human.
- Verify Command's "rebalance treasury funds" autonomy depth with a live product test (the pitch flags this).
- File the ex-ante receipt so the loop can close when they respond.

## To update or take down
- **Update:** edit `pitch-memo.md`, re-stamp `public/mercury.html` (or `-operator.html`), commit, merge.
- **Unpublish:** remove the four `public/mercury*.html` files (or the `next.config.ts` mercury rewrite) and
  merge; the subdomain then falls through to the default page.
