# Public-Repo Exposure Audit

**Date:** 2026-07-19 · **Tributary:** J2 (ATG, ratified 2026-07-19)
**Finding:** MEDIUM–HIGH exposure. **Remediation is a human decision** — this doc
only surfaces what's exposed and the options.

## The core fact

`github.com/flashesofbrilliance/arcs-v9` is **public** (confirmed in Vercel deploy
metadata: `githubRepoVisibility: "public"`). Everything in the tree — not just the
routed pages — is therefore world-readable and search-indexable at the source level,
including commit history.

## What's exposed

### 1. Named-individual dossiers (~18 files in `public/`)
Recoil reports / pre-call briefs on real, named people:
`chan, daniel, danny, jalaja, jeben, julia (+julia-ext), peter, kelly-interview,
kiko, labella, lewoof, thetrueai, todd-call, ayesha (+ayesha-ext),
vishal-kapadia-forensic-report, vishal-kapadia-awe-forensic`.

- Several are served **ungated** on subdomains **by design** (chan, status, todd,
  etc.) — that's intentional external sharing of *that page*.
- **The new exposure is the source repo**: even the *password-gated* subdomains
  (jeben, danny, kiko, jalaja, lewoof…) have their full HTML — gate included, so the
  gate is trivially bypassed — sitting in a public repo. And `ayesha.html` is
  committed-but-deliberately-unrouted ("internal Recoil Report… NOT routed to any
  domain") yet is still fully public via the repo.
- `vishal-kapadia-forensic-report` / `-awe-forensic` read as especially sensitive by
  name (a forensic report on a named person, public).

### 2. IP / strategy
- `_CANON/ARCS-YellowPaper.md`, `arcs-v9-additional/ARCS-WhitePaper-v2-1.md` (+ v1-2)
  — the patent-candidate disclosures. Already flagged (state-of-union §patent): their
  public-repo presence is the live §102 public-accessibility question for counsel.
- `_PATTERNS/` (this map, patent triage), `_DECISIONS/` ADRs — internal strategy.

## Risk

- **Privacy / reputational:** named-person dossiers (esp. "forensic") publicly
  attributable to their subjects and to the author.
- **Legal (IP):** public repo may start/extend the §102 disclosure clock on the papers.
- **Competitive:** full strategy, ADRs, and roadmap browsable.
- Password gates on subdomains give **false assurance** — the gated HTML is in the
  clear in the repo.

## Options (human decision — do not action silently)

| Option | Effort | Trade-off |
|--------|--------|-----------|
| **A. Make the repo private** | 1 click | Biggest single lever; kills the whole class. Breaks the public "every claim links to a public repo" thesis on status/chan (those pages cite `github.com/…(public)`) — copy would need adjusting. Recommended default. |
| **B. Split: sensitive → private repo/submodule** | med | Keep a public repo for the app; move `public/<person>.html`, `_CANON` papers, `_PATTERNS`, `_DECISIONS` to private. Preserves the public-provenance story for non-sensitive code. |
| **C. Scrub in place** | high | Remove/redact dossiers + papers from history (git filter). History rewrite; coordinate with the concurrent sessions (J5). Weakest — easy to miss something. |

## Recommendation

**A or B, this week**, and treat password-gated pages as *not* confidential while the
repo is public. Whichever is chosen, rotate anything that leaked and re-verify the
papers' first-public-appearance date with counsel (ties to the §102 item). The forensic
dossiers are the sharpest edge — prioritize those regardless of the broader choice.
