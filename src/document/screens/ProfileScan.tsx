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
import { AsideBox } from '../patterns/AsideBox'

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
    badges: ['Profile Scan', 'DEEP · LinkedIn profile PDF + full data export'],
    title: 'Profile Scan — Zach Harris',
    subtitle: 'The LinkedIn export surfaces far more than the headline competency list: 100 skills, 765 endorsements, 38 authored long-form articles, dated concurrent-role tenure, and the platform\'s own inferences about who it thinks you are.',
    meta: 'ARCS PROFILE · Jun 2026 · LinkedIn profile PDF + export ZIP, enrichment pipeline',
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

      <Sec id="z-contrast" idx="01" label="Signal Read" title="Headline vs. Full Export" accent={A}>
        <TwoColumn accent={A}
          left={{
            heading: 'What the PDF/Headline Says',
            items: ['A short competency list and a top-15 skill cluster — the surface LinkedIn shows by default', 'Career read as a sequence of roles with no visible concurrency', 'No authored writing, no endorsement depth, no sense of platform-side inference'],
            note: 'The headline is a summary. The export is the actual record.',
          }}
          right={{
            heading: 'What the Full Export Actually Contains',
            items: ['<b>100</b> skills with real per-skill endorsement counts (765 endorsements total), not the 15-skill cluster the summary view shows', '<b>38</b> authored long-form articles — a full first-person corpus, not just short post copy', 'Dated position history reveals <b>concurrent</b> advisor roles (Le Woof Brand, Cornell Tech, Outlier Ventures) running alongside one 6.5-year anchor engagement (Mañana) — not the sequential job-hopping a naive read of "5+ positions" would suggest', 'LinkedIn\'s own ad-targeting model of the account ("platform inferences") — a signal class with no slot in the document yet'],
          }}
        />
      </Sec>

      {showRich && (
      <Sec id="z-threads" idx="02" label="Profile Threads" title="Four-Thread Assessment" accent={A}>
        <SidelineList items={[
          { label: 'Red Thread · Recurring Risk', accent: T.red, title: 'Tenure Misreads Without Dated Data', body: 'The export-only parse flagged "frequent role changes (5+ positions)" as a drainer signal. Cross-checking against the dated PDF tenure shows 3 of those are concurrent advisor/mentor roles alongside one long anchor (Mañana, 6.5 yrs) — not sequential job-hopping. The flag doesn\'t survive contact with dates.', note: 'Concurrent: Le Woof Brand (advisor) · Cornell Tech (mentor) · Outlier Ventures (advisor).' },
          { label: 'Gold Thread · Working Asset', accent: T.gold, title: '100 Skills, 765 Endorsements — Fully Surfaced', body: 'The full export carries real per-skill endorsement counts for all 100 listed skills, not the 15-skill summary cluster most views stop at. This is straightforward, already-parsed enrichment (operators/linkedin_pipeline/linkedin_export.py), not a future build.' },
          { label: 'Green Thread · Conviction', accent: T.green, title: '38 Authored Articles — a Real First-Person Corpus', body: 'Full long-form writing, HTML-stripped and parsed from the export\'s Articles/ directory. The longest single article ran 6,013 words. This corpus is the primary input for anything that wants to read voice or thesis, not the short post text alone.' },
          { label: 'Vermillion · Constraint', accent: T.orange, title: 'Platform Inferences Have No Document Slot Yet', body: 'LinkedIn\'s own ad-targeting categories about this account (Inferences_about_you.csv) are a genuinely different signal class — the platform\'s model of the person, not the person\'s own data. Parsed and available, but the canonical six-section document shape has nowhere to put it yet — see below.' },
        ]} />
      </Sec>
      )}

      {showDeep && (
      <Sec id="z-inferences" idx="03" label="Platform Model" title="What LinkedIn Infers About This Account" accent={A}>
        <SmartGrid cols={2} items={[
          { label: 'Inference', color: T.cyan, title: 'Frontier-Tech Affinity', body: 'LinkedIn\'s ad-targeting model categorizes this account as having an affinity for emerging/frontier technology — its own read of the signal, not a self-report.' },
          { label: 'Inference', color: T.gold, title: 'Interest: Technology Media', body: 'Flagged as interested in media about technology — consistent with the authored-article corpus, but derived independently by the platform.' },
        ]} />
      </Sec>
      )}

      <Sec id="z-assertion" idx="04" label="Key Assertion" title="The Enrichment Theorem" accent={A}>
        <QuoteBlock accent={A} attribution="ARCS Profile Scan — Zach Harris, Thread Analysis">
          The headline view and the full export are not the same document at different resolutions — the export contains entire signal classes (the authored corpus, full endorsement depth, the platform's own inferences) that the headline never surfaces at all.
        </QuoteBlock>
      </Sec>
    </div>
  )
}

