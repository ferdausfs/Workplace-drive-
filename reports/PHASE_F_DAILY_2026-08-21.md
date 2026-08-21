# Phase F Daily Checkup — 2026-08-21 (Thursday, ৪ দিনের accumulated data)

**Data source:** Worker API থেকে fresh live pull (18 pair × 500 signal, 08-21 08:14 UTC) + drive tarballs। Dedup by id।
**নতুন data:** 08-17-র পর drive-এ কিছু push হয়নি, কিন্তু worker history-তে সব জমা আছে → এই pull-এ 08-17 (final), 08-18, 08-19, 08-20, 08-21 (intraday) সব এসেছে।

## ⚠️ Headline (honest — আগের optimism ভুল প্রমাণিত হয়েছে)
আগের checkup-এ আমি বলেছিলাম "trend breakeven-এর দিকে" — **সেটা premature ছিল।** এখন ৪ দিনের নতুন data-য় স্পষ্ট:

- **Last-7d WR: 52.9% → 44.6%** (08-17 থেকে নেমে গেছে)
- 08-11/12-এর breakeven-স্পর্শ (56.4%/58.3%) ছিল **noise, trend নয়**
- POST-FIX-EH **48% এ স্থির** হয়েছে — breakeven 55.6%-এর দিকে আর যাচ্ছে না

## 1) Full forward
| Metric | Value |
|---|---|
| Decided | 6,259 |
| WR | 43.5% (CI 42.3–44.8) |
| Verdict | ❌ below breakeven 55.6% |

## 2) Era
| Window | n | WR | CI |
|---|---|---|---|
| PRE (<08-07) | 4,462 | 41.8% | (40.3, 43.2) |
| POST-FIX-EH | 1,797 | 48.0% | (45.7, 50.3) |
| week1 (08-07..13) | 1,447 | 48.2% | (45.7, 50.8) |
| week2 (08-14..21) | 350 | 46.9% | (41.7, 52.1) |

## 3) Rolling 7-day trend (গুরুত্বপূর্ণ — peak থেকে পতন)
```
08-10..16  n=717  WR=48.7%
08-11..17  n=536  WR=52.8%   ← peak
08-12..18  n=495  WR=50.7%
08-13..19  n=405  WR=47.9%
08-14..20  n=340  WR=47.1%
08-15..21  n=267  WR=44.6%   ← নেমে গেছে
```

## 4) Per-day (নতুন দিন bold)
```
08-14  n= 83  54.2%
08-15  n= 28  42.9%
08-16  n= 40  55.0%
08-17  n= 65  43.1%   (final)
08-18  n= 53  39.6%   ← নতুন
08-19  n= 30  43.3%   ← নতুন
08-20  n= 41  46.3%   ← নতুন
08-21  n= 10  40.0%   ← আজ intraday (08:14 UTC, final না)
```

## 5) FIX-EH (entryHit corrected) — full
| Metric | n | WR | CI |
|---|---|---|---|
| eh-HIT | 1,213 | 47.5% | (44.7, 50.3) |
| eh-MISS | 379 | 50.9% | (45.9, 55.9) |
- Tautology: legacy-MISS 100% (expected) · eh-MISS 50.9% → **FIX working** ✅
- entryHit এখনো selector নয় (47.5% ≈ 50.9%)।

## 6) D4 ML (chronological, test = 08-19..21)
- LEGIT (signal-time only): confident-only **34.1%** (CI 21.9–48.9) → ❌ breakeven-এর নিচে, **স্পষ্ট no edge**
- [TRADE] p≥0.55 subset: 0/11 (CI 0–25.9) → ❌
- LEAKAGE diagnostic (entryHit সহ): 47.4% — fake edge-ও এখন দেখাচ্ছে না

## Verdict (honest, no hype)
1. **FIX-EH-এর আসল effect: 41.8% → ~48%।** এটা real improvement, কিন্তু সেটা breakeven-এর কাছাকাছিও নয়, আর **গত ৪ দিনে improvement-টা বাড়ছে না, বরং last-7d 44.6%-এ নেমেছে।**
2. **08-11/12-এর breakeven-স্পর্শ = noise** — ছোট n (94/120) + পরের দিনগুলোয় ফিরে গেছে। আমি আগে একে "trend হতে পারে" বলেছিলাম; এখন ৪ দিনের data-য় নিশ্চিত: trend ছিল না।
3. **System এখনো লাভজনক নয়।** AI-agree, grade, entryHit, D4 ML — কোনোটাতেই breakeven-এর উপরের edge নেই।
4. **সিদ্ধান্তের পয়েন্ট (তোমার call):** Phase F-এর মূল প্রশ্ন "forward signals কি লাভজনক?" — এখন পর্যন্ত উত্তর: **না**। বিকল্প: (a) আরও data জমা করা (ছোট-n noise কমাতে), (b) signal-filter/better model নিয়ে নতুন research, (c) Phase F pause করে অন্য কিছুতে focus। তুমি কী চাও বললে সেভাবে এগোই।

## Data note
- Drive-এ 08-17-র পর কোনো tarball push হয়নি (তোমার phone-এ `phase_f_snapshot.sh` চলে না)। Checkup-এর জন্য এটা আর দরকারও নেই — আমি worker থেকে direct pull করি। তবে audit trail-এর জন্য চাইলে phone-এ `bash ~/phase_f_snapshot.sh` + drive-তে push রাখতে পারো।
