# PRL Resins Chatbot — PROJECT REGISTRY (single reconciliation index)
_2026-08-04 · the one place that maps every artifact to its home + audience + status._
_SSOT for code/strategy = git. Browsable/shareable mirror = Google Drive (see §6). Cross-session index = memory tracker._

**Audience legend:** 🔒 internal-only (pricing/strategy) · 🤝 Todd-facing/shareable · 📥 source (from PRL) · ⚙ account/tool.

**Channel rule (access control by medium):** 🔒 = may be SHOWN in person / screen-share only (ephemeral,
in-room), **never emailed, hosted, or Drive-shared** (a forwardable copy can escape Todd → SM/owner/team).
🤝 = may get a forwardable copy (email/link/Drive). Todd not flinching at internal material in person does
NOT make it sendable. See memory: "channel is access control."

---

## 1. Strategy + scoping docs (git: `runtime/recoil/generated/`) — mostly 🔒
| Doc | Audience | Status |
|---|---|---|
| `2026-08-04-todd-PROJECT-REGISTRY.md` (this file) | 🔒 | live |
| `2026-08-04-todd-ROADMAP-1.1-to-1.4.md` | 🔒 | canonical roadmap |
| `2026-08-04-todd-1.2-1.5-derisked-plan-gantt-premortem.md` | 🔒 | Gantt + pre-mortem + phased pricing |
| `2026-08-04-todd-recalibration-and-engagement-shape.md` | 🔒 | pricing instruments |
| `2026-08-04-todd-phase-map-1.1-to-1.5.md` | 🔒 | acceptance-criteria detail |
| `2026-08-04-todd-punchlist-people-process-tools.md` | 🔒 (forwardable rows) | change-mgmt punchlist |
| `2026-08-04-todd-discovery-value-reveal.md` | 🤝 (client draft inside) | goodwill note draft |

## 2. Build specs (git: `runtime/recoil/generated/`) — 🔒
| Doc | Purpose |
|---|---|
| `2026-07-30-todd-MASTER-HANDOFF.md` | top-level build pickup |
| `2026-07-20-todd-chatbot-branch-logic-v1.md` | THE conversation design (v1.4) |
| `prl_tidio_flow_gen.py` | generates the importable Tidio flow JSON |
| `2026-07-30-todd-tidio-{build-sheet,voice-script,triggers-and-picker}-v1.md` | Tidio build detail |
| `2026-07-30-todd-personas-routing-persona-v1.md` | personas + territory (titles) |
| `2026-08-03-todd-lyro-ai-layer-v2.md` · `...vision-serialization.md` | Lyro arch · active-listening audit |
| `prl-territory-map.csv` | rep → state (delivered by Todd) |

## 3. Live client-facing pages (`public/`) — 🤝
| URL | File | Status |
|---|---|---|
| https://todd-call.arcs.care (alias prl.arcs.care) | `public/todd-call.html` | live, kept current |
| https://todd-call.arcs.care/teardown (pw todd) | `public/todd-teardown.html` | live |
| /logictree | `public/todd-logictree.html` | route BROKEN (known); use Artifact instead |

## 4. Claude Artifacts
| Artifact | Audience | URL |
|---|---|---|
| Build spec (chatbot logic/flow, no pricing) | 🤝 (SM may see) | claude.ai/code/artifact/e459357f-af02-4c0a-b58d-e9d1b4d7fe13 |
| Project hub | 🔒 | claude.ai/code/artifact/d9492ec7-5378-4437-ae07-634e84fef7b3 |

## 5. Communications + sources
| Item | Where | Note |
|---|---|---|
| Key emails (Aug-4 coffee follow-up; Tidio/Daniel; recaps) | Gmail drafts/sent | 231-opp + $26.5M findings in the Aug-4 note |
| Call transcripts (Jul-20, Jul-31 x2, Jul-2/9) | Granola | verbatim source for scoping |
| 📥 QATF001 Opportunity Form · Material Selection Matrix · Product Selection Guide 2025 | scratchpad/sm-source-docs (+ Todd email) | 1.3 recognition sources |
| Cross-session tracker | `~/.claude/projects/-Users-zharris-arcs-v9/memory/project_todd_hotes_prl_resins.md` | machine-local, all status + psychographic profile |

## 6. Accounts / tools ⚙
Tidio (key `nemtpdglmxzbcpmqlqh1gnj3wmgqsxeu`, Flows+Lyro) · Zapier (Todd's, paid) · SugarCRM (sandbox pending) · ZoomInfo · Mailgun · Unbounce · WP dev (wfaprlredev26) · GTM (Polymer, 9rooftops).
**Ownership goal:** transfer all to PRL for clean handoff.

---

## 6. Google Drive mirror (to set up)
Proposed structure in Zach's **private** Drive (access-gated, not public):
```
PRL Resins — Chatbot/
  00-INDEX (this registry, as a Drive doc)
  01-Client-facing/     (🤝 value-reveal, live-page PDFs, build-spec export)
  02-Strategy-internal/ (🔒 roadmap, pricing, pre-mortem — Zach-only)
  03-Source-from-PRL/   (📥 QATF001, matrices, product guide, territory csv)
  04-Build/             (branch logic, flow gen, Tidio sheets)
```
Git remains SSOT; Drive is the browsable copy + home for non-code assets. Sync is manual/periodic,
not automated (avoid a two-way-sync failure mode). Decision pending from Zach: does 🔒 internal
strategy go in Drive at all, or does Drive hold only 🤝 + 📥 (and internal stays git-only)?
