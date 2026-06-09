// ARCS Observatory — altitude deck, scored nodes, risk register, detail sheet.

const RISK_BORDER = { LOW: "solid", MED: "dashed", HIGH: "solid" };
// provenance links — Source cells point at the repo file (best-effort blob URL);
// prov IDs (P01–P28) point at the provenance ledger that substantiates the claim.
// lazy: window.REPO is installed by hydrateObservatory() at runtime (hot-swappable),
// so these must read it on call, not at module-load (which happens before hydrate).
const repoBase = () => String(window.REPO || "https://github.com/flashesofbrilliance/arcs-v9/commit/").replace(/\/commit\/$/, "");
const provLedger = () => `${repoBase()}/blob/main/docs/provenance-ledger.md`;
function srcHref(src) {
  const m = String(src || "").match(/^([\w./-]+\.[A-Za-z]+)(?::(\d+)(?:-(\d+))?)?$/);
  if (!m) return null; // commands / multi-source observations aren't single files
  let h = `${repoBase()}/blob/main/${m[1]}`;
  if (m[2]) h += `#L${m[2]}` + (m[3] ? `-L${m[3]}` : "");
  return h;
}
// resolve a provenance Source cell to a URL given what was Observed.
// commit SHAs → the GitHub commit; file paths → blob URL (srcHref).
function obsHref(src, observed) {
  if (String(observed).toLowerCase() === "commit" && /^[0-9a-f]{7,40}$/i.test(String(src)))
    return `${repoBase()}/commit/${src}`;
  return srcHref(src);
}
// a real provenance-ledger id (P01–P28); "—" / blanks are not linkable.
const isProvId = (v) => /^P\d+$/i.test(String(v || "").trim());
// confidence → subtle inset-bottom bloom intensity (underlit LED, never a halo)
const hx = (n) => Math.max(0, Math.min(255, Math.round(n))).toString(16).padStart(2, "0");
const confBloom = (conf) => hx((conf - 30) * 0.7);

function ScoreNode({ node, onOpen }) {
  const [h, setH] = React.useState(false);
  const c = GRADE[node.grade];
  const high = node.risk === "HIGH";
  return (
    <button onClick={() => onOpen(node)} onMouseEnter={() => setH(true)} onMouseLeave={() => setH(false)}
      data-pulse={high ? "" : undefined}
      style={{ position: "relative", textAlign: "left", cursor: "pointer", border: `1.5px ${RISK_BORDER[node.risk]} ${high ? C.red : c}`,
        borderRadius: 9, background: "linear-gradient(160deg, rgba(255,255,255,.05), rgba(255,255,255,.01) 40%, rgba(0,0,0,.18)), linear-gradient(165deg, #11181f, #0a1016)", padding: "7px 10px", minWidth: 120, maxWidth: 240, flex: "1 1 150px",
        boxShadow: high ? undefined : `inset 0 1px 0 rgba(255,255,255,.05), inset 0 -8px 13px -9px ${c}${confBloom(node.conf)}, 0 0 ${h ? 13 : 8}px -4px ${c}, 0 4px 11px rgba(0,0,0,.4)`,
        transform: h ? "translateY(-2px)" : "none", transition: "transform .25s, box-shadow .2s", fontFamily: "var(--font-mono)",
        animation: high ? "obs-pulse 1.8s infinite" : "none" }}>
      <div style={{ fontSize: 11.5, color: "#e2e8f0", lineHeight: 1.3 }}>{node.lab}</div>
      <div style={{ fontSize: 9.5, color: "#8593a6", letterSpacing: ".04em", marginTop: 3, display: "flex", gap: 6 }}>
        <span style={{ fontWeight: 700, color: c }}>{node.grade}</span><span>conf {node.conf}</span><span>{node.risk}</span>
      </div>
    </button>
  );
}

