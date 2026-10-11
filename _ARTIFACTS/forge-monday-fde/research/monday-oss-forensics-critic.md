# Completeness critique

## 1. Modalities and sources not run or read
- **Nothing executed.** No clone, no Sensei run, no stub adapter, no sandbox monday account, no hosted-MCP call. The report's core defects are source reads only, and it lists them as "test first" itself.
- **The take-home prompt is absent.** The ranking, the "fix one flaw" advice and the 6-step order are all ungrounded. If the take-home is built on Sensei or on another eval, the plan may be irrelevant.
- **Three truncations.** Developer docs, the architect lens and the last skeptic block were cut off. Lost corrections may contradict current text, yet the report uses verdict language.
- **"Their dev documentation" is ambiguous.** The request could mean GitHub and Hugging Face documentation. Nothing from HF docs or eval tooling (lighteval, smolagents, TRL, Inspect) was read. Nothing covered third-party MCP and agent benchmarks that include monday tasks. HF was only checked for a monday org.
- **Sources unread:**
  - monday engineering blog, product pages, changelog for Sidekick, Agent Factory and vibe
  - earnings calls and investor decks (monday is public)
  - npm download counts
  - the mcp repo's open PRs, CI status and maintainer response times
  - commit history of the mcp repo
  - the job description cross-read against the team's real stack
  - HF Spaces and community wrappers
- **Search-summary claims** (FAQ, data retention, bring-your-own model) are second-hand.

## 2. Claims unverified or in tension
- **"Verified" is defined as "a reader saw it in source", and the report mixes it with unrun inferences.** Fixture dropping, the fixed `'default'` model and the missing judge clamp are labeled verified. The Zod key-stripping behind the `model` key and the `rate_limit`/`retry` keys is admitted unrun. Shape 5 is rated "Gap" while the text says the config path is "plausible but untested".
- **Tool count arithmetic:** 33 + 54 + 2 = 89, but the text says "at least about 90".
- **Badge math:** the layer-to-weight mapping is never stated. The 70/80/50 caps only work if execution = 50, reasoning = 30 and self-improvement = 20. Verify `LAYER_WEIGHTS`.
- **"Harness not published"** rests on 404s for PR 729 and the run. A 404 in public API calls is also consistent with a private repo, so "unpublished" is not shown.
- **ATP ownership is unclear.** It sits in the "GitHub (org mondaycom)" table, but section 6 says it is not part of the official stack. Settle which org owns it before saying either.
- **"Nine-item menu" for the RL lens:** only four proposals are shown.
- **Issues #501, #496 and #508** are cited by title. Maintainer confirmation, label and fix status in v5.73.0 are unchecked.
- **"Dormant, no commits after 2026-03-22"** is a crawl snapshot. Branches, forks and other repos were not checked.
- **"monday's docs index never mentions it"** is absence from `llms.txt` only.
- **Time estimates** (90 min, 2 hours) and the n≥30 threshold are unsourced.
- **ARCS claims are unverified:**
  - existence and behavior of `provenance_lint.py`, `receipt_outcome_resolver.py` and `arcs-verb-eval`
  - the Drift Sentinel
  - the "2 of 247" capture figure, with a later cohort correction noted but unresolved

## 3. Over-confident language
- "Demo-grade", "not a qualification standard", "unadopted side project" and "AI-built" rest on repo metadata and commit messages.
- The gap ratings rest on absence from public GitHub, but monday's internal evals are invisible to a crawl. They should read "no public evidence of", not "Gap".
- "No HF presence" rests on a code search the report admits can miss things.
- "Fixtures never reach the judge/agent" is an unrun inference.
- The architect's risks mix local-server behavior (registration-filter read-only, apps mode) with the hosted server, whose source is unseen.

## 4. Could embarrass the candidate in front of a monday hiring manager
- **Biggest risk: Sensei is a `mondaycom` repo.** The HM, the team or the take-home author may have written it or may care about it. Calling it "AI-built", naming AgentTalent.ai and Nymeria, and noting the personal-Gmail `SECURITY.md` is petty. If any of it is wrong, it costs credibility. Drop the named third parties and the Gmail point. Frame it as "what an eval needs next".
- **ATP's hard-coded JWT secret and the ATP security claims** could land on someone's own project.
- **ARCS jargon** (Y-gate, Kintsugi, WRITE-LOCK, Golden Inchworm) is private vocabulary. A heavy ARCS plug can read as a pivot to self-promotion. The candidate's own "2 of 247" capture rate undercuts the calibration pitch if raised.
- **Unrun defect claims stated as fact**, if one fails to reproduce in front of the HM.
- **Drifting counts** (stars, versions, issue states, tool count) stated from a stale snapshot.

## 5. Falsifiers
| Conclusion | Evidence that would change it |
|---|---|
| Sensei is not monday's standard | A monday blog, docs or marketplace reference; a monday employee as main maintainer; newer commits on other branches or forks; the take-home built on it |
| Judge blind to fixtures | A logged judge prompt that contains them; a different code path (SDK, multi_judge); a newer release |
| Fixtures dropped on `openai-compat` | A stub endpoint that receives fixtures; adapter changes since the crawl |
| Model name fixed to `'default'` | Schema passthrough, or an env or CLI override |
| No clamp; judge outage becomes 0 | A run with a score of 15 and malformed JSON that behaves otherwise |
| Badge arithmetic | Different `LAYER_WEIGHTS` or thresholds |
| `multi_judge` is not a bias fix | A cross-model or randomized variant in the code |
| No HF presence | A `mondaycom`-affiliated HF org, a model card or a Space; the HF site search |
| Hosted-MCP gaps | Admin audit-export docs, an enterprise feature, or a trial-account probe |
| #501 and #496 matter | Issues closed as fixed or as user error; a maintainer reply |
| 13/13 routing eval is meaningless | A public or accessible harness; more evals in other plugins |
| Gap ratings | monday-owned eval suites, talks or posts; internal-eval references |
| ARCS fits | A run on a real trace that surfaces a defect the take-home rubric rewards. If it does not, the plug is noise. |