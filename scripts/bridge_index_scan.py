#!/usr/bin/env python3
"""Bridge employer-index scan: curated employer lists -> ATS boards -> winnable reqs -> live board.

stdlib only. Three verbs:

  probe   <names.txt|->        resolve each employer name to a public ATS board (Greenhouse /
                               Ashby / Lever) by probing slug variants; caches hits + misses in
                               employer-index/ats-probe-cache.json. Only a board that returns
                               real jobs counts (the API is ground truth for slugs).
  pull    <index.json>          fetch live reqs for every resolved board, apply the Zach-shape
                               winnable filter (title/level/location), write reqs.jsonl.
  ingest  <reqs.jsonl>          POST to https://jobs.arcs.care/api/jobs as source=bridge_scan,
                               jobid = bridge-<slug>-<sha1(url)[:8]> (idempotent upsert).

Run from the worktree root. Token: `set -a; . ~/.arcs/jobs-pipeline.env; set +a`.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDX = ROOT / "_STATE" / "job-search" / "employer-index"
CACHE = IDX / "ats-probe-cache.json"
UA = {"User-Agent": "Mozilla/5.0 (ARCS bridge-index-scan; +https://arcs.care)"}
TIMEOUT = 12

# ----------------------------------------------------------------------------- http

def get_json(url: str, retries: int = 2):
    """GET -> parsed JSON, or None. 404 is a definitive miss; other failures retry with backoff."""
    req = urllib.request.Request(url, headers=UA)
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                if r.status != 200:
                    return None
                body = r.read()
            try:
                return json.loads(body)
            except ValueError:
                return None
        except urllib.error.HTTPError as e:
            if e.code in (400, 401, 403, 404, 410):
                return None
        except (urllib.error.URLError, TimeoutError, OSError):
            pass
        time.sleep(0.8 * (attempt + 1))
    return None


# ----------------------------------------------------------------------------- ATS adapters

def gh_jobs(slug: str):
    d = get_json(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=false")
    if not isinstance(d, dict) or "jobs" not in d:
        return None
    out = []
    for j in d["jobs"]:
        out.append({
            "title": j.get("title", ""),
            "location": (j.get("location") or {}).get("name", "") or "",
            "url": j.get("absolute_url", ""),
            "updated": j.get("updated_at"),
        })
    return out


def ashby_jobs(slug: str):
    d = get_json(f"https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=false")
    if not isinstance(d, dict) or "jobs" not in d:
        return None
    out = []
    for j in d["jobs"]:
        loc = j.get("location") or ""
        secondary = [s.get("location", "") for s in (j.get("secondaryLocations") or [])]
        if j.get("isRemote"):
            secondary.append("Remote")
        out.append({
            "title": j.get("title", ""),
            "location": "; ".join([x for x in [loc] + secondary if x]),
            "url": j.get("jobUrl") or j.get("applyUrl") or "",
            "updated": j.get("publishedAt"),
            "dept": j.get("department"),
            "team": j.get("team"),
        })
    return out


def lever_jobs(slug: str):
    d = get_json(f"https://api.lever.co/v0/postings/{slug}?mode=json")
    if not isinstance(d, list):
        return None
    out = []
    for j in d:
        cats = j.get("categories") or {}
        locs = [cats.get("location") or ""] + list(cats.get("allLocations") or [])
        if j.get("workplaceType") == "remote":
            locs.append("Remote")
        out.append({
            "title": j.get("text", ""),
            "location": "; ".join(sorted({x for x in locs if x})),
            "url": j.get("hostedUrl") or "",
            "updated": j.get("createdAt"),
            "dept": cats.get("department"),
            "team": cats.get("team"),
        })
    return out


ADAPTERS = {"greenhouse": gh_jobs, "ashby": ashby_jobs, "lever": lever_jobs}

# ----------------------------------------------------------------------------- slugs

STRIP_WORDS = {
    "inc", "inc.", "llc", "l.l.c.", "ltd", "ltd.", "corp", "corp.", "corporation", "co", "co.",
    "company", "the", "group", "holdings", "plc", "lp", "l.p.", "llp", "&", "and", "of",
    "usa", "u.s.", "us", "n.a.", "na", "north", "america", "americas", "international",
    "global", "technologies", "technology", "software", "systems", "financial", "services",
    "bank", "insurance", "health", "healthcare", "pharmaceuticals", "pharma",
}


def slug_variants(name: str) -> list[str]:
    base = name.lower()
    base = re.sub(r"\(.*?\)", " ", base)
    base = base.replace("&", " and ")
    base = re.sub(r"[’'`]", "", base)
    toks = [t for t in re.split(r"[^a-z0-9.+]+", base) if t]
    toks_np = [t.replace(".", "") for t in toks]
    core = [t for t in toks_np if t not in STRIP_WORDS] or toks_np
    joined = "".join(toks_np)
    joined_core = "".join(core)
    dashed = "-".join(toks_np)
    dashed_core = "-".join(core)
    first = core[0] if core else joined
    cands = [joined_core, dashed_core, joined, dashed, first]
    # common suffixes people use for job boards
    for c in list(cands[:2]):
        cands += [c + "careers", c + "jobs", c + "inc", c + "hq", c + "io", c + "ai", c + "labs"]
    if len(core) >= 2:
        cands.append(core[0] + core[1])
        cands.append(core[0] + "-" + core[1])
    seen, out = set(), []
    for c in cands:
        c = c.strip("-")
        if c and c not in seen and len(c) >= 2:
            seen.add(c)
            out.append(c)
    return out


def load_cache() -> dict:
    if CACHE.exists():
        return json.loads(CACHE.read_text())
    return {}


def save_cache(c: dict):
    IDX.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(c, indent=1, sort_keys=True))


def probe_one(name: str, explicit: dict | None = None):
    """Return {'ats':..., 'slug':..., 'n':...} or {'ats': None}. Tries explicit hint first."""
    tried = []
    order = []
    if explicit and explicit.get("ats") and explicit.get("slug"):
        order.append((explicit["ats"], explicit["slug"]))
    for slug in slug_variants(name):
        for ats in ("greenhouse", "ashby", "lever"):
            order.append((ats, slug))
    for ats, slug in order:
        if (ats, slug) in tried:
            continue
        tried.append((ats, slug))
        jobs = ADAPTERS[ats](slug)
        if jobs is not None and len(jobs) > 0:
            return {"ats": ats, "slug": slug, "n": len(jobs), "tried": len(tried)}
        if len(tried) >= 36:
            break
    return {"ats": None, "slug": None, "n": 0, "tried": len(tried)}


def cmd_probe(path: str, hints_path: str | None = None):
    names = [l.strip() for l in (sys.stdin if path == "-" else open(path)) if l.strip() and not l.startswith("#")]
    hints = json.loads(Path(hints_path).read_text()) if hints_path else {}
    cache = load_cache()
    todo = [n for n in names if n not in cache or (cache[n].get("ats") is None and n in hints)]
    print(f"probe: {len(names)} names, {len(todo)} to probe ({len(names) - len(todo)} cached)", file=sys.stderr)

    def work(n):
        r = probe_one(n, hints.get(n))
        r["probed_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        return n, r

    with ThreadPoolExecutor(max_workers=8) as ex:
        for i, (n, r) in enumerate(ex.map(work, todo), 1):
            cache[n] = r
            tag = f"{r['ats']}/{r['slug']} n={r['n']}" if r["ats"] else "MISS"
            print(f"[{i}/{len(todo)}] {n}: {tag}", file=sys.stderr)
            if i % 10 == 0:
                save_cache(cache)
    save_cache(cache)
    # second pass: re-probe misses serially (rate-limit / transient protection)
    misses = [n for n in todo if not cache[n].get("ats")]
    if misses:
        print(f"re-probing {len(misses)} misses serially", file=sys.stderr)
        for n in misses:
            r = probe_one(n, hints.get(n))
            r["probed_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
            if r["ats"]:
                print(f"  recovered {n}: {r['ats']}/{r['slug']} n={r['n']}", file=sys.stderr)
            cache[n] = r
        save_cache(cache)
    hits = {n: cache[n] for n in names if cache[n].get("ats")}
    print(f"probe done: {len(hits)}/{len(names)} resolved", file=sys.stderr)
    return hits


# ----------------------------------------------------------------------------- filter
# Three layers, calibrated 2026-09-11 against the 75 bridge_scan rows already on the board:
#   INCLUDE      title must carry a Zach-shape token (AI / product / transformation / ops / ...)
#   HARD_EXCL    never-fit roles (design, legal, recruiting, clinical, sales quota, HR, finance,
#                marketing, admin, pure SWE unless FDE/applied-AI) — no override
#   SOFT_EXCL    eng-IC / scientist / support flavours that a strong-shape token may override
#   LEVEL_EXCL   below-senior (associate / junior / intern / specialist / coordinator / assistant)

INCLUDE = re.compile(r"""
    \b(ai|a\.i\.|genai|gen\s*ai|generative|llm|ml|machine\s+learning|applied|forward[\s-]*deployed|fde|
       agent(s|ic)?|automation|intelligen(ce|t)|copilot|assistant|
       product\s+(manager|management|lead|director|owner|head|vp|strategist|operations|ops|partnerships)|
       (group|principal|staff|senior|sr\.?|lead|head|director|vp|vice\s+president|chief)[\s,]+(of\s+)?product|
       transformation|innovation|solutions?\s+(architect|engineer|consultant|lead|manager|director)|
       strategy|strategic|architect|
       (business|revenue|product|technical|platform|ai|ml|analytics|data|program|programme|gtm|sales|growth)\s+operations|
       \bops\b|bizops|biz\s+ops|business\s+systems|
       platforms?|principal|staff|
       program\s+(manager|lead|director)|technical\s+program|tpm\b|
       enablement|implementation|customer\s+engineer|
       chief\s+of\s+staff|analytics\s+(lead|manager|director)|
       data\s+(science|scientist)|decision\s+science|
       change\s+management|digital|process\s+(improvement|excellence)|
       head\s+of|general\s+manager|\bgm\b|intelligence)\b
