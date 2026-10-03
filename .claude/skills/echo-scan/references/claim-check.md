# claim-check: verify an outside source before building on it

Nested stage 1 of `/echo-scan`, callable alone as `/echo-scan claim-check <source>`.

The repo's `claims-skeptic` agent checks documents against this repository. This module checks
content that came from outside it: a LinkedIn post, a news article, a screenshot, a paper's
abstract, a podcast quote. The ARCS rule is the same one receipts follow: anything not
verifiable goes in `what_unconfirmed`, never `what_confirmed`. A viral post is the kind of thing
that arrives feeling verified, which is why it gets checked first.

## Input
The source itself (pasted text, screenshot, URL). If it is an image, transcribe the claims
first; do not paraphrase numbers. Pasted text with no author, date, or link still gets
checked; its provenance row is THIN by default.

## Procedure
1. **Atomize.** Split the source into single checkable claims: one number, one date, one
   attribution, one causal statement per row. Keep the source's own wording short. Give an
   **implied** claim its own row when the post leans on it (a return rate presented as a
   given, "better than engineers" when the paper says "comparable"), worded as "Implied: ...".
   Then mark the **central claim**: the one that, if false, makes the post pointless. A famous
   name attached to a claim is usually borrowed authority, not the central claim.
2. **Find the primary record** for each claim: the journal paper (venue, volume, page, year,
   authors), the lab page, the dataset. News coverage is a pointer, not evidence.
3. **Recompute every number** the source derives (unit conversions, ratios, "X times
   slower"). Show the arithmetic in one line; `python3 -c` is fine.
4. **Check credit.** Who else did this, at the same time or first? Simultaneous discoveries
   and dropped co-authors are the most common silent error in popular science posts.
5. **When the primary page is unreachable** (paywall, proxy block, dead link), you may
   still give a verdict from consistent secondary summaries, but name the page you could not
   open in the Evidence cell. If secondary sources disagree, cap the verdict at UNCONFIRMED.
6. **Check provenance.** Shortened links, "CTTO" (credit to the owner), no author, reposts
   with the original removed: record it, do not chase it forever.
7. **Note what the source gets right about its own limits.** A good caveat in the source is
   evidence of care; say so.

## Verdict scale (use exactly these)
| Verdict | Meaning |
|---|---|
| CONFIRMED | a primary record says the same thing, or a recomputation reproduces the number (say which, and state the assumptions the number needs, such as annual compounding) |
| ROUNDED | right direction, number stretched (give the real figure) |
| INCOMPLETE | true but missing credit, conditions, or context that changes its weight |
| UNCONFIRMED | no primary record found in reasonable effort |
| FALSE | a primary record contradicts it. For a quote or attribution: an earlier origin by someone else, plus no record in the person's authoritative corpus or a standard quotation reference rating it spurious |
| THIN | provenance only (who wrote it, where it came from) is weak |

## Output
1. A table `| Claim | Verdict | Evidence |`, one row per atom, with the provenance row last.
   Mark the central claim with `(central)` in its Claim cell.
2. One summary line naming the substance and the attribution separately, in the shape
   "accurate science, generous rounding, thin sourcing" or "accurate arithmetic, fabricated
   attribution, missing conditions."
3. A short source list with URLs (in standalone mode this is the whole deliverable, so the
   reader needs the links).

## Stop rule
If the **central** claim is FALSE, stop and report. Do not scan a field built on a claim that
did not happen unless Zach asks to scan the real field instead. In standalone
`claim-check` mode the run ends here anyway; the rule then only decides the closing line.

## Privacy
The person who posted is usually a private individual. Name them in the working note if
useful, but in anything public (NFTT, shared pages) describe them ("a retired security
engineer's post") instead of naming them. Public scientists and their published work are
named normally.
