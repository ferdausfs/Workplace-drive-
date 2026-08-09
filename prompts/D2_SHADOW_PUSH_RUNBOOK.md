# D2 Shadow Collector + BAD_PAIR Suspend — Push Runbook (২০২৬-০৮-০২)

> **কী হলো:** Block-গুলো আর Phase F-এর data আটকাবে না — দুটো উপায়ে:
> 1. **BAD_PAIR block suspend** → USD/JPY, AUD/USD, DOT/USD আবার real signal দেবে (forward data জমবে)
> 2. **D2 Shadow Collector** → TRENDING/HIGHEST-session block-গুলোও private shadow observation দিয়ে data দেবে — production behavior অপরিবর্তিত
>
> Commit: `dd0d473` (worker repo `Ftt-Otc-v6`)

---

## যা যা বদলালো (৬ ফাইল)

| ফাইল | পরিবর্তন |
|---|---|
| `src/config.js` | `D2_BAD_PAIR_BLOCK_ENABLED: false` (Phase F suspend flag) |
| `src/signal/engine.js` | D2 block-এর সময় would-be signal capture (Symbol-এ, non-enumerable) |
| `src/signal/d2shadow.js` | **নতুন** — audit transport + admission gate |
| `src/history/d2store.js` | **নতুন** — private KV store (`d2obs:`/`d2pending:`/`d2idx:`) |
| `src/handlers/signal.js` | admission (ctx.waitUntil, fail-open) |
| `src/index.js` | resolver (R7.1-এর মতোই 2-min cron-এ) |

## Verification (আমি যা চালিয়েছি)

```
node scripts/d2_tests.mjs ............ 39/39 PASS ✅
node scripts/phase7_smoke.mjs ........ 68/68 PASS ✅
node scripts/phase7_integration.mjs .. 36/36 PASS ✅
node scripts/phase10_smoke.mjs ....... 61/61 PASS ✅
node scripts/phase10_integration.mjs . 19/19 PASS ✅
node scripts/r71_tests.mjs ........... 113/116 — ৩টা fail HEAD-এও ছিল (pre-existing)
node --check ....................... সব ফাইল clean ✅
```

## Termux থেকে deploy

```bash
cd ~/Ftt-Otc-v6
# d2-shadow-collector.bundle ফাইলটা Termux-এ আনুন (e.g. /sdcard/Download/)
git fetch /sdcard/Download/d2-shadow-collector.bundle HEAD
git merge FETCH_HEAD
git push origin main
```

GitHub Actions (`deploy.yml`) main-এ push হলেই Cloudflare Worker-এ auto-deploy করবে।

**অথবা** tar.gz দিয়ে: `tar xzf d2-shadow-worker-changes.tar.gz` → `git add -A && git commit -m "..." && git push origin main`

## Deploy-এর পরে verify

```bash
# 1) BAD_PAIR suspend লাইভ: USD/JPY (forex open হলে, ২২:০০ GMT-এর পর)
curl -s "https://fttotcv6.umuhammadiswa.workers.dev/api/signal?pair=USD/JPY" | python3 -m json.tool | grep -A2 finalSignal

# 2) TRENDING block এখনো live (নিরাপদ):
curl -s "https://fttotcv6.umuhammadiswa.workers.dev/api/signal?pair=BTC/USD" | python3 -m json.tool | grep -E "finalSignal|D2_TRENDING"

# 3) Public API-তে কোনো D2 shadow leak নেই:
curl -s "https://fttotcv6.umuhammadiswa.workers.dev/api/signal?pair=BTC/USD" | grep -c "wouldBeDirection"   # output: 0
curl -s "https://fttotcv6.umuhammadiswa.workers.dev/api/history?pair=BTC/USD&limit=1" | grep -c "d2obs"     # output: 0
```

## কীভাবে data পড়বেন (৭–১৪ দিন পরে)

- **BAD_PAIR pair-গুলো (USD/JPY, AUD/USD, DOT/USD):** `/api/history?pair=X&limit=500` — এখন real signal আসবে
- **Blocked-slice shadow data:** শুধু KV-র ভেতরে (`d2obs:*`), public API-তে নেই। পড়ার জন্য ছোট analyzer script বানিয়ে দেবো (যেমন R7.1-এর report) — চাইলে বলুন, `${HOME}/Ftt-Otc-v6`-এ worker env-সহ রান করতে হবে
- **নিয়ম:** D2 shadow = pre-AI counterfactual। AI-rescued ট্রেড এতে নেই (সেগুলো real history-তে) — তাই shadow-র WR-কে "production-এর মতোই হতো" পড়া যাবে না, এটা "D2 block-টা pre-AI slice-কে বাঁচিয়েছে কি না" দেখায়

## Fallback (কিছু সমস্যা হলে)

```bash
git revert dd0d473 && git push origin main
```

## যে নিয়ম ভাঙা হয়নি

- ❌ Engine-এর মূল logic/tuning বদলায়নি — শুধু instrumentation + suspend
- ❌ কোনো public contract বদলায়নি (API/history/telegram একই)
- ❌ কোনো real-money recommendation নেই
- ✅ TRENDING + HIGHEST_SESSION block active আছে — resume-টা shadow-তেই মাপা হবে
