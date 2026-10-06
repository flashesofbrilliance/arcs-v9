# ARCS v9 — Memory Log

> **Versioning convention (amended 2026-07-19):** append new entries at top; keep only the recent
> window live. Relocate older entries to `_ARCHIVE/memory-archive.md` (never delete — archival honors
> "never delete prior versions" without paying the per-read token tax).
> Format: `## [vX.Y.Z] YYYY-MM-DD — title` then 2-4 bullets.

## [v3.85.0] 2026-10-05 — cruft_sweep prune: own-HEAD bundles (#807) + incremental bundles (#809)

- Prune refuses non-worktrees and tip != HEAD (exit 2); detached heads pinned `refs/cruft-archive/<name>-<sha8>`; bundles `^origin/<base>`.
- `--self-test` 13 checks, fails on both prior versions; pre-commit runs it when staged. No live prune on the new code yet.

## [v3.83.0] 2026-10-05 — COURT probe declares admin-guard carve-outs (#780); #762 #780 #766 merged without full CI

- `probes.COURT.allowed_carveouts` {route, term, why}: undeclared carve-out fails; dev-outside-prod sanctioned. Swipe `evalRow` declared.
- Re-check main CI on the first non-cancelled run containing `eec73f51`.

## [v3.82.0] 2026-10-05 — Worktree hooksPath repointed (PR #756); #760 + #756 merged without CI during an Actions outage

- Desktop app writes the main checkout's absolute hooksPath per worktree; `scripts/hookspath_arm.sh` + session-start repoint it. Only worktrees containing `04622e99` self-heal; ordering vs the app untested.
- GitHub Actions major outage 2026-10-05: re-check the unrun checks on #760 and #756.

## [v3.81.1] 2026-10-05 — Backlog freshness clock + grooming (PRs #713 #759 #767); gh-actions-billing reopened

- `scripts/backlog_freshness.py`: rows past review_by (explicit or derived P1 7d / P2,none 21d / P3 45d / HELD trigger); stalled STARTING/DELEGATED flagged revert-to-OPEN; decides nothing.
- 33 rows groomed over 2026-10-04/05; ~13 P1 rows due 2026-10-12. Numbered .1 because a parallel session took v3.81.0.

## [v3.81.0] 2026-10-05 — Job Factory: prototype read, gauntleted spec, slices 0+1 merged (#754 #757), morning loop dead since 9/11 and fixed

