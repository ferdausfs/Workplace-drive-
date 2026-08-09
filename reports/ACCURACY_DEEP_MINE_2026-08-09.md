# 🔍 FTT SIGNAL ACCURACY — DEEP DATA MINING + ACTION PLAN (2026-08-09)
**Independent — Arena main agent · data: Workplace-drive- (Phase F 08-01..09, 5097 decided rows)**

---

## 1. WHY ACCURACY HASN'T IMPROVED (the honest answer)
Ekhon porjonto amra **bug fix korechi (correctness), accuracy na**. Worker rounds 1-3 fixed mechanical bugs (push, timezone, OTC resolve, dedup, ties). Those stop losses — but **nothing made signals actually win more**. The system is now CORRECT but still LOSING (overall WR 42.5% vs 55.6% breakeven).

## 2. THE BIG DISCOVERY — engine's own "quality" signals are INVERTED

| Slice | WR | Engine says |
|---|---|---|
| Grade **A+** | **37.8%** | "EXCELLENT" — actually WORST |
| Grade C | 46.9% | "MODERATE" — actually BEST |
| Conf **80-84%** | **37.4%** | high confidence — actually WORST bucket |
| Conf 72-74% | 43.0% | low confidence — better |
| **FOREX** | **30.4%** | (vs crypto 44.6%) |
| Session **HIGHEST** | **11.9%** | worst |
| AUD/USD | 24.2% · USD/JPY 29.3% · GBP/USD 31.7% · EUR/USD 33.5% | all bad |

## 3. ROOT CAUSE — grade/confidence scoring is miscalibrated
`grade.js`: `sc = confidence*0.4 + avgConf*5 + alignment*25`
- **alignment +25** = "all TFs same direction" — a TREND AGREEMENT bonus, NOT a quality measure
- **avgConf*5** — confluence count × 5, capped 35 — again "many categories agree", not "high probability"
- **A+ (sc≥85)** is mostly reached by **confidence*0.4 (35) + alignment (25) + avgConf (25)** = high-confidence + all-TFs-same-direction — which is exactly the "trending/parked" regime that's LOSING
- **Evidence:** A+ WR 37.8% vs C WR 46.9% — the grade ladder is INVERTED

**The engine's confidence ≈ "how many signals agree", not "how likely to win".**

## 4. HOLDOUT TEST — can a simple filter rule beat it? (HONEST result)
```
Rules (learned from train 08-01..06): skip AUD/USD, USD/JPY, EUR/USD, GBP/USD, HIGHEST session, conf 80-84
TRAIN: 41.8% → 44.9% (+3.1)
VAL (08-07..09, rules unseen): 48.0% → 49.6% (+1.6)   ← modest, NOT breakeven
```
**Verdict: simple slice filters alone get +1.6 pts — NOT enough (49.6% vs 55.6% breakeven).** The easy wins are already partially blocked (D2 blocks); the remaining edge needs deeper work.

## 5. ACTION PLAN (what we'll do — PR-first, Phase F rules)

### A. Confidence/grade CALIBRATION FIX (worker — highest leverage)
**Bug:** grade is a "consensus" score, not a probability. Fix direction (needs PR + evidence):
- Re-derive grade thresholds from ACTUAL WR per confidence bucket (data shows 80-84% conf is the worst — so high conf must NOT mean high grade)
- OR recalibrate: grade = f(historical WR of the slice), not f(confidence×0.4 + avgConf×5 + alignment)
- **Proof required:** after fix, grade A+ WR > grade C WR (currently inverted). Holdout-tested.

### B. AVOIDANCE model (D4 v2 — replace "predict winner" with "predict loser")
Current D4 predicts WIN (hard, ~50%). New approach: predict **LOSER slices** (which signal is likely to fail) — same as the filter rules but learned + with **raw indicator features** (RSI value, ATR%, ADX, BB bandwidth, session, hour — all available at signal time).
- Add raw features to D4: engine currently trains on grade/regime/pair only.

### C. Slice GATES (Phase F evidence-based)
Keep collecting; the moment a slice shows WR < 40% with n≥50 AND it holds across 2 holdout windows → block it via config (PR-first, evidence in PR).

### D. What we will NOT do
- No blanket inversion (SELL→BUY flip) — evidence doesn't support direction flips, and Phase F rules forbid.
- No real-money recs until gate (55.6% CI, 7-14 days).

## 6. NEXT ACTIONS (concrete)
1. **Worker PR: grade calibration** (A) — with holdout proof that A+ stops being the worst grade.
2. **D4 v2 script** (B) — raw features + avoidance framing; run on drive data.
3. **Daily holdout check** — every day: train rules on window-1, validate on window-2 (no overfit claims without this).
4. Push everything to Workplace-drive- (RULE-2).

## FILES
- This report → drive `reports/ACCURACY_DEEP_MINE_2026-08-09.md`
- `slice_mine.py`, `refine_rules.py`, `filter_test.py` → drive `scripts/`
