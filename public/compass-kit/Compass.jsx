// ARCS Compass — the Question Compass form, recomposed on the updated atoms
// (Field · SegmentedSlider · ChipToggle · Button) in a tight Swiss column.

const HORIZONS = { TODAY: "Today", THIS_WEEK: "This week", THIS_QUARTER: "This quarter", ONE_TO_THREE_YEARS: "1–3 years" };
const STAKE_OPTS = [
  { value: "LOW", label: "Low", accent: "green" },
  { value: "MEDIUM", label: "Medium", accent: "gold" },
  { value: "HIGH", label: "High", accent: "red" },
];
const PROTECTION = ["Cash", "Time", "Reputation", "Relationship", "Health", "Optionality"];
const EXAMPLES = [
  "Should I take the Series A now or extend runway six months?",
  "Do I make the leverage hire this quarter or wait?",
];

function CompassForm({ onResult, initialQuestion }) {
  const [question, setQuestion] = React.useState(initialQuestion || "");
  const [horizon, setHorizon] = React.useState("THIS_WEEK");
  const [stakes, setStakes] = React.useState("MEDIUM");
  const [loading, setLoading] = React.useState(false);
  const [calibrated, setCalibrated] = React.useState(false);
  const [protecting, setProtecting] = React.useState([]);
  const [step, setStep] = React.useState(0);

  function run(e) {
    e && e.preventDefault();
    if (!question.trim()) return;
    setLoading(true); setStep(0);
    let s = 0;
    const iv = setInterval(() => { s += 1; setStep(s); if (s >= 5) clearInterval(iv); }, 180);
    setTimeout(() => { clearInterval(iv); setLoading(false); onResult(window.mockCompass(question, { stakes, horizon })); }, 1100);
  }
  function toggleProtect(c) {
    setProtecting(p => p.includes(c) ? p.filter(x => x !== c) : p.length >= 2 ? p : [...p, c]);
  }

  return (
    <div style={{ maxWidth: 620, margin: "0 auto", padding: "2rem 1.5rem 4rem", containerType: "inline-size" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingBottom: "1rem" }}>
        <Wordmark section="Question Compass" />
        <Button variant="ghost" size="sm">History</Button>
      </div>
      <Rule style={{ marginBottom: "2rem" }} />

      <SectionLabel index="01" style={{ marginBottom: "0.9rem" }}>State the decision</SectionLabel>
      <h1 style={{ fontFamily: T.sans, fontSize: "5.4cqw", whiteSpace: "nowrap", fontWeight: 600, color: T.fg1, margin: "0 0 1.5rem", lineHeight: 1.12, letterSpacing: "-0.02em" }}>
        What are you really trying to decide?
      </h1>

      <form onSubmit={run}>
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          <Field as="textarea" rows={3} label="Decision" value={question} onChange={e => setQuestion(e.target.value)}
            placeholder="Type the real fork — not the symptom." />

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
            <Picker label="Horizon" value={horizon} options={Object.keys(HORIZONS).map(h => ({ value: h, label: HORIZONS[h] }))} onChange={setHorizon} />
            <div style={{ position: "relative", borderRadius: 6, padding: "12px 14px 13px",
              border: "1px solid #2a3647",
              background: "linear-gradient(160deg, rgba(255,255,255,.06), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, #131b23, #0a1016)",
              boxShadow: "inset 0 1px 0 rgba(255,255,255,.14), inset 0 -2px 6px rgba(0,0,0,.55), 0 5px 14px rgba(0,0,0,.5)" }}>
              <span style={{ display: "block", fontFamily: T.mono, fontSize: 11, color: T.fg2, textTransform: "uppercase", letterSpacing: "0.1em", fontWeight: 700, marginBottom: 8 }}>Stakes</span>
              <SegmentedSlider options={STAKE_OPTS} value={stakes} onChange={setStakes} />
            </div>
          </div>
        </div>

        <div style={{ margin: "1.25rem 0" }}>
          <SectionLabel index="02" color={T.gold} style={{ marginBottom: "0.75rem" }}>Calibrate · optional</SectionLabel>
          {!calibrated ? (
            <Button variant="gold" glyph="◈" onClick={() => setCalibrated(true)} style={{ width: "100%" }}>Sharpen the read</Button>
          ) : (
            <div>
              <div style={{ fontFamily: T.mono, fontSize: 10, color: T.fg4, letterSpacing: "0.06em", marginBottom: "0.6rem" }}>What can't you afford to lose? &nbsp;·&nbsp; pick up to 2</div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "0.5rem" }}>
                {PROTECTION.map(c => <ChipToggle key={c} label={c} selected={protecting.includes(c)} onClick={() => toggleProtect(c)} style={{ width: "100%", justifyContent: "center" }} />)}
              </div>
            </div>
          )}
        </div>

        <Button type="submit" variant="primary" size="lg" glyph={loading ? "~" : "⊕"} disabled={loading || !question.trim()} style={{ width: "100%" }}>
          {loading ? "Running L0–L5 pipeline…" : <>Get True North&nbsp;<span style={{ fontFamily: T.sans, fontWeight: 500, opacity: .75 }}>→</span></>}
        </Button>

        {loading && (
          <div style={{ marginTop: "1rem", display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <Spinner size={18} />
              <span style={{ fontFamily: T.mono, fontSize: 11, letterSpacing: "0.08em", color: T.cyan }}>RUNNING L0–L5…</span>
            </div>
            <StepProgress current={step} />
          </div>
        )}
      </form>

      {!question && (
        <div style={{ marginTop: "2rem" }}>
          <SectionLabel style={{ marginBottom: "0.75rem" }}>Or start from an example</SectionLabel>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            {EXAMPLES.map(ex => (
              <TributaryTile key={ex} label="Example" glyph="⊕" color={T.cyan} onClick={() => setQuestion(ex)}>{ex}</TributaryTile>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

window.CompassForm = CompassForm;
