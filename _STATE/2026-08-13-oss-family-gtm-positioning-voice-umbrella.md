# OSS Family — GTM decisions: positioning · README voice · the ARCS umbrella

**Status:** DECISIONS (owner-approved forks; per-repo push still gated) · 2026-08-13 · ARCS-private
**Forked from:** the 2026-08-13 germinate / OSS-family conformance session (to keep context clean)
**Grounds on:** `_STATE/2026-08-13-oss-family-conformance-standard.md` · `_SEEDS/` (index + ledger) ·
`~/germinate/docs/adjacencies.md` §"The arcs umbrella" · ADR-053 (dormant seed / vox animus) ·
[[oss-family-seedbank-two-tier-conformance]] · [[oss-family-founder-led-growth-surface]]
**Boundary (ADR-053):** repos public, the `_SEEDS` registry + priorities private. **No public repo
was touched this session.** Per-repo pushes wait for explicit owner authorization.

> The ATG-FAQ eval (2026-08-13) found the portfolio-wide weak axis: **no repo names a nearest
> alternative** — every README says what it *is*, none says what it's *unlike*. This doc fixes that
> (decision 1), settles the founder-vs-neutral voice fork the founder-led-growth memory parked
> (decision 2), and scopes the umbrella aggregator without publishing it (decision 3).

---

## Decision 1 — Positioning: one-line nearest-alternative differentiator per repo

Each is grounded in the repo's actual README (read locally 2026-08-13), not its description field.
Shape: *"Unlike [nearest alternative], [repo] [the differentiated thing]."* **Owner approves each
line before it lands in a README.** These slot into the README skeleton as a positioning line
directly under the one-line "what."

| repo | tier | nearest-alternative differentiator |
|---|---|---|
| **germinate** | A (ref) | Unlike a HANDOFF.md convention or a LangGraph checkpointer, germinate makes the **serialized-vs-advisory** state gap enforceable — one seed schema verified across four runtimes (Node/Python/Rust/POSIX) against a single shared conformance suite. |
| **state-sync-skill** | A | Unlike a hand-maintained CLAUDE.md or scratch context notes, state-sync scaffolds one committed `snapshot.json` a cold session restores from with a single cheap file read — instead of re-deriving deploy/sync/decision state every time. |
| **rca-skill** | B | Unlike a 5-whys template or an ad-hoc "debug this" prompt, rca **gates on effort first** — a five-minute fix stays inline, subagent fan-out is reserved for incidents that earn it — then captures the root cause so it isn't re-diagnosed next month. |
| **fix-toolbar-comments-skill** | B | Unlike working the Vercel Toolbar queue by hand (open, fix, deploy, resolve — one thread at a time), it runs the whole fetch→fix→build→deploy→resolve loop in a single pass. |
| **token-savings-bank** | B | Unlike a static "just use the cheap model" rule or per-call price config, it installs a budget-mode **discipline** — right-tier routing, batched reads, small work kept inline, state checkpointed so nothing is re-derived. |
| **linkedin-connections-toolkit** | B | Unlike importing `Connections.csv` into a spreadsheet or a SaaS CRM, this is stdlib-only and offline — it parses LinkedIn's awkward export once and gives recency/concentration/seniority/staleness views on data you never upload. |
| **arcs-field-scan** | A (cand) | Unlike a résumé parser or profile summarizer, it turns a LinkedIn profile or PDF into an ARCS "energy scan" — a structured read of a person's field you can carry forward as a **seed**. |
| **arcs-claude-project-scaffold** | A (cand) | Unlike a bare `claude init` or a generic starter template, it plants a full ARCS Field scaffold (state-sync, drift, seed discipline) into a new Claude project from the start, instead of retrofitting it later. |

**Care:** these are *nearest* alternatives, chosen for legibility to a dev evaluating the repo — not
exhaustive competitor lists. Revisit if a named alternative (e.g. LangGraph checkpointer) changes
shape enough that the contrast no longer holds.

---

## Decision 2 — README/footer voice: **hybrid (neutral body + one founder byline)**

**Chosen (owner, 2026-08-13):** keep the tool-neutral ecosystem footer, **add exactly one founder
byline.** germinate MAY opt out to stay the purest neutral public good.

**Why hybrid, not either pole:**
- *Brand-neutral (prior default)* preserved germinate's credibility as a standalone public good — the
  adjacencies doctrine is explicit: "its identity is not `arcs/tools/germinate`." Adoption-first.
- *Founder-forward* is the growth motion the [[oss-family-founder-led-growth-surface]] memory names:
  the public git history is already authored under the builder's identity; the repos double as
  founder-led / dev-tool-led / media-led top-of-funnel. But the builder is never **named on the page**.
- The hybrid keeps the body tool-neutral (credibility) and makes the founder **legible** with one line
  (growth) — no README becomes a pitch. The git identity was already there; the byline just surfaces it.

**Byline spec (one line, footer, above or beside the existing ecosystem block):**

