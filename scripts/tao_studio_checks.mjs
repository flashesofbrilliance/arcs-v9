#!/usr/bin/env node
/**
 * tao_studio_checks.mjs: the pre-registered checks for the Tao print studio's Drive, AnalysisFrame and key map, run headless.
 *
 *   node scripts/tao_studio_checks.mjs drive|frame|slice2|realtime|probe|offline [--phosphor path/to/phosphor.html]
 *
 *   drive   D1-D8   _PATTERNS/2026-10-18-studio-drive-prereg.md        (audio features move the print controls)
 *   frame   F1-F7   _PATTERNS/2026-10-18-analysis-frame-v1.md          (needs a Phosphor build that has window.PhosphorFrame for F2)
 *   slice2  S1-S8   _PATTERNS/2026-10-18-studio-drive-slice2-prereg.md (stutter, flash limiter, key map)
 *   offline O1-O7   _PATTERNS/2026-10-18-studio-offline-renderer-prereg.md (frame-exact video render in four shapes with audio; needs ffmpeg, ffprobe, python3 with PIL; renders for a minute or two)
 *   probe           median ms to draw one 1920x1080 frame of each look from SVG to canvas, with and without embedded fonts (the realtime cost basis)
 *   realtime R1-R8  _PATTERNS/2026-10-18-studio-realtime-frames-prereg.md (responsive frames, adaptive quality, live capture; needs ffmpeg and ffprobe)
 *
 * Opens _ARTIFACTS/tao-print-studio.html with Playwright (repo node_modules or global). Needs python3 with PIL for the luminance checks (D4, S2).
 * Writes scratch files to $TAO_TMP or the system temp directory. Prints one JSON object; read the pass fields. Local only, no network.
 */