// ─── Dynamic variant — real per-subject data, not the static ZACH_PROFILE mock ─
// Produced by the profile-scan pipeline (see _SPECS/profile-scan-spec-v1.md).
// A scan file is written to runtime/scan/generated/<scanId>.json, then the
// /scan/[scanId] route renders it through this tolerant normalizer onto the
// SAME six canonical sections/patterns as the ProfileScan sample above:
//   Cover → 01 Signal Read (TwoColumn) → 02 Thread Assessment (SidelineList)
//   → 03 Evidence Ledger (DataTable) → 04 Capability Map (SmartGrid)
//   → 05 Key Assertion (QuoteBlock).
//
// Governing invariants (spec §"Governing invariants for the block library"):
// Traceable · Transparent · Factual · thread-color convention
// (red=risk, gold=working asset, green=conviction, vermillion/orange=constraint).
// Depth truncates, it does not branch: SIMPLE ⊂ RICH ⊂ DEEP (spec §"Depth
// model, finalized"). Do NOT change the shared pattern prop contracts — they
// are also consumed by RecoilReport/Brief/Receipt.

export type ProfileScanRaw = Record<string, unknown>

const P_COLOR_ALIAS: Record<string, string> = {
  green: T.green, gold: T.gold, red: T.red, cyan: T.cyan,
  orange: T.orange, vermillion: T.orange, purple: T.purple, steel: T.steel,
}

function pIsRecord(v: unknown): v is Record<string, unknown> {
  return typeof v === 'object' && v !== null
}
function pStr(v: unknown, fallback = ''): string {
  return typeof v === 'string' ? v : fallback
}
function pStrArr(v: unknown): string[] {
  return Array.isArray(v) ? v.filter((s): s is string => typeof s === 'string') : []
}
function pColor(v: unknown, fallback: string): string {
  const s = pStr(v)
  return P_COLOR_ALIAS[s] ?? (s || fallback)
}

export interface ProfileScanData {
  cover: { badges: string[]; title: string; subtitle: string; meta: string; actions: string[] }
  notice: string
  signalRead: { left: TwoColumnPanelLike; right: TwoColumnPanelLike }
  threads: { label?: string; accent: string; title: string; body: string; note?: string }[]
  evidenceLedger: { columns: string[]; rows: string[][] }
  capabilityMap: { label?: string; color: string; title: string; body: string }[]
  keyAssertion: { text: string; attribution: string }
}
interface TwoColumnPanelLike { heading?: string; body?: string; items?: string[]; note?: string }

function pPanel(raw: unknown): TwoColumnPanelLike {
  if (!pIsRecord(raw)) return {}
  return {
    heading: pStr(raw.heading) || undefined,
    body: pStr(raw.body) || undefined,
    items: pStrArr(raw.items).length ? pStrArr(raw.items) : undefined,
    note: pStr(raw.note) || undefined,
  }
}

