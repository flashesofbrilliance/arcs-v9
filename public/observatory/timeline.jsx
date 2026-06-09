// ARCS Observatory — chrome + unified ledger (header, controls, legend, track,
// REPLAY scrubber, grouped event/risk rows). Faithful to uploads/observatory.html.

const ALT_TABS = [["all", "all"], ["L5", "Exec"], ["L4", "Strategic"], ["L3", "Operational"], ["L2", "Tactical"], ["L1", "Surgical"]];

function ObsHeader() {
  return (
    <header style={{ display: "flex", alignItems: "baseline", gap: 14, padding: "12px 0 10px", flexWrap: "wrap" }}>
      <h1 style={{ fontSize: 14, letterSpacing: ".04em", margin: 0, fontWeight: 600, color: C.cyan }}>
        ARCS v9 <span style={{ color: "#475569" }}>·</span> <span style={{ color: "#e2e8f0" }}>OBSERVATORY</span>
      </h1>
      <span style={{ color: "#8593a6", fontSize: 11 }}>Forensic reconstruction — 5 altitudes · scored · provenance-cited · reusable</span>
    </header>
  );
}

function Ctl({ active, accent = C.green, children, ...rest }) {
  const [h, setH] = React.useState(false);
  const on = active;
  return (
    <button onMouseEnter={() => setH(true)} onMouseLeave={() => setH(false)} {...rest} style={{
      flex: "0 0 auto", border: `1px solid ${on ? accent : (h ? C.cyan : "#1e293b")}`, color: on ? accent : (h ? C.cyan : "#cbd5e1"),
      background: on ? `linear-gradient(180deg, ${accent}14, ${accent}06)` : "linear-gradient(180deg, #0e151e, #0b1117)",
      padding: "7px 11px", fontSize: 11, borderRadius: 6, cursor: "pointer", minHeight: 34, whiteSpace: "nowrap",
      fontFamily: "var(--font-mono)", display: "inline-flex", alignItems: "center", letterSpacing: ".02em",
      boxShadow: on ? `inset 0 -6px 11px -7px ${accent}40` : "inset 0 1px 0 rgba(255,255,255,.04)", transition: "all .15s",
    }}>{children}</button>
  );
}
const Sep = () => <span style={{ flex: "0 0 auto", width: 1, height: 20, background: "#1e293b", margin: "0 3px" }} />;