import { createRequire } from 'node:module'
import { execFileSync } from 'node:child_process'
import { existsSync, mkdirSync, writeFileSync, readFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'

const req = createRequire(import.meta.url)
let chromiumLib = null
for (const base of [process.cwd(), execFileSync('npm', ['root', '-g']).toString().trim()]) { try { chromiumLib = req(req.resolve('playwright', { paths: [base] })); break } catch {} }
if (!chromiumLib) { console.error('Playwright not found (repo node_modules or global).'); process.exit(3) }
const { chromium } = chromiumLib
const fs = { writeFileSync, readFileSync, existsSync, mkdirSync }
const SP = process.env.TAO_TMP || join(tmpdir(), 'tao-studio-checks'); mkdirSync(SP, { recursive: true })
const args = process.argv.slice(2), which = args[0], pi = args.indexOf('--phosphor')
const PHOSPHOR = resolve(pi >= 0 ? args[pi + 1] : '_ARTIFACTS/phosphor.html')
const dec = (b64, n) => { const b = Buffer.from(b64, 'base64'); if (n !== undefined && b.length !== n) throw new Error('len ' + b.length + ' != ' + n); return b }
function writeFixtureWav(path) {          // deterministic 10 s, 16-bit mono 22,050 Hz: kick, hats, bass, pad at 120 BPM
  const sr = 22050, n = sr * 10, pcm = Buffer.alloc(n * 2); let seed = 12345, prev = 0; const notes = [55, 55, 73.4, 65.4]
  const rnd = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647 * 2 - 1 }
  for (let i = 0; i < n; i++) { const t = i / sr, bt = t % 0.5, kick = Math.sin(2 * Math.PI * (45 * bt + 110 * (1 - Math.exp(-30 * bt)) / 30)) * Math.exp(-bt * 9) * 0.9
    const nz = rnd(), ht = t % 0.25, hat = (nz - prev) * Math.exp(-ht * 60) * 0.35; prev = nz
    const bass = Math.sin(2 * Math.PI * notes[Math.floor(t / 2) % 4] * t) * 0.3, sw = 0.5 - 0.5 * Math.cos(2 * Math.PI * t / 8)
    const pad = (Math.sin(2 * Math.PI * 440 * t) + Math.sin(2 * Math.PI * 554.4 * t) + Math.sin(2 * Math.PI * 659.3 * t)) * 0.05 * sw
    pcm.writeInt16LE(Math.trunc(Math.max(-1, Math.min(1, kick + hat + bass + pad)) * 32000), i * 2) }
  const h = Buffer.alloc(44); h.write('RIFF', 0); h.writeUInt32LE(36 + pcm.length, 4); h.write('WAVEfmt ', 8); h.writeUInt32LE(16, 16); h.writeUInt16LE(1, 20); h.writeUInt16LE(1, 22); h.writeUInt32LE(sr, 24); h.writeUInt32LE(sr * 2, 28); h.writeUInt16LE(2, 32); h.writeUInt16LE(16, 34); h.write('data', 36); h.writeUInt32LE(pcm.length, 40)
  writeFileSync(path, Buffer.concat([h, pcm]))
}
writeFixtureWav(join(SP, 'fixture.wav'))
async function runDrive() {const b=await chromium.launch();const p=await b.newPage({viewport:{width:1280,height:900}});
const errs=[],reqs=[];p.on('pageerror',e=>errs.push(e.message));p.on('request',r=>{if(!/^(file|data|blob):/.test(r.url()))reqs.push(r.url())});
await p.goto('file://'+process.cwd()+'/_ARTIFACTS/tao-print-studio.html');
await p.waitForFunction(()=>window.TaoDrive&&TaoDrive.ready());await p.waitForTimeout(600);
const res={};
// D6/D7 at rest
const m0=await p.evaluate(()=>TaoDrive.markup());await p.waitForTimeout(1200);const m1=await p.evaluate(()=>TaoDrive.markup());
res.D6={playingBeforePlay:await p.evaluate(()=>TaoDrive.playing()),audioContextCreated:await p.evaluate(()=>TaoDrive.acCreated()),markupMovedAtRest:m0!==m1};
// Tag preset + stutter map, drive on
await p.click('#p-tag');await p.waitForTimeout(2500);await p.click('#drive-tagmap');await p.waitForTimeout(500);
const mk=async t=>{await p.evaluate(t=>window.seek(t),t);return p.evaluate(()=>TaoDrive.markup())};
const a1=await mk(2.5),b1=await mk(7.25),a2=await mk(2.5);
res.D1={same_at_2_5:a1===a2,different_at_7_25:a1!==b1};
// D8 scrub path equals seek path
await p.evaluate(()=>{const e=document.getElementById('drive-pos');e.value=2.5;e.dispatchEvent(new Event('input'))});await p.waitForTimeout(400);
const scrub=await p.evaluate(()=>TaoDrive.markup());res.D8={scrub_equals_seek:scrub===a1};
// D5 build time
const ms=await p.evaluate(()=>{const xs=[];for(let i=0;i<24;i++){const t0=performance.now();window.seek(0.4+i*0.55);xs.push(performance.now()-t0)}xs.sort((a,b)=>a-b);return xs[12]});
res.D5_median_ms=+ms.toFixed(1);
// D4 calm: render 4 s at 20 fps through the Tag stutter map, measure mean luminance jumps
const lum=[];
for(let i=0;i<80;i++){await p.evaluate(t=>window.seek(t),i/20);const png=await p.locator('#print').screenshot({type:'jpeg',quality:60,scale:'css'});fs.writeFileSync(SP+'/lum.jpg',png);const v=execFileSync('python3',['-c',"from PIL import Image,ImageStat;im=Image.open('"+SP+"/lum.jpg').convert('L').resize((96,96));print(ImageStat.Stat(im).mean[0])"]).toString();lum.push(+v)}
let perSec=[0,0,0,0];for(let i=1;i<80;i++){if(Math.abs(lum[i]-lum[i-1])>0.12*255)perSec[Math.floor(i/20)]++}
res.D4={jumps_per_second:perSec,lum_min:Math.min(...lum).toFixed(1),lum_max:Math.max(...lum).toFixed(1)};
// D2 + D3 tones
const tone=async(f)=>{await p.evaluate(f=>{const sr=22050,n=sr*3,pcm=new Float32Array(n);for(let i=0;i<n;i++)pcm[i]=0.8*Math.sin(2*Math.PI*f*i/sr);TaoDrive.load(pcm,sr,'tone '+f)},f);await p.waitForFunction(()=>TaoDrive.ready()&&TaoDrive.dur()>2.9&&TaoDrive.dur()<3.1);await p.waitForTimeout(300);return p.evaluate(()=>TaoDrive.feat(1.5))};
const f110=await tone(110),f440=await tone(440),f1760=await tone(1760),f7040=await tone(7040);
res.D2={f110,f440,f1760,f7040};
res.D2.pass=(f110.low>f110.mid&&f110.low>f110.high)&&(f7040.high>f7040.low&&f7040.high>f7040.mid)&&(f440.mid>f440.low&&f440.mid>f440.high);
// D3 slip <- low +100, base slip 0
await p.evaluate(()=>{const e=document.getElementById('slip');e.value=0;e.dispatchEvent(new Event('input'))});
await p.evaluate(()=>{for(let i=0;i<6;i++){const t=document.getElementById('drive-t'+i),s=document.getElementById('drive-s'+i),a=document.getElementById('drive-a'+i);if(i===0){t.value='slip';s.value='low';a.value=100}else{s.value='none';a.value=0}[t,s].forEach(x=>x.dispatchEvent(new Event('change')));a.dispatchEvent(new Event('input'))}});
await tone(110);const e110=await p.evaluate(()=>TaoDrive.eff(1.5));await tone(7040);const e7040=await p.evaluate(()=>TaoDrive.eff(1.5));
res.D3={slip_110:e110&&e110.slip,slip_7040:e7040&&e7040.slip};
res.D3.pass=!!(e110&&e110.slip>0&&(!e7040||!e7040.slip||e110.slip>=3*e7040.slip));
res.D7_requests_after_load=reqs.length;res.errors=errs;
console.log(JSON.stringify(res,null,1));await b.close()}
async function runFrame() {const b=await chromium.launch();const res={};
const studio='file://'+process.cwd()+'/_ARTIFACTS/tao-print-studio.html';
const p=await (await b.newContext({viewport:{width:1280,height:900}})).newPage();const errs=[],reqs=[];p.on('pageerror',e=>errs.push(e.message));p.on('request',r=>{if(!/^(file|data|blob):/.test(r.url()))reqs.push(r.url())});
await p.goto(studio);await p.waitForFunction(()=>window.TaoDrive&&TaoDrive.ready());await p.waitForTimeout(500);
// F1 round trip: demo analysis -> frame -> reload page -> loadFrame -> same sources and markup
await p.click('#p-tag');await p.waitForTimeout(2500);await p.click('#drive-tagmap');await p.waitForTimeout(300);
const times=Array.from({length:40},(_,i)=>0.17+i*0.39);
const feat1=await p.evaluate(ts=>ts.map(t=>TaoDrive.feat(t)),times);
const mk=async t=>{await p.evaluate(t=>window.seek(t),t);return p.evaluate(()=>TaoDrive.markup())};
const marks1=[];for(const t of [0.5,3.3,6.1,9.9,13.7])marks1.push(await mk(t));
const frame=await p.evaluate(()=>TaoDrive.frame());fs.writeFileSync(SP+'/demo-frame.json',JSON.stringify(frame));
await p.evaluate(()=>{const f=TaoDrive.frame();TaoDrive.loadFrame(JSON.parse(JSON.stringify(f)))});await p.waitForTimeout(400);
const feat2=await p.evaluate(ts=>ts.map(t=>TaoDrive.feat(t)),times);
const marks2=[];for(const t of [0.5,3.3,6.1,9.9,13.7])marks2.push(await mk(t));
res.F1={features_equal:JSON.stringify(feat1)===JSON.stringify(feat2),markup_equal:marks1.every((m,i)=>m===marks2[i])};
// F3 contract
const ok=(()=>{try{if(frame.v!==1||frame.kind!=='tao.analysis')return false;dec(frame.bands,frame.nf*frame.nb);dec(frame.lev,frame.nf);dec(frame.flux,frame.nf);for(let i=1;i<frame.chapters.length;i++)if(frame.chapters[i]<=frame.chapters[i-1])return false;return true}catch(e){return false}})();
res.F3={studio_frame_valid:ok};
// F4 size: scale this frame to 4 minutes
const bytes=JSON.stringify(frame).length;res.F4={json_bytes_for_dur:Math.round(frame.dur),json_bytes:bytes,projected_4min_kb:Math.round(bytes/frame.dur*240/1024)};
// F7: a loaded frame is the only source: doctor lev, the source must follow the file
const doc=JSON.parse(JSON.stringify(frame));const lev=Buffer.alloc(frame.nf,255);doc.lev=lev.toString('base64');
await p.evaluate(f=>TaoDrive.loadFrame(f),doc);await p.waitForTimeout(300);
const loud=await p.evaluate(()=>{const o=[];for(let i=0;i<20;i++)o.push(TaoDrive.feat(1+i*0.2).loud);return o});
res.F7={doctored_loudness_followed_file:loud.every(v=>v>0.9)};
// F5 no network, no PCM-sized data
res.F5={requests_after_load:reqs.length,frame_has_pcm_sized_field:Object.values(frame).some(v=>typeof v==='string'&&v.length>frame.nf*frame.nb*1.4)};
// F2 parity with Phosphor on the same decoded fixture file
const ph=await (await b.newContext({viewport:{width:1280,height:800}})).newPage();const perrs=[];ph.on('pageerror',e=>perrs.push(e.message));
await ph.goto('file://'+PHOSPHOR+'?test=1');await ph.waitForTimeout(1500);
if(!(await ph.evaluate(()=>typeof window.PhosphorFrame==='function'))){res.F2={skipped:'this Phosphor build has no window.PhosphorFrame (pass --phosphor with a build from PR 1549)'};res.errors=errs;console.log(JSON.stringify(res,null,1));await b.close();return}
await ph.setInputFiles('#file',SP+'/fixture.wav');
let pf=null;for(let i=0;i<60;i++){await ph.waitForTimeout(500);pf=await ph.evaluate(()=>window.PhosphorFrame&&window.PhosphorFrame());if(pf&&pf.name&&/fixture/.test(pf.name))break}
const st=await (await b.newContext({viewport:{width:1280,height:900}})).newPage();st.on('pageerror',e=>errs.push('S '+e.message));
await st.goto(studio);await st.waitForFunction(()=>window.TaoDrive&&TaoDrive.ready());await st.setInputFiles('#drive-file',SP+'/fixture.wav');
let sf=null;for(let i=0;i<60;i++){await st.waitForTimeout(500);sf=await st.evaluate(()=>{const f=TaoDrive.frame();return f&&/fixture/.test(f.name)?f:null});if(sf)break}
if(!pf||!sf){res.F2={error:'frame missing',phosphor:!!pf,studio:!!sf,perrs}}else{
 const cmp=(a,b)=>{let m=0,ne=0;for(let i=0;i<a.length;i++){const d=Math.abs(a[i]-b[i]);if(d>m)m=d;if(d>0)ne++}return{max:m,differing:ne,of:a.length}};
 const same=pf.nf===sf.nf;
 res.F2={phosphor_nf:pf.nf,studio_nf:sf.nf,same_nf:same,sr_p:pf.sr,sr_s:sf.sr,dur_p:+pf.dur.toFixed(3),dur_s:+sf.dur.toFixed(3)};
 if(same){res.F2.bands=cmp(dec(pf.bands),dec(sf.bands));res.F2.lev=cmp(dec(pf.lev),dec(sf.lev));res.F2.flux=cmp(dec(pf.flux),dec(sf.flux));res.F2.pass=res.F2.bands.max<=1&&res.F2.lev.max<=1&&res.F2.flux.max<=1}
 res.F2.phosphor_extra={bpm:pf.bpm,grid0:pf.grid0,chapters:pf.chapters.length,dna_beats:pf.dna?pf.dna.length:null,json_kb:Math.round(JSON.stringify(pf).length/1024)};
 // a Phosphor frame must load into the studio and drive it
 await st.evaluate(f=>TaoDrive.loadFrame(f),pf);await st.waitForTimeout(400);
 res.F2.studio_loads_phosphor_frame=await st.evaluate(()=>{const f=TaoDrive.feat(2.0);return {low:f.low,loud:f.loud,beat:f.beat,genF:f.genF}});
 writeFileSync(SP+'/phosphor-fixture-frame.json',JSON.stringify(pf));
}
res.errors=errs;res.phosphor_errors=perrs;
console.log(JSON.stringify(res,null,1));await b.close()}
async function runSlice2() {const b=await chromium.launch();const ctx=await b.newContext({viewport:{width:1280,height:900}});const p=await ctx.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
const url='file://'+process.cwd()+'/_ARTIFACTS/tao-print-studio.html';
const boot=async()=>{await p.goto(url);await p.waitForFunction(()=>window.TaoDrive&&TaoDrive.ready());await p.waitForTimeout(400)};
await boot();const res={};
const set=(id,v)=>p.evaluate(([id,v])=>{const e=document.getElementById(id);if(e.type==='checkbox')e.checked=v;else e.value=v;e.dispatchEvent(new Event(e.tagName==='SELECT'||e.type==='checkbox'?'change':'input',{bubbles:true}))},[id,v]);
const setRow=(i,t,s,a)=>p.evaluate(([i,t,s,a])=>{const T=document.getElementById('drive-t'+i),S=document.getElementById('drive-s'+i),A=document.getElementById('drive-a'+i);T.value=t;S.value=s;A.value=a;T.dispatchEvent(new Event('change'));S.dispatchEvent(new Event('change'));A.dispatchEvent(new Event('input'))},[i,t,s,a]);
// S6 consent first: nothing before Play
res.S6_before_play={fx:await p.evaluate(()=>Object.keys(TaoDrive.fxState()).length),ac:await p.evaluate(()=>TaoDrive.acCreated())};
// S1 slew: worst case stacking, keys mashed
await p.click('#p-tag');await p.waitForTimeout(2500);await set('drive-on',true);
await setRow(0,'fidelity','stutter',100);await setRow(1,'fidelity','onset',-100);await setRow(2,'slip','onset',100);await setRow(3,'dropout','low',100);await setRow(4,'views','sine',100);await setRow(5,'travel','saw',100);
await set('drive-stdepth',100);await set('drive-strate',16);
await p.evaluate(()=>{for(let t=0.5;t<12;t+=0.1){const k=Math.floor(t*10)%6;TaoDrive.key(k,true,+t.toFixed(3));TaoDrive.key(k,false,+(t+0.05).toFixed(3))}});
const ranges=await p.evaluate(()=>{const o={};['fidelity','slip','dropout','views','travel','pixel','rough','spray','spatter'].forEach(k=>{const e=document.getElementById(k);o[k]=+e.max-+e.min});return o});
const effs=await p.evaluate(()=>{const o=[];for(let i=0;i<14*30;i++)o.push(TaoDrive.eff((i+0.5)/30));return o});
let worst=0,worstK='';for(let i=1;i<effs.length;i++){const a=effs[i-1]||{},c=effs[i]||{};for(const k in ranges){if(k==='pixel')continue;const x=(a[k]===undefined?null:a[k]),y=(c[k]===undefined?null:c[k]);if(x===null||y===null)continue;const d=Math.abs(y-x)/ranges[k];if(d>worst){worst=d;worstK=k}}}
res.S1={max_step_fraction_of_range:+worst.toFixed(4),control:worstK,pass:worst<=0.2+1e-6};
// S3 stutter impact
for(let i=0;i<6;i++)await setRow(i,'fidelity','none',0);
await p.evaluate(()=>{});await set('drive-stdepth',100);
const gate=await p.evaluate(()=>{const g=[];for(let i=0;i<14*30;i++)g.push(TaoDrive.stutterGate((i+0.5)/30));return g});
const hi=[],lo=[];for(let i=12;i<gate.length;i++){let ok=true;for(let j=i-10;j<=i;j++)if(gate[j]!==gate[i])ok=false;if(!ok)continue;(gate[i]?hi:lo).push(i)}
const fx=await p.evaluate(()=>{const o=[];for(let i=0;i<14*30;i++)o.push(TaoDrive.eff((i+0.5)/30));return o});
const mean=(a,k)=>a.reduce((s,i)=>s+((fx[i]&&fx[i][k]!==undefined)?fx[i][k]:(k==='fidelity'?80:100)),0)/Math.max(1,a.length);
res.S3={frames_high:hi.length,frames_low:lo.length,fidelity_high:+mean(hi,'fidelity').toFixed(1),fidelity_low:+mean(lo,'fidelity').toFixed(1),slip_high:+mean(hi,'slip').toFixed(1),slip_low:+mean(lo,'slip').toFixed(1)};
res.S3.pass=hi.length>5&&lo.length>5&&(res.S3.fidelity_low-res.S3.fidelity_high>=40)&&(res.S3.slip_high>res.S3.slip_low);
await set('drive-stdepth',0);const off=await p.evaluate(()=>{const e=TaoDrive.eff(3.0);return e});res.S3.depth0_effect=off;
// S5 pairing responds (crush -> pixel), on a clean log
await set('drive-stdepth',0);await p.click('#key-clear');
await p.evaluate(()=>{TaoDrive.key(0,true,2.0);TaoDrive.key(0,false,3.0)});
const e25=await p.evaluate(()=>TaoDrive.eff(2.5)),e36=await p.evaluate(()=>TaoDrive.eff(3.6));
const want=Math.round(0.6*96/8)*8;res.S5={pixel_at_2_5:e25&&e25.pixel,pixel_at_3_6:e36?e36.pixel:0,paired_amount_rounded:want,pass:!!e25&&e25.pixel>=want&&(!e36||e36.pixel<=0.1*want+4)};
// S4 log purity: perform, markup, reload from saved settings, markup, seek away and back
await p.click('#key-clear');await p.evaluate(()=>{TaoDrive.key(2,true,1.2);TaoDrive.key(2,false,2.4);TaoDrive.key(4,true,2.0);TaoDrive.key(4,false,3.1)});
const mk=async t=>{await p.evaluate(t=>window.seek(t),t);return p.evaluate(()=>TaoDrive.markup())};
const m1=await mk(2.5);const mFar=await mk(9);const m2=await mk(2.5);
await p.waitForTimeout(300);await boot();const m3=await mk(2.5);
res.S4={scrub_back_equal:m1===m2,differs_far:m1!==mFar,reload_from_saved_equal:m1===m3};
// S8 recipe carries it: save a look, wipe, load it
await p.evaluate(()=>{const n=document.getElementById('save-name');n.value='perf';document.getElementById('save-btn').click()});await p.waitForTimeout(200);
const before=await p.evaluate(()=>JSON.parse(JSON.parse(localStorage.getItem('tao-print-studio-saves'))[0].cfg.drive?JSON.stringify(JSON.parse(localStorage.getItem('tao-print-studio-saves'))[0].cfg.drive):'null'));
await p.click('#key-clear');await set('drive-stdepth',0);const mWiped=await mk(2.5);
await p.evaluate(()=>{document.querySelector('#saves li button').click()});await p.waitForTimeout(500);
const m4=await mk(2.5);
res.S8={carried_stutter_keymap_log:/stutter/.test(before)&&/keymap/.test(before)&&/keylog/.test(before),wiped_differs:mWiped!==m1,restored_equal:m4===m1};
// S7 log size: 10 minutes of mashing against the cap
await p.click('#key-clear');
const sz=await p.evaluate(()=>{let t=0,n=0;for(let s=0;s<600*4;s++){t=s*0.25;const k=s%6;TaoDrive.key(k,true,+t.toFixed(3));TaoDrive.key(k,false,+(t+0.12).toFixed(3));n+=2}return {offered:n,bytes:TaoDrive.logSize(),stored:JSON.parse(JSON.stringify(0))}});
const stored=await p.evaluate(()=>JSON.parse(JSON.parse(localStorage.getItem('tao-print-studio')||'{}').drive||'{}').keylog);
res.S7={events_offered:sz.offered,bytes:sz.bytes,under_60KB:sz.bytes<=60*1024};
// S6 live audio effects: play, press, measure engage and release
await p.click('#key-clear');await p.click('#drive-play');await p.waitForTimeout(600);
res.S6_after_play={nodes:await p.evaluate(()=>Object.keys(TaoDrive.fxState()))};
await p.evaluate(()=>TaoDrive.key(0,true));await p.waitForTimeout(60);const on=await p.evaluate(()=>TaoDrive.fxState().crush);
await p.evaluate(()=>TaoDrive.key(0,false));await p.waitForTimeout(60);const offv=await p.evaluate(()=>TaoDrive.fxState().crush);
res.S6={engaged_after_60ms:+(on||0).toFixed(3),released_after_60ms:+(offv===null?1:offv).toFixed(3),pass:(on||0)>0.9&&offv!==null&&offv<0.1&&res.S6_before_play.fx===0&&!res.S6_before_play.ac};
await p.click('#drive-play');
// S2 calm: 10 Hz kick, stutter 100, keys mashed, 30 fps, 5 s
await p.evaluate(()=>{const sr=22050,n=sr*6,pcm=new Float32Array(n);for(let i=0;i<n;i++){const t=i/sr,bt=t%0.1;pcm[i]=Math.sin(2*Math.PI*(60*bt+120*(1-Math.exp(-60*bt))/60))*Math.exp(-bt*25)*0.9}TaoDrive.load(pcm,sr,'kick 10 Hz')});
await p.waitForFunction(()=>TaoDrive.ready()&&TaoDrive.dur()<6.1&&TaoDrive.dur()>5.9);await p.waitForTimeout(300);
await p.click('#p-tag');await p.waitForTimeout(2200);await set('drive-on',true);await set('drive-stdepth',100);await set('drive-strate',16);
await setRow(0,'fidelity','loud',100);await setRow(1,'slip','onset',100);await setRow(2,'views','onset',100);for(let i=3;i<6;i++)await setRow(i,'fidelity','none',0);
await p.click('#key-clear');await p.evaluate(()=>{for(let t=0;t<5;t+=0.1){const k=Math.floor(t*10)%6;TaoDrive.key(k,true,+t.toFixed(3));TaoDrive.key(k,false,+(t+0.05).toFixed(3))}});
const L=[];for(let i=0;i<150;i++){await p.evaluate(t=>window.seek(t),i/30);const png=await p.locator('#print').screenshot({type:'jpeg',quality:60});fs.writeFileSync(SP+'/lum2.jpg',png);L.push(+execFileSync('python3',['-c',"from PIL import Image,ImageStat;im=Image.open('"+SP+"/lum2.jpg').convert('L').resize((96,96));print(ImageStat.Stat(im).mean[0])"]).toString())}
const thr=0.12*255;let dir=0,ext=L[0],rev=new Array(5).fill(0);for(let i=1;i<L.length;i++){const d=L[i]-ext;if(dir>=0&&d>=thr){if(dir<0)rev[Math.floor(i/30)]++;dir=1;ext=L[i]}else if(dir<=0&&d<=-thr){if(dir>0)rev[Math.floor(i/30)]++;dir=-1;ext=L[i]}else if(dir>=0&&L[i]>ext){ext=L[i]}else if(dir<=0&&L[i]<ext){ext=L[i]}else if(dir>0&&d<=-thr){rev[Math.floor(i/30)]++;dir=-1;ext=L[i]}else if(dir<0&&d>=thr){rev[Math.floor(i/30)]++;dir=1;ext=L[i]}}
res.S2={reversals_per_second:rev,flashes_per_second:rev.map(r=>+(r/2).toFixed(1)),lum_range:[Math.min(...L).toFixed(1),Math.max(...L).toFixed(1)],pass:rev.every(r=>r/2<=3)};
res.errors=errs;console.log(JSON.stringify(res,null,1));await b.close()}

