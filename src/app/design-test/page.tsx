'use client'
import React, { useState } from 'react'
import { surface, signal, font, text, yWeather, nciColor, signalGlow } from '@/ui/tokens'
import { Wordmark } from '@/ui/Wordmark'
import { Label } from '@/ui/Label'
import { Gauge } from '@/ui/Gauge'
import { Badge } from '@/ui/Badge'
import { Button } from '@/ui/Button'
import { Card, CardHeader, CardDivider } from '@/ui/Card'
import { Field } from '@/ui/Field'
import { Picker } from '@/ui/Picker'
import { Tabs } from '@/ui/Tabs'
import { SegmentedSlider } from '@/ui/SegmentedSlider'
import { ChipToggle } from '@/ui/ChipToggle'
import { WeatherBar } from '@/instrument/WeatherBar'
import { TrueNorthPanel } from '@/instrument/TrueNorthPanel'
import { TributaryTile } from '@/instrument/TributaryTile'
import { SectionLabel } from '@/ui/SectionLabel'
import { Rule } from '@/ui/Rule'
import { Spinner } from '@/ui/Spinner'
import { ProgressBar } from '@/ui/ProgressBar'
import { StepProgress } from '@/ui/StepProgress'
import { HeaderLockup } from '@/molecules/HeaderLockup'
import { HorizonStakesRow } from '@/molecules/HorizonStakesRow'
import { CalibrationChips } from '@/molecules/CalibrationChips'
import { PipelineRunning } from '@/molecules/PipelineRunning'
import { ConvictionSidebar } from '@/molecules/ConvictionSidebar'
import { TributariesStack } from '@/molecules/TributariesStack'
import { InstrumentCluster } from '@/molecules/InstrumentCluster'
import { FatedGrid } from '@/molecules/FatedGrid'
import { TerrainPaths } from '@/molecules/TerrainPaths'
import { Home } from '@/organisms/Home'
import { CompassForm } from '@/organisms/CompassForm'
import { ResultView } from '@/organisms/ResultView'
import { Brief } from '@/organisms/Brief'
import { mockCompass } from '@/lib/mockCompass'
import { T as docT } from '@/document/tokens'
import { CoverBlock } from '@/document/patterns/CoverBlock'
import { TwoColumn } from '@/document/patterns/TwoColumn'
import { SidelineList } from '@/document/patterns/SidelineList'
import { Timeline } from '@/document/patterns/Timeline'
import { ScenarioStack } from '@/document/patterns/ScenarioStack'
import { QuoteBlock } from '@/document/patterns/QuoteBlock'
import { AsideBox } from '@/document/patterns/AsideBox'
import { SmartGrid } from '@/document/patterns/SmartGrid'
import { ProcessSteps } from '@/document/patterns/ProcessSteps'
import { DataTable } from '@/document/patterns/DataTable'
import { DOC_PATTERNS, DOC_TYPES } from '@/document/registry'
import { RecoilReport } from '@/document/screens/RecoilReport'
import { ProfileScan } from '@/document/screens/ProfileScan'
import { Brief as DocBrief } from '@/document/screens/Brief'
import { PrepDoc } from '@/document/screens/PrepDoc'
import { Receipt as DocReceipt } from '@/document/screens/Receipt'

const DOC_SCREEN_COMPS = [RecoilReport, ProfileScan, DocBrief, PrepDoc, DocReceipt]

