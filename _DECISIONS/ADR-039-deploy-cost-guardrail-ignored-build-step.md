# ADR-039 — Deploy Cost Guardrail: Path-Based Ignored-Build-Step

> **Status:** DECIDED
> **Date:** 2026-08-01
> **Commit:** (set at merge)

---

## D — The Decision

**Sharp question:** How does arcs-v9 stop non-shipping commits (docs, handoffs, session state, Claude Code tooling) from triggering full paid Vercel production builds, without accidentally skipping real shippable changes?

---

## E — Entity / System

Vercel project `arcs-v9` (`prj_aKmLj1UvT2oaDSH4KIAqEPaULqx9`, team `team_narCbxUgS4eiieJKRv1QMfff`) — specifically its `commandForIgnoringBuildStep` setting. Affects every push to `main`, which the GitHub integration builds. Downstream: build-credit spend, and any iteration loop on a hosted surface (e.g. `/omakase`, `louisville.arcs.care`, future Tao hosting).

---

## W — Window

**Horizon:** QUARTER
**Revisit trigger:** a new class of non-shipping files enters the repo (add its path to the exclude list); or Vercel changes the ignored-build-step contract; or the app's shippable surface stops being `public/` + `src/`.

---

## Context

Diagnosed 2026-08-01: `list_deployments` showed every commit to `main` firing a full production build, including pure docs commits — `docs(handoff): v3.19.0` and `docs(handoff): v3.20.0` both built READY. ~20 production builds fired across the Louisville session window, one per polish/docs commit.

Two distinct failure modes have now hit this same setting:
1. **2026-07-25 (ADR-context prior):** the command had inverted logic — a leading `!` — so real code commits CANCELED and docs commits built. Fixed by removing the `!`. (memory `vercel-ignored-build-step-was-inverted`.)
2. **2026-08-01 (this ADR):** logic was correct, but the **exclude list was incomplete**. `docs(handoff)` commits touch `.claude/arcs-session-state.md`; `.claude/` was not excluded, so `git diff` saw a change and exited 1 (build). Confirmed: `953effc docs(handoff): v3.20.0` deployed READY.

Vercel contract: `commandForIgnoringBuildStep` runs per deploy; **exit 0 = skip the build, exit 1 = build**. `git diff --quiet` exits 0 when there are no differences in the pathspec, 1 when there are. So the correct shape is a plain (non-negated) `git diff --quiet HEAD^ HEAD -- . :(exclude)<non-shipping paths>`.

---

## Options Considered

### Option A — Path-based exclude list (chosen)
- `git diff --quiet` over `.` minus an exclude list of non-shipping paths.
- Pros: deterministic; keyed on what actually ships, not on human-authored commit metadata; a `public/` or `src/` change always builds.
- Cons: exclude list must be maintained when a new non-shipping file class appears.

### Option B — Key skip off the commit message (`[NCI:SKIP]`)
- Skip when the subject carries `[NCI:SKIP]`.
- Pros: no path list.
- Cons: **wrong.** A `[NCI:SKIP]` commit can still touch shippable `public/` content — e.g. `47b5700 polish(omakase): … [NCI:SKIP]` changed `public/omakase/index.html` and *must* build. Message tags do not track shippability.

### Option C — Do nothing / manual redeploys
- Pros: none.
- Cons: silent credit burn; canceled-vs-ready ambiguity already caused wrong "deployed" claims.

---

## Decision

**Chosen:** Option A.

Current setting (via `PATCH /v9/projects/<id>`):
```
bash -c "git diff --quiet HEAD^ HEAD -- . \":(exclude)_MEMORY\" \":(exclude)_PATTERNS\" \":(exclude)_ARCHIVE\" \":(exclude)_STATE\" \":(exclude).claude\" \":(exclude)CLAUDE.md\" \":(exclude)MEMORY.md\" \":(exclude)AGENTS.md\" \":(exclude)WORLD.md\""
```
`.claude` was the field added 2026-08-01.

**Rationale:** shippability is a property of *which files changed*, not of the commit message. Path-based excludes are the only mechanism that can't be fooled by a `[NCI:SKIP]` tag on a real content change.

**Trade-offs accepted:** the exclude list is a maintenance surface — a new non-shipping directory needs a one-line addition (that's this ADR's revisit trigger).

---

## Y — Conviction

**Polarity:** GREEN
**Conviction:** HIGH
**Stability:** STABLE

**Loki test:** Strongest case against — the exclude list silently rots as the repo grows, and a new docs dir starts triggering builds again unnoticed. Mitigation: verification discipline below (canceled != ready), and this ADR's explicit revisit trigger. A future hardening would be a CI check or a test asserting the exclude list covers all known non-shipping roots.

---

## Consequences

- Docs-only / handoff / session-state / `.claude/` commits no longer build. Verified live: docs-only commit `a1fed75` → deployment **CANCELED** (skipped), while `public/` changes still build **READY**.
- **Verification discipline (load-bearing):** a skipped build shows as **Canceled**, not Ready. After pushing, confirm the newest production deployment's state before trusting a URL — a 200 can be the previous build. `vercel redeploy` re-runs the ignore step, so it does not bypass a broken one.
- Vercel Agent audit (same session): both on-demand billing burners confirmed OFF via `GET /v2/teams/<id>` — `agent.codeReview.auto.enabled=false` and `alertInvestigation.enabled=false` ("Investigate Anomalies Automatically", stale "left ON" note from handoff v3.18.0 now corrected). These are API-readable; no dashboard trip needed to check.
- Generalized as an impeccable-skill cost-discipline anti-pattern (SKILL.md → Cost discipline; reference/init.md captures deploy-cost constraints into PRODUCT.md; reference/live.md frames local iteration as the cost-correct loop).

**Implementation pointer:** Vercel `commandForIgnoringBuildStep` (not a repo file); documented in `_PATTERNS/durable-gotchas.md` (commit `a1fed75`) and memory `vercel-ignored-build-step-was-inverted`.

---

## Linked receipts / ADRs

- Relates to the deploy-efficiency posture in memories `vercel-deploy-efficiency-rules`, `vercel-config-via-cli-token-rest-api`, `vercel-ignored-build-step-was-inverted`.
- Governs cost discipline for iteration on all hosted surfaces (ADR-036 repo-split public/private context).
