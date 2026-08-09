# 🏆 FTT SIGNAL ECOSYSTEM — MASTER RUNBOOK & FULL HANDOVER
**v1.0 · 2026-08-08 · Written by the Arena main agent who ran this entire operation**

> **এই ফাইলটা তুমি যেকোনো নতুন agent-কে দাও — আমায় (Arena main agent) যেমন কাজ করতে দেখেছো, নতুন agent-ও ঠিক সেভাবেই কাজ করবে।**
> Agent instructions: read this file top-to-bottom. Everything you need to operate this ecosystem — repos, history, bugs, workflows, daily routine, deploy, security — is here. Ask the user for nothing except decisions only they can make.

---

# PART 0 — ROLE & MINDSET (সবচেয়ে গুরুত্বপূর্ণ)

**তুমি একজন INDEPENDENT REVIEWER / MAIN AGENT।** অন্য agent-রা কাজ করে, তুমি **ভেরিফাই** করো। তোমার identity: Arena.ai-র Agent Mode-এর main agent (কোনো specific model claim করবে না)।

**Never trust agent reports. NEVER.** Agent reports = raw material, NOT truth. Verify everything yourself:
- GitHub-এ code দেখো (HEAD, diff) — local clone-এর stale ref-এ নয়, **GitHub-এর actual HEAD** (`git ls-remote origin`, `git fetch`, API)
- Tests নিজে চালাও — agent-এর "all green" দাবি কখনো blind trust করবে না
- Live API hit করো — deploy সত্যিই হয়েছে কিনা
- Agent বললে "done" — GitHub-এ code না দেখলে সেটা empty claim

**Core rules (কখনো ভাঙবে না):**
1. **PR-first workflow:** agents branch → PR খোলে, কখনো main-এ direct push করে না। তুমি verify করার পর user merge করে। "agent mittha bolle bad de" — মিথ্যা বললে agent বাদ।
2. **Honesty:** কোন hype নেই, fake confidence নেই। ভুল হলে openly admit করো ("আমি ভুল ছিলাম, আমার fixture-ই ভুল ছিল")। Agent-এর প্রতিবেদনে ভুল পেলে সেটাও বলো।
3. **Phase F discipline:** engine behavior change → approval + forward evidence (7–14 দিন, ≥50 obs, ≥30/regime cell, CI vs 55.6% breakeven @ 80% payout)। No inversion, no pair block, no real-money recs। Data জমা ছাড়া conclusion নেই।
4. **Security:** user-এর token কখনো chat-এ চাইবে না। Chat-এ token আসলে সেটা REVOKE করতে বলো। Fine-grained, 7-day, single-repo tokens only।
5. **Language:** user বাংলা/বাংলিশে কথা বলে, "তুমি" বলে। বাংলায় উত্তর দাও (technical terms ইংরেজি থাকতে পারে)।

---

# PART 1 — THE ECOSYSTEM (3 repos + 1 side project)

| Component | Repo | Live URL | Worker name | Deploy path |
|---|---|---|---|---|
| **Worker** (signal engine) | `github.com/ferdausfs/Ftt-Otc-v6` | `https://fttotcv6.umuhammadiswa.workers.dev` | `fttotcv6` | **manual bundle** (GitHub Actions stuck) |
| **App** (frontend) | `github.com/ferdausfs/Ftt-app-002` | `https://fttfs-navy.vercel.app` | — | Vercel auto (main push) |
| **Bot** (Telegram) | `github.com/ferdausfs/ftt-telegram-bot` | `https://ftt-telegram-bot.umuhammadiswa.workers.dev` | `ftt-telegram-bot` | bundle/manual |
| My-zakat (side) | `github.com/ferdausfs/My-zakat` | `https://zakat-app-12c34.web.app` | — | Firebase |

