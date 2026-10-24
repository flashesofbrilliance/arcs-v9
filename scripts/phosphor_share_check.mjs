#!/usr/bin/env node
// phosphor_share_check.mjs: the recipe link (amendment 64). A recipe travels as a link: moves and actions only, never the song; opened links wait for a press and are checked field by field. Usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_share_check.mjs <page.html>
import { chromium } from 'playwright'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
import { check, failed } from './lib/phosphor_check_lib.mjs'
const page = process.argv[2], file = path.basename((process.env.PHOSPHOR_FILES || '').split(',')[0])
if (!page || !file) { console.log('usage: PHOSPHOR_FILES=break-100.wav node scripts/phosphor_share_check.mjs <page.html>'); process.exit(2) }
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }), errs = []
const ctx = await b.newContext({ viewport: { width: 1270, height: 990 } }); await ctx.addInitScript(() => { try { localStorage.setItem('phosphor.consent.v1', '1') } catch (e) {} })
const base = pathToFileURL(path.resolve(page)).href + '?test=1&shutter=off&level=4'
const open = async (hash) => { const pg = await ctx.newPage(); pg.on('pageerror', (e) => errs.push(String(e))); await pg.goto(base + (hash || '')); await pg.waitForFunction(() => document.getElementById('status').textContent === ''); await pg.setInputFiles('input[type=file]', '/private/tmp/claude-501/fx/' + file); await pg.waitForTimeout(2500); await pg.evaluate(() => document.querySelectorAll('details').forEach((d) => d.open = true)); return pg }
const set = (pg, id, v) => pg.evaluate(([id, v]) => { const e = document.getElementById(id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })) }, [id, v])
const p1 = await open()
await p1.evaluate(() => window.PhosphorTest.seek(0)); await p1.click('#play'); await set(p1, 'gamt', 20); await p1.waitForTimeout(400); await set(p1, 'gamt', 70); await p1.evaluate(() => window.PhosphorTest.hold.on('echo', 'latch', true)); await p1.waitForTimeout(500); await p1.evaluate(() => window.PhosphorTest.hold.on('echo', 'latch', false)); await p1.waitForTimeout(400); await p1.click('#play'); await p1.waitForTimeout(300)
const text = await p1.evaluate(() => window.PhosphorTest.recipe.exp()), evs = JSON.parse(text.split('\n').slice(1).join('\n')).events
const link = await p1.evaluate(() => window.PhosphorTest.recipe.link()), hash = link.slice(link.indexOf('#'))
const payload = await p1.evaluate(async (h) => { const s = atob(h.slice(3).replace(/-/g, '+').replace(/_/g, '/')), u = Uint8Array.from(s, (c) => c.charCodeAt(0)); return new TextDecoder().decode(new Uint8Array(await new Response(new Blob([u]).stream().pipeThrough(new DecompressionStream('deflate-raw'))).arrayBuffer())) }, hash)
check(/#r=[A-Za-z0-9_-]+$/.test(link) && link.length < 8000 && !payload.includes(file) && !/\.wav|\.mp3|data:audio/i.test(payload) && !link.includes('?'), `S1: the link is the page address plus one hash of ${link.length} characters, and holds no song and no file name (payload ${payload.length} bytes)`)
// S2 round trip on a fresh page: waits for a press, then holds the same events
const p2 = await open(hash)
const pend = await p2.evaluate(() => ({ msg: document.getElementById('rnsum').textContent, load: !document.getElementById('rload').hidden, shared: window.PhosphorTest.recipe.shared() }))
check(/carries a recipe of \d+ events/.test(pend.msg) && pend.load && pend.shared === null, `S2: an opened link only offers to load: "${pend.msg.slice(0, 60)}", nothing applied yet`)
await p2.click('#rload'); await p2.waitForTimeout(200)
const dbg = await p2.evaluate(() => document.getElementById('rnsum').textContent); const got = await p2.evaluate(() => window.PhosphorTest.recipe.shared()); if (!got) { console.log('DEBUG', dbg, errs); process.exit(1) } const gev = JSON.parse(got.split('\n').slice(1).join('\n')).events
check(gev.length === evs.length && JSON.stringify(gev) === JSON.stringify(evs), `S3: Load holds the same ${gev.length} events that were shared`)
// S4 rendering the shared recipe equals rendering the original on the same song
const h = (pg, t) => pg.evaluate(async (t) => { const o = await window.PhosphorTest.recipe.render(t); let x = 2166136261; for (let i = 0; i < o.l.length; i += 5) { x ^= Math.round(o.l[i] * 32767) & 0xffff; x = Math.imul(x, 16777619) >>> 0 } return x + ':' + o.l.length }, t)
const [ha, hb] = [await h(p2, got), await h(p2, text)]; check(ha === hb, `S4: the shared recipe renders the same as the original (${ha} and ${hb})`)
// S5 hostile payloads: bad ids and unknown actions dropped; non-recipes refused
const hostile = await p2.evaluate(async () => {
  const z = async (t) => { const c = await new Response(new Blob([new TextEncoder().encode(t)]).stream().pipeThrough(new CompressionStream('deflate-raw'))).arrayBuffer(), u = new Uint8Array(c); let s = ''; u.forEach((x) => s += String.fromCharCode(x)); return '#r=' + btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '') }
  const mix = await z(JSON.stringify({ base: { 'x"]': 1, gamt: 40 }, events: [[10, null, 'gamt', 55], [20, null, 'x"] , a[b="', 1], [30, null, '@evil', 1], [40, null, 'nosuchcontrol', 5], [50, null, '@fx', ['echo', 'latch', 1]]] }))
  const r = await window.PhosphorTest.recipe.open(mix); let rej = 0; for (const t of ['hello', JSON.stringify({ a: 1 })]) { try { await window.PhosphorTest.recipe.open(await z(t)) } catch (e) { rej++ } } try { await window.PhosphorTest.recipe.open('#r=' + 'A'.repeat(9000)) } catch (e) { rej++ }
  return { n: r.events.length, ids: r.events.map((e) => e[2]).join(), dropped: r.dropped, base: Object.keys(r.base).join(), rej }
})
check(hostile.ids === 'gamt,@fx' && hostile.dropped === 3 && hostile.base === 'gamt' && hostile.rej === 3, `S5: unsafe fields are dropped and non-recipes refused (kept ${hostile.ids}, dropped ${hostile.dropped}, base ${hostile.base}, refused ${hostile.rej} of 3)`)
// S6 drop returns to the own session; S7 too long to share is refused with a message
await p2.evaluate(() => document.getElementById('rdrop').click()); check((await p2.evaluate(() => window.PhosphorTest.recipe.shared())) === null, 'S6: Drop shared recipe returns to your own session')
await p1.evaluate(() => { for (let i = 0; i < 7000; i++) window.PhosphorTest.recipe.act('fx', ['echo', 'latch', Math.floor(Math.random() * 1e9)]) }); await p1.evaluate(() => document.getElementById('rlink').click()); await p1.waitForTimeout(600)
const long = await p1.evaluate(() => document.getElementById('rnsum').textContent); check(/too long to fit in a link/.test(long), `S7: a session too long for a link says so (${long.slice(0, 50)})`)
check(errs.length === 0, 'S8: no page errors ' + errs.join('|'))
await b.close(); process.exit(failed() ? 1 : 0)
