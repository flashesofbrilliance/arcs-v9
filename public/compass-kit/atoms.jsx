// ARCS Compass — composite atoms built on the updated design language.
// Dark semi-opaque glass + subtle bevel (cards), signal only in the accents
// (badges), recessed optical screens for inputs (gauges / True North),
// underlit-LED glow (never ambient neon). Loaded after primitives.jsx.

const { useState } = React;

// ─── Swiss scaffolding ───────────────────────────────────────────────────────
function SectionLabel({ index, children, color = T.fg4, style }) {
  return (
    <div style={{ display: "flex", alignItems: "baseline", gap: 10, ...style }}>
      {index && <span style={{ fontFamily: T.mono, fontSize: 10, fontWeight: 700, color: T.cyan, letterSpacing: "0.1em" }}>{index}</span>}
      <span style={{ fontFamily: T.mono, fontSize: 10, fontWeight: 700, letterSpacing: "0.14em", textTransform: "uppercase", color }}>{children}</span>
    </div>
  );
}
function Rule({ style }) { return <div style={{ height: 1, background: T.border, ...style }} />; }

// ─── Field — instrument input module (bezel + recessed screen + cyan focus) ───
function Field({ label, as = "input", value, onChange, placeholder, rows, children, style, fieldStyle }) {
  const [f, setF] = useState(false);
  const isSelect = as === "select";
  const glow = f && !isSelect; // horizon (select) gets a clean focus line, no glow
  const well = {
    width: "100%", boxSizing: "border-box", color: T.fg1, fontSize: 14, padding: "10px 12px", outline: "none", fontFamily: T.sans,
    borderRadius: 5, border: `1px solid ${f ? (isSelect ? "#3a4a5e" : "#00F0FF66") : "#1c2736"}`,
    background: "linear-gradient(180deg, #090d12, #0c1219)",
    boxShadow: glow ? "inset 0 2px 5px rgba(0,0,0,.55), inset 0 -9px 14px -9px rgba(0,240,255,.34), 0 0 0 1px #00F0FF3a"
                 : "inset 0 2px 5px rgba(0,0,0,.65), inset 0 -1px 0 rgba(255,255,255,.04)",
    transition: "box-shadow .16s, border-color .16s",
    resize: as === "textarea" ? "vertical" : undefined, lineHeight: as === "textarea" ? 1.6 : undefined,
    ...fieldStyle,
  };
  const common = { value, onChange, placeholder, onFocus: () => setF(true), onBlur: () => setF(false), style: well };
  return (
    <div style={{ position: "relative", borderRadius: 6, padding: "12px 14px 13px", overflow: "hidden",
      border: "1px solid #2a3647",
      background: "linear-gradient(160deg, rgba(255,255,255,.06), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, #131b23, #0a1016)",
      boxShadow: "inset 0 1px 0 rgba(255,255,255,.14), inset 0 -2px 6px rgba(0,0,0,.55), 0 5px 14px rgba(0,0,0,.5)", ...style }}>
      <div style={{ position: "absolute", inset: "0 0 auto 0", height: "34%", background: "linear-gradient(rgba(255,255,255,.05), rgba(255,255,255,0))", pointerEvents: "none" }} />
      {label && <span style={{ position: "relative", display: "block", fontFamily: T.mono, fontSize: 11, color: T.fg2, textTransform: "uppercase", letterSpacing: "0.1em", fontWeight: 700, marginBottom: 8 }}>{label}</span>}
      {as === "textarea" ? <textarea rows={rows || 3} {...common} />
        : as === "select" ? <select {...common}>{children}</select>
        : <input type="text" {...common} />}
    </div>
  );
}

