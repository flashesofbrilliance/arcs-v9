# Brief trace: monday.com FDE take-home (RET / Maple Creek) vs submission-rc17.zip

Audited 2026-10-12. The brief was extracted with `pdftotext -layout` (747 lines; line numbers below are lines in that extraction, "L"). The ZIP was unzipped to scratchpad/zip and audited as shipped. I ran these from the ZIP: `./rfp e2e --provider mock --runs 1` (5/5 pass), `./rfp eval --provider mock` (14/18; Q5, Q6, Q8 and T3 fail) and several `./rfp ask --provider mock` probes. I did not run anything against Claude or live monday.com.

## A. Requirements extracted from the brief

| # | Brief loc | Requirement (short quote) |
|---|---|---|
| R1 | L5-6 | Timing: "Interview: 60 min (~30 min presentation & demonstration + Panel Q&A)" |
| R2 | L12-15 | "analyze ... design a strategic proposal, and build a working AI-powered proof of concept" |
| R3 | L28-29 | "Review all three [materials] before beginning" |
| R4 | L43-44 | Problem: RFPs "several hundred pages ... strict deadlines, deposits, and security requirements, and are frequently amended mid-cycle" |
| R5 | L56-58 | Expansion: "~250 seats across Business Development, Proposals, and Regulatory if the RFP pilot succeeds" |
| R6 | L68-70 | Elena: "owns bid/no-bid decisions and the win-rate mandate" |
| R7 | L72-74, L120-128 | Doug: "a dozen fields" (due date, Q&A window, bid deposit, proposal security, voltage/mileage/transfer capability, eligibility, evaluation weights) "on one page" |
| R8 | L125-126 | Doug: "the tracker — about fifty rows of milestones, deliverables, and owners ... fresh every cycle" |
| R9 | L89-90 | "slide decks rebuilt for each leadership review" |
| R10 | L132-137 | Doug as a "human search engine": "~180 internal questions", answers take "a day or two" |
| R11 | L144-146 | Nina #1: "every answer cites its source — the section and page" |
| R12 | L146-148 | Nina #2: "if the answer is not in the document, the system says so, plainly" |
| R13 | L152-153 | Nina: "Verbatim. Dates, dollar amounts, percentages ... No rounding, no paraphrase" |
| R14 | L160-162 | Sam: "document indexing and retrieval runs in our own environment"; "question patterns" not in a third-party service |
| R15 | L162 | Sam: "If a model call goes out, I want to know what's in it" |
| R16 | L162-163 | Sam: "my two-person team supports it ... keep the moving parts countable" |
| R17 | L167-170 | Doug: amendments "supersede specific sections"; never "a brand-new RFP" and never ignored |
| R18 | L170-172 | Doug: "same document twice — I don't want two trackers" |
| R19 | L174-178 | Elena success #1: "key facts are on a board the same day"; #2: "answers ... in minutes, with a citation"; #3: "Doug's team spends their time on bid strategy" |
| R20 | L182-184 | NOT wanted: "Don't build portal scraping" |
| R21 | L186-188 | NOT wanted: "nothing auto-submits ... nothing drafts binding proposal language without a human" |
| R22 | L190-191 | NOT wanted: "don't integrate with our document management system ... Hand the files to the system directly" |
| R23 | L196-197 | Doug's trust test: "If it catches that the deadline moved and the deposit changed, and it tells me where it says so" |
| R24 | L208-235 | Metrics: 15 days to "same day for key facts; ≤3 days for the brief"; 650 h to ≤150 h; Q&A in "Minutes, with citation"; misses 3 to 0; $1.6M to "≥50% recovery" |
| R25 | L250-251 | Part 1.1, Executive Summary: "the problem, the approach, the expected outcome" in one slide |
| R26 | L252-255 | Part 1.2, Pain/business case: "quantified value. Use their numbers, their language, and their success criteria" |
| R27 | L256-260 | Part 1.3, Architecture: "monday.com as the operational backbone"; "where the system runs, where the documents live, what (if anything) reaches external AI"; "how each stakeholder's stated constraints are honored"; "AI approach and why you chose it" |
| R28 | L262-265 | Part 1.4, Rollout: "pilot ... to all of RET's annual RFP cycles and the adjacent departments"; "success metrics aligned to what each stakeholder said"; "risk analysis"; "what you are deliberately not building, and why" |
| R29 | L267-268 | Part 1.5, Product Recommendations for monday.com |
| R30 | L272-274 | Format: executive, "be concise!"; Part 1 "approximately 15–20 minutes" |
| R31 | L284-285 | Grading lens: "A technically impressive build that ignores what the client actually said will score worse than a modest build that proves you listened" |
| R32 | L289-291 | Sample data: base RFP, one Amendment, the internal questions |
| R33 | L292-293 | "free monday.com trial account with whatever boards your design requires, and land your results there" |
| R34 | L294-296 | Live fresh question "through whatever path your design gives real users ... end to end" (repeated at L723-724) |
| R35 | L297-299 | Panel plays the client in character, "including the awkward ones" |
| R36 | L303-306 | Build outside monday and push in via "GraphQL API, the monday MCP, or a combination — be ready to defend the choice" |
| R37 | L309-310 | "inspectable system with distinct steps and state ... not a single mega-prompt" |
| R38 | L311-314 | "real code of your own": "data model, your API integration layer, and your system's core logic" |
| R39 | L315-318 | Python/TS etc.; "at least one AI model provider" |
| R40 | L319 | "runnable end to end and include appropriate error handling" |
| R41 | L321, L324-325 | Demo "~10–15 minutes with your code on screen"; code walkthrough "is not optional" |
| R42 | L326-327 | Explain "which parts of the scenario materials drove each design decision, and what you deliberately chose not to build" |
| R43 | L328-329 | Defend document processing: "trade-offs, and their failure modes" |
| R44 | L330-331 | Defend "schema and data-model choices" |
| R45 | L332-333 | Defend "query construction, pagination, rate/complexity handling, batching" |
| R46 | L334 | "prompt engineering approach and how you iterated" |
| R47 | L335-336 | "harden this for production ... limitations and failure modes" |
| R48 | L341-346 | AI-assisted dev: "Keep notes on how you used AI, including specific examples of prompts, iterations, and where AI was most or least effective" |
| R49 | L347-349 | "AI-accelerated does not mean AI-opaque" |
| R50 | L360-361 | Demo must cover "the solicitation package and the internal questions — including the panel's live question" |
| R51 | L368 | "Slides recommended for Part 1 (maximum 10)" |
| R52 | L369-372 | "make modifications ... run queries live"; "what you would do differently with more time" |
| R53 | L702-719 | Edge cases in the questions: Q5 union labor (not in RFP), Q7 contacting the ISO (§4.2 prohibits it), Q12 cost cap revised upward (§7.4 says no), Q1/Q2 (amended values), Q8/Q9/Q13/Q14 multi-figure answers |
| R54 | Checklist (e) + briefing-video.md L12 | "source/, exactly one presentation PDF, and README.md inside one ZIP" |
| R55 | Checklist (d) | "document setup and decisions in your README" |
| R56 | briefing-video.md L8-9 | "how you structure ambiguity, evaluate trade-offs, use the available data, and communicate your reasoning clearly" |

