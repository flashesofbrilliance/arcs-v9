<!-- The PR body is the decision receipt. Fill it so a future reader learns why,
     not just what. A thin body on a risky change is itself a drift signal. -->

## What & why
<!-- One or two sentences. The decision, not the diff. -->

## Design brief
<!-- REQUIRED at 800+ changed lines, 10+ files, or several parts: write
     _PROPOSALS/<date>-<slug>-design.md with `pr: <number>` and `artifact: <url>` in its
     frontmatter (spec, requirements, implementation plan), publish it as a private Artifact,
     and cite the path here. Mechanical or generated changes: write `design-brief: skip <reason>`.
     Checked by scripts/pr_brief_check.py at session start; update the brief's status when this merges. -->
- Brief: <!-- _PROPOSALS/... | design-brief: skip <reason> -->

## Blast radius
- [ ] Touches `public/**` or `next.config.ts` (prospect-facing / routing)
- [ ] Touches API routes, auth, schema, or env
- [ ] Touches a hosted surface (a push = a paid Vercel build)

## Drift / tech-debt receipt
<!-- REQUIRED if this fixes decay, or if it knowingly adds debt.
     If it adds debt: name it, and link/where the paying-down is tracked.
     "Blight or neglect" left unnamed is how drift compounds. -->
- Debt added / paid: <!-- none | describe -->
- SSOT respected? <!-- does this extend the single source of truth, or fork a copy? (ADR-031) -->
- Internal↔external air-gap held? <!-- no real names / internal paths on public pages -->

## Verification
- [ ] `bash scripts/tripwire.sh <changed public pages>` clean (auto-gated in CI on `public/**`)
- [ ] Live/preview checked, or `npx playwright test tests/family.spec.ts` green (E2E)
- [ ] Screenshot / evidence attached for UI changes

## Promotion criteria (see docs/PROMOTION.md)
- [ ] Required checks green: `Family Tripwire`, `ci`, and `Deploy Verify` will run post-merge
- [ ] This body stands alone as the receipt
