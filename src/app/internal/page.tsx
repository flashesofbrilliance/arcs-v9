import type { CSSProperties } from "react";
import { redirect } from "next/navigation";
import { auth } from "@/lib/auth";
import { isOwner } from "@/lib/internal-access";

// Owner hub (/internal). The signed-in navigator: every internal surface and
// every load-bearing record, each with "what this is" and "how to use it".
// Adding a surface is one row in CARDS. The patent pressure-test that used to
// live at this path moved to /internal/patents (nothing dropped).
//
// Gate: identical to before. No session -> sign in; session not on the owner
// allowlist (src/lib/internal-access.ts) -> 403. Never indexed, never cached.
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

const REPO = "https://github.com/flashesofbrilliance/arcs-v9/blob/main/";

type Card = {
  group: "Instruments" | "Rooms" | "Admin" | "Records";
  name: string;
  href: string;
  what: string;
  how: string;
  external?: boolean;
  gate?: string;
};

const CARDS: Card[] = [
  // Instruments: the product loop, in the order a decision moves through it.
  { group: "Instruments", name: "Compass", href: "/dashboard", what: "The parser. A question goes in, the L0 to L5 pipeline runs, and a DEWY receipt with a Y-gate state comes out.", how: "Type the decision as a question. Run Prep first if the stakes are real. Follow the three tributaries before you act." },
  { group: "Instruments", name: "Prep", href: "/prep", what: "The calibration instrument. Five fields, two minutes: stakes, window, what you protect, prior certainty, strongest counter-argument.", how: "Fill it before a compass run on anything with a real horizon. The compass then runs with richer context and the terrain sharpens." },
  { group: "Instruments", name: "History", href: "/history", what: "Your receipt ledger. Every position frozen in time, with Y-gate and NCI.", how: "Open any receipt to reach its brief, guide, reflect, and debrief. Close the loop on old ones: the outcome field is what calibrates the whole instrument." },
  { group: "Instruments", name: "Observatory", href: "/observatory", what: "Instant replay. Sessions as kinematic trajectories, a risk register in severity lanes, altitude and trajectory faces.", how: "Scrub a session backward to the receipt where conviction peaked or collapsed. Flip a card to see risks by severity." },
  { group: "Instruments", name: "Onboarding", href: "/onboarding", what: "The under-30-second upload step (ADR-029). Store-only today; no pipeline reads the files yet.", how: "Skip it or complete it once. The dashboard stops nudging after either." },

  // Rooms: internal surfaces built around counterparts and corpora.
  { group: "Rooms", name: "Recoil", href: "/recoil", what: "History-as-index for recoil reports: the pre-call and post-call ledgers the /recoil-report skill writes.", how: "Open a report to see its cover, ex-ante receipt, and close. New reports appear when a skill writes a JSON under the generated folder.", gate: "ADMIN_EMAILS" },
  { group: "Rooms", name: "Reading room", href: "/reading-room", what: "The Desk. Five reader intents as the heading, the shelf second. Private long-form reading.", how: "Pick the question you arrived with, not a category. The shelf reorders to it." },
  { group: "Rooms", name: "Advisory", href: "/advisory", what: "The advisory intake surface. Captures land in the Lead table.", how: "Use it to test the intake copy as a visitor would. Review what came in under Admin, Leads." },
  { group: "Rooms", name: "Jobs board", href: "/jobs", what: "The Alert Swipe Board. Real roles from the inbox, scored, with forge runs from a seed resume.", how: "Swipe to keep or drop. A kept role can be forged. The inbox re-pull runs on a schedule; nothing here sends anything.", gate: "ADMIN_EMAILS" },
  { group: "Rooms", name: "Scan", href: "/scan", what: "Staging surface for scan.arcs.care (ADR-028). LinkedIn-derived analytics, currently hardcoded mock data.", how: "Design review only. Do not read the numbers as live until a pipeline is wired." },

  // Admin: review and trust surfaces.
  { group: "Admin", name: "Leads", href: "/admin/leads", what: "Server-rendered review of the Lead table: waitlist and advisory captures, each with its linked receipt.", how: "Scan newest first. Follow the receipt link before replying to anyone.", gate: "ADMIN_EMAILS" },
  { group: "Admin", name: "Patents", href: "/internal/patents", what: "The patent pressure-test: candidate inventions from the Yellow and White papers, stack-ranked by filing priority.", how: "Triage for counsel, not legal advice. Resolve the disclosure alarm at the top before anything is filed." },
  { group: "Admin", name: "Trust", href: "/trust", what: "The published trust contract: what is stored, what is not, and for how long.", how: "Read it before shipping any change that touches storage, email, or analytics. The privacy-review agent checks code against this page." },
  { group: "Admin", name: "Waitlist", href: "/waitlist", what: "Public waitlist capture. Writes to the Lead table.", how: "Use it to verify the capture path end to end after any form or email change." },

  // Records: the repo files that govern the above. Private repo; you are signed in on GitHub.
  { group: "Records", name: "RC-OPS-001 criteria audit", href: REPO + "_STATE/2026-09-27-rc-ops-001-criteria-audit.md", external: true, what: "The 2026-09-27 audit of the Echo Detector's four graduation criteria: evidence, proposed value, and what would flip each.", how: "Start here before touching the registry. The proposed diff at the bottom lands only on your explicit go." },
  { group: "Records", name: "RC-OPS-001 initiation receipt", href: REPO + "_STATE/2026-08-29-rc-ops-001-graduation-initiation.md", external: true, what: "The 2026-08-29 record that opened the graduation and pinned the four criteria. Not a promotion.", how: "Read for the criteria's original wording and the falsifier. The audit above supersedes its status lines." },
  { group: "Records", name: "ROM candidate registry", href: REPO + "operators/RC-REGISTRY.json", external: true, what: "Every ROM candidate with status and criteria_status. criteria_status is a human ruling.", how: "Edit only through a PR you have said go on. Never let a session write criteria_status on its own." },
  { group: "Records", name: "ROM axis index", href: REPO + "runtime/specs/ROM-AXIS-INDEX.md", external: true, what: "The 2026-08-28 ruling on which ROM vocabulary is canon (the 7 primitives) and how the other two tiers nest.", how: "Cite this, not a sibling file, when anyone asks what the ROM primitives are." },
  { group: "Records", name: "Operator periodic table", href: REPO + "operators/docs/PERIODIC-TABLE.md", external: true, what: "The only enumeration of operator numbers. Folksonomy is 20, Librarian is 21, locked.", how: "Never hand-write an operator-to-file map. Regenerate the registry with the emit script instead." },
  { group: "Records", name: "Operator registry (generated)", href: REPO + "operators/OPERATOR-REGISTRY.json", external: true, what: "The grep-verified binding of each operator to its file and readiness: READY, PARTIAL, BLOCKED, UNBUILT.", how: "Read it to know what the MCP bridge can actually run. A blocked operator answers with a reason, never a fake." },
  { group: "Records", name: "Induced backlog", href: REPO + "_QUEUE/induced-backlog.jsonl", external: true, what: "Open work as ranked rows with route, gates, trigger, fates, and dependency edges. Mirrored to GitHub issues.", how: "Sessions execute from here without replanning. Append to a row's status; never rewrite it." },
  { group: "Records", name: "Decisions (ADRs and collisions)", href: REPO + "_DECISIONS", external: true, what: "Architecture decision records and canon collision files, numbered through the oracle.", how: "Open a collision file to rule on it. Options are listed; pick one in the doc, never resolve under write-lock by editing sources." },
  { group: "Records", name: "Witness stubs", href: REPO + "_STATE/witness", external: true, what: "Verbatim, timestamped attestations of moments that named themselves. Upstream of any ADR or receipt.", how: "Promote one only if it proves durable. Candidate blind echoes for the detector are counted from here." },
];

