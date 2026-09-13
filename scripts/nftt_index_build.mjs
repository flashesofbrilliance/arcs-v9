#!/usr/bin/env node
/**
 * nftt_index_build.mjs — single source of truth for the "Notes from the Trenches" index.
 *
 * WHY THIS EXISTS
 *   The index is an every.to-style modular landing page: a featured lead, image grids for the
 *   art-bearing posts, and a compact archive for the text-only ones, grouped into thematic
 *   sections. Zach can rearrange it visually from the page itself (drag-and-drop) at
 *   good.arcs.care/blog/nftt?edit=1 — that editor exports a layout.json which this script
 *   consumes to regenerate the static HTML. The reader view is always fully static (SEO-safe);
 *   the editor never persists to readers on its own. Export -> commit -> live.
 *
 * PUBLISH FLOW (after editing on ?edit=1)
 *   1. In edit mode, click "Export layout", save the JSON as scripts/nftt_index_layout.json
 *   2. node scripts/nftt_index_build.mjs        # regenerates public/blog-nftt-index.html
 *   3. commit both files
 *
 * No em-dashes anywhere (repo gate). No new dependencies (native drag-and-drop, stdlib only).
 */
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');
const OUT = join(ROOT, 'public', 'blog-nftt-index.html');
const LAYOUT_OVERRIDE = join(__dirname, 'nftt_index_layout.json');

// ---- hero images (only 4 distinct files exist; reused across 7 posts) --------------------
const IMG = {
  instinct: '/blog-nftt-the-instinct-before-it-had-a-name-hero.jpg',
  method:   '/blog-nftt-the-method-that-was-already-built-hero.jpg',
  closing:  '/blog-nftt-closing-the-loop-receipts-hero.jpg',
  tuning:   '/blog-nftt-tuning-into-the-distortion-field-hero.jpg',
};

