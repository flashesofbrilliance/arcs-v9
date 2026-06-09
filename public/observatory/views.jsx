// ARCS Observatory — the named views' bespoke modes:
//   • ChainOfEvents — Exec→Surgical swimlanes, events threaded in build order.
//   • RiskLanes     — severity swimlanes (RUIN→MED), risks threaded by date.
//   • IsoExplorer   — terraced topographic terrain (kept, currently not surfaced).
// (At-a-glance reuses Timeline + Deck from timeline/deck.jsx.)

const ALT_ORDER = ["L5", "L4", "L3", "L2", "L1"]; // Exec (top) → Surgical (base)

// ── Causal chain ──────────────────────────────────────────────────────────────
// 5 altitude lanes; build events plotted left→right by time; a thread links them
// in chronological order so you watch the decision cascade Exec↔Surgical.
function ChainOfEvents({ focus, query, current, setCurrent, onOpen }) {
  const laneH = 72, padL = 116, plotW = 1000;
  const evs = [...EVENTS].sort((a, b) => Date.parse(a.date) - Date.parse(b.date));
  const laneY = (alt) => ALT_ORDER.indexOf(alt) * laneH + laneH / 2;
  const xOf = (idx) => padL + (evs.length <= 1 ? 0 : idx / (evs.length - 1)) * (plotW - padL - 34); // uniform chronological spacing
  const pts = evs.map((e, idx) => ({ e, x: xOf(idx), y: laneY(e.alt) }));
  const H = ALT_ORDER.length * laneH;
  const [hv, setHv] = React.useState(null);

  return (
    <section style={{ border: "1px solid #243042", borderRadius: 14, padding: "14px 14px 8px",
      background: "linear-gradient(160deg, rgba(255,255,255,.05), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, #11181f, #0a1016)",
      boxShadow: "inset 0 1px 0 rgba(255,255,255,.08), inset 0 -2px 8px rgba(0,0,0,.5), 0 5px 16px rgba(0,0,0,.4)" }}>
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "baseline", gap: 10, marginBottom: 6 }}>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 12, letterSpacing: ".08em", color: C.green, fontWeight: 700 }}>CHAIN OF EVENTS</span>
        <span style={{ fontSize: 10, color: "#8593a6" }}>Exec → Surgical — lanes are altitude · x is uniform build order · ★ kairos punctuated · tap a node → card</span>
      </div>
      <div style={{ overflowX: "auto" }}>
        <div style={{ position: "relative", minWidth: 680, height: H }}>
          {/* lane bands + labels */}
          {ALT_ORDER.map((alt, i) => (
            <div key={alt} style={{ position: "absolute", left: 0, right: 0, top: i * laneH, height: laneH,
              borderBottom: i < 4 ? "1px solid #16202e" : "none",
              background: focus !== "all" && focus !== alt ? "transparent" : (i % 2 ? "rgba(255,255,255,.012)" : "transparent"),
              opacity: focus !== "all" && focus !== alt ? 0.22 : 1, transition: "opacity .3s" }}>
              <div style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", display: "flex", flexDirection: "column", gap: 2, width: 88 }}>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, fontWeight: 700, color: ALT[alt].accent, letterSpacing: ".06em" }}>{alt}</span>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: 8, color: "#707e92", letterSpacing: ".1em", whiteSpace: "nowrap" }}>{ALT[alt].name}</span>
              </div>
              <span style={{ position: "absolute", left: 96, top: 0, bottom: 0, width: 1, background: "#16202e" }} />
            </div>
          ))}
          {/* causal thread + punctuated kairos guides */}
          <svg viewBox={`0 0 ${plotW} ${H}`} preserveAspectRatio="none" style={{ position: "absolute", inset: 0, width: "100%", height: "100%", pointerEvents: "none" }}>
            {pts.filter(p => p.e.peak).map(p => <line key={p.e.id} x1={p.x} x2={p.x} y1="0" y2={H} stroke={C.gold} strokeOpacity=".26" strokeWidth="1.5" strokeDasharray="3 4" vectorEffect="non-scaling-stroke" />)}
            <polyline points={pts.map(p => `${p.x},${p.y}`).join(" ")} fill="none" stroke={C.cyan} strokeOpacity="0.34" strokeWidth="1.5" vectorEffect="non-scaling-stroke" />
          </svg>
          {/* nodes */}
          {pts.map(({ e, x, y }) => {
            const dim = (focus !== "all" && focus !== e.alt) || !matchQ(e, query);
            const accent = e.peak ? C.gold : (TYPE_COLOR[e.type] || ALT[e.alt].accent);
            const sz = e.peak ? 16 : 12;
            const li = LEDGER.findIndex(x => x.id === e.id);
            const selected = current === li;
            return (
              <React.Fragment key={e.id}>
              {selected && !dim && <span style={{ position: "absolute", left: `${(x / plotW) * 100}%`, top: y, width: sz + 11, height: sz + 11, marginLeft: -(sz + 11) / 2, marginTop: -(sz + 11) / 2, borderRadius: "50%", border: `1.5px solid ${C.cyan}`, boxShadow: `0 0 11px -1px ${C.cyan}`, pointerEvents: "none" }} />}
              <button onClick={() => { setCurrent && setCurrent(li); onOpen(e); }} title={e.label}
                style={{ position: "absolute", left: `${(x / plotW) * 100}%`, top: y, width: sz, height: sz, marginLeft: -sz / 2, marginTop: -sz / 2,
                  borderRadius: "50%", cursor: "pointer", padding: 0,
                  border: `1.5px solid ${e.peak ? "#1a1404" : "#020408"}`, background: accent,
                  boxShadow: `inset 0 1px 0 rgba(255,255,255,.5), 0 0 ${e.peak ? 10 : 6}px -1px ${accent}, 0 2px 5px rgba(0,0,0,.5)`,
                  opacity: dim ? 0.18 : 1, pointerEvents: dim ? "none" : "auto", transition: "opacity .3s, transform .15s" }}
                onMouseEnter={ev => { ev.currentTarget.style.transform = "scale(1.35)"; setHv({ x: (x / plotW) * 100, y, e }); }}
                onMouseLeave={ev => { ev.currentTarget.style.transform = "scale(1)"; setHv(h => (h && h.e.id === e.id ? null : h)); }}>
                {e.peak && <span style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 9, color: "#1a1404" }}>★</span>}
              </button>
              </React.Fragment>
            );
          })}
          {/* kairos / peak punctuation tags */}
          {pts.filter(p => p.e.peak).map(p => (
            <span key={p.e.id + "-tag"} style={{ position: "absolute", left: `${(p.x / plotW) * 100}%`, top: p.y - 20, transform: "translateX(-50%)",
              fontFamily: "var(--font-mono)", fontSize: 8, letterSpacing: ".08em", color: C.gold, whiteSpace: "nowrap", pointerEvents: "none",
              background: "rgba(8,12,18,.72)", padding: "1px 5px", borderRadius: 3 }}>★ {p.e.type.toUpperCase()}</span>
          ))}
          {/* mini collapsed-card hover preview */}
          {hv && (() => {
            const e = hv.e, below = hv.y < 90, accent = e.peak ? C.gold : (TYPE_COLOR[e.type] || ALT[e.alt].accent);
            return (
              <div style={{ position: "absolute", left: `${hv.x}%`, top: below ? hv.y + 16 : hv.y - 16, transform: `translate(-50%, ${below ? "0" : "-100%"})`,
                zIndex: 8, pointerEvents: "none", width: "max-content", maxWidth: 250,
                border: `1px solid ${accent}66`, borderRadius: 8, padding: "7px 10px",
                background: "linear-gradient(180deg, #0e151e, #0a0f16)", boxShadow: `0 12px 26px -10px rgba(0,0,0,.85), 0 0 0 1px rgba(0,0,0,.4), inset 0 1px 0 rgba(255,255,255,.05)` }}>
                <div style={{ fontFamily: "var(--font-mono)", fontSize: 9, letterSpacing: ".06em", color: accent, fontWeight: 700, marginBottom: 3, whiteSpace: "nowrap" }}>
                  {e.alt} {ALT[e.alt].name} · {String(e.type).toUpperCase()}{e.peak ? " · ★" : ""}
                </div>
                <div style={{ fontFamily: "var(--font-sans)", fontSize: 11.5, color: "#e2e8f0", lineHeight: 1.35 }}>{e.label}</div>
                <div style={{ fontFamily: "var(--font-mono)", fontSize: 9, color: "#8593a6", marginTop: 4, whiteSpace: "nowrap" }}>conf {e.conf}</div>
              </div>
            );
          })()}
        </div>
      </div>
      {/* build order axis label */}
      <div style={{ display: "flex", justifyContent: "center", padding: "6px 34px 2px 116px", fontFamily: "var(--font-mono)", fontSize: 9, color: "#707e92", letterSpacing: ".06em" }}>
        <span>genesis → build order → demo-ready</span>
      </div>
    </section>
  );
}

