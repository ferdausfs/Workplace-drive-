#!/usr/bin/env python3
"""
D4 ML — run with 08-06 data (Arena main agent, independent)

Two runs:
  1. LEGIT: signal-time features only (things knowable at signal time).
     entryHit is NOT included — it is post-hoc (measured during expiry window)
     AND provably a tautology with result (entryHit=false => WIN is
     mathematically guaranteed with the expiry±5min window). Including it
     would be leakage and fake 100%.
  2. LEAKAGE DIAGNOSTIC: same model + entryHit — demonstrates exactly how a
     cheating model would "win", so nobody mistakes it for signal quality.

Bar: 55.6% WR (80% payout breakeven). Chronological split, Wilson CI.
"""
import argparse, glob, json, os, math
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score

BREAKEVEN = 0.556

def load_forward(floor, data_dir="phase_f_forward"):
    seen = {}
    for day in sorted(glob.glob(os.path.join(data_dir, "*/"))):
        for f in glob.glob(day.rstrip("/") + "/*.json"):
            name = os.path.basename(f)
            if name in ("pairs.json", "health.json"): continue
            try: data = json.load(open(f))
            except Exception: continue
            for s in data.get("signals", []):
                if s.get("id"): seen[s["id"]] = s
    rows = []
    for s in seen.values():
        ts = s.get("timestamp", "")
        if ts < floor: continue
        if s.get("result") not in ("WIN", "LOSS"): continue
        rows.append(s)
    return rows

def conf_num(s):
    c = s.get("confidence", "0%")
    if isinstance(c, (int, float)): return float(c)
    try: return float(str(c).replace("%", ""))
    except: return 50.0

def grade_of(s):
    g = s.get("grade")
    if isinstance(g, dict): return g.get("grade", "?")
    return g or "?"

def struct_overall(s):
    sv = s.get("structureVerdict")
    if isinstance(sv, dict): return sv.get("overall") or "?"
    return sv or "?"

def build_frame(rows, with_entryHit=False):
    recs = []
    for s in rows:
        pair = s.get("pair", "?")
        sessions = s.get("session") or []
        sess = sessions[0] if sessions else "?"
        rec = {
            "pair": pair,
            "asset_type": "FOREX" if pair in ("EUR/USD","GBP/USD","GBP/CHF","USD/CAD","USD/CHF","USD/JPY","AUD/USD") else "CRYPTO",
            "direction": s.get("direction", "?"),
            "confidence": conf_num(s),
            "grade": grade_of(s),
            "regime": s.get("marketRegime", "?"),
            "alignment": s.get("alignment", "?"),
            "structure_overall": struct_overall(s),
            "session": sess,
            "hour": int(s["timestamp"][11:13]),
            "dow": int(pd.Timestamp(s["timestamp"]).dayofweek),
            "win": 1 if s["result"] == "WIN" else 0,
            "ts": s["timestamp"],
        }
        if with_entryHit:
            eh = s.get("entryHit")
            rec["entryHit"] = 1.0 if eh is True else (0.0 if eh is False else -1.0)
        recs.append(rec)
    df = pd.DataFrame(recs)
    cats = ["pair","asset_type","direction","grade","regime","alignment","structure_overall","session"]
    df = pd.get_dummies(df, columns=cats, prefix=["p","at","dir","g","reg","align","str","sess"])
    return df

def wilson(w, n, z=1.96):
    if n == 0: return (0, 0, 0)
    p = w / n
    d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = z * math.sqrt((p*(1-p) + z*z/(4*n))/n) / d
    return p, max(0, c-h), min(1, c+h)

