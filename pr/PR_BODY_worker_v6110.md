# chore(version): 6.10.4 → 6.11.0 (selectivity gate release marker)

**Repo:** `ferdausfs/Ftt-Otc-v6` · **Base:** `main` (`176f485`) · **Branch:** `chore/version-6110`

## Why
Selectivity gate (PR #27) main-এ merge হয়ে গেছে, কিন্তু **deploy verify-র কোনো উপায় নেই** —
version 6.10.4-ই থাকলে live worker-এ গেট এসেছে কিনা `/health` দেখে বোঝা যাবে না। এই bump-টা
deploy-এর পর `/health` → `version: 6.11.0` দেখিয়ে live confirm করবে।

## Changes (2 files, +3/−3)
- `src/index.js` — header comment + welcome message `v6.10.4` → `v6.11.0`
- `src/handlers/health.js` — `/health` response version `6.10.4` → `6.11.0`

## Verification
- ✅ `git apply --check` OK on `176f485` · `node --check` pass (২ file)

## Deploy flow (এই bump merge-এর পর)
```bash
cd ~/Ftt-Otc-v6 && git checkout main && git pull
git checkout -b chore/version-6110
git apply ~/Workplace-drive-/pr/ftt_worker_v6110_version_bump.patch
git add -A && git commit -m "chore(version): 6.10.4 -> 6.11.0 (selectivity gate marker)"
git push -u origin chore/version-6110
# → PR open + merge
# → bundle: npm i esbuild && ./node_modules/.bin/esbuild src/index.js --bundle --format=esm --target=es2022 --outfile=worker-selectivity-20260821.js
# → Termux: cp worker-selectivity-20260821.js ~/Ftt-Otc-v6/ && bash redeploy.sh
# → verify: curl https://fttotcv6.umuhammadiswa.workers.dev/health  → version 6.11.0
```
