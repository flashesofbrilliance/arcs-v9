import { NextResponse } from "next/server";
import { prisma } from "@/lib/db";
import {
  assertPublicSafe,
  riskStates,
  shapeGates,
  shapeTempo,
  summarizeDebt,
  weekStarts,
  type CohortCounts,
  type DebtIssue,
} from "@/lib/pulse";

/**
 * GET /api/pulse — cached, CORS-open live telemetry for the public status surfaces
 * (status.arcs.care and friends).
 *
 * The repo is PRIVATE, so every GitHub read happens here, server-side, with
 * GITHUB_TOKEN (never sent to the browser). The page no longer calls api.github.com.
 * Shaping and the public-safety check live in src/lib/pulse.ts: counts, trends and
 * curated slugs only, never an issue title or body. A section whose read failed is
 * `null` (never 0) and named in `degraded`, so the page keeps its static floor.
 */

// ISR: regenerated at most once per window. One regeneration = ~4 REST + 3 GraphQL
// calls + 2 small DB counts.
export const revalidate = 600;

const OWNER = "flashesofbrilliance";
const NAME = "arcs-v9";
const REPO = `${OWNER}/${NAME}`;
const GH = `https://api.github.com/repos/${REPO}`;
const TEMPO_WEEKS = 12;
// Mirrors operators/prod_receipt_to_accountant.py FOUNDER_EMAILS: the founder QA account is
// its own cohort and never counts toward the external calibration gate. Server-side only.
const FOUNDER_EMAILS = new Set(["zach.harris@gmail.com"]);

const CORS: Record<string, string> = { "Access-Control-Allow-Origin": "*" };

function token(): string | undefined {
  return process.env.GITHUB_TOKEN || process.env.GH_TOKEN || undefined;
}

function ghHeaders(): Record<string, string> {
  const h: Record<string, string> = {
    Accept: "application/vnd.github+json",
    "User-Agent": "arcs-live-pulse",
    "X-GitHub-Api-Version": "2022-11-28",
  };
  const t = token();
  if (t) h.Authorization = `Bearer ${t}`;
  return h;
}

function rest(path: string): Promise<Response> {
  return fetch(`${GH}${path}`, { headers: ghHeaders(), next: { revalidate: 600 } });
}

