# The Flora and Fauna of ARCS

**Status:** REFERENCE · Ethereal (Hyperstition Pipeline stage 1 — not ROM; nothing starts at ROM)
**Version:** 0.1.0 · 2026-09-03 · **Companion instrument:** `scripts/corpus_prospector.py`
**Companion survey:** `_STATE/2026-09-03-prospecting-survey.md` (loop 1: index) · **Surface:** `_ARTIFACTS/flora-and-fauna/surface.html` (five lenses, one corpus) · **World:** `_ARTIFACTS/world/` (the 720° Möbius surface, built by `scripts/world_build.py`)
**Reads with:** `WORLD.md` (the physics) · `Tao-of-ARCS.md` (seed / spark) · `.claude/arcs-canon.md` (ROM primitives) · `ARCS-Canon-v2-0-Complete.md` Part I (the ARCS Law)

> A spec says what a thing must do. A field guide says how to recognize it in the wild, what it
> feeds on, what feeds on it, and where it is found. ARCS already has specs. This is the guide.
>
> "Ecosystem" here is meant three ways at once, and the guide never picks one: **literally** (five
> repos, a hundred scripts, a corpus of receipts, one operator, many sessions), **figuratively**
> (the navigable world of WORLD.md, fog to nucleus), and **metaphorically** (a thermodynamic system
> whose only law is that coherence is negentropy). Every entry below is true in all three registers
> or it does not belong here. That is the admission gate.

---

## How to read an entry

Each organism carries the same six field marks. They are the DEWY of taxonomy: enough to place it,
never a form to fill.

| Mark | What it answers |
|---|---|
| **Binomial** | Its name in the guide's own Latin — playful, but stable. Italic, like every binomial. |
| **Habitat** | Where in the repo / the world it lives (a path, a zone, a phase). |
| **Field marks** | How you know it's this and not its look-alike. |
| **Diet** | What it consumes: attention, signal, receipts, entropy. |
| **Produces** | What it leaves behind: an artifact, a gate, a fate (ADR-068). |
| **Predators / pathogens** | What kills it, hollows it, or wears its skin. |

A quick **dichotomous key** for anything you find in the tree:

```
1a. Does it act — detect, judge, consume signal, emit an artifact? ............ FAUNA (§IV)
1b. It does not act ........................................................... go to 2
2a. Does it store charge and accrete — a coordinate, a rule, a record? ........ FLORA (§III)
2b. It does not store ......................................................... go to 3
3a. Does it connect or decompose — carry nutrient between sessions? ........... MYCELIUM (§V)
3b. It neither connects nor decomposes ........................................ go to 4
4a. Does it read wrong later, or wear a healthy organism's skin? .............. PATHOGEN (§VI)
4b. Nothing points at it, and it has not moved in a season .................... ORE (§VII)
```

---

## I. The physics of the biome — where the energy comes from

There is exactly one sun in this ecosystem: **human attention**. ROM Primitive 1 (NOTOMATION) is
the ecological statement that nothing may photosynthesize on the operator's behalf. Instruments
scaffold and sequence; they do not replace the light. Every organism below is either a plant that
stores that light or an animal that moves it. None of them make it.

**Free energy** is the gap between fog and clarity: the distance between where a decision is and
where it could be if the terrain were readable. The ARCS Law names the currency exactly:

```
C = α·A − β·S + γ·W
    A = alignment of the parts        (rowers pulling the same way)
    S = Shannon entropy of the state  (how many futures still look equally likely)
    W = useful work                   (energy that became a receipt, not heat)
```

