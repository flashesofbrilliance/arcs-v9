#!/usr/bin/env python3
"""video_cut: one shot spec -> (a) an HTML scene for html_video_render.mjs, (b) a prompt pack.

The `video` cut type for the LinkedIn cut format (scripts/linkedin_cut.py). A spec lives in
_QUEUE/video/<id>.json: a source (essay or Tao proverb), a thesis, and beats. Each beat carries
the on-screen caption (what the HTML scene renders, word for word) and a shot (what an external
video model is asked to make: subject, camera, motion, light). Two outputs from one spec:

  scene   _PROPOSALS/video/<id>-<16x9|9x16>.html  window.DURATION + window.seek(t), every frame a
          pure function of t. Palette read from src/ui-kit/recoil-report/_tokens.css at build
          time (never copied). Render: node scripts/html_video_render.mjs <html> <mp4> --w --h
  prompts _PROPOSALS/video/<id>-prompts.md        one block per beat per aspect: prompt, camera,
          motion, duration, negative prompt. Paste into whichever model; captions are NOT in the
          prompt (models garble text), they are burned in afterward from the scene.

Honest scope: this writes render code and prompts. It does not generate video pixels. The HTML
scene is the fully controlled, on-brand path; the prompt pack is the generative path, and its
output still has to be watched before it ships.

Gates (any miss exits 1), the same as essays via linkedin_cut: slop_lint (cliches + em-dashes),
provenance_lint (every metric covered by the spec's evidence), PII grep, plus shape: 3-8 beats,
beat 1.5-8s, total 6-60s, caption <= 14 words, every shot field present, aspects in {16:9, 9:16}.

Usage:
  python3 scripts/video_cut.py check [_QUEUE/video/*.json]
  python3 scripts/video_cut.py build <spec.json> [--out _PROPOSALS/video]
  python3 scripts/video_cut.py --self-test
Stdlib only.
"""
import glob, html, json, os, re, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import linkedin_cut as lc  # noqa: E402  (reuse the essay gates, do not fork them)

ROOT = lc.ROOT
QUEUE = os.path.join(ROOT, "_QUEUE", "video")
OUT = os.path.join(ROOT, "_PROPOSALS", "video")
TOKENS = os.path.join(ROOT, "src", "ui-kit", "recoil-report", "_tokens.css")
MONO = os.path.join(ROOT, "public", "fonts", "jetbrains-mono-normal-100-800-latin-v1.woff2")
SANS = os.path.join(ROOT, "public", "fonts", "inter-normal-100-900-latin-v1.woff2")
ASPECTS = {"16:9": (1280, 720, "16x9"), "9:16": (720, 1280, "9x16")}
SHOT_FIELDS = ("subject", "camera", "motion", "light")
ACCENTS = ("cyan", "green", "gold", "red")
NEGATIVE = ("on-screen text, letters, captions, logos, watermarks, faces in close-up, hands with "
            "extra fingers, stock-footage office scenes, glossy 3D render look, lens flare, "
            "saturated neon overload, fast cuts, shaky handheld")


def tokens():
    """Palette from the kit (single source). Fails loudly if the kit moved."""
    css = open(TOKENS).read()
    t = dict(re.findall(r"--([\w-]+):\s*([^;]+);", css))
    need = ["bg", "surface", "border", "text", "dimmed", *ACCENTS]
    missing = [k for k in need if k not in t]
    if missing: raise SystemExit(f"video_cut: tokens missing from {TOKENS}: {missing}")
    return {k: t[k].strip() for k in need}


def spec_text(s):
    return "\n\n".join([s.get("thesis", "")] + [b.get("caption", "") for b in s.get("beats", [])])


def shape_errors(s):
    e = []
    for k in ("id", "source", "thesis", "beats", "aspects"):
        if not s.get(k): e.append(f"missing {k}")
    bad = [a for a in s.get("aspects", []) if a not in ASPECTS]
    if bad: e.append(f"unknown aspect(s) {bad}; want {list(ASPECTS)}")
    beats = s.get("beats", [])
    if not 3 <= len(beats) <= 8: e.append(f"{len(beats)} beats (want 3-8)")
    total = 0.0
    for i, b in enumerate(beats, 1):
        d = b.get("duration", 0); total += d
        if not 1.5 <= d <= 8: e.append(f"beat {i} duration {d}s (want 1.5-8)")
        if not b.get("caption") or lc.words(b["caption"]) > 14: e.append(f"beat {i} caption missing or > 14 words")
        miss = [f for f in SHOT_FIELDS if not (b.get("shot") or {}).get(f)]
        if miss: e.append(f"beat {i} shot missing {miss}")
        if b.get("accent", "cyan") not in ACCENTS: e.append(f"beat {i} accent not a kit signal color")
    if beats and not 6 <= total <= 60: e.append(f"total {total:.1f}s (want 6-60)")
    return e


