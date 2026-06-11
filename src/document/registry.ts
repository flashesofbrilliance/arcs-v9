'use client'
// ARCS Document UIKit — registries.
// DOC_TYPES: the 5 document format ids (recoil, profile, brief, prep, receipt).
// DOC_PATTERNS: the 10 reader-view patterns with Demo render + code string.
// Faithful port of patterns.jsx's DOC_TYPES + DOC_PATTERNS.

import React from 'react'
import { T } from './tokens'
import { CoverBlock } from './patterns/CoverBlock'
import { TwoColumn } from './patterns/TwoColumn'
import { SidelineList } from './patterns/SidelineList'
import { Timeline } from './patterns/Timeline'
import { ScenarioStack } from './patterns/ScenarioStack'
import { QuoteBlock } from './patterns/QuoteBlock'
import { AsideBox } from './patterns/AsideBox'
import { SmartGrid } from './patterns/SmartGrid'
import { ProcessSteps } from './patterns/ProcessSteps'
import { DataTable } from './patterns/DataTable'

export interface DocType {
  id: 'recoil' | 'profile' | 'brief' | 'prep' | 'receipt'
  label: string
  mono: string
  accent: string
  icon: string
}

export const DOC_TYPES: DocType[] = [
  { id: 'recoil', label: 'Recoil Report', mono: 'RECOIL', accent: T.cyan, icon: '◉' },
  { id: 'profile', label: 'Profile Scan', mono: 'PROFILE', accent: T.green, icon: '◈' },
  { id: 'brief', label: 'Brief', mono: 'BRIEF', accent: T.gold, icon: '◆' },
  { id: 'prep', label: 'Prep Doc', mono: 'PREP', accent: T.orange, icon: '◇' },
  { id: 'receipt', label: 'Receipt', mono: 'RECEIPT', accent: T.steel, icon: '▣' },
]

export interface DocPattern {
  id: string
  name: string
  desc: string
  Demo: React.ComponentType
  code: string
}

const h = React.createElement

