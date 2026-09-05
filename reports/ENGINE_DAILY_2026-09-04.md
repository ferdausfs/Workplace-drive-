# ENGINE DAILY — 2026-09-04 (Sig-v1.0.0 প্রথম পূর্ণদিনের খবর)

**সময়:** 2026-09-04 ~06:20 UTC (দিন এখনো মাত্র ~৬.৩ ঘণ্টা বয়সী) · **ভিত্তি:** লাইভ API পুল (scripts/engine_daily_0904.py)

## ১. ইঞ্জিন স্বাস্থ্য

- `/health`: **Sig-v1.0.0** healthy, push pipeline intact (subs=1, tokenValid=true)
- **delivered24h = 10** — ঠিক প্রেডিক্টেড ৫-১৫/দিন ব্যান্ডে ✓ (পুরনো legacy stream ~৭৮/দিন ছিল)

## ২. আজকের মিন্ট (৬.৩ ঘণ্টায় ৪৬টা)

| মার্কেট | মিন্ট | W/L (resolved) | WR |
|---|---|---|---|
| Crypto | 10 | 2W/7L | 22.2% |
| Forex | 17 | 6W/10L | 37.5% |
| **OTC (নতুন)** | 19 | 10W/9L | **52.6%** |
| **মোট** | **46** | 18W/26L | 40.9% |

- গতকাল (২৪ঘ): 187 মিন্ট, 45.6% — আজকের পেস ~175/দিন, স্বাভাবিক
- **OTC প্রথম দিনেই সেরা স্লাইস** (52.6%, n=19) — Sig-v1.0.0-এর "সব পেয়ার খোলা" ফিচার কাজ করছে
- Crypto 22.2% (n=9) — নমুনা ছোট, TRENDING দিনে legacy stream-এর পরিচিত দুর্বলতা

## ৩. Strategy-based counting-এর অবস্থা (গুরুত্বপূর্ণ)

- History রেকর্ডে strategy ট্যাগ **থাকে না by design** — sigv1 ট্যাগ শুধু push-payload-এ যায়, প্রতিটা strategy-wanted emit v7obs KV-তে আলাদা জমছে (cron resolve করছে)
- **Per-strategy × per-market scoreboard এখনো public API-তে নেই** — `summarizeV7()` v7store-এ আছে কিন্তু কোনো route একে এক্সপোজ করে না
- আজকের ১০টা push-ই playbook-এর কথা বলা (strategy-approved); বাকি ৩৬ legacy mint = শেখার ডেটা
- লাইভ স্পট-চেক: BTC/ETH TRENDING → playbook চুপ ✓, GBP RANGING → কোনো trigger নেই ✓ — router ঠিকমতো সংযত

## ৪. পরের ধাপ

1. ৩-৫ দিন emit জমুক (প্রতি স্ট্র্যাটেজি n≥50 দরকার voice-gate-এ)
2. Scoreboard পড়ার ২টা পথ: (a) পরের token উইন্ডোতে CF KV সরাসরি পড়া, (b) worker-এ ছোট `/api/v7summary` route যোগ করা (summarizeV7 রিওয়্যার) — পরের deploy-এ করা যায়
3. Flip-gate অপরিবর্তিত: per-strategy WR ≥ 55.6% (n≥50) → voice; মোট WR ≥ 60% (n≥100, CI-lo>50%) → decision

**নোট:** PAT revoke করা — এই রিপোর্ট + handoff §৬ এন্ট্রি লোকাল কমিটে আছে, push হবে পরের token উইন্ডোতে।

---

## সংযোজন — 2026-09-05 ভোর (~02:50 UTC): আজকের প্রথম চেক

- আজ (০৯-০৫, ~৩ঘ বয়সী): 14 mint, 10 resolved → **0W/10L**। দুই উইন্ডো:
  - 00:00–00:40Z: 3 LOSS (ETH BUY, AUD/USD-OTC BUY, XRP SELL) — hour-0 playbook-এর অনুমোদিত ঘণ্টা; health.lastAttempt প্রমাণ করে 00:00:15Z-এ ETH/USD BUY playbook push হয়েছে → LOSS (n=1)
  - **02:00–02:40Z burst: 7 LOSS** — BTC/ETH/XRP/ADA একসাথে SELL = correlated burst; কিন্তু এই সময় **VETO_HOUR [1,2,3]**-এর ভেতরে → playbook চুপ ✓ (শেষ push 00:00Z, পরে কিছু নেই); এগুলো legacy stream-এর শেখার ডেটা
- গতকাল (০৯-০৪) পূর্ণদিন: 235 mint, 229 resolved, 94W/135L = 41.0% (legacy প্রত্যাশিত রেঞ্জ)
- ⚠️ **delivered24h = 28** — প্রেডিক্টেড ৫–১৫/দিনের ~২×; playbook প্রত্যাশার চেয়ে বেশি কথা বলছে — per-strategy WR দেখা না পর্যন্ত এটা নিয়ন্ত্রণহীন
- Correlation risk প্রথমবার লাইভ প্রমাণিত: এক টিকে ৪ পেয়ারে SELL = আসলে ১টা বাজি — daily budget / per-minute push-cap প্রয়োজন (decision-mode ডিজাইনে ছিল, push-mode-এ নেই)
- **অগ্রাধিকার:** `/api/v7summary` route — playbook-এর নিজের W/L এখনো বাইরে থেকে অদৃশ্য
