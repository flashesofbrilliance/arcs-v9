#!/usr/bin/env python3
"""
resume_ats_render — turn a designed ARCS resume into an ATS-safe companion.

WHY THIS EXISTS
The designed resume (glassmorphic card spine, 2-column pillars, 6-cell skills grid, telemetry
band) is a *print/leave-behind* artifact. Run `pdftotext` over it and it fails as an ATS input in
three measurable ways, all verified against the real files on 2026-08-31:

  1. decorative glyphs baked into the text stream (literal U+25C6/25C7/25CF next to company names)
  2. the skills grid extracts all six LABELS as one block and all six BODIES as another, so the
     label->content pairing is destroyed
  3. multi-column flow interleaves reading order: a section header can land between two pillars,
     and an employer's dates can detach from the employer (ATS computes tenure from those)

None of that is fixable without abandoning the design, so the correct answer is two artifacts:
upload the ATS PDF to the portal, send the designed PDF as the leave-behind. This script generates
the former from the latter, so the pair cannot drift.

DELIBERATE ATS RULES ENFORCED IN THE OUTPUT
single column (no grid/flex/table) · standard section headers · no decorative glyphs and no
CSS-generated marks · employer and dates on adjacent lines · one common font · no page frame,
header, or footer · black on white · no invented job titles (a consulting entry that carries only
a date range is emitted as "Advisory engagement, <dates>", never a fabricated title).

USAGE
    python3 scripts/resume_ats_render.py _ARTIFACTS/resume-x/resume-x.html
    python3 scripts/resume_ats_render.py _ARTIFACTS/resume-x/resume-x.html --out custom-ats.html
Writes <stem>-ats.html next to the input. Render it with that folder's render.sh.
"""
from __future__ import annotations
import argparse
import html
import os
import re
import sys

# ---------- tiny HTML helpers (stdlib only; no new deps per CLAUDE.md) ----------

def strip_tags(frag: str) -> str:
    frag = re.sub(r"<br\s*/?>", "\n", frag, flags=re.I)
    # tags become a SPACE, not nothing, so text on either side of an inline tag
    # (e.g. "<b>In practice</b>ARCS" or "<span>A</span><span>Forward") never fuses
    # into one word. norm() collapses the resulting runs and tidies stray spaces.
    frag = re.sub(r"<[^>]+>", " ", frag)
    return html.unescape(frag)


def norm(s: str) -> str:
    """Collapse whitespace and normalise typography that ATS parsers mangle."""
    # an en-dash means "to" only between numbers (a date range); elsewhere it is a separator
    s = re.sub(r"(\d)\s*\u2013\s*(\d)", r"\1 to \2", s)
    s = re.sub(r"(\d)\s*\u2013\s*(Present)", r"\1 to \2", s, flags=re.I)
    s = s.replace("\u2013", ", ").replace("\u2014", ", ")   # remaining en/em dash
    s = s.replace("·", ", ").replace("↔", " to ").replace("→", " to ")
    s = s.replace("‘", "'").replace("’", "'")
    s = s.replace("“", '"').replace("”", '"')
    s = re.sub(r"[◆◇●○•]", "", s)      # decorative glyphs
    s = re.sub(r"\s+", " ", s).strip()
    # stray spaces left by stripping inline tags to a space:
    s = re.sub(r"\s+([,.;:)])", r"\1", s)          # no space before closing punctuation
    s = re.sub(r"(?<=\S)/ +", "/", s)              # "in/ zharris" -> "in/zharris" (keeps "TS / JS")
    s = re.sub(r",\s*,", ",", s)
    return s.strip(" ,")


def grab(pattern: str, s: str, flags=re.S) -> str | None:
    m = re.search(pattern, s, flags)
    return m.group(1) if m else None


def grab_all(pattern: str, s: str, flags=re.S) -> list[str]:
    return re.findall(pattern, s, flags)


DATE_ONLY = re.compile(r"^\s*(?:19|20)\d{2}(?:\s*(?:to|-)\s*(?:(?:19|20)\d{2}|Present))?\s*$", re.I)

# ---------- extraction ----------

