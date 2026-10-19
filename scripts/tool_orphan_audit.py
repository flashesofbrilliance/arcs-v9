#!/usr/bin/env python3
"""tool_orphan_audit.py — read-only install-state audit: wired, available-not-installed, unused, duplicate, broken.

Why: flashesofbrilliance/token-savings-bank was published 2026-08-15 and installed nowhere until
2026-10-06. Nothing told any session it existed. This pass inventories every tool surface and
classifies each item so sessions stop neglecting published tools or reinventing them.

Surfaces:
  repo  .claude/{skills,commands,agents}, scripts/, operators/OPERATOR-REGISTRY.json
  user  ~/.claude/{skills,commands}, ~/.claude/plugins/installed_plugins.json (+ settings
        enabledPlugins, known_marketplaces.json), ~/.claude/scheduled-tasks/*/SKILL.md
  pub   flashesofbrilliance public, non-fork repos that ship SKILL.md or .claude-plugin/
        (gh; cached daily in ~/.claude/cache/tool-orphan-public.json; never on every start)

Classes:
  WIRED                  loaded by sessions (skill/command/agent/enabled plugin) or referenced by
                         a hook, scheduled task, command, workflow, CI, git hook, or doc
  AVAILABLE-NOT-INSTALLED published skill/plugin/marketplace with no local install or local variant
  INSTALLED-UNUSED       present but nothing references it (scripts/operators), or a plugin that is
                         installed but not enabled / scoped to a stale project path.
                         Invocation telemetry does not exist, so "recent use" is not determinable.
  DUPLICATE              same normalized name on two surfaces, or near-identical declared JTBD
  BROKEN                 a referenced path is missing (scheduled task -> repo path, registry
                         binding -> module, plugin installPath, skill dir without SKILL.md)

Usage:
  python3 scripts/tool_orphan_audit.py            full report (uses public cache; refreshes if >24h)
  python3 scripts/tool_orphan_audit.py --json     full JSON
  python3 scripts/tool_orphan_audit.py --line     ONE line from the cached result, no scan, no network
                                                  (stale cache -> detached background refresh)
  python3 scripts/tool_orphan_audit.py --refresh  force the gh public-repo fetch, then audit
  python3 scripts/tool_orphan_audit.py --self-test

Read-only except its two cache files under ~/.claude/cache/. Stdlib only. Exit 0 (receipt, not gate),
except --self-test which exits 1 on failure.
"""
import fnmatch, json, os, re, subprocess, sys, tempfile, time

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = os.path.expanduser("~")
OWNER = "flashesofbrilliance"
DAY = 86400

CLASSES = ["WIRED", "AVAILABLE-NOT-INSTALLED", "INSTALLED-UNUSED", "DUPLICATE", "BROKEN"]

# files whose text counts as "someone references this tool" (repo-relative dirs/files)
REF_DIRS = [".claude", "scripts", ".github/workflows", "_PATTERNS", "runtime/specs", "docs",
            "operators/docs", "tools", "_QUEUE", "_CANON", "_DECISIONS"]
REF_FILES = ["CLAUDE.md", "AGENTS.md", "WORLD.md", "package.json", "README.md", ".mcp.json"]
REF_EXT = (".md", ".sh", ".py", ".mjs", ".js", ".json", ".jsonl", ".yml", ".yaml", ".ts", "")
SKIP_REF = {"runtime/specs/tool-catalog.json", "runtime/specs/tool-catalog.md"}  # the catalog lists everything


def cache_dir(home):
    return os.path.join(home, ".claude", "cache")


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def norm(name):
    n = name.lower()
    n = re.sub(r"\.(md|py|sh|mjs|js)$", "", n)
    n = re.sub(r"[-_](skill|plugin)$", "", n)
    return re.sub(r"[^a-z0-9]+", "-", n).strip("-")


def frontmatter_name(text):
    m = re.search(r"^name:\s*(.+)$", text, re.M)
    return m.group(1).strip().strip('"') if m else ""


def desc_of(text):
    m = re.search(r"^description:\s*(.+)$", text, re.M)
    if m:
        return m.group(1).strip().strip('"')
    for ln in text.splitlines():
        s = ln.strip().lstrip("> ").strip()
        if s and not s.startswith(("#", "---")):
            return s
    return ""


# ---------------------------------------------------------------- inventory

