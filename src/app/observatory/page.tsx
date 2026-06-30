"use client"

import { useState, useEffect, useRef, useCallback } from "react"

// ── CSS variables + keyframes injected once ───────────────────────────────────
const OBS_CSS = `
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
  :root {
    --bg:#020408; --surface:#0d1117; --elevated:#111827;
    --border:#1e293b; --border-active:rgba(122,210,255,0.38);
    --fg1:#e2e8f0; --fg2:#94a3b8; --fg3:#8593a6; --fg4:#707e92;
    --cyan:#00F0FF; --green:#00FF9D; --gold:#FFD700; --orange:#ff9d3c; --red:#FF4D6D; --steel:#94a3b8;
    --font-sans:'Inter',system-ui,-apple-system,sans-serif;
    --font-mono:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;
    --ease-luxury:cubic-bezier(.16,1,.3,1);
  }
  @keyframes obs-pulse {
    0%,100% { box-shadow: inset 0 1px 0 rgba(255,255,255,.05), 0 0 5px -1px #FF4D6D, 0 4px 11px rgba(0,0,0,.4); }
    50%      { box-shadow: inset 0 1px 0 rgba(255,255,255,.05), 0 0 14px -2px #FF4D6D, 0 4px 11px rgba(0,0,0,.4); }
  }
  @media (prefers-reduced-motion: reduce) { [data-pulse] { animation: none !important; } }
`

// ── Data ──────────────────────────────────────────────────────────────────────
const C = { cyan:"#00F0FF", green:"#00FF9D", gold:"#FFD700", orange:"#ff9d3c", red:"#FF4D6D", steel:"#94a3b8" }
const REPO = "https://github.com/flashesofbrilliance/arcs-v9/commit/"
const REPO_BASE = "https://github.com/flashesofbrilliance/arcs-v9"
const PROV_LEDGER = `${REPO_BASE}/blob/main/docs/provenance-ledger.md`

const ALT: Record<string,{name:string;accent:string}> = {
  L5:{name:"EXECUTIVE",  accent:C.green},
  L4:{name:"STRATEGIC",  accent:C.cyan},
  L3:{name:"OPERATIONAL",accent:C.gold},
  L2:{name:"TACTICAL",   accent:C.orange},
  L1:{name:"SURGICAL",   accent:C.red},
}
const GRADE: Record<string,string> = {A:C.green,B:C.cyan,C:C.gold,D:C.orange,F:C.red}
const SEV:   Record<string,string> = {RUIN:C.red,HIGH:C.orange,MED:C.gold}
const STATUS:Record<string,string> = {AVERTED:C.green,MITIGATED:C.gold,OPEN:C.red}
const TYPE_COLOR: Record<string,string> = {genesis:C.green,canon:C.green,kairos:C.gold,milestone:C.cyan,feat:C.cyan,security:C.red,fix:C.orange}

const SPAN_START = Date.parse("2026-04-09"), SPAN_DAYS = 56
const leftPct = (d: string) => Math.round(((Date.parse(d)-SPAN_START)/86400000/SPAN_DAYS)*1000)/10

interface Event { id:string;date:string;alt:string;type:string;peak?:boolean;label:string;sha:string;desc:string;conf:number }
interface Risk  { id:string;date:string;risk:string;sev:string;status:string;sha:string|null;how:string;note:string }
interface Finding { id:string;lab:string;grade:string;conf:number;risk:string;kind:string;desc:string;prov:[string,string,string,string][] }
interface Layer { id:string;findings:Finding[] }
type LedgerItem = (Event|Risk) & {kind:"event"|"risk";left:number}

const EVENTS: Event[] = [
  {id:"ev-0",date:"2026-04-09",alt:"L3",type:"genesis",peak:true, label:"Genesis — Next.js 16 + Prisma 7 + Auth.js v5 scaffold",sha:"471d573",desc:"First commit: the spec-first scaffold — Next.js 16 App Router, Prisma 7, Auth.js v5.",conf:90},
  {id:"ev-1",date:"2026-05-26",alt:"L4",type:"canon",          label:"Book II Parts V & VI → CANONICAL v1.0.0",sha:"b6e59e4",desc:"Canon promoted to v1.0.0 — the written world the running code executes.",conf:93},
  {id:"ev-2",date:"2026-05-27",alt:"L2",type:"feat",            label:"Design-system bootstrap — tokens + Badge",sha:"924fd10",desc:"Token layer + first Badge primitive land — the cockpit's visual grammar.",conf:88},
  {id:"ev-3",date:"2026-05-27",alt:"L4",type:"security",        label:"RLS deny-all on all 9 Supabase tables",sha:"9970c3f",desc:"Row-level security set to deny-all across every table — closes the open-data hole.",conf:92},
  {id:"ev-4",date:"2026-05-27",alt:"L4",type:"security",        label:"Soft-guard all API routes (ADR-001 auth gate)",sha:"25e76e8",desc:"Every API route gated behind the ADR-001 auth check.",conf:90},
  {id:"ev-5",date:"2026-05-27",alt:"L1",type:"fix",             label:"Prisma 7 adapter fix (PrismaPg) — unblocks deploy",sha:"11ba2fc",desc:"PrismaPg adapter swap clears P1012 and unblocks the first deploy.",conf:85},
  {id:"ev-6",date:"2026-05-28",alt:"L3",type:"milestone",peak:true,label:"P4 — first READY Vercel+Supabase deploy (ADR-002 closed)",sha:"dfce59d",desc:"First fully-READY production deploy on Vercel + Supabase; ADR-002 closed.",conf:94},
  {id:"ev-7",date:"2026-05-29",alt:"L3",type:"feat",            label:"Auth.js v5 magic link wired (Resend + PrismaAdapter)",sha:"935759f",desc:"Passwordless magic-link auth via Resend + the Prisma adapter.",conf:90},
  {id:"ev-8",date:"2026-06-03",alt:"L1",type:"security",        label:"Secrets purged from all git history",sha:"11a0fe7",desc:"git history rewritten to remove every committed secret.",conf:95},
  {id:"ev-9",date:"2026-06-03",alt:"L5",type:"kairos",peak:true,label:"ADR-016 Option C — anonymous compass + receipt claim (funnel opened)",sha:"6a5b856",desc:"The kairos move: anonymous compass + later receipt-claim opens the PLG funnel.",conf:92},
  {id:"ev-10",date:"2026-06-04",alt:"L2",type:"feat",           label:"Forensic analytics + observatory",sha:"b44fbac",desc:"This layer: forensic analytics + the zero-JS observability deck.",conf:88},
]
const RISKS: Risk[] = [
  {id:"risk-0",date:"2026-06-03",risk:"Credentials committed to git history",sev:"RUIN",status:"AVERTED", sha:"11a0fe7",how:"history rewrite + secret rotation",note:"API keys reached git history; purged before exploitation. Ruin-class — single exposure is unrecoverable."},
  {id:"risk-1",date:"2026-06-04",risk:"Free-solo decision (zero reversibility)",sev:"RUIN",status:"MITIGATED",sha:null,how:"ADR governance + reversibility gate",note:"Solo author, no review surface. Mitigated by ADR discipline; structurally standing."},
  {id:"risk-2",date:"2026-05-27",risk:"Unauthenticated data access (no RLS)",sev:"HIGH",status:"AVERTED", sha:"9970c3f",how:"RLS deny-all on all 9 tables",note:"Tables briefly readable without auth; closed by deny-all RLS."},
  {id:"risk-3",date:"2026-06-03",risk:"Cross-user data leakage",sev:"HIGH",status:"MITIGATED",sha:"6a5b856",how:"anonymous + scoped receipt-claim",note:"Receipt-claim flow scoped per session to prevent cross-user reads."},
  {id:"risk-4",date:"2026-05-28",risk:"DATABASE_URL silent rotation",sev:"HIGH",status:"OPEN",sha:"dfce59d",how:"needs alerting + pinned secret",note:"Provider can rotate the URL silently; no alert wired yet. Open."},
  {id:"risk-5",date:"2026-05-27",risk:"Prisma 7 P1012 — deploy blocked",sev:"MED",status:"AVERTED",sha:"11ba2fc",how:"PrismaPg adapter fix",note:"Schema/engine mismatch blocked deploy; resolved by adapter swap."},
  {id:"risk-6",date:"2026-06-04",risk:"computeYGate unaudited logic",sev:"MED",status:"OPEN",sha:null,how:"needs unit coverage + audit",note:"Core gate logic ships without test coverage. Open."},
]
const LAYERS: Layer[] = [
  {id:"L5",findings:[
    {id:"s-L5-0",lab:"Compass → Receipt",grade:"A",conf:96,risk:"LOW",kind:"CLASS",desc:"The product: a posed decision runs a 6-stage Claude pipeline and returns one bearing + a graded receipt.",prov:[["Product = compass pipeline","src/app/api/compass/route.ts:105-258","POST handler → receipt","P09"]]},
    {id:"s-L5-1",lab:"Solo · pre-revenue",grade:"A",conf:95,risk:"LOW",kind:"INSTANCE",desc:"One author; no external contributors; no PRs; one star.",prov:[["Single contributor","git log --format='%an' | sort -u","Zach Harris","P04"],["No PRs / 1 star","mcp github list_pull_requests","stars:1, PRs:[]","P21/P24"]]},
    {id:"s-L5-2",lab:"Spec-first world",grade:"A",conf:92,risk:"LOW",kind:"CLASS",desc:"Canon is the substrate; running code is the thinnest executable slice of a written world.",prov:[["Canon precedes code","WORLD.md + canon/","Book II v1.0.0","P02"]]},
    {id:"s-L5-3",lab:"Traction unproven",grade:"D",conf:88,risk:"MED",kind:"INSTANCE",desc:"No revenue, one star, no external usage signal yet.",prov:[["No traction signal","mcp github search_repositories","stars:1","P24"]]},
  ]},
  {id:"L4",findings:[
    {id:"s-L4-0",lab:"Dev/prod DB split",grade:"A",conf:94,risk:"LOW",kind:"INSTANCE",desc:"Separate dev and prod databases, cleanly externalized.",prov:[["Split confirmed",".env + supabase config","2 projects","P11"]]},
    {id:"s-L4-1",lab:"3-way externalization",grade:"A",conf:93,risk:"LOW",kind:"CLASS",desc:"Secrets, data, and deploy all externalized from the repo.",prov:[["Externalized","vercel + supabase + resend","3 providers","P12"]]},
    {id:"s-L4-2",lab:"ADR governance",grade:"A",conf:90,risk:"LOW",kind:"CLASS",desc:"Architecture decisions recorded as ADRs; reversibility is explicit.",prov:[["ADRs present","docs/adr/","ADR-001…016","P15"]]},
    {id:"s-L4-3",lab:"App-layer auth",grade:"C",conf:85,risk:"MED",kind:"INSTANCE",desc:"Auth enforced at the app layer rather than the data layer alone.",prov:[["Soft-guard routes","src/app/api/**","ADR-001","P17"]]},
    {id:"s-L4-4",lab:"Cross-repo ADRs",grade:"D",conf:70,risk:"MED",kind:"INSTANCE",desc:"Some ADRs live in sibling repos; provenance is split.",prov:[["Split ADRs","arcs-canon + arcs-v9","2 repos","P18"]]},
  ]},
  {id:"L3",findings:[
    {id:"s-L3-0",lab:"Compass request path",grade:"A",conf:95,risk:"LOW",kind:"CLASS",desc:"The full request path from compass POST to rendered receipt.",prov:[["Request path","src/app/api/compass/route.ts","POST→receipt","P09"]]},
    {id:"s-L3-1",lab:"Y-gate → render",grade:"A",conf:92,risk:"LOW",kind:"INSTANCE",desc:"Y-gate state drives render resolution (earned fidelity).",prov:[["Y-gate→render","src/lib/ygate.ts","state→resolution","P10"]]},
    {id:"s-L3-2",lab:"CLI 5-verb engine",grade:"B",conf:90,risk:"LOW",kind:"CLASS",desc:"A 5-verb CLI mirrors the core engine surface.",prov:[["5 verbs","arcs_core/cli","5 commands","P13"]]},
    {id:"s-L3-3",lab:"Manual env / rotation",grade:"C",conf:82,risk:"HIGH",kind:"INSTANCE",desc:"Env + secret rotation is manual; no automated alerting.",prov:[["Manual rotation","ops runbook","no automation","P19"]]},
    {id:"s-L3-4",lab:"exports/ freshness",grade:"D",conf:55,risk:"MED",kind:"INSTANCE",desc:"Generated exports/ can drift from source.",prov:[["Freshness risk","exports/","stale possible","P20"]]},
  ]},
  {id:"L2",findings:[
    {id:"s-L2-0",lab:"compass route 258",grade:"A",conf:98,risk:"LOW",kind:"INSTANCE",desc:"The compass route is 258 lines — the heaviest single handler.",prov:[["258 lines","src/app/api/compass/route.ts","L1-258","P09"]]},
    {id:"s-L2-1",lab:"arcs_core / cli",grade:"C",conf:97,risk:"MED",kind:"INSTANCE",desc:"Core logic + CLI share a small surface; coupling risk.",prov:[["Shared surface","arcs_core/","core+cli","P13"]]},
    {id:"s-L2-2",lab:"src/ = UI over tiny logic",grade:"A",conf:94,risk:"LOW",kind:"CLASS",desc:"src/ is mostly UI over a small logic core — thin executable slice.",prov:[["UI-heavy","src/","UI ≫ logic","P14"]]},
    {id:"s-L2-3",lab:"ygate.ts 248",grade:"B",conf:88,risk:"MED",kind:"INSTANCE",desc:"ygate.ts is 248 lines and carries the core gate logic.",prov:[["248 lines","src/lib/ygate.ts","L1-248","P10"]]},
    {id:"s-L2-4",lab:"network scanner ×2",grade:"D",conf:75,risk:"LOW",kind:"INSTANCE",desc:"Two network scanners present; low impact.",prov:[["2 scanners","scripts/","×2","P22"]]},
  ]},
  {id:"L1",findings:[
    {id:"s-L1-0",lab:"L0–L5 prose prompt",grade:"A",conf:98,risk:"LOW",kind:"CLASS",desc:"The pipeline is a single L0–L5 prose prompt, not orchestrated agents.",prov:[["Prose prompt","src/lib/pipeline","1 prompt","P25"]]},
    {id:"s-L1-1",lab:"single model call",grade:"A",conf:97,risk:"LOW",kind:"INSTANCE",desc:"One Claude call returns the whole receipt.",prov:[["1 call","compass/route.ts","single call","P26"]]},
    {id:"s-L1-2",lab:"arrays → TEXT",grade:"A",conf:95,risk:"LOW",kind:"INSTANCE",desc:"Structured arrays serialized to TEXT columns.",prov:[["arrays→TEXT","prisma/schema.prisma","TEXT cols","P27"]]},
    {id:"s-L1-3",lab:"computeYGate unaudited",grade:"C",conf:60,risk:"MED",kind:"INSTANCE",desc:"computeYGate ships without unit coverage.",prov:[["No tests","src/lib/ygate.ts","0 specs","P28"]]},
  ]},
]