def parse(src: str) -> dict:
    doc: dict = {}
    doc["name"] = norm(strip_tags(grab(r'<div class="name">(.*?)</div>', src) or "Resume"))
    doc["tagline"] = norm(strip_tags(grab(r'<div class="tagline">(.*?)</div>', src) or ""))
    doc["target"] = norm(strip_tags(grab(r'<div class="target">(.*?)</div>', src) or ""))

    contact = grab(r'<div class="contact">(.*?)</div>', src) or ""
    doc["contact"] = [norm(x) for x in strip_tags(contact).split("\n") if norm(x)]

    doc["thesis"] = norm(strip_tags(grab(r'<p class="thesis">(.*?)</p>', src) or ""))

    doc["pillars"] = [norm(strip_tags(p)) for p in
                      grab_all(r'<span class="pt">(.*?)</span>', src)]

    # jobs, in document order, tagged with the section they sit in
    jobs = []
    for sec in grab_all(r'<section class="card".*?>(.*?)</section>', src):
        # the lv span nests <span class="n">NN</span>; drop it so the lazy match sees the real label
        sec_lbl = re.sub(r'<span class="n">.*?</span>', "", sec, flags=re.S)
        label = norm(strip_tags(grab(r'<span class="lv">(.*?)</span>', sec_lbl) or ""))
        label = re.sub(r"^\d+\s*", "", label)
        # .job contains nested <div>s, so a lazy `.*?</div>` closes too early.
        # Split on job boundaries instead and take each chunk whole.
        for jb in re.split(r'(?=<div class="job"[ >])', sec):
            if not jb.lstrip().startswith('<div class="job"'):
                continue
            # class may carry extra tokens (e.g. "job-co gs" from the drawn-glyph fix)
            co_raw = grab(r'<div class="job-co[^"]*"[^>]*>(.*?)</div>', jb)
            if not co_raw:
                continue
            dom = grab(r'<span class="dom">(.*?)</span>', co_raw) or ""
            # dom opens with a separator dash in the designed markup; it is not prose
            dom = re.sub(r"^\s*(?:&[mn]dash;|[-\u2013\u2014])\s*", "", dom)
            company = norm(strip_tags(re.sub(r'<span class="dom">.*?</span>', "", co_raw)))
            role = norm(strip_tags(grab(r'<div class="job-role">(.*?)</div>', jb) or ""))
            summ = norm(strip_tags(grab(r'<div class="job-sum">(.*?)</div>', jb) or ""))
            bullets = [norm(strip_tags(b)) for b in grab_all(r"<li>(.*?)</li>", jb)]
            jobs.append({"section": label, "company": company, "dom": norm(strip_tags(dom)),
                         "role": role, "summary": summ,
                         "bullets": [b for b in bullets if b]})
    doc["jobs"] = jobs

    # Any .card section that yielded no job/skill/pillar/edu/oss content would otherwise be
    # DROPPED SILENTLY. resume-general's "Deep Profile" / role-fit panels carry real evidence
    # (metrics, IN PRACTICE blocks), so capture them generically rather than lose them.
    doc["results"] = [
        (norm(strip_tags(n)), norm(strip_tags(k)))
        for n, k in grab_all(r'<div class="stat"><div class="n">(.*?)</div><div class="k">(.*?)</div>', src)
    ]

    extras = []
    for sec in grab_all(r'<section class="card".*?>(.*?)</section>', src):
        if re.search(r'class="(?:job|skill-k|pillar|edu-line|cc-h)', sec):
            continue
        if 'class="telem"' in sec:      # emitted compactly as Selected Results instead
            continue
        sec_lbl = re.sub(r'<span class="n">.*?</span>', "", sec, flags=re.S)
        head = norm(strip_tags(grab(r'<span class="lv">(.*?)</span>', sec_lbl) or ""))
        head = re.sub(r"^\d+\s*", "", head)
        items = []
        for blk in grab_all(r'<div class="(?:dp-h|h|dp-li|ip|dp-adv|dp-tension|dp-role|rt|rl|rd|t|s|m|d|k)"[^>]*>(.*?)</div>', sec):
            v = norm(strip_tags(blk))
            if v and v not in items:
                items.append(v)
        if not items:
            v = norm(strip_tags(re.sub(r'<div class="sec">.*?</div>', "", sec, flags=re.S)))
            if v:
                items = [v]
        if items:
            extras.append({"heading": head or "Additional Detail", "items": items})
    doc["extras"] = extras

    ks = grab_all(r'<div class="skill-k"[^>]*>(.*?)</div>', src)
    vs = grab_all(r'<div class="skill-v"[^>]*>(.*?)</div>', src)
    doc["skills"] = [(norm(strip_tags(k)), norm(strip_tags(v))) for k, v in zip(ks, vs)]

    hs = grab_all(r'<div class="cc-h"[^>]*>(.*?)</div>', src)
    ls = grab_all(r'<div class="cc-lede"[^>]*>(.*?)</div>', src)
    doc["oss"] = [(norm(strip_tags(h)), norm(strip_tags(l))) for h, l in zip(hs, ls)]

    edu_block = grab(r'<div class="edu-line"[^>]*>(.*?)</div>\s*</section>', src) or ""
    doc["education"] = [norm(strip_tags(x)) for x in
                        grab_all(r"<span>(.*?)</span>", edu_block)] if edu_block else []
    return doc