```
Built by Zach Harris — <personal profile URL>.  Part of the open ARCS / flashesofbrilliance family.
```

- `<personal profile URL>` = owner to supply the canonical link (personal GitHub handle or site). Do
  **not** guess the handle; leave the token for owner fill before any push.
- **germinate opt-out:** allowed; if germinate keeps a byline, place it in `docs/` or the footer only,
  never in the opening lede — the opening must stay a neutral spec voice.

**Ride-along fix (found this session):** state-sync / rca / token-savings / linkedin / fix-toolbar each
carry the footer **twice** — a one-line "An open, MIT-licensed tool…" *and* a near-duplicate
"## Part of the ARCS ecosystem" block. Dedup to a single footer (neutral block + byline) in the same PR
that adds the byline. This is Tier-B presentation drift, not new work.

**Rollout:** batched into the existing Tier-B presentation PRs (one per repo, owner merges). Do NOT
re-push repos reflexively just for the byline — fold it into the next gated Tier-B pass.

---

## Decision 3 — The ARCS umbrella: **scope only (private spec; no public repo yet)**

**Chosen (owner, 2026-08-13):** write the umbrella architecture as this private spec + a ledger event.
**No public `arcs` repo created.** Standing up the public repo waits for explicit go-ahead (ADR-053).

### What it is (from `~/germinate/docs/adjacencies.md` §"The arcs umbrella")
A thin **aggregator, not a monolith**. The public goods stay standalone, independently-adoptable repos.
The umbrella **links to / dispatches over** them; it **never vendors** them. Two faces:
1. **Headless meta-CLI** — shells to each tool through its stable `--json` contract.
2. **Head mini-app** — same tools with a UI, on **labs.arcs.care** (the consumer-facing head of the funnel).

Same "wrap-the-core, never import the platform" pattern the adapters use, one level up: the umbrella is
a **launcher/registry** over standalone tools. Repo decision (from adjacencies): **two repos**; umbrella
scoped to `skills/` + the aggregator.

### The `--json` contract each tool must expose (the interop precondition)
The meta-CLI can only dispatch over tools that emit machine-readable output. Precondition per tool:
- a documented `--json` (or equivalent) mode that prints a single JSON object to stdout,
- a stable top-level shape: `{ tool, version, ok, result, error }` (accretes; no top-down taxonomy),
- non-zero exit on failure so the meta-CLI can aggregate verdicts.
Today only germinate has a mature `--json` surface. **This contract is the real gating work** — the
umbrella is cheap; making each tool speak `--json` is the engineering. Track per-tool `--json` status
as a future `_SEEDS` column or ledger events; do not build the meta-CLI against tools that can't answer.

### Meta-CLI dispatch shape (sketch)
```
arcs <tool> [args...]            # dispatch: shell to the standalone tool, pass --json, relay
arcs list                        # registry: enumerate known tools + their --json status
arcs doctor                      # check each registered tool is installed + speaks --json
```
The registry is a static manifest of `{ alias, repo, install-hint, json: yes|no|partial }` — a PUBLIC
subset of `_SEEDS/index.jsonl` (never mirror tier/priority/lab_candidate/routing into it; ADR-053).

### labs.arcs.care head (scope)
A single page that presents the same tools with a UI, sourced from ripe `_SEEDS` lab candidates
(`arcs-field-scan` is the ripe first per the seed bank). This is the same germination pathway the
`_SEEDS/README.md` already draws (`_SEEDS` → ripeness/Kairos → `/lab-mint` → lab.arcs.care). The head
is a **consumer** of the umbrella registry, not a separate build.

### Boundary check (ADR-053) — what stays private
The umbrella is **public** (a launcher over public tools). What stays private: the `_SEEDS` registry
itself (tier/priority/conformance/routing), the ripeness judgment that ranks lab candidates, and this
strategy doc. The umbrella's registry is a **flattened, presentation-only projection** of `index.jsonl`
— alias + repo + install + `--json` status only.

### Not done this session (needs explicit go-ahead)
- Creating the public `arcs` (umbrella) repo.
- Building the meta-CLI.
- Adding `--json` modes to the Tier-A/B tools that lack them.
- Standing up the labs.arcs.care head page.

---

## Ledger events recorded (`_SEEDS/ledger.jsonl`, appended this session)
- `positioning-drafted` (family) — 8 nearest-alternative differentiators, owner-approval-pending.
- `voice-decided` (family) — hybrid: neutral body + founder byline; germinate opt-out; dedup double-footer.
- `umbrella-scoped` (family) — scope-only private spec; no public repo; `--json` contract = the gating work.

## Next (all gated)
1. Owner approves/edits the 8 positioning lines → fold into README-skeleton PRs.
2. Owner supplies canonical personal profile URL for the byline.
3. Positioning + byline + footer-dedup batched into the existing Tier-B per-repo PRs (owner merges).
4. Umbrella: decide go/no-go on creating the public `arcs` repo + the `--json` contract rollout order.
