---
description: Implement the CBS Anti-Slop Engine, Zero-Telemetry Public Tool, and API Shadow in arcs-v9
---

# /cbs-anti-slop: Production CBS Engine & Public Good Implementation

Execute the following sequential build in `flashesofbrilliance/arcs-v9`:
Standing Rules: Zero new dependencies. Single App Router root (src/lib/, src/app/, src/proxy.ts).

## 1. Core CBS Metric Engine
Create `src/lib/cbs.ts`:
- PATHOGEN_DICTIONARY: 20 banned filler adverbs (crucially, delve, nuanced approach, synergy, etc.)
- COUPLET_REGEX: /(?:not\s+(?:only\s+)?[\w\s,]+(?:but|it\s+is)\s+[\w\s]+)/gi
- PHYSICAL_ANCHOR_PATTERNS: Software nouns (slack, cli, grep, ram, api), timestamps, cost/token numbers.
- `runCBSAnalysis(text: string): CBSMetrics` returning:
  - wordCount, uniqueWordCount, vocabDensity (floor: 0.540)
  - sentenceLengths, sentenceVariance (ΔL >= 35), sentenceStdDev
  - slopMatches, coupletMatches, physicalNounsCount
  - passed (boolean), score (0-100)

## 2. Zero-Telemetry Public Good Page
Create `src/app/tools/anti-slop/page.tsx`:
- "use client" React component running `runCBSAnalysis` entirely in browser RAM.
- Real-time score badges: Vocab Density, Burstiness ΔL, Pathogens, Couplets.
- ARCS Zero-Telemetry Guarantee Badge: 0 bytes outbound, auditable via DevTools Network tab.
- Enterprise API link for automated CI/CD.

## 3. Subdomain Route
Verify `src/proxy.ts` routes `good.arcs.care/tools/anti-slop` or `/tools/anti-slop` directly to the page.

## 4. Enterprise API Route
Create `src/app/api/v1/scan/route.ts`:
- POST handler checking `x-arcs-api-key`.
- Runs `runCBSAnalysis(text)` and returns JSON `{ status: 'success', data: metrics, receipt: { hash, timestamp } }`.
- If missing/invalid key, returns 401 with pricing/waitlist link.

## 5. Verification
Run `npm run build` or `npm run type-check`. Confirm 0 errors.
