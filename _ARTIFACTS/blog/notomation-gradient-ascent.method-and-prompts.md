# Method & Prompts — the record behind the record

*The upstream link in the chain of custody. Everything else — the essay, the scar-log, the trajectory,
the redline — is downstream of the prompts collected here. This file exists so an outsider can check
that the gauntlets were real and adversarial, not staged. It is the answer to "how do I know you didn't
just write the critiques you wanted?"*

> **Private, by design.** Like the rest of the evidence set, this is a private artifact. Nothing here is
> publicly hosted. Provenance for whoever you choose to show it to, not a broadcast.
>
> **Integrity note:** these are the actual driving brief and the verbatim adversarial prompts. What each
> gauntlet *returned*, and which findings were upheld vs overruled after verification against source,
> lives in the scar-log (`notomation-gradient-ascent.hardening.md`). Prompts here; verdicts there.

---

## Part 0 — The driving brief (the input)

The task that started it, in its own terms:

> Draft an ARCS blog post forking a concept that crystallized in a working session: **"NOTOMATION
> powering gradient ascent."** The honest frame — refining a skill with Claude, one accept/reject at a
> time, is NOT literal reinforcement learning (no reward model, no weight update, no policy gradient);
> it is gradient ascent where the human's revealed preference is the gradient, the human-in-the-loop is
> the optimizer, and the human's taste is the objective function, never guessed. NOTOMATION (ROM
> primitive #1 — "scaffold/sequence cognition only; never compress/replace/overrule revealed
> preference") is the guardrail that keeps the human as the objective function. The "weights" the ascent
> writes to are not model parameters — they are the skill file + exemplars + memory. Ground every claim;
> keep it defensibly true over impressive; no em-dashes in prose; draft-first, do not publish.

That brief is itself one of the things the hardening later corrected: the "objective function never
guessed" and "weights" framings were both narrowed under adversarial pressure (see the redline).

---

## Part 1 — The method, in one paragraph

Draft first. Run each epoch as a *battery of distinct adversarial lenses* in parallel. The integrator
verifies every finding against source before applying it (never trust a subagent's citation), and logs
overruled findings too. Repair with the seam showing (kintsugi). Log each epoch in the scar-log with a
render-fidelity ladder and a moving belief ledger. Escalate the *kind* of attack each epoch: facts →
overclaim → thesis-break → dialectic → cold falsifier. Full method: memory
`artifact-hardening-gauntlet-epochs-kintsugi-ledger`.

---

## Part 2 — Epoch 1 prompts (fact + honesty battery, 5 lenses, run in parallel)

**1 · claims-skeptic (fact).** *Adversarially verify the factual/mechanism claims against the live repo.
For each checkable claim return quote + verdict (TRUE/FALSE/UNVERIFIABLE/OVERREACH) + ground-truth
evidence (file:line) + a proposed fix. Prioritize: is the NOTOMATION quote verbatim to canon? Is the "no
RL" trio technically defensible? Is "a bearing, not a command" real documented behavior? Does telling
the compass a GREEN decision feels wrong actually record the Y-field as undefined — check src/lib/ygate.ts
and the compass route; if the code does not do this it is HIGH severity. Is the "weights = SKILL.md /
exemplars / memory" framing defensible or overstated? Rank most-severe first; find the claim that cannot
survive contact with the repo.*

**2 · BAR / overclaim.** *ARCS's core promise is refuse-to-overclaim (survivability not immunity; never
borrow a term of art the artifact cannot back). The essay invokes this rule on itself — hold it to that
standard. Find every place it claims more than it backs. Is "gradient ascent" itself an overclaim the one
hedge doesn't cover? Is the bitter-lesson counter overstated? Is NOTOMATION asserting a guarantee it
doesn't provide? For each: quote, name the overclaim, severity, minimal honest rewrite.*

**3 · cold-reader (ATG-FAQ).** *You are a skeptical senior ML researcher reading cold, instinctively
suspicious of grand reframes. List the 5 hardest questions you'd ask; for each, judge ANSWERED / PARTIAL
/ UNANSWERED with the quote. Prioritize "isn't this just active learning / RLHF with extra words," "the
human is the objective function is trivial," "the bitter-lesson counter is a dodge," "NOTOMATION is
defined circularly — is it falsifiable." Then name the single weakest axis and the one fix that most
raises the floor.*

