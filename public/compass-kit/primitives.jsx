// ARCS Compass — UI kit primitives
// Cockpit/instrument-grade tokens + atoms, lifted from arcs-v9 src/ui/tokens.ts.
// Inline styles only — matches the product's no-CSS-framework convention.

const T = {
  bg: "#020408", surface: "#0d1117", elevated: "#111827",
  border: "#1e293b",
  fg1: "#e2e8f0", fg2: "#94a3b8", fg3: "#64748b", fg4: "#475569",
  cyan: "#00F0FF", green: "#00FF9D", gold: "#FFD700", orange: "#ff9d3c",
  red: "#FF4D6D", steel: "#94a3b8", violet: "#A78BFA", magenta: "#E879F9",
  sans: "'Inter', system-ui, -apple-system, sans-serif",
  mono: "'JetBrains Mono', 'IBM Plex Mono', ui-monospace, monospace",
};

// Y-state → weather reading (from dashboard Y_WEATHER)
const Y_WEATHER = {
  GREEN:   { label: "CLARITY RIDGE",         icon: "▲", color: T.green },
  YELLOW:  { label: "PRESSURE BAND",         icon: "◈", color: T.gold },
  FORK:    { label: "FORK · PATH SELECTION", icon: "⊕", color: T.cyan },
  SCRATCH: { label: "FOG LAYER · ORIENT",    icon: "~", color: T.fg4 },
  DELTA:   { label: "CONVICTION SHIFT",      icon: "△", color: T.violet },
  PARADOX: { label: "PARADOX · CURATOR",     icon: "∞", color: T.magenta },
  LOCKED:  { label: "KAIROS LOCK · LOCKED",  icon: "◆", color: T.cyan },
};

const RES_STYLE = {
  SHARP:    { opacity: 1.0,  fontWeight: 500, letterSpacing: "0" },
  DEGRADED: { opacity: 0.85, fontWeight: 400, letterSpacing: "0.01em" },
  GRAIN:    { opacity: 0.70, fontWeight: 300, letterSpacing: "0.02em" },
  MOIRE:    { opacity: 0.60, fontWeight: 300, letterSpacing: "0.03em" },
};

const nciColor = (s) => s >= 70 ? T.green : s >= 45 ? T.gold : T.red;

// ─── Wordmark ────────────────────────────────────────────────────────────────
function Wordmark({ section }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
      <span style={{ fontFamily: T.mono, fontSize: "0.65rem", letterSpacing: "0.15em", color: T.cyan, textTransform: "uppercase", fontWeight: 700, whiteSpace: "nowrap" }}>
        ARCS <span style={{ color: T.fg2, fontWeight: 500 }}>FIELD OS</span>
      </span>
      {section && <>
        <span style={{ width: 1, height: 12, background: T.border }} />
        <span style={{ fontFamily: T.mono, fontSize: "0.65rem", letterSpacing: "0.12em", color: T.fg4, textTransform: "uppercase" }}>{section}</span>
      </>}
    </div>
  );
}

// ─── Instrument label ──────────────────────────────────────────────────────────
function Label({ children, color, style }) {
  return (
    <div style={{ fontFamily: T.mono, fontSize: "0.65rem", letterSpacing: "0.12em", textTransform: "uppercase", color: color || T.fg4, fontWeight: 700, ...style }}>
      {children}
    </div>
  );
}

// ─── Button ──────────────────────────────────────────────────────────────────
// Cards × Badges fusion: semi-opaque dark-glass body + subtle emboss bevel; the
// gate color lives only in the accents (rim, glyph, label tint, a whisper of
// bloom). No saturated fills. Optional leading `glyph`.
// hover border (bdH) runs hotter than rest — same hue, more saturation/brightness
const BTN_ACCENT = {
  primary:        { ink: "#b9e8f4", bd: "#00F0FF3a", bdH: "#00F0FF99", sig: "#00F0FF", bloom: "#00F0FF12", bloomH: "#00F0FF2b" },
  "outline-cyan": { ink: "#b9e8f4", bd: "#00F0FF3a", bdH: "#00F0FF99", sig: "#00F0FF", bloom: "#00F0FF12", bloomH: "#00F0FF2b" },
  green:          { ink: "#bdf2dc", bd: "#00FF9D3a", bdH: "#00FF9D99", sig: "#00FF9D", bloom: "#00FF9D12", bloomH: "#00FF9D2b" },
  gold:           { ink: "#f0e4ba", bd: "#FFD7003a", bdH: "#FFD70099", sig: "#FFD700", bloom: "#FFD70010", bloomH: "#FFD70026" },
  danger:         { ink: "#f6c9d2", bd: "#FF4D6D3a", bdH: "#FF4D6D99", sig: "#FF6B85", bloom: "#FF4D6D12", bloomH: "#FF4D6D2b" },
  ghost:          { ink: "#cbd5e1", bd: "#2a3647",   bdH: "#566b86",   sig: "#94a3b8", bloom: "transparent", bloomH: "rgba(0,0,0,.01)" },
};
const GLASS_BODY = "linear-gradient(160deg, rgba(255,255,255,.06), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, #141c24, #0b1117)";

