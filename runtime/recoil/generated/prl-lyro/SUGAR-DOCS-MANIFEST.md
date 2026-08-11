# PRL × SugarCRM — Docs Manifest & Version Control

**Docset version: `2026-08-11-postcall.1`** · Canonical branch: `claude/chatbot-1-1-jtbd-blockers-edda33`.

_The single registry of every surface in this engagement and whether it is in sync. Version control lives in
**git**: the repo SSOT files below are canonical and diffable; Drive docs and claude.ai artifacts are
**projections** stamped to a docset version. When a fact changes: (1) update the canonical repo SSOT, (2) bump
the docset version here, (3) re-render the affected projections, (4) flip their status to IN SYNC. A surface
whose version < the header version is **STALE by definition**._

## Version scheme
`YYYY-MM-DD-<phase>.<n>` — date + phase (`precall` / `postcall` / build phase) + increment. Bump `.n` for any
content change; roll the date/phase at a real state change (a call, a decision, a build milestone). Every
rendered surface should carry `docset: <version>` in its header so drift is visible on open.

## Canonical sources (repo — git-versioned, the source of truth)
| # | File | Role | Docset |
|---|---|---|---|
| S1 | `prl-lyro/INTEGRATION-DOSSIER.md` | **Master technical SSOT** (system, contract, gates, registry) | 2026-08-11-postcall.1 |
| S2 | `prl-lyro/sugar-alignment-belieflog.jsonl` | **Change log** — append-only belief history (the version history of *understanding*), 42 spans | running |
| S3 | `2026-08-11-todd-sugar-recoil-close.md` | Event record — the Aug-11 call recoil | 2026-08-11-postcall.1 |
| S4 | `prl-lyro/STATE-OF-SUGAR-2026-08-11.md` | Internal walk-in brief | ✅ reconciled (post-call banner → S1 §0/S3) |
| S5 | `prl-lyro/SUGAR-call-prep-2026-08-11.md` | Pre-call prep (historical; frozen) | precall (archival) |

## Projections — Google Docs (shared folder `PRL Resins — Chatbot`)
| # | Doc | ID | Source | Status |
|---|---|---|---|---|
| G1 | Open Questions + Call Outcomes (**live SSOT intake**) | `1fjGqDLohB7z8pcqyd7KNmkaf0ipoOWPYbmgWo2-_MC8` | S1+S3 | ✅ IN SYNC |
| G2 | Alignment Brief | `1TGFrFmJAMx-gyeIkxZtkxyI7QaZoXH4MOP_nIfP6OnM` | S1 | ✅ IN SYNC |
| G3 | POVs & Approaches | `1Uj0CgUmN5NfRBYrRV77RbcKuzDsBCJWMJK6dE9gLuyM` | S1 | ✅ IN SYNC |
| G4 | Recap & Agenda (completed) | `1EB5Q8Lw3Zdkyf2ljzCDKiPiP6JkkaDVXJX5qbBUeUoc` | S3 | ✅ IN SYNC |
| G5 | PRL Chatbot — Project Knowledge Base | `1XsFIPm5xhsuRDPjJUqcOVUZEnyB14V8zuB__BAqZfAY` | S1 | ⚠ STALE (pre-Aug; "bot never states a spec") |

## Projections — claude.ai artifacts
| # | Artifact | URL id | Audience | Status |
|---|---|---|---|---|
| A1 | Integration Dossier (visual) | `a3ea57a1-72d1-4091-9fdf-dfa85b0de189` | internal | ✅ IN SYNC (call banner) |
| A2 | Alignment (visual) | `0e0280a6-aee9-4948-bfb7-0abd28e97d6a` | client-safe | ✅ IN SYNC (call banner) |

## Superseded — TRASH (owner: Zach; delete-by-ID)
| Doc | ID |
|---|---|
| Alignment Brief (pre-call) | `1M1bESSTZVVb8Qziugonqyna06M5jAeA-PgHgV3RM7Co` |
| POVs & Approaches (pre-call) | `1xxjk00yoHEEHTZCbg9esXDqUP8YGEkTDpLEkiWeH73c` |
| Agenda (pre-call) | `1A29rOpW6zw3JPJ7hZ8rGt5hBbmtimq2b7Q2LrO98vPc` |
| Open Questions (folder, pre-call) | `1vpJQ_AClrDitwY9MuwNa_Ka34H5YrIiRJHmdWj-HfHc` |
| Open Questions v1 (My Drive root) | `1R_5KrszhixFrxUnDabxGa8gAnqMMhuSJiOwvc3YR1sM` |
| Open Questions v2 (My Drive root) | `1LNmDNe_PO_YJwmzL-JsV9E9GZiKk-T7ORUD6i7hT1v0` |

## Open sync gaps (this version)
- **G5 Project KB** — refresh the "never states a spec" line (superseded by governed answering) + confirm Mailgun (now correct). _(only remaining gap)_
- ~~S4 STATE-OF-SUGAR~~ — reconciled (post-call banner).
- ~~A2 client visual~~ — republished with the call outcomes.

## Sync procedure (every change, forever)
1. Edit the **canonical repo SSOT** (S1/S2/S3), never a projection first.
2. Bump the **docset version** in this manifest header; note what changed.
3. Re-render affected **projections** (Drive docs via replace; artifacts via republish-same-URL) and stamp them.
4. Flip each projection's **status → IN SYNC**; trash any superseded copy and record its ID above.
5. Commit S1–S5 + this manifest on `-edda33`. Git history = the version control.
