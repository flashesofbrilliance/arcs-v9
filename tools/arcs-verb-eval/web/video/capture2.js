/* eslint-disable @typescript-eslint/no-require-imports -- standalone Node script, not app code */
// Frame-accurate capture for recut.html (both formats).
// node capture2.js <src.html> <wide|square> stills 1.3,3.0     -> stills/<fmt>-<t>.png
// node capture2.js <src.html> <wide|square> frames <outdir>     -> <outdir>/00000.jpg ... at 30 fps
// node capture2.js <src.html> <wide|square> gates               -> JSON: size/lane/em-dash/rule gates
const { chromium } = require('/Users/zharris/arcs-v9/node_modules/playwright');
const path = require('path'), fs = require('fs');
const [src, fmt, mode, arg] = process.argv.slice(2);
const W = fmt === 'square' ? 1080 : 1920, H = 1080;
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve(src) + (fmt === 'square' ? '?fmt=square' : ''));
  await page.waitForFunction(() => window.READY === true, null, { timeout: 20000 });
  const fonts = await page.evaluate(() => ({
    inter: document.fonts.check('700 150px Inter'), mono: document.fonts.check('700 104px "JetBrains Mono"'),
    iowan: document.fonts.check('500 150px "Iowan Old Style"'),
  }));
  console.error('fonts:', JSON.stringify(fonts));
  if (mode === 'stills') {
    fs.mkdirSync(path.join(__dirname, 'stills'), { recursive: true });
    for (const s of arg.split(',')) {
      await page.evaluate((t) => window.renderAt(t), +s);
      await page.screenshot({ path: path.join(__dirname, 'stills', `${fmt}-${s}.png`) });
    }
  } else if (mode === 'frames') {
    fs.mkdirSync(arg, { recursive: true });
    const n = Math.round((await page.evaluate(() => window.TOTAL)) * 30);
    for (let f = 0; f < n; f++) {
      await page.evaluate((t) => window.renderAt(t), f / 30);
      await page.screenshot({ path: path.join(arg, String(f).padStart(5, '0') + '.jpg'), type: 'jpeg', quality: 94 });
    }
    console.error('frames:', n);
  } else if (mode === 'gates') {
    // sample every 0.25 s: every visible text node's computed size and box must pass
    const out = await page.evaluate(() => {
      const bad = [], seen = new Set();
      const g = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--g'));
      const W = document.getElementById('stage').clientWidth;
      for (let t = 0; t < window.TOTAL; t += 0.25) {
        window.renderAt(t);
        document.querySelectorAll('#stage *').forEach((el) => {
          if (el.closest('[data-mark]')) return; if (!el.childNodes.length || ![...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim())) return;
          const cs = getComputedStyle(el);
          let vis = true; for (let p = el; p && p.id !== 'stage'; p = p.parentElement) { const s = getComputedStyle(p); if (s.visibility === 'hidden' || s.display === 'none' || +s.opacity === 0) { vis = false; break; } }
          if (!vis) return;
          const txt = el.textContent.trim().slice(0, 40), fs = parseFloat(cs.fontSize);
          const r = el.getBoundingClientRect();
          const key = txt + '|' + fs;
          if (fs < 64 && !seen.has('size' + key)) { seen.add('size' + key); bad.push({ gate: 'size', t, txt, px: fs }); }
          // lane: judge untransformed layout only when no transform is in flight
          if (cs.transform === 'none' && (r.left < g - 2 || r.right > W - g + 2) && !seen.has('lane' + key)) { seen.add('lane' + key); bad.push({ gate: 'lane', t, txt, left: Math.round(r.left), right: Math.round(r.right) }); }
        });
      }
      const html = document.documentElement.outerHTML;
      const dashes = (html.match(/[–—]/g) || []).length;
      return { bad, dashes };
    });
    console.log(JSON.stringify(out, null, 1));
  }
  await browser.close();
})();
