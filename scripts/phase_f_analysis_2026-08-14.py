#!/usr/bin/env python3
"""Phase F forward analysis — 2026-08-14 (Arena main agent, independent).
Data: fresh live snapshot phase_f_forward/2026-08-14/ (18 pairs, dedup by id).
Honest protocol: decided = WIN/LOSS only; breakeven 55.6% (80% payout);
Wilson CI; forward window 08-01..08-14; no premature conclusions."""
import json, glob, math
from collections import Counter

def wilson(k, n, z=1.96):
    if n == 0: return (None, None)
    p = k/n; d = 1 + z*z/n
    c = (p + z*z/(2*n))/d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return (max(0,c-h), min(1,c+h))

def pct(a,b): return round(100*a/b,1) if b else None

CRYPTO_BASES = ['BTC','ETH','SOL','DOGE','XRP','ADA','LINK','AVAX','BNB','DOT']
def asset(s):
    if s.get('isOTC'): return 'OTC'
    p = s.get('pair','')
    base = p.split('/')[0] if '/' in p else ''
    return 'CRYPTO' if base in CRYPTO_BASES else 'FOREX'

def confnum(s):
    v = s.get('confidence')
    if isinstance(v,(int,float)): return float(v)
    if isinstance(v,str):
        try: return float(v.rstrip('%'))
        except: return None
    return None

def grade_of(s):
    g = s.get('grade')
    return g.get('grade') if isinstance(g,dict) else (g or '?')

rows = []
for f in sorted(glob.glob('phase_f_forward/2026-08-14/*.json')):
    b = f.split('/')[-1]
    if b in ('health.json','pairs.json'): continue
    try: d = json.load(open(f))
    except: continue
    rows += d.get('signals') or []
seen = {}
for s in rows:
    if s.get('id'): seen[s['id']] = s
rows = list(seen.values())

FW = [s for s in rows if (s.get('timestamp') or '') >= '2026-08-01']
dec = [s for s in FW if s.get('result') in ('WIN','LOSS')]
def wsum(sub): return sum(1 for s in sub if s.get('result')=='WIN')

print("="*72)
print("PHASE F FORWARD — 2026-08-14  (18 pairs, live snapshot, dedup by id)")
print("="*72)
print(f"forward-window rows (>=08-01): {len(FW)} | decided: {len(dec)}")
allw = wsum(dec)
ci = wilson(allw, len(dec))
print(f"OVERALL WR: {pct(allw,len(dec))}%  ({allw}/{len(dec)})  CI95 [{round(ci[0]*100,1)}-{round(ci[1]*100,1)}]  breakeven 55.6%")

print("\n-- decided WR by day --")
for d in sorted({(s.get('timestamp') or '')[:10] for s in dec}):
    sub = [s for s in dec if (s.get('timestamp') or '').startswith(d)]
    w = wsum(sub); n = len(sub)
    c = wilson(w,n)
    flag = "  <-- " + ("ABOVE 55.6%" if (pct(w,n) or 0) > 55.6 else "below")
    print(f"  {d}: n={n:4d} WR={pct(w,n):5.1f}%  CI[{round(c[0]*100,1)}-{round(c[1]*100,1)}]{flag}")

print("\n-- by asset class --")
for at in ['CRYPTO','FOREX','OTC']:
    sub = [s for s in dec if asset(s)==at]
    if sub:
        w = wsum(sub); c = wilson(w,len(sub))
        print(f"  {at:7s} n={len(sub):4d} WR={pct(w,len(sub)):5.1f}%  CI[{round(c[0]*100,1)}-{round(c[1]*100,1)}]")

print("\n-- by direction --")
for dirc in ['BUY','SELL']:
    sub = [s for s in dec if s.get('direction')==dirc]
    if sub:
        w = wsum(sub); c = wilson(w,len(sub))
        print(f"  {dirc:5s} n={len(sub):4d} WR={pct(w,len(sub)):5.1f}%  CI[{round(c[0]*100,1)}-{round(c[1]*100,1)}]")

print("\n-- by marketRegime --")
for reg, n in Counter(s.get('marketRegime') for s in dec).most_common():
    sub = [s for s in dec if s.get('marketRegime')==reg]
    w = wsum(sub)
    print(f"  {str(reg):14s} n={n:4d} WR={pct(w,n):5.1f}%")

print("\n-- top pairs by n --")
for p, n in Counter(s.get('pair') for s in dec).most_common(10):
    sub = [s for s in dec if s.get('pair')==p]
    w = wsum(sub)
    print(f"  {p:9s} n={n:4d} WR={pct(w,n):5.1f}%")

print("\n-- confidence buckets --")
for lo,hi,lbl in [(72,101,'>=72 (floor)'),(60,72,'60-71'),(0,60,'<60')]:
    sub = [s for s in dec if confnum(s) is not None and lo<=confnum(s)<hi]
    if sub:
        w = wsum(sub)
        print(f"  {lbl:14s} n={len(sub):4d} WR={pct(w,len(sub)):5.1f}%")

print("\n-- grade buckets --")
for g, n in Counter(grade_of(s) for s in dec).most_common():
    sub = [s for s in dec if grade_of(s)==g]
    w = wsum(sub)
    print(f"  {str(g):8s} n={n:4d} WR={pct(w,n):5.1f}%")

# FIX-EH corrected entryHit
print("\n" + "="*72)
print("FIX-EH — corrected entryHit vs legacy (tautology check)")
print("="*72)
eh_rows = [s for s in dec if 'entryHitLegacy' in s and s.get('entryHit') is not None]
print(f"rows with both entryHit fields (post-FIX-EH deploy ~08-07): {len(eh_rows)}")
for field, lbl in [('entryHitLegacy','LEGACY (old expiry±5min)'), ('entryHit','CORRECTED (re-test)')]:
    for v, tag in [(True,'HIT '),(False,'MISS')]:
        sub = [s for s in eh_rows if s.get(field) is v]
        w = wsum(sub); c = wilson(w,len(sub))
        print(f"  {lbl:26s} {tag} n={len(sub):4d} WR={pct(w,len(sub)):5.1f}%  CI[{round(c[0]*100,1) if c[0] else None}-{round(c[1]*100,1) if c[1] else None}]")

# fillStatus vs corrected hit
print("\n-- fillStatus x corrected entryHit (decided, eh rows) --")
for fs in ['INSTANT','PENDING_ENTRY']:
    sub = [s for s in eh_rows if s.get('fillStatus')==fs]
    if sub:
        w = wsum(sub)
        hit = [s for s in sub if s.get('entryHit') is True]
        hw = wsum(hit)
        print(f"  {fs:14s} n={len(sub):4d} WR={pct(w,len(sub)):5.1f}%  | eh-HIT n={len(hit)} WR={pct(hw,len(hit)):5.1f}%")

print("\n-- pre/post round-3 (deployed ~08-06 19:00 UTC) --")
pre  = [s for s in dec if (s.get('timestamp') or '') < '2026-08-06T19:00']
post = [s for s in dec if (s.get('timestamp') or '') >= '2026-08-06T19:00']
for lbl, sub in [('pre-round3',pre),('post-round3',post)]:
    w = wsum(sub); c = wilson(w,len(sub))
    print(f"  {lbl:13s} n={len(sub):4d} WR={pct(w,len(sub)):5.1f}%  CI[{round(c[0]*100,1)}-{round(c[1]*100,1)}]")

print("\nNOTE: Phase F gate = >=50 obs, >=30/regime cell, 7-14 days, CI vs 55.6%.")
