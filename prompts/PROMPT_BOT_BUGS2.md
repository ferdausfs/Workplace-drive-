# BOT (ftt-telegram-bot) — AGENT PROMPT (bug-fix round 2: duplicate signals + permanent 1042 fix)

**Repo:** `ferdausfs/ftt-telegram-bot` · **Main HEAD:** `872b61c` (PR #4 merged, live v4.4.1)
**Reviewer:** Arena main agent — I verify everything on GitHub + live after you push. No "done" claims until code is on a branch.

---

## CONTEXT (reviewer-verified 2026-08-08)

1. **Worker push is now WORKING.** Worker BUG-001 (push never fired) was fixed in round 1; `phase10_integration.mjs` = 19/19; live: worker `*/2` cron pushes signals + results to subscribers (verified: BTC row resolved + pushLog written). Worker also has its own dedup (`claimPushLock`, 30-min lock, pushLog per signal).
2. **BUT the bot's `cronLite` (scheduled handler) ALSO runs `autoScan`**, which independently fetches signals and **pushes its own Telegram messages** (comment says "worker push alone was not delivering reliably" — that was BEFORE the BUG-001 fix). Result: **users get the SAME signal twice — once from worker push, once from bot autoScan.**
3. **Deploy-side 1042 issue:** bot wrangler.toml lacks `compatibility_flags = ["global_fetch_strictly_public"]` → bot→worker fetch (service binding `SIGNAL_WORKER`) fails with Cloudflare `error 1042`. I fixed it at runtime via the Cloudflare API (flag + binding set on the deployed worker), but **the repo must carry the fix** or any future GitHub-Actions deploy regresses it.

## BUG-B3 (High) — duplicate signal pushes: bot autoScan + worker push both send

**Root cause:** two independent push paths to the same Telegram users:
- **Worker:** `*/2` cron → `pushSignalToSubscribers` (signal.js → engine → pushToSubscribers.js) → sendMessage to all matching subscribers. Has `claimPushLock` + pushLog dedup.
- **Bot:** `*/5` cron → `cronLite` → `autoScan` (src/index.js:1973) → `fetchSig` → `sendMsg(cid, fmtSignal(...))` per user per pair. Has its own same-candle + lock dedup, but **it is a SECOND sender**.

**Fix (choose + justify in PR):**
- **Option A (recommended):** bot autoScan should NOT push signals — worker push is the single source. In `autoScan`, keep the fetch/log/analytics (result tracking, `logAndSchedule`, KV bookkeeping) but **remove the `sendMsg` signal sends** (lines ~2075-2090 in the current main: the `fmtSignal` + `Custom Alert` sends). Then autoScan only maintains bot-side analytics (`lc:`, `sc:`, locks, `logAndSchedule`) and worker push delivers the message. The custom-alert feature (`getAlerts`) also moves to worker push if it must live (or is dropped with a note) — **decide and document.**
- **Option B:** keep bot autoScan, but gate it so it only pushes when worker push is disabled (env flag e.g. `DISABLE_WORKER_PUSH`). More moving parts; only pick if A breaks something you can prove.
- ⚠️ Whatever you pick: **do not remove `resultCheck`/`expiryReminder`/`dailySummary`/`weeklyReport`** — those are bot-only analytics, no worker equivalent.

**Proof required:** after your change, a single signal for a user results in exactly ONE Telegram message (worker push). Test: mock autoScan path — assert no `sendMsg(fmtSignal(...))` remains in autoScan (Option A) or is gated (Option B); assert `logAndSchedule`/KV bookkeeping still runs.

## BUG-B4 (Med) — permanent 1042 fix in repo

**Fix:** `wrangler.toml`:
```toml
name = "ftt-telegram-bot"
main = "src/index.js"
compatibility_date = "2024-01-01"
compatibility_flags = ["global_fetch_strictly_public"]
```
(keep the existing `[triggers]`, `[[kv_namespaces]] BOT_KV`, `[[services]] SIGNAL_WORKER → fttotcv6` exactly as-is — the deployed worker already has these bindings; the repo must match so GitHub-Actions deploys keep them + the flag.)

**Proof:** wrangler.toml shows the flag; if the repo has a `.github/workflows/deploy.yml` that deploys via wrangler, confirm it would carry the flag (wrangler reads wrangler.toml).

## ALSO — verify (report findings, don't assume)
1. **Bot pushLog interplay:** after BUG-B3, does the bot still write any pushLog/analytics the worker's `pushResultToSubscribers` depends on? Worker reads pushLog from ITS KV (SIGNAL_CACHE) — bot writes to BOT_KV. Confirm they don't collide.
2. **Custom Alerts (F09):** if you drop them from autoScan (Option A), the `/alerts` UI + `getAlerts` become dead for signal delivery — either wire them into worker push (worker's `pushToSubscribers` would need alert thresholds — flag this as a separate PR) or remove the dead UI. **Do not silently leave a half-working feature.**
3. **No new duplication:** search for other `sendMsg(.*fmtSignal` call sites (lines ~1515, 1560, 1601 are `doSignal`/watchlist manual triggers — those are FINE, user-initiated). Only autoScan's cron-driven sends must go.

## TESTS — run all, show output
- Bot: `node --check src/index.js` + `round2-bugfix-test.mjs` (35/35) + your new BUG-B3/B4 asserts (add to the test file).
- Worker untouched — do not touch Ftt-Otc-v6 from here.

## WORKFLOW
1. PR-first off `main` (`872b61c`), never push main directly.
2. PR body: root-cause recap, fix choice (A/B) + justification, custom-alert decision, test matrix, wrangler.toml diff.
3. After you push: I re-verify (diff, run tests, live-check after merge+deploy: exactly one signal per trigger).

## AFTER MERGE (deploy note)
- Bot deploy is manual bundle (like worker): I rebuild `bot.js` from new main, you run `bash bot_deploy2.sh` (SIGNAL_WORKER binding + `global_fetch_strictly_public` in metadata). Then I verify: no duplicate signals live.
- GitHub Actions bot deploy also works (`872b61c` deployed successfully) — but it reads wrangler.toml, so the BUG-B4 flag addition is what makes future CI deploys correct.
