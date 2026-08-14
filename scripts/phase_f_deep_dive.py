#!/usr/bin/env python3
"""Phase F DEEP DIVE — 2026-08-14 (independent multi-angle passes).
Pass A: round-3 improvement decomposition (composition vs within-class)
Pass B: session slice        Pass C: sessionQuality
Pass D: regime cells (asset x regime x dir, gate >=30/cell)
Pass E: structure / alignment / aiStatus
Pass F: indicator features (rsi/adx/atrPct)
Pass G: permutation test (round-3) + FOREX deep dive
Breakeven 55.6%, Wilson CI 95%. Pre-registered slices only."""
import json, glob, math, random
from collections import Counter

def wilson(k,n,z=1.96):
    if n==0: return (None,None)
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return (max(0,c-h),min(1,c+h))
def pct(a,b): return round(100*a/b,1) if b else None
def ci_str(w,n):
    c=wilson(w,n); return f"{pct(w,n)}% CI[{round(c[0]*100,1)}-{round(c[1]*100,1)}]"
CRYPTO=['BTC','ETH','SOL','DOGE','XRP','ADA','LINK','AVAX','BNB','DOT']
def asset(s):
    if s.get('isOTC'): return 'OTC'
    return 'CRYPTO' if s['pair'].split('/')[0] in CRYPTO else 'FOREX'

rows=[]
for f in sorted(glob.glob('phase_f_forward/2026-08-14/*.json')):
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
BREAK=55.6

print("="*78)
print("PASS A — ROUND-3 IMPROVEMENT DECOMPOSITION (composition vs within-class)")
print("="*78)
pre=[s for s in R if (s.get('timestamp') or '')<'2026-08-06T19:00']
post=[s for s in R if (s.get('timestamp') or '')>='2026-08-06T19:00']
print(f"pre  n={len(pre)}  overall WR={pct(W(pre),len(pre))}%  | forex_share={pct(sum(1 for s in pre if asset(s)=='FOREX'),len(pre))}%")
print(f"post n={len(post)} overall WR={pct(W(post),len(post))}%  | forex_share={pct(sum(1 for s in post if asset(s)=='FOREX'),len(post))}%")
print("\n-- within-class WR (pre vs post) --")
for at in ['CRYPTO','FOREX']:
    pp=[s for s in pre if asset(s)==at]; po=[s for s in post if asset(s)==at]
    print(f"  {at:7s} pre  n={len(pp):4d} WR={ci_str(W(pp),len(pp))}")
    print(f"  {at:7s} post n={len(po):4d} WR={ci_str(W(po),len(po))}")
# standardization: apply pre asset-mix to post within-class WR
pre_crypto_share = sum(1 for s in pre if asset(s)=='CRYPTO')/len(pre)
post_crypto_wr = pct(W([s for s in post if asset(s)=='CRYPTO']), len([s for s in post if asset(s)=='CRYPTO'])) or 0
post_forex_wr = pct(W([s for s in post if asset(s)=='FOREX']), len([s for s in post if asset(s)=='FOREX'])) or 0
standardized = pre_crypto_share*post_crypto_wr + (1-pre_crypto_share)*post_forex_wr
print(f"\n-- decomposition --")
print(f"  if POST had PRE's asset mix: WR would be ~{round(standardized,1)}%")
print(f"  => mix-shift contributes ~{round((pct(W(post),len(post)) or 0)-standardized,1)}pt of the post-vs-pre change")
print(f"  => within-class improvement is the REST (~{round(standardized-(pct(W(pre),len(pre)) or 0),1)}pt)")

print("\n"+"="*78)
print("PASS B — SESSION slice (24/7=crypto; forex sessions)")
print("="*78)
for sess, n in Counter((s.get('session') or ['?'])[0] for s in R).most_common():
    sub=[s for s in R if (s.get('session') or ['?'])[0]==sess]
    print(f"  {sess:10s} n={len(sub):4d} WR={ci_str(W(sub),len(sub))}")

print("\n"+"="*78)
print("PASS C — SESSION QUALITY (forex only, non-N/A)")
print("="*78)
for q in ['HIGHEST','HIGH','MEDIUM','LOW']:
    sub=[s for s in R if s.get('sessionQuality')==q]
    if sub: print(f"  {q:9s} n={len(sub):4d} WR={ci_str(W(sub),len(sub))}")

