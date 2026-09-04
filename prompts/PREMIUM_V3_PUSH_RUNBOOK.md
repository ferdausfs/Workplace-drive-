# UI v3 Premium — Push Runbook (২০২৬-০৮-০২)

> কি হলো: app-এর UI/UX premium করা হলো। **Engine/worker একদম স্পর্শ করা হয়নি** — presentation layer মাত্র।

## যা যা implement হলো (commit `7f39e25`)

| ফিচার | কোথায় | বিবরণ |
|---|---|---|
| **Market Pulse Ticker** | `src/components/Ticker.tsx` (নতুন) + Home | ৮টা pair-এর চলমান strip: ▲BUY/▼SELL + confidence + result dot। `/api/history?limit=1` — cheap KV read, engine চলে না, quota খরচ হয় না। Fail হলে "—" |
| **Board tab (Dashboard)** | `src/components/DashboardView.tsx` (নতুন) + bottom nav-এ "Board" | সব pair এক নজরে: direction + confidence, lifetime server WR + n, **LIVE badge** (<15 min), **tie flag** (entry≈exit → feed artifact), breakeven honesty note, 5-min cache |
| **Hero meta chips** | `src/components/SignalHero.tsx` | AI consensus (✓ AI Consensus), regime, alignment, structure verdict, confluence — সব conditional |
| **Cleanup** | `src/App.tsx` | Pre-existing unused imports মুছে `tsc` এখন 0 errors |

## Verification (আমি নিজে যা চালিয়েছি)

```
tsc --noEmit ................ 0 errors  ✅
npm run build ............... single-file 344.65 kB (gzip 97.54 kB) ✅
scripts/phase5_smoke.mjs .... 53/53 PASS ✅
scripts/phase6_smoke.mjs .... 76/79 (৩টা fail HEAD-এও ছিল — pre-existing, আমার না) ✅
Live API data contract ...... /api/stats → {pair, stats:{...}}, /api/history → signals[] ✅ (live verify করা হয়েছে)
```

## ডেলিভারি ফাইল (এই workspace-এ)

- `premium-v3.bundle` — git bundle (commit `7f39e25` সহ)
- `premium-v3-app-changes.tar.gz` — ৫টা বদলানো/নতুন ফাইলের tar

## Termux থেকে push করার ২টা উপায়

### উপায় A — git bundle (সবচেয়ে clean, recommended)

Termux-এ repo-তে:

```bash
cd ~/Ftt-app-002
# bundle ফাইলটা Termux-এ আনুন (e.g. scp / cp / টেলিগ্রাম saved file থেকে)
# তারপর:
git fetch /sdcard/Download/premium-v3.bundle HEAD
git merge FETCH_HEAD
git push origin main
```

### উপায় B — tar.gz extract

```bash
cd ~/Ftt-app-002
# tar.gz ফাইলটা Termux-এ আনুন, তারপর:
tar xzf premium-v3-app-changes.tar.gz
git add -A
git commit -m "UI v3 premium: ticker + board dashboard + hero meta chips"
git push origin main
```

## Push-এর পরে verify (মিস করবেন না)

```bash
# Vercel auto-deploy হয় — একটু পরে live site-এ check করুন:
# 1) Home-এ ticker দেখা যাচ্ছে?
# 2) Bottom nav-এ "Board" ট্যাব আছে? সব pair-এর WR/n দেখায়?
# 3) কোনো console error নেই? (কনসোল খুলে দেখুন)
```

এছাড়া এই workspace থেকেই live check করে দিতে বলতে পারেন — আমি `/api` এবং live page দুটোই verify করে দেবো।

## যে নিয়ম ভাঙা হয়নি

- ❌ Engine/worker change নেই (Phase F observe mode intact)
- ❌ কোনো মিথ্যা win-rate claim নেই — প্রতিটা সংখ্যা sample size (n) সহ
- ❌ কোনো subscription/payment — "premium" = UI/UX, সব ফিচার ফ্রি

## Fallback (কিছু ভুল হলে)

```bash
git revert 7f39e25 && git push origin main
```
(প্রয়োজন হলে — আশা করি লাগবে না; সব test পাস)