// ---- POSTS: the content model (single source of truth) -----------------------------------
const POSTS = {
  'post-1': { href: '/blog/nftt/post-1', title: `The week my notes started filing themselves`,
    desc: `A corpus that learned to catalog itself, from cold DM to witnessed law.` },
  'post-2': { href: '/blog/nftt/post-2', title: `The week my own memory tried to make me lie to a friend`,
    desc: `A featherlight respark, a memory caught lying by the record, and provenance-led growth.` },
  'post-3': { href: '/blog/nftt/post-3', title: `The names were already there. We just could not say them yet.`,
    desc: `Seven vision films made from the corpus foreshadowed the product; the words for it arrived eight months later.` },
  'post-4': { href: '/blog/nftt/post-4', title: `The detector's first catch was the document it was built to protect`,
    desc: `A recurring bug becomes a gate, a misattribution becomes a named pathogen, and the first true positive lands on its own canon.` },
  'take-home-trap': { href: '/blog/nftt/take-home-trap', title: `With Life, and Without It`,
    desc: `Two recruiters called an hour apart. One of them had no one home. A field account of the morning a DPRK threat vector called, and the tell that came before any analysis.` },
  'confirmed-not-my-bug': { href: '/blog/nftt/confirmed-not-my-bug', title: `Confirmed Not My Bug`,
    desc: `We pointed an audit harness at real decisions and it turned around and audited its author. An independent strand then caught the false receipt the self-audit could not see.` },
  'assets-and-liabilities': { href: '/blog/nftt/assets-and-liabilities', title: `Assets and Liabilities`,
    desc: `A system that only counts what it built is keeping half a book. The week the liability side opened, and the fourteen false receipts it booked against itself.` },
  'cheapest-edit-is-a-diff': { href: '/blog/nftt/cheapest-edit-is-a-diff', title: `The Cheapest Edit Is a Diff`,
    desc: `Chasing token efficiency, I built a worker to edit a resume instead of forging each one fresh. It timed out, and the timeout taught the real lesson: pay for the delta, not the document.` },
  'the-loop-closes': { href: '/blog/nftt/the-loop-closes', title: `The Loop Closes`,
    desc: `I built a job-search machine one tool at a time. The event was not any single worker. It was the last connection, when the tools became a circuit that runs itself for cents a morning.` },
  'the-factory-on-itself': { href: '/blog/nftt/the-factory-on-itself', title: `The Factory on Itself`,
    desc: `The tool that stamps these field notes wrote one about itself: it had drifted from the site it serves, carried a false proof-of-life in its own docs, and had to retire its own engine to close the gap. The audit, one turn further, now writing its own retirement.` },
  'probably-confirmation-bias': { href: '/blog/nftt/probably-confirmation-bias', title: `Probably Confirmation Bias, Might Delete Later`,
    desc: `I turned a flattering hunch about myself into a decision record and a map you could orbit, then noticed the one thing confirmation bias can never do: hand you the list of things that would prove it wrong.` },
  'schematic-scaffolds': { href: '/blog/nftt/schematic-scaffolds', title: `The Schematic That Scaffolds In The Missing Pieces`,
    desc: `I sat down to draw a picture of a system I had already built. The empty boxes in the diagram turned out to be the missing pieces, and naming them was the same act as building them. A schematic that scaffolds a territory instead of describing one.` },
  'ledger-not-story': { href: '/blog/nftt/ledger-not-story', title: `The Ledger Is Not the Story`,
    desc: `I built a record of every job application that ended this year. The outcome was knowable in all thirty-eight cases. The reason was knowable in one. An account of holding those two facts at their proper distance, in a spreadsheet and then in a production deploy.` },
  'pulp-governance': { href: '/blog/nftt/pulp-governance', title: `The Ancestry Check`,
    desc: `A rule was written. A pull request made a smaller promise than its own diff. Both looked finished until the record was asked a rude question.` },
  'second-pass': { href: '/blog/nftt/second-pass', title: `The Second Pass`,
    desc: `An audit script does not judge whether a claim is acceptable. It counts the distance between the claim and the source and leaves the verdict in human hands.` },
  'the-instinct-before-it-had-a-name': { href: '/blog/nftt/the-instinct-before-it-had-a-name', title: `The Instinct Before It Had a Name`,
    desc: `Two pieces, six years apart, no shared vocabulary, and the same cognitive reflex both times. The instinct was native; the framework only made it legible to other people.`,
    img: IMG.instinct, alt: `A luminous Mobius surface, the instinct seen before it had a name.` },
  'four-dates-one-thesis-three-confirmations': { href: '/blog/nftt/four-dates-one-thesis-three-confirmations', title: `Four Dates, One Thesis, Three Confirmations`,
    desc: `A dated Apple thesis read as a Bayesian ledger, not six hot takes. Three predictions resolved against the public record, including the one margin figure I had wrong and corrected in the open.`,
    img: IMG.closing, alt: `A luminous Mobius figure-eight closing on itself, the prediction loop resolving into receipt.` },
  'the-pre-mortem-that-asked-to-be-wrong': { href: '/blog/nftt/the-pre-mortem-that-asked-to-be-wrong', title: `The Pre-Mortem That Asked to Be Wrong`,
    desc: `Institutional-crypto plumbing written as proactive risk disclosure: name the specific mechanism, then state plainly what evidence would prove the thesis wrong.`,
    img: IMG.instinct, alt: `A luminous Mobius surface from a new vantage, the same circuit read with the opposite sign.` },
  'the-same-rigor-applied-to-slang': { href: '/blog/nftt/the-same-rigor-applied-to-slang', title: `The Same Rigor, Applied to Slang`,
    desc: `Holding a Gen-Z phrase to the identical standard as a custody clause. The range between sacred and absurd subject matter is the actual evidence for a way of seeing, not a trick fit to one domain.`,
    img: IMG.method, alt: `A luminous Mobius traversal from another orientation, the same instrument turned to a new bench.` },
  'the-method-that-was-already-built': { href: '/blog/nftt/the-method-that-was-already-built', title: `The Method That Was Already Built`,
    desc: `Eight months before a mechanized pipeline existed, the pipeline was already named and dated in prose. The plain fact, stated once, and what the ordering implies.`,
    img: IMG.method, alt: `A luminous Mobius traversal, the method that was already built.` },
  'closing-the-loop-receipts': { href: '/blog/nftt/closing-the-loop-receipts', title: `Closing the Loop: Receipts on Three Predictions`,
    desc: `Three predictions with their falsifiers stated in advance, checked against primary sources, the Q3 tariff caveat disclosed, and the one figure I got wrong corrected on the record.`,
    img: IMG.closing, alt: `A luminous Mobius figure-eight drawing tight, the same loop seen as it closes.` },
  'tuning-into-the-distortion-field': { href: '/blog/nftt/tuning-into-the-distortion-field', title: `Tuning into the Distortion Field`,
    desc: `A distortion field is not a spell, it is force, and force leaves a wave. Reading Apple's canceled car by its recoil: the Q.ai sensor bet, the succession, and the margin, read as one serialized prediction ledger.`,
    img: IMG.tuning, alt: `A composite portrait dissolving into a distortion field, force leaving a wave.` },
};