// ── Dropdown — dark-glass capsule trigger + menu (the shared Compass finish) ──
function Dropdown({ label, value, options, onChange, accent = C.cyan, minWidth = 150 }) {
  const [open, setOpen] = React.useState(false);
  const [h, setH] = React.useState(false);
  const ref = React.useRef(null);
  React.useEffect(() => {
    if (!open) return;
    const close = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, [open]);
  const current = options.find(o => o.value === value) || options[0];
  return (
    <div ref={ref} style={{ position: "relative", flex: "0 0 auto" }}>
      <button onClick={() => setOpen(v => !v)} onMouseEnter={() => setH(true)} onMouseLeave={() => setH(false)} style={{
        display: "inline-flex", alignItems: "center", gap: 8, width: minWidth, minHeight: 34, padding: "7px 11px",
        border: `1px solid ${open ? accent : (h ? C.cyan : "#1e293b")}`, borderRadius: 8, cursor: "pointer",
        background: "linear-gradient(160deg, rgba(255,255,255,.05), rgba(255,255,255,.01) 40%, rgba(0,0,0,.18)), linear-gradient(165deg, #11181f, #0a1016)",
        boxShadow: open ? `inset 0 1px 0 rgba(255,255,255,.06), inset 0 -6px 11px -7px ${accent}40` : "inset 0 1px 0 rgba(255,255,255,.05), inset 0 -2px 6px rgba(0,0,0,.45)",
        fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: ".02em", transition: "all .15s",
      }}>
        {label && <span style={{ fontSize: 9, color: "#707e92", letterSpacing: ".12em", textTransform: "uppercase" }}>{label}</span>}
        {current.glyph && <span style={{ color: current.accent || accent }}>{current.glyph}</span>}
        <span style={{ color: open || h ? accent : "#e2e8f0", flex: 1, minWidth: 0, textAlign: "left", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{current.label}</span>
        <span style={{ color: "#707e92", fontSize: 9, transform: open ? "rotate(180deg)" : "none", transition: "transform .2s" }}>▾</span>
      </button>
      {open && (
        <div style={{ position: "absolute", top: "calc(100% + 5px)", left: 0, width: "max-content", minWidth: minWidth, zIndex: 70,
          border: `1px solid ${accent}55`, borderRadius: 9, overflow: "hidden", padding: 4,
          background: "linear-gradient(180deg, #0e151e, #0a0f16)", boxShadow: `0 16px 34px -14px rgba(0,0,0,.8), 0 0 0 1px rgba(0,0,0,.4), inset 0 1px 0 rgba(255,255,255,.05)` }}>
          {options.map(o => {
            const sel = o.value === value;
            return (
              <button key={o.value} onClick={() => { onChange(o.value); setOpen(false); }} style={{
                display: "flex", alignItems: "center", gap: 9, width: "100%", padding: "8px 10px", borderRadius: 6, cursor: "pointer",
                border: "1px solid transparent", textAlign: "left", whiteSpace: "nowrap",
                background: sel ? `linear-gradient(180deg, ${(o.accent || accent)}1c, ${(o.accent || accent)}08)` : "transparent",
                fontFamily: "var(--font-mono)", fontSize: 11.5, transition: "background .12s",
                boxShadow: sel ? `inset 0 -6px 11px -8px ${(o.accent || accent)}50` : "none",
              }} onMouseEnter={e => { if (!sel) e.currentTarget.style.background = "rgba(255,255,255,.04)"; }}
                 onMouseLeave={e => { if (!sel) e.currentTarget.style.background = "transparent"; }}>
                {o.glyph && <span style={{ color: o.accent || accent, width: 14, textAlign: "center" }}>{o.glyph}</span>}
                <span style={{ display: "flex", flexDirection: "column", gap: 1, flex: 1 }}>
                  <span style={{ color: sel ? (o.accent || accent) : "#e2e8f0" }}>{o.label}</span>
                  {o.hint && <span style={{ color: "#707e92", fontSize: 9.5, letterSpacing: ".01em" }}>{o.hint}</span>}
                </span>
                {sel && <span style={{ color: o.accent || accent, fontSize: 10 }}>●</span>}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

const MODE_OPTS = [
  { value: "glance", label: "At a glance",     glyph: "▦", accent: C.cyan,  hint: "ledger + scored deck" },
  { value: "chain",  label: "Chain of events", glyph: "⌥", accent: C.green, hint: "Exec → Surgical, linked" },
  { value: "risk",   label: "Risk register",   glyph: "⚠", accent: C.red,   hint: "ruin-paths by severity" },
];
const ALT_OPTS = [
  { value: "all", label: "All altitudes", accent: C.cyan },
  { value: "L5", label: "Executive",   glyph: "●", accent: C.green },
  { value: "L4", label: "Strategic",   glyph: "●", accent: C.cyan },
  { value: "L3", label: "Operational", glyph: "●", accent: C.gold },
  { value: "L2", label: "Tactical",    glyph: "●", accent: C.orange },
  { value: "L1", label: "Surgical",    glyph: "●", accent: C.red },
];
const GROUP_OPTS = [
  { value: "day", label: "By day" }, { value: "week", label: "By week" }, { value: "month", label: "By month" },
];
// Risk view reuses the Focus slot for severity and the Period slot for window length
const SEV_OPTS = [
  { value: "all", label: "All severities", accent: C.cyan },
  { value: "RUIN", label: "Ruin",   glyph: "◆", accent: C.red },
  { value: "HIGH", label: "High",   glyph: "◆", accent: C.orange },
  { value: "MED",  label: "Medium", glyph: "◆", accent: C.gold },
];
const WIN_OPTS = [
  { value: 7, label: "1 week" }, { value: 14, label: "2 weeks" }, { value: 28, label: "4 weeks" }, { value: 999, label: "All time" },
];

function ControlBar({ mode, setMode, focus, setFocus, sevFocus, setSevFocus, view, setView, riskWin, setRiskWin, legendOpen, setLegendOpen, query, setQuery, face, setFace }) {
  const isRisk = mode === "risk";
  // Focus slot: altitude (glance/chain) or severity (risk) — always present, fixed position
  const focusVal = isRisk ? sevFocus : focus;
  const focusOpts = isRisk ? SEV_OPTS : ALT_OPTS;
  const focusSet = isRisk ? setSevFocus : setFocus;
  // Period slot removed — no date-based grouping or rolling window
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8, padding: "0 0 2px" }}>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        <Dropdown label="View" value={mode} options={MODE_OPTS} onChange={setMode} accent={C.cyan} minWidth={190} />
        <Dropdown label="Focus" value={focusVal} options={focusOpts} onChange={focusSet} accent={C.cyan} minWidth={188} />
        <Sep />
        <Ctl active={legendOpen} accent={C.cyan} onClick={() => setLegendOpen(v => !v)}>legend <span style={{ display: "inline-block", fontSize: 9, color: "#707e92", transform: legendOpen ? "rotate(180deg)" : "none", transition: "transform .2s" }}>▾</span></Ctl>
        <Sep />
        <Ctl active accent={C.gold} onClick={() => setFace(f => f === "trajectory" ? "altitude" : "trajectory")} title="flip the card — trajectory ⇄ by lane">⇄ {face === "trajectory" ? (isRisk ? "by severity" : "by altitude") : "trajectory"}</Ctl>
      </div>
      <SearchBox query={query} setQuery={setQuery} />
    </div>
  );
}

// Free-text filter, sits just right of the legend. Width is responsive;
// dims/hides non-matching rows + nodes across the ledger, deck and swimlanes.
function SearchBox({ query, setQuery }) {
  const [h, setH] = React.useState(false);
  const [f, setF] = React.useState(false);
  const lit = f || h || query;
  return (
    <div style={{ position: "relative", display: "flex", alignItems: "center", width: "100%" }}>
      <span style={{ position: "absolute", left: 9, fontSize: 14, color: lit ? C.cyan : "#707e92", pointerEvents: "none", transition: "color .15s" }}>⌕</span>
      <input value={query} onChange={e => setQuery(e.target.value)} onFocus={() => setF(true)} onBlur={() => setF(false)}
        onMouseEnter={() => setH(true)} onMouseLeave={() => setH(false)} placeholder="Filter events, risks, commits…"
        style={{ width: "100%", minHeight: 34, padding: "7px 26px 7px 28px", borderRadius: 8,
          border: `1px solid ${f ? C.cyan : (h ? C.cyan + "88" : "#1e293b")}`, outline: "none",
          background: "linear-gradient(160deg, rgba(255,255,255,.04), rgba(0,0,0,.18)), linear-gradient(165deg, #0e151e, #0a1016)",
          boxShadow: f ? `inset 0 1px 0 rgba(255,255,255,.05), inset 0 -6px 11px -7px ${C.cyan}40, 0 0 0 1px ${C.cyan}2a` : "inset 0 1px 0 rgba(255,255,255,.04), inset 0 2px 5px rgba(0,0,0,.45)",
          color: "#e2e8f0", fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: ".02em", transition: "all .15s" }} />
      {query && (
        <button onClick={() => setQuery("")} aria-label="clear filter" style={{ position: "absolute", right: 7, width: 18, height: 18, borderRadius: 5, border: "none", cursor: "pointer",
          background: "rgba(255,255,255,.06)", color: "#8593a6", fontFamily: "var(--font-mono)", fontSize: 11, display: "inline-flex", alignItems: "center", justifyContent: "center", padding: 0 }}>✕</button>
      )}
    </div>
  );
}

// Inline expand/collapse docked under the nav — no floating modal, no scrim.
function Legend({ open }) {
  const sw = (bg) => <span style={{ display: "inline-block", width: 10, height: 10, borderRadius: 3, verticalAlign: "middle", margin: "0 4px 0 8px", background: bg }} />;
  return (
    <div style={{ overflow: "hidden", maxHeight: open ? 460 : 0, opacity: open ? 1 : 0,
      transition: "max-height .32s var(--ease-luxury), opacity .25s ease, margin .32s var(--ease-luxury)",
      margin: open ? "8px 0 0" : "0" }}>
      <div style={{ border: "1px solid #22324d", borderRadius: 10, padding: "12px 16px",
        background: "linear-gradient(180deg, #0e151e, #0b1117)", boxShadow: "inset 0 1px 0 rgba(255,255,255,.05), inset 0 -2px 8px rgba(0,0,0,.4)" }}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2px 28px", fontSize: 11, whiteSpace: "nowrap" }}>
          <div>
            <p style={{ color: C.gold, fontSize: 10, letterSpacing: ".08em", textTransform: "uppercase", margin: "0 0 5px" }}>How to use</p>
            <ul style={{ margin: 0, paddingLeft: 16, color: "#8593a6", lineHeight: 1.85, listStyle: "none" }}>
              <li><b style={{ color: "#cbd5e1" }}>Tap</b> a row or node → its card</li>
              <li><b style={{ color: "#cbd5e1" }}>View</b> → glance · chain · risk</li>
              <li><b style={{ color: "#cbd5e1" }}>Focus</b> → isolate altitude · <b style={{ color: "#cbd5e1" }}>↑ ↓</b></li>
              <li><b style={{ color: "#cbd5e1" }}>Replay</b> → ▶ play · <b style={{ color: "#cbd5e1" }}>← →</b> step</li>
              <li><b style={{ color: "#cbd5e1" }}>Filter</b> → match events · risks · commits</li>
              <li><b style={{ color: "#cbd5e1" }}>Space</b> legend · <b style={{ color: "#cbd5e1" }}>Enter</b> card · <b style={{ color: "#cbd5e1" }}>Esc</b> close</li>
            </ul>
          </div>
          <div>
            <p style={{ color: C.gold, fontSize: 10, letterSpacing: ".08em", textTransform: "uppercase", margin: "0 0 5px" }}>The 4 encoded dimensions</p>
            <div style={{ color: "#8593a6", lineHeight: 2.0 }}>
              <div><b style={{ color: C.gold }}>1 Altitude</b> — Exec → Surgical · audience zoom</div>
              <div><b style={{ color: C.gold }}>2 Hue</b> — grade{sw(C.green)}A{sw(C.cyan)}B{sw(C.gold)}C{sw(C.orange)}D{sw(C.red)}F</div>
              <div><b style={{ color: C.gold }}>3 Glow</b> — confidence · brighter = surer</div>
              <div><b style={{ color: C.gold }}>4 Border</b> — risk · solid · dashed · pulsing</div>
            </div>
          </div>
        </div>
        <div style={{ marginTop: 12, borderTop: "1px solid #16202e", paddingTop: 10 }}>
          <p style={{ color: C.gold, fontSize: 10, letterSpacing: ".08em", textTransform: "uppercase", margin: "0 0 7px" }}>Map glyphs — glyph = type · color = altitude / grade</p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "8px 16px" }}>
            {[["✦", "genesis", C.steel], ["❖", "canon", C.steel], ["⊕", "feature", C.steel], ["⊘", "security", C.steel], ["✕", "fix", C.steel], ["◇", "kairos", C.gold], ["★", "peak milestone", C.gold], ["◆", "risk", C.red]].map(([g, l, col]) => {
              const isRisk = g === "◆";
              return (
                <span key={l} style={{ display: "inline-flex", alignItems: "center", gap: 7, fontSize: 11 }}>
                  <span style={{ width: 17, height: 17, flex: "0 0 auto", borderRadius: isRisk ? 3 : "50%", transform: isRisk ? "rotate(45deg)" : "none",
                    display: "inline-flex", alignItems: "center", justifyContent: "center", background: col, color: "#04070c",
                    fontFamily: "var(--font-mono)", fontSize: 9.5, fontWeight: 700, boxShadow: `0 0 6px -1px ${col}, inset 0 1px 0 rgba(255,255,255,.4)` }}>{isRisk ? "" : g}</span>
                  <b style={{ color: "#cbd5e1", fontWeight: 500 }}>{l}</b>
                </span>
              );
            })}
          </div>
        </div>
        <p style={{ color: "#707e92", fontSize: 10, margin: "10px 0 0" }}>Build wins + ruin-paths share the <b style={{ color: "#cbd5e1" }}>unified ledger</b>; REPLAY scrubs it. Every node cites provenance IDs (P01–P28).</p>
      </div>
    </div>
  );
}

// ── Timeline ──────────────────────────────────────────────────────────────────
// type → hieroglyph (mono, no emoji). Peak events override with ★; risks use ◆.
const TYPE_GLYPH = { genesis: "✦", canon: "❖", milestone: "★", feat: "⊕", security: "⊘", fix: "✕", kairos: "◇" };
const MAP_ALTS = ["L5", "L4", "L3", "L2", "L1"]; // Exec (top) → Surgical (base)

// ── Trajectory map — the chain-of-events altitude lanes, folded into at-a-glance.
// Replaces the flat dot-track: every milestone is a glyph placed by date (x) and
// altitude (y); risks ride a slim band below. Honors REPLAY + filter dimming.
function TrajectoryMap({ visibleCount, query, focus, onOpen }) {
  const laneH = 28, riskH = 36;
  const H = MAP_ALTS.length * laneH + riskH;
  const laneCenter = (alt) => MAP_ALTS.indexOf(alt) * laneH + laneH / 2;
  const riskCenter = MAP_ALTS.length * laneH + riskH / 2;
  const N = LEDGER.length;
  const xpct = (i) => N <= 1 ? 50 : 1.5 + (i / (N - 1)) * 97; // uniform chronological slots
  const evThread = LEDGER.map((x, i) => ({ x, i })).filter(o => o.x.kind === "event");
  const peaks = LEDGER.map((x, i) => ({ x, i })).filter(o => o.x.peak);
  const [hv, setHv] = React.useState(null);
  const laneOff = (alt) => focus && focus !== "all" && focus !== alt; // dim non-focus altitude
  const riskOff = focus && focus !== "all";                         // risks have no altitude
  return (
    <div style={{ display: "flex", margin: "4px 0 14px" }}>
      {/* altitude label gutter */}
      <div style={{ position: "relative", flex: "0 0 78px", height: H }}>
        {MAP_ALTS.map(alt => (
          <div key={alt} style={{ position: "absolute", left: 0, top: laneCenter(alt), transform: "translateY(-50%)", display: "flex", flexDirection: "column", lineHeight: 1.1, opacity: laneOff(alt) ? 0.2 : 1, transition: "opacity .3s" }}>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: 9.5, fontWeight: 700, color: ALT[alt].accent, letterSpacing: ".04em", whiteSpace: "nowrap" }}>{alt}</span>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: 7, color: "#707e92", letterSpacing: ".07em", whiteSpace: "nowrap" }}>{ALT[alt].name}</span>
          </div>
        ))}
        <div style={{ position: "absolute", left: 0, top: riskCenter, transform: "translateY(-50%)", opacity: riskOff ? 0.2 : 1, transition: "opacity .3s" }}>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: 9.5, fontWeight: 700, color: C.red, letterSpacing: ".04em", whiteSpace: "nowrap" }}>⚠ RISK</span>
        </div>
      </div>
      {/* plot */}
      <div style={{ position: "relative", flex: "1 1 auto", height: H, minWidth: 0 }}>
        {MAP_ALTS.map(alt => (
          <div key={alt} style={{ position: "absolute", left: 0, right: 6, top: laneCenter(alt), height: 1, background: `linear-gradient(90deg, ${ALT[alt].accent}24, ${ALT[alt].accent}0a)`, opacity: laneOff(alt) ? 0.25 : 1, transition: "opacity .3s" }} />
        ))}
        <div style={{ position: "absolute", left: 0, right: 6, top: riskCenter, height: 1, background: `linear-gradient(90deg, ${C.red}24, ${C.red}0a)`, opacity: riskOff ? 0.25 : 1, transition: "opacity .3s" }} />
        {/* build-order thread + punctuated kairos / peak guides */}
        <svg viewBox={`0 0 100 ${H}`} preserveAspectRatio="none" style={{ position: "absolute", inset: 0, width: "100%", height: "100%", pointerEvents: "none" }}>
          {peaks.map(o => <line key={o.x.id} x1={xpct(o.i)} x2={xpct(o.i)} y1="2" y2={MAP_ALTS.length * laneH} stroke={C.gold} strokeOpacity=".3" strokeWidth="1" strokeDasharray="2 3" vectorEffect="non-scaling-stroke" />)}
          <polyline points={evThread.map(o => `${xpct(o.i)},${laneCenter(o.x.alt)}`).join(" ")} fill="none" stroke={C.cyan} strokeOpacity=".26" strokeWidth="1.2" vectorEffect="non-scaling-stroke" />
        </svg>
        {/* milestone glyphs */}
        {LEDGER.map((x, i) => {
          const isRisk = x.kind === "risk";
          const dim = i >= visibleCount || !matchQ(x, query) || (isRisk ? riskOff : laneOff(x.alt));
          const accent = isRisk ? SEV[x.sev] : (x.peak ? C.gold : ALT[x.alt].accent);
          const cy = isRisk ? riskCenter : laneCenter(x.alt);
          const glyph = x.peak ? "★" : (TYPE_GLYPH[x.type] || "•");
          const sz = x.peak ? 20 : 16;
          const base = isRisk ? "rotate(45deg)" : "none";
          return (
            <button key={x.id} onClick={() => onOpen(x)} title={`${x.date.slice(5)} · ${x.label || x.risk}`}
              data-pulse={isRisk && x.status === "OPEN" ? "" : undefined}
              style={{ position: "absolute", left: `${xpct(i)}%`, top: cy, width: sz, height: sz, marginLeft: -sz / 2, marginTop: -sz / 2,
                display: "inline-flex", alignItems: "center", justifyContent: "center", padding: 0, cursor: "pointer",
                borderRadius: isRisk ? 3 : "50%", transform: base,
                border: `1.5px solid ${isRisk ? STATUS[x.status] : (x.peak ? "#1a1404" : "#03060b")}`, background: accent,
                boxShadow: `0 0 ${x.peak ? 10 : 6}px -1px ${accent}, inset 0 1px 0 rgba(255,255,255,.4), 0 2px 4px rgba(0,0,0,.5)`,
                opacity: dim ? 0.15 : 1, pointerEvents: dim ? "none" : "auto", transition: "opacity .3s, transform .15s",
                animation: isRisk && x.status === "OPEN" ? "obs-pulse 1.8s infinite" : "none" }}
              onMouseEnter={ev => { ev.currentTarget.style.transform = `${base === "none" ? "" : base} scale(1.28)`; setHv({ i, x: xpct(i), cy, item: x, isRisk, accent }); }}
              onMouseLeave={ev => { ev.currentTarget.style.transform = base; setHv(h => (h && h.i === i ? null : h)); }}>
              {!isRisk && <span style={{ color: "#04070c", fontFamily: "var(--font-mono)", fontSize: x.peak ? 11 : 9, fontWeight: 700, lineHeight: 1 }}>{glyph}</span>}
            </button>
          );
        })}
        {/* mini hover preview — condensed card facts at a glance */}
        {hv && (() => {
          const x = hv.item, isRisk = hv.isRisk, accent = hv.accent, below = hv.cy < 70;
          return (
            <div style={{ position: "absolute", left: `${hv.x}%`, top: below ? hv.cy + 14 : hv.cy - 14, transform: `translate(-50%, ${below ? "0" : "-100%"})`,
              zIndex: 6, pointerEvents: "none", width: "max-content", maxWidth: 250,
              border: `1px solid ${accent}66`, borderRadius: 8, padding: "7px 10px",
              background: "linear-gradient(180deg, #0e151e, #0a0f16)", boxShadow: `0 12px 26px -10px rgba(0,0,0,.85), 0 0 0 1px rgba(0,0,0,.4), inset 0 1px 0 rgba(255,255,255,.05)` }}>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: 9, letterSpacing: ".06em", color: accent, fontWeight: 700, marginBottom: 3, whiteSpace: "nowrap" }}>
                {x.date.slice(5)} · {isRisk ? `⚠ ${x.sev} · ${x.status}` : `${x.alt} ${ALT[x.alt].name} · ${String(x.type).toUpperCase()}`}
              </div>
              <div style={{ fontFamily: "var(--font-sans)", fontSize: 11.5, color: "#e2e8f0", lineHeight: 1.35 }}>{x.label || x.risk}</div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: 9, color: "#8593a6", marginTop: 4, whiteSpace: "nowrap" }}>
                {isRisk ? `countered: ${x.how}` : `conf ${x.conf}${x.sha ? " · " + x.sha : ""}`}
              </div>
            </div>
          );
        })()}
      </div>
    </div>
  );
}

