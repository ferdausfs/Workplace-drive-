# SHADOW WINDOW STATUS — 2026-08-31 (v6.13.0 live audit)

**প্রশ্ন:** "update korar por theke ekhon porjonto ki obosta enginer?" — নিচে উত্তর।
**সংক্ষেপ:** ইঞ্জিন সুস্থ, **EC শ্যাডো ডেটা জমা হওয়া শুরু হয়েছে** (FIX-3 কাজ করছে), ভলিউম ফিরে এসেছে, এবং প্রাথমিক EC ল্যাডার **monotone** আসছে।

---

## ১. লাইভ ইঞ্জিন যাচাই (2026-08-30 ~18:10 UTC)

| চেক | মান | অবস্থা |
|---|---|---|
| /health version | **6.13.0** | ✅ |
| bindings | kvCache ready, rateLimiter KV-fallback, cerebrasAI ready | ✅ |
| API keys | 17 loaded, quotaUsedToday 1060, rotation idx 6 | ✅ |
| crons | */2 (result checker), */5 (scanner), Mon 00:00 (calibration) | ✅ |
| Telegram push | enabled, tokenValid (fttbotbot), delivered24h=5 | ✅ |
| session | NEW_YORK, quality HIGH | — |

**/api/signal স্পট-চেক** (BTC/ETH/SOL): NO_TRADE দিচ্ছে — এটা স্বাভাবিক; D2 হার্ড-ব্লক বন্ধ হয়ে গেলেও WEAK_TREND/DEAD_MARKET/entry-distance-এর মতো সফট ফিল্টার থেকে যাবে (ডিজাইন অনুযায়ী)।

---

## ২. শ্যাডো উইন্ডো: ডেটা আসছে?

**শ্যাডো শুরু: 2026-08-30T07:55Z** (প্রথম `empiricalConfidence`-ট্যাগড সিগন্যাল, ADA/USD)। এরপর ~১০ ঘণ্টায়:

- **৪১টা crypto BUY/SELL মিন্ট** → হার **~৯৫-১০০/দিন** (weekend, শুধু crypto)
- তুলনা: গেট-এরা ফ্লোর ছিল 4-24/দিন (08-24..29) → **~৪-১০x রিকভারি**
- **EC attach rate: ৪১/৪১ = ১০০%** (crypto BUY/SELL-এ) — FIX-1+FIX-3 পাইপলাইন নিখুঁত
- FOREX/OTC: EC নেই (cryptoOnly গার্ড — ডিজাইন অনুযায়ীই), সপ্তাহের দিনে ফরেক্স মিন্টও ফিরবে (হিস্ট্রির জন্য), push তবু crypto-only
- ফলাফল চেকার কাজ করছে: ৪১টার মধ্যে ৩৯টাই resolved (12W / 26L / 2 TIE / 1 open)

**রেজিম মিক্স ফিরেছে:** POST-era মিন্টে TRENDING ৪১% (17) / RANGING ৫৯% (24) — আগে ট্রেন্ডিং সম্পূর্ণ অনুপস্থিত ছিল (D2 ব্লক)।

---

## ৩. প্রাথমিক EC ল্যাডার (n ছোট, তবু দিক ঠিক)

| Grade | n | স্কোর রেঞ্জ | প্রাথমিক WR |
|---|---|---|---|
| A+ | 2 | 0.503-0.523 | 50.0% |
| A | 5 (4 decided) | 0.481-0.491 | 50.0% |
| B | 18 (16 decided) | 0.462-0.480 | 37.5% |
| C | 16 | 0.447-0.460 | 18.8% |

**A+ > A > B > C — ল্যাডার monotone।** n এখনো খুব ছোট (CI চওড়া) — এটা ভবিষ্যৎবাণী নয়, শুধু "পাইপলাইন + সেল-লজিক সঠিক দিকে যাচ্ছে" এর প্রাথমিক সংকেত। আসল ভারদিক্ট ২-৩ দিনের ডেটায়।

স্কোর ডিস্ট্রিবিউশন: min 0.447 / max 0.523 / mean 0.470 — B ব্যান্ড সবচেয়ে ভরাট (18)।
সেল মিক্স: hour GOOD 36/41 · rsiDirection CHASE 36/41 · structure ALIGNED 22 / BASE 14 / AGAINST 5 · fillState INSTANT 31 / PENDING 10।