// ── Isometric explorer ────────────────────────────────────────────────────────
// Terraced topographic terrain: 5 altitude terraces stacked at increasing
// elevation (dim 1 · altitude). Each tile = a finding — hue = grade (dim 2),
// glow + lift = confidence (dim 3), border = risk (dim 4).
function IsoTile({ node, onOpen }) {
  const [h, setH] = React.useState(false);
  const c = node.risk === "HIGH" ? C.red : GRADE[node.grade];
  const lift = Math.round((node.conf - 50) * 0.5); // 0..24 — confidence relief
  const bloom = Math.max(8, Math.round(node.conf * 0.55)).toString(16).padStart(2, "0");
  const border = node.risk === "MED" ? "dashed" : "solid";
  return (
    <button onClick={() => onOpen(node)} onMouseEnter={() => setH(true)} onMouseLeave={() => setH(false)}
      data-pulse={node.risk === "HIGH" ? "" : undefined}
      style={{ position: "relative", transformStyle: "preserve-3d", transform: `translateZ(${lift + (h ? 10 : 0)}px)`, transition: "transform .2s",
        cursor: "pointer", padding: "7px 9px", minWidth: 92, maxWidth: 150, borderRadius: 7,
        border: `1.5px ${border} ${c}`, background: "linear-gradient(160deg, rgba(255,255,255,.07), rgba(0,0,0,.2)), linear-gradient(165deg, #11181f, #0a1016)",
        boxShadow: `inset 0 1px 0 rgba(255,255,255,.08), inset 0 -7px 12px -8px ${c}${bloom}, 0 ${6 + lift}px ${10 + lift}px -6px rgba(0,0,0,.7), 0 0 ${h ? 13 : 7}px -4px ${c}`,
        fontFamily: "var(--font-mono)", textAlign: "left" }}>
      <div style={{ fontSize: 10.5, color: "#e2e8f0", lineHeight: 1.25 }}>{node.lab}</div>
      <div style={{ fontSize: 9, color: "#8593a6", marginTop: 2, display: "flex", gap: 5 }}>
        <span style={{ fontWeight: 700, color: c }}>{node.grade}</span><span>·</span><span>{node.conf}</span>
      </div>
    </button>
  );
}

