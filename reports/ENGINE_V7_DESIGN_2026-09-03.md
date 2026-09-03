# ENGINE V7 — Next-Generation Signal Engine (Design + Build Record)

**Date:** 2026-09-03 · **Status:** BUILT, committed on `feat/v7-shadow` (push pending fresh PAT)
**Trigger:** User directive — "engine take ekdom new kore banate chai … 10 signals/day, 6-8 win"

---

## 1. Why a new engine (the measured case)

The v6 vote-paradigm is forward-dead. Evidence, all measured (4-day EC shadow
window, 655 records / 630 decided, + the 2026-08-30 audits):

| Fact | Number |
|---|---|
| Pooled crypto WR (current stream) | **37.3%** (n=630) vs breakeven 55.6% @ 80% payout |
| EC score vs win correlation | **−0.063** (score anti-ranks wins) |
| Best slice (RANGING non-CHASE) | 52.3% (n=44) |
| TRENDING regime | 35.4% (n=325); counter-trend BUY **20.5%** |
| RSI CHASE (73% of stream) | 37.8% |
| Independent edge-decay confirmations | 4 |

Vote counting cannot be repaired by re-weighting: the EC ladder went
non-monotone at scale and the flip was cancelled (EC_SHADOW_WINDOW_FINAL_2026-09-03.md).
**Conclusion: replace the decision paradigm, not its weights.**

## 2. Target translation (user's ask → engineering contract)

User: "10 signals, 8 win; or 6/7 — profit." Honest contract:

- Breakeven at 80% payout = 55.6%. **6/10 = 60% → profitable. 7/10 = 70% → strong.**
- 8/10 sustained (80%) is NOT promised by anyone honest — no measured slice in
  any of our pools reaches it. We engineer for 60-70% and MEASURE forward.
- Volume ≤ ~10-12/day is accepted by the user (accuracy over volume).

## 3. V7 paradigm: exclusion + trigger, not votes

```
tick → [independent indicators] → REGIME ROUTER → hard REQUIREMENTS →
       VETO STACK → H1 ENTRY TRIGGER → would-mint (counterfactual shadow)
```

1. **Regime router** — RANGING mean-reversion only in v0.1. TRENDING/VOLATILE
   = sit out (proven poison). "Any-market" robustness comes from NOT trading
   bad markets, not from winning in all of them.
2. **Extremes + non-chase (H2)** — BUY only at %B ≤ 0.15 with RSI ≤ 40
   (buy the dip, never chase); SELL mirror. Chase is measured poison (37.8%).
3. **H1 entry trigger** — a CLOSED rejection candle in trade direction
   (bullish close in top half of its range at the low extreme). The v6 engine
   has NO entry timing at all — this is the missing ingredient the whole
   60%-gap thesis rests on, and the shadow exists to test it.
4. **Veto stack** — dead squeeze (BW < 0.20), ATR explosion (pctile > 85),
   measured bad UTC hours {01,02,03,11,14,19} (all ≤29.5% WR, n≥16).
5. **Daily budget** — decision-mode only (not in shadow v0.1): rank candidates
   by evidence, cap ~10 pushes/day.

## 4. Ship discipline (RULE 6 — non-negotiable)

- V7 runs as a **pure counterfactual shadow**: every crypto tick evaluated
  (incl. NO_TRADE ticks — that's why the evaluator computes its OWN indicators;
  edgeFeatures is null on NO_TRADE and would bias the sample).
- Would-mints → KV `v7obs:` → forward resolution via the production price path
  (`fetchExpiryPrice`, 5-min expiry). Dedup 30 min/pair, cap 40/pair/30d.
- **Flip gate:** shadow WR must clear 55.6% (Wilson CI lower bound > 50%,
  n ≥ 100) before `decision` mode is even discussed. Same gate the EC ladder
  just failed — that gate SAVED the subscribers from a 32.5% B-band.
- Zero production-output effect in shadow (asserted by the same byte-equality
  philosophy as EC-V2: the evaluator is additive, fail-open, try/catch-wrapped).

## 5. Build record (2026-09-03)

| File | Role |
|---|---|
| `src/signal/v7shadow.js` | pure evaluator + fail-open admission hook |
| `src/history/v7store.js` | counterfactual store (admit/list/resolve/summarize) |
| `src/config.js` | `V7_SHADOW` block (every threshold evidence-tagged) |
| `src/handlers/signal.js` | `ctx.waitUntil(maybeAdmitV7Observation(...))` |
| `src/index.js` | cron resolver wiring (`*/2` / `*/5` tick) |
| `scripts/v7_tests.mjs` | 13 tests: rule matrix + store admit/dedup/cap/resolve |

Tests: **v7 13/13 · EC-V2 43/43 · fix 328/328 (version pin updated) · rsi-gate 18/18**
Bundle: esbuild OK (347.8 KB). Version bumped **6.13.0 → 6.14.0**.

## 6. What ships together in v6.14.0 (deploy checklist, needs tokens)

1. This branch (`feat/v7-shadow`) — v7 shadow instrumentation.
2. Safety patch (2 config flips, user-facing): `D2_TRENDING_BLOCK_ENABLED: true`
   + `SELECTIVITY_GATE.excludeTrending: true` — kills the measured-poison
   TRENDING slice while v7 shadow accumulates (simulated effect: stream
   ~163/day @ 37.3% → ~79/day @ 39.3%; CHASE push-filter comes later as its
   own change so the v7 trigger signal stays clean).
3. Push pending reports to Workplace-drive.

**Needs from user (deploy time only):** fresh GitHub PAT (fine-grained, both
repos, contents+PR) + Cloudflare Workers token + Account ID. Revoke right
after deploy — standing rule.

## 7. Success metrics (shadow window, 5-7 days)

- Primary: v7 shadow WR ≥ 60% (n≥100, CI lower > 50%) → decision-mode design.
- Secondary: trigger slice analysis (closePos ≥ 0.7 vs <), RSI-depth slices,
  per-side balance, admission rate (target 5-15 obs/day overall).
- If H1/H2 fail: iterate thresholds (v0.2) or add pullback-entry strategy;
  the store records the features needed for every slice.
