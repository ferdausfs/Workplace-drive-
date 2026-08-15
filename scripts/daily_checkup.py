#!/usr/bin/env python3
"""Daily routine checkup — 2026-08-15 (Arena main agent). Fresh live snapshot analysis."""
import json, glob, math
from collections import Counter

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
for f in sorted(glob.glob('phase_f_forward/*/*.json')):
    b=f.split('/')[-1]
    if b in ('health.json','pairs.json'): continue
    try: d=json.load(open(f))
    except: continue
    rows += d.get('signals') or []
seen={}
for s in rows:
    if s.get('id'): seen[s['id']]=s
allrows=list(seen.values())
R=[s for s in allrows if (s.get('timestamp') or '')>='2026-08-01' and s.get('result') in ('WIN','LOSS')]
W=lambda sub: sum(1 for s in sub if s['result']=='WIN')
BREAK=55.6

print("="*72)
print("DAILY CHECKUP — 2026-08-15 (UTC) — fresh live snapshot")
print("="*72)
print(f"unique signals (all): {len(allrows)} | forward decided (WIN/LOSS): {len(R)}")
# day coverage
days=sorted({(s.get('timestamp') or '')[:10] for s in allrows if (s.get('timestamp') or '')>='2026-08-01'})
print(f"forward days covered: {days[0]} → {days[-1]}")

print("\n--- overall forward WR ---")
print(f"  {ci(W(R), len(R))}   (breakeven {BREAK}%)")

print("\n--- decided WR by day (signal day) ---")
for d in days:
    sub=[s for s in R if (s.get('timestamp') or '').startswith(d)]
    w=W(sub)
    flag = ""
    if len(sub)>=30:
        c=wilson(w,len(sub))
        if c[0]*100>BREAK: flag="  << CI above breakeven"
    print(f"  {d}: n={len(sub):4d} WR={pct(w,len(sub)):5.1f}%{flag}")

print("\n--- pre/post round-3 ---")
for lbl, fn in [('pre', lambda s:(s.get('timestamp') or '')<'2026-08-06T19:00'),
                ('post', lambda s:(s.get('timestamp') or '')>='2026-08-06T19:00')]:
    sub=[s for s in R if fn(s)]
    print(f"  {lbl:5s} n={len(sub):4d} WR={ci(W(sub),len(sub))}")

print("\n--- asset x direction ---")
for at in ['CRYPTO','FOREX']:
    for dirc in ['BUY','SELL']:
        sub=[s for s in R if asset(s)==at and s.get('direction')==dirc]
        if sub: print(f"  {at:7s} {dirc:4s} n={len(sub):4d} WR={ci(W(sub),len(sub))}")

print("\n" + "="*72)
print("🔑 V6.10.2 FIX VERIFICATION — PENDING_ENTRY unfilled (deploy 08-14T13:10Z)")
print("="*72)
# all rows (incl TIE) since deploy
post_dep=[s for s in allrows if (s.get('timestamp') or '')>='2026-08-14T13:10']
pe=[s for s in post_dep if s.get('fillStatus')=='PENDING_ENTRY']
pe_unfilled=[s for s in pe if s.get('entryHit') is False]
print(f"post-deploy resolved rows: {len(post_dep)}")
print(f"  PENDING_ENTRY rows: {len(pe)}")
print(f"  PENDING_ENTRY + entryHit=false (unfilled): {len(pe_unfilled)}")
res=Counter(s.get('result') for s in pe_unfilled)
print(f"  unfilled result distribution: {dict(res)}")
# before deploy, unfilled -> WIN 100% (n=43). Now should be TIE.
if pe_unfilled:
    wins=res.get('WIN',0); ties=res.get('TIE',0)
    print(f"  => fix working: {ties} TIE / {wins} WIN  (before fix: 43/43 WIN)")
    verdict = "✅ FIX CONFIRMED LIVE" if ties>0 and wins==0 else ("⚠️ PARTIAL — some unfilled still WIN" if wins>0 else "⏳ no TIE yet but 0 WIN too")
    print(f"  => {verdict}")
else:
    print("  ⏳ no unfilled PENDING_ENTRY resolved since deploy yet (small window)")

# PENDING_ENTRY WR pre vs post deploy (all decided)
print("\n-- PENDING_ENTRY slice WR: pre-fix vs post-fix --")
pe_pre=[s for s in R if s.get('fillStatus')=='PENDING_ENTRY' and (s.get('timestamp') or '')<'2026-08-14T13:10']
pe_post=[s for s in R if s.get('fillStatus')=='PENDING_ENTRY' and (s.get('timestamp') or '')>='2026-08-14T13:10']
print(f"  pre-fix  PE n={len(pe_pre):4d} WR={ci(W(pe_pre),len(pe_pre))}  (inflated by mechanical WIN)")
print(f"  post-fix PE n={len(pe_post):4d} WR={ci(W(pe_post),len(pe_post))}  (honest — TIE excluded)")

print("\n" + "="*72)
print("NEW DATA SINCE LAST SNAPSHOT (08-14 ~09:55Z → now)")
print("="*72)
new=[s for s in R if (s.get('timestamp') or '')>='2026-08-14T09:55']
print(f"new decided rows: {len(new)} | WR={ci(W(new),len(new))}")
for d in ['2026-08-14','2026-08-15']:
    sub=[s for s in new if (s.get('timestamp') or '').startswith(d)]
    print(f"  {d}: n={len(sub):4d} WR={pct(W(sub),len(sub)):5.1f}%")

print("\n--- top pairs (full forward) ---")
for p,n in Counter(s.get('pair') for s in R).most_common(6):
    sub=[s for s in R if s.get('pair')==p]
    print(f"  {p:9s} n={n:4d} WR={pct(W(sub),n):5.1f}%")

print("\n--- FIX-EH corrected (legacy-annotated rows) ---")
eh=[s for s in R if 'entryHitLegacy' in s and s.get('entryHit') is not None]
for v,t in [(True,'HIT '),(False,'MISS')]:
    sub=[s for s in eh if s.get('entryHit') is v]
    print(f"  corrected {t} n={len(sub):4d} WR={ci(W(sub),len(sub))}")

print("\nNOTE: gate = CI_lo > 55.6% with n≥30. No premature conclusions.")
