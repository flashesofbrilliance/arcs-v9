// Real weekly commit counts, full history (git log, main branch, measured 2026-08-16)
var CADENCE = [
  { w: "APR", n: 1 }, { w: "", n: 0 }, { w: "", n: 0 }, { w: "", n: 0 }, { w: "", n: 0 }, { w: "", n: 0 },
  { w: "MAY", n: 2 }, { w: "", n: 84 }, { w: "", n: 66 }, { w: "JUN", n: 48 }, { w: "", n: 90 }, { w: "", n: 71 },
  { w: "JUL", n: 277 }, { w: "", n: 123 }, { w: "", n: 265 }, { w: "", n: 167 }, { w: "", n: 83 },
  { w: "AUG", n: 114 }, { w: "NOW", n: 92 }
];

// Milestones, Day 0 to today. rank 1 shows on the one-page read; 2 and 3 appear as you go deeper.
// alt: [one-page, direction, process, detail] narratives; commits shown at the deepest level.
var MILESTONES = [
  {
    date: "DAY 0 · APR 9", title: "One commit. An empty scaffold.", rank: 1, proof: {url:"https://app.arcs.care", label:"the product it became"},
    alt: [
      "The starting line: a blank app skeleton. No product, no data, no users.",
      "The stack was chosen for boredom on purpose: proven web framework, proven database, simple email login. Every interesting risk in this project lives in the product logic, so everything under it had to be unexciting.",
      "One commit: Next.js 16, Prisma 7, magic-link auth wired but empty. Then the repo went quiet for five weeks while the design work happened on paper.",
      "The five quiet weeks were the specification period: the decision-receipt concept, the confidence-gate model, and the product's written constitution were drafted before the second commit ever landed. Code came second on purpose."
    ],
    commits: [
      { sha: "471d573", msg: "Day 1 scaffold: Next.js 16 + Prisma 7 + Auth.js v5 magic link" }
    ]
  },
  {
    date: "DAY 39 · MAY 18", title: "Ignition. The whole working core lands at once.", rank: 1, proof: {url:"https://app.arcs.care", label:"the live compass"},
    alt: [
      "After five quiet weeks of design, the full working core arrived in one push: ask a question, get a scored answer, keep the <span class='term' data-def='A short record made before acting: what you expect, what could go wrong, what else you considered. Scored later against what really happened.'>receipt</span>.",
      "The bet was to build the spine end to end before polishing any single part. A thin, complete loop beats a deep, half-connected one, because a complete loop can be tested against reality immediately.",
      "One commit carried the <span class='term' data-def='The main app surface. Ask a question, get an honest read of where you stand and which direction is uphill.'>compass</span> (ask), the <span class='term' data-def='The longer written readout generated from a compass run. Renders only as sharply as the data deserves.'>brief</span> (read), history, prep, the <span class='term' data-def='A check every answer passes through that rates how solid it is. The rating controls how confidently the answer is displayed.'>confidence gate</span>, and follow-up threads. A full operating handbook for the repo landed the same day, so any future contributor, human or AI, starts oriented.",
      "The handbook is written for AI collaborators as much as humans: what the system is, what must never be violated, and where each piece lives. That document is why 800+ commits later the architecture still matches its description."
    ],
    commits: [
      { sha: "a61d492", msg: "feat(v9): full pipeline: compass, brief, guide, history, prep, confidence gate" },
      { sha: "752739d", msg: "docs(agents): full agent and devops handbook" }
    ]
  },
  {
    date: "DAY 47 · MAY 26", title: "The data contract gets locked.", rank: 2,
    alt: [
      "",
      "Before scaling anything, the exact shape of a decision receipt was pinned down as a machine-readable contract. The database conforms to the contract, not the other way around. That single choice is why two months of speed never required a rework.",
      "The receipt format was written as a formal schema. The confidence gate's states were aligned across the engine, the database, and the screen in one pass, so all three always speak the same language.",
      "Alongside the schema, a small command-line tool made the whole analysis pipeline runnable and testable from a terminal, so the engine could be exercised and debugged without touching the web app at all."
    ],
    commits: [
      { sha: "61095c5", msg: "refactor: align confidence-gate states to the canonical schema" },
      { sha: "38aa0f6", msg: "feat(spec): time and window confidence rules, v0.1.0" },
      { sha: "e66d4de", msg: "feat: command-line pipeline for the analysis engine" }
    ]
  },
  {
    date: "DAY 47 · MAY 26", title: "The rulebook gets ratified.", rank: 3,
    alt: [
      "",
      "",
      "The product's written constitution, six chapters covering what the system may and may never do, was drafted, sent through an independent audit that raised 21 findings, corrected, and only then ratified.",
      "The audit protocol itself became a reusable asset: findings are keyed to specific sections and sentences, and consistency problems outrank missing features when reviewing a design document."
    ],
    commits: [
      { sha: "b6e59e4", msg: "feat(canon): rulebook chapters V and VI ratified at v1.0.0" }
    ]
  },
  {
    date: "DAY 48-49 · MAY 27-28", title: "Live in production, ten days after ignition.", rank: 1,
    alt: [
      "Ten days after the core landed, it was deployed, and hardened the same week: real database, locked-down access, users could sign in.",
      "The deploy surfaced a real fork: the database toolkit had just shipped a breaking change. Fixed in-flight. Then a harder call: the textbook access-control setup would have looked right and protected nothing here, so a stricter model was chosen and the reasoning was written down.",
      "Production database stood up and migrated, deny-by-default access rules applied to every table, and the plan-versus-reality gaps from the deploy logged as amendments to the original decision records rather than papered over.",
      "The as-built record matters: environment settings that were set by hand instead of through the integration got documented as a rotation risk on day one, with the fix procedure attached. That honesty is what makes the risk register on this page trustworthy."
    ],
    commits: [
      { sha: "11ba2fc", msg: "fix(db): adapt to the database toolkit's breaking change" },
      { sha: "5262c1a", msg: "chore: baseline migration applied to production database" },
      { sha: "9970c3f", msg: "feat(security): deny-by-default access rules on all tables" }
    ]
  },
  {
    date: "DAY 48 · MAY 27", title: "A design system, from day one.", rank: 3, proof: {url:"https://app.arcs.care", label:"the design system, live"},
    alt: [
      "",
      "",
      "A shared color and component system was pinned early, so every later surface, internal or client-facing, looks like one product for free.",
      "Tokens were extracted from the app's actual rendered colors rather than aspirational brand values, and three visual registers were defined up front so client pages and internal tools can differ in tone without differing in system."
    ],
    commits: [
      { sha: "924fd10", msg: "feat(ui): canonical color tokens and first components" }
    ]
  },
  {
    date: "DAY 57 · JUN 5", title: "The architecture gets challenged before it ships.", rank: 1,
    alt: [
      "A major architecture proposal was sent through an independent challenge review before acceptance. The review caught four overclaims, including a cited theorem that does not exist. The corrected version shipped.",
      "The question on the table: should the platform's picture of its own goals be hand-drawn, like a roadmap slide, or inferred from actual behavior? Inferred won, but with hard limits written in: the system may never tune its own guardrails.",
      "The design, its tuning constants, and a simulation harness to stress-test the structure all landed together. Activation was gated behind a minimum volume of real data, the same rule applied to every advanced feature since.",
      "The challenge review ran as five independent research passes attacking the draft's citations and claims. All four corrections were applied before the merge, and the record of what was wrong stayed in the document."
    ],
    commits: [
      { sha: "9f669fa", msg: "feat(spec): goal-map architecture plus tuning rules" },
      { sha: "bbeb8a8", msg: "feat(observatory): timeline demo regenerated clean for external viewing" }
    ]
  },
  {
    date: "DAY 82 · JUN 30", title: "The platform merge: 170 files, five subsystems, one day.", rank: 1, proof: {url:"https://app.arcs.care", label:"the platform, live"},
    alt: [
      "The biggest single integration: legal pages (trust, privacy, terms), an interactive <span class='term' data-def='A viewer for scrubbing back through past decisions like game film: what was known, what was expected, and where confidence peaked or collapsed.'>replay theater</span> for past decisions, and the whole engine re-implemented in plain Python as a vendor hedge. Merged and live in production the same day.",
      "This merge is the line where ARCS stopped being an app and became a platform: legal surfaces, observability, and vendor independence are the prerequisites for putting client traffic on something.",
      "170 files and 42,000+ lines: the trust/privacy/terms routes, a 1,174-line interactive replay page, a 34-file standalone engine library, four database migrations, six new decision records, and an indexed registry of all 272.",
      "The merge initially landed on the wrong branch, a real mistake. It was caught, re-merged correctly, and the failure mode was turned into a standing pre-flight check in the deploy script so it structurally cannot recur."
    ],
    commits: [
      { sha: "5db496b", msg: "Merge: production platform features (trust pages, replay theater, engine library)" }
    ]
  },
  {
    date: "DAY 84-90 · JUL 2-8", title: "Client pages become a production line.", rank: 1,
    alt: [
      "The commercial motion, proven live: 14+ branded client-facing pages (briefs, proposals, analyses), each stood up in hours on the same engine, demand tested with real clients, not a deck.",
      "The productized-consulting motion, proven on real clients: branded, client-facing pages (briefs, proposals, analyses) stood up as their own web addresses in hours each. 14+ went live in that window, all riding the same engine and design system.",
      "A single reusable template with fill-in slots plus a documented publishing routine turned each new client page into a two-hour exercise instead of a project. A consolidation pass then pulled scattered assets from a sibling repository into the main one, with review.",
      "The routine encodes its own past mistakes: which config file actually controls routing, why deploys must run from the main working copy (a wrong-copy deploy once silently dropped every other client page), and how new addresses get attached to the project."
    ],
    commits: [
      { sha: "1ea5e8a", msg: "fix(routing): client proposal page live on its own address" },
      { sha: "cf8b084", msg: "chore: consolidate scattered assets plus the reusable page template" }
    ]
  },
  {
    date: "DAY 93-95 · JUL 11-13", title: "Trust cleanup: delete first, rebuild second.", rank: 1,
    alt: [
      "Two integrity fixes back to back: an audit showed the project's own rules were not being enforced (fixed at the root), and visitor data was being saved without an account (the saving was deleted first, then rebuilt as opt-in). The public trust page was updated to match.",
      "Both fixes follow one doctrine: when what the product does and what it promises drift apart, ship the deletion before the feature. Credibility comes from the order of operations.",
      "A leftover styling framework the docs claimed was never there got removed and the automated checks were aligned with the written rules. The no-account save path was cut at the API level, then opt-in saving shipped as its own feature, and the trust contract was versioned to 1.2.",
      "The structural follow-through landed days later: an enforcement ledger where every audit finding closes only through a working mechanism or a signed, dated exception, checked automatically. The audit-then-forget loop is broken by construction."
    ],
    commits: [
      { sha: "35fc2e7", msg: "fix(governance): remove unused framework, align docs and checks with reality" },
      { sha: "8b486e8", msg: "fix(trust): no account means no saving. Stop persisting visitor data" },
      { sha: "b9dab2a", msg: "feat(trust): opt-in save plus trust contract v1.2" },
      { sha: "570e575", msg: "docs(governance): reconciliation of two independent audits" }
    ]
  },
  {
    date: "DAY 98 · JUL 16", title: "The loop closes. The system now grades itself.", rank: 1, proof: {url:"https://app.arcs.care", label:"the product that grades itself"},
    alt: [
      "Since Day 98 the loop closes on a schedule: when a prediction comes due, a daily job emails a debrief automatically, so none is silently forgotten. When the outcome is logged, it is scored against the expectation recorded beforehand and written to an audit trail. The reminder is automatic; logging the outcome is still a human keystroke.",
      "This is the product thesis completing itself: decision receipts only compound if outcomes get scored against them, and outcome scoring only scales if it does not depend on anyone's discipline. It also generates the calibration data every gated feature is waiting on.",
      "A scheduled job matches ended calendar events to their transcripts, reads each transcript twice (once backward from the ending, once forward against the pre-call expectation), writes the scored result to a private ledger, and notifies with the deltas. Three real calls were processed autonomously on the first production run, on Day 98.",
      "The job's specification encodes its own failure history: a duplicate-work incident led to a strict naming rule and a check-before-work step, because scheduled runs share no memory with each other. Treating amnesia as a design constraint is what makes unattended automation safe."
    ],
    commits: [
      { sha: "eab39a3", msg: "feat(recoil): first autonomous post-call scoring run, three calls processed" }
    ]
  },
  {
    date: "DAY 120 · AUG 7", title: "Stop building things by hand. Build the machine that builds them.", rank: 1, proof: {url:"https://good.arcs.care", label:"the generated index"},
    alt: [
      "The work crossed a line from craft to manufacturing: instead of hand-building each page and report, one renderer reads a single source of truth and generates a whole family of surfaces. Change the source once, every surface updates.",
      "Hand-building does not scale and it drifts: ten pages built by hand become ten slightly different pages. A factory keeps them identical by construction and makes the next one nearly free. The bet was to spend the effort once, on the machine, not every time on the output.",
      "A client page became generated rather than typed; a reusable design pattern was published; a data-driven milestone renderer and a single-source distribution registry followed. Each is the same shape underneath: one source of truth, one renderer, many surfaces.",
      "The discipline is composability: small, atomic parts assembled by machine, so a change propagates instead of being re-typed. Several of this page's sibling surfaces are generated exactly this way."
    ],
    commits: [
      { sha: "ac96aa9", msg: "feat(forge): full one-door renderer, the page is now generated" },
      { sha: "b6b1b76", msg: "feat(forge): publish the reusable design pattern" },
      { sha: "5ca190b", msg: "feat(milestone): data-driven template + renderer" },
      { sha: "50aef5e", msg: "feat(seeds): single-source distribution registry" }
    ]
  },
  {
    date: "DAY 124 · AUG 11", title: "The system learns to catch its own insights.", rank: 1,
    alt: [
      "A way to capture a flash of insight the moment it lands, not reconstructed hours later, and file it as a durable note that is promoted only if it proves out. Paired with a written philosophy of how knowledge is held and passed on.",
      "Insight is perishable: the thought that names itself mid-work is usually gone by the time the notes get written. Catching it live and verbatim, then deciding later whether it was durable, keeps the good ones and discards the rest honestly.",
      "The witness mechanism attests in the moment; a written doctrine sets down how a dormant idea is stored and when it is allowed to animate; every decision and receipt is minted as a reusable seed with the conditions it needs to germinate.",
      "This is what makes the opening claim real: the thinking behind the build is captured as it happens, so it is inheritable, not locked in one head."
    ],
    commits: [
      { sha: "d32b7fc", msg: "feat(witness): live capture of a flash of brilliance (ADR-046)" },
      { sha: "d16b377", msg: "feat(canon): the doctrine for how knowledge is held and passed on" },
      { sha: "325d21e", msg: "chore(seeds): mint each decision as a reusable seed" }
    ]
  },
  {
    date: "DAY 126 · AUG 13", title: "The system turns its scrutiny on itself.", rank: 1,
    alt: [
      "The machinery that records decisions started policing its own integrity: a sequence authority to stop ID collisions, a gate that refuses to ship an aspiration as a present fact, and a self-audit that downgraded one of its own claims from green to yellow.",
      "A falsifier that will not turn on itself is just propaganda with footnotes. The real test is whether the honesty system will catch and correct its own errors, in public, at cost to its own story.",
      "A cross-session sweep traced a family of colliding decision IDs to ground truth with four independent auditors and remapped them in one pass (031 to 048, 032 to 049, and more). An adversarial gauntlet was run against the canon itself.",
      "The economics are logged, not guessed: 947,000 tokens of self-verification across five gauntlet runs, 32 of its own claims stress-tested to falsified, and a 13x correction to its own cost model once the log proved that agent count, not prompt size, drives the bill."
    ],
    commits: [
      { sha: "e5aa6b8", msg: "feat(oracle): sequence oracle + 30-day cross-session reconciliation" },
      { sha: "08330a8", msg: "refactor(adr): apply the forensic cross-session ID remap" },
      { sha: "39a5408", msg: "fix(canon): self-audit downgrades a claim green to yellow" },
      { sha: "c1b21d8", msg: "canon: a falsifier is only honest if it turns on itself" }
    ]
  },
  {
    date: "DAY 129 · AUG 16", title: "The front door opens, and the telemetry goes live.", rank: 1, proof: {url:"https://good.arcs.care", label:"the front door"},
    alt: [
      "A public index of the open tools stood up, and this status page itself became live-computed, reading real numbers from the repository instead of a frozen snapshot. The page you are reading stopped being a photograph and became an instrument.",
      "A body of work only compounds in the open if there is a door into it. The index gives the open tools one address; the live page makes the build legible to anyone, updated on its own rather than by hand.",
      "The open tools were grouped behind a single front door, led by the ones that are fully baked, while the private intelligence that orchestrates them was kept deliberately separate. This page was rewired to read its own commit count, day count, and deploy state server-side.",
      "The number at the top of this page updates itself now. From Day 98 the pieces began to compound; the next frontier is choreographing them into deep multi-agent orchestration, agents nesting several layers deep. That last part is intent, not yet built, and is labeled as such on purpose."
    ],
    commits: [
      { sha: "9098fd4", msg: "feat: first public-goods connector + subdomain" },
      { sha: "aeaf140", msg: "feat(good): public-goods index, led by the fully-baked tools" },
      { sha: "db41d40", msg: "feat(seeds): the open-source family the index fronts" }
    ]
  },
  {
    date: "DAY 151 · SEP 7", title: "The ledger learns to tell its assets from its liabilities.", rank: 1,
    alt: [
      "The system that grades itself was pointed at its own production data, and for the first time it booked the other half of the ledger: not just what it knew, but what it had gotten wrong and stamped as true at the time. Fourteen false receipts, caught and carried rather than deleted.",
      "A record that only counts its wins is survivorship bias wearing a green badge. This week the liability side opened. A receipt is a claim that survived contact with the ground; a deceipt is one that felt identical when it was written and did not survive. The honest position is the difference between them, not the sum of the wins.",
      "The audit ran on the live database, not a fixture. It caught a signal rated evidence-backed across forty-five records that was one constant value wearing a decimal point, a field reported as 247-of-247 that was naming the wrong column, and a task called blocked that never was. None of these were caught by looking inward; every one was caught by a query, a failed build, or an independent second pass. The correction is always a move from the asset side to the liability side, never a silent delete.",
      "The mechanism was wired, not merely written. A deterministic degeneracy sensor became a commit-time gate that blocks a new signal from silently going constant, and the database claims were rewritten as reproducible queries anyone with access can re-run. A zero-liability ledger is the one to distrust: the fourteen entries are the evidence the system was in contact with reality rather than admiring its own coherence. That is the whole promise, corrected from navigate-to-clarity-as-confidence to a clarity that knows its own liabilities."
    ],
    commits: [
      { sha: "79bf6f5", msg: "wire(sensor): informativeness ratchet gate blocks new signal degeneracy" },
      { sha: "eca36c2", msg: "audit(db): reproducible DB audit, 247/189/2 confirmed, deceipt booked" },
      { sha: "f2f4378", msg: "fix(build): delete dead scaffolding a prune missed, caught by first real build" }
    ]
  },
  {
    date: "DAY 159 · SEP 15", title: "The constitutional gate learns to report its own zeros.", rank: 1,
    alt: [
      "A separate governance layer, the fail-closed brake that sits in front of the highest-consequence one-way-door decisions, got a real end-to-end test suite and a set of honest benchmark numbers. Including the zeros. The point of a brake is not that it scores well on someone else's harm quiz; it is that it holds on the three classes it was built to hold.",
      "A benchmark you pass by redefining the test is a mirror, not a measurement. The suite boots the real daemon, asserts the gate refuses the cases it must refuse under a real latency budget, and reports the recall it actually gets on public ethics and jailbreak sets rather than the recall a demo would claim.",
      "The scope was narrowed on purpose, not widened. The tempting move, when a gate scores zero on a broad harm benchmark, is to make the gate do more. The honest move is to name what it is for, a narrow brake on a few irreversible classes, and measure that, and let the broad number stay zero because the broad job was never the job.",
      "The whole layer leads with an honest inventory now, its theology demoted to an appendix and its unimported scaffolding deleted. A governance system that cannot say what it does not do is not one you would let stand in front of a one-way door."
    ],
    commits: [
      { sha: "e2d9df3", msg: "docs(handoff): arcs-algorethics E2E/benchmarks/kabuki audit; PR #446 held" },
      { sha: "34ad3f2", msg: "queue(backlog): narrow algorethics item to the in-scope benchmark, drop 'widen to broad harm'" },
      { sha: "fde93c0", msg: "queue(backlog): algorethics gate-widening design decision (AgentHarm 0/176 both ways)" }
    ]
  },
  {
    date: "DAY 167 · SEP 23", title: "A question meant to test one feature found a six-week outage.", rank: 1, proof: {url:"https://good.arcs.care/blog/nftt/the-question-that-found-the-outage", label:"the war story"},
    alt: [
      "The session started small: how do I actually test the operator pre-screen? The insistence on a live end-to-end check, rather than trusting that a green merge meant a working feature, is what pulled the thread. Under it was a total, weeks-old outage of the signed-in product that no dashboard had reported.",
      "A green build is a claim that the code compiled, not a claim that the system works. The signed-in compass had been failing every write for roughly six weeks, on a database column the code expected and the production database had never been given. The migration existed in the repository. It had simply never been run against production, because production was bootstrapped in a way that skipped the migration ledger entirely.",
      "The fix ran on the live database, and in the same move it revived a feature that had shipped months earlier and quietly died on the same fault. Then the client got a defense: the run now persists server-side even when a slow phone gives up on it, and a deep health endpoint turns what had been a twenty-minute forensic investigation into a single request that reports schema drift, staleness, and the state of every dependency.",
      "The lesson is the one the whole system is built on, turned back on itself: trust the artifact that survived contact with the ground, not the transient signal that says everything is fine. The green checkmark was the transient signal. The failing write was the ground."
    ],
    commits: [
      { sha: "7d864ea", msg: "fix(sage): activate operator pre-screen - enum reconcile + SAGE_URL" },
      { sha: "90a9f5d", msg: "fix(compass): graceful timeout recovery + admin health endpoint" }
    ]
  },
  {
    date: "DAY 168 · SEP 24", title: "The prevention, and an honest look at the number that hid the fault.", rank: 1,
    alt: [
      "A fix that only fixes the instance invites the class to recur. So the root cause of the outage was closed for good: production was baselined into the migration ledger it never had, and the deploy pipeline was wired so that pending migrations run on every build. The same drift cannot ship silently again, because a build that would ship it now fails.",
      "The outage had been masked for six weeks by a metric that looked like a problem of its own: two closed outcomes out of two hundred forty-seven. That two-of-247 keel gap turned out to be a measurement artifact, not a capture failure, one account was closing ninety-five percent of its eligible receipts; the funnel had been counting the wrong denominator.",
      "This is the same discipline as the liability ledger: a number that looks bad is not a verdict, and a number that looks fine is not an alibi. The honest move is to pull the funnel apart mechanically before reaching for any story about it, and to let the real figure replace the alarming one only once a query, not a hunch, has produced it.",
      "The through-line of both days: a system earns trust not by never breaking, but by being built so its breaks are visible, its fixes are structural, and its own metrics are held to the same burden of proof as everything it measures."
    ],
    commits: [
      { sha: "f2aae73", msg: "feat(db): P1 prod migrate-deploy groundwork (baseline + gated wrapper + runbook)" },
      { sha: "625fe0b", msg: "feat(db): complete P1 - baseline prod + wire production-gated migrate deploy" },
      { sha: "b5076f6", msg: "feat(health): honest outcome-capture funnel - 2/247 keel gap was a founder-QA artifact" }
    ]
  },
  {
    date: "DAY 169 · SEP 25", title: "Can a cold agent rebuild a session from git alone?", rank: 2, proof: {url:"https://good.arcs.care/blog/nftt/the-control-and-the-experiment", label:"the experiment"},
    alt: [
      "A new open tool, tools/cold-recon, hands an agent only the commits and files from a session, never the transcript, and asks it to reconstruct what happened. Whatever it cannot rebuild is a gap in the record. The coldness is structural: the gather step has no code path that reads a transcript.",
      "The tool was then tested against its own claim. Two cold runs scored 0.90 and 0.84 on provenance. A warm run given a relaxed instruction to cite scored 0.26; a warm run held to the same citation rule scored 1.00. One small run, stated as illustrative, not as proof.",
      "The finding is narrower than the pitch would have been: memory does not corrupt what an agent grounds, it changes whether the agent bothers to ground at all. A reader with no memory cannot narrate from memory, and that is the whole value."
    ],
    commits: [
      { sha: "87ac486", msg: "PR #505 cold-reconstruction CLI + NFTT pair + warm-vs-cold experiment" }
    ]
  },
  {
    date: "DAY 170 · SEP 26", title: "The audit offer went live, with two cases you can play first.", rank: 2, proof: {url:"https://good.arcs.care/audit", label:"the audit page"},
    alt: [
      "good.arcs.care/audit now describes a fixed-scope Agent Receipts Audit: every claim an agent made about a repo, checked against the repo. Two free playable cases sit in front of it, built from published posts. In each one you defend a claim with evidence or concede it, and stake play-money conviction that is scored when the case resolves.",
      "Prices stay off the page on purpose until real scoping conversations set them. The routing bug found on the way (a catch-all rewrite swallowing the new paths) was caught by serving the build with the production host header, not by the build passing."
    ],
    commits: [
      { sha: "24e2fee", msg: "PR #530 route the Agent Receipts Audit + two playable cases on good.arcs.care" },
      { sha: "ac087aa", msg: "PR #553 the accountable copypasta card at good.arcs.care/copypasta" }
    ]
  },
  {
    date: "DAY 171 · SEP 27", title: "A scoreboard that refuses to grade itself on too little data.", rank: 1, proof: {url:"https://good.arcs.care/audit", label:"the ledger count"},
    alt: [
      "Operator 19, the Accountant, now reads real production receipts and reports, per cohort (founder, external, anonymous), how many decisions were logged and how many were ever closed with an outcome. The first run: 254 receipts, 3 closed, all 3 by the founder. It emits a calibration score only once a cohort has 30 closed positions; below that it prints the n and the word insufficient.",
      "The echo detector, which looks for the same pattern across unrelated domains, moved from keyword matching to sentence embeddings. On scrambled-text controls its false-positive rate fell from 0.8 to 0.0. Then a second control removed boilerplate lines shared across inputs, and the real echo count went to zero. That result is published as it came out.",
      "Two small gates landed alongside: an altitude canary that flags confident prose with no citation in it, and a per-source trust ledger. The audit page gained a count of the project's own falsified beliefs, stamped by a script from the belief log so it can never be typed by hand."
    ],
    commits: [
      { sha: "e36084f", msg: "PR #578 bind Operator 19 Accountant + scoreboard from real data" },
      { sha: "defaecc", msg: "PR #612 embedding-backed signature/orthogonality for the echo detector" },
      { sha: "4356f50", msg: "PR #565 altitude canary: fluent, confident, uncited prose" },
      { sha: "740aa55", msg: "PR #591 falsification count on the audit page, stamped from the ledger" }
    ]
  },
  {
    date: "DAY 172 · SEP 28", title: "Retrieval by expected value, and a hole closed in the database.", rank: 1,
    alt: [
      "Operator 21, the Librarian, used to hand back the most recent material. It now scores each candidate by how likely it is to be load-bearing for the question, minus the cost of reading it, under a context budget, and takes it only if the value clears the cost. Anything it cannot back with a commit or path goes into an explicitly unconfirmed list. Its first run ranked its own registry note first, because that note was written in the same change; that is written down as a lesson, not hidden.",
      "An outside audit flagged two tables readable through the public API. It was verified, fixed live the same day (row-level security on, deny-all), and a pre-commit check now fails any new table created without it. A daily job now also flags any pull request merged by squash, since squashing erases the per-PR history that receipts cite."
    ],
    commits: [
      { sha: "150beb1", msg: "PR #613 Librarian.recommend(q, budget), Operator 21 rebound" },
      { sha: "01af2f3", msg: "PR #637 enable RLS on Tribune + _prisma_migrations, gate new tables" },
      { sha: "f0f9d92", msg: "PR #640 no-squash policy + daily squash-merge detector" }
    ]
  },
  {
    date: "DAY 173 · SEP 29", title: "The privacy promise now has a test that fails if it breaks.", rank: 1,
    alt: [
      "The trust page promises that visitors without an account are not saved. A unit test now runs the real prep and compass handlers anonymously and asserts zero database writes, no email and no cookie. Removing either route's guard makes the test fail; that was checked, not assumed. The decision-gate logic got 17 cases of its own. No new dependencies.",
      "A second guard fails CI on any Tailwind or className creep outside the two sanctioned exceptions. Both close findings on the project's own open-defect ledger."
    ],
    commits: [
      { sha: "df94e60", msg: "PR #642 ygate + trust-contract no-anon-write tests, close YG-005 + TC-004" },
      { sha: "62edaa9", msg: "PR #641 className/Tailwind guard, close LINT-006" }
    ]
  }
];