## B. Trace

| # | Req | Where satisfied | Status | Note |
|---|---|---|---|---|
| R1/R30/R41 | Timing | DEMO.md L1, L7 ("about 9 minutes") | PARTIAL | The demo plan runs 9 min, below the brief's 10-15 min. No time plan exists for the deck. The brief contradicts itself (~30 min total at L5 vs 15-20 + 10-15 at L357-359); nothing in the materials reconciles the two. |
| R4 | Core problem | Deck s1-s2 | MET | |
| R5 | ~250-seat expansion | Deck s10 ($86K ARR), s8 phase 3 | MET | |
| R6 | Elena owns bid/no-bid and win rate | Deck s3 row Elena | PARTIAL | Win rate never appears. The bid/no-bid brief (the "≤3 days" target) is not produced by the system. |
| R7 | Dozen key fields on one page | sync_boards.py L18-33 (14 facts); deck s4 | MET | The Q&A window close and voltage/mileage are inside §3.2 and §1.2 text, not separate fields. |
| R8 | 50-row response tracker | none in code (grep for "tracker"/"milestone" finds only a docstring in sink.py L3) | MISSING | It is not built, and it is not named as deliberately not built. It is part of the 650 h the deck claims to cut. |
| R9 | Leadership decks rebuilt each review | none | MISSING | Not addressed and not scoped out. |
| R10 | ~180 questions/cycle | live_questions.py L29 `items_page(limit: 100)` with no cursor | CONTRADICTED | The poller reads only the first 100 items. A cycle of ~180 questions overflows that, and later questions are never picked up. |
| R11 | Section and page cite | answer.py citations, e.g. "RFP Section 7, pp. 42–51, §7.1" | MET | Page ranges are section-level, which is the finest the RFP provides. |
| R12 | Say "not addressed" plainly | answer.py SYSTEM rule 2; Claude evals per deck s6 | PARTIAL | On mock, Q5 (union labor) returns `[answered]` citing §6.5 outage coordination. DEMO.md L92 says the mock is the fallback that "gives the same cited answer path". If the fallback is used, the Nina beat fails on stage. The draft refusal is also labeled status `not_addressed` ("Not addressed: ... Drafting ... is out of scope"), which mixes "RFP is silent" with "we refuse". |
| R13 | Verbatim figures | answer.py figure check; Q1 fast path returns verbatim text | MET | |
| R14 | Indexing/retrieval local; question patterns | Deck s5; store.py (SQLite) | PARTIAL | Retrieval is local (MET). But every question is sent to Anthropic and stored on the monday.com Questions board, which is the exact "question patterns in a third-party service" Sam named. Deck s5 lists "Never sent: RET's internal assessments" and does not state this tension. |
| R15 | Know what's in each model call | flightlog/model_calls.jsonl; deck s5 | MET | |
| R16 | Countable moving parts | 1,597 LOC of product, but the ZIP holds 129 files: 20 scripts, flight recorder, sims, hooks, 13 flightlogs, history.bundle | PARTIAL | ONBOARDING L123 adds that a laptop must stay awake to run the poller. That is a hidden moving part for a two-person team. |
| R17 | Amendments supersede | resolve.py; e2e; `ask "bid deposit"` cites 7.1 and A1.2 with "amended value governs" | MET | Shown for Amendment 1 only (see R19 #1). |
| R18 | Same document twice | store.py L67 content-hash dedupe; ONBOARDING step 6 | MET | |
| R19 #1 | Key facts on a board the same day a document lands | sync_boards.py L45-46 hardcodes `("rfp_maple_creek.txt", "rfp_maple_creek_amendment_1.txt")` | MISSING | The board path has no way to hand it a new RFP or Amendment 2 without editing code. The test bench (server.py build_db) accepts new documents but only into an in-memory DB, never monday.com. |
| R19 #2 | Answers in minutes with citation | Questions board + `./rfp poll` | MET | Subject to the R10 cap. |
| R19 #3 | Doug's team on bid strategy | Deck s7 (≥200 h of 650 h) | PARTIAL | Only extraction and Q&A are touched; the tracker and decks are not (R8, R9). |
| R20 | No portal scraping | Code has none | CONTRADICTED | source/README.md L69 claims "a daily portal-check stamp" lands on the boards. No code does this, and it reads as portal monitoring. Scraping is never named as out of scope in the deck, README or DECISIONS (it appears only in CONSTRAINTS B9 and snapshots). |
| R21 | No auto-submit / no drafting | answer.py DRAFT/VERDICT guards; deck s9 "Will not ... draft bid language, decide the bid" | PARTIAL | Drafting is covered. Auto-submit is not stated in any shipped material except CONSTRAINTS.md. |
| R22 | No DMS integration; hand files directly | Code has none | PARTIAL | Never stated as a deliberate non-build in the deck, README or DECISIONS. "Hand the files directly" has no user path (R19 #1). |
| R23 | Doug's test: deadline AND deposit, with where | DEMO.md L11; proof-of-one-answer.html (deadline) | PARTIAL | The demo shows the deadline. The deposit is only a parenthetical ("same pattern"). Doug named both. |
| R24 | Their metrics | Deck s2 table | MET | |
| R25 | Exec summary: problem, approach, outcome | Deck s1 | PARTIAL | Problem and outcome are there. The approach (monday boards, local search, AI selects cited clauses, rules resolve amendments) is absent from s1. |
| R26 | Business case quantified in their numbers | Deck s2, s7; README L76-81 | PARTIAL | The deck never converts hours into dollars and says "Cost to be agreed". The $800K arithmetic sits in the README, not the deck. |
| R27 | Architecture, data flow, constraints, AI approach and why | Deck s4-s5; DECISIONS D-600, D-MCP | PARTIAL | The data flow is good. The "why this AI approach" (select-not-generate, lexical search vs embeddings, why Claude) is not on the slide. The Sam tension in R14 is unstated. |
| R28 | Rollout, per-stakeholder metrics, risks, scope discipline with why | Deck s8, s9 | PARTIAL | The phases are fine. Sam has no success metric. The "not building" line (s9) omits portal scraping, DMS and auto-submit, and gives no "why". |
| R29 | Product recommendations | Deck s10 (3 items) | MET | |
| R31 | Modest build that proves listening | — | PARTIAL | See section C. The materials emphasize the harness over the client asks. |
| R32/R53 | Sample data and edge cases | data/*.txt identical to the brief; eval golden.json; mock eval: Q7, Q12, Q14 pass | MET (Claude, per logs) / PARTIAL (mock) | Mock fails Q5, Q6 and Q8. Claude results are not re-runnable here. |
| R33 | monday trial boards, results landed | sink.py, sync_boards.py; presentation/monday-*.jpg | UNVERIFIABLE HERE | Needs `./rfp doctor` and `./rfp sync` with the live token, then a check of the 3 boards. |
| R34/R50 | Live question via the user path | Questions board + poller; DEMO L12 | MET | The ≤60 s poll plus 3 s answer works, apart from the R10 pagination gap. |
| R35 | In-character awkward tests | sim/wargame.py; DEMO backups | MET | |
| R36 | GraphQL vs MCP, defended | DECISIONS D-MCP, D-SDK | MET | |
| R37 | Distinct steps, inspectable | answer.py pipeline; test bench provenance | MET | |
| R38 | Own data model, API layer, core logic | store.py SCHEMA, monday.py, sink.py, answer.py, resolve.py | MET | |
| R39 | Language and provider | Python; provider.py (Claude, local, mock) | MET | |
| R40 | Runnable E2E with error handling | Ran from ZIP: e2e 5/5 incl. timeout, garbage, wrong-figure and fake-citation faults; monday.py retries | MET | |
| R41 | Code on screen, not optional | DEMO.md L21 puts code in "Backups, only when asked" | CONTRADICTED | The brief makes code walkthrough mandatory. The demo plan makes it optional. |
| R42 | Why built / what not built | DECISIONS.md (rejected alternatives) | PARTIAL | The client's three exclusions (R20-22) are absent from DECISIONS. D-SCOPE (L127) claims a "Deadlines board and the Amendment Log" were kept, but neither exists in code (only Solicitations, Key Facts, Questions and Pilot Scorecard; sink.py L18). |
| R43 | Document processing and failure modes | DECISIONS D-600; parse.py; deck s8-s9 | MET | |
| R44 | Schema / data model | store.py L14-33 | PARTIAL | The schema is in code but not explained in the README or DECISIONS. |
| R45 | Query, pagination, rate, batching | monday.py retries and complexity pacing (MET) | PARTIAL | Pagination is absent: no cursor anywhere, `limit: 100/200` is hardcoded (live_questions L29, sink L113, demo_reset L11, sink L33 boards limit 200). No batching (one mutation per item) and no doc on it. |
| R46 | Prompt engineering and iteration | KINTSUGI K27, K38, K43; answer.py SYSTEM | PARTIAL | The evidence exists but is scattered. No README section collects it. |
| R47 | Production hardening and limits | Deck s8 "Next", s9; DEMO prepared answers | PARTIAL | The top-level README promises "limits" (L7) and source/README has no limits section. |
| R48/R49 | AI-use notes with prompt examples, most/least effective | snapshots/T+2h.md L60-65 (self-assessment); KINTSUGI | PARTIAL | No shipped file gives specific examples of the prompts used with the coding assistant. KINTSUGI is written in the assistant's voice ("my own scope guard"), which invites the "AI-opaque" probe. |
| R51 | ≤10 slides | PDF 10 pages | MET | |
| R52 | Modify live; more time | DEMO; deck s8 | MET | |
| R54 | ZIP: source/, exactly one PDF, README.md | ZIP root: README.md, START-HERE.txt, presentation/ (1 PDF plus 4 html, csv, 2 jpg), source/; 9.26 MB | MET | The PDF sits under presentation/, not the root. The size is close to the 10 MB cap. |
| R55 | README documents setup and decisions | source/README.md links out to ONBOARDING and DECISIONS | PARTIAL | The README opens with the "flight recorder", not the product. Its Layout table (L24) puts `presentation/` inside source/, which is wrong. It cites 5 files that do not ship: QUESTIONS.json, HYPOTHESES.md, plan.json, HANDOFF.md, .github/workflows/check.yml (DEMO L64 also cites check.yml). |
| R56 | Clear reasoning | how-we-decided.html (4,034 words) | MET | |

Other FALSE claims in shipped material:
- source/README L69: "What else lands on the boards (slide 4): a daily portal-check stamp; what Amendment 1 now owes ...; unanswered questions routed to the ISO's Q&A portal". No code implements any of these (grep for portal/remit/owes in .py finds nothing).
- Deck s4: "Documents board: Every RFP and amendment received". The board is named "RET · Solicitations" and only ever receives the two hardcoded files.
- README slide references are stale. "slide 4" for the proof of one answer: s4 has no proof. "slide 8" for the open questions for counsel: s8 is the plan, and no open-questions list is on any slide.
- index.html says "Five cards" and renders six.

Counts (52 trace rows): MET 24 · PARTIAL 21 · MISSING 3 (R8, R9, R19#1) · CONTRADICTED 3 (R10, R20, R41) · UNVERIFIABLE 1 (R33). Separately, the 4 FALSE claims listed above.

## C. Drift (scope creep), ranked by panel attention consumed

1. **The flight recorder / meta-harness.** source/README spends L9-42 on it before setup. It brings flight/, hooks, rubrics, grades, belief_before/after, JOURNEY, 13 flightlogs, predictions with Brier scoring and history.bundle. The brief asks for none of it. Panel reads this first.
2. **Proof-volume framing.** "3,072 combinations", "30,000 fuzzed sequences", war game, canaries, mutation tests, 48 KINTSUGI rows. Deck s6 is the densest slide. This is the very thing L284-285 warns against.
3. **Evidence-grade letters (A/B/D) on every figure, plus a legend.** They spend deck real estate on s1-s2, s6-s7 and s10.
4. **index.html, how-we-decided.html (4k words, 5 depth levels), build-log.html (build cost $173.29, four run modes), proof-of-one-answer.html with hashes.** That is four extra presentation surfaces for one requested PDF.
5. **Engineering-led-growth projection** (README L83-100): reuse curves for the next client. Not asked for, and labeled assumption.
6. **"What's next" proposals** (Brier scoring of bid calls, CRM integration). CRM is a new data flow, which cuts against Sam.
7. **Pilot Scorecard board, local Qwen mode, Haiku mode cost table.** Extra moving parts for Sam.
8. **explainer.mp4 beside the ZIP.** It cannot be submitted (one ZIP only), so it is wasted effort unless it gets used in rehearsal.

## D. Top 10 actions, ranked by grade impact (smallest concrete change)

1. **Add a document-intake path.** Make sync_boards.py ingest every `data/*.txt` (glob) instead of the two hardcoded names, document "drop the file in data/, run ./rfp sync" in ONBOARDING, and rehearse a live Amendment 2. This is Elena #1 and the awkward-panel test.
2. **Paginate the poller.** Loop on `items_page { cursor }` / `next_items_page` in live_questions.pending (and sink L113), or query only items whose State is empty via `items_page(query_params:)`. Be ready to explain it, since the brief lists pagination by name.
3. **Move code-on-screen into the main DEMO path.** Make answer.py retrieve → select → verbatim check → amendment attach a 2-min segment, and bring the demo to 10-12 min.
4. **Delete the false README line L69** (portal-check stamp, what Amendment 1 owes, routed to the ISO portal), and fix the stale slide refs (s4, s8).
5. **Add one "Not building, and why" line to deck s9 and DECISIONS:** portal scraping (Doug: it broke; pain starts after the PDF), DMS integration (Sam: fewer moving parts), auto-submit and binding drafting (Nina), the 50-row tracker and leadership decks (phase 2, or explicitly deferred).
6. **Fix the mock fallback for the Nina beat.** Either make mock return not_addressed on Q5 (union labor), or change DEMO L92 so the fallback for that beat is the test bench on Claude. Also give the draft refusal its own status ("Out of scope") rather than `not_addressed`.
7. **Add to deck s1 one line of approach,** e.g. "Rules resolve amendments; local search finds clauses; the AI only picks clauses; code checks every figure; results land on monday.com".
8. **State the Sam tension on deck s5:** "Questions themselves go to the AI provider and the monday.com board; the local-model mode keeps them in-house". Also add a Sam success metric to s8.
9. **Restructure source/README to lead with product, setup, data model, decisions and limits.** Move the flight recorder to the bottom. Add a short schema section (documents/clauses/effects tables) and an "AI-assisted development" section with 3 concrete prompts to the coding assistant and where it failed (point to K27, K38, K43). Remove the 5 phantom file references, and fix the Layout row for presentation/.
10. **Show the deposit in Doug's beat** (DEMO L11): open the Bid deposit item on screen, $75,000 to $100,000 per §A1.2. Then fix DECISIONS D-SCOPE, which claims a Deadlines board and an Amendment Log that do not exist.