// ---- SECTIONS + default LAYOUT (overridable by nftt_index_layout.json) --------------------
const DEFAULT_SECTIONS = [
  { id: 'apple-ledger', label: 'The Apple Ledger', blurb: 'A serialized prediction loop, read by its recoil.' },
  { id: 'factory',      label: 'The Factory on Itself', blurb: 'The build turning its instruments on its own record.' },
  { id: 'field',        label: 'Field Accounts', blurb: 'Dispatches from the morning it actually happened.' },
];
const DEFAULT_LAYOUT = [
  { slug: 'tuning-into-the-distortion-field', section: 'apple-ledger', view: 'featured' },
  { slug: 'closing-the-loop-receipts', section: 'apple-ledger', view: 'grid' },
  { slug: 'four-dates-one-thesis-three-confirmations', section: 'apple-ledger', view: 'grid' },
  { slug: 'the-pre-mortem-that-asked-to-be-wrong', section: 'apple-ledger', view: 'grid' },
  { slug: 'the-same-rigor-applied-to-slang', section: 'apple-ledger', view: 'grid' },
  { slug: 'the-method-that-was-already-built', section: 'apple-ledger', view: 'grid' },
  { slug: 'the-instinct-before-it-had-a-name', section: 'apple-ledger', view: 'grid' },
  { slug: 'the-factory-on-itself', section: 'factory', view: 'compact' },
  { slug: 'the-loop-closes', section: 'factory', view: 'compact' },
  { slug: 'confirmed-not-my-bug', section: 'factory', view: 'compact' },
  { slug: 'assets-and-liabilities', section: 'factory', view: 'compact' },
  { slug: 'second-pass', section: 'factory', view: 'compact' },
  { slug: 'pulp-governance', section: 'factory', view: 'compact' },
  { slug: 'schematic-scaffolds', section: 'factory', view: 'compact' },
  { slug: 'cheapest-edit-is-a-diff', section: 'factory', view: 'compact' },
  { slug: 'ledger-not-story', section: 'factory', view: 'compact' },
  { slug: 'probably-confirmation-bias', section: 'factory', view: 'compact' },
  { slug: 'post-4', section: 'field', view: 'compact' },
  { slug: 'post-3', section: 'field', view: 'compact' },
  { slug: 'post-2', section: 'field', view: 'compact' },
  { slug: 'post-1', section: 'field', view: 'compact' },
  { slug: 'take-home-trap', section: 'field', view: 'compact' },
];

let SECTIONS = DEFAULT_SECTIONS, LAYOUT = DEFAULT_LAYOUT;
if (existsSync(LAYOUT_OVERRIDE)) {
  try {
    const o = JSON.parse(readFileSync(LAYOUT_OVERRIDE, 'utf8'));
    if (Array.isArray(o.sections) && o.sections.length) SECTIONS = o.sections;
    if (Array.isArray(o.items) && o.items.length) LAYOUT = o.items;
    console.log(`[nftt-index] using layout override: ${LAYOUT_OVERRIDE}`);
  } catch (e) { console.warn(`[nftt-index] layout override ignored (${e.message}); using defaults`); }
}

// ---- render helpers ----------------------------------------------------------------------
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const READ = 'Read &#8594;';

function featuredCard(p) {
  const img = p.img ? `<img src="${p.img}" alt="${esc(p.alt || p.title)}" loading="lazy" width="1280" height="853">` : '';
  return `<a class="feat" href="${p.href}">
      <div class="feat-img">${img}</div>
      <div class="feat-body">
        <span class="feat-k">Latest dispatch</span>
        <h2 class="feat-t">${esc(p.title)}</h2>
        <p class="feat-d">${esc(p.desc)}</p>
        <span class="r">${READ}</span>
      </div>
    </a>`;
}
function gridCard(p) {
  const img = p.img ? `<div class="card-img"><img src="${p.img}" alt="${esc(p.alt || p.title)}" loading="lazy" width="1280" height="853"></div>` : '';
  return `<a class="card${p.img ? '' : ' card-noimg'}" href="${p.href}">
        ${img}
        <div class="card-body">
          <h3 class="card-t">${esc(p.title)}</h3>
          <p class="card-d">${esc(p.desc)}</p>
          <span class="r">${READ}</span>
        </div>
      </a>`;
}
function compactRow(p) {
  return `<a class="crow" href="${p.href}">
        <h3 class="crow-t">${esc(p.title)}</h3>
        <p class="crow-d">${esc(p.desc)}</p>
        <span class="crow-r">${READ}</span>
      </a>`;
}

