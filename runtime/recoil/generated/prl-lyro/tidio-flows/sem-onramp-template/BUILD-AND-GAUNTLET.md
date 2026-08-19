# SEM Onramp template — build + gauntlet runbook (for the budget-reset session)

Goal: stamp 5 landing-page onramp flows from `template.flow.json` + `instances.json`, all
delivering through the proven shared backbone (Zap 376827315), e2e-tested aggressively.
Gated on Todd's 1.4 go for PUBLISHING; building/importing as inactive drafts is prep, not scope.

## Phase 0 — fill the two unknown schemas (15 min, do first)
1. Export the now-ACTIVATED "AI Handoff (lead delivery bridge)" flow (export unlocks after
   first activation) → copy the real "Send to Zapier" node shape into template nodes[9].
2. Create a throwaway flow with ONLY a "Visitor opens a specific page" trigger, export it,
   copy the trigger node shape into template nodes[0], delete the throwaway.
3. Confirm whether Tidio's importer reads `edges[]` or rebuilds from `connections` (import one
   instance and diff). Fix the template accordingly. Precondition for everything below.

## Phase 1 — stamp + import (per instance)
Swap placeholders (mechanical — small script or careful find/replace), import via My Flows →
Import, DO NOT ACTIVATE yet. Verify in the editor: 6 questions in order, email+phone validation
on, every answer saved to the right variable, Zapier node carries the campaign tag.

## Phase 2 — backbone precondition checks (once, not per instance)
- [ ] Empty-email Filter step is live in Zap 376827315 (Task 1 of the co-pilot queue) — DO NOT
      run gauntlet traffic through a backbone that can corrupt real records.
- [ ] Roger Lamarre record repaired; test-lead cleanup done (clean baseline for assertions).
- [ ] Campaign tag arrives in Sugar (decide target field — description prefix is the zero-
      schema-change option, mirroring the audit-trail pattern).

## Phase 3 — gauntlet (per instance, then cross-cutting)
Per instance (5x):
- [ ] Landing URL loads widget; flow fires on THAT page only (visit a different page → no fire).
- [ ] Full conversation → Sugar lead lands: correct name split, location_c, lead_source,
      campaign tag present, ZoomInfo enrichment attempted.
- [ ] Second run same email → UPDATE not duplicate (dedup), campaign tag of the NEWER run visible.
- [ ] Trigger-collision check: chat icon on the landing page still runs the general AI-Handoff
      flow when opened manually — the two flows must not double-fire (this is the class of bug
      that bit both prior flow generations; test it explicitly, don't assume).
Cross-cutting:
- [ ] Layer 0 suite still green (no dictionary changes expected, run anyway — it's free).
- [ ] Quota check after gauntlet: visitors-reached and Zapier task consumption per full run,
      extrapolate to real PPC volume, write the number down (pricing input for 1.4).
- [ ] UAT harness: extend `../uat/fixtures.json` with one landing-page fixture per instance;
      selectors from the same debug run that greens `staging_chat_e2e.mjs`.

## Phase 4 — evidence + client surface
Screenshot one full run + its Sugar record per instance → `_ARTIFACTS/prl-1-1-evidence/`.
Update `/status/build` (or a new `/status/sem`) with the 5-instance status table. Then STOP —
activation on real Unbounce pages waits for Todd's 1.4 go + final URLs.

## Standing rules
Sandbox Sugar only. Legacy Unbounce→Sugar Zaps (other account, 6801141) stay untouched — this
template RETIRES them at 1.4 activation, one page at a time, not before.
