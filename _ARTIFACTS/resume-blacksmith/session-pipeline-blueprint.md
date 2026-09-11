# ARCS Pipeline Blueprint — `counterpart-application-forge`
_The composable, parameterized workflow that produced the Blacksmith application artifacts this session. Reusable by construction: swap the args, re-run for the next role or counterpart. This is the full forensic reconstruction (internal); the public Observatory renders only the stages inside the air-gap boundary._

## Args — what you feed it
| arg | this run | type |
|---|---|---|
| `role_posting` | Blacksmith Staff Product Engineer JD | text/URL |
| `counterpart_transcript` | Granola meeting `1831d31e` (Amy Szymarek screen, Sep 2) | transcript |
| `record_of_record` | LinkedIn export (Complete 05-21, Basic 07-11) | data export |
| `candidate_corpus` | `_ARTIFACTS/resume-general` + public repos + status.arcs.care | files/links |
| `org_intel` | DYOR subagent on blacksmith.sh (docs, blog, funding, competitors) | research |
| `decision_makers` | 3 founder LinkedIn profiles (JP / Aayush / Maru) | profiles |
| `target_surface` | `blacksmith.arcs.care` + `/observatory` | subdomain |
| `register` | honest · plain-language · no em-dashes · peer-to-peer engineer | style contract |

## Stages — in → out (with air-gap tag)
| # | stage | in → out | surface |
|---|---|---|---|
| 1 | **GATHER** | args → raw corpus (transcript, research, record) | public |
| 2 | **REVERSE-LISTEN** (recoil) | transcript → counterpart stated-vs-revealed read | **private** |
| 3 | **AUDIENCE-MODEL** (resonance) | decision-maker profiles → per-founder resonance model | **private** |
| 4 | **TRIANGULATE** | stated × revealed-team × revealed-customers → positioning spine (Insights A/B) | **private** |
| 5 | **HONEST-GRADE** (resume-tailor) | claims × record_of_record → graded record + defend-or-drop | public |
| 6 | **RED-TEAM** | draft → subtractive fixes only (true hits change a word) | public |
| 7 | **RENDER** | graded record → resume · cover · ATS · bundle · observatory | public |
| 8 | **GATE** | artifacts → deploy + send, each behind an explicit human yes | human-owned |

## Passthrough params — what flows across stages
- `graded_record` — the SSOT every RENDER reads from. Single source; all surfaces project from it.
- `register` — tone + constraints, applied at RENDER (honest, plain, no em-dashes, peer register).
- `air_gap_boundary` — `{public: [1,5,6,7], private: [2,3,4], human: [8]}`. The Observatory enforces this: private stages are *named* but their contents never surface.
- `evidence_grades` — `documented | self-reported | unverifiable`, attached per claim in stage 5, carried into RENDER so nothing is written past its grade.

## Composability — instance → class
Change `role_posting`, `counterpart_transcript`, `decision_makers`, and `target_surface`, and the same pipeline forges the next application or counterpart artifact family. This is the generalization already latent in the ARCS counterpart-forge / omakase-pipeline patterns: one engagement corpus → a three-surface artifact family (private SSOT, honest-method showcase, target-tuned front door). The pipeline is the reusable asset; each application is one parameterized run.

## Air-gap boundary (why the public showcase is safe)
The Observatory publishes only stages 1, 5, 6, 7: gather, grade, red-team, render. Stages 2–4 (read-the-room, audience-model, triangulate) are the persuasion craft. They are *named* in the pipeline view so the machinery reads as sophisticated, but their contents stay offstage. "I built you a rigorous, honest artifact" earns trust; the room-reading stays a private craft.

```json
{
  "blueprint": "counterpart-application-forge",
  "args": {
    "role_posting": "blacksmith-staff-product-engineer",
    "counterpart_transcript": "granola:1831d31e",
    "record_of_record": ["linkedin-export:complete-05-21", "linkedin-export:basic-07-11"],
    "candidate_corpus": ["_ARTIFACTS/resume-general", "github:flashesofbrilliance", "status.arcs.care"],
    "org_intel": "dyor:blacksmith.sh",
    "decision_makers": ["li:adijp", "li:aayushshah15", "li:maruaditya"],
    "target_surface": "blacksmith.arcs.care",
    "register": "honest|plain|no-emdash|peer-engineer"
  },
  "stages": [
    {"n": 1, "id": "gather", "surface": "public"},
    {"n": 2, "id": "reverse-listen", "surface": "private"},
    {"n": 3, "id": "audience-model", "surface": "private"},
    {"n": 4, "id": "triangulate", "surface": "private"},
    {"n": 5, "id": "honest-grade", "surface": "public"},
    {"n": 6, "id": "red-team", "surface": "public"},
    {"n": 7, "id": "render", "surface": "public"},
    {"n": 8, "id": "gate", "surface": "human"}
  ],
  "passthrough": ["graded_record", "register", "air_gap_boundary", "evidence_grades"],
  "air_gap_boundary": {"public": [1,5,6,7], "private": [2,3,4], "human": [8]}
}
```
