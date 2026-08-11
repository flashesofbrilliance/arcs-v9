import { NextResponse } from "next/server";
import { FIELD_HOSTS } from "@/lib/fieldHosts";

/**
 * GET /api/field — live "field state" of the whole arcs-v9 surface for the
 * status.arcs.care board.
 *
 * Two signals:
 *  1. LIVENESS per subtenant host — a cheap HEAD ping (does the host answer?).
 *  2. DEPLOY state — the single arcs-v9 production deployment from the Vercel API.
 *     Every *.arcs.care host is a rewrite of THIS one deployment, so there is one
 *     shared deploy state, not one-per-host; the board says so honestly.
 *
 * Cached at the CDN via `revalidate` so the ~42 pings run at most once/window
 * server-side regardless of how many browsers poll the cached JSON. CORS-open to
 * match /api/pulse (telemetry, not the gated prose).
 */
export const revalidate = 300;

const CORS: Record<string, string> = { "Access-Control-Allow-Origin": "*" };
const PING_TIMEOUT_MS = 3500;

interface HostState {
  host: string;
  label: string;
  group: string;
  ok: boolean;
  status: number | null;
  ms: number | null;
}

async function ping(host: string): Promise<{ ok: boolean; status: number | null; ms: number | null }> {
  const started = Date.now();
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), PING_TIMEOUT_MS);
  try {
    const res = await fetch(`https://${host}/`, {
      method: "HEAD",
      redirect: "manual",
      signal: ctrl.signal,
      cache: "no-store",
    });
    // Any HTTP answer (even a 3xx/4xx app page) means the host is live and
    // serving; only a network failure / timeout counts as down. 5xx is degraded.
    return { ok: res.status < 500, status: res.status, ms: Date.now() - started };
  } catch {
    return { ok: false, status: null, ms: null };
  } finally {
    clearTimeout(timer);
  }
}

interface DeployState {
  state: string; // READY | BUILDING | ERROR | ...
  created: number | null; // epoch ms
  url: string | null;
  source: "vercel" | "github";
}

interface VercelDeploy {
  state?: string;
  readyState?: string;
  created?: number;
  url?: string;
}

// Preferred: Vercel-native production deploy. Only runs if a VALID VERCEL_TOKEN
// is set (a CLI session token is rejected — use a dashboard-issued token). Returns
// null on any failure so the GitHub source below takes over.
async function vercelDeploy(): Promise<DeployState | null> {
  const token = process.env.VERCEL_TOKEN;
  if (!token) return null;
  const project = process.env.VERCEL_PROJECT_ID || "arcs-v9";
  const team = process.env.VERCEL_TEAM_ID;
  const qs = new URLSearchParams({ app: project, target: "production", limit: "1" });
  if (team) qs.set("teamId", team);
  try {
    const res = await fetch(`https://api.vercel.com/v6/deployments?${qs.toString()}`, {
      headers: { Authorization: `Bearer ${token}` },
      next: { revalidate: 300 },
    });
    if (!res.ok) return null;
    const data = (await res.json()) as { deployments?: VercelDeploy[] };
    const d = data.deployments?.[0];
    if (!d) return null;
    return {
      state: (d.state || d.readyState || "UNKNOWN").toUpperCase(),
      created: typeof d.created === "number" ? d.created : null,
      url: d.url ? `https://${d.url}` : null,
      source: "vercel",
    };
  } catch {
    return null;
  }
}

// JTBD: show production deploy state on the field board with the fewest secrets.
// TOOL-FIT: GitHub Deployments API over the native Vercel REST deployments API —
//   the Vercel path needs a dashboard-issued VERCEL_TOKEN (the CLI session token is
//   REST-rejected) AND team scoping, while Vercel already mirrors every production
//   deploy + status into GitHub Deployments, readable with the GITHUB_TOKEN we hold
//   anyway. Same signal, one fewer secret.
// EX-ANTE: predict this fits — /api/pulse already reads deploy state this exact way
//   and it works (proven precedent, same-shape job); scored ex-post if it drifts.
//   (Decision-provenance receipt; convention in AGENTS.md gotcha 9.)
//
// Fallback (and the default that actually works today): the GitHub Deployments
// API. Vercel posts each production deploy + its status here, so this IS the
// Vercel deploy state — read with the same GITHUB_TOKEN the pulse route uses, no
// separate Vercel secret required. Mirrors src/app/api/pulse/route.ts.
async function githubDeploy(): Promise<DeployState | null> {
  const token = process.env.GITHUB_TOKEN || process.env.GH_TOKEN;
  const gh = "https://api.github.com/repos/flashesofbrilliance/arcs-v9";
  const headers: Record<string, string> = {
    Accept: "application/vnd.github+json",
    "User-Agent": "arcs-field",
    "X-GitHub-Api-Version": "2022-11-28",
  };
  if (token) headers.Authorization = `Bearer ${token}`;
  try {
    const depRes = await fetch(`${gh}/deployments?per_page=1`, { headers, next: { revalidate: 300 } });
    if (!depRes.ok) return null;
    const deps = (await depRes.json()) as Array<{ id: number; created_at: string }>;
    const dep = deps[0];
    if (!dep) return null;
    const stRes = await fetch(`${gh}/deployments/${dep.id}/statuses?per_page=1`, {
      headers,
      next: { revalidate: 300 },
    });
    const statuses = stRes.ok ? ((await stRes.json()) as Array<{ state: string }>) : [];
    // GitHub deployment-status states: success | failure | error | pending | in_progress | queued.
    // Normalize to the board's READY/ERROR/BUILDING vocabulary.
    const raw = (statuses[0]?.state ?? "pending").toLowerCase();
    const state = raw === "success" ? "READY" : raw === "failure" || raw === "error" ? "ERROR" : "BUILDING";
    return { state, created: Date.parse(dep.created_at) || null, url: null, source: "github" };
  } catch {
    return null;
  }
}

async function latestDeploy(): Promise<DeployState | null> {
  return (await vercelDeploy()) ?? (await githubDeploy());
}

export async function GET() {
  const [hostResults, deploy] = await Promise.all([
    Promise.all(
      FIELD_HOSTS.map(async (h): Promise<HostState> => {
        const r = await ping(h.host);
        return { host: h.host, label: h.label, group: h.group, ...r };
      }),
    ),
    latestDeploy(),
  ]);

  const live = hostResults.filter((h) => h.ok).length;
  const payload = {
    ok: true,
    updated: new Date().toISOString(),
    deploy, // null if VERCEL_TOKEN unset — board shows "deploy state unavailable"
    counts: { live, down: hostResults.length - live, total: hostResults.length },
    hosts: hostResults,
  };
  return NextResponse.json(payload, { headers: CORS });
}
