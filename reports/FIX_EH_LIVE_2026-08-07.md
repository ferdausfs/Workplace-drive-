# FIX-EH — LIVE VERIFICATION (2026-08-07, ~09:00 UTC)

**Status:** ✅ FIX-EH metric deployed + LIVE + working

## Deploy journey (the important lesson)
1. **Merge PR #9** → main `7ed962a` ✓
2. **Bundle rebuilt** (esbuild) → `worker-fixeh-20260807.js` (275,816 bytes, MD5 `899d4fb9...`)
3. ⚠️ **First deploy uploaded the STALE bundle** — `~/storage/downloads/worker.js` still had the round-3 file (272,797 bytes), same filename → overwrote. Live showed FIX-EH fields absent on rows resolved after deploy.
4. **Unique filename fix** (`worker-fixeh-20260807.js`) → downloaded fresh, verified 275,816 bytes → deployed → **live FIX-EH fields confirmed**.

## LIVE PROOF (rows resolved AFTER the FIX-EH deploy)

| Pair | Time | Dir | Result | entryHit (new) | entryHitLegacy (old) | Meaning |
|---|---|---|---|---|---|---|
| BTC/USD | 08:05 | SELL | LOSS | True | True | price re-tested entry (left below, returned) then fell → LOSS. Both metrics agree |
| ETH/USD | 08:10 | BUY | **WIN** | **False** | False | price moved up in favor, never returned → WIN. **Informative, non-tautological row** |
| BTC/USD | 08:20 | BUY | pending | — | — | (pre-trigger, resolving) |
| ETH/USD | 08:26 | BUY | pending | — | — | (pre-trigger, resolving) |

**Key:**
- `entryHitLegacy` field present on post-deploy resolved rows ✓
- Corrected `entryHit` now reflects **re-test semantics** (INSTANT: leave-then-return; PENDING: plain touch) ✓
- **The 100% MISS-WR tautology can no longer exist** — `entryHit=false` no longer implies WIN by construction; ETH 08:10 shows WIN+eh=false is an informative outcome, and a straight-down LOSS will now be eh=false/legacy=true (verified in local T33b + my independent repro).

## Cron
- `*/2` (result checker) + `*/5` (scanner) confirmed live (BTC/ETH rows resolving on schedule).

## NEXT (Phase F tracking with the corrected metric)
1. Let ~1-2 days of new history accumulate (rows after ~08:30 UTC 08-07 carry FIX-EH fields).
2. I'll re-run entry-hit analysis reading `entryHit` (corrected) vs `entryHitLegacy`:
   - **Expectation:** the tautology (MISS-WR 100%) disappears; `entryHit` correlates with something real (re-tests → worse outcomes near expiry).
   - **Watch:** if `entryHit=true` rows show low WR AND `entryHit=false` rows show high WR with the NEW semantics, that IS meaningful signal (re-test = danger) — a candidate Phase-F slice, NOT an artifact.
3. Daily snapshot + D4 ML continue unchanged.

## Notes
- Keep the unique filename convention for future deploys: `worker-<feature>-<date>.js` — avoids stale-file overwrite traps.
- `worker.js` and `worker-fixeh-20260807.js` both in workspace (identical MD5) — the unique one is the deployed artifact.
- Token rotation still pending from earlier (Cloudflare token leaked in chat): REVOKE + recreate if not done.