def inventory(root, home):
    items = []

    def add(surface, kind, name, path, jtbd="", **kw):
        it = {"surface": surface, "kind": kind, "name": name, "path": path, "jtbd": jtbd[:200],
              "state": None, "why": "", "fix": ""}
        it.update(kw)
        items.append(it)

    # repo + user skills/commands/agents: loaded by sessions on start
    for surface, base in (("repo", os.path.join(root, ".claude")), ("user", os.path.join(home, ".claude"))):
        sk = os.path.join(base, "skills")
        if os.path.isdir(sk):
            for d in sorted(os.listdir(sk)):
                p = os.path.join(sk, d)
                if not os.path.isdir(p) or d.startswith("."):
                    continue
                if d == "synced":  # claude.ai-synced bucket: <bucket>/<skill>/SKILL.md
                    for b in sorted(os.listdir(p)):
                        bp = os.path.join(p, b)
                        if os.path.isdir(bp):
                            for s in sorted(os.listdir(bp)):
                                sp = os.path.join(bp, s, "SKILL.md")
                                if os.path.isfile(sp):
                                    add("synced", "skill", s, sp, desc_of(read(sp)))
                    continue
                sp = os.path.join(p, "SKILL.md")
                if os.path.isfile(sp):
                    add(surface, "skill", d, sp, desc_of(read(sp)))
                else:
                    add(surface, "skill", d, p, state="BROKEN", why="skill dir has no SKILL.md")
        for kind, sub in (("command", "commands"), ("agent", "agents")):
            cd = os.path.join(base, sub)
            if os.path.isdir(cd):
                for f in sorted(os.listdir(cd)):
                    if f.endswith(".md"):
                        add(surface, kind, f[:-3], os.path.join(cd, f), desc_of(read(os.path.join(cd, f))))

    # repo scripts
    sc = os.path.join(root, "scripts")
    if os.path.isdir(sc):
        for f in sorted(os.listdir(sc)):
            if f.endswith((".py", ".sh", ".mjs")) and os.path.isfile(os.path.join(sc, f)):
                add("repo", "script", f, os.path.join(sc, f))

    # operator registry bindings
    reg = load_json(os.path.join(root, "operators", "OPERATOR-REGISTRY.json"), {})
    for op in reg.get("operators", []):
        mod = (op.get("binding") or {}).get("module")
        if not mod:
            continue  # UNBUILT rows carry no binding; registry already answers status=blocked
        p = os.path.join(root, "operators", mod)
        add("repo", "operator", f"op{op.get('op')}:{op.get('name')}", p, op.get("function", ""),
            module=mod, reg_status=op.get("status"))

    # plugins
    pdir = os.path.join(home, ".claude", "plugins")
    inst = load_json(os.path.join(pdir, "installed_plugins.json"), {}).get("plugins", {})
    enabled = load_json(os.path.join(home, ".claude", "settings.json"), {}).get("enabledPlugins", {}) or {}
    for key, rows in sorted(inst.items()):
        for r in rows:
            add("user", "plugin", key, r.get("installPath", ""), scope=r.get("scope"),
                project=r.get("projectPath", ""), enabled=bool(enabled.get(key)))
    for mk, v in sorted(load_json(os.path.join(pdir, "known_marketplaces.json"), {}).items()):
        add("user", "marketplace", mk, (v or {}).get("installLocation") or os.path.join(pdir, "marketplaces", mk))

    # scheduled tasks
    st = os.path.join(home, ".claude", "scheduled-tasks")
    if os.path.isdir(st):
        for d in sorted(os.listdir(st)):
            sp = os.path.join(st, d, "SKILL.md")
            if os.path.isfile(sp):
                add("user", "task", d, sp, desc_of(read(sp)))
    return items


# ---------------------------------------------------------------- reference corpus

def ref_corpus(root, home):
    """{relpath: text} for every file whose mention of a tool counts as wiring."""
    out = {}
    paths = [os.path.join(root, f) for f in REF_FILES]
    for d in REF_DIRS:
        base = os.path.join(root, d)
        for dp, dns, fns in os.walk(base):
            dns[:] = [x for x in dns if x not in ("node_modules", "__pycache__", ".git", ".venv", "worktrees")]
            paths += [os.path.join(dp, f) for f in fns if f.endswith(REF_EXT)]
    for p in paths:
        rel = os.path.relpath(p, root)
        if rel in SKIP_REF or not os.path.isfile(p) or os.path.getsize(p) > 2_000_000:
            continue
        out[rel] = read(p)
    for sub in ("scheduled-tasks", "hooks", "commands", "skills"):
        base = os.path.join(home, ".claude", sub)
        for dp, dns, fns in os.walk(base):
            dns[:] = [x for x in dns if x != ".git"]
            for f in fns:
                if f.endswith((".md", ".sh", ".py", ".json")):
                    out["~/" + os.path.relpath(os.path.join(dp, f), home)] = read(os.path.join(dp, f))
    out["~/.claude/settings.json"] = read(os.path.join(home, ".claude", "settings.json"))
    return out


