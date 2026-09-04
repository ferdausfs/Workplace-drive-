# feat(selectivity-gate): quality-over-quantity push filter (evidence-backed)

**Repo:** `ferdausfs/Ftt-Otc-v6` · **Base:** `main` (`d6c0446`) · **Branch:** `feat/selectivity-gate`

## Why (Phase F forward data, ~6.3k decided signals)
Engine-এর core directional WR ~45-48% — breakeven 55.6%-এর নিচে। কিন্তু কিছু signal-time
feature-এ স্পষ্ট edge পাওয়া গেছে:
- `fillStatus=PENDING_ENTRY` (entryDist ≥ 0.05%): **57.9% WR** (n=178) vs INSTANT 46.9%
- ATR percentile < 50 (calm): **53.6%** (n=289)
- FOREX: **34.0%** (n=949) vs CRYPTO 45.2%
- TRENDING regime: **38.8%** (n=798)

## What this does
নতুন **SELECTIVITY_GATE** — শুধু Telegram push filter করে। History + `/api/signal` + `/api/latest`
আগের মতোই সব signal record/return করে (research window intact), শুধু **subscriber push** হয় তখনই
যখন signal নিচের bar pass করে:

1. `cryptoOnly: true` — forex push বন্ধ
2. `excludeTrending: true` — TRENDING regime push বন্ধ
3. `requirePendingEntry: true` — entryDist < 0.05% (INSTANT chase) বাদ
4. `maxAtrPercentile: 50` — high-vol বাদ

সব config-driven (`CONFIG.SELECTIVITY_GATE`), এক-line kill switch (`enabled`), fail-open
(feature missing হলে block হয় না)।

## Changes (3 files, +97/−1)
1. **`src/analysis/selectivity.js`** (নতুন) — `evaluateSelectivityGate(signal, pair, assetType)`।
2. **`src/config.js`** — `SELECTIVITY_GATE` config block (evidence comment সহ)।
3. **`src/handlers/signal.js`** — `saveAndPush`-এ push-এর আগে gate check; block হলে log
   (`selectivityGate: push suppressed for X — reason`)।

## Verification (honest)
- ✅ `node --check` — ৩ file pass
- ✅ `git apply --check` OK on `d6c0446` (fresh clone)
- ✅ Gate logic ৭ case-এ test: forex/trending/instant/high-vol → BLOCKED; good/missing-fail-open/OTC → PUSH
- ⚠️ **Build/deploy = আপনার Termux bundle** (runbook অনুযায়ী)। CI-র ওপর ভরসা নেই।
- ⚠️ Expected WR ~57-60% point-estimate, কিন্তু CI wide — **forward data-য় prove করতে হবে**।

## Expected effect
- Push হওয়া signal-এর WR ~57-60% (point estimate), signal count ~৭৬% কম (~11/day)।
- Research data কোনো ক্ষতি হয় না — gate-এর নিজের effect-ও history থেকে measure করা যাবে।

## Deploy (আপনার দিকে)
```bash
cd ~/Ftt-Otc-v6 && git checkout main && git pull
git checkout -b feat/selectivity-gate
git apply ~/Workplace-drive-/pr/ftt_worker_selectivity_gate.patch
git add -A && git commit -m "feat(selectivity-gate): quality-over-quantity push filter"
git push -u origin feat/selectivity-gate
```
PR: `https://github.com/ferdausfs/Ftt-Otc-v6/compare/main...feat/selectivity-gate`
Merge → bundle (`npm i esbuild && ./node_modules/.bin/esbuild src/index.js --bundle --format=esm --target=es2022 --outfile=worker-selectivity-20260821.js`) → Termux `bash redeploy.sh` (unique filename!)।