**Current GitHub main HEADs (verify live before relying on this):**
- Worker: `7ed962a` (PR #9 FIX-EH merged) — **deployed live** via `worker-fixeh-20260807.js` bundle
- App: `3d2e876` (modular refactor) — **PR #4 (APP-001) verified, merge status = CHECK**
- Bot: `3570f37` (menu redesign) — **PR #4 (BUG-B1/B2) verified, merge status = CHECK**

**Cloudflare account ID:** `b3082da169faec70425179ca62500bc1`
**KV:** SIGNAL_CACHE `f553a3f10915478fa1b8165dd58ff6ea` · BOT_KV `39653d1f9b5147259cf3791658f131d7`
**Worker wrangler config:** name `fttotcv6`, main `src/index.js`, crons `*/2` (result checker) + `*/5` (scanner)

---

# PART 2 — FULL HISTORY: WHAT WE DID & WHY

## Round 0 (before this run): the stack was built
- Worker: weighted-vote signal engine (candles → indicators → per-TF votes → filters → AI validation → grade → push). Phases B/C/D added history tracking, D2 blocks, FX mode, OTC synthetic engine, ML prototype.
- App: single-file React app (later modularized).
- Bot: Telegram bot (menu, premium messages, auto-scan).

## Round 1 — Worker bugfix (PR #5, merged `0c6d358`)
A deep audit found 10 bugs. I verified 7 real + 3 not-actionable, then approved 6 fixes + 1 check:
- **BUG-001 (CRITICAL):** `saveAndPush` referenced `noPush` out of scope → ReferenceError → **Telegram push NEVER fired**. Fixed: thread `noPush` through. (phase10_integration was failing; now 19/19.)
- **BUG-002 (HIGH):** AI rescue path overrode D2 hard blocks (TRENDING/HIGHEST). Fixed: `d2Audit` → rescue skipped.
- **BUG-003 (HIGH):** fillStatus degenerate — entry & current price were the SAME value → always INSTANT. Fixed: current = lowest-TF last close.
- **BUG-005:** `/api/report` double-count. Fixed: idempotent.
- **BUG-007:** post-AI confidence floor not re-checked. Fixed.
- **BUG-008:** tie (exit==entry) counted as LOSS. Fixed: shared `classifyOutcome()` → TIE, excluded from stats/push.
- **CHECK-A (BUG-006):** `passAI` never matched the post-AI dual-combiner shape. Fixed.

## Round 2 — Worker bugfix (same PR #5, commit `2636250`, merged with R1)
Independent audit (Sonnet-5) findings — I verified all:
- **FIX-A (BUG-004 OTC):** OTC grade missing `structureVerdict.overall` → A+ even when structure AGAINST. Fixed → capped at C.
- **FIX-B (BUG-005 OTC):** camarilla stored RAW but OTC unweight-loop divided by 0.84 → ~19% over-weight. Fixed: skip `÷rW` for camarilla only.
- **FIX-C (BUG-007 OTC):** round-number bonus identical both sides → dead. Fixed: directional (below level → resistance/DOWN; above → support/UP).
- **FIX-D:** confluence denominators `/11` → `/12` everywhere.
- **HARDEN-1:** `structure.multiplier?.value` optional chaining.

## Round 3 — Worker bugfix (PR #7, merged `e56cd33`)
2 audit PRs (PR #6 & #7) collided on numbering (both BUG-011..016). I verified **all 22 findings real** (strongest audit so far — zero fabrication). Canonicalized + 19 fixes (F3-01..F3-19):
- **F3-01:** channel mirror `message` ReferenceError → pushLog never written. Fixed: per-subscriber message carried.
- **F3-02:** OTC never auto-resolved (result:null forever, `pending:9` live). Fixed: OTC rows get pending + resolve vs base-pair price.
- **F3-03:** passGrade drops A+ (worker copy). Fixed.
- **F3-04:** OTC missing fillStatus. Fixed (mirror engine.js).
- **F3-05:** NO_TRADE carried tradable grade ("B — Suitable for trading"). Fixed: grade `N/A / NO_TRADE`.
- **F3-06:** HTF hard block → confidence 0 → alignment bonus resurrected to 8%. Fixed: bonus before zeroing.
- **F3-07:** forex candleTime AEST (UTC+10) — live candleTimes 10h in the future! Fixed: `timezone=UTC` param.
- **F3-08:** `mode=fx&preferCache=true` returned non-FX payload. Fixed: fx forces fresh.
- **F3-09:** FVG penalty checked 1min first (noisy). Fixed: 15min first.
- **F3-10:** current-bar BOS double-counted (2.0+0.5=2.5). Fixed: recentEvents only when `!bos`. (Proven by my repro.)
- **F3-11:** RANGING RSI 55-65/35-45 contradictory trend-following bias. Fixed: removed (mean-reversion only).
- **F3-12:** +3 HIGHEST-session bonus dead (D2 block zeroes it). Removed.
- **F3-13:** crypto got forex session weights (USD quote ×1.4). Fixed: non-FOREX → 1.0.
- **F3-14:** scheduledScan called handleSignalRaw without noPush. Fixed.
- **F3-15:** 2 LLM calls (~8s) spent on D2-blocked signals then discarded. Fixed: `d2Audit → aiTargetDir = null`, `AI_SKIPPED`.
- **F3-16:** fixture tests time-of-day dependent (fail 12-16 UTC). Fixed: `opts.now/session/newsBlock` injection.
- **F3-17:** `/api/history` counted cbShadow rows, `/api/stats` didn't. Fixed: history excludes them.
- **F3-18:** winRate all-time vs documented 20-lookback. Fixed: rolling 20-trade window.
- **F3-19:** decideTfDirection fallback bypassed MIN_CONFLUENCE=5 (used 4). Fixed: winning-side confluence.

## F3-20 — Worker test-infra (PR #8, merged `7b38185`)
r71_tests had **3 pre-existing fails (#1a/#2/#17)** — NOT product bugs, but a stale frozen baseline (`git archive 71e87eb`, the pre-round-1 engine). Fixed: `BASELINE_COMMIT = e56cd33` + self-healing bootstrap + anti-rot check. **r71: 113P/3F → 117P/0F.**

## FIX-EH — Worker entryHit correction (PR #9, merged `7ed962a`, LIVE)
**The big discovery (my analysis):** entryHit metric was **mathematically tautological**:
```
LOSS ⟹ price ends past entry ⟹ expiry±5min window low/high always satisfies ⟹ entryHit=true (guaranteed)
WIN ⟹ price moved away ⟹ entryHit=false (almost always)
```
Live proof: MISS WR = **100.0% on 08-05/06/07 (3/3 days)** — exactly what my 200k-row fair-coin simulation predicted. So "signals whose entry wasn't hit always win" was an artifact, NOT signal quality.
**Fix:** window [signalTime → expiry] + **re-test semantics** — INSTANT: price must LEAVE entry in favor then RETURN (straight-down LOSS is NOT a hit); PENDING_ENTRY: plain touch. `entryHit` (corrected) + `entryHitLegacy` (old, kept for comparison).
**Verified live:** eh-MISS WR dropped from 100% → 58.3% (n=271 rows). Tautology dead.

## App (Ftt-app-002)
- Modular refactor merged (`3d2e876`): App.tsx 1911→486 lines, split into lib/hooks/components. tsc 0, build clean.
- Chips (Mode/Fill/SL-TP) — user confirmed "he hoyese" (works now).
- **PR #4 (verified, merge pending):** APP-001 grade chip gray for N/A + deleted orphan SignalHero.tsx.

## Bot (ftt-telegram-bot)
- Premium messages v4.3 (`38dda66`) + Arena hub menu 2×3 grid (PR #3 `3570f37`) merged, live.
- **PR #4 (verified, merge pending):** BUG-B1 passGrade A+ drop (bot's own copy of worker F3-03) + BUG-B2 passAI dead with dual-combiner (bot's own copy of worker CHECK-A — AI-Only mode never matched) + integration fixes in fmtSignal/doAnalyze. 35/35 tests.

## My-zakat (side)
- Firebase live, Google OAuth fixed, FTT-style theme applied. Not active recently.

---

# PART 3 — BUG INVENTORY (canonical)

**Worker canonical IDs (BUG_REPORT.md in repo):** BUG-001..010 (rounds 1-2) · BUG-011..025 (PR#7 audit) · BUG-026..032 = PR#6's findings (canonicalized: 026=passGrade, 027=OTC fillStatus, 028=scanner noPush, 029=BOS double-count, 030=RSI zones, 031=FVG order, CLOCK-001=BUG-022).

**Status:**
- All BUG-001..008 fixed (R1+R2) · BUG-011..025 fixed (R3, all 19) · F3-20 fixed · FIX-EH fixed.
- **Still open (analysis-only / Phase-F, do NOT "fix" with code):**
  - BUG-023 entryHit — now FIX-EH corrected; continue tracking corrected metric.
  - BUG-024 forex SELL weakness — probe monitoring; no logic flip.
  - Finding #3 (round-2 audit): D2_TRENDING_BLOCK pair-agnostic vs bad-pair suspension — **user Phase-F decision needed** (shadow obs counting acceptable? probe for TRENDING cells?).
  - r71 baseline — done (F3-20). Re-baseline again after next engine change.

---

# PART 4 — PHASE F STATUS (as of 2026-08-08)

**Forward window:** 08-01 → 08-08 (day 7). Snapshots in `~/phase_f_forward/<date>/` (18 pairs, http=200, MANIFEST + SHA256SUMS).

**Overall WR trend (decided, by day):**
| Day | WR | Note |
|---|---|---|
| 08-01..04 | 42-43% | pre-round-3 |
| 08-05 | 39.2% | |
| 08-06 | 45.3% | round-3 deployed ~19:00 UTC |
| 08-07 | 47.1% | first full post-round-3 day |
| 08-08 (partial) | **61.9% (63)** | above breakeven — partial, all-crypto, BUY-heavy ⚠️ |

**Breakeven = 55.6% (80% payout).** Phase F gate: ≥50 obs ✓, ≥30/regime cell, 7-14 days, CI vs 55.6%.

**Corrected entryHit (FIX-EH) n=271:** eh-HIT WR 48.4% (CI 42-55) vs eh-MISS 58.3% (CI 44.3-71.2) — CIs overlap, provisional. Tautology dead ✓.

**D4 ML:** no actionable edge yet. LEGIT WIN-call 68.8% (n=16, CI 44.4-85.8) — ambiguous. LEAKAGE diagnostic no longer 100% (confirms FIX-EH works).

**Key slices to watch:** BUY 68% vs SELL 38.5% (08-08 partial) — SELL weakness echoes BUG-024. Crypto strong (SOL 91.7%, XRP 77.8%, DOT 83.3% on tiny n).

**Rules:** no inversion, no pair-block, no real-money recs until gate met. If WR ≥ 55% holds 2-3 more days WITH forex included → slice-level investigation.

---

# PART 5 — DAILY ROUTINE (every UTC day)

1. **Snapshot** (once per real UTC day):
   ```bash
   cd ~ && bash phase_f_snapshot.sh    # creates ~/phase_f_forward/<UTC-DATE>/
   ```
2. **Corrected entry-hit analysis** (after ≥08-07 data):
   ```bash
   python3 entryhit_corrected_analysis.py
   ```
3. **Signal WR + slices:**
   ```bash
   python3 day3_analysis.py   # (or update date filter)
   ```
4. **D4 ML rerun:**
   ```bash
   python3 d4_run.py    # pip install xgboost if missing (env resets per session)
   ```
5. **Report** to user in Bangla: WR trend, entryHit, D4, honest read, no premature conclusions.

---

# PART 6 — DEPLOY RUNBOOK (worker)

**GitHub Actions CI is unreliable** (free-tier queue stuck for hours). **Manual bundle deploy is the way.**

1. **I (main agent) build the bundle:**
   ```bash
   git worktree add /tmp/bundle origin/main
   cd /tmp/bundle && npm i esbuild && ./node_modules/.bin/esbuild src/index.js --bundle --format=esm --target=es2022 --outfile=worker.js
   node --check worker.js
   grep -c "<feature-marker>" worker.js   # verify feature present
   ```
2. **Save with UNIQUE filename:** `worker-<feature>-<date>.js` (e.g. `worker-fixeh-20260807.js`). ⚠️ **Lesson learned:** same filename `worker.js` caused a stale-file overwrite (round-3 file deployed twice; FIX-EH not live until unique name used).
3. **User deploys from Termux:**
   ```bash
   cd ~/Ftt-Otc-v6 && cp ~/storage/downloads/worker-fixeh-20260807.js ./ && bash redeploy.sh
   ```
   `redeploy.sh` = curl PUT with metadata (main_module + KV bindings + **triggers/crons in metadata** — else cron lost!) + token hidden input. Verify bytes: `ls -la` must show the NEW size (e.g. 275816 not 272797).
4. **I verify live:** health, candleTime UTC, feature markers in fresh responses, cron resolving (checkedAt advancing).

---

# PART 7 — SECURITY (critical)

- **NEVER ask for tokens in chat.** Tokens in chat = REVOKE immediately.
- **History of leaks:** 2 GitHub PATs (user revoked — I verified 401 on both ✓). 1 Cloudflare token `cfut_pTef5...` (leaked in a terminal error paste — **rotation recommended, verify status**).
- Token usage: Termux env or hidden `read -rs` input only.
- GitHub fine-grained PATs: 7-day, single-repo, minimal scopes.
- Leaked-token check: `curl -H "Authorization: Bearer <tok>" https://api.github.com/user` → 401 = revoked ✓.
- Cloudflare token check: `GET /user/tokens/verify` → active; `GET /accounts/<id>/workers/scripts` → permission check (if Authentication error → token lacks Workers Scripts permission → recreate with "Edit Cloudflare Workers" template).

---

# PART 8 — WORKFLOW WITH USER (exact operating model)

1. User gives you agent reports / pasted content → **verify independently** (GitHub HEAD, code, tests, live API) → verdict: CONFIRMED / PARTIAL / OVERSTATED with proof.
2. For fixes: I write **approval docs** (`WORKER_BUGFIX_ROUND3_APPROVAL.md` style) + **agent prompts** (`WORKER_ROUND3_AGENT_PROMPT.md` style) — exact file/line/spec/test requirements. Agent works PR-first.
3. Agent pushes PR → I re-verify: diff read, all suites run by ME, independent repros, live checks → **approve for merge** → USER merges (I have no write access; that's by design).
4. After merge → deploy (bundle) → live verify.
5. Phase F data → daily analysis → honest report in Bangla.

---

# PART 9 — TEST SUITES (worker) — ALWAYS RUN

```
scripts/fix_tests.mjs          158/158  (T1-T33, incl. FIX-EH re-test semantics)
scripts/phase10_integration.mjs 19/19   (push works — was failing pre-BUG-001)
scripts/phase10_smoke.mjs       61/61
scripts/phase7_integration.mjs  36/36 · phase7_smoke 68/68
scripts/d2_tests.mjs            39/39 · probe_tests 34/34
scripts/entry_hit_tests.mjs      7/7  · fx_mode_tests 20/20
scripts/r71_tests.mjs          117P/0F (frozen-baseline guard, BASELINE_COMMIT=e56cd33)
```
`r71_tests` needs `git fetch --unshallow` (baseline commit must exist locally). node --check all src; `git diff --check` clean.

---

# PART 10 — WORKSPACE FILES (reference)

**Scripts:** `phase_f_snapshot.sh` · `phase_f_prefill.py` · `entryhit_corrected_analysis.py` · `day3_analysis.py` · `entry_hit_analysis.py` · `d4_run.py` · `screenshot_analyzer.py`
**Prompts/approvals:** `WORKER_BUGFIX_APPROVAL.md` (R1) · `WORKER_BUGFIX_ROUND2_APPROVAL.md` · `WORKER_ROUND3_AGENT_PROMPT.md` · `PROMPT_WORKER_R4.md` (F3-20) · `PROMPT_WORKER_FIX_EH.md` · `PROMPT_APP_R1.md` · `PROMPT_BOT_R2.md`
**Reports:** `PR5_FINAL_VERIFICATION_2026-08-06.md` · `ROUND3_FINAL_VERIFICATION_2026-08-06.md` · `ROUND3_MERGE_VERIFY_2026-08-06.md` · `3PR_VERIFICATION_2026-08-07.md` · `FIX_EH_VERIFICATION_2026-08-07.md` · `FIX_EH_LIVE_2026-08-07.md` · `PHASE_F_DAY2/DAY3_*.md` · `PHASE_F_2026-08-08.md` · `D4_ML_2026-08-06.md`
**Deploy:** `worker.js` (current bundle) · `worker-fixeh-20260807.js` (deployed artifact, 275816 B, MD5 899d4fb9...) · `redeploy.sh` (script+cron) · `deploy_bundle.sh` · `termux_cf_deploy.sh` (bot)
**Bundles (git):** `<proj>-<update>-v<N>-<date>.bundle` — always `git bundle verify` in fresh clone before shipping.

---

# PART 11 — OPEN ITEMS (verify on first day)

1. **App PR #4** (APP-001 + SignalHero) — verified approved, merge status = CHECK → merge → Vercel auto-deploy → live check.
2. **Bot PR #4** (BUG-B1/B2) — verified approved, merge status = CHECK → merge → deploy bot bundle → live check (v4.4.1, A+ grade + AI-Only working).
3. **Cloudflare token rotation** — `cfut_pTef5...` leaked; confirm revoked/recreated.
4. **Phase F daily routine** — snapshot 08-09+ , corrected entryHit, D4, WR trend.
5. **Finding #3 (D2 TRENDING vs bad-pair data collection)** — needs user decision.
6. **Forex SELL** — keep probe monitoring; no flip without Phase F evidence.
7. **entryHit corrected** as D4 feature once ≥2-3 days of train rows carry it.
8. If WR ≥ 55.6% holds with forex + full days → slice-level investigation (which pairs/regimes improved post-round-3) — still no blanket changes.

---

# FINAL WORD FOR THE NEW AGENT

> User বলেছে: "তুমি verify করবে", "PR করবে, push না", "app যেন নষ্ট না হয়", "agent মিথ্যা বললে বাদ"।
> সব সময়: code পড়ো → test চালাও → live check করো → তারপর বলো। Agent-এর report-এ কিছুই assume করবে না। বাংলায় honest report দাও, hype নেই। Data ছাড়া conclusion নেই (Phase F)। Token chat-এ নেই। Deploy bundle + unique filename। এই runbook-এর বাইরে কিছু করলে — PR-first, verify করাও, user-কে জিজ্ঞেস করো।
