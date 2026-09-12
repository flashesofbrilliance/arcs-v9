import { notFound, redirect } from "next/navigation"
import { prisma } from "@/lib/db"
import { pageViewerAllowed, loadScanSpec, loadTriggerSpec, tierOf } from "@/lib/jobs"
import { surface, border, text, signal, font } from "@/ui/tokens"
import { Wordmark } from "@/ui/Wordmark"
import { Rule } from "@/ui/Rule"
import Link from "next/link"

// jobs.arcs.care/<jobid> — the Role Scan: the Profile Scan (who) overlaid on the
// Target Scan (where to aim) for ONE posting. Same HUD grammar as the two
// scans (mast + status LEDs, telemetry band, stated-vs-observed comparator,
// thread assessment, rubric ledger, one assertion, provenance), generated from
// the row in Prisma and the two specs. Server-rendered, inline styles, gated.
export const dynamic = "force-dynamic"

type Dims = Record<string, number>
const mono = font.mono
const sans = font.sans
const fg1 = text.primary, fg2 = text.secondary, fg3 = text.dimmed, fg4 = text.muted
const PANEL = "linear-gradient(165deg,#ffffff08,#ffffff02 40%,#00000030), #0d1117"
const PANEL_SHADOW = "inset 0 1px 0 #ffffff0e, 0 14px 34px -22px #000c"

const eyebrow: React.CSSProperties = { fontFamily: mono, fontSize: 10, fontWeight: 700, letterSpacing: ".16em", textTransform: "uppercase" }
const src: React.CSSProperties = { fontFamily: mono, fontSize: 9, letterSpacing: ".05em", color: fg4 }
const panel: React.CSSProperties = { background: PANEL, border: `1px solid ${border.subtle}`, borderRadius: 10, boxShadow: PANEL_SHADOW }
const secHd = (n: string, t: string, color: string, gloss: string) => (
  <div style={{ display: "flex", alignItems: "baseline", gap: 12, margin: "56px 0 16px" }}>
    <span style={{ fontFamily: mono, fontSize: 11, fontWeight: 700, color: fg4 }}>{n}</span>
    <span style={{ fontFamily: mono, fontSize: 13, fontWeight: 700, letterSpacing: ".14em", textTransform: "uppercase", color }}>{t}</span>
    <span style={{ flex: 1, height: 1, background: `linear-gradient(90deg, ${border.subtle}, transparent)` }} />
    <span style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: ".08em", color: fg4, textTransform: "uppercase", whiteSpace: "nowrap" }}>{gloss}</span>
  </div>
)
const led = (color: string) => <span style={{ display: "inline-block", width: 7, height: 7, borderRadius: "50%", verticalAlign: 1, marginRight: 6, background: color, boxShadow: `0 0 8px 1px ${color}` }} />
const parse = <T,>(s: string | null, fb: T): T => { try { return s ? (JSON.parse(s) as T) : fb } catch { return fb } }

