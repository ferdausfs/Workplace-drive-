#!/usr/bin/env python3
import json, glob, math
from collections import Counter
def wilson(k,n,z=1.96):
    if n==0: return (None,None)
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return (max(0,c-h),min(1,c+h))
def pct(a,b): return round(100*a/b,1) if b else None
def ci(w,n):
    c=wilson(w,n); return f"{pct(w,n)}% CI[{round(c[0]*100,1)}-{round(c[1]*100,1)}]"
def grade_of(s):
    g=s.get('grade'); return g.get('grade') if isinstance(g,dict) else (g or '?')
CRYPTO=['BTC','ETH','SOL','DOGE','XRP','ADA','LINK','AVAX','BNB','DOT']
def asset(s):
    if s.get('isOTC'): return 'OTC'
    return 'CRYPTO' if s['pair'].split('/')[0] in CRYPTO else 'FOREX'

rows=[]
for f in sorted(glob.glob('phase_f_forward/2026-08-15/*.json')):
    b=f.split('/')[-1]
    if b in ('health.json','pairs.json'): continue
    try: d=json.load(open(f))
    except: continue
    rows += d.get('signals') or []
seen={}
for s in rows:
    if s.get('id'): seen[s['id']]=s
R=[s for s in seen.values() if (s.get('timestamp') or '')>='2026-08-01' and s.get('result') in ('WIN','LOSS')]
W=lambda sub: sum(1 for s in sub if s['result']=='WIN')

# grade-label drift day (agents: ~08-10)
print("="*70)
print("A) GRADE LABEL DISTRIBUTION BY DAY (calibration deploy ~08-09/10?)")
print("="*70)
for d in sorted({(s.get('timestamp') or '')[:10] for s in R}):
    sub=[s for s in R if (s.get('timestamp') or '').startswith(d)]
    gs=Counter(grade_of(s) for s in sub)
    n=len(sub)
    print(f"  {d}: n={n:4d} A+={round(100*gs.get('A+',0)/n):3d}% A={round(100*gs.get('A',0)/n):3d}% B={round(100*gs.get('B',0)/n):3d}% C={round(100*gs.get('C',0)/n):3d}%")

print()
print("="*70)
print("B) GRADE WR BY ERA (pre vs post calibration label-shift)")
print("="*70)
# label shift at 08-10T00:00 (A-share collapsed 08-10)
eras=[('PRE-calib (08-01..09)', lambda s:(s.get('timestamp') or '')<'2026-08-10T00:00'),
      ('POST-calib (08-10..15)', lambda s:(s.get('timestamp') or '')>='2026-08-10T00:00')]
for en,fn in eras:
    sub=[s for s in R if fn(s)]
    print(f"-- {en}: n={len(sub)} --")
    for g in ['A+','A','B','C']:
        gg=[s for s in sub if grade_of(s)==g]
        if gg: print(f"   {g:3s} n={len(gg):4d} WR={ci(W(gg),len(gg))}")

print()
print("="*70)
print("C) structureVerdict x marketRegime (inversion = regime artifact?)")
print("="*70)
for reg in ['RANGING','TRENDING','BREAKOUT']:
    for sv in ['ALIGNED','AGAINST','MIXED','NEUTRAL']:
        sub=[s for s in R if s.get('marketRegime')==reg and s.get('structureVerdict')==sv]
        if len(sub)>=30:
            print(f"  {reg:9s} {sv:9s} n={len(sub):4d} WR={ci(W(sub),len(sub))}")

print()
print("="*70)
print("D) confBucket (raw) x era — the confidence inversion")
print("="*70)
def confnum(s):
    v=s.get('confidence')
    if isinstance(v,(int,float)): return float(v)
    if isinstance(v,str):
        try: return float(v.rstrip('%'))
        except: return None
    return None
for en,fn in eras:
    sub=[s for s in R if fn(s)]
    print(f"-- {en} --")
    for lo,hi,lbl in [(72,75,'72-75'),(76,79,'76-79'),(80,83,'80-83'),(84,87,'84-87'),(88,101,'88+')]:
        gg=[s for s in sub if confnum(s) is not None and lo<=confnum(s)<hi]
        if gg: print(f"   {lbl:5s} n={len(gg):4d} WR={ci(W(gg),len(gg))}")
