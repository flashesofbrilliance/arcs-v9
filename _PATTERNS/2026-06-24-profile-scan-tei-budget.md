# Profile Scan — Pre-Mortem + TEI Budget Plan (5-hour window)

**Date:** 2026-06-24 · **Context:** session on Opus 4.8 · **Canon hook:** "Five-hour window budget — bounded time allocation that forces scope discipline under finite operator energy" (`ARCS-Glossary-v0.2.md`).

> Caveat up front: I cannot measure exact remaining tokens/minutes. This budgets in *proportions and tiers*, not fake clock time. Treat "remaining" as "whatever is left."

---

## Part 1 — Light simulated pre-mortem

*Frame: it's the end of the window. The session burned out with no usable net gain. What killed it?* (BAR/ruin lens, anti-thesis pass — kept to the 5 highest-probability failure modes.)

| # | Failure mode | Likelihood | Why it would happen | Pre-empt |
|---|---|---|---|---|
| 1 | **Built on sand** | HIGH | Jumped into the Phase 1–7 build (TS types, wire into `arcs-v9`) — but that rests on `patterns.jsx`, whose provenance is UNCONFIRMED (Ledger B1). Budget spent encoding a shape that may not be canonical. | Do NOT build until `ui_kits/documents/` ownership is confirmed. Build is negative-EV right now. |
| 2 | **Opus tax on mechanical work** | HIGH | Staying on Opus 4.8 for file edits, list-writing, commits — work a cheaper model does identically. Pure burn. | Downshift to Sonnet/Haiku for any mechanical step; reserve Opus for genuine reasoning. |
| 3 | **Corpus rabbit-hole** | MED | Reading the full §2.5 scoring logic, a full Gamma sweep, the richer glossary corpus, more xlsx — token-heavy, low marginal value vs. what's already established. | Defer all bulk reads to a session that has a confirmed authority-map (cheaper then). |
| 4 | **Unilateral canon edits** | MED | Amending ADR-020/023's 100-gate, or editing `ARCS-Glossary-v0.2.md` in Downloads — both need Zach; doing them solo creates rework + drift. | Flag, don't change. Already the standing posture. |
| 5 | **One more mockup** | LOW-MED | Producing further widget variants — the render already failed once; diminishing returns, and the canonical document is already demonstrated. | Stop generating mockups. The point is made. |

**Pre-mortem headline:** the single biggest budget risk is spending it on the *highest-value* item (the build), because that item is *blocked on the highest-risk assumption*. Velocity into a wrong foundation is the trap.

---

## Part 2 — Total Economic Impact (TEI) meta-plan

Forrester TEI lens (Benefit · Cost · Flexibility · Risk) over the remaining work, ranked by **Benefit ÷ Cost, penalized by Risk**. Cost is in-session token/compute; "Zach-cost" = needs a human decision (≈ free to the session, just a question).

| Item | Benefit | Cost | Flexibility (options opened) | Risk | Verdict |
|---|---|---|---|---|---|
| **Bank the spec + ledger** (done) | HIGH — durable, kills re-derivation | ~0 (done) | Every future session starts warm | ~0 | ✅ DONE |
| **This TEI plan** (this file) | MED — graceful close, reusable pattern | LOW | Reusable budgeting artifact | ~0 | ✅ doing now |
| **Confirm `ui_kits/documents/` ownership** | HIGH — unblocks the entire build | Zach-cost only | Unblocks Phase 1 | ~0 | → hand to Zach |
| **Lock param grammar** (`mode`/`audience-direction`/depth) | HIGH — unblocks schema | Zach-cost (decision) | Unblocks `ProfileScanResponse` | LOW | → hand to Zach |
| **Drop richer glossary corpus** | HIGH — kills ~most of Ledger A | Zach-cost + 1 cheap session | Resolves term collision | LOW | → hand to Zach |
| **`arcs_cfa` disposition + push `fd6ea07`** | MED — unsticks committed work | LOW (mechanical) | Decides pipeline home | LOW | → quick Zach call, then mechanical |
| **Phase 1–7 build (types + wire-in)** | HIGH (eventually) | HIGH | — | HIGH (blocked on B1) | ⛔ DEFER — negative-EV now |
| **Read §2.5 / full Gamma sweep / big reads** | LOW now | HIGH | — | — | ⛔ DEFER to authority-mapped session |
| **Amend ADR-020/023 100-gate** | MED | LOW | — | MED (needs review) | ⛔ flag only |

### The graceful-close conclusion

The TEI math says: **the remaining high-value work is either (a) Zach-cost decisions that cost the session almost nothing, or (b) blocked on an unconfirmed authority and therefore negative-EV to start now.** So the *graceful* spend is to **stop here on substantive work**, having banked the two durable artifacts (spec + ledger), and convert everything else into a cheap decision queue for Zach.

### Budget allocation for whatever window remains

- **~0 effort:** spec + ledger + this plan are banked. ✅
- **Cheap (do if asked):** push `fd6ea07` / commit these two new docs into `arcs-v9` — mechanical, downshift off Opus.
- **Zach-cost (no session burn):** the 4 unblocking decisions above. Each is one answer, not one work-session.
- **Deferred (protect the budget):** the build, the bulk reads, the canon amendments — all wait for the authority-map + glossary, which make them cheap later instead of expensive-and-risky now.

**One-line meta-plan:** bank what's durable, defer what's blocked, downshift the model for anything mechanical, and route the unblockers to Zach as decisions — don't spend Opus budget building on an unconfirmed foundation.