function AltitudePlane({ layer, dim, iso, query, onOpen }) {
  const meta = ALT[layer.id];
  const findings = layer.findings.filter(n => matchQ(n, query));
  return (
    <section style={{ position: "relative", border: "1px solid #243042", borderLeft: `${iso ? 4 : 3}px solid ${meta.accent}`, borderRadius: 14,
      padding: "12px 14px 14px", background: "linear-gradient(160deg, rgba(255,255,255,.05), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, #11181f, #0a1016)",
      boxShadow: iso ? `inset 0 1px 0 rgba(255,255,255,.06), 0 24px 38px -22px #000, -9px 12px 0 -6px ${meta.accent}12` : "inset 0 1px 0 rgba(255,255,255,.08), inset 0 -2px 8px rgba(0,0,0,.5), 0 5px 16px rgba(0,0,0,.4)",
      opacity: dim ? 0.16 : 1, pointerEvents: dim ? "none" : "auto", transition: "opacity .3s, box-shadow .3s" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
        <span style={{ width: 8, height: 8, borderRadius: "50%", background: meta.accent, boxShadow: `0 0 8px ${meta.accent}` }} />
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 12, letterSpacing: ".08em", color: meta.accent, fontWeight: 600 }}>{meta.name}</span>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, color: "#8593a6" }}>{findings.length} findings</span>
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 9 }}>
        {findings.length ? findings.map(n => <ScoreNode key={n.id} node={n} onOpen={onOpen} />)
          : <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, color: "#5b6675" }}>no matching findings</span>}
      </div>
    </section>
  );
}

function Deck({ focus, iso, query, onOpen }) {
  return (
    <div style={{ transformOrigin: "top center", transition: "transform .4s ease",
      transform: iso ? "perspective(1500px) rotateX(38deg) rotateZ(-1deg)" : "none",
      display: "flex", flexDirection: "column", gap: 18 }}>
      {LAYERS.map(l => <AltitudePlane key={l.id} layer={l} iso={iso} dim={focus !== "all" && focus !== l.id} query={query} onOpen={onOpen} />)}
    </div>
  );
}

function RiskNode({ rk, onOpen }) {
  const [h, setH] = React.useState(false);
  const sc = STATUS[rk.status];
  return (
    <button onClick={() => onOpen(rk)} onMouseEnter={() => setH(true)} onMouseLeave={() => setH(false)}
      style={{ position: "relative", textAlign: "left", cursor: "pointer", flex: "1 1 220px", minWidth: 200, maxWidth: 340,
        border: `1px solid ${sc}45`, borderLeft: `3px solid ${sc}`, borderRadius: 12, padding: "9px 11px", background: "linear-gradient(160deg, rgba(255,255,255,.05), rgba(255,255,255,.01) 40%, rgba(0,0,0,.18)), linear-gradient(165deg, #11181f, #0a1016)",
        boxShadow: `inset 0 1px 0 rgba(255,255,255,.05), inset 0 -8px 13px -9px ${sc}40, 0 0 ${h ? 12 : 8}px -4px ${sc}, 0 4px 12px rgba(0,0,0,.4)`, transform: h ? "translateY(-2px)" : "none", transition: "transform .25s, box-shadow .2s", fontFamily: "var(--font-mono)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 5 }}>
        <span style={{ display: "flex", alignItems: "center", gap: 7 }}>
          <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: ".08em", padding: "1px 6px", borderRadius: 4, background: "rgba(255,255,255,.06)", color: SEV[rk.sev] }}>{rk.sev}</span>
        </span>
        <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: ".06em", padding: "1px 7px", border: `1px solid ${sc}`, borderRadius: 5, color: sc }}>{rk.status}</span>
      </div>
      <div style={{ fontSize: 12, fontWeight: 700, color: "#e2e8f0", lineHeight: 1.3 }}>{rk.risk}</div>
      <div style={{ fontSize: 9.5, color: C.cyan, marginTop: 3, letterSpacing: ".03em" }}>{rk.how}</div>
      <div style={{ fontSize: 9.5, color: STATUS[rk.status], marginTop: 6, letterSpacing: ".04em" }}>{rk.status}</div>
    </button>
  );
}

function RiskRegister({ onOpen }) {
  return (
    <section style={{ position: "relative", border: "1px solid #22324d", borderRadius: 12, padding: "12px 14px 14px",
      background: "linear-gradient(180deg,rgba(14,22,38,.92),rgba(9,14,24,.92))" }}>
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "baseline", gap: 10, marginBottom: 12 }}>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 12, letterSpacing: ".08em", color: C.red, fontWeight: 700 }}>RISK REGISTER</span>
        <span style={{ fontSize: 10, color: "#8593a6" }}>ruin-paths · severity × status — green AVERTED · gold MITIGATED · red OPEN</span>
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
        {RISKS.map(r => <RiskNode key={r.id} rk={r} onOpen={onOpen} />)}
      </div>
    </section>
  );
}