// Chart tooltip - shared floating readout
var chartTip = document.createElement("div"); chartTip.id = "charttip"; document.body.appendChild(chartTip);
function tipWire(el, html) {
  el.addEventListener("mouseenter", function () {
    var r = el.getBoundingClientRect();
    chartTip.innerHTML = html;
    chartTip.classList.add("on");
    var half = chartTip.offsetWidth / 2, cx = r.left + r.width / 2;
    cx = Math.max(half + 8, Math.min(window.innerWidth - half - 8, cx));
    chartTip.style.left = cx + "px";
    chartTip.style.top = r.top + "px";
  });
  el.addEventListener("mouseleave", function () { chartTip.classList.remove("on"); });
}
// Week label helper - nearest month marker walking backward
function weekName(i) {
  for (var j = i; j >= 0; j--) { if (CADENCE[j].w) return CADENCE[j].w + (i - j > 0 ? " +" + (i - j) + "WK" : ""); }
  return "WK " + (i + 1);
}

// Cadence chart
(function () {
  var max = Math.max.apply(null, CADENCE.map(function (c) { return c.n; }));
  var el = document.getElementById("cadence");
  CADENCE.forEach(function (c, i) {
    var col = document.createElement("div"); col.className = "cad-col";
    var n = document.createElement("div"); n.className = "cad-n"; n.textContent = c.n > 0 ? c.n : "";
    var bar = document.createElement("div");
    bar.className = "cad-bar" + (c.n === max ? " peak" : c.n === 0 ? " zero" : "");
    bar.style.height = c.n === 0 ? "2px" : Math.max(4, Math.round((c.n / max) * 58)) + "px";
    tipWire(bar, (i >= 1 && i <= 5)
      ? "DESIGN PERIOD<small>" + weekName(i) + " · 0 commits · the work was on the drawing board</small>"
      : c.n + " COMMIT" + (c.n === 1 ? "" : "S") + "<small>" + weekName(i) + (c.n === max ? " · peak week" : "") + "</small>");
    var w = document.createElement("div"); w.className = "cad-w"; w.textContent = c.w;
    col.appendChild(n); col.appendChild(bar); col.appendChild(w);
    if (i >= 1 && i <= 5) {
      col.classList.add("design-win");
      col.title = "The quiet stretch · tap to see what the silence was";
      col.addEventListener("click", function () { toggleUnlock("unlock-design"); });
    }
    el.appendChild(col);
  });
})();

