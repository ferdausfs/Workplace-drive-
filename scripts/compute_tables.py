#!/usr/bin/env python3
import json, glob, math
def wilson(k,n,z=1.96):
    if n==0: return (None,None)
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return (max(0,c-h),min(1,c+h))
def pct(a,b): return round(100*a/b,1) if b else None
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
def confnum(s):
    v=s.get('confidence')
    if isinstance(v,(int,float)): return float(v)
    if isinstance(v,str):
        try: return float(v.rstrip('%'))
        except: return None
    return None

print("structWR per regime (FULL forward 08-01..15, decided):")
print("="*72)
for reg in ['RANGING','TRENDING','BREAKOUT','VOLATILE']:
    sub=[s for s in R if s.get('marketRegime')==reg]
    if not sub: continue
    print(f"-- {reg}: total n={len(sub)} WR={pct(W(sub),len(sub))}%")
    for sv in ['ALIGNED','AGAINST','MIXED','NEUTRAL']:
        gg=[s for s in sub if s.get('structureVerdict')==sv]
        if gg:
            c=wilson(W(gg),len(gg))
            print(f"   {sv:9s} n={len(gg):5d} WR={pct(W(gg),len(gg)):5.1f}% CI[{round(c[0]*100,1)}-{round(c[1]*100,1)}]")

print()
print("structWR per regime (POST-calib era 08-10..15 only):")
print("="*72)
post=[s for s in R if (s.get('timestamp') or '')>='2026-08-10T00:00']
for reg in ['RANGING','TRENDING','BREAKOUT']:
    sub=[s for s in post if s.get('marketRegime')==reg]
    if not sub: continue
    print(f"-- {reg}: total n={len(sub)} WR={pct(W(sub),len(sub))}%")
    for sv in ['ALIGNED','AGAINST','MIXED','NEUTRAL']:
        gg=[s for s in sub if s.get('structureVerdict')==sv]
        if gg:
            c=wilson(W(gg),len(gg))
            print(f"   {sv:9s} n={len(gg):5d} WR={pct(W(gg),len(gg)):5.1f}% CI[{round(c[0]*100,1)}-{round(c[1]*100,1)}]")

print()
print("confBucket WR per era (for reference — recalibration):")
print("="*72)
for en,fn in [('PRE (08-01..09)', lambda s:(s.get('timestamp') or '')<'2026-08-10T00:00'),
              ('POST (08-10..15)', lambda s:(s.get('timestamp') or '')>='2026-08-10T00:00')]:
    sub=[s for s in R if fn(s)]
    print(f"-- {en}: n={len(sub)}")
    for lo,hi,lbl in [(72,75,'72-75'),(76,79,'76-79'),(80,83,'80-83'),(84,87,'84-87'),(88,101,'88+')]:
        gg=[s for s in sub if confnum(s) is not None and lo<=confnum(s)<hi]
        if gg: print(f"   {lbl:5s} n={len(gg):5d} WR={pct(W(gg),len(gg)):5.1f}%")

print()
print("Breakeven-nearest cells (regime x structure, n>=100):")
print("="*72)
cells=[]
for reg in ['RANGING','TRENDING']:
    for sv in ['ALIGNED','AGAINST','MIXED','NEUTRAL']:
        gg=[s for s in R if s.get('marketRegime')==reg and s.get('structureVerdict')==sv]
        if len(gg)>=100:
            cells.append((f"{reg}/{sv}", gg))
cells.sort(key=lambda x: -W(x[1])/len(x[1]))
for lbl, gg in cells:
    c=wilson(W(gg),len(gg))
    print(f"  {lbl:24s} n={len(gg):5d} WR={pct(W(gg),len(gg)):5.1f}% CI[{round(c[0]*100,1)}-{round(c[1]*100,1)}]")
