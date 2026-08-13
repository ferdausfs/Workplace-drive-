# WORKER v6.10.1 — what shipped (reconstructed archive)

**Original viewer prompt was never committed** (`<prompt content — viewer theke copy>`). This file archives the **actual** change that landed, verified against GitHub `ferdausfs/Ftt-Otc-v6` main `cd3dc08` (PR #19, merged 2026-08-12 09:43Z).

Source of truth for the writeup: worker `AGENT_LOG.md` (2026-08-12 entries) + bot `patches/PUSH_SILENT_DEATH_REPORT.md` + PR #19 files.

---

## Problem (live, 2026-08-12 ~06:47Z)

`/health` on v6.10.0: `pushEnabled=true`, `botKvBound=true`, `subscriberCount=1`, **`pushesLast24h=0`**. Scanner still saved tradeable rows (ADA/USD pending SELL, no `pushLog`). Users got manual `/api/signal` cards, not worker auto-push.

## Root causes (code, not guesses)

1. `claimPushLock` ran **before** `sendTelegramMessage`. 401/403 held the 30-min lock, wrote no pushLog → every later tick `skipped:'locked'`.
2. `pushesLast24h` counted open `pushLog:*` keys. Result-push **deletes** those keys → a healthy push+resolve day also shows 0.
3. Nested `waitUntil` on `*/5` (`scheduled` wraps scan, scan wraps saveAndPush) — isolate could freeze after fast KV save, before Telegram.
4. `!!BOT_TOKEN` treated whitespace / wrong-bot secrets as enabled. `/health` never called `getMe`.

## Fix (worker only — bot v4.5.0 untouched)

| # | Change |
|---|---|
| 1 | Release pushLock on Telegram send failure |
| 2 | Persist `push:lastAttempt` on every terminal outcome + per-sub skip reasons |
| 3 | Durable `push:delivered24h` KV ring (survives result-push) |
| 4 | `/health.push = {enabled, noTokenReason, tokenValid (cached getMe), tokenUsername, lastAttempt, subscribers[], delivered24h}` |
| 5 | `await scheduledScan` + scanner `awaitPersist:true` |
| 6 | `normalizeAutoUsers` + `botToken().trim()` |

Plus `scripts/redeploy.sh`: bundle preflight, quoted multipart, raw HTTP body on every Cloudflare call, `wmeta.json` `main_module` check, post-deploy `/health` verify. No more silent `JSONDecodeError`.

## Files (PR #19)

`src/index.js` · `src/handlers/{health,pushToSubscribers,scheduledScan,signal}.js` · `scripts/{fix_tests,phase10_smoke,redeploy}.sh|mjs` · `AGENT_LOG.md`

## Tests (re-run on this drive snapshot 2026-08-13)

fix_tests **304/0** (T43a–j) · phase10_integration 19/19 · phase10_smoke 71/0 · phase7 68+36 · d2 39 · probe 34 · eh 7 · fx 20.

## Deploy (still manual)

GitHub Action on `cd3dc08` **failed** (same as every recent main push). Live version was **not** verified from this sandbox (TLS to workers.dev fails).

```bash
cd Ftt-Otc-v6
# unique filename — do not overwrite worker.js
# then:
bash scripts/redeploy.sh
# expect /health version=6.10.1 and push.tokenValid=true
```

## Not in scope

- No engine / grade / pair-block change.
- No bot v4.5.0 behaviour change.
- Gates (pair / watchlist / grade / conf / AI) unchanged.
