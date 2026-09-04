# ENGINE V7 v0.2 — STRATEGY PLAYBOOK + REGIME ROUTER (2026-09-03)

**Owner directive (translated):** engine will NOT average indicator votes.
Many strategies exist; the ENGINE decides which strategy applies to which
market condition. One strategy may say SELL while every indicator says BUY —
if that strategy is the right one for the current market state, the engine
outputs SELL. No voting. The engine must "understand market condition".

This is the **playbook architecture**: a market-state ROUTER picks ONE
strategy from a playbook; the picked strategy alone decides direction
(or says NO_TRADE). Indicators are strategy INPUTS, never voters.

---

## 1. Why voting is dead (measured, 4-day pool 630 decided)

| Evidence | Number | Meaning |
|---|---|---|
| Pooled push WR | 37.3% | the vote average loses |
| score↔win correlation | **-0.063** | higher vote ≈ no (slightly negative) edge |
| TRENDING+BUY (voted counter-trend) | **20.5%** (n=39) | votes said BUY in an uptrend move — the exact user scenario, and the vote was wrong |
| non-CHASE slice | 52.3% (n=44) | conditions, not votes, carry the edge |

The user's hypothetical already happened in the data: in TRENDING regimes the
confluence vote averaged away any directional truth and produced 20.5% WR
counter-trend BUYs. A trend-pullback strategy would have said "wait for the
pullback, then enter WITH the trend" — or nothing.

---

## 2. How the engine understands market condition (the ROUTER)

The router is a classifier over closed candles — no votes, just measurements:

**Features (all computable from existing candle pipeline):**
- Trend structure: swing HH/HL vs LH/LL sequences on 5m + 15m (+1h confirm)
- ADX (already computed) for trend STRENGTH
- BB bandwidth percentile (VOL_STATE, exists) for squeeze vs normal vs expansion
- ATR percentile (exists) for volatility shock
- Session/hour context (measured bad-hours veto stays)

**States (v0.2 router output):**
| State | Defining measurements | Map to |
|---|---|---|
| RANGING | ADX < ~22, BB width narrow-flat, structure flat | S1 RANGE-FADE |
| TRENDING_UP | HH/HL on both TFs + ADX ≥ threshold | S2 TREND-PULLBACK |
| TRENDING_DOWN | LH/LL + ADX ≥ threshold | S2 TREND-PULLBACK (sell side) |
| SQUEEZE_COILING | BB width ≤ deadSqueeze zone BUT rising slope | S3 BREAKOUT-RETEST watch |
| EXPANSION_SHOCK | ATR pctile ≥ 85 or width spike | NO-TRADE (veto) |
| DEAD | width ≤ deadSqueezeBlock, flat | NO-TRADE |

**Router validation (mandatory, RULE-6 style):** every router label is stored
with what price did next (continued/reversed). We measure router precision —
e.g. "labeled TRENDING_UP: how often did the next N candles make HH" — before
any decision-mode use. A router that mislabels is worse than no router.

**Uncertainty rule:** if the router's confidence is low or two states blur,
output NO_TRADE. An ambiguous market is not a place to trade — it is a place
to be silent.

---

## 3. The PLAYBOOK (strategies, each with its own entry contract)

Shared veto stack (applies before any strategy runs): dead market, ATR
explosion shock, measured bad hours {01,02,03,11,14,19} UTC, news blackout,
OTC/forex excluded in v0.2 (crypto-only, same as v0.1).

### S1 — RANGE-FADE (state: RANGING)
- = current V7 v0.1 logic, unchanged and already collecting shadow data
- BUY at range bottom: %B ≤ 0.15 + RSI ≤ 40 + rejection candle (close in top
  half of its range); SELL mirrored at top
- Exits the position conceptually at range mid → short 5-min binary expiry
- Baseline to beat: measured non-CHASE 52.3%

### S2 — TREND-PULLBACK (state: TRENDING_UP / TRENDING_DOWN)  ← the big new one
- Purpose: monetize trends instead of fighting them (the 20.5% wound)
- Direction: WITH trend only (router state gives direction; strategy cannot
  flip it)
