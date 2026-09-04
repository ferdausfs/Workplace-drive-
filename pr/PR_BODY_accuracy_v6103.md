# feat(engine): RANGING+ALIGNED hard block + regime-conditional calibration (v6.10.3)

**Repo:** `ferdausfs/Ftt-Otc-v6` · **Base:** `main` (`cf7200e`) · **Branch:** `feat/accuracy-v6103`

## Why (data-proven, Phase F 2026-08-15)

Scoring-inversion audit (`reports/SCORING_INVERSION_AUDIT_2026-08-15.md`) found the single biggest
accuracy lever in the forward window (4,188 decided signals):

| Cell | n | WR | CI |
|---|---|---|---|
| **RANGING + ALIGNED structure** | **1,639** | **41.2%** | 38.9–43.6 (decisively below 55.6% breakeven) |
| RANGING + AGAINST | 752 | 50.1% | 46.6–53.7 |
| TRENDING + ALIGNED | 245 | 51.4% | 45.2–57.6 |

Two root causes fixed:
1. **Inverted structure verdict in RANGING** (mean-reversion): ALIGNED is the *worst* cell, AGAINST
   the *best*. The pooled calibration table (and its ALIGNED→C cap) was regime-blind — it also
   wrongly crushed TRENDING+ALIGNED (the *best* cell, 51.4%).
2. **RANGING+ALIGNED was being emitted as a normal signal** despite being the biggest losing pool.

## What changed (10 files, 144+/35-)

1. **`src/signal/engine.js`** — new D2 hard block `D2_RANGING_ALIGNED_BLOCK` (same mechanism as the
   existing TRENDING block: NO_TRADE + D2 shadow capture + AI skip). Behind
   `CONFIG.D2_RANGING_ALIGNED_BLOCK_ENABLED=true` (one-line rollback). Both calibration calls now
   pass `marketRegime`.
2. **`src/analysis/calibration.js`** — `structWRByRegime` table (RANGING: ALIGNED .412 / AGAINST .501 /
   MIXED .443 / NEUTRAL .422; TRENDING: ALIGNED .514 / MIXED .420 — cells with n<50 fall back to pooled,
   no invented numbers). `getCalibratedScore`/`getCalibratedGradeAndConfidence` take an optional regime.
   The structure cap is now regime-aware: ALIGNED→C only in RANGING; in TRENDING ALIGNED is NOT capped.
3. **`src/analysis/grade.js`** — regime passthrough (backward compatible).
4. **`src/config.js`** — `D2_RANGING_ALIGNED_BLOCK_ENABLED: true` with justification comment.
5. **`src/index.js`, `src/handlers/health.js`, `scripts/redeploy.sh`** — version **6.10.2 → 6.10.3**.
6. **`scripts/fix_tests.mjs`** — new T45 block (10 assertions: regime-aware cap + ranking + engine wiring).
7. **`scripts/d2_tests.mjs`** — #10 updated: flat (RANGING) fixtures may now hit ONLY the new
   RANGING_ALIGNED branch (previously asserted "no D2 filter"). Not weakened — asserts the exact new
   intended branch and no other.
8. **`scripts/r71_tests.mjs`** — `BASELINE_COMMIT` re-baselined to this engine tip (documented
   "re-baseline after engine change" protocol).

## Honest expected impact (NOT a 75% claim)

- Blocks ~39% of signals (RANGING+ALIGNED) → **fewer but better** signals.
- Pooled WR: **~44.3% → ~46.3%** (full window); post-calibration era **~48.5% → ~50.4%**.
- Still **below 55.6% breakeven**. This is a data-backed step (largest losing cell removed), not a
  breakthrough. 75%+ win rate remains unsupported by the data — no curve-fitting, no invented edge.

## Verification (run by the author)

- `node --check` all `src/*.js` — PASS
- `fix_tests.mjs` **321/0** · `d2_tests` **41/0** · `r71_tests` **117/0** (re-baselined)
- `phase10_integration` 19/0 · `phase10_smoke` 71/0 · `phase7_integration` 36/0 · `phase7_smoke` 68/0
- `probe_tests` 34/0 · `entry_hit_tests` 7/7 · `fx_mode_tests` 20/20
- Bundle `worker-v6103-20260815.js` built: 324,906 B, sha `cc9a680b…`, node --check PASS

## Deploy (separate step, user decision — engine behavior change)

```bash
# after merge: git checkout main && git pull
npm i esbuild && ./node_modules/.bin/esbuild src/index.js --bundle --format=esm --target=es2022 --outfile=worker-v6103-20260815.js
export CLOUDFLARE_ACCOUNT_ID=b3082da169faec70425179ca62500bc1
export EXPECTED_BYTES=324906
bash scripts/redeploy.sh worker-v6103-20260815.js   # verify_health now expects 6.10.3
```

Phase F rule: engine change is PR-first + user merge + deploy + forward verification. After deploy,
the next snapshot should show pooled WR lifting and NO new RANGING+ALIGNED signals.