// Telemetry tabs + unlock cards
function toggleUnlock(id) { document.getElementById(id).classList.toggle("open"); }
document.getElementById("chip-design").addEventListener("click", function () { toggleUnlock("unlock-design"); });
document.getElementById("chip-frontier").addEventListener("click", function () { toggleUnlock("unlock-frontier"); });
document.querySelectorAll(".tele-tab").forEach(function (b) {
  b.addEventListener("click", function () {
    document.querySelectorAll(".tele-tab").forEach(function (x) { x.classList.remove("active"); });
    b.classList.add("active");
    document.getElementById("tab-tempo").style.display = b.dataset.tab === "tempo" ? "" : "none";
    document.getElementById("tab-hands").style.display = b.dataset.tab === "hands" ? "" : "none";
    document.getElementById("tab-recent").style.display = b.dataset.tab === "recent" ? "" : "none";
  });
});

// Conductor lane: weekly commits by co-author (git log main, trailers, measured 2026-07-17)
var COND_MODELS = [
  { key: "Sonnet 4.6", color: "#00F0FF", total: 545 },
  { key: "Sonnet 5",   color: "#00FF9D", total: 78 },
  { key: "Fable 5",    color: "#c084fc", total: 47 },
  { key: "Haiku 4.5",  color: "#FFD700", total: 32 },
  { key: "Opus 4.8",   color: "#FF4D6D", total: 22 },
  { key: "solo",       color: "#64748b", total: 128, label: "BY HAND, NO AI" }
];
var COND_WEEKS = [
  { "Sonnet 4.6": 1 }, {}, {}, {}, {}, { "Sonnet 4.6": 2 },
  { "Sonnet 4.6": 59, "solo": 5 }, { "solo": 2, "Opus 4.8": 3, "Sonnet 4.6": 35 },
  { "Sonnet 4.6": 54, "solo": 15, "Opus 4.8": 1 }, { "solo": 43, "Sonnet 4.6": 26, "Opus 4.8": 14 },
  { "Sonnet 4.6": 52, "Opus 4.8": 4, "solo": 7, "Haiku 4.5": 4 },
  { "solo": 19, "Sonnet 4.6": 161, "Haiku 4.5": 28 }, { "Sonnet 4.6": 150, "solo": 21 },
  { "Sonnet 5": 56, "solo": 16, "Fable 5": 40, "Sonnet 4.6": 5 }, { "Fable 5": 7, "Sonnet 5": 22 }
];
(function () {
  var totals = COND_WEEKS.map(function (w) {
    var s = 0; for (var k in w) s += w[k]; return s;
  });
  var max = Math.max.apply(null, totals);
  var el = document.getElementById("cond");
  COND_WEEKS.forEach(function (w, i) {
    var col = document.createElement("div"); col.className = "cond-col";
    var h = totals[i] === 0 ? 0 : Math.max(4, Math.round((totals[i] / max) * 64));
    COND_MODELS.forEach(function (m) {
      if (!w[m.key]) return;
      var seg = document.createElement("div"); seg.className = "cond-seg";
      seg.style.background = m.color;
      seg.style.opacity = m.key === "solo" ? "0.55" : "0.85";
      seg.style.height = Math.max(2, Math.round((w[m.key] / totals[i]) * h)) + "px";
      tipWire(seg, (m.label || "CLAUDE " + m.key.toUpperCase()) + " · " + w[m.key] + " COMMITS<small>" + weekName(i) + " · " + Math.round((w[m.key] / totals[i]) * 100) + "% of the week's pen time</small>");
      col.appendChild(seg);
    });
    el.appendChild(col);
  });
  var lg = document.getElementById("condlegend");
  COND_MODELS.forEach(function (m) {
    var s = document.createElement("span");
    s.innerHTML = '<i style="background:' + m.color + '"></i>' + (m.label || "CLAUDE " + m.key.toUpperCase()) + " · " + m.total;
    lg.appendChild(s);
  });
})();