async function graphql<T>(query: string, variables: Record<string, unknown> = {}): Promise<T | null> {
  if (!token()) return null; // GraphQL has no anonymous access
  const r = await fetch("https://api.github.com/graphql", {
    method: "POST",
    headers: { ...ghHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify({ query, variables }),
    next: { revalidate: 600 },
  });
  if (!r.ok) return null;
  const j = (await r.json()) as { data?: T; errors?: unknown };
  return j.errors || !j.data ? null : j.data;
}

async function safe<T>(p: Promise<T>): Promise<T | null> {
  try {
    return await p;
  } catch {
    return null;
  }
}

async function readCommit() {
  const r = await rest("/commits?sha=main&per_page=1");
  if (!r.ok) return null;
  const c = ((await r.json()) as Array<{ sha: string; commit: { author: { date: string } } }>)[0];
  const m = (r.headers.get("link") || "").match(/[?&]page=(\d+)>;\s*rel="last"/);
  return {
    // The commit MESSAGE stays server-side: messages can name files and people.
    commit: c ? { sha: c.sha.slice(0, 7), date: c.commit.author.date } : null,
    commitsTotal: m ? Number(m[1]) : null,
  };
}

async function readDeploy() {
  // Vercel posts a GitHub deployment per deploy; the newest one is the last Vercel deploy.
  const r = await rest("/deployments?per_page=1");
  if (!r.ok) return null;
  const dep = ((await r.json()) as Array<{ id: number; created_at: string }>)[0];
  if (!dep) return null;
  const s = await rest(`/deployments/${dep.id}/statuses?per_page=1`);
  const st = s.ok ? ((await s.json()) as Array<{ state: string }>)[0]?.state : undefined;
  return { state: st ?? "pending", date: dep.created_at };
}

async function readOpenPrs(): Promise<number | null> {
  const d = await graphql<{ repository: { pullRequests: { totalCount: number } } }>(
    `query{repository(owner:"${OWNER}",name:"${NAME}"){pullRequests(states:OPEN){totalCount}}}`,
  );
  return d ? d.repository.pullRequests.totalCount : null;
}

async function readDebt(): Promise<DebtIssue[] | null> {
  // GraphQL, not REST: both REST issue lists lag fresh issues by minutes (measured 2026-10-06).
  type Page = { repository: { issues: { nodes: Array<{ number: number; state: "OPEN" | "CLOSED"; labels: { nodes: { name: string }[] } }>; pageInfo: { hasNextPage: boolean; endCursor: string | null } } } };
  const out: DebtIssue[] = [];
  let after: string | null = null;
  for (let page = 0; page < 5; page++) {
    const d: Page | null = await graphql<Page>(
      `query($after:String){repository(owner:"${OWNER}",name:"${NAME}"){issues(first:100,after:$after,labels:["debt"]){nodes{number state labels(first:10){nodes{name}}}pageInfo{hasNextPage endCursor}}}}`,
      { after },
    );
    if (!d) return null;
    for (const n of d.repository.issues.nodes) out.push({ number: n.number, state: n.state, labels: n.labels.nodes.map((l) => l.name) });
    if (!d.repository.issues.pageInfo.hasNextPage) break;
    after = d.repository.issues.pageInfo.endCursor;
  }
  return out;
}

async function readTempo(now: Date) {
  const weeks = weekStarts(now, TEMPO_WEEKS);
  const fields = weeks.map((w, k) => {
    const end = new Date(`${w}T00:00:00Z`);
    end.setUTCDate(end.getUTCDate() + 6);
    const q = `repo:${REPO} is:pr is:merged base:main merged:${w}..${end.toISOString().slice(0, 10)}`;
    return `w${k}:search(query:${JSON.stringify(q)},type:ISSUE,first:0){issueCount}`;
  });
  const d = await graphql<Record<string, { issueCount: number }>>(`query{${fields.join(" ")}}`);
  if (!d) return null;
  return shapeTempo(weeks, weeks.map((_, k) => d[`w${k}`]?.issueCount ?? null));
}

async function readCohorts(): Promise<CohortCounts | null> {
  if (!process.env.DATABASE_URL) return null;
  const [receipts, external, outcomes] = await Promise.all([
    prisma.receipt.count(),
    prisma.receipt.count({ where: { userId: { not: null }, NOT: { user: { email: { in: [...FOUNDER_EMAILS] } } } } }),
    prisma.outcome.findMany({ select: { receipt: { select: { userId: true, user: { select: { email: true } } } } } }),
  ]);
  const closed = { founder: 0, external: 0, anonymous: 0 };
  for (const o of outcomes) {
    const email = o.receipt.user?.email?.toLowerCase();
    if (!o.receipt.userId) closed.anonymous += 1;
    else if (email && FOUNDER_EMAILS.has(email)) closed.founder += 1;
    else closed.external += 1;
  }
  return { receipts, externalReceipts: external, closed };
}

export async function GET() {
  const now = new Date();
  const [commit, deploy, prsOpen, debtIssues, tempo, cohorts] = await Promise.all([
    safe(readCommit()),
    safe(readDeploy()),
    safe(readOpenPrs()),
    safe(readDebt()),
    safe(readTempo(now)),
    safe(readCohorts()),
  ]);

  const debt = summarizeDebt(debtIssues);
  const gates = shapeGates(cohorts);
  const payload = {
    ok: true,
    updated: now.toISOString(),
    commit: commit?.commit ?? null,
    commitsTotal: commit?.commitsTotal ?? null,
    prsOpen,
    deploy,
    debt,
    risks: riskStates(debtIssues),
    tempo,
    gates,
    // No efficacy-loop results exist yet; every claim in section 09 reads "not run".
    evals: null,
    degraded: [] as string[],
  };
  for (const k of ["commit", "deploy", "prsOpen", "debt", "risks", "tempo", "gates"] as const) {
    if (payload[k] == null) payload.degraded.push(k);
  }

  if (assertPublicSafe(payload).length) {
    // Fail closed: a payload that could leak is never served. The page keeps its floor.
    return NextResponse.json({ ok: false }, { headers: CORS });
  }
  return NextResponse.json(payload, { headers: CORS });
}