function IsoExplorer({ focus, onOpen }) {
  return (
    <section style={{ border: "1px solid #243042", borderRadius: 14, padding: "16px 14px 26px", overflow: "hidden",
      background: "radial-gradient(120% 100% at 50% -10%, #0c1a26, #0a1016 70%)",
      boxShadow: "inset 0 1px 0 rgba(255,255,255,.06), inset 0 -2px 10px rgba(0,0,0,.55), 0 5px 16px rgba(0,0,0,.4)" }}>
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "baseline", gap: 10, marginBottom: 4 }}>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 12, letterSpacing: ".08em", color: C.gold, fontWeight: 700 }}>ISOMETRIC EXPLORER</span>
        <span style={{ fontSize: 10, color: "#8593a6" }}>terrain — elevation = altitude · hue = grade · glow+lift = confidence · border = risk</span>
      </div>
      <div style={{ perspective: 1700, perspectiveOrigin: "50% 22%", padding: "60px 8px 30px", overflowX: "auto" }}>
        <div style={{ transformStyle: "preserve-3d", transform: "rotateX(56deg) rotateZ(-1deg)", display: "flex", flexDirection: "column", gap: 30, minWidth: 560, margin: "0 auto", width: "min(760px,100%)" }}>
          {ALT_ORDER.map((alt, i) => {
            const layer = LAYERS.find(l => l.id === alt);
            const meta = ALT[alt];
            const elev = (ALT_ORDER.length - 1 - i) * 34; // Exec highest terrace
            const dim = focus !== "all" && focus !== alt;
            return (
              <div key={alt} style={{ position: "relative", transformStyle: "preserve-3d", transform: `translateZ(${elev}px)`,
                opacity: dim ? 0.16 : 1, transition: "opacity .3s" }}>
                {/* terrace slab */}
                <div style={{ position: "relative", borderRadius: 12, padding: "16px 16px", border: `1px solid ${meta.accent}55`, borderLeft: `4px solid ${meta.accent}`,
                  background: `linear-gradient(${meta.accent}0d, rgba(0,0,0,.25)), repeating-linear-gradient(90deg, transparent 0 38px, ${meta.accent}0a 38px 39px), repeating-linear-gradient(0deg, transparent 0 38px, ${meta.accent}0a 38px 39px), linear-gradient(165deg, #0e151e, #090e15)`,
                  boxShadow: `inset 0 1px 0 rgba(255,255,255,.07), 0 ${20 + elev / 2}px ${24}px -16px rgba(0,0,0,.9), -8px 10px 0 -4px ${meta.accent}10` }}>
                  <div style={{ position: "absolute", left: 14, top: -22, transform: "rotateX(-56deg)", transformOrigin: "left bottom", fontFamily: "var(--font-mono)", display: "flex", alignItems: "center", gap: 7 }}>
                    <span style={{ width: 7, height: 7, borderRadius: "50%", background: meta.accent, boxShadow: `0 0 7px ${meta.accent}` }} />
                    <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: ".08em", color: meta.accent }}>{alt} · {meta.name}</span>
                    <span style={{ fontSize: 9, color: "#707e92" }}>{layer.findings.length}</span>
                  </div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 11, transformStyle: "preserve-3d" }}>
                    {layer.findings.map(n => <IsoTile key={n.id} node={n} onOpen={onOpen} />)}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

