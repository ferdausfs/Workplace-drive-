# ✅ signalIndicators INSTRUMENTATION — MERGED + LIVE (2026-08-09)

**Worker main:** `d696c6b` (Merge PR #13) · **Bundle:** `worker-ind-v1-20260809.js` (282,781 B, MD5 `025d3021...`) · Live

## LIVE PROOF (history rows saved AFTER deploy)
- ETH/USD 19:22 SELL → {bestTF:15min, rsi:44.79, atrPct:0.086, adx:22.32, bbBandwidth:0.357}
- ADA/USD 19:25 SELL → {bestTF:1min, rsi:39.06, atrPct:0.064, adx:19.21, bbBandwidth:0.438}
- DOT/USD 19:26 SELL → {bestTF:5min, rsi:37.07, atrPct:0.143, adx:35.83, bbBandwidth:0.329}
- DOT/USD 19:40 SELL → {bestTF:15min, rsi:43.54, atrPct:0.26, adx:18.03, bbBandwidth:1.13}

- ✅ signalIndicators on post-deploy rows (RSI/ATR%/ADX/BB at signal time)
- ✅ Values numeric + sane
- ✅ Both TF shapes handled (raw + formatted — PR #13 over PR #12)
- ✅ Calibration + prior fixes intact

## DEPLOY
- redeploy.sh filename updated to worker-ind-v1-20260809.js, verified via grep, success

## WHAT THIS UNLOCKS (D4 v2.1)
- ~2-3 days of history rows carry raw indicators
- Then D4 v2.1 reruns WITH RSI/ATR%/ADX/BB → does avoidance edge clear CI-low 50% (≥55.6%)?
- Gate deploy candidate only after 2+ holdout windows

## STATUS
- PR #11 (D4 v2 analysis): merged 229acdb (analysis-only)
- PR #13 (instrumentation): merged d696c6b, LIVE
- PR #12 (duplicate): closed
- Calibration (PR #10): live
- D4 v2 gate: NOT deployed (correct)
