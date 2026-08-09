#!/usr/bin/env python3
"""Day-2 entry-hit + signal analysis (clean by-day via timestamp).
Independent — Arena main agent. Uses the 2026-08-06 snapshot (latest resolution state)."""
import json, glob, math
from collections import Counter

def wilson_ci(k, n, z=1.96):
    if n == 0: return (None, None)
    p = k/n; denom = 1 + z*z/n
    centre = (p + z*z/(2*n))/denom
    half = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/denom
    return (max(0,centre-half), min(1,centre+half))

files = sorted(glob.glob('phase_f_forward/2026-08-06/*.json'))
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

for day in ['2026-08-05', '2026-08-06']:
    dr = day_rows(day)
    decided = [s for s in dr if s.get('result') in ('WIN','LOSS')]
    eh = [s for s in decided if s.get('entryHit') is not None]
    hit = [s for s in eh if s['entryHit'] is True]
    miss = [s for s in eh if s['entryHit'] is False]
    hw = sum(1 for s in hit if s['result']=='WIN'); mw = sum(1 for s in miss if s['result']=='WIN')
    aw = sum(1 for s in decided if s['result']=='WIN')
    hci = wilson_ci(hw, len(hit)); mci = wilson_ci(mw, len(miss))
    def pct(a,b): return round(100*a/b,1) if b else None
    print(f"=== {day} ===")
    print(f"  rows={len(dr)} decided={len(decided)} WIN={aw} LOSS={len(decided)-aw} ALL_WR={pct(aw,len(decided))}%")
    print(f"  ENTRY HIT : n={len(hit)}  WR={pct(hw,len(hit))}%  CI({round(hci[0]*100,1) if hci[0] else None}-{round(hci[1]*100,1) if hci[1] else None})")
    print(f"  ENTRY MISS: n={len(miss)} WR={pct(mw,len(miss))}%  CI({round(mci[0]*100,1) if mci[0] else None}-{round(mci[1]*100,1) if mci[1] else None})")
    print(f"  missRate={pct(len(miss),len(eh))}%")
    print()

# ── SIGNAL DATA for 08-06 (the day being analyzed) ──
print("="*60)
print("SIGNAL DATA — 2026-08-06 (clean by timestamp)")
dr = day_rows('2026-08-06')
decided = [s for s in dr if s.get('result') in ('WIN','LOSS')]
allrows = dr

print(f"\nTotal signals: {len(allrows)} | decided: {len(decided)} | pending: {len(allrows)-len(decided)}")
w = sum(1 for s in decided if s['result']=='WIN')
print(f"Overall WR: {round(100*w/len(decided),1)}% ({w}/{len(decided)})  | breakeven@80%payout = 55.6%")

# by direction
print("\n-- by direction --")
for dirc in ['BUY','SELL']:
    sub = [s for s in decided if s.get('direction')==dirc]
    if sub:
        sw = sum(1 for s in sub if s['result']=='WIN')
        print(f"  {dirc:5s} n={len(sub):4d} WR={round(100*sw/len(sub),1)}%")

# by asset type
print("\n-- by asset type --")
for at in ['CRYPTO','FOREX','OTC','CRYPTO_OTC']:
    sub = [s for s in decided if s.get('isOTC')==(at=='OTC' or at=='CRYPTO_OTC') or (s.get('assetType')==at)]
    # simpler: use assetType if present
    sub = [s for s in decided if (s.get('assetType') or ('OTC' if s.get('isOTC') else ('CRYPTO' if any(p in (s.get('pair') or '') for p in ['BTC','ETH','SOL','DOGE','XRP','ADA','LINK','AVAX','BNB']) else 'FOREX')))==at]
    if sub:
        sw = sum(1 for s in sub if s['result']=='WIN')
        print(f"  {at:10s} n={len(sub):4d} WR={round(100*sw/len(sub),1)}%")

# by regime
print("\n-- by marketRegime (decided) --")
rc = Counter(s.get('marketRegime') for s in decided)
for reg, n in rc.most_common():
    sub = [s for s in decided if s.get('marketRegime')==reg]
    sw = sum(1 for s in sub if s['result']=='WIN')
    print(f"  {str(reg):12s} n={n:4d} WR={round(100*sw/n,1)}%")

# by session quality
print("\n-- by sessionQuality --")
for sq in ['HIGHEST','HIGH','MEDIUM','LOW',None]:
    sub = [s for s in decided if s.get('sessionQuality')==sq]
    if sub:
        sw = sum(1 for s in sub if s['result']=='WIN')
        print(f"  {str(sq):8s} n={len(sub):4d} WR={round(100*sw/len(sub),1)}%")

# confidence distribution
print("\n-- confidence bucket (decided) --")
for lo,hi,lbl in [(72,101,'>=72 (traded)'),(60,72,'60-71'),(0,60,'<60')]:
    sub = [s for s in decided if isinstance(s.get('confidence'),(int,float)) and lo<=s['confidence']<hi]
    if sub:
        sw = sum(1 for s in sub if s['result']=='WIN')
        print(f"  {lbl:15s} n={len(sub):4d} WR={round(100*sw/len(sub),1)}%")

# entryHit rows breakdown incl. direction of miss
print("\n-- entryHit rows by direction (08-06) --")
eh = [s for s in decided if s.get('entryHit') is not None]
for dirc in ['BUY','SELL']:
    sub = [s for s in eh if s.get('direction')==dirc]
    h = [s for s in sub if s['entryHit']]; m = [s for s in sub if not s['entryHit']]
    hw = sum(1 for s in h if s['result']=='WIN'); mw = sum(1 for s in m if s['result']=='WIN')
    print(f"  {dirc}: hit n={len(h)} WR={round(100*hw/len(h),1) if h else None}% | miss n={len(m)} WR={round(100*mw/len(m),1) if m else None}%")

# NO_TRADE / direction of all rows
print("\n-- direction of ALL 08-06 rows --")
print(dict(Counter(s.get('direction') for s in allrows)))
