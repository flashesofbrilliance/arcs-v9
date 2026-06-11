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
    </div>
  )
}
