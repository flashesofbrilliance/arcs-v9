---
title: Honest proposals, a public good (design, not built)
date: 2026-11-08
status: MERGED 2026-11-09 (PR 2072, merge c87ceb58); approved 2026-11-08 (Zach: "Yes, build v0.1"). Open: public repo extraction, third engagement
pr: 2072
artifact: https://claude.ai/artifact/PGEkj5xJt9kXAxYgQnLwHB (private)
rendered: _PROPOSALS/rendered/2026-11-08-honest-proposals.html
owner: Zach Harris
prior_art: scripts/engagement_render.py, runtime/specs/engagement-record-v0.md, scripts/myally_hub_sync.py, the hub crawl leak check (on the My Ally branches, not on main yet), .claude/workflows/counterpart-gauntlet.js, rfp-engine (public), resume-tailor (public) with resume-tailor-zach (private), memories proposals-narrow-specific-no-pressure-value-first, avoid-front-loaded-unpaid-discovery, payment-terms-new-vs-existing-clients, cold-start-why-what-whynow-how-framing, label-every-probability-with-its-basis
---

# Honest proposals

**Why.** A small consulting proposal usually goes out as three or four hand-typed documents (a reply, a proposal,
an agreement, a scope exhibit) that drift apart the first time a date or price changes. It also tends to oversell:
a quote where a range belongs, a confident number with no source, a sharing ban the client cannot live with, and
silence about what has not been proven yet. The two engagements worked this way by hand (My Ally and Louisville)
showed that the fix is not better writing. It is one record that every document renders from, plus a few rules
that a check enforces before anything is sent.

**What.** A Claude Code skill, `honest-proposals`, that turns a client's ask (an email thread, call notes, or an
RFP) into one engagement record, and renders from it a reply, a proposal page, a plain-language agreement with a
scope exhibit, and a client page block. Every number cites a source or says it is judgment. A check fails when a
cited value changed and a document was not regenerated. A pre-send review reads it from the client's seats. It is
the sibling of the honest resume skill: that one refuses to claim what it cannot defend about a person; this one
refuses to promise what it cannot defend about a piece of work.

**Why now.** The engine is mid-flight, which is when the line between "generic" and "this client" is cheapest to
draw. The renderer is 536 lines of standard-library Python and only its self-test names the first client. The
My Ally agreement moved to rev 27 (a Claude Doc) and the rendered agreement in the repo is still v2 text marked
SUPERSEDED, so the record-to-agreement path already needs rework. The seedbank drift check flags `rfp-engine` as a
public repo with no catalogue entry, and that repo is the nearest public neighbour. No client deadline drives this.

**How.**
- Before (now): this design. Nothing built, nothing public.
- During (after your go): build v0.1 privately inside arcs-v9, on an anonymized example, with the gates below.
- After: a public repo only after your second go, and a claim that it generalizes only after a third engagement
  passes the test in section 7.

**How to read this page.** Sections 1 to 3 say what it is and who it is for. Section 4 is the core: the honesty
rules, each with how it is enforced. Sections 5 to 7 are the pieces it reuses, the smallest first release, and the
bar for generalizing. Section 8 is the home. Section 9 is what I need from you.

---

## 1. What it is

One record in, five things out, four gates before send.

```
client ask (email, call notes, RFP)
   |
   v
engagement record (one JSON; every value has a source and an append-only history)
   |
   +--> reply (email text)
   +--> proposal page (five altitudes, exec to surgical)
   +--> agreement + Exhibit A (plain language, draft for a lawyer)
   +--> client page block (rendered between markers in an existing page)
   +--> ex-ante receipt (what I expect the client to do, with odds and their basis)

gates: record validator | leak and voice lint | pre-send gauntlet | counsel flag
```

The skill does not send, publish or price for you. It refuses to mark the agreement sendable until a lawyer review
date is in the record, and it refuses to render a client-facing output that fails a gate.

## 2. Who it is for

- **First:** a solo consultant or fractional operator writing a small fixed-fee proposal to a private company that
  asked for help in an email or on a call. Roughly the shape of a paid first step followed by later steps that are
  not yet scoped. This is the one type v0.1 supports.
- **Later, not v0.1:** a response to a formal RFP (where `rfp-engine` would supply the cited asks), agencies with
  a procurement counterpart, multi-party agreements.
- **Not for:** anyone who wants a persuasive pitch generator. The skill makes a proposal less impressive and more
  defensible on purpose, the same trade the resume skill makes.

## 3. What stays private

Zach's own terms, rates, payment rules, state of law, voice and receipt ledger live in a private overlay skill
(`honest-proposals-zach`, in arcs-v9), the same split as `resume-tailor` and `resume-tailor-zach`. The public
method ships with one fictional worked example. No client name, price, date or clause from My Ally or Louisville
appears in anything public. The example is not a find-and-replace of My Ally: its figures, step count and dates
are invented, because the shape of a real engagement (three steps, a five-day first step, a particular fee) can
identify the client on its own.

