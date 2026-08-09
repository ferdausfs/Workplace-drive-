# ✅ signalIndicators INSTRUMENTATION — MERGED + LIVE (2026-08-09)

**Worker main:** `d696c6b` (Merge PR #13) · **Bundle:** `worker-ind-v1-20260809.js` (282,781 B, MD5 `025d3021...`) · Live

---

## LIVE PROOF (history rows saved AFTER deploy)

```
ETH/USD 19:22 SELL → signalIndicators: {bestTF:"15min", rsi:44.79, atrPct:0.086, adx:22.32, bbBandwidth:0.357}
ADA/USD 19:25 SELL → signalIndicators: {bestTF:"1min",  rsi:39.06, atrPct:0.064, adx:19.21, bbBandwidth:0.438}
DOT/USD 19:26 SELL → signalIndicators: {bestTF:"5min",  rsi:37.07, atrPct:0.143, adx:35.83, bbBandwidth:0.329}
DOT/USD 19:40 SELL → signalIndicators: {bestTF:"15min", rsi:43.54, atrPct:0.26,  adx:18.03, bbBandwidth:1.13}
```

- ✅ `signalIndicators` present on post-deploy rows — **RSI / ATR% / ADX / BB-bandwidth at signal time**
- ✅ Values numeric + sane (RSI 37-45, ATR% 0.06-0.26, ADX 18-36, BB 0.33-1.13)
- ✅ Both TF shapes handled (raw + formatted — the PR #13 win over PR #12)
- ✅ Calibration + all prior fixes intact (worker healthy, calib field on tradeable)

## DEPLOY (correct this time)
- Filename in `redeploy.sh` updated to `worker-ind-v1-20260809.js`, verified via `grep`, deployed → success
- (Lesson repeated: verify the deploy-script filename matches the NEW bundle)

## WHAT THIS UNLOCKS (D4 v2.1)
- ~2-3 days of history rows will carry raw indicators
- Then D4 v2.1 reruns WITH RSI/ATR%/ADX/BB features → does the avoidance edge finally clear CI-low 50% (≥55.6% bar)?
- If yes → gate deploy candidate (needs 2+ holdout windows still)
- If no → indicators aren't the edge either; reassess

## STATUS
| Item | Status |
|---|---|
| PR #11 (D4 v2 analysis) | merged `229acdb` (analysis-only) |
| PR #13 (instrumentation) | merged `d696c6b`, **LIVE** |
| PR #12 (duplicate) | closed (not merged) |
| Calibration (PR #10) | still live |
| D4 v2 gate | NOT deployed (correct — holdout CI-low < 50%) |

## NEXT
1. Daily Phase F continues — new rows accumulate indicators.
2. In ~2-3 days: rerun D4 v2.1 with raw indicators (I'll write the analysis prompt / run it).
3. Push this report to drive (RULE-2): `reports/INDICATORS_LIVE_2026-08-09.md`.
