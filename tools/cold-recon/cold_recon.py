#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cold_recon.py - cold-reconstruction incident report CLI (ARCS public good).

Given an incident (a git commit range, or a --since/--until time window), gather the
DURABLE, COMMITTED artifacts it touched into an evidence pack; hand that pack to a
ZERO-TRANSCRIPT cold agent; then audit what the agent could and could not reconstruct.

Coldness is a debiasing control, not a feature. The participant is the worst narrator
(hindsight, motivated coherence). A memoryless reader of the contemporaneous committed
record cannot spin. It corrects narrator/hindsight bias EXACTLY to the degree the record
was committed contemporaneously -- which is why the leak map is a second product: what
the cold agent cannot reconstruct is your telemetry / serialization / observability gap.

This is a good METHODOLOGY, not a patent. Prior art is dense (event sourcing / WAL replay,
git bisect, blameless post-mortems, blinded review, retrieval-grounded cite-or-abstain
generation). The fresh part is the framing: coldness-as-debiasing-control +
leak-map-as-observability-audit. It is only as good as the pre-commit / commit-as-you-go
discipline behind the record.

Division of labor (same contract as tools/recoil-report):
  - gather   : DETERMINISTIC. git + files only. Never reads a transcript. -> evidence pack JSON
  - prompt   : DETERMINISTIC. emits the exact cold-agent prompt (pack + contract + schema)
  - validate : DETERMINISTIC. checks a reconstruction JSON against the bundled schema
  - leakmap  : DETERMINISTIC. diffs the reconstruction's evidence trail against the pack
  - render   : DETERMINISTIC. standalone noindex HTML report
The one non-deterministic step -- the cold agent's reconstruction -- is done by a fresh
Claude Code session whose ONLY context is the pack. This CLI owns everything around it.

Pure standard library. No third-party packages, no install step, no network.

