#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D4 v2.1 — AVOIDANCE MODEL with RAW INDICATORS + EDGE FEATURES (Phase F)
========================================================================

GOAL
  Engine pool WR is ~42.5% (breakeven @ 80% payout = 55.6%). D4 v2 (PR #11,
  scripts/d4_v2_avoidance.py in Ftt-Otc-v6) proved that signal-time features
  available pre-2026-08-09 (conf / grade / regime / pair ...) cap the avoidance
  edge at ~52-58% with Wilson CI-low < 50% — no deployable gate.

  PR #13 (worker d696c6b) now persists `signalIndicators` on history rows
  (RSI / ATR% / ADX / BB-bandwidth at signal time) and PR #15 (worker bad7140,
  v6.10.0) adds the input-side edge feature values (hourMult, sessionRange,
  bbState, atrPercentile, totalMult, ...) folded into the same
  `signalIndicators` record (see src/history/stats.js ~line 200).

  THE QUESTION: with raw indicators + edge-feature values added, can an
  avoidance model isolate a TRADE subset with WR >= 55.6% AND Wilson
  CI-low >= 50% on a TRUE chronological holdout (R1), at coverage >= 15% (R3)?

WHAT IT DOES
  1. Loads phase_f_forward/*/*.json (18 pairs), dedups by id (later/more-complete
     record wins), keeps decided WIN/LOSS only.
  2. DATA AUDIT: decided + indicator-complete coverage per day. This is what
     makes the "insufficient data" verdict explicit and honest.
  3. v2-FEATURES RECAP on ALL decided rows (auto-holdout = newest day with
     >= MIN_HOLDOUT decided rows) — regression check that the v2 ceiling still
     stands on the current snapshot.
  4. PRIMARY v2.1 RUN on indicator-complete rows only:
       HOLDOUT = newest day with >= MIN_HOLDOUT (default 30) decided
                 indicator-complete rows (auto-picked; --holdout-day overrides).
       TRAIN   = all indicator-complete rows with signal day < HOLDOUT day.
       Modes:  train >= MIN_TRAIN (300) -> FULL RUN (gate certification possible)
               train >= 30, holdout >= 20 -> EXPLORATORY (labeled, never deploy)
               else -> INSUFFICIENT DATA verdict (pipeline still exits 0).
  5. Model: pure-numpy ridge LOGISTIC REGRESSION on P(WIN) (deterministic,
     portable). Optional sklearn / XGBoost cross-checks (degrade gracefully).
     Avoidance threshold tau selected on TRAIN ONLY (max TRAIN-subset WR at
     coverage >= 15% floor; ties -> higher coverage), frozen, applied to the
     untouched holdout. Wilson CI + coverage + EV/trade reported.
  6. GATE ARTIFACT (R4): scripts/d4v21_avoidance_gate.js —
       * R1 met  -> full coefficient/rule table, CERTIFIED: true
       * R1 unmet / insufficient data -> SAFE STUB, CERTIFIED: false
                    (d4v21Avoid() passes everything through; a worker can wire
                     the import today without gating anything).

LEAKAGE DISCIPLINE (R2)
  - Features are SIGNAL-TIME ONLY: pair, assetType, direction, bestTF,
    marketRegime, sessionQuality, grade, alignment, structureVerdict, confidence,
    coreConfidence, hour, dow + signalIndicators/edge values the worker stamped
    at signal time + `rsiChase` derived from (rsi, direction) against the STATIC
    config thresholds (BUY>55 / SELL<45 — src/analysis/edgeFeatures.js).
  - result / entryHit / entryHitLegacy / exitPrice / checkedAt / entryPrice /
    fillStatus NEVER enter the feature space.
  - Categorical vocabulary + numeric median/std are fit on TRAIN only; holdout
    rows with unseen categories encode as all-zero; numerics median-impute.
  - tau chosen on TRAIN only. The post-hoc holdout sweep is printed for
    illustration and is explicitly flagged as threshold-fishing if it "passes".

RE-RUN (R5 — fresh snapshots need no edits)
    tar -xzf data/phase_f_forward_<newest>.tar.gz -C phase_f_forward
    python3 scripts/d4_v21_avoidance.py --data-dir phase_f_forward
    # optional: pip install numpy (required); scikit-learn xgboost (optional)

DEPENDENCIES: python3 + numpy. sklearn / xgboost optional cross-checks only.
"""
import argparse
import datetime
import glob
import json
import math
import os
import sys
from collections import OrderedDict

try:
    import numpy as np
except ImportError:
    sys.stderr.write(
        "\nERROR: numpy is required (the only hard dependency).\n"
        "       pip install numpy        # or: pip install numpy scikit-learn xgboost\n\n"
    )
    raise SystemExit(2)

BREAKEVEN = 0.556          # 80% payout: WR*0.80 - (1-WR)*1.00 >= 0  ->  WR >= 0.556
PAYOUT = 0.80
COVERAGE_FLOOR_R1 = 0.15   # R1/R3 minimum coverage for the TRADE subset

# Asset map (worker convention: crypto tickers vs forex).
CRYPTO_TOKENS = ("BTC", "ETH", "SOL", "DOGE", "XRP", "ADA", "LINK", "AVAX", "BNB", "DOT")

# ── feature schema ────────────────────────────────────────────────────────
# v2 signal-time features (always available).
V2_CAT = ["pair", "assetType", "direction", "bestTF", "marketRegime",
          "sessionQuality", "grade", "alignment", "structureVerdict"]
V2_NUM = ["confidence", "coreConfidence", "hour", "dow"]

# PR #13 raw indicators persisted in row.signalIndicators (+ PR #15 edge values
# folded into the same record; an `edge` block is also accepted if a future
# snapshot persists it directly). Only these names are read — outcome fields
# are never touched.
IND_NUMERIC = ["rsi", "atrPct", "adx", "bbBandwidth"]                      # PR #13
EDGE_NUMERIC = ["hourMult", "sessionRange", "sessionRangeMult", "atrPercentile",
                "volMult", "atrMult", "recentFormWr", "recentFormMult",
                "totalMult"]                                                # PR #15
EDGE_CAT = ["bbState"]                        # HIGH_VOL / MID_SQUEEZE / DEAD_SQUEEZE
DERIVED_CAT = ["rsiChase"]                    # derived signal-time (static config)

# Indicator-completeness: all four PR #13 numerics present and numeric.
IC_REQUIRED = ["rsi", "atrPct", "adx", "bbBandwidth"]

V21_CAT_FULL = V2_CAT + EDGE_CAT + DERIVED_CAT
V21_NUM_FULL = V2_NUM + IND_NUMERIC + EDGE_NUMERIC

# Reduced set for the exploratory small-sample mode (fewer columns, more ridge:
# with n_train < 300 the full one-hot space overfits — exploratory only anyway).
V21_CAT_SMALL = ["direction", "assetType", "bbState", "rsiChase", "grade"]
V21_NUM_SMALL = ["confidence", "hour", "rsi", "atrPct", "adx", "bbBandwidth", "totalMult"]


# ─────────────────────────── value helpers ────────────────────────────────
def _to_num(v):
    """Best-effort numeric coercion (history values may be strings)."""
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v) if math.isfinite(float(v)) else None
    if isinstance(v, str):
        try:
            f = float(v.replace("%", "").strip())
            return f if math.isfinite(f) else None
        except Exception:
            return None
    return None


def _conf_num(s):
    return _to_num(s.get("confidence"))


def _grade(s):
    g = s.get("grade")
    if isinstance(g, dict):
        return g.get("grade")
    return g


def _struct(s):
    v = s.get("structureVerdict")
    if isinstance(v, dict):
        return v.get("overall")
    return v


def _asset(pair, is_otc):
    if is_otc:
        return "OTC"
    return "CRYPTO" if any(t in (pair or "") for t in CRYPTO_TOKENS) else "FOREX"


def indicators_of(s):
    """Merged signal-time indicator/edge record:
    {**row.edge, **row.signalIndicators}  (signalIndicators = persisted source
    of truth since PR #13/#15; `edge` accepted for future snapshots)."""
    out = {}
    for src in (s.get("edge"), s.get("signalIndicators")):
        if isinstance(src, dict):
            for k, v in src.items():
                if v is not None:
                    out[k] = v
                else:
                    out.setdefault(k, v)
    return out or None


def indicator_completeness(s):
    """(n_present, all_four) over IC_REQUIRED numeric fields."""
    ind = indicators_of(s) or {}
    n = sum(1 for k in IC_REQUIRED if _to_num(ind.get(k)) is not None)
    return n, n == len(IC_REQUIRED)


def extract_features(s):
    """Flat OrderedDict of ALL candidate signal-time features.
    Outcome fields (result/entryHit*/exitPrice/checkedAt/entryPrice/fillStatus)
    are NEVER read here."""
    pair = s.get("pair", "?")
    is_otc = bool(s.get("isOTC"))
    ts = s.get("timestamp", "") or ""
    try:
        hour = int(ts[11:13])
    except Exception:
        hour = None
    try:
        dow = int(datetime.date.fromisoformat(ts[:10]).weekday())
    except Exception:
        dow = None

    ind = indicators_of(s) or {}

    f = OrderedDict()
    # v2 features
    f["pair"] = pair
    f["assetType"] = _asset(pair, is_otc)
    f["direction"] = s.get("direction")
    f["bestTF"] = s.get("bestTF") or (ind.get("bestTF") if isinstance(ind.get("bestTF"), str) else None)
    f["marketRegime"] = s.get("marketRegime")
    f["sessionQuality"] = s.get("sessionQuality")
    f["grade"] = _grade(s)
    f["alignment"] = s.get("alignment")
    f["structureVerdict"] = _struct(s)
    f["confidence"] = _conf_num(s)
    f["coreConfidence"] = _to_num(s.get("coreConfidence"))
    f["hour"] = hour
    f["dow"] = dow
    # raw indicators (PR #13)
    for k in IND_NUMERIC:
        f[k] = _to_num(ind.get(k))
    # edge feature values (PR #15) — numeric part
    for k in EDGE_NUMERIC:
        f[k] = _to_num(ind.get(k))
    # edge categorical
    bb = ind.get("bbState")
    f["bbState"] = str(bb) if bb is not None else None
    # derived, signal-time, static thresholds (edgeFeatures.js RSI_DIRECTION_GATE):
    rsi, d = f["rsi"], s.get("direction")
    if rsi is not None and d in ("BUY", "SELL"):
        chasing = (d == "BUY" and rsi > 55.0) or (d == "SELL" and rsi < 45.0)
        f["rsiChase"] = "CHASE" if chasing else "OK"
    else:
        f["rsiChase"] = None
    return f


# ───────────────────────────── data loading ───────────────────────────────
def load_decided(data_dir):
    """Dedup by id (later day folder wins ties; most-complete record wins),
    keep decided WIN/LOSS only. Sorted deterministically by (timestamp, id)."""
    seen = {}
    for f in sorted(glob.glob(os.path.join(data_dir, "*", "[A-Z]*_*.json"))):
        name = os.path.basename(f)
        if name in ("health.json", "pairs.json"):
            continue
        try:
            d = json.load(open(f))
        except Exception:
            continue
        for s in d.get("signals") or []:
            sid = s.get("id")
            if not sid:
                continue
            prev = seen.get(sid)
            if prev is None or len(s.keys()) > len(prev.keys()):
                seen[sid] = s
    rows = [s for s in seen.values() if s.get("result") in ("WIN", "LOSS")]
    rows.sort(key=lambda s: ((s.get("timestamp") or ""), s.get("id") or ""))
    return rows


def day_of(s):
    return (s.get("timestamp") or "")[:10]


# ───────────────────────────── matrix build ───────────────────────────────
class Encoder:
    """One-hot (categorical) + standardized (numeric). Vocabulary and
    median/std are fit on TRAIN ONLY (leakage guard)."""
    def __init__(self, cat_features, num_features):
        self.cat_features = list(cat_features)
        self.num_features = list(num_features)
        self.cat_levels = {}
        self.num_med = {}
        self.num_std = {}
        self.feature_names = []
        self._col_index = {}

    def fit(self, feat_rows):
        for c in self.cat_features:
            self.cat_levels[c] = sorted({str(r[c]) for r in feat_rows if r.get(c) is not None})
        for n in self.num_features:
            vals = [r[n] for r in feat_rows if isinstance(r.get(n), (int, float))]
            med = float(np.median(vals)) if vals else 0.0
            std = float(np.std(vals)) if vals else 1.0
            if std < 1e-9:
                std = 1.0
            self.num_med[n] = med
            self.num_std[n] = std
        cols = [f"{c}={lv}" for c in self.cat_features for lv in self.cat_levels[c]]
        cols += self.num_features
        self.feature_names = cols
        self._col_index = {c: i for i, c in enumerate(cols)}
        return self

    def transform(self, feat_rows):
        X = np.zeros((len(feat_rows), len(self.feature_names)), dtype=np.float64)
        for i, r in enumerate(feat_rows):
            for c in self.cat_features:
                lv = r.get(c)
                if lv is None:
                    continue
                j = self._col_index.get(f"{c}={lv}")
                if j is not None:
                    X[i, j] = 1.0
            for n in self.num_features:
                v = r.get(n)
                if not isinstance(v, (int, float)):
                    v = self.num_med[n]           # TRAIN median imputation
                X[i, self._col_index[n]] = (v - self.num_med[n]) / self.num_std[n]
        return X


# ─────────────────────────── pure-numpy logistic ──────────────────────────
class LogReg:
    """Ridge logistic regression, full-batch gradient descent.
    Deterministic (zero init, fixed iterations, float64). The fitted (w, b) +
    the TRAIN encoder medians/stds ARE the portable artifact (JS gate)."""
    def __init__(self, l2=1.0, lr=0.5, n_iter=8000, class_weight="none"):
        self.l2 = l2
        self.lr = lr
        self.n_iter = n_iter
        self.class_weight = class_weight
        self.w = None
        self.b = 0.0

    @staticmethod
    def _sigmoid(z):
        return np.where(z >= 0, 1.0 / (1.0 + np.exp(-z)),
                        np.exp(z) / (1.0 + np.exp(z)))

    def fit(self, X, y):
        n, d = X.shape
        self.w = np.zeros(d)
        p0 = min(max(y.mean(), 1e-6), 1 - 1e-6)
        self.b = float(np.log(p0 / (1 - p0)))
        if self.class_weight == "balanced":
            n_pos = max(1.0, y.sum())
            n_neg = max(1.0, n - y.sum())
            sw = np.where(y == 1, n / (2 * n_pos), n / (2 * n_neg))
        else:
            sw = np.ones(n)
        sw_sum = sw.sum()
        # NOTE (v2.1 fix): ridge term is NOT divided by n — l2 therefore has
        # sklearn-style strength (C ≈ 1/l2), not the v2 script's l2/n which
        # made regularization vanish for large n and overfit the slice noise.
        for _ in range(self.n_iter):
            z = X @ self.w + self.b
            p = self._sigmoid(z)
            err = (p - y) * sw
            gw = X.T @ err / sw_sum + self.l2 * self.w
            gb = err.sum() / sw_sum
            self.w -= self.lr * gw
            self.b -= self.lr * gb
        return self

    def predict_proba(self, X):
        return self._sigmoid(X @ self.w + self.b)


# ─────────────────────────────── metrics ──────────────────────────────────
def wilson(w, n, z=1.96):
    if n == 0:
        return 0.0, 0.0, 0.0
    p = w / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / den
    return p, max(0.0, c - h), min(1.0, c + h)


def profit_metrics(win_mask, n_total):
    n = int(win_mask.size)
    w = int(win_mask.sum())
    p, lo, hi = wilson(w, n)
    cov = n / n_total if n_total else 0.0
    edge = p * PAYOUT - (1 - p) * 1.0    # EV per trade in stake units @80% payout
    return dict(n=n, w=w, wr=p, ci_lo=lo, ci_hi=hi, coverage=cov, edge=edge)


def eval_at_tau(p, y, tau, n_total):
    return profit_metrics(y[p >= tau] == 1, n_total)


def _auc(p, y):
    """ROC-AUC via Mann-Whitney with tie-averaged ranks. Deterministic."""
    pos = int(y.sum())
    neg = len(y) - pos
    if pos == 0 or neg == 0:
        return 0.5
    o = np.argsort(p, kind="stable")
    ranks = np.empty(len(p), dtype=np.float64)
    sp = p[o]
    i = 0
    while i < len(sp):
        j = i
        while j + 1 < len(sp) and sp[j + 1] == sp[i]:
            j += 1
        ranks[o[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    s = ranks[y == 1].sum()
    return float((s - pos * (pos + 1) / 2.0) / (pos * neg))


def _rank_corr(a, b):
    aa = a.argsort(kind="stable").argsort(kind="stable").astype(float)
    bb = b.argsort(kind="stable").argsort(kind="stable").astype(float)
    aa -= aa.mean()
    bb -= bb.mean()
    da = math.sqrt((aa ** 2).sum())
    db = math.sqrt((bb ** 2).sum())
    if da < 1e-12 or db < 1e-12:
        return 0.0
    return float((aa * bb).sum() / (da * db))


# ─────────────────── threshold selection (TRAIN only) ─────────────────────
def select_threshold(p_train, y_train, coverage_floor, tie_eps=0.02):
    """Pre-committed gate. On TRAIN ONLY:
      1. find the max TRAIN-subset WR over coverages >= floor;
      2. ROBUSTNESS TIE-BREAK: take the LARGEST coverage whose WR is within
         tie_eps of that max (a razor-thin argmax tail is noise-ordered — the
         widest near-optimal subset is the one that reproduces).
    tau is placed at the midpoint between adjacent scores so the JS gate
    reproduces membership exactly, even with float ties.
    TRAIN NEVER sees holdout."""
    n = len(p_train)
    order = np.argsort(-p_train, kind="stable")
    p_sorted = p_train[order]
    cum_w = np.cumsum(y_train[order])
    k_min = max(1, int(math.ceil(coverage_floor * n)))
    ks = range(k_min, n + 1)
    wrs = {k: cum_w[k - 1] / k for k in ks}
    wr_max = max(wrs.values())
    k = max(k for k in ks if wrs[k] >= wr_max - tie_eps)
    hi = p_sorted[k - 1]
    lo = p_sorted[k] if k < n else 0.0
    tau = (hi + lo) / 2.0 if k < n else max(0.0, hi - 1e-9)
    sel = profit_metrics(y_train[order[:k]] == 1, n)
    return tau, sel, (p_sorted, cum_w)


def sweep(p, y, n_total, label):
    """Coverage sweep — ILLUSTRATION ONLY. On holdout this is post-hoc
    (threshold-fishing); the frozen TRAIN tau above is the only fair gate."""
    order = np.argsort(-p, kind="stable")
    ys = y[order]
    cw = np.cumsum(ys)
    n = len(ys)
    print(f"   [{label} curve] cov    n    WR%     Wilson CI       edge ")
    for frac in (0.15, 0.20, 0.25, 0.33, 0.50, 0.67, 0.80, 1.00):
        k = int(round(n * frac))
        if k < 1 or k > n:
            continue
        wr = cw[k - 1] / k
        _, lo, hi = wilson(int(cw[k - 1]), k)
        edge = wr * PAYOUT - (1 - wr) * 1.0
        flag = "  <- R1 coverage floor" if abs(frac - COVERAGE_FLOOR_R1) < 1e-9 else ""
        print(f"    {frac*100:>4.0f}% {k:>5} {wr*100:>5.1f}   [{lo*100:>4.1f}-{hi*100:>4.1f}] {edge:>+7.3f}{flag}")


# ─────────────────────── optional cross-checks ────────────────────────────
def sklearn_check(Xtr, ytr, Xva):
    try:
        from sklearn.linear_model import LogisticRegression
    except Exception:
        return None
    m = LogisticRegression(C=1.0, penalty="l2", solver="lbfgs",
                           max_iter=8000, random_state=42)
    m.fit(Xtr, ytr)
    return m.predict_proba(Xtr)[:, 1], m.predict_proba(Xva)[:, 1]


def xgb_oracle(Xtr, ytr, Xva):
    try:
        from xgboost import XGBClassifier
    except Exception:
        return None
    m = XGBClassifier(n_estimators=200, max_depth=3, learning_rate=0.05,
                      subsample=0.8, colsample_bytree=0.8,
                      eval_metric="logloss", random_state=42, verbosity=0,
                      reg_lambda=2.0)
    m.fit(Xtr, ytr)
    return m.predict_proba(Xtr)[:, 1], m.predict_proba(Xva)[:, 1]


# ─────────────────────────────── printing ─────────────────────────────────
def _print_row(label, m, n_total, primary=False):
    verdict = ("PASS" if (m["wr"] >= BREAKEVEN and m["ci_lo"] >= 0.50
                          and m["coverage"] >= COVERAGE_FLOOR_R1) else "fail")
    star = "  <<<" if primary else ""
    print(f"   {label}: n={m['n']:>4} ({m['coverage']*100:>4.0f}% cov) "
          f"WR={m['wr']*100:>5.1f}% CI[{m['ci_lo']*100:>4.1f}-{m['ci_hi']*100:>4.1f}] "
          f"edge={m['edge']:+.3f}  [{verdict}]{star}")


def print_coef_table(model, enc):
    print(f"\n   intercept b0 = {model.b:+.4f}")
    print("   numeric coefficients (standardized scale):")
    for n in enc.num_features:
        j = enc._col_index[n]
        print(f"      {n:16s} w={model.w[j]:+.4f}  "
              f"(train med={enc.num_med[n]:.3f} std={enc.num_std[n]:.3f})")
    cat = [(c, w) for c, w in zip(enc.feature_names, model.w) if "=" in c]
    cat.sort(key=lambda x: x[1])
    print("   categorical — TOP 10 (WIN-associated, KEEP):")
    for name, w in cat[-10:][::-1]:
        print(f"      {name:36s} {w:+.4f}")
    print("   categorical — BOTTOM 10 (LOSS-associated, SKIP):")
    for name, w in cat[:10]:
        print(f"      {name:36s} {w:+.4f}")


# ────────────────────────────── model runner ──────────────────────────────
def run_model(train_rows, holdout_rows, label, cat_feats, num_feats,
              l2=1.0, class_weight="none", coverage_floor=COVERAGE_FLOOR_R1,
              cross_checks=True, per_day=True, ind_rows_ho_total=None):
    """Fit numpy logistic on TRAIN, freeze tau on TRAIN, evaluate on HOLDOUT.
    Returns the fitted artifacts + holdout metrics (the R1 evidence)."""
    print("\n" + "=" * 78)
    print(f"  {label}")
    print("=" * 78)
    n_total_ho = ind_rows_ho_total if ind_rows_ho_total else len(holdout_rows)

    feat_tr = [extract_features(s) for s in train_rows]
    feat_ho = [extract_features(s) for s in holdout_rows]
    y_tr = np.array([1.0 if s["result"] == "WIN" else 0.0 for s in train_rows])
    y_ho = np.array([1.0 if s["result"] == "WIN" else 0.0 for s in holdout_rows])

    enc = Encoder(cat_feats, num_feats).fit(feat_tr)
    Xtr = enc.transform(feat_tr)
    Xho = enc.transform(feat_ho)

    base_tr = profit_metrics(y_tr == 1, len(y_tr))
    base_ho = profit_metrics(y_ho == 1, n_total_ho)
    print(f"\n  TRAIN n={len(y_tr)}  WR={base_tr['wr']*100:.1f}% "
          f"(CI {base_tr['ci_lo']*100:.1f}-{base_tr['ci_hi']*100:.1f}%)")
    print(f"  HOLDOUT n={len(y_ho)}  WR={base_ho['wr']*100:.1f}% "
          f"(CI {base_ho['ci_lo']*100:.1f}-{base_ho['ci_hi']*100:.1f}%)  <- holdout base "
          f"(breakeven {BREAKEVEN*100:.1f}%)")

    lr_ = LogReg(l2=l2, lr=0.5, n_iter=8000, class_weight=class_weight).fit(Xtr, y_tr)
    p_tr = lr_.predict_proba(Xtr)
    p_ho = lr_.predict_proba(Xho)
    print(f"\n  [numpy logistic] l2={l2} w={class_weight}  "
          f"TRAIN rank-AUC={_auc(p_tr, y_tr):.3f}  HOLDOUT rank-AUC={_auc(p_ho, y_ho):.3f}")

    tau, sel, _ = select_threshold(p_tr, y_tr, coverage_floor)
    print(f"\n  >> tau selected on TRAIN only: P(WIN) >= {tau:.6f}")
    print(f"     TRAIN-subset @tau: WR={sel['wr']*100:.1f}% "
          f"CI[{sel['ci_lo']*100:.1f}-{sel['ci_hi']*100:.1f}] "
          f"n={sel['n']} (cov {sel['coverage']*100:.0f}%)")

    tr_sub = eval_at_tau(p_tr, y_tr, tau, len(y_tr))
    ho_sub = eval_at_tau(p_ho, y_ho, tau, n_total_ho)
    print("\n  ---- TRADE-subset @ frozen TRAIN tau ----")
    _print_row("TRAIN-subset  ", tr_sub, len(y_tr))
    _print_row("HOLDOUT-subset", ho_sub, n_total_ho, primary=True)

    print("\n  (post-hoc HOLDOUT coverage-sweep — ILLUSTRATION, threshold-fishing "
          "if read as a gate):")
    sweep(p_ho, y_ho, n_total_ho, "HOLDOUT")

    if per_day and holdout_rows:
        days = sorted({day_of(s) for s in holdout_rows})
        print(f"\n   per-day holdout stability @ frozen tau={tau:.4f}:")
        for d in days:
            idx = [i for i, s in enumerate(holdout_rows) if day_of(s) == d]
            bn = len(idx)
            bw = int(y_ho[idx].sum())
            bp, _, _ = wilson(bw, bn)
            mask = p_ho[idx] >= tau
            tn = int(mask.sum())
            tw = int(y_ho[idx][mask].sum())
            tp, tlo, thi = wilson(tw, tn) if tn else (0, 0, 0)
            print(f"   {d}: ALL n={bn:>3} WR={bp*100:>4.1f}%   |   "
                  f"TRADE n={tn:>3} WR={tp*100:>4.1f}% CI[{tlo*100:>4.1f}-{thi*100:>4.1f}]")

    # Honesty audit: best point on the HOLDOUT curve, with the
    # multiple-comparison caveat. A "pass" here is NOT evidence.
    order = np.argsort(-p_ho, kind="stable")
    ys = y_ho[order]
    cw = np.cumsum(ys)
    floor_k = max(1, int(math.ceil(COVERAGE_FLOOR_R1 * len(ys))))
    best_posthoc = None
    for k in range(floor_k, len(ys) + 1):
        wr = cw[k - 1] / k
        _, lo, hi = wilson(int(cw[k - 1]), k)
        ok = wr >= BREAKEVEN and lo >= 0.50
        score = (1 if ok else 0, wr, lo)
        if best_posthoc is None or score > best_posthoc[0]:
            best_posthoc = (score, k, wr, lo, hi, ok)
    if best_posthoc is not None and len(ys) > 0:
        _, k, wr, lo, hi, ok = best_posthoc
        n_checked = len(ys) - floor_k + 1
        print(f"\n   HONESTY AUDIT — best post-hoc point on HOLDOUT curve:")
        print(f"     scanned {n_checked} thresholds; best k={k} "
              f"(cov={k/len(ys)*100:.0f}%): WR={wr*100:.1f}% CI[{lo*100:.1f}-{hi*100:.1f}]")
        if ok:
            print(f"     >>> 'passes' R1 only post-hoc (max over {n_checked} holdout-peeking")
            print(f"         thresholds) — NOT credible; the pre-committed TRAIN gate stands.")
        else:
            print("     >>> no post-hoc point clears R1 either.")

    if cross_checks:
        sk = sklearn_check(Xtr, y_tr, Xho)
        if sk is not None:
            _, pva = sk
            print(f"\n  [sklearn cross-check] HOLDOUT rank-corr vs numpy = "
                  f"{_rank_corr(pva, p_ho):.3f}")
            _print_row("sklearn HOLDOUT", eval_at_tau(pva, y_ho, tau, n_total_ho), n_total_ho)
        else:
            print("\n  [sklearn cross-check] (skipped — sklearn not installed)")

        xg = xgb_oracle(Xtr, y_tr, Xho)
        if xg is not None:
            ptr_x, pva_x = xg
            print(f"\n  [XGBoost oracle] TRAIN rank-AUC={_auc(ptr_x, y_tr):.3f} "
                  f"HOLDOUT rank-AUC={_auc(pva_x, y_ho):.3f} (flexible ceiling)")
            tx, _, _ = select_threshold(ptr_x, y_tr, coverage_floor)
            _print_row("xgb HOLDOUT", eval_at_tau(pva_x, y_ho, tx, n_total_ho), n_total_ho)
        else:
            print("\n  [XGBoost oracle] (skipped — xgboost not installed)")

    print_coef_table(lr_, enc)
    return dict(label=label, tau=tau, encoder=enc, model=lr_,
                train=tr_sub, holdout=ho_sub, base_ho=base_ho,
                auc_tr=_auc(p_tr, y_tr), auc_ho=_auc(p_ho, y_ho))


# ──────────────────────── univariate indicator screen ─────────────────────
def univariate_screen(ic_rows):
    """Exploratory WR tables for each raw indicator / edge value (pooled,
    tertile bins). Multiple-comparison caveat: with many small bins some will
    look 'good' by chance; none of this is gate evidence."""
    print("\n" + "=" * 78)
    print("  UNIVARIATE SCREEN (exploratory — pooled indicator-complete rows)")
    print("=" * 78)
    n = len(ic_rows)
    print(f"  n={n} — bins are small; MULTIPLE-COMPARISON warning applies.\n")
    feats = [extract_features(s) for s in ic_rows]
    y = np.array([1 if s["result"] == "WIN" else 0 for s in ic_rows])

    def bin_table(name, vals):
        present = [(v, i) for i, v in enumerate(vals) if v is not None]
        if len(present) < 30:
            print(f"   {name:16s}: <30 values ({len(present)}) — skipped")
            return
        vs = np.array([v for v, _ in present], dtype=float)
        idxs = [i for _, i in present]
        qs = np.quantile(vs, [1 / 3, 2 / 3])
        b = np.digitize(vs, qs)
        print(f"   {name:16s} tertiles @ {qs[0]:.3f} / {qs[1]:.3f}")
        for bi, bl in enumerate(("LOW", "MID", "HIGH")):
            m = b == bi
            k = int(m.sum())
            if k == 0:
                continue
            w = int(y[np.array(idxs)[m]].sum())
            p, lo, hi = wilson(w, k)
            print(f"      {bl:4s} n={k:>4} WR={p*100:5.1f}% CI[{lo*100:4.1f}-{hi*100:4.1f}]")

    for name in ["rsi", "atrPct", "adx", "bbBandwidth", "totalMult",
                 "atrPercentile", "sessionRange", "hourMult"]:
        bin_table(name, [f[name] for f in feats])
    for name in ["bbState", "rsiChase"]:
        groups = {}
        for i, f in enumerate(feats):
            v = f.get(name)
            if v is not None:
                groups.setdefault(v, []).append(i)
        if not groups:
            print(f"   {name:16s}: no values")
            continue
        print(f"   {name:16s}")
        for lv in sorted(groups):
            ii = groups[lv]
            w = int(y[ii].sum())
            p, lo, hi = wilson(w, len(ii))
            print(f"      {lv:14s} n={len(ii):>4} WR={p*100:5.1f}% CI[{lo*100:4.1f}-{hi*100:4.1f}]")


# ───────────────────────────── JS gate emitter ────────────────────────────
def emit_gate_js(path, certified, result=None, reason="", feature_lists=None):
    """Write the worker-portable avoidance gate (R4).
    CERTIFIED -> full coefficient table; otherwise a safe pass-through stub."""
    L = []
    A = L.append
    A("// D4 v2.1 AVOIDANCE GATE — auto-generated by scripts/d4_v21_avoidance.py")
    A("// Phase F analysis artifact. Deterministic, no deps.")
    if certified:
        m = result["model"]
        enc = result["encoder"]
        tau = result["tau"]
        meta = result["meta"]
        A("// STATUS: CERTIFIED on holdout — TRADE-subset "
          f"WR={result['holdout']['wr']*100:.1f}% "
          f"CI[{result['holdout']['ci_lo']*100:.1f}-{result['holdout']['ci_hi']*100:.1f}] "
          f"cov={result['holdout']['coverage']*100:.0f}% "
          f"(holdout {meta['holdout_day']}, n={result['holdout']['n']}).")
        A("// TRAIN days " + ", ".join(meta["train_days"]) + f" (n={meta['n_train']}).")
        A("// Rule: compute P(WIN) from signal-time features; TRADE if P >= TAU else SKIP.")
        A("export const D4V21_GATE = Object.freeze({")
        A("  CERTIFIED: true,")
        A(f"  VERSION: 'd4v21-{meta['holdout_day']}',")
        A(f"  TAU: {tau:.6f},")
        A(f"  B0: {m.b:.6f},")
        A("  NUM: {")
        for n in enc.num_features:
            j = enc._col_index[n]
            A(f"    {json.dumps(n)}: {{ w: {m.w[j]:.6f}, med: {enc.num_med[n]:.6f}, std: {enc.num_std[n]:.6f} }},")
        A("  },")
        A("  CAT: {")
        for c in enc.cat_features:
            body = ", ".join(
                f'{json.dumps(lv)}: {m.w[enc._col_index[f"{c}={lv}"]]:.6f}'
                for lv in enc.cat_levels[c])
            A(f"    {json.dumps(c)}: {{ {body} }},")
        A("  },")
        A("});")
    else:
        A("// STATUS: NOT CERTIFIED.")
        for line in (reason or "insufficient data").splitlines():
            A("//   " + line)
        A("// d4v21Avoid() is a SAFE PASS-THROUGH (gates nothing) until a certified")
        A("// run regenerates this file. Do NOT hand-edit CERTIFIED to true.")
        A("export const D4V21_GATE = Object.freeze({")
        A("  CERTIFIED: false,")
        A(f"  REASON: {json.dumps((reason or 'insufficient data').splitlines()[0][:120])},")
        A("});")

    # JS-side feature extraction — EXACT parity with extract_features() above.
    A("")
    A("const _NUM = (v) => {")
    A("  if (typeof v === 'number' && isFinite(v)) return v;")
    A("  if (typeof v === 'string') { const f = parseFloat(v.replace('%','')); return isFinite(f) ? f : null; }")
    A("  return null;")
    A("};")
    A("const CRYPTO = ['BTC','ETH','SOL','DOGE','XRP','ADA','LINK','AVAX','BNB','DOT'];")
    A("function _features(s) {")
    A("  const ind = Object.assign({}, s.edge || {}, s.signalIndicators || {});")
    A("  const ts = s.timestamp || '';")
    A("  const pair = s.pair || '?';")
    A("  const rsi = _NUM(ind.rsi);")
    A("  const dir = s.direction;")
    A("  const g = s.grade;")
    A("  const sv = s.structureVerdict;")
    A("  let dow = null, hour = null;")
    A("  try { hour = parseInt(ts.slice(11, 13), 10); if (isNaN(hour)) hour = null; } catch (e) {}")
    A("  try { dow = new Date(ts.slice(0, 10) + 'T00:00:00Z').getUTCDay(); if (isNaN(dow)) dow = null; dow = (dow + 6) % 7; } catch (e) {}")
    A("  return {")
    A("    pair: pair,")
    A("    assetType: s.isOTC ? 'OTC' : (CRYPTO.some(t => pair.includes(t)) ? 'CRYPTO' : 'FOREX'),")
    A("    direction: dir,")
    A("    bestTF: s.bestTF || (typeof ind.bestTF === 'string' ? ind.bestTF : null),")
    A("    marketRegime: s.marketRegime || null,")
    A("    sessionQuality: s.sessionQuality || null,")
    A("    grade: (g && typeof g === 'object') ? g.grade : (g || null),")
    A("    alignment: s.alignment || null,")
    A("    structureVerdict: (sv && typeof sv === 'object') ? sv.overall : (sv || null),")
    A("    confidence: _NUM(s.confidence),")
    A("    coreConfidence: _NUM(s.coreConfidence),")
    A("    hour: hour, dow: dow,")
    for n in IND_NUMERIC + EDGE_NUMERIC:
        A(f"    {json.dumps(n)}: _NUM(ind[{json.dumps(n)}]),")
    A("    bbState: ind.bbState != null ? String(ind.bbState) : null,")
    A("    rsiChase: (rsi != null && (dir === 'BUY' || dir === 'SELL'))")
    A("      ? (((dir === 'BUY' && rsi > 55) || (dir === 'SELL' && rsi < 45)) ? 'CHASE' : 'OK')")
    A("      : null,")
    A("  };")
    A("}")
    A("")
    if certified:
        A("export function d4v21Avoid(signal) {")
        A("  const G = D4V21_GATE;")
        A("  const p = _features(signal);")
        A("  let z = G.B0;")
        A("  for (const n of Object.keys(G.NUM)) {")
        A("    const v = p[n] == null ? G.NUM[n].med : p[n];")
        A("    z += G.NUM[n].w * (v - G.NUM[n].med) / G.NUM[n].std;")
        A("  }")
        A("  for (const c of Object.keys(G.CAT)) {")
        A("    const lvl = p[c];")
        A("    if (lvl != null && G.CAT[c][lvl] !== undefined) z += G.CAT[c][lvl];")
        A("  }")
        A("  const pWin = 1 / (1 + Math.exp(-z));")
        A("  return { trade: pWin >= G.TAU, pWin, certified: true, gated: true };")
        A("}")
    else:
        A("export function d4v21Avoid(signal) {")
        A("  void signal;")
        A("  return { trade: true, pWin: null, certified: false, gated: false };")
        A("}")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as fh:
        fh.write("\n".join(L) + "\n")
    return path


# ───────────────────────────────── main ───────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="D4 v2.1 avoidance model — raw "
                                             "indicators + edge features")
    ap.add_argument("--data-dir", default="phase_f_forward")
    ap.add_argument("--holdout-day", default=None,
                    help="pin the holdout day (default: auto-pick = newest day "
                         "with >= --min-holdout decided indicator-complete rows)")
    ap.add_argument("--min-train", type=int, default=300,
                    help="FULL RUN requires >= this many TRAIN indicator-complete rows")
    ap.add_argument("--min-holdout", type=int, default=30)
    ap.add_argument("--coverage-floor", type=float, default=COVERAGE_FLOOR_R1)
    ap.add_argument("--gate-out", default=os.path.join("scripts", "d4v21_avoidance_gate.js"))
    ap.add_argument("--no-gate-write", action="store_true")
    ap.add_argument("--json-out", default=None, help="optional machine verdict JSON")
    args = ap.parse_args()

    rows = load_decided(args.data_dir)
    run_ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    wins = sum(1 for s in rows if s["result"] == "WIN")
    p, lo, hi = wilson(wins, len(rows))
    print("#" * 78)
    print("#  D4 v2.1 — AVOIDANCE MODEL (raw indicators + edge features)")
    print("#" * 78)
    print(f"  run: {run_ts}  data-dir: {args.data_dir}")
    print(f"  Universe: {len(rows)} decided WIN/LOSS (dedup by id)")
    print(f"  Engine pool WR = {wins}/{len(rows)} = {p*100:.1f}% "
          f"(CI {lo*100:.1f}-{hi*100:.1f}%)  | breakeven = {BREAKEVEN*100:.1f}%")

    # ── data audit ────────────────────────────────────────────────────────
    perday = {}
    ic_rows_all = []
    for s in rows:
        d = day_of(s)
        npres, complete = indicator_completeness(s)
        e = perday.setdefault(d, dict(decided=0, partial=0, ic=0))
        e["decided"] += 1
        if npres > 0:
            e["partial"] += 1
        if complete:
            e["ic"] += 1
            ic_rows_all.append(s)
    print("\n  DATA AUDIT (decided rows / indicator coverage per signal day)")
    print(f"   {'day':12s} {'decided':>8} {'any-ind':>8} {'IC(all 4)':>10}")
    for d in sorted(perday):
        e = perday[d]
        print(f"   {d:12s} {e['decided']:>8} {e['partial']:>8} {e['ic']:>10}")
    print(f"   {'TOTAL':12s} {len(rows):>8} "
          f"{sum(e['partial'] for e in perday.values()):>8} {len(ic_rows_all):>10}")
    ic_days = sorted({day_of(s) for s in ic_rows_all})

    # ── v2-features recap (all rows, auto holdout) ────────────────────────
    v2_days = sorted(perday)
    v2_ho_day = next((d for d in reversed(v2_days)
                      if perday[d]["decided"] >= args.min_holdout), None)
    if v2_ho_day:
        v2_tr = [s for s in rows if day_of(s) < v2_ho_day]
        v2_ho = [s for s in rows if day_of(s) == v2_ho_day]
        print("\n" + "#" * 78)
        print(f"#  PART 1 — v2-FEATURES RECAP (regression check; holdout auto-picked "
              f"= {v2_ho_day})")
        print("#" * 78)
        run_model(v2_tr, v2_ho,
                  "v2 baseline (NO indicators) — ceiling check",
                  V2_CAT, V2_NUM, l2=1.0, class_weight="none",
                  coverage_floor=args.coverage_floor, cross_checks=True)
    else:
        print("\n  (no day with >= %d decided rows — v2 recap skipped)" % args.min_holdout)

    # ── primary v2.1 routing ──────────────────────────────────────────────
    print("\n" + "#" * 78)
    print("#  PART 2 — PRIMARY v2.1 RUN (indicator-complete rows only)")
    print("#" * 78)

    verdict = dict(run=run_ts, mode="INSUFFICIENT_DATA", r1_pass=False,
                   ic_rows=len(ic_rows_all), holdout_day=None)
    gate_written = None

    if not ic_rows_all:
        print("\n  VERDICT: INSUFFICIENT DATA — ZERO indicator-complete rows in this snapshot.")
        print("  signalIndicators persistence (worker PR #13, live 2026-08-09 ~19:00 UTC)")
        print("  stamps only NEW rows; the current drive snapshot predates accumulation.")
        print("  Re-run when the daily snapshot lands (RULE-2): the pipeline is ready —")
        print(f"  FULL RUN triggers automatically at >= {args.min_train} TRAIN rows and")
        print(f"  >= {args.min_holdout} holdout rows.")
    else:
        if args.holdout_day:
            ho_day = args.holdout_day
            print(f"\n  holdout day PINNED: {ho_day}")
        else:
            cands = sorted({d for d in ic_days
                            if sum(1 for s in ic_rows_all if day_of(s) == d) >= args.min_holdout})
            ho_day = cands[-1] if cands else ic_days[-1]
            note = "" if cands else (f"  (no day reaches --min-holdout "
                                     f"{args.min_holdout}; using newest IC day)")
            print(f"\n  holdout day auto-picked: {ho_day}   {note}")
        tr = [s for s in ic_rows_all if day_of(s) < ho_day]
        ho = [s for s in ic_rows_all if day_of(s) == ho_day]
        verdict["holdout_day"] = ho_day
        verdict["n_train"] = len(tr)
        verdict["n_holdout"] = len(ho)
        print(f"  TRAIN (IC rows < {ho_day}): n={len(tr)}   "
              f"HOLDOUT (IC rows = {ho_day}): n={len(ho)}")

        if len(tr) >= args.min_train and len(ho) >= args.min_holdout:
            verdict["mode"] = "FULL_RUN"
            res = run_model(tr, ho,
                            f"FULL RUN — v2.1 features (holdout={ho_day})",
                            V21_CAT_FULL, V21_NUM_FULL, l2=1.0,
                            class_weight="balanced",
                            coverage_floor=args.coverage_floor,
                            cross_checks=True)
            m = res["holdout"]
            r1 = (m["wr"] >= BREAKEVEN and m["ci_lo"] >= 0.50
                  and m["coverage"] >= args.coverage_floor and m["n"] >= 10)
            verdict["r1_pass"] = bool(r1)
            verdict["holdout_metrics"] = m
            print("\n" + "-" * 78)
            if r1:
                print("  R1 RESULT: PASS on this holdout — BUT 2+ holdout windows are still")
                print("  required before any gate goes live (workflow rule). Emitting CERTIFIED")
                print("  gate artifact for PR review; deploy still gated on a second window.")
                res["meta"] = dict(holdout_day=ho_day,
                                   train_days=sorted({day_of(s) for s in tr}),
                                   n_train=len(tr))
                if not args.no_gate_write:
                    gate_written = emit_gate_js(args.gate_out, certified=True, result=res)
            else:
                print(f"  R1 RESULT: FAIL — TRADE-subset on holdout "
                      f"WR={m['wr']*100:.1f}% CI-low={m['ci_lo']*100:.1f}% "
                      f"cov={m['coverage']*100:.0f}% (need WR≥55.6, CI-low≥50, cov≥15%).")
                print("  No gate. Emitting safe stub.")
                if not args.no_gate_write:
                    gate_written = emit_gate_js(
                        args.gate_out, certified=False,
                        reason=f"R1 fail on holdout {ho_day}: WR={m['wr']*100:.1f}% "
                               f"CI-low={m['ci_lo']*100:.1f}% cov={m['coverage']*100:.0f}%")

        elif len(tr) >= 30 and len(ho) >= 20:
            verdict["mode"] = "EXPLORATORY"
            print(f"\n  >>> EXPLORATORY MODE (train {len(tr)} < {args.min_train}).")
            print("  >>> Numbers below are NOT gate evidence; pool is far too small.")
            res = run_model(tr, ho,
                            f"EXPLORATORY ONLY — small-sample v2.1 (holdout={ho_day})",
                            V21_CAT_SMALL, V21_NUM_SMALL, l2=5.0,
                            class_weight="balanced",
                            coverage_floor=args.coverage_floor,
                            cross_checks=False)
            m = res["holdout"]
            verdict["holdout_metrics"] = m
            print("\n  >>> EXPLORATORY verdict: small-sample run, NOT deployable. Need")
            print(f"  >>> train >= {args.min_train} IC rows (have {len(tr)}). Keep accumulating.")
            if not args.no_gate_write:
                gate_written = emit_gate_js(
                    args.gate_out, certified=False,
                    reason=f"exploratory only — train={len(tr)} IC rows (<{args.min_train}); "
                           f"holdout {ho_day} n={len(ho)}")
        else:
            verdict["mode"] = "INSUFFICIENT_DATA"
            print(f"\n  VERDICT: INSUFFICIENT DATA — train={len(tr)} (need "
                  f">={args.min_train} full / >=30 exploratory), holdout={len(ho)} "
                  f"(need >=20-30).")
            print("  Indicators are accumulating (~50-80 rows/day per the drive log).")
            print(f"  This script auto-upgrades: re-run when train >= {args.min_train}.")
            if not args.no_gate_write:
                gate_written = emit_gate_js(
                    args.gate_out, certified=False,
                    reason=f"insufficient data — {len(ic_rows_all)} indicator-complete rows "
                           f"(train={len(tr)}, holdout={len(ho)}); need train>={args.min_train}")

        if len(ic_rows_all) >= 40:
            univariate_screen(ic_rows_all)

    # stub gate even with zero rows (R4: a deterministic artifact exists from day 0)
    if not args.no_gate_write and gate_written is None:
        gate_written = emit_gate_js(
            args.gate_out, certified=False,
            reason=f"insufficient data — 0 indicator-complete rows in snapshot "
                   f"(run {run_ts}); pipeline armed, awaiting accumulation")
    if gate_written:
        print(f"\n  >> gate artifact written: {gate_written} "
              f"({'CERTIFIED' if verdict.get('r1_pass') else 'stub — CERTIFIED: false'})")

    # ── final verdict block ───────────────────────────────────────────────
    print("\n" + "#" * 78)
    print("#  FINAL VERDICT (requirements R1-R5)")
    print("#" * 78)
    mode = verdict["mode"]
    if mode == "INSUFFICIENT_DATA":
        print(f"  R1 holdout edge ...... N/A — INSUFFICIENT DATA "
              f"({len(ic_rows_all)} IC rows; need train>={args.min_train}, "
              f"holdout>={args.min_holdout})")
        print("  Best honest answer today: v2.1 edge untestable on this snapshot.")
        print("  (v2 recap above tracks the feature ceiling on the full pool.)")
    elif mode == "EXPLORATORY":
        m = verdict["holdout_metrics"]
        print(f"  R1 holdout edge ...... NOT TESTED properly — exploratory n too small "
              f"(holdout TRADE n={m['n']} WR={m['wr']*100:.1f}%)")
        print("  >>> reported numbers carry no decision weight; keep accumulating.")
    else:
        m = verdict["holdout_metrics"]
        ok = verdict["r1_pass"]
        print(f"  R1 holdout edge ...... {'PASS' if ok else 'FAIL'} — TRADE-subset "
              f"WR={m['wr']*100:.1f}% CI[{m['ci_lo']*100:.1f}-{m['ci_hi']*100:.1f}] "
              f"cov={m['coverage']*100:.0f}% n={m['n']}")
    print("  R2 no leakage ........ OK — features signal-time only; vocab/medians/tau "
          "\n                        "
          "fit on TRAIN; holdout day auto-picked strictly after TRAIN days")
    print(f"  R3 sanity ............ coverage floor {args.coverage_floor*100:.0f}% "
          "enforced at selection time; sweep + per-day + honesty audit printed")
    print(f"  R4 worker-portable ... {args.gate_out} "
          f"({'CERTIFIED' if verdict.get('r1_pass') else 'stub: CERTIFIED false, pass-through'})")
    print(f"  R5 rerunnable ........ yes — holdout auto-pick ({verdict.get('holdout_day')}), "
          "no hardcoded dates")
    print("\n  Honesty: an untested edge is not an edge. Honest gap > fake edge, always.")

    if args.json_out:
        with open(args.json_out, "w") as fh:
            json.dump(verdict, fh, indent=2, default=str)
        print(f"\n  machine verdict: {args.json_out}")

    return verdict


if __name__ == "__main__":
    main()
