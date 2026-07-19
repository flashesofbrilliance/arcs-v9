import { NextResponse } from "next/server";

/**
 * GET /api/pulse — cached, CORS-open live build telemetry for the public status
 * surfaces (status.arcs.care, chan.arcs.care, /state-of-union.html).
 *
 * Why this exists: those pages used to hit api.github.com directly from every
 * visitor's browser, which burns GitHub's unauthenticated 60 req/hr-per-IP
 * budget. This route fetches once server-side, is cached at the Vercel CDN via
 * `s-maxage`, and is served to every visitor from cache — so GitHub is hit at
 * most ~once/minute regardless of traffic. Set GITHUB_TOKEN in the Vercel env
 * to lift the origin's own limit to 5000 req/hr (any token can read a public
 * repo); it works without one, just closer to the free ceiling under load.
 */

export const dynamic = "force-dynamic";

const REPO = "flashesofbrilliance/arcs-v9";
const GH = `https://api.github.com/repos/${REPO}`;

const CORS: Record<string, string> = {
  "Access-Control-Allow-Origin": "*",
  // CDN caches the response ~60s and serves stale up to 5 min while it revalidates.
  "Cache-Control": "public, s-maxage=60, stale-while-revalidate=300",
};

function ghHeaders(): Record<string, string> {
  const h: Record<string, string> = {
    Accept: "application/vnd.github+json",
    "User-Agent": "arcs-live-pulse",
    "X-GitHub-Api-Version": "2022-11-28",
  };
  const token = process.env.GITHUB_TOKEN || process.env.GH_TOKEN;
  if (token) h.Authorization = `Bearer ${token}`;
  return h;
}

function gh(path: string): Promise<Response> {
  // no-store here: freshness is gated by the CDN Cache-Control above, so we
  // don't want Next's data cache layered on top (one cache, one mental model).
  return fetch(`${GH}${path}`, { headers: ghHeaders(), cache: "no-store" });
}

interface CommitApi {
  sha: string;
  commit: { message: string; author: { date: string } };
}
interface PrApi {
  number: number;
  title: string;
}
interface DeploymentApi {
  id: number;
  created_at: string;
}
interface DeploymentStatusApi {
  state: string;
}

export async function GET() {
  const payload: Record<string, unknown> = {
    ok: true,
    repo: REPO,
    updated: new Date().toISOString(),
  };

  try {
    const [commitsRes, prsRes, depRes] = await Promise.all([
      gh("/commits?sha=main&per_page=1"),
      gh("/pulls?state=open&per_page=100&sort=updated&direction=desc"),
      gh("/deployments?per_page=1"),
    ]);

    if (commitsRes.ok) {
      const commits = (await commitsRes.json()) as CommitApi[];
      const c = commits[0];
      if (c) {
        payload.commit = {
          sha: c.sha.slice(0, 7),
          message: c.commit.message.split("\n")[0],
          date: c.commit.author.date,
        };
      }
      // Total commit count via the pagination Link header's rel="last" page.
      const link = commitsRes.headers.get("link");
      const m = link ? link.match(/[?&]page=(\d+)>;\s*rel="last"/) : null;
      if (m) payload.commitsTotal = Number(m[1]);
    }

    if (prsRes.ok) {
      const prs = (await prsRes.json()) as PrApi[];
      payload.prsOpen = prs.length;
      payload.prTop = prs[0] ? { number: prs[0].number, title: prs[0].title } : null;
    }

    if (depRes.ok) {
      const deps = (await depRes.json()) as DeploymentApi[];
      const dep = deps[0];
      if (dep) {
        const stRes = await gh(`/deployments/${dep.id}/statuses?per_page=1`);
        const statuses = stRes.ok ? ((await stRes.json()) as DeploymentStatusApi[]) : [];
        payload.deploy = {
          state: statuses[0]?.state ?? "pending",
          date: dep.created_at,
        };
      }
    }

    return NextResponse.json(payload, { headers: CORS });
  } catch {
    // Never hard-fail the widget: return ok:false so the client falls back.
    return NextResponse.json({ ok: false, repo: REPO }, { headers: CORS });
  }
}