// ─── Picker — instrument dropdown (matches the Observatory control grammar) ───
function Picker({ label, value, options, onChange, style }) {
  const [open, setOpen] = useState(false);
  const [h, setH] = useState(false);
  const ref = React.useRef(null);
  React.useEffect(() => {
    if (!open) return;
    const close = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, [open]);
  const current = options.find(o => o.value === value) || options[0];
  return (
    <div ref={ref} style={{ position: "relative", borderRadius: 6, padding: "12px 14px 13px",
      border: "1px solid #2a3647",
      background: "linear-gradient(160deg, rgba(255,255,255,.06), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, #131b23, #0a1016)",
      boxShadow: "inset 0 1px 0 rgba(255,255,255,.14), inset 0 -2px 6px rgba(0,0,0,.55), 0 5px 14px rgba(0,0,0,.5)", ...style }}>
      {label && <span style={{ display: "block", fontFamily: T.mono, fontSize: 11, color: T.fg2, textTransform: "uppercase", letterSpacing: "0.1em", fontWeight: 700, marginBottom: 8 }}>{label}</span>}
      <button type="button" onClick={() => setOpen(o => !o)} onMouseEnter={() => setH(true)} onMouseLeave={() => setH(false)}
        style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8, width: "100%", padding: "10px 12px", borderRadius: 5, cursor: "pointer",
          border: `1px solid ${open ? "#00F0FF66" : (h ? "#34435a" : "#1c2736")}`, color: T.fg1, fontFamily: T.sans, fontSize: 14,
          background: "linear-gradient(180deg, #090d12, #0c1219)",
          boxShadow: "inset 0 2px 5px rgba(0,0,0,.65), inset 0 -1px 0 rgba(255,255,255,.04)", transition: "border-color .16s" }}>
        <span>{current.label}</span>
        <span style={{ color: T.fg3, fontSize: 10, transform: open ? "rotate(180deg)" : "none", transition: "transform .2s" }}>▾</span>
      </button>
      {open && (
        <div style={{ position: "absolute", left: 14, right: 14, top: "calc(100% - 4px)", zIndex: 30, padding: 4, borderRadius: 8, overflow: "hidden",
          border: "1px solid #00F0FF44", background: "linear-gradient(180deg, #0e151e, #0a0f16)", boxShadow: "0 16px 34px -14px rgba(0,0,0,.8), inset 0 1px 0 rgba(255,255,255,.05)" }}>
          {options.map(o => {
            const sel = o.value === value;
            return (
              <button key={o.value} type="button" onClick={() => { onChange(o.value); setOpen(false); }}
                style={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%", padding: "8px 10px", borderRadius: 5, cursor: "pointer",
                  border: "1px solid transparent", textAlign: "left", fontFamily: T.sans, fontSize: 13.5,
                  color: sel ? "#b9e8f4" : T.fg1, background: sel ? "linear-gradient(180deg, #00F0FF1c, #00F0FF08)" : "transparent" }}
                onMouseEnter={e => { if (!sel) e.currentTarget.style.background = "rgba(255,255,255,.04)"; }}
                onMouseLeave={e => { if (!sel) e.currentTarget.style.background = "transparent"; }}>
                {o.label}{sel && <span style={{ color: "#00F0FF", fontSize: 10 }}>●</span>}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ─── Tabs — glass tab strip + carded panel (mirrors the Card sensibilities) ───
function Tabs({ items, value, onChange, accent = T.cyan, style }) {
  const [internal, setInternal] = useState(items[0] && items[0].value);
  const active = value !== undefined ? value : internal;
  const set = onChange || setInternal;
  const cur = items.find(i => i.value === active) || items[0];
  return (
    <div style={style}>
      <div role="tablist" style={{ display: "flex", gap: 6, marginBottom: 12, flexWrap: "wrap" }}>
        {items.map(it => {
          const on = it.value === active;
          return (
            <button key={it.value} type="button" role="tab" aria-selected={on} onClick={() => set(it.value)} style={{
              display: "inline-flex", alignItems: "center", gap: 7, padding: "8px 15px", borderRadius: 10, cursor: "pointer",
              fontFamily: T.mono, fontSize: 11, fontWeight: 700, letterSpacing: "0.085em", textTransform: "uppercase", whiteSpace: "nowrap",
              color: on ? "#eafcff" : T.fg3,
              border: `1px solid ${on ? accent + "55" : "#243042"}`,
              background: on
                ? `linear-gradient(160deg, rgba(255,255,255,.06), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, ${accent}1f, #0a1620)`
                : "linear-gradient(180deg, #0c121a, #0e151e)",
              boxShadow: on
                ? `inset 0 1px 0 ${accent}73, inset 0 -8px 13px -9px ${accent}55, 0 0 11px ${accent}24, 0 4px 12px rgba(0,0,0,.42)`
                : "inset 0 1px 0 rgba(255,255,255,.04), inset 0 2px 4px rgba(0,0,0,.5)",
              transform: on ? "translateY(-1px)" : "none", transition: "color .16s, border-color .16s, box-shadow .16s, transform .12s",
            }}>
              {it.glyph && <span style={{ fontSize: "1.05em", color: on ? accent : T.fg4 }}>{it.glyph}</span>}{it.label}
            </button>
          );
        })}
      </div>
      <Card accent={accent} style={{ animation: "fade .2s ease-out" }}>{cur && cur.content}</Card>
    </div>
  );
}

// ─── Sliding segmented control — thumb slides, signal follows position ────────
const SEG_ACCENT = {
  green: { bd: "#00FF9D55", bloom: "#00FF9D1c", bloom2: "#00FF9D33", ink: "#bdf2dc" },
  gold:  { bd: "#FFD70055", bloom: "#FFD70016", bloom2: "#FFD7002b", ink: "#f0e4ba" },
  red:   { bd: "#FF4D6D55", bloom: "#FF4D6D1c", bloom2: "#FF4D6D33", ink: "#f6c9d2" },
  cyan:  { bd: "#00F0FF55", bloom: "#00F0FF1c", bloom2: "#00F0FF2b", ink: "#b9e8f4" },
};
function SegmentedSlider({ options, value, onChange, style }) {
  const idx = Math.max(0, options.findIndex(o => o.value === value));
  const a = SEG_ACCENT[options[idx]?.accent] || SEG_ACCENT.cyan;
  return (
    <div style={{ position: "relative", display: "grid", gridTemplateColumns: `repeat(${options.length}, 1fr)`, padding: 5, borderRadius: 6,
      background: "linear-gradient(180deg, #090d12, #0c1219)",
      boxShadow: "inset 0 2px 6px rgba(0,0,0,.7), inset 0 -1px 0 rgba(255,255,255,.04)", ...style }}>
      <div style={{ position: "absolute", top: 5, bottom: 5, left: 5, width: `calc((100% - 10px) / ${options.length})`, borderRadius: 4,
        transform: `translateX(${idx * 100}%)`, transition: "transform .24s cubic-bezier(.4,0,.2,1), border-color .2s, box-shadow .2s",
        border: `1px solid ${a.bd}`,
        background: "linear-gradient(180deg, #0d141c, #0f1822)",
        boxShadow: `inset 0 2px 4px rgba(0,0,0,.5), inset 0 -7px 11px -7px ${a.bloom2}, inset 0 0 0 1px rgba(255,255,255,.03)` }} />
      {options.map((o, i) => (
        <button key={o.value} type="button" onClick={() => onChange(o.value)} style={{ position: "relative", zIndex: 1, background: "transparent", border: "none", padding: "9px 0", cursor: "pointer",
          fontFamily: T.mono, fontWeight: 700, fontSize: 12, letterSpacing: "0.05em", color: i === idx ? a.ink : T.fg3, transition: "color .18s" }}>{o.label}</button>
      ))}
    </div>
  );
}

// ─── ChipToggle — depressed-into-surface well; selected lights a signal LED ───
function ChipToggle({ label, glyph = "▲", selected, onClick, accent = T.green, style }) {
  const [h, setH] = useState(false);
  return (
    <button type="button" onClick={onClick} onMouseEnter={() => setH(true)} onMouseLeave={() => setH(false)} style={{
      position: "relative", display: "inline-flex", alignItems: "center", gap: 6, overflow: "hidden",
      padding: "8px 14px", fontSize: 12, borderRadius: 5, cursor: "pointer", lineHeight: 1,
      fontFamily: T.mono, fontWeight: 600, letterSpacing: "0.04em",
      color: selected ? "#bdf2dc" : (h ? T.fg1 : T.fg3),
      border: `1px solid ${selected ? accent + "55" : (h ? "#34435a" : "#232f3e")}`,
      background: selected ? "linear-gradient(180deg, #0b1318, #0c1620)" : "linear-gradient(180deg, #0c121a, #0e151e)",
      boxShadow: selected ? `inset 0 2px 5px rgba(0,0,0,.55), inset 0 -8px 12px -7px ${accent}40, inset 0 0 0 1px ${accent}14`
        : `inset 0 2px 4px rgba(0,0,0,.55), inset 0 -1px 0 rgba(255,255,255,${h ? ".05" : ".04"})`,
      transition: "box-shadow .16s, border-color .16s, color .16s", ...style,
    }}>
      {selected && <span style={{ color: accent, fontSize: "1.05em", lineHeight: 1 }}>{glyph}</span>}{label}
    </button>
  );
}

// ─── WeatherBar — underlit-LED signal strip ───────────────────────────────────
function WeatherBar({ weather, delta, resolution, style }) {
  const c = weather.color;
  return (
    <div style={{ position: "relative", overflow: "hidden", display: "flex", alignItems: "center", justifyContent: "space-between", padding: "11px 16px", borderRadius: 6,
      border: `1px solid ${c}3d`,
      background: `linear-gradient(160deg, rgba(255,255,255,.05), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, ${c}1c, #0a1418)`,
      boxShadow: `inset 0 1px 0 ${c}66, inset 0 -9px 14px -9px ${c}40, 0 0 11px ${c}24, 0 4px 12px rgba(0,0,0,.45)`, ...style }}>
      <div style={{ position: "absolute", inset: "0 0 auto 0", height: "48%", background: "linear-gradient(rgba(255,255,255,.07), rgba(255,255,255,0))", pointerEvents: "none" }} />
      <div style={{ position: "relative", display: "flex", alignItems: "center", gap: 10 }}>
        <span style={{ color: c, fontWeight: 700, fontSize: 15, textShadow: `0 0 7px ${c}b3` }}>{weather.icon}</span>
        <span style={{ fontFamily: T.mono, fontSize: 10, letterSpacing: "0.12em", color: c, textTransform: "uppercase", fontWeight: 700 }}>{weather.label}</span>
      </div>
      <div style={{ position: "relative", display: "flex", alignItems: "center", gap: 16, fontFamily: T.mono }}>
        {delta != null && <span style={{ fontSize: 12, fontWeight: 700, color: delta >= 0 ? T.green : T.red }}>{delta >= 0 ? "+" : ""}{delta} NCI</span>}
        <span style={{ fontSize: 10, color: T.fg3, letterSpacing: "0.08em" }}>{resolution}</span>
      </div>
    </div>
  );
}

// ─── TrueNorthPanel — underlit cyan-glass conclusion surface ──────────────────
function TrueNorthPanel({ heading, children, footnotes, style }) {
  return (
    <div style={{ position: "relative", overflow: "hidden", padding: "1.25rem 1.5rem", borderRadius: 6,
      border: `1px solid ${T.cyan}42`,
      background: "linear-gradient(160deg, rgba(255,255,255,.06), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, #06343b, #0a1620)",
      boxShadow: "inset 0 1px 0 rgba(120,245,255,.48), inset 0 -11px 17px -11px rgba(0,240,255,.36), 0 0 12px rgba(0,240,255,.16), 0 5px 16px rgba(0,0,0,.5)", ...style }}>
      <div style={{ position: "absolute", inset: "0 0 auto 0", height: "42%", background: "linear-gradient(rgba(255,255,255,.07), rgba(255,255,255,0))", pointerEvents: "none" }} />
      <div style={{ position: "relative", fontFamily: T.mono, fontSize: 10, color: T.cyan, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 10, fontWeight: 700, textShadow: `0 0 8px ${T.cyan}66` }}>{heading}</div>
      <p style={{ position: "relative", fontFamily: T.sans, fontSize: "1.0625rem", lineHeight: 1.6, color: "#eafcff", margin: 0, fontWeight: 500 }}>{children}</p>
      {footnotes}
    </div>
  );
}

// ─── TributaryTile — glass tile, lifts to full opacity + underlit on hover ────
function TributaryTile({ label, glyph, color, children, onClick }) {
  const [h, setH] = useState(false);
  return (
    <button onClick={onClick} onMouseEnter={() => setH(true)} onMouseLeave={() => setH(false)} style={{
      position: "relative", overflow: "hidden", width: "100%", boxSizing: "border-box", padding: "12px 16px", borderRadius: 5, textAlign: "left", cursor: "pointer",
      display: "flex", flexDirection: "column", gap: 4, opacity: h ? 1 : 0.82,
      border: `1px solid ${color}${h ? "55" : "2e"}`,
      background: "linear-gradient(160deg, rgba(255,255,255,.05), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, #131b23, #0b1117)",
      boxShadow: h ? `inset 0 1px 0 rgba(255,255,255,.08), inset 0 -8px 14px -8px ${color}40, 0 0 12px ${color}1e, 0 5px 14px rgba(0,0,0,.42)` : "inset 0 1px 0 rgba(255,255,255,.05), 0 2px 7px rgba(0,0,0,.35)",
      transform: h ? "translateY(-1px)" : "none", transition: "all .16s",
    }}>
      <span style={{ fontFamily: T.mono, fontSize: 10, letterSpacing: "0.1em", textTransform: "uppercase", fontWeight: 700, color, display: "flex", alignItems: "center", gap: 6 }}>{glyph && <span>{glyph}</span>}{label}</span>
      <span style={{ fontFamily: T.sans, fontSize: 13, color: T.fg2, lineHeight: 1.5 }}>{children}</span>
    </button>
  );
}

// ─── Motion — spinner · progress · stepped pipeline (reduced-motion safe) ─────
function Spinner({ size = 20, width, color = T.cyan, style }) {
  const bw = width || (size >= 28 ? 3 : 2);
  return <div data-spin style={{ width: size, height: size, borderRadius: "50%", border: `${bw}px solid #1c2736`, borderTopColor: color,
    boxShadow: `0 0 7px -2px ${color}, inset 0 0 4px rgba(0,0,0,.6)`, animation: "arcs-spin .8s linear infinite", ...style }} />;
}
function ProgressBar({ value = 0, height = 6, indeterminate, color = T.cyan, style }) {
  return (
    <div style={{ width: "100%", height, borderRadius: 999, overflow: "hidden", position: "relative",
      background: "linear-gradient(180deg, #090d12, #0c1219)",
      boxShadow: "inset 0 2px 4px rgba(0,0,0,.65), inset 0 -1px 0 rgba(255,255,255,.04)", ...style }}>
      {indeterminate ? (
        <div data-indet style={{ position: "absolute", top: 0, bottom: 0, width: "34%", borderRadius: 999,
          background: `linear-gradient(90deg, transparent, ${color}, transparent)`, boxShadow: `0 0 9px -1px ${color}`, animation: "arcs-indet 1.35s cubic-bezier(0.4,0,0.2,1) infinite" }} />
      ) : (
        <div style={{ height: "100%", width: `${Math.max(0, Math.min(100, value))}%`, borderRadius: 999, position: "relative",
          background: `linear-gradient(90deg, #1ec3d4, ${color})`, boxShadow: `0 0 8px -1px ${color}, inset 0 1px 0 rgba(255,255,255,.35)`, transition: "width .3s ease" }}>
          <div data-shimmer style={{ position: "absolute", inset: 0, borderRadius: 999, background: "linear-gradient(90deg, transparent, rgba(255,255,255,.4), transparent)", transform: "translateX(-100%)", animation: "arcs-shimmer 1.6s ease-in-out infinite" }} />
        </div>
      )}
    </div>
  );
}
function StepProgress({ labels = ["L0", "L1", "L2", "L3", "L4", "L5"], current = 0, style }) {
  return (
    <div style={style}>
      <div style={{ display: "flex", gap: 5 }}>
        {labels.map((_, i) => {
          const done = i < current, now = i === current;
          return <div key={i} data-pulse={now ? "" : undefined} style={{ flex: 1, height: 6, borderRadius: 3,
            background: done ? `linear-gradient(90deg, #1ec3d4, ${T.cyan})` : now ? `linear-gradient(90deg, #0a4a52, ${T.cyan})` : "linear-gradient(180deg, #0a0f15, #0d141c)",
            boxShadow: done ? `0 0 7px -2px ${T.cyan}, inset 0 1px 0 rgba(255,255,255,.3)` : "inset 0 1px 2px rgba(0,0,0,.6)",
            animation: now ? "arcs-pulse 1.1s ease-in-out infinite" : "none" }} />;
        })}
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", fontFamily: T.mono, fontSize: 8.5, color: T.fg4, letterSpacing: "0.06em", marginTop: 7 }}>
        {labels.map((l, i) => <span key={l} style={{ color: i === current ? T.cyan : T.fg4 }}>{l}</span>)}
      </div>
    </div>
  );
}

Object.assign(window, { SectionLabel, Rule, Field, Picker, Tabs, SegmentedSlider, ChipToggle, WeatherBar, TrueNorthPanel, TributaryTile, Spinner, ProgressBar, StepProgress });
