# Recoil Report: MyAllyLD (Kelly Jacobson, Chelsea Starks; founder Leah Gambal)

INTERNAL ONLY. Call 2026-10-08, 9:30 to ~10:15 ET, Google Meet. Warm intro via Jess (Acorn Lane parents thread).
Sources: full Granola transcript (193 speaker turns, read end to end), LinkedIn PDFs for Gambal, Jacobson, Starks, leahgambal.com, category web search.
No PrepSession existed, so there is no ex-ante expectation to score against.

## Data-quality flags (read first)
- The transcript has the ages swapped: "I'm 34" is tagged Kelly and "I'm 55" tagged Chelsea. Profiles say the reverse (Kelly: Fairfield BS 1993, Kellogg MBA 1998; Chelsea: Hartford grad ~2014). Treat Kelly as ~55 and Chelsea as ~34.
- The transcript spells the founder "Leah Gamble". It is **Gambal**.
- MyAllyLD has no public web footprint beyond leahgambal.com ("launching in 2026"). It is stealth for real.

## Who they are
| | Role on team | Background | Core competency |
|---|---|---|---|
| **Leah Gambal** (absent) | Founder. 3rd-generation dyslexic, both kids dyslexic | Emerson TV; 8 yrs Sesame Workshop (international co-productions), Universal, Hearst; Access Consulting parent-to-parent (2017 to now); co-founded Access Dyslexia; boards incl. Lab School of Washington (10 yrs), Neurodiversity Foundation | Content and production, school-board fundraising, parent trust network in Fairfield County |
| **Kelly Fahey Jacobson** | Wrote the business plan. Commercial and finance voice | PwC audit, Kellogg MBA, Unilever (Wisk), Ghirardelli (took a franchise from $40M to $170M), BuzzBack online research, co-founder of MyVirtualLife (1999). Boards and PTA since 2013, substitute teacher | CPG brand P&L, consumer research, community connector |
| **Chelsea Starks** | Co-founder, "lead developer" (in practice a marketer using Lovable and Claude) | 12 yrs marketing: LiveGirl (Marketing, *Technology* and Partnerships), Korn Ferry content, Dooney & Bourke ecom; Horizons at SHU (overlaps with Leah's board years, which is likely the origin of their working relationship); now a Keller Williams realtor (Jan 2026) | Calm, detail-heavy execution; the self-described "highly technical non-coder" |
| **Morgan** | Helps Chelsea with Claude Code | Unknown | Did the token cost model with Chelsea |
| Unnamed consultant | Strategic AI advisor, "not a developer" | Unknown | Raises blockers each week |

## The product (as stated)
"A GPS for parents navigating learning differences", meant to last from diagnosis through college and the job search. Built on Lovable and Supabase. A 20 to 30 page build spec exists. The AI agent "Alice" is the next build. The site has five areas:
1. **Vault**: parents upload IEPs, evaluations and meeting notes. Alice reads all of it. *This is the highest-risk area.*
2. **My A-Team**: Alice searches the open web (with an exclusions list) for providers and tutors.
3. **Strengths**: a questionnaire about the child's strengths.
4. **Opportunities**: camps, scholarships and apprenticeships matched to strengths.
5. **Checklist and dashboard.**
Status: only the 4-person team uses it, nothing is live, and the AI isn't wired in yet. Funding is self plus friends and family, and they plan three funding paths (more friends and family, grants, partnerships) "starting at the beginning of the year". It is a for-profit, by choice, so they can later expand to "other life challenges".

## Pass 1: Reverse listening (reading the close back to the start)
**Where it landed:** Kelly asked for a rate ("Don't be afraid to say the number... we'll still negotiate"), asked whether you record calls, and agreed to next steps: **they send an NDA, then the codebase and the build spec. You give a scoped proposal across the advisory, fractional and hands-on build tiers.**

Reading back from there:
- **Kelly is the commercial gatekeeper and Chelsea is the technical gatekeeper.** "You impressed Chelsea for sure. She was gonna be the one that was gonna gauge... if it's the right fit." Once Chelsea left, Kelly moved straight to price, so the technical-fit gate is passed.
- **Rate posture (updated with your context):** they live on the same street and are in the same parent groups as your closest Fairfield friends. You intend to add value at a friends-and-family rate ($100 for a passion project up to $350 for a headache one), not to extract. That's the right posture. Kelly's "don't be afraid to say the number" means a plain, written number would land as a kindness. **The risk isn't the price. It's an unwritten scope,** where a neighborly favor and paid work blur and any friction spreads through the shared community.
- **The recording question is a trust signal.** She felt she had received value and wanted to keep it ("you shared so much"). That means you gave away a full discovery session for free. Fine for goodwill, but the next session should be the paid discovery or receipt workshop you described.
- **Kelly's "internal struggle" is the real decision.** She is "old school" and doesn't want to rush, while the team feels "we need to move really fast". Chelsea: "we're not in a rush, though we kind of are." That pace fork has not been resolved, and your offer should give them a way to settle it.
- **Chelsea's real decision** is to "move forward with the build and work with a developer side by side, or hire a developer and I'm advising them". That is a build-or-delegate fork, and it depends on cost and timing.

## Pass 2: Deep recall (start to end)
1. **Warm-up (0 to 6 min).** Logistics stress (Kelly's college trip with her son). You offered Turo, a small useful gift that set a giving-first tone.
2. **Pitch (6 to 12).** Kelly framed the product. You answered with your own Wilton resource-room story and "neural net worth", which landed as shared values. It also turned the floor toward ARCS for about 3 minutes before they had stated their need.
3. **Compliance (12 to 20).** You raised HIPAA and COPPA, PII redaction, and deterministic redaction instead of LLM redaction. **Chelsea's first concrete question was Anthropic vs OpenAI for Alice and the BAA.** This is her top pain point.
4. **Pressure-testing (20 to 32).** Dependency mapping. Chelsea admitted "every week we're uncovering more blockers... we haven't laid them out." **This was the strongest moment of revealed need on the call.** Chelsea then showed how deep their prep goes: model freeze windows, switch costs, audit log, voice and trust rounds. They are more sophisticated than they first appear.
5. **Turning point (~33).** Chelsea: "the build spec needs to be reevaluated... we don't even want to build this and then retrofit the right disclaimers." **She reframed her own plan live, which tells you the advice landed.**
6. **Cost and extensibility (33 to 45).** Unit economics, local models, nonprofit pricing (Kelly corrected: they are for-profit), grants (you suggested a Berkeley neurodivergent research program), build vs rent. Chelsea already has a token model by user tier, so cost is not new to them.
7. **Offer and scope (45 to 52).** Chelsea asked for numbers on your three tiers (she had read your site). You answered good/fast/cheap and "depends". She asked plainly for a price and got a range.
8. **Kelly only (52 to end).** Kelly's background, the business plan, plan-vs-roadmap drift (your double-entry analogy fit her accounting background), patentability, MySpace vs Facebook, rate, recording, ex-ante receipts and the pre-mortem pitch.

## Stated vs revealed preference
| Who | Stated | Revealed |
|---|---|---|
| Team | "We're not in a rush" | They want internal testing, then focus groups, then beta, and funding starts in Q1. That is a real clock. |
| Team | "We have the whole structure, the site works" | Alice, the AI core, has not been started. The scaffolding is a Lovable front end. |
| Chelsea | Wants a vendor answer (Anthropic or OpenAI) | Needs **sequencing and legal-gate ordering**. She admitted the blockers are not laid out. |
| Chelsea | "I'm highly technical" | True for a marketer: a spec, a token model, model freeze. She is honest about the line ("I don't write code"). Respect it and don't talk down to her. |
| Kelly | Old-school, do it right, competition is fine | Asked twice about **patentability and ownable IP**. Her CPG background wants a moat and a franchise. |
| Kelly | Asked about rate as a fact-find | Pre-negotiating. She told you to name a higher number. |
| Kelly | "Leah brought me on to write the business plan" | The plan is a year old and drifting from the build. She agreed. That plan-vs-roadmap reconciliation is something you can sell to her. |
| Leah (via proxies) | A strengths-based empowerment mission | She absorbs the legal risk personally ("Leah has out with counsel... spoke with another lawyer yesterday"). The founder carries the liability anxiety. |

## Zones of genius, energizers, drainers
**Leah:** *Genius:* narrative and production for children's media at global scale (Sesame co-productions with USAID and Nestlé), plus parent trust built from lived experience. *Energized by:* reframing a deficit as a strength, speaking, mentoring parents one to one. *Drained by (inferred):* reading-heavy compliance and spec work (she is dyslexic and outsources text-dense legal work to counsel). **Design implication: give her one visual decision map, not a 30-page memo.**

**Kelly:** *Genius:* turning a brand into a P&L (a 4x franchise), consumer research (BuzzBack), getting cross-functional groups to deliver. *Energized by:* leading ("you'll see me everywhere because I'm always leading something"), teaching, community. *Drained by:* tech ambiguity ("I kind of think you pay a lump sum a month") and wasted logistics time. **Speak to her in unit economics, double-entry and stop-losses.**

**Chelsea:** *Genius:* calm, detailed execution and turning ideas into working artifacts (she shipped the spec and the scaffold without being an engineer). Her LiveGirl "Technology and Partnerships" title shows she leans technical. *Energized by:* building, due diligence, being treated as competent. *Drained by:* finding blockers every week with no map, and by being the lead developer without the tools of one. She also has a second job as a realtor since Jan 2026, **so her bandwidth is limited, which is a hidden constraint on the "build it myself" path.**

## Category scan (what they shared, then the market)
- **Direct and adjacent players:** [Expert IEP](https://www.globenewswire.com/fr/news-release/2024/09/17/2947599/0/en/Expert-IEP-Launches-AI-ML-Powered-Platform-to-Support-Neurodiverse-Learners.html) (parent-built IEP AI, ~$1.7M raised, latest round Feb 2026, per [vcbacked](https://www.vcbacked.co/company/expert-iep)); Empower IEP ([Stanford AI + Learning Differences hackathon winner](https://acceleratelearning.stanford.edu/conference/ai-learning-differences-hackathon/)); Luca (dyslexia reading, [GovTech](https://www.govtech.com/education/k-12/chatgpt-enabled-luca-ai-platform-helps-dyslexic-students-read)); a mother-built AI tutor ([Stephen Gaynor School](https://www.stephengaynor.org/2025/11/04/how-one-mom-built-an-ai-tutor-for-her-son/)); Understood.org is the main free nonprofit. **The IEP-vault part is crowded. The lifespan arc from strengths to opportunities to careers is the thinner, more ownable lane.** That fits Kelly's IP instinct and your neural net worth thesis.
- **Vendor fork (Chelsea's question), from web sources and not yet verified against primary docs:** Anthropic's BAA reportedly needs sales-managed Enterprise and carries 30-day retention on covered models, with no zero data retention ([intuitionlabs](https://intuitionlabs.ai/insights/guides/zero-data-retention-claude-anthropic-life-sciences), [companyscope](https://companyscope.io/vendors/anthropic)). OpenAI's BAA covers zero-data-retention endpoints only, and its [under-18 guidance](https://developers.openai.com/api/docs/guides/safety-checks/under-18-api-guidance) says not to process data from children under 13 without zero data retention. **Verify both against the vendors' own terms before advising.**
- **The deeper premise to challenge: HIPAA probably isn't their main regime.** A parent-facing consumer app is usually not a HIPAA covered entity or business associate. IEPs are FERPA records at the school, but FERPA binds schools, not a parent's own uploads. The likely live regimes are **COPPA** (only if kids under 13 use it directly), **state child and health privacy laws** (Connecticut's CTDPA has minors' provisions; Washington's My Health My Data Act), and **FTC Section 5 / the Health Breach Notification Rule** for health apps. If that's right, the "sign a BAA" fork may be the wrong first question. This is exactly the kind of "pressure-test the premise" value you pitched. *Not legal advice. It's a question to put to their counsel.*

## Kintsugi: seams in your own performance
- **"Personally liable for $2 million... if memory serves."** This is unverified and probably wrong as stated. HIPAA penalties are tiered civil fines on the entity, with annual caps around $2M per violation category, not a personal liability you take on by signing. Correct it in the proposal before counsel catches it, because they will.
- **"I built ARCS with Claude, Lovable, Supabase."** ARCS runs on Next.js, Prisma and Vercel, with Supabase for the receipts and decisions tables. Lovable is not core. Keep claims precise, since Chelsea will rely on them.
- **Airtime.** Your turns ran long. You caught it yourself once ("I want to just pause myself"). Chelsea's stream of "mm-hmm"s while you talked hid her questions until the end. Next session: ask, then stop.
- **The early ARCS detour** came before you had heard their need. It worked because of the shared values, but it cost time with Chelsea.

## Scenarios (where this goes)
1. **Paid discovery plus decision-receipt workshop (most likely, recommended).** A fixed fee, about 2 weeks: spec audit, a dependency map with legal gates ordered first, a regime check for counsel, a vendor decision receipt, a pre-mortem, and a phased MVP (Strengths plus Opportunities first, Vault last). Built for Leah as a visual map, Kelly as a cost and stop-loss model, and Chelsea as a sequenced backlog.
2. **Fractional CTO with Chelsea or a hired dev building.** Comes after scenario 1, so they can choose with evidence.
3. **Hands-on build.** Lowest leverage for you given their budget, and it competes with Chelsea's ownership. Avoid unless they ask for it.
4. **Stall.** NDA lag, counsel delays and Q1 funding push the work out. Mitigation: make scenario 1 small, fixed and dated.

## Risk flags
- Founder-level legal anxiety plus a for-profit structure plus child data: that is a slow-to-sign profile.
- Blurred lines between a favor and paid work. In a tight community, friction reaches mutual friends. Write the scope down.
- Chelsea's bandwidth (realtor since 2026) versus the "build it ourselves" plan.
- Leah, the founder and probably the final decision-maker, wasn't on the call. **Get her into the next session.**

## Next moves
1. **Today:** a short thank-you to Kelly and Chelsea that confirms the NDA, then codebase and spec, then a proposal. Draft only. You send it. Include the "regime check" question as a teaser of value.
2. Before you see the proposal: write an **ex-ante receipt** with your fee number, the expected tier (scenario 1), and the risk of a stall.
3. When the spec arrives: audit Vault plus Alice first. Its data flows set both the regime and the vendor choice.
4. Propose scenario 1 as a written, fixed-scope friends-and-family engagement at the passion end of your range. Name the triggers that would move it toward the headache rate (scope creep, ad-hoc asks, stalled decisions), and ask for Leah to attend the kickoff.