// Depth explorer
var ALT_NAMES = ["ONE PAGE", "DIRECTION", "PROCESS", "DETAIL", "COMMITS"];
var ALT_DESC = [
  "one plain sentence per milestone",
  "why each path was chosen",
  "how the work actually ran",
  "the moves, including the mistakes",
  "every milestone linked to its real code"
];
var ALT_CFG = [
  { maxRank: 1, text: 0, commits: false },
  { maxRank: 2, text: 1, commits: false },
  { maxRank: 3, text: 2, commits: false },
  { maxRank: 3, text: 3, commits: false },
  { maxRank: 3, text: 3, commits: true }
];
var currentAlt = 0;

function buildCommits(m) {
  var cwrap = document.createElement("div"); cwrap.className = "ms-commits";
  m.commits.forEach(function (c) {
    var row = document.createElement("div"); row.className = "ms-commit";
    row.innerHTML = '<span class="msha" style="font-family:var(--mono);color:var(--faint)">' + c.sha + '</span><span>' + c.msg + '</span>';
    cwrap.appendChild(row);
  });
  return cwrap;
}

function render() {
  var cfg = ALT_CFG[currentAlt];
  var list = document.getElementById("mslist");
  list.innerHTML = "";
  var shown = 0;
  MILESTONES.forEach(function (m) {
    if (m.rank > cfg.maxRank) return;
    var text = "";
    for (var i = cfg.text; i >= 0; i--) { if (m.alt[i]) { text = m.alt[i]; break; } }
    if (!text) { for (var j = cfg.text + 1; j < m.alt.length; j++) { if (m.alt[j]) { text = m.alt[j]; break; } } }
    // Deepest narrative this milestone has - used by the per-card expand.
    var deepIdx = -1;
    for (var d = m.alt.length - 1; d >= 0; d--) { if (m.alt[d]) { deepIdx = d; break; } }
    var hasDeeper = (deepIdx >= 0 && m.alt[deepIdx] !== text) || (!cfg.commits && m.commits && m.commits.length);
    shown++;
    var card = document.createElement("div"); card.className = "ms" + (hasDeeper ? " expandable" : "");
    var top = document.createElement("div"); top.className = "ms-top";
    top.innerHTML = '<span class="ms-date">' + m.date + '</span><span class="ms-title">' + m.title + '</span>' +
      '<span class="ms-rank r' + m.rank + '">' + (m.rank === 1 ? "CORE" : m.rank === 2 ? "PLUS" : "DEEP") + '</span>';
    var body = document.createElement("div"); body.className = "ms-body"; body.innerHTML = text;
    card.appendChild(top); card.appendChild(body);
    var pf = document.createElement("div"); pf.className = "ms-proof";
    if (m.proof) { pf.innerHTML = '<a class="ms-verify" href="' + m.proof.url + '" target="_blank" rel="noopener">verify ↗ <span>' + m.proof.label + '</span></a>'; }
    else { pf.innerHTML = '<span class="ms-selfattest">internal · self-attested</span>'; }
    card.appendChild(pf);
    if (cfg.commits && m.commits && m.commits.length) {
      card.appendChild(buildCommits(m));
    }
    if (hasDeeper) {
      var more = document.createElement("div"); more.className = "ms-more"; more.textContent = "▾ TAP FOR FULL DEPTH";
      card.appendChild(more);
      card.addEventListener("click", function (e) {
        if (e.target.closest(".term") || e.target.closest("a")) return;
        var expanded = card.classList.toggle("expanded");
        body.innerHTML = expanded ? m.alt[deepIdx] : text;
        var cw = card.querySelector(".ms-commits");
        if (expanded && !cw && m.commits && m.commits.length) card.insertBefore(buildCommits(m), more);
        if (!expanded && cw && !cfg.commits) cw.remove();
        more.textContent = expanded ? "▴ COLLAPSE" : "▾ TAP FOR FULL DEPTH";
      });
    }
    list.appendChild(card);
  });
  document.getElementById("readout").innerHTML =
    'DEPTH: <strong>' + ALT_NAMES[currentAlt] + '</strong> · ' + shown + ' of ' + MILESTONES.length +
    ' milestones · ' + ALT_DESC[currentAlt];
  document.querySelectorAll(".alt-btn").forEach(function (b) {
    b.classList.toggle("active", Number(b.dataset.alt) === currentAlt);
  });
}

