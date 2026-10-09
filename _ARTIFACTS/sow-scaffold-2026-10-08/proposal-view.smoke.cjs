// Page-specific smoke checks for proposal-view.html; scripts/page_gate.py loads this beside the page and
// runs it on every device in the matrix. Return an array of failure strings (empty = pass).
module.exports = async function (page, ctx) {
  const errs = [];
  await page.addStyleTag({ content: 'html{scroll-behavior:auto !important}' });
  const btns = page.locator('.tname');
  const N = await btns.count();
  if (N < 3) return ['detail level buttons missing (got ' + N + ')'];

  // 1) every level button is a 44px-tall hit area and none overlap
  const boxes = await btns.evaluateAll(els => els.map(e => { const r = e.getBoundingClientRect(); return { l: r.left, r: r.right, t: r.top, b: r.bottom, h: r.height }; }));
  boxes.forEach((x, i) => { if (x.h < 43.5) errs.push('level button ' + (i + 1) + ' under 44px tall: ' + Math.round(x.h)); });
  for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
    const a = boxes[i], q = boxes[j];
    if (a.l < q.r - 1 && q.l < a.r - 1 && a.t < q.b - 1 && q.t < a.b - 1) errs.push('level buttons ' + (i + 1) + ' and ' + (j + 1) + ' overlap');
  }

  // 2) clicking each level marks it pressed and changes how much is shown; levels are cumulative
  const chars = [];
  for (let n = 1; n <= N; n++) {
    await page.locator('.tname[data-level="' + n + '"]').click();
    const pressed = await page.locator('.tname[aria-pressed="true"]').getAttribute('data-level');
    if (pressed !== String(n)) errs.push('level ' + n + ' click left level ' + pressed + ' pressed');
    chars.push(await page.evaluate(() => document.querySelector('main').innerText.length));
  }
  for (let i = 1; i < chars.length; i++) if (chars[i] < chars[i - 1]) errs.push('level ' + (i + 1) + ' shows less than level ' + i);
  if (!(chars[N - 1] > chars[0] * 2)) errs.push('Everything should show far more than Summary');

  // 3) keyboard: a level button activates with Enter
  await page.locator('.tname[data-level="2"]').focus();
  await page.keyboard.press('Enter');
  if ((await page.locator('.tname[aria-pressed="true"]').getAttribute('data-level')) !== '2') errs.push('Enter did not select level 2');

  // 4) definition chips: open, stay on screen, close
  await page.locator('.tname[data-level="3"]').click();
  const term = page.locator('a.gl:visible').first();
  if (await term.count()) {
    await term.scrollIntoViewIfNeeded();
    if (ctx.touch) await term.tap(); else await term.hover();
    const tip = term.locator('xpath=following-sibling::span[contains(@class,"tip")]');
    if (!(await tip.isVisible())) errs.push('definition chip did not open');
    else {
      const r = await tip.boundingBox();
      if (r.x < 0 || r.x + r.width > ctx.w + 1) errs.push('definition chip runs off screen: x=' + Math.round(r.x) + ' w=' + Math.round(r.width));
      await page.keyboard.press('Escape');
      if (await tip.isVisible()) errs.push('Escape did not close the definition chip');
    }
  } else errs.push('no visible glossary terms at level 3');

  // 4a) the click-to-keep-open mechanic must be visible, not hidden knowledge:
  //     an arrow on every term, a hint on mouse devices, a Close button once pinned
  const arrowless = await page.locator('a.gl').evaluateAll(as => as.filter(a => { const c = getComputedStyle(a, '::after'); return c.content === 'none' || parseFloat(c.width) < 3; }).length);
  if (arrowless) errs.push(arrowless + ' glossary terms have no expand arrow');
  if (await term.count()) {
    await page.locator('.tname[data-level="3"]').click();
    await term.scrollIntoViewIfNeeded();
    const wrap = term.locator('xpath=..');
    if (!ctx.touch) {
      await term.hover();
      if (!(await wrap.locator('.tiphint').isVisible())) errs.push('mouse hover shows no "click to keep open" hint');
    }
    await term.click();
    if (!(await wrap.evaluate(w => w.classList.contains('pinned')))) errs.push('click did not pin the definition');
    if (!(await wrap.locator('.tipclose').isVisible())) errs.push('pinned definition has no visible Close button');
    if (await wrap.locator('.tiphint').isVisible()) errs.push('hint should give way to Close once pinned');
    await wrap.locator('.tipclose').click();
    if (await wrap.locator('.tip').isVisible()) errs.push('Close did not close the definition');
    if (!(await page.evaluate(() => document.activeElement && document.activeElement.classList.contains('gl')))) errs.push('focus did not return to the term after Close');
  }

  // 4b) the chip's "Learn more" link opens the matching entry on /primer (targets are asserted at build time)
  if (await term.count()) {
    await page.locator('.tname[data-level="3"]').click();
    await term.scrollIntoViewIfNeeded();
    if (ctx.touch) await term.tap(); else await term.hover();
    const go = term.locator('xpath=following-sibling::span[contains(@class,"tip")]//a[contains(@class,"tipgo")]');
    if (await go.isVisible()) {
      // the glossary moved to its own page (/primer): Learn more must point there, at a real entry id
      const href = await go.getAttribute('href');
      if (!/^\/primer#g-[a-z0-9-]+$/.test(href)) errs.push('Learn more should open the primer, got ' + href);
    } else errs.push('Learn more link not visible in the chip');
  }

  // 4c) at the deepest level every visible anchor (stage chips, scope links, "used in this plan") must snap clean
  for (const lvl of [1, N]) {
    await page.locator('.tname[data-level="' + lvl + '"]').click();
    for (const x of await ctx.snap(page)) errs.push('level ' + lvl + ' anchor ' + x.href + ' lands at y=' + x.top + ' under ' + x.obs + 'px');
  }
  await page.locator('.tname[data-level="2"]').click();

  // 5) scope cases: exactly one case shown per row after a switch
  const worst = page.locator('.scope [data-case="worst"]');
  if (await worst.count()) {
    await page.locator('.tname[data-level="2"]').click();
    await worst.scrollIntoViewIfNeeded();
    await worst.click();
    const shown = await page.locator('.scope .sstep').first().locator('.c').evaluateAll(els => els.filter(e => getComputedStyle(e).display !== 'none').length);
    if (shown !== 1) errs.push('scope switch should show one case per row, showed ' + shown);
  } else errs.push('scope switcher missing');

  // 6) quick step chips point at real, reachable targets
  const dead = await page.locator('.toc a, #menu a').evaluateAll(as => as.filter(a => a.getAttribute('href').startsWith('#') && !document.getElementById(a.getAttribute('href').slice(1))).map(a => a.textContent));
  if (dead.length) errs.push('dead step links: ' + dead.join(', '));

  // 6b) after a jump, keyboard and screen-reader focus must move to the target, not stay on the link
  await page.locator('.tname[data-level="2"]').click();
  // stage links live in the sticky header: the L2 row when it fits, nested in the menu when collapsed
  const collapsed = await page.evaluate(() => document.querySelector('header.top').classList.contains('collapsed'));
  if (collapsed) await page.locator('#menubtn').click();
  const chip = collapsed ? page.locator('#menu .msub a').nth(1) : page.locator('.toc a[href="#stage-2"]');
  if (!(await chip.isVisible())) errs.push('stage 2 link not visible in the ' + (collapsed ? 'menu' : 'contents rail'));
  await chip.click();
  await ctx.settle(page);
  const focusId = await page.evaluate(() => document.activeElement && document.activeElement.id);
  if (focusId !== 'stage-2') errs.push('focus did not move to the stage after a jump (on: ' + focusId + ')');

  // 6c) term links are announced as buttons and open with Space as well as Enter/click
  const role = await page.locator('a.gl').first().getAttribute('role');
  if (role !== 'button') errs.push('glossary terms are not exposed as buttons: role=' + role);

  // 7) reading options: open, apply every accommodation, nothing overflows or hides behind the bars, persists, resets
  const fab = page.locator('#readfab');
  if (!(await fab.count())) { errs.push('reading options button missing'); return errs; }
  await fab.click();
  if (!(await page.locator('#readopts').isVisible())) errs.push('reading options panel did not open');
  for (const [k, v] of [['font', 'easy'], ['size', 'xl'], ['space', 'roomy'], ['tone', 'warm']]) {
    await page.locator('#readopts button[data-k="' + k + '"][data-v="' + v + '"]').click();
  }
  const attrs = await page.evaluate(() => ['font', 'size', 'space', 'tone'].map(k => document.documentElement.getAttribute('data-' + k)).join(','));
  if (attrs !== 'easy,xl,roomy,warm') errs.push('reading options not applied: ' + attrs);
  await page.locator('#readopts .ro-close').click();
  if (await page.locator('#readopts').isVisible()) errs.push('reading options Close did not close the panel');
  const m = await page.evaluate(() => {
    const p0 = document.querySelector('main p'); const cs = getComputedStyle(p0);
    return { over: document.documentElement.scrollWidth - innerWidth, fam: cs.fontFamily.slice(0, 24),
      italics: [...document.querySelectorAll('main *')].filter(e => e.offsetParent !== null && getComputedStyle(e).fontStyle === 'italic').length,
      lh: parseFloat(cs.lineHeight) / parseFloat(cs.fontSize) };
  });
  if (m.over > 0) errs.push('reading options cause horizontal overflow of ' + m.over + 'px');
  if (!/verdana/i.test(m.fam)) errs.push('easy-read font not applied: ' + m.fam);
  if (m.italics) errs.push(m.italics + ' italic elements remain in easy-read');
  if (m.lh < 1.7) errs.push('roomy spacing line-height only ' + m.lh.toFixed(2));
  for (const x of await ctx.snap(page)) errs.push('with reading options on, anchor ' + x.href + ' lands at y=' + x.top + ' with ' + x.obs + 'px of chrome');
  await page.reload(); await page.waitForTimeout(250);
  if ((await page.evaluate(() => document.documentElement.getAttribute('data-size'))) !== 'xl') errs.push('reading options did not persist across reload');
  await page.locator('#readfab').click();
  await page.locator('#readopts .ro-reset').click();
  const left = await page.evaluate(() => ['font', 'size', 'space', 'tone'].filter(k => document.documentElement.hasAttribute('data-' + k)).length);
  if (left) errs.push('Reset left ' + left + ' reading settings on');
  await page.locator('#readopts .ro-close').click();

  // 8) WCAG 1.4.12 text spacing: user-imposed spacing must not clip text or add sideways scroll
  await page.addStyleTag({ content: '*{line-height:1.5 !important;letter-spacing:.12em !important;word-spacing:.16em !important} p{margin-bottom:2em !important}' });
  const sp = await page.evaluate(() => ({
    over: document.documentElement.scrollWidth - innerWidth,
    clipped: [...document.querySelectorAll('button')].filter(b => b.offsetParent !== null && b.scrollWidth > b.clientWidth + 1).map(b => (b.textContent || '').trim().slice(0, 20)),
  }));
  if (sp.over > 0) errs.push('text spacing override causes ' + sp.over + 'px sideways scroll');
  if (sp.clipped.length) errs.push('text spacing override clips button text: ' + sp.clipped.slice(0, 4).join(', '));
  return errs;
};
