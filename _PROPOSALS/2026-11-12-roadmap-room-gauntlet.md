# Roadmap room gauntlet (independent review, 2026-11-12)

Files read: roadmap.html (data JSON parsed), scripts/roadmap_render.py, DESIGN.md, WORLD.md, craft-floor.md. `_QUEUE/induced-backlog.jsonl` is not in this worktree upload, so row-level priority could only be checked against the rendered JSON.

## 1. Steelman
- The arithmetic holds: 352 + 287 = 639. 318 backlog rows + 34 debt nodes = 352. The ten unsequenced kinds sum to 287.
- Every row names a source: 0 of 352 jobs and 0 of 287 unsequenced rows have an empty `src`.
- Priority is copied, never guessed: `norm_pri(r.get("priority") or sev)` with `sev = None` (py 80, 87). It shows unranked honestly, 242 of 352.
- The absence rule is respected: it sweeps 10+ ledgers instead of claiming the backlog is the whole job, and it states "Waves are dependency depth, not dates" (html note, py 358).
- The risk rules are printed on the page (py 380), so any reader can audit them.

## 2. Strawman
- **Double counting.** 41 of the 72 "open GitHub issues (not debt)" are titled `[backlog] <slug>`, and all 41 slugs are already sequenced jobs. The real total is about 598, not 639. The debt dedupe (py 106) catches the `debt` label only.
- **"Can start now" is false.** The lede says 273 jobs at wave 0 "can start now". 145 of those are HELD/HOLDING, and only 24 have `ready_now`. Of the 18 jobs in state READY, 17 have `ready_now=false`. Wave 0 means "no edges", not "go".
- **Blocked has no blocker.** 13 of 15 BLOCKED jobs have `deps: []`, so the page cannot say what blocks them.
- **Rule gaps.** The one-way filter and the gold ring test `door==='one-way'` exactly (JS `pass`, `draw`), which misses `recoil-ship-twin` ("one-way (counterpart-facing)"). Concave tests `ruin in ("high","medium")` exactly (py 191), which drops `medium (PII)`, `medium (client-confidential)` and `medium (widens autopilot)`. The rows with the highest exposure are the ones that fall through.
- **Risk noise.** All 8 Convex rows are one `filing-*` chain, so they are one risk, not eight. Orthogonal is a substring count (py 210): "gate" matches any jtbd text containing the word, and "one primitive, not 36 fixes" is asserted with no isomorphism behind it. Posterior and Parabolic are Project-snapshot echoes, not roadmap risk.
- **Junk in the unsequenced table.** It holds Lore essays as "proposals awaiting ruling" ("The Exoskeleton", "The Gap"), 22 receipts titled only "overdue, unscored", 22 rows marked "stale?" from a repo last committed 2026-08-23, RET lines caught by a numbered-line regex (`todo-0` is a status note), and the counter "proposals (newest 80)", which is all 51 of them.
- **Waves read as dates.** W0 to W11 columns styled as a Gantt invite a calendar reading, and 273 of 352 bars sit in W0. The chart is really a dot plot.

## 3. Persona seats
**(a) Zach, CPO, Executive.** The 17 count tiles carry no decision. The only P0 is `prl-phase-path-close` (cash), and it is HELD. Ten other PRL rows are unranked and HELD. Demand: an income strip at the top (paid work, its state, the one move that unblocks it), with everything else below the fold.

**(b) PM, Operational.** 69% of jobs are unranked, and "Ready now" disagrees with the READY state. Demand: one "startable this week" set (`ready_now` and ranked and not HELD), with the HELD rows collapsed.

**(c) Engineer, Surgical.** The detail pane lists dep ids but not their state, and 13 blocked jobs have none. At least 20 dep ids point at non-active nodes (likely DONE; unconfirmed). Demand: dep state inline, plus a "blocked by: unstated" flag.

**(d) Hiring manager.** It reads as a solo operator sweeping 639 items while one cash row sits HELD, and the register flags this room itself as R-035, "built against the PARKED hold". Demand: never show this page externally without that framing. If it is shown, show the method (sources, rules), not the volume.

