#!/usr/bin/env python3
"""Phase F — corrected entryHit analysis (FIX-EH).
Compares NEW re-test semantics (entryHit) vs OLD expiry±5min rule (entryHitLegacy).
Only rows with 'entryHitLegacy' (deployed 2026-08-07 ~08:30 UTC) count.
Usage: python3 entryhit_corrected_analysis.py [--min-date 2026-08-07]
"""
import json, glob, math, sys, argparse

def wilson(k, n, z=1.96):
    if n == 0: return (None, None)
    p = k/n; d = 1 + z*z/n
    c = (p + z*z/(2*n))/d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return (max(0,c-h), min(1,c+h))

ap = argparse.ArgumentParser()
ap.add_argument('--min-date', default='2026-08-07')
args = ap.parse_args()

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
rows = [s for s in seen.values()
        if (s.get('timestamp') or '') >= args.min_date
        and s.get('result') in ('WIN','LOSS')
        and 'entryHitLegacy' in s]

print(f"FIX-EH decided rows (>= {args.min_date}): {len(rows)}")
if len(rows) < 30:
    print(f"⚠️ n={len(rows)} < 30 — partial/too small. Let data accumulate (1-2 days).")

def wr(sub):
    if not sub: return (None, (None,None))
    w = sum(1 for s in sub if s['result']=='WIN')
    return (round(100*w/len(sub),1), tuple(round(x*100,1) if x else None for x in wilson(w,len(sub))))

print("\n=== OLD metric (entryHitLegacy — expiry±5min rule) ===")
for v, lbl in [(True,'HIT'), (False,'MISS')]:
    sub = [s for s in rows if s['entryHitLegacy'] is v]
    r, ci = wr(sub)
    print(f"  legacy-{lbl:5s} n={len(sub):4d}  WR={r}%  CI {ci}")

print("\n=== NEW metric (entryHit — re-test semantics) ===")
for v, lbl in [(True,'HIT '), (False,'MISS')]:
    sub = [s for s in rows if s['entryHit'] is v]
    r, ci = wr(sub)
    print(f"  eh-{lbl:5s} n={len(sub):4d}  WR={r}%  CI {ci}")

print("\n=== Tautology check ===")
miss_leg = [s for s in rows if s['entryHitLegacy'] is False]
if miss_leg:
    r, _ = wr(miss_leg)
    print(f"  legacy-MISS WR = {r}%  (100% = tautology STILL in old field — expected)")
eh_miss = [s for s in rows if s['entryHit'] is False]
if eh_miss:
    r, _ = wr(eh_miss)
    print(f"  eh-MISS WR     = {r}%  (100% = broken metric; <100% = FIX WORKING)")

print("\n=== Combination table (eh, legacy, result) ===")
from collections import Counter
for (eh, lg, res), n in sorted(Counter((s['entryHit'], s['entryHitLegacy'], s['result']) for s in rows).items()):
    print(f"  eh={eh} legacy={lg} → {res}: {n}")

print("\n=== By fillStatus (INSTANT vs PENDING_ENTRY) ===")
for fs in ['INSTANT','PENDING_ENTRY',None]:
    sub = [s for s in rows if s.get('fillStatus')==fs]
    if not sub: continue
    r, _ = wr(sub)
    eh_t = [s for s in sub if s['entryHit'] is True]
    rt, _ = wr(eh_t)
    print(f"  fill={str(fs):14s} n={len(sub):4d} WR={r}%  |  eh-HIT n={len(eh_t)} WR={rt}%")

print("\n=== By direction ===")
for dirc in ['BUY','SELL']:
    sub = [s for s in rows if s.get('direction')==dirc]
    if not sub: continue
    r, _ = wr(sub)
    print(f"  {dirc:5s} n={len(sub):4d} WR={r}%")

print("\nNOTE: n<50 → provisional only. Phase F gate: ≥50 obs, ≥30/regime cell, 7-14 days.")