function renderReader(sections, layout, posts) {
  return sections.map((sec) => {
    const list = layout.filter((i) => i.section === sec.id && posts[i.slug]);
    if (!list.length) return '';
    const feats = list.filter((i) => i.view === 'featured');
    const grids = list.filter((i) => i.view === 'grid');
    const comps = list.filter((i) => i.view === 'compact');
    const parts = [];
    parts.push(`  <section class="sec">
    <div class="sec-h">
      <span class="sec-tag">${esc(sec.label)}</span>
      <span class="sec-blurb">${esc(sec.blurb || '')}</span>
      <span class="sec-rule"></span>
    </div>`);
    feats.forEach((i) => parts.push('    ' + featuredCard(posts[i.slug])));
    if (grids.length) parts.push(`    <div class="grid">\n      ${grids.map((i) => gridCard(posts[i.slug])).join('\n      ')}\n    </div>`);
    if (comps.length) parts.push(`    <div class="clist">\n      ${comps.map((i) => compactRow(posts[i.slug])).join('\n      ')}\n    </div>`);
    parts.push('  </section>');
    return parts.join('\n');
  }).filter(Boolean).join('\n');
}

// ---- in-page editor (runs only in the browser; .toString()'d into the page, never called in Node) ----
function editorMain() {
  var params = new URLSearchParams(location.search);
  if (params.get('edit') !== '1' && location.hash !== '#edit') return;
  var dataEl = document.getElementById('nftt-data');
  if (!dataEl) return;
  var data = JSON.parse(dataEl.textContent);
  var POSTS = data.posts, SECTIONS = data.sections, DEFAULT = data.layout;
  var VIEWS = ['featured', 'grid', 'compact'];
  var LS = 'nftt-layout-draft-v1';
  var items = loadDraft() || DEFAULT.map(function (x) { return { slug: x.slug, section: x.section, view: x.view }; });
  var dragging = null;

  function loadDraft() { try { var s = localStorage.getItem(LS); return s ? JSON.parse(s) : null; } catch (e) { return null; } }
  function saveDraft() { try { localStorage.setItem(LS, JSON.stringify(items)); } catch (e) {} }

  document.body.classList.add('nftt-edit');
  var main = document.querySelector('main');
  main.innerHTML = '<div class="wrap"><div id="ezmount"></div></div>';
  var mount = document.getElementById('ezmount');

  var bar = document.createElement('div');
  bar.className = 'ezbar';
  bar.innerHTML = '<span class="ezbar-t">Edit mode</span>'
    + '<button class="ezbtn" id="ezExport">Export layout</button>'
    + '<button class="ezbtn ezbtn-ghost" id="ezReset">Reset to committed</button>'
    + '<a class="ezbtn ezbtn-ghost" href="' + location.pathname + '">Exit</a>';
  document.body.appendChild(bar);

  function chipAfter(zone, y) {
    var chips = [].slice.call(zone.querySelectorAll('.ezchip:not(.dragging)'));
    for (var i = 0; i < chips.length; i++) {
      var r = chips[i].getBoundingClientRect();
      if (y < r.top + r.height / 2) return chips[i].dataset.slug;
    }
    return null;
  }
  function move(it, section, beforeSlug) {
    items = items.filter(function (x) { return x !== it; });
    it.section = section;
    if (beforeSlug) {
      var idx = items.findIndex(function (x) { return x.slug === beforeSlug; });
      items.splice(idx < 0 ? items.length : idx, 0, it);
    } else {
      var last = -1;
      items.forEach(function (x, i) { if (x.section === section) last = i; });
      if (last >= 0) items.splice(last + 1, 0, it); else items.push(it);
    }
  }

  function render() {
    mount.innerHTML = '';
    SECTIONS.forEach(function (sec) {
      var zone = document.createElement('div');
      zone.className = 'ezzone';
      zone.dataset.section = sec.id;
      var h = document.createElement('div');
      h.className = 'ezzone-h';
      h.textContent = sec.label;
      zone.appendChild(h);
      items.filter(function (i) { return i.section === sec.id; }).forEach(function (it) {
        var p = POSTS[it.slug] || { title: it.slug };
        var chip = document.createElement('div');
        chip.className = 'ezchip' + (p.img ? ' has-img' : '');
        chip.draggable = true;
        chip.dataset.slug = it.slug;
        var vb = document.createElement('button');
        vb.className = 'ezview ezview-' + it.view;
        vb.type = 'button';
        vb.title = 'cycle view (featured / grid / compact)';
        vb.textContent = it.view.charAt(0).toUpperCase();
        vb.addEventListener('click', function (e) {
          e.stopPropagation();
          it.view = VIEWS[(VIEWS.indexOf(it.view) + 1) % VIEWS.length];
          saveDraft(); render();
        });
        var t = document.createElement('span');
        t.className = 'ezchip-t';
        t.textContent = p.title;
        chip.appendChild(vb); chip.appendChild(t);
        chip.addEventListener('dragstart', function (e) { dragging = it; chip.classList.add('dragging'); e.dataTransfer.effectAllowed = 'move'; });
        chip.addEventListener('dragend', function () { chip.classList.remove('dragging'); dragging = null; });
        zone.appendChild(chip);
      });
      zone.addEventListener('dragover', function (e) { e.preventDefault(); zone.classList.add('over'); });
      zone.addEventListener('dragleave', function () { zone.classList.remove('over'); });
      zone.addEventListener('drop', function (e) {
        e.preventDefault(); zone.classList.remove('over');
        if (!dragging) return;
        move(dragging, sec.id, chipAfter(zone, e.clientY));
        saveDraft(); render();
      });
      mount.appendChild(zone);
    });
  }

  document.getElementById('ezReset').addEventListener('click', function () {
    try { localStorage.removeItem(LS); } catch (e) {}
    items = DEFAULT.map(function (x) { return { slug: x.slug, section: x.section, view: x.view }; });
    render();
  });
  document.getElementById('ezExport').addEventListener('click', function () {
    var payload = { sections: SECTIONS, items: items.map(function (i) { return { slug: i.slug, section: i.section, view: i.view }; }) };
    var json = JSON.stringify(payload, null, 2);
    var ov = document.createElement('div');
    ov.className = 'ezoverlay';
    ov.innerHTML = '<div class="ezmodal">'
      + '<h3>Export layout</h3>'
      + '<p>Save this as <code>scripts/nftt_index_layout.json</code>, then run <code>node scripts/nftt_index_build.mjs</code> and commit. That regenerates the static page for all readers.</p>'
      + '<textarea readonly></textarea>'
      + '<div class="ezmodal-row"><button class="ezbtn" id="ezCopy">Copy JSON</button>'
      + '<button class="ezbtn" id="ezDownload">Download file</button>'
      + '<button class="ezbtn ezbtn-ghost" id="ezClose">Close</button></div></div>';
    document.body.appendChild(ov);
    var ta = ov.querySelector('textarea');
    ta.value = json;
    ov.querySelector('#ezCopy').addEventListener('click', function () { ta.select(); try { document.execCommand('copy'); } catch (e) {} });
    ov.querySelector('#ezDownload').addEventListener('click', function () {
      var blob = new Blob([json], { type: 'application/json' });
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob); a.download = 'nftt_index_layout.json'; a.click();
      setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
    });
    ov.querySelector('#ezClose').addEventListener('click', function () { ov.remove(); });
    ov.addEventListener('click', function (e) { if (e.target === ov) ov.remove(); });
  });

  render();
}

