#!/usr/bin/env python3
"""Independent Phase-F forward analysis over phase_f_forward/2026-08-*.

Usage:
  python3 scripts/full_forward_analysis.py [--min-date 2026-08-01] [--max-date 2026-08-12]
"""
from __future__ import annotations

import argparse
import glob
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


BE = 55.6  # breakeven @ 80% payout


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def pct(k, n):
    return None if not n else round(100.0 * k / n, 1)


def ci100(k, n):
    lo, hi = wilson(k, n)
    if lo is None:
        return (None, None)
    return (round(lo * 100, 1), round(hi * 100, 1))


def asset(s):
    p = s.get("pair") or ""
    if s.get("isOTC"):
        return "OTC"
    if any(x in p for x in ("BTC", "ETH", "SOL", "DOGE", "XRP", "ADA", "LINK", "AVAX", "BNB", "DOT")):
        return "CRYPTO"
    return "FOREX"


def day_of(s):
    ts = s.get("timestamp") or ""
    return ts[:10]


def load_rows(min_date: str, max_date: str):
    rows = []
    for f in sorted(glob.glob("phase_f_forward/2026-08-*/*.json")):
        name = Path(f).name
        if name in ("health.json", "pairs.json"):
            continue
        try:
            d = json.load(open(f))
        except Exception:
            continue
        rows.extend(d.get("signals") or [])
    seen = {}
    for s in rows:
        sid = s.get("id")
        if not sid:
            continue
        ts = s.get("timestamp") or ""
        if ts < min_date or ts[:10] > max_date:
            continue
        # later snapshot wins (more likely resolved)
        prev = seen.get(sid)
        if prev is None or (s.get("checkedAt") or s.get("timestamp") or "") >= (
            prev.get("checkedAt") or prev.get("timestamp") or ""
        ):
            seen[sid] = s
    return list(seen.values())


def wr_line(label, sub):
    n = len(sub)
    w = sum(1 for s in sub if s.get("result") == "WIN")
    r = pct(w, n)
    lo, hi = ci100(w, n)
    flag = ""
    if n and r is not None and lo is not None:
        if hi < BE:
            flag = "  BELOW_BE"
        elif lo >= BE:
            flag = "  CLEARS_BE"
    print(f"  {label:22s} n={n:5d}  WR={r}%  CI[{lo}-{hi}]{flag}")
    return r, n, lo, hi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-date", default="2026-08-01")
    ap.add_argument("--max-date", default="2026-08-12")
    args = ap.parse_args()

    rows = load_rows(args.min_date, args.max_date)
    decided = [s for s in rows if s.get("result") in ("WIN", "LOSS")]
    print(f"=== POOL {args.min_date}..{args.max_date} ===")
    print(f"unique signals: {len(rows)}  decided: {len(decided)}  other: {len(rows)-len(decided)}")
    wr_line("ALL decided", decided)

    print("\n=== BY DAY ===")
    days = sorted({day_of(s) for s in decided if day_of(s)})
    for d in days:
        wr_line(d, [s for s in decided if day_of(s) == d])

    print("\n=== BY ASSET ===")
    for a in ("CRYPTO", "FOREX", "OTC"):
        wr_line(a, [s for s in decided if asset(s) == a])

    print("\n=== BY DIRECTION ===")
    for dirc in ("BUY", "SELL"):
        wr_line(dirc, [s for s in decided if s.get("direction") == dirc])

    print("\n=== FOREX PAIRS ===")
    fx = [s for s in decided if asset(s) == "FOREX"]
    for p, n in Counter(s.get("pair") for s in fx).most_common():
        wr_line(p, [s for s in fx if s.get("pair") == p])

    print("\n=== CRYPTO PAIRS ===")
    cr = [s for s in decided if asset(s) == "CRYPTO"]
    for p, n in Counter(s.get("pair") for s in cr).most_common():
        wr_line(p, [s for s in cr if s.get("pair") == p])

    print("\n=== REGIME ===")
    for reg, n in Counter(s.get("marketRegime") for s in decided).most_common():
        wr_line(str(reg), [s for s in decided if s.get("marketRegime") == reg])

    print("\n=== ASSET x DIRECTION ===")
    for a in ("CRYPTO", "FOREX"):
        for dirc in ("BUY", "SELL"):
            wr_line(f"{a} {dirc}", [s for s in decided if asset(s) == a and s.get("direction") == dirc])

    eh_rows = [s for s in decided if "entryHitLegacy" in s]
    print(f"\n=== ENTRY-HIT (FIX-EH field present) n={len(eh_rows)} ===")
    print("-- legacy (expiry±5min) --")
    for v, lbl in ((True, "legacy-HIT"), (False, "legacy-MISS")):
        wr_line(lbl, [s for s in eh_rows if s.get("entryHitLegacy") is v])
    print("-- corrected (re-test) --")
    for v, lbl in ((True, "eh-HIT"), (False, "eh-MISS")):
        wr_line(lbl, [s for s in eh_rows if s.get("entryHit") is v])

    print("\n=== POST v6.10 WINDOW (2026-08-10..max) ===")
    post = [s for s in decided if day_of(s) >= "2026-08-10"]
    wr_line("post-v610 all", post)
    wr_line("post CRYPTO", [s for s in post if asset(s) == "CRYPTO"])
    wr_line("post FOREX", [s for s in post if asset(s) == "FOREX"])

    # forex-block counterfactual
    no_fx = [s for s in decided if asset(s) != "FOREX"]
    print("\n=== COUNTERFACTUAL: drop FOREX (config gate, NOT a rec) ===")
    wr_line("crypto+otc only", no_fx)

    print("\nNOTE: breakeven 55.6% @ 80% payout. Gate needs CI-low >= 55.6%, n>=50, >=30/regime, 7-14 days.")
    print("No inversion / pair-block / real-money claim from this script.")


if __name__ == "__main__":
    main()
