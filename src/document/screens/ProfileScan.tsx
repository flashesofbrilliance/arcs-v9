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

export interface ProfileScanProps { data?: Partial<typeof PROFILE_SAMPLE> }

export const PROFILE_SAMPLE = {
  cover: {
    badges: ['Profile Scan', 'Level 3 · Operational'],
    title: 'Genome Intelligence Brief — Andon Profile',
    subtitle: 'Four-thread read of career arc, signal coherence, and cohesion across instantiations. The genome is clear from the inside. The external signal is not yet.',
    meta: 'ARCS PROFILE · Jun 2026 · CONFIDENTIAL · L3 ACCESS',
    actions: ['Export Brief', 'Open Prep Doc'],
  },
}

export function ProfileScan({ data }: ProfileScanProps = {}) {
  const A = T.green
  const d = { ...PROFILE_SAMPLE, ...data }
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

      <Sec id="p-threads" idx="02" label="Genome Threads" title="Four-Thread Assessment" accent={A}>
        <SidelineList items={[
          { label: 'Red Thread · Chain of Custody', accent: T.red, title: 'The Genome Is Coherent. The Signal Is Not.', body: 'Every career move traces back: advances the gold thread, operates in the vermillion tension. No random moves in this career. One coherence gap visible from the outside: 34 months without a publicly visible case study or externalized methodology artifact.' },
          { label: 'Gold Thread · Provenance', accent: T.gold, title: 'Three Instantiations, One Genome', body: 'Nike, La Vida, and Raiden are not three jobs. They are three instantiations of the same genome in three different substrates. Running them concurrently is not distraction — it is the genome operating at full expression.' },
          { label: 'Green Thread · Conviction', accent: T.green, title: 'The Most Load-Bearing Data Point', body: 'UBA5 disorder: estimated global patient population in the hundreds. No commercial upside to founding a rare disease org for a condition this rare. This is the genome\'s most honest expression — the provenance question applied to human life.', note: 'The genome is provable. UBA5 is the proof.' },
          { label: 'Vermillion · Constraint', accent: T.orange, title: 'The Packaging Underserves the Signal', body: 'LinkedIn headline is a list of competencies. Underlying signal is extraordinary. La Vida\'s scaling constraint is the direct expression of the vermillion tension: holding now, next, and wow simultaneously requires presence.' },
        ]} />
      </Sec>

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

      <Sec id="p-capabilities" idx="04" label="Capability Map" title="Four Quadrant Read" accent={A}>
        <SmartGrid cols={2} items={[
          { label: 'Quadrant A · Core', color: T.green, title: 'IP Chain of Custody', body: 'Establishing, protecting, and transferring ownership across substrates — digital, biological, conceptual. 28 years of compounding practice.' },
          { label: 'Quadrant B · Compound', color: T.cyan, title: 'Provenance System Builder', body: 'Turns implicit decision logic into explicit, transferable systems. Every major role produced a methodology artifact that outlasted the engagement.' },
          { label: 'Quadrant C · Signal', color: T.gold, title: 'Rare Disease Foundation Operator', body: 'Founded and operates a gene therapy research org with a global patient population in the hundreds. Zero commercial upside. Signals conviction depth.' },
          { label: 'Quadrant D · Gap', color: T.orange, title: 'External Signal Packaging', body: 'The genome doesn\'t project yet. No public case study, no externalized methodology, no positioning statement that matches the actual signal. Fixable in one artifact.' },
        ]} />
      </Sec>

      <Sec id="p-assertion" idx="05" label="Key Assertion" title="The Provenance Theorem" accent={A}>
        <QuoteBlock accent={A} attribution="ARCS Genome Report — Red Thread Analysis">
          A single question has been answered, in different forms, across every role in the table: How do we establish, protect, and transfer the chain of custody from creation to present?
        </QuoteBlock>
      </Sec>
    </div>
  )
}
