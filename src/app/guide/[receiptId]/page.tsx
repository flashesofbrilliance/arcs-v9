"use client"

import { useEffect, useState, useCallback } from "react"
import { useParams, useRouter } from "next/navigation"

const s = {
  bg: "#020408",
  surface: "#0d1117",
  border: "#1e293b",
  text: "#e2e8f0",
  muted: "#475569",
  dimmed: "#64748b",
  cyan: "#00F0FF",
  green: "#00FF9D",
  gold: "#FFD700",
  red: "#FF4D6D",
  arcs: "#00F0FF",
}

// ── Density levels ────────────────────────────────────────────────────────────
// 1=Executive(90s) 2=Strategic(5m) 3=Operational(15m) 4=Tactical(30m) 5=Surgical(45m)
type Density = 1 | 2 | 3 | 4 | 5
const DENSITY_LEVELS: { level: Density; label: string; time: string; color: string }[] = [
  { level: 1, label: "Exec",        time: "90 sec", color: "#94a3b8" },
  { level: 2, label: "Strategic",   time: "5 min",  color: "#00F0FF" },
  { level: 3, label: "Operational", time: "15 min", color: "#00FF9D" },
  { level: 4, label: "Tactical",    time: "30 min", color: "#FFD700" },
  { level: 5, label: "Surgical",    time: "45 min", color: "#FF4D6D" },
]
const DENSITY_KEY = "arcs_guide_density"

interface Artifact {
  title: string
  abstract: string
}

interface StageData {
  id: string
  title: string
  shortLabel: string
  spineLabel: string
  questionCompass: string
  stageJTBD: string
  testingAboutThem: string
  agenda: string[]
  preWork: string[]
  kycLens: string[]
  midcurveTripwire: string
  writesIntoNextTable: { yes: string; no: string }
  artifacts: Artifact[]
}

interface StageLogEntry {
  stageId: string
  completedAt: string
  verdict: string
  vibe?: string
}

interface GuideData {
  id: string
  receiptId: string
  mode: string
  guideTitle: string
  betLabel: string
  totalPrepHours: string
  stages: string
  stageLog: string
  outcomeStatement: string
  leadingIndicator: string
  kpiLabel: string
  failureSignal: string
}

