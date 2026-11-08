---
title: Honest proposals, findings from instance three (Harrison Wright, 2026-11-06 call)
date: 2026-11-08
status: FINDINGS for the design in PR 2072 (that branch is owned by another session; not edited)
design: _PROPOSALS/2026-11-08-honest-proposals-design.md on claude/honest-proposals-design
instance: _ARTIFACTS/harrison-wright-2026-11-06/, runtime/recoil/generated/2026-11-06-wright.json
---

# Instance three: what the method got right, missed, and lacked

**Why.** The design (PR 2072) asks a third engagement to prove the method before it generalizes. This is that third
run, on a real call. **What.** The call turned out to be a recruiting conversation, not a client ask, so it tests the
method's edges rather than its core. **Why now.** The design is still waiting on Zach's go, which is the cheapest time
to fix its intake. **How to read.** Top three findings first, then the rest, then the section 7 scorecard.

## Top three

1. **The method has no step zero: "what kind of conversation was this?"** The design's input is "a client's ask" and it
   assumes one exists. Here the counterpart was a recruiter assessing Zach as a candidate. Forcing the record would
   have produced a fake offer with invented fees. The recoil template already carries the classifier the method needs
   (`opportunity.engagement_type`: candidacy, client, partner, peer, plus the `req_reality` gate). Proposed: the skill
   opens by classifying, and refuses to build a record unless the type is `client` and someone asked for paid work.
   For other types it runs only the portable parts (gate, restate, ladder, ex-ante). One call also opened three loops
   (a candidacy, a product demo lead, a network intro); the skill should split them, not fold them into one record.

2. **The qualification gate is missing from the ten rules.** All ten rules govern Zach's honesty; none checks the
   counterpart before work is invested. The global trust-tier rule (T0 to T4, hold below T2) should be rule 0 and a
   required record field (`trust {tier, evidence[], date}`). It mattered here: the same afternoon, a fake recruiter
   impersonating a real executive reached Zach, and nothing in the design would have stopped that call from becoming a
   record. Harrison scored T3 on a 2023 intro thread through a mutual, not on DMARC (his domain is `p=none`, monitor
   only), which also shows the tier needs evidence rows, not a checkbox.

3. **Rule 1 (every number cites a source) must reach what Zach said out loud, not only what renders.** On the call
   Zach made claims a follow-up could easily repeat: "250 commits last week" (roughly holds: 262 non-merge commits
   across all refs, Oct 30 to Nov 6), "zero declined PRs" (not checked), and receipts "on ledger" (a Supabase table,
   which a crypto listener hears as on-chain). The restate step should list Zach's own live claims and mark each
   checked, struck, or keep-out-of-writing before any draft. The counterpart's figures need the same treatment:
   Harrison guessed a fund size and said he could not remember it.

## The rest

4. **Consent belongs in the rule list.** ADR-093 (no quoting a counterpart without notetaker consent) is not among
   the ten rules. No consent was on record here, so the restate is paraphrase and the reply carries no call citations.
   Proposed: a lint for `src:`, timestamps and quoted call lines in client-facing text unless `consent.on_record` is set.
5. **Rule 6 assumes prep happened.** No ex-ante was filed before this call. The fix that worked: file the ex-ante
   before the follow-up and score that. The design should say the ex-ante attaches to the next send, not the call.
6. **"First step small and paid" does not apply to a candidacy.** The ladder here is unpaid (note, intro, partner
   conversation). The only place a paid step could appear is the demo thread, and only if Harrison wants it on his real
   searches. The design should say the paid-first-step rule is for `client` type only.
7. **recoil-close publishes by default.** Its step 6 renders to `public/` and pushes to main. The honest-proposals
   flow calls recoil-close for calls; it should pass a local-only render, or the skill inherits a publish step that
   the design says it never does.
8. **Identity of third parties.** The intro target's name came through the transcriber two ways. A name the counterpart
   offers is not confirmed until spelled in writing; the reply leaves a placeholder.

## What worked

- The cold-read header and first-person, no-em-dash voice rules carried over unchanged to a non-proposal reply.
- The ex-ante with labelled odds and an abort rule fit a candidacy with no changes.
- Running the gate first, before reading for an offer, kept the work cheap: about a dozen tool calls to know this was
  not a proposal.

## Section 7 scorecard (the design's own bar)

| Test | Result |
|---|---|
| 1. Different shape | Yes, but too different: it is not a proposal at all, so it cannot count toward generalizing |
| 2. Cold use from SKILL.md | Not possible: no SKILL.md exists yet |
| 3. No hand edits to rendered outputs | Not applicable: no record was rendered |
| 4. Small code change | Not applicable |
| 5. Gates earn their keep | Trust gate and req-reality gate both ran; req gate passed at FORK. Gauntlet not run (no client-facing offer) |
| 6. Ex-ante scored | Filed 2026-11-08; scoreable after Harrison replies |

**Net:** instance three is a boundary test, not a third pass. The design still needs a third real client proposal
before its README claims generality. The cheapest change it suggests is findings 1 and 2: a classifier and a trust
field at intake.