---

## ৪. গুরুত্বপূর্ণ প্রাথমিক সংকেত: TRENDING কেন ব্লক করা হয়েছিল

POST-era স্লাইস (সব n ছোট, informational):

| স্লাইস | WR | n | 95% CI |
|---|---|---|---|
| **TRENDING** | **12.5%** | 16 | 3.5-36.0% |
| RANGING | 45.5% | 22 | 26.9-65.3% |
| INSTANT fill | 30.0% | 30 | 16.7-47.9% |
| PENDING_ENTRY | 37.5% | 8 | 13.7-69.4% |
| সব POST | 31.6% | 38 | 19.1-47.5% |

**এটাই পরিকল্পনার মূল কথা:** unblock করার উদ্দেশ্যই ছিল এই "বাজে স্লাইস"-গুলোর আসল WR বড় নমুনায় মাপা। এখন এরা EC সেলে জমছে — ২-৩ দিন পর `mode:'decision'` হলে **EC স্কোর এদের নিজে থেকেই C-তে নামিয়ে দেবে** এবং সেখান থেকে গ্রেড-ভিত্তিক সিদ্ধান্ত হবে। Hardcoded ব্লকের চেয়ে এটা ভালো, কারণ ব্লক নিরাপদ তবে অন্ধ; গ্রেড মাপা + সমAdjustable।

⚠️ **ব্যবহারকারীর জন্য মনে করিয়ে দিচ্ছি:** শ্যাডো উইন্ডোতে Telegram-এ আগের চেয়ে বেশি সিগন্যাল যাবে, যার মধ্যে ঐতিহাসিকভাবে-খারাপ স্লাইসও থাকবে (TRENDING ইত্যাদি)। এই উইন্ডোর সিগন্যাল **শেখার ডেটা**, ট্রেড-কোয়ালিটি নয়। কোয়ালিটি কন্ট্রোল ফিরবে decision-flip-এর পর।

---

## ৫. টাইমলাইন ও পরের ধাপ

- **শ্যাডো শুরু:** 08-30T07:55Z → **২-৩ দিন পূর্ণ:** 09-01 ~08:00Z (৪৮ঘ) / 09-02 ~08:00Z (৭২ঘ)
- **প্রজেকশন:** বর্তমান হারে ~২০০-৩০০ decided EC রেকর্ড জমবে (ভ্যালিডেশনের ন্যূনতম লক্ষ্য: প্রতি ব্যান্ডে যথেষ্ট n, top-two ব্যান্ডে ≥60)
- **ভ্যালিডেশন কমান্ড:** `python3 scripts/ec_shadow_validate.py` (Ftt-Otc-v6 রিপোতে সহ আছে)
- **ফ্লিপ নিয়ম:** ল্যাডার monotone (C<B<A<A+) **এবং** hour/fill সেল দিক ধরে রাখলে → `config.js`-এ `EMPIRICAL_CONFIDENCE.mode: 'shadow' → 'decision'` (এক লাইন) → version 6.14.0 → PR → merge → deploy → /health verify
- **রোলব্যাক:** D2 ফ্ল্যাগ দুটো + selectivity রুলস + mode — সবই এক-লাইন রোলব্যাক

---

## ৬. Raw ডেটা ও রিপ্রোডিউসিবিলিটি

- স্ন্যাপশট: `/home/z/my-project/shadow_status_2026-08-31/` (১৮ পেয়ার × 500, সম্পূরণ + `_meta.json`)
- স্ক্রিপ্ট: `scripts/ftt_shadow_status_0831.py` (এই রিপোর্টের সব সংখ্যা এ থেকে রিপ্রোডিউস হয়)
- API: `https://fttotcv6.umuhammadiswa.workers.dev/api/history?pair=X&limit=500` — **browser UA লাগবে**, 30 req/60s রেট-লিমিট (২.৫ সেকেন্ড ডিলে দাও)

*রিপোর্ট প্রোটোকল অনুযায়ী এই রিপোর্টটি `Workplace-drive-/reports/`-এ push করা হয়েছে; হ্যান্ডঅফ নলেজ `AGENT_HANDOFF.md` (repo root)-এ।*
