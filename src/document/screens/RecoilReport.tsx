'use client'
import React from 'react'
import { T } from '../tokens'
import { Sec } from '../primitives'
import { CoverBlock } from '../patterns/CoverBlock'
import { QuoteBlock } from '../patterns/QuoteBlock'
import { Timeline } from '../patterns/Timeline'
import { SidelineList } from '../patterns/SidelineList'
import { ScenarioStack } from '../patterns/ScenarioStack'
import { AsideBox } from '../patterns/AsideBox'
import { ProcessSteps } from '../patterns/ProcessSteps'

export interface RecoilReportProps { data?: Partial<typeof RECOIL_SAMPLE> }

export const RECOIL_SAMPLE = {
  cover: {
    badges: ['Recoil Report', 'First Round · DS Analyst'],
    title: 'Jon Smyrl × Zach Harris — Figma DS Screen',
    subtitle: 'Post-call forensic analysis. Signal was strong; behavioral pattern repeated twice. NCI: 84.2 — recoverable. One fix owns the outcome.',
    meta: 'ARCS RECOIL · Jun 1, 2026 · 47 min call · Figma People Team',
    actions: ['Open Receipt', 'File to Prep Book'],
  },
}

export function RecoilReport({ data }: RecoilReportProps = {}) {
  const A = T.cyan
  const d = { ...RECOIL_SAMPLE, ...data }
  return (
    <div>
      <CoverBlock {...d.cover} accent={A} />

      <Sec id="r-quote" idx="01" label="Signal Quote" title="The Most Load-Bearing Moment" accent={A}>
        <QuoteBlock accent={A} attribution="Jon Smyrl · Jun 1, 2026 — response to stack walk">
          More succinct than I would have been able to communicate it.
        </QuoteBlock>
      </Sec>

      <Sec id="r-walk" idx="02" label="Call Walk" title="Chronological Signal Map" accent={A}>
        <Timeline accent={A} steps={[
          { label: 'Cold Open', title: 'Late Arrival — Rapport Recovery', body: 'Jon arrived 7 min late. Zach matched with the "plan-in-talker-buffer-time" riff. Clean entry — but self-planted the verbosity flag before Jon had a chance to form the concern.' },
          { label: 'Process Recap', title: 'CONSTRUCTIVE INTERFERENCE — Peak Signal', body: '"More succinct than I would have been able to communicate it." Clearest scoring signal on the call. Concision rewarded explicitly and immediately.', peak: true },
          { label: 'Stack Probe', title: 'Builder-Fit Peak', body: 'Stack named: Claude Code, Warp, Supabase RLS, Prisma, Next.js, Jest, Vercel. "Opinion earns a seat at the table" — Jon mirrored "pick the right tool for the problem."' },
          { label: 'Context-Mgmt', title: 'Builder-Credibility Peak — Call Closer', body: 'Stateful global world file, handoff files, decision-receipt logic applied to self-documentation. Jon: "I gotta drop… really enjoyed this." Offset both recoil zones.', peak: true },
        ]} />
      </Sec>

      <Sec id="r-signal" idx="03" label="Signal Assessment" title="Four-Thread Read" accent={A}>
        <SidelineList items={[
          { label: 'Coherence', accent: T.cyan, title: 'Signal is coherent, packaging is not', body: 'Every capability demonstrated on the call traces to the red thread. The problem: external signal (LinkedIn, positioning) doesn\'t convey this. The genome reads internally but doesn\'t project.' },
          { label: 'Recoil Zone 1', accent: T.red, title: 'Verbosity at the Panel of 2', body: 'Self-seeded the concern before the panel identified it. Jon is warmer and more patient than the next round will be. Fix: lead-with-the-point as a mechanical discipline, not a judgment call.', note: 'Two instances observed. Do not make it three.' },
          { label: 'Recoil Zone 2', accent: T.orange, title: 'Over-ran the runway twice', body: 'When the interviewer kept completing the sentence, the runway was already past. That is the behavioral tell — not verbosity per se, but not reading the signal to stop.' },
          { label: 'Recovery', accent: T.green, title: 'Context-management sequence closed cleanly', body: 'The builder-credibility sequence (stateful files, handoff logic, decision receipts) was the strongest signal of the call and directly offset both recoil zones. Jon dropped warmly.' },
        ]} />
      </Sec>

      <Sec id="r-scenarios" idx="04" label="Outcome Model" title="Three Paths Forward" accent={A}>
        <ScenarioStack scenarios={{
          best: { title: 'Founding Seat — DS Intelligence', body: 'Figma is building a design-intent intelligence function. You define what gets measured across their AI-native surface, which becomes the training signal for the next product. 18 months: influencing the roadmap, not just reporting on it.', note: 'Life-changing scope. The practitioner-analyst compound becomes a category advantage.' },
          base: { title: 'Strong Embedded DS Role', body: 'Real product influence, good comp, interesting technical problem. Developer workflow analytics is genuinely hard. Builder archetype fits. Solid career step.' },
          worst: { title: 'Adobe-Era Backfill', body: '"Own the DS roadmap" is aspirational. You\'re the third analyst supporting one PM\'s OKRs. Embedded means surrounded, not empowered.', note: 'Not a trap if you go in clear-eyed — exit in 18 months after building the portfolio piece.' },
        }} />
      </Sec>

      <Sec id="r-flags" idx="05" label="Risk Flags" title="What to Watch" accent={A}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <AsideBox variant="warning" label="Behavioral Pattern">Verbosity showed twice under open prompts. Panel of 2 will be less warm, harder clock. Lead-with-the-point is the #1 fix. Mechanical — not a judgment call.</AsideBox>
          <AsideBox variant="caution" label="External Signal Gap">LinkedIn headline is a list of competencies, not a statement of the genome. The underlying signal is extraordinary but doesn&apos;t project. Packaging underserves the signal.</AsideBox>
          <AsideBox variant="info" label="Godel Status">EXTERNAL_EVIDENCE_REQUIRED — real confirmation signal comes from recruiter feedback or homework invite. Grade the process, not the result.</AsideBox>
          <AsideBox variant="success" label="Validated">NCI 84.2 — strong and recoverable. The single fix (verbosity) is observable, mechanical, and within full control. No genome problem. No fit problem.</AsideBox>
        </div>
      </Sec>

      <Sec id="r-next" idx="06" label="Protocol" title="Recovery Protocol" accent={A}>
        <ProcessSteps accent={A} steps={[
          { label: 'Fix 01', title: 'Mechanical Verbosity Drill', body: 'Before the Panel of 2: answer every question in ≤2 sentences first. Pause. Offer to expand. Do not expand unless asked. Run this as a drill, not an intention.', active: true },
          { label: 'Fix 02', title: 'Lead With The Point', body: 'Open every answer with the conclusion. Put the mechanism and evidence behind it. Never earn the conclusion — state it first, then prove it.' },
          { label: 'Fix 03', title: 'Runway Read', body: 'When the interviewer interrupts or completes your sentence: that is the signal to stop. Not a politeness cue — a behavioral read. Treat it as a hard stop.' },
          { label: 'Confirm', title: 'Wait for the Signal', body: 'Homework invite or recruiter note within 5 business days is the confirmation signal. Absence of contact at 7 days is the Godel trigger — request a status update.' },
        ]} />
      </Sec>
    </div>
  )
}
