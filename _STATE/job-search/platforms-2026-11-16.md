# Jack & Jill and Fonzi, mined and graded (2026-11-16)

Zach: "we haven't mined either of them and refined my resume for both."

How it was read (no account changes):
- **Jack & Jill:** match emails in Gmail since the 2026-11-04 grading (`_STATE/job-search/jackandjill-2026-11-04.md` covers Cursor, OnCorps, Lunos and GovWell). The app was not driven. Its robots.txt allows ClaudeBot except the job-index pages, but its terms page renders only in a browser and is unread, so the email path was used.
- **Fonzi:** the connector, read-only: get_my_fonzi, get_my_profile, list_interview_requests, and search_companies with the Autorun's Step 3c queries.
- Each role was posted to jobs.arcs.care with source `jackandjill_match` or `fonzi`, and scored from its public ATS posting where one exists. A signed-in app page is never fetched.

Hard screen (Fonzi profile): base at or above $220K (flexible for a dream role), NYC metro or remote US, no sponsorship, no relocation.

## Already in motion on Fonzi
- **Patty, Senior Systems Engineer:** request accepted 2026-11-05, outcome "interviewing", $200K base offered in the request. Before booking the next step, apply the pre-call gate. A company that reached Zach through Fonzi is T1 (listed on the platform). The scheduler's email should come from Patty's own domain and pass DMARC (T2) before he sends anything beyond what Fonzi already holds.
- **Concourse, Forward Deployed Engineer:** company rejected (October). Closed, do not re-add.

## Ranking

| # | Role | Source | Board score | Verdict | Time |
|---|---|---|---|---|---|
| 1 | Obin AI, Forward Deployed AI Engineer (NYC in office, $200K to $300K) | J&J 11-16 | unscored (no public posting found) | PURSUE: Maybern seed fits | about 30 min |
| 2 | Genesis Computing, Forward Deployed Engineer (US remote, NYC hybrid) | J&J 11-09 | unscored (no public posting found) | PURSUE: Maybern seed fits | about 30 min |
| 3 | GovWell, AI Product Engineer (NYC hybrid, $160K to $260K) | Fonzi + J&J | 0.83 PURSUE | PURSUE (graded 11-04); apply once | about 2 hours (bundle) |
| 4 | Footprint, Forward Deployed Engineer (NYC in person, $170K to $205K) | Fonzi | 0.84 PURSUE | HOLD on pay: top of range is under the $220K floor | 10 min to decide |
| 5 | Perplexity AI, AI Strategist, Financial Services (NYC or SF) | J&J 11-10 | not posted (title outside the scan lanes) | CONSIDER: one stated gate to argue | 10 min to check |
| 6 | Brain Co., ML Engineer, Applied AI (NYC in office) | J&J 11-12 | 0.83 PURSUE | HOLD: the ML depth asked for is a real gap | none until decided |
| 7 | Patlytics, AI Engineer (NYC hybrid, $200K to $250K) | Fonzi | 0.62 CONSIDER | Lower priority | about 30 min |
| - | Guild.ai FDE 0.48, Arize FDE West 0.47 | J&J, Fonzi | PASS | Skip | - |
| - | Varick Agents, Senior FDE (SF in office, weekends expected) | J&J 11-08 | not posted | Skip: SF in office and pace | - |
| - | FLORA, Farsight, Smoke AI (AI Engineer, NYC) | Fonzi | unscored (no public posting found) | Read on Fonzi Talent before grading | 5 min each |

Elm AI (0.85), Concurrence Staff Applied AI (0.89), Ramp Applied AI and Klarity were already on the board from LinkedIn.