function Button({ variant = "primary", size = "md", glyph, disabled, children, style, ...rest }) {
  const [h, setH] = React.useState(false);
  const [p, setP] = React.useState(false);
  const a = BTN_ACCENT[variant] || BTN_ACCENT.primary;
  const sz = size === "lg" ? { fontSize: 12, padding: "13px 23px", borderRadius: 6 }
    : size === "sm" ? { fontSize: 10, padding: "7px 12px", borderRadius: 4 }
    : { fontSize: 11, padding: "10px 16px", borderRadius: 5 };
  const base = `inset 0 1px 0 rgba(255,255,255,.09), inset 0 -2px 7px rgba(0,0,0,.5), 0 0 14px ${a.bloom}, 0 4px 12px rgba(0,0,0,.4)`;
  const hover = `inset 0 1px 0 rgba(255,255,255,.12), inset 0 -2px 7px rgba(0,0,0,.45), 0 0 20px ${a.bloomH}, 0 6px 16px rgba(0,0,0,.5)`;
  const press = `inset 0 2px 6px rgba(0,0,0,.6), inset 0 1px 0 rgba(255,255,255,.05), 0 0 10px ${a.bloom}`;
  const lit = !disabled && (h || p);
  return (
    <button disabled={disabled}
      onMouseEnter={() => setH(true)} onMouseLeave={() => { setH(false); setP(false); }}
      onMouseDown={() => setP(true)} onMouseUp={() => setP(false)}
      style={{
        position: "relative", display: "inline-flex", alignItems: "center", justifyContent: "center", gap: "0.5em",
        fontFamily: T.mono, fontWeight: 600, letterSpacing: "0.085em", textTransform: "uppercase", lineHeight: 1, whiteSpace: "nowrap",
        color: a.ink, border: `1px solid ${lit ? a.bdH : a.bd}`, background: GLASS_BODY,
        boxShadow: disabled ? base : p ? press : h ? hover : base,
        transform: disabled ? "none" : p ? "translateY(1px)" : h ? "translateY(-1px)" : "none",
        cursor: disabled ? "not-allowed" : "pointer", opacity: disabled ? 0.42 : 1, filter: disabled ? "saturate(.55)" : "none",
        transition: "box-shadow .16s, transform .09s, border-color .16s, filter .16s", WebkitFontSmoothing: "antialiased",
        ...sz, ...style,
      }} {...rest}>
      {glyph && <span style={{ fontSize: "1.05em", lineHeight: 1, color: a.sig }}>{glyph}</span>}
      {children}
    </button>
  );
}

// ─── Badge ───────────────────────────────────────────────────────────────────
// Y-gate weather DNA: optional signal glyph + mono UPPERCASE label in a
// signal-tinted capsule. register: state (default) | governance | light.
function Badge({ label, glyph, color = T.steel, register = "state", style }) {
  const common = { display: "inline-flex", alignItems: "center", gap: 6, fontFamily: T.mono, fontWeight: 700, whiteSpace: "nowrap", lineHeight: 1, textTransform: "uppercase", color };
  const v = (register === "governance" || register === "gov")
      ? { fontSize: 11, letterSpacing: "0.12em", padding: "4px 11px", borderRadius: 7, background: `${color}1f`, border: `1px solid ${color}55` }
    : register === "light"
      ? { fontSize: 10, fontWeight: 500, letterSpacing: "0.06em", padding: "2px 9px", borderRadius: 6, background: "transparent", border: `1px solid ${color}40`, opacity: 0.92 }
    : { fontSize: 11, letterSpacing: "0.11em", padding: "6px 12px", borderRadius: 8, background: `linear-gradient(165deg, ${color}2e, ${color}0f)`, border: `1px solid ${color}45`, boxShadow: `inset 0 1px 0 rgba(255,255,255,.05), 0 0 12px ${color}26` };
  return <span style={{ ...common, ...v, ...style }}>{glyph && <span style={{ fontSize: "1.05em", lineHeight: 1 }}>{glyph}</span>}{label}</span>;
}