// ── Risk register — severity swimlanes on a week-ticked time axis, with all 18
// milestones overlaid: build events ride a BUILD lane up top, week gridlines tie
// each risk to the moment that caused it. ←→ step risks · ↑↓ change severity lane.
const SEV_ORDER = ["RUIN", "HIGH", "MED"];
const SEV_NAME = { RUIN: "RUIN-CLASS", HIGH: "HIGH", MED: "MEDIUM" };
const EV_GLYPH = { genesis: "✦", canon: "❖", milestone: "★", feat: "⊕", security: "⊘", fix: "✕", kairos: "◇" };

function RiskLanes({ query, sel = 0, setSel, sevFocus = "all", onOpen }) {
  const buildH = 38, laneH = 72, axisH = 0, gut = 92;
  const LEDGER_ALL = window.LEDGER || [];
  const total = Math.max(1, LEDGER_ALL.length - 1);
  // x-position by LEDGER index (build order), same spacing as ChainOfEvents
  const xpItem = (id) => {
    const idx = LEDGER_ALL.findIndex(x => x.id === id);
    return idx < 0 ? 50 : 3 + (idx / total) * 94;
  };
  const rks = [...RISKS];
  const evs = [...EVENTS];
  const laneDim = (sev) => sevFocus !== "all" && sev !== sevFocus;
  const sevCenter = (sev) => buildH + SEV_ORDER.indexOf(sev) * laneH + laneH / 2;
  const buildCenter = buildH / 2;
  const H = buildH + SEV_ORDER.length * laneH;
  const [hv, setHv] = React.useState(null);
  const StatusKey = ({ c, children }) => (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 5 }}>
      <span style={{ width: 8, height: 8, borderRadius: 2, transform: "rotate(45deg)", border: `2px solid ${c}`, background: "#0a1016" }} />
      <span style={{ color: "#8593a6" }}>{children}</span>
    </span>
  );
  const rows = [{ key: "BUILD", name: "BUILD EVENTS", color: C.cyan, cy: buildCenter, n: evs.length, glyph: "⌥" },
    ...SEV_ORDER.map(sev => ({ key: sev, name: SEV_NAME[sev], color: SEV[sev], cy: sevCenter(sev), n: rks.filter(r => r.sev === sev).length, glyph: "⚠" }))];

  return (
    <section style={{ border: "1px solid #243042", borderRadius: 14, padding: "14px 14px 10px",
      background: "linear-gradient(160deg, rgba(255,255,255,.05), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, #11181f, #0a1016)",
      boxShadow: "inset 0 1px 0 rgba(255,255,255,.08), inset 0 -2px 8px rgba(0,0,0,.5), 0 5px 16px rgba(0,0,0,.4)" }}>
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "baseline", gap: 10, marginBottom: 10 }}>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 12, letterSpacing: ".08em", color: C.red, fontWeight: 700 }}>RISK REGISTER</span>
        <span style={{ fontSize: 10, color: "#8593a6" }}>◆ risk in severity lanes · glyph = build-event overlay · ring = status · ← → step · ↑ ↓ focus lane</span>
      </div>
      <div style={{ display: "flex" }}>
        {/* gutter labels */}
        <div style={{ position: "relative", flex: `0 0 ${gut}px`, height: H + axisH }}>
          {rows.map(r => (
            <div key={r.key} style={{ position: "absolute", left: 0, top: r.cy, transform: "translateY(-50%)", display: "flex", flexDirection: "column", lineHeight: 1.15, opacity: r.key !== "BUILD" && laneDim(r.key) ? 0.28 : 1, transition: "opacity .3s" }}>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, fontWeight: 700, color: r.color, letterSpacing: ".04em", whiteSpace: "nowrap" }}>{r.glyph} {r.key}</span>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: 7.5, color: "#707e92", letterSpacing: ".06em", whiteSpace: "nowrap" }}>{r.name} · {r.n}</span>
            </div>
          ))}
        </div>
        {/* plot */}
        <div style={{ position: "relative", flex: "1 1 auto", height: H + axisH, minWidth: 0 }}>
          <div style={{ position: "absolute", left: 0, right: 0, top: buildH, height: 1, background: "#1b2a3d" }} />
          {SEV_ORDER.map((sev, i) => i > 0 && <div key={sev} style={{ position: "absolute", left: 0, right: 0, top: buildH + i * laneH, height: 1, background: "#13202e" }} />)}
          {/* build-overlay verticals */}
          <svg viewBox={`0 0 100 ${H}`} preserveAspectRatio="none" style={{ position: "absolute", left: 0, top: 0, width: "100%", height: H, pointerEvents: "none" }}>
            {evs.map(e => <line key={"o" + e.id} x1={xpItem(e.id)} x2={xpItem(e.id)} y1={buildH} y2={H} stroke={e.peak ? C.gold : C.cyan} strokeOpacity={e.peak ? ".24" : ".09"} strokeWidth="1" strokeDasharray={e.peak ? "3 4" : undefined} vectorEffect="non-scaling-stroke" />)}
          </svg>
          {/* build-event overlay markers (the other 11 milestones) */}
          {evs.map(e => {
            const dim = !matchQ(e, query);
            const accent = e.peak ? C.gold : ALT[e.alt].accent;
            const glyph = e.peak ? "★" : (EV_GLYPH[e.type] || "•");
            const sz = e.peak ? 17 : 14;
            return (
              <button key={e.id} onClick={() => onOpen(e)} title={`${e.alt} ${ALT[e.alt].name} · ${e.label}`}
                style={{ position: "absolute", left: `${xpItem(e.id)}%`, top: buildCenter, width: sz, height: sz, marginLeft: -sz / 2, marginTop: -sz / 2,
                  display: "inline-flex", alignItems: "center", justifyContent: "center", borderRadius: "50%", cursor: "pointer", padding: 0,
                  border: `1px solid ${e.peak ? "#1a1404" : "#03060b"}`, background: accent, color: "#04070c",
                  fontFamily: "var(--font-mono)", fontSize: e.peak ? 10 : 8, fontWeight: 700,
                  boxShadow: `0 0 ${e.peak ? 8 : 5}px -1px ${accent}, inset 0 1px 0 rgba(255,255,255,.4)`,
                  opacity: dim ? 0.14 : 0.95, pointerEvents: dim ? "none" : "auto", transition: "opacity .3s, transform .15s" }}
                onMouseEnter={ev => { ev.currentTarget.style.transform = "scale(1.25)"; setHv({ x: xpItem(e.id), cy: buildCenter, item: e, isRisk: false }); }}
                onMouseLeave={ev => { ev.currentTarget.style.transform = "scale(1)"; setHv(h => (h && h.item.id === e.id ? null : h)); }}>{glyph}</button>
            );
          })}
          {/* risk diamonds */}
          {rks.map((r, idx) => {
            const dim = !matchQ(r, query) || laneDim(r.sev);
            const c = SEV[r.sev], sc = STATUS[r.status];
            const sz = r.sev === "RUIN" ? 18 : 14;
            const selected = sel === idx;
            return (
              <React.Fragment key={r.id}>
                {selected && !dim && <span style={{ position: "absolute", left: `${xpItem(r.id)}%`, top: sevCenter(r.sev), width: sz + 13, height: sz + 13, marginLeft: -(sz + 13) / 2, marginTop: -(sz + 13) / 2, borderRadius: "50%", border: `1.5px solid ${C.cyan}`, boxShadow: `0 0 11px -1px ${C.cyan}`, pointerEvents: "none" }} />}
                <button onClick={() => { setSel && setSel(idx); onOpen(r); }} title={`${r.sev} · ${r.status} — ${r.risk}`}
                  data-pulse={r.status === "OPEN" ? "" : undefined}
                  style={{ position: "absolute", left: `${xpItem(r.id)}%`, top: sevCenter(r.sev), width: sz, height: sz, marginLeft: -sz / 2, marginTop: -sz / 2,
                    borderRadius: 2, cursor: "pointer", padding: 0, transform: "rotate(45deg)",
                    border: `2px solid ${sc}`, background: c,
                    boxShadow: `inset 0 1px 0 rgba(255,255,255,.4), 0 0 ${r.sev === "RUIN" ? 11 : 7}px -1px ${c}, 0 2px 5px rgba(0,0,0,.5)`,
                    opacity: dim ? 0.16 : 1, pointerEvents: dim ? "none" : "auto",
                    animation: r.status === "OPEN" ? "obs-pulse 1.8s infinite" : "none", transition: "opacity .3s, transform .15s" }}
                  onMouseEnter={ev => { ev.currentTarget.style.transform = "rotate(45deg) scale(1.32)"; setHv({ x: xpItem(r.id), cy: sevCenter(r.sev), item: r, isRisk: true }); }}
                  onMouseLeave={ev => { ev.currentTarget.style.transform = "rotate(45deg) scale(1)"; setHv(h => (h && h.item.id === r.id ? null : h)); }} />
              </React.Fragment>
            );
          })}
          {/* build-order axis — no dates */}
          {/* mini collapsed-card hover preview */}
          {hv && (() => {
            const x = hv.item, isRisk = hv.isRisk, below = hv.cy < 70;
            const accent = isRisk ? SEV[x.sev] : (x.peak ? C.gold : ALT[x.alt].accent);
            return (
              <div style={{ position: "absolute", left: `${hv.x}%`, top: below ? hv.cy + 16 : hv.cy - 16, transform: `translate(-50%, ${below ? "0" : "-100%"})`,
                zIndex: 8, pointerEvents: "none", width: "max-content", maxWidth: 250,
                border: `1px solid ${accent}66`, borderRadius: 8, padding: "7px 10px",
                background: "linear-gradient(180deg, #0e151e, #0a0f16)", boxShadow: `0 12px 26px -10px rgba(0,0,0,.85), 0 0 0 1px rgba(0,0,0,.4), inset 0 1px 0 rgba(255,255,255,.05)` }}>
                <div style={{ fontFamily: "var(--font-mono)", fontSize: 9, letterSpacing: ".06em", color: accent, fontWeight: 700, marginBottom: 3, whiteSpace: "nowrap" }}>
                  {isRisk ? `⚠ ${x.sev} · ${x.status}` : `${x.alt} ${ALT[x.alt].name} · ${String(x.type).toUpperCase()}`}
                </div>
                <div style={{ fontFamily: "var(--font-sans)", fontSize: 11.5, color: "#e2e8f0", lineHeight: 1.35 }}>{x.risk || x.label}</div>
                <div style={{ fontFamily: "var(--font-mono)", fontSize: 9, color: "#8593a6", marginTop: 4, whiteSpace: "nowrap" }}>
                  {isRisk ? `countered: ${x.how}` : `conf ${x.conf}`}
                </div>
              </div>
            );
          })()}
        </div>
      </div>
      {/* status ring legend */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 16, padding: "10px 4px 2px 92px", fontFamily: "var(--font-mono)", fontSize: 9.5, letterSpacing: ".04em" }}>
        <StatusKey c={STATUS.AVERTED}>AVERTED</StatusKey>
        <StatusKey c={STATUS.MITIGATED}>MITIGATED</StatusKey>
        <StatusKey c={STATUS.OPEN}>OPEN · standing</StatusKey>
      </div>
    </section>
  );
}

