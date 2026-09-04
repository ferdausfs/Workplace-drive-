#!/usr/bin/env python3
"""Phase F baseline harness — canonical, reproducible.
Every agent (human or AI) MUST run this FIRST and report the exact numbers,
so all independent analyses start from an identical verified baseline.

Usage:
  # unpack data first:
  mkdir -p phase_f_forward && tar -xzf data/phase_f_forward_2026-08-14.tar.gz -C phase_f_forward
  python3 phase_f_baseline.py --data phase_f_forward

Protocol (NON-NEGOTIABLE):
  - decided = result in (WIN, LOSS) only; TIE/UNKNOWN excluded.
  - forward window = timestamp >= 2026-08-01.
  - breakeven 55.6% (80% payout); Wilson 95% CI.
  - dedup by signal id.
  - NO entryHit in any signal-time model (post-hoc + historically tautological).
  - NO invented data. If a number is missing from the data, say so.
"""
import argparse, json, glob, math
from collections import Counter

BREAK = 55.6
CRYPTO = ['BTC','ETH','SOL','DOGE','XRP','ADA','LINK','AVAX','BNB','DOT']

def wilson(k, n, z=1.96):
    if n == 0: return (None, None)
    p = k/n; d = 1 + z*z/n
    c = (p + z*z/(2*n))/d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return (max(0,c-h), min(1,c+h))

def pct(a,b): return round(100*a/b,1) if b else None
def ci(w,n):
    c = wilson(w,n)
    return f"{pct(w,n)}%  CI[{round(c[0]*100,1)}-{round(c[1]*100,1)}]"

def asset(s):
    if s.get('isOTC'): return 'OTC'
    return 'CRYPTO' if s['pair'].split('/')[0] in CRYPTO else 'FOREX'

def load(data_dir):
    rows = []
    for f in sorted(glob.glob(data_dir + '/*/*.json')):
        b = f.split('/')[-1]
        if b in ('health.json','pairs.json'): continue
        try: d = json.load(open(f))
        except: continue
        rows += d.get('signals') or []
    seen = {}
    for s in rows:
        if s.get('id'): seen[s['id']] = s
    rows = [s for s in seen.values()
            if (s.get('timestamp') or '') >= '2026-08-01'
            and s.get('result') in ('WIN','LOSS')]
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', default='phase_f_forward')
    a = ap.parse_args()
    R = load(a.data)
    W = lambda sub: sum(1 for s in sub if s['result']=='WIN')
    print(f"BASELINE (decided forward rows): {len(R)}")
    print(f"OVERALL WR: {ci(W(R), len(R))}   (breakeven {BREAK}%)")
    print("\n-- by asset --")
    for at in ['CRYPTO','FOREX','OTC']:
        sub=[s for s in R if asset(s)==at]
        if sub: print(f"  {at:7s} n={len(sub):4d} WR={ci(W(sub),len(sub))}")
    print("\n-- by day --")
    for d in sorted({(s.get('timestamp') or '')[:10] for s in R}):
        sub=[s for s in R if (s.get('timestamp') or '').startswith(d)]
        print(f"  {d}: n={len(sub):4d} WR={pct(W(sub),len(sub)):5.1f}%")
    print("\n-- pre/post round-3 (boundary 2026-08-06T19:00Z) --")
    for lbl, fn in [('pre', lambda s:(s.get('timestamp') or '')<'2026-08-06T19:00'),
                    ('post', lambda s:(s.get('timestamp') or '')>='2026-08-06T19:00')]:
        sub=[s for s in R if fn(s)]
        print(f"  {lbl:5s} n={len(sub):4d} WR={ci(W(sub),len(sub))}")
    print("\n-- FIX-EH (rows with entryHitLegacy) --")
    eh=[s for s in R if 'entryHitLegacy' in s and s.get('entryHit') is not None]
    for fld,lbl in [('entryHitLegacy','LEGACY'),('entryHit','CORRECTED')]:
        for v,t in [(True,'HIT '),(False,'MISS')]:
            sub=[s for s in eh if s.get(fld) is v]
            print(f"  {lbl:9s} {t} n={len(sub):4d} WR={ci(W(sub),len(sub))}")
    print("\nDONE — report these numbers verbatim in your findings doc.")

if __name__ == '__main__':
    main()
