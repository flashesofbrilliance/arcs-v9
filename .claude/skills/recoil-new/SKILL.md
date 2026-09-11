---
name: recoil-new
description: Scaffold a new counterpart engagement SSOT from the 6-tab war-room template. Use at the very start of a new relationship/deal you'll track over calls. Creates runtime/recoil/generated/<date>-<name>.json ready for /recoil-prep.
---

# /recoil-new — scaffold an engagement SSOT

The closed loop runs on ONE JSON per counterpart (the single source of truth). This skill creates it.

**ADR-068:** this SSOT is the substrate of the ex-ante print — the mandatory blocking gate
before ANY counterpart send (teardown note, forge send, recoil-ship note). If a send is
being prepared and no SSOT exists for the counterpart, run this skill FIRST; the Ex-Ante
tab must be filed before the note leaves DRAFT, or the close-loop has nothing to score.

## Steps
1. Ask (or infer from args) the counterpart's **name**, **company**, and today's **date**.
2. Copy the template:
   ```bash
   cp runtime/recoil/templates/war-room-6tab.template.json \
      runtime/recoil/generated/<YYYY-MM-DD>-<surname>.json
   ```
3. Fill `meta` immediately: `report_id`, `date`, `counterpart`, `company`, and a **non-guessable**
   internal gate password (NOT their first name — they may be given a sibling `*-ext` link).
   Leave the rest as `{{placeholders}}` for /recoil-prep.
4. Report the file path. That path is the `--data` arg every other recoil skill uses.

## Guardrails
- One SSOT per counterpart. If a file for them already exists, extend it, don't create a duplicate.
- Every field/block is tagged `audience: internal` (war-room only) or `both` (safe to share). Default
  new content to `internal`.
- Read the template's `_METHOD` + per-block `_doc` once — they define each tab's discipline.

## Next
Hand off to **/recoil-prep** to gather context and fill the Pre-Call + Ex-Ante tabs.
Relates to [[recoil-brief-ssot-cli]], [[internal-external-artifact-air-gap]].
