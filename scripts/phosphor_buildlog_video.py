#!/usr/bin/env python3
"""phosphor_buildlog_video: assemble _PROPOSALS/video/phosphor-buildlog/video.html from the template, the kit tokens (verbatim, sentinel kept) and the receipts snapshot (data.json).
Render: node scripts/html_video_render.mjs _PROPOSALS/video/phosphor-buildlog/video.html <out.mp4> --poster 3
Stdlib only. Never edit video.html by hand; edit video.tpl.html or refresh data.json."""
import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(R, "_PROPOSALS/video/phosphor-buildlog")
tok = open(os.path.join(R, "src/ui-kit/recoil-report/_tokens.css"), encoding="utf-8").read()
tpl = open(os.path.join(D, "video.tpl.html"), encoding="utf-8").read()
data = json.load(open(os.path.join(D, "data.json"), encoding="utf-8"))
assert "/*__TOKENS__*/" in tpl and "/*__DATA__*/null" in tpl
out = tpl.replace("/*__TOKENS__*/", tok).replace("/*__DATA__*/null", json.dumps(data))
open(os.path.join(D, "video.html"), "w", encoding="utf-8").write(out)
print("wrote video.html", len(out), "bytes")