- Spec is the claude.ai doc dd89f5d5; 5 slices open (#761 #769 #771 #773 #775), merge on green after the GitHub Actions outage.
- Find stalled 2026-09-11: dirty main checkout broke `git pull --ff-only`, runs still read "succeeded"; task now runs in `.claude/worktrees/morning-jobs` with a loud preflight.
- Seeds 5-16 planted from job-tracker-pro (9 candidates, 3 anti-seeds); culture cap unproven on live rows.

## [v3.80.0] 2026-10-05 — Family-roster drift cleared; build.html glow overflow; stale worktree hooks found (PR #745)

- `sync_family_roster.py` accepts locked (carded, non-linking) performers; ADR stat 79; masthead glow held to gutter below 1280px.
- Kintsugi "77 -> 95" was a phantom: 25/27 worktrees run the main checkout's stale pre-commit via absolute `core.hooksPath`; chip task_bd140094.

## [v3.79.0] 2026-10-05 — Schriner recoil-close on Vico calls; recoil gate fix; Lyndon pre-call refresh (PRs #742 #746)

- Schriner SSOT closed YELLOW/CONVERGENT, req_reality 2; P10-P13 added (owner engaged, seat unarchitected, comp floor stated at <=2, Autopilot stalled).
- `scripts/recoil_brief.py` gate: sessionStorage wrapped in try/catch; blocked storage had killed the Enter listener in data:/file-pane previews.
- Lyndon pre-call (`2026-10-03-oh-vico.json`, from #699) refreshed, not rebuilt.

## [v3.79.2] 2026-10-05 — Trust contract 1.5 + privacy v1.3: SAGE, analytics and shared-link disclosure (privacy PR 2)

- Code: anon compass questions never cached; per-user cache key; account delete removes Blob uploads first; /api/brief response drops userId, prep.adversarialInput, raw output beyond reasoning; reminder links HMAC-signed with AUTH_SECRET.

## [v3.78.0] 2026-10-04 — Cloud wind-down + v3.76.0 open items: shavasana exhale scoped by branch, post-1 measure pinned (PRs #714 #718 #721 #728)

- `scripts/shavasana_handoff.py` exhale: counted by `git config user.name`, which reads 0 in cloud (author owner, committer Claude); now scoped to the session branch (merged PRs from it + their commits + unmerged), identity fallback on main. `--self-test` 8/8.
- `post-1-brief` / `post-1-exec`: `max-width:68ch` → `680px` on `<main>`, and in `scripts/blog_render.py`; the renderer lags its outputs, so edit those pages in place.
- Contrast ratchet: npm `impeccable@4.1.0` runs in cloud but 14/42 NFTT pages read over baseline; cause (version drift vs series-panel regression) to be settled by one Mac run.
- Wind-down: all cloud + Remote Control sessions asked to push, then archived; open asks for Zach listed in the CLAUDE.md v3.78.0 block.

---

## [vX.Y.Z] YYYY-MM-DD — <what changed>`

---

## [v3.79.0] 2026-10-04 — Field landing on arcs.care (PR #705 `81db248a`); privacy hotfix (PR #737 `85ec7a5d`)

- Home = survey field + compact header waitlist; `/api/lead` hardened; trust 1.4 / privacy v1.2. Receipts `2026-10-04--field-landing-waitlist-pr705--ZH`, `2026-10-04--privacy-hotfix-annotations-pr737--ZH`.
- Showcase mirror tooling on `claude/showcase-mirror` (unpublished); its review found the anon-read bug fixed in #737 and four more queued as privacy PR 2.

## [v3.77.0] 2026-10-04 — Video cut type: one shot spec to an HTML scene + a prompt pack; exoskeleton video v2 merged (PRs #689 `6892b016`, #709 `8f2f98e2`)

- `scripts/video_cut.py`: `_QUEUE/video/<id>.json` -> `_PROPOSALS/video/<id>-<16x9|9x16>.html` (seek(t) scenes for `html_video_render.mjs`, kit tokens, Inter + JetBrains Mono from `public/fonts/`) + `<id>-prompts.md` (per-beat prompts for external video models). Reuses linkedin_cut's gates; self-test 7 mutations. First input `tao-284`.
- #689's conflict (`connector_render.py`) resolved to main's repo-keyed row. Receipts `2026-10-04--exoskeleton-video-v2-pr689--ZH`, `2026-10-04--video-cut-type-pr709--ZH`.
- Lessons: fe-smoke page-gates fixed-size scene HTML at 375/790 (scale the stage to the viewport); the Write tool can turn escape sequences into literal em-dashes.

## [v3.76.1] 2026-10-04 — Trust contract v1.4 + privacy v1.2: waitlist and advisory capture disclosed

- `_CANON/trust-contract.md` 1.4: §1 "Waitlist and advisory requests" (stored fields, team email alert, Resend, one confirmation), §3 deletion covers lead rows case-insensitively. `/privacy` v1.2 mirrors it and names processors (Vercel, Supabase, Resend, Anthropic).
- Triggered by the survey landing replacing `/` (waitlist form on the home page). Privacy-review found the old copy claimed "anonymous sessions store nothing" while the form wrote rows.

## [v3.76.0] 2026-10-04 — NFTT bylines date the LinkedIn originals; main's generated-views fixed (PRs #697 `cb0d8772`, #703 `348ae373`, #706 pending)

- **Originals, not "first published":** every NFTT post is a new essay, so bylines date the pieces it was written from ("From the LinkedIn original(s), <dates>"). SSOT `runtime/specs/nftt-originals.json` with quoted evidence; `nftt_published.py` stamps + gates it (self-test 21/21). Six of seven series posts carry it; Tuning cites, not adapts. Dates only where the post states them; a source marked undated stays out.
- **generated-views:** #695 hand-edited `good.html`; the renderer keyed the honest card by page slug, the distribution row by repo name. `EXTERNAL_PAGES` entries may now name their row. A hand edit to a generated page reddens every PR.
- Receipts `2026-10-04--nftt-linkedin-originals-pr697--ZH`, `2026-10-04--nftt-method-byline-dedup-pr703--ZH`. Lessons: read provenance before naming it; count what a check ran before trusting its pass.

## [v3.75.0] 2026-10-04 — Stopped-light research -> 15 isomorphisms + /echo-scan skill + oracle strict-args fix + NFTT essay and companion (PRs #683 `5d64551`, #686 `44b80d1`; handoff renumbered from v3.73.0 after a parallel-session collision)

- Research note `_PATTERNS/2026-10-03-stopped-light-quantum-memory-isomorphisms.md`; 3 backlog rows with kill conditions. `/echo-scan` (nested `claim-check`, standalone-callable) minted and fresh-agent tested.
- `scripts/oracle.py`: unknown flags/extra args now exit 2; real `next <ns> --dry-run`; `--self-test` 12/12 in pre-commit. Root cause of the session's false herald (a "dry run" that allocated and stamped `_STATE/pulse.json`).
- NFTT "Light at Thirty-Eight Miles an Hour" + `/research` companion + `tao-284`. Receipts `2026-10-03--stopped-light-echo-scan-oracle-nftt-pr683--ZH`, `2026-10-04--nftt-research-companion-tao284-pr686--ZH`.
- Seeds planted: `seed-gate-hookspath-bootstrap`, `seed-pattern-strict-cli-args` (61/63 argv scripts hand-parse, 38 write), `seed-skill-echo-scan`.
- Lessons: a preview flag a tool does not recognize turns a look into a touch; a herald must come from the write it reports; `core.hooksPath` is unset in fresh clones, so gates silently skip.
- Memory consolidation 2026-10-04: v3.53.0 to v3.63.0 (2026-09-04 to 09-15) relocated verbatim to `_ARCHIVE/memory-archive.md`.

## [v3.74.0] 2026-10-04 — NFTT posts dated from git; the serialized thread denoted; index reorganized (PR #688 -> `0bfa5877`)

- **Publish time is a git fact, frozen once:** `scripts/nftt_published.py` + `runtime/specs/nftt-published.json` (32 rows). Published = first commit on main's TRUE line holding the route commit; the line hops to the second parent at "Merge ... 'origin/main' into ..." sync merges, which fast-forwards had put on the first-parent line (it misdated five posts by a day). `a-draft-is-not-a-verb` = commit-time lower bound (direct push). Every post: `article:published_time` + byline `<time data-pub>`.
- **Series as data:** `runtime/specs/nftt-series.json` + `scripts/nftt_series.py`. The seven PR #411 essays are one isomorphic series (one method, seven subjects); order/roles from Tuning's own map. Index: series 1 to 7; sections The serialized thread / The Factory on Itself / The Cold Reader / The Workshop / Field Accounts.
- Gates: both `--check`s in CI + pre-commit. Receipt `2026-10-04--nftt-timestamps-serialized-thread-pr688--ZH`. Live verified via Vercel (`dpl_7C9ivtd9NHPeWZC99bs4T1bWBGgw`); good.arcs.care is proxy-blocked from the cloud container.
- Lessons: check every git-derived row against the commit it names; generator comments that render into a page are public text (tripwire caught a repo path); `shavasana_handoff.py` misses cloud commits (author filter).

## [v3.73.0] 2026-10-04 — Essay drafted: "Tribes, Vibes, Lies" (The Exoskeleton, Not the Oracle), demand piece for a paid tier; lives in a Claude Doc, not shipped

- Doc: https://claude.ai/code/artifact/a2b5bb76-183c-4f0d-95f8-dc9f8a19e08f. Nine sections + short-version block + two pull quotes + six drawn share cards (prosthetic vs exoskeleton; Tribes/Vibes/Lies ladder; three dials + one tripwire; the decide/act/receipt/measure loop from tao-041/tao-222; the four zones from WORLD.md; a 2x2 of tao-227/220/194/045 quoted as minted) + three tributaries.
- Zach's screening instrument, now canon-adjacent: dials = good use of my time / symmetric value / right time; tripwire = stated-vs-revealed gap (tao-220 is the same rule). Quid pro quo is not symmetry: symmetry is measured over the relationship, quid pro quo settles per transaction.
- Owed: two worked examples (one pass, one yes), re-measure 2/247 against `Outcome`, port via `/nftt-story-factory`, decide what the 30-person cohort actually buys. No commits, no receipt (nothing merged or published). Backlog row `essay-tribes-vibes-lies`.

## [v3.71.0] 2026-09-28 — Chip rank 7: Librarian.recommend(q, budget), Operator 21 rebound latest -> recommend (PR #613 -> `150beb19`)

- `operators/arcs_librarian.py` (stdlib, 3.9+): value = p_load_bearing x cost_if_absent(stakes); cost = read_friction + displacement; source-trust tier before backing; unbacked -> `what_unconfirmed` only; ZERO-WEIGHT source -> no backing; `reserve_ratio` + `curation_debt` always; ouroboros demotes classes whose prior picks were falsified. `--self-test` 13/13.
- `runtime/specs/read-friction-tiers.json` (tier prose made data). Registry row 21 READY on `--probe`; bridge self-test 15/15. First real run `_STATE/librarian/2026-09-28-librarian-first-run-op21-policy.json` (1087 candidates, 6 taken, reserve 0:6; `op:21` ranked itself first).
- Receipt `2026-09-28--librarian-recommend-op21-merge--ZH`. Owed: backlog row `librarian-recommend-needle` status append (row not on main; lives on `claude/fanout-ranks-2-7`), issue #584 close.

## [v3.70.0] 2026-09-28 — Chip rank 2: falsification count on the public audit page, stamped from the ledger (PR #591 -> `740aa55f`)

- **good.arcs.care/audit** now shows the ledger count (40), latest date (2026-09-27), and links status.arcs.care/beliefs.
  `scripts/belief_log_emit.py` stamps the marked block on the page AND the generated row of its `.evidence.jsonl`;
  `--check` (CI `belief-log` job) fails on drift, fail-on-bad proved both ways. Live verified via `get_deployment`.
- Receipt `2026-09-28--audit-page-falsification-count--ZH`. Backlog row is on PR #585's branch, not main; status
  append + closing issue #579 wait on that merge.
- Lesson: the blocking gate was `case_evidence_lint` (pre-commit), not one of the four the chip named. Run the
  hook path, not only the named gates. A computed public number must be stamped by the script that computes it.

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
  `public/` and `_ARTIFACTS/` HTML). Frustration Gate, AGENTS #15.
- **Joe-beats eval** (`_ARTIFACTS/vico-joe-eval/`): 16 beats (12 email + 4 Sep-17 call) graded S against
  the live pages, one honesty asterisk (unverified 0.15 Brier premise, handled by omission). The eval is
  INTERNAL / do-not-send.