async function runRealtime() {
  const b = await chromium.launch(), ctx = await b.newContext({ viewport: { width: 1280, height: 900 } }), p = await ctx.newPage(), res = {}, errs = [], reqs = []
  p.on('pageerror', (e) => errs.push(e.message)); p.on('request', (r) => { if (!/^(file|data|blob):/.test(r.url())) reqs.push(r.url()) })
  const url = 'file://' + process.cwd() + '/_ARTIFACTS/tao-print-studio.html'
  await p.goto(url); await p.waitForFunction(() => window.TaoDrive && TaoDrive.ready()); await p.waitForTimeout(500)
  const sel = (id, v) => p.evaluate(([id, v]) => { const e = document.getElementById(id); e.value = v; e.dispatchEvent(new Event('change', { bubbles: true })) }, [id, v])
  const chk = (id, v) => p.evaluate(([id, v]) => { const e = document.getElementById(id); e.checked = v; e.dispatchEvent(new Event('change', { bubbles: true })) }, [id, v])
  res.R6_at_rest = { recording: await p.evaluate(() => !!TaoRT.recInfo()), audioContext: await p.evaluate(() => TaoDrive.acCreated()) }
  // R1 layout fills the frame, R8 deterministic layout
  const fills = {}, shapes = { '16:9': [1280, 720], '4:3': [960, 720], '1:1': [720, 720], '9:16': [720, 1280] }
  await sel('layout', 'fit'); res.R8 = {}
  for (const fr of Object.keys(shapes)) { await sel('frame', fr); await p.waitForTimeout(400); fills[fr] = { fill: +(await p.evaluate(() => TaoRT.fill())).toFixed(3), layout: await p.evaluate(() => { const l = TaoRT.layout(); return l.cols + 'x' + l.rows }) }
    const m1 = await p.evaluate(() => TaoRT.markup()); await p.evaluate(() => window.seek(0)); await p.waitForTimeout(150); const m2 = await p.evaluate(() => TaoRT.markup()); res.R8[fr] = m1 === m2 }
  res.R1 = { fills, pass: Object.values(fills).every((f) => f.fill >= 0.75) }
  // R2 responsive: Auto + Fit through a desktop to a phone width
  await sel('frame', 'auto'); await p.waitForTimeout(400); const lay1 = await p.evaluate(() => { const l = TaoRT.layout(); return l.cols + 'x' + l.rows })
  await p.setViewportSize({ width: 390, height: 800 }); await p.waitForTimeout(700)
  const lay2 = await p.evaluate(() => { const l = TaoRT.layout(); return l.cols + 'x' + l.rows }), sw = await p.evaluate(() => document.documentElement.scrollWidth)
  res.R2 = { desktop: lay1, phone: lay2, scrollWidth: sw, innerWidth: 390, pass: lay1 !== lay2 && sw <= 390 }
  await p.setViewportSize({ width: 1280, height: 900 }); await p.waitForTimeout(500)
  // R3 adaptive quality: an affordable look, throttled 6x, then released
  await p.click('#p-silk'); await p.waitForTimeout(1500); await sel('frame', 'auto'); await sel('layout', 'square'); await sel('rt-quality', 'auto')
  const cdp = await ctx.newCDPSession(p); await p.click('#drive-play'); await p.waitForTimeout(1200)
  const tier0 = await p.evaluate(() => TaoRT.tier())
  await cdp.send('Emulation.setCPUThrottlingRate', { rate: 6 }); let dropped = null, t0 = Date.now()
  while (Date.now() - t0 < 6000) { await p.waitForTimeout(250); if ((await p.evaluate(() => TaoRT.tier())) === 2) { dropped = (Date.now() - t0) / 1000; break } }
  await cdp.send('Emulation.setCPUThrottlingRate', { rate: 1 }); let back = null; t0 = Date.now()
  while (Date.now() - t0 < 10000) { await p.waitForTimeout(250); if ((await p.evaluate(() => TaoRT.rawTier())) === 3 && (await p.evaluate(() => TaoRT.tier())) === 3) { back = (Date.now() - t0) / 1000; break } }
  await p.click('#drive-play'); await p.waitForTimeout(300)
  res.R3 = { tier_before: tier0, seconds_to_draft_under_throttle: dropped, seconds_back_to_full_after_release: back, pass: tier0 === 3 && dropped !== null && dropped <= 3 && back !== null && back <= 8 }
  // R4 + R5 + R7: capture each shape for 3 s, probe with ffmpeg
  await sel('layout', 'fit'); await sel('rt-quality', 'draft'); await sel('rt-size', '720'); await chk('rt-stop', false); res.R4 = {}
  for (const [fr, [ew, eh]] of Object.entries(shapes)) {
    await sel('frame', fr); await p.waitForTimeout(500); await p.evaluate(() => window.seek(0)); await p.click('#rec-btn'); await p.waitForTimeout(3200); await p.click('#rec-btn')
    await p.waitForFunction(() => !!TaoRT.recBlob(), null, { timeout: 15000 }); await p.waitForTimeout(300)
    const info = await p.evaluate(() => TaoRT.recInfo()), b64 = await p.evaluate(async () => { const buf = new Uint8Array(await TaoRT.recBlob().arrayBuffer()); let s = ''; for (let i = 0; i < buf.length; i += 32768) s += String.fromCharCode.apply(null, buf.subarray(i, i + 32768)); return btoa(s) })
    const file = join(SP, 'rec-' + fr.replace(':', 'x') + '.webm'); writeFileSync(file, Buffer.from(b64, 'base64'))
    let probe = {}; try { const j = JSON.parse(execFileSync('ffprobe', ['-v', 'error', '-show_streams', '-of', 'json', file]).toString()); probe.video = j.streams.filter((x) => x.codec_type === 'video').length; probe.audio = j.streams.filter((x) => x.codec_type === 'audio').length; const v = j.streams.find((x) => x.codec_type === 'video'); probe.w = v && v.width; probe.h = v && v.height } catch (e) { probe.err = String(e.message).slice(0, 80) }
    let dur = null, vol = null; try { const o = execFileSync('ffmpeg', ['-v', 'info', '-i', file, '-af', 'volumedetect', '-f', 'null', '-'], { stdio: ['ignore', 'pipe', 'pipe'] }); } catch (e) {}
    const lg = (() => { try { return execFileSync('sh', ['-c', 'ffmpeg -i "' + file + '" -af volumedetect -f null - 2>&1 | tail -30']).toString() } catch (e) { return '' } })()
    const tm = lg.match(/time=(\d+):(\d+):([\d.]+)/g); if (tm) { const m = /time=(\d+):(\d+):([\d.]+)/.exec(tm[tm.length - 1]); dur = +m[1] * 3600 + +m[2] * 60 + +m[3] }
    const mv = /mean_volume: (-?[\d.]+) dB/.exec(lg); vol = mv ? +mv[1] : null
    await p.evaluate(() => { document.getElementById('rec-out').innerHTML = '' })
    res.R4[fr] = { expected: ew + 'x' + eh, got: probe.w + 'x' + probe.h, video: probe.video, audio: probe.audio, seconds: dur, mean_volume_db: vol, fps: info && info.fps, tier: info && info.tier, pass: probe.video === 1 && probe.audio === 1 && probe.w === ew && probe.h === eh && dur >= 2.4 && dur <= 3.9 }
    await p.evaluate(() => { window.seek(0) })
  }
  res.R4.pass = Object.values(res.R4).every((x) => x.pass !== false && x.pass !== undefined)
  res.R5 = { pass: Object.entries(res.R4).filter(([k]) => k !== 'pass').every(([, x]) => x.mean_volume_db !== null && x.mean_volume_db > -60) }
  res.R7 = { fps: Object.fromEntries(Object.entries(res.R4).filter(([k]) => k !== 'pass').map(([k, x]) => [k, x.fps])), pass: Object.entries(res.R4).filter(([k]) => k !== 'pass').every(([, x]) => x.fps >= 12) }
  res.R6 = { requests_after_load: reqs.length, nothing_before_click: !res.R6_at_rest.recording && !res.R6_at_rest.audioContext }
  res.errors = errs; console.log(JSON.stringify(res, null, 1)); await b.close()
}


