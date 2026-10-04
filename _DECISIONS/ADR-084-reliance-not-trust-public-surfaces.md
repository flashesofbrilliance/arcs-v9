# ADR-084 — Reliance, not trust: public surfaces say what to rely on them for, and what not

> **Status:** PROPOSED
> **Date:** 2026-10-03
> **Author:** Claude Opus 5.5, from a session with Zach (2026-09-30)
> **Oracle:** number allocated via `scripts/oracle.py next adr` (84); `_SEEDS/_oracle.json` committed.
> **Commit:** (set at merge)

---

## D — The Decision

**Sharp question:** Should every public ARCS surface describe itself by what a reader can rely on it
for and what they cannot, and never ask to be trusted or call itself trustworthy or objective?

**Proposed answer (for review, not decreed):** Yes. A public surface states its reliance boundary in
plain words, in two halves: what it can be leaned on for (mechanical, reproducible, inspectable) and
what it cannot (truth it never checks, inputs it never sees, judgment it leaves to a person). The
words "trust us", "trustworthy" and "objective" are not used about our own tools.

---

## E — Entity / System

- `public/honest.html` (honest.arcs.care): the first surface built to this rule; its reliance block
  replaces the drafted "Why you can trust it".
- `public/blog-nftt-the-video-that-said-too-much.html`: section VI, "Not trustworthy, checkable",
  states the principle in prose (PR #670).
- `public/belief-log.html` (status.arcs.care/beliefs): already shaped this way; it publishes the shape
  of the falsification record, not a claim of reliability.
- `public/good.html` (good.arcs.care): "Open tools, honest by default" and "Nothing here claims an
  install path that is not live" are reliance statements; future cards follow the rule.
- github.com/flashesofbrilliance/check-it-before-you-say-it: the README opens with the same two halves.

---

## W — Window

**Horizon:** QUARTER
**Revisit trigger:** a surface that cannot state a reliance boundary honestly (for example, one whose
behaviour depends on a model with no mechanical half), or reader evidence that the two-halves
framing confuses more than it clarifies.

---

## Context

On 2026-09-30, after the tool's own explainer video failed its claims check (84 of 111 lines flagged
for saying the tool does work only a person does), the next draft of the product page proposed a block
headed "Why you can trust it". Zach asked whether "objectively trustworthy" was the right way to think
about it (witness `_STATE/witness/2026-09-30.jsonl`). It was not, for three reasons:

1. **Trust is not a property of a tool.** It is a relation between a tool and a job. The same checker
   is fully reliable for "does every marked fact name a source" (deterministic: the same input always
   gets the same stamp) and not reliable at all for "is this fact true" (it never looks).
2. **Deterministic is not objective.** The rules are mechanical, but a person chose them. The
   too-agreeable threshold (agreements divided by disagreements plus one, above 4) and the rubric pass
   floors are choices, and the floors are not yet calibrated against outcomes.
3. **The trust that matters is the reader's in the author, not the author's in the tool.** A checker
   does not make anyone trustworthy; it makes claims traceable.

The same session produced two other overclaims of this class: the page's scope line ("every fact says
where it came from"; true only of marked facts) and the post's statement of the too-agreeable rule
(corrected in PR #672). The class recurs, so it earns a rule rather than a fix per instance.

---

## Options Considered

### Option A — Keep "trust" framing, tighten the claims
- Say "trustworthy" but qualify it.
- Pro: familiar marketing register.
- Con: the qualifier is where the overclaim hides; it invites the reader to over-rely and puts the
  burden of the boundary on them.

### Option B — Reliance boundary, two halves (chosen)
- Every public surface says what it can be relied on for and what it cannot, plainly.
- Pro: true by construction; matches the brand promise to refuse to overclaim; makes the honest limit
  visible where a reader decides whether to use the thing.
- Con: reads less confident; costs a few lines of copy per surface.

### Option C — Say nothing about reliability
- Let the surface speak for itself.
- Pro: no copy cost.
- Con: readers fill the silence with an assumption, usually the generous one; the video overclaim was
  exactly that silence filled with a natural sentence.

---

## Decision

**Chosen:** Option B.

**Rationale:** It is the only option that is true for every reader at once, and it turns the honest
limit into a feature a reader can check. It is also the principle the product itself enforces: the
person owns the judgment, the rules own the stamp.

**Trade-offs accepted:** marketing copy that sounds less certain; a small, recurring copy cost on each
new public surface.

**Rule of thumb for authors:**

| Write | Not |
|---|---|
| "You can rely on it for X. Not for Y." | "You can trust it." |
| "The same input always gets the same stamp." | "It is objective." |
| "It checks the facts you mark." | "It checks your facts." |
| "A person chose these thresholds." | "Industry-standard thresholds." |
| "You do not have to trust it: every check is visible." | "Trusted by N teams." |

---

## Y — Conviction

**Polarity:** YELLOW
**Conviction:** HIGH
**Stability:** STABLE

**Loki test:** Strongest case against this decision: buyers respond to confidence, and a page that
leads with its limits may convert worse than one that leads with a promise. Unmeasured. If honest.arcs.care
or a later surface shows the reliance block costing engagement with no gain in qualified use, revisit the
placement (lower on the page), not the honesty.

---

## Consequences

- honest.arcs.care gets a "What you can rely on it for, and what you can't" block in place of the
  drafted trust block (the page refresh that follows this ADR).
- New public surfaces (NFTT posts, good.arcs.care cards, tool READMEs) state a reliance boundary when
  they describe a tool.
- Candidate gate, not built here: a lint over `public/*.html` that flags "trustworthy", "trust us" and
  "objective" in self-description. Build it only if the class recurs after this ADR (Frustration Gate,
  AGENTS.md #15).

**Implementation pointer:** PR #670 (post section VI); the honest.arcs.care page refresh PR; the public
repo README (commit 7382226 in check-it-before-you-say-it).

---

## Linked receipts / ADRs

- ADR-068: the print schedule the tool implements.
- Receipts: `2026-09-30--nftt-video-post-reliance-frame--ZH`, `2026-09-30--nftt-ratio-rule-correction--ZH`,
  `2026-10-03--check-it-public-repo--ZH`.
- Witness: `_STATE/witness/2026-09-30.jsonl` (the "objectively trustworthy" question, ratified).
- Memory: `brand-promise-refusal-to-overclaim`.