document.querySelectorAll(".alt-btn").forEach(function (b) {
  b.addEventListener("click", function () { currentAlt = Number(b.dataset.alt); render(); });
});
document.addEventListener("keydown", function (e) {
  if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
  if (document.getElementById("pres").classList.contains("on")) return;
  var k = e.key;
  if (k >= "1" && k <= "5") { currentAlt = Number(k) - 1; render(); }
});
render();

// Progressive disclosure - collapsible sections; FOCUS mode is the default
(function () {
  var sections = Array.prototype.slice.call(document.querySelectorAll(".section"));
  var expandBtn = document.getElementById("fb-expand"), focusBtn = document.getElementById("fb-focus");
  var TLDRS = [
    "Twelve design principles set before the first feature, each enforced in code, plus the loop that keeps learning that they run.",
    "Day 0 to today at whatever depth you want, from one plain sentence per milestone down to the actual commits.",
    "Where I was wrong and what changed: delete before you rebuild, enforce don't decorate, honesty over polish.",
    "What I'd tell a board today: single-operator context, gated features, vendor concentration, each with its mitigation.",
    "One backlog, three horizons. Nothing moves up on enthusiasm; every later item has a named condition that promotes it.",
    "The whole roadmap hangs on one dependency, scored outcomes, and it shipped on Day 98.",
    "Every piece of product vocabulary on this page, translated into plain words."
  ];
  var focusOn = true;
  function open(sec) { sec.classList.remove("collapsed"); sec._body.style.maxHeight = "none"; }
  function collapse(sec, instant) {
    var b = sec._body;
    if (!instant && (b.style.maxHeight === "none" || !b.style.maxHeight)) { b.style.maxHeight = b.scrollHeight + "px"; void b.offsetHeight; }
    b.style.maxHeight = "0px"; sec.classList.add("collapsed");
  }
  function toggle(sec) {
    if (sec.classList.contains("collapsed")) {
      open(sec);
      if (focusOn) sections.forEach(function (o) { if (o !== sec) collapse(o); });
    } else { collapse(sec); }
  }
  sections.forEach(function (sec, idx) {
    var head = sec.querySelector(".section-head");
    if (!head) return;
    var body = document.createElement("div"); body.className = "sec-body";
    var node = head.nextElementSibling;
    while (node) { var next = node.nextElementSibling; body.appendChild(node); node = next; }
    sec.appendChild(body); sec._body = body; body.style.maxHeight = "none";
    // Pull the headline out of the collapsible body so it stays visible when folded
    var title = body.querySelector(".section-title");
    if (title) sec.insertBefore(title, body);
    // TL;DR line - shown only when collapsed
    var tldr = document.createElement("div"); tldr.className = "sec-tldr"; tldr.textContent = TLDRS[idx] || "";
    sec.insertBefore(tldr, body);
    var tog = document.createElement("span"); tog.className = "sec-toggle"; tog.textContent = "▾";
    head.appendChild(tog);
    [head, title, tldr].forEach(function (el) { if (el) el.addEventListener("click", function () { toggle(sec); }); });
  });
  expandBtn.addEventListener("click", function () {
    focusOn = false; expandBtn.classList.add("active"); focusBtn.classList.remove("active");
    sections.forEach(open);
  });
  focusBtn.addEventListener("click", function () {
    focusOn = true; focusBtn.classList.add("active"); expandBtn.classList.remove("active");
    sections.forEach(function (s, i) { i === 0 ? open(s) : collapse(s); });
  });
  // Default state: FOCUS mode, section 01 open, the rest folded to their TL;DR (no load animation)
  focusBtn.classList.add("active"); expandBtn.classList.remove("active");
  sections.forEach(function (s, i) { i === 0 ? open(s) : collapse(s, true); });
})();

