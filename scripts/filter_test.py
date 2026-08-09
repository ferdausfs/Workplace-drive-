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

def asset(s):
    p=s.get('pair','')
    if any(x in p for x in ['BTC','ETH','SOL','DOGE','XRP','ADA','LINK','AVAX','BNB','DOT']): return 'CRYPTO'
    return 'FOREX'
def conf(s):
    v=s.get('confidence')
    if isinstance(v,(int,float)): return float(v)
    if isinstance(v,str):
        try: return float(v.rstrip('%'))
        except: return None
    return None
def gr(s):
    g=s.get('grade')
    return g.get('grade') if isinstance(g,dict) else g

# RULES discovered from TRAIN (08-01..08-06)
def bad(s):
    # forex pairs with WR<35 on train
    if s.get('pair') in ('AUD/USD','USD/JPY','GBP/USD','EUR/USD','DOT/USD'): return True
    if s.get('sessionQuality')=='HIGHEST': return True
    c = conf(s)
    if c is not None and 80 <= c < 85: return True   # worst conf bucket
    if gr(s)=='A+': return True                        # worst grade
    return False

# CHRONOLOGICAL: train 08-01..08-06, test 08-07..08-09
train = [s for s in rows if (s.get('timestamp') or '')[:10] <= '2026-08-06']
test  = [s for s in rows if (s.get('timestamp') or '')[:10] >= '2026-08-07']
def wr(sub):
    if not sub: return 0
    return round(100*sum(1 for s in sub if s['result']=='WIN')/len(sub),1)

print("=== CHRONOLOGICAL HOLDOUT TEST ===")
print(f"TRAIN (08-01..06): n={len(train)} WR={wr(train)}%")
print(f"TEST  (08-07..09): n={len(test)} WR={wr(test)}%")
print()
print("Rules (learned from train):")
print("  skip: AUD/USD, USD/JPY, GBP/USD, EUR/USD, DOT/USD")
print("  skip: sessionQuality==HIGHEST")
print("  skip: confidence 80-84")
print("  skip: grade A+")
print()

train_f = [s for s in train if not bad(s)]
test_f  = [s for s in test  if not bad(s)]
print(f"FILTERED TRAIN: n={len(train_f)} WR={wr(train_f)}%  (was {wr(train)}%)")
print(f"FILTERED TEST : n={len(test_f)} WR={wr(test_f)}%  (was {wr(test)}%)  ← HOLDOUT LIFT?")
print()
# how many signals dropped
print(f"dropped: train {len(train)-len(train_f)} ({round(100*(len(train)-len(train_f))/len(train))}%), test {len(test)-len(test_f)} ({round(100*(len(test)-len(test_f))/len(test))}%)")
