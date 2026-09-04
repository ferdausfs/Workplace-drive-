# Forex SELL Probe — Push Runbook (২০২৬-০৮-০৪)

> **কী:** engine-এ কোনো বদল নয় — শুধু **instrumentation**। প্রতিটা forex SELL signal-এর
> context (regime/session/HTF/RSI) + actual/flipped outcome private KV-তে জমবে।
> ৭–১৪ দিন পরে evidence দিয়ে সিদ্ধান্ত: forex SELL সত্যিই ভুল দিকে তাকায় কিনা,
> কোন slice-এ (regime/RSI/session) বেশি ভুল, আর উল্টালে (BUY) breakeven-এর উপরে যায় কিনা।

## Deploy (Termux)

```bash
cd ~/Ftt-Otc-v6
git fetch /sdcard/Download/ftt-probe-fxsell-2026-08-04.bundle HEAD
git merge FETCH_HEAD
git push origin main
```

GitHub Actions auto-deploy করবে (deploy.yml)।

## Deploy-এর পর verify

```bash
# 1) worker healthy
curl -s https://fttotcv6.umuhammadiswa.workers.dev/health | head -c 120

# 2) কোনো public leak নেই (প্রতিটা = 0)
curl -s "https://fttotcv6.umuhammadiswa.workers.dev/api/signal?pair=EUR/USD" | grep -c "FOREX_SELL_PROBE"
curl -s "https://fttotcv6.umuhammadiswa.workers.dev/api/history?pair=EUR/USD&limit=1" | grep -c "probe:"

# 3) forex SELL এখনো স্বাভাবিক ট্রেড হচ্ছে (production unchanged)
curl -s "https://fttotcv6.umuhammadiswa.workers.dev/api/signal?pair=EUR/USD" | grep -o '"finalSignal":"[A-Z_]*"'
```

## ৭–১৪ দিন পরে — কীভাবে পড়বেন

Probe data public API-তে নেই — private KV-তে (`probe:obs:*`)। Reading/analysis:
- আমি একটি analyzer script বানিয়ে দেবো (R7.1/D2 report-এর মতো)
- অথবা এখানে বলুন, আমি worker-এ একটা internal-only report endpoint/script করি

**Analyzer যা দেখাবে:**
- forex SELL actual WR (দিন-বিভক্ত, CI সহ)
- flipped (BUY) counterfactual WR — একই trade-এ
- slice breakdown: RANGING vs TRENDING, RSI<45 / 45-60 / >60, session quality
- কোন slice-এ SELL systematically ভুল → conditional fix-এর টার্গেট

## সিদ্ধান্ত-গাছ (window শেষে)

```
forex SELL WR < 45% (CI-সহ) এবং flipped > 55.6% breakeven?
  ├─ হ্যাঁ, নির্দিষ্ট slice-এ (যেমন RANGING+RSI>60)
  │    → paper-only conditional flip test → engine-এ conditional fix
  ├─ হ্যাঁ, সব slice-এ
  │    → forex SELL blanket restriction/flip — তবে আগে paper test
  └─ না / ছোট n / দিন কম
       → আরো observe — কোনো বদল না
```

## নিয়ম (ভাঙা হয়নি)

- ❌ engine behavior change নেই — production byte-identical
- ❌ কোনো public contract বদলায়নি
- ✅ fail-open — probe error কখনো live signal-কে প্রভাবিত করে না
- ✅ private namespace (`probe:`) — R7.1/D2-র থেকে আলাদা
