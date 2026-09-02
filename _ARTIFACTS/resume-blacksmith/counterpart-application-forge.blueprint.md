# Blueprint — `counterpart-application-forge` (v1.0)

> The componentized, parameterized workflow that produced the Blacksmith application
> bundle this session. **Reusable by construction:** fill the params, run the stages,
> and it stands up a `<company>.arcs.care` bundle for the next role or counterpart.
> This is the full forensic reconstruction (internal). The public **Forge** surface
> renders only the stages inside the air-gap boundary.
>
> Names are parameters, never hardcoded — so this spec is safe to reuse and share.

---

## 1. Params — the complete input contract

```json
{
  "company":            "<Company>",                         // display name
  "role_posting":       "<JD text or URL>",
  "target_surface":     "<company>.arcs.care",               // subdomain to stand up
  "counterpart": {
    "name":             "<recruiter or referrer>",           // credited publicly IF attested
    "firm":             "<firm>",
    "transcript":       "<Granola/Fathom id or transcript>", // the intro call
    "credit_public":    true                                  // deliberate attribution on/off
  },
  "record_of_record":   "<LinkedIn export / canonical CV data>",
  "candidate_corpus":   ["_ARTIFACTS/resume-general", "public repos", "status.arcs.care"],
  "org_intel":          "<DYOR research bundle: docs, blog, funding, customers, security>",
  "decision_makers":    ["<profile 1>", "<profile 2>", "<profile 3>"],   // founders/panel
  "register":           "honest · plain-language · no em-dashes · peer-to-peer",
  "air_gap": {
    "public_credit":    ["<counterpart.name>", "<counterpart.firm>"],    // intended, attested
    "hard_forbidden":   ["<decision_maker surnames>", "reverse-listen", "resonance model",
                         "<counterpart surname>", "<sourcing platform>"] // never on public HTML
  }
}
```

Everything downstream is a pure function of this block. Swap it, re-run, get the next bundle.

---

## 2. Stages — component · in → out · surface

| # | stage | component (skill/agent/tool) | in → out | surface |
|---|-------|------------------------------|----------|---------|
| 1 | **GATHER** | `recoil-gather-git` + `recoil-gather-web` (least-priv agents) | params → raw corpus | public |
| 2 | **REVERSE-LISTEN** | `recoil-reason` (recoil report) | transcript → stated-vs-revealed read | **private** |
| 3 | **AUDIENCE-MODEL** | `recoil-reason` (per-persona resonance) | decision-makers → resonance model | **private** |
| 4 | **TRIANGULATE** | `recoil-reason` (synthesis) | stated × team × customers → positioning spine | **private** |
| 5 | **HONEST-GRADE** | `resume-tailor` skill | claims × record_of_record → graded record + defend-or-drop | public |
| 6 | **PERSONA-GAUNTLET** | subagent panel (one per decision-maker) | draft → steelmanned objections + ATG replies | **private** |
| 7 | **RED-TEAM** | `claims-skeptic` (constitutional court) | draft → subtractive fixes only | public |
| 8 | **RENDER** | inline-style HTML build | graded record → landing · résumé (PDF/ATS/viewer) · cover · Forge | public |
| 9 | **KINTSUGI** | `operators/arcs_kintsugi.py` | final receipt → healthy/heal + golden-seam ledger | public |
| 10 | **GATE + SEND** | CI + human | artifacts → deploy + send, each behind an explicit human yes | human-owned |

---

## 3. Advancement gates — the eval between each stage (ADR-068 print schedule)

Every stage prints an artifact, **through a gate, to a fate**. These are the gates now
rendered on the public Forge (stages 5→10 map to the six on-page gates):

| gate | condition to advance |
|------|----------------------|
| GATHER → GRADE | Titles, dates, credentials reconciled line-by-line vs `record_of_record`. Nothing advances that could fail a background check. |
| GRADE → STRESS-TEST | Every claim carries an evidence grade (documented / self-reported / unverifiable). No ungraded claim reaches the page. |
| STRESS-TEST → ORDER | Every claim that fails the evidence bar is removed to defend-or-drop. |
| ORDER → BUILD | The lead is the single most checkable AND most differentiated claim, mapped to the role. |
| BUILD → RED-TEAM | Rendered pixels verified in CI: Playwright, zero horizontal overflow at four widths; PDF reachable. Page-count is not a pass. |
| RED-TEAM → SHIP | CI green or no merge: lint + `next build`, the **air-gap leak-check run as a test**, security scan; bad deploy auto-rolls-back. |

---

## 4. Air-gap boundary — why the public showcase is safe

`air_gap_boundary = { public: [1,5,7,8,9], private: [2,3,4,6], human: [10] }`

- Private stages (reverse-listen, audience-model, triangulate, persona-gauntlet) are the
  persuasion craft. They are **named** in the Forge so the machinery reads as rigorous, but
  their **contents never surface.** The Forge's own line: *"Nothing about you. Reading the
  room is a private craft, not a thing to publish."*
- The boundary is **enforced mechanically**, not by promise: a Playwright test
  (`tests/<surface>.spec.ts`) fails the build if any `air_gap.hard_forbidden` token appears
  in the served HTML. `air_gap.public_credit` is the deliberate exception (attested by the
  candidate).
- **Never** publish the org-intel / DYOR recon on the target's own hiring surface: it reads
  as surveillance. Its *public* facts (funding, customers, security posture) may inform the
  copy; its *method* stays offstage.

---

## 5. Output manifest — the three-surface family

| surface | reader | file(s) |
|---------|--------|---------|
| **Front door** `<company>.arcs.care` | recruiter + panel | landing (hero ship-clock, domain-map, kitchen, Forge CTA) |
| **Honest-method showcase** `/forge` | panel (technical) | replay with per-stage gates, evidence grades, cut list, CI gates |
| **Deliverables** `/resume` | ATS + human | résumé PDF · ATS text · cover PDF, via a sticky-eyebrow viewer |
| **Private SSOT** (never served) | candidate only | recoil report · persona-gauntlet · triangulation · kintsugi receipt |

---

## 6. Run recipe

1. Fill §1 params. Register the `<company>.arcs.care` subdomain + `next.config.ts` host rewrite.
2. Stages 1–4 (gather → triangulate): least-priv gather agents, then `recoil-reason`. **Private.**
3. Stage 5 `resume-tailor`; stage 6 persona-gauntlet (one subagent per decision-maker). 
4. Stage 7 `claims-skeptic` red-team (subtractive only). 
5. Stage 8 RENDER: inline-style HTML, self-hosted fonts, favicon = the company's real mark.
6. Add `tests/<surface>.spec.ts` (smoke + air-gap FORBIDDEN + four-width responsive) and a
   `<surface>-verify.yml` workflow. 
7. Stage 9 kintsugi: run `arcs_kintsugi.py` on the final receipt; attach the golden-seam ledger.
8. Stage 10: deploy behind the render smoke-gate; draft the send note; **human sends.**

---

## 7. Composability — instance → class → factory

One engagement corpus → a three-surface artifact family (private SSOT · honest-method
showcase · target-tuned front door). The **pipeline is the reusable asset**; each application
is one parameterized run. This is the counterpart-forge / omakase-pipeline pattern generalized:
change `company`, `role_posting`, `counterpart`, `decision_makers`, `target_surface`, and the
same forge produces the next bundle — with the air-gap, the gates, and the kintsugi validation
carried for free.

_Provenance: first instance = Blacksmith Staff Product Engineer, 2026-09-02. Kintsugi receipt:
`_STATE/2026-09-02-blacksmith-kintsugi.json`. Prior draft: `session-pipeline-blueprint.md`._