Object.assign(window, { ChainOfEvents, RiskLanes, RiskByLane, IsoExplorer });

// ── Risk register, by-lane face — severities as readable labelled lanes ───────
function RiskByLane({ sevFocus = "all", query, onOpen }) {
  return (
    <section style={{ border: "1px solid #243042", borderRadius: 14, padding: "14px 14px 10px",
      background: "linear-gradient(160deg, rgba(255,255,255,.05), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, #11181f, #0a1016)",
      boxShadow: "inset 0 1px 0 rgba(255,255,255,.08), inset 0 -2px 8px rgba(0,0,0,.5), 0 5px 16px rgba(0,0,0,.4)" }}>
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "baseline", gap: 10, marginBottom: 10 }}>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 12, letterSpacing: ".08em", color: C.red, fontWeight: 700 }}>RISK REGISTER</span>
        <span style={{ fontSize: 10, color: "#8593a6" }}>the card's back — each severity as a labelled lane · Focus dims the rest · ring = status · tap → card</span>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {SEV_ORDER.map(sev => {
          const dimLane = sevFocus !== "all" && sev !== sevFocus;
          const items = RISKS.filter(r => r.sev === sev);
          return (
            <div key={sev} style={{ display: "flex", alignItems: "center", gap: 10, padding: "7px 10px", borderRadius: 8,
              border: `1px solid ${SEV[sev]}2e`, borderLeft: `3px solid ${SEV[sev]}`,
              background: "linear-gradient(180deg, rgba(255,255,255,.015), rgba(0,0,0,.12))",
              opacity: dimLane ? 0.22 : 1, pointerEvents: dimLane ? "none" : "auto", transition: "opacity .3s" }}>
              <div style={{ flex: "0 0 96px", display: "flex", flexDirection: "column", lineHeight: 1.15 }}>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: 10.5, fontWeight: 700, color: SEV[sev] }}>⚠ {sev}</span>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: 8, color: "#707e92", letterSpacing: ".07em" }}>{SEV_NAME[sev]} · {items.length}</span>
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6, flex: "1 1 auto", minWidth: 0 }}>
                {items.length ? items.map(r => {
                  const dim = !matchQ(r, query);
                  const sc = STATUS[r.status];
                  return (
                    <button key={r.id} onClick={() => onOpen(r)} title={`${r.status} — ${r.risk}`} data-pulse={r.status === "OPEN" ? "" : undefined}
                      style={{ display: "inline-flex", alignItems: "center", gap: 7, padding: "4px 9px 4px 5px", borderRadius: 6, cursor: "pointer",
                        border: `1px solid ${sc}55`, background: `${SEV[sev]}10`, fontFamily: "var(--font-mono)",
                        opacity: dim ? 0.22 : 1, pointerEvents: dim ? "none" : "auto", transition: "opacity .3s, border-color .15s",
                        animation: r.status === "OPEN" ? "obs-pulse 1.8s infinite" : "none" }}
                      onMouseEnter={ev => ev.currentTarget.style.borderColor = sc}
                      onMouseLeave={ev => ev.currentTarget.style.borderColor = `${sc}55`}>
                      <span style={{ flex: "0 0 auto", width: 13, height: 13, transform: "rotate(45deg)", background: SEV[sev], border: `2px solid ${sc}`, boxShadow: `0 0 6px -1px ${SEV[sev]}` }} />
                      <span style={{ fontSize: 10, color: "#cbd5e1", maxWidth: 230, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{r.risk}</span>
                      <span style={{ flex: "0 0 auto", fontSize: 8.5, color: sc }}>{r.status}</span>
                    </button>
                  );
                }) : <span style={{ fontFamily: "var(--font-mono)", fontSize: 9, color: "#5b6675" }}>no risks</span>}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