const GROUPS: Card["group"][] = ["Instruments", "Rooms", "Admin", "Records"];
const GROUP_NOTE: Record<Card["group"], string> = {
  Instruments: "The product loop, in the order a decision moves through it.",
  Rooms: "Surfaces built around counterparts and corpora.",
  Admin: "Review and trust surfaces.",
  Records: "The repo files that govern everything above. Opens GitHub in a new tab; the repo is private, so stay signed in there.",
};

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

export default async function InternalHub() {
  const session = await auth();
  const email = session?.user?.email ?? null;

  if (!email) redirect("/compass?callbackUrl=/internal");
  if (!isOwner(email)) return <Denied email={email} />;

  const label: CSSProperties = { fontFamily: C.mono, fontSize: 9, letterSpacing: "0.12em", textTransform: "uppercase", color: C.faint, display: "block", marginBottom: 3 };
  const para: CSSProperties = { fontSize: 12.5, color: C.muted, lineHeight: 1.5, margin: "0 0 9px" };

  return (
    <main style={{ minHeight: "100vh", background: C.bg, color: C.text, fontFamily: C.sans }}>
      <div style={{ maxWidth: 1080, margin: "0 auto", padding: "32px 16px 72px" }}>
        <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: 10, border: `1px solid ${C.border}`, borderLeft: `3px solid ${C.cyan}`, borderRadius: 8, background: "rgba(0,240,255,0.04)", padding: "10px 14px", marginBottom: 22, fontFamily: C.mono, fontSize: 11 }}>
          <span style={{ color: C.cyan, fontWeight: 700, letterSpacing: "0.14em" }}>🔒 INTERNAL</span>
          <span style={{ color: C.muted }}>authenticated as {email}</span>
          <span style={{ marginLeft: "auto", color: C.faint }}>owner hub · never indexed</span>
        </div>

        <h1 style={{ fontSize: 30, fontWeight: 650, letterSpacing: "-0.02em", margin: "0 0 6px" }}>Where everything is</h1>
        <p style={{ color: C.muted, fontSize: 14, lineHeight: 1.6, margin: "0 0 28px", maxWidth: "none" }}>
          Every internal surface and every governing record, each with what it is and how to use it. Instruments run the decision loop, rooms hold counterparts and corpora, admin reviews what came in, records are the files that rule the rest.
        </p>

        {GROUPS.map((g) => (
          <section key={g} style={{ marginBottom: 30 }}>
            <div style={{ display: "flex", alignItems: "baseline", gap: 12, borderBottom: `1px solid ${C.border}`, paddingBottom: 8, marginBottom: 14 }}>
              <h2 style={{ fontSize: 13, fontFamily: C.mono, letterSpacing: "0.16em", textTransform: "uppercase", color: C.cyan, margin: 0, fontWeight: 600 }}>{g}</h2>
              <span style={{ fontSize: 12, color: C.faint }}>{GROUP_NOTE[g]}</span>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 12 }}>
              {CARDS.filter((c) => c.group === g).map((c) => (
                <a
                  key={c.href}
                  href={c.href}
                  target={c.external ? "_blank" : undefined}
                  rel={c.external ? "noopener noreferrer" : undefined}
                  style={{ display: "block", textDecoration: "none", color: "inherit", border: `1px solid ${C.borderSoft}`, borderRadius: 10, background: C.surface2, padding: "13px 14px" }}
                >
                  <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginBottom: 8 }}>
                    <h3 style={{ fontSize: 14.5, color: C.text, margin: 0, fontWeight: 650 }}>{c.name}</h3>
                    <span style={{ fontFamily: C.mono, fontSize: 10, color: C.faint, marginLeft: "auto", whiteSpace: "nowrap" }}>{c.external ? "github ↗" : c.href}</span>
                  </div>
                  <p style={para}><b style={label}>What this is</b>{c.what}</p>
                  <p style={{ ...para, margin: 0 }}><b style={label}>How to use it</b>{c.how}</p>
                  {c.gate && <div style={{ fontFamily: C.mono, fontSize: 9.5, color: C.gold, marginTop: 8, letterSpacing: "0.06em" }}>gate: {c.gate}</div>}
                </a>
              ))}
            </div>
          </section>
        ))}

        <div style={{ fontFamily: C.mono, fontSize: 10, color: C.faint, letterSpacing: "0.04em", borderTop: `1px solid ${C.borderSoft}`, paddingTop: 14 }}>
          Gate: session + owner allowlist (INTERNAL_EMAILS). Cards marked with a gate also require ADMIN_EMAILS on the target. Add a surface by adding one row to CARDS in src/app/internal/page.tsx.
        </div>
      </div>
    </main>
  );
}