""", re.I | re.X)

LEVEL_EXCL = re.compile(r"\b(associate|junior|jr\.?|intern(ship)?|entry[\s-]level|apprentice|graduate|new\s+grad|co-?op|coordinator|specialist|assistant|analyst\s+i\b)\b", re.I)

HARD_EXCL = re.compile(r"""
    \b(account\s+(executive|manager|director)|\bae\b|sdr\b|bdr\b|sales\s+(development|rep|representative|manager|director|executive)|
       recruit(er|ing|ment)|talent\s+(acquisition|partner|management|operations|sourcer)|sourcer\b|executive\s+search|
       designer|design\b|\bux\b|\bui\b|creative|copywriter|brand|
       counsel|attorney|legal|paralegal|compliance\s+officer|privacy\s+officer|
       clinical|clinician|nurse|physician|therapist|pharmacist|medical\s+(director|assistant)|
       accountant|accounting|controller|treasury|payroll|equity\s+administration|
       (strategic|corporate)\s+finance|fp&a|finance\b|financial\s+(analyst|planning)|
       actuar|underwrit|claims\s+(adjuster|examiner|specialist)|
       procurement|sourcing|supply\s+chain|logistics|facilities|real\s+estate|workplace\s+experience|
       people\s+(strategy|ops|operations|analytics|partner|team)|human\s+resources|\bhr\b|total\s+rewards|compensation\s+&|benefits\s+(manager|analyst|partner|administrator)|
       marketing|content|seo|social\s+media|events?\b|communications|public\s+relations|\bpr\b|
       developer\s+(advocate|relations|evangelist)|evangelist|community\s+manager|
       executive\s+support|administrative|receptionist|office\s+manager|
       warehouse|driver|technician|mechanic|electrician|installer|production\s+assistant|
       store|retail|cashier|barista|chef|cook|
       teacher|instructor|professor|faculty|
       social\s+worker|case\s+manager|
       security\s+(guard|officer)|
       research\s+scientist|postdoc|phd\b)\b
