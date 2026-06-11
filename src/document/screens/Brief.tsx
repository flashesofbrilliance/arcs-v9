'use client'
import React from 'react'
import { T } from '../tokens'
import { Sec } from '../primitives'
import { CoverBlock } from '../patterns/CoverBlock'
import { TwoColumn } from '../patterns/TwoColumn'
import { ScenarioStack } from '../patterns/ScenarioStack'
import { SmartGrid } from '../patterns/SmartGrid'
import { AsideBox } from '../patterns/AsideBox'

export interface BriefProps { data?: Partial<typeof BRIEF_SAMPLE> }

export const BRIEF_SAMPLE = {
  cover: {
    badges: ['Strategic Brief', 'Pre-Event · Figma DS'],
    title: 'Figma DS Analyst — Opportunity Receipt',
    subtitle: 'The altitude layer. Read this before the call prep doc. This is not a job application — this is a stakeholder positioning brief. Walk in at executive altitude. Land at surgical.',
    meta: 'ARCS BRIEF · Jun 2026 · CONFIDENTIAL · PRE-EVENT',
    actions: ['Open Prep Doc', 'View Receipt'],
  },
}

export function Brief({ data }: BriefProps = {}) {
  const A = T.gold
  const d = { ...BRIEF_SAMPLE, ...data }
  return (
    <div>
      <CoverBlock {...d.cover} accent={A} />

      <Sec id="b-context" idx="01" label="Context Frame" title="What the Posting Says vs. What It Signals" accent={A}>
        <TwoColumn accent={A}
          left={{
            heading: 'What the Posting Says',
            items: ['Embedded DS, own the roadmap for a key product area', 'Shape strategy, work closely with PMs and engineering leads', '<b>$140K–$348K range</b> — a 2.5× spread that is negotiating leverage'],
            note: 'The comp range signals the role can be shaped. The 2.5× spread is the most useful data point in the posting.',
          }}
          right={{
            heading: 'What It Actually Signals',
            items: ['This is <b>not a data team hire</b> — it\'s a product org hire who happens to be a data scientist', 'Reporting chain will be product-side; success = <b>product decisions influenced</b>, not models shipped', 'Inbound cold outreach: something specific about your profile triggered the reach — you are not one of many applicants'],
          }}
        />
      </Sec>

      <Sec id="b-scenarios" idx="02" label="Scenario Model" title="Three Paths In" accent={A}>
        <ScenarioStack scenarios={{
          best: { title: 'Founding DS Intelligence Seat', body: 'Figma is building a design-intent intelligence function and this is the founding seat. You define what gets measured across their AI-native surface. 18 months: influencing the AI roadmap, not just reporting on it.', note: 'Life-changing scope. The practitioner-analyst compound is a category advantage.' },
          base: { title: 'Strong Embedded Role', body: 'Real product influence, good comp, interesting technical problem. Developer workflow analytics is genuinely hard. Builder archetype fits. Solid career step either way.' },
          worst: { title: 'Support Backfill', body: '"Own the DS roadmap" is aspirational positioning. Reality: third analyst supporting one PM\'s OKRs. Embedded means surrounded, not empowered.', note: 'Exit in 18 months after building the portfolio piece if this is the scenario.' },
        }} />
      </Sec>

      <Sec id="b-assets" idx="03" label="Strategic Assets" title="What Figma Actually Has" accent={A}>
        <SmartGrid cols={2} items={[
          { label: 'Data Asset 01', color: T.cyan, title: 'The Design Graph', body: 'Millions of community files, design systems, component libraries — the largest labeled corpus of human design intent on the planet. Not prompts. Not code. Design decisions.' },
          { label: 'Data Asset 02', color: T.gold, title: 'The Intent Graph', body: 'Every developer inspection, annotation, and Code Connect mapping is a behavioral signal: design intent → developer interpretation → production code.' },
          { label: 'Data Asset 03', color: T.green, title: 'Plugin Observatory', body: '~1,000+ plugins, millions of sessions. What tools do designers reach for inside Figma that Figma doesn\'t natively provide? That\'s a whitespace map of every unmet need.' },
          { label: 'Data Asset 04', color: T.orange, title: 'FigJam Upstream Signal', body: 'The path from FigJam diagram → Figma frame → Code Connect → production is a complete product development lifecycle, entirely inside Figma\'s ecosystem.' },
        ]} />
      </Sec>

      <Sec id="b-cautions" idx="04" label="Risk Flags" title="What to Watch" accent={A}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <AsideBox variant="warning" label="Panel of 2">Second round will be less warm, harder clock. Verbosity at the Jon screen was recoverable. It will not be at the panel. Lead-with-the-point is non-negotiable.</AsideBox>
          <AsideBox variant="caution" label="Scope Disambiguation">Don&apos;t anchor on base case before you know if best case is on the table. One disambiguating question locates the scenario. Wait for it.</AsideBox>
          <AsideBox variant="info" label="Inbound Signal">Cold outreach means something specific triggered the reach. You are not one of many applicants. This changes the power dynamic — own it.</AsideBox>
        </div>
      </Sec>
    </div>
  )
}
