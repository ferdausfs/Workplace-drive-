# 🔬 PHASE F DEEP DIVE — 2026-08-14 (independent multi-angle passes)

**Analyst:** Arena main agent · **Method:** একই snapshot-এ ৭টা স্বাধীন pass (প্রতিটা আলাদা কোণ, cross-check)।
**Data:** ৪,১৬১ decided (forward window ≥08-01)। Breakeven 55.6%, Wilson CI 95%, pre-registered slices।

---

## ১. সবচেয়ে বড় NEW finding — round-3-এর উন্নতি ১০০% real (composition নয়)

| | n | Overall WR | FOREX share |
|---|---|---|---|
| pre-round3 | 2568 | 41.8% | 12.2% |
| post-round3 | 1593 | 48.5% | 12.6% |

**Within-class decomposition:**
- CRYPTO: 43.9% → **48.3%** (CI 45.7–50.9)
- FOREX: **26.8% → 49.5%** (CI 42.6–56.4) ← প্রায় দ্বিগুণ!
- Mix-shift contribution: **0.1pt** → পুরো +6.7pt-ই **within-class উন্নতি**, asset-shift-এর ছলনা নয়।
- **Permutation test (5000 shuffle): p < 0.001** — chance নয় (আগের CI-separation-ও তাই বলেছিল, এখন দ্বিতীয় স্বাধীন পদ্ধতিতে confirmed)।

## ২. FOREX-এর আগের "35.6% drag" গল্পটা আংশিক ভুল ছিল

- Pre-round3 FOREX = **26.8%** (ভাঙা ছিল — bugfix-এর আগে), post-round3 = **49.5%**।
- FOREX সমস্যা এখন **concentrated**: 
  - **RANGING regime**: FOREX/RANGING/BUY **32.8%** (n=250), SELL 41.7% (n=228)
  - **ASIAN session**: 34.1% (n=331) · LONDON 36.9% · NEW_YORK 41.0%
  - sessionQuality HIGH/HIGHEST ফিল্টারও FOREX-কে বাঁচায় না (HIGH 39.5%)।

## ৩. সবচেয়ে promising cell (কিন্তু gate এখনো CLEAR নয়)

| Cell | n | WR | CI |
|---|---|---|---|
| **CRYPTO / TRENDING / BUY** | 183 | **56.3%** | 49.0–63.3 |

- WR breakeven-এর উপরে, কিন্তু **CI lower 49.0 < 55.6** → gate পাস করেনি। Single-cell + multiple-comparison risk → **watch only**, এখনো কোনো action নয়।

## ৪. অন্যান্য notable slices (কেউই breakeven clear করে না)

- **structureVerdict উল্টো**: AGAINST 49.9% (n=768) > MIXED 43.9% > ALIGNED 42.5% — structure label predictive নয় (বা anti-predictive)।
- **alignment**: ALL_BEARISH 46.4% > ALL_BULLISH 42.5% (SELL-bias-এর সাথে মেলে)।
- **aiStatus**: BOTH_AGREE 40.5% < OK 44.3% < BOTH_UNAVAILABLE 44.7% — **AI agreement WR বাড়ায় না** (উল্টো সামান্য কম)। AI এখনো edge দেয় না।
- **Indicators**: RSI>70 56.4% (n=39), ADX>40 52.3% (n=65), atrPct 0.3–0.7 51.8% (n=83) — ছোট n, CI wide, কোনোটা gate clear নয়।

## ৫. Honest bottom line

1. **Round-3 real +6.7pt (within-class), permutation-confirmed** — engine-র দিক সঠিক।
2. **FOREX এখনো weakest, কিন্তু আর "hopeless" নয়** (post-round3 49.5%) — residual weakness = RANGING + ASIAN session-এ।
3. **কোনো slice-ই 55.6% breakeven CI-সহ clear করে না** — Phase F gate এখনো বন্ধ। Action: কিছুই নয় (no inversion/pair-block/real-money)।
4. **আরও analysis ≠ নতুন data** — নতুন data আসবে শুধু forward window চলতে থাকলে (live worker চালু আছে, আজ 08-14 এখনো partial)।

---
**বাকি:** একই data-তে আরও agents-এর independent pass চালানোর pack → `prompts/PROMPT_PHASE_F_MULTI_AGENT_2026-08-14.md` + `scripts/phase_f_baseline.py` (identical baseline, যেন সবার তুলনা apples-to-apples হয়)।
