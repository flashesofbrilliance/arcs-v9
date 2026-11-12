# Red-team router: adversarial review by materiality, not by memory (2026-11-03)

Status: PROPOSED. Nothing is built by writing this. Spec only, per Zach ("Spec it", 2026-11-03).
Prior art: `chief-loki`, `chief-bayesian`, `chief-conductor` and the `idea-*` seats (`.claude/agents/`), the seed ledger and gate
(`runtime/specs/agent-seed-ledger.jsonl`, `scripts/agent_seed_gate.py`), door declared on backlog rows (`scripts/readiness_packet.py`; the compass's `doorClass` at `route.ts:52` infers door from stakes and horizon, so it is not prior art for a declared door), WRITE-LOCK (ROM primitive 7), the receipt form (`job_id`, `tool_id`, `supersedes`),
`scripts/safe_merge.sh`. Rules: `.claude/rules/coding-discipline.md` (grug first), memory `design-inside-the-trust-contract`.

## 1. The problem, with today's evidence

Adversarial review happens when someone remembers to ask for it. On 2026-11-03, in one session:
- `privacy-review`, run only because Zach asked, found a canon conflict and four wrong code claims in a proposal.
- `devils-advocate`, same, found the pass/fail bar was noise at n = 10 and that the 0-of-11 evidence was really 0-of-3 emailed.
- `grug` cut a 14-branch cleanup to two merges and a short ask list.
None of these would have run unprompted. `chief-loki` has 2 recorded uses in two weeks. The cost is not the review; it is the decisions
that went out without one.

## 2. Reviews of the first draft (2026-11-03)

The first draft of this spec went through two of the seats it proposes, which is the point of it.
- **`grug`** cut it to: two routes, enforced as a refusal at merge, a table the session reads, no script, no command, no domain seats,
  no receipt field, no learning loop yet, one synthesis step instead of two blue-team seats.
- **`chief-loki`** ran checks and broke the mechanics: `scripts/agent_seed_gate.py:18` covers only `idea-`, `chief-`, `scenario-`
  (3 of 10 seats) and accepts only `helpful`/`not_helpful` (line 43); a lifetime kill at 2 `not_helpful` with "no-change counts as
  unhelpful" kills a seat that changes 70% of decisions 99.2% of the time within 20 uses, and punishes `chief-conductor` for succeeding;
  `safe_merge.sh` has no notion of one-way and the repo has no such PR label; 78% of backlog rows (353 of 450) declare no door; the
  receipt enum has `critical`, the table did not; `devils-advocate` is a machine-local plugin, not a repo agent.

Where they disagree: grug cuts the learning loop; Zach asked for judgment that improves over time. This version keeps the loop in its
cheapest form (record, don't auto-grade) and drops the parts Loki showed would misfire.

## 3. The rule

**A one-way change does not merge until a red team has run on it.** One-way is decided by the files it touches plus the session's label,
not by memory. Two-way work is never blocked.

## 4. The routes (one file: `runtime/specs/red-team-routes.json`, read by the session)

| Route | When | Seats |
|---|---|---|
| **one-way** | The PR touches a one-way path (below), or carries the `one-way` label, or its stakes are high or critical | `chief-loki` and `grug` in parallel, then the session writes one synthesis: what changed, what was rejected and why |
| **two-way** | Everything else, including work with no declared door | none required; `grug` on request |

One-way paths (file rule, so 78% undeclared does not matter): `_CANON/**`, `prisma/schema.prisma`, `prisma/migrations/**`,
`src/app/{trust,privacy,terms}/**`, `src/app/api/account/**`, `vercel.json`, `next.config.ts`, `src/proxy.ts`. Zach edits this list.

Domain seats (`privacy-review` for data or policy pages, `ciso-review` for auth, `sre-review` for migrations) are added to the
one-way route only after a real one-way merge shows the gap. `devils-advocate` joins when it has a repo agent file, so the cast is the
same on every machine and harness.

### 4a. The synthesis keeps the disagreement (Zach, 2026-11-03)

Agreement is not the goal of the debate, and the synthesis must never manufacture it. A held impasse can be the load-bearing result:
it sorts the decision as cleanly as a consensus would. The `## Red team` section therefore has three parts, and the third is required
even when it is empty:
1. **Changed:** what the decision changed because of a seat, with the seat named.
2. **Rejected:** what a seat raised that the session overruled, and why, in the seat's own strongest wording, not a softened one.
3. **Held open:** each disagreement left standing. For each: both positions at full strength, the evidence that would settle it, and
   who owns the call to proceed anyway. This is a FORK held deliberately, not a defect to smooth over.

Two guards against sycophancy:
- A one-way synthesis that reports nothing rejected and nothing held open is flagged for a second look: a red team that found nothing
  to disagree with on a one-way change has more often been softened than satisfied.
- The session may not restate a seat's objection more mildly than the seat wrote it. Quote it.

Example from this spec's own review: grug said cut the learning loop; Zach asked for judgment that improves over time. Held open in
section 2, not averaged away.

## 5. Enforcement

`scripts/safe_merge.sh` already refuses on a head mismatch, a pending check or a conflict. Add one refusal: if the PR's changed files hit
a one-way path, or it has the `one-way` label, the PR body must contain a `## Red team` section naming each seat that ran and the
synthesis. Missing, refuse with the route and the seats to run. The label is created once (`gh label create one-way`).

## 6. Learning loop, cheapest form

Each seat run is appended to the seed ledger as a use with the existing verdict (`helpful` or `not_helpful`, judged by the session) plus
a separate `effect` field: `changed`, `premise-killed` or `no-change`. Nothing auto-kills on `no-change`. Two changes to the gate:
widen its pattern to the seats the routes name (`grug` today), and accept the `effect` field. Once a month, the drift sentry or Zach
reads each seat's effect rate and proposes one edit to that seat's `.md`. Composition (a named chain of seats) waits until the logs show
the same chain running repeatedly.

## 7. What this does not do

It does not decide (NOTOMATION): the routes pick reviewers, the session and Zach decide. It does not touch two-way work. It adds no new
agent.

## 8. Build order

1. `runtime/specs/red-team-routes.json` (routes and one-way paths) and the `one-way` label.
2. The `safe_merge.sh` refusal, with a self-test case for a one-way PR with and without `## Red team`.
3. Gate: widen the seed pattern to `grug`, accept `effect`.
No script, no command, no receipt field until a pattern in real use asks for one.

## 9. Open questions (Zach)

1. The one-way path list in section 4: add or remove paths.
2. Do high or critical stakes alone make a PR one-way, or only paths and the label?
