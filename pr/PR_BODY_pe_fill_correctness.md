# fix(stats): PENDING_ENTRY unfilled trades must not count as mechanical WIN (v6.10.2)

**Repo:** `ferdausfs/Ftt-Otc-v6` · **Base:** `main` (`e7fbeac`) · **Branch:** `fix/pending-entry-fill-correctness`

## Why (data-proven, Phase F review 2026-08-14)

Independent multi-agent Phase F review (4 agents + reviewer, all CONFIRMED) found a **grading
artifact** in the result resolver (`scheduledTracker`):

- A `PENDING_ENTRY` signal is one whose entry price sits away from the current price (the trade
  can only be taken if price comes to the entry).
- If the entry is **never touched** during `[signal → expiry]` (`entryHit === false`), the trade
  never filled — but the resolver still graded it WIN/LOSS against `entryPrice`.
- An unfilled favourable limit (BUY entry below market / SELL entry above market) that the market
  never revisits is "in the money" by construction → **100% WIN**.
- **Live evidence (forward window):** `PENDING_ENTRY` + `entryHit=false` → **100.0% WIN (n=43)**;
  excluding those rows drops the `PENDING_ENTRY` slice from a fake 60.1% to 43.8%.

This inflates live WR stats (and would push fake WIN notifications). It also silently corrupted
Phase F forward analysis.

## What changed (5 files, 90 insertions / 12 deletions)

1. **`src/history/stats.js`** — the fix. After the FIX-EH entry-hit computation, a non-shadow
   `PENDING_ENTRY` signal whose `entryHit === false` is reclassified **TIE** (stored, but excluded
   from WR stats and result pushes via the existing TIE/UNKNOWN path). `INSTANT` rows are
   unaffected; `cbShadow` rows deliberately keep their counterfactual WIN/LOSS resolution (D2
   shadow semantics unchanged).
2. **`src/handlers/health.js`** + **`src/index.js`** — version bump **6.10.1 → 6.10.2** (this is a
   stats-behavior change; the version anchor must move so a deploy is verifiable).
3. **`scripts/fix_tests.mjs`** — new `T44` regression block (4 cases: unfilled→TIE + no stats;
   filled→still graded; INSTANT untouched; cbShadow untouched) + version assertion updated to 6.10.2.
4. **`scripts/redeploy.sh`** — `/health` post-deploy check now expects 6.10.2 (else the next deploy
   would falsely fail).

## Verification (run by the reviewer on the patched tree)

- `git apply --check` — **PASS** (clean on `e7fbeac` state)
- `node --check` all `src/*.js` — **PASS**
- `fix_tests.mjs` — **311 / 0** (304 prior + 7 new T44 assertions)
- `phase10_integration` 19/0 · `phase10_smoke` 71/0 · `phase7_integration` 36/0 · `phase7_smoke` 68/0
- `d2_tests` 39/0 · `probe_tests` 34/0 · `entry_hit_tests` 7/7 · `fx_mode_tests` 20/20
- `bash -n scripts/redeploy.sh` — **PASS**

## Impact on live stats (expected, honest)

After deploy, the next `/api/history` + `/api/stats` will stop counting unfilled PENDING_ENTRY
trades as wins. Recorded WR will **drop slightly** (removing fake wins) but become honest. Phase F
forward data from the deploy point onward is clean.

## Deploy note (NOT in this PR)

- Rebuild the bundle after merge (esbuild), unique filename `worker-v6102-<date>.js`,
  `EXPECTED_BYTES` = the new bundle's exact size.
- `/health` should show `version: "6.10.2"`.
- User decision + change control per Phase F rules (this is an engine/stats change, data-backed).
