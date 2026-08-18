# Tidio config state backup / rollback point (before build A)
_2026-08-09 · The pre-build snapshot. To roll back A, restore to exactly this. Live flow exported alongside
(live-flow-lead-capture-2026-08-09.json = the ACTIVE "PRL Resins - Lead Capture" flow, exported from Tidio)._

## Plan
Base tier + Flows (2,000 visitors/mo) + Lyro AI Agent (50 conversations/mo), both paid. NOT Plus.

## Flows (8 total)
- ACTIVE: "PRL Resins - Lead Capture" (21 executed, 38% eng). Settings: Active ON; "Works even when agents are
  offline" ON; "Works when an agent is handling the conversation" OFF; "Works even when another Flow is running"
  OFF. Trigger = onFirstVisit. Exported -> live-flow-lead-capture-2026-08-09.json.
- DRAFTS (7, all inactive): AI Handoff (lead delivery bridge); SEM Onramp x5 (SABIC alternatives, Lexan/Makrolon
  PC, Ultem PEI, Noryl modified PPE, Valox PBT); Lead Capture (AI-forward).

## Lyro data sources (13 total) - ALL currently ON for Lyro AND Copilot, audience = "Everyone"
Spec-bearing (these get set Copilot-only in A step 1; to roll back, re-enable Lyro on all 5):
1. PRL-Competitor-Cross-Reference (PDF)
2. PRL-Product-Catalog-2025 (PDF; exploded into 150 "specifications" Q&A pairs)
3. PRL-Material-Selection (PDF)
4. Engineering_Thermoplastics (PDF)
5. Polymer-Resources-Pro... (PDF)
Public website (stay ON for Lyro): prlresins.com/contact, /our-team, /products (x2), /about, prlresins.com/ (+others)

## Audiences
Only "Everyone" exists. A creates "Molder" and "OEM". To roll back: delete those audiences.

## Lyro Guidance / Behavior
CAPTURE THE CURRENT GUIDANCE TEXT IN-APP BEFORE OVERWRITING in A step 2 (was ~"friendly tone" per earlier
finding; exact text not yet snapshotted - do it at build time and paste here for true rollback).

## Widget
Branded: background #7a1f2b (maroon), action #c9a227 (gold), text white. Greeting: "Welcome to PRL Resins /
Looking for a resin or a spec? We'll get you to the right specialist fast."

## Rollback procedure
1. Re-enable Lyro on the 5 spec PDFs. 2. Restore Guidance from the captured text. 3. Delete Molder/OEM
audiences. 4. Deactivate/delete any new flows; the original active flow is untouched (and backed up here).