print("\n"+"="*78)
print("PASS D — REGIME CELLS (asset x regime x direction, gate >=30/cell)")
print("="*78)
cells=[]
for at in ['CRYPTO','FOREX']:
    for reg in ['RANGING','TRENDING','BREAKOUT','VOLATILE']:
        for dirc in ['BUY','SELL']:
            sub=[s for s in R if asset(s)==at and s.get('marketRegime')==reg and s.get('direction')==dirc]
            if len(sub)>=30:
                cells.append((f"{at}/{reg}/{dirc}", sub))
cells.sort(key=lambda x:-len(x[1]))
for lbl, sub in cells:
    flag = ""
    w=W(sub); c=wilson(w,len(sub))
    if c[0]*100>BREAK: flag="  << ABOVE-BREAKEVEN(CI)"
    print(f"  {lbl:24s} n={len(sub):4d} WR={ci_str(w,len(sub))}{flag}")

print("\n"+"="*78)
print("PASS E — STRUCTURE / ALIGNMENT / AI STATUS")
print("="*78)
print("-- structureVerdict --")
for sv, n in Counter(s.get('structureVerdict') for s in R).most_common():
    sub=[s for s in R if s.get('structureVerdict')==sv]
    print(f"  {str(sv):10s} n={len(sub):4d} WR={ci_str(W(sub),len(sub))}")
print("-- alignment --")
for al, n in Counter(s.get('alignment') for s in R).most_common():
    sub=[s for s in R if s.get('alignment')==al]
    print(f"  {str(al):16s} n={len(sub):4d} WR={ci_str(W(sub),len(sub))}")
print("-- aiStatus --")
for ai, n in Counter(s.get('aiStatus') for s in R).most_common():
    sub=[s for s in R if s.get('aiStatus')==ai]
    print(f"  {str(ai):18s} n={len(sub):4d} WR={ci_str(W(sub),len(sub))}")

print("\n"+"="*78)
print("PASS F — INDICATOR FEATURES (signalIndicators)")
print("="*78)
def num(s, key):
    v=(s.get('signalIndicators') or {}).get(key)
    if isinstance(v,(int,float)): return float(v)
    return None
for key, buckets in [('rsi',[(0,30,'<30'),(30,50,'30-50'),(50,70,'50-70'),(70,101,'>70')]),
                     ('adx',[(0,20,'<20'),(20,40,'20-40'),(40,101,'>40')]),
                     ('atrPct',[(0,0.3,'<0.3'),(0.3,0.7,'0.3-0.7'),(0.7,100,'>0.7')])]:
    print(f"-- {key} --")
    for lo,hi,lbl in buckets:
        sub=[s for s in R if num(s,key) is not None and lo<=num(s,key)<hi]
        if sub: print(f"  {lbl:10s} n={len(sub):4d} WR={ci_str(W(sub),len(sub))}")

print("\n"+"="*78)
print("PASS G — PERMUTATION TEST (round-3) + FOREX deep dive")
print("="*78)
random.seed(42)
obs_diff = pct(W(post),len(post)) - pct(W(pre),len(pre))
labels=[1 if s in post else 0 for s in R]  # careful: use timestamps, not object identity
labels=[1 if (s.get('timestamp') or '')>='2026-08-06T19:00' else 0 for s in R]
wins=[1 if s['result']=='WIN' else 0 for s in R]
n_post=sum(labels); n_pre=len(R)-n_post
def diff_perm():
    idx=list(range(len(R))); random.shuffle(idx)
    w_post=sum(wins[i] for i in idx if labels[i]==1); w_pre=sum(wins[i] for i in idx if labels[i]==0)
    return w_post/n_post - w_pre/n_pre
perms=[diff_perm() for _ in range(5000)]
p_val=sum(1 for p in perms if p>=obs_diff)/len(perms)
print(f"  observed +{round(obs_diff*100,2)}pt | permutation p-value ~{p_val} (n=5000)")
print(f"  => {('SIGNIFICANT (not chance)' if p_val<0.01 else 'NOT significant')}")
print("-- FOREX by session --")
fx=[s for s in R if asset(s)=='FOREX']
for sess, n in Counter((s.get('session') or ['?'])[0] for s in fx).most_common():
    sub=[s for s in fx if (s.get('session') or ['?'])[0]==sess]
    print(f"  FOREX/{sess:9s} n={len(sub):4d} WR={ci_str(W(sub),len(sub))}")
print("-- FOREX by direction x regime --")
for dirc in ['BUY','SELL']:
    for reg in ['RANGING','TRENDING']:
        sub=[s for s in fx if s.get('direction')==dirc and s.get('marketRegime')==reg]
        if len(sub)>=20: print(f"  {dirc:4s}/{reg:8s} n={len(sub):4d} WR={ci_str(W(sub),len(sub))}")
