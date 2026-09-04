# Phase F Daily Checkup — 2026-08-16 (sandbox, drive data)

**Data source:** `Workplace-drive-/data/` tarballs (FULL 08-12 + daily 08-14, 08-15)
**Snapshot days available:** 26 দিন (06-03 → 08-15; 08-13 missing হিসেবে note হয়নি — 08-14/15 snapshot-এর history 500-row span-এ ঢাকা)
**আজকের (08-16) snapshot এখনো drive-এ push হয়নি** — latest = 08-15। 08-15 = Saturday (weekend), snapshot নেওয়া 03:28 UTC-তে → সেদিন decided signal মাত্র **5টা**।

## Headline (honest)
- **Full forward WR: 43.5%** (5,997 decided) — breakeven 55.6%-এর নিচে ❌
- **কিন্তু স্পষ্ট উন্নতি:** PRE-FIX-EH 41.8% → **POST-FIX-EH (>=08-07) 48.6%** (+6.8pp, n=1535)
- **Last 7 দিন (08-09..15): 49.6%** (n=957) — এখনো breakeven-এর নিচে, তবে trend উপরের দিকে
- **D4 ML: কোনো edge নেই** (confident-only 47.4%, breakeven-এর নিচে)
- **FIX-EH সঠিক কাজ করছে:** entryHit tautology ভেঙেছে (eh-MISS WR 53.0%, আগে 100% ছিল)

## 1) Full forward (সব history)
| Metric | Value |
|---|---|
| Decided signals | 5,997 |
| WR | **43.5%** |
| Wilson CI | (42.3, 44.8) |
| Breakeven (80% payout) | 55.6% |
| Verdict | ❌ below breakeven |

## 2) Era comparison (FIX-EH deploy-এর আগে/পরে)
| Era | n | WR | CI |
|---|---|---|---|
| PRE (<08-07) | 4,462 | 41.8% | (40.3, 43.2) |
| POST-FIX-EH (>=08-07) | 1,535 | **48.6%** | (46.1, 51.1) |
| Last 7d (08-09..15) | 957 | 49.6% | (46.5, 52.8) |

→ **Improvement real**, কিন্তু breakeven 55.6% এখনো clear হয়নি। Research item-ই থাকছে।

## 3) Per-day WR (chronological)
```
07-29  n= 445  39.1%
07-30  n= 738  39.6%
07-31  n= 572  46.3%
08-01  n= 339  45.7%
08-02  n= 206  49.0%
08-03  n= 322  45.3%
08-04  n= 639  36.0%
08-05  n= 630  39.2%
08-06  n= 530  45.3%
08-07  n= 413  46.0%   ← FIX-EH deploy
08-08  n= 165  49.1%
08-09  n= 303  51.8%
08-10  n= 246  38.2%
08-11  n=  94  56.4%  ↑ breakeven-এর উপরে
08-12  n= 120  58.3%  ↑
08-13  n= 106  50.0%
08-14  n=  83  54.2%
08-15  n=   5  60.0%  (n খুব ছোট — weekend)
```

## 4) আজকের (08-15) detail — n=5, কোনো conclusion-এর জন্য যথেষ্ট নয়
- WR 60% (3/5), CI (23.1, 88.2) — অর্থহীনভাবে চওড়া
- Asset: CRYPTO only (forex weekend-এ closed)
- Direction: BUY only (5টাই)
- Grade: C (3টা, 66.7%), B (2টা, 50%)
- Confidence: সব >=72
- entryHit: HIT 5/5

## 5) FIX-EH (entryHit corrected) — full
| Metric | n | WR | CI |
|---|---|---|---|
| eh-HIT | 1,013 | 47.9% | (44.8, 51.0) |
| eh-MISS | 317 | 53.0% | (47.5, 58.4) |
- Tautology check: legacy-MISS = 100% (old field, expected) · eh-MISS = 53.0% (≠100% → **FIX working**)
- Insight: entryHit নতুন semantics-এও winner আলাদা করতে পারে না (HIT 47.9% vs MISS 53.0% — দুটোই coin-flip-এর কাছাকাছি)।

## 6) D4 ML (chronological split, train→test on last 2 days)
- LEGIT (signal-time features only): all-pred accuracy 43.2%, confident-only **47.4%** (CI 32.5–62.7) → ⚠️ breakeven-এর নিচে
- LEAKAGE diagnostic (entryHit সহ): 59.7% — fake edge-টা দেখানো হয়েছে, use নয়
- Top features (LEGIT): asset_type, direction, session, alignment — কোনো single feature-এ edge নেই

## Verdict (honest, no hype)
1. **System আগের চেয়ে ভালো, লাভজনক নয়।** 41.8% → 48.6% বাস্তব উন্নতি, but breakeven 55.6%-এ পৌঁছাতে আরও কাজ লাগবে।
2. **08-11/12-এ breakeven ছুঁয়েছে** (56.4%/58.3%) — এটা noise নাকি trend, আরও দিনের data লাগবে (n ছোট)।
3. **আজকের (08-15) data-য় কিছু বলা যাবে না** — weekend + early snapshot = মাত্র 5 signal। পরের weekday snapshot (Mon 08-17) পর্যন্ত অপেক্ষা।
4. **AI agreement, grade, entryHit — কেউই reliable selector নয়** (সব 47–53% range)।
5. **পরামর্শ:** এখনই নতুন কিছু বানানোর দরকার নেই; Mon (08-17)-এর snapshot-এ দেখতে হবে 08-13..16-এর weekend ছোট-n wash out হওয়ার পর trend ধরে রাখে কি না।

## Next snapshot (phone, Termux)
```bash
cd ~ && bash phase_f_snapshot.sh      # UTC day-এ একবার
```
08-16 (Sun) snapshot-ও ছোট হবে (weekend)। **আসল পরবর্তী meaningful snapshot = Mon 2026-08-17।**