// ─── Card ────────────────────────────────────────────────────────────────────
// accent → signal glass with an underlit-LED finish (tight glow + inset
// bottom-up bloom); default → neutral semi-opaque glass with a subtle bevel.
function Card({ accent, children, style }) {
  const glass = accent ? {
      border: `1px solid ${accent}45`,
      background: `linear-gradient(160deg, rgba(255,255,255,.06), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, ${accent}1c, #0a1620)`,
      boxShadow: `inset 0 1px 0 ${accent}80, inset 0 -11px 17px -11px ${accent}55, 0 0 12px ${accent}26, 0 5px 16px rgba(0,0,0,.5)`,
    } : {
      border: `1px solid #243042`,
      background: "linear-gradient(160deg, rgba(255,255,255,.05), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, #11181f, #0a1016)",
      boxShadow: "inset 0 1px 0 rgba(255,255,255,.10), inset 0 -2px 8px rgba(0,0,0,.5), 0 5px 16px rgba(0,0,0,.45)",
    };
  return (
    <div style={{ borderRadius: 4, padding: "1.25rem 1.5rem", ...glass, ...style }}>
      {children}
    </div>
  );
}

// ─── Gauge ───────────────────────────────────────────────────────────────────
// Instrument readout: raised glass bezel around a recessed optical "screen".
// The signature ARCS hardware tile (NCI / Coherence / Satoshi). Pass `accent`
// for a signal-tinted bezel; `children` to fill the body (e.g. macro-tag pills).
function Gauge({ label, value, sub, color = "#cdd7e3", glow = "rgba(160,180,210,.35)", accent, valueSize = 33, flex = 1, minWidth = 120, children, style }) {
  const bezel = accent ? {
      border: `1px solid ${accent}40`,
      boxShadow: `inset 0 1px 0 ${accent}73, inset 0 -2px 6px rgba(0,0,0,.55), 0 0 14px ${accent}2e, 0 5px 14px rgba(0,0,0,.5)`,
    } : {
      border: "1px solid #2a3647",
      boxShadow: "inset 0 1px 0 rgba(255,255,255,.14), inset 0 -2px 6px rgba(0,0,0,.55), inset 0 0 0 1px rgba(255,255,255,.02), 0 5px 14px rgba(0,0,0,.5)",
    };
  return (
    <div style={{ position: "relative", flex, minWidth, padding: "15px 16px 14px", borderRadius: 6, overflow: "hidden",
      background: "linear-gradient(160deg, rgba(255,255,255,.06), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, #131b23, #0a1016)",
      ...bezel, ...style }}>
      <div style={{ position: "absolute", inset: "0 0 auto 0", height: "40%", background: "linear-gradient(rgba(255,255,255,.06), rgba(255,255,255,0))", pointerEvents: "none" }} />
      <div style={{ position: "relative", fontFamily: T.mono, fontSize: 10, color: accent || T.fg4, letterSpacing: ".1em", textTransform: "uppercase", fontWeight: 700 }}>{label}</div>
      {value !== undefined && value !== null && (
        <div style={{ position: "relative", marginTop: 4, borderRadius: 8, padding: "4px 2px",
          boxShadow: "inset 0 2px 5px rgba(0,0,0,.6), inset 0 -1px 0 rgba(255,255,255,.05)" }}>
          <div style={{ position: "relative", fontSize: valueSize, fontWeight: 700, lineHeight: 1, color, textShadow: `0 0 16px ${glow}` }}>{value}</div>
        </div>
      )}
      {sub && <div style={{ position: "relative", fontSize: 11, color: T.fg4, marginTop: 4 }}>{sub}</div>}
      {children}
    </div>
  );
}

// glow tint for a signal color (used by stat readouts)
const signalGlow = (c) => c === T.green ? "rgba(0,255,157,.6)" : c === T.gold ? "rgba(255,215,0,.55)"
  : c === T.red ? "rgba(255,77,109,.55)" : c === T.cyan ? "rgba(0,240,255,.55)" : "rgba(160,180,210,.35)";

Object.assign(window, { T, Y_WEATHER, RES_STYLE, nciColor, signalGlow, Wordmark, Label, Button, Badge, Card, Gauge });