Exit codes: 0 ok | 1 validation/leak-threshold failed | 2 usage/IO error | 127 python3 missing.
"""

import argparse
import datetime as _dt
import html
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(HERE, "schema", "reconstruction.schema.json")
SAMPLE_PATH = os.path.join(HERE, "sample", "sample-reconstruction.json")
PROMPT_PATH = os.path.join(HERE, "prompts", "cold-agent.md")

# Durable, committed record globs -- the substrate a cold reader is allowed to see.
# NOTE what is deliberately absent: session transcripts, _STATE/handoff-progress.*
# (gitignored, the WARM narrator's log), scratchpads. Coldness is enforced structurally:
# gather only ever touches git history and tracked files, never a conversation.
DEFAULT_DURABLE_GLOBS = [
    "_STATE/incidents/*.md",
    "_STATE/witness/*.jsonl",
    "_SEEDS/*.jsonl",
    "_SEEDS/*.md",
    "_QUEUE/*.jsonl",
    "public/blog-nftt-*.html",
    "public/blog-til-*.html",
    "_CANON/*.md",
    "_CANON/*.jsonl",
    "docs/adr/*.md",
    "_ADR/*.md",
]
# Per-file content cap so a pack stays a pack, not a repo dump.
CONTENT_CAP = 24000
TRAILER_RE = re.compile(r"^([A-Z][A-Za-z-]+):\s*(.+)$")
NCI_RE = re.compile(r"\[NCI:(\d+)\]")


# --------------------------------------------------------------------------- utils
def die(msg, code=2):
    sys.stderr.write("cold-recon: %s\n" % msg)
    sys.exit(code)


def run_git(repo, args):
    try:
        out = subprocess.run(
            ["git", "-C", repo] + args,
            capture_output=True, text=True, check=True,
        )
        return out.stdout
    except FileNotFoundError:
        die("git not found on PATH", 127)
    except subprocess.CalledProcessError as e:
        die("git %s failed: %s" % (" ".join(args), (e.stderr or "").strip()), 2)


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        die("file not found: %s" % path, 2)
    except ValueError as e:
        die("invalid JSON in %s: %s" % (path, e), 2)


def write_out(payload, out, is_html=False):
    text = payload if is_html else json.dumps(payload, indent=2, ensure_ascii=False)
    if out in (None, "-"):
        sys.stdout.write(text + ("" if text.endswith("\n") else "\n"))
        return
    d = os.path.dirname(out)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    sys.stderr.write("cold-recon: wrote %s\n" % out)


def coerce(v):
    if v in ("true", "false"):
        return v == "true"
    try:
        return json.loads(v)
    except ValueError:
        return v


def apply_sets(obj, sets):
    for pair in sets or []:
        if "=" not in pair:
            die("--set expects dotted.key=value, got %r" % pair)
        key, val = pair.split("=", 1)
        node = obj
        parts = key.split(".")
        for p in parts[:-1]:
            node = node.setdefault(p, {})
        node[parts[-1]] = coerce(val)
    return obj


# ----------------------------------------------------------- output normalization
# The render output inherits em-dashes from commit subjects embedded in the pack /
# leak-map anchor lists (e.g. a commit "NFTT — 'forge'..."). The repo's wrap gate
# (scripts/artifact_wrap_lint.py) fails any published HTML with an em-dash, so a
# rendered report has to be em-dash-0 BY CONSTRUCTION -- not by a hand post-process.
# Mapping (task-fixed): em-dash / en-dash -> spaced hyphen; minus sign -> hyphen.
# Surrounding spaces are collapsed so " x — y " and "x—y" both become "x - y".
_DASH_SPACED_RE = re.compile(r"[ \t]*[—–][ \t]*")


def normalize_dashes(text):
    text = _DASH_SPACED_RE.sub(" - ", text)
    text = text.replace("−", "-")  # U+2212 MINUS SIGN -> ASCII hyphen (no padding)
    return text


# ----------------------------------------------------------------- in-tool redaction
# PII scrubbing lives IN the tool, not in a hand-written post-process. The unredacted
# render is the internal record (private repo); the redacted render is the public
# artifact. This is the internal/external air-gap. Redactions are applied
# case-insensitively, LONGEST-PATTERN-FIRST, so "zach.harris@gmail.com" is scrubbed
# before the shorter "Zach" can partially match inside it.
def load_redactions(pairs, redact_file):
    reds = {}
    if redact_file:
        data = load_json(redact_file)
        if not isinstance(data, dict):
            die("--redact-file must be a JSON object {pattern: replacement}, got %s"
                % type(data).__name__)
        for k, v in data.items():
            reds[str(k)] = str(v)
    for pair in pairs or []:
        if "=" not in pair:
            die("--redact expects PATTERN=REPLACEMENT, got %r" % pair)
        k, v = pair.split("=", 1)
        if not k:
            die("--redact pattern is empty in %r" % pair)
        reds[k] = v
    # Longest pattern first: a superstring is scrubbed before any substring of it.
    return sorted(reds.items(), key=lambda kv: len(kv[0]), reverse=True)


def apply_redactions(text, reds):
    for pat, repl in reds:
        if not pat:
            continue
        # lambda replacement avoids backslash/group interpretation in `repl`.
        text = re.sub(re.escape(pat), lambda _m, r=repl: r, text, flags=re.IGNORECASE)
    return text


# A token-by-token redaction can strand a doubled article at the seam: the source
# "a Fun.xyz Senior PMM candidate bundle" with {Fun.xyz Senior PMM -> "a candidate role"}
# renders "a a candidate role ...". Longest-match-first does not prevent this -- the leading
# article is already in the prose, and the replacement re-introduces one. So after redaction
# we collapse an immediately-repeated ARTICLE (a / an / the), case-insensitively, keeping the
# first. Article-only is deliberate: "a a" / "the the" is never grammatical English, so this
# has effectively zero false positives, unlike a blanket repeated-word collapse (which would
# eat the legitimate "had had" / "that that"). A NON-adjacent repeat left by a phrase-shaped
# redaction (".. candidate role candidate bundle") is a redaction-MAP design issue, not a seam
# a mechanical pass can safely fix: map the whole noun phrase incl. its article instead
# ("a Fun.xyz Senior PMM candidate bundle" -> "a candidate bundle"). See README + selftest.
_DUP_ARTICLE_RE = re.compile(r"\b(a|an|the)(\s+)\1\b", re.IGNORECASE)


def collapse_redaction_artifacts(text):
    prev = None
    while prev != text:  # loop dissolves chains, e.g. "the the the" -> "the"
        prev = text
        text = _DUP_ARTICLE_RE.sub(lambda m: m.group(1), text)
    return text


# ----------------------------------------------------------------- schema validate
def _type_ok(val, typ):
    return {
        "string": isinstance(val, str),
        "number": isinstance(val, (int, float)) and not isinstance(val, bool),
        "integer": isinstance(val, int) and not isinstance(val, bool),
        "boolean": isinstance(val, bool),
        "array": isinstance(val, list),
        "object": isinstance(val, dict),
    }.get(typ, True)


def validate_against(obj, schema, path="$", errors=None):
    """Minimal draft-07 subset: type, required, properties, items. Extra keys allowed."""
    if errors is None:
        errors = []
    typ = schema.get("type")
    if typ and not _type_ok(obj, typ):
        errors.append("%s: expected %s, got %s" % (path, typ, type(obj).__name__))
        return errors
    if typ == "object":
        for req in schema.get("required", []):
            if req not in obj:
                errors.append("%s: missing required key '%s'" % (path, req))
        for k, sub in schema.get("properties", {}).items():
            if k in obj:
                validate_against(obj[k], sub, "%s.%s" % (path, k), errors)
    if typ == "array" and "items" in schema and isinstance(obj, list):
        for i, it in enumerate(obj):
            validate_against(it, schema["items"], "%s[%d]" % (path, i), errors)
    return errors


# ------------------------------------------------------------------------- gather
def resolve_files_at_range(repo, rng):
    """Union of files touched across the range (name-status), plus rename targets."""
    status = run_git(repo, ["diff", "--name-status", rng])
    touched = []
    for line in status.splitlines():
        cols = line.split("\t")
        if len(cols) >= 2:
            touched.append(cols[-1])  # target path (handles renames R100 old\tnew)
    return sorted(set(touched))


def glob_match(path, globs):
    import fnmatch
    return any(fnmatch.fnmatch(path, g) for g in globs)


def read_capped(repo, path):
    full = os.path.join(repo, path)
    try:
        with open(full, "r", encoding="utf-8", errors="replace") as f:
            data = f.read()
    except (IOError, OSError):
        return None, 0, False
    n = len(data)
    return data[:CONTENT_CAP], n, n > CONTENT_CAP


def parse_commit_block(block):
    lines = block.split("\n")
    sha = lines[0].strip()
    author = lines[1].strip() if len(lines) > 1 else ""
    date = lines[2].strip() if len(lines) > 2 else ""
    subject = lines[3].strip() if len(lines) > 3 else ""
    body = "\n".join(lines[4:]).strip()
    trailers = {}
    for ln in body.splitlines():
        m = TRAILER_RE.match(ln.strip())
        if m:
            trailers[m.group(1)] = m.group(2)
    ncim = NCI_RE.search(subject) or NCI_RE.search(body)
    return {
        "sha": sha, "author": author, "date": date,
        "subject": subject, "body": body,
        "trailers": trailers,
        "nci": int(ncim.group(1)) if ncim else None,
    }


def cmd_gather(args):
    repo = os.path.abspath(args.repo)
    if not os.path.isdir(os.path.join(repo, ".git")) and not os.path.isfile(os.path.join(repo, ".git")):
        die("not a git repo (no .git): %s" % repo)

    rng = args.range
    if args.since or args.until:
        # Resolve a time window to a concrete first^..last range for reproducibility.
        revs = run_git(repo, ["log", "--format=%H"] +
                       (["--since", args.since] if args.since else []) +
                       (["--until", args.until] if args.until else [])).split()
        if not revs:
            die("no commits in window since=%s until=%s" % (args.since, args.until), 1)
        last, first = revs[0], revs[-1]
        rng = "%s~1..%s" % (first, last) if not rng else rng

    if not rng:
        die("provide a commit range (e.g. A~1..B) or --since/--until")

    # Commits (delimiter-safe format).
    SEP = "\x1e"  # record separator
    raw = run_git(repo, ["log", "--no-merges", "--format=%H%n%an <%ae>%n%aI%n%s%n%b" + SEP, rng])
    commits = [parse_commit_block(b.strip("\n")) for b in raw.split(SEP) if b.strip()]

    include_merges = run_git(repo, ["log", "--merges", "--format=%H %s", rng]).splitlines()

    touched = resolve_files_at_range(repo, rng)
    globs = args.durable_glob or DEFAULT_DURABLE_GLOBS

    artifacts = []
    for path in touched:
        is_durable = glob_match(path, globs)
        if not is_durable and not args.all_files:
            continue
        content, size, truncated = read_capped(repo, path)
        artifacts.append({
            "path": path,
            "durable": is_durable,
            "exists_at_head": content is not None,
            "size_bytes": size,
            "truncated": truncated,
            "content": content if content is not None else "",
        })

    # Also pull durable artifacts that MATCH the globs and were touched-by-content even
    # if name-status missed them (defensive; union is cheap).
    pack = {
        "kind": "cold-recon-evidence-pack",
        "schema_version": "1",
        "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "repo": os.path.basename(repo.rstrip("/")),
        "range": rng,
        "window": {"since": args.since, "until": args.until},
        "coldness_contract": (
            "This pack is the COMPLETE context a cold agent may see. It contains only "
            "committed record (git history + tracked files). It contains NO conversation "
            "transcript, NO handoff-progress log, NO scratchpad. A reconstruction built "
            "from this pack is hindsight-immune to the degree the record was committed "
            "contemporaneously."
        ),
        "counts": {
            "commits": len(commits),
            "merges": len(include_merges),
            "files_touched": len(touched),
            "artifacts_included": len(artifacts),
            "durable_artifacts": sum(1 for a in artifacts if a["durable"]),
        },
        "commits": commits,
        "merges": include_merges,
        "files_touched": touched,
        "artifacts": artifacts,
    }
    # Optional in-tool redaction: produce a shareable pack whose PII is scrubbed at the
    # source, so the cold agent never sees it (same air-gap as `render --redact`). The
    # un-redacted pack stays the internal record. Dashes are NOT normalized here -- a
    # pack is faithful JSON data, not published HTML; that normalization is render-only.
    reds = load_redactions(getattr(args, "redact", None), getattr(args, "redact_file", None))
    if reds:
        redacted = apply_redactions(json.dumps(pack, indent=2, ensure_ascii=False), reds)
        write_out(redacted, args.out, is_html=True)
    else:
        write_out(pack, args.out)


# ------------------------------------------------------------------------- prompt
def cmd_prompt(args):
    pack = load_json(args.pack)
    try:
        with open(PROMPT_PATH, "r", encoding="utf-8") as f:
            template = f.read()
    except IOError:
        die("bundled prompt template missing: %s" % PROMPT_PATH, 2)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_text = f.read()
    filled = (
        template
        .replace("{{RANGE}}", str(pack.get("range", "")))
        .replace("{{REPO}}", str(pack.get("repo", "")))
        .replace("{{COUNTS}}", json.dumps(pack.get("counts", {}), indent=2))
        .replace("{{SCHEMA}}", schema_text.strip())
        .replace("{{PACK}}", json.dumps(pack, indent=2, ensure_ascii=False))
    )
    write_out(filled, args.out, is_html=True)  # is_html just means "raw text, no json wrap"


# ------------------------------------------------------------------------ validate
def cmd_validate(args):
    obj = load_json(args.file)
    schema = load_json(SCHEMA_PATH)
    errs = validate_against(obj, schema)
    if errs:
        sys.stderr.write("cold-recon: %d validation error(s):\n" % len(errs))
        for e in errs:
            sys.stderr.write("  - %s\n" % e)
        sys.exit(1)
    sys.stderr.write("cold-recon: %s is valid.\n" % args.file)


# ------------------------------------------------------------------------- leakmap
def _anchors_from_pack(pack):
    """The claim-anchors a faithful reconstruction should reference: every durable
    artifact path, plus each commit sha (short). Presence of the anchor (or its basename)
    anywhere in the reconstruction's evidence trail counts as reconstructed."""
    anchors = []
    for a in pack.get("artifacts", []):
        if a.get("durable"):
            anchors.append(("artifact", a["path"]))
    for c in pack.get("commits", []):
        anchors.append(("commit", c["sha"][:9] + "  " + c.get("subject", "")))
    return anchors


