#!/usr/bin/env python3
"""universe_ask: cheap, clean-room retrieval over ONE universe of sourced claims.

Rule: before asking Zach or a counterpart a question about an entity, run this first.
Isolation is the point: a universe is the only thing searched. There is no wildcard.
Crossing universes needs --bridge <other> --why "<reason>"; every bridged hit is tagged and the
bridge is logged locally (sources/bridge-log.jsonl, gitignored).

Atoms: _STATE/job-search/universe/<universe>.claims.jsonl, one per line:
  id (<universe>/<n>), entity, type (claim|inference|hypothesis|quote|collision), claim, source,
  grade (A primary doc by the entity, B self-reported, C second-hand, inference, hypothesis),
  verified_at, ttl_days, tags, audience (internal|external; missing = internal, fail closed).
  quote atoms also carry speaker + source_ref (mapped in the registry to a speaker-tagged transcript).
Registry: _STATE/job-search/universe/_registry.json (tier, entities, names, anti_aliases,
  shape, name_shapes, speakers, quote_sources, canon roots).

Loader refusals (the clean-room checks): id prefix or entity not in this universe; a claim with no
source; external audience on anything but a sourced type=claim; a quote with no speaker/source_ref;
in a canon-tier universe, a source outside its roots or any counterpart name in the text.

  python3 scripts/universe_ask.py --universe wonderful-ai "how many FDEs are they hiring" [-k 5]
  python3 scripts/universe_ask.py --universe wonderful-ai --project public     # external-safe atoms, pseudonymised
  python3 scripts/universe_ask.py --universe wonderful-ai --lint-quotes        # ADR-033 speaker check
  python3 scripts/universe_ask.py --self-test
Stdlib only. ~60 tokens per hit; STALE marks claims past their ttl.
"""
import argparse, hashlib, importlib.util, json, os, re, sys, tempfile
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ROOT = os.path.join(REPO, "_STATE", "job-search", "universe")
STOP = set("a an the of to in on for and or is are was were did does do he she they it his her their with at by from as be that this what who how when where why any about".split())
tok = lambda s: [w for w in re.findall(r"[a-z0-9$%+]+", s.lower()) if w not in STOP]
EXTERNAL_TYPES = {"claim"}
EXTERNAL_GRADES = {"A", "B", "C"}


def word_re(name):
    return re.compile(r"(?<![a-z0-9])" + re.escape(name.lower()) + r"(?![a-z0-9])")


def find_names(text, names):
    t = text.lower()
    return [n for n in names if word_re(n).search(t)]


def load_registry(root=ROOT):
    return json.load(open(os.path.join(root, "_registry.json"), encoding="utf-8"))


def counterpart_names(reg, exclude=()):
    """Every name that identifies a counterpart: registered counterpart universes + the extra deny list."""
    out = list(reg.get("canon_denied_names_extra", []))
    for u, d in reg["universes"].items():
        if d.get("tier") == "counterpart" and u not in exclude:
            out += d.get("names", [])
    return out


def atom_text(r):
    """The text a name/alias grep covers: claim, entity and tags. Never the source path (provenance may name the room)."""
    return " ".join([r.get("claim", ""), r.get("entity", ""), " ".join(r.get("tags", []))])


