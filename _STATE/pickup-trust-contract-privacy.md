# Pickup — Trust Contract privacy wording (Zak's feedback)

> Paste as the first message in a fresh thread. Self-contained — no other file needs
> reading first, though `_CANON/trust-contract.md` is the actual target.

## The one blocker

**Zak gave Zach feedback on the privacy wording in `_CANON/trust-contract.md`. The
actual content of that feedback was never captured in this session** — only the topic
was confirmed ("wording/clarity of what trust-contract.md already claims — data
retention, what's stored for signed-in vs. anonymous users, etc."). Before editing
anything: **ask Zach what Zak actually said.** Don't guess at a rewrite from the topic
alone — that's exactly the kind of unverified-but-confident move this session's own
governance work (see `ALTITUDE_MISMATCH` / 5-verb-loop entries in
`_PATTERNS/2026-06-23-governance-roadmap.md` and the project memory at
`run-5-verb-loop-before-opining.md`) flags as a standing failure pattern.

## Once you have the actual feedback

Target file: `_CANON/trust-contract.md` — `Status: CANONICAL`, so any edit needs a
version bump (currently `1.0`) and a `MEMORY.md` entry per the doc's own amendment rule.

Section 1 ("What is stored, and what isn't") is the most likely target — current text,
for reference:

> **Your question (compass input):** Processed in real time and used to generate your
> result. If you are not signed in, it is not stored beyond your session — it exists
> only long enough to produce the receipt.
>
> **Your receipt:** If you are signed in, your decision receipt is stored in your
> account and accessible via your history. It is yours. If you are not signed in, the
> receipt is generated and displayed but not persisted to a named account.
>
> **Your debrief:** If you log an outcome (how the decision went), that is stored in
> your account linked to the receipt. This data is used to improve ARCS's ability to
> read terrain accurately over time — specifically, to validate whether the system's
> confidence grades correspond to real outcomes. It is never shared or sold.
>
> **System logs:** Standard infrastructure logs (request metadata, error traces) are
> retained for debugging. They do not contain your decision content.

Before rewriting wording, verify each claim against actual code, don't just polish
prose — this document is the authority other surfaces derive from, so an inaccurate
claim here is worse than an inaccurate claim anywhere else in the app:
- `src/lib/db.ts` — what's actually persisted, anonymous vs. signed-in
- `prisma/schema.prisma` — `Receipt`/`Outcome`/`PrepSession` models, what fields exist
- Any analytics/logging call sites that touch decision content (search for what
  "request metadata, error traces" actually means in practice — confirm it's true, not
  aspirational)

## Separately — don't conflate these two

The **trust-contract page** (a route that renders this document live — it currently has
zero product surface, confirmed via `find src/app -iname "*trust*"` returning nothing)
is a **different, older, already-tracked task** — see `MEMORY.md`, `CLAUDE.md`, and
`.claude/arcs-session-state.md` (all three reference it; the newer
`_STATE/cold-start-v3.1.0.md` for the unrelated 8-item governance backlog does not,
deliberately — different scope). Zak's feedback is about the document's *wording*, not
about building the missing page. Don't let "let's also ship the page while we're in
here" silently expand scope unless Zach asks for that too.