async function runOffline() {
  const { existsSync: ex, statSync: st, readdirSync: rd } = await import('node:fs'), here = process.cwd(), vid = join(here, 'scripts/tao_studio_video.mjs'), res = {}
  const run = (args) => { try { return { code: 0, out: execFileSync('node', [vid, ...args], { stdio: ['ignore', 'pipe', 'pipe'] }).toString() } } catch (e) { return { code: e.status, out: String(e.stdout || ''), err: String(e.stderr || '').slice(0, 200) } } }
  const shapes = { '16:9': [1280, 720], '4:3': [960, 720], '1:1': [720, 720], '9:16': [720, 1280] }, secs = 2, fps = 12
  const tmpBefore = rd(tmpdir()).filter((n) => n.startsWith('tao-video-')).length
  const probe = (f) => JSON.parse(execFileSync('ffprobe', ['-v', 'error', '-show_streams', '-show_format', '-of', 'json', f]).toString())
  const vol = (f, t) => { const o = execFileSync('sh', ['-c', 'ffmpeg -t ' + t + ' -i "' + f + '" -vn -af volumedetect -f null - 2>&1 | grep mean_volume']).toString(), m = /(-?[\d.]+) dB/.exec(o); return m ? +m[1] : null }
  res.O2 = {}; res.O3 = {}; res.O5 = {}; let net = 0, demoWav = null
  for (const [r, [ew, eh]] of Object.entries(shapes)) {
    const f = join(SP, 'off-' + r.replace(':', 'x') + '.mp4'), o = run(['--out', f, '--preset', 'tag', '--ratio', r, '--short', '720', '--fps', String(fps), '--seconds', String(secs), '--force', ...(r === '16:9' ? ['--keep-frames', join(SP, 'off-frames')] : [])])
    if (o.code !== 0) { res.O2[r] = { error: o.err || o.out.slice(0, 200) }; continue }
    const sum = JSON.parse(o.out.trim().split('\n').pop()); net += sum.network_blocked
    const j = probe(f), v = j.streams.find((x) => x.codec_type === 'video'), a = j.streams.find((x) => x.codec_type === 'audio')
    res.O2[r] = { size: v.width + 'x' + v.height, expected: ew + 'x' + eh, video_streams: j.streams.filter((x) => x.codec_type === 'video').length, audio_streams: j.streams.filter((x) => x.codec_type === 'audio').length, video_s: +(+v.duration).toFixed(3), seconds_per_frame: sum.seconds_per_frame }
    res.O2[r].pass = res.O2[r].video_streams === 1 && res.O2[r].audio_streams === 1 && v.width === ew && v.height === eh && Math.abs(+v.duration - secs) <= 1 / fps + 1e-6
    res.O3[r] = { audio_minus_video_ms: Math.round((+a.duration - +v.duration) * 1000), out_mean_db: vol(f, secs) }
    res.O5[r] = { start_gap_ms: Math.round(Math.abs(+a.start_time - +v.start_time) * 1000) }
  }
  // source audio mean volume over the same span: the page's demo signal written as a WAV
  { const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 800, height: 600 } }); await p.goto('file://' + here + '/_ARTIFACTS/tao-print-studio.html?stage=1'); await p.waitForFunction(() => window.TaoDrive && TaoDrive.ready()); const b64 = await p.evaluate(() => TaoDrive.wavBase64()); demoWav = join(SP, 'demo-source.wav'); writeFileSync(demoWav, Buffer.from(b64, 'base64'))
    const srcDb = vol(demoWav, secs); for (const r of Object.keys(res.O3)) { res.O3[r].source_mean_db = srcDb; res.O3[r].pass = Math.abs(res.O3[r].audio_minus_video_ms) <= 50 && res.O3[r].out_mean_db !== null && Math.abs(res.O3[r].out_mean_db - srcDb) <= 1; res.O5[r].pass = res.O5[r].start_gap_ms <= 20 }
    res.O2.pass = Object.entries(res.O2).filter(([k]) => k !== 'pass').every(([, x]) => x.pass === true); res.O3.pass = Object.entries(res.O3).filter(([k]) => k !== 'pass').every(([, x]) => x.pass === true); res.O5.pass = Object.entries(res.O5).filter(([k]) => k !== 'pass').every(([, x]) => x.pass === true)
    // O1 frame exact + O4 full quality: same setup as the renderer, in a 1280x720 stage-only page
    await p.setViewportSize({ width: 1280, height: 720 }); await p.evaluate(() => document.getElementById('p-tag').click()); await p.waitForTimeout(600)
    const setv = (id, v) => p.evaluate(([id, v]) => { const e = document.getElementById(id); e.value = v; e.dispatchEvent(new Event('change', { bubbles: true })) }, [id, v]); await setv('layout', 'fit'); await setv('frame', 'auto'); await p.evaluate(() => document.getElementById('drive-tagmap').click()); await p.evaluate(() => TaoRT.forceFull()); await p.waitForTimeout(400)
    const shot = async (t) => { await p.evaluate((t) => window.seek(t), t); await p.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)))); return p.screenshot({ type: 'png' }) }
    const A = await shot(1.0); await shot(0.4); await shot(1.7); const B = await shot(1.0)
    res.O1 = { identical_bytes: Buffer.compare(A, B) === 0 }; res.O1.pass = res.O1.identical_bytes
    writeFileSync(join(SP, 'o4-full.png'), A); await p.evaluate(() => TaoRT.setQuality('draft')); const D = await shot(1.0); writeFileSync(join(SP, 'o4-draft.png'), D); await p.evaluate(() => TaoRT.forceFull())
    const diff = (x, y) => parseFloat(execFileSync('python3', ['-c', "from PIL import Image, ImageChops, ImageStat;a=Image.open('" + x + "').convert('RGB');b=Image.open('" + y + "').convert('RGB');print(sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3/255*100)"]).toString())
    const rf = join(SP, 'off-frames', 'f00012.png')
    res.O4 = { renderer_frame_vs_full_pct: ex(rf) ? +diff(rf, join(SP, 'o4-full.png')).toFixed(4) : null, draft_vs_full_pct: +diff(join(SP, 'o4-draft.png'), join(SP, 'o4-full.png')).toFixed(4) }
    res.O4.pass = res.O4.renderer_frame_vs_full_pct !== null && res.O4.renderer_frame_vs_full_pct <= 1 && res.O4.draft_vs_full_pct > res.O4.renderer_frame_vs_full_pct * 3
    await b.close() }
  // O6 private and safe: network, overwrite, temp folder
  const again = run(['--out', join(SP, 'off-16x9.mp4'), '--preset', 'tag', '--seconds', '0.2'])
  const tmpAfter = rd(tmpdir()).filter((n) => n.startsWith('tao-video-')).length
  res.O6 = { network_requests_blocked: net, refuses_overwrite_exit_code: again.code, temp_folders_left: tmpAfter - tmpBefore }; res.O6.pass = net === 0 && again.code === 2 && tmpAfter === tmpBefore
  // O7 fills the shape: Brainwash, first frame, border ring against the stage colour
  res.O7 = {}
  for (const r of ['16:9', '9:16']) { const dir = join(SP, 'o7-' + r.replace(':', 'x')); const o = run(['--out', join(SP, 'o7-' + r.replace(':', 'x') + '.mp4'), '--preset', 'brain', '--ratio', r, '--short', '720', '--fps', '10', '--seconds', '0.1', '--drive', 'off', '--force', '--keep-frames', dir]); if (o.code !== 0) { res.O7[r] = { error: o.err }; continue }
    const f = join(dir, 'f00000.png'), py = "from PIL import Image\nim=Image.open('" + f + "').convert('RGB');w,h=im.size;px=im.load();key=(0x14,0x06,0x0f)\nk=lambda p:all(abs(p[i]-key[i])<14 for i in range(3))\nn=c=0\nfor x in range(w):\n  for y in (0,h-1):\n    c+=1;n+=k(px[x,y])\nfor y in range(h):\n  for x in (0,w-1):\n    c+=1;n+=k(px[x,y])\nrows=sum(all(k(px[x,y]) for x in range(w)) for y in list(range(0,8))+list(range(h-8,h)))\ncols=sum(all(k(px[x,y]) for y in range(h)) for x in list(range(0,8))+list(range(w-8,w)))\nprint(n/c*100,rows,cols)", o2 = execFileSync('python3', ['-c', py]).toString().trim().split(' ')
    // O7 as registered is the border share in the stage colour; O7b is the direct letterbox test (whole border rows or columns in the stage colour)
    res.O7[r] = { border_pct_stage_colour: +(+o2[0]).toFixed(2), registered_pass: +o2[0] <= 5, letterbox_rows: +o2[1], letterbox_cols: +o2[2], letterbox_pass: +o2[1] === 0 && +o2[2] === 0 } }
  res.O7.registered_pass = Object.entries(res.O7).filter(([k]) => !/pass/.test(k)).every(([, x]) => x.registered_pass === true); res.O7.letterbox_pass = Object.entries(res.O7).filter(([k]) => !/pass/.test(k)).every(([, x]) => x.letterbox_pass === true)
  console.log(JSON.stringify(res, null, 1))
}