def load(u, reg, root=ROOT, repo=REPO):
    if u not in reg["universes"]:
        sys.exit(f"unknown universe '{u}'. Registered: {', '.join(reg['universes'])}. Add it to _registry.json first.")
    d = reg["universes"][u]
    p = os.path.join(root, f"{u}.claims.jsonl")
    rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if os.path.exists(p) else []
    ents = set(d["entities"])
    deny = counterpart_names(reg) if d.get("tier") == "canon" else []
    for r in rows:
        if not r["id"].startswith(u + "/") or r["entity"] not in ents:
            sys.exit(f"CONTAMINATION: atom {r['id']} (entity {r['entity']}) does not belong to universe {u}. Refusing to load.")
        if r["type"] in ("claim", "collision") and not r.get("source"):
            sys.exit(f"UNSOURCED claim {r['id']}: a claim needs a source; use type inference or hypothesis.")
        aud = r.get("audience", d.get("audience_default", "internal"))
        if aud not in ("internal", "external"):
            sys.exit(f"BAD AUDIENCE on {r['id']}: '{aud}' (internal|external).")
        if aud == "external" and d.get("tier") == "personal":
            sys.exit(f"AIR-GAP: {r['id']} is tagged external but universe '{u}' is a personal-tier universe (a person's own receipts never leave internal).")
        if aud == "external" and r.get("bridges"):
            sys.exit(f"AIR-GAP: {r['id']} is tagged external but declares bridges {r['bridges']} to counterpart universes.")
        if aud == "external" and (r["type"] not in EXTERNAL_TYPES or r.get("grade") not in EXTERNAL_GRADES):
            sys.exit(f"AIR-GAP: {r['id']} is tagged external but is type={r['type']} grade={r.get('grade')}. Only sourced claims (A/B/C) may be external; inferences, hypotheses, quotes and collisions are internal.")
        if r["type"] == "quote" and not (r.get("speaker") and r.get("source_ref")):
            sys.exit(f"QUOTE {r['id']} needs speaker and source_ref (ADR-033 speaker coordinate).")
        if d.get("tier") == "canon":
            top = r["source"].split(":")[0].split("/")[0]
            if top not in d.get("roots", []):
                sys.exit(f"CANON {r['id']}: source {r['source']} is outside the read-only roots {d.get('roots')}.")
            hit = find_names(atom_text(r), deny)
            if hit:
                sys.exit(f"COUNTERPART IN CANON: {r['id']} mentions '{hit[0]}'. No counterpart fact may enter canon.")
    return rows


def audience_of(r, reg, u):
    return r.get("audience", reg["universes"][u].get("audience_default", "internal"))


def canon_drift(rows, repo=REPO):
    """Canon atoms carry src_sha (sha256 of the source file at adapter time). Return atoms whose source changed or vanished."""
    out = []
    for r in rows:
        f = os.path.join(repo, r["source"].split(":")[0])
        sha = hashlib.sha256(open(f, "rb").read()).hexdigest()[:16] if os.path.exists(f) else None
        if r.get("src_sha") and sha != r["src_sha"]:
            out.append(r["id"])
    return out


KEY_PLAIN, KEY_ENC = "pseudonym-key.json", "pseudonym-key.enc"


