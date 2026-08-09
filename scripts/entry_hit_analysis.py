#!/usr/bin/env python3
"""Entry-hit + signal analysis for Phase F forward days.
Independent analysis by the Arena main agent — same methodology across days."""
import json, glob, math, sys

def wilson_ci(k, n, z=1.96):
    if n == 0: return (None, None)
    p = k / n
    denom = 1 + z*z/n
    centre = (p + z*z/(2*n)) / denom
    half = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / denom
    return (max(0, centre-half), min(1, centre+half))

def analyze_day(path):
    files = sorted(glob.glob(path + '/*.json'))
    rows = []
    for f in files:
        base = f.split('/')[-1]
        if base in ('health.json','pairs.json'): continue
        try: d = json.load(open(f))
        except Exception: continue
        sigs = d.get('signals') or []
        for s in sigs:
            rows.append(s)
    # dedup by id
    seen = {}
    for s in rows:
        if s.get('id'): seen[s['id']] = s
    rows = list(seen.values())

    decided = [s for s in rows if s.get('result') in ('WIN','LOSS') and s.get('entryHit') is not None]
    all_decided = [s for s in rows if s.get('result') in ('WIN','LOSS')]
    pending = [s for s in rows if s.get('result') not in ('WIN','LOSS')]

    hit = [s for s in decided if s['entryHit'] is True]
    miss = [s for s in decided if s['entryHit'] is False]
    hit_w = sum(1 for s in hit if s['result']=='WIN')
    miss_w = sum(1 for s in miss if s['result']=='WIN')
    all_w = sum(1 for s in all_decided if s['result']=='WIN')

    def wr(win, n): return round(100*win/n, 1) if n else None

    return {
        'total_rows': len(rows),
        'decided_with_entryHit': len(decided),
        'all_decided': len(all_decided),
        'pending': len(pending),
        'hit_n': len(hit), 'hit_wr': wr(hit_w,len(hit)), 'hit_ci': wilson_ci(hit_w,len(hit)),
        'miss_n': len(miss), 'miss_wr': wr(miss_w,len(miss)), 'miss_ci': wilson_ci(miss_w,len(miss)),
        'miss_rate': round(100*len(miss)/len(decided),1) if decided else None,
        'all_wr': wr(all_w,len(all_decided)),
        'hit_win': hit_w, 'miss_win': miss_w,
    }

if __name__ == '__main__':
    for day in ['2026-08-02','2026-08-03','2026-08-04','2026-08-05','2026-08-06']:
        p = 'phase_f_forward/' + day
        r = analyze_day(p)
        hci = r['hit_ci']; mci = r['miss_ci']
        print(f"{day}: rows={r['total_rows']} decided={r['all_decided']} | "
              f"HIT n={r['hit_n']} WR={r['hit_wr']}% CI({(round(hci[0]*100,1) if hci[0] else None)}-{(round(hci[1]*100,1) if hci[1] else None)}) | "
              f"MISS n={r['miss_n']} WR={r['miss_wr']}% CI({(round(mci[0]*100,1) if mci[0] else None)}-{(round(mci[1]*100,1) if mci[1] else None)}) | "
              f"missRate={r['miss_rate']}% | ALL WR={r['all_wr']}%")
