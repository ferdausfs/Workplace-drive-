# EC SHADOW VALIDATION — INTERIM (day 1) — 2026-08-31 08:33Z

**প্রশ্ন:** "kono balo thik ki pele? flip/deploy-এর জন্য কিছু লাগবে?" — নিচে সৎ উত্তর।
**ভেরডিক্ট:** ডেটা-মেশিন নিখুঁত চলছে; কিন্তু **এখনই flip না, deploy-ও দরকার নেই** — ল্যাডার এখনো non-monotone + নতুন একটা সেল-ডিজাইন ঘাটতি ধরা পড়েছে। উইন্ডো পূর্ণ হোক (09-02), তারপর সিদ্ধান্ত।

---

## ১. সংগ্রহ স্বাস্থ্য — সবুজ

| মেট্রিক | মান |
|---|---|
| ইঞ্জিন | v6.13.0 healthy, bindings ঠিক, push tokenValid |
| EC রেকর্ড (২৪.৫ঘ-তে) | **১৭৮** (08-30: 99, 08-31: 79) — ~৮৯/দিন, টার্গেট হারে |
| decided | ১৬৪/১৭৮ (checker দ্রুত) |
| Telegram delivered24h | **৯২** (ভলিউম ফিরেছে — মনে রাখবে: এগুলো শেখার ডেটা) |

## ২. প্রাথমিক ল্যাডার — এখনো ফ্লিপ-যোগ্য না

| Grade | WR | n | CI |
|---|---|---|---|
| C | 42.6% | 68 | 31.6-54.5 |
| B | 36.8% | 76 | 26.9-48.1 |
| A | 38.9% | 18 | [n<30] |
| A+ | 50.0% | 2 | [n<30] |

- Monotone: **NO** (C > B); A+ > C: YES কিন্তু A+ n=2 অর্থহীন
- Pooled EC-era WR: **39.6%** (n=164) — base 45%-এর নিচে
- Score quantiles: p50=0.466, p75=0.467, p90=0.486 — **A+ ব্যান্ড (≥0.500) আসলে প্রায় কখনো ভরবে না** (178-এ ২টা) → flip-এর আগে ব্যান্ড re-derive আবশ্যক

## ৩. 🔍 আসল আবিষ্কার: structure সেল regime-নির্ভর — EC-তে regime নেই!

EC-era-তে **TRENDING = ৭৭% সিগন্যাল** (আগে ব্লকড ছিল, এখন মাপা হচ্ছে — এটাই উইন্ডোর কাজ):

| মিক্স | WR | n | ব্যাখ্যা |
|---|---|---|---|
| TRENDING + ALIGNED | **28.8%** | 59 | trend-এর দিকে ঢুকলে = late entry, mean-reversion-এর শিকার |
| TRENDING + BASE | 40.0% | 40 | — |
| TRENDING + AGAINST | **60.7%** | 28 | counter-trend এখানে সেরা (exhausted move) |
| RANGING + ALIGNED | 38.5% | 13 | ছোট n |
| RANGING + BASE | 50.0% | 16 | — |
| RANGING + AGAINST | 28.6% | 7 | ছোট n |

→ **একই structure সেল দুই regime-এ উল্টো কাজ করে** (TRENDING: AGAINST>>ALIGNED; RANGING: উল্টো)। EC শুধু structure মাপে, regime মেলায় না — তাই সেল স্কোর misspecified। এটাই C>B inversion-এর মূল ইঞ্জিন।

অন্যান্য সেল: hour GOOD 34.0% (n=100) vs BAD 52.4% (n=42) — উল্টো দিক; fillState PENDING 33.3% (n=33) vs পুরনো মাপ 56.0%; rsiDirection CHASE 94% ঘিরে রেখেছে (SELL CHASE 40.6% n=133, BUY CHASE 22.7% n=22) — সেলটা এখন প্রায় discriminates-ই না।

**সতর্কতা:** সবগুলোই day-1 নমুনা; CI চওড়া। দিক-পরিবর্তনগুলো suggestive, conclusive নয়।

## ৪. সিদ্ধান্ত — কী করবো, কী করবো না

**এখন (09-01):**
- ❌ Flip না — checklist (a)(b)(d) ব্যর্থ
- ❌ Deploy না — deploy করার মতো কোনো change-ই নেই
- ✅ উইন্ডো চলুক — 09-02 সকালে ~২৪০-২৭০ decided রেকর্ড হবে, তখন সেল দিকগুলো স্থির হবে

**09-02-তে দুইটা পথ:**
1. **ল্যাডার ঠিক হয়ে গেলে** → one-line `mode:'decision'` flip (তখন fresh PAT + CF token লাগবে)
2. **regime-dependence স্থির থাকলে** → ছোট EC-v2.1 প্যাচ: structure সেলকে **regime-ভাগ করা** করা (TRENDING/RANGING-এ আলাদা মান) — সেই প্যাচেও token লাগবে; এটাই সম্ভাব্য সেরা পথ, কারণ flip করলেও regime-blind স্কোর ভুল দিকে গেট করবে

## ৫. টোকেন গাইড

**আজ কিছুই লাগবে না — টোকেন দেওয়ার দরকার নেই।** Flip/প্যাচের দিন (সম্ভবত 09-02) লাগবে: fresh GitHub PAT (দুই রিপো push/PR) + CF token (Workers Scripts:Edit) + Account ID। ততদিন worker নিজে চলবে, ডেটা জমবে।

*Raw: /home/z/my-project/ec_shadow_day1_2026-08-31 (স্ন্যাপশট) · স্ক্রিপ্ট: scripts/ec_shadow_validate.py (2 বাগফিক্সসহ) · PAT revoke-এর কারণে এই রিপোর্ট+হ্যান্ডঅফ লোকালে কমিটেড, fresh PAT পেলেই push হবে।*