export const DOC_PATTERNS: DocPattern[] = [
  {
    id: 'cover-block', name: 'CoverBlock', desc: 'Document hero: label badges (solid/outline), h1, subtitle, metadata strip, action buttons. Opens every ARCS document type.',
    Demo: () => h(CoverBlock, { badges: ['Recoil Report', 'First Round'], title: 'Jon Smyrl × Zach Harris', subtitle: 'Post-call forensic analysis. NCI: 84.2 — recoverable. One fix owns the outcome.', meta: 'ARCS RECOIL · Jun 1, 2026 · 47 min', actions: ['Open Receipt', 'File to Prep Book'], accent: T.cyan }),
    code: `<CoverBlock\n  badges={['Recoil Report', 'First Round']}\n  title="Jon Smyrl × Zach Harris"\n  subtitle="Post-call forensic analysis. NCI: 84.2 — recoverable."\n  meta="ARCS RECOIL · Jun 1, 2026 · 47 min"\n  actions={['Open Receipt', 'File to Prep Book']}\n  accent={T.cyan}\n/>`,
  },
  {
    id: 'two-column', name: 'TwoColumn', desc: 'Side-by-side contrast panel. Dark left (known/stated), standard right (inference/signal). Inline bold for key terms.',
    Demo: () => h(TwoColumn, { accent: T.gold, left: { heading: 'What the Posting Says', items: ['Embedded DS, <b>own the roadmap</b> for a key product area', '$140K–$348K range — a 2.5× spread'], note: 'The comp spread is negotiating leverage.' }, right: { heading: 'What It Actually Signals', items: ['Not a data team hire — a <b>product org hire</b> who happens to be a data scientist', 'Inbound cold outreach: something specific triggered the reach'] } }),
    code: `<TwoColumn\n  accent={T.gold}\n  left={{\n    heading: 'What the Posting Says',\n    items: ['Own the roadmap', '$140K–$348K range'],\n    note: 'The comp spread is leverage.',\n  }}\n  right={{\n    heading: 'What It Signals',\n    items: ['Product org hire, not data team hire'],\n  }}\n/>`,
  },
  {
    id: 'sideline-list', name: 'SidelineList', desc: 'Cards with left-accent color border. Accent color is semantic: cyan=nominal, green=strong, gold=caution, orange=drift.',
    Demo: () => h(SidelineList, { items: [{ label: 'Coherence', accent: T.cyan, title: 'Signal is coherent, packaging is not', body: 'Every capability traces back to the red thread. The external signal doesn\'t convey this yet.' }, { label: 'Recoil Zone', accent: T.red, title: 'Verbosity at the Panel of 2', body: 'Self-seeded the concern before the panel identified it. Fix: lead-with-the-point as a mechanical discipline.', note: 'Two instances observed. Do not make it three.' }] }),
    code: `<SidelineList items={[\n  {\n    label: 'Coherence',\n    accent: T.cyan,\n    title: 'Signal is coherent, packaging is not',\n    body: 'Every capability traces back to the red thread.',\n  },\n  {\n    label: 'Recoil Zone',\n    accent: T.red,\n    title: 'Verbosity at the Panel of 2',\n    body: 'Self-seeded the concern before the panel identified it.',\n    note: 'Two instances. Do not make it three.',\n  },\n]}/>`,
  },
  {
    id: 'timeline', name: 'Timeline', desc: 'Numbered vertical sequence with gradient connector. Peak steps highlighted in accent color. Use for call walks, phase plans, career arcs.',
    Demo: () => h(Timeline, { accent: T.cyan, steps: [{ label: 'Cold Open', title: 'Late Arrival — Rapport Recovery', body: 'Jon arrived 7 min late. Matched with the "plan-in-talker-buffer-time" riff. Clean entry.' }, { label: 'Process Recap', title: 'CONSTRUCTIVE INTERFERENCE — Peak Signal', body: '"More succinct than I would have been able to communicate it." Concision rewarded explicitly.', peak: true }, { label: 'Stack Probe', title: 'Builder-Fit Peak', body: 'Stack named: Claude Code, Warp, Supabase, Prisma, Next.js, Jest, Vercel.' }] }),
    code: `<Timeline accent={T.cyan} steps={[\n  { label: 'Phase 01', title: 'Open at Executive Altitude',\n    body: 'Demonstrate the strategic frame.' },\n  { label: 'Phase 02', title: 'Let the Interviewer Calibrate',\n    body: 'Pause after every answer.', peak: true },\n  { label: 'Phase 03', title: 'Drop the Disambiguating Question',\n    body: 'Her answer tells you the scenario.' },\n]}/>`,
  },
  {
    id: 'scenario-stack', name: 'ScenarioStack', desc: 'Interactive best/base/worst explorer. Tab switches animate. Note strip shows tactical implication per scenario.',
    Demo: () => h(ScenarioStack, { scenarios: { best: { title: 'Founding DS Intelligence Seat', body: 'Figma is building a design-intent intelligence function. You define what gets measured. 18 months: influencing the roadmap, not just reporting.', note: 'Life-changing scope. Practitioner-analyst compound is a category advantage.' }, base: { title: 'Strong Embedded Role', body: 'Real product influence, good comp, interesting technical problem. Builder archetype fits.' }, worst: { title: 'Support Backfill', body: '"Own the DS roadmap" is aspirational. Third analyst supporting one PM\'s OKRs.', note: 'Exit in 18 months after building the portfolio piece.' } } }),
    code: `<ScenarioStack scenarios={{\n  best: {\n    title: 'Founding Seat',\n    body: 'You define what gets measured across the AI-native surface.',\n    note: 'Life-changing scope.',\n  },\n  base: {\n    title: 'Strong Embedded Role',\n    body: 'Real product influence, good comp.',\n  },\n  worst: {\n    title: 'Support Backfill',\n    body: 'Third analyst supporting one PM.',\n    note: 'Exit in 18 months.',\n  },\n}}/>`,
  },
  {
    id: 'quote-block', name: 'QuoteBlock', desc: 'Left-bordered blockquote for key assertions, invariant observations, and strategic verdicts.',
    Demo: () => h('div', { style: { display: 'flex', flexDirection: 'column', gap: 10 } },
      h(QuoteBlock, { accent: T.cyan, attribution: 'Jon Smyrl · Jun 1, 2026 — response to stack walk', children: 'More succinct than I would have been able to communicate it.' }),
      h(QuoteBlock, { accent: T.gold, attribution: 'ARCS Recoil Protocol — Jon Smyrl × Zach Harris', children: 'When the interviewer keeps landing your point for you, you over-ran the runway.' }),
    ),
    code: `<QuoteBlock accent={T.cyan} attribution="Jon Smyrl · Jun 1, 2026">\n  More succinct than I would have been able to communicate it.\n</QuoteBlock>\n\n<QuoteBlock accent={T.gold} attribution="ARCS Recoil Protocol">\n  When the interviewer keeps landing your point, you over-ran the runway.\n</QuoteBlock>`,
  },
  {
    id: 'aside-box', name: 'AsideBox', desc: 'Color-coded callout boxes. Four variants: info (blue), caution (gold), success (green), warning (red). Label is overrideable.',
    Demo: () => h('div', { style: { display: 'flex', flexDirection: 'column', gap: 8 } },
      h(AsideBox, { variant: 'success', label: 'Validated', children: 'NCI 84.2 — strong and recoverable. The single fix is observable, mechanical, and within full control.' }),
      h(AsideBox, { variant: 'caution', label: 'Watch', children: 'Verbosity showed twice under open prompts. Panel of 2 will be harder clock.' }),
      h(AsideBox, { variant: 'info', label: 'Godel Status', children: 'EXTERNAL_EVIDENCE_REQUIRED — real signal comes from recruiter feedback or homework invite.' }),
      h(AsideBox, { variant: 'warning', label: 'High Risk', children: 'Lead-with-the-point is the #1 fix. Mechanical — not a judgment call. Do not make it three instances.' }),
    ),
    code: `<AsideBox variant="success" label="Validated">NCI 84.2 — recoverable.</AsideBox>\n<AsideBox variant="caution" label="Watch">Verbosity showed twice.</AsideBox>\n<AsideBox variant="info" label="Godel Status">EXTERNAL_EVIDENCE_REQUIRED.</AsideBox>\n<AsideBox variant="warning" label="High Risk">Lead-with-the-point is the #1 fix.</AsideBox>`,
  },
  {
    id: 'smart-grid', name: 'SmartGrid', desc: 'Equal-weight 2-column card grid. No hierarchy within grid. Use for data assets, capabilities, feature maps. Icon is optional.',
    Demo: () => h(SmartGrid, { cols: 2, items: [{ label: 'Data Asset 01', color: T.cyan, title: 'The Design Graph', body: 'Millions of community files — the largest labeled corpus of human design intent on the planet.' }, { label: 'Data Asset 02', color: '#7AD2FF', title: 'The Intent Graph', body: 'Every developer inspection is a behavioral signal: design intent → interpretation → production code.' }, { label: 'Data Asset 03', color: T.green, title: 'Plugin Observatory', body: '~1,000+ plugins, millions of sessions — a whitespace map of every unmet Figma need.' }, { label: 'Data Asset 04', color: T.gold, title: 'FigJam Upstream', body: 'FigJam diagram → Figma frame → Code Connect → production. Complete product lifecycle inside one ecosystem.' }] }),
    code: `<SmartGrid cols={2} items={[\n  { label: 'Quadrant A', color: T.cyan,\n    title: 'IP Chain of Custody',\n    body: '28 years of compounding practice.' },\n  { label: 'Quadrant B', color: T.green,\n    title: 'Provenance System Builder',\n    body: 'Turns implicit logic into transferable systems.' },\n]}/>`,
  },
  {
    id: 'process-steps', name: 'ProcessSteps', desc: 'Numbered sequential protocol. Active step highlighted in accent color. Use for protocols, walk-in strategies, phased plans.',
    Demo: () => h(ProcessSteps, { accent: T.orange, steps: [{ label: 'Phase 01', title: 'Open at Executive Altitude', body: 'Demonstrate you understand the strategic frame. Don\'t anchor to scope until you\'ve established altitude.', active: true }, { label: 'Phase 02', title: 'Let the Interviewer Calibrate', body: 'Pause. Read the signal. Don\'t anchor before you know if the best case is on the table.' }, { label: 'Phase 03', title: 'Drop the Disambiguating Question', body: '"Is this role defining the measurement strategy, or implementing one?" Her answer locates the scenario.' }, { label: 'Phase 04', title: 'Close with Conviction', body: '"I\'d like to understand the timeline for next steps." State it and wait.' }] }),
    code: `<ProcessSteps accent={T.orange} steps={[\n  { label: 'Phase 01', title: 'Open at Executive Altitude',\n    body: 'Demonstrate the strategic frame.',\n    active: true },\n  { label: 'Phase 02', title: 'Let the Interviewer Calibrate',\n    body: 'Pause after every substantive answer.' },\n  { label: 'Phase 03', title: 'Drop the Disambiguating Question',\n    body: 'Her answer locates the scenario.' },\n]}/>`,
  },
  {
    id: 'data-table', name: 'DataTable', desc: 'Bordered table with monospace first column and alternating surface rows. Use for career timelines, evidence ledgers, audit records.',
    Demo: () => h(DataTable, { columns: ['Period', 'Role', 'Domain'], rows: [['1997–2007', 'Innovation × Patents', 'IP Law Firms — Klarquist, Kolisch'], ['2007–2013', 'Technology Transfer Officer', 'OHSU — startup creation, licensing'], ['2013–2022', 'Sr. Director, Digital Patents', 'Nike — CryptoKicks (filed 2019)'], ['2021–present', 'Executive Director', 'Raiden Science Foundation — UBA5'], ['2023–present', 'Founder', 'La Vida Innovation — strategy, IP counsel']] }),
    code: `<DataTable\n  columns={['Period', 'Role', 'Domain']}\n  rows={[\n    ['1997–2007', 'Innovation × Patents', 'IP Law Firms'],\n    ['2007–2013', 'Technology Transfer', 'OHSU'],\n    ['2013–2022', 'Sr. Director, IP',    'Nike'],\n  ]}\n/>`,
  },
]
