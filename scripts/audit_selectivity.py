#!/usr/bin/env python3
import json, glob, math
def wilson(k,n,z=1.96):
    if n==0: return (None,None)
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return (max(0,c-h),min(1,c+h))
def pct(a,b): return round(100*a/b,1) if b else None
def ci(w,n):
    c=wilson(w,n); return f"{pct(w,n)}% CI[{round(c[0]*100,1)}-{round(c[1]*100,1)}]"
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

print("Selectivity rule candidates (full forward 08-01..15, decided):")
print("="*72)
rules=[
 ("BASELINE (all)", lambda s: True),
 ("skip RANGING+ALIGNED", lambda s: not (s.get('marketRegime')=='RANGING' and s.get('structureVerdict')=='ALIGNED')),
 ("keep TRENDING only", lambda s: s.get('marketRegime')=='TRENDING'),
 ("keep TRENDING+ALIGNED", lambda s: s.get('marketRegime')=='TRENDING' and s.get('structureVerdict')=='ALIGNED'),
 ("keep TRENDING+MIXED/ALIGNED", lambda s: s.get('marketRegime')=='TRENDING' and s.get('structureVerdict') in ('ALIGNED','MIXED')),
 ("skip RANGING+ALIGNED & FOREX", lambda s: not ((s.get('marketRegime')=='RANGING' and s.get('structureVerdict')=='ALIGNED') or asset(s)=='FOREX')),
 ("keep AGAINST (any regime)", lambda s: s.get('structureVerdict')=='AGAINST'),
 ("keep NOT-ALIGNED", lambda s: s.get('structureVerdict')!='ALIGNED'),
]
for lbl, fn in rules:
    sub=[s for s in R if fn(s)]
    w=W(sub); c=wilson(w,len(sub))
    flag = "  << CI ABOVE 55.6" if c[0]*100>55.6 else ("  (CI touches 55.6)" if c[1]*100>=55.6 and pct(w,len(sub))>55.6 else "")
    print(f"  {lbl:32s} n={len(sub):5d} WR={pct(w,len(sub)):5.1f}% CI[{round(c[0]*100,1)}-{round(c[1]*100,1)}]{flag}")

print()
print("Post-calibration era (08-10..15) rules:")
print("="*72)
post=[s for s in R if (s.get('timestamp') or '')>='2026-08-10T00:00']
for lbl, fn in rules:
    sub=[s for s in post if fn(s)]
    if not sub: continue
    w=W(sub); c=wilson(w,len(sub))
    flag = "  << CI ABOVE 55.6" if c[0]*100>55.6 else ("  (CI touches 55.6)" if c[1]*100>=55.6 and pct(w,len(sub))>55.6 else "")
    print(f"  {lbl:32s} n={len(sub):5d} WR={pct(w,len(sub)):5.1f}% CI[{round(c[0]*100,1)}-{round(c[1]*100,1)}]{flag}")