**4 · voice / register.** *Calibrate against WORLD.md/AGENTS.md. ARCS voice: aphoristic, honest, plain,
no em-dashes in prose, no thought-leader hype, copy must not explain what the reader already understands.
Flag: any prose-body em-dash; lines that over-explain; SaaS/LinkedIn drift; strained aphorisms; a closer
that overstays. Surgical findings; also mark the load-bearing aphorisms NOT to cut.*

**5 · Loki (three-lens thesis-break).** *Break the central thesis three ways: (1) it's a rebrand of
active learning, contributing nothing you could DO differently; (2) NOTOMATION is unfalsifiable / does no
work — show the case where it would "fire" and argue it's indistinguishable from its absence; (3) the
weights-are-files metaphor is a category error that smuggles rigor the artifacts don't have. For each:
strongest attack, then the minimal defense needed to survive. Verdict: survives / survives-amended /
collapses.*

---

## Part 3 — Epoch 2 prompts (pathogen + dual bar-raiser)

**6 · pathogen detection.** *A "pathogen" is a false claim CARRIED from a trusted upstream source that
propagates. Epoch 1 found one (the UNDEFINED claim, inherited verbatim from canon that overstates the
code). Find the remaining pathogens: inherited overclaims (verify the "bearing, not a command" claim
against the actual compass prompt/route, not just canon); latent/contagious assertions ranked by
blast-radius if quoted by a hostile expert; dormant/aspirational claims stated as present-tense behavior
(is "a cheaper model rolls in the grooves" done or designed?). For each: quote, upstream source, ground
truth (file:line), contagion rating, minimal inoculation. If clean, say so — do not manufacture findings.*

**7 · Architect bar-raiser (canon-worthiness).** *You hold ARCS as a whole. Not bug-hunting — judge
whether this deserves the ARCS name in public. Axes: NET-NEW vs RESTATEMENT (is the non-amortization idea
a real tributary or elegant relabeling? name the exact sentence that carries the new idea); CANON
COLLISION (cross-check Tao of ARCS, refuse-to-overclaim, render-scale); POSITIONING FIT (does it close or
widen the product-marketing legibility gap; is it legible without the cosmology?); THE ARCS TEST (Myst vs
SaaS onboarding). End with a verdict — canon-worthy as-is / after named moves / not yet — and the one
structural change that raises it most.*

**8 · Editorial bar-raiser (ceiling-lift).** *Five gauntlets raised the floor; raise the ceiling. THE
FORWARD TEST: the one sentence that makes a busy reader forward it — quote it, or if there isn't one, that
is the finding. THE CEILING GAP: the single biggest gap between what it is and its best self (a missed
opportunity, not a bug). CONCRETE ELEVATION: 2-3 specific high-leverage moves. TITLE: which of the three
working titles serves best, or propose better. Rank by ceiling-lift.*

---

## Part 4 — Epoch 3 prompts (the dialectic + Constitutional Court)

**9 · Stoic (defends the thesis).** *The Stoic defends what is durable and true regardless of applause.
Make the strongest principled case that the thesis names something real and worth stating: the genuine
difference in kind that survives every fashion cycle; what a practitioner DOES better having internalized
it; steelman against triviality by conceding the obvious and isolating the residue. Deliver your strongest
defense, the single most durable true claim, and the narrowest version you would stake your name on. End
with what the Cynic will attack and where you concede.*

**10 · Cynic (attacks the thesis).** *Diogenes plucked a chicken to mock Plato's grand definitions. Do
that here. OBVIOUSNESS: strip the vocabulary — what's left but "iterate with a human and save your notes"?
SELF-INTEREST: published by ARCS, about an ARCS primitive, moralized with the ARCS house rule — insight or
content marketing inoculated against the critiques of content marketing? ONE-TRICK: is "never amortize" a
virtue or just not having built the reward model yet? ACTIONABLE-CORE: is "keep the rejected directions" a
real insight or a fortune cookie? Rank by damage; for each, the minimum to survive. Verdict: empty /
thin-but-real / survives.*

