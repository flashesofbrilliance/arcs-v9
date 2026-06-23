# Pickup — Trust Contract vs. Zak's feedback (RESOLVED, one residual question)

> Paste as the first message in a fresh thread. Self-contained — no other file needs
> reading first, though `_CANON/trust-contract.md` is the actual target if there's more
> to do.

## What this was, and what it turned out to be

Zak (Zach's contact) gave feedback in a chat thread (16–22 June) on what ARCS needed
before he'd trust it with sensitive decision material. His checklist, verbatim:

> "the missing layer may not just be a privacy policy in the legal sense, but a visible
> trust contract in the product itself: what is stored vs ephemeral · whether inputs
> train anything · whether there is export/delete · what a lightweight/open-source
> version can run locally · what kinds of decisions ARCS is and is not designed to
> handle · how much confidence the user should place in the output"

Plus two framing questions: *"why would I want to trust a system I did not build myself
with my human decision making/judgement"* and *"how will you catch people at the fork
the system is solving for"* — and a positioning note: ARCS should feel less like
"submit your uncertainty into a black box" and more like "a disciplined reasoning
instrument you control."

**Checked against `_CANON/trust-contract.md` (verified, not assumed) — it already
covers all six checklist items, in the same order:**

| Zak's item | Section |
|---|---|
| stored vs. ephemeral | §1 |
| inputs train anything | §2 |
| export/delete | §3 |
| lightweight/open-source local version | §4 |
| what ARCS is/isn't designed for | §5 |
| confidence calibration | §6 |

§7 ("Your autonomy is the point") directly answers the "why trust a system I didn't
build" framing: *"The goal is not that you trust ARCS. The goal is that you trust your
own judgment more."*

**Timestamps confirm this isn't coincidence:** Zak's "valuable feedback" close-out was
22 June, 12:03 PM. The document was committed `2026-06-22 16:04:44 -0400` — same day,
four hours later. The document is the response, already written. There is no rewrite
to do based on this feedback — that earlier framing (treat this as a wording-edit task)
was wrong, corrected after actually reading the file end to end against the real
checklist instead of the topic alone.

**One claim spot-checked, not just trusted from the doc's own text:** §3 says data
export "is on the near-term roadmap and not yet shipped." Confirmed via
`find src/app/api -iname "*export*"` → no matches. Still accurate as of this writing —
re-check if picking this up much later, since it's a roadmap claim that can go stale.

## The one thing that's actually still open

Zak's second framing question — **"how will you catch people at the fork the system is
solving for"** — is not directly answered anywhere in the document. §5 lists *what kinds
of decisions* ARCS handles, but not *how a user recognizes they're standing at one of
those forks* before they ever open the compass. That's arguably a product/onboarding-UX
question, not a trust-contract content gap — it's about discovery, not disclosure.

**Decide, don't assume:** ask Zach whether this belongs in the trust contract (a new
§8?), in product copy/onboarding (the homepage already gestures at this — "Name the
real fork" — per the earlier copy-rewrite plan, `parsed-leaping-nova.md`), or nowhere
yet (a real gap, parked, not actioned). Don't add a section to a `CANONICAL` document
without that decision made first — bumping the version for an unconfirmed addition is
the wrong default.

## Separately — don't conflate these two

The **trust-contract page** (a route that renders this document live — it has zero
product surface, confirmed via `find src/app -iname "*trust*"` returning nothing) is a
**different, older, already-tracked task** — see `MEMORY.md`, `CLAUDE.md`, and
`.claude/arcs-session-state.md` (all three reference it; the newer
`_STATE/cold-start-v3.1.0.md`, scoped to the unrelated 8-item governance backlog,
deliberately does not). Resolving Zak's feedback does not require building that page.
