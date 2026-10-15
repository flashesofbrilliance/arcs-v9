# Backlog hindcast v1, run once on 2026-10-15 (evidence for _PROPOSALS/2026-10-15-next-measurements.json, control M5h).
# Reads _QUEUE/induced-backlog.jsonl through git history, time-locked. Pass line fixed before computing: AUC 0.60 and permutation p 0.05.
# Not a registered tool. Stdlib only. Run from the repo root: python3 _PROPOSALS/evidence/backlog-hindcast-v1.py
import subprocess,json,re,collections,random,datetime as dt,bisect,statistics
random.seed(27)
log=subprocess.run(['git','log','--format=%h %ct','--','_QUEUE/induced-backlog.jsonl'],capture_output=True,text=True).stdout.split('\n')
commits=[(l.split()[0],int(l.split()[1])) for l in log if l.strip()][::-1]
def load(h):
    t=subprocess.run(['git','show',h+':_QUEUE/induced-backlog.jsonl'],capture_output=True,text=True).stdout
    rows={}
    for l in t.split('\n'):
        l=l.strip()
        if not l: continue
        try: r=json.loads(l)
        except: continue
        if isinstance(r,dict) and r.get('id'): rows[r['id']]=r
    return rows
snaps=[(t,load(h)) for h,t in commits]
times=[t for t,_ in snaps]
TERM={'DONE','COMPOSTED','SUPERSEDED'}
def word(r):
    s=str(r.get('state') or r.get('status') or '').strip().upper()
    m=re.match(r'[A-Z]+',s); return m.group(0) if m else ''
def terminal(r): return word(r) in TERM
first={}
for t,rows in snaps:
    for i in rows: first.setdefault(i,t)
def snap_at(t):
    k=bisect.bisect_right(times,t)-1
    return snaps[k] if k>=0 else None
def mins(s):
    if not isinstance(s,str): return None
    m=re.match(r'\s*(\d+(?:\.\d+)?)\s*(min|h|hr|hour|d|day)',s)
    if not m: return None
    v=float(m.group(1)); u=m.group(2); return v*(1 if u=='min' else 60 if u[0]=='h' else 480)
H=14*86400
day=86400
anchors=[times[0]+d*day for d in range(7,48,7)]
data=[]  # (T, id, feats, label)
for T in anchors:
    s=snap_at(T); f=snap_at(T+H)
    if not s or not f or T+H>times[-1]: continue
    ts,rows=s; tf,rowsf=f
    for i,r in rows.items():
        if terminal(r): continue
        feats={'age':(T-first[i])/day,'has_cost':1 if mins(r.get('cost_prior')) is not None else 0,
               'cost_cheap':-(mins(r.get('cost_prior')) if mins(r.get('cost_prior')) is not None else -1),
               'n_gates':-len(r.get('gates') or []),
               'ripe':1 if (r.get('depends_on') and all(terminal(rows[d]) for d in r['depends_on'] if d in rows)) else 0,
               'has_trigger':1 if r.get('trigger') else 0,
               'open_word':1 if word(r)=='OPEN' else 0}
        lab=1 if (i in rowsf and terminal(rowsf[i])) else 0
        data.append((T,i,feats,lab))
print('anchors used',len({d[0] for d in data}),'candidate-rows',len(data),'positives',sum(d[3] for d in data),'base rate %.3f'%(sum(d[3] for d in data)/len(data)))
def auc(scores,labels):
    pos=[s for s,l in zip(scores,labels) if l]; neg=[s for s,l in zip(scores,labels) if not l]
    if not pos or not neg: return None
    w=0
    for p in pos:
        for n in neg: w+= 1 if p>n else 0.5 if p==n else 0
    return w/(len(pos)*len(neg))
def pooled(fn,labs_by_T):
    tot=0;wt=0
    for T,(sc,lb) in labs_by_T.items():
        a=auc(sc,lb)
        if a is None: continue
        n=sum(lb)*(len(lb)-sum(lb)); tot+=a*n; wt+=n
    return tot/wt if wt else None
byT=collections.defaultdict(list)
for T,i,f,l in data: byT[T].append((f,l))
for fname in ['age','has_cost','cost_cheap','n_gates','ripe','has_trigger','open_word']:
    sc={T:([x[0][fname] for x in v],[x[1] for x in v]) for T,v in byT.items()}
    obs=pooled(None,sc)
    ge=0; N=1000
    for _ in range(N):
        sh={}
        for T,(s,l) in sc.items():
            l2=l[:]; random.shuffle(l2); sh[T]=(s,l2)
        if pooled(None,sh)>=obs: ge+=1
    p=(ge+1)/(N+1)
    # random-direction check: also report inverted
    print('%-12s AUC %.3f  perm p=%.3f  %s'%(fname,obs,p,'PASS' if obs>=0.60 and p<0.05 else ('inverse signal' if obs<=0.40 and p>0.95 else 'drop')))
print('--- variance check')
for fname in ['ripe','has_trigger','has_cost','open_word']:
    vals=collections.Counter(d[2][fname] for d in data); print(fname,dict(vals))
sc={T:([x[0]['has_cost'] for x in v],[x[1] for x in v]) for T,v in byT.items()}
obs=pooled(None,sc); le=0;N=2000
for _ in range(N):
    sh={}
    for T,(s,l) in sc.items():
        l2=l[:]; random.shuffle(l2); sh[T]=(s,l2)
    if pooled(None,sh)<=obs: le+=1
print('has_cost left-tail perm p=%.4f (AUC %.3f)'%((le+1)/(N+1),obs))
pos=[d for d in data if d[3]]; print('positives with cost',sum(d[2]['has_cost'] for d in pos),'of',len(pos),'; all candidates with cost',sum(d[2]['has_cost'] for d in data),'of',len(data))
