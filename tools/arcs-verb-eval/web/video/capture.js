// Frame-accurate capture of explainer.html: renderAt(t) per frame, then ffmpeg joins them.
// node capture.js            -> frames/00000.jpg ... at 30 fps
// node capture.js 2.5,8.5    -> still-2.5.png, still-8.5.png (layout check)
const { chromium } = require('/Users/zharris/arcs-v9/node_modules/playwright');
const path = require('path');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.join(__dirname, 'explainer.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(400);
  const fonts = await page.evaluate(() => [...document.fonts].filter((f) => f.status === 'loaded').map((f) => f.family));
  console.log('fonts loaded:', [...new Set(fonts)].join(', '));
  const stills = process.argv[2];
  if (stills) {
    for (const s of stills.split(',')) {
      await page.evaluate((t) => window.renderAt(t), +s);
      await page.screenshot({ path: path.join(__dirname, `still-${s}.png`) });
    }
  } else {
    const fps = 30, total = await page.evaluate(() => window.TOTAL), n = Math.round(total * fps);
    for (let f = 0; f < n; f++) {
      await page.evaluate((t) => window.renderAt(t), f / fps);
      await page.screenshot({ path: path.join(__dirname, 'frames', String(f).padStart(5, '0') + '.jpg'), type: 'jpeg', quality: 92 });
    }
    console.log('frames:', n);
  }
  await browser.close();
})();