// Mobile: horizontal swipe on the milestone list steps the depth dial
(function () {
  var sx = null, sy = null, ml = document.getElementById("mslist");
  ml.addEventListener("touchstart", function (e) { sx = e.changedTouches[0].clientX; sy = e.changedTouches[0].clientY; }, { passive: true });
  ml.addEventListener("touchend", function (e) {
    if (sx === null) return;
    var dx = e.changedTouches[0].clientX - sx, dy = e.changedTouches[0].clientY - sy;
    sx = sy = null;
    if (Math.abs(dx) > 64 && Math.abs(dx) > Math.abs(dy) * 1.6) {
      currentAlt = Math.min(4, Math.max(0, currentAlt + (dx < 0 ? 1 : -1)));
      render();
      document.getElementById("altbar").scrollIntoView({ block: "nearest" });
    }
  }, { passive: true });
})();
// Term tooltips: one viewport-clamped floating element. Hover on desktop, tap-toggle on touch.
var termTip = document.createElement("div"); termTip.id = "termtip"; document.body.appendChild(termTip);
var termActive = null;
function showTermTip(el) {
  termTip.textContent = el.getAttribute("data-def") || "";
  termTip.classList.add("on");
  var r = el.getBoundingClientRect(), tw = termTip.offsetWidth, th = termTip.offsetHeight;
  var cx = r.left + r.width / 2, half = tw / 2;
  cx = Math.max(half + 10, Math.min(window.innerWidth - half - 10, cx));
  var above = r.top - th - 9;
  termTip.style.left = cx + "px";
  termTip.style.transform = "translateX(-50%)";
  termTip.style.top = (above >= 8 ? above : r.bottom + 9) + "px";
  termActive = el;
}
function hideTermTip() { termTip.classList.remove("on"); termActive = null; }
document.addEventListener("mouseover", function (e) {
  var t = e.target.closest ? e.target.closest(".term") : null;
  if (t && t !== termActive) showTermTip(t);
});
document.addEventListener("mouseout", function (e) {
  var t = e.target.closest ? e.target.closest(".term") : null;
  if (t && t === termActive) hideTermTip();
});
document.addEventListener("click", function (e) {
  var t = e.target.closest ? e.target.closest(".term") : null;
  if (t) { termActive === t ? hideTermTip() : showTermTip(t); }
  else if (termActive) hideTermTip();
});
window.addEventListener("scroll", function () { if (termActive) hideTermTip(); }, { passive: true });