TOKEN_RE = re.compile(r"[A-Za-z0-9_][\w.-]*")


def token_index(corpus):
    """token -> files containing it. One pass over the corpus (the per-name regex scan took 60s)."""
    idx = {}
    for k, t in corpus.items():
        for tok in set(TOKEN_RE.findall(t)):
            idx.setdefault(tok.rstrip(".-"), set()).add(k)
    return idx


GLOB_RE = re.compile(r"(?<![\w/.~*-])((?:[\w.-]+/)*[\w.-]*\*[\w.*-]*)")
GLOB_EXT = (".py", ".sh", ".mjs", ".js", ".ts", ".md", ".json")


def glob_patterns(corpus):
    """[(pattern, file)] for path globs written in the reference corpus, for example the loop in
    phosphor_suite.sh that runs scripts/phosphor_*_check.mjs. A text match on the name cannot see these.
    Guards against over-broad globs: the pattern must end in a file extension and its file-name part must
    carry at least 4 literal characters, so scripts/* and *.py never wire everything."""
    out = []
    for f, t in corpus.items():
        if f == "scripts/tool_orphan_audit.py":   # its own docstring quotes example globs; those must not wire anything
            continue
        for m in GLOB_RE.findall(t):
            pat = m.strip(".,;:)'\"`")
            if not pat.endswith(GLOB_EXT):
                continue
            base = pat.rsplit("/", 1)[-1].rsplit(".", 1)[0]
            if len(re.sub(r"[^A-Za-z0-9_-]", "", base)) < 4:
                continue
            out.append((pat, f))
    return out


def glob_referrers(relpath, globs, own):
    """Files whose written glob matches this script's repo-relative path (never the file's own text)."""
    name = relpath.rsplit("/", 1)[-1]
    hits = set()
    for pat, f in globs:
        if f in own:
            continue
        if fnmatch.fnmatch(relpath if "/" in pat else name, pat):
            hits.add(f"{f} ({pat})")
    return sorted(hits)


def referrers(name, own_path, idx, root, home):
    stem = re.sub(r"\.(py|sh|mjs)$", "", name)
    own = {os.path.relpath(own_path, root), "~/" + os.path.relpath(own_path, home)}
    hits = idx.get(name, set()) | idx.get(stem, set())
    return sorted(hits - own)


REPO_PATH_RE = re.compile(r"(?<![\w/.~-])((?:scripts|operators|tools|\.claude)/[\w./-]+\.(?:py|sh|mjs|js|md|json))")


# ---------------------------------------------------------------- public repos

def fetch_public(owner=OWNER):
    """gh: public non-fork repos that ship a skill or plugin. Network; called at most daily."""
    def gh(*a):
        return subprocess.run(["gh", *a], capture_output=True, text=True, timeout=30).stdout
    repos = json.loads(gh("repo", "list", owner, "--visibility", "public", "--limit", "200",
                          "--json", "name,description,isFork,defaultBranchRef") or "[]")
    out = []
    for r in repos:
        if r.get("isFork"):
            continue
        br = (r.get("defaultBranchRef") or {}).get("name") or "main"
        tree = gh("api", f"repos/{owner}/{r['name']}/git/trees/{br}?recursive=1", "-q", ".tree[].path").split()
        skills = [p for p in tree if p == "SKILL.md" or p.endswith("/SKILL.md")]
        plugin = ".claude-plugin/plugin.json" in tree
        market = ".claude-plugin/marketplace.json" in tree
        if not (skills or plugin or market):
            continue
        entry = {"repo": r["name"], "description": (r.get("description") or "")[:200],
                 "skills": skills, "plugin": None, "marketplace": None}
        def content(path):
            raw = gh("api", f"repos/{owner}/{r['name']}/contents/{path}", "-q", ".content")
            import base64
            try:
                return json.loads(base64.b64decode(raw).decode())
            except Exception:
                return {}
        if plugin:
            entry["plugin"] = content(".claude-plugin/plugin.json").get("name") or r["name"]
        if market:
            m = content(".claude-plugin/marketplace.json")
            entry["marketplace"] = {"name": m.get("name") or r["name"],
                                    "plugins": [p.get("name") for p in m.get("plugins", [])]}
        out.append(entry)
    return out