""", re.I | re.X)

SOFT_EXCL = re.compile(r"""
    \b(software\s+(engineer|developer)|swe\b|sde\b|front[\s-]*end|back[\s-]*end|full[\s-]*stack|
       site\s+reliability|sre\b|devops|infrastructure\s+engineer|security\s+engineer|
       data\s+engineer|analytics\s+engineer|ml\s+engineer|machine\s+learning\s+engineer|
       (ios|android|mobile|web|embedded|firmware|kernel|compiler|database|storage|network|
        systems|cloud|qa|test|quality|release|build|tools|platform|distributed|performance|
        graphics|hardware|electrical|mechanical|civil|structural|manufacturing|process|
        controls|automation|field|service|support)\s+engineer|
       engineer(ing)?\s*(i{1,3}|iv|v)?\b|
       scientist\b|analyst\b|
       customer\s+(service|support|success)|
       tax\b)\b
""", re.I | re.X)

# strong-shape override: these beat SOFT_EXCL (never HARD_EXCL)
STRONG = re.compile(r"""
    \b(forward[\s-]*deployed|\bfde\b|applied\s+(ai|ml|scien)|(gen\s*ai|genai|ai|llm|agents?|agentic|generative\s+ai)\s+(platform\s+)?engineer|
       solutions?\s+(architect|engineer|consultant)|customer\s+engineer|business\s+systems|
       product\s+(manager|management|lead|director|owner)|
       head\s+of|director|\bvp\b|vice\s+president|chief|general\s+manager|
       (principal|staff|senior|sr\.?|lead)\s+(applied\s+scientist|data\s+scien\w+|program\s+manager|technical\s+program)|
       transformation|innovation)\b
