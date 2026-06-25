'use client'
import React from 'react'
import { T } from '../tokens'
import { Sec } from '../primitives'
import { CoverBlock } from '../patterns/CoverBlock'
import { TwoColumn } from '../patterns/TwoColumn'
import { SidelineList } from '../patterns/SidelineList'
import { DataTable } from '../patterns/DataTable'
import { SmartGrid } from '../patterns/SmartGrid'
import { QuoteBlock } from '../patterns/QuoteBlock'

export type ScanDepth = 'simple' | 'rich' | 'deep'

export interface ProfileScanProps {
  data?: Partial<typeof PROFILE_SAMPLE>
  // Truncation, not branching — one document, SIMPLE shows least, DEEP shows all six
  // sections. See ADR-028 / Profile Scan Spec v1 "Depth model, finalized."
  depth?: ScanDepth
}

export const PROFILE_SAMPLE = {
  cover: {
    badges: ['Profile Scan', 'Level 3 · Operational'],
    title: 'Genome Intelligence Brief — Andon Profile',
    subtitle: 'Four-thread read of career arc, signal coherence, and cohesion across instantiations. The genome is clear from the inside. The external signal is not yet.',
    meta: 'ARCS PROFILE · Jun 2026 · CONFIDENTIAL · L3 ACCESS',
    actions: ['Export Brief', 'Open Prep Doc'],
  },
}

export const ZACH_PROFILE = {
  cover: {
    badges: ['Profile Scan', 'DEEP · LinkedIn export + Creator Analytics'],
    title: 'Profile Scan — Zach Harris',
    subtitle: 'Reach and quiet resonance are separable axes. Thesis-consistency, not impression volume, predicts which content lands quietly and specifically with a technical audience.',
    meta: 'ARCS PROFILE · Jun 2026 · 4 LinkedIn data surfaces, per-post attribution',
    actions: ['Export Brief', 'Open Prep Doc'],
  },
}