**11 · Funhouse (distortion mirrors).** *Bend the thesis and report what survives the reflection.
MAGNIFYING (reductio by exaggeration); INVERTING (flip each claim — what if amortizing is the point? what
if the artifacts are a liability?); CARNIVAL-BARKER (rewrite it as the hype LinkedIn version — how far is
the real essay from its own worst caricature?); HALL-OF-MIRRORS (the essay was hardened by the loop it
describes — is that rigor or an unfalsifiable immunization?). Per mirror: the distortion, what SHATTERS,
what SURVIVES. End with the single most fragile and most robust claim.*

**12 · Constitutional Court (adjudicates).** *Adjudicate the dialectic against ARCS axioms (NOTOMATION;
refuse-to-overclaim; earned-fidelity/render-scale; net-new-is-DEEMED-not-claimed). For each Cynic charge
and the Funhouse meta-charge: UPHELD / PARTLY / DENIED with constitutional basis. Disposition of the
thesis: STAND / STAND-NARROWED (state the holding) / FALL. Remedies: the specific minimal changes the
essay AND the ledger must make, MUST-FIX vs SHOULD-FIX. The one concession the essay must make in its own
text. Rule sine ira et studio.*

---

## Part 5 — Epoch 4 prompts (the cold CRYSTAL falsifier — a budget fan-out workflow)

Run as a workflow: 5 cold cheap probes (Haiku) + 1 expensive adjudicator (Opus). Each cold probe received
**only the artifact file** — no conversation, no prior answers — the literal "second model without the
original author" test.

**13a · cold-execute-practice.** *No prior context. Read ONLY the essay. Take the toy task "improve 'The
cat sat on the mat.'" and perform ONE step of the "keep rejected directions" practice EXACTLY as its
mechanism instructs. Judge: could you execute it from the artifact alone? drew_blood=true if too vague.*

**13b · cold-recover-thesis.** *No prior context. Read ONLY the essay. State back (1) the thesis and (2)
its LIMITS. Judge: does the artifact make its own limits legible without an author, or does its rhetoric
invite a cold reader to re-inflate into an overclaim? drew_blood=true if a fair reader walks away
overclaiming.*

**13c · collapse-b-proxy** *(the spine falsifier).* *No prior context. Read ONLY the essay. The spine: at
N=1 the objective is never distilled into a proxy because "there is no sample to train one on." Attempt to
COLLAPSE it — strongest case that distilling into a proxy at N=1 loses nothing. drew_blood=true only if
you build a persuasive collapse the essay has no answer to.*  ← **this is the probe that drew blood.**

**13d · cold-apply-method.** *No prior context. Read ONLY the essay + scar-log. Apply the METHOD to one
new small claim, producing a scar in the ledger's own format. Judge: is the method portable — could a
stranger run it from the artifact alone? drew_blood=true if underspecified.*

**13e · diff-skeptic.** *Read ONLY the essay. Judge internal consistency of the three Epoch-3 additions
(N=1 scoping; the "append the cut" mechanism; the two new honest edges). drew_blood=true if the repairs
introduced a fresh overclaim or contradiction.*

**13f · adjudicator (Opus fan-in).** *Given the five results: CRYSTAL requires a sought spine-falsifier
that drew no blood AND no new upheld cuts. Rule honestly — and crucially, a falsifier that drew no blood
only because the attempt was weak is NOT a pass; inspect each drew_blood=false for whether it was a
genuine hard attempt. Return {crystal, rationale, residual_cuts, test_quality}.*

**Outcome:** CRYSTAL **denied**, test_quality **genuine**. Probe 13c collapsed the spine (the accept/reject
trace *is* a sample), and 13d produced a real new cut. The full verdict and repairs are in the scar-log,
Epoch 4.

---

*This is the whole apparatus, exposed. If any critique in the scar-log reads as convenient, its prompt is
above — check whether it was aimed to break the essay or to flatter it. They were aimed to break it.*