// ── Back face — by-altitude lens. Each altitude as a readable labeled lane; a
// specific Focus dims the others (focused-altitude view). Risks omitted (no alt).
function FocusedAltitudeStrip({ focus, visibleCount, query, onOpen }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8, margin: "4px 0 14px" }}>
      {MAP_ALTS.map(alt => {
        const dimAlt = focus !== "all" && focus !== alt;
        const evs = EVENTS.filter(e => e.alt === alt);
        return (
          <div key={alt} style={{ display: "flex", alignItems: "center", gap: 10, padding: "7px 10px", borderRadius: 8,
            border: `1px solid ${ALT[alt].accent}2e`, borderLeft: `3px solid ${ALT[alt].accent}`,
            background: "linear-gradient(180deg, rgba(255,255,255,.015), rgba(0,0,0,.12))",
            opacity: dimAlt ? 0.2 : 1, pointerEvents: dimAlt ? "none" : "auto", transition: "opacity .3s" }}>
            <div style={{ flex: "0 0 86px", display: "flex", flexDirection: "column", lineHeight: 1.15 }}>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: 10.5, fontWeight: 700, color: ALT[alt].accent }}>{alt}</span>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: 8, color: "#707e92", letterSpacing: ".07em" }}>{ALT[alt].name}</span>
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6, flex: "1 1 auto", minWidth: 0 }}>
              {evs.length ? evs.map(e => {
                const i = LEDGER.findIndex(x => x.id === e.id);
                const dim = i >= visibleCount || !matchQ(e, query);
                const accent = e.peak ? C.gold : ALT[alt].accent;
                const glyph = e.peak ? "★" : (TYPE_GLYPH[e.type] || "•");
                return (
                  <button key={e.id} onClick={() => onOpen(e)} title={e.label}
                    style={{ display: "inline-flex", alignItems: "center", gap: 6, padding: "4px 9px 4px 5px", borderRadius: 6, cursor: "pointer",
                      border: `1px solid ${accent}45`, background: `${accent}10`, fontFamily: "var(--font-mono)",
                      opacity: dim ? 0.22 : 1, pointerEvents: dim ? "none" : "auto", transition: "opacity .3s, border-color .15s" }}
                    onMouseEnter={ev => ev.currentTarget.style.borderColor = accent}
                    onMouseLeave={ev => ev.currentTarget.style.borderColor = `${accent}45`}>
                    <span style={{ flex: "0 0 auto", width: 16, height: 16, borderRadius: "50%", background: accent, color: "#04070c", display: "inline-flex", alignItems: "center", justifyContent: "center", fontSize: 9, fontWeight: 700, boxShadow: `0 0 6px -1px ${accent}` }}>{glyph}</span>
                    <span style={{ fontSize: 10, color: "#cbd5e1", maxWidth: 230, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{e.label}</span>
                  </button>
                );
              }) : <span style={{ fontFamily: "var(--font-mono)", fontSize: 9, color: "#5b6675" }}>no build events</span>}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function Track({ visibleCount, query, onOpen }) {
  return (
    <div style={{ position: "relative", height: 24, margin: "4px 4px 12px" }}>
      <div style={{ position: "absolute", left: 0, right: 0, top: 11, height: 1, background: "linear-gradient(90deg,#23344f,#3b4f70,#23344f)" }} />
      {LEDGER.map((x, i) => {
        const dim = i >= visibleCount || !matchQ(x, query);
        const isRisk = x.kind === "risk";
        const accent = isRisk ? SEV[x.sev] : (x.peak ? C.gold : ALT[x.alt].accent);
        const sz = x.peak ? 17 : isRisk ? 11 : 13;
        return (
          <a key={x.id} href="#" onClick={(e) => { e.preventDefault(); onOpen(x); }}
            title={x.label || x.risk}
            style={{ position: "absolute", top: x.peak ? 3 : isRisk ? 6 : 5, left: `${x.left}%`, width: sz, height: sz, marginLeft: -sz / 2,
              borderRadius: isRisk ? 2 : "50%", transform: isRisk ? "rotate(45deg)" : "none", background: accent, border: "2px solid var(--bg, #020408)",
              boxShadow: `0 0 ${x.peak ? 12 : 8}px ${accent}`, opacity: dim ? 0.16 : 1, transition: "opacity .3s", textDecoration: "none" }} />
        );
      })}
    </div>
  );
}

function Scrubber({ replay, setReplay, playing, setPlaying, focus }) {
  const steps = stepIndices(focus);
  const pos = typeof replay === "number" ? steps.indexOf(replay) : -1;
  const sel = typeof replay === "number" ? LEDGER[replay] : null;
  const tColor = (x) => x.kind === "risk" ? SEV[x.sev] : (x.peak ? C.gold : ALT[x.alt].accent);
  const tLabel = (x) => x.kind === "risk" ? `⚠ ${x.sev} risk · ${x.status}` : (x.peak ? `★ peak milestone · ${x.type}` : x.type);
  const tGlyph = (x) => x.kind === "risk" ? "◆" : (x.peak ? "★" : null);
  return (
    <div style={{ margin: "2px 0 14px" }}>
      <div style={{ display: "flex", alignItems: "baseline", gap: 9, marginBottom: 8, flexWrap: "wrap" }}>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 10.5, fontWeight: 700, letterSpacing: ".1em", color: C.gold }}>▸ MILESTONE REPLAY</span>
        <span style={{ fontSize: 10, color: "#8593a6" }}>each numbered marker is one logged milestone — a build commit (●/★) or a risk (◆) — in the order it happened. ★ = peak. Press ▶ to play the build forward, or pick a step (or ← / →) to isolate the trajectory up to that point.</span>
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 5, alignItems: "center" }}>
        <button onClick={() => {
            if (playing) { setPlaying(false); return; }
            if (pos < 0 || pos >= steps.length - 1) setReplay(steps[0]);
            setPlaying(true);
          }} title={playing ? "pause" : "play through each milestone"}
          style={{ cursor: "pointer", fontSize: 10, borderRadius: 5, padding: "3px 9px", minHeight: 24, fontFamily: "var(--font-mono)", fontWeight: 700, letterSpacing: ".04em",
            border: `1px solid ${playing ? C.gold : C.green}`, color: playing ? "#04070c" : "#04070c",
            background: playing ? C.gold : C.green, display: "inline-flex", alignItems: "center", gap: 5, transition: "all .14s" }}>
          <span style={{ fontSize: 9 }}>{playing ? "⏸" : "▶"}</span>{playing ? "PLAYING" : "PLAY"}
        </button>
        <span style={{ width: 1, height: 18, background: "#1e293b", margin: "0 2px" }} />
        {steps.map((li, n) => { const x = LEDGER[li]; return (
          <ScBtn key={x.id} active={replay === li} accent={tColor(x)} glyph={tGlyph(x)} title={`${n + 1}. ${x.label || x.risk}`} onClick={() => { setPlaying(false); setReplay(li); }}>{n + 1}</ScBtn>
        ); })}
        <span style={{ width: 1, height: 18, background: "#1e293b", margin: "0 2px" }} />
        <ScBtn active={replay === "all"} accent={C.cyan} onClick={() => { setPlaying(false); setReplay("all"); }}>all</ScBtn>
      </div>
      {/* live readout — names the selected milestone so the row speaks for itself */}
      <div style={{ marginTop: 9, padding: "8px 11px", borderRadius: 8, border: `1px solid ${sel ? tColor(sel) + "55" : "#1e293b"}`,
        background: "linear-gradient(180deg, #0c121a, #0e151e)", boxShadow: "inset 0 1px 0 rgba(255,255,255,.04)",
        fontFamily: "var(--font-mono)", fontSize: 11, display: "flex", gap: 10, alignItems: "baseline", flexWrap: "wrap" }}>
        {sel ? <>
          <span style={{ color: "#707e92" }}>{String(Math.max(1, pos + 1)).padStart(2, "0")} / {steps.length}</span>
          <span style={{ color: tColor(sel), fontWeight: 700, letterSpacing: ".02em" }}>{tLabel(sel)}</span>
          <span style={{ color: "#e2e8f0", flex: "1 1 auto", minWidth: 0 }}>{sel.label || sel.risk}</span>
        </> : <>
          <span style={{ color: C.cyan, fontWeight: 700, letterSpacing: ".06em" }}>ALL {steps.length} MILESTONES</span>
          <span style={{ color: "#8593a6" }}>genesis → now · the full evidentiary chain. Pick a step to replay up to it.</span>
        </>}
      </div>
    </div>
  );
}
function ScBtn({ active, accent, glyph, children, ...rest }) {
  const [h, setH] = React.useState(false);
  return (
    <button {...rest} onMouseEnter={() => setH(true)} onMouseLeave={() => setH(false)} style={{
      cursor: "pointer", fontSize: 10, borderRadius: 5, padding: "3px 6px", minHeight: 24, minWidth: glyph ? 28 : 22, fontFamily: "var(--font-mono)",
      border: `1px solid ${active ? accent : (h ? C.cyan : accent + "55")}`,
      color: active ? "#04070c" : (h ? C.cyan : accent),
      background: active ? accent : `${accent}12`, fontWeight: active ? 700 : 400,
      transition: "all .14s", display: "inline-flex", alignItems: "center", justifyContent: "center", gap: 3,
    }}>{glyph && <span style={{ fontSize: 8 }}>{glyph}</span>}{children}</button>
  );
}