// ── OutcomeTargetCard ────────────────────────────────────────────────────────
function OutcomeTargetCard({
  outcomeStatement,
  leadingIndicator,
  kpiLabel,
  failureSignal,
  onChangeOutcome,
  onChangeLeading,
  onChangeKpi,
  onChangeFailure,
}: {
  outcomeStatement: string
  leadingIndicator: string
  kpiLabel: string
  failureSignal: string
  onChangeOutcome: (v: string) => void
  onChangeLeading: (v: string) => void
  onChangeKpi: (v: string) => void
  onChangeFailure: (v: string) => void
}) {
  return (
    <div style={{ background: s.surface, border: `1px solid ${s.border}`, borderRadius: 8, padding: "0.625rem 1rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
      <div style={{ fontSize: "0.55rem", fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", color: s.muted }}>OUTCOME TARGET</div>
      <input
        value={outcomeStatement}
        onChange={e => onChangeOutcome(e.target.value)}
        style={{ background: "transparent", border: "none", outline: "none", fontSize: "0.85rem", fontWeight: 600, color: s.text, width: "100%", padding: 0 }}
        placeholder="By end of [stage], [entity] has [specific observable action]"
      />
      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.375rem", background: `${s.cyan}12`, border: `1px solid ${s.cyan}33`, borderRadius: 5, padding: "0.2rem 0.5rem" }}>
          <span style={{ fontSize: "0.5rem", color: s.cyan, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", whiteSpace: "nowrap" }}>Leading</span>
          <input
            value={leadingIndicator}
            onChange={e => onChangeLeading(e.target.value)}
            style={{ background: "transparent", border: "none", outline: "none", fontSize: "0.72rem", color: s.cyan, minWidth: 120 }}
            placeholder="Signal before outcome confirmed"
          />
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.375rem", background: `${s.green}12`, border: `1px solid ${s.green}33`, borderRadius: 5, padding: "0.2rem 0.5rem" }}>
          <span style={{ fontSize: "0.5rem", color: s.green, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", whiteSpace: "nowrap" }}>KPI</span>
          <input
            value={kpiLabel}
            onChange={e => onChangeKpi(e.target.value)}
            style={{ background: "transparent", border: "none", outline: "none", fontSize: "0.72rem", color: s.green, minWidth: 80 }}
            placeholder="Measurable proxy"
          />
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.375rem", background: `${s.red}12`, border: `1px solid ${s.red}33`, borderRadius: 5, padding: "0.2rem 0.5rem" }}>
          <span style={{ fontSize: "0.5rem", color: s.red, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", whiteSpace: "nowrap" }}>Failure</span>
          <input
            value={failureSignal}
            onChange={e => onChangeFailure(e.target.value)}
            style={{ background: "transparent", border: "none", outline: "none", fontSize: "0.72rem", color: s.red, minWidth: 120 }}
            placeholder="Early warning signal"
          />
        </div>
      </div>
    </div>
  )
}

// ── CollapsibleBand ──────────────────────────────────────────────────────────
function CollapsibleBand({
  title,
  isOpen,
  onToggle,
  children,
  accentColor = s.muted,
}: {
  title: string
  isOpen: boolean
  onToggle: () => void
  children: React.ReactNode
  accentColor?: string
}) {
  return (
    <div style={{ background: s.bg, border: `1px solid ${s.border}`, borderRadius: 8, overflow: "hidden", marginBottom: "0.875rem" }}>
      <button
        onClick={onToggle}
        style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0.625rem 1rem", background: s.surface, border: "none", cursor: "pointer" }}
      >
        <span style={{ fontSize: "0.65rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", color: accentColor }}>{title}</span>
        <span style={{ fontSize: "0.75rem", color: s.dimmed }}>{isOpen ? "▲" : "▼"}</span>
      </button>
      {isOpen && <div style={{ padding: "1rem" }}>{children}</div>}
    </div>
  )
}

// ── ArtifactModal ────────────────────────────────────────────────────────────
function ArtifactModal({ artifact, onClose }: { artifact: Artifact; onClose: () => void }) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") onClose() }
    window.addEventListener("keydown", handler)
    return () => window.removeEventListener("keydown", handler)
  }, [onClose])

  return (
    <div
      onClick={onClose}
      style={{ position: "fixed", inset: 0, background: "rgba(15,23,42,0.4)", zIndex: 100, display: "flex", alignItems: "center", justifyContent: "center", padding: "1rem" }}
    >
      <div
        onClick={e => e.stopPropagation()}
        style={{ background: s.bg, border: `1px solid ${s.border}`, borderRadius: 12, padding: "1.5rem", maxWidth: 480, width: "100%", boxShadow: "0 20px 60px rgba(0,0,0,0.15)" }}
      >
        <div style={{ fontSize: "0.6rem", color: s.muted, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: "0.5rem" }}>Artifact</div>
        <div style={{ fontSize: "1rem", fontWeight: 700, color: s.text, marginBottom: "0.75rem" }}>{artifact.title}</div>
        <div style={{ fontSize: "0.85rem", color: s.muted, lineHeight: 1.6 }}>{artifact.abstract}</div>
        <button
          onClick={onClose}
          style={{ marginTop: "1.25rem", padding: "0.5rem 1rem", borderRadius: 6, background: s.surface, border: `1px solid ${s.border}`, color: s.text, fontSize: "0.75rem", cursor: "pointer" }}
        >
          Close
        </button>
      </div>
    </div>
  )
}

// ── PostCallLogModal ─────────────────────────────────────────────────────────
function PostCallLogModal({
  stage,
  onClose,
  onLog,
}: {
  stage: StageData
  onClose: () => void
  onLog: (verdict: string, vibe?: string, indicatorObserved?: boolean) => void
}) {
  const [verdict, setVerdict] = useState<string | null>(null)
  const [vibe, setVibe] = useState<string | null>(null)
  const [indicatorObserved, setIndicatorObserved] = useState(false)

  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") onClose() }
    window.addEventListener("keydown", handler)
    return () => window.removeEventListener("keydown", handler)
  }, [onClose])

  const vibes = [
    { emoji: "🔥", label: "Fire" },
    { emoji: "✅", label: "Solid" },
    { emoji: "😐", label: "Meh" },
    { emoji: "😬", label: "Rough" },
    { emoji: "💀", label: "Dead" },
  ]

  const verdicts = [
    { id: "advance", label: "Advance ✓", color: s.green },
    { id: "pause", label: "Pause ⏸", color: s.gold },
    { id: "abort", label: "Abort ✗", color: s.red },
  ]

  return (
    <div
      onClick={onClose}
      style={{ position: "fixed", inset: 0, background: "rgba(15,23,42,0.4)", zIndex: 100, display: "flex", alignItems: "center", justifyContent: "center", padding: "1rem" }}
    >
      <div
        onClick={e => e.stopPropagation()}
        style={{ background: s.bg, border: `1px solid ${s.border}`, borderRadius: 12, padding: "1.5rem", maxWidth: 440, width: "100%", boxShadow: "0 20px 60px rgba(0,0,0,0.15)" }}
      >
        <div style={{ fontSize: "0.6rem", color: s.muted, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: "0.25rem" }}>{stage.id}</div>
        <div style={{ fontSize: "0.95rem", fontWeight: 700, color: s.text, marginBottom: "1.25rem" }}>{stage.title}</div>

        <div style={{ marginBottom: "1rem" }}>
          <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", cursor: "pointer" }}>
            <input
              type="checkbox"
              checked={indicatorObserved}
              onChange={e => setIndicatorObserved(e.target.checked)}
              style={{ accentColor: s.cyan, width: 14, height: 14, cursor: "pointer" }}
            />
            <span style={{ fontSize: "0.78rem", color: s.muted }}>Leading indicator observed</span>
          </label>
        </div>

        <div style={{ marginBottom: "1.25rem" }}>
          <div style={{ fontSize: "0.65rem", fontWeight: 700, color: s.muted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "0.625rem" }}>Time Verdict</div>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            {verdicts.map(v => (
              <button
                key={v.id}
                onClick={() => setVerdict(v.id)}
                style={{
                  flex: 1, padding: "0.5rem 0.25rem", borderRadius: 6, border: `2px solid ${verdict === v.id ? v.color : s.border}`,
                  background: verdict === v.id ? `${v.color}15` : s.surface, color: verdict === v.id ? v.color : s.muted,
                  fontSize: "0.75rem", fontWeight: 600, cursor: "pointer", transition: "all 0.1s",
                }}
              >
                {v.label}
              </button>
            ))}
          </div>
        </div>

        <div style={{ marginBottom: "1.5rem" }}>
          <div style={{ fontSize: "0.65rem", fontWeight: 700, color: s.muted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "0.625rem" }}>Vibes</div>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            {vibes.map(v => (
              <button
                key={v.emoji}
                onClick={() => setVibe(v.emoji)}
                style={{
                  flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: "0.25rem",
                  padding: "0.5rem 0.25rem", borderRadius: 6, border: `2px solid ${vibe === v.emoji ? s.text : s.border}`,
                  background: vibe === v.emoji ? s.surface : "transparent", cursor: "pointer", transition: "all 0.1s",
                }}
              >
                <span style={{ fontSize: "1.25rem" }}>{v.emoji}</span>
                <span style={{ fontSize: "0.6rem", color: s.muted }}>{v.label}</span>
              </button>
            ))}
          </div>
        </div>

        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button
            onClick={onClose}
            style={{ flex: 1, padding: "0.625rem", borderRadius: 6, border: `1px solid ${s.border}`, background: s.surface, color: s.muted, fontSize: "0.8rem", cursor: "pointer" }}
          >
            Cancel
          </button>
          <button
            onClick={() => {
              if (verdict) onLog(verdict, vibe ?? undefined, indicatorObserved)
            }}
            disabled={!verdict}
            style={{
              flex: 2, padding: "0.625rem", borderRadius: 6, border: "none",
              background: verdict ? s.text : s.border, color: verdict ? s.bg : s.muted,
              fontSize: "0.8rem", fontWeight: 600, cursor: verdict ? "pointer" : "not-allowed", transition: "all 0.1s",
            }}
          >
            Done
          </button>
        </div>
      </div>
    </div>
  )
}

// ── ExplorerSpine ────────────────────────────────────────────────────────────
function ExplorerSpine({
  stages,
  activeStageId,
  stageLog,
  onSelect,
}: {
  stages: StageData[]
  activeStageId: string
  stageLog: StageLogEntry[]
  onSelect: (id: string) => void
}) {
  return (
    <div style={{ position: "sticky", top: 0, zIndex: 30, background: s.bg, borderBottom: `1px solid ${s.border}`, padding: "1rem 1.5rem" }}>
      <div style={{ position: "relative", display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div style={{ position: "absolute", left: "5%", right: "5%", top: 9, height: 1, background: s.border }} />
        {stages.map(stage => {
          const isActive = activeStageId === stage.id
          const isComplete = stageLog.some(e => e.stageId === stage.id)
          return (
            <button
              key={stage.id}
              onClick={() => onSelect(stage.id)}
              style={{
                position: "relative", display: "flex", flexDirection: "column", alignItems: "center",
                background: "none", border: "none", cursor: "pointer", width: `${100 / stages.length}%`, zIndex: 1,
              }}
            >
              <div style={{
                width: 18, height: 18, borderRadius: "50%", marginBottom: 8,
                background: isComplete ? s.green : isActive ? s.text : s.bg,
                border: `2px solid ${isComplete ? s.green : isActive ? s.text : s.border}`,
                boxShadow: isActive ? `0 0 0 3px ${s.text}22` : "none",
                transition: "all 0.15s",
              }} />
              <span style={{ fontSize: "0.65rem", fontFamily: "monospace", fontWeight: isActive ? 700 : 400, color: isActive ? s.text : s.muted, textAlign: "center" }}>
                {stage.spineLabel}
              </span>
            </button>
          )
        })}
      </div>
    </div>
  )
}

// ── Mode selector ────────────────────────────────────────────────────────────
function ModeSelector({
  receiptId,
  onGenerate,
  generating,
  hasEntity,
}: {
  receiptId: string
  onGenerate: (mode: string, entityOverride?: string) => void
  generating: boolean
  hasEntity: boolean
}) {
  const router = useRouter()
  const [selected, setSelected] = useState<string | null>(null)
  const [entityInput, setEntityInput] = useState("")

  const modes = [
    { id: "RECON", label: "Recon", time: "5 min", color: s.cyan, description: "Quick orientation. 1 stage, minimal artifact. For fast context before a conversation." },
    { id: "ACTIVE", label: "Active", time: "20 min", color: s.gold, description: "Full prep sequence. 2 stages, agenda plus KYC lens. For structured meeting prep." },
    { id: "LEAD", label: "Lead", time: "60 min", color: s.gold, description: "Deep intelligence build. 3 to 5 stages, full artifact suite. For high-stakes first contact." },
  ]

  return (
    <div style={{ minHeight: "100vh", background: s.bg, padding: "2rem 1.5rem", fontFamily: "system-ui, sans-serif" }}>
      <div style={{ maxWidth: 680, margin: "0 auto" }}>
        <div style={{ marginBottom: "0.5rem" }}>
          <button
            onClick={() => router.push(`/brief/${receiptId}`)}
            style={{ background: "none", border: "none", color: s.muted, fontSize: "0.75rem", cursor: "pointer", padding: 0 }}
          >
            ← Brief
          </button>
        </div>
        <div style={{ marginBottom: "2rem" }}>
          <div style={{ fontSize: "0.6rem", color: s.arcs, letterSpacing: "0.15em", textTransform: "uppercase", marginBottom: "0.5rem" }}>ARCS FIELD OS</div>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 700, color: s.text, margin: 0 }}>Generate Prep Guide</h1>
          <p style={{ fontSize: "0.875rem", color: s.muted, marginTop: "0.5rem" }}>Select your prep mode to generate a field guide for this interaction.</p>
        </div>

        {!hasEntity && (
          <div style={{ marginBottom: "1.25rem" }}>
            <label style={{ display: "block", fontSize: "0.65rem", color: s.muted, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: "0.375rem" }}>
              Who are you preparing for?
            </label>
            <input
              value={entityInput}
              onChange={e => setEntityInput(e.target.value)}
              placeholder="e.g. Marcus Chen, VP Sales"
              style={{
                width: "100%", padding: "0.625rem 0.75rem", borderRadius: 7,
                background: s.surface, border: `1px solid ${s.border}`, outline: "none",
                color: s.text, fontSize: "0.875rem",
              }}
            />
          </div>
        )}

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "1rem", marginBottom: "1.5rem" }}>
          {modes.map(m => (
            <button
              key={m.id}
              onClick={() => setSelected(m.id)}
              style={{
                padding: "1.25rem", borderRadius: 10, textAlign: "left", cursor: "pointer",
                background: selected === m.id ? `${m.color}08` : s.surface,
                border: `2px solid ${selected === m.id ? m.color : s.border}`,
                transition: "all 0.15s",
              }}
            >
              <div style={{ fontSize: "1.25rem", fontWeight: 700, color: m.color, marginBottom: "0.25rem" }}>{m.label}</div>
              <div style={{
                display: "inline-block", fontSize: "0.65rem", fontWeight: 600, padding: "0.15rem 0.5rem",
                borderRadius: 4, background: `${m.color}15`, color: m.color, marginBottom: "0.625rem",
              }}>
                {m.time}
              </div>
              <div style={{ fontSize: "0.8rem", color: s.muted, lineHeight: 1.5 }}>{m.description}</div>
            </button>
          ))}
        </div>

        {selected && (
          <button
            onClick={() => onGenerate(selected, entityInput || undefined)}
            disabled={generating}
            style={{
              width: "100%", padding: "0.75rem", borderRadius: 8, border: "none",
              background: generating ? s.border : s.text, color: generating ? s.muted : s.bg,
              fontSize: "0.875rem", fontWeight: 600, cursor: generating ? "not-allowed" : "pointer",
            }}
          >
            {generating ? "Generating your field guide…" : `Generate ${selected.charAt(0) + selected.slice(1).toLowerCase()} Guide →`}
          </button>
        )}
      </div>
    </div>
  )
}

// ── DensityToggle ─────────────────────────────────────────────────────────────
function DensityToggle({ density, onChange }: { density: Density; onChange: (d: Density) => void }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "0.375rem" }}>
      {DENSITY_LEVELS.map(d => {
        const active = density === d.level
        return (
          <button
            key={d.level}
            onClick={() => onChange(d.level)}
            title={`${d.label}: ${d.time}`}
            style={{
              padding: "0.2rem 0.5rem", borderRadius: 4, border: `1px solid`,
              borderColor: active ? d.color : s.border,
              background: active ? `${d.color}15` : "transparent",
              color: active ? d.color : s.muted,
              fontSize: "0.6rem", fontWeight: active ? 700 : 400,
              cursor: "pointer", letterSpacing: "0.04em", transition: "all 0.12s",
              lineHeight: 1.4,
            }}
          >
            {d.label}
            <span style={{ display: "block", fontSize: "0.5rem", color: active ? d.color : s.dimmed, opacity: 0.8 }}>{d.time}</span>
          </button>
        )
      })}
    </div>
  )
}