export function ProfileScan({ data, depth = 'deep' }: ProfileScanProps = {}) {
  const A = T.green
  const d = { ...PROFILE_SAMPLE, ...data }
  const showRich = depth === 'rich' || depth === 'deep'
  const showDeep = depth === 'deep'
  return (
    <div>
      <CoverBlock {...d.cover} accent={A} />

      <Sec id="p-contrast" idx="01" label="Signal Read" title="Stated vs. Observed" accent={A}>
        <TwoColumn accent={A}
          left={{
            heading: 'What the Profile Says',
            items: ['Innovation counsel — IP, tech transfer, startup formation', 'Three concurrent instantiations: Nike IP, La Vida, Raiden Foundation', '34 months since last externalized methodology artifact'],
            note: 'The packaging is a competency list. The genome is a provenance system.',
          }}
          right={{
            heading: 'What the Signal Actually Is',
            items: ['A single question answered in every role: <b>How do we establish, protect, and transfer the chain of custody from creation to present?</b>', 'Not three jobs — three instantiations of one genome in three substrates', 'UBA5: estimated global patient population in the hundreds. No commercial upside. Most honest genome expression.'],
          }}
        />
      </Sec>

      {showRich && (
      <Sec id="p-threads" idx="02" label="Genome Threads" title="Four-Thread Assessment" accent={A}>
        <SidelineList items={[
          { label: 'Red Thread · Chain of Custody', accent: T.red, title: 'The Genome Is Coherent. The Signal Is Not.', body: 'Every career move traces back: advances the gold thread, operates in the vermillion tension. No random moves in this career. One coherence gap visible from the outside: 34 months without a publicly visible case study or externalized methodology artifact.' },
          { label: 'Gold Thread · Provenance', accent: T.gold, title: 'Three Instantiations, One Genome', body: 'Nike, La Vida, and Raiden are not three jobs. They are three instantiations of the same genome in three different substrates. Running them concurrently is not distraction — it is the genome operating at full expression.' },
          { label: 'Green Thread · Conviction', accent: T.green, title: 'The Most Load-Bearing Data Point', body: 'UBA5 disorder: estimated global patient population in the hundreds. No commercial upside to founding a rare disease org for a condition this rare. This is the genome\'s most honest expression — the provenance question applied to human life.', note: 'The genome is provable. UBA5 is the proof.' },
          { label: 'Vermillion · Constraint', accent: T.orange, title: 'The Packaging Underserves the Signal', body: 'LinkedIn headline is a list of competencies. Underlying signal is extraordinary. La Vida\'s scaling constraint is the direct expression of the vermillion tension: holding now, next, and wow simultaneously requires presence.' },
        ]} />
      </Sec>
      )}

      {showRich && (
      <Sec id="p-arc" idx="03" label="Career Arc" title="Evidence Ledger" accent={A}>
        <DataTable
          columns={['Period', 'Role', 'Domain', 'Genome Expression']}
          rows={[
            ['1997–2007', 'Innovation × Patents', 'IP Law Firms — Klarquist, Kolisch', 'Chain of custody: creation → protection'],
            ['2007–2013', 'Technology Transfer Officer', 'OHSU — startup creation, licensing', 'Chain of custody: lab → market'],
            ['2013–2022', 'Sr. Director, Digital Patents', 'Nike — CryptoKicks (filed 2019)', 'Chain of custody: physical → digital goods'],
            ['2021–present', 'Executive Director', 'Raiden Science Foundation — UBA5', 'Chain of custody: research → patient'],
            ['2023–present', 'Founder', 'La Vida Innovation — strategy, IP counsel', 'Chain of custody: insight → decision'],
          ]}
        />
      </Sec>
      )}

      {showDeep && (
      <Sec id="p-capabilities" idx="04" label="Capability Map" title="Four Quadrant Read" accent={A}>
        <SmartGrid cols={2} items={[
          { label: 'Quadrant A · Core', color: T.green, title: 'IP Chain of Custody', body: 'Establishing, protecting, and transferring ownership across substrates — digital, biological, conceptual. 28 years of compounding practice.' },
          { label: 'Quadrant B · Compound', color: T.cyan, title: 'Provenance System Builder', body: 'Turns implicit decision logic into explicit, transferable systems. Every major role produced a methodology artifact that outlasted the engagement.' },
          { label: 'Quadrant C · Signal', color: T.gold, title: 'Rare Disease Foundation Operator', body: 'Founded and operates a gene therapy research org with a global patient population in the hundreds. Zero commercial upside. Signals conviction depth.' },
          { label: 'Quadrant D · Gap', color: T.orange, title: 'External Signal Packaging', body: 'The genome doesn\'t project yet. No public case study, no externalized methodology, no positioning statement that matches the actual signal. Fixable in one artifact.' },
        ]} />
      </Sec>
      )}

      <Sec id="p-assertion" idx="05" label="Key Assertion" title="The Provenance Theorem" accent={A}>
        <QuoteBlock accent={A} attribution="ARCS Genome Report — Red Thread Analysis">
          A single question has been answered, in different forms, across every role in the table: How do we establish, protect, and transfer the chain of custody from creation to present?
        </QuoteBlock>
      </Sec>
    </div>
  )
}

