import type { CSSProperties } from "react";
import { redirect } from "next/navigation";
import { auth } from "@/lib/auth";
import { isOwner } from "@/lib/internal-access";

// Auth-dependent → never statically cached; never indexed.
export const dynamic = "force-dynamic";
export const metadata = {
  title: "ARCS · Internal",
  robots: { index: false, follow: false },
};

const C = {
  bg: "#020408",
  surface: "#0d1117",
  surface2: "#10161f",
  border: "#1e293b",
  borderSoft: "#141c28",
  text: "#e2e8f0",
  muted: "#64748b",
  faint: "#334155",
  cyan: "#00F0FF",
  green: "#00FF9D",
  gold: "#FFD700",
  red: "#FF4D6D",
  mono: "ui-monospace, 'JetBrains Mono', Menlo, monospace",
  sans: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, system-ui, sans-serif",
};

type Row = {
  r: string; c: string; s: string; e: string; n: string; st: string; v: string; tier: 1 | 2 | 3;
};
const CANDIDATES: Row[] = [
  { r: "1", c: "Kairos multi-signal convergence + window + EV-gate", s: "YP Pillar 3 + WP #7", e: "3.5", n: "3.5", st: "4.5", v: "FORMALIZE — strongest", tier: 1 },
  { r: "2", c: "Ex-ante decision-receipt lock + reconciliation", s: "WP #2", e: "2.5", n: "3.0", st: "5.0", v: 'FORMALIZE — off "blockchain"', tier: 1 },
  { r: "3", c: "Phase-cancellation multi-campaign scheduler", s: "WP #6", e: "3.0", n: "4.0", st: "3.5", v: "FORMALIZE — best novelty", tier: 1 },
  { r: "4", c: "Abductive prediction + uncertainty quantification", s: "YP Pillar 1", e: "2.0", n: "2.0", st: "4.5", v: "Narrow claims only", tier: 2 },
  { r: "5", c: "Adaptive coherence (ARCS Law)", s: "WP #1", e: "2.5", n: "2.5", st: "3.0", v: "Needs concrete control app", tier: 2 },
  { r: "6", c: "Privacy-preserving cross-customer learning", s: "YP Pillar 4", e: "3.0", n: "1.5", st: "4.0", v: "Defensive — crowded", tier: 3 },
  { r: "7", c: "Real-time 2nd-derivative trend detection", s: "WP #4", e: "2.5", n: "1.5", st: "3.0", v: "Pressure hardest → drop", tier: 3 },
  { r: "8–11", c: "Wave-diffusion · rhetorical/wavefunction · chemical-bonding · decelerator", s: "WP #9/#5/#11/#8/#10", e: "≤2", n: "≤2", st: "low", v: "Likely drop", tier: 3 },
];
const verdictColor = (t: 1 | 2 | 3) => (t === 1 ? C.green : t === 2 ? C.gold : C.muted);

const TIER1 = [
  { i: "① strongest", h: "Kairos convergence engine", claim: "cross-domain convergence (≥3σ) → window estimate → EV-gated activation.", note: 'Cut the "energetic catalysis" metaphor — §112/§101 liability.', cpc: "G06F9/50 · G06Q10/04 · H04L67/10" },
  { i: "② highest value", h: "Ex-ante receipt lock", claim: "commit prediction before spend, reconcile to outcome — not “records on a blockchain.”", note: "§101: Bprotocol v. Uniswap (2026) kills economic-practice-on-chain.", cpc: "G06F21/64 · H04L9/50" },
  { i: "③ cleanest novelty", h: "Phase-cancellation scheduler", claim: "detect destructive interference between concurrent campaigns; schedule to minimize.", note: "Frame as technical scheduling; search ad-pacing prior art.", cpc: "G06Q10/0631 · G06Q30/0242" },
];

