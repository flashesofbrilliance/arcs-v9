/**
 * Pure shaping for GET /api/pulse (status.arcs.care). No network, no env: the route
 * fetches, this module turns raw inputs into the PUBLIC payload, so tests can pin it.
 *
 * Public-safety contract (the page is world-readable, the repo is private):
 *   - counts, trends and curated text only;
 *   - never an issue title or body, a file path, a key location, a person's name, an
 *     email address or a balance. `assertPublicSafe` enforces it and the route refuses
 *     to emit a payload that fails it.
 * No-false-zeros contract: a section whose live read failed or came back implausibly
 * empty is `null`, never 0. The page keeps its static floor and shows "degraded".
 */

export const DEBT_SEVS = ["P1", "P2", "P3"] as const;
export const DEBT_STATUSES = ["open", "in-progress", "decision", "done"] as const;
export type DebtSev = (typeof DEBT_SEVS)[number];
export type DebtStatus = (typeof DEBT_STATUSES)[number];

export interface DebtIssue {
  number: number;
  state: "OPEN" | "CLOSED";
  labels: string[];
}

export interface DebtSummary {
  total: number;
  open: number;
  done: number;
  byStatus: Record<DebtStatus, number>;
  bySev: Record<DebtSev, number>; // open issues only
}

function pick<T extends string>(labels: string[], prefix: string, allowed: readonly T[], dflt: T): T {
  for (const l of labels) {
    if (l.startsWith(prefix)) {
      const v = l.slice(prefix.length) as T;
      if (allowed.includes(v)) return v;
    }
  }
  return dflt;
}

export function statusOf(i: DebtIssue): DebtStatus {
  return i.state === "CLOSED" ? "done" : pick(i.labels, "status:", DEBT_STATUSES, "open");
}
export function sevOf(i: DebtIssue): DebtSev {
  return pick(i.labels, "sev:", DEBT_SEVS, "P3");
}

/** null when the read is implausible: the tracker holds 50+ debt issues, so 0 means a broken read. */
export function summarizeDebt(issues: DebtIssue[] | null): DebtSummary | null {
  if (!issues || issues.length === 0) return null;
  const byStatus = { open: 0, "in-progress": 0, decision: 0, done: 0 } as Record<DebtStatus, number>;
  const bySev = { P1: 0, P2: 0, P3: 0 } as Record<DebtSev, number>;
  for (const i of issues) {
    const st = statusOf(i);
    byStatus[st] += 1;
    if (st !== "done") bySev[sevOf(i)] += 1;
  }
  return { total: issues.length, open: issues.length - byStatus.done, done: byStatus.done, byStatus, bySev };
}

/**
 * Risk-register rows bound to debt issues. The WORDING is curated on the page; only the
 * live severity/status crosses, keyed by a neutral slug. Issue numbers stay server-side.
 */
export const RISK_BINDINGS: Record<string, number> = {
  "spend-cap": 1000, // old API account still capped, keys to retire
  "write-lock": 1019, // ADR-085 write-lock advisory until every merge uses it
  "ci-spend": 973, // CI review was the dominant API cost
};

export interface RiskState {
  sev: DebtSev;
  status: DebtStatus;
}

export function riskStates(issues: DebtIssue[] | null): Record<string, RiskState> | null {
  if (!issues || issues.length === 0) return null;
  const byNum = new Map(issues.map((i) => [i.number, i]));
  const out: Record<string, RiskState> = {};
  for (const [slug, n] of Object.entries(RISK_BINDINGS)) {
    const i = byNum.get(n);
    if (i) out[slug] = { sev: sevOf(i), status: statusOf(i) };
  }
  return Object.keys(out).length ? out : null;
}

/**
 * State-of-the-Union card items: tracker issue number -> PUBLIC label (curated, same pattern as
 * RISK_BINDINGS; approved by Zach 2026-11-12). The label is wording written for the page; an issue
 * title or body never crosses. Each item lands on the card for its LIVE status, so it moves when
 * the issue does. Issue numbers stay server-side.
 */
export const PUBLIC_ITEMS: Record<number, string> = {
  1000: "Spend cap: retire the old API keys",
  1019: "Write-lock stays advisory until every merge uses it",
  992: "Human check of the Librarian calibration",
  991: "Lattice regeneration (human-owned)",
  979: "Claim-unit spec ruling",
  1969: "Decision geometry explorer: data feed",
  1970: "Field HUD: real-device touch and screen-reader testing",
  1971: "App: keyboard support for clickable elements",
  1977: "Universe view: mapping the unmapped files",
  1013: "SHARP render checked on real data",
  1961: "Design and accessibility debt burn-down",
  1046: "CI minutes leak",
  1975: "Page renderers: retire old greys and small sizes",
  1012: "Security review: false red on reruns",
  1003: "Receipt closure: separating test data",
  966: "Accountant weekly run, unattended",
  1006: "Raw API errors no longer shown to visitors",
  994: "Main kept green for every PR",
  973: "CI review spend cut",
  997: "npm test script added",
  1965: "Design file label size fixed",
};

