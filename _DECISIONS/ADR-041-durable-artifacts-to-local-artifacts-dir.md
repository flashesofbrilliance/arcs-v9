# ADR-041 — Durable Deliverable Artifacts Live in `_ARTIFACTS/`, Local-First

> **Status:** DECIDED
> **Date:** 2026-08-03
> **Commit:** (set at merge)

---

## D — The Decision

**Sharp question:** Where should a self-contained HTML deliverable (a spec deck, wireframe/animatic, one-off visual artifact) live so it survives the session, renders without any external dependency, and never triggers a paid build?

---

## E — Entity / System

The repo's `_ARTIFACTS/` directory and the session scratchpad
(`/private/tmp/claude-501/.../scratchpad/`). Affects any standalone HTML deliverable
produced during a session. Downstream: the Vercel ignored-build-step exclude list
(ADR-039), the claude.ai artifact-hosting path, and the local file-preview pane.

---

## W — Window

**Horizon:** QUARTER
**Revisit trigger:** `_ARTIFACTS/` starts holding files that *should* ship (then it needs
splitting), or claude.ai artifact hosting becomes reliably reachable on Zach's primary
network (then the hosted route regains value as a *secondary* share surface, never the primary).

---

## Context

Diagnosed 2026-08-03 while producing the "60-Second Read" chronograph onramp spec for Ahmed.
Three delivery surfaces were tried, in this order, and only the third worked:

1. **claude.ai Artifact** (`Artifact` tool) — published fine, returned a URL. But Zach hit a
   **Cloudflare block page** ("Sorry, you have been blocked — You are unable to access claude.ai"),
   affecting artifacts *and* other claude.ai content. Network-layer block, before account/file
   matters. Not fixable from the agent side. **A hosted artifact is only as good as the viewer's
   ability to reach the host.**
2. **Scratchpad file** (`SendUserFile` from `/private/tmp/.../scratchpad/`) — renders locally,
   no claude.ai. But the scratchpad is **session-temporary**: it vanishes, and a `ls` of the repo
   root does not show it, which read as "the file isn't working" (the file was fine; it was in a
   path Zach did not expect and would not persist).
3. **`_ARTIFACTS/<name>.html` in the repo** (this ADR) — renders in the local file-preview pane
   with **zero claude.ai dependency**, is version-controlled so it survives the session, and sits
   in a directory already on the ADR-039 ignored-build-step exclude list, so saving it triggers
   **no Vercel build**.

The self-contained-HTML property (all CSS/JS inline, no external assets/fonts/fetch) is what makes
local rendering work with no server. `file://` opens directly in a browser; a local server is only
needed if a hardened browser blocks inline `<script>` under the `file://` origin.

---

## Options Considered

### Option A — Save durable deliverables to repo `_ARTIFACTS/`, local-first (chosen)
- Self-contained HTML committed to `_ARTIFACTS/`; viewed via the local preview pane or a browser.
- Pros: survives the session (git-tracked); renders with no external dependency, so a claude.ai /
  network block cannot stop it; already build-excluded (ADR-039) so it costs nothing; discoverable
  at an expected repo path.
- Cons: not a shareable URL — for an external recipient it still needs a deploy or file send.

### Option B — claude.ai Artifact as the primary delivery
- Pros: instant hosted URL, live rendering, theme-aware.
- Cons: **depends on the viewer reaching claude.ai.** Cloudflare/VPN/corp-network blocks make it
  unreachable, and the agent cannot clear that. Fine as a *secondary* convenience, never the SSOT.

### Option C — Leave it in the session scratchpad
- Pros: zero repo footprint.
- Cons: **ephemeral** (lost with the session) and lives at an unexpected path, which reads as
  "missing / broken." Fine as a working-file staging area, wrong as the resting place.

---

## Decision

**Chosen:** Option A.

Durable, self-contained HTML deliverables are saved to `_ARTIFACTS/<name>.html` in the repo,
authored to be fully self-contained (inline CSS/JS, no external assets), and viewed locally.
The scratchpad remains the staging area during a build; claude.ai Artifact remains an *optional
secondary* share surface, offered but never relied on as the only copy.

**Rationale:** the delivery surface must not have a single point of failure the recipient cannot
control. A committed, self-contained local file has none: no host to block, no session to expire,
no build to pay for. This is the same principle as ADR-039 (cost) and the static-public-files
gotcha (host reachability) applied to *deliverables* rather than shipped product.

**Trade-offs accepted:** `_ARTIFACTS/` files are not URLs, so sharing with an external party still
requires a deliberate send or deploy. That is correct: durability and shareability are separate
decisions, and defaulting to durable-local keeps a private artifact from leaking to a host by reflex.

---

## Y — Conviction

**Polarity:** GREEN
**Conviction:** HIGH
**Stability:** STABLE

**Loki test:** Strongest case against — `_ARTIFACTS/` becomes a junk drawer of stale one-offs that
rot and mislead. Mitigation: it is deliberately *not* a shipping surface (build-excluded, not
served), so rot there is inert; and durable artifacts carry their own "parked / status" footer so a
future reader knows the state. A second objection — "we lose the nice hosted URL" — is answered by
keeping claude.ai Artifact available as an explicit secondary, chosen per-artifact, not by default.

---

## Consequences

- New default: a session that produces a self-contained deliverable saves it to `_ARTIFACTS/`
  (git-tracked, build-excluded) and offers the claude.ai Artifact / file-send as *additional*
  routes, not the only copy.
- **Verification discipline:** confirm the artifact renders in the local preview pane (no claude.ai)
  before treating delivery as done. If the preview says "Couldn't preview this file," the file is
  missing at that path — check where it was actually written, do not assume a render bug.
- Reinforces ADR-039: `_ARTIFACTS/` must stay on the ignored-build-step exclude list. If it is ever
  removed, saving an artifact would start triggering builds (that link is this ADR's dependency on 039).
- Banked as anti-patterns in memory: `[[deliverable-durability-local-first-not-hosted]]`,
  and the claude.ai-block triage folded into delivery guidance.

**Implementation pointer:** `_ARTIFACTS/sixty-second-read.html` (first instance);
`_ARTIFACTS/` already excluded in Vercel `commandForIgnoringBuildStep` (ADR-039).

---

## Linked receipts / ADRs

- **ADR-039** (deploy cost guardrail) — `_ARTIFACTS/` is build-excluded there; this ADR depends on it.
- Relates to memory `static-public-files-worldreadable-client-gates-theater` (host-reachability /
  where files live), `souvenir-ship-ritual` (self-contained SHARP artifacts), and the
  build-reusable-decomposable-default posture.
