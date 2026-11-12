---
spec_id: arcs-prep-guide
version: 2.0.0-fortified
original_path: /Users/zharris/Downloads/arcs_prep_guide_spec.md
original_sha256_prefix: fe1f3fbdae0a19f2
original_file_date: 2026-04-10
fortified: 2026-11-12 by Claude Opus 5.5 from ledger runtime/specs/fortified/ledgers/prep.json
status: DRAFT for Zach's review
---

# ARCS Prep Guide, fortified

## Cold read

- **Why this spec exists:** The Prep Guide turns one decision receipt into staged prep for a meeting with a named party: before, during and after.
- **What it is now:** A record of what the built guide does, what the April spec got wrong, and what is still unproven.
- **Why now:** The pressure test found the April spec describes a pipeline that was never built. The guide reads a Receipt, not a Brief. Two defects sit in the build: invented source labels and an unguarded JSON parse.
- **How to use it:** Before building, read Gaps and Corrected. During, treat the "What holds" table as the contract and cite its file lines. After, re-run the evidence commands and update this page.
- **How to read this page:** Every statement carries evidence (file:line or command). Anything without evidence is under Hypotheses. Line numbers in the original are from the file with the sha above.

## Verdict

Nobody should build from the April spec as written. Its data flow (Brief receipt drives the guide), its types (CompassSeed, EntityInput, BriefReceipt, GuideReceipt, UserEdits), its storage model (key-value documents) and its component list do not match the repo. A builder can trust the "What holds" section below, which describes the live route, page and schema. The original's design intent survives in parts: entity-specific stage names, a required "what they are testing" field, a tripwire, a yes/no fork per stage, and a dark-world look. Treat the build's mode-driven stage count (RECON 1, ACTIVE 2, LEAD 3 to 5) and its outcome_target block as current truth, since both are better than the spec. Fix the two defects in Gaps first.

## What holds

| Statement | Evidence |
|---|---|
| Guide lives at `/guide/[receiptId]`, a client page (GuidePage) that fetches its API. | src/app/guide/[receiptId]/page.tsx:621, 682-692 |
| API has GET (read), POST (generate), PATCH (stage log). | src/app/api/guide/[receiptId]/route.ts:186, 205, 292 |
| Guide input is the Receipt plus its PrepSession: decision, trueNorth, entity, mode, nciScore, yState, fated, protecting, stakes, horizon, confidence, adversarialInput. | route.ts:82-124, 222-225 |
| Guide is private to the receipt owner. Anonymous gets 401 in production; non-owner gets 404, never 403. | route.ts:159-172 |
| Generation is rate limited to 10 per 10 minutes per user and IP. | route.ts:217-220 |
| User picks a mode before generation: RECON, ACTIVE or LEAD. Body is zod-validated. | route.ts:174-177, 214-215; page.tsx:366 (ModeSelector) |
| Stage count is set by mode: RECON exactly 1, ACTIVE exactly 2, LEAD 3 to 5. Item counts also scale by mode. | route.ts:17-20 |
| Model output is one object: guide_title, bet_label, total_prep_hours, outcome_target, stages[]. | route.ts:52-79 |
| outcome_target has outcome_statement, leading_indicator, kpi_label, failure_signal, each with a format rule. Stored on PrepGuide and shown in OutcomeTargetCard. | route.ts:44-48; prisma/schema.prisma:264-278; page.tsx:76 |
| Per-stage fields: id, title, shortLabel, spineLabel, questionCompass (binary), stageJTBD, testingAboutThem (required by prompt), agenda, preWork, kycLens (KYC/KYT/KYB/KYI prefixes), midcurveTripwire ("If I..."), writesIntoNextTable {yes,no}, artifacts {title, abstract}. Lists are flat strings. | route.ts:22-35; page.tsx:37-51 |
| Groups are handled by a keyword rule: "panel" or "committee" in the entity expands kycLens per role. | route.ts:39 |
| Model errors, refusals and truncation return clean errors, never parsed. | route.ts:240-253 |
| Model is read from MODELS.guide, currently claude-sonnet-5-5, noted as "no eval". | src/lib/claude-models.ts:23; route.ts:242 |
| Anonymous prep is never persisted (trust contract); only signed-in users get a PrepSession row. | src/app/api/prep/route.ts:29-41 |
| Stage log stores {stageId, completedAt, verdict, vibe}; PATCH keeps one entry per stageId. | route.ts:179-184, 315 |
| Density is a 5-level ladder (Exec 90 sec to Surgical 45 min), saved in localStorage key arcs_guide_density. | page.tsx:20-30, 640-652 |
| Guide header has a back button to `/brief/[receiptId]`. (Ledger C10 said unverifiable; it is verified.) | page.tsx:769-774 |
| Dark-world tokens: bg #020408, cyan #00F0FF, green #00FF9D, gold #FFD700, inline styles only. | page.tsx:6-19; AGENTS.md gotcha 2 |

