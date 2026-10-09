// Reading-options matrix smoke test for the My Ally LD proposal page.
// Renders every combination of font x size x spacing x tone x theme at four widths
// and fails on: page errors, sideways scroll, a header that wraps instead of collapsing,
// a collapsed menu missing the plan stages, detail buttons that overflow or overlap,
// and a Reading options panel that opens under the sticky header.
// Run from the repo root (Playwright lives in the main checkout's node_modules):
//   NODE_PATH=/path/to/arcs-v9/node_modules node _ARTIFACTS/sow-scaffold-2026-10-08/reading_matrix.smoke.cjs public/myally.html
const path = require("path");
const { chromium } = require("playwright");

const file = "file://" + path.resolve(process.argv[2] || "public/myally.html");
const WIDTHS = [360, 768, 1024, 1440];
const OPTS = { font: ["std", "easy"], size: ["std", "l", "xl"], space: ["std", "roomy"], tone: ["std", "warm"] };
const THEMES = ["light", "dark"];

function combos() {
  const out = [];
  for (const font of OPTS.font) for (const size of OPTS.size) for (const space of OPTS.space)
    for (const tone of OPTS.tone) for (const theme of THEMES) out.push({ font, size, space, tone, theme });
  return out;
}

(async () => {
  const browser = await chromium.launch();
  const fails = [];
  let n = 0;
  for (const w of WIDTHS) {
    for (const c of combos()) {
      const ctx = await browser.newContext({ viewport: { width: w, height: 800 } });
      await ctx.addInitScript((c) => {
        try {
          localStorage.setItem("myAllyRead", JSON.stringify({ font: c.font, size: c.size, space: c.space, tone: c.tone }));
          localStorage.setItem("myAllyTheme", c.theme);
        } catch (e) {}
      }, c);
      const page = await ctx.newPage();
      const errs = [];
      page.on("pageerror", (e) => errs.push(String(e.message || e)));
      await page.goto(file);
      await page.waitForTimeout(250);
      const r = await page.evaluate(async () => {
        const d = document.documentElement, hd = document.querySelector("header.top"), bar = hd.querySelector(".bar");
        const res = { hscroll: d.scrollWidth > innerWidth + 1, collapsed: hd.classList.contains("collapsed") };
        res.barWraps = !res.collapsed && bar.getBoundingClientRect().height > 72;
        const t = [...document.querySelectorAll(".tname")];
        res.btnOverflow = t.some((b) => b.scrollWidth > b.clientWidth + 1 || b.getBoundingClientRect().right > innerWidth);
        res.btnOverlap = t.some((b, i) => t.some((o, j) => {
          if (i >= j) return false;
          const a = b.getBoundingClientRect(), q = o.getBoundingClientRect();
          return a.left < q.right - 1 && q.left < a.right - 1 && a.top < q.bottom - 1 && q.top < a.bottom - 1;
        }));
        if (res.collapsed) {
          document.getElementById("menubtn").click();
          await new Promise((r) => setTimeout(r, 50));
          const st = [...document.querySelectorAll(".mstages a")];
          res.menuStages = st.length === 4 && st.every((a) => a.offsetParent !== null);
          document.getElementById("menubtn").click();
        } else {
          const sub = [...hd.querySelectorAll(".sub a")];
          res.menuStages = sub.length === 4 && sub.every((a) => a.offsetParent !== null);
        }
        const fab = document.getElementById("readfab"), ro = document.getElementById("readopts");
        fab.click();
        await new Promise((r) => setTimeout(r, 50));
        res.panelClear = ro.getBoundingClientRect().top >= hd.getBoundingClientRect().bottom - 1;
        fab.click();
        return res;
      });
      const bad = [];
      if (errs.length) bad.push("pageerror: " + errs[0]);
      if (r.hscroll) bad.push("sideways scroll");
      if (r.barWraps) bad.push("header wraps");
      if (!r.menuStages) bad.push("plan stages missing from nav");
      if (r.btnOverflow) bad.push("detail button overflow");
      if (r.btnOverlap) bad.push("detail buttons overlap");
      if (!r.panelClear) bad.push("reading panel under header");
      if (bad.length) fails.push(`${w}px ${JSON.stringify(c)}: ${bad.join(", ")}`);
      n++;
      await ctx.close();
    }
  }
  await browser.close();
  console.log(`reading-matrix: ${n - fails.length}/${n} configurations pass`);
  for (const f of fails.slice(0, 40)) console.log("  FAIL " + f);
  process.exit(fails.length ? 1 : 0);
})();
