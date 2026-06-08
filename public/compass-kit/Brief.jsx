// ARCS Compass — Cartography Brief. The "earned fidelity" map of a decision.
// Recreates the spirit of src/app/brief/[receiptId]/page.tsx (two-column layout).

function Brief({ result, onBack }) {
  const r = result.reasoning || {};
  const fated = r.fated || {};
  const weather = Y_WEATHER[result.y_state] || Y_WEATHER.GREEN;
  const FATED_ORDER = [
    ["Facts", fated.facts], ["Assumptions", fated.assumptions],
    ["Tradeoffs", fated.tradeoffs], ["Emotions", fated.emotions], ["Direction", fated.direction],
  ];
  const pathColor = (s) => s === "selected" ? T.cyan : s === "blocked" ? `${T.red}55` : T.border;

  return (
    <div style={{ maxWidth: 880, margin: "0 auto", padding: "2.5rem 1.5rem 4rem" }}>
      <div style={{ marginBottom: "1.5rem", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <Wordmark section="Cartography Brief" />
        <Button variant="ghost" size="sm" onClick={onBack}>← Back to receipt</Button>
      </div>

      {/* Title block */}
      <div style={{ marginBottom: "2rem" }}>
        <Label style={{ marginBottom: "0.75rem", color: weather.color }}>{weather.icon} {weather.label} · {result.render_resolution}</Label>
        <h1 style={{ fontFamily: T.sans, fontSize: "1.5rem", fontWeight: 600, color: T.fg1, margin: "0 0 0.75rem", lineHeight: 1.3, letterSpacing: "-0.01em" }}>{result.question}</h1>
        <p style={{ fontFamily: T.sans, fontSize: "1.0625rem", color: T.fg1, margin: 0, lineHeight: 1.6, fontWeight: 500 }}>
          <span style={{ color: T.cyan }}>True North · </span>{result.true_north}
        </p>
      </div>

      {/* Two-column */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 280px", gap: "1.25rem", alignItems: "start" }}>
        {/* Main column */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          {/* FATED */}
          <Card>
            <Label style={{ marginBottom: "1rem" }}>FATED Decomposition</Label>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              {FATED_ORDER.map(([k, v]) => (
                <div key={k} style={{ display: "grid", gridTemplateColumns: "92px 1fr", gap: "0.75rem", alignItems: "baseline" }}>
                  <span style={{ fontFamily: T.mono, fontSize: "0.6rem", letterSpacing: "0.1em", textTransform: "uppercase", color: T.fg4 }}>{k}</span>
                  <span style={{ fontFamily: T.sans, fontSize: "0.85rem", color: T.fg2, lineHeight: 1.55 }}>{v}</span>
                </div>
              ))}
            </div>
          </Card>

          {/* Terrain paths */}
          <Card>
            <Label style={{ marginBottom: "1rem" }}>Terrain Paths</Label>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.875rem" }}>
              {r.paths?.map(p => (
                <div key={p.id} style={{ paddingLeft: "0.875rem", borderLeft: `2px solid ${pathColor(p.status)}` }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.2rem" }}>
                    <span style={{ fontFamily: T.sans, fontSize: "0.875rem", fontWeight: 600, color: p.status === "selected" ? T.fg1 : T.fg3, textDecoration: p.status === "blocked" ? "line-through" : "none" }}>{p.title}</span>
                    <Badge label={p.tag} color={p.status === "selected" ? T.cyan : T.steel} register="light" />
                    {p.status === "selected" && <span style={{ fontFamily: T.mono, fontSize: "0.55rem", letterSpacing: "0.1em", color: T.cyan }}>SELECTED LINE</span>}
                  </div>
                  <div style={{ fontFamily: T.sans, fontSize: "0.8rem", color: T.fg3, lineHeight: 1.5 }}>{p.detail}</div>
                </div>
              ))}
            </div>
          </Card>

          {/* Court */}
          {r.court && (
            <Card>
              <Label style={{ marginBottom: "1rem" }}>Constitutional Court</Label>
              {r.court.map((c, i) => (
                <div key={i} style={{ display: "flex", gap: "0.75rem", marginBottom: "0.5rem", fontSize: "0.82rem" }}>
                  <span style={{ fontFamily: T.mono, color: c.verdict === "PASS" ? T.green : c.verdict === "TENSION" ? T.gold : T.red, fontWeight: 700, minWidth: 64 }}>{c.verdict}</span>
                  <span style={{ color: T.fg2 }}><strong style={{ color: T.fg1 }}>{c.name}</strong> — {c.detail}</span>
                </div>
              ))}
              {r.court_verdict && <div style={{ marginTop: "0.75rem", paddingTop: "0.75rem", borderTop: `1px solid ${T.border}`, fontSize: "0.82rem", color: T.fg3, fontStyle: "italic" }}>{r.court_verdict}</div>}
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem", position: "sticky", top: "1rem" }}>
          <Card padding="compact" style={{ padding: "1rem 1.25rem" }}>
            <Label style={{ marginBottom: "0.75rem" }}>Conviction</Label>
            <div style={{ fontFamily: T.sans, fontSize: "2.5rem", fontWeight: 700, color: nciColor(result.nci_score), lineHeight: 1 }}>{result.nci_score}</div>
            <div style={{ fontFamily: T.mono, fontSize: "0.65rem", color: T.fg4, marginTop: "0.35rem", letterSpacing: "0.08em" }}>NCI / 100 · COHERENCE {result.coherence_pct}%</div>
            <div style={{ height: 1, background: T.border, margin: "1rem 0" }} />
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {[["Mode", result.decision_mode], ["Door", result.door_class], ["Bayesian risk", (r.advisors?.bayesian_risk_pct ?? "—") + "%"]].map(([k, v]) => (
                <div key={k} style={{ display: "flex", justifyContent: "space-between", fontFamily: T.mono, fontSize: "0.7rem" }}>
                  <span style={{ color: T.fg4, textTransform: "uppercase", letterSpacing: "0.06em" }}>{k}</span>
                  <span style={{ color: T.fg2 }}>{v}</span>
                </div>
              ))}
            </div>
          </Card>

          <Card padding="compact" style={{ padding: "1rem 1.25rem" }}>
            <Label style={{ marginBottom: "0.75rem" }}>Tributaries</Label>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.625rem" }}>
              {result.tributaries?.map((t, i) => {
                const c = t.type === "meta" ? T.cyan : t.type === "challenge" ? T.red : T.gold;
                return (
                  <div key={i}>
                    <span style={{ fontFamily: T.mono, fontSize: "0.55rem", color: c, letterSpacing: "0.1em", textTransform: "uppercase", fontWeight: 700 }}>{t.label}</span>
                    <div style={{ fontFamily: T.sans, fontSize: "0.75rem", color: T.fg3, lineHeight: 1.45, marginTop: "0.2rem" }}>{t.prompt}</div>
                  </div>
                );
              })}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

window.Brief = Brief;
