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

// ISR: the route response is cached and regenerated at most once per window.
// 600s keeps GitHub calls (~5 per regeneration: commits, pulls, deployments,
// deploy-status, issues) at ~30 req/hr — comfortably under the unauthenticated
// 60 req/hr ceiling even with constant traffic. Set GITHUB_TOKEN to lift the
// origin to 5000/hr, after which this can safely drop back to 60–300.
export const revalidate = 600;

const REPO = "flashesofbrilliance/arcs-v9";
const GH = `https://api.github.com/repos/${REPO}`;

const CORS: Record<string, string> = {
  "Access-Control-Allow-Origin": "*",
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
  // Align the data-cache window with the route's ISR window (600s) so the whole
  // response regenerates as one unit — otherwise the shorter fetch-cache wins and
  // GitHub gets hit twice as often as the route's rate-limit budget assumes.
  return fetch(`${GH}${path}`, { headers: ghHeaders(), next: { revalidate: 600 } });
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
interface IssueApi {
  // The REST /issues endpoint returns PRs too; a PR carries this key, a plain
  // issue does not. We filter PRs out so the status counts are issues only.
  pull_request?: unknown;
  state: string; // "open" | "closed"
  state_reason?: string | null; // "completed" | "not_planned" | "reopened" | null
  labels: Array<{ name: string } | string>;
}

// The status-board buckets ARE these GitHub Issue labels — one per issue.
// Keep this list in sync with the labels used when triaging work.
const STATUS_LABELS = ["in-progress", "blocked", "next"] as const;

function labelNames(issue: IssueApi): string[] {
  return issue.labels.map((l) => (typeof l === "string" ? l : l.name));
}

export async function GET() {
  const payload: Record<string, unknown> = {
    ok: true,
    repo: REPO,
    updated: new Date().toISOString(),
  };

  try {
    const [commitsRes, prsRes, depRes, issuesRes] = await Promise.all([
      gh("/commits?sha=main&per_page=1"),
      gh("/pulls?state=open&per_page=100&sort=updated&direction=desc"),
      gh("/deployments?per_page=1"),
      // All issues (open + closed) drive the live status board in ONE call:
      // open-by-label → the three backlog buckets; closed-completed → shipped.
      // per_page=100 covers the whole set today; if it ever exceeds 100 this
      // undercounts — the truncated flag says so rather than lying.
      gh("/issues?state=all&per_page=100"),
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

    if (issuesRes.ok) {
      const raw = (await issuesRes.json()) as IssueApi[];
      const issues = raw.filter((i) => !i.pull_request); // drop PRs
      const open = issues.filter((i) => i.state === "open");
      const counts: Record<string, number> = {};
      for (const label of STATUS_LABELS) {
        counts[label] = open.filter((i) => labelNames(i).includes(label)).length;
      }
      // Shipped = closed issues that were actually completed (exclude the ones
      // closed as not-planned/duplicate — those aren't shipped, they're dropped).
      const shipped = issues.filter(
        (i) => i.state === "closed" && i.state_reason !== "not_planned",
      ).length;
      const link = issuesRes.headers.get("link");
      payload.issues = {
        // Every bucket now live from GitHub Issues — the whole board is real.
        shipped,
        inProgress: counts["in-progress"],
        blocked: counts["blocked"],
        next: counts["next"],
        openTotal: open.length,
        // Honesty flag: if there's a next page the set exceeds 100 and these are
        // a floor, not exact. The client labels it "floor" rather than lying.
        truncated: !!(link && /rel="next"/.test(link)),
      };
    }

    return NextResponse.json(payload, { headers: CORS });
  } catch {
    // Never hard-fail the widget: return ok:false so the client falls back.
    return NextResponse.json({ ok: false, repo: REPO }, { headers: CORS });
  }
}
