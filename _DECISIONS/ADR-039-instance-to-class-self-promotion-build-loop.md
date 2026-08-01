# ADR-039 — Instance→Class Self-Promotion Build Loop (preferred build pattern)

> **Status:** RC — PROPOSED
> **Date:** 2026-08-01
> **Commit:** (set at merge)
> **Y:** GREEN / HIGH / STABLE
> **Relates to:** `tools/recoil-report/` (the instance→class exemplar this session), `omakase-pipeline`
> skill (the prior exemplar: jeben→omakase→louisville), the `tool-forge` skill (the mechanism),
> ADR-038 (recoil bookmark primitive), the head-first-build-loop + cut-not-add memories

## D — The Decision

**Sharp question:** When we build something concrete to solve one case (a Shannon recoil report, a
Louisville pitch suite), when — and how — should it be promoted from a one-off *instance* into a
reusable *class*? Promote too early and you abstract before you understand the shape (speculative
generality, the classic waste). Promote too late (or never) and every next case is a copy-paste
fork that drifts — exactly how the repo ended up with **three incompatible "recoil report" JSON
shapes** before this session.

**Decision (proposed):** Adopt **instance→class self-promotion** as the preferred build loop:

1. **Build the instance first**, concretely and WYSIWYG (per [[head-first-build-loop]]). Solve the
   actual case. Do not abstract yet.
2. **On the second real (or imminent) case**, promote instance→class — extract a **self-contained,
   composable package** with a fixed contract, rather than forking the instance. "Rule of three" is
   the ceiling, not the target: promote at two when the second is already in hand.
3. **The contract is fixed and uniform** (this is what makes them interoperable microservices):
   **deps · args · passthrough params · resources · runtime files · README manifest**, plus a
   machine-checkable **schema** for the data the tool consumes. Stdlib-only, zero-install, one
   entrypoint. `tools/recoil-report/` is the reference shape.
4. **Prefer subtraction on promotion** (per [[cut-not-add-provable-architecture]]): the class keeps
   only what is materially load-bearing across cases; instance-specific richness stays in the data,
   not the code.
5. **The promotion itself is tooled** — the `tool-forge` skill scaffolds a new package in this exact
   shape, so promotion costs minutes, not a redesign. Cheap promotion is what makes the loop
   *generative and compounding* instead of aspirational.

## E — Entity (who/what this governs)

Applies to any build that (a) produced a concrete artifact and (b) is about to be repeated. Owners:
whoever builds the second instance. Governs `tools/*`, engagement pipelines (`omakase-pipeline`),
and the recoil/report family. Does **not** mandate premature abstraction of genuinely one-off work.

## W — Window

Now, ongoing. Retroactive cleanup (unifying the three drifted recoil shapes onto one schema) is
**not** required by this ADR — the new schema is permissive and tolerant; convergence is
opportunistic, not a migration.

## Y — Y-Gate: GREEN / HIGH / STABLE

- **Polarity GREEN:** two independent exemplars already validate it (recoil-report this session;
  omakase-pipeline earlier). It is a description of what already works, promoted to a rule.
- **Conviction HIGH:** the anti-pattern it prevents (silent fork-drift) is concretely evidenced by
  the three-shape mess this session surfaced.
- **Stability STABLE:** the contract (deps/args/params/resources/schema/README) is small and
  general enough to hold across tool types.

**The honest edge / failure mode to watch:** the loop can become a *promotion compulsion* — turning
every one-off into a package because packaging is satisfying (the build-list disease in
[[external-artifact-eval-ground-and-skeptic-route]]). Guard: promote only on a real or imminent
**second** use, and let genuinely singular work stay an instance. Instance→class is a response to
repetition, not a substitute for judgment about whether repetition exists.