def _passphrase():
    """Env ARCS_KEY_PASS (tests, CI), else the macOS Keychain item the backups use (service arcs-memory-backup). Never printed."""
    import subprocess
    if os.environ.get("ARCS_KEY_PASS"):
        return os.environ["ARCS_KEY_PASS"]
    r = subprocess.run(["security", "find-generic-password", "-s", "arcs-memory-backup", "-w"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def _openssl(mode, data, pw):
    import subprocess
    r = subprocess.run(["openssl", "enc", mode, "-aes-256-cbc", "-pbkdf2", "-iter", "600000", "-salt", "-pass", "env:ARCS_KEY_PW"],
                       input=data, capture_output=True, env={**os.environ, "ARCS_KEY_PW": pw})
    if r.returncode != 0:
        sys.exit("openssl failed (wrong passphrase or corrupt file).")
    return r.stdout


def _read_key(root):
    enc, plain = (os.path.join(root, "sources", n) for n in (KEY_ENC, KEY_PLAIN))
    if os.path.exists(enc):
        pw = _passphrase()
        if not pw:
            return None, True
        want = open(enc + ".sha256").read().split()[0] if os.path.exists(enc + ".sha256") else None
        if want and hashlib.sha256(open(enc, "rb").read()).hexdigest() != want:
            sys.exit("INTEGRITY: pseudonym-key.enc does not match its recorded SHA-256. Restore from the iCloud copy.")
        return json.loads(_openssl("-d", open(enc, "rb").read(), pw)), True
    if os.path.exists(plain):
        return json.load(open(plain)), False
    return {"salt": hashlib.sha256(os.urandom(16)).hexdigest(), "map": {}}, False


def _write_key(root, key, sealed):
    os.makedirs(os.path.join(root, "sources"), exist_ok=True)
    plain, enc = (os.path.join(root, "sources", n) for n in (KEY_PLAIN, KEY_ENC))
    if sealed:
        ct = _openssl("-e", json.dumps(key).encode(), _passphrase())
        open(enc, "wb").write(ct); open(enc + ".sha256", "w").write(hashlib.sha256(ct).hexdigest() + "  " + KEY_ENC + "\n")
    else:
        json.dump(key, open(plain, "w"), indent=1)


def seal_key(root=ROOT):
    """Two parts. (1) tags are salted SHA-256 of the universe name (one-way). (2) the salt+map file is AES-256-CBC/PBKDF2-600k
    encrypted at rest with the backup passphrase, with a SHA-256 of the ciphertext beside it. Plaintext is deleted only
    after a decrypt round-trip matches. The .enc + .sha256 pair is safe to copy to iCloud ARCS/_backups next to the memory backups."""
    plain, enc = (os.path.join(root, "sources", n) for n in (KEY_PLAIN, KEY_ENC))
    if not os.path.exists(plain):
        sys.exit("nothing to seal: no plaintext pseudonym-key.json.")
    pw = _passphrase()
    if not pw:
        sys.exit("no passphrase: set ARCS_KEY_PASS or add the Keychain item 'arcs-memory-backup'.")
    key = json.load(open(plain)); _write_key(root, key, True)
    back = json.loads(_openssl("-d", open(enc, "rb").read(), pw))
    if back != key:
        os.unlink(enc); sys.exit("round-trip mismatch; plaintext kept, ciphertext discarded.")
    os.unlink(plain)
    print(f"sealed {len(key['map'])} tag(s) -> {enc} (+ .sha256 {open(enc + '.sha256').read().split()[0][:12]}...). Plaintext removed after a verified round-trip.")


def pseud_tag(u, root=ROOT):
    """The tag lets Zach map a public surface back to a client; it never carries the name."""
    key, sealed = _read_key(root)
    if key is None:
        return "unavailable (key sealed, passphrase not found)"
    if u not in key["map"]:
        key["map"][u] = "c-" + hashlib.sha256((key["salt"] + u).encode()).hexdigest()[:6]
        _write_key(root, key, sealed)
    return key["map"][u]


def project_public(u, reg, rows, root=ROOT):
    """External-safe projection: only audience=external atoms. Names are replaced by the client's SHAPE (what it does, from the
    registry `shape` / `name_shapes`), never by a hand-picked alias. Fails closed: no shape, a shape that names a counterpart,
    or any counterpart name left after substitution -> refuse. Atom ids are opaque hashes (the universe name identifies too)."""
    d = reg["universes"][u]
    if d.get("tier") == "personal":
        sys.exit(f"REFUSED: universe '{u}' is personal-tier; it has no public projection.")
    shape = d.get("shape")
    if d.get("tier") != "canon" and not shape:
        sys.exit(f"REFUSED: universe '{u}' has no `shape` in the registry (a public description of what the client does, e.g. 'a predictive analytics and forecasting company').")
    leaks = find_names(shape or "", counterpart_names(reg))
    if leaks:
        sys.exit(f"LEAK: the shape for '{u}' contains the name '{leaks[0]}'.")
    ns = d.get("name_shapes", {})
    names = sorted(d.get("names", []) + d.get("redact", []), key=len, reverse=True)  # redact = bare words too ambiguous for query warnings but identifying in a public surface
    out = []
    for r in rows:
        if audience_of(r, reg, u) != "external":
            continue
        text = r["claim"]
        for n in names:
            text = re.sub(r"(?i)(?<![a-z0-9])" + re.escape(n) + r"(?![a-z0-9])", ns.get(n) or shape or n, text)
        for other in counterpart_names(reg) + d.get("redact", []):  # nothing else identifying may remain, from this or any universe
            if shape and find_names(text, [other]):
                sys.exit(f"LEAK: '{other}' survives in projected atom {r['id']}. Add it to name_shapes or fix the atom before projecting.")
        out.append({"id": "pub-" + hashlib.sha1(r["id"].encode()).hexdigest()[:6], "claim": text, "grade": r["grade"]})
    if d.get("tier") != "canon":
        print(f"# client {pseud_tag(u, root)}: {shape}", file=sys.stderr)
    return out


def lint_quotes(u, reg, rows, root=ROOT):
    """Wire ADR-033 (speaker coordinate): every quote atom must anchor in a turn spoken by its attributed speaker.
    Returns [(atom_id, verdict, detail)]. SKIPPED when the transcript is not on this machine (it is gitignored)."""
    spec = importlib.util.spec_from_file_location("apl", os.path.join(HERE, "attribution_provenance_lint.py"))
    apl = importlib.util.module_from_spec(spec); spec.loader.exec_module(apl)
    d = reg["universes"][u]
    out = []
    for side in ("them", "me"):
        qs = [r for r in rows if r["type"] == "quote" and d.get("speakers", {}).get(r["speaker"]) == side]
        for r in rows:
            if r["type"] == "quote" and r["speaker"] not in d.get("speakers", {}):
                out.append((r["id"], "UNSOURCED", f"speaker '{r['speaker']}' has no side in registry speakers"))
        if not qs:
            continue
        srcs = {ref: os.path.join(root, rel) for ref, rel in d.get("quote_sources", {}).items()}
        have = {k: v for k, v in srcs.items() if os.path.exists(v)}
        for r in qs:
            if r["source_ref"] not in have:
                out.append((r["id"], "SKIPPED", f"transcript {r['source_ref']} not on this machine"))
        qs = [r for r in qs if r["source_ref"] in have]
        if not qs:
            continue
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump({"items": [{"quote": r["claim"], "source_ref": r["source_ref"]} for r in qs]}, f)
        try:  # the lint treats 'Them' as the counterpart; for a Zach-attributed quote swap the sides
            raw = apl.lint_artifact(f.name, have, me_labels=("Me",) if side == "them" else ("Them",))
        finally:
            os.unlink(f.name)
        for fd in raw["findings"]:
            idx = int(re.search(r"items\[(\d+)\]", fd["where"]).group(1))
            out.append((qs[idx]["id"], fd["verdict"], f"them={fd.get('them')} me={fd.get('me')}"))
    return out


def log_bridge(names, why, query, root=ROOT):
    p = os.path.join(root, "sources", "bridge-log.jsonl")
    if os.path.isdir(os.path.dirname(p)):
        open(p, "a", encoding="utf-8").write(json.dumps({"ts": datetime.now().isoformat(timespec="seconds"), "universes": names, "why": why, "query": query}) + "\n")


def self_test():
    """Fixture universes in a temp dir: contamination, unsourced, air-gap, canon-name, projection leak, ventriloquy."""
    import shutil, subprocess
    tmp = tempfile.mkdtemp(); sh = lambda *a: subprocess.run([sys.executable, __file__] + list(a), capture_output=True, text=True, env={**os.environ, "UNIVERSE_ROOT": tmp})
    try:
        os.makedirs(os.path.join(tmp, "sources"))
        reg = {"canon_denied_names_extra": ["zed corp"], "universes": {
            "acme": {"tier": "counterpart", "entities": ["acme", "pat"], "names": ["acme", "pat jones"], "anti_aliases": ["acme foods"], "shape": "an anvil manufacturer", "name_shapes": {"pat jones": "its founder"}, "audience_default": "internal",
                     "speakers": {"pat": "them", "zach": "me"}, "quote_sources": {"c1": "sources/c1.txt"}},
            "other": {"tier": "counterpart", "entities": ["other"], "names": ["othercorp"], "anti_aliases": [], "shape": None},
            "canon": {"tier": "canon", "readonly": True, "roots": ["_CANON"], "entities": ["adr"], "names": [], "anti_aliases": []}}}
        json.dump(reg, open(os.path.join(tmp, "_registry.json"), "w"))
        open(os.path.join(tmp, "sources", "c1.txt"), "w").write("Me: I ship code every single day and I love it.\nThem: We are hiring about ten engineers this quarter across the whole region.\n")
        W = lambda u, rows: open(os.path.join(tmp, f"{u}.claims.jsonl"), "w").write("".join(json.dumps(r) + "\n" for r in rows))
        base = {"entity": "acme", "type": "claim", "source": "s", "grade": "A", "verified_at": "2026-10-15", "ttl_days": 30, "tags": []}
        results = []
        def case(name, ok): results.append((name, ok)); print(("PASS " if ok else "FAIL ") + name)
        W("acme", [dict(base, id="acme/1", claim="Acme sells anvils.", audience="external")])
        case("clean universe loads", sh("--universe", "acme", "anvils").returncode == 0)
        W("acme", [dict(base, id="other/1", claim="x")]); r = sh("--universe", "acme", "x")
        case("foreign id prefix refused (CONTAMINATION)", r.returncode != 0 and "CONTAMINATION" in r.stderr)
        W("acme", [dict(base, id="acme/1", claim="x", source="")]); r = sh("--universe", "acme", "x")
        case("unsourced claim refused", "UNSOURCED" in r.stderr)
        W("acme", [dict(base, id="acme/1", claim="x", type="inference", grade="inference", audience="external")]); r = sh("--universe", "acme", "x")
        case("external inference refused (AIR-GAP)", "AIR-GAP" in r.stderr)
        W("acme", [dict(base, id="acme/1", claim="Acme sells anvils.", audience="external")]); r = sh("--universe", "acme", "--project", "public")
        case("public projection swaps the name for the client's shape", r.returncode == 0 and "an anvil manufacturer sells anvils." in r.stdout and "acme" not in r.stdout.lower())
        W("other", [dict(base, id="other/1", entity="other", claim="Othercorp ships.", audience="external")]); r = sh("--universe", "other", "--project", "public")
        case("projection refused without a shape", r.returncode != 0 and "no `shape`" in r.stderr)
        W("acme", [dict(base, id="acme/1", claim="Acme works with Othercorp.", audience="external")]); r = sh("--universe", "acme", "--project", "public")
        case("another universe's name surviving projection refused (LEAK)", r.returncode != 0 and "LEAK" in r.stderr)
        W("canon", [dict(base, id="canon/1", entity="adr", claim="Zed Corp validated this.", source="_CANON/x.md:1")]); r = sh("--universe", "canon", "x")
        case("counterpart name in canon refused", "COUNTERPART IN CANON" in r.stderr)
        W("canon", [dict(base, id="canon/1", entity="adr", claim="ok", source="elsewhere/x.md:1")]); r = sh("--universe", "canon", "ok")
        case("canon source outside roots refused", "outside the read-only roots" in r.stderr)
        q = dict(base, type="quote", grade="C", speaker="pat", source_ref="c1", audience="internal")
        W("acme", [dict(q, id="acme/1", claim="We are hiring about ten engineers this quarter across the whole region."),
                   dict(q, id="acme/2", claim="I ship code every single day and I love it."),
                   dict(q, id="acme/3", claim="The moon is made of reasonably aged cheddar and nobody told the board.")])
        r = sh("--universe", "acme", "--lint-quotes")
        case("quote lint: CLEAN / CONTAMINATED (Zach's words in Pat's mouth) / UNSOURCED",
             "acme/1 CLEAN" in r.stdout and "acme/2 CONTAMINATED" in r.stdout and "acme/3 UNSOURCED" in r.stdout and r.returncode == 2)
        os.environ["ARCS_KEY_PASS"] = "test-pass-not-real"
        pseud_tag("acme", tmp); t1 = pseud_tag("acme", tmp); seal_key(tmp)
        sealed_ok = os.path.exists(os.path.join(tmp, "sources", KEY_ENC)) and not os.path.exists(os.path.join(tmp, "sources", KEY_PLAIN)) and "acme" not in open(os.path.join(tmp, "sources", KEY_ENC), "rb").read().decode("latin-1")
        case("key sealed: ciphertext on disk, plaintext gone, tag stable after unseal", sealed_ok and pseud_tag("acme", tmp) == t1)
        open(os.path.join(tmp, "sources", KEY_ENC), "ab").write(b"x")
        r = subprocess.run([sys.executable, "-c", "import sys;sys.path.insert(0,%r);import universe_ask as u;u.pseud_tag('acme',%r)" % (HERE, tmp)], capture_output=True, text=True)
        case("tampered ciphertext fails the SHA-256 integrity check", "INTEGRITY" in r.stderr)
        os.environ.pop("ARCS_KEY_PASS", None)
        bad = [n for n, ok in results if not ok]
        print(f"self-test: {len(results) - len(bad)}/{len(results)} pass"); return 1 if bad else 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    global ROOT
    if os.environ.get("UNIVERSE_ROOT"):
        ROOT = os.environ["UNIVERSE_ROOT"]
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", nargs="?", default=""); ap.add_argument("-k", type=int, default=5)
    ap.add_argument("--universe")
    ap.add_argument("--bridge", help="comma list of other universes to include (explicit, logged)")
    ap.add_argument("--why", help="reason for bridging (required with --bridge)")
    ap.add_argument("--project", choices=["public"], help="emit only external-safe atoms, pseudonymised; fails closed")
    ap.add_argument("--lint-quotes", action="store_true", help="ADR-033 speaker check over this universe's quote atoms")
    ap.add_argument("--seal-key", action="store_true", help="AES-256/PBKDF2 encrypt the private pseudonym key with the backup passphrase")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.seal_key:
        return seal_key(ROOT) or 0
    if not a.universe:
        sys.exit("--universe is required: there is no wildcard search. Name the one universe you mean.")
    reg = load_registry(ROOT)
    if a.project or a.lint_quotes:
        rows = load(a.universe, reg, ROOT)
        if a.project:
            for r in project_public(a.universe, reg, rows, ROOT):
                print(f'{r["id"]} [{r["grade"]}] {r["claim"]}')
            return 0
        res = lint_quotes(a.universe, reg, rows, ROOT)
        for i, v, det in res:
            print(f"{i} {v}  {det}")
        return 2 if any(v in ("CONTAMINATED", "UNSOURCED") for _, v, _ in res) else 0
    names = [a.universe] + ([b for b in (a.bridge or "").split(",") if b])
    if len(names) > 1 and not a.why:
        sys.exit("--bridge needs --why: say why these universes may be read together.")
    if len(names) > 1:
        log_bridge(names, a.why, a.query, ROOT)
    q_low = a.query.lower()
    for other, d in reg["universes"].items():   # conflation warnings before any hit is shown
        if other in names: continue
        hit = find_names(q_low, d["names"] + d["anti_aliases"])
        if hit: print(f"WARN conflation risk: query mentions '{hit[0]}' which belongs to universe '{other}', not '{a.universe}'.", file=sys.stderr)
    for u in names:
        for n in find_names(q_low, reg["universes"].get(u, {}).get("anti_aliases", [])):
            print(f"WARN '{n}' is a known look-alike of {u}, NOT {u}: {reg['universes'][u].get('alias_notes','')}", file=sys.stderr)
    q = set(tok(a.query)); scored = []
    for u in names:
        rows = load(u, reg, ROOT)
        drifted = set(canon_drift(rows)) if reg["universes"][u].get("tier") == "canon" else set()
        for r in rows:
            tags = set(tok(" ".join(r.get("tags", [])))) | set(tok(r["entity"]))
            s = sum(1 for w in q if w in set(tok(r["claim"]))) + 2 * sum(1 for w in q if w in tags)
            if s: scored.append((s, u, r, r["id"] in drifted))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        print(f"NO HIT in universe(s) {','.join(names)}: nothing sourced; research it, then add an atom."); return 1
    for s, u, r, dr in scored[: a.k]:
        age = (date.today() - datetime.strptime(r["verified_at"], "%Y-%m-%d").date()).days
        flags = (" STALE" if age > r.get("ttl_days", 30) else "") + (" SOURCE-CHANGED" if dr else "")
        bridged = f" BRIDGED<-{u}" if u != a.universe else ""
        aud = "ext" if audience_of(r, reg, u) == "external" else "int"
        who = f" said:{r['speaker']}" if r["type"] == "quote" else ""
        print(f'{r["id"]} [{r["entity"]}|{r["grade"]}|{aud}{who}{flags}{bridged}] {r["claim"]}  <{r["source"] or "no source"}>')
    return 0

if __name__ == "__main__":
    sys.exit(main())