function Denied({ email }: { email: string }) {
  return (
    <main style={{ minHeight: "100vh", background: C.bg, color: C.text, fontFamily: C.sans, display: "flex", alignItems: "center", justifyContent: "center", padding: 24 }}>
      <div style={{ maxWidth: 460, textAlign: "center" }}>
        <div style={{ fontFamily: C.mono, fontSize: 11, letterSpacing: "0.2em", color: C.red, textTransform: "uppercase" }}>403 · Not authorized</div>
        <h1 style={{ fontSize: 22, fontWeight: 650, margin: "10px 0 8px" }}>This is an internal surface.</h1>
        <p style={{ color: C.muted, fontSize: 14, lineHeight: 1.6 }}>
          You&rsquo;re signed in as <b style={{ color: C.text }}>{email}</b>, but that address isn&rsquo;t on the
          owner allowlist. Access to internal material is restricted to specific accounts by design.
        </p>
      </div>
    </main>
  );
}

export default async function InternalPage() {
  const session = await auth();
  const email = session?.user?.email ?? null;

  // Fail closed: no session → sign in; session but not owner → 403.
  if (!email) redirect("/compass?callbackUrl=/internal");
  if (!isOwner(email)) return <Denied email={email} />;

  const th: CSSProperties = { textAlign: "left", fontFamily: C.mono, fontSize: 9.5, letterSpacing: "0.12em", textTransform: "uppercase", color: C.muted, fontWeight: 500, padding: "10px 10px", borderBottom: `1px solid ${C.border}`, background: C.surface };
  const td: CSSProperties = { padding: "9px 10px", borderBottom: `1px solid ${C.borderSoft}`, verticalAlign: "top", fontSize: 12.5, lineHeight: 1.4 };

  return (
    <main style={{ minHeight: "100vh", background: C.bg, color: C.text, fontFamily: C.sans }}>
      <div style={{ maxWidth: 1080, margin: "0 auto", padding: "32px 24px 72px" }}>
        {/* Ribbon */}
        <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: 10, border: `1px solid ${C.border}`, borderLeft: `3px solid ${C.cyan}`, borderRadius: 8, background: "rgba(0,240,255,0.04)", padding: "10px 14px", marginBottom: 22, fontFamily: C.mono, fontSize: 11 }}>
          <span style={{ color: C.cyan, fontWeight: 700, letterSpacing: "0.14em" }}>🔒 INTERNAL</span>
          <span style={{ color: C.muted }}>authenticated as {email}</span>
          <span style={{ marginLeft: "auto", color: C.faint }}>pulled from the public pages · owner-gated</span>
        </div>

        <h1 style={{ fontSize: 30, fontWeight: 650, letterSpacing: "-0.02em", margin: "0 0 6px" }}>Patent pressure-test</h1>
        <p style={{ color: C.muted, fontSize: 14, maxWidth: "70ch", lineHeight: 1.6, margin: "0 0 22px" }}>
          Candidate inventions from the Yellow &amp; White papers, stack-ranked by filing priority — §101 eligibility
          and novelty gated first. Triage for counsel, not legal advice. This lives here (authenticated) rather than
          on the public status pages.
        </p>

        {/* Disclosure alarm */}
        <div style={{ border: `1px solid rgba(255,77,109,0.35)`, borderLeft: `3px solid ${C.red}`, borderRadius: 10, background: "rgba(255,77,109,0.05)", padding: "14px 16px", marginBottom: 22 }}>
          <div style={{ fontFamily: C.mono, fontSize: 10, fontWeight: 700, letterSpacing: "0.18em", textTransform: "uppercase", color: C.red }}>⚠ Disclosure status — resolve before filing · US §102 unresolved</div>
          <h2 style={{ fontSize: 16, color: "#ffd7de", margin: "8px 0 5px", fontWeight: 650 }}>The papers are internal drafts — not published.</h2>
          <p style={{ fontSize: 12.5, color: C.muted, lineHeight: 1.55, margin: 0 }}>
            The Yellow/White papers have not been publicly released — the &ldquo;Public Release / CC BY 4.0&rdquo; header is an
            aspirational draft label. But they sit in a <b style={{ color: "#ff8fa3" }}>public GitHub repo</b>, and a publicly-accessible
            repo file can itself count as a §102 public-accessibility event — a question for counsel keyed to when the
            files first went public. File Tier-1 provisionals <b style={{ color: "#ff8fa3" }}>before any actual publication</b>; treat the repo as sensitive.
          </p>
        </div>

        {/* Stack-rank table */}
        <div style={{ overflowX: "auto", border: `1px solid ${C.borderSoft}`, borderRadius: 10, marginBottom: 22 }}>
          <table style={{ borderCollapse: "collapse", width: "100%", minWidth: 640, fontVariantNumeric: "tabular-nums" }}>
            <thead>
              <tr>
                <th style={{ ...th, textAlign: "center", width: 44 }}>#</th>
                <th style={th}>Candidate</th>
                <th style={{ ...th, textAlign: "center" }}>§101</th>
                <th style={{ ...th, textAlign: "center" }}>Novel</th>
                <th style={{ ...th, textAlign: "center" }}>Strat</th>
                <th style={th}>Verdict</th>
              </tr>
            </thead>
            <tbody>
              {CANDIDATES.map((row) => (
                <tr key={row.r}>
                  <td style={{ ...td, textAlign: "center", fontFamily: C.mono, fontWeight: 700, color: verdictColor(row.tier) }}>{row.r}</td>
                  <td style={{ ...td, color: C.text, fontWeight: 600 }}>
                    {row.c}
                    <span style={{ display: "block", fontFamily: C.mono, fontSize: 10, color: C.faint, fontWeight: 400, marginTop: 2 }}>{row.s}</span>
                  </td>
                  <td style={{ ...td, textAlign: "center", fontFamily: C.mono, color: C.muted }}>{row.e}</td>
                  <td style={{ ...td, textAlign: "center", fontFamily: C.mono, color: C.muted }}>{row.n}</td>
                  <td style={{ ...td, textAlign: "center", fontFamily: C.mono, color: C.muted }}>{row.st}</td>
                  <td style={{ ...td, fontFamily: C.mono, fontSize: 10.5, color: verdictColor(row.tier) }}>{row.v}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Tier-1 cards */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 12, marginBottom: 22 }}>
          {TIER1.map((k) => (
            <div key={k.h} style={{ border: `1px solid rgba(0,255,157,0.22)`, borderRadius: 10, background: C.surface2, padding: "13px 14px" }}>
              <div style={{ fontFamily: C.mono, fontSize: 9, letterSpacing: "0.12em", textTransform: "uppercase", color: C.green }}>{k.i}</div>
              <h3 style={{ fontSize: 14, color: "#eafff6", margin: "5px 0 8px", fontWeight: 650 }}>{k.h}</h3>
              <p style={{ fontSize: 11.5, color: C.muted, lineHeight: 1.45, margin: "5px 0" }}><b style={{ color: C.text, fontFamily: C.mono, fontSize: 9, letterSpacing: "0.06em", textTransform: "uppercase", display: "block", marginBottom: 2 }}>Claim</b>{k.claim}</p>
              <p style={{ fontSize: 11.5, color: C.muted, lineHeight: 1.45, margin: "5px 0" }}><b style={{ color: C.text, fontFamily: C.mono, fontSize: 9, letterSpacing: "0.06em", textTransform: "uppercase", display: "block", marginBottom: 2 }}>Pressure-test</b>{k.note}</p>
              <div style={{ fontFamily: C.mono, fontSize: 9, color: C.cyan, marginTop: 6 }}>{k.cpc}</div>
            </div>
          ))}
        </div>

        {/* Do-not-file */}
        <div style={{ border: `1px dashed ${C.faint}`, borderRadius: 10, padding: "13px 16px", marginBottom: 18 }}>
          <div style={{ fontFamily: C.mono, fontSize: 9, letterSpacing: "0.14em", textTransform: "uppercase", color: C.red, marginBottom: 7 }}>Do-not-file — strategy, not inventions (§101-ineligible)</div>
          <p style={{ fontSize: 11.5, color: C.muted, lineHeight: 1.5, margin: 0 }}>
            <b style={{ color: C.faint, fontFamily: C.mono }}>YP §5.1–5.5</b> agency tiering · prediction-market preference detection · gamification/passport ·
            performance-guarantee structure · regulatory-partnership strategy. Protect via trade secret, trademark, copyright — not utility patents.
          </p>
        </div>

        <div style={{ fontFamily: C.mono, fontSize: 10, color: C.faint, letterSpacing: "0.04em", borderTop: `1px solid ${C.borderSoft}`, paddingTop: 14 }}>
          Sources: ADR-031/032 · ARCS Yellow + White papers (internal drafts) · USPTO/CPC + live prior-art · triage for counsel, not legal advice.
        </div>
      </div>
    </main>
  );
}
