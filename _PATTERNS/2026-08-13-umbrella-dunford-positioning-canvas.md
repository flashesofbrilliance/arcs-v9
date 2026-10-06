# The ARCS umbrella — April Dunford positioning canvas

**Status:** POSITIONING CANVAS (draft for owner review) · 2026-08-13 · ARCS-private (strategy)
**Method:** April Dunford, *Obviously Awesome* — the 5-component canvas (competitive alternatives →
unique attributes → value themes → target-market characteristics → market category → +trend), then an
assembled positioning statement, stress-tested with the 5 whys.
**Subject of positioning:** the **open ARCS family**, embodied by the umbrella front door
(germinate as anchor + the headless meta-CLI + the labs.arcs.care head). NOT ARCS-the-private-product —
that is the paid layer this funnels into (ADR-053/054).
**Grounds on:** `~/germinate/README.md` + `docs/adjacencies.md` · `_STATE/2026-08-13-oss-family-*` ·
[[oss-family-founder-led-growth-surface]] · [[seed-monetization-free-to-hold-metered-to-fire]]

> **Unit-of-analysis note (why the umbrella, not each repo).** Dunford positions *a product in a market*.
> The 8 repo one-liners are differentiators (her components #1+#2 only); running the full framework on a
> toolbar-cleaner is a category error. The umbrella/germinate is the thing with a market — so the full
> canvas lives here, and the repo lines inherit their *value* vocabulary from §3 below.

---

## 1. Competitive alternatives (what someone uses if the family didn't exist)

Dunford's rule: alternatives are what the customer would *actually* do, not the products you wish you
competed with. For "durable, trustworthy state across an agentic workflow," the real alternatives are:

- **Hand-rolled conventions** — a `HANDOFF.md` / `CLAUDE.md` file, a scratch notes doc, "it's in my head."
- **Framework-native persistence** — LangGraph checkpointers, framework agent-memory / vector stores.
- **Experiment trackers** — MLflow / W&B run notes (for the belief-log/hypothesis use).
- **Raw git + discipline** — commit often and hope the untracked context stays coherent.
- **A pile of disconnected one-off skills/scripts** — each solving a slice, none interoperating.

**The category-defining gap they share:** all of them either (a) leave the *advisory* state — everything
not git-tracked — invisible and un-checked, or (b) lock the state inside one framework/vendor as a
black box. None makes the **serialized-vs-advisory gap** both visible *and* enforceable, and none is
provenance-carrying by construction.

## 2. Unique attributes (what the family has that the alternatives lack)

Only include attributes that are *true today* and *differentiated*. Verified against germinate's README
+ SPEC:

1. **Serialized-vs-advisory made enforceable** — `drift-check` / `serializability` gates exit non-zero;
   the gap isn't just documented, CI trips on it.
2. **Runtime-agnostic, one contract** — a single seed/belief-log/manifest schema verified across
   **Node · Python · Rust · POSIX** against one shared conformance suite. (Proof, not just claim.)
3. **Provenance-carrying by construction** — append-only belief-log, lineage genetic markers
   (`g1:<sha>` + parents), hash-chainable → tamper-evident. Not a bolt-on.
4. **Crosses every boundary** — time · session · branch/worktree · context · environment · agent. Git
   solves *order* for tracked files; the belief-log solves it for *understanding*; the manifest for the
   surfaces git can't lock.
5. **Dependency-light · local-first · git-native** — no platform to import, airgap-deployable
   (`--trace tenant` = the tenant boundary), no vendor lock-in.
6. **Composable family via one `--json` contract** — the umbrella *dispatches over* standalone tools,
   never vendors them; adopt one, they interoperate.
7. **Publishable without leaking** — redaction-by-reference (public ledger / private rosetta): publish
   the trace, keep the substance private.

## 3. Value themes (attributes → what the customer gets) — the repo lines inherit these

| value theme | one-line customer payoff | backed by attributes |
|---|---|---|
| **Trust** | Multi-agent work can't silently corrupt shared state. | #1, #2, #4 |
| **Continuity** | A cold session / new agent starts on ground truth, not stale assumptions. | #4, #6 |
| **Auditability** | Every belief and decision carries dated, evidence-backed provenance. | #3, #7 |
| **Portability** | Your state runs anywhere and outlives any one framework or vendor. | #2, #5 |
| **Composability** | Adopt one tool; get a family that interoperates through one contract. | #6 |

The umbrella's *headline* value = **Trust + Continuity**: *trustworthy, continuous state across every
boundary agentic work crosses.* Auditability/Portability are the deeper hooks for the regulated/forensic
and no-lock-in buyers.

## 4. Target-market characteristics (who cares *a lot*, not just who *could* use it)

Best-fit customers share these observable traits:

- **Runs multi-agent or multi-worktree agentic dev** — concurrent workers who must reconcile without
  lost updates (this is the acute-pain segment).
- **Already feels the cold-start / drift tax** — Claude Code / agentic-IDE power users re-deriving
  context every session and getting subtly-wrong assumptions.
- **Distrusts black-box agent memory** — wants glass-box, git-native, inspectable state.
- **Provenance matters** — regulated, forensic, or high-consequence decision contexts where "when did
  we first believe X, and what moved it" is a real question.
- **Values local-first / no-lock-in** — airgap or data-sovereignty constraints, or just allergic to
  vendor capture.

Anti-fit (say it out loud): single-agent, single-session, throwaway scripting with no audit need — the
value ceiling is low and they should not be chased.

## 5. Market category / frame (the Dunford crux — the context that makes the value obvious)

The frame is a *choice*, and the wrong frame buries the value. Evaluated:

- ❌ **"Agent memory"** — crowded; connotes a black-box vector store. We're the opposite (glass-box,
  git-native). Fighting an incumbent frame on its terms.