function DocFrame({ dt, children }: { dt: typeof DOC_TYPES[number]; children: React.ReactNode }) {
  return (
    <div style={{ borderRadius: 10, border: '1px solid #243042', overflow: 'hidden', marginBottom: 22, background: '#020408' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 18px', borderBottom: `1px solid ${docT.border}`, background: 'linear-gradient(180deg,#0e151e,#0c121a)' }}>
        <span style={{ display: 'flex', gap: 6 }}>
          <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#FF4D6D66' }} />
          <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#FFD70066' }} />
          <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#00FF9D66' }} />
        </span>
        <span style={{ fontFamily: docT.mono, fontSize: 12, color: dt.accent, fontWeight: 700 }}>{dt.icon}</span>
        <span style={{ fontFamily: docT.mono, fontSize: 13, fontWeight: 700, color: '#dbe6f1' }}>{dt.label}</span>
        <span style={{ fontFamily: docT.mono, fontSize: 10.5, color: docT.fg4 }}>patterns.jsx</span>
        <span style={{ marginLeft: 'auto', fontFamily: docT.mono, fontSize: 10, color: dt.accent, letterSpacing: '.14em' }}>{dt.mono}</span>
      </div>
      <div style={{ maxWidth: 760, margin: '0 auto', padding: '4px 40px 36px' }}>{children}</div>
    </div>
  )
}

function DocCard({ idx, p }: { idx: string; p: typeof DOC_PATTERNS[number] }) {
  const Demo = p.Demo
  return (
    <div style={{ borderRadius: 8, border: '1px solid #243042', overflow: 'hidden', background: 'linear-gradient(165deg,#0c131b,#0a0f15)', display: 'flex', flexDirection: 'column', marginBottom: 18 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '11px 16px', borderBottom: `1px solid ${docT.border}`, background: 'linear-gradient(180deg,#0e151e,#0c121a)' }}>
        <span style={{ fontFamily: docT.mono, fontSize: 9.5, color: docT.fg4, width: 20 }}>{idx}</span>
        <span style={{ fontFamily: docT.mono, fontSize: 13, fontWeight: 700, color: '#dbe6f1' }}>{p.name}</span>
        <span style={{ marginLeft: 'auto', fontFamily: docT.mono, fontSize: 10, color: docT.fg4 }}>patterns.jsx</span>
      </div>
      <div style={{ padding: '13px 18px 4px', fontFamily: docT.sans, fontSize: 12.5, lineHeight: 1.55, color: docT.fg3 }}>{p.desc}</div>
      <div style={{ padding: '10px 20px 24px' }}><Demo /></div>
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section style={{ marginBottom: 40 }}>
      <Label style={{ marginBottom: 14, color: signal.cyan }}>{title}</Label>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, alignItems: 'flex-start' }}>{children}</div>
    </section>
  )
}

export default function DesignTestPage() {
  const [conf, setConf] = useState('mid')
  const [picker, setPicker] = useState('week')
  const [chips, setChips] = useState<Record<string, boolean>>({ lab: true, bar: false, kkl: false })
  const [field, setField] = useState('')
  // molecule/organism demo state
  const [mHorizon, setMHorizon] = useState('THIS_WEEK')
  const [mStakes, setMStakes] = useState('MEDIUM')
  const [mProtect, setMProtect] = useState<string[]>(['Cash'])
  const toggleProtect = (c: string) => setMProtect(p => p.includes(c) ? p.filter(x => x !== c) : p.length >= 2 ? p : [...p, c])
  const runwayResult = mockCompass('Should I take the Series A now or extend runway?')
  const hireResult = mockCompass('Do I make the leverage hire this quarter?')

  return (
    <div style={{ minHeight: '100vh', background: surface.bg, padding: '40px 48px', fontFamily: font.sans }}>
      <div style={{ marginBottom: 36 }}>
        <Wordmark section="DESIGN TEST" />
      </div>

      <Section title="Wordmark / Label">
        <Wordmark />
        <Wordmark section="OBSERVATORY" />
        <Label>Instrument Label</Label>
        <Label color={signal.gold}>Gold Label</Label>
      </Section>

      <Section title="Gauge">
        <Gauge label="NCI" value={74} sub="coherence index" color={nciColor(74)} glow={signalGlow(nciColor(74))} accent={signal.green} minWidth={140} flex="0 0 auto" />
        <Gauge label="Coherence" value={42} sub="degraded" color={nciColor(42)} glow={signalGlow(nciColor(42))} accent={signal.gold} minWidth={140} flex="0 0 auto" />
        <Gauge label="Satoshi" value="∞" minWidth={140} flex="0 0 auto" />
      </Section>

      <Section title="Badge — registers">
        <Badge label="CLARITY RIDGE" glyph="▲" color={signal.green} register="state" />
        <Badge label="GOVERNANCE" color={signal.gold} register="governance" />
        <Badge label="metadata" color={text.muted} register="light" />
        <Badge label="COCKPIT ALIAS" glyph="◆" color={signal.cyan} register="cockpit" />
      </Section>

      <Section title="Button — variants & sizes">
        <Button variant="primary" glyph="▲">Primary</Button>
        <Button variant="green">Green</Button>
        <Button variant="gold">Gold</Button>
        <Button variant="danger" glyph="●">Danger</Button>
        <Button variant="ghost">Ghost</Button>
        <Button variant="primary" size="sm">Small</Button>
        <Button variant="primary" size="lg">Large</Button>
        <Button variant="primary" disabled>Disabled</Button>
      </Section>

      <Section title="Card">
        <Card style={{ width: 280 }}>
          <CardHeader label="DEFAULT CARD" />
          <div style={{ color: text.secondary, fontSize: 14 }}>Neutral glass body with subtle bevel.</div>
          <CardDivider />
          <div style={{ color: text.dimmed, fontSize: 12 }}>Footer metadata</div>
        </Card>
        <Card accent={signal.cyan} style={{ width: 280 }}>
          <CardHeader label="ACCENT CARD" accent={signal.cyan} />
          <div style={{ color: text.secondary, fontSize: 14 }}>Signal glass, underlit-LED finish.</div>
        </Card>
      </Section>

      <Section title="WeatherBar">
        <WeatherBar weather={yWeather.GREEN} delta={12} resolution="SHARP" style={{ width: 360 }} />
        <WeatherBar weather={yWeather.PARADOX} delta={-8} resolution="MOIRE" style={{ width: 360 }} />
      </Section>

      <Section title="TrueNorthPanel">
        <TrueNorthPanel heading="TRUE NORTH · BEARING" style={{ maxWidth: 560 }}>
          Ship the conviction-gated Lab card before the case study; the gate is the test, not the copy.
        </TrueNorthPanel>
      </Section>

      <Section title="TributaryTile — meta / challenge / adjacent">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10, width: 420 }}>
          <TributaryTile label="META" glyph="≡" color={signal.cyan}>What are you actually deciding beneath the stated question?</TributaryTile>
          <TributaryTile label="CHALLENGE" glyph="△" color={signal.gold}>The overlooked constraint you keep routing around.</TributaryTile>
          <TributaryTile label="ADJACENT" glyph="⊕" color={signal.violet}>A cross-domain reframe from avalanche terrain.</TributaryTile>
        </div>
      </Section>

      <Section title="Tabs">
        <Tabs style={{ width: 480 }} items={[
          { value: 'risk', label: 'Risk', glyph: '△', content: <div style={{ color: text.secondary, fontSize: 14 }}>Risk reading panel content.</div> },
          { value: 'timing', label: 'Timing', glyph: '◆', content: <div style={{ color: text.secondary, fontSize: 14 }}>Timing reading panel content.</div> },
        ]} />
      </Section>

      <Section title="SegmentedSlider">
        <SegmentedSlider style={{ width: 360 }} value={conf} onChange={setConf} options={[
          { value: 'low', label: 'LOW', accent: 'red' },
          { value: 'mid', label: 'MID', accent: 'gold' },
          { value: 'high', label: 'HIGH', accent: 'green' },
        ]} />
      </Section>

      <Section title="ChipToggle group">
        <ChipToggle label="LAB" glyph="▲" accent={signal.green} selected={chips.lab} onClick={() => setChips(c => ({ ...c, lab: !c.lab }))} />
        <ChipToggle label="BAR" glyph="◆" accent={signal.gold} selected={chips.bar} onClick={() => setChips(c => ({ ...c, bar: !c.bar }))} />
        <ChipToggle label="KKL" glyph="⊕" accent={signal.cyan} selected={chips.kkl} onClick={() => setChips(c => ({ ...c, kkl: !c.kkl }))} />
      </Section>

      <Section title="Field / Picker">
        <Field label="Question" placeholder="What are you deciding?" value={field} onChange={(e) => setField(e.target.value)} style={{ width: 360 }} />
        <Field label="Strongest counter-argument" as="textarea" rows={3} placeholder="The best case against your instinct…" style={{ width: 360 }} />
        <Picker label="Horizon" value={picker} onChange={setPicker} style={{ width: 240 }} options={[
          { value: 'today', label: 'Today' },
          { value: 'week', label: 'This week' },
          { value: 'quarter', label: 'This quarter' },
          { value: 'years', label: 'Years out' },
        ]} />
      </Section>

      {/* ─── Newer atoms ─────────────────────────────────────────── */}
      <Section title="SectionLabel / Rule">
        <div style={{ width: 360, display: 'flex', flexDirection: 'column', gap: 12 }}>
          <SectionLabel index="01">State the decision</SectionLabel>
          <SectionLabel index="02" color={signal.gold}>Calibrate · optional</SectionLabel>
          <SectionLabel>Tributaries · where to navigate next</SectionLabel>
          <Rule />
        </div>
      </Section>

      <Section title="Spinner">
        <Spinner size={18} />
        <Spinner size={28} />
        <Spinner size={28} color={signal.gold} />
      </Section>

      <Section title="ProgressBar">
        <div style={{ width: 360, display: 'flex', flexDirection: 'column', gap: 12 }}>
          <ProgressBar value={68} />
          <ProgressBar indeterminate />
          <ProgressBar value={40} color={signal.gold} />
        </div>
      </Section>

      <Section title="StepProgress">
        <StepProgress current={3} style={{ width: 360 }} />
      </Section>

      {/* ─── Molecules ───────────────────────────────────────────── */}
      <Section title="MOLECULE · HeaderLockup">
        <div style={{ width: 560 }}>
          <HeaderLockup section="Receipt" actionLabel="New question" actionGlyph="←" />
        </div>
      </Section>

      <Section title="MOLECULE · HorizonStakesRow">
        <div style={{ width: 480 }}>
          <HorizonStakesRow horizon={mHorizon} stakes={mStakes} onHorizonChange={setMHorizon} onStakesChange={setMStakes} />
        </div>
      </Section>

      <Section title="MOLECULE · CalibrationChips">
        <div style={{ width: 420 }}>
          <CalibrationChips selected={mProtect} onToggle={toggleProtect} />
        </div>
      </Section>

      <Section title="MOLECULE · PipelineRunning">
        <div style={{ width: 360 }}>
          <PipelineRunning current={3} />
        </div>
      </Section>

      <Section title="MOLECULE · InstrumentCluster">
        <div style={{ width: 640 }}>
          <InstrumentCluster result={runwayResult} />
        </div>
      </Section>

      <Section title="MOLECULE · TributariesStack">
        <div style={{ width: 480 }}>
          <TributariesStack tributaries={runwayResult.tributaries} />
        </div>
      </Section>

      <Section title="MOLECULE · FatedGrid">
        <div style={{ width: 480 }}>
          <FatedGrid fated={runwayResult.reasoning.fated || {}} />
        </div>
      </Section>

      <Section title="MOLECULE · TerrainPaths">
        <div style={{ width: 480 }}>
          <TerrainPaths paths={runwayResult.reasoning.paths} />
        </div>
      </Section>

      <Section title="MOLECULE · ConvictionSidebar">
        <div style={{ width: 300 }}>
          <ConvictionSidebar result={runwayResult} />
        </div>
      </Section>

      {/* ─── Organisms ───────────────────────────────────────────── */}
      <Section title="ORGANISM · Home">
        <div style={{ width: '100%', border: `1px solid ${signal.cyan}30`, borderRadius: 6, overflow: 'hidden', background: surface.bg }}>
          <Home />
        </div>
      </Section>

      <Section title="ORGANISM · CompassForm">
        <div style={{ width: '100%', border: `1px solid ${signal.cyan}30`, borderRadius: 6, overflow: 'hidden', background: surface.bg }}>
          <CompassForm
            question="" horizon={mHorizon} stakes={mStakes} protecting={mProtect} calibrated
            step={3}
            onQuestionChange={() => {}} onHorizonChange={setMHorizon} onStakesChange={setMStakes}
            onToggleProtect={toggleProtect} onSubmit={() => {}}
          />
        </div>
      </Section>

      <Section title="ORGANISM · ResultView">
        <div style={{ width: '100%', border: `1px solid ${signal.cyan}30`, borderRadius: 6, overflow: 'hidden', background: surface.bg }}>
          <ResultView result={hireResult} />
        </div>
      </Section>

      <Section title="ORGANISM · Brief">
        <div style={{ width: '100%', border: `1px solid ${signal.cyan}30`, borderRadius: 6, overflow: 'hidden', background: surface.bg }}>
          <Brief result={runwayResult} />
        </div>
      </Section>

      {/* ─── DOCUMENT KIT ───────────────────────────────────────────── */}
      <Section title="DOCUMENT KIT · 10 reader-view patterns">
        <div style={{ width: '100%', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24, marginBottom: 24 }}>
            <DocCard idx="01" p={DOC_PATTERNS[0]} />
            <DocCard idx="02" p={DOC_PATTERNS[1]} />
            <DocCard idx="03" p={DOC_PATTERNS[2]} />
            <DocCard idx="04" p={DOC_PATTERNS[3]} />
            <DocCard idx="05" p={DOC_PATTERNS[4]} />
            <DocCard idx="06" p={DOC_PATTERNS[5]} />
            <DocCard idx="07" p={DOC_PATTERNS[6]} />
            <DocCard idx="08" p={DOC_PATTERNS[7]} />
            <DocCard idx="09" p={DOC_PATTERNS[8]} />
            <DocCard idx="10" p={DOC_PATTERNS[9]} />
          </div>
        </div>
      </Section>

      <Section title="DOCUMENT KIT · 5 document screens">
        <div style={{ width: '100%' }}>
          {DOC_TYPES.map((dt, i) => {
            const Comp = DOC_SCREEN_COMPS[i]
            return <DocFrame key={dt.id} dt={dt}><Comp /></DocFrame>
          })}
        </div>
      </Section>
    </div>
  )
}
