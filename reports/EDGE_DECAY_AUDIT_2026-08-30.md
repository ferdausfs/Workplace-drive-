# EDGE DECAY AUDIT — 2026-08-30 (fresh live pull)

**প্রশ্ন:** selectivity gate (v6.11.0, live 08-21) deploy-এর পর আসলে কী হচ্ছে? Single accuracy (WR) বাড়লো না কমলো?

**Method:** Live worker API থেকে fresh pull — 18 pair × 500 history, dedup → **5,611 decided signals** (08-01 → 08-30)। Gate-era (08-21..30) n=193। Wilson CI সহ। Script: `scripts/` (live pull + decay audit, re-runnable)।

---

## ১. Headline (honest — আগের প্রত্যাশা data-য় টেকেনি)

| Metric | PRE-gate (08-01..20) | POST-gate (08-21..30) |
|---|---|---|
| Decided | 5,418 | 193 |
| **WR** | **43.3%** (CI 41.9–44.6) | **38.9%** (CI 32.3–45.9) |
| Volume/day | ~175 | **~21 (−88%)** |
| Gate-pass (would-be-pushed) | — | **n=9 only (9 দিনে!)** |

- **Gate deploy-এর পর WR নামেছে, বাড়েনি।** Promise ছিল push-WR ~57-60% — বাস্তবে gate-era-র would-be-pushed slice = 44.4% (n=9, পরিসংখ্যানগতভাবে অর্থহীন ছোট)।
- **Volume ধ্বসে ~88% কমেছে** — TRENDING block (post-gate TRENDING n=0) + RANGING+ALIGNED block + ATR gate + cryptoOnly মিলে signal generation প্রায় শুকিয়ে গেছে। Telegram-এ সংকেতই প্রায় আসছে না।

## ২. Edge decay — প্রমাণসহ (এটাই মূল রোগ নির্ণয়)

প্রতিটা "edge" historical window-এ কাজ করেছে, forward-এ মরে গেছে:

| Slice | 08-21-র আগে (research claim) | POST-gate (fresh data) |
|---|---|---|
| PENDING_ENTRY | **57.9%** (n=178) | 40.9% (n=22) |
| entryDist ≥ 0.1% | **60.0%** (n=95) | 50.0% (n=14) |
| ATRpct < 50 (calm) | 54.0% (n=285) | 41.6% (n=77) |
| ATRpct ≥ 50 (hot) | 48.4% | 37.1% |
| TRENDING (খারাপ বলা হতো) | 39.3% (n=641) | n=0 (blocked) |

- PENDING_ENTRY all-time এখনো সবচেয়ে বড় gap: **56.0% (n=200) vs INSTANT 46.1% (n=1,570)** — কিন্তু post-gate ছোট n-এ টেকেনি।
- **প্যাটার্ন পরিষ্কার:** যে slice থেকে যে সময়ে "edge" দেখা যায়, সেটা deploy-এর পরের regime-এ decay করে। এটা এখন ৩ বার প্রমাণিত (round-3 improvement, PENDING_ENTRY, ATR)।
- **কারণ:** RSI/MACD/BB/pattern-এর মতো 1–15min TA feature-এর binary OTC/crypto-তে **কোনো স্থায়ী causal edge নেই**। D4 ML-ও এটাই বলেছিল। Window-specific "edge" = regime noise + overfit।

## ৩. Grade ladder আজও উল্টো (calibration fix-ও forward-এ টেকেনি)

ALL-TIME (নতুন data, n বড়):
```
grade C  → 47.3% WR (n=1,161)   ← সেরা
grade B  → 43.6% WR (n=2,440)
grade A  → 41.0% WR (n=1,012)
grade A+ → 39.1% WR (n=998)     ← সবচেয়ে খারাপ
```
Post-gate: A+ = 30.8% (n=65)। calib-v1 (train 08-01..06) deploy হওয়ার পরেও ladder উল্টোই আছে।

