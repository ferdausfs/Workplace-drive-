import json, glob, math
from collections import Counter
rows = []
for f in sorted(glob.glob('phase_f_forward/*/*.json')):
    b = f.split('/')[-1]
    if b in ('health.json','pairs.json'): continue
    try: d = json.load(open(f))
    except: continue
    rows += d.get('signals') or []
seen = {}
for s in rows:
    if s.get('id'): seen[s['id']] = s
rows = [s for s in seen.values() if s.get('result') in ('WIN','LOSS')]
print(f"TOTAL decided: {len(rows)} | overall WR: {round(100*sum(1 for s in rows if s['result']=='WIN')/len(rows),1)}%")

def wr(sub):
    if not sub: return None
    w = sum(1 for s in sub if s['result']=='WIN')
    return round(100*w/len(sub),1)

print("\n=== BY CONFIDENCE BUCKET ===")
def conf(s):
    v = s.get('confidence')
    if isinstance(v,(int,float)): return float(v)
    if isinstance(v,str):
        try: return float(v.rstrip('%'))
        except: return None
    return None
for lo,hi,lbl in [(72,75,'72-74'),(75,80,'75-79'),(80,85,'80-84'),(85,90,'85-89'),(90,101,'90+')]:
    sub=[s for s in rows if conf(s) is not None and lo<=conf(s)<hi]
    if len(sub)>=10: print(f"  conf {lbl}: n={len(sub)} WR={wr(sub)}%")

print("\n=== BY ASSET ===")
def asset(s):
    p=s.get('pair','')
    if s.get('isOTC'): return 'OTC'
    if any(x in p for x in ['BTC','ETH','SOL','DOGE','XRP','ADA','LINK','AVAX','BNB','DOT']): return 'CRYPTO'
    return 'FOREX'
for at in ['CRYPTO','FOREX','OTC']:
    sub=[s for s in rows if asset(s)==at]
    if len(sub)>=10: print(f"  {at}: n={len(sub)} WR={wr(sub)}%")

print("\n=== BY PAIR (n>=30) ===")
for p,n in Counter(s.get('pair') for s in rows).most_common():
    if n<30: continue
    sub=[s for s in rows if s.get('pair')==p]
    print(f"  {p:9s} n={n:4d} WR={wr(sub)}%")

print("\n=== BY REGIME ===")
for reg,n in Counter(s.get('marketRegime') for s in rows).most_common():
    if n<10: continue
    sub=[s for s in rows if s.get('marketRegime')==reg]
    print(f"  {reg:12s} n={n:4d} WR={wr(sub)}%")

print("\n=== BY SESSION QUALITY ===")
for sq in ['HIGHEST','HIGH','MEDIUM','LOW',None]:
    sub=[s for s in rows if s.get('sessionQuality')==sq]
    if len(sub)>=10: print(f"  {str(sq):8s} n={len(sub):4d} WR={wr(sub)}%")

print("\n=== BY GRADE ===")
def gr(s):
    g=s.get('grade')
    if isinstance(g,dict): return g.get('grade')
    return g
for g in ['A+','A','B','C','D','F']:
    sub=[s for s in rows if gr(s)==g]
    if len(sub)>=10: print(f"  grade {g}: n={len(sub)} WR={wr(sub)}%")

print("\n=== BY ALIGNMENT ===")
for a in ['ALL_BULLISH','ALL_BEARISH','MOSTLY_BULLISH','MOSTLY_BEARISH','MIXED']:
    sub=[s for s in rows if s.get('alignment')==a]
    if len(sub)>=10: print(f"  {a:15s} n={len(sub):4d} WR={wr(sub)}%")

print("\n=== BY STRUCTURE VERDICT ===")
sv=s.get('structureVerdict')
def st(s):
    v=s.get('structureVerdict')
    if isinstance(v,dict): return v.get('overall')
    return v
for x in ['ALIGNED','AGAINST','MIXED','NEUTRAL','N/A',None]:
    sub=[s for s in rows if st(s)==x]
    if len(sub)>=10: print(f"  {str(x):10s} n={len(sub):4d} WR={wr(sub)}%")

print("\n=== BY DIRECTION ===")
for d in ['BUY','SELL']:
    sub=[s for s in rows if s.get('direction')==d]
    if len(sub)>=10: print(f"  {d}: n={len(sub)} WR={wr(sub)}%")

print("\n=== BY HOUR (UTC) ===")
for h in range(24):
    sub=[s for s in rows if (s.get('timestamp') or '')[11:13]==f'{h:02d}']
    if len(sub)>=15: print(f"  {h:02d}:00 n={len(sub):4d} WR={wr(sub)}%")