Coherence is negentropy. The ecosystem is alive to the degree it converts scatter into work,
and the guide's central claim is that **the conversion compounds**: each receipt lowers S for
every decision downstream of it (WORLD.md, The Progression — "the terrain you've already
navigated doesn't fog over again").

**Charge and current.** The Tao names the two halves. A seed *stores* charge — dormant, viable,
free to hold. The **vox animus** *fires* it — the spark that judges ripeness and converts potential
into kinetic at Kairos. A bank of seeds without a spark is a graveyard; a spark without a bank is
noise. The whole architecture is the difference (Tao §I–II).

**The dynamo.** The end state regenerates the source. In the superionic nucleus (WORLD.md; ADR-071)
a rigid lattice and a mobile charge occupy one volume — structure *and* flow — and that is exactly
where a planetary core generates its own field. The loop closes: flux → current → spark → loop →
superionic dynamo → flux. This is why the ecosystem is described as **externally vibrating**: a
self-exciting circuit radiates. The Orthogonal Echo Detector (Primitive 5) is the organ that
listens for that radiation in other domains — when two unrelated fields move the same way, name
the pattern. Pollen carries coordinate-free content; soil is the local chart the receiver supplies
(Tao §V).

---

## II. Biomes — the four zones and the strata beneath them

The terrain of WORLD.md is the map. Read it as habitat.

| Biome | Y states | Phase | What lives there |
|---|---|---|---|
| **Outer Fog Layer** | SCRATCH · PARADOX | Gas | Questions, scratch notes, `_INBOX/`, unfired seeds. Orient only. |
| **Pressure Band** | YELLOW · FORK · DELTA | Liquid | The Court, the Loki test, forks, worktrees, war rooms. Y gate active. |
| **Clarity Ridge** | GREEN · HIGH | Solid | Receipts, ADRs, patterns, the proverbs. Lock what you've earned. |
| **Superionic Nucleus** | LOCKED | Superionic | Kairos-locked canon, ROM primitives, WORLD.md. Charge through crystal. |

Beneath the zones, three strata that every organism roots into:

- **Bedrock — git.** The tamper-evident stratigraphy. A non-fast-forward rejection is the
  physical write-lock; the commit is the session seal; the branch is the arc identity. (Note for
  prospectors: a *shallow clone* exposes only the top strata. Ages read off it are lower bounds.)
- **Watershed — the monorepo and its family.** `arcs-v9` is the main channel; `arcs-canon` is the
  Library of Alexandria (Dewey shelves 0xx–7xx); `arcs-care` the public shore; `arcs-decision-receipts`
  the architect surface; `arcs-field-os` the spec headwaters. Worktrees are braided channels off
  the main stem. Seventy-two of them at last count is not a river, it is a delta — see §VI.
- **Slope — the avalanche terrain.** Fresh snow is apparent optionality. Hidden weak layers are
  ruin risks. The snowpit is prep + Court. The skintrack is the FORK. Free solo is RED.

---

## III. Flora — what stores charge and grows by accretion

Plants do not move. They root, they accrete rings, they hold energy in a form that survives
winter. Everything in this kingdom is *free to hold*.

### *Semen atomicum* — the Seed
- **Habitat:** `_SEEDS/` (index, ledger, distribution, the oracle). Genesis seed #0 is `adam == atom`.
- **Field marks:** small, typed, dormant. Has provenance and a lineage back to seed #0. Has not
  necessarily done anything yet — that is not a defect.
- **Diet:** nothing while dormant. Soil, when it returns.
- **Produces:** on firing — a germinated instance; on harvest — new seeds (the bank compounds).
- **Pathogens:** garbage collection on staleness. *Never GC a dormant seed* (Tao §IV). The
  look-alike is cruft (§VII), which has no provenance and no lineage.

### *Receptum dewyi* — the Receipt
- **Habitat:** the `Receipt` table in prod; `_STATE/*.dewy.json`; `runtime/recoil/generated/`.
- **Field marks:** a state vector frozen in time — D, E, W, Y plus the Y-gate triple (polarity ×
  conviction × stability) and an NCI. WORLD.md calls it "a coordinate, a seed"; the guide agrees:
  the receipt is the *fruit*, and a fruit is a seed with a story wrapped around it.
- **Sub-species:** the **Decision Receipt** (ex-ante, immutable header, outcome appended never
  edited); the **DEWY meta-receipt** (a receipt for the use of ARCS itself); the **Kintsugi
  receipt** (a healthy-plus-golden-seam ledger); the **Witness Receipt** and **Graduation
  Receipt** (candidates only — see *Baldur* and *Ullr*, §IV).
- **Diet:** one sharpened question, one prep session, one L0–L5 pass.
- **Produces:** fog retreat for every decision downstream. This is the compounding organ.
- **Pathogens:** reconstruction filed as witness (ADR-044); an outcome edited *into* the header
  instead of appended; a receipt with no close-loop (open-loop decay, §VI).

### *Quercus decisionis* — the ADR (heartwood)
- **Habitat:** `_DECISIONS/ADR-NNN-*.md`, indexed 1:1 in `_DECISIONS/index.json`.
- **Field marks:** numbered by the oracle and nothing else. Carries D/E/W/Y sections, options
  considered, a decision, consequences, a revisit trigger. Growth rings: status lines dated.
- **Diet:** a canon collision, a fork, a print-schedule gate that needed a fate.
- **Produces:** the durable "why" that stops an architecture from dissolving back into fog.
- **Pathogens:** numbering-without-registry (033 and 067 both doubled this way). Cure: the oracle
  (§IV) plus the pre-commit hook.

### *Sequoia canonica* — Canon (old growth)
- **Habitat:** `_CANON/` — Book II Parts I–VI, the Tao, WORLD.md, the trust contract, the apex spines.
- **Field marks:** status banner, version, a Kairos Lock when petrified. Referenced as authority
  by downstream artifacts without producing failures — that is the definition of ROM status.
- **Diet:** patterns that kept appearing in concrete sessions *before* they were named (Golden
  Inchworm: the abstraction is earned by the example).
- **Produces:** shade. Everything else grows in relation to it.
- **Pathogens:** three competing vocabularies for the same root (the ROM collision, resolved
  2026-08-28: 7 primitives are canon; 6 laws derived; 7 axioms foundations).

### *Pollen taoense* — the Proverb
- **Habitat:** `_CANON/tao-proverbs.jsonl` (250+ minted), each `generated-from` an ADR.
- **Field marks:** one sentence, coordinate-free, carries an aspect (D/E/W/Y) and a verb. Tiny.
  Travels on any wind. Lands in any soil.
- **Diet:** a ripened ADR.
- **Produces:** the compressed, portable form of a decision — the Hemingway pass of the canon.

### *Lichen durabilis* — the Pattern
- **Habitat:** `_PATTERNS/` — durable gotchas, audits, blueprints, the ledger.
- **Field marks:** slow, flat, grows on rock (infrastructure). An indicator species: where lichen
  is thick, the same failure recurred at least twice.
- **Produces:** the "do not re-derive" layer. Reads on demand only.

### *Flos artificialis* — the Artifact (bloom)
- **Habitat:** `_ARTIFACTS/`, `runtime/warroom/*.html`, published surfaces on `*.arcs.care`.
- **Field marks:** showy, seasonal, made for one counterpart or one moment. Silkscreen fidelity
  — renders only as sharp as the data underneath.
- **Diet:** an engagement, a call, a recoil.
- **Produces:** the print of a stage cut (ADR-068). A stage without a print happened only in
  conversation and will be re-derived at full cost.
- **Pathogens:** *orphaning.* Blooms are the most-orphaned organism in the tree by a wide margin
  (see the survey). A bloom nobody links to is not dead, but it is ore (§VII).

### *Folium traditum* — the Handoff (leaf litter)
- **Habitat:** the last 1–2 in `CLAUDE.md`; the rest relocated to `_ARCHIVE/handoffs.md`.
- **Field marks:** versioned (v3.NN.0), dated, names what shipped and what is open. Falls each
  season; is never burned, only relocated — history is relocated, never deleted.
- **Produces:** humus for the next session's pickup.

---

## IV. Fauna — what moves, detects, judges, and consumes signal

Animals move. They eat signal and excrete artifacts. Every animal here is *metered to fire*:
running one costs attention, tokens, or time, which is why the guide records diet.

### *Homo navigans* — the Operator (keystone species)
- **Habitat:** everywhere the sun is.
- **Field marks:** the only organism whose revealed preference the system may not compress,
  replace, or overrule. The vox animus is *their* breath, scaffolded.
- **Diet:** the world. Produces: questions, "wait, that's it", rulings ("I'll allow it").
- **Predators:** false urgency ("the road to ruin"); the 5-hour window; entropy masquerading as
  motion. The Ullr candidate (below) says the instrument's highest success is this organism
  needing it less.

### *Pyxis quaerens* — the Compass (the parser)
- **Habitat:** `POST /api/compass`, `src/lib/ygate.ts`.
- **Field marks:** takes a question, runs L0–L5, returns a bearing plus a Y-gate state. Does not
  say what to decide. Says where you are and which way is uphill.
- **Diet:** one question + one prep session. **Produces:** one *Receptum dewyi* with exactly three
  tributaries (meta · challenge · adjacent).

### The Sentinels (genus *Sentinella*)
Watchers. They do not decide; they notice, and they say one sentence.

| Species | Watches for | Where |
|---|---|---|
| *S. derivans* — **Drift Sentinel** | entropy masquerading as motion; N turns without an artifact | "Land the plane, or keep exploring?" (WORLD.md, The Enemy) |
| *S. testis* — **Witness Trigger** | a flash crystallizing live — "wait, that's it" | `/witness`; files a verbatim timestamped stub (ADR-046) |
| *S. oraculum* — **the Oracle** | two sessions minting the same number | `scripts/oracle.py` + `_SEEDS/_oracle.json`; git non-ff is the lock (ADR-057) |
| *S. tokenomica* — **Hall Monitor** | prompt cost vs. expected altitude | glossary v0.1; proposes chunk / compress / defer |
| *S. kairotica* — **Kairos** | ripeness; the window; the one-way door | `operators/arcs_operator_kairos.py`; not yet a background job |
| *S. custodia* — **pre-commit hook** | a duplicate ADR number in the commit | `scripts/git-hooks/pre-commit` |
| *S. tripwire / watchdog / leak_check* | secrets, air-gap leaks, hung deploys | `scripts/` |

### The Court (genus *Curia*)
- **Habitat:** the Pressure Band. `operators/arcs_constitutional_court.py`; Book II Part III.
- **Members:** the three lenses of **LAB** — *Loki* (adversary), *Advisor*, *Bayes*; **BAR**
  (Bayesian / Adversarial / Ruin); **KKL** (Known-known / Known-unknown / Loki).
- **Field marks:** invoked automatically at PARADOX and RED; RED is the free-solo topology. The
  relief heuristic: if a verdict would feel like *relief* rather than *information*, you were
  deferring into Court territory.
- **Produces:** a LOCKED state, or a redesign of the climb.

### *Loki adversarius* — the Trickster (beneficial parasite)
- **Habitat:** inside every candidate before it becomes canon. Hyperstition stage 2.
- **Field marks:** looks like an attack; is an immune training. A concept earns a receipt only
  by surviving the Loki test. "Hubris doesn't self-examine. Megalopsychia does."
- **Diet:** confidence. **Produces:** the inversion — the written failure mode that would falsify
  the claim. The Norse candidates each carry one (written 2026-08-28).
- **Not to be confused with:** a pathogen. Loki strengthens the host. Pathogens hollow it.

### The Six Operators (family *Operatoridae*, Canon v2 Part IV)
| Species | Role | Diet |
|---|---|---|
| **Orchestrator** | integrates all inputs, makes the call | everyone else's output |
| **Detective** | inversion reasoning, edge cases (Operator 17) | the Orchestrator's confidence |
| **Immune** | values / identity guardian | proposals that don't smell like us |
| **Accountant** | trust numbers, not narratives | receipts, outcomes |
| **Folksonomist** (Operator 20) | bottom-up taxonomy by DBSCAN over 54 dims | pooled signals; coins tags backward |
| **Librarian** | store / retrieve for pattern matching | the corpus |

Plus the meta-operators of the library: **SAGE** (somatic + epistemic), **CURATOR** (synthesis),
**Operator 21** (anterior/posterior spline — the knot resolver), **KINTSUGI** (phase-gate validation
and healing), **CONTRACT**, **LTE** (trajectory).

### *Geometrida aurea* — the Golden Inchworm (ROM Primitive 4)
- **Field marks:** the only animal that *is* a constitutional primitive. Moves by contraction in
  three passes — Red Thread (the concrete case) → Golden Thread (the pattern) → Needle (the rule).
  Non-blocking. Every abstraction is earned by a worked example first; the Inchworm is its own
  first example.
- **Diet:** concrete sessions. **Produces:** names.

### *Auris orthogonalis* — the Orthogonal Echo Detector (ROM Primitive 5)
- **Field marks:** listens for the same kinematics in two unrelated domains. When it hears one,
  it names the isomorphism.
- **Honest status:** the stub matcher is **not seaworthy** (dogfood 2026-08-29: adversarial
  false-positive rate 1.0 at default; no threshold gives high recall with low adversarial FP).
  The fix is an injectable signature function and an embedding-based orthogonality function.
  The organ exists; the ear is not yet tuned.

### The Foragers (the scanner suite)
- **Habitat:** `scripts/*_scan.py` — calendar, reader, listening, network, forensic, archetype.
- **Field marks:** graze on personal data across six domains and extract OM (present, resolved)
  from it. Stdlib-only; production-ready.

### The Prospectors (detectors that read the repo itself)
| Species | Detects | Path |
|---|---|---|
| **Corpus Prospector** | orphans, dormancy, training-grade | `scripts/corpus_prospector.py` (this guide's instrument) |
| **Gravity-well fork scan** | mass × gravity → when to fork a session | `scripts/gravity_well_fork_scan.py` |
| **Canon propagation check** | source→copy drift (ABSENT / DEROT / ESCALATE) | `scripts/canon_propagation_check.py` |
| **Branch hygiene** | two worktrees on one branch; name mismatch | `scripts/branch_hygiene_check.py` |
| **Seedbank / lattice / state-sync drift** | the ledgers disagreeing with the tree | `scripts/*_drift_check.py`, `state_sync_check.py` |
| **Ledger check** | enforcement parity (ADR-034) | `scripts/ledger_check.py` |
| **Receipt lookup --sweep** | unactioned obligations | `scripts/receipt_lookup.py` |
| **Cruft sweep** | stale worktrees (bundles before removing) | `scripts/cruft_sweep.py` |
| **Tool catalog** | the 131-instrument inventory itself | `scripts/tool_catalog_emit.py` → `/catalog` |
| **Claims skeptic** (agent) | a document's claims vs. the live repo | `.claude/agents/claims-skeptic.md` |

### The Pack Hunters (subagents with narrow diets)
`ciso-review` · `privacy-review` · `sre-review` · `claims-skeptic` · the three `recoil-*` gatherers
and reasoner (least-privilege by construction: the web gatherer cannot run a shell; the reasoner
cannot fetch). Each eats one kind of prey.

### *Ouroboros falsificans* — recursive self-falsification (ADR-062)
The animal that eats its own tail on purpose. Every claim the system makes about itself must carry
an executable kill condition; an unfalsifiable claim is a NULL signal.

### Candidates, not yet ratified (the Norse stack — recovered 2026-08-27, absent from v9 canon until then)
- ***Ullr*** — the **graduation invariant**. The instrument must be able to *decrease* visible
  scaffolding as fluency rises. Retaining a fluent user by making the instrument necessary is a
  NOTOMATION breach. Graduation ≠ churn. Detected by ≥3 signals across consecutive sessions, never
  by self-declaration. Produces a Graduation Receipt.
- ***Baldur*** — the **non-instrumentalization no-go zone**. Some moments ask to be *held*, not
  processed: grief, trust, intimacy phrased as a decision question. In a held moment no pipeline
  runs, no NCI, no nudge, no "turn this into a receipt?" Produces a Witness Receipt. The mistletoe
  is always the thing overlooked for being too small.
- **Gate still open:** one live Graduation Receipt and one live Witness Receipt. Cannot be
  fabricated. The guide lists them because a field guide records what has been *sighted*, and
  says so when a sighting is unconfirmed.

---

## V. Mycelium — what connects sessions and decomposes the dead

Neither plant nor animal. Runs underground. Moves nutrient from a tree that has it to a tree that
needs it, and turns last season's litter into next season's soil.

- ***Mycorrhiza memoriae* — Memory.** `_MEMORY/`, `MEMORY.md`, `memory_index_sync.py`. Hyphae
  between sessions. Recent entries live; dead history relocated to `_ARCHIVE/memory-archive.md`.
  Failure mode: the index outgrowing what a session can load (21KB > 17KB at last check).
- ***Hypha bisuperficialis* — the two-surface protocol.** `_STATE/snapshot.json` on main plus the
  raw-GitHub handoff: the architect surface (`arcs-decision-receipts`) and the implementor surface
  (`arcs-v9`) share state through one file. Zero infrastructure. Drift between snapshot and ground
  truth is the pathogen; `state_sync_check.py` the antibody.
- ***Humus archivi* — the Archive.** `_ARCHIVE/`. Where handoffs and memory go when they fall.
  Never burned.
- **Decomposers.** `/night-moves` (the dusk digest — what shipped, what's next, what we learned),
  `/fold` (re-serialize a dense session into composed sessions), `/consolidate-memory`, the
  nightly canon-propagation cron (still HELD — arm after merge), `cruft_sweep` (bundles every
  branch before it removes anything: reversible by construction).
- **The Library of Alexandria.** `arcs-canon`, shelved by Dewey code (0xx core and mythology →
  7xx titans). The mycelium's fruiting body: where a law from one project becomes pasteable in
  the next. Every file one canon block, spine + dewey + dependencies + attestation.

---

## VI. Pathogens, parasites, and the enemy

WORLD.md is exact: no boss, no villain, the terrain is not hostile. The enemy is **entropy
masquerading as motion** — the feeling of navigating while looping. Everything in this section is
a way that feeling wears the skin of a healthy organism.

### The Serialization Pathogen Family (ADR-033 — one axiom, a registry, an admission gate)
A belief ARCS wrote to ARCS that later reads wrong. Members, each with a mechanism-first cure:

| Member | The lie it tells | Looks like |
|---|---|---|
| **chronos-sequencer** | was true; read after it stopped being true | a stale handoff, a snapshot with closed items still open |
| **inductive-overfit** | validated *there*, treated as law *here* | n=2 under near-constant conditions promoted to a model |
| **open-loop decay** | a shipped-*feeling* mechanism that never landed | a memory citing "CI-gated" law that lives on an unmerged branch |
| **epistemic-sequencer** | serialized as enforced, warrant stripped | prose that says "git enforces" when only a hook would |
| **ventriloquy** | a voice attributed to someone who did not say it | investigated 2026-08-29 (`_PATTERNS/`) |

### Other pathogens, by field mark
- **False urgency** — pressure to act at low coherence. Mantra: *the road to ruin*. Cure: a
  deferment receipt ("do not build after midnight; revisit mañana").
- **Numbering-without-registry** — "highest + 1" across parallel sessions. Cure: the Oracle.
- **False zeros** — a degraded live count overwriting a curated floor (fixed 2026-09-02; banked).
- **Unearned optimism** — confidence climbing while risk stays flat (germinate's belief-log lint).
  The nearest thing to sycophancy the ecosystem has named; a wirable anti-sycophancy gate.
- **Reconstruction-as-witness** — a receipt filed later, describing itself as having been there
  (ADR-044 temporal provenance). Cure: attest in the moment, or label it reconstruction.
- **Algal bloom** — worktree sprawl (72 at last count). Not malignant; suffocating. Human-gated
  prune; bundle first.
- **Instrument self-citation** — a detector reading its own output as evidence. Sighted live
  2026-09-03: the corpus index listed every path, so on the next run every orphan looked homed.
  Cure: an instrument's outputs are excluded from its own reference corpus. (Kintsugi: the seam is
  shown here on purpose.)

### The immune system
**Kintsugi** (Primitive 6). Repair seams visibly. No silent patching of an integrity failure. Show
the break and the gold. Every pathogen above is listed with its cure because an unnamed pathogen is
the only kind that spreads.

---

## VII. Ore and dormancy — the deposits, and how to tell them from cruft

This kingdom exists because the tree is full of things nobody points at. Since April the watershed
has laid down blooms, war rooms, recoil ledgers, scratch notes, state files, and prior mining
outputs, and a large share of them have no inbound reference from anything else. The guide's
position, inherited from the Tao, is that **staleness is not death**, but also that **dormancy is
a claim that must be earned**. Three look-alikes:

| | Dormant seed | Ore | Cruft |
|---|---|---|---|
| **Provenance** | yes — lineage to seed #0 | usually partial (a date, a name) | none |
| **Inbound references** | may be zero (waiting for soil) | zero | zero |
| **What it holds** | a typed unit ready to fire | *refined* or *refinable* content with no home | nothing a second pass would want |
| **Correct fate** | hold; never GC | index → catalog → organize → bundle (§IX) | bundle, then let it go |
| **Who decides** | the vox animus (ripeness) | the harvest cycle | the human, after the bundle exists |

**Latent potential energy** in this ecosystem means: content that already cost attention to make,
that still holds charge, and that has no current path to a socket. Converting it is not "clean up".
It is the vox animus applied to the repo's own past — the spark judging which seeds are ripe *for
this soil, at this moment*. Kairos detection is the organ; the corpus is the seed bank.

**Grades** (as the survey uses them — a training-reuse heuristic, one point per signal: dated ·
provenance · referenced · well-formed):

- **Grade A / native metal** — refined, dated, sourced, but homeless. Example: the 2026-08-27
  forensic sweep's six `mine/g*.jsonl` ledgers and its report — 190 decision-lineage records
  already skeptic-adjudicated, sitting in `_ARTIFACTS/` with no index pointing at them.
- **Grade B / rich vein** — finished prose or data missing one signal, usually a reference.
  Example: five NFTT stories and two field-notes never published; the seven vision-film transcripts.
- **Grade C / placer** — real content, thin metadata. Example: war-room pages, per-counterpart
  recoil JSONs, PRL close-loop notes.
- **Grade D / overburden** — heavy, low doctrine yield, sometimes sensitive (résumé renders, raw
  CRM exports). Bundle privately or leave in place; never host.

Numbers, per-directory tables, and the named work list live in the survey, not here — a guide
is not a ledger, and the ledger is regenerated by the instrument.

---

## VIII. Seasons and succession

- **A session is a day.** The 5-hour window is its daylight. `/night-moves` is dusk.
- **A handoff is winter.** The leaf falls into `CLAUDE.md`, then into the archive. Spring is
  `/handoff-pickup`.
- **Succession** is the Progression of WORLD.md read ecologically. Pioneer species first: heavy
  fog, coarse briefs, yellow gates firing. Then patterns surface, the compass gets faster, NCI
  climbs. Climax community: navigation from the clarity ridge, the receipt history a personal
  atlas. Superionic: structure of clarity, fluidity of instinct — the dynamo self-exciting.
- **Graduation is not extinction.** In a healthy ecosystem the keystone species needs the
  instruments less over time (Ullr). An ecosystem that must keep its operator dependent to survive
  is a monoculture, and the guide records that as a pathogen, not a business model.

---

## IX. The harvest cycle — index → catalog → organize → bundle

The protocol for converting ore. Four verbs in fixed order, each printing an artifact through a
gate to a fate (ADR-068). Run in loops until the exit gate passes; the human, not the loop, says
when the quality is enough.

| Loop | Verb | Instrument | Prints | Gate (must pass to advance) |
|---|---|---|---|---|
| 1 | **Index** | `corpus_prospector.py index` | `_STATE/<date>-corpus-index.jsonl` + survey | every addressable file classed; secret_risk = 0; shallow-clone caveat stated |
| 2 | **Catalog** | Folksonomist (Op20) over the index residue; claims-skeptic on anything that claims canon | emergent tags + `ALREADY_CANON / VARIANT / NET_NEW` per item | ≥90% of Grade A/B items tagged; every NET_NEW claim skeptic-checked |
| 3 | **Organize** | oracle for anything that earns a number; canon index / `_ARTIFACTS/README` / Dewey shelf for a home | inbound references (the homing edges) | orphan rate for Grade A/B → 0; no ADR minted off-oracle |
| 4 | **Bundle** | `cruft_sweep` for branches; a dated `_ARCHIVE/bundles/<date>/` manifest for files | one manifest per bundle, hashed, with a fate per item (KEEP / ARCHIVE / PRIVATE / RELEASE) | every Grade D item has a declared fate; nothing deleted without a bundle |

**Exit gate for the whole cycle (training-reuse quality):** A+B share of the graded corpus rises
each loop and the residue of untagged Grade A/B items is empty; provenance present on every
Grade A item; zero secret hits; every bundle has a manifest. The loop stops on the human's ruling,
never on its own.

**Deterministic first, judgment second** (AGENTS.md gotcha 11): loop 1 is pure shell. Spend the
Folksonomist and the skeptic only on the residue loop 1 cannot score.

---

## X. Field marks for the reader in a hurry

- If it **stores** and does not move: flora. Hold it. It is free to hold.
- If it **moves** and costs something to run: fauna. Feed it deliberately. It is metered to fire.
- If it **connects** sessions or **rots** litter into soil: mycelium. Keep the hyphae short.
- If it **reads wrong later**: a pathogen. Name it; show the seam.
- If **nothing points at it**: ore, seed, or cruft. Index before you judge. Never delete before
  the bundle exists.
- If it is the **operator**: the sun. Nothing here replaces it.

---

*Loki inversion (written with the guide, per Hyperstition stage 2):* the failure mode of a field
guide is that the taxonomy becomes the territory — that organisms get *built to match the plates*
rather than plates drawn from sightings. The discriminator: every entry above cites a path or a
receipt where the organism was seen. An entry that cannot is decoration and must be cut. If a
future session finds itself creating a file so that the guide has an example, the guide has
failed its own test.

*Provenance:* drawn 2026-09-03 from `WORLD.md`, `Tao-of-ARCS.md`, `.claude/arcs-canon.md`,
`ARCS-Canon-v2-0-Complete.md`, `ARCS-v9-Canon-Operational.md`, `ADR-033`, `ADR-071`,
`ROM-CANDIDATES-norse-witness.md`, the 2026-08-27 forensic-recoil report, the v3.49–v3.52
handoffs, and one live run of `scripts/corpus_prospector.py`. No organism was invented for the
guide.