Design choices from the original that survive as intent: stage names written from the entity's view (spec line 465; route.ts:24-26), a required "what they silently test" field (spec line 241; route.ts:29), and "the guide is a structuring task, no new research" (spec line 372). The last one matters most: it is the basis for Gap 1.

## Corrected

| Original (line) | Correction | Evidence |
|---|---|---|
| "Version 1.0 · ARCS v8.5 Field OS" (2) | The repo is ARCS v9. | CLAUDE.md, AGENTS.md |
| "reference implementation (`ArcsExplorer.tsx` + `stageData.ts`) is the proven pattern" (14) | Neither file is in the repo. Built equivalents are inlined in page.tsx: ExplorerSpine, ArtifactModal, ModeSelector, DecideHeader, CollapsibleBand, PostCallLogModal, DensityToggle, OutcomeTargetCard. | `git ls-files \| grep -iE 'ArcsExplorer\|stageData\|StageBlock\|ReceiptA'` returns nothing; page.tsx:76-620 |
| "The Brief is the **single source of truth** for guide generation" (60) | The guide reads the Receipt and PrepSession. No Brief row is read. Precondition is an owned Receipt. | route.ts:222-233 |
| "destructive on regeneration... preserves the `stageLog`" (61) | No regenerate path exists. POST calls create on a unique receiptId, so a second POST fails with an uncaught unique-constraint error (500). | route.ts:272; schema.prisma:266 |
| "/compass → Alias for /" (72) | /compass is the magic-link sign-in page. The compass UI is /dashboard. | src/app/compass/page.tsx:13-15; CLAUDE.md route table |
| "Generate Prep Guide" CTA in brief header (79) | Not built. Nothing outside the guide links to /guide/. | `grep -rn '/guide/' src` outside the guide dirs returns nothing |
| "Receipt not found" empty state (86) | Not built. A 401 or 404 falls through to the mode selector. | page.tsx:682-692 (non-ok sets loading false only) |
| CompassSeed stakes and horizon in lowercase (103) | PrepSession enums: LOW, MEDIUM, HIGH; TODAY, THIS_WEEK, THIS_QUARTER, ONE_TO_THREE_YEARS. | schema.prisma:61-62 |
| Structured EntityInput with isGroup and members (~120) | entity is one nullable string. Groups use the keyword rule. | schema.prisma:65; route.ts:39 |
| BriefReceipt, GuideReceipt, UserEdits types (~148, ~322) | Real tables: PrepSession, Receipt, Brief, PrepGuide. No userEdits, no persisted activeStageId. | schema.prisma:59, 75, 218, 264 |
| Output is "Valid JSON array matching StageData[]" (~404) | Output is an object with outcome_target and stages[]. | route.ts:52-79 |
| Auto stage-count table, 2 to 5 by decision type (434) | User-chosen mode sets count: 1, 2, or 3 to 5. | route.ts:17-20 |
| Model "must justify the count in an internal chain-of-thought" (446) | No such instruction. Call sends effort medium only. | route.ts:241-247 |
| questionCompass as an open "what is [entity] deciding" question (479) | Built rule is binary, "Is..." or "Can I...". Keep binary; the evaluation belongs in testingAboutThem. | route.ts:27, 29 |
| Artifacts "Minimum 2, maximum 6 per stage" (502) | Counts are per mode; RECON makes exactly 1. Artifacts carry only title and abstract. | route.ts:18-19, 35 |
| density 'full', 'mid', 'compact', saved to UserEdits (650) | 5 levels in localStorage. | page.tsx:20-30, 640-652 |
| Stored as compass/brief/guide documents in one store (689) | Prisma tables; anonymous prep is not stored at all. | schema.prisma; prep/route.ts:33-35 |
| Stage log writes back to the Brief (706) | PATCH writes only PrepGuide.stageLog. | route.ts:317-320 |
| activeStageId saved on every click (715) | React state only, reset to the first stage on load. | page.tsx:633, 678, 813 |
| Label "[inferred from public context]" in inferenceDisclaimer (728) | Built label is "[inferred]", for role archetype only. No inferenceDisclaimer field. | route.ts:40 |
| `window.print()` button (789) | Not built. | `grep -n 'window.print\|@media print' page.tsx` returns nothing |
| Regenerate with confirmation modal (826) | Not built; see line 61 row. | route.ts:272 |
| "Surface 2–3 meaningful options" (853) vs "exactly 3 options" (864) | The spec contradicts itself. Neither is built in the guide. Decision for Zach. | spec lines 853, 864 |
| Utility classes such as `text-[10px]`, Satoshi body font (~597) | Repo bans Tailwind and className. Page uses system-ui with monospace labels. | AGENTS.md gotcha 2; page.tsx:354, 388 |