export default async function RoleScanPage({ params }: { params: Promise<{ jobid: string }> }) {
  const { jobid } = await params
  if (!(await pageViewerAllowed())) redirect(`/compass?next=/jobs/${jobid}`)
  const row = await prisma.jobOpportunity.findUnique({ where: { jobid }, include: { swipe: true, forge: true } })
  if (!row) notFound()
  const spec = loadScanSpec()
  const trig = loadTriggerSpec()
  const dims = parse<Dims>(row.dims, {})
  const gates = parse<string[]>(row.gates, [])
  const hits = parse<Record<string, string[]>>(row.jdHits, {})
  const DIMS = spec?.rubric.dims ?? []
  const MAX = spec?.rubric.max ?? 72
  const total = DIMS.reduce((t, d) => t + (dims[d.key] ?? 0) * d.weight, 0)
  const tier = row.band === "UNSCORED" ? null : tierOf(row.composite, spec)
  const scored = row.band !== "UNSCORED" && row.composite != null
  const quads = (spec?.quads ?? []).map((q) => { let p = 0, m = 0; q.dims.forEach((k) => { const d = DIMS.find((x) => x.key === k); if (d) { p += (dims[k] ?? 0) * d.weight; m += 3 * d.weight } }); return { ...q, p, m, ratio: m ? p / m : 0 } }).sort((a, b) => b.ratio - a.ratio)
  const weakest = [...DIMS].map((d) => ({ ...d, sc: dims[d.key] ?? 0 })).sort((a, b) => a.sc - b.sc || b.weight - a.weight)
  const strongest = [...DIMS].map((d) => ({ ...d, sc: dims[d.key] ?? 0 })).sort((a, b) => b.sc * b.weight - a.sc * a.weight)
  const archetype = spec?.archetypes.find((a) => (row.alertQuery ?? "").includes("forward") ? a.id.startsWith("forward") : (row.alertQuery ?? "").includes("applied") ? a.id.startsWith("applied") : (row.alertQuery ?? "").includes("product") ? a.id.startsWith("ai-native") : a.id.startsWith("solutions"))
  const bandColor = row.band === "PURSUE" ? signal.green : row.band === "CONSIDER" ? signal.gold : row.band === "PASS" ? signal.red : fg3
  const forge = row.forge
  const verdict = !scored ? "Unscored. Nothing is asserted until the posting is read and the rubric runs."
    : gates.length ? `Hard gate fired (${gates.join(", ")}). Score is irrelevant; do not load the rod.`
    : tier === 1 ? "Load the rod. Full omakase: tailor, size, prep. The genome compounds here."
    : tier === 2 ? "Worth a cut on a swipe, not a campaign. One-pass tailor, quick go/no-go, apply if cheap."
    : tier === 3 ? "Watch. On the cutoff edge; a right swipe queues a cut only after a confirm."
    : "Below the board cutoff. Log why and move on; the correct output is often nothing."

  return (
    <main style={{ minHeight: "100vh", color: fg1, fontFamily: sans, background: `radial-gradient(1100px 500px at 50% -10%, #00F0FF0a 0, transparent 60%), radial-gradient(700px 400px at 90% 20%, #00FF9d06 0, transparent 55%), ${surface.bg}` }}>
      <div style={{ maxWidth: 1060, margin: "0 auto", padding: "24px 24px 56px" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingBottom: 12 }}><Wordmark section="Role scan" /><Link href="/jobs" style={{ ...eyebrow, color: signal.cyan, textDecoration: "none" }}>← board</Link></div>
        <Rule />

        {/* mast */}
        <header style={{ padding: "40px 0 24px", borderBottom: `1px solid ${border.subtle}` }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 20, flexWrap: "wrap" }}>
            <div>
              <div style={{ display: "flex", gap: 8, marginBottom: 14, flexWrap: "wrap" }}>
                <span style={{ ...eyebrow, fontSize: 9.5, letterSpacing: ".09em", padding: "4px 10px", borderRadius: 4, background: signal.cyan, color: "#03151a" }}>Role Scan</span>
                <span style={{ ...eyebrow, fontSize: 9.5, letterSpacing: ".09em", padding: "4px 10px", borderRadius: 4, border: `1px solid #2c3b52`, color: fg2 }}>Internal · profile × target · one posting</span>
              </div>
              <h1 style={{ fontSize: "clamp(24px,3.6vw,36px)", fontWeight: 700, letterSpacing: "-.025em", lineHeight: 1.06, margin: 0, textWrap: "balance" }}>{row.title}</h1>
              <div style={{ ...eyebrow, color: signal.cyan, marginTop: 10 }}>{row.company}{row.location ? ` · ${row.location}` : ""}{row.compBand ? ` · ${row.compBand}` : ""}</div>
            </div>
            <div style={{ fontFamily: mono, fontSize: 10, letterSpacing: ".07em", color: fg3, textAlign: "left", lineHeight: 2.1, whiteSpace: "nowrap" }}>
              {led(bandColor)}BAND · {row.band}{tier ? ` · TIER ${tier}` : ""}<br />
              {led(gates.length ? signal.red : signal.green)}GATES · {gates.length ? `${gates.length} FIRED` : "NONE FIRED"}<br />
              {led(row.swipe ? (row.swipe.direction === "r" ? signal.green : signal.red) : fg4)}SWIPE · {row.swipe ? (row.swipe.direction === "r" ? "RIGHT" : `LEFT${row.swipe.why ? ` · ${row.swipe.why.toUpperCase()}` : ""}`) : "NONE"}<br />
              {led(forge ? (forge.status === "live" ? signal.green : signal.cyan) : fg4)}FORGE · {forge ? forge.status.toUpperCase() : "NOT REQUESTED"}
            </div>
          </div>
          <p style={{ maxWidth: "66ch", fontSize: 13.5, lineHeight: 1.7, color: fg2, marginTop: 16, textWrap: "pretty" }}>{row.assessment ?? "No read recorded yet. The scorer writes one line per posting after reading the JD; until then this page shows only what the digest carried."}</p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", marginTop: 24 }}>
            {[[scored ? row.composite!.toFixed(3) : "—", "composite · sum ÷ 72"], [scored ? `${total}` : "—", `points of ${MAX}`], [row.atsName ?? "unverified", "applicant tracking"], [row.companyType ?? "—", "company type"], [row.firstSeen.toISOString().slice(0, 10), `first seen · ${row.alertQuery ?? "by hand"}`]].map(([v, k], i) => (
              <div key={k} style={{ padding: "14px 18px", borderLeft: i ? `1px solid ${border.subtle}` : "none", paddingLeft: i ? 18 : 0 }}>
                <div style={{ fontFamily: mono, fontSize: 22, fontWeight: 700, color: i === 0 ? signal.cyan : fg1, lineHeight: 1, overflowWrap: "anywhere" }}>{v}</div>
                <div style={{ fontFamily: mono, fontSize: 8.5, fontWeight: 600, letterSpacing: ".11em", textTransform: "uppercase", color: fg3, marginTop: 7, lineHeight: 1.5 }}>{k}</div>
              </div>))}
          </div>
          <div style={{ ...src, marginTop: 10 }}>SRC · <a href={row.url} target="_blank" rel="noopener" style={{ color: signal.cyan }}>the posting</a> · runtime/specs/target-role-scan.json v{spec?.version ?? "?"} · resume.arcs.care (record of record){row.scoredAt ? ` · scored ${row.scoredAt.toISOString().slice(0, 10)}` : ""}</div>
        </header>

        {/* 01 comparator: what the posting asks vs what the record shows, per differentiator */}
        {secHd("01", "Posting vs Record", signal.cyan, "what it asks · what the record shows")}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 16 }}>
          <div style={{ padding: "18px 20px 16px", borderRadius: 10, border: `1px solid ${border.subtle}`, background: `linear-gradient(165deg,#ffffff05,#00000038), ${surface.bg}` }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12, paddingBottom: 10, borderBottom: `1px solid ${border.subtle}` }}>{led("#7d8fa3")}<span style={{ ...eyebrow, color: fg3 }}>CH·A — What the posting asks</span></div>
            {Object.values(hits).some((h) => h?.length) ? (
              <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>{quads.map((q) => (hits[q.id] ?? []).map((h, i) => <li key={q.id + i} style={{ position: "relative", paddingLeft: 16, fontSize: 12.5, lineHeight: 1.62, color: fg2, marginBottom: 10, textWrap: "pretty" }}><span style={{ position: "absolute", left: 2, top: 8, width: 5, height: 5, borderRadius: "50%", border: `1px solid ${fg3}`, opacity: .55 }} /><b style={{ color: fg1, fontWeight: 600 }}>{q.id} ·</b> {h}</li>))}</ul>
            ) : (
              <p style={{ fontSize: 12, lineHeight: 1.6, color: fg3, fontStyle: "italic" }}>JD evidence per differentiator arrives with the next scoring pass (the scorer quotes the sentences of the posting itself under A through D). Until then the posting is linked above, not paraphrased here.</p>
            )}
          </div>
          <div style={{ ...panel, padding: "18px 20px 16px", borderColor: "#00F0FF35", boxShadow: "inset 0 1px 0 #ffffff0e, 0 0 26px -14px #00F0FF55, 0 14px 34px -22px #000c" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12, paddingBottom: 10, borderBottom: "1px solid #00F0FF2b" }}>{led(signal.cyan)}<span style={{ ...eyebrow, color: signal.cyan }}>CH·B — What the record shows</span></div>
            <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>{quads.map((q) => <li key={q.id} style={{ position: "relative", paddingLeft: 16, fontSize: 12.5, lineHeight: 1.62, color: fg2, marginBottom: 10, textWrap: "pretty" }}><span style={{ position: "absolute", left: 2, top: 8, width: 5, height: 5, borderRadius: "50%", background: signal.cyan, opacity: .55 }} /><b style={{ color: fg1, fontWeight: 600 }}>{q.id} · {q.label}</b> <span style={{ fontFamily: mono, fontSize: 10, color: scored ? (q.ratio >= .67 ? signal.green : q.ratio >= .34 ? signal.gold : signal.red) : fg4 }}>{scored ? `${q.p}/${q.m}` : "—"}</span><br />{q.proof.claim}</li>)}</ul>
            <span style={{ ...src, display: "block", marginTop: 6 }}>SRC · target-role-scan.json quads · proof points from the profile scan</span>
          </div>
        </div>

        {/* 02 threads */}
        {secHd("02", "Thread Assessment", signal.green, "red risk · gold asset · green conviction · vermillion constraint")}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 16 }}>
          {[
            [signal.red, "Red Thread · Risk", gates.length ? `A hard gate fired: ${gates.join(", ")}.` : scored ? `Weakest dimension: ${weakest[0].label} at ${weakest[0].sc} of 3 (×${weakest[0].weight}). ${weakest[0].sc === 0 ? "A zero here is a live objection, not a rounding error." : "This is where the posting and the record disagree most."}` : "Not yet scored."],
            [signal.gold, "Gold Thread · Asset", scored ? `Strongest lever: ${strongest[0].label} at ${strongest[0].sc} of 3 (×${strongest[0].weight}); top differentiator ${quads[0].id}, ${quads[0].label}. ${quads[0].proof.company ? `Proof: ${quads[0].proof.company}.` : ""}` : "Not yet scored."],
            [signal.green, "Green Thread · Conviction", archetype ? `Surfaced under the ${archetype.title} archetype: ${archetype.titles.slice(0, 3).join(", ")}. The lead proof of the record for it${archetype.lead_proof?.company ? `, ${archetype.lead_proof.company},` : ""} is what the cut leads with.` : "Archetype not inferred (hand-added row)."],
            [signal.orange, "Vermillion · Constraint", `${row.atsName ? `Apply path is ${row.atsName}` : "Apply path unverified"}${row.contactDetail ? `: ${row.contactDetail}` : ""}. Hiring manager ${row.hmKind ?? "unknown"}${row.hmText ? `: ${row.hmText}` : ""}. ${row.nextStep ?? ""}`],
          ].map(([c, t, body]) => (
            <div key={t as string} style={{ ...panel, position: "relative", padding: "16px 18px 14px 21px", overflow: "hidden" }}>
              <span style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: 3, background: c as string, boxShadow: `0 0 14px 0 ${c}` }} />
              <span style={{ ...eyebrow, color: c as string }}>{t}</span>
              <p style={{ fontSize: 12, lineHeight: 1.62, color: fg2, marginTop: 7, textWrap: "pretty" }}>{body}</p>
            </div>))}
        </div>

        {/* 03 rubric ledger with this row's scores */}
        {secHd("03", "Scoring Ledger", "#7d8fa3", "this posting against the rubric")}
        <div style={{ ...panel, overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
            <thead><tr>{["Dimension", "Weight", "Score", "Points", "0 reads as", "3 reads as"].map((h, i) => <th key={h} style={{ fontFamily: mono, fontSize: 9, fontWeight: 700, letterSpacing: ".11em", textTransform: "uppercase", color: fg3, textAlign: i === 1 || i === 2 || i === 3 ? "center" : "left", padding: "10px 14px", borderBottom: `1px solid #2c3b52` }}>{h}</th>)}</tr></thead>
            <tbody>{DIMS.map((d) => { const sc = dims[d.key]; return (
              <tr key={d.key}>
                <td style={{ padding: "9px 14px", borderBottom: `1px solid ${border.subtle}`, color: fg1, fontWeight: 600 }}>{d.label}</td>
                <td style={{ padding: "9px 14px", borderBottom: `1px solid ${border.subtle}`, fontFamily: mono, color: signal.gold, fontWeight: 700, textAlign: "center" }}>×{d.weight}</td>
                <td style={{ padding: "9px 14px", borderBottom: `1px solid ${border.subtle}`, fontFamily: mono, fontWeight: 700, textAlign: "center", color: sc == null ? fg4 : sc === 0 ? signal.red : sc === 3 ? signal.green : fg1 }}>{sc ?? "—"}</td>
                <td style={{ padding: "9px 14px", borderBottom: `1px solid ${border.subtle}`, fontFamily: mono, textAlign: "center", color: fg2 }}>{sc == null ? "—" : `${sc * d.weight}/${d.weight * 3}`}</td>
                <td style={{ padding: "9px 14px", borderBottom: `1px solid ${border.subtle}`, color: fg3 }}>{d.anchor0}</td>
                <td style={{ padding: "9px 14px", borderBottom: `1px solid ${border.subtle}`, color: signal.green }}>{d.anchor3}</td>
              </tr>) })}</tbody>
          </table>
        </div>
        <p style={{ ...src, marginTop: 12 }}>COMPOSITE · Σ(score × weight) ÷ {MAX} · bands from the spec: pursue ≥ {spec?.rubric.bands.pursue ?? .7}, consider ≥ {spec?.rubric.bands.consider ?? .5}, board cutoff {spec?.rubric.board_cutoff ?? .58} · trigger rules v{trig.version}: auto tiers {trig.tiers.auto.join(", ")}, confirm tier {trig.tiers.confirm.join(", ")}</p>

        {/* 04 forge */}
        {secHd("04", "Forge", signal.gold, "what has been printed for this role")}
        <div style={{ ...panel, padding: "18px 20px" }}>
          {forge ? (<>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>{led(forge.status === "live" ? signal.green : signal.cyan)}<span style={{ ...eyebrow, color: forge.status === "live" ? signal.green : signal.cyan }}>{forge.status}</span><span style={{ ...src }}>requested {forge.requestedAt.toISOString().slice(0, 16).replace("T", " ")} · updated {forge.updatedAt.toISOString().slice(0, 16).replace("T", " ")}</span></div>
            {forge.notes && <p style={{ fontSize: 12, lineHeight: 1.6, color: fg2, marginTop: 10, textWrap: "pretty" }}>{forge.notes}</p>}
            <p style={{ fontSize: 12, lineHeight: 1.6, color: fg3, marginTop: 10 }}>{forge.url ? <>Live at <a href={forge.url} style={{ color: signal.cyan }}>{forge.url}</a>.</> : <>Bundle on disk under <span style={{ fontFamily: mono, color: fg2 }}>_ARTIFACTS/forge-*/</span> (resume PDF, tailor notes, red-team, hiring-manager and contact json, kintsugi, landing page staged as page.html). Hosting is a separate, human-approved step.</>}</p>
          </>) : <p style={{ fontSize: 12, lineHeight: 1.6, color: fg3 }}>Nothing printed. A right swipe on the board files the request{tier === 3 ? "; on this tier the run waits for a confirm before a cut is spent" : ""}.</p>}
        </div>

        {/* 05 assertion */}
        {secHd("05", "Verdict", signal.cyan, "the load-bearing sentence")}
        <div style={{ position: "relative", padding: "26px 30px 22px", border: "1px solid #00F0FF35", borderRadius: 14, background: "linear-gradient(165deg,#00F0FF0e,#00000030 55%), #0d1117", boxShadow: "inset 0 1px 0 #ffffff10, 0 0 44px -18px #00F0FF40" }}>
          <p style={{ fontSize: 16.5, lineHeight: 1.72, color: fg1, fontWeight: 450, textWrap: "pretty", margin: 0 }}>{verdict}</p>
          <cite style={{ display: "block", marginTop: 14, fontStyle: "normal", fontFamily: mono, fontSize: 9.5, letterSpacing: ".1em", textTransform: "uppercase", color: fg3 }}>ARCS Role Scan · {row.company} · sizing, not conviction · conviction comes after the reads</cite>
        </div>
        <div style={{ marginTop: 24, padding: "16px 20px", border: `1px dashed #2c3b52`, borderRadius: 10, background: "#0d111780" }}>
          <span style={{ ...eyebrow, color: signal.orange, display: "block", marginBottom: 8 }}>Provenance · flags lit, not smoothed</span>
          <p style={{ fontSize: 11, lineHeight: 1.7, color: fg3, margin: 0 }}>Scores are the pre-work sizing composite, 0 to 3 per dimension against the anchors in the ledger, weights a v1 calibration. The record side of the comparator is the proof points of the target scan, which carry the flags of the profile scan: the ARCS decision-noise and time-to-insight figures are self-reported, ARCS is not a listed LinkedIn position, and AUM reads $7B here. Nothing on this page is sent anywhere; the public forge page is built separately and air-gapped from this instrument. Sibling instruments: <Link href="/jobs/profile" style={{ color: signal.cyan }}>Profile Scan</Link> · <Link href="/jobs/scan" style={{ color: signal.cyan }}>Target Scan</Link>.</p>
        </div>
      </div>
    </main>
  )
}
