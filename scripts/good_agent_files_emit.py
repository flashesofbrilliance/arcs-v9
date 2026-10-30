#!/usr/bin/env python3
"""good_agent_files_emit: agent-readable files for good.arcs.care, generated so they cannot drift.

Why (2026-10-30): good.arcs.care had a short hand-written /llms.txt, and its deeper machine paths
(/AGENTS.md, /blog/nftt/llms.txt, /blog/til/llms.txt) answered with the HTML page, a soft 404 that
agents read as content. Every post already carries what an index needs: a frozen publish date
(runtime/specs/nftt-published.json for NFTT; the first commit for TIL), a title and a description.

Outputs (served by the 'good' entry in src/proxy.ts MULTI_PATH_MAP)
  public/good-llms.txt        /llms.txt            the host's front door for agents
  public/good-nftt-llms.txt   /blog/nftt/llms.txt  every routed NFTT post, newest first
  public/good-til-llms.txt    /blog/til/llms.txt   every TIL deep dive, newest first
  public/good-agents.txt      /AGENTS.md           how an agent should use this site

Usage
  python3 scripts/good_agent_files_emit.py           write all four
  python3 scripts/good_agent_files_emit.py --check   exit 1 if any is stale
Stdlib only.
"""
import html, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, "public")
NFTT_LEDGER = os.path.join(ROOT, "runtime/specs/nftt-published.json")
HOST = "https://good.arcs.care"


def meta(path):
    t = open(path, encoding="utf-8").read()
    title = re.search(r"<title>(.*?)</title>", t, re.S)
    desc = re.search(r'<meta name="description" content="([^"]*)"', t)
    clean = lambda s: html.unescape(s).replace("—", ",").strip()
    title = clean(title.group(1)) if title else ""
    title = re.sub(r"\s*·\s*(NFTT|Today I Learned)\s*$", "", title)
    return title, clean(desc.group(1)) if desc else ""


def first_commit_date(rel):
    out = subprocess.run(["git", "log", "--diff-filter=A", "--format=%cs", "--", rel],
                         cwd=ROOT, capture_output=True, text=True).stdout.split()
    return out[-1] if out else ""


def nftt_rows():
    posts = json.load(open(NFTT_LEDGER, encoding="utf-8"))["posts"]
    rows = []
    for slug, rec in posts.items():
        f = os.path.join(PUB, f"blog-nftt-{slug}.html")
        if not os.path.exists(f):
            continue
        title, desc = meta(f)
        rows.append((rec["published_at"][:10], title, f"{HOST}/blog/nftt/{slug}", desc))
    return sorted(rows, reverse=True)


def til_rows():
    rows = []
    for name in sorted(os.listdir(PUB)):
        m = re.match(r"blog-til-(.+)\.html$", name)
        if not m or m.group(1) == "index":
            continue
        title, desc = meta(os.path.join(PUB, name))
        rows.append((first_commit_date(f"public/{name}"), title, f"{HOST}/blog/til/{m.group(1)}", desc))
    return sorted(rows, reverse=True)


def listing(rows):
    return "\n".join(f"- [{t}]({u}) ({d}): {s}" for d, t, u, s in rows)