// ── Detail sheet (slide-up) ───────────────────────────────────────────────────
// Header mirrors the ledger-row lockup: kicker + title at left, commit / provenance
// pinned top-right. Type, spacing, color all conform to colors_and_type.css.
const MetaPill = ({ label, value, color }) => (
  <span style={{ display: "inline-flex", alignItems: "baseline", gap: 6, fontFamily: "var(--font-mono)", fontSize: 11,
    padding: "4px 10px", borderRadius: 6, border: `1px solid ${color}45`, background: `${color}12` }}>
    <span style={{ fontSize: 9, color: "var(--fg4)", letterSpacing: ".1em", textTransform: "uppercase" }}>{label}</span>
    <span style={{ color, fontWeight: 700 }}>{value}</span>
  </span>
);

function Sheet({ item, onClose }) {
  const open = !!item;
  const isNode = !!(item && item.grade);
  const isRisk = !!(item && item.sev && !item.grade);
  const isEvent = !!(item && !isNode && !isRisk);
  const accent = !item ? C.cyan
    : isNode ? (item.risk === "HIGH" ? C.red : GRADE[item.grade])
    : isRisk ? SEV[item.sev]
    : (item.peak ? C.gold : (ALT[item.alt] && ALT[item.alt].accent) || C.cyan);
  const kicker = !item ? ""
    : isNode ? `${item.kind} · scored finding`
    : isRisk ? `ruin-path · ${item.sev}`
    : `${item.alt} · ${ALT[item.alt] && ALT[item.alt].name}${item.peak ? " · ★ peak" : ""}`;
  const leadProv = isNode && item.prov && item.prov[0] && isProvId(item.prov[0][3]) ? item.prov[0][3] : null;

  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 50, visibility: open ? "visible" : "hidden", pointerEvents: open ? "auto" : "none" }}>
      <div onClick={onClose} style={{ position: "absolute", inset: 0, background: "rgba(2,4,8,.6)", opacity: open ? 1 : 0, transition: "opacity .3s" }} />
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, transform: open ? "translateY(0)" : "translateY(100%)", transition: "transform .35s cubic-bezier(.2,.8,.2,1)",
        background: "linear-gradient(180deg, #0d1117, #060a11)", borderTop: `1px solid ${accent}`,
        boxShadow: `0 -1px 0 ${accent}40, 0 -18px 40px -18px rgba(0,0,0,.85)`, padding: "18px 20px 28px", maxHeight: "82vh", overflow: "auto" }}>
        {item && (
          <div style={{ maxWidth: 880, margin: "0 auto" }}>
            {/* header lockup — title left · commit/prov + close pinned top-right */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 16 }}>
              <div style={{ minWidth: 0 }}>
                <div style={{ fontFamily: "var(--font-mono)", fontSize: 10, letterSpacing: ".12em", textTransform: "uppercase", color: accent, fontWeight: 700, marginBottom: 6 }}>{kicker}</div>
                <h3 style={{ margin: 0, fontFamily: "var(--font-sans)", fontSize: 17, fontWeight: 600, letterSpacing: "-0.01em", color: "var(--fg1)", lineHeight: 1.25 }}>{item.lab || item.risk || item.label}</h3>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 8, flex: "0 0 auto" }}>
                {isRisk && !item.sha && (
                  <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: STATUS[item.status], padding: "5px 10px", borderRadius: 6, border: `1px solid ${STATUS[item.status]}45`, background: `${STATUS[item.status]}10`, whiteSpace: "nowrap" }}>{item.status}</span>
                )}
                {isNode && leadProv && <a href={provLedger()} target="_blank" rel="noopener" title="open the provenance ledger" style={{ display: "inline-flex", alignItems: "center", gap: 5, fontFamily: "var(--font-mono)", fontSize: 11, color: C.cyan, padding: "5px 10px", borderRadius: 6, border: `1px solid ${C.cyan}45`, background: `${C.cyan}10`, whiteSpace: "nowrap", textDecoration: "none" }}>prov {leadProv}<span style={{ fontSize: 9 }}>↗</span></a>}
                <button onClick={onClose} aria-label="close" style={{ width: 30, height: 30, borderRadius: 6, border: "1px solid #243042", background: "linear-gradient(180deg, #11181f, #0a1016)", color: "var(--fg3)", cursor: "pointer", fontFamily: "var(--font-mono)", fontSize: 12, display: "inline-flex", alignItems: "center", justifyContent: "center" }}>✕</button>
              </div>
            </div>

            {/* meta pills — Badge register */}
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", margin: "13px 0 14px" }}>
              {isNode && <>
                <MetaPill label="NCI" value={item.grade} color={GRADE[item.grade]} />
                <MetaPill label="confidence" value={item.conf} color={C.cyan} />
                <MetaPill label="risk" value={item.risk} color={item.risk === "HIGH" ? C.red : item.risk === "MED" ? C.gold : C.green} />
              </>}
              {isRisk && <>
                <MetaPill label="severity" value={item.sev} color={SEV[item.sev]} />
                <MetaPill label="status" value={item.status} color={STATUS[item.status]} />
                <MetaPill label="countered by" value={item.how} color={C.cyan} />
              </>}
              {isEvent && <>
                <MetaPill label="altitude" value={`${item.alt} · ${ALT[item.alt] && ALT[item.alt].name}`} color={ALT[item.alt] && ALT[item.alt].accent} />
                <MetaPill label="type" value={item.type} color={TYPE_COLOR[item.type] || C.steel} />
                {item.conf && <MetaPill label="confidence" value={item.conf} color={C.cyan} />}
              </>}
            </div>

            <p style={{ color: "var(--fg2)", maxWidth: "76ch", margin: "0 0 14px", lineHeight: 1.6, fontFamily: "var(--font-sans)", fontSize: 13 }}>{item.desc || item.note}</p>

            {isNode && item.prov && (
              <div>
                <div style={{ fontFamily: "var(--font-mono)", fontSize: 9, letterSpacing: ".12em", textTransform: "uppercase", color: "var(--fg4)", marginBottom: 7 }}>Provenance · reproducible</div>
                <div style={{ overflowX: "auto", border: "1px solid #1a2533", borderRadius: 8 }}>
                  <table style={{ borderCollapse: "collapse", width: "100%", minWidth: 520, fontSize: 11.5, fontFamily: "var(--font-mono)" }}>
                    <thead><tr>{["Claim", "Source", "Observed", "ID"].map(th => <th key={th} style={{ padding: "7px 10px", textAlign: "left", color: C.cyan, fontWeight: 500, letterSpacing: ".04em", borderBottom: "1px solid #1a2533", background: "rgba(255,255,255,.015)" }}>{th}</th>)}</tr></thead>
                    <tbody>{item.prov.map((row, i) => (
                      <tr key={i}>
                        <td style={tdS}>{row[0]}</td>
                        <td style={tdS}>{(() => { const h = obsHref(row[1], row[2]); return h
                          ? <a href={h} target="_blank" rel="noopener" style={{ color: C.green, fontSize: 11, wordBreak: "break-word", textDecoration: "none" }}>{row[1]}<span style={{ fontSize: 9 }}>↗</span></a>
                          : <code style={{ color: C.green, fontSize: 11, wordBreak: "break-word" }}>{row[1]}</code>; })()}</td>
                        <td style={{ ...tdS, color: C.gold }}>{row[2]}</td>
                        <td style={tdS}>{isProvId(row[3])
                          ? <a href={provLedger()} target="_blank" rel="noopener" title="provenance ledger" style={{ color: "var(--fg3)", textDecoration: "none" }}>{row[3]}<span style={{ fontSize: 9, color: C.cyan }}> ↗</span></a>
                          : <span style={{ color: "var(--fg4)" }}>{row[3]}</span>}</td>
                      </tr>
                    ))}</tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
const tdS = { padding: "7px 10px", textAlign: "left", verticalAlign: "top", color: "var(--fg2)", borderBottom: "1px solid #131c28" };

Object.assign(window, { Deck, RiskRegister, Sheet });
