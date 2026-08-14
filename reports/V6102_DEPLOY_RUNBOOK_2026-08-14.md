# 🚀 DEPLOY RUNBOOK — Worker v6.10.2 (PENDING_ENTRY fill-correctness) — 2026-08-14

**Repo:** `ferdausfs/Ftt-Otc-v6` · **Merged:** PR #21 → main `380916cb` ✅ (reviewer-verified)
**Live status:** এখনো 6.10.1 (deploy আলাদা ধাপ — এই doc-এ শুধু প্রস্তুতি; deploy করলে change control হয়)।

## কেন v6.10.2 (Phase F data-proven)
- `PENDING_ENTRY` + `entryHit=false` (entry never touched) → আগে mechanical WIN। Live evidence: 100% WIN (n=43)।
- Fix: unfilled PENDING_ENTRY → **TIE** (WR stats + result push থেকে বাদ)। INSTANT/cbShadow unchanged।
- ফল: deploy-এর পর live WR সামান্য কমবে কিন্তু **honest** — Phase F forward data deploy-পয়েন্ট থেকে clean।

## Bundle (READY — verified by me)
- `bundles/worker-v6102-20260814.js`
- **322,420 bytes** · SHA256 `a0551d67080b8919b8cd56faf6525af65e663789935b7531b529c3a65f3976dd`
- `node --check` PASS · `FTT Signal Worker v6.10.2` · fill-fix + TIE present · 0 secrets

## Deploy (যখন decision নেবেন — Termux)
```bash
cd ~/Ftt-Otc-v6
# (a) fresh build (preferred) বা (b) drive থেকে bundle copy
# a) git pull origin main
#    npm i esbuild && ./node_modules/.bin/esbuild src/index.js --bundle --format=esm --target=es2022 --outfile=worker-v6102-20260814.js
# b) cp ~/Workplace-drive-/bundles/worker-v6102-20260814.js ./
ls -la worker-v6102-20260814.js        # expect 322420

export CLOUDFLARE_ACCOUNT_ID=b3082da169faec70425179ca62500bc1
export EXPECTED_BYTES=322420
bash scripts/redeploy.sh worker-v6102-20260814.js
```

## Post-deploy live verify
```bash
curl -sS https://fttotcv6.umuhammadiswa.workers.dev/health | python3 -c "import sys,json; d=json.load(sys.stdin); print('version', d['version'])"
```
- expect `version 6.10.2` (redeploy.sh-এর verify_health-ও 6.10.2 check করে)।

## Phase F পরবর্তী ধাপ
- Forward window খোলা রাখুন (live worker চলছে)। Deploy-এর **পরের** snapshot-এ unfilled PE আর fake WIN হবে না।
- পরের snapshot-এর সাথে এই fix-এর আগের data তুলনা করলে PE slice-এর WR drop **expected** (fake wins gone) — সেটা bug না।

## Notes
- Deploy করা হলে version anchor 6.10.2 দিয়ে live-verify হবে; না করলে live 6.10.1-ই থাকবে (দুটোই সঠিক, শুধু সিদ্ধান্তের ব্যাপার)।
- Old PR #18 (stale duplicate) — GitHub-এ close করে দিন।
