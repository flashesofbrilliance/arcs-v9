# Champion-Sourcing — the Amy signal, characterized + a fit heuristic

_The PEOPLE pipeline, distinct from the postings scrape that feeds jobs.arcs.care. Goal: find more
recruiters / hiring champions who GET the rare pair (operator who ALSO ships, across domains, into
0→1) and can place it. Amy is the acceptance test._

Source of the signal: `_ARTIFACTS/resume-blacksmith/recruiter-recoil-report.md` (Granola verbatim,
Sep 2 call) + the tear-sheet built for her (`tear-sheet-amy.html`, live at recruithaus.arcs.care).

---

## Part 1 — What Amy recognized, and in what language (resonance markers)

Verbatim anchors, tagged by the marker they evidence:

| Marker | Her words / behavior |
|---|---|
| **Crossover-recognizer** | "when you have technical teams, sales teams, the client, and someone who can speak to all of them... that's a really hard and rare find." → "You're the unicorn." "some people are technical, some operational. God forbid they cross over — that's the unicorn, and that's you." |
| **Bet-on-the-person thesis** | Agreed hard with the cautious-capital thread: right person = "exponential upside," wrong person = "death spiral for a Series B." "Exactly. It's incredibly detrimental." Hiring as risk-of-ruin, not headcount. |
| **Shape-over-title** | Killed the PM read unprompted: "it definitely wasn't a PM situation." Reads the actual shape (engineer who owns product), refuses to flatten to a lane. |
| **Anti-single-lane / anti-corporate** | "Army of one punching at the weight class of a heavyweight" landed as the deliberate counter to the rejected ex-AWS "too corporate" candidate. |
| **Advocacy conversion** | Raised his comp floor herself ($325–375), "we're not going to undersell you." Flipped from screener to seller at ~minute 20 and negotiated FOR him. |
| **Portfolio / parallel-path** | Offered a Paraform list unprompted: "fantastic candidate no matter where we sent you." Thinks relationship, not one-req. |
| **Org-design literacy** | Leaned into the zone-of-genius / energizers-drainers / "constructive interference and torque" framing (she came out of an MSP leading a global team). |
| **Effortless register** (Zach's own tell) | Zach: the call "felt a lot more effortless than previous ones with recruiters." Low translation-tax — she met him at his level, "it's so fun to listen to you talk like this." When you don't have to *explain* the pair, they already see it. |
| **Relational, not transactional** (Zach's tell) | Zach: "less transactional, more professional than most younger ones — a decidedly different carrier signal and vibe vs many others." The champion treats placement as a craft/relationship (27 yrs, org-design roots), not a req-fill transaction. The carrier wave itself is the tell, upstream of any single line. |
| **Value-justification over band-match** (Zach's tell) | Zach: "she saw the value as to WHY I'd justify that price point." The champion argues *why premium is warranted* (two-hires-in-one), not conformance to a comp band. **Caveat — double-edged:** market-pricing cuts both ways; anchoring to a band can cap the pair back into a comparable as easily as it can raise the floor. A true champion prices the value, not the market. |

**The core resonance frequency:** rarity-of-the-crossover, spoken in comp/leverage/de-risk terms
(not the FDE/applied-AI taxonomy). Everything else rides that one.

---

## Part 2 — Champion-fit heuristic (mirrors the board rubric dim/weight style)

Score a candidate recruiter/leader 0–3 per dim. **Pre-contact** dims are discoverable from public
signal (posts, placements, bio, network graph) and drive sourcing. **On-call** dims are the
acceptance test — they can't be scored from a distance, only confirmed the way Amy confirmed them.

### Pre-contact (drives who to source)
| Dim | wt | What it measures | Amy |
|---|---|---|---|
| `crossover_recognition` | 3 | Language/placements value technical×operational×client spanning ("unicorn", "bridge", "bilingual", "generalist", "founder-shaped", "athlete") | 3 |
| `warm_path` | 3 | Already in Zach's network or one hop. Warm beats cold every time. | ~1 (Paraform, semi-warm) |
| `domain_fit` | 2 | Places into agent-infra / devtools / applied-AI / regulated / 0→1 — where the pair is rare AND central (the Blacksmith shape), not incidental | 3 |
| `shape_over_title` | 2 | Writes JDs / posts about the *shape* of a person; skeptical of pure-lane / "too corporate"; independent or founder-embedded, not big-agency keyword-match | 3 |
| `org_design_literacy` | 1 | Background as ex-operator / team-builder; talks team composition, zone-of-genius, systems | 3 |

### On-call (the acceptance test — confirms champion, not just fit)
| Dim | wt | What it measures | Amy |
|---|---|---|---|
| `bet_on_person` | 3 | Frames hiring as exponential-upside / risk-of-ruin on the individual, esp. Series A–B | 3 |
| `advocacy_conversion` | 3 | Converts belief into action — argues *why premium is warranted* (value, not band), raises the floor, opens parallel paths. NOT band-conformance. | 3 |
| `effortless_register` | 2 | Conversation flows with low translation-tax; enjoys the human channel; you don't have to explain the pair | 3 |
| `relational_carrier` | 2 | Non-transactional vibe — treats it as craft/relationship, not a req-fill. Seasoned/operator-rooted correlates but the carrier wave is the real read. | 3 |

**Anti-champion gates (any → deprioritize):** ATS keyword-matcher who needs one title to slot you ·
big-agency volume down-seller who flattens comp bands · "we need a pure X" single-lane filter ·
title-flattener who reads FDE/builder as "just a PM" or "just an engineer".

**Acceptance test:** a target is a champion if, on first real contact, they name the crossover
rarity *back to you* in their own words the way Amy did — unprompted, and it feels effortless.
Pre-contact score gets them in the room; the on-call dims are what make them an Amy.

**Champion pitch = reuse the recruiter-enablement tear-sheet framing** (two-hires-in-one /
comp-as-discount-vs-two / de-risk circuit breakers), tuned to each target's own register — never
the engineering taxonomy. Once a champion is found, the counterpart-forge / recoil machinery works
the individual relationship (forge skill, recoil-* skills).

---

## Part 3 — Sourcing (NOT yet run — awaiting Zach's go; cost discipline)

Cheapest-first, legitimate sources only (no login-scraping; PII air-gap on any public artifact):
1. `scripts/network_scan*.py` over data Zach already has (his network export, existing threads).
2. Warm paths first: people one hop from Amy / from existing champions / from prior threads.
3. Public signal for `crossover_recognition` + `domain_fit`: recruiters/leaders who post about
   founder-shaped / generalist / operator-builder hiring in agent-infra / applied-AI / regulated 0→1.
4. Apollo / ZoomInfo enrichment only if available and only on Zach's go.

Output = a ranked champion list (pre-contact score + warm path + suggested register), then decide
whether "champions" earns a second lane alongside the postings board (Compass Lane is
domain-agnostic; this is a candidate lane).