// Architecture-diagram lightbox: expand the whole loop into a full-screen view (no scrollbar needed)
(function () {
  var btn = document.getElementById("flowexpand");
  if (!btn) return;
  var svg = document.querySelector(".flow-svg");
  var lb = document.createElement("div");
  lb.className = "flow-lightbox";
  lb.innerHTML = '<button class="flow-lightbox-close" type="button">CLOSE ✕</button>';
  var clone = svg.cloneNode(true);
  clone.removeAttribute("class");
  lb.appendChild(clone);
  document.body.appendChild(lb);
  function open() { lb.classList.add("on"); }
  function close() { lb.classList.remove("on"); }
  btn.addEventListener("click", open);
  lb.addEventListener("click", function (e) { if (e.target === lb || e.target.closest(".flow-lightbox-close")) close(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && lb.classList.contains("on")) close(); });
})();

/* Keyboard and screen-reader access for the click-to-open surfaces that are not buttons (2026-11-12): role, tabindex, Enter/Space.
   A milestone card holds links, so its focusable toggle is the header row inside it (a role=button may not contain links).
   #mslist is rendered at runtime, so the enhancement reruns when it changes. */
(function () {
  var SEL = ".section-head, .ms.expandable .ms-top, .cad-col.design-win";
  function enh() {
    [].forEach.call(document.querySelectorAll(SEL), function (el) { if (!el.hasAttribute("tabindex")) { el.setAttribute("tabindex", "0"); el.setAttribute("role", "button"); } });
    [].forEach.call(document.querySelectorAll(".ms.expandable .ms-top"), function (el) { el.setAttribute("aria-expanded", String(el.parentNode.classList.contains("expanded"))); });
    [].forEach.call(document.querySelectorAll(".su-tw"), function (el, i) { el.setAttribute("tabindex", "0"); el.setAttribute("role", "region"); el.setAttribute("aria-label", "Table " + (i + 1) + ", scrolls sideways"); });
  }
  document.addEventListener("keydown", function (e) {
    if ((e.key !== "Enter" && e.key !== " ") || !e.target.matches || !e.target.matches(SEL)) return;
    e.preventDefault(); e.target.click();
  });
  enh();
  var ml = document.getElementById("mslist");
  if (ml && window.MutationObserver) new MutationObserver(enh).observe(ml, { childList: true, subtree: true, attributes: true, attributeFilter: ["class"] });
})();