function normalizeProfileScan(raw: ProfileScanRaw): ProfileScanData {
  const rc = pIsRecord(raw.cover) ? raw.cover : {}
  const sr = pIsRecord(raw.signalRead) ? raw.signalRead : {}
  const el = pIsRecord(raw.evidenceLedger) ? raw.evidenceLedger : {}
  const ka = pIsRecord(raw.keyAssertion) ? raw.keyAssertion : {}
  return {
    cover: {
      badges: pStrArr(rc.badges).length ? pStrArr(rc.badges) : ['Profile Scan', ''],
      title: pStr(rc.title, 'Profile Scan'),
      subtitle: pStr(rc.subtitle),
      meta: pStr(rc.meta),
      actions: pStrArr(rc.actions),
    },
    notice: pStr(raw.notice),
    signalRead: { left: pPanel(sr.left), right: pPanel(sr.right) },
    threads: (Array.isArray(raw.threads) ? raw.threads : []).filter(pIsRecord).map((t) => ({
      label: pStr(t.label) || undefined,
      accent: pColor(t.accent ?? t.color, T.cyan),
      title: pStr(t.title),
      body: pStr(t.body),
      note: pStr(t.note) || undefined,
    })),
    evidenceLedger: {
      columns: pStrArr(el.columns),
      rows: (Array.isArray(el.rows) ? el.rows : [])
        .filter(Array.isArray)
        .map((r) => (r as unknown[]).map((c) => pStr(c))),
    },
    capabilityMap: (Array.isArray(raw.capabilityMap) ? raw.capabilityMap : []).filter(pIsRecord).map((c) => ({
      label: pStr(c.label) || undefined,
      color: pColor(c.color ?? c.accent, T.fg4),
      title: pStr(c.title),
      body: pStr(c.body),
    })),
    keyAssertion: { text: pStr(ka.text), attribution: pStr(ka.attribution, 'ARCS Profile Scan · Thread Analysis') },
  }
}

export function ProfileScanFromData({ data: raw, depth = 'deep' }: { data: ProfileScanRaw; depth?: ScanDepth }) {
  const A = T.green
  const d = normalizeProfileScan(raw)
  // Depth truncates per spec: SIMPLE = Signal Read + Key Assertion; RICH adds
  // Thread Assessment + Evidence Ledger; DEEP adds Capability Map.
  const rawDepth = pStr(raw.depth)
  const eff: ScanDepth = (rawDepth === 'simple' || rawDepth === 'rich' || rawDepth === 'deep') ? rawDepth : depth
  const showRich = eff === 'rich' || eff === 'deep'
  const showDeep = eff === 'deep'
  return (
    <div>
      <CoverBlock {...d.cover} accent={A} />

      {d.notice && (
        <div style={{ margin: '16px 0' }}>
          <AsideBox variant="info" label="Provenance & honesty note">{d.notice}</AsideBox>
        </div>
      )}

      <Sec id="s-signal" idx="01" label="Signal Read" title="Stated vs. Observed" accent={A}>
        <TwoColumn accent={A} left={d.signalRead.left} right={d.signalRead.right} />
      </Sec>

      {showRich && d.threads.length > 0 && (
        <Sec id="s-threads" idx="02" label="Thread Assessment" title="Four-Thread Read" accent={A}>
          <SidelineList items={d.threads} />
        </Sec>
      )}

      {showRich && d.evidenceLedger.rows.length > 0 && (
        <Sec id="s-ledger" idx="03" label="Evidence Ledger" title="Dated Career Record" accent={A}>
          <DataTable columns={d.evidenceLedger.columns} rows={d.evidenceLedger.rows} />
        </Sec>
      )}

      {showDeep && d.capabilityMap.length > 0 && (
        <Sec id="s-capabilities" idx="04" label="Capability Map" title="Core · Compound · Signal · Gap" accent={A}>
          <SmartGrid cols={2} items={d.capabilityMap} />
        </Sec>
      )}

      <Sec id="s-assertion" idx={showDeep ? '05' : '02'} label="Key Assertion" title="The Load-Bearing Read" accent={A}>
        <QuoteBlock accent={A} attribution={d.keyAssertion.attribution}>
          {d.keyAssertion.text}
        </QuoteBlock>
      </Sec>
    </div>
  )
}
