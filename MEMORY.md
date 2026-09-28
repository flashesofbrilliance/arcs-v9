# ARCS v9 — Memory Log

> **Versioning convention (amended 2026-07-19):** append new entries at top; keep only the recent
> window live. Relocate older entries to `_ARCHIVE/memory-archive.md` (never delete — archival honors
> "never delete prior versions" without paying the per-read token tax).
> Format: `## [vX.Y.Z] YYYY-MM-DD — <what changed>`

---

## [v3.70.0] 2026-09-28 — Chip rank 2: falsification count on the public audit page, stamped from the ledger (PR #591 -> `740aa55f`)

- **good.arcs.care/audit** now shows the ledger count (40), latest date (2026-09-27), and links status.arcs.care/beliefs.
  `scripts/belief_log_emit.py` stamps the marked block on the page AND the generated row of its `.evidence.jsonl`;
  `--check` (CI `belief-log` job) fails on drift, fail-on-bad proved both ways. Live verified via `get_deployment`.
- Receipt `2026-09-28--audit-page-falsification-count--ZH`. Backlog row is on PR #585's branch, not main; status
  append + closing issue #579 wait on that merge.
- Lesson: the blocking gate was `case_evidence_lint` (pre-commit), not one of the four the chip named. Run the
  hook path, not only the named gates. A computed public number must be stamped by the script that computes it.

## [v3.69.1] 2026-09-27 — Flow-State axis instrumented: om_gap + breath_net_direction on the Shavasana block (PR #598, merged 2026-09-28)

- `scripts/shavasana_handoff.py` now reads the fifth Hypersphere axis: `confidence` = backed fraction of the
  draft's sections (altitude canary cite classes), `conviction` = `--conviction 0-10` (human, null when absent,
  not imputed), `om_gap` = their distance or null; `breath_net_direction` = exhale_n - inhale_n, signed, no
  verdict (asm-009 open, Maekawa). Self-test asserts zero confidence markers on the block by the canary's regex.