**কাঠামোগত কারণ (এটা fix করা যায়, কিন্তু WR-এর মূল lever না):** বেশি indicator agreement = move-এর শেষ দিকে entry = mean-reversion-এ ধরা। "সবুজ সংকেত বেশি = ভালো trade" ধারণাটাই এই বাজারে উল্টো। Static table দিয়ে এটা ঠিক হয় না, কারণ সম্পর্কটা regime-dependent।

## ৪. যেগুলো STABLE সব window-এ (এগুলোই আসল সম্পদ)

1. **FOREX সব সময় খারাপ:** BUY 32.8% / SELL 35.7% (all-time, n=979) — প্রতিটা window-এ একই। cryptoOnly gate সঠিক ছিল।
2. **Entry price > prediction:** INSTANT-chase (price পিছু নেওয়া) সব window-এ PENDING-এর চেয়ে খারাপ। এটা predictive edge না — mechanical price-improvement।
3. **Crypto SELL (46.4%) > BUY (43.4%)** all-time — দুর্বল কিন্তু স্থায়ী lean।
4. বাকি সব (hour-of-day, grade, AI-agree, confidence bucket) — window-dependent noise।

## ৫. Single accuracy বাড়ানোর পথ (ranked by evidence + honesty)

### Lever 1 — Entry-timing engine change (সবচেয়ে বড় mechanical lever)
Signal আসার সাথে সাথে 5-min ঘড়ি শুরু না করে, **pullback পর্যন্ত অপেক্ষা → fill হলে ঘড়ি শুরু**। INSTANT-chase loss-pool (n=1,570, 46.1%) পুরোটা বাদ যাবে। এটা prediction না — ভালো দামে কেনা। Engine change: medium complexity, PR-ready করা যায়।
- Honest expectation: WR moves toward the 56% slice, **গ্যারান্টি নয়** — কারণ post-gate PENDING-ও 40.9% দেখিয়েছে (n=22)। Forward test ছাড়া নিশ্চিত না।

### Lever 2 — Rolling weekly recalibration (ranking সৎ করা)
CALIB table এখন 08-01..06 train — পুরনো। Weekly rolling window-এ নিজেকে refresh করবে, নাহলে **grade/confidence bot-এ দেখানোই বন্ধ** (ভুল তথ্য দেখানোর চেয়ে না দেখানো ভালো)।

### Lever 3 — Gate loosen (forward test-এর জন্য যথেষ্ট sample দরকার)
এখন gate-pass ~1/day — ১০০ sample জমতে ৩+ মাস। `maxAtrPercentile` 50→65, RANGING allow, INSTANT + dist≥0.1% allow করলে gate-pass volume 5-10× হবে — তবে WR কিছুটা নামবে। **Data ছাড়া কোনো সিদ্ধান্ত নেওয়া যাবে না।**

### Lever 4 — নতুন signal source (একমাত্র সত্যিকারের +7pp পথ)
বর্তমান feature-set exhausted। নতুন কী হতে পারে: BTC→alt lead-lag, 1h/4h regime context, funding/liquidation events, লম্বা expiry (15-30min — noise কম)। এটা বড় scope, আগে data collection দরকার।

### Lever 5 — Expectation re-scope
80% payout-এ breakeven 55.6% খুব উঁচু। যদি engine-এর ceiling সত্যিই ~48% হয়, তাহলে সৎ উত্তর: **এই setup-এ profitable হওয়া যাচ্ছে না** — মডেল নয়, payout/expiry/বাজার প্রশ্নটাই দেখতে হবে।

## ৬. কী করবো এখন (proposal)

1. **আজ:** Lever 2 + 3 একসাথে PR (calibration refresh + gate params) — কম ঝুঁকি, বেশি data flow।
2. **এই সপ্তাহ:** Lever 1 (entry-at-fill) design + PR — সবচেয়ে বড় lever, ভালোভাবে test করে।
3. **চলন্ত:** Lever 4-এর data collection (lead-lag correlation study) — নতুন research track।
4. **বন্ধ করা উচিত:** নতুন কোনো "magic filter" খোঁজা পুরনো window-এ — প্রমাণিত হয়েছে ওগুলো decay করে।

---

*Data: live worker pull 2026-08-30 · 5,611 decided · Wilson CI · no invented numbers · honest, no hype*