## 4. Council
- **HEAD: conditional.** The arithmetic is right, but the totals inflate (about 41 double-counted) and "can start now" mislabels.
- **HEART: no.** 639 items is an anxiety surface, and income-first is invisible on it.
- **WALLET: no for more build.** By its own Parabolic row (R-035), this room displaced the hold. Freeze it after the P0/P1 fixes.

## 5. Design seat
- **Muted contrast passes.** The premise in the brief is wrong: #8391a7 measures 5.92:1 on #0d1117, 6.42:1 on #020408 and 5.55:1 on #111827.
- **Non-text contrast fails.** Default and HELD bars use `border:1px solid var(--ln2)` (#26374a) on `--el`, which is 1.46:1. The fill is 1.07:1 against the panel. That makes 202 bars (57%) nearly invisible, below the 3:1 WCAG 1.4.11 minimum.
- **Fonts not loaded.** Inter and JetBrains Mono are declared, but there is no `@font-face` and no `<link>` (0 found), so most machines get system-ui and Menlo.
- **Focus ring.** `:focus-visible{outline:1px ...;outline-offset:-1px}` breaks the DESIGN state matrix, which calls for a 2px cyan outline.
- **Ambient glow.** `html{background:radial-gradient(...rgba(0,240,255,.05)...)}` puts glow on a surface at rest. Glow-Not-Shadow says glow appears only in response to state.
- **Decorative glass.** `#detail{backdrop-filter:blur(10px)}` at 0.94 alpha buys nothing. The blur is sanctioned only for the deck.
- **One-way glow is fine.** `.bar.oneway` glow is a sanctioned state glow. Keep it, but fix the matcher.
- **Hero-metric template.** `.counts` is 17 equal tiles of big number plus small label. It also mixes non-work counts (ADR files 88, corpus records 216, all-state rows 548) in with open work.
- **Group header semantics.** `.grp` is a div with `role=button`, which handles Enter but not Space and has no `aria-expanded`.
- **Sticky header does nothing.** `.gh` sticks inside a `.wrap` that has no max-height.
- **No empty state.** A zero-result filter shows "0 shown" and a blank grid.
- **Broken link.** `/hud` breaks when the file is opened from `_ARTIFACTS`.
- **Mono is not costume here.** Mono is used for ids, labels and data, which passes. Em-dashes: 0.

## 6. Findings

| # | Sev | Finding | Fix | Ship without? |
|---|---|---|---|---|
| 1 | P0 | 41 `[backlog]` issues double counted | Skip issues whose slug is in seq_ids | no |
| 2 | P0 | "273 can start now" while 145 are HELD | Lede uses ready_now and splits out HELD | no |
| 3 | P1 | Exact-match door and ruin rules miss 4 high-exposure rows | `startswith("one-way")`, `startswith(("high","medium"))` in py and JS | no |
| 4 | P1 | No income-first view; the P0 cash row is buried | Income strip above the tiles | no |
| 5 | P1 | Blocked rows with no deps; dep state hidden | Flag "blocker unstated"; show dep state | yes |
| 6 | P1 | HELD bar 1.46:1 non-text contrast | Border #8391a7 dashed (5.5:1) | no |
| 7 | P2 | Convex all one chain; Orthogonal is a substring count | One row per chain; drop or rename Orthogonal | yes |
| 8 | P2 | Junk unsequenced rows (lore, "overdue, unscored", stale repo) | Filter by kind; collapse "stale?" | yes |
| 9 | P2 | Fonts not loaded; 1px focus ring | Self-host or state the fallback; 2px outline | yes |
| 10 | P2 | Gantt reads as dates | Label the axis "dependency depth"; switch to a dot plot | yes |
| 11 | P3 | Ambient radial glow, glass on #detail, hero tiles | Remove; trim tiles to 4 | yes |
| 12 | P3 | `.grp` keyboard and ARIA, dead sticky, no empty state | Native `<button aria-expanded>`, empty message | yes |