def check_file(path):
    s = json.load(open(path))
    errs = shape_errors(s)
    text = spec_text(s)
    errs += [f"PII-shaped string: {m.group(0)}" for r in lc.PII for m in r.finditer(text)]
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "evidence.jsonl"), "w").write(
            "".join(json.dumps(ev) + "\n" for ev in s.get("evidence", [])))
        fp = os.path.join(d, "video.txt"); open(fp, "w").write(text)
        for script in ("slop_lint.py", "provenance_lint.py"):
            rc, out = lc.run(script, fp)
            if rc: errs.append(f"{script}: {out.splitlines()[-1] if out else 'fail'}")
    return errs


SCENE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<!--
  Generated by scripts/video_cut.py from {spec}. Do not hand-edit: change the spec and rebuild.
  Render: node scripts/html_video_render.mjs {self} out.mp4 --w {w} --h {h} --fps 30
-->
<style>
@font-face{{font-family:'JetBrains Mono';font-weight:100 800;src:url('{mono}') format('woff2')}}
@font-face{{font-family:'Inter';font-weight:100 900;src:url('{sans}') format('woff2')}}
:root{{{vars}}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:100%;height:100%;overflow:hidden;background:var(--bg)}}
#stage{{position:absolute;left:0;top:0;width:{w}px;height:{h}px;overflow:hidden;transform-origin:0 0}}
body{{font-family:'Inter','InstrumentSans','Work Sans',system-ui,sans-serif;color:var(--text)}}
#grid{{position:absolute;inset:0;background-image:linear-gradient(var(--border) 1px,transparent 1px),linear-gradient(90deg,var(--border) 1px,transparent 1px);background-size:{cell}px {cell}px;opacity:.35}}
#fog{{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 55%,transparent 20%,var(--bg) 75%)}}
#rule{{position:absolute;left:{pad}px;height:2px;top:{rule_y}px;width:0}}
#cap{{position:absolute;left:{pad}px;right:{pad}px;top:{cap_y}px;font-size:{fs}px;line-height:1.18;font-weight:500;letter-spacing:-.01em}}
#tag{{position:absolute;left:{pad}px;bottom:{pad}px;font-family:'GeistMono','JetBrains Mono',monospace;font-size:{ts}px;color:var(--dimmed);letter-spacing:.08em;text-transform:uppercase}}
#bar{{position:absolute;left:0;bottom:0;height:3px;background:var(--border);width:100%}}
#bar i{{display:block;height:100%;width:0}}
</style></head><body>
<div id="stage"><div id="grid"></div><div id="fog"></div><div id="rule"></div>
<div id="cap"></div><div id="tag">{tag}</div><div id="bar"><i></i></div></div>
<script>
const BEATS = {beats};
window.DURATION = BEATS.reduce((a, b) => a + b.d, 0);
const $ = (id) => document.getElementById(id);
const ease = (x) => 1 - Math.pow(1 - Math.min(Math.max(x, 0), 1), 3);
window.seek = function (t) {{
  let s = 0, i = 0;
  while (i < BEATS.length - 1 && t >= s + BEATS[i].d) {{ s += BEATS[i].d; i++; }}
  const b = BEATS[i], u = (t - s) / b.d, c = `var(--${{b.accent}})`;
  const fin = ease(u / 0.18), fout = i === BEATS.length - 1 ? 1 : 1 - ease((u - 0.86) / 0.14);
  const cap = $('cap');
  if (cap.dataset.i !== String(i)) {{ cap.textContent = b.caption; cap.dataset.i = String(i); }}
  cap.style.opacity = (fin * fout).toFixed(3);
  cap.style.transform = `translateY(${{((1 - fin) * 18).toFixed(2)}}px)`;
  $('rule').style.background = c;
  $('rule').style.width = `${{(ease(u / 0.35) * {rule_w}).toFixed(1)}}px`;
  $('grid').style.transform = `translateY(${{(-t * 6).toFixed(2)}}px)`;
  $('bar').firstElementChild.style.background = c;
  $('bar').firstElementChild.style.width = `${{(t / window.DURATION * 100).toFixed(2)}}%`;
}};
// Fit the fixed frame to the viewport: scale 1 at the render size, a preview anywhere else.
const fit = () => {{ $('stage').style.transform = `scale(${{Math.min(innerWidth / {w}, innerHeight / {h}, 1)}})`; }};
addEventListener('resize', fit); fit();
window.seek(0);
</script></body></html>
"""


def scene(s, aspect, spec_rel, self_rel):
    w, h, _ = ASPECTS[aspect]
    tall = h > w
    tk = tokens()
    beats = [dict(d=b["duration"], caption=b["caption"], accent=b.get("accent", "cyan")) for b in s["beats"]]
    return SCENE.format(
        title=html.escape(s.get("title", s["id"])), spec=spec_rel, self=self_rel, w=w, h=h,
        vars="".join(f"--{k}:{v};" for k, v in tk.items()),
        cell=48 if tall else 64, pad=72 if tall else 96, fs=68 if tall else 64, ts=18 if tall else 16,
        rule_y=int(h * (0.36 if tall else 0.30)), cap_y=int(h * (0.36 if tall else 0.30)) + 28,
        rule_w=160 if tall else 220, tag=html.escape(s.get("tag", "")),
        beats=json.dumps(beats, ensure_ascii=False),
        mono=os.path.relpath(MONO, os.path.dirname(os.path.join(ROOT, self_rel))),
        sans=os.path.relpath(SANS, os.path.dirname(os.path.join(ROOT, self_rel))))


def prompt_pack(s):
    tk = tokens()
    pal = ", ".join(f"{k} {tk[k]}" for k in ("bg", "surface", "cyan", "green", "gold"))
    L = [f"# Prompt pack: {s.get('title', s['id'])}", "",
         f"Source: `{s['source']}`. Generated by `scripts/video_cut.py`; edit the spec, not this file.", "",
         "How to use: one generation per beat per aspect. Captions are not in the prompts on purpose",
         "(video models garble text); burn them in afterward from the HTML scene, or composite over it.",
         "Watch every clip before it ships: a prompt is a request, not a result.", "",
         f"Global style (append to every prompt): {s.get('style', '')} Palette: {pal}.", "",
         f"Negative prompt (every beat): {NEGATIVE}.", ""]
    for i, b in enumerate(s["beats"], 1):
        sh = b["shot"]
        L += [f"## Beat {i} ({b['duration']}s): \"{b['caption']}\"", ""]
        for a in s["aspects"]:
            frame = "vertical 9:16, subject centered, safe area top and bottom" if a == "9:16" \
                else "horizontal 16:9, subject on the left third, open space right"
            L += [f"**{a}**", "", "```",
                  f"{sh['subject']}. Camera: {sh['camera']}. Motion: {sh['motion']}. Light: {sh['light']}. "
                  f"Framing: {frame}. Duration {b['duration']} seconds, one continuous shot. "
                  f"{s.get('style', '')}", "```", ""]
    return "\n".join(L)


def build(path, out=OUT):
    errs = check_file(path)
    if errs:
        print(f"[FAIL] {path}"); [print(f"   - {e}") for e in errs]; return 1
    s = json.load(open(path))
    os.makedirs(out, exist_ok=True)
    spec_rel = os.path.relpath(os.path.abspath(path), ROOT)
    for a in s["aspects"]:
        fp = os.path.join(out, f"{s['id']}-{ASPECTS[a][2]}.html")
        open(fp, "w").write(scene(s, a, spec_rel, os.path.relpath(fp, ROOT)))
        print(f"wrote {os.path.relpath(fp, ROOT)}  ({ASPECTS[a][0]}x{ASPECTS[a][1]})")
    fp = os.path.join(out, f"{s['id']}-prompts.md")
    open(fp, "w").write(prompt_pack(s))
    print(f"wrote {os.path.relpath(fp, ROOT)}")
    return 0


def cmd_check(paths):
    bad = 0
    for p in paths or sorted(glob.glob(os.path.join(QUEUE, "*.json"))):
        errs = check_file(p)
        print(f"[{'FAIL' if errs else 'PASS'}] {os.path.relpath(p, ROOT)}")
        for e in errs: print(f"   - {e}")
        bad += bool(errs)
    return 1 if bad else 0


def self_test():
    good = sorted(glob.glob(os.path.join(QUEUE, "*.json")))
    assert good, "no video specs to test against"
    assert not check_file(good[0]), f"good fixture should pass: {check_file(good[0])}"
    s = json.load(open(good[0]))
    html_out = scene(s, "9:16", "x", "y")
    assert "window.seek" in html_out and tokens()["cyan"] in html_out and "\u2014" not in html_out
    assert "\u2014" not in prompt_pack(s)
    assert os.path.exists(MONO) and "jetbrains-mono" in html_out, "tag font must load from public/fonts"
    assert os.path.exists(SANS) and "inter-normal" in html_out, "caption font must load from public/fonts"
    muts = {
        "em-dash": lambda m: m["beats"][0].__setitem__("caption", m["beats"][0]["caption"] + " \u2014 x"),
        "uncited metric": lambda m: m["beats"][1].__setitem__("caption", "It grew 87%."),
        "PII": lambda m: m["beats"][1].__setitem__("caption", "write me at a@b.co"),
        "long caption": lambda m: m["beats"][0].__setitem__("caption", "word " * 15),
        "no camera": lambda m: m["beats"][0]["shot"].pop("camera"),
        "bad aspect": lambda m: m.__setitem__("aspects", ["4:3"]),
        "too short": lambda m: m.__setitem__("beats", m["beats"][:2]),
    }
    with tempfile.TemporaryDirectory() as d:
        for name, mut in muts.items():
            m = json.loads(json.dumps(s)); mut(m)
            fp = os.path.join(d, "t.json"); json.dump(m, open(fp, "w"))
            assert check_file(fp), f"mutation '{name}' should fail"
            print(f"  fail-on-bad ok: {name}")
    print("video_cut self-test: PASS"); return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--self-test"]: sys.exit(self_test())
    if a[:1] == ["check"]: sys.exit(cmd_check(a[1:]))
    if a[:1] == ["build"] and len(a) in (2, 4) and (len(a) == 2 or a[2] == "--out"):
        sys.exit(build(a[1], a[3] if len(a) == 4 else OUT))
    print(__doc__); sys.exit(2)