async function runProbe() {const b=await chromium.launch();const p=await b.newPage({viewport:{width:1280,height:900}});
await p.goto('file://'+process.cwd()+'/_ARTIFACTS/tao-print-studio.html');await p.waitForFunction(()=>window.TaoDrive&&TaoDrive.ready());await p.waitForTimeout(500);
const run=async(label,setup)=>{await p.evaluate(setup);await p.waitForTimeout(800);
 const r=await p.evaluate(async()=>{
  const svgEl=document.querySelector('#print svg');const svg=svgEl.outerHTML;const css=document.getElementById('studio-fonts').textContent;
  const fam=(document.getElementById('font').value);
  const draw=async(doc,w,h)=>{const t0=performance.now();const url=URL.createObjectURL(new Blob([doc],{type:'image/svg+xml'}));const img=new Image();img.src=url;await img.decode();const c=document.createElement('canvas');c.width=w;c.height=h;c.getContext('2d').drawImage(img,0,0,w,h);URL.revokeObjectURL(url);return performance.now()-t0};
  const med=async(doc,w,h,n=8)=>{const xs=[];for(let i=0;i<n;i++)xs.push(await draw(doc,w,h));xs.sort((a,b)=>a-b);return xs[Math.floor(n/2)]};
  const noFont=svg.replace(/^(<svg[^>]*>)/,'$1');
  const withAll=svg.replace(/^(<svg[^>]*>)/,'$1<style>'+css+'</style>');
  // only the face in use: keep font-faces whose family appears in the svg
  const used=css.split('\n').filter(l=>{const m=/font-family:'([^']+)'/.exec(l);return m&&svg.indexOf(m[1])>=0}).join('\n');
  const withUsed=svg.replace(/^(<svg[^>]*>)/,'$1<style>'+used+'</style>');
  return {markupKB:Math.round(svg.length/1024),usedFontKB:Math.round(used.length/1024),noFont:Math.round(await med(noFont,1920,1080)),usedFont:Math.round(await med(withUsed,1920,1080)),allFonts:Math.round(await med(withAll,1920,1080))};
 });console.log(label,JSON.stringify(r))};
await run('silkscreen 3x3 plain',()=>{document.getElementById('p-silk').click()});
await run('tag 2x2 full grit',()=>{document.getElementById('p-tag').click()});
await run('street 3x3 spray+rough+wall',()=>{document.getElementById('p-street').click()});
await run('tag, grit off (fidelity 100, auto)',()=>{document.getElementById('p-tag').click();const e=document.getElementById('fidelity');e.value=100;e.dispatchEvent(new Event('input'))});
await b.close()}
const table = { drive: runDrive, frame: runFrame, slice2: runSlice2, realtime: runRealtime, probe: runProbe, offline: runOffline }
if (!table[which]) { console.error('usage: tao_studio_checks.mjs drive|frame|slice2|realtime|probe|offline [--phosphor path]'); process.exit(2) }
await table[which]()