export type PublicItems = Record<DebtStatus, string[]>;

/** Public labels grouped by each issue's live status, in map order. null on a failed or empty read. */
export function publicItems(issues: DebtIssue[] | null): PublicItems | null {
  if (!issues || issues.length === 0) return null;
  const byNum = new Map(issues.map((i) => [i.number, i]));
  const out: PublicItems = { decision: [], open: [], "in-progress": [], done: [] };
  let n = 0;
  for (const [num, label] of Object.entries(PUBLIC_ITEMS)) {
    const i = byNum.get(Number(num));
    if (i) { out[statusOf(i)].push(label); n += 1; }
  }
  return n ? out : null;
}

export interface TempoWeek {
  week: string; // ISO date of the Monday (UTC) that starts the week
  merges: number;
}

/** Monday-start UTC weeks, oldest first, ending with the week that contains `now`. */
export function weekStarts(now: Date, n: number): string[] {
  const d = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()));
  const dow = (d.getUTCDay() + 6) % 7; // 0 = Monday
  d.setUTCDate(d.getUTCDate() - dow);
  const out: string[] = [];
  for (let k = n - 1; k >= 0; k--) {
    const w = new Date(d);
    w.setUTCDate(d.getUTCDate() - 7 * k);
    out.push(w.toISOString().slice(0, 10));
  }
  return out;
}

/** null when every week is 0: this repo merges most days, so all-zero is a failed read. */
export function shapeTempo(weeks: string[], counts: (number | null)[]): TempoWeek[] | null {
  if (counts.length !== weeks.length || counts.some((c) => c == null)) return null;
  if (counts.every((c) => c === 0)) return null;
  return weeks.map((week, k) => ({ week, merges: counts[k] as number }));
}

export const GATES = { calibrationClosed: 30, goalMapDecisions: 100 } as const;

export interface CohortCounts {
  receipts: number; // every recorded decision
  externalReceipts: number; // not the founder QA account, not anonymous
  closed: { founder: number; external: number; anonymous: number };
}

export interface GateState {
  receipts: number; // all recorded, incl. founder QA and anonymous
  calibration: { n: number; gate: number; cohort: "external" };
  goalMap: { n: number; gate: number };
}

export function shapeGates(c: CohortCounts | null): GateState | null {
  if (!c || c.receipts <= 0) return null;
  return {
    receipts: c.receipts,
    calibration: { n: c.closed.external, gate: GATES.calibrationClosed, cohort: "external" },
    // Gates count EXTERNAL decisions: 209 of 267 receipts (2026-10-06) are the founder QA
    // account, so the raw total would show a gate as met that the data does not support.
    goalMap: { n: c.externalReceipts, gate: GATES.goalMapDecisions },
  };
}

// ── public-safety check ─────────────────────────────────────────────────────

const UNSAFE: Array<[string, RegExp]> = [
  ["email address", /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/],
  ["API key or token", /\b(sk-ant-|sk-|ghp_|gho_|github_pat_|xox[bp]-|AKIA)[A-Za-z0-9_-]{6,}/],
  ["bearer credential", /\bBearer\s+[A-Za-z0-9._-]{10,}/i],
  ["file path", /(^|[\s"'(])(\.{0,2}\/)?(src|scripts|operators|public|runtime|_[A-Z]+)\/[\w./-]+/],
  ["env file", /\.env(\.\w+)?\b/],
  ["key location", /\b(ANTHROPIC|OPENAI|GITHUB|VERCEL|DATABASE|RESEND)_[A-Z_]*(KEY|TOKEN|URL|SECRET)\b/],
  ["money amount", /[$€£]\s?\d/],
];

/** Every key the public payload may carry. Anything else (a title, a body) fails the check. */
const ALLOWED_KEYS = new Set([
  "ok", "updated", "commit", "sha", "date", "commitsTotal", "prsOpen", "deploy", "state",
  "debt", "total", "open", "done", "byStatus", "bySev", "in-progress", "decision",
  "P1", "P2", "P3", "items", "risks", "sev", "status", "spend-cap", "write-lock", "ci-spend",
  "tempo", "week", "merges", "gates", "receipts", "calibration", "n", "gate", "cohort",
  "goalMap", "evals", "degraded",
]);

export function assertPublicSafe(payload: unknown): string[] {
  const problems: string[] = [];
  const walk = (v: unknown, path: string) => {
    if (v == null || typeof v === "number" || typeof v === "boolean") return;
    if (typeof v === "string") {
      for (const [what, re] of UNSAFE) if (re.test(v)) problems.push(`${path}: ${what}`);
      return;
    }
    if (Array.isArray(v)) { v.forEach((x, k) => walk(x, `${path}[${k}]`)); return; }
    if (typeof v === "object") {
      for (const [k, x] of Object.entries(v as Record<string, unknown>)) {
        if (!ALLOWED_KEYS.has(k)) problems.push(`${path}.${k}: key not on the public allowlist`);
        walk(x, `${path}.${k}`);
      }
    }
  };
  walk(payload, "$");
  return problems;
}
