# Claims ledger: presentation/deck.html (RET RFP Intelligence), audited 2026-10-12

Repo: /Users/zharris/ret-rfp-intelligence (deck last changed 2c591f8). Read-only audit.
Client source of truth: the brief, which is NOT in the repo: /Users/zharris/Downloads/energy-rfp-take-home-v1.md.pdf
(pdftotext line numbers cited as "brief L###"). RFP text: data/rfp_maple_creek*.txt.

| # | slide | claim (short quote) | verdict | evidence | proposed honest wording |
|---|---|---|---|---|---|
| 1 | 1 | "Facts the same day. Answers in minutes." (headline) | REWORD | Not measured. Grade-D estimates only (E-est-facts, E-est-qa). KINTSUGI K31 already logged "same day (never measured)" as an error | "Aim: facts the same day, answers in minutes." |
| 2 | 1 | "Every answer shows its source" | HOLDS | answer.py L4-6 (verbatim figure gate, amendments attached by code); test_seams test_K19, test_K20. Refusals are not answers | - |
| 3 | 1 | Elena's three tests ("key facts are on a board the same day"; "answers in minutes, with a citation they can check"; "on bid strategy, not re-keying") | HOLDS | brief L174-177 (verbatim, lightly trimmed) | - |
| 4 | 1-2 | ~15 business days to bid/no-bid brief (A) | HOLDS | brief L210 | - |
| 5 | 1-2 | Internal answers take 1-2 days (A) | HOLDS | brief L94, L227 | - |
| 6 | 1-2 | Missed or near-missed windows: 3 in 24 months (A); target 0 | HOLDS | brief L230-233 | - |
| 7 | 1 | Pilot aims ≤1 business day, <5 min, 0 from unnoticed amendment (D) | HOLDS | evidence.jsonl E-est-facts / E-est-qa / E-est-missed, pre-registered 2026-10-10 | - |
| 8 | 2 | "From your Q2 2026 review" | HOLDS | brief L205 "RET Business Development Operations Review, Q2 2026" | - |
| 9 | 2 | ~650 h per intake cycle; target ≤150 h (A) | HOLDS | brief L215 | - |
| 10 | 2 | Target "key facts same day; brief ≤3 days" (A) | HOLDS | brief L210-212 | - |
| 11 | 2 | Target "minutes, with citation" (A) | HOLDS | brief L227 | - |
| 12 | 2 | ~$1.6M a year; target ≥50% recovery (A) | HOLDS | brief L235 | - |
| 13 | 2 | "Today it takes weeks, and a missed change can cost a bid" | HOLDS | brief L98-99, L111-116, L210 | - |
| 14 | 2 | "$0.0041 per question" (B) | HOLDS (caveat) | Recomputed: 1,068 ok Sonnet calls, tokens x cited $2/$10 per Mtok = $4.1459 / 1,019 answer calls = $0.00407. Caveat: the logged `usd` column sums to $4.2891 (= $0.0042/q, $0.76/cycle), a 3.5% internal inconsistency. Price is from a cached table, not verified live (E-price-sonnet55) | Optional: "about $0.004 per question" |
| 15 | 3 | "Four people told us what good looks like" | HOLDS (in character) | Discovery transcript, monday.com's FDE lead present (brief L103-199); Elena: "what success looks like" L174. These are brief personas. The presenter was not on the call, but "us" = monday.com holds in the fiction | Optional: "Four people told monday.com in discovery what good looks like." |
| 16 | 3 | Doug: "Show me it noticing the amendment... and it tells me where it says so." | HOLDS | brief L196-197, verbatim with ellipsis; meaning kept | - |
| 17 | 3 | Nina: "Every answer cited, numbers exact, 'not addressed in the RFP' over a guess" | HOLDS | Paraphrase, not in quotes except the quoted phrase, which is verbatim (brief L144-153) | - |
| 18 | 3 | Sam: "Search stays inside RET; know exactly what goes to the AI" | HOLDS | Paraphrase of brief L160-162. Note: the build runs on the builder's laptop, not inside RET (KINTSUGI K31) | - |
| 19 | 3 | System for Sam: "sends only the question and a few clauses" | REWORD | Every Claude call also sends a fixed system prompt (867 or 1,083 chars): answer.py L23-35; model_calls.jsonl `payload.system` on every Claude row | "sends only fixed instructions, the question and a few clauses" |
| 20 | 3 | System for Elena: "on monday.com boards your team already uses" | CUT/REWORD | FALSE for Elena's team. RET's 900 monday seats are Engineering PMO (brief L51-52). BD, Proposals and Regulatory are the ~250-seat *expansion* (L56-58). Doug's tracker is a spreadsheet (L89). The boards are new: monday_calls.jsonl `create board` x4 | "Puts facts and answers on monday.com, which RET already runs for engineering" |
| 21 | 3 | "Works out which text governs, cites both, and flags wording it cannot read" | HOLDS | resolve.py L4, L13, L48 (UNRESOLVED goes to a human); test_K18, test_K19; eval Q1 cites 7.1 + A1.2 | - |
| 22 | 3 | "Checks every figure word for word against the source" | HOLDS | answer.py L4-6, L133-135; test_K16_wrong_figure_trips_gate | - |
| 23 | 3, 9 | "logs every call" / "Every call logged" | HOLDS | provider.py L96-145 writes payload, response and usage for every call | - |
| 24 | 4 | Headline "It lives on the boards your team already uses." | REWORD | Same as #20 | "It lives in monday.com, where RET already works." |
| 25 | 4 | "14 facts (B): due date, deposit, security, weights, eligibility" | HOLDS | sync_boards.py L18-33: KEY_FACTS has 14 entries; E-facts | - |
| 26 | 4 | "answered in about 3 s (B) once picked up" | REWORD | Median 3.2 s over 5 passing live runs (e2e_runs.jsonl: 3.20, 3.24, 2.92, 3.49, 2.96). That figure is the poll step divided by questions. Pickup waits for a poll: default 60 s, minimum 30 (live_questions.py L67, L90). The repo's own E-poll says "about a minute" | "Picked up within a minute, then answered in about 3 s" |
| 27 | 4 | "Uploading a file twice changes nothing" | HOLDS | store.py L1, L67 (sha256 dedupe); scenarios.py L76 invariant V1, which also covers reformatted_duplicate; every live e2e run passes "sync 2 (must create nothing)". No dedicated unit test in test_seams.py | - |
| 28 | 4 | Amendment §A1.2 raises the deposit from $75,000 to $100,000 (A) | HOLDS | data/rfp_maple_creek_amendment_1.txt A1.2; brief L683-684 | - |
| 29 | 4 | "Live in monday.com, screenshots of the two boards" | UNVERIFIABLE HERE | monday_calls.jsonl shows live writes, but the screenshots can't be matched to the boards from the repo. To settle: open the RET boards and compare | - |
| 30 | 5 | Headline: "Nothing else goes to the AI." | CUT/REWORD | FALSE. Each request = system prompt (answer.py L23-35) + "Question: ... Clauses: [id] (doc, section, pages) text". Inspected model_calls.jsonl call e3aa767140. The refusal retry adds a further instruction paragraph (answer.py L253-257; 49 `answer_context` calls logged) | "The AI sees our fixed instructions, the question and a few clauses. Nothing else." |
| 31 | 5 | "~2,500 characters sent to the AI per question (mean 2,469)" | REWORD | Recomputed 2,468.6 = user message only (1,098 ok Claude calls). Counting the system prompt that is also sent, the mean is 3,342 | "~3,300 characters per question (fixed instructions ~1,000 + question and clauses ~2,500)" |
| 32 | 5 | "AI model (one call)" | REWORD | Fast path and scope guard make 0 calls (answer.py L171, L208-211; 4 of 18 golden pass with no key). The refusal retry makes 2 calls (L250-258) | "at most two calls; none when the answer is copied straight from the clause" |
| 33 | 5 | "Returns: which clauses, one sentence" | REWORD | Prompt requires "one or two plain sentences" (answer.py L34) | "which clauses, one or two sentences" |
| 34 | 5 | "Stays on the machine: RFP + amendments (files)"; monday.com box: "Not the full documents" | CUT/REWORD | FALSE. sync_boards.py L70-71 → sink.attach_once (sink.py L99-107) uploads the full RFP and amendment files to the monday Documents board. monday_calls.jsonl `upload file` x2 (2026-10-11T03:26) | "monday.com also holds the RFP files themselves (public documents), attached to the Documents board" |
| 35 | 5 | "Never sent: ... RET's bid strategy" | REWORD | Every question is sent verbatim to Anthropic. Sam defines "what questions our engineers are asking" as bid strategy (brief L158-160) | "Never sent: the full RFP, other solicitations, RET's internal assessments. Questions are sent, and logged." |
| 36 | 5 | "Never sent: the full RFP" (to the AI) | HOLDS | PAYLOAD_MAX 12,000 chars refuses the call (answer.py L200, L229-232); 400-word clause cap at ingest; test_K46 | - |
| 37 | 5 | Local model "slower, less accurate in our tests" | HOLDS | eval_runs.jsonl 2026-10-10T14:35 local 14/18; E-local-eval 11.2 s vs 1.7 s | - |
| 38 | 5 | "Search (finds ~8 clauses)" | HOLDS | answer.py L207 k=8, plus amendment expansion | - |
| 39 | 6 | Headline: "What broke is now tested." | REWORD | Absolute claim. KINTSUGI has 51 rows; test_seams.py has 19 tests. Several repairs are process or wording fixes with no test (e.g. K29, K31) | "We tried to break it. The failures that matter now have tests." |
| 40 | 6 | "18 of 18 sample questions we wrote, including four traps" | CUT/REWORD | FALSE attribution. Q1-Q14 are RET's own sample questions (brief L702-719; data/sample_questions.txt). Only T1-T4 were written by us (golden.json). 18/18 on the latest run HOLDS (eval_runs 2026-10-11T09:48:58) | "18 of 18: your 14 sample questions plus 4 traps we added" |
| 41 | 6 | "37 of 43 runs fully green (worst 15/18); 4 runs with no API key set excluded" | HOLDS | Recomputed: 47 Claude runs of the wave-1 set (including 6 early rows with set=null), 4 with gate "ANTHROPIC_API_KEY is not set" → 43 runs, 37 green, worst 15/18 | - |
| 42 | 6 | "Written blind by reviewers who never saw our tests: 16 of 20 and 17 of 20" | REWORD | The scores hold (evidence/blind/blind-set-*.json `score`). The authors were not human reviewers: a Claude Sonnet subagent prompted "You are a BLIND test writer", limited to the RFP, the amendment and the brief (~/.claude/projects/...mystifying-neumann.../subagents/agent-afbce9b8047cef8ed.jsonl, 2026-10-10T19:12Z). The repo never names a human writer | "Written blind by separate AI sessions that saw only the RFP and brief, never our tests: 16 of 20 and 17 of 20, before fixes" |
| 43 | 6 | "13 of 13 follow-ups each of you would ask next" | REWORD | Written by the builder with Claude as "anticipated objections" (JOURNEY.md L56; commit 0426b55, Co-Authored Claude). The persona tags (Doug, Nina...) are our attribution. The set was tuned on: 10/12 first, 12/12 after fixes (JOURNEY L60) | "13 of 13 follow-ups we anticipated from each of you (our set, after fixes)" |
| 44 | 6 | "Across every run: 17 of 25 runs fully green (worst 9/12)" | REWORD | eval_runs.jsonl has 28 Claude runs of golden_wave2.json. The 3 single-question runs at 17:06 (0/1, 1/1, 0/1) are left out. Over the 25 full-set runs, 17 green and worst 9/12 holds | "Across 25 full runs: 17 fully green (worst 9/12)" |
| 45 | 6 | "the set grew by one question after the early runs" | HOLDS | 12 → 13 from 2026-10-10T18:31 | - |
| 46 | 6 | "3,072 of 3,072 combinations of broken documents and a misbehaving AI, all handled safely" | REWORD | The "AI" is a mock provider with 6 scripted behaviours (scenario_runs.jsonl `mock_fault`: none/timeout/garbage/wrong_figure/fake_citation/refuse). No real model. 2,048 of 3,072 are "vacuous" (no answer produced), 1,024 load-bearing | "3,072 of 3,072 combinations of broken documents and a simulated misbehaving AI (6 scripted faults) handled safely; 1,024 produced an answer that passed the checks" |
| 47 | 6 | Reworded amendment read as "no change", "would have shown November 13"; test fails if it returns | HOLDS | KINTSUGI.md L29 (K17); test_seams.py L55 test_K17; mutate.py L17. Note: the rewording was a test-bench fault, not a real amendment | - |
| 48 | 7 | "about $0.73 of AI for a cycle of ~180 questions" | HOLDS | 180 (brief L135, L224) x $0.00407 = $0.732. With the logged usd column it would be $0.76 (see #14) | - |
| 49 | 7 | "The AI costs under a dollar a cycle" | HOLDS | #48 | - |
| 50 | 7 | ≥200 h of ~650 h, 50% confident (D), toward ≤150 h (A) | HOLDS | E-est-hours; brief L215 | - |
| 51 | 7 | "fund the rollout, as you proposed" | HOLDS | brief L177-178 | - |
| 52 | 7 | "Not measured yet: accuracy on your staff's own questions, review minutes, staff cost" | HOLDS | No such data in flightlog; consistent with #42 (the blind sets are not staff questions) | - |
| 53 | 8 | "~12 solicitations a year" | HOLDS | brief L115 | - |
| 54 | 8 | "a federal package is refused today, not guessed" | HOLDS | KINTSUGI K42 (USACE package, fail closed); test_K42 | - |
| 55 | 8 | Phase 3 teams: BD, Proposals, Regulatory | HOLDS | brief L56-58 | - |
| 56 | 9 | §7.4: cost cap "may not be revised upward"; flagged for estimators | HOLDS | rfp_maple_creek.txt §7.4 "Cost caps, once submitted, may not be revised upward" (brief L555-556); key fact sync_boards.py L23 | - |
| 57 | 9 | Control: "To the AI: only the question and a few clauses; to monday.com: answers and the clauses they quote" | REWORD | System prompt also goes to the AI (#30). Full RFP files also go to monday.com (#34) | "To the AI: fixed instructions, the question and a few clauses. To monday.com: answers, quoted clauses and the (public) RFP files." |
| 58 | 9 | "Refused with a reason, never answered as 'not addressed'" | HOLDS | answer.py L222-225 (K42); test_K42 | - |
| 59 | 9 | "Will not, by design: guess, draft bid language, decide the bid, contact the ISO, send the whole document to the AI" | HOLDS | Scope guards answer.py L202-213; test_K38; PAYLOAD_MAX. "Guess" is a design intent, enforced by the figure gate and the refusal path | - |
| 60 | 10 | "~250-seat expansion is about $86K (B) of new ARR at today's seat price" | REWORD | Arithmetic holds: 250 x ($310K / 900 = $344) = $86.1K (E-elg; brief L51-58). But "seat price" is RET's blended ARR per seat, not a list price. Grade B is wrong: every input is client data (A) and nothing was measured | "about $86K of new ARR at RET's current ~$344 per seat (ARR ÷ seats)", grade A-derived |
| 61 | 10 | "Usage analytics needs Enterprise" | REWORD / UNVERIFIABLE HERE | E-monday-analytics-gate: "Enterprise plan **or the API limit increase add-on**", cited from a Developer Center page viewed 2026-10-10. No capture in the repo. To settle: open assessment-lab-assignment.monday.com/apps/platform_api_analytics | "API usage analytics needs Enterprise or a paid add-on" |
| 62 | 10 | "so smaller accounts hit the daily cap blind" | UNVERIFIABLE HERE | Cap from docs: Free/Basic/Standard 1,000/day (docs/monday-platform.md L49). The repo marks the dev-account cap UNVERIFIED (L11, L211). "Blind" (no other usage signal) was never tested | "so smaller accounts cannot see daily usage in the dashboard before they hit the cap" |
| 63 | 10 | "Each item write costs 30,000 complexity points (B), far more than a read" | HOLDS | monday_calls.jsonl: create item 28/28, update item 30/30, write answer 57/57, create board 4/4 all `query: 30000`. Reads cost 10-376. (post update = 1,000, which is not an item write) | - |
| 64 | 10 | "Let AI columns cite sources" (implies they cannot) | HOLDS (doc-derived) | docs/native-agent-comparison.md L11, citing monday-platform.md §10.1. From docs, not measured | - |
| 65 | 10 | "one pilot opens the rest of the account" | HOLDS | brief L56-58 (expansion "if the RFP pilot succeeds") | - |

Tally (65 claims): HOLDS 43 · REWORD 16 (incl. #61, partly unverifiable) · CUT/REWORD, FALSE as written, 4 (#20, #30, #34, #40) · UNVERIFIABLE 2 (#29, #62).

## Highest-risk 5

1. **#34 + #57: the full RFP files are uploaded to monday.com, but slides 5 and 9 say "Not the full documents" and "only answers and the clauses they quote."** This is FALSE on the security slide built for Sam Ito. The proof is one click away during the demo: the Documents board's file column (sync_boards.py L70-71, monday_calls `upload file`).
2. **#30/#31/#19: "Nothing else goes to the AI."** Every request carries a ~1,000-char system prompt, and some get a second retry call. Sam asked to "know what's in it" (brief L162). The call log the deck points to shows `payload.system` on every row, so a panelist who opens it catches this at once. The 2,469 figure also leaves the instructions out.
3. **#42: "reviewers who never saw our tests."** The blind writers were Claude subagents, not people. Presenting AI-generated sets as independent reviewers is a provenance misstatement in an assessment that grades AI-use honesty (brief L337-349).
4. **#40: "18 of 18 sample questions we wrote."** 14 of the 18 are RET's own sample questions from the brief. The panel wrote them, so they will notice.
5. **#20/#24: "boards your team already uses."** The brief says RET's monday seats are Engineering PMO. BD, Proposals and Regulatory are the expansion target, and Doug runs a spreadsheet. Slide 10 itself relies on that fact ($86K expansion), so the deck contradicts itself.

Runners-up: #46 (the "misbehaving AI" is a scripted mock; 2/3 of combinations produce no answer), #35 (questions are bid strategy by Sam's own definition and are sent), #26 (3 s hides a poll of up to 60 s), #43 (persona follow-ups were written by us and tuned on).