""", re.I | re.X)

NYC = re.compile(r"\b(new\s+york|nyc|\bny\b|manhattan|brooklyn|jersey\s+city|hoboken|stamford|greenwich|white\s+plains|long\s+island|newark|us[\s-]*east|east\s+coast|northeast)\b", re.I)
REMOTEISH = re.compile(r"\b(remote|anywhere|hybrid|distributed|flexible|virtual|work\s+from\s+home|wfh)\b", re.I)
US_WIDE = re.compile(r"^\s*(remote\s*[-(]?\s*)?(us|usa|u\.s\.|u\.s\.a\.|united\s+states|north\s+america|americas|americas?\s*-?\s*remote|remote)\s*\)?\s*$", re.I)
FOREIGN = re.compile(r"""
    \b(international|emea|apac|latam|europe|uk|u\.k\.|united\s+kingdom|london|ireland|dublin|canada|toronto|vancouver|montreal|
       germany|berlin|munich|france|paris|spain|madrid|barcelona|italy|portugal|lisbon|netherlands|amsterdam|belgium|
       sweden|stockholm|denmark|norway|finland|poland|warsaw|czech|prague|austria|switzerland|zurich|
       india|bangalore|bengaluru|hyderabad|pune|chennai|mumbai|singapore|australia|sydney|melbourne|new\s+zealand|
       japan|tokyo|korea|seoul|china|shanghai|beijing|hong\s+kong|taiwan|philippines|manila|vietnam|indonesia|jakarta|malaysia|kuala\s+lumpur|thailand|bangkok|
       israel|tel\s+aviv|uae|dubai|brazil|sao\s+paulo|mexico|colombia|bogot|argentina|chile|peru|
       south\s+africa|nigeria|kenya|egypt|turkey)\b
