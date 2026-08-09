#!/usr/bin/env python3
"""Day-2 (2026-08-06) FULL signal data + entry-hit — clean by timestamp."""
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

def confnum(s):
    v = s.get('confidence')
    if isinstance(v,(int,float)): return float(v)
    if isinstance(v,str):
        try: return float(v.rstrip('%'))
        except: return None
    return None

dr = [s for s in rows if (s.get('timestamp') or '').startswith('2026-08-06')]
decided = [s for s in dr if s.get('result') in ('WIN','LOSS')]
print(f"08-06 (UTC, partial day — snapshot 08:42 UTC, merge was 08:38 UTC):")
print(f"  rows={len(dr)} decided={len(decided)} pending={len(dr)-len(decided)}")

# ---- CONFIDENCE BUCKETS (fixed parse) ----
print("\n-- confidence bucket (decided) --")
buckets = [(72,101,'>=72 (above floor)'),(68,72,'68-71'),(60,68,'60-67'),(0,60,'<60'),(None,None,'no conf')]
for lo,hi,lbl in buckets:
    if lo is None: sub = [s for s in decided if confnum(s) is None]
    else: sub = [s for s in decided if confnum(s) is not None and lo<=confnum(s)<hi]
    if sub:
        sw = sum(1 for s in sub if s['result']=='WIN')
        print(f"  {lbl:20s} n={len(sub):4d} WR={round(100*sw/len(sub),1)}%")

# ---- AI agree/disagree ----
print("\n-- aiAgreed (decided) --")
for a in [True, False, None]:
    sub = [s for s in decided if s.get('aiAgreed')==a]
    if sub:
        sw = sum(1 for s in sub if s['result']=='WIN')
        print(f"  aiAgreed={str(a):5s} n={len(sub):4d} WR={round(100*sw/len(sub),1)}%")

# ---- forex vs crypto ----
print("\n-- forex pairs breakdown (decided) --")
for p, n in Counter(s.get('pair') for s in decided if s.get('isOTC') is not True and any(x in (s.get('pair') or '') for x in ['USD/','EUR/','GBP/','/JPY','/CHF','/CAD','AUD/','NZD/'])).most_common():
    sub = [s for s in decided if s.get('pair')==p]
    sw = sum(1 for s in sub if s['result']=='WIN')
    print(f"  {p:9s} n={n:4d} WR={round(100*sw/n,1)}%")

print("\n-- crypto breakdown (decided) --")
for p, n in Counter(s.get('pair') for s in decided if s.get('isOTC') is not True and not any(x in (s.get('pair') or '') for x in ['USD/','EUR/','GBP/','/JPY','/CHF','/CAD','AUD/','NZD/'])).most_common():
    sub = [s for s in decided if s.get('pair')==p]
    sw = sum(1 for s in sub if s['result']=='WIN')
    print(f"  {p:9s} n={n:4d} WR={round(100*sw/n,1)}%")

# ---- bestTF ----
print("\n-- bestTF (decided) --")
for tf, n in Counter(s.get('bestTF') for s in decided).most_common():
    sub = [s for s in decided if s.get('bestTF')==tf]
    sw = sum(1 for s in sub if s['result']=='WIN')
    print(f"  {str(tf):6s} n={n:4d} WR={round(100*sw/n,1)}%")

# ---- entry-hit final (clean) ----
eh = [s for s in decided if s.get('entryHit') is not None]
hit = [s for s in eh if s['entryHit'] is True]
miss = [s for s in eh if s['entryHit'] is False]
hw = sum(1 for s in hit if s['result']=='WIN'); mw = sum(1 for s in miss if s['result']=='WIN')
hci = wilson_ci(hw,len(hit)); mci = wilson_ci(mw,len(miss))
print("\n-- ENTRY-HIT (day 2 clean) --")
print(f"  decided w/ entryHit: {len(eh)} | HIT n={len(hit)} WR={round(100*hw/len(hit),1)}% CI({round(hci[0]*100,1)}-{round(hci[1]*100,1)}) | MISS n={len(miss)} WR={round(100*mw/len(miss),1)}% CI({round(mci[0]*100,1)}-{round(mci[1]*100,1)}) | missRate={round(100*len(miss)/len(eh),1)}%")

# ---- combined two days ----
print("\n-- COMBINED 08-05 + 08-06 (clean by timestamp, from 08-06 snapshot) --")
dr2 = [s for s in rows if (s.get('timestamp') or '').startswith(('2026-08-05','2026-08-06'))]
dec2 = [s for s in dr2 if s.get('result') in ('WIN','LOSS')]
eh2 = [s for s in dec2 if s.get('entryHit') is not None]
h2 = [s for s in eh2 if s['entryHit'] is True]; m2 = [s for s in eh2 if s['entryHit'] is False]
h2w = sum(1 for s in h2 if s['result']=='WIN'); m2w = sum(1 for s in m2 if s['result']=='WIN')
print(f"  decided={len(dec2)} | HIT n={len(h2)} WR={round(100*h2w/len(h2),1)}% | MISS n={len(m2)} WR={round(100*m2w/len(m2),1)}% | missRate={round(100*len(m2)/len(eh2),1)}%")