- First reading `_STATE/2026-09-27-om-first-reading.md`: conviction null, confidence 0.33, net +33.
- Backlog row `flow-state-om-metric` (#582) is on PR #585, not main; status append waits for that merge.

## [v3.68.1] 2026-09-27 — Accountant keel chip: external funnel measured, distribution gap located (PR #586, draft)

- **The external funnel, from prod, founder split out:** external 10 receipts / 4 users / 6 debriefed / 0 closed,
  last external receipt 2026-07-10 (79 days, 0 in 30d). Founder 196 / 135 / 3 (a third closure, drifted, on
  2026-09-26). Anonymous 48, none after 2026-07-13. Instrument: `scripts/outcome_funnel.py` (read-only, stdlib,
  `--self-test`), feed `_STATE/outcome-funnel/2026-09-27.json`. Queries ran verbatim via Supabase `execute_sql`.
- **The gap is inflow, not conversion, and it was findable by grep:** the three live good.arcs.care surfaces
  (`/copypasta`, `/fears`, `/audit`) carried no link to the compass at all. The move: 11 kill-clause cards on
  `/fears` hand the sharpened claim to `app.arcs.care/dashboard?q=&horizon=`; dashboard reads `?horizon=`.
- **Detector comparisons must share a directory:** the kintsugi ratchet's 15-vs-2 was the HEAD copy sitting in
  `/tmp` without `DESIGN.md`. Inside the repo: 15 vs 15, no new findings.
- Unmerged: PR #586 awaits Zach's go; receipt follows the merge.

---

## [v3.68.0] 2026-09-27 — The membrane day: operator registry + MCP bridge, LEGEND, LORE, source-trust, altitude canary, witness scout, Operator 25 (11 PRs merged, 11 receipts)

- **An external "audit" (Perplexity) mapped an invented 1-19 operator numbering onto files that implement
  something else; ~1/3 of its "Full Production" cells failed a grep.** Numbering LOCKED to
  `operators/docs/PERIODIC-TABLE.md`. `scripts/operator_registry_emit.py` generates
  `operators/OPERATOR-REGISTRY.json` and refuses any binding it cannot grep (it caught its own author on run 1:
  Librarian `query` did not exist). `operators/arcs_mcp_bridge.py` (mcp 2.x, py>=3.10 venv) dispatches only via the
  registry; unbuilt operators answer `status=blocked`. PR #559 `1ffed09e`. See
  [[operator-numbering-locked-periodic-table-registry-generated]].
- **Vocabulary became data with gates:** LEGEND (`runtime/specs/legend.jsonl`, `scripts/legend.py`; every acronym
  carries an operational definition, [[always-expand-acronyms-with-operational-definition]]); LORE
  (`runtime/specs/lore.jsonl`: class x verdict, a verdict without a test is a rumor, stories never deleted);
  fate registry (`runtime/specs/fates.json`, PR #570 open). PRs #561, #569.
- **Trust became a generated table:** `runtime/specs/source-trust.json` from an events ledger; asymmetric (falsified
  1.0, confirmed 0.1, 90-day half-life, Beta prior). Its v0 formula could not let decay act; the self-test caught it
  before the first table. PR #568.
- **Operator 25 Shavasana** spec v0 + `/handoff` Step -2 (`scripts/shavasana_handoff.py`): this handoff is the first
  to run through it (breath: 31 commits / 11 merges out, 3 falsifications + 20 dissent markers in; sycophancy OK).
  PRs #566, #567. Deceipts F38-F40 filed.
- **Measured, not asserted:** the harness loads only the first 25,000 chars of MEMORY.md (spawned session), so the
  80KB project index is mostly invisible until curated. [[memory-index-load-cap-observed]].
- **Tao two-books collision raised, not resolved** (`_DECISIONS/CANON-COLLISION-tao-two-books.md`): 256 oracle rows vs
  242 rendered rows, 0 shared ids; tao-257 minted into both. Tao coverage: NFTT 2/29, TIL 0/5 → gate + backlog.
- Method banked: [[forensic-quality-bar-correct-premise-name-loss-channel]] (correct the premise, name the loss
  channel by rate/visibility/direction); recursion terminates at git.

## [v3.67.0] 2026-09-26 — NFTT contrast debt repaid + whole-corpus head-meta conformance + batch gate (merged, live)

- **take-home-trap-dossier genuine WCAG fix:** the `--dimmed` token failed AA on its real dark surfaces
  (`#64748b` = 3.63:1 on `#161b22`, 3.98:1 on `#0d1117` — and 4.31:1 even on `#020408`) and in light mode
  (`#75828f` = 3.46:1). Raised dark → kit-canonical `#748699` (AA, from `45fd49a5`), light → `#5e6b78`.
  Detector low-contrast **111 → 81**; residue all verified artifacts. Ratchet baseline dropped 111 → 81
  per its own provenance ("when fixed, drop those files' counts here"). Commits `3fbefb74`, `b235654c`.
- **Method — classify detector findings against the ACTUAL surface, not the detector's inference:** the
  impeccable detector cross-themes (dark text × light `#ffffff` fallback) and defaults unresolved text to
  `#000000`. Compute the real contrast on the surface read from the CSS; artifact vs. real falls out.
  No literal `#000` in the markup ⇒ every black-on-dark finding was a sampling artifact. See
  [[verify-recalled-defect-with-dom-measurement-not-eyeball]].
- **Whole-corpus head-meta conformance:** `nftt-gates.sh` checks title-suffix/description/robots ONE FILE
  AT A TIME, so ~9 legacy NFTT pages drifted until touched. Conformed all 9 (`· NFTT` suffix + faithful
  description; `robots=index` on the 4 public posts; `noindex` KEPT on the 4 recon-report fragments + HUD
  — the gate checks robots *presence not value*, so a sweep never breaks the int/ext air-gap). Index page
  exempt. New **Frustration Gate** `scripts/nftt_meta_gate.py` (per-file + `--all`, exempts index,
  `--self-test`) wired into pre-commit. Commits `ce2b504b` → `ef4282ee`. See
  [[run-the-repos-own-gates-before-shipping]], [[text-wrapping-defect-class-and-gate]].
- **Defang IOC emails to `[.]com`** on published dossiers: clears the gate's blanket email/PII scan AND is
  correct threat-intel hygiene; match the page's own existing defang convention rather than inventing one.
- Both merges prod-verified live on good.arcs.care (deploys READY; recon fragment confirmed still `noindex`
  live). Receipts `2026-09-26--nftt-dossier-contrast-and-gate-merge--ZH`,
  `2026-09-26--nftt-headmeta-conform-all-plus-gate--ZH`.

## [v3.66.1] 2026-09-26 — falsifiable-criteria bet for a public debate (@six vs @czar, Farcaster) + memory consolidation

- **Ask:** Zach flagged a false-binary on Farcaster (@six: personal agents close loops at scale, good for
  humanity · @czar: most people would rather live with open loops) and asked for falsifiable criteria for both.
- **Core move (reusable):** a stated kill condition can test the WRONG variable. czar's "if agents reach
  mainstream in 2y I'm wrong" measures adoption, but his claim is about desire (agents adopted to pass time
  would CONFIRM him). six's "will take time to diffuse" has no deadline, so it can't fail. Fix = decompose
  each position into sub-claims, each with observable + threshold + deadline + agreed source, pre-registered.
- **The crux test:** czar's own words ("rather than even THINK about it") mean an agent that removes the
  thinking is the discriminating experiment: does >50% keep default-on proactive loop-closing after 90 days?
  Adoption x freed-attention 2x2 shows 3 of 4 cells leave both partly right (the non-binary proof).
- **Definitions that stop technicality wins:** "agent" = acts in an external system (not a chatbot);
  "mainstream" = 16% weekly use (Rogers early-majority line); resolve 2028-09-26; no data = unresolved.
- **Shipped:** private Artifact https://claude.ai/artifact/ApVz1HbRKh575HTSBDEZZY (full wager, v2) + a
  plain-language 390px phone card rendered to PNG via headless Playwright (global install; needs
  `NODE_PATH=$(npm root -g)`). Sources banked in `_ARTIFACTS/2026-09-26-loop-closing-wager/`.
- **Gate caught a real bug:** `artifact_wrap_lint.py` measure-mismatch (860px column vs 680px prose); fixed
  by setting the column to the measure; republished. Google Fonts don't load in the cloud sandbox render,
  so the PNG uses fallback faces.
- **Consolidation:** relocated v3.46.0 and older (July to Aug 27) to `_ARCHIVE/memory-archive.md`; live log
  now holds Sept entries only. Gap noted: v3.66.0 (cold-recon trilogy) has a CLAUDE.md handoff but no
  MEMORY entry; not backfilled here (not this session's record to reconstruct).

## [v3.65.3] 2026-09-24 — gravity-well framework for candidate surfaces + 2 leak fixes; 3rd Frustration Gate

- **Reusable framework (bank this):** what turns a candidate page into a *gravity well / attractor basin*
  for a hiring manager, whose real JTBD is **de-risk the hire**. Mass = **verifiability** (a checkable,
  linked claim has mass; an adjective is massless). Depth = how much the page **pre-answers their private
  doubts before they voice them**. Width of the basin = **read-at-any-depth** (skimmer/skeptic/peer/exec
  all converge on "advance this candidate"). Other mass sources: **owned losses** (scored wrong-calls
  neutralize the skeptic's escape velocity), **the loop as strange attractor** (score→check→correct
  repeated across surfaces = "I get how they think"), **the mirror** (their exact problem worked in public
  = heaviest pull), **the pre-registered receipt** (a call filed before the outcome makes rivals'
  retrospective claims feel massless), and a **live/compounding surface** (status.arcs.care is the only one
  with an intrinsic reason to return). **Leak list (inverse):** unverifiable claims · single altitude ·
  no owned losses · no mirror · static/no-return · over-claiming (re-arms the skeptic).
- **Pressure-tested the vico family against the leak list** (grounded in live content, not asserted): memo
  = deep well already; status = compounding well; résumé + ammo each leaked. **Closed 2 leaks** (`65d3781`,
  prod-verified cache-MISS): (1) résumé had **zero mirror** → added a "worked in public" clause linking the
  ZIM/Hapag-Lloyd geopolitical call; (2) ammo **described running systems without linking them** (1 link) →
  wired the public status log → status.arcs.care and the automation pipeline → good.arcs.care (now 3 links).
  Left leak #3 (memo's own live pulse) per Zach — polish on an already-deep well.
- **status.arcs.care milestone cards + template-wide gutter fix** (see v3.65.2 handoff): 3 curated cards
  (DAY 159/167/168), and the 44-vs-40 header/footer gutter fixed on 6 sibling pages + banked
  `scripts/gutter_consistency_lint.py` (3rd Frustration Gate: div-balance · tooltip-link · gutter).
- **Deploy discipline confirmed all day:** the live domain serves `main`, not the branch — "stale" renders
  were the real live version until merge. Verify prod via Vercel API + Vercel-side fetch (`cache: MISS` =
  fresh); local `curl` is proxy-blocked (len=0 ≠ site down). `get_deployment_file_contents` 401s; gated
  `*-ammo` pages can't be HTTP-fetched raw (proxy serves the passcode gate) — verify via the atomic deploy.

## [v3.65.2] 2026-09-24 — VICO: strip VP tonality per Joe (intro, not application); smoke-test fixes; close-loop reminder set

- **Joe's morning ask (day of the 3 PM Lyndon call):** make the shared page an "introduction without
  expectations" — Lyndon should *conclude* the VP-of-Engineering fit himself, not have it pre-set.
  **Removed VP-of-Engineering tonality across ALL live shared surfaces:** memo `vico.html` (`e7fbdde`:
  the one role-claiming line + "No VP title" from the honesty beats), resume `vico-resume.html`
  (`91c091e`, option B: title/target chip/pillar/role-fit heading/honest-gap/footer → role-agnostic
  "Engineering Leadership"), and ammo `vico-ammo.html` ("VP of Engineering seat" / "hands-on VP" /
  "VP/Director title" → "engineering leadership"). Honest-gap CONTENT kept (formal title not yet held),
  just without presupposing the role. `EVP of Partnerships` (a real past IBRShop title) correctly stays.
  Internal `_ARTIFACTS/vico-vp-wargame` left as-is (do-not-send; its subject IS the VP question).
  Stale `_ARTIFACTS/vico-joe-eval` K3 evidence re-pointed to the current resume strings.
- **Back-prop discipline lesson:** when asked "are you 100% nothing is stale," DO NOT assert — SWEEP.
  A grep across every `<name>-*.html` + `_ARTIFACTS/` caught the ammo "VP seat" line and the eval's
  dead resume quotes that the memo/resume fixes alone missed. (Matches forge phase-6 rule 3: sweep every
  surface + domain, not just the one in front of you.)
- **Visual smoke-test (headless Chromium, `/opt/pw-browsers/chromium-1194`):** two regressions the user
  flagged, both verified + fixed by measurement, not eyeball. (1) The **column-collapse** (unclosed
  `.row` div) — confirmed FIXED: How-I-build/Leadership/Craft now share x=271, w=738, stacked; the
  user's screenshot of it was a stale pre-fix render. (2) **Footer indent** — real 4px: body sections
  use `.pad` (40px gutter) while header+footer used 44px. Unified all three to 40px → delta 0 at
  1280/768/375. Import gotcha: playwright is CJS — `import pw from '.../playwright/index.js'; const {chromium}=pw`,
  and point the import at the repo's node_modules (scratchpad can't resolve it).
- **Landing is the LEANED version** (confirmed vs a revert worry): Ahmed 60-second-read lean `2db5bee` +
  Why-pruned-to-top-2 `3e40a5e` are both in HEAD, with all of today's edits stacked on top. ~1148 visible words.
- **Close-loop reminder SET** (`send_later` trig `trig_01FS48pXd5V6vbPne6E7p8KB`, fires 2026-09-24
  20:30 UTC / 4:30 PM EST): score the 5 beats after Joe×Lyndon, check if Lyndon reached the URL vs
  Joe's paraphrase (message-drift lever), plan follow-up + the Autopilot parallel path.

## [v3.65.1] 2026-09-23 — vico send: fact-check vs VICO's site, div-balance lint, Joe email SENT

- **Joe email SENT** (thread `1a0cf7ab604aa2e4`): corrected 5-beat memo pitch + one-screen Lyndon
  talking-points card, for Joe's **3 PM EST Thu 2026-09-24 call with Lyndon**. Beat-2 corrected
  **"finance" → "regulated industries"** (government/insurers/banks — honest AND points harder at
  VICO's federal motion). The prior fuller Gmail draft was never sent and Gmail auto-discarded it;
  a fresh reply draft was created and Zach sent it.
- **VICO fact-check (uploaded vico.io careers + product HTML):** their site is a JS-SPA — tag-stripping
  yields ~23 chars; grep the RAW file for fact-strings. CONFIRMED by their own copy: tagline "AI-powered
  forecasting and simulation for decision superiority", "financial institutions AND governments",
  geopolitical event tickers (Iran clerical-regime, Venezuela Risk `VICOIVNZ`), a Bloomberg comparator.
  NOT on their site: "150,000 sources", Brier, Polymarket/Kalshi by name, "Israel". Memo opener reworded
  to their vocabulary (prod `ca38b69`). **Careers page = 4 open GTM/leadership roles** (VP Eng NY "partner
  with the CTO to drive execution + grow the team"; Head of Sales NY; **Head of Federal Sales DC** founding;
  Head of Marketing) — confirms Zach's IC-to-manager + public-sector positioning is aimed right.
- **Second Frustration Gate lint banked:** `scripts/html_div_balance_lint.py` — an unclosed `.row` `<div>`
  (ends in `</p>`, no `</div>`) nests the next sibling and collapses it into a pinched column; invisible to
  wrap-lint (nothing overflows). Gate counts `<div>` vs `</div>` per page (strips script/style), proven
  fails-on-bad/passes-on-good, wired into pre-commit (added+modified). Fix commit `1859b86`, gate `6bd191f`.
- **Lessons (portable):** (1) **Do not assert a tool's negative as a world-fact** — a failed measurement
  (MCP 404 on analytics) is not "it's off"; verify against source. (2) **Gmail rewraps outbound hrefs**
  through `google.com/url` at send; to get a clean URL in front of someone, paste the domain as PLAIN TEXT
  (no `<a>`), which also forwards better. Use this by default on future Joe/Lyndon-facing emails.
- Night-moves digest: `_STATE/night-moves/2026-09-23.md` (41 commits, 3 workstreams, 0 ADR/DEWY minted —
  execution-heavy day; residue is the two lints, not new architecture).

## [v3.65.0] 2026-09-23 — vico.arcs.care family refit (plain-language, tooltips, moiré, eval) + two banked failure modes

- **vico family shipped** (prod main `3e40a5e`): the "Zach × VICO" partnership memo, deeper case, and
  VP resume rebuilt in plain language with status.arcs.care-style hover/tap **glossary tooltips**, the
  chan **moiré** deck backdrop, the **one-loop spine** (score→check→correct), earned-fidelity render, and
  a **"How I tried to break this"** honesty beat. Closing-the-Loop promoted into the TIL series with a
  **light-recoil render** at `/blog/til/closing-the-loop` (dark NFTT render kept at `/blog/nftt/`). Landing
  leaned 1770→1094 words; Why-interests pruned to the top two whys (instrument-panel-is-the-product +
  public-sector/government fit). Joe changelog drafted in Gmail (not sent).
- **Two Joe calls are two different opportunities** — do NOT conflate. Sep-14 "Joe - CTO" (Granola
  `c8e1da62`) = **Autopilot** (copy-trading / RIA consumer fintech); its **Catholic / mission-driven
  recruiting framing belongs to Autopilot's co-founders, NOT VICO**, and must stay off the VICO page.
  Sep-17 (Granola `e347f4d2`) = **VICO** (transcribed "Veeqo"): government/public-sector emphasis
  (DC/NY, interfaces with government customers), Lyndon's phrase "an engineer who builds LLMs that don't
  exist," foreground senior-IC preference while open to VP, Token Savings Bank as a proof point. Joe is a
  strong channel for process/bar/candor, a poor one for company/people/technical nuance — the page
  carries the nuance to Lyndon directly rather than relying on Joe's retelling.
- **Failure mode banked → lint:** a glossary `.term` wrapped in an `<a>` had its link nav blocked by the
  tooltip click handler's `preventDefault`. Fix = `if(t.closest('a'))return;` guard. Gated by
  `scripts/tooltip_link_lint.py` (fails-on-bad/passes-on-good, wired into pre-commit on added+modified
  public/_ARTIFACTS HTML). Frustration Gate, AGENTS #15.
- **Joe-beats eval** (`_ARTIFACTS/vico-joe-eval/`): 16 beats (12 email + 4 Sep-17 call) graded S against
  the live pages, one honesty asterisk (unverified 0.15 Brier premise, handled by omission). The eval is
  INTERNAL / do-not-send.

## [v3.63.0] 2026-09-15 — arcs-algorethics: scaffold → tested repo; honest benchmarks; PR #446 held

- **arcs-algorethics PRs #1–#8 merged** (main `a3ae0c3`): E2E suite (boots daemon), HF + AgentHarm
  benchmarks with nightly history, `arcs ops` CLI, `specs/invariants.json` SSOT + parity gate, ledger
  renamed `gate_receipts` + preflight, Ed25519-signed resume with operator key custody, unwired
  scaffolding deleted, README honest inventory.
- **Numbers:** ethics recall 0, JailBreakV 0/200, AgentHarm 0/176 harmful AND 0/176 benign. Purpose
  settled: narrow brake on life/vital-care/livelihood one-way doors, not a harm classifier.
- **arcs-v9:** keyed Edge gate route in PR #446, build green, unmerged by design. Empty Perplexity
  branch deleted. Queue item `algorethics-in-scope-benchmark` (#449) replaces the drifted "widen" item.
- **Blockers are credentials, not code:** algorethics schema not exposed (existence unverified);
  `ARCS_GATE_KEY`/`SUPABASE_*` unset on Vercel + Actions. Supabase MCP here is wrong-org.
- **Lesson:** assume the spec is stupid first; the Perplexity handoff carried four false premises.

## [v3.62.0] 2026-09-14 — Schriner/Oxenham job-search engagement: full recoil lifecycle + resume correction

- **`schriner.arcs.care`** (recruiter pitch + resume viewer/PDF/ATS) and **`schriner-ext.arcs.care`**
  (safe external recoil twin, air-gap verified) shipped live via normal PR/merge.
- **Resume correction shipped live**: technical-cut resume first sent to Joe had dropped real
  leadership scope; corrected to a three-modes (builder/team-lead/executive-partner) framing and a
  closed 2010-2016 work-history gap (Selectable Media, IBRShop), sourced from real iCloud PDFs.
- **Internal recoil receipt** closed post-call at FORK/DIVERGENT; the CEO-identity gate was resolved
  by independent search after the call, not by the recruiter on it — generalized into
  `inbound-opportunity-three-gate-smoke-test` memory (verify identity BEFORE the call).
- **Global memory**: new project memory `project_joe_schriner_oxenham_autopilot_vico`, new feedback
  memory `technical-cut-resume-must-keep-leadership-scope`, `MEMORY.md` index deduped/tidied.
- **Open**: Joe-facing fit-note drafted, held pending follow-up call; `resume-tailor` skill repo
  itself not yet updated with the lesson (deferred to next session).

## [v3.61.0] 2026-09-13 — Bridge employer index live · Triune Stream A/B/C landed · seed bank clean

- **`scripts/bridge_index_scan.py`** (new, stdlib): curated employer lists → public ATS boards → winnable
  reqs → jobs.arcs.care. 578 rows live as `bridge_scan` UNSCORED across 84 employers; index at
  `_STATE/job-search/employer-index/`. Ingest skips existing jobids (API upsert would reset scores).
- **ADR-078/079/080/081 + 041 on main** — the three 2026-08-03 hold branches renumbered through the
  oracle and merged (#408–#413); `_STATE/worktree-audit-2026-09-11.md` is the patch-id sweep of all 74 worktrees.
- **`scripts/scout_dossier_ingest.py`** (new): Perplexity dossier gate (validate/map/post). Caught real
  drift on first use (Parloa lacks `extraction_risk`).
- **Seed bank**: +4 candidates, 2 orphans receipted, 4 broken locals fixed; drift check OK (41/80).
- **Receipts**: 8 `decision_receipt` rows this session; AGENTS.md now documents the CHECK enums.
- Cross-harness: `_STATE/convergence.json` on `fresh-starts` beat 6; Hermes owns JTBD-004, Perplexity JTBD-007.
- Next: Thread 2 scores the bridge rows; human prune call on 17 worktrees; Workday adapter seed.

## [v3.57.0] 2026-09-07 — Reading Room back-propagation organ (1b gate MET)

- **`scripts/cache_backprop.py`** (new, stdlib): the Metabolic Router's lazy pull-driven repair for a
  DIRTY `(domain, epoch)` cache slice. `plan` (list dirty) → `packet` (assemble a Curator work-packet:
  slice nodes + cited provenance AS-IS at HEAD + rubric) → `apply` (write graded statuses back into the
  digest, stamp only THAT slice fresh). Grading is JUDGMENT and stays external by construction
  (NOTOMATION) — the script never grades.
- **Per-slice grade preservation** (the load-bearing fix in `cache_manifest.py`): `stamp`/`check` now
  carry a prior slice's recorded `graded_at_sha` forward instead of recomputing it from the shared
  digest file's last commit. Without this, re-grading one epoch falsely frees every sibling epoch that
  shares the file. Only a *complete* re-grade advances the sha; `--partial` leaves the slice dirty and
  says so (WITNESS honesty).
- **Gauntlet before commit** (runner + adversarial skeptic, refuter per finding) — 3 real defects found
  and fixed: (1) write-before-validate left a half-graded digest on a bad apply (KINTSUGI: all
  validation now precedes the write); (2) `--partial` falsely stamped the whole slice fresh; (3) a
  cleared note outlived a status change. 5 stdlib tests green (`scripts/tests/test_cache_backprop.py`).
- **1b gate MET**: proved end-to-end — `product/2026-04` dirty → re-graded LIVE → fresh, 19 siblings
  stay dirty; freshness survived a full re-stamp AND 11 commits of base advance. PR #320 → `343b266`.
- **Lesson banked**: when many slices share one provenance/digest file, freshness MUST be tracked
  per-slice in the manifest, never derived from the shared file's git history — the shared file is the
  wrong granularity and silently over-frees.

## [v3.56.0] 2026-09-07 — wrap-lint MODE 5 safeguard, post-4 s-tier pass, Dealroom research, ADR-076 MCP-led growth

- **wrap-lint MODE 5** (`scripts/artifact_wrap_lint.py`, pre-commit wired, PRs #256/#258/#260): gates the
  desktop measure/container-mismatch wrap bug that overflow checks miss. `<style>`-only scan, CSS-comment
  strip, FP-reducer for `max-width:none` overrides, `wrap-lint-allow: measure-mismatch` opt-out for
  intentional two-width designs. Fixed dossier + 3 ledes; marked wing/scott-cut/observatory. AEO
  robots/sitemap reachable on good.arcs.care (proxy + next.config both layers).
- **NFTT post-4 impeccable pass = s-tier, zero edits**; posts 1-3 swept clean. Template gives diamond-cut
  text handling by construction; 4-width JS test method banked.
- **Dealroom talent research** (`_ARTIFACTS/research/2026-09-04-dealroom-talent-report-grammar.md`, PR #273):
  15 report/viz patterns + MCP-led-growth GTM analysis.
- **ADR-076 — MCP-Led Growth: the attribution wedge** (PR #307). DRAFT/YELLOW, demand-probe gated.
  Drafted as ADR-075; renumbered to 076 after a parallel session's DECIDED **ADR-075 Metabolic Router**
  merged first (oracle-first: ratified canon keeps the number, unmerged draft renumbers; audit no-dup).
- Housekeeping: lattice epoch re-pinned e9 (spot-check); iCloud deliverable→Files sync convention; 5 new
  memories banked (MODE-5 tripwire doctrine, MCP-led-growth, dealroom grammar, NFTT provenance/aphorisms).

## [v3.53.0] 2026-09-04 — The Reading Room: the Almanac, ADR-075 the Metabolic Router, locked build plan

- **Almanac** (`scripts/research_render.py`): 264 full-temporal epoch-tagged nodes read at 3 altitudes
  (Skim/Scan/Trenches); two-shelf Required Reading (Foundational by canon + Load-bearing by in-degree);
  per-row export. Local-only. Library taxonomy: Alexandria index / Atlas map / Almanac dated state.
- **ADR-075** minted through the oracle from a live witness: mechanical fan-out automatable, judgment
  never; integrity gate = cites exist on origin/main (caught 5 memories describing never-merged gates).
- **Locked plan** `_SPECS/reading-room-build-plan-v1.md`: spine (Desk+Reader+cache) first, tenants
  cheap; token-savings-bank levers; CBA ledger. Loop: Desk -> Almanac -> Concordance -> Chronicle -> Lexicon.
- growth-ai.arcs.care family live; recruithaus `/ammo` gated live; Blacksmith polish; drift swept.