function Ledger({ view, visibleCount, query, onOpen }) {
  let lastKey = null;
  const rows = LEDGER.filter(x => matchQ(x, query));
  if (rows.length === 0) return (
    <div style={{ padding: "18px 11px", fontFamily: "var(--font-mono)", fontSize: 11, color: "#707e92", textAlign: "center" }}>
      No milestones match <span style={{ color: C.cyan }}>“{query}”</span>.
    </div>
  );
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      {rows.map((x) => {
        const i = LEDGER.indexOf(x);
        const dim = i >= visibleCount;
        return x.kind === "event"
          ? <EventRow key={x.id} ev={x} dim={dim} onOpen={onOpen} />
          : <RiskRow key={x.id} rk={x} dim={dim} onOpen={onOpen} />;
      })}
    </div>
  );
}

function EventRow({ ev, dim, onOpen }) {
  const [h, setH] = React.useState(false);
  const accent = ev.peak ? C.gold : ALT[ev.alt].accent;
  return (
    <div onMouseEnter={() => setH(true)} onMouseLeave={() => setH(false)} style={{ display: "flex", gap: 12, alignItems: "center", borderLeft: `3px solid ${accent}`,
      padding: "9px 11px", borderRadius: 7, background: ev.peak ? "rgba(255,215,0,.05)" : (h ? "rgba(0,240,255,.06)" : "rgba(255,255,255,.015)"), opacity: dim ? 0.16 : 1, transition: "opacity .3s, background .2s" }}>
      <button onClick={() => onOpen(ev)} style={{ display: "flex", flexDirection: "column", gap: 3, flex: "1 1 auto", minWidth: 0, background: "none", border: "none", cursor: "pointer", textAlign: "left", padding: 0 }}>
        <span style={{ display: "flex", gap: 8, alignItems: "baseline", flexWrap: "wrap", whiteSpace: "nowrap", fontFamily: "var(--font-mono)", fontSize: 10, letterSpacing: ".04em" }}>
          <span style={{ fontWeight: 700, color: ALT[ev.alt].accent }}>{ev.alt} {ALT[ev.alt].name}</span>
          <span style={{ color: "#3a4a5e" }}>·</span>
          <span style={{ color: TYPE_COLOR[ev.type] || C.steel, textTransform: "uppercase", letterSpacing: ".08em" }}>{ev.peak ? "★ " : ""}{ev.type}</span>
        </span>
        <span style={{ fontFamily: "var(--font-sans)", fontSize: 14, fontWeight: 500, lineHeight: 1.35, color: h ? C.cyan : "var(--fg1)", transition: "color .15s" }}>{ev.label}</span>
      </button>
    </div>
  );
}