- Entry: pullback to EMA20/EMA50 zone OR 38–61% retracement of the last swing,
  THEN a rejection/resumption candle in trend direction
- Hard vetoes: RSI chase (BUY rsi>55 = paying premium at extension), entry
  distance to MA zone too far (chasing), trend exhaustion signs (climax bar)
- This strategy MUST show WR > breakeven in its own cells before any voice

### S3 — BREAKOUT-RETEST (state: SQUEEZE_COILING → confirmed break)
- Trigger: BB width percentile crosses up from squeeze zone + candle CLOSE
  outside the range + RETEST holds the broken edge
- Only after retest — direct break entries are chasing (measured 37.2%)
- Conservative sizing of expectations: OTC-style feeds fake-break often; the
  retest requirement is the defense

### S4 — REVERSAL-EXHAUSTION (PARKED, no code in v0.2)
- Trending + RSI divergence + climax volume bar
- Only gets implemented if forward data shows S2 leaves exhaustion windows
  unmonetized AND divergence cells measure > breakeven. High-risk by nature.

**No averaging rule (the user's scenario, codified):** when the router says
TRENDING_UP, S2's output IS the signal (BUY after pullback, or NO_TRADE if no
pullback setup). RSI, Stoch, other indicators never get a counter-vote; they
only appear inside S2's own entry conditions (e.g. rsi>55 veto). If another
strategy disagrees — e.g. S1 range logic says "top of range, SELL" — it is
simply not the assigned strategy for that state, so it is silent.

---

## 4. Measurement & selection (how a strategy EARNS its voice)

- All shadow observations go to the same `v7obs:` store, each record tagged
  `strategy: S1|S2|S3` + `state:` + `routerConfidence:` (v0.1 records are
  implicitly S1 — backward compatible)
- Weekly slice report: per strategy × per state WR with Wilson CI
- **Voice gate:** a strategy may affect live decisions only in states where it
  has WR ≥ 55.6% (breakeven), n ≥ 50, CI-lo > 45 — and the FULL flip to
  decision mode needs the v0.1 gate: WR ≥ 60%, n ≥ 100, CI-lo > 50%
- Strategies failing their cells get demoted (state removed from their map)
  or rewritten — measured, not debated

## 5. Migration path

1. **Now:** v0.1 (S1) shadow collecting — untouched, 5–7 days baseline
2. **v0.2 deploy:** router + S2 + S3 as additional tagged shadow writers
   (zero live effect, same admission path, same store)
3. **+7 days:** comparative slice report → demote/keep strategies + fix router
   precision numbers
4. **Then:** flip-gate review for decision mode (only router-assigned strategy
   speaks; volume scales only after WR holds)

## 6. Config sketch (evidence-tagged, one-line rollbacks)

```js
V7_SHADOW: { enabled: true, ...existing v0.1 keys...,
  STRATEGIES: {
    rangeFade:      { enabled: true },                    // v0.1 logic
    trendPullback:  { enabled: true, EMA: [20, 50], RETRACE_MIN: 0.38, RETRACE_MAX: 0.61,
                      ADX_MIN: 22, CHASE_RSI_BUY: 55, CHASE_RSI_SELL: 45 },  // H: fixes TRENDING 20.5%
    breakoutRetest: { enabled: true, WIDTH_PCTILE_EXIT: 60, RETEST_TOL: 0.1 }, // H: squeeze→expansion
  },
  ROUTER: { ADX_TREND: 22, CONF_MIN: 0.6 }               // below CONF_MIN -> NO_TRADE
}
```

## 7. Explicit non-goals

- No ML model, no AI re-ranking (both measured dead in this pipeline)
- No forex/OTC in v0.2 (34% WR drag, unmeasured cells)
- No volume scaling before decision-mode WR proof
- No vote, no score average, no confidence blend — single decision path

## Honest target restatement

User goal: ~10 signals/day, 6–8 win. Playbook expectation: S1+S2 combined
early shadow likely yields fewer, higher-quality observations (5–15/day
admissions before caps); 60–70% sustained is the realistic battle — 80% has
no measured support. The playbook's advantage: each percentage point comes
from a NAMED strategy in a NAMED state, so a losing week points to a fixable
cell instead of a mystery.