- ❌ **"Observability for agents"** — the belief-log *is* OTel-shaped, but the frame implies dashboards;
  under-sells the *enforcement* (gates that trip) and the *provenance*.
- ✅ **"The provenance + state layer for agentic development"** — positions as **infrastructure beneath
  the agent**, not another agent. Makes Trust/Continuity/Auditability the obvious payoff.

**Anchoring analogy (the frame's carrier):** *"Git already versions your files. germinate versions your
team's — and your agents' — understanding."* One sentence, and the whole value stack becomes obvious to
a developer.

## 6. Relevant trend (layer on, don't lead with)

Agents now write and act on most of the code, but their *state* is ephemeral and untrusted — and audit
pressure on AI-made decisions is rising. Multi-agent / multi-worktree is going from exotic to default.
The provenance+state layer is the missing infrastructure that shift creates demand for. (Dunford: a
trend gives urgency, but only *after* the category frame lands — never lead with it.)

---

## The assembled positioning statement

> **For** teams running multi-agent or multi-worktree agentic development **who** keep losing trustworthy
> state across sessions, branches, and agents, **the ARCS open family** is a **provenance + state layer
> for agentic development** that makes the gap between git-tracked and advisory state **visible and
> enforceable** — one seed/belief-log/manifest contract, verified across four runtimes, provenance-
> carrying by construction. **Unlike** HANDOFF.md conventions or framework-locked checkpointers, it is
> runtime-agnostic, local-first, and publishable without leaking. *Git versions your files; this
> versions your understanding.*

**One-liner (umbrella tagline candidate):** *Durable, trustworthy state across every boundary your
agents cross.*

## The funnel ladder to ARCS (the GTM, per ADR-054)

Positioning the *open* family is deliberately the top of the funnel:
- **Free to hold** — germinate + the skills + the umbrella are the open public good (adopt → meet the
  discipline → meet ARCS). This is the founder-led / dev-tool-led growth surface.
- **Metered to fire** — the private ARCS *vox animus* (ripeness judgment, Kairos activation) is the paid
  spark on top. The open family creates the credibility and the install base; ARCS monetizes activation.

The open positioning must therefore be *complete and honest on its own* (it has to earn adoption without
mentioning ARCS), while leaving a clean seam upward. The canvas above does that: nothing here depends on
the private layer.

---

## 5-whys stress test on the umbrella statement (does IT survive?)

- Makes serialized-vs-advisory enforceable across runtimes → **why care?** → advisory state drifts
  silently between agents/sessions → **why care?** → an agent acts on stale understanding → **why
  care?** → you ship a bug, redo work, or a wrong decision reaches prod → **why care?** → in multi-agent
  workflows this is the *dominant, invisible* failure mode → **bottom:** *"I can't trust multi-agent work
  not to silently corrupt state, and I can't prove after the fact what was believed when."*

Bottoms out at a pain the target buyer feels acutely and can't currently solve → **survives.** Crucially,
the surviving value (*trust + auditability*) is now *in* the statement (§"assembled") — which is the fix
the repo one-liners still need (they stop at the mechanism).

## How the 8 repo lines inherit from this

Each repo's differentiator should append a **"…so that [value theme]"** clause drawn from §3, so the
line crosses from attribute to value (the gap the earlier review found). Mapping:
- germinate → **Trust**; state-sync → **Continuity**; token-savings-bank → cost (a Portability-adjacent
  "stop paying premium rates for cheap work"); rca → auditability-of-fixes ("not re-diagnosed next
  month"); linkedin-toolkit → **Portability/privacy** ("data never leaves your machine"); the rest are
  honest-niche and keep low-ceiling value.

## Next (gated)
1. Owner review of category frame (§5) — the single highest-leverage choice; everything downstream
   inherits it.
2. On approval, fold the value clauses into the 8 repo lines (part (b) of the review) + into the umbrella
   README when the aggregator repo is greenlit.
3. Optional: a one-page public version of §5's frame + tagline for the umbrella repo README (owner-gated).
