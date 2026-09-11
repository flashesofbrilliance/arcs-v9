# Architect Review — Triune Productization Proposal (grounded)

> Reviews: PROP-2026-09-12-USERN-EXTENSIBILITY-001
> Reviewer: Claude Code (architect/compiler), 2026-09-12
> Governing constitution: `_SPECS/job-search-invariant-shape.md`
> Method: verified every load-bearing claim against git/runtime; Hermes attestations carry zero
> evidentiary weight until confirmed. Findings below are what git actually shows.

## Verdict: APPROVE the direction. Adopt the topology, bind it to the six invariants, clear the gates.

The proposal is credible, not vapor. The portability crux (a User0-clean reusable core) is real, which
is the thing most such proposals fake. Two invariants and two schema details need to be bound before
`resume-tailor.arcs.care` is promoted.

## Verified real (git-confirmed)

- `resume-tailor-skill`: real; `.claude-plugin/plugin.json` + `SKILL.md` + (new) `skill.yaml`;
  **0 files with Zach/Harris hardcoding**. The "portable, harness-agnostic core" claim holds.
- `hermes-agent`: real repo with `skills/`, `plugins/`, `optional-skills/` (real dual-manifest landing spot).
- `_INBOX/evidence/role-dossier-schema.json` on `fresh-starts` (commit 99f4a68d): real and solid.
  Ternary `scout_verdict.classification` [ATTAINABLE/TRAP/UNDECIDABLE], required `raw_sources`,
  `retrieved_at`, core-required vs nullable `extension_intelligence`, Perplexity's TRAP flags present.
- `scripts/pii_leak_gate.py` (commit b10a363): a REAL gate. Stress-tested: fails-on-bad (exit 1 on a
  planted email + phone), passes-on-good (exit 0 on allowlisted). Not theater.
- `target-role-scan.json` v1.3 (PR #393): byte-identical on my branch and `fresh-starts` (no collision).
- `convergence.json` + `self-serve-atlas-scan-v1.md`: present on `fresh-starts` (Perplexity's
  "not found" was a ref mismatch: it checked `main`; the anchor lives on the plane. Everyone reads `fresh-starts`.)

## Described but narrower than claimed (harden before promotion)

1. **PII air-gap (blocker #1).** The gate is real redaction-QC (email/phone patterns in output files),
   but its "clean air-gap" banner overclaims: a file-content scan is not proof of *network* egress
   control, and it misses address/SSN/DOB. Before public promotion: either narrow the banner to
   "output redaction verified" OR add an actual egress/boundary assertion. Different guarantees.
2. **Surface reality.** `public/resume-tailor-pwa.html` is not on `main`/this branch (claimed on
   `feat/resume-pwa-theming`, unverified). Do not route the domain until the PWA is verified *rendering*,
   not grep-confirmed.
3. **Tenant isolation.** Supabase RLS row-scoping needs a passing isolation test (RLS silently hides
   rows; prove UserN cannot read UserM) before any second tenant.

## Schema collision — ESCALATE (do not let the landed version stand as "ratified")

Two divergent `role-dossier-schema.json` exist, and the wrong one is on the plane:

- **Perplexity's owner-draft** (the sensor's actual output): draft-07; `required: [dossier_id,
  generated_at, core, verdict, evidence]`; HAS per-claim `source_urls[]` and a `premortem` flag; ternary.
  Honors all 5 ratification bindings.
- **Landed on `fresh-starts` (99f4a68d, authored by Hermes)**: 2020-12; different required keys
  (`schema_version/target_role/company/scout_verdict/raw_sources`); `raw_sources` is dossier-level not
  per-claim; NO premortem flag. Honors ~3 of 5. 391-line diff from the owner-draft.

Hermes attested this "implements Perplexity's exact 5 binding requirements." Git contradicts that on two
of the five. It also breaks the agreed role boundary: **the sensor owns its output contract.** Hermes
(actuator) rewrote and shipped the sensor's schema unilaterally.

Resolution (not the architect's to force; escalated to the human + plane): reconcile the plane to
Perplexity's owner-draft, OR merge Hermes's richer company/salary fields INTO Perplexity's draft with
Perplexity's explicit sign-off. Either way the two non-negotiables from the bindings must survive:
per-claim provenance (invariant #4) and UNDECIDABLE -> human premortem (invariant #5). Until reconciled,
the schema is NOT ratified regardless of the convergence.json flag.

## The one gap the proposal omits (now added by the constitution)

**Invariant #2, the falsification loop.** The proposal logs `decision_receipt` (Stage 5 posterior) but
has no Stage 6: pre-registered hypotheses that test whether fit predicts conversion, and recalibrate the
rubric when it does not. Without it, the productized UserN engine optimizes fit *without proving it
converts* — the exact blind spot of the four FE studies. The hypothesis ledger
(`_STATE/job-search/hypothesis-ledger.md`) is the missing layer and must ship with the class, not just
User0's instance.

## Answers to the three review questions

1. **Boundaries / CANON_COLLISION:** sound and match the instance/class seam. The one real collision
   risk (three producers, one scorer, no shared record) is resolved by the ratified dossier schema as
   the Stage-1 contract. Register `bridge-scan.json` so the ADR/worktree sweep does not renumber it.
2. **Job-search lane integration:** clean. It IS Stages 1-3; the opportunity record is the join that
   feeds both scorer and resume-tailor. Add Stage 6 (above) so the lane carries falsification into the product.
3. **Failure modes to harden:** the three "described-but-narrower" items above, PII banner first.