def _trail_text(recon):
    """Everything the reconstruction offers as its evidence trail, flattened to a
    lowercase haystack. We look in the whole doc plus explicit evidence fields."""
    return json.dumps(recon, ensure_ascii=False).lower()


def cmd_leakmap(args):
    pack = load_json(args.pack)
    recon = load_json(args.reconstruction)
    hay = _trail_text(recon)

    reconstructed, partial, leaked = [], [], []
    for kind, ident in _anchors_from_pack(pack):
        if kind == "artifact":
            base = os.path.basename(ident)
            stem = re.sub(r"\.[a-z0-9]+$", "", base)
            if ident.lower() in hay or base.lower() in hay:
                reconstructed.append({"kind": kind, "ref": ident})
            elif stem.lower() in hay:
                partial.append({"kind": kind, "ref": ident, "note": "basename stem referenced, exact path not cited"})
            else:
                leaked.append({"kind": kind, "ref": ident})
        else:  # commit
            sha = ident.split()[0]
            if sha[:7].lower() in hay:
                reconstructed.append({"kind": kind, "ref": ident})
            else:
                leaked.append({"kind": kind, "ref": ident})

    total = len(reconstructed) + len(partial) + len(leaked)
    rate = (len(reconstructed) + 0.5 * len(partial)) / total if total else 1.0
    leakmap = {
        "kind": "cold-recon-leak-map",
        "range": pack.get("range"),
        "repo": pack.get("repo"),
        "reads": (
            "The leak map is an observability audit, not a grade of the agent. A leaked "
            "anchor means the durable record did not carry enough for a cold reader to "
            "surface it -- a serialization / telemetry gap, or a thread that died "
            "uncommitted. Reconstructability-from-evidence is the measured property."
        ),
        "totals": {
            "anchors": total,
            "reconstructed": len(reconstructed),
            "partial": len(partial),
            "leaked": len(leaked),
            "reconstructability": round(rate, 3),
        },
        "reconstructed": reconstructed,
        "partial": partial,
        "leaked": leaked,
    }
    write_out(leakmap, args.out)
    if args.min_rate is not None and rate < args.min_rate:
        sys.stderr.write("cold-recon: reconstructability %.3f below --min-rate %.3f\n" % (rate, args.min_rate))
        sys.exit(1)


