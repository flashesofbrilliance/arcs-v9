#!/usr/bin/env python3
"""tool_catalog_emit.py — flat tool-catalog emitter (atomic first slice, ADR-070 induction surface).

Walks the six tool surfaces and emits ONE flat catalog with a one-line JTBD per tool,
harvested (never inferred) from each tool's own declaration:
  - .claude/skills/*/SKILL.md      <- frontmatter `description:`
  - .claude/commands/*.md          <- first `> ...` blockquote line (or first prose line)
  - .claude/workflows/*.{js,mjs}   <- meta description literal, else first comment line
  - .claude/hooks/*.sh             <- first `# ` comment after the shebang
  - scripts/*.{py,sh}              <- py: module docstring first line; sh: first comment
  - tools/*/README.md              <- first prose line (packaged tool-forge microservices;
                                      added 2026-09-29 so tools/arcs-verb-eval and siblings are
                                      discoverable, not only those with a slash-command wrapper)
  - operators/*.py                 <- module docstring first line
    (backlog listed generate_arcs_operator_data.py as the operator-table emitter to
    reuse; that file never landed in this repo, so operators are harvested directly
    with the same docstring rule as scripts/.)

Emits runtime/specs/tool-catalog.json + runtime/specs/tool-catalog.md.
Deterministic (no wall-clock in output — run twice, diff clean). Read-only over the
repo except its two output files. Stdlib only. Exit 0 always (receipts, not failures).
"""
import json, os, re, sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "runtime", "specs", "tool-catalog.json")
OUT_MD = os.path.join(ROOT, "runtime", "specs", "tool-catalog.md")

DESC_RE = re.compile(r"^description:\s*(.+)$", re.M)
DOCSTRING_RE = re.compile(r'^\s*(?:#[^\n]*\n)*\s*[ru]{0,2}("""|\'\'\')(.*?)\1', re.S)


def first_line(text):
    for ln in text.splitlines():
        ln = ln.strip()
        if ln:
            return ln
    return ""


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def py_jtbd(path):
    text = read(path)
    m = DOCSTRING_RE.match(text)
    if m:
        return first_line(m.group(2))
    # fallback: comment-header style (some operators declare via leading # lines)
    return sh_jtbd(path)


def sh_jtbd(path):
    for ln in read(path).splitlines():
        ln = ln.strip()
        if ln.startswith("#!") or not ln:
            continue
        if ln.startswith("#"):
            txt = ln.lstrip("#").strip()
            if txt:
                return txt
            continue
        break  # hit code before any comment
    return ""


def md_command_jtbd(text):
    # prefer the first blockquote line; fall back to first non-heading prose line
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith(">"):
            t = s.lstrip("> ").strip()
            if t:
                return t
    for ln in text.splitlines():
        s = ln.strip()
        if s and not s.startswith("#") and not s.startswith("---"):
            return s
    return ""


def js_jtbd(text):
    m = re.search(r"description:\s*['\"]([^'\"]+)['\"]", text)
    if m:
        return m.group(1)
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("//"):
            t = s.lstrip("/ ").strip()
            if t:
                return t
        elif s and not s.startswith("/*") and not s.startswith("*"):
            break
    return ""


def clean(s):
    s = re.sub(r"\s+", " ", s or "").strip().strip('"')
    return s[:240]