function RiskRow({ rk, dim, onOpen }) {
  const [h, setH] = React.useState(false);
  return (
    <div onMouseEnter={() => setH(true)} onMouseLeave={() => setH(false)} style={{ display: "flex", gap: 12, alignItems: "center", borderLeft: `3px solid ${SEV[rk.sev]}`,
      padding: "9px 11px", borderRadius: 7, background: h ? "rgba(255,77,109,.10)" : "rgba(255,77,109,.045)", opacity: dim ? 0.16 : 1, transition: "opacity .3s, background .2s" }}>
      <button onClick={() => onOpen(rk)} style={{ display: "flex", flexDirection: "column", gap: 3, flex: "1 1 auto", minWidth: 0, background: "none", border: "none", cursor: "pointer", textAlign: "left", padding: 0 }}>
        <span style={{ display: "flex", gap: 8, alignItems: "baseline", flexWrap: "wrap", whiteSpace: "nowrap", fontFamily: "var(--font-mono)", fontSize: 10, letterSpacing: ".04em" }}>
          <span style={{ fontWeight: 700, color: SEV[rk.sev] }}>⚠ {rk.sev} RISK</span>
          <span style={{ color: "#3a4a5e" }}>·</span>
          <span style={{ color: STATUS[rk.status], textTransform: "uppercase", letterSpacing: ".08em" }}>{rk.status}</span>
        </span>
        <span style={{ fontFamily: "var(--font-sans)", fontSize: 14, fontWeight: 500, lineHeight: 1.35, color: h ? C.cyan : "var(--fg1)", transition: "color .15s" }}>{rk.risk}</span>
      </button>
      <span style={{ color: "#707e92", fontSize: 10, flex: "0 0 auto", alignSelf: "center", fontFamily: "var(--font-mono)" }}>{rk.status === "OPEN" ? "⚠ open" : "averted"}</span>
    </div>
  );
}