""", re.I | re.X)


US_TOKEN = re.compile(r"\b(us|usa|u\.s\.a?\.?|united\s+states|us-[a-z]{2}\b|north\s+america|americas?)\b", re.I)
FOREIGN_CODE = re.compile(r"\b(gb|uk|au|ca|can|de|fr|es|it|nl|se|pl|in|sg|my|id|jp|kr|cn|hk|il|ae|br|mx|co|ar|cl|za|ie|pt|ch|at|be|dk|no|fi|cz|tw|ph|vn|nz|tr|eg|ke|ng)[-:]\s*[a-z]", re.I)


def location_ok(loc: str, title: str = "") -> bool:
    """NYC-metro, or remote/hybrid, or US-wide — but any foreign marker (country name, ISO-code
    prefix like GB-/AU:, or a foreign city in the title) demands an explicit US/NYC token too.
    Unknown/blank => keep (scorer decides)."""
    if not loc:
        return not FOREIGN.search(title)
    foreign = bool(FOREIGN.search(loc) or FOREIGN_CODE.search(loc) or FOREIGN.search(title))
    us = bool(NYC.search(loc) or US_TOKEN.search(loc))
    if foreign and not us:
        return False
    for seg in re.split(r"[;|/]|\s+or\s+", loc):
        seg = seg.strip()
        if not seg:
            continue
        if NYC.search(seg) or US_WIDE.match(seg):
            return True
        if REMOTEISH.search(seg) and not (FOREIGN.search(seg) or FOREIGN_CODE.search(seg)):
            return True
    return False


def title_ok(title: str) -> tuple[bool, str]:
    t = title.strip()
    if LEVEL_EXCL.search(t):
        return False, "below-senior"
    if HARD_EXCL.search(t):
        return False, "hard-excluded-role"
    if not INCLUDE.search(t):
        return False, "no-shape-match"
    if SOFT_EXCL.search(t) and not STRONG.search(t):
        return False, "soft-excluded-role"
    # pure SWE stays out unless FDE / applied-AI shaped
    if re.search(r"software\s+engineer|\bswe\b", t, re.I) and not re.search(r"forward[\s-]*deployed|\bfde\b|applied\s+ai|gen\s*ai", t, re.I):
        return False, "pure-swe"
    return True, "ok"


def fit_hint(title: str) -> int:
    """Cheap 0-10 shape score for ordering only (Thread 2 owns real scoring)."""
    t = title.lower()
    s = 0
    if re.search(r"forward[\s-]*deployed|\bfde\b", t): s += 5
    if re.search(r"\bai\b|genai|generative|llm|agent", t): s += 3
    if re.search(r"applied", t): s += 2
    if re.search(r"product\s+(manager|lead|director|head)|(group|principal|staff|senior|sr|lead|director)\s+product", t): s += 2
    if re.search(r"transformation|innovation|automation|strategy", t): s += 2
    if re.search(r"director|head\s+of|\bvp\b|principal|staff|group", t): s += 1
    if re.search(r"solutions?\s+(architect|engineer)|customer\s+engineer|implementation", t): s += 1
    if re.search(r"operations|\bops\b|platform|program", t): s += 1
    return min(s, 10)


def cmd_pull(index_path: str, out_path: str):
    index = json.loads(Path(index_path).read_text())
    rows, stats = [], {"employers": 0, "reqs_total": 0, "kept": 0, "rej": {}}

    def fetch(item):
        name, meta = item
        jobs = ADAPTERS[meta["ats"]](meta["slug"]) or []
        return name, meta, jobs

    with ThreadPoolExecutor(max_workers=8) as ex:
        for name, meta, jobs in ex.map(fetch, index.items()):
            stats["employers"] += 1
            stats["reqs_total"] += len(jobs)
            for j in jobs:
                ok, why = title_ok(j["title"])
                if ok and not location_ok(j["location"], j["title"]):
                    ok, why = False, "location"
                if not ok:
                    stats["rej"][why] = stats["rej"].get(why, 0) + 1
                    continue
                if not j["url"]:
                    continue
                rows.append({
                    "jobid": f"bridge-{meta['slug']}-{hashlib.sha1(j['url'].encode()).hexdigest()[:8]}",
                    "title": j["title"],
                    "company": meta.get("display", name),
                    "location": j["location"] or None,
                    "url": j["url"],
                    "source": "bridge_scan",
                    "band": "UNSCORED",
                    "unscoredWhy": "bridge index scan",
                    "atsName": meta["ats"],
                    "companyType": meta.get("lists_tag"),
                    "fit_hint": fit_hint(j["title"]),
                })
                stats["kept"] += 1
    # dedupe by jobid
    seen, uniq = set(), []
    for r in rows:
        if r["jobid"] in seen:
            continue
        seen.add(r["jobid"])
        uniq.append(r)
    with open(out_path, "w") as f:
        for r in uniq:
            f.write(json.dumps(r) + "\n")
    stats["unique"] = len(uniq)
    print(json.dumps(stats, indent=1), file=sys.stderr)


# ----------------------------------------------------------------------------- ingest

def cmd_ingest(reqs_path: str, batch: int = 100, force: bool = False):
    """POST new rows only. The API upsert overwrites band/composite, so re-sending a row that the
    scorer (Thread 2) already scored would silently reset it to UNSCORED — skip existing jobids
    unless --force."""
    token = os.environ.get("JOBS_PIPELINE_TOKEN")
    if not token:
        sys.exit("JOBS_PIPELINE_TOKEN missing: set -a; . ~/.arcs/jobs-pipeline.env; set +a")
    rows = [json.loads(l) for l in open(reqs_path) if l.strip()]
    if not force:
        req = urllib.request.Request("https://jobs.arcs.care/api/jobs", headers={**UA, "x-jobs-token": token})
        with urllib.request.urlopen(req, timeout=120) as r:
            existing = {x["jobid"] for x in json.loads(r.read())["rows"]}
        skipped = sum(1 for r in rows if r["jobid"] in existing)
        rows = [r for r in rows if r["jobid"] not in existing]
        print(f"ingest: {skipped} already on board (skipped), {len(rows)} new", file=sys.stderr)
    keep = ("jobid", "title", "company", "location", "url", "source", "band", "unscoredWhy", "atsName", "companyType")
    total = 0
    for i in range(0, len(rows), batch):
        chunk = [{k: r.get(k) for k in keep} for r in rows[i:i + batch]]
        req = urllib.request.Request(
            "https://jobs.arcs.care/api/jobs",
            data=json.dumps(chunk).encode(),
            headers={**UA, "Content-Type": "application/json", "x-jobs-token": token},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.loads(r.read())
        total += d.get("upserted", 0)
        print(f"batch {i // batch + 1}: upserted {d.get('upserted')}", file=sys.stderr)
    print(f"ingest done: {total}/{len(rows)} upserted", file=sys.stderr)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "probe":
        hits = cmd_probe(a[1], a[2] if len(a) > 2 else None)
        print(json.dumps(hits, indent=1, sort_keys=True))
    elif a[0] == "pull":
        cmd_pull(a[1], a[2])
    elif a[0] == "ingest":
        cmd_ingest(a[1], force="--force" in a)
    elif a[0] == "verify":
        pass  # dispatched below (defined after main block)
    else:
        sys.exit(__doc__)


# ----------------------------------------------------------------------------- verify (slug collision guard)

def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def cmd_verify(index_path: str):
    """For each resolved board, check the board actually belongs to the named employer.
    Greenhouse exposes the board name; Ashby/Lever do not, so those are flagged for eyeball
    when the slug came from a short/generic variant. Writes verify field into the index."""
    index = json.loads(Path(index_path).read_text())
    for name, meta in index.items():
        n = _norm(name)
        core = _norm("".join(t for t in re.split(r"[^a-z0-9]+", name.lower()) if t and t not in STRIP_WORDS))
        if meta["ats"] == "greenhouse":
            d = get_json(f"https://boards-api.greenhouse.io/v1/boards/{meta['slug']}")
            bname = (d or {}).get("name", "") if isinstance(d, dict) else ""
            bn = _norm(bname)
            ok = bool(bn) and (bn in n or n in bn or core in bn or bn in core or bn[:6] == core[:6])
            meta["board_name"] = bname
            meta["verify"] = "ok" if ok else "MISMATCH"
        else:
            slug = _norm(meta["slug"])
            ok = slug == core or slug == n or (len(slug) >= 6 and (slug in core or core in slug))
            meta["verify"] = "ok" if ok else "REVIEW"
    Path(index_path).write_text(json.dumps(index, indent=1, sort_keys=True))
    bad = {k: v for k, v in index.items() if v["verify"] != "ok"}
    print(json.dumps(bad, indent=1, sort_keys=True))
    print(f"verify: {len(index) - len(bad)} ok, {len(bad)} flagged", file=sys.stderr)


if __name__ == "__main__" and sys.argv[1:2] == ["verify"]:
    cmd_verify(sys.argv[2])
