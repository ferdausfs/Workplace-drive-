#!/usr/bin/env python3
"""
phase_f_prefill.py — Phase F platform log auto-prefill (worker side)

Worker-এর কলামগুলো (10টা) নিজে-নিজে /api/history থেকে ভরে দেয়।
আপনাকে শুধু PLATFORM-এর 7টা কলাম লিখতে হবে (platform entry/expiry price,
platform result, payout) — ওগুলো platform-এ trade করে দেখে নিতে হয়।

Usage:
  python3 phase_f_prefill.py                 # target pairs, last 24h
  python3 phase_f_prefill.py --days 3        # last 3 days
  python3 phase_f_prefill.py --all           # full forward window (>=08-01)
  python3 phase_f_prefill.py --out out.csv   # output file (default: phase_f_prefilled.csv)

Output: CSV with worker columns filled; platform columns empty (ready to edit).
Re-running skips/updates only worker columns — never overwrites platform edits
if you use --merge (see below).
"""
import argparse, csv, json, sys, time, urllib.request
from datetime import datetime, timedelta

API = "https://fttotcv6.umuhammadiswa.workers.dev"
PAIRS = ["ADA/USD","AUD/USD","AVAX/USD","BNB/BTC","BNB/USD","BTC/USD","DOGE/USD","DOT/USD",
         "ETH/USD","EUR/USD","GBP/CHF","GBP/USD","LINK/USD","SOL/USD","USD/CAD","USD/CHF","USD/JPY","XRP/USD"]
TARGET = {"USD/JPY","AUD/USD","DOT/USD"}   # Phase F target pairs (must all be logged)

HEADER = ["obs_id","worker_timestamp","pair","asset_class","target_pair","direction",
          "worker_entry_price","worker_expiry_iso","platform_symbol","platform_entry_timestamp",
          "platform_entry_price","platform_expiry_timestamp","platform_expiry_price",
          "platform_result","payout_pct","worker_result","notes"]

def get_json(url, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "phase-f-prefill/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            last = e
            if isinstance(e, urllib.error.HTTPError) and e.code in (403, 429):
                time.sleep(3 + i * 3)   # backoff on rate-limit
                continue
            break
    raise last

def asset_class(pair):
    base = pair.split("/")[0]
    if base in ("EUR","GBP","USD","JPY","AUD","NZD","CAD","CHF","SEK","NOK","DKK","PLN","HUF","CZK","RON","BGN","HRK","ISK","RUB","TRY","UAH","HKD","SGD","CNH","CNY","KRW","TWD","THB","MYR","PHP","IDR","INR","VND","PKR","BDT","LKR","MXN","BRL","CLP","COP","PEN","ARS","AED","SAR","ILS","JOD","KWD","BHD","OMR","QAR","ZAR","EGP","NGN","KES","GHS","TZS","UGX","MAD"):
        return "FOREX"
    if "OTC" in pair:
        return "OTC"
    return "CRYPTO"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=1)
    ap.add_argument("--all", action="store_true", help="use full forward window (>= 2026-08-01)")
    ap.add_argument("--out", default="phase_f_prefilled.csv")
    ap.add_argument("--merge", action="store_true", help="keep existing platform columns from --out if present")
    args = ap.parse_args()

    cutoff = "2026-08-01T00:00:00" if args.all else (datetime.utcnow() - timedelta(days=args.days)).strftime("%Y-%m-%dT00:00:00")

    # load existing (for merge)
    existing = {}
    if args.merge:
        try:
            with open(args.out, encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    if row.get("worker_timestamp"):
                        existing[row["worker_timestamp"] + "|" + row.get("pair","")] = row
        except FileNotFoundError:
            pass

    rows = []
    for pair in PAIRS:
        url = f"{API}/api/history?pair={pair.replace('/','%2F')}&limit=500"
        try:
            data = get_json(url)
            time.sleep(0.6)   # polite spacing between pairs
        except Exception as e:
            print(f"  !! {pair}: {e}")
            continue
        for s in data.get("signals", []):
            ts = s.get("timestamp", "")
            if ts < cutoff:
                continue
            if s.get("result") not in ("WIN", "LOSS"):
                continue  # pending/unknown → not a decided observation
            key = ts + "|" + pair
            if args.merge and key in existing:
                row = existing[key]  # keep platform columns
                row["worker_timestamp"] = ts
                row["pair"] = pair
                row["worker_result"] = s.get("result")
                continue
            row = {
                "obs_id": "",
                "worker_timestamp": ts,
                "pair": pair,
                "asset_class": asset_class(pair),
                "target_pair": "TRUE" if pair in TARGET else "FALSE",
                "direction": s.get("direction"),
                "worker_entry_price": s.get("entryPrice"),
                "worker_expiry_iso": s.get("expiryTime"),
                "platform_symbol": "",
                "platform_entry_timestamp": "",
                "platform_entry_price": "",
                "platform_expiry_timestamp": "",
                "platform_expiry_price": "",
                "platform_result": "",
                "payout_pct": "",
                "worker_result": s.get("result"),
                "notes": "",
            }
            rows.append(row)

    # merge: append new rows
    merged = list(existing.values()) + rows
    # sort by timestamp
    merged.sort(key=lambda r: r.get("worker_timestamp", ""))

    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        w.writerows(merged)

    n_target = sum(1 for r in merged if r.get("target_pair") == "TRUE")
    print(f"✔ {len(merged)} worker observations → {args.out}")
    print(f"  target pairs (USD/JPY, AUD/USD, DOT/USD): {n_target}")
    print(f"  অসম্পূর্ণ (platform columns বাকি): {sum(1 for r in merged if not r.get('platform_result'))}")

if __name__ == "__main__":
    main()
