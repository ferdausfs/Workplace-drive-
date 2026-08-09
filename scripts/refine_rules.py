import json, glob
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
def wr(sub):
    if not sub: return 0
    return round(100*sum(1 for s in sub if s['result']=='WIN')/len(sub),1)
def conf(s):
    v=s.get('confidence')
    if isinstance(v,(int,float)): return float(v)
    if isinstance(v,str):
        try: return float(v.rstrip('%'))
        except: return None
    return None
def asset(s):
    p=s.get('pair','')
    if any(x in p for x in ['BTC','ETH','SOL','DOGE','XRP','ADA','LINK','AVAX','BNB','DOT']): return 'CRYPTO'
    return 'FOREX'

train = [s for s in rows if (s.get('timestamp') or '')[:10] <= '2026-08-06']
val   = [s for s in rows if (s.get('timestamp') or '')[:10] >= '2026-08-07']
print(f"TRAIN n={len(train)} WR={wr(train)}% | VAL n={len(val)} WR={wr(val)}%")

# Candidate rules, each evaluated on TRAIN then checked on VAL
def rules(s):
    """returns (skip, reason)"""
    p = s.get('pair','')
    if p == 'AUD/USD': return (True,'AUD/USD')
    if p == 'USD/JPY': return (True,'USD/JPY')
    if p in ('GBP/USD','EUR/USD'): return (True,'EUR/GBP')
    if s.get('sessionQuality')=='HIGHEST': return (True,'HIGHEST')
    c = conf(s)
    if c is not None and 80 <= c < 85: return (True,'conf80-84')
    return (False,None)

train_f = [s for s in train if not rules(s)[0]]
val_f   = [s for s in val   if not rules(s)[0]]
print(f"\nRULES (train-learned):")
print(f"  skip: AUD/USD, USD/JPY, EUR/USD, GBP/USD, HIGHEST session, conf 80-84")
print(f"  TRAIN: {wr(train)}% -> {wr(train_f)}%  (n {len(train)}->{len(train_f)})")
print(f"  VAL  : {wr(val)}% -> {wr(val_f)}%  (n {len(val)}->{len(val_f)})  ← holdout lift")

# per-day val WR (stability)
print("\n=== VAL by day (filtered vs all) ===")
for d in ['2026-08-07','2026-08-08','2026-08-09']:
    sub = [s for s in val if (s.get('timestamp') or '')[:10]==d]
    subf = [s for s in sub if not rules(s)[0]]
    print(f"  {d}: all {wr(sub)}% (n={len(sub)}) | filtered {wr(subf)}% (n={len(subf)})")

# how much does each rule contribute (train)
print("\n=== per-rule contribution (train) ===")
base = [s for s in train]
for name, test in [
    ('AUD/USD', lambda s: s.get('pair')=='AUD/USD'),
    ('USD/JPY', lambda s: s.get('pair')=='USD/JPY'),
    ('EUR/USD', lambda s: s.get('pair')=='EUR/USD'),
    ('GBP/USD', lambda s: s.get('pair')=='GBP/USD'),
    ('DOT/USD', lambda s: s.get('pair')=='DOT/USD'),
    ('HIGHEST', lambda s: s.get('sessionQuality')=='HIGHEST'),
    ('conf80-84', lambda s: conf(s) is not None and 80<=conf(s)<85),
]:
    skip = [s for s in train if test(s)]
    keep = [s for s in train if not test(s)]
    print(f"  skip {name:10s}: removed n={len(skip)} WR={wr(skip)}% | keep n={len(keep)} WR={wr(keep)}%")