## 4. The honesty rules, and how each is enforced

"Code" means the validator or a lint refuses the output. "Gate" means a review step must pass before send.
"Human" means the skill asks and records the answer but cannot check it.

| # | Rule | Enforced by | Exists today? | My view |
|---|---|---|---|---|
| 1 | Every number cites a source or is labeled judgment | Code: every stored field needs `source {kind, ref, date}`; `judgment` is a kind. Add: any figure in rendered text that did not come from a cite fails (the rfp-engine rule "figures are quoted, never computed", turned on our own output) | Partly: validator yes, literal-figure lint no | Keep. The literal-figure lint is the cheap gap closer. |
| 2 | Ranges with written assumptions, never a quote | Code: a phase after the paid first step must use a `money_range` field and link at least one assumption with `test_that_would_decide` | No | Keep, with one refinement: the paid first step is a fixed fee. That is not a quote for the whole job, it is the price of finding out. A range on a five-day step reads as evasive. |
| 3 | A reliance disclaimer instead of a sharing ban | Code: the agreement template carries the reliance clause; a lint fails on ban phrases ("may not share", "do not forward") in client-facing text | Clause yes (My Ally), lint no | Keep. The ban backfired in review because the client has to show the work to people who were not in the room. |
| 4 | No task-level bid sheet before the paid step | Code: the leak check. A per-engagement ceiling (any figure above it is full-build pricing) plus a pattern check for per-task hour or rate tables, applied to every client-facing output while the step is unpaid | Yes for one page (hub crawl, on branches only, ceiling hard-coded) | Keep, generalize: ceiling and "paid" flag move into the record. This is the rule that protects you from being shopped to other bidders. |
| 5 | "Opinion, not legal or compliance advice" and "as is" stated plainly; a lawyer reads the agreement once | Code for the wording (template header and clause, lint fails if missing). Human for the lawyer: a `counsel_review {date, by_role}` field must be set before the agreement can render as sendable | Wording yes, gate no | Keep. "Once" means once per template version, not once per client. Say in the public README that the templates follow one US state's habits and are a starting draft. |
| 6 | An ex-ante receipt, scored after the client replies | Gate: the record needs `ex_ante {expect, p, basis, date}` before any send; `close {what_happened, date, scored}` after the reply. Public version writes a local JSONL; the overlay writes the Supabase `decision_receipt` row | No in the record (recoil-close does this for calls) | Keep. Without it there is no way to learn whether honest proposals win or lose more often. |
| 7 | A gauntlet pass before anything is sent | Gate: `counterpart-gauntlet` with a proposal preset of five seats (founder, finance, counsel, skeptic, busy reader). Public version: the same seats as a checklist prompt, since the workflow is ARCS-specific | Yes (workflow), no preset | Keep. On My Ally it caught a narrowed office-hours term and the sharing ban; that is two real catches on one engagement (measured, n=1). |
| 8 | What is not proven yet is said out loud | Code: `not_proven[]` must be non-empty and renders as its own section on the proposal page | No | Keep. An empty list is itself a red flag, so the validator treats it as an error. |

Two I would add, both already half built:

| # | Rule | Enforced by |
|---|---|---|
| 9 | A change after sending is shown, never silent | Code: already built. Once `last_sent` is set, a changed cited value prints "changed DATE, was X" in each output. |
| 10 | Plain language, first person singular, no em-dashes, no invented urgency | Code: em-dash and voice lint (the `page_gate.py --counterpart` check that caught "our call" and "how we stay in touch" on the hub). Human: the cold-read `why_now` must name a real trigger. |

One I considered and would leave out: a "price last" ordering rule. It is a good habit for video and calls, but a
written proposal reader often scrolls to the price first, and hiding it reads as a sales move.

## 5. The pieces it reuses

| Piece | Where now | Generic today? | Change for v0.1 |
|---|---|---|---|
| Renderer (`render`, `--check`, `--self-test`) | `scripts/engagement_render.py`, 536 lines, stdlib | Yes, except the self-test fixtures point at the first client | Self-test runs on the fictional example. |
| Record schema | `runtime/specs/engagement-record-v0.md` | Yes | v1 adds `not_proven`, `ex_ante`, `close`, `counsel_review`, `money_range`, `phase.paid`, `leak.ceiling`. |
| Page block sync | `scripts/myally_hub_sync.py`, 52 lines | Nearly (paths are client-specific) | Take marker names and paths as arguments. |
| Leak check | hub crawl, on the My Ally branches | No (one page, one ceiling) | Pull the leak part out as its own lint over every output; leave the hub-specific crawl behind. |
| Voice lint | `scripts/page_gate.py --counterpart` | Yes | Run on rendered text, not just pages. |
| Pre-send gauntlet | `.claude/workflows/counterpart-gauntlet.js` | Yes (parameterized) | Add a proposal seat preset; write the public checklist version. |
| Assumption rows | `scripts/assumptions.py` shape | Yes | None. |
| Progress events | `scripts/engagement_progress.py` (PR 2066) | Nearly | Not in v0.1. |
| RFP intake | `rfp-engine` (public) | Yes | Not in v0.1. Later it can turn an RFP into `asks[]` with clause sources. |
| Method/overlay split | `resume-tailor` + `resume-tailor-zach` | Pattern | Copy the layout: SKILL.md, schema, templates, evals, private overlay. |