## 1. Obin AI, Forward Deployed AI Engineer
- **Need-to-have (per Jack's summary; the posting itself is unread):** production agents and retrieval, Python, cloud infrastructure, backend APIs; direct work with financial institutions; NYC in office. **Met or arguable:** ARCS covers agents, retrieval and evaluation; Grayscale covers institutional finance; Python at builder depth.
- **Nice-to-have:** credit-workflow domain knowledge (adjacent: regulated digital-asset products).
- **Insurmountable:** none stated. In-office NYC is fine (Zach, 2026-11-03).
- **Best:** early-hire FDE at a finance AI company, the closest match to the regulated-finance plus AI story; offer near $250K. **Base:** technical screen on cloud infrastructure decides it. **Worst:** they want a career backend engineer first.
- **Objections:**
  - "Cloud infrastructure depth?" Vercel, Supabase and Postgres in production. Name AWS or GCP as the gap and the plan to close it.
  - "One of the earliest hires: can you build alone?" ARCS is built solo, end to end.
- **Resume:** the Maybern cut (Technical Solutions Lead, Applied AI) fits as is.

## 2. Genesis Computing, Forward Deployed Engineer
- **Need-to-have (per Jack's summary; the posting is unread):** customer workflow discovery through integration, deployment and debugging, in hedge-fund, financial-services and pharma data environments. **Met:** Grayscale plus the Mañana discovery work plus ARCS.
- **Nice-to-have:** Snowflake (founders are early Snowflake alumni). Not met.
- **Insurmountable:** none.
- **Best:** remote or NYC hybrid FDE on a young data-agent product. **Base:** first call, then a data-stack technical round. **Worst:** Snowflake depth is the filter.
- **Objection:** "No Snowflake." Postgres in production; the warehouse layer is learnable. Say it plainly.
- **Resume:** the Maybern cut.

## 4. Footprint, Forward Deployed Engineer
- Fonzi lists $170K to $205K. Zach's Fonzi floor is $220K, flexible only for a dream company, team or role. Decide in 10 minutes whether this is one; otherwise skip. The board score (0.84) is fit, not pay.

## 5. Perplexity AI, AI Strategist, Financial Services
- **Stated gate:** 3+ years inside investment banking, PE, hedge funds, equity research or institutional asset management, plus front-office fluency.
- **Argument:** Grayscale is an institutional asset manager. Zach was its Product Lead (2024 to 2025) for private placements and exchange-traded products, which is about 1.5 years, short of 3. Treat this as an objection to answer in a short note, not a pass.
- **Best:** the domain argument lands; the strategy-plus-build profile is the fit. **Worst:** auto-screen on years in finance.

## 6. Brain Co., ML Engineer, Applied AI
- **Gap:** fine-tuning, distribution shift and multimodal modeling at ML-engineer depth. ARCS is an applied systems build, not model training. This is near insurmountable for an MLE title. Hold unless Brain Co. has a forward-deployed or product seat.

# Profile refinement drafts (not entered: Zach approves each change first)

## Fonzi profile (via save_profile, only on Zach's yes)
Current values were read 2026-11-16. Proposed changes:

1. **built**: replace "6,800+ commits, 1,900+ PRs merged with a human approving every one."
   with: "Over 7,000 commits and nearly 2,000 merged pull requests on a private repository, with a human in the merge loop."
   Why: the live counts are 7,133 commits on main and 1,993 merged PRs (2026-11-16). "Every one" is not provable, the resume skill bans it, and the repository is private.
2. **matchDayBio**: replace "built KPI and evaluation frameworks across three AI-enabled product lines"
   with: "researched three AI-enabled digital-therapeutics lines and recommended two for investment".
   Why: that is what the vetted master supports.
3. **rolePreference** (one value allowed): currently "AI Engineering". Option: "Forward Deployed Engineering". Fonzi's own requests so far were FDE (Concourse) and Systems (Patty). Zach's call; both fit his lookingFor text.
4. **salaryFloor** stays $220K unless Zach wants Footprint-range roles ($205K top) to appear. Fonzi says lowering the floor does not raise request volume, and companies anchor offers to it.

## Fonzi resume upload (via upload_resume, only on Zach's yes)
File: the Maybern cut PDF in the forge-maybern-principal-fde bundle (added in PR 2311). It is one page, its header reads "Technical Solutions Lead, Applied AI", the company is not named anywhere in the text, and its gates are green. That makes it a clean generic forward-deployed and applied-AI cut. Fonzi uses the upload to enrich the profile.

## Jack & Jill
Jack builds the profile from LinkedIn and edits it himself (emails of 2026-10-12 and 10-26 say so; each edit can be undone from Profile). The lever is the brief Jack searches against. Draft reply to Jack, for Zach to send himself if he wants:

> Jack, two adjustments to the search. Weight toward forward-deployed and applied-AI roles in regulated finance, healthcare and government, NYC hybrid or in office, or US remote. Skip San Francisco in-office roles and anything that expects weekend work. Base floor $220K. Also, I've attached a one-page resume that reflects how I want to be positioned.

Attach the same Maybern-cut PDF. Driving the app in Chrome waits on reading Jack & Jill's terms (browser-rendered) and on Zach's go.

# Adjacent title families (Dean Harris and Marcia Harris, 2026-11-16)

Sources: Dean's "Don't know if you have been looking under this job title?" and "Forward Deployed Creative Jobs", and Marcia's "Forward Deployed Creative (FDC)" (a screenshot). Dean's two emails are pasted AI search summaries that say "AI can make mistakes", so each named listing counted only after it was found on the company's own public board.

## Forward Deployed Strategist and Deployment Strategist: HOLDS (primary adjacent)
- **Need-to-have:** executive discovery, scoping, delivery through adoption and ROI, enough technical depth to work with engineers. **Met:** Grayscale, the Manana engagements, ARCS. The 2026-11-04 card already graded Cursor's FDS as PURSUE.
- **Insurmountable:** none for the family. Pay varies: Palantir Deployment Strategist ($110K to $170K per Dean's list) sits under the floor, while Context ($180K to $350K) clears it.
- **Board:** the scan's forward-deployed lane already matched these titles; 89 strategist rows were on the board, several already right-swiped. Added today: the Context board (its Forward Deployed Strategist is live on Ashby) and an AI Strategist pattern (Perplexity, Edra, Distyl, Thomson Reuters style titles).
- **Objection:** "Consulting pedigree?" Two decades of embedded engagements and a regulated launch stand in for a top-tier consulting badge; lead with outcomes.

## AI Strategist: HOLDS
- Same evidence as above, domain-specialized (financial services is common). Perplexity's needs 3+ years in front-office finance (see card 5).

## Forward Deployed Creative: SELECTIVE
- **Need-to-have (per Dean's summary):** hands-on generative image and video production (node-based tools such as ComfyUI), paid-ad creative under deadline, client workshops.
- **Met:** creative technologist with a studio-art degree, ran a video ad network (Selectable Media), design-first foundation. **Not met:** a current portfolio of generative-media production work. That is near insurmountable for production-heavy FDC roles.
- **Verified on a public board:** Newform (Ashby, NYC on-site; Dean lists $80K to $120K, under the floor). Google Flow's FDC ($183K to $265K per Dean) is on Google's own careers site, unverified here; it is the one FDC worth a 10-minute check. Hightouch, Magnific and Comfy Org have no matching public posting.
- **Verdict:** keep FDC in the scan (the forward-deployed pattern already matches it) and grade each posting; do not retarget the resume toward it.

Not verified on any public board (treat as rumors): Adverity, Opmed (Stamford, CT), Mason, Hyro, FIS.

# Canonical positioning (2026-11-16)
One source now drives every channel: `positioning.json` in the private resume-tailor-zach skill (headline, summary, looking-for line, target titles, floor, locations, unconfirmed claims). A renderer writes each channel's fields and the master resume, which carries the Jack & Jill CV edits so the next export does not regress them. Channel text is shown to Zach and applied only on his yes. LinkedIn, Indeed and ZipRecruiter bar automated access, so Zach applies those by hand from the rendered text. Lever has no candidate profile, only a per-application resume.

# Jack & Jill diversified search (2026-11-16, against the new CV): 8 matches

Each role was checked on the company's own board before grading; scores come from that posting's JD.

| Role | Verified on | Board score | Verdict |
|---|---|---|---|
| ServiceNow, Principal, AI Deployment Strategist, FDE ($221,200 to $387,100) | SmartRecruiters 744000155133610, posted 2026-10-13 | 0.69 CONSIDER (re-scored from the posting; the older 0.41 came from an unknown JD) | CONSIDER: see card |
| Sayari, Forward Deployed Engineer II (remote US, $160K to $180K) | Greenhouse 4465984009 | 0.88 PURSUE | PURSUE if the floor allows: under $220K, at or under Fonzi's current $180K |
| Runlayer, Deployment Strategist (NY hybrid, est $145K to $175K) | Ashby | 0.49 PASS | Skip: low fit and under the floor |
| Raspberry AI, AI Transformation Lead (NY hybrid, est $155K to $215K) | Ashby | 0.41 PASS | Skip on this posting; the title family now scans (see below) |
| Fireworks, AI Deployment Strategist (San Mateo hybrid) | Ashby | not posted | Skip: outside the location scope |
| Fulcrum, Founding AI Deployment Strategist (SF in office) | not found on a public board | not posted | Skip: outside the location scope |
| talentpluto (agency) for "Tenex", Forward Deployed Engineer (NYC in office, $180K to $260K) | not verified | not posted | HOLD at T0: Tenex's public FDE roles are all in Kansas City, so the NYC req is not on Tenex's own board |
| True Talent Solutions Partners (agency), Forward Deployed Strategist (NYC in office, $160K to $250K) | not verified | not posted | HOLD at T0: end client unnamed |

## ServiceNow, Principal, AI Deployment Strategist, FDE
- **Posting:** New York, 50 Hudson Yards, hybrid (Jack & Jill said remote; the posting says hybrid). Base $221,200 to $387,100 plus equity and incentive.
- **Need-to-have:** strategic ownership of an FDE portfolio and go-to-market calibration (the scorer's read). **Met:** Grayscale go-to-market for 10 regulated products, Manana engagements.
- **Gap:** the scorer reads it as an operator seat, not hands-on build, which runs against the "hands on the problem" line in your positioning.
- **Best:** principal-level strategist seat at the top of the pay range. **Base:** recruiter screen, then a large-company loop. **Worst:** they want ServiceNow platform tenure.
- **Objection:** "No ServiceNow platform background." Answer with deployment outcomes in regulated settings; the platform is learnable.
- **Time:** about 25 minutes on SmartRecruiters with the master resume.

## Agency listings (pre-call gate)
Both agencies start at T0 (self-asserted). Before sending a CV or booking a call, ask the recruiter to name the end client, then confirm the role on that company's own careers page (T1). For talentpluto, if the client is the Kansas City security company Tenex, the NYC in-office detail conflicts with its public postings.

## Scan change
"AI Transformation Lead / Director / Manager / Head" titles now match the scan (forward-deployed lane). They fit the "go-to digital transformation person for a principal-led organization" shape from 2026-11-03.

# Floor change (Zach, 2026-11-16)
Base floor is now $180K (was $220K), matching Fonzi. Re-read of the holds above: Sayari FDE II ($160K to $180K, 0.88) and Footprint FDE ($170K to $205K, 0.84) now clear the floor and move to PURSUE. Runlayer (est $145K to $175K) stays under it. Jack & Jill has no minimum salary set; setting one there is an account change for Zach.