def collect():
    tools = []

    def add(kind, name, path, jtbd, invoke):
        tools.append({
            "kind": kind, "name": name,
            "path": os.path.relpath(path, ROOT),
            "jtbd": clean(jtbd) or "(no declared JTBD — add a docstring/description)",
            "invoke": invoke,
        })

    # skills
    sk = os.path.join(ROOT, ".claude", "skills")
    if os.path.isdir(sk):
        for d in sorted(os.listdir(sk)):
            p = os.path.join(sk, d, "SKILL.md")
            if os.path.isfile(p):
                body = read(p)
                m = DESC_RE.search(body)
                add("skill", d, p, m.group(1) if m else md_command_jtbd(body), f"/{d}")

    # commands
    cm = os.path.join(ROOT, ".claude", "commands")
    if os.path.isdir(cm):
        for f in sorted(os.listdir(cm)):
            if f.endswith(".md"):
                name = f[:-3]
                add("command", name, os.path.join(cm, f),
                    md_command_jtbd(read(os.path.join(cm, f))), f"/{name}")

    # workflows
    wf = os.path.join(ROOT, ".claude", "workflows")
    if os.path.isdir(wf):
        for f in sorted(os.listdir(wf)):
            if f.endswith((".js", ".mjs")):
                p = os.path.join(wf, f)
                add("workflow", os.path.splitext(f)[0], p, js_jtbd(read(p)),
                    f"Workflow scriptPath={os.path.relpath(p, ROOT)}")

    # hooks
    hk = os.path.join(ROOT, ".claude", "hooks")
    if os.path.isdir(hk):
        for f in sorted(os.listdir(hk)):
            if f.endswith(".sh"):
                p = os.path.join(hk, f)
                add("hook", os.path.splitext(f)[0], p, sh_jtbd(p), "(automatic — hook)")

    # scripts
    sc = os.path.join(ROOT, "scripts")
    if os.path.isdir(sc):
        for f in sorted(os.listdir(sc)):
            p = os.path.join(sc, f)
            if not os.path.isfile(p):
                continue
            if f.endswith(".py"):
                add("script", f, p, py_jtbd(p), f"python3 scripts/{f}")
            elif f.endswith(".sh"):
                add("script", f, p, sh_jtbd(p), f"scripts/{f}")

    # packaged tools (tool-forge shape): tools/<name>/ with a README and a runner
    tl = os.path.join(ROOT, "tools")
    if os.path.isdir(tl):
        for d in sorted(os.listdir(tl)):
            readme = os.path.join(tl, d, "README.md")
            if not os.path.isfile(readme):
                continue
            prose = ""
            for ln in read(readme).splitlines():
                ln = ln.strip()
                if ln and not ln.startswith(("#", "[!", "![", "<", "|", "```", ">")):
                    prose = ln
                    break
            runner = os.path.join(tl, d, d)
            invoke = f"tools/{d}/{d}" if os.path.isfile(runner) else f"see tools/{d}/README.md"
            add("package", d, readme, prose, invoke)

    # operators
    op = os.path.join(ROOT, "operators")
    if os.path.isdir(op):
        for f in sorted(os.listdir(op)):
            if f.endswith(".py"):
                p = os.path.join(op, f)
                add("operator", f, p, py_jtbd(p), f"python3 operators/{f}")

    return tools


def main():
    tools = collect()
    counts = {}
    for t in tools:
        counts[t["kind"]] = counts.get(t["kind"], 0) + 1
    missing = sum(1 for t in tools if t["jtbd"].startswith("(no declared"))
    cat = {
        "schema": "tool-catalog-v1",
        "note": "Harvested one-line JTBDs, never inferred. Deterministic — no wall-clock. "
                "Regenerate with: python3 scripts/tool_catalog_emit.py",
        "counts": dict(sorted(counts.items())),
        "total": len(tools),
        "missing_jtbd": missing,
        "tools": tools,
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(cat, f, indent=1, ensure_ascii=False)
        f.write("\n")

    lines = ["# Tool Catalog", "",
             "> Generated by `scripts/tool_catalog_emit.py` — do not hand-edit. "
             "One line per tool, JTBD harvested from the tool's own declaration.", "",
             "Counts: " + " · ".join(f"{k} {v}" for k, v in sorted(counts.items()))
             + f" · total {len(tools)} · missing JTBD {missing}", ""]
    for kind in ["skill", "command", "workflow", "hook", "script", "package", "operator"]:
        grp = [t for t in tools if t["kind"] == kind]
        if not grp:
            continue
        lines.append(f"## {kind}s ({len(grp)})")
        lines.append("")
        for t in grp:
            lines.append(f"- **{t['name']}** — {t['jtbd']}  \n  `{t['invoke']}`")
        lines.append("")
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"tool-catalog: {len(tools)} tools "
          f"({', '.join(f'{v} {k}' for k, v in sorted(counts.items()))}) · "
          f"{missing} missing JTBD -> {os.path.relpath(OUT_JSON, ROOT)} + .md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