// ── DecideHeader ─────────────────────────────────────────────────────────────
function DecideHeader({
  stage,
  stageLog,
  onOpenLog,
  density,
}: {
  stage: StageData
  stageLog: StageLogEntry[]
  density: Density
  onOpenLog: () => void
}) {
  const [open, setOpen] = useState(true)
  const isComplete = stageLog.some(e => e.stageId === stage.id)

  // Executive (density=1): title + question compass only, no right col, no sub-sections
  // Strategic (density=2): + testingAboutThem right col
  // Operational (density=3): + stageJTBD + yes/no ladder
  // Tactical (density=4): + tripwire
  // Surgical (density=5): everything

  return (
    <div style={{ border: `1px solid ${s.border}`, borderRadius: 10, overflow: "hidden", marginBottom: "1rem" }}>
      <button
        onClick={() => setOpen(o => !o)}
        style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0.75rem 1rem", background: s.surface, border: "none", cursor: "pointer" }}
      >
        <span style={{ fontSize: "0.65rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", color: s.text }}>
          {stage.id}: {stage.title}
        </span>
        <span style={{ fontSize: "0.75rem", color: s.dimmed }}>{open ? "▲" : "▼"}</span>
      </button>

      {open && (
        <div style={{ padding: "1rem" }}>
          {/* Always show: question compass */}
          <div style={{ marginBottom: density >= 2 ? "1rem" : 0 }}>
            <div style={{ fontSize: "0.6rem", color: s.arcs, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: "0.375rem" }}>
              ◎ Question Compass
            </div>
            <div style={{ fontSize: "0.95rem", fontWeight: 700, color: s.text, lineHeight: 1.4 }}>{stage.questionCompass}</div>
          </div>

          {/* Strategic+: two-column layout */}
          {density >= 2 && (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
              {/* Left col */}
              <div style={{ display: "flex", flexDirection: "column", gap: "0.875rem" }}>
                {/* Operational+: stage JTBD */}
                {density >= 3 && (
                  <div>
                    <div style={{ fontSize: "0.6rem", color: s.muted, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: "0.375rem" }}>
                      ⊕ Stage JTBD
                    </div>
                    <div style={{ fontSize: "0.82rem", color: s.muted, lineHeight: 1.5 }}>{stage.stageJTBD}</div>
                  </div>
                )}
                {/* Operational+: yes/no ladder */}
                {density >= 3 && (
                  <div style={{ border: `1px solid ${s.border}`, borderRadius: 6, overflow: "hidden" }}>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr" }}>
                      <div style={{ padding: "0.5rem 0.75rem", borderRight: `1px solid ${s.border}`, borderBottom: `1px solid ${s.border}` }}>
                        <div style={{ fontSize: "0.6rem", color: s.green, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "0.25rem" }}>Yes →</div>
                        <div style={{ fontSize: "0.75rem", color: s.text, lineHeight: 1.4 }}>{stage.writesIntoNextTable.yes}</div>
                      </div>
                      <div style={{ padding: "0.5rem 0.75rem", borderBottom: `1px solid ${s.border}` }}>
                        <div style={{ fontSize: "0.6rem", color: s.red, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "0.25rem" }}>No →</div>
                        <div style={{ fontSize: "0.75rem", color: s.text, lineHeight: 1.4 }}>{stage.writesIntoNextTable.no}</div>
                      </div>
                    </div>
                    <button
                      onClick={onOpenLog}
                      style={{
                        width: "100%", padding: "0.5rem", border: "none", borderTop: `1px solid ${s.border}`,
                        background: isComplete ? `${s.green}10` : s.surface, color: isComplete ? s.green : s.muted,
                        fontSize: "0.7rem", fontWeight: 600, cursor: "pointer", letterSpacing: "0.04em",
                      }}
                    >
                      {isComplete ? "✓ Logged" : "After this stage →"}
                    </button>
                  </div>
                )}
              </div>

              {/* Right col */}
              <div style={{ display: "flex", flexDirection: "column", gap: "0.875rem" }}>
                {/* Strategic+: testing about them */}
                <div>
                  <div style={{ fontSize: "0.6rem", color: s.muted, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: "0.375rem" }}>
                    ◉ Testing About Them
                  </div>
                  <div style={{ fontSize: "0.82rem", color: s.text, lineHeight: 1.5 }}>{stage.testingAboutThem}</div>
                </div>

                {/* Tactical+: tripwire */}
                {density >= 4 && (
                  <div style={{ background: `${s.gold}0d`, border: `1px solid ${s.gold}33`, borderRadius: 6, padding: "0.625rem 0.75rem" }}>
                    <div style={{ fontSize: "0.6rem", color: s.gold, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: "0.25rem" }}>⚠ Where this goes sideways</div>
                    <div style={{ fontSize: "0.8rem", color: s.text, lineHeight: 1.5 }}>{stage.midcurveTripwire}</div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Executive: inline log button (no two-col layout) */}
          {density === 1 && (
            <div style={{ marginTop: "0.75rem" }}>
              <button
                onClick={onOpenLog}
                style={{
                  padding: "0.35rem 0.875rem", border: `1px solid ${s.border}`, borderRadius: 5,
                  background: isComplete ? `${s.green}10` : "transparent", color: isComplete ? s.green : s.muted,
                  fontSize: "0.7rem", fontWeight: 600, cursor: "pointer",
                }}
              >
                {isComplete ? "✓ Logged" : "After this stage →"}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ── Main Page ────────────────────────────────────────────────────────────────
export default function GuidePage() {
  const params = useParams()
  const router = useRouter()
  const receiptId = params.receiptId as string

  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [guide, setGuide] = useState<GuideData | null>(null)
  const [entity, setEntity] = useState<string | null>(null)
  const [decision, setDecision] = useState<string>("")
  const [stages, setStages] = useState<StageData[]>([])
  const [stageLog, setStageLog] = useState<StageLogEntry[]>([])
  const [activeStageId, setActiveStageId] = useState<string>("")
  const [betLabel, setBetLabel] = useState("")
  const [outcomeStatement, setOutcomeStatement] = useState("")
  const [leadingIndicator, setLeadingIndicator] = useState("")
  const [kpiLabel, setKpiLabel] = useState("")
  const [failureSignal, setFailureSignal] = useState("")

  // Density — persisted to localStorage, default Operational (3)
  const [density, setDensity] = useState<Density>(3)
  useEffect(() => {
    const saved = localStorage.getItem(DENSITY_KEY)
    if (saved && ["1","2","3","4","5"].includes(saved)) setDensity(Number(saved) as Density)
  }, [])
  function changeDensity(d: Density) {
    setDensity(d)
    localStorage.setItem(DENSITY_KEY, String(d))
  }

  // Band open states — collapse lower-priority bands at low density
  const [agendaOpen, setAgendaOpen] = useState(true)
  const [preWorkOpen, setPreWorkOpen] = useState(true)
  const [kycOpen, setKycOpen] = useState(true)
  const [artifactsOpen, setArtifactsOpen] = useState(true)

  // Modals
  const [artifactModal, setArtifactModal] = useState<Artifact | null>(null)
  const [logModalOpen, setLogModalOpen] = useState(false)

  const loadGuide = useCallback(async () => {
    const res = await fetch(`/api/guide/${receiptId}`)
    const data = await res.json()
    if (data.ok && data.guide) {
      applyGuide(data.guide, data.entity, data.decision)
    }
    setLoading(false)
  }, [receiptId])

  useEffect(() => { loadGuide() }, [loadGuide])

  function applyGuide(g: GuideData, ent: string | null, dec: string) {
    setGuide(g)
    setEntity(ent)
    setDecision(dec)
    setBetLabel(g.betLabel)
    setOutcomeStatement(g.outcomeStatement ?? "")
    setLeadingIndicator(g.leadingIndicator ?? "")
    setKpiLabel(g.kpiLabel ?? "")
    setFailureSignal(g.failureSignal ?? "")
    const parsed: StageData[] = JSON.parse(g.stages)
    setStages(parsed)
    const log: StageLogEntry[] = JSON.parse(g.stageLog)
    setStageLog(log)
    if (parsed.length > 0) setActiveStageId(parsed[0].id)
  }

  async function generateGuide(mode: string, entityOverride?: string) {
    setGenerating(true)
    try {
      const res = await fetch(`/api/guide/${receiptId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode, entityOverride }),
      })
      const data = await res.json()
      if (data.ok && data.guide) {
        applyGuide(data.guide, data.entity, data.decision)
      }
    } finally {
      setGenerating(false)
    }
  }

  async function logStage(stageId: string, verdict: string, vibe?: string, indicatorObserved?: boolean) {
    const entry = { stageId, completedAt: new Date().toISOString(), verdict, vibe }
    await fetch(`/api/guide/${receiptId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(entry),
    })
    setStageLog(prev => [...prev.filter(e => e.stageId !== stageId), entry])
    setLogModalOpen(false)
  }

  const activeStage = stages.find(s => s.id === activeStageId) ?? null
  const modeColor = guide?.mode === "RECON" ? s.cyan : guide?.mode === "ACTIVE" ? s.gold : s.green

  if (loading) {
    return (
      <div style={{ minHeight: "100vh", background: s.bg, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ fontSize: "0.75rem", color: s.muted, letterSpacing: "0.1em" }}>Loading…</div>
      </div>
    )
  }

  if (!guide && !generating) {
    return <ModeSelector receiptId={receiptId} onGenerate={generateGuide} generating={generating} hasEntity={!!entity} />
  }

  if (generating) {
    return (
      <div style={{ minHeight: "100vh", background: s.bg, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: "1rem" }}>
        <div style={{ fontSize: "0.6rem", color: s.arcs, letterSpacing: "0.15em", textTransform: "uppercase" }}>ARCS FIELD OS</div>
        <div style={{ fontSize: "1rem", fontWeight: 600, color: s.text }}>Generating your field guide…</div>
        <div style={{ fontSize: "0.8rem", color: s.muted }}>Building staged intelligence for {entity ?? "this interaction"}</div>
      </div>
    )
  }

  if (!guide || !activeStage) return null

  return (
    <div style={{ minHeight: "100vh", background: s.bg, fontFamily: "system-ui, sans-serif" }}>
      {/* Header bar */}
      <div style={{ borderBottom: `1px solid ${s.border}`, padding: "0.625rem 1.5rem", display: "flex", alignItems: "center", justifyContent: "space-between", background: s.bg }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.75rem" }}>
          <span style={{ color: s.arcs, fontSize: "0.6rem", fontWeight: 700, letterSpacing: "0.15em", textTransform: "uppercase" }}>ARCS FIELD OS</span>
          <span style={{ color: s.border }}>|</span>
          <span style={{ color: s.muted }}>Field Guide</span>
          <span style={{ color: s.border }}>|</span>
          <span style={{ color: s.text, fontWeight: 600 }}>{guide.guideTitle}</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.875rem" }}>
          <DensityToggle density={density} onChange={changeDensity} />
          <span style={{
            fontSize: "0.6rem", fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase",
            padding: "0.2rem 0.6rem", borderRadius: 4, background: `${modeColor}15`, color: modeColor, border: `1px solid ${modeColor}44`,
          }}>
            {guide.mode}
          </span>
          <button
            onClick={() => router.push(`/brief/${receiptId}`)}
            style={{ background: "none", border: `1px solid ${s.border}`, color: s.muted, fontSize: "0.7rem", padding: "0.25rem 0.625rem", borderRadius: 5, cursor: "pointer" }}
          >
            ← Brief
          </button>
        </div>
      </div>

      {/* Eyebrow bar */}
      <div style={{ background: s.surface, borderBottom: `1px solid ${s.border}`, padding: "0.5rem 1.5rem", display: "flex", alignItems: "center", gap: "1.5rem", fontSize: "0.7rem" }}>
        <span style={{ color: s.muted }}>Bet:</span>
        <input
          value={betLabel}
          onChange={e => setBetLabel(e.target.value)}
          style={{ background: "transparent", border: "none", outline: "none", color: s.text, fontWeight: 600, fontSize: "0.7rem", minWidth: 120 }}
        />
        <span style={{ color: s.border }}>|</span>
        <span style={{ color: s.muted }}>Prep:</span>
        <span style={{ color: s.text, fontWeight: 600 }}>{guide.totalPrepHours} hrs</span>
        <span style={{ color: s.border }}>|</span>
        <span style={{ color: s.muted }}>Stage:</span>
        <span style={{ color: s.text, fontWeight: 600 }}>{activeStage.id}: {activeStage.shortLabel}</span>
      </div>

      {/* Outcome Target Card — pinned between eyebrow and spine */}
      <div style={{ padding: "0.5rem 1.5rem", background: s.bg, borderBottom: `1px solid ${s.border}` }}>
        <OutcomeTargetCard
          outcomeStatement={outcomeStatement}
          leadingIndicator={leadingIndicator}
          kpiLabel={kpiLabel}
          failureSignal={failureSignal}
          onChangeOutcome={setOutcomeStatement}
          onChangeLeading={setLeadingIndicator}
          onChangeKpi={setKpiLabel}
          onChangeFailure={setFailureSignal}
        />
      </div>

      {/* ExplorerSpine */}
      <ExplorerSpine
        stages={stages}
        activeStageId={activeStageId}
        stageLog={stageLog}
        onSelect={setActiveStageId}
      />

      {/* Main content */}
      <div style={{ maxWidth: 900, margin: "0 auto", padding: "1.5rem" }}>
        <DecideHeader stage={activeStage} stageLog={stageLog} onOpenLog={() => setLogModalOpen(true)} density={density} />

        {/* Agenda — Operational+ */}
        {density >= 3 && (
        <CollapsibleBand title="Agenda" isOpen={agendaOpen} onToggle={() => setAgendaOpen(o => !o)} accentColor={s.cyan}>
          <ul style={{ margin: 0, paddingLeft: "1.25rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            {activeStage.agenda.map((item, i) => (
              <li key={i} style={{ fontSize: "0.85rem", color: s.text, lineHeight: 1.5 }}>{item}</li>
            ))}
          </ul>
        </CollapsibleBand>
        )}

        {/* Pre-Work — Tactical+ */}
        {density >= 4 && (
        <CollapsibleBand title="Pre-Work" isOpen={preWorkOpen} onToggle={() => setPreWorkOpen(o => !o)} accentColor={s.gold}>
          <ul style={{ margin: 0, paddingLeft: "1.25rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            {activeStage.preWork.map((item, i) => (
              <li key={i} style={{ fontSize: "0.85rem", color: s.text, lineHeight: 1.5 }}>{item}</li>
            ))}
          </ul>
        </CollapsibleBand>
        )}

        {/* KYC Lens — Surgical only */}
        {density >= 5 && (
        <CollapsibleBand title="KYC / KYT / KYB / KYI" isOpen={kycOpen} onToggle={() => setKycOpen(o => !o)} accentColor={s.green}>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.375rem" }}>
            {activeStage.kycLens.map((item, i) => {
              const prefix = item.match(/^(KYC|KYT|KYB|KYI):/)?.[1]
              const rest = item.replace(/^(KYC|KYT|KYB|KYI):/, "").trim()
              const pColor = prefix === "KYC" ? s.cyan : prefix === "KYT" ? s.green : prefix === "KYB" ? s.gold : s.red
              return (
                <div key={i} style={{ display: "flex", gap: "0.5rem", alignItems: "flex-start", fontFamily: "monospace" }}>
                  {prefix && (
                    <span style={{ fontSize: "0.65rem", fontWeight: 700, color: pColor, minWidth: 32, paddingTop: 2 }}>{prefix}</span>
                  )}
                  <span style={{ fontSize: "0.8rem", color: s.text, lineHeight: 1.5 }}>{rest}</span>
                </div>
              )
            })}
          </div>
        </CollapsibleBand>
        )}

        {/* Artifacts — Tactical+ */}
        {density >= 4 && (
        <CollapsibleBand title="Minimum-Viable Artifacts" isOpen={artifactsOpen} onToggle={() => setArtifactsOpen(o => !o)} accentColor={s.gold}>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            {activeStage.artifacts.map((artifact, i) => (
              <button
                key={i}
                onClick={() => setArtifactModal(artifact)}
                style={{
                  display: "flex", alignItems: "center", gap: "0.75rem", padding: "0.625rem 0.875rem",
                  border: `1px solid ${s.border}`, borderRadius: 6, background: s.surface,
                  cursor: "pointer", textAlign: "left", transition: "border-color 0.1s",
                }}
              >
                <span style={{ fontSize: "0.8rem", color: s.gold }}>◈</span>
                <div>
                  <div style={{ fontSize: "0.82rem", fontWeight: 600, color: s.text }}>{artifact.title}</div>
                  <div style={{ fontSize: "0.72rem", color: s.muted }}>{artifact.abstract}</div>
                </div>
              </button>
            ))}
          </div>
        </CollapsibleBand>
        )}

        {/* Decision context footer */}
        <div style={{ marginTop: "1.5rem", padding: "0.875rem 1rem", background: s.surface, border: `1px solid ${s.border}`, borderRadius: 8 }}>
          <div style={{ fontSize: "0.6rem", color: s.muted, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "0.375rem" }}>Decision Context</div>
          <div style={{ fontSize: "0.8rem", color: s.text, lineHeight: 1.5 }}>{decision}</div>
        </div>
      </div>

      {/* Modals */}
      {artifactModal && <ArtifactModal artifact={artifactModal} onClose={() => setArtifactModal(null)} />}
      {logModalOpen && (
        <PostCallLogModal
          stage={activeStage}
          onClose={() => setLogModalOpen(false)}
          onLog={(verdict, vibe, indicatorObserved) => logStage(activeStageId, verdict, vibe, indicatorObserved)}
        />
      )}
    </div>
  )
}
