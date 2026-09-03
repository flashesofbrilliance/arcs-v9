---
name: recoil-ship
description: T-plus phase. Project the internal war-room SSOT into a counterpart-safe external artifact, safety-scan it, deploy it, and draft the accompanying note (never sent automatically). Use when you're ready to share something with the counterpart.
---

# /recoil-ship — externalize, safety-scan, deploy, draft

Turns the internal war-room into a safe, shareable artifact via mechanical audience projection.

## Step 1 — decide what crosses the air gap
The three rules ([[internal-external-artifact-air-gap]]), non-negotiable:
1. **Show your own updates, not their intent-scores.** External belief lines are YOUR self-corrections,
   never your scoring of them.
2. **Method can cross; subject-about-them cannot.** A pre-mortem of the deal, objection-handling of
   their asks, or reads of their motives NEVER cross, redacted or not.
3. **Architecture crosses; weights don't.** Show the shape (Bayesian tracking, temporal join,
   self-adversarial pass); withhold schema DDL, exact operators, tunable params.

In the SSOT, tag shareable content `audience: "both"`; everything else stays `internal`. Add a
forward-looking `pilot` block (the concrete safe offer) and a `provenance` block (verbatim grounding).

## Step 2 — generate the external twin
```bash
./scripts/recoil --data runtime/recoil/generated/<id>.json --audience external --format html \
    > public/<name>-ext.html
```
The generator drops every `internal`-tagged field/row and hides empty tabs — the redaction is a code
path, not a manual pass.

## Step 3 — SAFETY SCAN (mandatory gate)
```bash
grep -ciE "candidacy|already hired|intent|red.?team|Loki|manifold|schema|posterior|<their private facts>" public/<name>-ext.html   # want 0
grep -c "—" public/<name>-ext.html   # want 0 (no em-dashes — plain-language rule)
```
Also scan the **rendered source** (view-source) for internal terms in comments — a technical
counterpart will read HTML. If anything real leaks, fix the SSOT tags and regenerate. Do NOT ship on a
non-zero scan.

## Step 4 — fact-check
Verify every quote against the source transcript ([[fact-check-final-pass-vs-transcript]]). No
compressed quotes, no overclaimed consent.

## Step 5 — deploy
Wire `<name>-ext.arcs.care` (next.config.ts + `vercel domains add`), gate as appropriate (often their
first name), commit on main, push, verify live + re-run the leak scan on the live URL.

## Step 5b — pre-send gates (BLOCKING; ADR-068 recapitulate cut)

1. **Ex-ante receipt current?** The SSOT's Ex-Ante tab must contain a filed, current
   expectation for THIS send (expected response, falsifier). If the last ex-ante was for a
   prior call/move, file a fresh entry. No receipt, no send.
2. **Pre-send gauntlet.** Run the `counterpart-gauntlet` workflow on the -ext artifact +
   note draft. Fate: send-worthy / parked. Verify each surviving flag against source
   yourself before healing.
3. **Log the close-loop obligation**: `/recoil-close` (expected vs actual) is owed when
   they respond.

## Step 6 — draft the note (do NOT send)
Draft in the counterpart's register, plain language, **no em-dashes**, mirroring their own words. Create
it as a **Gmail draft** (`create_draft`) or hand back the text — never send on the user's behalf. Point
it at the `-ext` link; tie it to the provenance ("every read traces to a line you actually said").

## Guardrails
- Sending is the user's action, always. Deploying ≠ sending.
- The safety scan is a hard gate. A page that leaks a read-about-them can damage the relationship.

## Render gate (ADR-075; blocking)
Before deploy, every external page runs `python3 scripts/cold_reader_gate.py <page.html>` alongside
`leak_check.sh`. A FAIL blocks the ship. Fix the page's order and disclosure, not the gate; if the gate
disagrees with a counterpart's stated verdict, amend the gate via ADR-075's calibration set.