def run(df, test_days, label):
    df = df.sort_values("ts").reset_index(drop=True)
    feat_cols = [c for c in df.columns if c not in ("win", "ts")]
    train = df[~df["ts"].str[:10].isin(test_days)]
    test = df[df["ts"].str[:10].isin(test_days)]
    print(f"\n── {label} ──")
    print(f"  train n={len(train)}  test n={len(test)}")

    X_train, y_train = train[feat_cols], train["win"]
    X_test, y_test = test[feat_cols], test["win"]
    model = XGBClassifier(n_estimators=120, max_depth=3, learning_rate=0.08,
        subsample=0.8, colsample_bytree=0.8, eval_metric="logloss",
        random_state=42, verbosity=0)
    model.fit(X_train, y_train)
    proba = model.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)
    acc = accuracy_score(y_test, pred)

    # confident-only
    mask = (proba >= 0.55) | (proba <= 0.45)
    sel_n = int(mask.sum()); sel_w = int(y_test[mask].sum())
    print(f"  all-pred accuracy: {acc*100:.1f}%")
    if sel_n >= 10:
        sp, slo, shi = wilson(sel_w, sel_n)
        verdict = "✅ breakeven (tentative)" if slo > BREAKEVEN else ("⚠️ below breakeven — no edge" if shi < BREAKEVEN else "⚠️ ambiguous")
        print(f"  confident-only WR (all conf preds): n={sel_n} WR {sp*100:.1f}% (CI {slo*100:.1f}-{shi*100:.1f}%)  → {verdict}")

    # ── TRADING METRIC: precision@WIN (WR among model's WIN calls) ──
    for thr, thrlbl in [(0.5, "p>=0.50"), (0.55, "p>=0.55")]:
        pred_w = proba >= thr
        nw = int(pred_w.sum()); ww = int(y_test[pred_w].sum())
        if nw >= 10:
            wp, wlo, whi = wilson(ww, nw)
            v = "✅ beats breakeven" if wlo > BREAKEVEN else ("⚠️ below breakeven" if whi < BREAKEVEN else "⚠️ ambiguous")
            print(f"  [TRADE] WIN-call subset ({thrlbl}): n={nw} ({nw/len(test)*100:.0f}% of test) "
                  f"WR {wp*100:.1f}% (CI {wlo*100:.1f}-{whi*100:.1f}%)  → {v}")
        elif nw > 0:
            print(f"  [TRADE] WIN-call subset ({thrlbl}): n={nw} — too small")
        else:
            print(f"  [TRADE] WIN-call subset ({thrlbl}): n=0 — model never called WIN")

    imp = sorted(zip(feat_cols, model.feature_importances_), key=lambda x: -x[1])[:10]
    print("  top features:")
    for name, v in imp:
        print(f"    {name:32s} {v:.3f}")
    return model

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-date", default="2026-08-01T00:00:00")
    ap.add_argument("--test-days", type=int, default=1)
    ap.add_argument("--data-dir", default="phase_f_forward")
    args = ap.parse_args()

    rows = load_forward(args.min_date, args.data_dir)
    days = sorted(set(r["timestamp"][:10] for r in rows))
    print(f"═══ D4 ML — 08-06 data ═══")
    print(f"forward decided: {len(rows)} | days: {days}")
    print(f"breakeven bar: {BREAKEVEN*100:.1f}% (80% payout)")

    # engine baseline
    engine_w = sum(1 for r in rows if r["result"] == "WIN")
    p, lo, hi = wilson(engine_w, len(rows))
    print(f"\n── Baseline: engine WR: {engine_w}/{len(rows)} = {p*100:.1f}% (CI {lo*100:.1f}-{hi*100:.1f}%)")

    test_days = days[-args.test_days:]
    print(f"\n  TEST days: {test_days} | TRAIN: {days[:-args.test_days]}")

    # 1. LEGIT run — signal-time features
    df = build_frame(rows, with_entryHit=False)
    run(df, test_days, "LEGIT MODEL (signal-time features only — entryHit EXCLUDED, leakage)")

    # 2. LEAKAGE DIAGNOSTIC — with entryHit
    df2 = build_frame(rows, with_entryHit=True)
    run(df2, test_days, "LEAKAGE DIAGNOSTIC (entryHit included — post-hoc + tautology)")

    print("\n═══ honest notes ═══")
    print(" 1. entryHit is measured AFTER the expiry window (post-hoc) and is a")
    print("    mathematical tautology with result: entryHit=false => WIN is")
    print("    guaranteed with the expiry±5min window. ANY model using it is")
    print("    cheating — the")
    print("    diagnostic above shows the fake 'edge' it creates.")
    print(" 2. Only the LEGIT run counts for Phase F. If its confident-only CI")
    print("    stays below 55.6%, no conditional strategy.")
    print(" 3. 08-06 is a partial pre-merge day; rerun tomorrow for post-merge data.")

if __name__ == "__main__":
    main()
