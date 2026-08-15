# 🔬 SCORING INVERSION — ROOT-CAUSE AUDIT (Lever 1) — 2026-08-15

**Auditor:** Arena main agent · **Method:** live code (GitHub main `cf7200e`) + fresh data (4,188 decided) + live `/api/calib`।
**Scope:** কেন Grade/structure/confidence উল্টো কাজ করছে + কীভাবে accuracy বাড়ানো যায় (data-backed)।

---

## ১. সবচেয়ে বড় খবর — inversion-এর অর্ধেক আগেই ঠিক হয়েছে

Engine-এ **calibration system already আছে** (`src/analysis/calibration.js`, version `calib-v1-2026-08-09`):
- Empirical table: `structWR` (ALIGNED 39.3% worst / AGAINST 46.6% best) + `confBucketWR` (80-83 worst 36.7% / 88+ best 44.6%) — TRAIN 08-01..06 থেকে derived।
- Grade এখন এই calibrated score থেকে আসে + **structure override**: ALIGNED → max C, MIXED → max B, AGAINST/NEUTRAL no cap।

**Data-প্রমাণ (grade WR by era):**

| Era | A+ | A | B | C |
|---|---|---|---|---|
| PRE-calib (08-01..09, n=3533) | 40.2% (worst) | 43.1% | 42.9% | **48.5% (best)** ← উল্টো |
| **POST-calib (08-10..15, n=655)** | **50.0%** | 50.0% | **51.3%** | **45.7% (worst)** ← **ঠিক হয়ে গেছে** |

**অর্থাৎ:** ৪-agent review-র "C > A+" headline-টা **era-confounded** ছিল — pooled window-এর বেশিরভাগ row pre-calibration যুগের। Calibration deploy (08-09/10)-এর পর grade ladder **monotonic** (A+/A/B ~50% > C 45.7%)।

## ২. কিন্তু ৩টা সমস্যা এখনো বাকি (root cause)

### Root cause #1 — self-calibration **কখনো চলেনি**
- Live `/api/calib` → **`dynamic: null`**। Weekly self-calib (`recomputeCalibration`) একবারও run হয়নি।
- কারণ: cron `0 0 * * 1` শুধু **08-14-তে live add হয়েছে**; প্রথম fire হবে **08-17 Monday 00:00 UTC**।
- ফল: engine এখনো **08-01..06-এর frozen static table** দিয়ে চলছে — ৮ দিনের পুরনো, আর v6.10.2-এর honest data-তে recompute হয়নি।

### Root cause #2 — structureVerdict inversion-টা **RANGING-regime artifact**
- **RANGING** (window-র 75%): ALIGNED **41.2%** vs AGAINST **50.1%** — structure confirm করলে লস, disagree করলে জয় (mean-reversion)।
- **TRENDING**: ALIGNED **51.4%** (n=245) — structure confirm **কাজ করে**!
- calibration-এর pooled `structWR` (AGAINST best) ranging-bias বেক করে নিয়েছে। **Market TRENDING হলে এই table-ই উল্টো হয়ে যাবে।**

### Root cause #3 — confidence non-monotone + era-drift
- PRE: 80-83 worst (36.7%) · POST: 76-79 best (55.6%) — relationship **unstable**, frozen `confBucketWR` stale।

## ৩. Selectivity-র বাস্তব সীমা (data থেকে)

| Rule | Full window | Post-calib era |
|---|---|---|
| BASELINE (all) | 44.3% | 48.5% |
| skip RANGING+ALIGNED | 46.3% (n=2549) | 50.4% (n=399) |
| keep AGAINST | 49.7% (n=779) | 52.6% (n=137) |
| keep TRENDING+ALIGNED | 51.4% (n=245) | 50.0% (n=32) |
| keep NOT-ALIGNED | 45.9% | 50.8% |

**কোনো rule-ই 55.6% CI clear করে না** — কিন্তু direction স্পষ্ট: post-calib era ~48-52%।

## ৪. Proposed fix design (PR-first, approval লাগবে — engine change)

### FIX-A — Regime-conditional calibration (আসল accuracy lever)
`structWR` এখন pooled; এটাকে **marketRegime-conditional** করো:
- `structWR = { RANGING: {ALIGNED 0.41, AGAINST 0.50, ...}, TRENDING: {ALIGNED 0.51, ...} }`
- grade/confidence যেন regime-সচেতন হয় — ranging-এ AGAINST-কে reward, trending-এ ALIGNED-কে reward।
- Impact: ranking inversion দূর + confidence honest। **Promise নয়** — forward data লাগবে।

### FIX-B — self-calib চালু verify (কোনো code change নয়, সোমবার)
- 08-17 Monday 00:00 UTC-তে `recomputeCalibration` fire করবে → `dynamic` populate হবে (≥100 obs fail-open)।
- আমি সোমবার সকালে verify করবো। (ঐচ্ছিক: on-demand trigger endpoint যোগ করা — ছোট PR।)

### FIX-C — selectivity emission gate (future, approval লাগবে)
- "RANGING + ALIGNED → emit না / grade C-তে flag" — আসলে calibration-এর ALIGNED→C cap-ই এটা আংশিক করে। আলাদা emission gate করলে signal-count কমবে (quantity → quality), কিন্তু data এখনো breakeven-এর প্রমাণ দেয় না।

## ৫. Honest expectation (75% নিয়ে সোজা কথা)

- FIX-A + FIX-B মিলিয়ে: post-calib WR **48.5% → ~50-52%**-এ যাওয়া plausible, সেরা regime+structure cell-এ breakeven **ছোঁয়া** সম্ভব — কিন্তু **55.6% CI-সহ clear** করতে গেলে আরো forward data + নতুন edge দরকার।
- **75%+ = data-supported নয়।** Engine-এর core directional edge ~48-52%; calibration/selectivity শুধু ranking + noise-cutting করে, direction-টা নতুন করে বানায় না।
- প্রকল্পের ইতিহাস: সবচেয়ে বড় জাম্প +6.7pp (real bug fix)। পরের ধাপগুলো ছোট কিন্তু জমে যায়।

## ৬. Recommendation (কী করবো?)

1. **FIX-B আগে** (ঝুঁকি শূন্য): সোমবারের self-calib verify — ইতিমধ্যে scheduled।
2. **FIX-A implement** (PR-first, আপনি approve করলে): regime-conditional `structWR` — এটাই সবচেয়ে evidence-backed engine change।
3. **FIX-C পরে**: forward data জমলে।

**আপনার decision লাগবে:** FIX-A implement করবো (PR + test + patch ready)? এটা engine change, তাই Phase F rule মেনে আপনার approval চাইছি।