# -------------------------------------------------------------------------- render
def _esc(x):
    return html.escape(str(x if x is not None else ""))


def _confidence_bar(conf):
    try:
        pct = max(0, min(100, int(round(float(conf) * 100))))
    except (TypeError, ValueError):
        pct = 0
    color = "var(--green)" if pct >= 75 else ("var(--gold)" if pct >= 45 else "var(--red)")
    word = "well grounded" if pct >= 75 else ("partial" if pct >= 45 else "thin")
    return ('<span class="conflabel">record support</span>'
            '<span class="confbar" aria-label="record support %d%% (%s)">'
            '<span class="conffill" style="width:%d%%;background:%s"></span></span>'
            '<span class="confnum">%d%% %s</span>') % (pct, word, pct, color, pct, word)


def cmd_render(args):
    recon = load_json(args.reconstruction)
    if not args.no_validate:
        errs = validate_against(recon, load_json(SCHEMA_PATH))
        if errs:
            die("reconstruction failed validation (%d errs); use --no-validate to force" % len(errs), 1)
    apply_sets(recon, args.set)
    leakmap = load_json(args.leakmap) if args.leakmap else None

    title = recon.get("title") or ("Cold-reconstruction report: %s" % recon.get("range", ""))
    sections = recon.get("sections", [])
    could_not = recon.get("could_not_verify", [])
    forward = recon.get("forward_items", [])
    lm = leakmap or recon.get("leak_map") or {}

    sec_html = []
    for s in sections:
        conf = s.get("confidence")
        conf_html = _confidence_bar(conf) if conf is not None else ""
        body = s.get("body", "")
        # paragraph split on blank lines
        paras = "".join("<p>%s</p>" % _esc(p.strip()) for p in re.split(r"\n\s*\n", body) if p.strip())
        sec_html.append(
            '<section class="rsec"><div class="rsec-h"><span class="rsec-tag">%s</span>'
            '<span class="rsec-conf">%s</span></div><h2>%s</h2>%s</section>'
            % (_esc(s.get("tag", "")), conf_html, _esc(s.get("heading", "")), paras)
        )

    cnv_html = "".join("<li>%s</li>" % _esc(x) for x in could_not) or "<li class='none'>Nothing flagged unverifiable.</li>"
    fwd_html = "".join("<li>%s</li>" % _esc(x) for x in forward) or "<li class='none'>None.</li>"

    leak_html = ""
    if lm and lm.get("totals"):
        t = lm["totals"]
        try:
            rc_pct = "%d%% reconstructed" % int(round(float(t.get("reconstructability", 0)) * 100))
        except (TypeError, ValueError):
            rc_pct = "reconstructability n/a"
        leaked_rows = "".join("<li><span class='lk'>LEAKED</span> %s</li>" % _esc(x.get("ref")) for x in lm.get("leaked", []))
        partial_rows = "".join("<li><span class='pt'>PARTIAL</span> %s</li>" % _esc(x.get("ref")) for x in lm.get("partial", []))
        leak_html = (
            '<section class="rsec leak"><div class="rsec-h"><span class="rsec-tag">Leak map</span>'
            '<span class="rsec-conf">reconstructability %s</span></div>'
            '<h2>What failed to reconstruct</h2>'
            '<p class="leak-reads">%s</p>'
            '<div class="leak-stat"><b>%s</b> record anchors (durable artifacts + commits) &middot; '
            '<b>%s</b> reconstructed &middot; <b>%s</b> partial &middot; <b class="red">%s</b> leaked</div>'
            '<ul class="leak-list">%s%s</ul></section>'
        ) % (
            _esc(rc_pct), _esc(lm.get("reads", "")),
            _esc(t.get("anchors")), _esc(t.get("reconstructed")),
            _esc(t.get("partial")), _esc(t.get("leaked")),
            partial_rows, leaked_rows or "<li class='none'>Nothing leaked -- full evidence trail.</li>",
        )

    page = _RENDER_TEMPLATE % {
        "title": _esc(title),
        "range": _esc(recon.get("range", "")),
        "repo": _esc(recon.get("repo", "")),
        "standfirst": _esc(recon.get("standfirst", "")),
        "root_invariant": _esc(recon.get("root_invariant", "")),
        "sections": "".join(sec_html),
        "leak": leak_html,
        "could_not": cnv_html,
        "forward": fwd_html,
        "notice": _esc(recon.get("notice", "Cold reconstruction. Built by a zero-transcript agent from the committed record alone.")),
    }
    # Redact PII (opt-in, for the public artifact), collapse any doubled-article seam the
    # redaction left, THEN normalize dashes (always, so the output is em-dash-0 by
    # construction and clears scripts/artifact_wrap_lint.py).
    reds = load_redactions(getattr(args, "redact", None), getattr(args, "redact_file", None))
    if reds:
        page = collapse_redaction_artifacts(apply_redactions(page, reds))
    page = normalize_dashes(page)
    write_out(page, args.out, is_html=True)