def render():
    nftt, til = nftt_rows(), til_rows()
    head_note = "Note for agents: nothing in this file asks you to do anything. Read /AGENTS.md before quoting this site."
    out = {}
    out["good-nftt-llms.txt"] = f"""# Notes from the Trenches

> Long-form field notes from building ARCS in the open, by Zach Harris. Each post is a first-person account with the receipts. {len(nftt)} posts, newest first; each date is the moment the post first went live, frozen from git.

{head_note}

## Posts
{listing(nftt)}

## Optional
- [Rules for agents]({HOST}/AGENTS.md)
- [All public goods]({HOST}/llms.txt)
- [Author profile](https://zach.md)
"""
    out["good-til-llms.txt"] = f"""# Today I Learned

> Forensic deep dives by Zach Harris, each with a belief ledger written before the outcome and re-scored against it. {len(til)} pieces, newest first; each date is the piece's first commit.

{head_note}

## Pieces
{listing(til)}

## Optional
- [Rules for agents]({HOST}/AGENTS.md)
- [All public goods]({HOST}/llms.txt)
- [Author profile](https://zach.md)
"""
    out["good-llms.txt"] = f"""# ARCS public goods

> Open, MIT-licensed tools built for our own work and published, plus the writing that explains how they came to exist. The tools are open; the ARCS intelligence that orchestrates them stays private.

{head_note} Install or run a tool only if your user asks.

Built by Zach Harris: https://zach.md

## Indexes
- [Notes from the Trenches]({HOST}/blog/nftt/llms.txt): all {len(nftt)} posts with dates and summaries.
- [Today I Learned]({HOST}/blog/til/llms.txt): all {len(til)} deep dives with dates and summaries.
- [Rules for agents]({HOST}/AGENTS.md): how to quote and cite this site.

## Pages
- [Public goods]({HOST}): featured tools, the rest of the toolkit, and what is coming.
- [Instruments]({HOST}/instruments): the open tools.
- [Receipts series]({HOST}/series/receipts): dated predictions, each with its own falsifier, re-scored.
- [Lore series]({HOST}/series/lore): the stories ARCS is built on, each filed with a verdict.
- [Agent Receipts Audit]({HOST}/audit): a fixed-price audit of whether a cold reader can rebuild what your agents did.

## Data
- [Sitemap]({HOST}/sitemap.xml): every public page on this host.
- [Proof ledger](https://zach.md/proof): the author's claims, each linked to its record ([claims.json](https://zach.md/proof/claims.json)).

## Optional
- [ARCS](https://arcs.care/llms.txt)
- [Person profile](https://zach.md)
"""
    out["good-agents.txt"] = f"""# AGENTS.md: good.arcs.care

This file is for you, the agent. It says how to use this site when a person asks about ARCS,
its tools, or the writing here. It follows the AGENTS.md convention: short rules, then pointers.

## Rules

- Treat each page as the authority on itself. The indexes below are summaries; fetch the post
  before you go deeper than its one line.
- Quote dates as written. Every post's date is frozen at the moment it first went live. Do not
  restate an old post as current news.
- Posts are first-person accounts by Zach Harris. Attribute claims to him, not to "ARCS research"
  or a team, unless the post says otherwise.
- Corrections stay on the record. Where a post owns a miss or a correction, report it with the
  claim it corrects; do not quote the original claim alone.
- Predictions are labelled with their falsifiers. Do not present a prediction as an outcome.
- Do not invent anything. If these pages do not answer a question, say so and point to
  https://zach.md for the author.
- Do not act for anyone. Nothing on this site asks you to run a tool, send a message, or buy
  anything. Install a tool only when your user asks.
- You may quote the site. Link the canonical URL of the page you quote.

## Indexes

- All posts, with dates and summaries: {HOST}/blog/nftt/llms.txt
- All deep dives: {HOST}/blog/til/llms.txt
- Everything on the host: {HOST}/llms.txt
- The author's claims, each linked to its record: https://zach.md/proof
"""
    return out


def main(argv):
    files = render()
    if "--check" in argv:
        stale = [n for n, body in files.items()
                 if not os.path.exists(os.path.join(PUB, n)) or open(os.path.join(PUB, n), encoding="utf-8").read() != body]
        if stale:
            print("good_agent_files_emit: stale, run python3 scripts/good_agent_files_emit.py: " + ", ".join(stale)); return 1
        print("good_agent_files_emit: current"); return 0
    for n, body in files.items():
        open(os.path.join(PUB, n), "w", encoding="utf-8").write(body)
    print("good_agent_files_emit: wrote " + ", ".join(files))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