const LEDGER: LedgerItem[] = [
  ...EVENTS.map(e=>({...e,kind:"event" as const,left:leftPct(e.date)})),
  ...RISKS.map(r=>({...r,kind:"risk"  as const,left:leftPct(r.date)})),
].sort((a,b)=>Date.parse(a.date)-Date.parse(b.date)||(a.kind==="event"?-1:1))

const DOW=["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]
const MON=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
function groupKeys(dateStr:string){
  const d=new Date(dateStr+"T00:00:00")
  const day=`${DOW[d.getDay()]} · ${MON[d.getMonth()]} ${d.getDate()}`
  const monday=new Date(d); monday.setDate(d.getDate()-((d.getDay()+6)%7))
  const week=`Week of ${MON[monday.getMonth()]} ${monday.getDate()}`
  const month=["January","February","March","April","May","June","July","August","September","October","November","December"][d.getMonth()]+` ${d.getFullYear()}`
  return {day,week,month}
}
function matchQ(x:Record<string,unknown>,q:string){
  if(!q||!q.trim())return true
  const s=q.trim().toLowerCase()
  const hay=[x.label,x.risk,x.type,x.alt,x.status,x.sev,x.sha,x.desc,x.note,x.lab,x.grade,x.how,x.kind,
    x.alt&&ALT[x.alt as string]&&ALT[x.alt as string].name].filter(Boolean).join(" ").toLowerCase()
  return hay.includes(s)
}
function stepIndices(focus:string){
  return(!focus||focus==="all")?LEDGER.map((_,i)=>i):LEDGER.map((x,i)=>((x as unknown as Record<string,unknown>).alt===focus?i:-1)).filter(i=>i>=0)
}

// ── Shared primitives ─────────────────────────────────────────────────────────
function Ctl({active,accent=C.green,children,...rest}:{active?:boolean;accent?:string;children:React.ReactNode;[k:string]:unknown}){
  const [h,setH]=useState(false)
  return(
    <button onMouseEnter={()=>setH(true)} onMouseLeave={()=>setH(false)} {...rest as React.ButtonHTMLAttributes<HTMLButtonElement>} style={{
      flex:"0 0 auto",border:`1px solid ${active?accent:(h?C.cyan:"#1e293b")}`,color:active?accent:(h?C.cyan:"#cbd5e1"),
      background:active?`linear-gradient(180deg,${accent}14,${accent}06)`:"linear-gradient(180deg,#0e151e,#0b1117)",
      padding:"7px 11px",fontSize:11,borderRadius:6,cursor:"pointer",minHeight:34,whiteSpace:"nowrap",
      fontFamily:"var(--font-mono)",display:"inline-flex",alignItems:"center",letterSpacing:".02em",
      boxShadow:active?`inset 0 -6px 11px -7px ${accent}40`:"inset 0 1px 0 rgba(255,255,255,.04)",transition:"all .15s",
    }}>{children}</button>
  )
}
const Sep=()=><span style={{flex:"0 0 auto",width:1,height:20,background:"#1e293b",margin:"0 3px"}}/>

interface DropdownOption{value:string|number;label:string;glyph?:string;accent?:string;hint?:string}
function Dropdown({label,value,options,onChange,accent=C.cyan,minWidth=150}:{label:string;value:string|number;options:DropdownOption[];onChange:(v:string|number)=>void;accent?:string;minWidth?:number}){
  const [open,setOpen]=useState(false)
  const [h,setH]=useState(false)
  const ref=useRef<HTMLDivElement>(null)
  useEffect(()=>{
    if(!open)return
    const close=(e:MouseEvent)=>{if(ref.current&&!ref.current.contains(e.target as Node))setOpen(false)}
    document.addEventListener("mousedown",close)
    return()=>document.removeEventListener("mousedown",close)
  },[open])
  const current=options.find(o=>o.value===value)||options[0]
  return(
    <div ref={ref} style={{position:"relative",flex:"0 0 auto"}}>
      <button onClick={()=>setOpen(v=>!v)} onMouseEnter={()=>setH(true)} onMouseLeave={()=>setH(false)} style={{
        display:"inline-flex",alignItems:"center",gap:8,width:minWidth,minHeight:34,padding:"7px 11px",
        border:`1px solid ${open?accent:(h?C.cyan:"#1e293b")}`,borderRadius:8,cursor:"pointer",
        background:"linear-gradient(160deg,rgba(255,255,255,.05),rgba(255,255,255,.01) 40%,rgba(0,0,0,.18)),linear-gradient(165deg,#11181f,#0a1016)",
        boxShadow:open?`inset 0 1px 0 rgba(255,255,255,.06),inset 0 -6px 11px -7px ${accent}40`:"inset 0 1px 0 rgba(255,255,255,.05),inset 0 -2px 6px rgba(0,0,0,.45)",
        fontFamily:"var(--font-mono)",fontSize:11,letterSpacing:".02em",transition:"all .15s",
      }}>
        {label&&<span style={{fontSize:9,color:"#707e92",letterSpacing:".12em",textTransform:"uppercase"}}>{label}</span>}
        {current?.glyph&&<span style={{color:current.accent||accent}}>{current.glyph}</span>}
        <span style={{color:open||h?accent:"#e2e8f0",flex:1,textAlign:"left",whiteSpace:"nowrap",overflow:"hidden",textOverflow:"ellipsis"}}>{current?.label}</span>
        <span style={{color:"#707e92",fontSize:9,transform:open?"rotate(180deg)":"none",transition:"transform .2s"}}>▾</span>
      </button>
      {open&&(
        <div style={{position:"absolute",top:"calc(100% + 5px)",left:0,width:"max-content",minWidth,zIndex:70,
          border:`1px solid ${accent}55`,borderRadius:9,overflow:"hidden",padding:4,
          background:"linear-gradient(180deg,#0e151e,#0a0f16)",boxShadow:`0 16px 34px -14px rgba(0,0,0,.8),0 0 0 1px rgba(0,0,0,.4),inset 0 1px 0 rgba(255,255,255,.05)`}}>
          {options.map(o=>{
            const sel=o.value===value
            return(
              <button key={o.value} onClick={()=>{onChange(o.value);setOpen(false)}} style={{
                display:"flex",alignItems:"center",gap:9,width:"100%",padding:"8px 10px",borderRadius:6,cursor:"pointer",
                border:"1px solid transparent",textAlign:"left",whiteSpace:"nowrap",
                background:sel?`linear-gradient(180deg,${(o.accent||accent)}1c,${(o.accent||accent)}08)`:"transparent",
                fontFamily:"var(--font-mono)",fontSize:11.5,transition:"background .12s",
                boxShadow:sel?`inset 0 -6px 11px -8px ${(o.accent||accent)}50`:"none",
              }}
              onMouseEnter={ev=>{if(!sel)(ev.currentTarget as HTMLButtonElement).style.background="rgba(255,255,255,.04)"}}
              onMouseLeave={ev=>{if(!sel)(ev.currentTarget as HTMLButtonElement).style.background="transparent"}}>
                {o.glyph&&<span style={{color:o.accent||accent,width:14,textAlign:"center"}}>{o.glyph}</span>}
                <span style={{display:"flex",flexDirection:"column",gap:1,flex:1}}>
                  <span style={{color:sel?(o.accent||accent):"#e2e8f0"}}>{o.label}</span>
                  {o.hint&&<span style={{color:"#707e92",fontSize:9.5}}>{o.hint}</span>}
                </span>
                {sel&&<span style={{color:o.accent||accent,fontSize:10}}>●</span>}
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}

// ── Control bar ───────────────────────────────────────────────────────────────
const ALT_TABS=[["all","all"],["L5","Exec"],["L4","Strategic"],["L3","Operational"],["L2","Tactical"],["L1","Surgical"]]
const MODE_OPTS=[
  {value:"glance",label:"At a glance",    glyph:"▦",accent:C.cyan, hint:"ledger + scored deck"},
  {value:"chain", label:"Chain of events",glyph:"⌥",accent:C.green,hint:"Exec → Surgical, linked"},
  {value:"risk",  label:"Risk register",  glyph:"⚠",accent:C.red,  hint:"ruin-paths by severity"},
]
const ALT_OPTS=[
  {value:"all",label:"All altitudes",accent:C.cyan},
  {value:"L5", label:"Executive",  glyph:"●",accent:C.green},
  {value:"L4", label:"Strategic",  glyph:"●",accent:C.cyan},
  {value:"L3", label:"Operational",glyph:"●",accent:C.gold},
  {value:"L2", label:"Tactical",   glyph:"●",accent:C.orange},
  {value:"L1", label:"Surgical",   glyph:"●",accent:C.red},
]
const GROUP_OPTS=[{value:"day",label:"By day"},{value:"week",label:"By week"},{value:"month",label:"By month"}]
const SEV_OPTS=[
  {value:"all", label:"All severities",accent:C.cyan},
  {value:"RUIN",label:"Ruin",  glyph:"◆",accent:C.red},
  {value:"HIGH",label:"High",  glyph:"◆",accent:C.orange},
  {value:"MED", label:"Medium",glyph:"◆",accent:C.gold},
]
const WIN_OPTS=[{value:7,label:"1 week"},{value:14,label:"2 weeks"},{value:28,label:"4 weeks"},{value:999,label:"All time"}]

function SearchBox({query,setQuery}:{query:string;setQuery:(v:string)=>void}){
  const [h,setH]=useState(false),[f,setF]=useState(false)
  const lit=f||h||query
  return(
    <div style={{position:"relative",display:"flex",alignItems:"center",width:"100%"}}>
      <span style={{position:"absolute",left:9,fontSize:14,color:lit?C.cyan:"#707e92",pointerEvents:"none",transition:"color .15s"}}>⌕</span>
      <input value={query} onChange={e=>setQuery(e.target.value)} onFocus={()=>setF(true)} onBlur={()=>setF(false)}
        onMouseEnter={()=>setH(true)} onMouseLeave={()=>setH(false)} placeholder="Filter events, risks, commits…"
        style={{width:"100%",minHeight:34,padding:"7px 26px 7px 28px",borderRadius:8,
          border:`1px solid ${f?C.cyan:(h?C.cyan+"88":"#1e293b")}`,outline:"none",
          background:"linear-gradient(160deg,rgba(255,255,255,.04),rgba(0,0,0,.18)),linear-gradient(165deg,#0e151e,#0a1016)",
          boxShadow:f?`inset 0 1px 0 rgba(255,255,255,.05),inset 0 -6px 11px -7px ${C.cyan}40,0 0 0 1px ${C.cyan}2a`:"inset 0 1px 0 rgba(255,255,255,.04),inset 0 2px 5px rgba(0,0,0,.45)",
          color:"#e2e8f0",fontFamily:"var(--font-mono)",fontSize:11,letterSpacing:".02em",transition:"all .15s"}}/>
      {query&&<button onClick={()=>setQuery("")} style={{position:"absolute",right:7,width:18,height:18,borderRadius:5,border:"none",cursor:"pointer",
        background:"rgba(255,255,255,.06)",color:"#8593a6",fontFamily:"var(--font-mono)",fontSize:11,display:"inline-flex",alignItems:"center",justifyContent:"center",padding:0}}>✕</button>}
    </div>
  )
}

function ControlBar({mode,setMode,focus,setFocus,sevFocus,setSevFocus,view,setView,riskWin,setRiskWin,legendOpen,setLegendOpen,query,setQuery,face,setFace}:{
  mode:string;setMode:(v:string)=>void;focus:string;setFocus:(v:string)=>void;sevFocus:string;setSevFocus:(v:string)=>void;
  view:string;setView:(v:string)=>void;riskWin:number;setRiskWin:(v:number)=>void;legendOpen:boolean;setLegendOpen:(f:(v:boolean)=>boolean)=>void;
  query:string;setQuery:(v:string)=>void;face:string;setFace:(f:(v:string)=>string)=>void;
}){
  const isRisk=mode==="risk"
  const focusVal=isRisk?sevFocus:focus
  const focusOpts=isRisk?SEV_OPTS:ALT_OPTS
  const focusSet=isRisk?setSevFocus:setFocus
  const periodShown=isRisk||mode==="glance"
  const periodVal=isRisk?riskWin:view
  const periodOpts=isRisk?WIN_OPTS:GROUP_OPTS
  const periodSet=isRisk?(v:string|number)=>setRiskWin(v as number):(v:string|number)=>setView(v as string)
  return(
    <div style={{display:"flex",flexDirection:"column",gap:8,padding:"0 0 2px"}}>
      <div style={{display:"flex",gap:8,flexWrap:"wrap",alignItems:"center"}}>
        <Dropdown label="View" value={mode} options={MODE_OPTS} onChange={v=>setMode(v as string)} accent={C.cyan} minWidth={190}/>
        <Dropdown label="Focus" value={focusVal} options={focusOpts} onChange={v=>focusSet(v as string)} accent={C.cyan} minWidth={188}/>
        {periodShown&&<Dropdown label={isRisk?"Window":"Group"} value={periodVal} options={periodOpts} onChange={periodSet} accent={C.cyan} minWidth={130}/>}
        <Sep/>
        <Ctl active={legendOpen} accent={C.cyan} onClick={()=>setLegendOpen(v=>!v)}>legend <span style={{display:"inline-block",fontSize:9,color:"#707e92",transform:legendOpen?"rotate(180deg)":"none",transition:"transform .2s"}}>▾</span></Ctl>
        <Sep/>
        <Ctl active accent={C.gold} onClick={()=>setFace(f=>f==="trajectory"?(isRisk?"by severity":"by altitude"):"trajectory")} title="flip the card">⇄ {face==="trajectory"?(isRisk?"by severity":"by altitude"):"trajectory"}</Ctl>
      </div>
      <SearchBox query={query} setQuery={setQuery}/>
    </div>
  )
}

function Legend({open}:{open:boolean}){
  const sw=(bg:string)=><span style={{display:"inline-block",width:10,height:10,borderRadius:3,verticalAlign:"middle",margin:"0 4px 0 8px",background:bg}}/>
  return(
    <div style={{overflow:"hidden",maxHeight:open?460:0,opacity:open?1:0,
      transition:"max-height .32s var(--ease-luxury),opacity .25s ease,margin .32s var(--ease-luxury)",
      margin:open?"8px 0 0":"0"}}>
      <div style={{border:"1px solid #22324d",borderRadius:10,padding:"12px 16px",
        background:"linear-gradient(180deg,#0e151e,#0b1117)",boxShadow:"inset 0 1px 0 rgba(255,255,255,.05),inset 0 -2px 8px rgba(0,0,0,.4)"}}>
        <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:"2px 28px",fontSize:11,whiteSpace:"nowrap"}}>
          <div>
            <p style={{color:C.gold,fontSize:10,letterSpacing:".08em",textTransform:"uppercase",margin:"0 0 5px"}}>How to use</p>
            <ul style={{margin:0,paddingLeft:16,color:"#8593a6",lineHeight:1.85,listStyle:"none"}}>
              <li><b style={{color:"#cbd5e1"}}>Tap</b> a row or node → its card</li>
              <li><b style={{color:"#cbd5e1"}}>View</b> → glance · chain · risk</li>
              <li><b style={{color:"#cbd5e1"}}>Focus</b> → isolate altitude · <b style={{color:"#cbd5e1"}}>↑ ↓</b></li>
              <li><b style={{color:"#cbd5e1"}}>Replay</b> → ▶ play · <b style={{color:"#cbd5e1"}}>← →</b> step</li>
              <li><b style={{color:"#cbd5e1"}}>Filter</b> → match events · risks · commits</li>
              <li><b style={{color:"#cbd5e1"}}>Space</b> legend · <b style={{color:"#cbd5e1"}}>Enter</b> card · <b style={{color:"#cbd5e1"}}>Esc</b> close</li>
            </ul>
          </div>
          <div>
            <p style={{color:C.gold,fontSize:10,letterSpacing:".08em",textTransform:"uppercase",margin:"0 0 5px"}}>The 4 encoded dimensions</p>
            <div style={{color:"#8593a6",lineHeight:2.0}}>
              <div><b style={{color:C.gold}}>1 Altitude</b> — Exec → Surgical · audience zoom</div>
              <div><b style={{color:C.gold}}>2 Hue</b> — grade{sw(C.green)}A{sw(C.cyan)}B{sw(C.gold)}C{sw(C.orange)}D{sw(C.red)}F</div>
              <div><b style={{color:C.gold}}>3 Glow</b> — confidence · brighter = surer</div>
              <div><b style={{color:C.gold}}>4 Border</b> — risk · solid · dashed · pulsing</div>
            </div>
          </div>
        </div>
        <div style={{marginTop:12,borderTop:"1px solid #16202e",paddingTop:10}}>
          <p style={{color:C.gold,fontSize:10,letterSpacing:".08em",textTransform:"uppercase",margin:"0 0 7px"}}>Map glyphs</p>
          <div style={{display:"flex",flexWrap:"wrap",gap:"8px 16px"}}>
            {[["✦","genesis",C.steel],["❖","canon",C.steel],["⊕","feature",C.steel],["⊘","security",C.steel],["✕","fix",C.steel],["◇","kairos",C.gold],["★","peak milestone",C.gold],["◆","risk",C.red]].map(([g,l,col])=>{
              const isR=g==="◆"
              return(
                <span key={l} style={{display:"inline-flex",alignItems:"center",gap:7,fontSize:11}}>
                  <span style={{width:17,height:17,flex:"0 0 auto",borderRadius:isR?3:"50%",transform:isR?"rotate(45deg)":"none",
                    display:"inline-flex",alignItems:"center",justifyContent:"center",background:col,color:"#04070c",
                    fontFamily:"var(--font-mono)",fontSize:9.5,fontWeight:700,boxShadow:`0 0 6px -1px ${col},inset 0 1px 0 rgba(255,255,255,.4)`}}>{isR?"":g}</span>
                  <b style={{color:"#cbd5e1",fontWeight:500}}>{l}</b>
                </span>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}

// ── Timeline / trajectory map ─────────────────────────────────────────────────
const TYPE_GLYPH: Record<string,string> = {genesis:"✦",canon:"❖",milestone:"★",feat:"⊕",security:"⊘",fix:"✕",kairos:"◇"}
const MAP_ALTS = ["L5","L4","L3","L2","L1"]

function TrajectoryMap({visibleCount,query,focus,onOpen}:{visibleCount:number;query:string;focus:string;onOpen:(x:LedgerItem)=>void}){
  const laneH=28,riskH=36
  const H=MAP_ALTS.length*laneH+riskH
  const laneCenter=(alt:string)=>MAP_ALTS.indexOf(alt)*laneH+laneH/2
  const riskCenter=MAP_ALTS.length*laneH+riskH/2
  const N=LEDGER.length
  const xpct=(i:number)=>N<=1?50:1.5+(i/(N-1))*97
  const evThread=LEDGER.map((x,i)=>({x,i})).filter(o=>o.x.kind==="event")
  const peaks=LEDGER.map((x,i)=>({x,i})).filter(o=>(o.x as Event).peak)
  const [hv,setHv]=useState<{i:number;x:number;cy:number;item:LedgerItem;isRisk:boolean;accent:string}|null>(null)
  const laneOff=(alt:string)=>focus&&focus!=="all"&&focus!==alt
  const riskOff=focus&&focus!=="all"
  return(
    <div style={{display:"flex",margin:"4px 0 14px"}}>
      <div style={{position:"relative",flex:"0 0 78px",height:H}}>
        {MAP_ALTS.map(alt=>(
          <div key={alt} style={{position:"absolute",left:0,top:laneCenter(alt),transform:"translateY(-50%)",display:"flex",flexDirection:"column",lineHeight:1.1,opacity:laneOff(alt)?0.2:1,transition:"opacity .3s"}}>
            <span style={{fontFamily:"var(--font-mono)",fontSize:9.5,fontWeight:700,color:ALT[alt].accent,letterSpacing:".04em",whiteSpace:"nowrap"}}>{alt}</span>
            <span style={{fontFamily:"var(--font-mono)",fontSize:7,color:"#707e92",letterSpacing:".07em",whiteSpace:"nowrap"}}>{ALT[alt].name}</span>
          </div>
        ))}
        <div style={{position:"absolute",left:0,top:riskCenter,transform:"translateY(-50%)",opacity:riskOff?0.2:1,transition:"opacity .3s"}}>
          <span style={{fontFamily:"var(--font-mono)",fontSize:9.5,fontWeight:700,color:C.red,letterSpacing:".04em",whiteSpace:"nowrap"}}>⚠ RISK</span>
        </div>
      </div>
      <div style={{position:"relative",flex:"1 1 auto",height:H,minWidth:0}}>
        {MAP_ALTS.map(alt=>(
          <div key={alt} style={{position:"absolute",left:0,right:6,top:laneCenter(alt),height:1,background:`linear-gradient(90deg,${ALT[alt].accent}24,${ALT[alt].accent}0a)`,opacity:laneOff(alt)?0.25:1,transition:"opacity .3s"}}/>
        ))}
        <div style={{position:"absolute",left:0,right:6,top:riskCenter,height:1,background:`linear-gradient(90deg,${C.red}24,${C.red}0a)`,opacity:riskOff?0.25:1,transition:"opacity .3s"}}/>
        <svg viewBox={`0 0 100 ${H}`} preserveAspectRatio="none" style={{position:"absolute",inset:0,width:"100%",height:"100%",pointerEvents:"none"}}>
          {peaks.map(o=><line key={(o.x as Event).id} x1={xpct(o.i)} x2={xpct(o.i)} y1="2" y2={MAP_ALTS.length*laneH} stroke={C.gold} strokeOpacity=".3" strokeWidth="1" strokeDasharray="2 3" vectorEffect="non-scaling-stroke"/>)}
          <polyline points={evThread.map(o=>`${xpct(o.i)},${laneCenter((o.x as Event).alt as string)}`).join(" ")} fill="none" stroke={C.cyan} strokeOpacity=".26" strokeWidth="1.2" vectorEffect="non-scaling-stroke"/>
        </svg>
        {LEDGER.map((x,i)=>{
          const isRisk=x.kind==="risk"
          const ev=x as Event; const rk=x as Risk
          const dim=i>=visibleCount||!matchQ(x as unknown as Record<string,unknown>,query)||(isRisk?!!riskOff:laneOff(ev.alt))
          const accent=isRisk?SEV[rk.sev]:(ev.peak?C.gold:ALT[ev.alt]?.accent||C.cyan)
          const cy=isRisk?riskCenter:laneCenter(ev.alt)
          const glyph=ev.peak?"★":(TYPE_GLYPH[ev.type]||"•")
          const sz=ev.peak?20:16
          const base=isRisk?"rotate(45deg)":"none"
          return(
            <button key={x.id} onClick={()=>onOpen(x)} title={`${x.date.slice(5)} · ${(x as Event).label||(x as Risk).risk}`}
              data-pulse={isRisk&&rk.status==="OPEN"?"":undefined}
              style={{position:"absolute",left:`${xpct(i)}%`,top:cy,width:sz,height:sz,marginLeft:-sz/2,marginTop:-sz/2,
                display:"inline-flex",alignItems:"center",justifyContent:"center",padding:0,cursor:"pointer",
                borderRadius:isRisk?3:"50%",transform:base,
                border:`1.5px solid ${isRisk?STATUS[rk.status]:(ev.peak?"#1a1404":"#03060b")}`,background:accent,
                boxShadow:`0 0 ${ev.peak?10:6}px -1px ${accent},inset 0 1px 0 rgba(255,255,255,.4),0 2px 4px rgba(0,0,0,.5)`,
                opacity:dim?0.15:1,pointerEvents:dim?"none":"auto",transition:"opacity .3s,transform .15s",
                animation:isRisk&&rk.status==="OPEN"?"obs-pulse 1.8s infinite":"none"}}
              onMouseEnter={ev_=>{(ev_.currentTarget as HTMLButtonElement).style.transform=`${base==="none"?"":base} scale(1.28)`;setHv({i,x:xpct(i),cy,item:x,isRisk,accent})}}
              onMouseLeave={ev_=>{(ev_.currentTarget as HTMLButtonElement).style.transform=base;setHv(h=>(h&&h.i===i?null:h))}}>
              {!isRisk&&<span style={{color:"#04070c",fontFamily:"var(--font-mono)",fontSize:ev.peak?11:9,fontWeight:700,lineHeight:1}}>{glyph}</span>}
            </button>
          )
        })}
        {hv&&(()=>{
          const x=hv.item,isRisk=hv.isRisk,accent=hv.accent,below=hv.cy<70
          const ev=x as Event; const rk=x as Risk
          return(
            <div style={{position:"absolute",left:`${hv.x}%`,top:below?hv.cy+14:hv.cy-14,transform:`translate(-50%,${below?"0":"-100%"})`,
              zIndex:6,pointerEvents:"none",width:"max-content",maxWidth:250,
              border:`1px solid ${accent}66`,borderRadius:8,padding:"7px 10px",
              background:"linear-gradient(180deg,#0e151e,#0a0f16)",boxShadow:`0 12px 26px -10px rgba(0,0,0,.85),0 0 0 1px rgba(0,0,0,.4),inset 0 1px 0 rgba(255,255,255,.05)`}}>
              <div style={{fontFamily:"var(--font-mono)",fontSize:9,letterSpacing:".06em",color:accent,fontWeight:700,marginBottom:3,whiteSpace:"nowrap"}}>
                {x.date.slice(5)} · {isRisk?`⚠ ${rk.sev} · ${rk.status}`:`${ev.alt} ${ALT[ev.alt]?.name} · ${String(ev.type).toUpperCase()}`}
              </div>
              <div style={{fontFamily:"var(--font-sans)",fontSize:11.5,color:"#e2e8f0",lineHeight:1.35}}>{ev.label||rk.risk}</div>
              <div style={{fontFamily:"var(--font-mono)",fontSize:9,color:"#8593a6",marginTop:4,whiteSpace:"nowrap"}}>
                {isRisk?`countered: ${rk.how}`:`conf ${ev.conf}${ev.sha?" · "+ev.sha:""}`}
              </div>
            </div>
          )
        })()}
      </div>
    </div>
  )
}

function FocusedAltitudeStrip({focus,visibleCount,query,onOpen}:{focus:string;visibleCount:number;query:string;onOpen:(x:LedgerItem)=>void}){
  return(
    <div style={{display:"flex",flexDirection:"column",gap:8,margin:"4px 0 14px"}}>
      {MAP_ALTS.map(alt=>{
        const dimAlt=focus!=="all"&&focus!==alt
        const evs=EVENTS.filter(e=>e.alt===alt)
        return(
          <div key={alt} style={{display:"flex",alignItems:"center",gap:10,padding:"7px 10px",borderRadius:8,
            border:`1px solid ${ALT[alt].accent}2e`,borderLeft:`3px solid ${ALT[alt].accent}`,
            background:"linear-gradient(180deg,rgba(255,255,255,.015),rgba(0,0,0,.12))",
            opacity:dimAlt?0.2:1,pointerEvents:dimAlt?"none":"auto",transition:"opacity .3s"}}>
            <div style={{flex:"0 0 86px",display:"flex",flexDirection:"column",lineHeight:1.15}}>
              <span style={{fontFamily:"var(--font-mono)",fontSize:10.5,fontWeight:700,color:ALT[alt].accent}}>{alt}</span>
              <span style={{fontFamily:"var(--font-mono)",fontSize:8,color:"#707e92",letterSpacing:".07em"}}>{ALT[alt].name}</span>
            </div>
            <div style={{display:"flex",flexWrap:"wrap",gap:6,flex:"1 1 auto",minWidth:0}}>
              {evs.length?evs.map(e=>{
                const li=LEDGER.findIndex(x=>x.id===e.id)
                const dim=li>=visibleCount||!matchQ(e as unknown as Record<string,unknown>,query)
                const accent=e.peak?C.gold:ALT[alt].accent
                const glyph=e.peak?"★":(TYPE_GLYPH[e.type]||"•")
                return(
                  <button key={e.id} onClick={()=>onOpen(LEDGER[li])} title={e.label}
                    style={{display:"inline-flex",alignItems:"center",gap:6,padding:"4px 9px 4px 5px",borderRadius:6,cursor:"pointer",
                      border:`1px solid ${accent}45`,background:`${accent}10`,fontFamily:"var(--font-mono)",
                      opacity:dim?0.22:1,pointerEvents:dim?"none":"auto",transition:"opacity .3s,border-color .15s"}}
                    onMouseEnter={ev=>(ev.currentTarget as HTMLButtonElement).style.borderColor=accent}
                    onMouseLeave={ev=>(ev.currentTarget as HTMLButtonElement).style.borderColor=`${accent}45`}>
                    <span style={{flex:"0 0 auto",width:16,height:16,borderRadius:"50%",background:accent,color:"#04070c",display:"inline-flex",alignItems:"center",justifyContent:"center",fontSize:9,fontWeight:700,boxShadow:`0 0 6px -1px ${accent}`}}>{glyph}</span>
                    <span style={{fontSize:10,color:"#cbd5e1",maxWidth:230,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{e.label}</span>
                    <span style={{flex:"0 0 auto",fontSize:8.5,color:"#707e92"}}>{e.date.slice(5)}</span>
                  </button>
                )
              }):<span style={{fontFamily:"var(--font-mono)",fontSize:9,color:"#5b6675"}}>no build events</span>}
            </div>
          </div>
        )
      })}
    </div>
  )
}

function ScBtn({active,accent,glyph,children,...rest}:{active?:boolean;accent:string;glyph?:string;children:React.ReactNode;[k:string]:unknown}){
  const [h,setH]=useState(false)
  return(
    <button {...rest as React.ButtonHTMLAttributes<HTMLButtonElement>} onMouseEnter={()=>setH(true)} onMouseLeave={()=>setH(false)} style={{
      cursor:"pointer",fontSize:10,borderRadius:5,padding:"3px 6px",minHeight:24,minWidth:glyph?28:22,fontFamily:"var(--font-mono)",
      border:`1px solid ${active?accent:(h?C.cyan:accent+"55")}`,
      color:active?"#04070c":(h?C.cyan:accent),
      background:active?accent:`${accent}12`,fontWeight:active?700:400,
      transition:"all .14s",display:"inline-flex",alignItems:"center",justifyContent:"center",gap:3,
    }}>{glyph&&<span style={{fontSize:8}}>{glyph}</span>}{children}</button>
  )
}

function Scrubber({replay,setReplay,playing,setPlaying,focus}:{replay:"all"|number;setReplay:(v:"all"|number)=>void;playing:boolean;setPlaying:(v:boolean)=>void;focus:string}){
  const steps=stepIndices(focus)
  const pos=typeof replay==="number"?steps.indexOf(replay):-1
  const sel=typeof replay==="number"?LEDGER[replay]:null
  const tColor=(x:LedgerItem)=>x.kind==="risk"?SEV[(x as Risk).sev]:((x as Event).peak?C.gold:ALT[(x as Event).alt]?.accent||C.cyan)
  const tLabel=(x:LedgerItem)=>x.kind==="risk"?`⚠ ${(x as Risk).sev} risk · ${(x as Risk).status}`:((x as Event).peak?`★ peak milestone · ${(x as Event).type}`:(x as Event).type)
  return(
    <div style={{margin:"2px 0 14px"}}>
      <div style={{display:"flex",alignItems:"baseline",gap:9,marginBottom:8,flexWrap:"wrap"}}>
        <span style={{fontFamily:"var(--font-mono)",fontSize:10.5,fontWeight:700,letterSpacing:".1em",color:C.gold}}>▸ MILESTONE REPLAY</span>
        <span style={{fontSize:10,color:"#8593a6"}}>each numbered marker is one logged milestone. ★ = peak. Press ▶ to play forward, or pick a step.</span>
      </div>
      <div style={{display:"flex",flexWrap:"wrap",gap:5,alignItems:"center"}}>
        <button onClick={()=>{if(playing){setPlaying(false);return}if(pos<0||pos>=steps.length-1)setReplay(steps[0]);setPlaying(true)}}
          style={{cursor:"pointer",fontSize:10,borderRadius:5,padding:"3px 9px",minHeight:24,fontFamily:"var(--font-mono)",fontWeight:700,letterSpacing:".04em",
            border:`1px solid ${playing?C.gold:C.green}`,color:"#04070c",background:playing?C.gold:C.green,display:"inline-flex",alignItems:"center",gap:5,transition:"all .14s"}}>
          <span style={{fontSize:9}}>{playing?"⏸":"▶"}</span>{playing?"PLAYING":"PLAY"}
        </button>
        <span style={{width:1,height:18,background:"#1e293b",margin:"0 2px"}}/>
        {steps.map((li,n)=>{const x=LEDGER[li];return(
          <ScBtn key={x.id} active={replay===li} accent={tColor(x)} glyph={x.kind==="risk"?"◆":(x as Event).peak?"★":undefined} title={`${n+1}. ${(x as Event).label||(x as Risk).risk}`} onClick={()=>{setPlaying(false);setReplay(li)}}>{n+1}</ScBtn>
        )})}
        <span style={{width:1,height:18,background:"#1e293b",margin:"0 2px"}}/>
        <ScBtn active={replay==="all"} accent={C.cyan} onClick={()=>{setPlaying(false);setReplay("all")}}>all</ScBtn>
      </div>
      <div style={{marginTop:9,padding:"8px 11px",borderRadius:8,border:`1px solid ${sel?tColor(sel)+"55":"#1e293b"}`,
        background:"linear-gradient(180deg,#0c121a,#0e151e)",boxShadow:"inset 0 1px 0 rgba(255,255,255,.04)",
        fontFamily:"var(--font-mono)",fontSize:11,display:"flex",gap:10,alignItems:"baseline",flexWrap:"wrap"}}>
        {sel?<>
          <span style={{color:"#707e92"}}>{String(Math.max(1,pos+1)).padStart(2,"0")} / {steps.length}</span>
          <span style={{color:"#8593a6"}}>{sel.date.slice(5)}</span>
          <span style={{color:tColor(sel),fontWeight:700,letterSpacing:".02em"}}>{tLabel(sel)}</span>
          <span style={{color:"#e2e8f0",flex:"1 1 auto",minWidth:0}}>{(sel as Event).label||(sel as Risk).risk}</span>
        </>:<>
          <span style={{color:C.cyan,fontWeight:700,letterSpacing:".06em"}}>ALL {steps.length} MILESTONES</span>
          <span style={{color:"#8593a6"}}>genesis → now · the full evidentiary chain.</span>
        </>}
      </div>
    </div>
  )
}

function EventRow({ev,dim,onOpen}:{ev:LedgerItem;dim:boolean;onOpen:(x:LedgerItem)=>void}){
  const [h,setH]=useState(false)
  const e=ev as Event
  const accent=e.peak?C.gold:ALT[e.alt]?.accent||C.cyan
  return(
    <div onMouseEnter={()=>setH(true)} onMouseLeave={()=>setH(false)} style={{display:"flex",gap:12,alignItems:"center",borderLeft:`3px solid ${accent}`,
      padding:"9px 11px",borderRadius:7,background:e.peak?"rgba(255,215,0,.05)":(h?"rgba(0,240,255,.06)":"rgba(255,255,255,.015)"),opacity:dim?0.16:1,transition:"opacity .3s,background .2s"}}>
      <button onClick={()=>onOpen(ev)} style={{display:"flex",flexDirection:"column",gap:3,flex:"1 1 auto",minWidth:0,background:"none",border:"none",cursor:"pointer",textAlign:"left",padding:0}}>
        <span style={{display:"flex",gap:8,alignItems:"baseline",flexWrap:"wrap",whiteSpace:"nowrap",fontFamily:"var(--font-mono)",fontSize:10,letterSpacing:".04em"}}>
          <span style={{color:"#8593a6"}}>{e.date.slice(5)}</span>
          <span style={{color:"#3a4a5e"}}>·</span>
          <span style={{fontWeight:700,color:ALT[e.alt]?.accent}}>{e.alt} {ALT[e.alt]?.name}</span>
          <span style={{color:"#3a4a5e"}}>·</span>
          <span style={{color:TYPE_COLOR[e.type]||C.steel,textTransform:"uppercase",letterSpacing:".08em"}}>{e.peak?"★ ":""}{e.type}</span>
        </span>
        <span style={{fontFamily:"var(--font-sans)",fontSize:14,fontWeight:500,lineHeight:1.35,color:h?C.cyan:"var(--fg1)",transition:"color .15s"}}>{e.label}</span>
      </button>
      <a href={REPO+e.sha} target="_blank" rel="noopener" style={{color:C.green,fontFamily:"var(--font-mono)",fontSize:11,flex:"0 0 auto",textDecoration:"none",alignSelf:"center"}}>{e.sha}↗</a>
    </div>
  )
}

function RiskRow({rk,dim,onOpen}:{rk:LedgerItem;dim:boolean;onOpen:(x:LedgerItem)=>void}){
  const [h,setH]=useState(false)
  const r=rk as Risk
  return(
    <div onMouseEnter={()=>setH(true)} onMouseLeave={()=>setH(false)} style={{display:"flex",gap:12,alignItems:"center",borderLeft:`3px solid ${SEV[r.sev]}`,
      padding:"9px 11px",borderRadius:7,background:h?"rgba(255,77,109,.10)":"rgba(255,77,109,.045)",opacity:dim?0.16:1,transition:"opacity .3s,background .2s"}}>
      <button onClick={()=>onOpen(rk)} style={{display:"flex",flexDirection:"column",gap:3,flex:"1 1 auto",minWidth:0,background:"none",border:"none",cursor:"pointer",textAlign:"left",padding:0}}>
        <span style={{display:"flex",gap:8,alignItems:"baseline",flexWrap:"wrap",whiteSpace:"nowrap",fontFamily:"var(--font-mono)",fontSize:10,letterSpacing:".04em"}}>
          <span style={{color:"#8593a6"}}>{r.date.slice(5)}</span>
          <span style={{color:"#3a4a5e"}}>·</span>
          <span style={{fontWeight:700,color:SEV[r.sev]}}>⚠ {r.sev} RISK</span>
          <span style={{color:"#3a4a5e"}}>·</span>
          <span style={{color:STATUS[r.status],textTransform:"uppercase",letterSpacing:".08em"}}>{r.status}</span>
        </span>
        <span style={{fontFamily:"var(--font-sans)",fontSize:14,fontWeight:500,lineHeight:1.35,color:h?C.cyan:"var(--fg1)",transition:"color .15s"}}>{r.risk}</span>
      </button>
      {r.sha?<a href={REPO+r.sha} target="_blank" rel="noopener" style={{color:SEV[r.sev],fontFamily:"var(--font-mono)",fontSize:11,flex:"0 0 auto",textDecoration:"none",alignSelf:"center"}}>{r.sha}↗</a>
        :<span style={{color:"#707e92",fontSize:10,flex:"0 0 auto",alignSelf:"center"}}>standing</span>}
    </div>
  )
}

function Ledger({view,visibleCount,query,onOpen}:{view:string;visibleCount:number;query:string;onOpen:(x:LedgerItem)=>void}){
  let lastKey:string|null=null
  const rows=LEDGER.filter(x=>matchQ(x as unknown as Record<string,unknown>,query))
  if(rows.length===0)return(
    <div style={{padding:"18px 11px",fontFamily:"var(--font-mono)",fontSize:11,color:"#707e92",textAlign:"center"}}>
      No milestones match <span style={{color:C.cyan}}>"{query}"</span>.
    </div>
  )
  return(
    <div style={{display:"flex",flexDirection:"column",gap:4}}>
      {rows.map(x=>{
        const i=LEDGER.indexOf(x)
        const keys=groupKeys(x.date)
        const key=keys[view as keyof typeof keys]
        const showHeader=key!==lastKey; lastKey=key
        const dim=i>=visibleCount
        return(
          <div key={x.id}>
            {showHeader&&<p style={{margin:"9px 0 1px",padding:"2px 8px",fontSize:9,letterSpacing:".1em",textTransform:"uppercase",
              color:view==="month"?C.cyan:view==="week"?C.gold:"#8593a6",
              borderBottom:view==="month"?"1px solid #1c2a40":"none",fontWeight:view==="month"?700:400}}>{key}</p>}
            {x.kind==="event"?<EventRow ev={x} dim={dim} onOpen={onOpen}/>:<RiskRow rk={x} dim={dim} onOpen={onOpen}/>}
          </div>
        )
      })}
    </div>
  )
}

function Timeline({replay,setReplay,view,query,face,focus,onOpen}:{replay:"all"|number;setReplay:(v:"all"|number)=>void;view:string;query:string;face:string;focus:string;onOpen:(x:LedgerItem)=>void}){
  const [playing,setPlaying]=useState(false)
  const replayRef=useRef(replay); replayRef.current=replay
  useEffect(()=>{
    if(!playing)return
    const steps=stepIndices(focus)
    const iv=setInterval(()=>{
      const cur=replayRef.current
      const p=cur==="all"?-1:steps.indexOf(cur)
      const np=p+1
      if(np>=steps.length-1){setReplay(steps[steps.length-1]);setPlaying(false)}
      else setReplay(steps[np])
    },1050)
    return()=>clearInterval(iv)
  },[playing,focus])
  const visibleCount=replay==="all"?LEDGER.length:(replay as number)+1
  const onBack=face==="altitude"
  return(
    <section style={{position:"relative",border:"1px solid #22324d",borderRadius:12,padding:"12px 14px 14px",
      background:"linear-gradient(180deg,rgba(14,22,38,.92),rgba(9,14,24,.92))"}}>
      <div style={{display:"flex",flexWrap:"wrap",alignItems:"baseline",gap:10,marginBottom:12}}>
        <span style={{fontFamily:"var(--font-mono)",fontSize:12,letterSpacing:".08em",color:onBack?C.gold:C.cyan,fontWeight:700}}>{onBack?"BY ALTITUDE":"8-WEEK TRAJECTORY"}</span>
        <span style={{fontSize:10,color:"#8593a6"}}>{onBack?"each altitude as a labelled lane · tap → card":"5 altitude lanes · glyph = type · ★ peak · ⚠ risk band · tap → card"}</span>
      </div>
      {onBack?<FocusedAltitudeStrip focus={focus} visibleCount={visibleCount} query={query} onOpen={onOpen}/>
        :<TrajectoryMap visibleCount={visibleCount} query={query} focus={focus} onOpen={onOpen}/>}
      <Scrubber replay={replay} setReplay={setReplay} playing={playing} setPlaying={setPlaying} focus={focus}/>
      <Ledger view={view} visibleCount={visibleCount} query={query} onOpen={onOpen}/>
    </section>
  )
}

// ── Deck (altitude planes + score nodes + risk register + sheet) ──────────────
const RISK_BORDER: Record<string,string> = {LOW:"solid",MED:"dashed",HIGH:"solid"}
const hx=(n:number)=>Math.max(0,Math.min(255,Math.round(n))).toString(16).padStart(2,"0")
const confBloom=(conf:number)=>hx((conf-30)*0.7)
function srcHref(src:string){
  const m=String(src||"").match(/^([\w./-]+\.[A-Za-z]+)(?::(\d+)(?:-(\d+))?)?$/)
  if(!m)return null
  let h=`${REPO_BASE}/blob/main/${m[1]}`
  if(m[2])h+=`#L${m[2]}`+(m[3]?`-L${m[3]}`:"")
  return h
}

function ScoreNode({node,onOpen}:{node:Finding;onOpen:(x:Finding)=>void}){
  const [h,setH]=useState(false)
  const c=GRADE[node.grade]
  const high=node.risk==="HIGH"
  return(
    <button onClick={()=>onOpen(node)} onMouseEnter={()=>setH(true)} onMouseLeave={()=>setH(false)}
      data-pulse={high?"":undefined}
      style={{position:"relative",textAlign:"left",cursor:"pointer",border:`1.5px ${RISK_BORDER[node.risk]} ${high?C.red:c}`,
        borderRadius:9,background:"linear-gradient(160deg,rgba(255,255,255,.05),rgba(255,255,255,.01) 40%,rgba(0,0,0,.18)),linear-gradient(165deg,#11181f,#0a1016)",padding:"7px 10px",minWidth:120,maxWidth:240,flex:"1 1 150px",
        boxShadow:high?undefined:`inset 0 1px 0 rgba(255,255,255,.05),inset 0 -8px 13px -9px ${c}${confBloom(node.conf)},0 0 ${h?13:8}px -4px ${c},0 4px 11px rgba(0,0,0,.4)`,
        transform:h?"translateY(-2px)":"none",transition:"transform .25s,box-shadow .2s",fontFamily:"var(--font-mono)",
        animation:high?"obs-pulse 1.8s infinite":"none"}}>
      <div style={{fontSize:11.5,color:"#e2e8f0",lineHeight:1.3}}>{node.lab}</div>
      <div style={{fontSize:9.5,color:"#8593a6",letterSpacing:".04em",marginTop:3,display:"flex",gap:6}}>
        <span style={{fontWeight:700,color:c}}>{node.grade}</span><span>conf {node.conf}</span><span>{node.risk}</span>
      </div>
    </button>
  )
}

function AltitudePlane({layer,dim,query,onOpen}:{layer:Layer;dim:boolean;query:string;onOpen:(x:Finding)=>void}){
  const meta=ALT[layer.id]
  const findings=layer.findings.filter(n=>matchQ(n as unknown as Record<string,unknown>,query))
  return(
    <section style={{position:"relative",border:"1px solid #243042",borderLeft:`3px solid ${meta.accent}`,borderRadius:14,
      padding:"12px 14px 14px",background:"linear-gradient(160deg,rgba(255,255,255,.05),rgba(255,255,255,.01) 38%,rgba(0,0,0,.18)),linear-gradient(165deg,#11181f,#0a1016)",
      boxShadow:"inset 0 1px 0 rgba(255,255,255,.08),inset 0 -2px 8px rgba(0,0,0,.5),0 5px 16px rgba(0,0,0,.4)",
      opacity:dim?0.16:1,pointerEvents:dim?"none":"auto",transition:"opacity .3s,box-shadow .3s"}}>
      <div style={{display:"flex",alignItems:"center",gap:10,marginBottom:10}}>
        <span style={{width:8,height:8,borderRadius:"50%",background:meta.accent,boxShadow:`0 0 8px ${meta.accent}`}}/>
        <span style={{fontFamily:"var(--font-mono)",fontSize:12,letterSpacing:".08em",color:meta.accent,fontWeight:600}}>{meta.name}</span>
        <span style={{fontFamily:"var(--font-mono)",fontSize:10,color:"#8593a6"}}>{findings.length} findings</span>
      </div>
      <div style={{display:"flex",flexWrap:"wrap",gap:9}}>
        {findings.length?findings.map(n=><ScoreNode key={n.id} node={n} onOpen={onOpen}/>)
          :<span style={{fontFamily:"var(--font-mono)",fontSize:10,color:"#5b6675"}}>no matching findings</span>}
      </div>
    </section>
  )
}

function Deck({focus,query,onOpen}:{focus:string;query:string;onOpen:(x:Finding)=>void}){
  return(
    <div style={{display:"flex",flexDirection:"column",gap:18}}>
      {LAYERS.map(l=><AltitudePlane key={l.id} layer={l} dim={focus!=="all"&&focus!==l.id} query={query} onOpen={onOpen}/>)}
    </div>
  )
}

function RiskNode({rk,onOpen}:{rk:Risk;onOpen:(x:Risk)=>void}){
  const [h,setH]=useState(false)
  const sc=STATUS[rk.status]
  return(
    <button onClick={()=>onOpen(rk)} onMouseEnter={()=>setH(true)} onMouseLeave={()=>setH(false)}
      style={{position:"relative",textAlign:"left",cursor:"pointer",flex:"1 1 220px",minWidth:200,maxWidth:340,
        border:`1px solid ${sc}45`,borderLeft:`3px solid ${sc}`,borderRadius:12,padding:"9px 11px",background:"linear-gradient(160deg,rgba(255,255,255,.05),rgba(255,255,255,.01) 40%,rgba(0,0,0,.18)),linear-gradient(165deg,#11181f,#0a1016)",
        boxShadow:`inset 0 1px 0 rgba(255,255,255,.05),inset 0 -8px 13px -9px ${sc}40,0 0 ${h?12:8}px -4px ${sc},0 4px 12px rgba(0,0,0,.4)`,transform:h?"translateY(-2px)":"none",transition:"transform .25s,box-shadow .2s",fontFamily:"var(--font-mono)"}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:5}}>
        <span style={{fontSize:9,fontWeight:700,letterSpacing:".08em",padding:"1px 6px",borderRadius:4,background:"rgba(255,255,255,.06)",color:SEV[rk.sev]}}>{rk.sev}</span>
        <span style={{fontSize:9,fontWeight:700,letterSpacing:".06em",padding:"1px 7px",border:`1px solid ${sc}`,borderRadius:5,color:sc}}>{rk.status}</span>
      </div>
      <div style={{fontSize:12,fontWeight:700,color:"#e2e8f0",lineHeight:1.3}}>{rk.risk}</div>
      <div style={{fontSize:9.5,color:C.cyan,marginTop:3,letterSpacing:".03em"}}>{rk.how}</div>
      <div style={{fontSize:9.5,color:rk.sha?C.green:"#707e92",marginTop:6}}>{rk.sha?rk.sha+"↗":"standing"}</div>
    </button>
  )
}

const MetaPill=({label,value,color}:{label:string;value:string;color:string})=>(
  <span style={{display:"inline-flex",alignItems:"baseline",gap:6,fontFamily:"var(--font-mono)",fontSize:11,
    padding:"4px 10px",borderRadius:6,border:`1px solid ${color}45`,background:`${color}12`}}>
    <span style={{fontSize:9,color:"var(--fg4)",letterSpacing:".1em",textTransform:"uppercase"}}>{label}</span>
    <span style={{color,fontWeight:700}}>{value}</span>
  </span>
)
const tdS:React.CSSProperties={padding:"7px 10px",textAlign:"left",verticalAlign:"top",color:"var(--fg2)",borderBottom:"1px solid #131c28"}

type SheetItem = LedgerItem | Finding | Risk
function Sheet({item,onClose}:{item:SheetItem|null;onClose:()=>void}){
  const open=!!item
  const isNode=!!(item&&(item as Finding).grade)
  const isRisk=!!(item&&(item as Risk).sev&&!(item as Finding).grade)
  const isEvent=!!(item&&!isNode&&!isRisk)
  const accent=!item?C.cyan
    :isNode?(((item as Finding).risk==="HIGH"?C.red:GRADE[(item as Finding).grade]))
    :isRisk?SEV[(item as Risk).sev]
    :((item as Event).peak?C.gold:(ALT[(item as Event).alt]?.accent||C.cyan))
  const kicker=!item?""
    :isNode?`${(item as Finding).kind} · scored finding`
    :isRisk?`ruin-path · ${(item as Risk).sev}`
    :`${(item as Event).alt} · ${ALT[(item as Event).alt]?.name||""}${(item as Event).peak?" · ★ peak":""}`
  const findingProv=isNode?(item as Finding).prov:null; const leadProv=findingProv?findingProv[0]?.[3]:null
  return(
    <div style={{position:"fixed",inset:0,zIndex:50,visibility:open?"visible":"hidden",pointerEvents:open?"auto":"none"}}>
      <div onClick={onClose} style={{position:"absolute",inset:0,background:"rgba(2,4,8,.6)",opacity:open?1:0,transition:"opacity .3s"}}/>
      <div style={{position:"absolute",left:0,right:0,bottom:0,transform:open?"translateY(0)":"translateY(100%)",transition:"transform .35s cubic-bezier(.2,.8,.2,1)",
        background:"linear-gradient(180deg,#0d1117,#060a11)",borderTop:`1px solid ${accent}`,
        boxShadow:`0 -1px 0 ${accent}40,0 -18px 40px -18px rgba(0,0,0,.85)`,padding:"18px 20px 28px",maxHeight:"82vh",overflow:"auto"}}>
        {item&&(
          <div style={{maxWidth:880,margin:"0 auto"}}>
            <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",gap:16}}>
              <div style={{minWidth:0}}>
                <div style={{fontFamily:"var(--font-mono)",fontSize:10,letterSpacing:".12em",textTransform:"uppercase",color:accent,fontWeight:700,marginBottom:6}}>{kicker}</div>
                <h3 style={{margin:0,fontFamily:"var(--font-sans)",fontSize:17,fontWeight:600,letterSpacing:"-0.01em",color:"var(--fg1)",lineHeight:1.25}}>
                  {(item as Finding).lab||(item as Risk).risk||(item as Event).label}
                </h3>
              </div>
              <div style={{display:"flex",alignItems:"center",gap:8,flex:"0 0 auto"}}>
                {(isEvent||isRisk)&&((item as Event|Risk).sha
                  ?<a href={REPO+(item as Event|Risk).sha} target="_blank" rel="noopener" style={{display:"inline-flex",alignItems:"center",gap:5,fontFamily:"var(--font-mono)",fontSize:11,color:C.green,padding:"5px 10px",borderRadius:6,border:`1px solid ${C.green}45`,background:`${C.green}10`,textDecoration:"none",whiteSpace:"nowrap"}}>{(item as Event|Risk).sha}<span style={{fontSize:9}}>↗</span></a>
                  :<span style={{fontFamily:"var(--font-mono)",fontSize:11,color:"var(--fg4)",padding:"5px 10px",borderRadius:6,border:"1px solid #243042",whiteSpace:"nowrap"}}>standing</span>)}
                {isNode&&leadProv&&<a href={PROV_LEDGER} target="_blank" rel="noopener" style={{display:"inline-flex",alignItems:"center",gap:5,fontFamily:"var(--font-mono)",fontSize:11,color:C.cyan,padding:"5px 10px",borderRadius:6,border:`1px solid ${C.cyan}45`,background:`${C.cyan}10`,whiteSpace:"nowrap",textDecoration:"none"}}>prov {leadProv}<span style={{fontSize:9}}>↗</span></a>}
                <button onClick={onClose} style={{width:30,height:30,borderRadius:6,border:"1px solid #243042",background:"linear-gradient(180deg,#11181f,#0a1016)",color:"var(--fg3)",cursor:"pointer",fontFamily:"var(--font-mono)",fontSize:12,display:"inline-flex",alignItems:"center",justifyContent:"center"}}>✕</button>
              </div>
            </div>
            <div style={{display:"flex",gap:8,flexWrap:"wrap",margin:"13px 0 14px"}}>
              {isNode&&<><MetaPill label="NCI" value={(item as Finding).grade} color={GRADE[(item as Finding).grade]}/><MetaPill label="confidence" value={String((item as Finding).conf)} color={C.cyan}/><MetaPill label="risk" value={(item as Finding).risk} color={(item as Finding).risk==="HIGH"?C.red:(item as Finding).risk==="MED"?C.gold:C.green}/></>}
              {isRisk&&<><MetaPill label="severity" value={(item as Risk).sev} color={SEV[(item as Risk).sev]}/><MetaPill label="status" value={(item as Risk).status} color={STATUS[(item as Risk).status]}/><MetaPill label="countered by" value={(item as Risk).how} color={C.cyan}/></>}
              {isEvent&&<><MetaPill label="altitude" value={`${(item as Event).alt} · ${ALT[(item as Event).alt]?.name||""}`} color={ALT[(item as Event).alt]?.accent||C.cyan}/><MetaPill label="type" value={(item as Event).type} color={TYPE_COLOR[(item as Event).type]||C.steel}/><MetaPill label="date" value={(item as Event).date.slice(5)} color={C.steel}/></>}
            </div>
            <p style={{color:"var(--fg2)",maxWidth:"76ch",margin:"0 0 14px",lineHeight:1.6,fontFamily:"var(--font-sans)",fontSize:13}}>
              {(item as Finding).desc||(item as Risk).note}
            </p>
            {isNode&&(item as Finding).prov&&(
              <div>
                <div style={{fontFamily:"var(--font-mono)",fontSize:9,letterSpacing:".12em",textTransform:"uppercase",color:"var(--fg4)",marginBottom:7}}>Provenance · reproducible</div>
                <div style={{overflowX:"auto",border:"1px solid #1a2533",borderRadius:8}}>
                  <table style={{borderCollapse:"collapse",width:"100%",minWidth:520,fontSize:11.5,fontFamily:"var(--font-mono)"}}>
                    <thead><tr>{["Claim","Source","Observed","ID"].map(th=><th key={th} style={{padding:"7px 10px",textAlign:"left",color:C.cyan,fontWeight:500,letterSpacing:".04em",borderBottom:"1px solid #1a2533",background:"rgba(255,255,255,.015)"}}>{th}</th>)}</tr></thead>
                    <tbody>{(item as Finding).prov.map((row,i)=>(
                      <tr key={i}>
                        <td style={tdS}>{row[0]}</td>
                        <td style={tdS}>{(()=>{const h=srcHref(row[1]);return h?<a href={h} target="_blank" rel="noopener" style={{color:C.green,fontSize:11,wordBreak:"break-word",textDecoration:"none"}}>{row[1]}<span style={{fontSize:9}}>↗</span></a>:<code style={{color:C.green,fontSize:11,wordBreak:"break-word"}}>{row[1]}</code>})()}</td>
                        <td style={{...tdS,color:C.gold}}>{row[2]}</td>
                        <td style={tdS}><a href={PROV_LEDGER} target="_blank" rel="noopener" style={{color:"var(--fg3)",textDecoration:"none"}}>{row[3]}<span style={{fontSize:9,color:C.cyan}}> ↗</span></a></td>
                      </tr>
                    ))}</tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// ── Chain of events view ──────────────────────────────────────────────────────
const ALT_ORDER=["L5","L4","L3","L2","L1"]
const EV_GLYPH: Record<string,string>={genesis:"✦",canon:"❖",milestone:"★",feat:"⊕",security:"⊘",fix:"✕",kairos:"◇"}

function ChainOfEvents({focus,query,current,setCurrent,onOpen}:{focus:string;query:string;current:"all"|number;setCurrent:(v:number)=>void;onOpen:(x:LedgerItem)=>void}){
  const laneH=72,padL=116,plotW=1000
  const evs=[...EVENTS].sort((a,b)=>Date.parse(a.date)-Date.parse(b.date))
  const laneY=(alt:string)=>ALT_ORDER.indexOf(alt)*laneH+laneH/2
  const xOf=(idx:number)=>padL+(evs.length<=1?0:idx/(evs.length-1))*(plotW-padL-34)
  const pts=evs.map((e,idx)=>({e,x:xOf(idx),y:laneY(e.alt)}))
  const H=ALT_ORDER.length*laneH
  const [hv,setHv]=useState<{x:number;y:number;e:Event}|null>(null)
  return(
    <section style={{border:"1px solid #243042",borderRadius:14,padding:"14px 14px 8px",
      background:"linear-gradient(160deg,rgba(255,255,255,.05),rgba(255,255,255,.01) 38%,rgba(0,0,0,.18)),linear-gradient(165deg,#11181f,#0a1016)",
      boxShadow:"inset 0 1px 0 rgba(255,255,255,.08),inset 0 -2px 8px rgba(0,0,0,.5),0 5px 16px rgba(0,0,0,.4)"}}>
      <div style={{display:"flex",flexWrap:"wrap",alignItems:"baseline",gap:10,marginBottom:6}}>
        <span style={{fontFamily:"var(--font-mono)",fontSize:12,letterSpacing:".08em",color:C.green,fontWeight:700}}>CHAIN OF EVENTS</span>
        <span style={{fontSize:10,color:"#8593a6"}}>Exec → Surgical — lanes are altitude · x is uniform build order · ★ kairos punctuated · tap a node → card</span>
      </div>
      <div style={{overflowX:"auto"}}>
        <div style={{position:"relative",minWidth:680,height:H}}>
          {ALT_ORDER.map((alt,i)=>(
            <div key={alt} style={{position:"absolute",left:0,right:0,top:i*laneH,height:laneH,
              borderBottom:i<4?"1px solid #16202e":"none",
              background:focus!=="all"&&focus!==alt?"transparent":(i%2?"rgba(255,255,255,.012)":"transparent"),
              opacity:focus!=="all"&&focus!==alt?0.22:1,transition:"opacity .3s"}}>
              <div style={{position:"absolute",left:10,top:"50%",transform:"translateY(-50%)",display:"flex",flexDirection:"column",gap:2,width:88}}>
                <span style={{fontFamily:"var(--font-mono)",fontSize:11,fontWeight:700,color:ALT[alt].accent,letterSpacing:".06em"}}>{alt}</span>
                <span style={{fontFamily:"var(--font-mono)",fontSize:8,color:"#707e92",letterSpacing:".1em",whiteSpace:"nowrap"}}>{ALT[alt].name}</span>
              </div>
              <span style={{position:"absolute",left:96,top:0,bottom:0,width:1,background:"#16202e"}}/>
            </div>
          ))}
          <svg viewBox={`0 0 ${plotW} ${H}`} preserveAspectRatio="none" style={{position:"absolute",inset:0,width:"100%",height:"100%",pointerEvents:"none"}}>
            {pts.filter(p=>p.e.peak).map(p=><line key={p.e.id} x1={p.x} x2={p.x} y1="0" y2={H} stroke={C.gold} strokeOpacity=".26" strokeWidth="1.5" strokeDasharray="3 4" vectorEffect="non-scaling-stroke"/>)}
            <polyline points={pts.map(p=>`${p.x},${p.y}`).join(" ")} fill="none" stroke={C.cyan} strokeOpacity="0.34" strokeWidth="1.5" vectorEffect="non-scaling-stroke"/>
          </svg>
          {pts.map(({e,x,y})=>{
            const dim=(focus!=="all"&&focus!==e.alt)||!matchQ(e as unknown as Record<string,unknown>,query)
            const accent=e.peak?C.gold:(TYPE_COLOR[e.type]||ALT[e.alt].accent)
            const sz=e.peak?16:12
            const li=LEDGER.findIndex(x=>x.id===e.id)
            const selected=current===li
            return(
              <div key={e.id}>
                {selected&&!dim&&<span style={{position:"absolute",left:`${(x/plotW)*100}%`,top:y,width:sz+11,height:sz+11,marginLeft:-(sz+11)/2,marginTop:-(sz+11)/2,borderRadius:"50%",border:`1.5px solid ${C.cyan}`,boxShadow:`0 0 11px -1px ${C.cyan}`,pointerEvents:"none"}}/>}
                <button onClick={()=>{setCurrent(li);onOpen(LEDGER[li])}} title={e.label}
                  style={{position:"absolute",left:`${(x/plotW)*100}%`,top:y,width:sz,height:sz,marginLeft:-sz/2,marginTop:-sz/2,
                    borderRadius:"50%",cursor:"pointer",padding:0,
                    border:`1.5px solid ${e.peak?"#1a1404":"#020408"}`,background:accent,
                    boxShadow:`inset 0 1px 0 rgba(255,255,255,.5),0 0 ${e.peak?10:6}px -1px ${accent},0 2px 5px rgba(0,0,0,.5)`,
                    opacity:dim?0.18:1,pointerEvents:dim?"none":"auto",transition:"opacity .3s,transform .15s"}}
                  onMouseEnter={ev_=>{(ev_.currentTarget as HTMLButtonElement).style.transform="scale(1.35)";setHv({x:(x/plotW)*100,y,e})}}
                  onMouseLeave={ev_=>{(ev_.currentTarget as HTMLButtonElement).style.transform="scale(1)";setHv(h=>(h&&h.e.id===e.id?null:h))}}>
                  {e.peak&&<span style={{position:"absolute",inset:0,display:"flex",alignItems:"center",justifyContent:"center",fontSize:9,color:"#1a1404"}}>★</span>}
                </button>
              </div>
            )
          })}
          {hv&&(()=>{
            const e=hv.e,below=hv.y<90,accent=e.peak?C.gold:(TYPE_COLOR[e.type]||ALT[e.alt].accent)
            return(
              <div style={{position:"absolute",left:`${hv.x}%`,top:below?hv.y+16:hv.y-16,transform:`translate(-50%,${below?"0":"-100%"})`,
                zIndex:8,pointerEvents:"none",width:"max-content",maxWidth:250,
                border:`1px solid ${accent}66`,borderRadius:8,padding:"7px 10px",
                background:"linear-gradient(180deg,#0e151e,#0a0f16)",boxShadow:`0 12px 26px -10px rgba(0,0,0,.85),0 0 0 1px rgba(0,0,0,.4),inset 0 1px 0 rgba(255,255,255,.05)`}}>
                <div style={{fontFamily:"var(--font-mono)",fontSize:9,letterSpacing:".06em",color:accent,fontWeight:700,marginBottom:3,whiteSpace:"nowrap"}}>
                  {e.date.slice(5)} · {e.alt} {ALT[e.alt].name} · {String(e.type).toUpperCase()}{e.peak?" · ★":""}
                </div>
                <div style={{fontFamily:"var(--font-sans)",fontSize:11.5,color:"#e2e8f0",lineHeight:1.35}}>{e.label}</div>
              </div>
            )
          })()}
        </div>
      </div>
      <div style={{display:"flex",justifyContent:"space-between",padding:"6px 34px 2px 116px",fontFamily:"var(--font-mono)",fontSize:9,color:"#707e92",letterSpacing:".06em"}}>
        <span>Apr 9 · genesis</span><span>build order →</span><span>Jun 4 · now</span>
      </div>
    </section>
  )
}

// ── Risk lanes ────────────────────────────────────────────────────────────────
const SEV_ORDER=["RUIN","HIGH","MED"]
const SEV_NAME: Record<string,string>={RUIN:"RUIN-CLASS",HIGH:"HIGH",MED:"MEDIUM"}

function RiskLanes({query,sel=0,setSel,sevFocus="all",win=14,onOpen}:{query:string;sel:number;setSel:(v:number)=>void;sevFocus:string;win:number;onOpen:(x:LedgerItem)=>void}){
  const buildH=38,laneH=72,axisH=18,gut=92,DAY=86400000
  const allMs=[...EVENTS,...RISKS].map(x=>Date.parse(x.date))
  const END=Math.max(...allMs)
  const START=win>=999?Math.min(...allMs):END-win*DAY
  const spanDays=Math.max(1,Math.round((END-START)/DAY))
  const inWin=(dstr:string)=>Date.parse(dstr)>=START
  const rks=[...RISKS].filter(r=>inWin(r.date)).sort((a,b)=>Date.parse(a.date)-Date.parse(b.date))
  const evs=[...EVENTS].filter(e=>inWin(e.date)).sort((a,b)=>Date.parse(a.date)-Date.parse(b.date))
  const xp=(dstr:string)=>3+((Date.parse(dstr)-START)/(END-START))*94
  const xpDay=(d:number)=>3+(d/spanDays)*94
  const laneDim=(sev:string)=>sevFocus!=="all"&&sev!==sevFocus
  const sevCenter=(sev:string)=>buildH+SEV_ORDER.indexOf(sev)*laneH+laneH/2
  const buildCenter=buildH/2
  const H=buildH+SEV_ORDER.length*laneH
  const [hv,setHv]=useState<{x:number;cy:number;item:Event|Risk;isRisk:boolean}|null>(null)
  const weeks:number[]=[]; for(let d=0;d<=spanDays;d+=7)weeks.push(d); if(weeks[weeks.length-1]!==spanDays)weeks.push(spanDays)
  const wkLabel=(d:number)=>{const dt=new Date(START+d*DAY);return`${dt.getMonth()+1}/${dt.getDate()}`}
  const rows=[{key:"BUILD",name:"BUILD EVENTS",color:C.cyan,cy:buildCenter,n:evs.length,glyph:"⌥"},
    ...SEV_ORDER.map(sev=>({key:sev,name:SEV_NAME[sev],color:SEV[sev],cy:sevCenter(sev),n:rks.filter(r=>r.sev===sev).length,glyph:"⚠"}))]
  return(
    <section style={{border:"1px solid #243042",borderRadius:14,padding:"14px 14px 10px",
      background:"linear-gradient(160deg,rgba(255,255,255,.05),rgba(255,255,255,.01) 38%,rgba(0,0,0,.18)),linear-gradient(165deg,#11181f,#0a1016)",
      boxShadow:"inset 0 1px 0 rgba(255,255,255,.08),inset 0 -2px 8px rgba(0,0,0,.5),0 5px 16px rgba(0,0,0,.4)"}}>
      <div style={{display:"flex",flexWrap:"wrap",alignItems:"baseline",gap:10,marginBottom:10}}>
        <span style={{fontFamily:"var(--font-mono)",fontSize:12,letterSpacing:".08em",color:C.red,fontWeight:700}}>RISK REGISTER</span>
        <span style={{fontSize:10,color:"#8593a6"}}>rolling window · ◆ risk in severity lanes · ← → step · ↑ ↓ focus lane</span>
      </div>
      <div style={{display:"flex"}}>
        <div style={{position:"relative",flex:`0 0 ${gut}px`,height:H+axisH}}>
          {rows.map(r=>(
            <div key={r.key} style={{position:"absolute",left:0,top:r.cy,transform:"translateY(-50%)",display:"flex",flexDirection:"column",lineHeight:1.15,opacity:r.key!=="BUILD"&&laneDim(r.key)?0.28:1,transition:"opacity .3s"}}>
              <span style={{fontFamily:"var(--font-mono)",fontSize:10,fontWeight:700,color:r.color,letterSpacing:".04em",whiteSpace:"nowrap"}}>{r.glyph} {r.key}</span>
              <span style={{fontFamily:"var(--font-mono)",fontSize:7.5,color:"#707e92",letterSpacing:".06em",whiteSpace:"nowrap"}}>{r.name} · {r.n}</span>
            </div>
          ))}
        </div>
        <div style={{position:"relative",flex:"1 1 auto",height:H+axisH,minWidth:0}}>
          <div style={{position:"absolute",left:0,right:0,top:buildH,height:1,background:"#1b2a3d"}}/>
          {SEV_ORDER.map((sev,i)=>i>0&&<div key={sev} style={{position:"absolute",left:0,right:0,top:buildH+i*laneH,height:1,background:"#13202e"}}/>)}
          <svg viewBox={`0 0 100 ${H}`} preserveAspectRatio="none" style={{position:"absolute",left:0,top:0,width:"100%",height:H,pointerEvents:"none"}}>
            {weeks.map(d=><line key={"w"+d} x1={xpDay(d)} x2={xpDay(d)} y1="0" y2={H} stroke="#27374f" strokeWidth="1" vectorEffect="non-scaling-stroke"/>)}
            {evs.map(e=><line key={"o"+e.id} x1={xp(e.date)} x2={xp(e.date)} y1={buildH} y2={H} stroke={e.peak?C.gold:C.cyan} strokeOpacity={e.peak?".24":".09"} strokeWidth="1" strokeDasharray={e.peak?"3 4":undefined} vectorEffect="non-scaling-stroke"/>)}
          </svg>
          {evs.map(e=>{
            const dim=!matchQ(e as unknown as Record<string,unknown>,query)
            const accent=e.peak?C.gold:ALT[e.alt].accent
            const glyph=e.peak?"★":(EV_GLYPH[e.type]||"•")
            const sz=e.peak?17:14
            const li=LEDGER.findIndex(x=>x.id===e.id)
            return(
              <button key={e.id} onClick={()=>onOpen(LEDGER[li])} title={`${e.date.slice(5)} · ${e.label}`}
                style={{position:"absolute",left:`${xp(e.date)}%`,top:buildCenter,width:sz,height:sz,marginLeft:-sz/2,marginTop:-sz/2,
                  display:"inline-flex",alignItems:"center",justifyContent:"center",borderRadius:"50%",cursor:"pointer",padding:0,
                  border:`1px solid ${e.peak?"#1a1404":"#03060b"}`,background:accent,color:"#04070c",
                  fontFamily:"var(--font-mono)",fontSize:e.peak?10:8,fontWeight:700,
                  boxShadow:`0 0 ${e.peak?8:5}px -1px ${accent},inset 0 1px 0 rgba(255,255,255,.4)`,
                  opacity:dim?0.14:0.95,pointerEvents:dim?"none":"auto",transition:"opacity .3s,transform .15s"}}
                onMouseEnter={ev_=>{(ev_.currentTarget as HTMLButtonElement).style.transform="scale(1.25)";setHv({x:xp(e.date),cy:buildCenter,item:e,isRisk:false})}}
                onMouseLeave={ev_=>{(ev_.currentTarget as HTMLButtonElement).style.transform="scale(1)";setHv(h=>(h&&h.item.id===e.id?null:h))}}>{glyph}</button>
            )
          })}
          {rks.map((r,idx)=>{
            const dim=!matchQ(r as unknown as Record<string,unknown>,query)||laneDim(r.sev)
            const c=SEV[r.sev],sc=STATUS[r.status]
            const sz=r.sev==="RUIN"?18:14
            const selected=sel===idx
            const li=LEDGER.findIndex(x=>x.id===r.id)
            return(
              <div key={r.id}>
                {selected&&!dim&&<span style={{position:"absolute",left:`${xp(r.date)}%`,top:sevCenter(r.sev),width:sz+13,height:sz+13,marginLeft:-(sz+13)/2,marginTop:-(sz+13)/2,borderRadius:"50%",border:`1.5px solid ${C.cyan}`,boxShadow:`0 0 11px -1px ${C.cyan}`,pointerEvents:"none"}}/>}
                <button onClick={()=>{setSel(idx);onOpen(LEDGER[li])}} title={`${r.sev} · ${r.status} — ${r.risk}`}
                  data-pulse={r.status==="OPEN"?"":undefined}
                  style={{position:"absolute",left:`${xp(r.date)}%`,top:sevCenter(r.sev),width:sz,height:sz,marginLeft:-sz/2,marginTop:-sz/2,
                    borderRadius:2,cursor:"pointer",padding:0,transform:"rotate(45deg)",
                    border:`2px solid ${sc}`,background:c,
                    boxShadow:`inset 0 1px 0 rgba(255,255,255,.4),0 0 ${r.sev==="RUIN"?11:7}px -1px ${c},0 2px 5px rgba(0,0,0,.5)`,
                    opacity:dim?0.16:1,pointerEvents:dim?"none":"auto",
                    animation:r.status==="OPEN"?"obs-pulse 1.8s infinite":"none",transition:"opacity .3s"}}
                  onMouseEnter={ev_=>{(ev_.currentTarget as HTMLButtonElement).style.transform="rotate(45deg) scale(1.32)";setHv({x:xp(r.date),cy:sevCenter(r.sev),item:r,isRisk:true})}}
                  onMouseLeave={ev_=>{(ev_.currentTarget as HTMLButtonElement).style.transform="rotate(45deg) scale(1)";setHv(h=>(h&&h.item.id===r.id?null:h))}}/>
              </div>
            )
          })}
          {weeks.map(d=>(
            <span key={"wl"+d} style={{position:"absolute",left:`${xpDay(d)}%`,top:H+3,transform:"translateX(-50%)",fontFamily:"var(--font-mono)",fontSize:8.5,color:"#707e92",whiteSpace:"nowrap"}}>{wkLabel(d)}</span>
          ))}
          {hv&&(()=>{
            const x=hv.item,isRisk=hv.isRisk,below=hv.cy<70
            const accent=isRisk?SEV[(x as Risk).sev]:((x as Event).peak?C.gold:ALT[(x as Event).alt].accent)
            return(
              <div style={{position:"absolute",left:`${hv.x}%`,top:below?hv.cy+16:hv.cy-16,transform:`translate(-50%,${below?"0":"-100%"})`,
                zIndex:8,pointerEvents:"none",width:"max-content",maxWidth:250,
                border:`1px solid ${accent}66`,borderRadius:8,padding:"7px 10px",
                background:"linear-gradient(180deg,#0e151e,#0a0f16)",boxShadow:`0 12px 26px -10px rgba(0,0,0,.85),0 0 0 1px rgba(0,0,0,.4),inset 0 1px 0 rgba(255,255,255,.05)`}}>
                <div style={{fontFamily:"var(--font-mono)",fontSize:9,letterSpacing:".06em",color:accent,fontWeight:700,marginBottom:3,whiteSpace:"nowrap"}}>
                  {x.date.slice(5)} · {isRisk?`⚠ ${(x as Risk).sev} · ${(x as Risk).status}`:`${(x as Event).alt} ${ALT[(x as Event).alt].name} · ${String((x as Event).type).toUpperCase()}`}
                </div>
                <div style={{fontFamily:"var(--font-sans)",fontSize:11.5,color:"#e2e8f0",lineHeight:1.35}}>{(x as Risk).risk||(x as Event).label}</div>
              </div>
            )
          })()}
        </div>
      </div>
      <div style={{display:"flex",flexWrap:"wrap",gap:16,padding:"10px 4px 2px 92px",fontFamily:"var(--font-mono)",fontSize:9.5,letterSpacing:".04em"}}>
        {[["AVERTED",STATUS.AVERTED],["MITIGATED",STATUS.MITIGATED],["OPEN · standing",STATUS.OPEN]].map(([l,c])=>(
          <span key={l} style={{display:"inline-flex",alignItems:"center",gap:5}}>
            <span style={{width:8,height:8,borderRadius:2,transform:"rotate(45deg)",border:`2px solid ${c}`,background:"#0a1016"}}/>
            <span style={{color:"#8593a6"}}>{l}</span>
          </span>
        ))}
      </div>
    </section>
  )
}

function RiskByLane({sevFocus="all",query,onOpen}:{sevFocus:string;query:string;onOpen:(x:LedgerItem)=>void}){
  return(
    <section style={{border:"1px solid #243042",borderRadius:14,padding:"14px 14px 10px",
      background:"linear-gradient(160deg,rgba(255,255,255,.05),rgba(255,255,255,.01) 38%,rgba(0,0,0,.18)),linear-gradient(165deg,#11181f,#0a1016)",
      boxShadow:"inset 0 1px 0 rgba(255,255,255,.08),inset 0 -2px 8px rgba(0,0,0,.5),0 5px 16px rgba(0,0,0,.4)"}}>
      <div style={{display:"flex",flexWrap:"wrap",alignItems:"baseline",gap:10,marginBottom:10}}>
        <span style={{fontFamily:"var(--font-mono)",fontSize:12,letterSpacing:".08em",color:C.red,fontWeight:700}}>RISK REGISTER</span>
        <span style={{fontSize:10,color:"#8593a6"}}>by lane — ring = status · tap → card</span>
      </div>
      <div style={{display:"flex",flexDirection:"column",gap:8}}>
        {SEV_ORDER.map(sev=>{
          const dimLane=sevFocus!=="all"&&sev!==sevFocus
          const items=RISKS.filter(r=>r.sev===sev).sort((a,b)=>Date.parse(a.date)-Date.parse(b.date))
          return(
            <div key={sev} style={{display:"flex",alignItems:"center",gap:10,padding:"7px 10px",borderRadius:8,
              border:`1px solid ${SEV[sev]}2e`,borderLeft:`3px solid ${SEV[sev]}`,
              background:"linear-gradient(180deg,rgba(255,255,255,.015),rgba(0,0,0,.12))",
              opacity:dimLane?0.22:1,pointerEvents:dimLane?"none":"auto",transition:"opacity .3s"}}>
              <div style={{flex:"0 0 96px",display:"flex",flexDirection:"column",lineHeight:1.15}}>
                <span style={{fontFamily:"var(--font-mono)",fontSize:10.5,fontWeight:700,color:SEV[sev]}}>⚠ {sev}</span>
                <span style={{fontFamily:"var(--font-mono)",fontSize:8,color:"#707e92",letterSpacing:".07em"}}>{SEV_NAME[sev]} · {items.length}</span>
              </div>
              <div style={{display:"flex",flexWrap:"wrap",gap:6,flex:"1 1 auto",minWidth:0}}>
                {items.map(r=>{
                  const dim=!matchQ(r as unknown as Record<string,unknown>,query)
                  const sc=STATUS[r.status]
                  const li=LEDGER.findIndex(x=>x.id===r.id)
                  return(
                    <button key={r.id} onClick={()=>onOpen(LEDGER[li])} data-pulse={r.status==="OPEN"?"":undefined}
                      style={{display:"inline-flex",alignItems:"center",gap:7,padding:"4px 9px 4px 5px",borderRadius:6,cursor:"pointer",
                        border:`1px solid ${sc}55`,background:`${SEV[sev]}10`,fontFamily:"var(--font-mono)",
                        opacity:dim?0.22:1,pointerEvents:dim?"none":"auto",transition:"opacity .3s",
                        animation:r.status==="OPEN"?"obs-pulse 1.8s infinite":"none"}}
                      onMouseEnter={ev=>(ev.currentTarget as HTMLButtonElement).style.borderColor=sc}
                      onMouseLeave={ev=>(ev.currentTarget as HTMLButtonElement).style.borderColor=`${sc}55`}>
                      <span style={{flex:"0 0 auto",width:13,height:13,transform:"rotate(45deg)",background:SEV[sev],border:`2px solid ${sc}`,boxShadow:`0 0 6px -1px ${SEV[sev]}`}}/>
                      <span style={{fontSize:10,color:"#cbd5e1",maxWidth:230,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{r.risk}</span>
                      <span style={{flex:"0 0 auto",fontSize:8.5,color:sc}}>{r.status}</span>
                    </button>
                  )
                })}
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}

// ── App + page export ─────────────────────────────────────────────────────────
const ATM: Record<string,string>={
  deepspace:"radial-gradient(1200px 820px at 70% -8%,#0a1622 0%,#020408 62%)",
  blueprint:"radial-gradient(1200px 820px at 70% -8%,#0c1a33 0%,#05091a 60%)",
  phosphor:"radial-gradient(1200px 820px at 70% -8%,#0a1a10 0%,#04080a 62%)",
}
const VIVID=(v:number)=>{const f=Math.max(0,Math.min(100,v))/100;return`saturate(${(0.55+f*0.95).toFixed(2)}) contrast(${(0.96+f*0.16).toFixed(2)}) brightness(${(0.96+f*0.1).toFixed(2)})`}

export default function ObservatoryPage(){
  const [mode,setMode]=useState("glance")
  const [focus,setFocus]=useState("all")
  const [view,setView]=useState("week")
  const [replay,setReplay]=useState<"all"|number>("all")
  const [legendOpen,setLegendOpen]=useState(true)
  const [sheet,setSheet]=useState<SheetItem|null>(null)
  const [query,setQuery]=useState("")
  const [face,setFace]=useState("trajectory")
  const [riskSel,setRiskSel]=useState(0)
  const [sevFocus,setSevFocus]=useState("all")
  const [riskWin,setRiskWin]=useState(14)
  const [tweaks,setTweaks]=useState({atmosphere:"phosphor",vividness:51})

  // Apply bg on atm change
  useEffect(()=>{
    if(typeof document!=="undefined")
      document.body.style.background=ATM[tweaks.atmosphere]||ATM.deepspace
    return()=>{document.body.style.background=""}
  },[tweaks.atmosphere])

  const replayRef=useRef(replay); replayRef.current=replay
  const sheetRef=useRef(sheet); sheetRef.current=sheet
  const modeRef=useRef(mode); modeRef.current=mode
  const focusRef=useRef(focus); focusRef.current=focus
  const riskSelRef=useRef(riskSel); riskSelRef.current=riskSel

  useEffect(()=>{
    const FOCUS_SEQ=["all","L5","L4","L3","L2","L1"]
    const RKS=[...RISKS].sort((a,b)=>Date.parse(a.date)-Date.parse(b.date))
    const eventIdxs=LEDGER.map((x,i)=>x.kind==="event"?i:-1).filter(i=>i>=0)
    const onKey=(e:KeyboardEvent)=>{
      const t=e.target as HTMLElement
      if(t&&(t.tagName==="INPUT"||t.tagName==="TEXTAREA"||t.isContentEditable))return
      if(e.key===" "||e.code==="Space"){e.preventDefault();setLegendOpen(v=>!v);return}
      if(e.key==="Escape"){if(sheetRef.current)setSheet(null);return}
      if(modeRef.current==="risk"){
        if(e.key==="ArrowRight"){e.preventDefault();const ni=Math.min(RKS.length-1,riskSelRef.current+1);setRiskSel(ni);if(sheetRef.current){const li=LEDGER.findIndex(x=>x.id===RKS[ni].id);setSheet(LEDGER[li])}}
        else if(e.key==="ArrowLeft"){e.preventDefault();const ni=Math.max(0,riskSelRef.current-1);setRiskSel(ni);if(sheetRef.current){const li=LEDGER.findIndex(x=>x.id===RKS[ni].id);setSheet(LEDGER[li])}}
        else if(e.key==="ArrowUp"||e.key==="ArrowDown"){e.preventDefault();const SEQ=["all","RUIN","HIGH","MED"];const d=e.key==="ArrowDown"?1:-1;setSevFocus(s=>SEQ[Math.max(0,Math.min(SEQ.length-1,SEQ.indexOf(s)+d))])}
        else if(e.key==="Enter"){e.preventDefault();if(sheetRef.current)setSheet(null);else{const r=RKS[riskSelRef.current];const li=LEDGER.findIndex(x=>x.id===r.id);setSheet(LEDGER[li])}}
        return
      }
      if(modeRef.current==="chain"){
        if(e.key==="ArrowRight"){e.preventDefault();const cur=replayRef.current;const pos=cur==="all"?-1:eventIdxs.indexOf(cur);const next=eventIdxs[Math.min(eventIdxs.length-1,pos+1)];setReplay(next);if(sheetRef.current)setSheet(LEDGER[next])}
        else if(e.key==="ArrowLeft"){e.preventDefault();const cur=replayRef.current;const pos=cur==="all"?-1:eventIdxs.indexOf(cur);const next=eventIdxs[Math.max(0,(pos<0?0:pos)-1)];setReplay(next);if(sheetRef.current)setSheet(LEDGER[next])}
        else if(e.key==="ArrowDown"){e.preventDefault();setFocus(f=>FOCUS_SEQ[Math.min(FOCUS_SEQ.length-1,FOCUS_SEQ.indexOf(f)+1)])}
        else if(e.key==="ArrowUp"){e.preventDefault();setFocus(f=>FOCUS_SEQ[Math.max(0,FOCUS_SEQ.indexOf(f)-1)])}
        else if(e.key==="Enter"){e.preventDefault();if(sheetRef.current)setSheet(null);else{const cur=replayRef.current;setSheet(LEDGER[cur==="all"?eventIdxs[0]:cur])}}
        return
      }
      if(e.key==="ArrowRight"){
        e.preventDefault()
        const steps=stepIndices(focusRef.current)
        const cur=replayRef.current
        const p=cur==="all"?-1:steps.indexOf(cur as number)
        const next=steps[Math.min(steps.length-1,p+1)]
        setReplay(next)
        if(sheetRef.current)setSheet(LEDGER[next])
      }else if(e.key==="ArrowLeft"){
        e.preventDefault()
        const steps=stepIndices(focusRef.current)
        const cur=replayRef.current
        if(cur==="all")return
        const p=steps.indexOf(cur as number)
        if(p<=0){setReplay("all");if(sheetRef.current)setSheet(null)}
        else{const next=steps[p-1];setReplay(next);if(sheetRef.current)setSheet(LEDGER[next])}
      }else if(e.key==="ArrowDown"){e.preventDefault();setFocus(f=>FOCUS_SEQ[Math.min(FOCUS_SEQ.length-1,FOCUS_SEQ.indexOf(f)+1)])}
      else if(e.key==="ArrowUp"){e.preventDefault();setFocus(f=>FOCUS_SEQ[Math.max(0,FOCUS_SEQ.indexOf(f)-1)])}
      else if(e.key==="Enter"){e.preventDefault();if(sheetRef.current)setSheet(null);else{const cur=replayRef.current;const steps=stepIndices(focusRef.current);setSheet(LEDGER[cur==="all"?steps[0]:cur as number])}}
    }
    window.addEventListener("keydown",onKey)
    return()=>window.removeEventListener("keydown",onKey)
  },[])

  const openSheet=useCallback((x:unknown)=>setSheet(x as SheetItem),[])

  return(
    <>
      <style>{OBS_CSS}</style>
      <div style={{minHeight:"100vh",color:"var(--fg1)",fontFamily:"var(--font-mono)",overflowY:"scroll"}}>
        {/* sticky header */}
        <div style={{position:"sticky",top:0,zIndex:40,background:"linear-gradient(180deg,rgba(2,4,8,.96) 70%,rgba(2,4,8,0))",paddingBottom:8}}>
          <div style={{width:"min(880px,100%)",margin:"0 auto",padding:"0 16px",boxSizing:"border-box"}}>
            {/* header */}
            <header style={{display:"flex",alignItems:"baseline",gap:14,padding:"12px 0 10px",flexWrap:"wrap"}}>
              <h1 style={{fontSize:14,letterSpacing:".04em",margin:0,fontWeight:600,color:C.cyan}}>
                ARCS v9 <span style={{color:"#475569"}}>·</span> <span style={{color:"#e2e8f0"}}>OBSERVATORY</span>
              </h1>
              <span style={{color:"#8593a6",fontSize:11}}>Forensic reconstruction — 5 altitudes · scored · provenance-cited · reusable</span>
            </header>
            <ControlBar mode={mode} setMode={setMode} focus={focus} setFocus={setFocus} sevFocus={sevFocus} setSevFocus={setSevFocus}
              view={view} setView={setView} riskWin={riskWin} setRiskWin={setRiskWin}
              legendOpen={legendOpen} setLegendOpen={setLegendOpen} query={query} setQuery={setQuery}
              face={face} setFace={setFace}/>
            <Legend open={legendOpen}/>
          </div>
        </div>

        {/* stage */}
        <div style={{padding:"18px 0 80px",filter:VIVID(tweaks.vividness),transition:"filter .3s"}}>
          <div style={{width:"min(880px,100%)",margin:"0 auto",padding:"0 16px",boxSizing:"border-box",display:"flex",flexDirection:"column",gap:20}}>
            {mode==="glance"&&<>
              <Timeline replay={replay} setReplay={setReplay} view={view} query={query} face={face} focus={focus} onOpen={openSheet}/>
              <Deck focus={focus} query={query} onOpen={openSheet as (x:Finding)=>void}/>
            </>}
            {mode==="chain"&&(face==="altitude"
              ?<FocusedAltitudeStrip focus={focus} visibleCount={LEDGER.length} query={query} onOpen={openSheet}/>
              :<ChainOfEvents focus={focus} query={query} current={replay} setCurrent={(v)=>setReplay(v)} onOpen={openSheet}/>)}
            {mode==="risk"&&(face==="altitude"
              ?<RiskByLane sevFocus={sevFocus} query={query} onOpen={openSheet}/>
              :<RiskLanes query={query} sel={riskSel} setSel={setRiskSel} sevFocus={sevFocus} win={riskWin} onOpen={openSheet}/>)}
          </div>
        </div>

        <Sheet item={sheet} onClose={()=>setSheet(null)}/>

        {/* tweaks corner */}
        <div style={{position:"fixed",bottom:16,right:16,zIndex:45,display:"flex",flexDirection:"column",alignItems:"flex-end",gap:8}}>
          <div style={{background:"linear-gradient(180deg,#0e151e,#0a1016)",border:"1px solid #22324d",borderRadius:10,padding:"10px 14px",display:"flex",flexDirection:"column",gap:8}}>
            <span style={{fontFamily:"var(--font-mono)",fontSize:9,letterSpacing:".1em",color:"#707e92",textTransform:"uppercase"}}>Atmosphere</span>
            <div style={{display:"flex",gap:5}}>
              {(["deepspace","blueprint","phosphor"] as const).map(atm=>{
                const on=tweaks.atmosphere===atm
                return<button key={atm} onClick={()=>setTweaks(t=>({...t,atmosphere:atm}))} style={{padding:"3px 7px",borderRadius:5,border:`1px solid ${on?C.cyan:"#1e293b"}`,background:on?`${C.cyan}18`:"transparent",color:on?C.cyan:"#8593a6",fontFamily:"var(--font-mono)",fontSize:9,cursor:"pointer",transition:"all .14s"}}>{atm}</button>
              })}
            </div>
            <span style={{fontFamily:"var(--font-mono)",fontSize:9,letterSpacing:".1em",color:"#707e92",textTransform:"uppercase"}}>Vividness {tweaks.vividness}</span>
            <input type="range" min={0} max={100} value={tweaks.vividness} onChange={e=>setTweaks(t=>({...t,vividness:Number(e.target.value)}))}
              style={{width:"100%",accentColor:C.cyan}}/>
          </div>
        </div>
      </div>
    </>
  )
}