// ---- page template -----------------------------------------------------------------------
const readerHTML = renderReader(SECTIONS, LAYOUT, POSTS);
const embedData = JSON.stringify({ sections: SECTIONS, layout: LAYOUT, posts: POSTS });
const editorJS = '(' + editorMain.toString() + ')();';
const OG_IMG = 'https://good.arcs.care' + IMG.tuning;

const page = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Notes from the Trenches &middot; ARCS</title>
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="description" content="Notes from the Trenches: what building ARCS in the open actually taught me. Real stories from the build, with the receipts.">
<meta property="og:type" content="website">
<meta property="og:title" content="Notes from the Trenches">
<meta property="og:description" content="What building ARCS in the open actually taught me. Real stories from the build, with the receipts.">
<meta property="og:image" content="${OG_IMG}">
<meta property="og:url" content="https://good.arcs.care/blog/nftt">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Notes from the Trenches">
<meta name="twitter:description" content="What building ARCS in the open actually taught me. Real stories from the build, with the receipts.">
<meta name="twitter:image" content="${OG_IMG}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Newsreader:ital,opsz,wght@0,6..72,500;0,6..72,600;1,6..72,500&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root{--bg:#020408;--elev:#0b111a;--elev2:#0e141d;--surface-2:#0a0f16;--border:#1e2c3a;--border2:#26374a;
    --fg1:#eff4fa;--fg2:#c6d3e1;--fg3:#a3b4c6;--fg4:#7e8fa4;--cyan:#00F0FF;--green:#00FF9D;
    --sans:'Inter',system-ui,-apple-system,sans-serif;--serif:'Newsreader',Georgia,serif;--mono:'JetBrains Mono',ui-monospace,monospace;}
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
  html{background:var(--bg);color:var(--fg1);font-family:var(--sans);-webkit-font-smoothing:antialiased;overflow-x:clip;}
  body{overflow-x:clip;}
  a{color:inherit;text-decoration:none;}
  img{display:block;max-width:100%;}
  .wrap{max-width:1080px;margin:0 auto;padding:0 24px;}
  header{border-bottom:1px solid var(--border);background:radial-gradient(900px 460px at 12% -12%,rgba(0,240,255,.10),transparent 60%);}
  .hero{padding-block:64px 40px;}
  .kick{display:inline-flex;align-items:center;gap:9px;font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--cyan);border:1px solid rgba(0,240,255,.35);border-radius:999px;padding:6px 13px;}
  .kick .dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 10px var(--green);}
  h1{font-size:clamp(38px,6.4vw,62px);font-weight:800;letter-spacing:-.03em;line-height:1;margin-top:22px;text-wrap:balance;}
  h1 .g{background:linear-gradient(100deg,var(--cyan),var(--green));-webkit-background-clip:text;background-clip:text;color:transparent;}
  .lede{font-size:clamp(15px,2.1vw,19px);line-height:1.6;color:var(--fg2);margin-top:18px;max-width:none;text-wrap:pretty;}
  main{padding:20px 0 40px;}

  /* section */
  .sec{margin-top:52px;}
  .sec:first-child{margin-top:34px;}
  .sec-h{display:flex;align-items:center;gap:16px;margin-bottom:22px;}
  .sec-tag{font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--cyan);white-space:nowrap;}
  .sec-blurb{font-size:13px;color:var(--fg4);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  .sec-rule{flex:1;height:1px;background:linear-gradient(90deg,var(--border2),transparent);}

  /* shared read affordance */
  .r{font-family:var(--mono);font-size:10.5px;font-weight:600;color:var(--cyan);margin-top:14px;display:inline-block;}

  /* featured */
  .feat{display:grid;grid-template-columns:1.12fr .88fr;border:1px solid var(--border);border-radius:18px;overflow:hidden;
    background:linear-gradient(165deg,rgba(255,255,255,.025),rgba(0,0,0,.18));transition:.18s;}
  .feat:hover{border-color:var(--cyan);transform:translateY(-2px);}
  .feat-img{position:relative;min-height:260px;background:var(--surface-2);}
  .feat-img img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;}
  .feat-body{padding:34px 34px 30px;display:flex;flex-direction:column;justify-content:center;}
  .feat-k{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--green);}
  .feat-t{font-family:var(--serif);font-size:clamp(24px,3.4vw,34px);font-weight:600;letter-spacing:-.01em;line-height:1.1;margin-top:12px;text-wrap:balance;}
  .feat:hover .feat-t{color:var(--cyan);}
  .feat-d{font-size:15px;line-height:1.62;color:var(--fg3);margin-top:14px;text-wrap:pretty;}

  /* grid */
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:18px;}
  .card{display:flex;flex-direction:column;border:1px solid var(--border);border-radius:15px;overflow:hidden;
    background:linear-gradient(165deg,rgba(255,255,255,.02),rgba(0,0,0,.16));transition:.16s;}
  .card:hover{border-color:var(--cyan);transform:translateY(-2px);}
  .card-img{aspect-ratio:16/10;background:var(--surface-2);border-bottom:1px solid var(--border);overflow:hidden;}
  .card-img img{width:100%;height:100%;object-fit:cover;transition:.3s;}
  .card:hover .card-img img{transform:scale(1.03);}
  .card-body{padding:18px 18px 18px;display:flex;flex-direction:column;flex:1;}
  .card-t{font-family:var(--serif);font-size:19px;font-weight:600;letter-spacing:-.005em;line-height:1.2;text-wrap:balance;
    display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
  .card:hover .card-t{color:var(--cyan);}
  .card-d{font-size:13px;line-height:1.55;color:var(--fg3);margin-top:9px;text-wrap:pretty;
    display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;}
  .card .r{margin-top:auto;padding-top:12px;}

  /* compact archive */
  .clist{display:grid;grid-template-columns:1fr 1fr;gap:14px;}
  .crow{border:1px solid var(--border);border-radius:12px;padding:18px 18px 16px;
    background:linear-gradient(165deg,rgba(255,255,255,.015),rgba(0,0,0,.12));transition:.15s;}
  .crow:hover{border-color:var(--cyan);transform:translateY(-1px);}
  .crow-t{font-family:var(--serif);font-size:17px;font-weight:600;line-height:1.22;letter-spacing:-.005em;text-wrap:balance;
    display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
  .crow:hover .crow-t{color:var(--cyan);}
  .crow-d{font-size:12.5px;line-height:1.5;color:var(--fg4);margin-top:7px;text-wrap:pretty;
    display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
  .crow-r{font-family:var(--mono);font-size:10px;font-weight:600;color:var(--cyan);margin-top:11px;display:inline-block;opacity:0;transition:.15s;}
  .crow:hover .crow-r{opacity:1;}

  footer{border-top:1px solid var(--border);padding:26px 0 46px;margin-top:44px;}
  .foot{font-family:var(--mono);font-size:11px;color:var(--fg4);letter-spacing:.04em;} .foot a{color:var(--fg3);} .foot a:hover{color:var(--cyan);}

  @media(max-width:760px){
    .feat{grid-template-columns:1fr;} .feat-img{min-height:200px;aspect-ratio:16/10;}
    .clist{grid-template-columns:1fr;}
    .sec-blurb{display:none;}
  }

  /* ---- editor (only visible under body.nftt-edit) ---- */
  .ezbar{position:fixed;left:0;right:0;bottom:0;z-index:50;display:flex;align-items:center;gap:12px;
    padding:12px 20px;background:rgba(6,10,16,.94);border-top:1px solid var(--border2);backdrop-filter:blur(8px);}
  .ezbar-t{font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--green);}
  .ezbtn{font-family:var(--mono);font-size:12px;font-weight:700;color:#001014;background:linear-gradient(100deg,var(--cyan),var(--green));
    border:none;border-radius:9px;padding:9px 15px;cursor:pointer;text-decoration:none;}
  .ezbtn:hover{transform:translateY(-1px);}
  .ezbtn-ghost{background:transparent;color:var(--fg3);border:1px solid var(--border2);}
  .nftt-edit main{padding-bottom:90px;}
  .ezzone{border:1px dashed var(--border2);border-radius:14px;padding:14px;margin-top:16px;transition:.12s;}
  .ezzone.over{border-color:var(--cyan);background:rgba(0,240,255,.04);}
  .ezzone-h{font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--cyan);margin-bottom:10px;}
  .ezchip{display:flex;align-items:center;gap:11px;border:1px solid var(--border);border-radius:10px;padding:10px 12px;margin-bottom:8px;
    background:var(--elev2);cursor:grab;}
  .ezchip.has-img{border-left:3px solid var(--green);}
  .ezchip.dragging{opacity:.4;}
  .ezchip-t{font-size:13.5px;color:var(--fg2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
  .ezview{width:24px;height:24px;flex:0 0 auto;border-radius:6px;border:1px solid var(--border2);background:var(--surface-2);
    font-family:var(--mono);font-size:11px;font-weight:700;cursor:pointer;color:var(--fg3);}
  .ezview-featured{color:#001014;background:var(--green);border-color:var(--green);}
  .ezview-grid{color:#001014;background:var(--cyan);border-color:var(--cyan);}
  .ezview-compact{color:var(--fg3);}
  .ezoverlay{position:fixed;inset:0;z-index:60;display:flex;align-items:center;justify-content:center;background:rgba(2,4,8,.7);padding:24px;}
  .ezmodal{width:min(680px,100%);background:var(--elev2);border:1px solid var(--border2);border-radius:16px;padding:24px;}
  .ezmodal h3{font-size:18px;font-weight:800;}
  .ezmodal p{font-size:13px;color:var(--fg3);line-height:1.6;margin-top:8px;} .ezmodal code{font-family:var(--mono);color:var(--cyan);font-size:12px;}
  .ezmodal textarea{width:100%;height:240px;margin-top:14px;background:var(--bg);border:1px solid var(--border);border-radius:10px;
    color:var(--fg2);font-family:var(--mono);font-size:11.5px;line-height:1.5;padding:12px;resize:vertical;}
  .ezmodal-row{display:flex;gap:10px;margin-top:14px;}
</style>
<script defer src="/_vercel/insights/script.js"></script>
</head>
<body>
<header>
  <div class="wrap hero">
    <span class="kick"><span class="dot"></span>good.arcs.care &middot; field notes</span>
    <h1>Notes from the <span class="g">Trenches</span></h1>
    <p class="lede">What building ARCS in the open actually taught me. Each post is a real story from the build, with the receipts.</p>
  </div>
</header>
<main>
  <div class="wrap">
${readerHTML}
  </div>
</main>
<style>
  /* ADR-076 MCP-led-growth demand probe (Stage 0, painted door). Honest framing: the connector
     does not exist yet; the CTA click is the interest signal, tracked via Vercel custom events. */
  .mcp-probe{padding:36px 0 44px;}
  .mp-card{border:1px solid rgba(0,240,255,.28);border-radius:16px;padding:26px 26px 24px;max-width:1080px;margin:0 auto;
    background:radial-gradient(700px 300px at 12% -30%,rgba(0,240,255,.08),transparent 60%),linear-gradient(165deg,rgba(255,255,255,.02),rgba(0,0,0,.16));}
  .mp-eyebrow{display:inline-flex;align-items:center;gap:8px;font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--cyan);}
  .mp-dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 10px var(--green);}
  .mp-h{font-size:clamp(19px,3vw,25px);font-weight:800;letter-spacing:-.02em;line-height:1.2;margin-top:12px;color:var(--fg1);text-wrap:balance;}
  .mp-b{font-size:14.5px;line-height:1.6;color:var(--fg2);margin-top:11px;max-width:none;text-wrap:pretty;} .mp-b b{color:var(--fg1);font-weight:600;}
  .mp-cta{margin-top:18px;font-family:var(--mono);font-size:13px;font-weight:700;letter-spacing:.03em;color:#001014;background:linear-gradient(100deg,var(--cyan),var(--green));border:none;border-radius:10px;padding:12px 20px;cursor:pointer;transition:transform .15s;}
  .mp-cta:hover{transform:translateY(-1px);}
  .mp-cta:focus-visible{outline:2px solid var(--cyan);outline-offset:3px;}
  .mp-done{font-size:13.5px;line-height:1.6;color:var(--fg3);margin-top:16px;max-width:none;} .mp-done a{color:var(--cyan);}
</style>
<section class="mcp-probe" aria-label="Connect an agent (demand probe)">
  <div class="wrap">
    <div class="mp-card">
      <div class="mp-eyebrow"><span class="mp-dot"></span>Connect an agent &middot; considering this</div>
      <h2 class="mp-h">Query these field notes from your AI tools</h2>
      <p class="mp-b">We are weighing an ARCS connector for Claude, Cursor, and other agents: ask about anything in these notes and get an answer that <b>cites its source, not a guess</b>. It does not exist yet. This is a live demand probe, so if you would use it, say so and we will build it.</p>
      <button class="mp-cta" id="mpCta" type="button">I'd use this &#8594;</button>
      <p class="mp-done" id="mpDone" hidden>Noted, thank you. Enough signal and we ship the connector. In the meantime the underlying tools are open at <a href="https://github.com/flashesofbrilliance/arcs-skills">github.com/flashesofbrilliance/arcs-skills</a>.</p>
    </div>
  </div>
</section>
<script id="nftt-data" type="application/json">${embedData}</script>
<script>
  /* Vercel Web Analytics custom events; guarded so the page is fine if analytics is blocked. */
  (function(){
    function ev(name){ try{ window.va && window.va('event', { name: name, data: { surface: 'nftt' } }); }catch(e){} }
    var card = document.querySelector('.mcp-probe');
    if (card && 'IntersectionObserver' in window){
      var seen = false;
      var io = new IntersectionObserver(function(entries){
        entries.forEach(function(en){ if(en.isIntersecting && !seen){ seen = true; ev('mcp_probe_view'); io.disconnect(); } });
      }, { threshold: 0.4 });
      io.observe(card);
    }
    /* Owned record alongside the Vercel event: POST /api/probe (our table, deduped by a random
       visitor id kept in this browser; survives blockers that eat /_vercel/insights). */
    var ls = { get:function(k){ try{ return localStorage.getItem(k) }catch(e){ return null } }, set:function(k,v){ try{ localStorage.setItem(k,v) }catch(e){} } };
    var vid = ls.get('arcs_vid');
    if (!vid){ vid = 'v-' + Math.random().toString(36).slice(2,10) + '-' + Date.now().toString(36); ls.set('arcs_vid', vid); }
    function own(action){
      try{ fetch('/api/probe', { method:'POST', keepalive:true, headers:{ 'content-type':'application/json' },
        body: JSON.stringify({ probe:'mcp-connector', action:action, surface:'nftt', vid:vid, path:location.pathname }) }).catch(function(){}); }catch(e){}
    }
    var cta = document.getElementById('mpCta'), done = document.getElementById('mpDone');
    function markDone(){ if(done){ done.hidden = false; } if(cta){ cta.disabled = true; cta.style.opacity = '.55'; cta.style.cursor = 'default'; } }
    if (ls.get('mp_voted_mcp-connector')){ markDone(); }
    if (card && !sessionStorage.getItem('mp_viewed')){ try{ sessionStorage.setItem('mp_viewed','1') }catch(e){}; own('view'); }
    if (cta){ cta.addEventListener('click', function(){ ev('mcp_probe_interest'); own('interest'); ls.set('mp_voted_mcp-connector','1'); markDone(); }); }
  })();
</script>
<script>${editorJS}</script>
<footer>
  <div class="wrap foot"><a href="https://good.arcs.care/">&#9664; good.arcs.care</a> &middot; open-source tools and field notes by ARCS</div>
</footer>
</body>
</html>
`;

writeFileSync(OUT, page);
console.log(`[nftt-index] wrote ${OUT} (${SECTIONS.length} sections, ${LAYOUT.length} posts, ${page.length} bytes)`);
