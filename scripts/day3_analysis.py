#!/usr/bin/env python3
"""Day-3 (2026-08-07) entry-hit + signal analysis — clean by timestamp.
Independent — Arena main agent. Uses the 2026-08-07 snapshot (latest resolution state)."""
import json, glob, math
from collections import Counter

def wilson_ci(k, n, z=1.96):
    if n == 0: return (None, None)
    p = k/n; denom = 1 + z*z/n
    centre = (p + z*z/(2*n))/denom
    half = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/denom
    return (max(0,centre-half), min(1,centre+half))

files = sorted(glob.glob('phase_f_forward/2026-08-07/*.json'))
rows = []
for f in files:
    b = f.split('/')[-1]
    if b in ('health.json','pairs.json'): continue
    try: d = json.load(open(f))
    except: continue
    rows += d.get('signals') or []
seen = {}
for s in rows:
    if s.get('id'): seen[s['id']] = s
rows = list(seen.values())

def day_rows(d):
    return [s for s in rows if (s.get('timestamp') or '').startswith(d)]

print("=== ENTRY-HIT — clean by-timestamp (from 08-07 snapshot) ===")
for day in ['2026-08-05', '2026-08-06', '2026-08-07']:
    dr = day_rows(day)
    decided = [s for s in dr if s.get('result') in ('WIN','LOSS')]
    eh = [s for s in decided if s.get('entryHit') is not None]
    hit = [s for s in eh if s['entryHit'] is True]
    miss = [s for s in eh if s['entryHit'] is False]
    hw = sum(1 for s in hit if s['result']=='WIN'); mw = sum(1 for s in miss if s['result']=='WIN')
    aw = sum(1 for s in decided if s['result']=='WIN')
    hci = wilson_ci(hw, len(hit)); mci = wilson_ci(mw, len(miss))
    def pct(a,b): return round(100*a/b,1) if b else None
    print(f"{day}: rows={len(dr)} decided={len(decided)} ALL_WR={pct(aw,len(decided))}% | "
          f"HIT n={len(hit)} WR={pct(hw,len(hit))}% CI({round(hci[0]*100,1) if hci[0] else None}-{round(hci[1]*100,1) if hci[1] else None}) | "
          f"MISS n={len(miss)} WR={pct(mw,len(miss))}% CI({round(mci[0]*100,1) if mci[0] else None}-{round(mci[1]*100,1) if mci[1] else None}) | "
          f"missRate={pct(len(miss),len(eh))}%")

# combined 3-day
print("\n=== COMBINED 08-05..08-07 ===")
dr3 = [s for s in rows if (s.get('timestamp') or '').startswith(('2026-08-05','2026-08-06','2026-08-07'))]
dec3 = [s for s in dr3 if s.get('result') in ('WIN','LOSS')]
eh3 = [s for s in dec3 if s.get('entryHit') is not None]
h3 = [s for s in eh3 if s['entryHit'] is True]; m3 = [s for s in eh3 if s['entryHit'] is False]
h3w = sum(1 for s in h3 if s['result']=='WIN'); m3w = sum(1 for s in m3 if s['result']=='WIN')
print(f"decided={len(dec3)} | HIT n={len(h3)} WR={round(100*h3w/len(h3),1)}% | MISS n={len(m3)} WR={round(100*m3w/len(m3),1)}% | missRate={round(100*len(m3)/len(eh3),1)}%")

# ---- SIGNAL DATA for 08-07 (full day so far) ----
print("\n=== SIGNAL DATA — 2026-08-07 (UTC partial, snapshot 05:21) ===")
dr = day_rows('2026-08-07')
decided = [s for s in dr if s.get('result') in ('WIN','LOSS')]
w = sum(1 for s in decided if s['result']=='WIN')
print(f"Total: {len(dr)} | decided: {len(decided)} | pending: {len(dr)-len(decided)} | WR: {round(100*w/len(decided),1)}% ({w}/{len(decided)}) | breakeven 55.6%")

print("\n-- by asset class --")
def asset(s):
    p = s.get('pair','')
    if s.get('isOTC'): return 'OTC'
    if any(x in p for x in ['BTC','ETH','SOL','DOGE','XRP','ADA','LINK','AVAX','BNB','DOT']): return 'CRYPTO'
    return 'FOREX'
for at in ['CRYPTO','FOREX','OTC']:
    sub = [s for s in decided if asset(s)==at]
    if sub:
        sw = sum(1 for s in sub if s['result']=='WIN')
        print(f"  {at:8s} n={len(sub):4d} WR={round(100*sw/len(sub),1)}%")

print("\n-- by direction --")
for dirc in ['BUY','SELL']:
    sub = [s for s in decided if s.get('direction')==dirc]
    if sub:
        sw = sum(1 for s in sub if s['result']=='WIN')
        print(f"  {dirc:5s} n={len(sub):4d} WR={round(100*sw/len(sub),1)}%")

print("\n-- by marketRegime --")
for reg, n in Counter(s.get('marketRegime') for s in decided).most_common():
    sub = [s for s in decided if s.get('marketRegime')==reg]
    sw = sum(1 for s in sub if s['result']=='WIN')
    print(f"  {str(reg):12s} n={n:4d} WR={round(100*sw/n,1)}%")

print("\n-- forex pairs (decided) --")
for p, n in Counter(s.get('pair') for s in decided if asset(s)=='FOREX').most_common():
    sub = [s for s in decided if s.get('pair')==p]
    sw = sum(1 for s in sub if s['result']=='WIN')
    print(f"  {p:9s} n={n:4d} WR={round(100*sw/n,1)}%")

print("\n-- crypto pairs (decided) --")
for p, n in Counter(s.get('pair') for s in decided if asset(s)=='CRYPTO').most_common():
    sub = [s for s in decided if s.get('pair')==p]
    sw = sum(1 for s in sub if s['result']=='WIN')
    print(f"  {p:9s} n={n:4d} WR={round(100*sw/n,1)}%")

print("\n-- confidence bucket (decided) --")
def confnum(s):
    v = s.get('confidence')
    if isinstance(v,(int,float)): return float(v)
    if isinstance(v,str):
        try: return float(v.rstrip('%'))
        except: return None
    return None
for lo,hi,lbl in [(72,101,'>=72 (floor)'),(60,72,'60-71'),(0,60,'<60')]:
    sub = [s for s in decided if confnum(s) is not None and lo<=confnum(s)<hi]
    if sub:
        sw = sum(1 for s in sub if s['result']=='WIN')
        print(f"  {lbl:14s} n={len(sub):4d} WR={round(100*sw/len(sub),1)}%")
