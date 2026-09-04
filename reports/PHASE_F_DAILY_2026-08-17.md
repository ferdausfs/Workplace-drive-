# Phase F Daily Checkup — 2026-08-17 (Monday, live data)

**Data source:** Worker API থেকে **সরাসরি fresh snapshot** (sandbox → `fttotcv6...workers.dev`, 18 pair × 500 signal) + drive tarballs (FULL 08-12, 08-14, 08-15)। Dedup by signal id।
**Snapshot time:** 2026-08-17 12:42 UTC (সোমবার, day এখনো চলছে — forex আজ open)।
**নতুন:** এই turn থেকে snapshot-টা আমি নিজেই worker থেকে টেনে নিই — phone-এ `phase_f_snapshot.sh` চালানোর দরকার নেই।

## Headline (honest)
- **Full forward WR: 43.5%** (6,099 decided) — breakeven 55.6%-এর নিচে ❌ (অপরিবর্তিত, expected — পুরনো data dominate করে)
- **POST-FIX-EH: 48.4%** (n=1,637) — improvement টিকে আছে ✅
- **Last 7 দিন: 52.9%** (n=510, CI 48.6–57.2) — **breakeven-এর দিকে আসছে** (উপরের প্রান্ত 57.2 > 55.6), কিন্তু এখনো clear নয়
- **D4 ML: এখনো no edge** (LEGIT confident-only 52.4%, CI 37.7–66.6 — ambiguous)
- **FIX-EH কাজ করছে** ✅ (eh-MISS 52.2%, tautology ভাঙা)

## 1) Full forward
| Metric | Value |
|---|---|
| Decided | 6,099 |
| WR | 43.5% |
| CI | (42.3, 44.8) |
| Verdict | ❌ below breakeven |

## 2) Era + trend
| Window | n | WR | CI |
|---|---|---|---|
| PRE (<08-07) | 4,462 | 41.8% | (40.3, 43.2) |
| POST-FIX-EH | 1,637 | 48.4% | (46.0, 50.8) |
| **Last 7d (08-11..17)** | 510 | **52.9%** | (48.6, 57.2) |
| Last 3d (08-15..17) | 107 | 45.8% | (36.7, 55.2) |

## 3) Per-day (নতুন দিন bold)
```
08-11  n= 94  56.4%  ↑
08-12  n=120  58.3%  ↑
08-13  n=106  50.0%
08-14  n= 83  54.2%
08-15  n= 28  42.9%   (আগের 5 → এখন 28; weekend, ছোট n)
08-16  n= 40  55.0%   (নতুন data)
08-17  n= 39  38.5%   (আজ, day চলছে — final না)
```

## 4) TODAY (08-17) — intraday, final নয় (12:42 UTC)
- **WR 38.5%** (15/39), CI (24.9, 54.1) — n ছোট + day অর্ধেক শেষ
- Asset: CRYPTO 31.0% (29) · FOREX **60.0%** (10) — forex আজ open
- Direction: BUY 41.2% (17) · SELL 36.4% (22)
- Grade: A+ 27.8% (18) ⚠️ · B 40.0% (15) · C 80.0% (5)
- Pair (n≥5): LINK/USD **0%** (8) ⚠️ · DOT/USD 66.7% (6) · AVAX/USD 20.0% (5)
- entryHit: HIT 39.3% (28) · MISS 36.4% (11)

## 5) FIX-EH (corrected entryHit) — full
| Metric | n | WR | CI |
|---|---|---|---|
| eh-HIT | 1,089 | 47.8% | (44.8, 50.7) |
| eh-MISS | 343 | 52.2% | (46.9, 57.4) |
- Tautology: legacy-MISS 100% (expected) · **eh-MISS 52.2% → FIX working** ✅
- entryHit এখনো selector নয় (HIT 47.8% ≈ MISS 52.2%)।

## 6) D4 ML (chronological, test = 08-16+17)
- Baseline engine WR (test window সব): 44.4%
- LEGIT (signal-time only): confident-only 52.4% (CI 37.7–66.6) → ⚠️ ambiguous, **no edge**
- LEAKAGE diagnostic (entryHit সহ): 47.2% — fake edge-ও আসলে নেই (আগের 59.7% ছিল; sample-ভেদে fluctuate করে)
- [TRADE] p≥0.55 subset: 55.6% (n=18, CI 33.7–75.4) — sample খুব ছোট, এতে ভরসা নেই

## Verdict (honest, no hype)
1. **Trend positive, breakeven এখনো স্পর্শ হয়নি।** POST 48.4% + last-7d 52.9% = FIX-EH-এর পর উন্নতি টিকে আছে, কিন্তু 55.6% breakeven-এর উপরে **নির্ভরযোগ্যভাবে** ওঠেনি (CI overlap করছে)।
2. **আজ (08-17) intraday খারাপ দেখাচ্ছে (38.5%), কিন্তু final না** — সোমবারের day শেষ হওয়া পর্যন্ত অপেক্ষা। LINK/USD-এর 0/8 আর A+ grade-এর 27.8% আজকের n-এ noise হতে পারে।
3. **D4 ML-এ edge নেই** — কোনো conditional strategy এখনো evidence-ভিত্তিক নয়।
4. **পরের meaningful check:** আজ রাত (UTC 08-18 শুরু) — 08-17-এর পুরো দিনের result settle হলে।

## Workflow note (নতুন ক্ষমতা)
- স্যান্ডবক্স থেকে worker API direct pull করছি → প্রতিদিনের snapshot আমার হাতেই, phone ছাড়া। তুমি শুধু বলবে "checkup", বাকিটা আমি করবো।
- Drive tarball push এখনো লাগবে (audit trail-এর জন্য), তবে checkup-এর জন্য নয়।
