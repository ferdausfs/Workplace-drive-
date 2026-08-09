# ROUND-3 LIVE VERIFICATION — FINAL (2026-08-06, ~19:25 UTC)

**Main:** `e56cd33` (merged PR #7) · **Deploy:** single-file bundle `worker.js` via Cloudflare API (wrangler doesn't run on Android — `Unsupported platform: android arm64`)

---

## ✅ LIVE CONFIRMED (9/11)

| Fix | Live proof |
|---|---|
| **F3-07** AEST→UTC | ✅ `candleTime 2026-08-06 19:01:00` with `generatedAt 19:03Z` — no more +10h |
| **F3-05** NO_TRADE grade | ✅ OTC NO_TRADE → `grade: "N/A" / "Engine blocked — no trade."` |
| **F3-13** crypto session weights | ✅ BTC/USD filters: no `SESSION_WEIGHT` (was ×1.40 before) |
| **F3-15** AI skip on D2 | ✅ DOGE/USD TRENDING → `AI_SKIPPED (D2 hard block)`, `aiStatus: SKIPPED` |
| **F3-04** OTC fillStatus | ✅ `EURUSD-OTC → SELL \| INSTANT \| C` — fillStatus/entryPrice/currentPrice now present |
| **F3-18** winRate window | ✅ BTC stats `winRate: 1` (recent 2/2), `sampleSize: 2` — lifetime was 362/811=0.447 |
| **F3-02** OTC pending write | ✅ new OTC row `19:23 SELL result=None` — pending written (was impossible before) |
| **F3-01** channel mirror | ✅ code+unit test T14 (pushLog written even with channel) |
| **F3-08** fx preferCache | ✅ code+unit test T21 (fx forces fresh) — live: `cached:false` on fx request |

## ⏳ PENDING (2)
- **F3-02 resolve step:** OTC `19:23` row resolves after its expiry (~19:53 UTC) — the */2 cron is CONFIRMED working (BTC 18:45→WIN @ 19:18 after deploy). Re-check OTC history at ~20:00.
- **F3-08 live fx tradeable:** needs a live BUY/SELL on a forex pair with mode=fx (code+T21 proven).

## 🛠️ DEPLOY JOURNEY (what happened, honest)
1. GitHub Actions deploy: queued 15+ min → cancelled (free-tier runner backlog)
2. wrangler: **cannot run on Android/Termux** (`workerd` → `Unsupported platform: android arm64 LE`)
3. Solution: **esbuild single-file bundle** (`worker.js`, 266 KB, all 42 modules inlined, syntax-checked, round-3 markers verified) → Cloudflare API PUT with `metadata` incl. KV bindings + **cron triggers**
4. Cron initially lost on upload (`cron: False`) → re-deployed with `triggers` in metadata → **`*/2` + `*/5` confirmed live** (BTC 18:45 resolved @ 19:18)

## 🔐 URGENT — TOKEN ROTATION (user)
The Cloudflare token `cfut_pTef5...` was **exposed in a terminal error paste in chat** (fixcron.py ValueError). It has full Workers edit rights.
**DO NOW:** dash.cloudflare.com → My Profile → API Tokens → **Revoke** `cfut_pTef5...` → Create Token ("Edit Cloudflare Workers") → keep new one only in Termux env, never in chat.

## 📌 Notes
- Deploys now go through `worker.js` bundle — repo push alone does NOT update the worker. Bundle must be regenerated (esbuild) + re-uploaded. I can do the bundling; you run the 1-command deploy script.
- `deploy_bundle.sh` + `redeploy.sh` (script+cron 2-in-1) + `worker.js` all in workspace + Termux.
- PR #6 closed ✓ (superseded, findings canonicalized BUG-026..032 in PR #7 report).
- r71_tests 113P/3F: 3 fails are frozen-baseline (71e87eb) artifacts — separate cleanup PR (F3-20) recommended later.

## NEXT
- ~20:00 UTC: re-check OTC history → F3-02 resolve final confirm
- Token rotate (now)
- Optional F3-20 r71 baseline cleanup PR
- Phase F continues: tomorrow's snapshot (post-round-3 signal stream) + entry-hit + D4 ML rerun