export function ProfileScanZach({ depth = 'deep' }: { depth?: ScanDepth } = {}) {
  const A = T.green
  const showRich = depth === 'rich' || depth === 'deep'
  const showDeep = depth === 'deep'
  return (
    <div>
      <CoverBlock {...ZACH_PROFILE.cover} accent={A} />

      <Sec id="z-contrast" idx="01" label="Signal Read" title="Reach vs. Resonance" accent={A}>
        <TwoColumn accent={A}
          left={{
            heading: 'What the Reach Numbers Say',
            items: ['Jan 29, 2026 "Forgetting Machine" article — 74,851 impressions, the #1 post of the year', 'Jun 3, 2026 off-thesis post — 41,710 impressions, the 4th-highest reach of any post measured', 'Both look like strong performers by impression count alone'],
            note: 'Impressions are the metric every export surfaces first. They are also the least informative one here.',
          }}
          right={{
            heading: 'What the Per-Post Data Actually Shows',
            items: ['Jun 3 (off-thesis) save-rate: <b>0.0048%</b>, send-rate: 0.0000% — the weakest quiet-resonance reading of the six posts measured', 'Jun 4, 2026 — a direct callback to the Jan 29 thesis — save-rate <b>0.046%</b>, ~2x the next-highest, despite lower reach than Jun 3', 'Thesis-consistency predicts save/send density independent of impression volume (n=6, one account — directional, not law)'],
          }}
        />
      </Sec>

      {showRich && (
      <Sec id="z-threads" idx="02" label="Resonance Threads" title="Four-Thread Assessment" accent={A}>
        <SidelineList items={[
          { label: 'Red Thread · Recurring Risk', accent: T.red, title: 'High Reach Does Not Predict Quiet Resonance', body: 'Jun 3 had the 4th-highest impressions of the six posts measured but the lowest save-rate and a zero send-rate. Optimizing for impressions alone would have called this post a win.' },
          { label: 'Gold Thread · Working Asset', accent: T.gold, title: 'Trend Surfing, Used in Production', body: 'The Jan 29 → Jun 4 callback chain was deliberately timed using the existing Trend Surfing molecule (velocity/acceleration entry-exit detection) against a tracked attention-value signal — not posted on intuition. A jerk-based pre_peak_warning() extension, validated against this real engagement series, now buys ~1 day of lead time over the prior acceleration-only signal.' },
          { label: 'Green Thread · Conviction', accent: T.green, title: 'The Jan 29 → Jun 4 Callback', body: 'Jun 4\'s direct callback to the Jan 29 thesis produced 71,906 impressions, 19 followers gained, 33 saves, 7 sends — and a measured 9% Apple-employee audience composition on that specific post, an order of magnitude above the 1% account-wide baseline. Concentrated, attributable, on-thesis.', note: 'Per-post demographics, not inference — this is the most evidenced finding in the whole scan.' },
          { label: 'Vermillion · Constraint', accent: T.orange, title: 'Four Manual, Creator-Mode-Gated Exports', body: 'Every finding above required four separate manual LinkedIn exports (personal data ZIP, 365-day Content Analytics, live 90-day Saves/Sends, per-post analytics) — none API-automatable, two gated behind Creator Mode. This doesn\'t scale past a one-person manual walkthrough yet.' },
        ]} />
      </Sec>
      )}

      {showRich && (
      <Sec id="z-arc" idx="03" label="Post Chain" title="Evidence Ledger — Top 6 Posts" accent={A}>
        <DataTable
          columns={['Date', 'Topic', 'Impressions', 'Saves', 'Save-Rate']}
          rows={[
            ['Jan 29', '"Forgetting Machine" — original thesis', '74,851', '17', '0.023%'],
            ['Feb 24–26', 'Anticipatory cluster — Apple 50th lead-in', '~27,000 ea.', '5–6', '0.018%'],
            ['May 25', 'Gap-breaker — "wrong instrument"', '51,059', '9', '0.018%'],
            ['Jun 3', 'Off-thesis post', '41,710', '2', '0.0048%'],
            ['Jun 4', 'Direct callback to Jan 29 thesis', '71,906', '33', '0.046%'],
          ]}
        />
      </Sec>
      )}

      {showDeep && (
      <Sec id="z-capabilities" idx="04" label="Capability Map" title="Four Quadrant Read" accent={A}>
        <SmartGrid cols={2} items={[
          { label: 'Quadrant A · Core', color: T.green, title: 'Thesis-Consistent Long-Form Authorship', body: '38 authored articles in the LinkedIn export, full first-person long-form corpus — the primary input for a future Rhetorical Resonance Engine, not just short post copy.' },
          { label: 'Quadrant B · Compound', color: T.cyan, title: 'Trend Surfing Applied to Real Timing', body: 'A generic velocity/acceleration/jerk detector (operators/linkedin_pipeline/primitives.py), validated against real Creator Analytics data at two real peaks — not a theoretical primitive, a production one.' },
          { label: 'Quadrant C · Signal', color: T.gold, title: 'Per-Post Attributable Demographics', body: 'Per-post analytics close the loop a personal-data-export or 365-day aggregate alone cannot: attributable followers-gained, saves/sends, and audience composition per individual post.' },
          { label: 'Quadrant D · Gap', color: T.orange, title: 'Manual, Creator-Mode-Gated Acquisition', body: 'All four data surfaces require manual UI export; two require Creator Mode. No automatable pipeline exists yet — the acquisition step, not the analysis, is the current bottleneck.' },
        ]} />
      </Sec>
      )}

      <Sec id="z-assertion" idx="05" label="Key Assertion" title="The Resonance Theorem" accent={A}>
        <QuoteBlock accent={A} attribution="ARCS Profile Scan — Zach Harris, Thread Analysis">
          Reach and quiet resonance are separable axes. The post with the highest save-rate in this corpus was not the post with the most impressions — it was the post most consistent with an already-established thesis.
        </QuoteBlock>
      </Sec>
    </div>
  )
}
