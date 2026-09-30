# Pre-mortem: launching honest.arcs.care ("Check it before you say it")

**Date:** 2026-09-29 · **Scope:** PR #649 (the `arcs-verb-eval` tool) and PR #655 (the honest.arcs.care page and route) · **Method:** assume it is three months after launch and the launch went badly; name each way it could have failed, what would catch it before it ships, and who owns it.

Status key: **caught** (a check exists and passed) · **open** (needs an action before or at launch) · **watch** (can't be fully prevented; needs a signal after launch).

| # | How it fails | What it looks like | Check that catches it | Owner | Status |
|---|---|---|---|---|---|
| 1 | The domain never serves the page | honest.arcs.care returns 404 after merge | Attach the domain to the Vercel project at merge; verify with `get_deployment(honest.arcs.care)` and `curl -I` showing 200 and the page title | Claude at merge | **open** (404 today: DNS points at Vercel, domain not attached) |
| 2 | The route catches more than it should | Another subdomain, or `/api`, starts serving the honest page | `src/proxy.ts` uses the one-to-one `SUBDOMAIN_MAP` path, which passes `/_next`, `/_vercel` and `/api` through; confirm a neighbour (resume.arcs.care) still returns 200 after deploy | Claude at merge | **open** (verify after deploy) |
| 3 | Dead links for visitors | "For builders" points at code in a private repo | Decide whether the standalone repo goes public; until then, the page must not link into arcs-v9 | Zach decides, Claude edits | **open** |
| 4 | The page and the tool disagree | The browser says Go where the command-line tool says Stop | Parity was checked by hand (23 of 23 cases). Needs a CI job that runs the Python self-test cases through `web/arcs-verb-eval.js` on every change | Claude | **open** (manual only today) |
| 5 | The name overpromises | Readers take "honest" to mean "true", and screenshot a Go on a false claim | Tagline "Check it before you say it" stays under the name; add one line saying what it checks (sources, nothing sneaking in, real pushback) and what it doesn't (whether a claim is true) | Claude, Zach approves copy | **open** |
| 6 | Someone pastes something sensitive | A private draft or client name typed into the box | Checks run in the browser; nothing pasted is sent. Page-view analytics count visits only. The page says "nothing you paste is uploaded"; keep that sentence exactly true on every future edit | Claude | **caught** (copy corrected when analytics was added) |
| 7 | A judge key leaks | An Anthropic key in the page, the repo, or a trace file | The judge runs only in the command-line tool and reads the key from the shell; the page has no judge call. Add a `leak_check` pattern for `sk-ant-` across `public/` and `tools/` | Claude | **caught** in code; **open** for the pattern |
| 8 | The judge quietly changes a verdict | An LLM score flips a Stop to Go | `judge()` works on a copy and never touches gates or fate; self-test proves stop stays stop with perfect scores | Claude | **caught** (judge self-test 8/8) |
| 9 | False Stops erode trust | Users hit "Stop" on list numbers or self-reported stats | Known from the LinkedIn dry run: list markers ("2.") and ledger-backed facts not in the post. Fix both before promoting the page | Claude | **open** |
| 10 | Design gate blocks the next kit page the same way | Every new kit page hits 20 findings on first commit | Per-file exemption precedent plus the seam entry in `_PATTERNS/kintsugi-visual-grammar-seams.md` (in #655): use `padding`, not `padding-block`; CLI flags read as em-dashes | Claude | **caught** (documented) |
| 11 | Name clash surfaces later | Another product called "Check It" or "Keep Me Honest" objects | One web search each found no conflicting product. Not a trademark search | Zach | **watch** |
| 12 | Merge without a receipt | Ship happens, the record doesn't | AGENTS.md "Receipts or it didn't happen": one `decision_receipt` row per merge (#649, #655) and one for the domain attach | Claude at merge | **open** |
| 13 | Nobody uses it, and we can't tell | Page is live, no signal either way | Vercel Web Analytics is on the page; check page views at 7 days before investing in the NFTT rollout | Zach | **watch** |
| 14 | #655 ships a stale copy of the page | honest.arcs.care shows an older layout than the tool's page | `public/honest.html` in #655 is a copy of `web/index.html` from #649. Regenerate it from #649's source right before merging #655 | Claude at merge | **open** (#649 has had layout changes since #655 was cut) |

## Launch order (hardened)

1. Fix #9 (the two false Stops) and add the #5 copy line on #649's page source.
2. Decide #3 (repo public or not) and adjust "For builders".
3. Regenerate `public/honest.html` in #655 from #649's page source (#14).
4. Merge #649, receipt. Merge #655, receipt.
5. Attach honest.arcs.care in Vercel (#1), then verify live and check a neighbour subdomain (#2), receipt.
6. Add the parity CI job (#4) and the `sk-ant-` leak pattern (#7) as a follow-up PR.
7. At 7 days, read analytics (#13) before starting the NFTT rollout.