## Hypotheses, not facts

| Claim | What would verify or kill it |
|---|---|
| The reference pattern is "proven" (14, ~515). | No tests or evals for the guide exist (`git ls-files \| grep -i guide.*test` is empty). Verify with an eval set of real receipts graded by Zach. Until then, unproven. |
| "Generic outputs fail the NOTOMATION rule" (856). | NOTOMATION is about not overruling revealed preference, not a specificity gate. No check measures genericness. Kill the sentence, or add a real specificity check and name it. |
| Every field will reference the specific entity (route.ts:38). | A prompt rule only. Verify by sampling generated guides and counting generic fields. |
| testingAboutThem is always present. | Required by the prompt, not by code. Verify with output schema validation (Gap 2). |
| Claude can draw on public context about a named person "accurately" (725-729). | No retrieval exists. Model recall of a real person can be wrong. Only a fetch with stored citations, or user-supplied context, can verify it. |
| Sonnet 5.5 output quality is fit for this job. | claude-models.ts:23 says "no eval, 0 calls in 30d". Needs an eval before any claim of quality. |
| The fixed overfit/underfit/calibrated fork with A3 always recommended (864) helps users. | A fixed recommendation biases output. Test against user choices before keeping it. |

## Gaps and open questions

1. **Invented provenance about real people (must fix in spec).** Spec line 866 has the model list `publicContextSources` such as "LinkedIn" or "Crunchbase". The guide call has no tools and no retrieval: one `messages.create` with system and user text only (route.ts:241-247). The brief route has no tool use either (`grep -n 'tools\|web_search'` on src/app/api/brief/[receiptId]/route.ts returns nothing). So any such label claims a source the system never read, about a named person. **Fortified rule:** the system must never emit a source label for a source it did not fetch in that request and store with the output. Content from model priors is labelled `[inferred]` and stays at role archetype, never personal facts. If source labels are wanted later, they require a real fetch step that stores URL and fetch time, and the label is written by code, not by the model.
2. **Unguarded model JSON (defect in the build, not a spec change).** route.ts:256-257 strips code fences, then calls `JSON.parse(cleaned)` with no try/catch and no schema check; the result is cast with `as` and written straight to `prisma.prepGuide.create` (272-287). A malformed reply becomes a bare 500. A reply missing `stages` makes `JSON.stringify(undefined)` reach a required column and also fails as a 500. The model-call errors, refusals and truncation are already handled (240-253), so the fix is narrow: wrap the parse, validate with a zod schema matching the "What holds" stage shape, and return a 502 with a retry message. The client also parses `stages` and `stageLog` without a guard (page.tsx:674-676).
3. **Second generation fails.** POST uses create on a unique receiptId (route.ts:272; schema.prisma:266). Needs a 409 guard today, then a decided regenerate (upsert that keeps stageLog) if Zach wants one.
4. **No way in.** Nothing links to /guide/ from the brief or dashboard. Decide: add the brief CTA or accept URL-only access.
5. **No not-found or not-owner state.** Page shows the mode selector on a 401 or 404 (page.tsx:682-692). Generating then fails with no clear message.
6. **Stage log keeps one entry per stage** (route.ts:315), which blocks the Phase 2 vibe history (spec line ~929). Decide if history matters.
7. **Spec omits auth.** The build is owner-only. "Direct-linkable" (spec 86) holds only for the owner; there is no sharing model.
8. **No eval of guide output.** Needed before any quality claim (Hypotheses table).
9. **Decisions only Zach can make:** keep or drop the overfit/underfit/calibrated fork, and fix its count (2 to 3, or exactly 3); whether a guide can be regenerated and what it keeps; whether named-person context should ever use retrieval, given the trust contract at /trust; whether activeStageId and density should persist server-side.

## Kintsugi seam

- **It described a system as built that was not.** The spec called a reference "proven" and drew a Brief-driven pipeline with typed receipts. The repo has none of those files, and the guide reads the Receipt. A builder trusting the spec would wire the wrong inputs.
- **It invited fabricated sources about real people.** It told the model to name source types it never consulted, while also saying the model does no research (372) and never fabricates (729). The two rules cannot both hold without retrieval.
- **It promised safety the code does not have.** "Output validated against StageData before storing" (~392) and clean error states (~881-893) are not built; the live route trusts raw model JSON.