_RENDER_TEMPLATE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>%(title)s</title>
<style>
  :root{--bg:#020408;--surface:#0b1017;--surface2:#111823;--border:#1e293b;--border2:#2a3a4d;
    --text:#e7ecf3;--muted:#9aa8bc;--dim:#5f6f84;--cyan:#00F0FF;--green:#00FF9D;--gold:#FFD700;--red:#FF4D6D;
    --mono:ui-monospace,SFMono-Regular,Menlo,monospace;--serif:Georgia,"Times New Roman",serif;--measure:42rem;}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--text);font-family:var(--serif);font-size:18px;line-height:1.7;-webkit-font-smoothing:antialiased}
  .wrap{max-width:var(--measure);margin:0 auto;padding:0 22px}
  .cls{font-family:var(--mono);font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--dim);
    display:flex;gap:12px;flex-wrap:wrap;border-bottom:1px solid var(--border);padding:14px 0;margin-bottom:36px}
  .cls b{color:var(--cyan)}
  h1{font-family:var(--serif);font-weight:600;font-size:clamp(2rem,6vw,3rem);line-height:1.05;letter-spacing:-.015em;margin:24px 0 14px;text-wrap:balance}
  .standfirst{font-size:1.2rem;color:var(--muted);font-style:italic;margin:0 0 8px;max-width:none}
  .keel{border-left:2px solid var(--cyan);padding:2px 0 2px 18px;margin:28px 0;font-size:1.1rem;color:var(--text)}
  .keel .k{font-family:var(--mono);font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:var(--cyan);display:block;margin-bottom:6px}
  .rsec{margin:44px 0}
  .rsec-h{display:flex;align-items:center;gap:14px;margin-bottom:12px}
  .rsec-tag{font-family:var(--mono);font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--cyan)}
  .rsec-conf{font-family:var(--mono);font-size:11px;color:var(--dim);display:flex;align-items:center;gap:8px;margin-left:auto}
  .conflabel{font-family:var(--mono);font-size:9.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--dim)}
  .confbar{display:inline-block;width:70px;height:6px;border-radius:3px;background:var(--surface2);overflow:hidden;vertical-align:middle}
  .conffill{display:block;height:100%%}
  .confnum{font-family:var(--mono);font-size:11px;color:var(--muted)}
  .legend{border:1px solid var(--border);border-radius:8px;padding:14px 16px;margin:26px 0;background:var(--surface)}
  .legend p{font-family:var(--mono);font-size:12px;line-height:1.6;color:var(--muted);margin:0 0 10px}
  .legend .keys{display:flex;flex-wrap:wrap;gap:8px 18px;font-family:var(--mono);font-size:11px;color:var(--muted)}
  .legend .key{display:flex;align-items:center;gap:7px}
  .legend .sw{width:22px;height:6px;border-radius:3px;display:inline-block}
  h2{font-family:var(--serif);font-weight:600;font-size:1.5rem;line-height:1.15;margin:0 0 14px;text-wrap:balance}
  p{margin:0 0 18px}
  .panel{border:1px solid var(--border2);background:var(--surface2);border-radius:10px;padding:20px 22px;margin:32px 0}
  .panel h3{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--cyan);margin:0 0 14px}
  .panel ul{margin:0;padding-left:20px;font-family:var(--mono);font-size:13px;line-height:1.6;color:var(--muted)}
  .panel li{margin-bottom:8px} .panel li.none{color:var(--dim);list-style:none;margin-left:-20px}
  .leak{border:1px solid color-mix(in srgb,var(--red) 30%%,var(--border));background:#140d11;border-radius:10px;padding:22px}
  .leak-reads{font-size:14px;color:var(--muted);font-style:italic}
  .leak-stat{font-family:var(--mono);font-size:12px;color:var(--muted);margin:14px 0}
  .leak-stat b{color:var(--text)} .leak-stat b.red{color:var(--red)}
  .leak-list{margin:0;padding-left:0;list-style:none;font-family:var(--mono);font-size:12.5px;line-height:1.7;color:var(--muted)}
  .leak-list .lk{color:var(--red);font-weight:600} .leak-list .pt{color:var(--gold);font-weight:600} .leak-list .none{color:var(--dim)}
  footer{margin:56px 0 70px;padding-top:20px;border-top:1px solid var(--border);font-family:var(--mono);font-size:11px;color:var(--dim);line-height:1.8}
  ::selection{background:rgba(0,240,255,.22)}
</style></head><body>
<div class="wrap">
  <div class="cls"><span>Cold reconstruction</span><span>Repo: %(repo)s</span><span>Range: %(range)s</span><span style="margin-left:auto"><b>zero transcript</b></span></div>
  <h1>%(title)s</h1>
  <p class="standfirst">%(standfirst)s</p>
  <div class="keel"><span class="k">Root invariant</span>%(root_invariant)s</div>
  <div class="legend">
    <p>Each section carries a <b style="color:var(--muted)">record support</b> score: how well the committed record backs that claim, not how fluent the writing is. A section the cold reader could write well but only weakly ground scores low on purpose.</p>
    <div class="keys">
      <span class="key"><span class="sw" style="background:var(--green)"></span>75-100%% &middot; well grounded</span>
      <span class="key"><span class="sw" style="background:var(--gold)"></span>45-74%% &middot; partial, record is thin</span>
      <span class="key"><span class="sw" style="background:var(--red)"></span>under 45%% &middot; described, not confirmed</span>
    </div>
  </div>
  %(sections)s
  %(leak)s
  <div class="panel"><h3>Claims it could not verify</h3><ul>%(could_not)s</ul></div>
  <div class="panel"><h3>Forward items</h3><ul>%(forward)s</ul></div>
  <footer>%(notice)s</footer>
</div></body></html>
"""


# ------------------------------------------------------------------------ selftest
# Frustration-gate proofs (AGENTS.md gotcha #15): each hardening is proven to FAIL on
# bad input AND PASS on good, wired to the tool's own runnable test path (`selftest`).
# The PII grep here is the exact one used at publish time to clear the public reports.
_PII_GREP = re.compile(r"lycett|riskpod|fun\.xyz|robert|zach|@gmail", re.IGNORECASE)
_MDASH_CHARS = ("—", "–", "−")


class _Args(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)


def _render_to_str(recon, leakmap=None, redact=None, redact_file=None):
    import io
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        # write to stdout ("-") and capture; validation stays on (fixtures are valid).
        import tempfile
        rf = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(recon, rf); rf.close()
        lf = None
        if leakmap is not None:
            lf = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
            json.dump(leakmap, lf); lf.close()
        cmd_render(_Args(reconstruction=rf.name, leakmap=(lf.name if lf else None),
                         out="-", set=None, no_validate=False,
                         redact=redact, redact_file=redact_file))
    finally:
        sys.stdout = old
    return buf.getvalue()


def cmd_selftest(args):
    checks = []  # (name, ok, detail)

    # ---- GAP 1: em-dash normalization ----------------------------------------
    # Fixture carries em-dashes in a section body AND in a leaked commit-subject anchor,
    # exactly how the live reports inherited them from the pack.
    em_recon = {
        "range": "A~1..B", "repo": "arcs-v9",
        "title": "Fixture — em-dash in the title",
        "root_invariant": "the record either carries it — or it leaked",
        "standfirst": "one sentence – with an en-dash too",
        "sections": [{
            "tag": "What happened", "heading": "A heading",
            "body": "First the commit — subject line — then the outcome.\n\n"
                    "A minus−sign and an en–dash for good measure.",
            "confidence": 0.9,
        }],
        "could_not_verify": ["a claim — unconfirmed"],
        "forward_items": ["next – item"],
    }
    em_leakmap = {
        "totals": {"anchors": 1, "reconstructed": 0, "partial": 0, "leaked": 1,
                   "reconstructability": 0.0},
        "reads": "observability audit",
        "leaked": [{"kind": "commit",
                    "ref": "39c9c0971  fix(blog): NFTT — 'forge' reads as counterfeit [NCI:50]"}],
        "partial": [], "reconstructed": [],
    }
    # fails-on-bad: the fixture INPUT genuinely contains em/en/minus dashes.
    raw_has = any(c in json.dumps(em_recon, ensure_ascii=False)
                  + json.dumps(em_leakmap, ensure_ascii=False) for c in _MDASH_CHARS)
    # passes-on-good: the rendered HTML is dash-clean by construction.
    em_html = _render_to_str(em_recon, em_leakmap)
    out_dashes = sum(em_html.count(c) for c in _MDASH_CHARS)
    checks.append(("em-dash fails-on-bad (fixture has em/en/minus dashes)", raw_has,
                   "found dashes in fixture" if raw_has else "FIXTURE HAS NO DASHES"))
    checks.append(("em-dash passes-on-good (rendered HTML has 0)", out_dashes == 0,
                   "0 dashes in output" if out_dashes == 0 else "%d dashes leaked" % out_dashes))

    # ---- GAP 2: in-tool redaction --------------------------------------------
    pii_recon = {
        "range": "A~1..B", "repo": "arcs-v9",
        "title": "Robert Lycett cold-recon",
        "root_invariant": "Zach's air-gap holds",
        "standfirst": "RiskPod at Fun.xyz (funxyz) — email zach.harris@gmail.com",
        "sections": [{
            "tag": "What happened", "heading": "Lycett review",
            "body": "Robert reviewed the Fun.xyz brief. Contact zach.harris@gmail.com.",
            "confidence": 0.8,
        }],
        "could_not_verify": ["Robert Lycett's title unconfirmed"],
        "forward_items": ["ping Robert"],
    }
    redact_map = {
        "zach.harris@gmail.com": "the operator's email",
        "Robert Lycett": "the recruiter",
        "Fun.xyz": "the company", "funxyz": "the company",
        "RiskPod": "the product", "Lycett": "the recruiter",
        "Robert": "the recruiter", "Zach's": "the operator's", "Zach": "the operator",
    }
    # fails-on-bad: no redaction -> the PII grep FINDS the tokens.
    bad_html = _render_to_str(pii_recon)
    bad_hits = _PII_GREP.findall(bad_html)
    # passes-on-good: with the redaction map, the PII grep finds NOTHING.
    good_html = _render_to_str(pii_recon, redact_file=None,
                               redact=["%s=%s" % (k, v) for k, v in redact_map.items()])
    good_hits = _PII_GREP.findall(good_html)
    checks.append(("redaction fails-on-bad (no --redact -> PII present)", len(bad_hits) > 0,
                   "grep found %d PII token(s)" % len(bad_hits)))
    checks.append(("redaction passes-on-good (--redact -> PII grep clean)", len(good_hits) == 0,
                   "0 PII tokens" if not good_hits else "leaked: %s" % sorted(set(good_hits))))

    # ---- GAP 3: doubled-article collapse at the redaction seam ----------------
    # The live warm-relaxed report hit this: "a Fun.xyz Senior PMM candidate bundle" with
    # {Fun.xyz Senior PMM -> "a candidate role"} rendered "a a candidate role candidate
    # bundle" -- PII-clean but ungrammatical (doubled article + a stranded repeat).
    seam_recon = {
        "range": "A~1..B", "repo": "arcs-v9",
        "title": "Seam fixture", "root_invariant": "the record either carries it or it leaked",
        "standfirst": "Reviewed a Fun.xyz Senior PMM candidate bundle this week.",
        "sections": [{"tag": "What happened", "heading": "Review",
                      "body": "We shipped a Fun.xyz Senior PMM candidate bundle.",
                      "confidence": 0.8}],
        "could_not_verify": ["none"], "forward_items": ["none"],
    }
    dup_art = re.compile(r"\b(a|an|the)\s+\1\b", re.IGNORECASE)
    # fails-on-bad: token-by-token map re-introduces the article -> raw redaction doubles it.
    raw_tokenwise = apply_redactions(json.dumps(seam_recon),
                                     load_redactions(["Fun.xyz Senior PMM=a candidate role"], None))
    checks.append(("collapse fails-on-bad (token-wise redaction doubles the article)",
                   bool(dup_art.search(raw_tokenwise)),
                   "found doubled article pre-collapse" if dup_art.search(raw_tokenwise)
                   else "NO DOUBLED ARTICLE IN FIXTURE"))
    # passes-on-good #1: rendering with that same token-wise map now collapses the seam.
    seam_html = _render_to_str(seam_recon, redact=["Fun.xyz Senior PMM=a candidate role"])
    checks.append(("collapse passes-on-good (rendered report has no doubled article)",
                   not dup_art.search(seam_html),
                   "no doubled article" if not dup_art.search(seam_html) else "doubled article survived"))
    # passes-on-good #2: the RECOMMENDED whole-phrase map (article included) leaves no repeat
    # at all -- neither a doubled article nor the stranded "candidate .. candidate".
    phrase_html = _render_to_str(seam_recon,
                                 redact=["a Fun.xyz Senior PMM candidate bundle=a candidate bundle"])
    no_stray_repeat = (not dup_art.search(phrase_html)
                       and phrase_html.lower().count("candidate bundle") >= 1
                       and "candidate role candidate" not in phrase_html.lower())
    checks.append(("collapse passes-on-good (whole-phrase map leaves no repeat)",
                   no_stray_repeat,
                   "clean phrase" if no_stray_repeat else "phrase still repeats a word"))

    # ---- report --------------------------------------------------------------
    ok_all = all(ok for _, ok, _ in checks)
    for name, ok, detail in checks:
        sys.stderr.write("  [%s] %s -- %s\n" % ("PASS" if ok else "FAIL", name, detail))
    if not ok_all:
        die("selftest FAILED", 1)
    sys.stderr.write("cold-recon: selftest passed (%d checks)\n" % len(checks))


# ---------------------------------------------------------------------------- main
def build_parser():
    p = argparse.ArgumentParser(prog="cold-recon", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd")

    g = sub.add_parser("gather", help="git+files -> evidence pack (deterministic, zero transcript)")
    g.add_argument("range", nargs="?", help="commit range, e.g. A~1..B")
    g.add_argument("--repo", default=".", help="repo path (default cwd)")
    g.add_argument("--since", help="time window start (git --since)")
    g.add_argument("--until", help="time window end (git --until)")
    g.add_argument("--durable-glob", action="append", help="override durable globs (repeatable)")
    g.add_argument("--all-files", action="store_true", help="include all touched files, not just durable")
    g.add_argument("--redact", action="append", metavar="PATTERN=REPLACEMENT",
                   help="scrub PATTERN->REPLACEMENT in the pack, case-insensitive, longest-first (repeatable)")
    g.add_argument("--redact-file", metavar="JSON",
                   help="JSON object {pattern: replacement} of redactions to apply")
    g.add_argument("--out", default="-", help="output path or - for stdout")
    g.set_defaults(func=cmd_gather)

    pr = sub.add_parser("prompt", help="evidence pack -> the exact cold-agent prompt")
    pr.add_argument("pack", help="evidence pack JSON from `gather`")
    pr.add_argument("--out", default="-", help="output path or -")
    pr.set_defaults(func=cmd_prompt)

    v = sub.add_parser("validate", help="check a reconstruction JSON against the schema")
    v.add_argument("file")
    v.set_defaults(func=cmd_validate)

    lm = sub.add_parser("leakmap", help="diff reconstruction vs pack -> observability audit")
    lm.add_argument("pack")
    lm.add_argument("reconstruction")
    lm.add_argument("--out", default="-")
    lm.add_argument("--min-rate", type=float, default=None, help="fail (exit 1) below this reconstructability")
    lm.set_defaults(func=cmd_leakmap)

    r = sub.add_parser("render", help="reconstruction (+leakmap) -> standalone noindex HTML")
    r.add_argument("reconstruction")
    r.add_argument("--leakmap", help="optional leak-map JSON to embed")
    r.add_argument("--out", default="-")
    r.add_argument("--set", action="append", help="dotted.key=value override (repeatable)")
    r.add_argument("--redact", action="append", metavar="PATTERN=REPLACEMENT",
                   help="scrub PATTERN->REPLACEMENT in the rendered report, case-insensitive, "
                        "longest-first (repeatable) -- the public artifact; the un-redacted render "
                        "stays the internal record")
    r.add_argument("--redact-file", metavar="JSON",
                   help="JSON object {pattern: replacement} of redactions to apply")
    r.add_argument("--no-validate", action="store_true")
    r.set_defaults(func=cmd_render)

    st = sub.add_parser("selftest", help="run the fails-on-bad + passes-on-good gate proofs")
    st.set_defaults(func=cmd_selftest)

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "cmd", None):
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
