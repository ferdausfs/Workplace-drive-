# ✅ CALIBRATION — MERGED + DEPLOYED + LIVE (2026-08-09)

**Worker main:** `9b3bc08` (Merge PR #10) · **Bundle:** `worker-calib-v1-20260809.js` (280,351 B, MD5 `b813f094...`) · Live

---

## LIVE PROOF

**DOGE/USD → BUY**
```
confidence (calibrated): 77%        (was raw vote-share 96% pre-fix)
coreConfidence (raw):    96
grade: C — MODERATE "calibrated. (Structure conflict — capped from B to C)"
calibration: { rawConfidence: 96, calibratedConfidence: 77, calibratedScore: 0.415, version: "calib-v1-2026-08-09" }
structureVerdict: ALIGNED
```

**What this demonstrates:**
1. ✅ **Calibration field live** — raw vs calibrated confidence traceable.
2. ✅ **Inverted cap working** — structure ALIGNED (worst WR 39.3% per train) → capped to C. Pre-fix this signal would be A+/A (trend-consensus bonus).
3. ✅ **Confidence recalibrated** — 96% vote-share → 77% calibrated (empirical WR of its bucket).
4. ✅ NO_TRADE → 0% / N/A still works.

## DEPLOY JOURNEY (the lesson, again)
- First redeploy uploaded the OLD bundle — `redeploy.sh` still pointed at `worker-fixeh-20260807.js` (sed from a previous round). Live showed NO calibration field.
- Fix: `sed` the script filename → `worker-calib-v1-20260809.js`, verify `grep`, redeploy → **calibration live**.
- **Rule:** always verify the bundle filename in the deploy script matches the NEW bundle before deploying (unique-name convention).

## VERIFY SUMMARY (all green)
- Merge: `9b3bc08` == PR#10 head `c556cf5` ✓
- r71 117P/0F, fix_tests 160/160, all suites ✓ (verified pre-merge)
- R1/R2 holdout: grade A+ 54.8% > A 51.3% > B 44.9% > C 42.9% · conf monotonic ✓
- Live: calibration field + inverted cap + calibrated conf ✓

## STILL OPEN (the actual profit work)
1. **Avoidance model (D4 v2)** — predict LOSERS with raw indicator features.
2. **Slice gates** — holdout-proven low-WR slices (FOREX 30%, HIGHEST 11.9%, AUD/USD 24%) as config blocks.
3. **Weekly calibration refresh** — recompute CALIB on rolling window.
4. Phase F daily continues; breakeven gate (55.6%) not yet met.

## RULE-2: push this report to Workplace-drive- (`reports/CALIBRATION_LIVE_2026-08-09.md`)