# ---------- emission ----------

CSS = """  /* ATS-SAFE RENDER, generated by scripts/resume_ats_render.py - do not hand-edit.
     Single column (no grid/flex/table), standard section headers, no decorative glyphs and no
     CSS-generated marks, employer and dates on adjacent lines, one common font, no page frame,
     no header/footer, black on white. */
  @page{size:letter;margin:0.5in;}
  *{box-sizing:border-box;margin:0;padding:0;}
  body{font-family:Arial,Helvetica,sans-serif;font-size:9.05pt;line-height:1.22;color:#000;background:#fff;}
  h1{font-size:17pt;line-height:1.1;margin-bottom:2pt;}
  .sub{font-size:9.6pt;margin-bottom:1.5pt;}
  .contact{font-size:9.2pt;margin-bottom:8pt;}
  h2{font-size:10.5pt;text-transform:uppercase;letter-spacing:.04em;
     margin:6pt 0 2.5pt;padding-bottom:1pt;border-bottom:1px solid #000;}
  h3{font-size:9.4pt;margin:5pt 0 1pt;}
  .role{font-size:9.4pt;font-style:italic;margin-bottom:2pt;}
  p{margin-bottom:3.5pt;}
  ul{margin:0 0 3.5pt 16pt;}
  li{margin-bottom:1.6pt;}
  .kv{margin-bottom:3.5pt;}
  /* Page-break logic: a section header never sits alone at the foot of a page (it moves to the
     next page with its content), a job entry stays intact rather than splitting across the break,
     and paragraphs keep >=2 lines together on each side. */
  h2{break-after:avoid-page;}
  h3{break-after:avoid-page;}
  .role{break-after:avoid-page;}
  .entry{break-inside:avoid;}
  p,li{orphans:2;widows:2;}"""


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def emit(doc: dict) -> str:
    o: list[str] = []
    a = o.append
    a("<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">")
    title = f"{doc['name']} - Resume"
    if doc["target"]:
        title += " - " + re.sub(r"^Target,?\s*", "", doc["target"], flags=re.I)
    a(f"<title>{esc(title)}</title>\n<style>\n{CSS}\n</style>\n</head>\n<body>\n")

    a(f"<h1>{esc(doc['name'])}</h1>")
    if doc["tagline"]:
        a(f'<div class="sub">{esc(doc["tagline"])}</div>')
    # The designed resume shows the applied-for role as a styled badge. Deliberately NOT emitted
    # here: ATS parsers treat the headline block beside the name as the candidate's CURRENT title,
    # so "Target, Director, Product Development" can be ingested as his title. The application form
    # already captures which role this is for.
    if doc["contact"]:
        a('<div class="contact">' + "<br>\n".join(esc(c) for c in doc["contact"]) + "</div>\n")

    if doc["thesis"]:
        a("<h2>Summary</h2>")
        a(f"<p>{esc(doc['thesis'])}</p>\n")

    if doc["pillars"]:
        a("<h2>Core Strengths</h2>\n<ul>")
        for p in doc["pillars"]:
            a(f"<li>{esc(p)}</li>")
        a("</ul>\n")

    # group jobs by their originating section, preserving order
    seen: list[str] = []
    for j in doc["jobs"]:
        if j["section"] not in seen:
            seen.append(j["section"])
    for sec in seen:
        rows = [j for j in doc["jobs"] if j["section"] == sec]
        heading = "Experience" if re.search(r"operational|experience", sec, re.I) else \
                  "Advisory and Fractional Consulting" if re.search(r"advisory|consult", sec, re.I) else \
                  sec.title()
        a(f"<h2>{esc(heading)}</h2>\n")
        for j in rows:
            # one job = one break-safe unit, so it never splits mid-entry across a page break
            a('<div class="entry">')
            head = j["company"] + (f", {j['dom']}" if j["dom"] else "")
            a(f"<h3>{esc(head)}</h3>")
            role = j["role"]
            # never invent a title: a bare date range stays a described engagement
            if role and DATE_ONLY.match(role):
                role = f"Advisory engagement, {role}"
            if role:
                a(f'<div class="role">{esc(role)}</div>')
            if j["summary"]:
                a(f"<p>{esc(j['summary'])}</p>")
            if j["bullets"]:
                a("<ul>")
                for b in j["bullets"]:
                    a(f"<li>{esc(b)}</li>")
                a("</ul>")
            a("</div>")

    if doc["skills"]:
        a("<h2>Skills</h2>")
        for k, v in doc["skills"]:
            a(f'<p class="kv"><b>{esc(k)}:</b> {esc(v)}</p>')
        a("")

    if doc["oss"]:
        a("<h2>Open Source</h2>\n<ul>")
        for h_, l_ in doc["oss"]:
            a(f"<li>{esc(h_)}: {esc(l_)}</li>")
        a("</ul>\n")

    if doc.get("results"):
        joined = "; ".join(f"{n} {k}" for n, k in doc["results"])
        a("<h2>Selected Results</h2>")
        a(f'<p class="kv">{esc(joined)}.</p>\n')

    for ex in doc.get("extras", []):
        a(f"<h2>{esc(ex['heading'])}</h2>\n<ul>")
        for it in ex["items"]:
            a(f"<li>{esc(it)}</li>")
        a("</ul>\n")

    if doc["education"]:
        a("<h2>Education and Credentials</h2>")
        for e in doc["education"]:
            a(f'<p class="kv">{esc(e)}</p>')
        a("")

    a("</body>\n</html>")
    return "\n".join(o) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("input", help="designed resume .html")
    ap.add_argument("--out", help="output path (default: <stem>-ats.html beside input)")
    ap.add_argument("--no-extras", action="store_true",
                    help="omit generic-capture sections (a design's Deep-Profile / role-fit panels "
                         "that do not linearise cleanly), for a shorter, conventional resume")
    args = ap.parse_args()

    src = open(args.input, encoding="utf-8").read()
    doc = parse(src)
    if args.no_extras:
        doc["extras"] = []
    if not doc["jobs"]:
        print(f"WARNING: no .job blocks parsed from {args.input} - check the structure",
              file=sys.stderr)
    # coverage guard - catch silent content loss from an unrecognised layout
    # tags become spaces here (not nothing) so adjacent blocks do not fuse into fake tokens
    def words(frag: str) -> set:
        frag = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", frag, flags=re.S | re.I)
        frag = re.sub(r"<!--.*?-->", " ", frag, flags=re.S)
        frag = re.sub(r"<[^>]+>", " ", frag)
        return set(re.findall(r"[A-Za-z0-9$%]{4,}", html.unescape(frag).lower()))

    designed_words = words(grab(r"<body>(.*?)</body>", src) or src)
    emitted_words = words(emit(doc))
    missing = designed_words - emitted_words
    # --no-extras is a deliberate cut, so the coverage guard would only cry wolf
    if not args.no_extras and designed_words and len(missing) / len(designed_words) > 0.10:
        print(f"WARNING: {len(missing)}/{len(designed_words)} distinct words "
              f"({100*len(missing)//len(designed_words)}%) present in the designed resume are "
              f"absent from the ATS output - the layout may have sections this script cannot see.",
              file=sys.stderr)
        print("  sample dropped: " + ", ".join(sorted(missing)[:12]), file=sys.stderr)

    out = args.out or os.path.join(os.path.dirname(args.input) or ".",
                                   os.path.basename(args.input)[:-5] + "-ats.html")
    open(out, "w", encoding="utf-8").write(emit(doc))
    print(f"{out}  <-  {args.input}   "
          f"[{len(doc['jobs'])} roles, {len(doc['skills'])} skill groups, "
          f"{len(doc['pillars'])} pillars, {len(doc['education'])} edu]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
