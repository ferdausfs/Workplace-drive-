# Sig-v1.0.0 LIVE — STRATEGY-PLAYBOOK ENGINE (2026-09-03)

## Status: LIVE (deployed ~07:5x UTC, /health confirmed "Sig-v1.0.0")

- PR: [#33 feat/sigv1-engine → main](https://github.com/ferdausfs/Ftt-Otc-v6/pull/33) — merged (da42199)
- Bundle: esbuild, 364,568 bytes; deploy via CF direct-API (`--fix-metadata`)
- Push health: tokenValid=True (fttbotbot), 1 subscriber

## Why (user directive, 2026-09-03)

"Engine সাজাবে strategy অনুযায়ী — vote হবে না। এক strategy SELL বললে বাকিরা
BUY বলুক আর না বলুক — ইঞ্জিন মার্কেট-কন্ডিশন বুঝে ঠিক strategy-র কথাই বলবে।"
+ "সব পেয়ার খোলা" + "নতুন version: Sig-v1.0.0, পুরনো 6.14.x বাদ"।

Context at deploy time: today's live WR 41.7% (10W/14L, all-BUY mints,
TRENDING counter-trend BUYs again losing) — the vote paradigm's 4th
confirmation. Sig-v1.0.0 replaces the decision path.

## Architecture (no votes)

```
tick (all pairs, every scan/API call)
  └─ ROUTER reads: swing structure (HH/HL vs LH/LL), EMA20/50, ADX,
     BB-width percentile + coil-broke check, ATR percentile, hour
        ├─ DEAD                  → silence
        ├─ coil-broke            → S3 BREAKOUT-RETEST (before ATR veto: the
        │                          first expansion candle IS an ATR spike)
        ├─ EXPANSION_SHOCK       → silence (S1/S2 protected)
        ├─ TRENDING_UP/DOWN      → S2 TREND-PULLBACK (with-trend only,
        │                          38–61% retrace into EMA/swing zone,
        │                          rejection candle, RSI chase-veto 55/45)
        ├─ SQUEEZE (narrow now)  → S3 BREAKOUT-RETEST
        ├─ RANGING               → S1 RANGE-FADE (v0.1 measured core:
        │                          %B extremes + non-chase RSI + rejection)
        └─ UNCERTAIN (<0.6 conf) → silence
```

- Router picks ONE strategy; only that strategy's output is pushed.
- Indicators never vote — they only appear inside a strategy's own conditions.
- Kill-switch: `SIG_V1.enabled=false` → legacy v6 selectivity-gate pushes
  (proven by fix_tests T4/T27 under the kill-switch).

## Pairs — ALL OPEN (user directive)

- SCAN_PAIRS: 10 crypto + 4 forex (market-hours gated) + **4 OTC** (EURUSDOTC,
  GBPUSDOTC, USDJPYOTC, AUDUSDOTC — 24/7) = 18 pairs
- SIG_V1.MARKETS: CRYPTO/FOREX/FOREX_OTC all true

## Push behavior change (expected!)

- Volume drops hard: only playbook setups are pushed (~5–15/day expected).
- Message format: `Sig-v1 S1_RANGEFADE | state=RANGING | rsi=38 | pair` —
  strategy + state visible in every push.
- History volume unchanged (all signals still recorded) — research intact.
- delivered24h will fall from ~78 to the playbook's emit count.

## Measurement (RULE-6 continues)

- Every playbook emit → `v7obs:` store, strategy-tagged (SIGV1_S1/S2/S3),
  forward-resolved with production fetchExpiryPrice (5-min binary).
- Voice gates: per strategy × market WR ≥ 55.6% (breakeven), n ≥ 50.
- Engine flip gate (unchanged): WR ≥ 60%, n ≥ 100, Wilson CI-lo > 50%.
- v0.1 (S1-only, crypto) baseline from earlier today keeps collecting —
  dedup naturally prevents double-counting.

## Tests (431 green)

- **sigv1 14/14** (new): router state classification, S1 dip+rejection BUY,
  S2 pullback+resume BUY + no-pullback silence, S3 break+dip+hold BUY +
  no-retest silence, veto-hour, ATR explosion, market gating (forex off,
  OTC on), determinism, insufficient-candles, kill-switch.
- fix 328/328 (T4/T27 legacy-push contracts proven under SIG_V1 kill-switch;
  T43j version line updated), rsi_gate 18/18, ec_v2 43/43, v7 13/13,
  selectivity_chase 15/15.

## Honest expectation

Today's target: 10/day with 6–8 wins. The playbook emits rarely and only in
its measured/hypothesized cells; sustained 60–70% is the realistic battle.
First Sig-v1 WR read: allow 3–5 days of emissions, then slice by strategy ×
market. If S2 fixes the trend-fighting wound, pooled WR should clear the
old 37.3% decisively.