function Timeline({ replay, setReplay, view, query, face, focus, onOpen }) {
  const [playing, setPlaying] = React.useState(false);
  const replayRef = React.useRef(replay);
  replayRef.current = replay;
  React.useEffect(() => {
    if (!playing) return;
    const steps = stepIndices(focus);
    const iv = setInterval(() => {
      const cur = replayRef.current;
      const p = cur === "all" ? -1 : steps.indexOf(cur);
      const np = p + 1;
      if (np >= steps.length - 1) { setReplay(steps[steps.length - 1]); setPlaying(false); }
      else setReplay(steps[np]);
    }, 1050);
    return () => clearInterval(iv);
  }, [playing, focus]);
  const visibleCount = replay === "all" ? LEDGER.length : replay + 1;
  const onBack = face === "altitude";
  return (
    <section style={{ position: "relative", border: "1px solid #22324d", borderRadius: 12, padding: "12px 14px 14px",
      background: "linear-gradient(180deg,rgba(14,22,38,.92),rgba(9,14,24,.92))" }}>
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "baseline", gap: 10, marginBottom: 12 }}>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 12, letterSpacing: ".08em", color: onBack ? C.gold : C.cyan, fontWeight: 700 }}>{onBack ? "BY ALTITUDE" : "8-WEEK TRAJECTORY"}</span>
        <span style={{ fontSize: 10, color: "#8593a6" }}>{onBack
          ? "the card's back — each altitude Exec→Surgical as a labelled lane · Focus dims the rest · tap → card"
          : "5 altitude lanes Exec→Surgical · glyph = type · ★ peak · ⚠ risk band · tap → card · ▶ or ← / → to replay"}</span>
      </div>
      {onBack
        ? <FocusedAltitudeStrip focus={focus} visibleCount={visibleCount} query={query} onOpen={onOpen} />
        : <TrajectoryMap visibleCount={visibleCount} query={query} focus={focus} onOpen={onOpen} />}
      <Scrubber replay={replay} setReplay={setReplay} playing={playing} setPlaying={setPlaying} focus={focus} />
      <Ledger view={view} visibleCount={visibleCount} query={query} onOpen={onOpen} />
    </section>
  );
}

Object.assign(window, { ObsHeader, ControlBar, Legend, Timeline, FocusedAltitudeStrip });
