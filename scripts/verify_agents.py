#!/usr/bin/env python3
"""Reviewer verification of the 4 agent reports — every critical claim re-run on data."""
import json, glob, math
from collections import Counter

def wilson(k,n,z=1.96):
    if n==0: return (None,None)
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return (max(0,c-h),min(1,c+h))
def pct(a,b): return round(100*a/b,1) if b else None
def ci(w,n):
    c=wilson(w,n); return f"{pct(w,n)}% CI[{round(c[0]*100,1)}-{round(c[1]*100,1)}]"

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
print("decided:", len(R), "| WIN:", W(R), "| LOSS:", len(R)-W(R))
print("="*72)

# ── CLAIM A (Agent01 §1.8 + Agent03 §2a): corrected entryHit STILL tautological on
#    rows WITHOUT entryHitLegacy; full-population HIT 33.8% vs MISS 78.3% (n=2510)
print("\n[CLAIM A] entryHit full-population (all rows with entryHit field):")
eh=[s for s in R if s.get('entryHit') is not None]
hit=[s for s in eh if s['entryHit'] is True]; miss=[s for s in eh if s['entryHit'] is False]
print(f"  n with entryHit={len(eh)} | HIT n={len(hit)} WR={ci(W(hit),len(hit))} | MISS n={len(miss)} WR={ci(W(miss),len(miss))}")
leg=[s for s in eh if 'entryHitLegacy' in s]; noleg=[s for s in eh if 'entryHitLegacy' not in s]
print(f"  WITH legacy: {len(leg)} | WITHOUT legacy: {len(noleg)}")
for lbl, sub in [('WITH-legacy',leg),('NO-legacy',noleg)]:
    h=[s for s in sub if s['entryHit'] is True]; m=[s for s in sub if s['entryHit'] is False]
    print(f"    {lbl:11s} HIT n={len(h)} WR={ci(W(h),len(h))} | MISS n={len(m)} WR={ci(W(m),len(m))}")
# day-level for no-legacy rows
print("  NO-legacy rows by day (MISS WR):")
for d in sorted({(s.get('timestamp') or '')[:10] for s in noleg}):
    sub=[s for s in noleg if (s.get('timestamp') or '').startswith(d)]
    m=[s for s in sub if s['entryHit'] is False]
    print(f"    {d}: n={len(sub)} | MISS n={len(m)} WR={ci(W(m),len(m))}")

# ── CLAIM B (Agent02 §2.2 + Agent03 §2a): PENDING_ENTRY + entryHit=false -> 100% WIN (n=43)
print("\n[CLAIM B] PENDING_ENTRY x corrected entryHit (legacy rows):")
pe=[s for s in leg if s.get('fillStatus')=='PENDING_ENTRY']
pem=[s for s in pe if s['entryHit'] is False]
print(f"  PENDING_ENTRY n={len(pe)} | entryHit=False n={len(pem)} WR={ci(W(pem),len(pem))}")
print("  INSTANT-only (legacy rows):")
inst=[s for s in leg if s.get('fillStatus')=='INSTANT']
ih=[s for s in inst if s['entryHit'] is True]; im=[s for s in inst if s['entryHit'] is False]
print(f"    INSTANT HIT n={len(ih)} WR={ci(W(ih),len(ih))} | INSTANT MISS n={len(im)} WR={ci(W(im),len(im))}")
# claim: PENDING_ENTRY 60.1% inflated by the 43 mechanical wins; rest = 43.8% (n=105)
rest=[s for s in pe if s['entryHit'] is not False]
print(f"    PENDING_ENTRY excl. MISS rows: n={len(rest)} WR={ci(W(rest),len(rest))}")

# ── CLAIM C (Agent03 §2b): aiAgreed constant (all True)
print("\n[CLAIM C] aiAgreed distribution:")
print("  ", dict(Counter(s.get('aiAgreed') for s in R)))

# ── CLAIM D (Agent03 §2d / Agent02 §2.5): grade-label regime change ~08-10
print("\n[CLAIM D] grade share by day (A+ vs C):")
for d in sorted({(s.get('timestamp') or '')[:10] for s in R}):
    sub=[s for s in R if (s.get('timestamp') or '').startswith(d)]
    def g(s):
        v=s.get('grade'); return v.get('grade') if isinstance(v,dict) else v
    gs=Counter(g(s) for s in sub)
    if len(sub)>0:
        print(f"    {d}: n={len(sub):4d} A+={round(100*gs.get('A+',0)/len(sub)):3d}% A={round(100*gs.get('A',0)/len(sub)):3d}% C={round(100*gs.get('C',0)/len(sub)):3d}%")

# ── CLAIM E: signalIndicators coverage only from 08-09
print("\n[CLAIM E] signalIndicators coverage:")
si=[s for s in R if s.get('signalIndicators')]
print(f"  rows with signalIndicators: {len(si)} ({pct(len(si),len(R))}%)")
print("  earliest ts with SI:", min((s.get('timestamp') or '') for s in si))
print("  latest ts without SI:", max((s.get('timestamp') or '') for s in R if not s.get('signalIndicators')))

# ── CLAIM F: entryHitLegacy only post-round-3
print("\n[CLAIM F] entryHitLegacy presence pre/post:")
pre=[s for s in R if (s.get('timestamp') or '')<'2026-08-06T19:00']
post=[s for s in R if (s.get('timestamp') or '')>='2026-08-06T19:00']
print(f"  pre rows with legacy: {sum(1 for s in pre if 'entryHitLegacy' in s)}/{len(pre)}")
print(f"  post rows with legacy: {sum(1 for s in post if 'entryHitLegacy' in s)}/{len(post)}")

# ── CLAIM G (Agent04 §1.9): PENDING_ENTRY entryDistancePct >> INSTANT
print("\n[CLAIM G] entryDistancePct by fillStatus:")
for fs in ['PENDING_ENTRY','INSTANT']:
    sub=[s for s in R if s.get('fillStatus')==fs and s.get('entryDistancePct') is not None]
    if sub:
        vals=[float(s['entryDistancePct']) for s in sub]
        print(f"  {fs:14s} n={len(sub)} mean={sum(vals)/len(vals):.4f}")

# ── CLAIM H (all agents): 0 slices clear breakeven CI. Spot-check the "near misses":
print("\n[CLAIM H] near-miss spot checks (should all have CI_lo < 55.6):")
def spot(lbl, fn):
    sub=[s for s in R if fn(s)]
    print(f"  {lbl:34s} n={len(sub):4d} WR={ci(W(sub),len(sub))}")
spot("CRYPTO/TRENDING/BUY", lambda s: s['pair'].split('/')[0] in ['BTC','ETH','SOL','DOGE','XRP','ADA','LINK','AVAX','BNB','DOT'] and s.get('marketRegime')=='TRENDING' and s.get('direction')=='BUY')
spot("PENDING_ENTRY", lambda s: s.get('fillStatus')=='PENDING_ENTRY')
spot("structureVerdict=AGAINST", lambda s: s.get('structureVerdict')=='AGAINST')
spot("grade C", lambda s: (s.get('grade') or {}).get('grade')=='C' if isinstance(s.get('grade'),dict) else s.get('grade')=='C')
spot("newest-4d (08-11..14)", lambda s: (s.get('timestamp') or '')>='2026-08-11')
print("\nDONE — reviewer verification complete.")