What does not carry over: the Louisville proposal page and PDF were built by hand (`_ARTIFACTS/louisville-proposal/
source.html` to `public/`), not from the record. So Louisville is an instance of the method, not of the code. Of
the two engagements, only My Ally exercised the renderer.

## 6. The smallest first release (v0.1)

One engagement type: **a fixed-fee paid first step for a private client who asked by email or call, with later
steps shown as ranges.**

In:
- `SKILL.md`: intake questions, then fill the record, render, lint, gauntlet checklist, ex-ante, stop before send.
- Schema v1 and the validator.
- Renderer with four outputs: reply, proposal page, agreement, Exhibit A.
- Four lints: literal figures, sharing-ban phrases, leak ceiling and bid-sheet pattern, voice and em-dash.
- The counsel flag and the ex-ante requirement.
- One fictional worked example and a self-test that fails on a stale output and passes on a fresh one.

Out (each a later row, not a hidden promise):
- Client page tabs and progress tracking.
- RFP intake through `rfp-engine`.
- PDF output, hosting, passcode gates.
- Supabase receipts (overlay only).
- Any second engagement type.

Size, judgment: one to two working sessions, because the renderer and most checks exist and the new work is the
schema additions, four lints and the example. Basis: the 588 lines already written and the rate the My Ally
pieces were built this week. Not measured.

## 7. What a third engagement must prove before generalizing

My Ally and Louisville are two instances, and only one of them used the code. Before the README says it works
for proposals in general, a third engagement should pass this, written down now so the count is not bent later:

1. **Different shape.** A different client type or a formal RFP, not another paid-diagnostic-then-build.
2. **Cold use.** Run end to end by a session that did not build the skill, from `SKILL.md` alone.
3. **No hand edits.** Zero edits to rendered outputs. Every change goes through the record.
4. **Small code change.** Renderer changes under about 50 lines and no more than three new record keys. More than
   that means the schema was fitted to My Ally and needs another pass, not a release. (Thresholds are judgment.)
5. **Gates earn their keep.** The gauntlet and lints each catch at least one real issue or are recorded as having
   caught none, with the count published either way.
6. **The ex-ante is scored.** The client replied, and the receipt says whether the prediction held.

If it passes, it moves to a plugin with the second engagement type. If it fails on 4, the fix is the schema, not
more templates.

## 8. Where it lives

**Recommendation: a new public repo, `honest-proposals`, as a Claude Code skill, built first inside arcs-v9.**
Not a skill inside `rfp-engine`.

The reason is `rfp-engine`'s own contract. Its README says requests to draft proposal language or decide whether
to bid are refused before any model call, and that rule is enforced in code. That refusal is what makes it
trustworthy as a reader of solicitations. A drafting skill in the same repo would either break that rule or sit
next to it as an exception, and both weaken the thing it is known for. The two should be neighbours: `rfp-engine`
reads the RFP and returns cited asks; `honest-proposals` takes cited asks and writes an offer. A README link in
each, and later an intake adapter, joins them without merging their promises.

A plugin is premature: a plugin bundles several skills and hooks, and there is one skill with one engagement type.
Revisit at the third instance.

Sequence:
1. Build v0.1 in arcs-v9 under `scripts/` and `_ARTIFACTS/engagements/example-fictional/`, with the overlay as
   `.claude/skills/honest-proposals-zach/`.
2. On your second go, extract the public method to `flashesofbrilliance/honest-proposals` (MIT, like the resume
   skill), add it to the seedbank catalogue, and link it from `rfp-engine`'s README. That catalogue entry also
   settles the seedbank drift flag for `rfp-engine` if both are catalogued together.

## 9. What I need from you

1. Home: new repo `honest-proposals` (recommended) or a skill inside `rfp-engine`.
2. First release type: fixed-fee paid first step, private client (recommended), or something else.
3. Go to build v0.1 privately in arcs-v9. Nothing public until a separate go.
4. The rule changes: the fixed-fee refinement to rule 2, and adding rules 9 and 10.

## Not proven yet

- That honest proposals win more often, or lose less painfully, than ordinary ones. There is no outcome data; the
  ex-ante rule exists to start collecting it.
- That the schema fits a second engagement type. Only one engagement used the code.
- That the agreement template is sound outside the one state it was drafted for.
- That the fictional example is far enough from My Ally that nobody can tell. It needs a skeptic read before it
  goes public.
