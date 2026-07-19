# ADR-035 — Split the repo: public app / private sensitive

- **Status:** ACCEPTED (owner decision, 2026-07-19) — execution pending
- **Y-gate:** YELLOW / HIGH / REVISIT — the decision is firm; the *history-rewrite* step is irreversible and must be staged carefully
- **Supersedes question raised in:** `_PATTERNS/public-repo-exposure-audit.md` (J2)
- **Relates to:** ADR-032 (zero-trust posture), ADR-031 (secrets), Issue #77

---

## Context

`flashesofbrilliance/arcs-v9` is a **public** repo. The J2 exposure audit
(`_PATTERNS/public-repo-exposure-audit.md`) found three classes of sensitive
content living in public git history and committed files:

1. **Named-person material** — prospect dossiers, recoil reports, and
   discovery-call artifacts referencing real, identifiable people who did not
   consent to public publication of a profile about them.
2. **Unpublished IP** — the Yellow/White paper drafts. These were never
   published; committing them to a public repo may start a §102 prior-art clock
   and weakens patent optionality. (The papers are internal drafts — this ADR
   does not change that; it changes where they live.)
3. **Patent strategy** — the stack-ranked pressure-test / triage content, now
   gated off public pages to `/internal`, but **still present in git history and
   in committed ADRs**. Gating a rendered page does not un-publish the history.

Gating (already done for the live pages) addresses *presentation*, not
*provenance*. The content is still `git clone`-able by anyone.

## Decision

**Option B — split.** Two repos:

- **`arcs-v9` (stays public)** — the Next.js app, operators, canon that is
  meant to be public, sanitized subdomain pages, non-sensitive ADRs.
- **`arcs-v9-sensitive` (new, private)** — named-person dossiers, recoil
  reports, Yellow/White paper drafts, patent strategy/triage, and any ADR whose
  body contains the above.

Public history is **rewritten** to purge the sensitive classes; the sensitive
content is preserved in the private repo with full history.

Rejected alternatives:
- **A. Make the whole repo private** — cleanest for exposure, but throws away
  the public-portfolio value of the app/canon, which is a real asset. Over-broad.
- **C. Scrub in place, stay public** — keeps one repo but still requires the
  same history rewrite; loses the durable home for the sensitive material (it
  would have to be deleted, not relocated). Split keeps the material, just
  private.

## Why this ordering (the irreversible step is last)

A history rewrite on a public repo is a one-way gate (per WORLD.md: treat a
0-margin operation as a design bug — add protection, don't optimize grip). The
execution plan front-loads the reversible, verifiable steps and gates the
`filter-repo` push behind an explicit confirmation.

## Execution plan (staged — do NOT run as one shot)

1. **Inventory freeze.** Produce the authoritative path/commit list of sensitive
   content from `_PATTERNS/public-repo-exposure-audit.md`. Each entry tagged
   class 1/2/3. This list is the single source of truth for what moves and what
   gets purged. **Owner reviews the list before anything is deleted.**
2. **Create `arcs-v9-sensitive` (private).** Push a copy of the sensitive paths
   *with* their history (via `git filter-repo --path ... ` into a fresh repo, or
   subtree export). Verify the private repo has everything before touching public.
3. **Verify preservation.** Confirm every class-1/2/3 artifact is readable in the
   private repo. This is the checkpoint — nothing is lost after this point.
4. **Rewrite public history.** `git filter-repo --invert-paths` the sensitive
   list out of `arcs-v9`. This rewrites SHAs and is **force-push + irreversible**
   for collaborators. Gate behind:
   - branch protection temporarily relaxed / coordinated (see #76),
   - all concurrent sessions quiesced (no in-flight branches — coordinate),
   - a fresh backup of the pre-rewrite public repo (bare mirror) kept offline.
5. **Invalidate the mirror.** GitHub caches + forks retain old objects. After the
   rewrite: check for forks, and treat anything already public as *already
   disclosed* — the rewrite limits future spread, it does not un-ring the bell
   for content that was already cloned. Note this honestly in the closing receipt.
6. **Re-point references.** Fix links in `CLAUDE.md`/`AGENTS.md`/ADRs that pointed
   at moved paths; add a stub in public ADRs where a sensitive ADR was removed
   ("moved to private repo — see arcs-v9-sensitive").

## Consequences

- **Positive:** exposure of classes 1–3 stops growing; named individuals are no
  longer publicly profiled; IP optionality is protected going forward.
- **Cost / honest caveats:**
  - Content already cloned/forked/indexed is **not** recoverable — this is
    forward-protection, not erasure. The closing receipt must say so.
  - History rewrite breaks every open branch/worktree SHA; concurrent sessions
    must be coordinated (ties to #76 branch protection and J14/#80 serializability).
  - Two repos = a new sync seam. Rule: sensitive content lives ONLY in the
    private repo; the public repo never re-imports it. Enforce via J24
    external-surface leak check extended to "no sensitive path in public."
- **Blast radius if done wrong:** a botched `filter-repo` that force-pushes
  before step 3 verification could lose the only copy of a paper draft. Step 3 is
  the hard gate; do not proceed past it without confirmation.

## Open sub-decisions (not blocking the ADR)

- Exact private-repo name (`arcs-v9-sensitive` proposed).
- Whether the live subdomain prospect pages (`public/*.html` — chan, status,
  fanatics, etc.) count as class-1. They are *intentionally public and
  sanitized*, so likely stay — but the audit list (step 1) must confirm each one
  carries no un-sanitized internal text before that ruling stands.

## Follow-ups

- Execution is a separate, owner-gated work session — this ADR authorizes the
  *decision*, not an unattended history rewrite.
- Update `_PATTERNS/public-repo-exposure-audit.md` J2 status → DECIDED (split).