def public_cached(home, refresh=False, fetch=fetch_public):
    path = os.path.join(cache_dir(home), "tool-orphan-public.json")
    c = load_json(path, {})
    if refresh or not c or time.time() - c.get("fetched_at", 0) > DAY:
        try:
            repos = fetch()
            c = {"fetched_at": int(time.time()), "repos": repos}
            os.makedirs(cache_dir(home), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(c, f, indent=1)
        except Exception as e:  # offline / gh missing: keep the stale cache, say so
            c.setdefault("repos", [])
            c["error"] = f"{type(e).__name__}: {e}"[:200]
    return c


def public_items(pub, local_names, known_markets):
    """Each published skill/plugin/marketplace -> item. Installed if any local name matches or contains it."""
    items = []

    def local_match(n):
        n = norm(n)
        return sorted(l for l in local_names if l == n or n in l)

    for r in pub.get("repos", []):
        src = f"{OWNER}/{r['repo']}"
        if r.get("marketplace"):
            mk = r["marketplace"]["name"]
            it = {"surface": "pub", "kind": "marketplace", "name": mk, "path": src,
                  "jtbd": r.get("description", ""), "why": "", "fix": ""}
            if mk in known_markets:
                it.update(state="WIRED", why="marketplace known locally")
            else:
                it.update(state="AVAILABLE-NOT-INSTALLED",
                          why=f"marketplace '{mk}' ({len(r['marketplace']['plugins'])} plugins) not added",
                          fix=f"claude plugin marketplace add {src}")
            items.append(it)
        if r.get("plugin") or r.get("skills"):
            name = r.get("plugin") or norm(r["repo"])
            hits = local_match(name)
            it = {"surface": "pub", "kind": "plugin" if r.get("plugin") else "skill", "name": name,
                  "path": src, "jtbd": r.get("description", ""), "why": "", "fix": ""}
            if hits:
                exact = norm(name) in hits
                it.update(state="WIRED", why=("installed" if exact else "local variant: " + ", ".join(hits)))
            else:
                it.update(state="AVAILABLE-NOT-INSTALLED", why="published, no local install or variant",
                          fix=f"git clone https://github.com/{src}.git ~/.claude/skills/{norm(name)}")
            items.append(it)
    return items


# ---------------------------------------------------------------- classify

STOP = set("the a an and or of to for in on with is are be it this that use when any from by as at your you its into".split())


def toks(s):
    return {w for w in re.findall(r"[a-z]{3,}", (s or "").lower()) if w not in STOP}


def classify(root, home, pub=None):
    items = inventory(root, home)
    corpus = ref_corpus(root, home)
    idx = token_index(corpus)
    globs = glob_patterns(corpus)

    for it in items:
        if it["state"]:
            continue
        k = it["kind"]
        if k in ("skill", "command", "agent"):
            it.update(state="WIRED", why="loaded by sessions")
        elif k == "script":
            refs = referrers(it["name"], it["path"], idx, root, home)
            grefs = [] if refs else glob_referrers(os.path.relpath(it["path"], root), globs,
                                                     {os.path.relpath(it["path"], root)})
            if refs:
                it.update(state="WIRED", why=f"{len(refs)} ref(s): " + ", ".join(refs[:3]))
            elif grefs:
                it.update(state="WIRED", why=f"matched by a written glob: " + ", ".join(grefs[:2]))
            else:
                it.update(state="INSTALLED-UNUSED", why="no hook/command/task/CI/doc references it",
                          fix="wire it (command/hook/doc) or retire it to _ARCHIVE")
        elif k == "operator":
            if not os.path.isfile(it["path"]):
                it.update(state="BROKEN", why=f"registry binding module missing: operators/{it['module']}",
                          fix="python3 scripts/operator_registry_emit.py")
            else:
                it.update(state="WIRED", why=f"registry binding ({it.get('reg_status')}) via MCP bridge")
        elif k == "plugin":
            if not it["path"] or not os.path.isdir(it["path"]):
                it.update(state="BROKEN", why="installPath missing", fix=f"claude plugin install {it['name']}")
            elif it.get("scope") == "project" and it.get("project") and not os.path.isdir(it["project"]):
                it.update(state="BROKEN", why=f"project scope path gone: {it['project']}")
            elif it.get("scope") == "project" and not (root + "/").startswith(it["project"].rstrip("/") + "/"):
                it.update(state="INSTALLED-UNUSED",
                          why=f"project-scoped to {it['project']} only", fix=f"claude plugin uninstall {it['name']}")
            elif not it.get("enabled"):
                it.update(state="INSTALLED-UNUSED", why="installed, not in settings enabledPlugins",
                          fix=f"claude plugin enable {it['name']}")
            else:
                it.update(state="WIRED", why="enabled")
        elif k == "marketplace":
            if os.path.isdir(it["path"]):
                it.update(state="WIRED", why="known marketplace")
            else:
                it.update(state="BROKEN", why="known marketplace, clone missing",
                          fix=f"claude plugin marketplace update {it['name']}")
        elif k == "task":
            text = read(it["path"])
            # a task may target another checkout by absolute path; a relative path is fine if it exists in any
            bases = [root] + [d for d in set(re.findall(r"(/Users/[\w.-]+/[\w.-]+)", text)) if os.path.isdir(d)]
            missing = sorted({p for p in REPO_PATH_RE.findall(text) if "*" not in p and "<" not in p
                              and not any(os.path.exists(os.path.join(b, p)) for b in bases)})
            if missing:
                it.update(state="BROKEN", why="references missing repo path(s): " + ", ".join(missing[:4]),
                          missing=missing)
            else:
                it.update(state="WIRED", why="scheduled task")

    # public catalog (available-not-installed)
    local_names = {norm(i["name"].split("@")[0]) for i in items if i["kind"] in ("skill", "command", "agent", "plugin")}
    if pub is not None:
        known = {i["name"] for i in items if i["kind"] == "marketplace"}
        items += public_items(pub, local_names, known)

    # duplicates: same normalized name across >1 loaded surface, or near-identical JTBD
    loaded = [i for i in items if i["kind"] in ("skill", "command", "agent") and i["state"] == "WIRED"]
    by = {}
    for i in loaded:
        by.setdefault(norm(i["name"]), []).append(i)
    dups = []
    for n, grp in sorted(by.items()):
        if len({(g["surface"], g["kind"]) for g in grp}) > 1:
            dups.append({"reason": "same name", "key": n,
                         "members": [f"{g['surface']}:{g['kind']}:{g['name']}" for g in grp]})
    for a_i in range(len(loaded)):
        a = loaded[a_i]
        ta = toks(a["jtbd"])
        if len(ta) < 6:
            continue
        for b in loaded[a_i + 1:]:
            if norm(a["name"]) == norm(b["name"]):
                continue
            tb = toks(b["jtbd"])
            if len(tb) < 6:
                continue
            j = len(ta & tb) / len(ta | tb)
            if j >= 0.5:
                dups.append({"reason": f"jtbd jaccard {j:.2f}", "key": f"{norm(a['name'])}~{norm(b['name'])}",
                             "members": [f"{a['surface']}:{a['kind']}:{a['name']}", f"{b['surface']}:{b['kind']}:{b['name']}"]})
    for d in dups:
        it = {"surface": "multi", "kind": "duplicate", "name": d["key"], "path": "", "jtbd": "",
              "state": "DUPLICATE", "why": f"{d['reason']}: " + " | ".join(d["members"]),
              "fix": "pick the canonical one; retire or point the other at it"}
        items.append(it)
    return items


def summarize(items, pub=None):
    counts = {c: 0 for c in CLASSES}
    for i in items:
        counts[i["state"]] += 1
    res = {"schema": "tool-orphan-audit-v1", "counts": counts, "total": len(items),
           "items": [{k: v for k, v in i.items() if k not in ("missing",)} for i in items]}
    if pub is not None:
        res["public_fetched_at"] = pub.get("fetched_at")
        if pub.get("error"):
            res["public_error"] = pub["error"]
    return res


def one_line(res):
    c = res["counts"]
    s = (f"tools: {c['WIRED']} wired · {c['AVAILABLE-NOT-INSTALLED']} available-not-installed · "
         f"{c['INSTALLED-UNUSED']} unused · {c['DUPLICATE']} duplicates · {c['BROKEN']} broken")
    if c["AVAILABLE-NOT-INSTALLED"] or c["DUPLICATE"] or c["BROKEN"]:
        s += " (run /catalog --orphans)"
    return s


def write_result(home, res):
    os.makedirs(cache_dir(home), exist_ok=True)
    res = dict(res, generated_at=int(time.time()))
    with open(os.path.join(cache_dir(home), "tool-orphan-audit.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)


def run(root, home, refresh=False):
    pub = public_cached(home, refresh=refresh)
    res = summarize(classify(root, home, pub), pub)
    write_result(home, res)
    return res


def line_mode(home):
    """No scan, no network. Stale or missing cache -> detached background refresh."""
    res = load_json(os.path.join(cache_dir(home), "tool-orphan-audit.json"), {})
    stale = not res or time.time() - res.get("generated_at", 0) > DAY
    if stale:
        try:
            subprocess.Popen([sys.executable, os.path.abspath(__file__)], cwd=ROOT,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
                             start_new_session=True, env=dict(os.environ, CLAUDE_PROJECT_DIR=ROOT))
        except OSError:
            pass
    if not res:
        return "tools: audit not cached yet (refreshing in background; or run python3 scripts/tool_orphan_audit.py)"
    return one_line(res) + (" [cache >24h, refreshing]" if stale else "")


def report(res):
    out = [one_line(res)]
    if res.get("public_error"):
        out.append(f"  (public-repo fetch failed, using stale cache: {res['public_error']})")
    for cls in CLASSES[1:]:
        grp = [i for i in res["items"] if i["state"] == cls]
        if not grp:
            continue
        out.append(f"\n## {cls} ({len(grp)})")
        for i in grp:
            out.append(f"- [{i['surface']}:{i['kind']}] {i['name']} — {i['why']}")
            if i.get("fix"):
                out.append(f"    fix: {i['fix']}")
    return "\n".join(out)


# ---------------------------------------------------------------- self-test

def self_test():
    ok = True
    with tempfile.TemporaryDirectory() as t:
        root, home = os.path.join(t, "repo"), os.path.join(t, "home")

        def w(p, s=""):
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                f.write(s)
        # repo
        w(f"{root}/.claude/skills/handoff/SKILL.md", "---\nname: handoff\ndescription: write a handoff\n---\n")
        w(f"{root}/.claude/skills/empty/README.md", "no skill file")                      # BROKEN skill dir
        w(f"{root}/.claude/commands/run-wired.md", "> run `python3 scripts/wired_tool.py`\n")
        w(f"{root}/scripts/wired_tool.py", '"""wired"""\n')                                 # WIRED (good)
        w(f"{root}/scripts/lonely_tool.py", '"""nobody calls me"""\n')                      # INSTALLED-UNUSED
        # glob wiring: good (both match the written glob) and bad (too-broad globs and a non-matching sibling)
        w(f"{root}/scripts/glob_a_check.mjs", "// a\n")
        w(f"{root}/scripts/glob_b_check.mjs", "// b\n")
        w(f"{root}/scripts/glob_a_other.mjs", "// not matched by the glob\n")
        w(f"{root}/scripts/broad_victim.py", '"""only broad globs point here"""\n')
        w(f"{root}/scripts/tool_orphan_audit.py", "# example only: scripts/glob_x_only_*.mjs\n")   # self-quote must wire nothing
        w(f"{root}/scripts/glob_x_only_one.mjs", "// matched only by the audit's own comment\n")
        w(f"{root}/.claude/commands/run-suite.md", "> run every `scripts/glob_*_check.mjs`; never `scripts/*` or `*.py` or `scripts/*.mjs`\n")
        w(f"{root}/operators/core/atoms.py", "class A: pass\n")
        w(f"{root}/operators/OPERATOR-REGISTRY.json", json.dumps({"operators": [
            {"op": 1, "name": "Good", "binding": {"module": "core/atoms.py"}, "status": "READY"},
            {"op": 2, "name": "Gone", "binding": {"module": "core/missing.py"}, "status": "READY"}]}))
        # user
        w(f"{home}/.claude/commands/handoff.md", "> a second handoff\n")                    # DUPLICATE (name)
        w(f"{home}/.claude/skills/token-savings-bank/SKILL.md", "---\ndescription: budget\n---\n")
        w(f"{home}/.claude/scheduled-tasks/good-task/SKILL.md", "run scripts/wired_tool.py\n")
        w(f"{home}/.claude/scheduled-tasks/bad-task/SKILL.md", "run scripts/vanished.py\n")  # BROKEN task
        os.makedirs(f"{home}/.claude/plugins/cache/p1")
        w(f"{home}/.claude/plugins/installed_plugins.json", json.dumps({"plugins": {
            "ok@m": [{"scope": "user", "installPath": f"{home}/.claude/plugins/cache/p1"}],
            "gone@m": [{"scope": "user", "installPath": f"{home}/nope"}],
            "off@m": [{"scope": "user", "installPath": f"{home}/.claude/plugins/cache/p1"}]}}))
        w(f"{home}/.claude/settings.json", json.dumps({"enabledPlugins": {"ok@m": True, "gone@m": True}}))
        w(f"{home}/.claude/plugins/known_marketplaces.json", json.dumps({"official": {}}))
        os.makedirs(f"{home}/.claude/plugins/marketplaces/official")
        pub = {"repos": [
            {"repo": "token-savings-bank", "plugin": "token-savings-bank", "skills": ["SKILL.md"]},   # WIRED (installed)
            {"repo": "rca-skill", "plugin": "rca", "skills": ["SKILL.md"]},                            # AVAILABLE
            {"repo": "arcs-skills", "skills": [], "plugin": None,
             "marketplace": {"name": "arcs", "plugins": ["rca"]}}]}                                   # AVAILABLE (mkt)
        items = classify(root, home, pub)
        st = {(i["surface"], i["kind"], i["name"]): i["state"] for i in items}
        expect = {
            ("repo", "script", "wired_tool.py"): "WIRED",
            ("repo", "script", "lonely_tool.py"): "INSTALLED-UNUSED",
            ("repo", "script", "glob_a_check.mjs"): "WIRED",
            ("repo", "script", "glob_b_check.mjs"): "WIRED",
            ("repo", "script", "glob_a_other.mjs"): "INSTALLED-UNUSED",
            ("repo", "script", "broad_victim.py"): "INSTALLED-UNUSED",
            ("repo", "script", "glob_x_only_one.mjs"): "INSTALLED-UNUSED",
            ("repo", "script", "tool_orphan_audit.py"): "INSTALLED-UNUSED",
            ("repo", "skill", "empty"): "BROKEN",
            ("repo", "operator", "op1:Good"): "WIRED",
            ("repo", "operator", "op2:Gone"): "BROKEN",
            ("user", "task", "good-task"): "WIRED",
            ("user", "task", "bad-task"): "BROKEN",
            ("user", "plugin", "ok@m"): "WIRED",
            ("user", "plugin", "gone@m"): "BROKEN",
            ("user", "plugin", "off@m"): "INSTALLED-UNUSED",
            ("pub", "plugin", "token-savings-bank"): "WIRED",
            ("pub", "plugin", "rca"): "AVAILABLE-NOT-INSTALLED",
            ("pub", "marketplace", "arcs"): "AVAILABLE-NOT-INSTALLED",
            ("multi", "duplicate", "handoff"): "DUPLICATE",
        }
        for k, v in expect.items():
            got = st.get(k)
            flag = "PASS" if got == v else "FAIL"
            ok &= got == v
            print(f"  {flag} {k[0]}:{k[1]}:{k[2]} expected {v} got {got}")
        # pass-on-good: a clean world yields zero non-WIRED findings
        unexpected = [i for i in items if (i["surface"], i["kind"], i["name"]) not in expect and i["state"] != "WIRED"]
        print(f"  {'PASS' if not unexpected else 'FAIL'} no unexpected findings ({len(unexpected)})")
        ok &= not unexpected
        line = one_line(summarize(items))
        good = "run /catalog --orphans" in line
        print(f"  {'PASS' if good else 'FAIL'} one-line nudges when gaps exist: {line}")
        ok &= good
        clean_line = one_line({"counts": {c: (5 if c == 'WIRED' else 0) for c in CLASSES}})
        good = "--orphans" not in clean_line
        print(f"  {'PASS' if good else 'FAIL'} one-line silent nudge when clean: {clean_line}")
        ok &= good
    print("self-test:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    if "--line" in argv:
        print(line_mode(HOME))
        return 0
    res = run(ROOT, HOME, refresh="--refresh" in argv)
    print(json.dumps(res, indent=1) if "--json" in argv else report(res))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
