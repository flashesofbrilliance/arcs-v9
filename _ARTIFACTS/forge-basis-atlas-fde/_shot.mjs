import { chromium } from '/Users/zharris/arcs-v9/node_modules/playwright/index.mjs';
import path from 'path';

const HERE = path.dirname(new URL(import.meta.url).pathname);
const widths = [375, 768, 790, 1280];

const browser = await chromium.launch();
for (const w of widths) {
  const page = await browser.newPage({ viewport: { width: w, height: 1000 } });
  await page.goto('file://' + path.join(HERE, 'page.html'));
  await page.waitForTimeout(300);
  const bodyWidth = await page.evaluate(() => document.documentElement.scrollWidth);
  const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
  await page.screenshot({ path: path.join(HERE, `forge-shot-${w}.png`), fullPage: true });
  console.log(`width=${w} scrollWidth=${bodyWidth} clientWidth=${clientWidth} overflow=${bodyWidth > clientWidth}`);
  await page.close();
}
await browser.close();
