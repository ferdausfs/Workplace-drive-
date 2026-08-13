# 🏆 FTT SIGNAL ECOSYSTEM — FULL ARCHIVE (A to Z)
**Snapshot: 2026-08-13 · Independent re-verify by Arena drive session · One repo, everything.**

> Ekta single repo-te sob kichu: 4 ta project code + Phase F data + scripts + reports + prompts + deployed bundles + runbook. Jekono AI agent shudhu ei repo clone/link diye puro context load korte parbe.

---

## 📂 STRUCTURE

| Folder | Ki ache |
|---|---|
| `worker/` | Ftt-Otc-v6 snapshot — **main `cd3dc08` · v6.10.1** (push silent-death + redeploy.sh diagnostics) |
| `app/` | Ftt-app-002 snapshot — **main `af9bf22`** (modular React + APP-001 + WORKSPACE_DRIVE pointer) |
| `bot/` | ftt-telegram-bot snapshot — **main `2555d20` · v4.5.0** (worker = single source) + v6.10.1 patch archive |
| `my-zakat/` | My-zakat snapshot — **main `dca5ca8`** |
| `data/` | `phase_f_forward_FULL_2026-08-12.tar.gz` — 08-01..12 (+ earlier recovery days) |
| `scripts/` | Analysis pipeline (entryHit, day3, D4, **full_forward_analysis**) + deploy scripts |
| `reports/` | Verification + Phase F analysis |
| `prompts/` | Agent prompts + approval docs |
| `bundles/` | Older deployed artifacts (`worker-fixeh-20260807.js`, `bot-v442-20260808.js`) — **not v6.10.1** |
| `runbook/` | `MASTER_RUNBOOK_2026-08-08.md` + `STATUS_2026-08-13.md` |

---

## ✅ CURRENT HEADS (verified on GitHub 2026-08-13)

| Component | Repo | main HEAD | Live URL | Deploy |
|---|---|---|---|---|
| Worker | `ferdausfs/Ftt-Otc-v6` | `cd3dc08` (PR #19, v6.10.1) | `https://fttotcv6.umuhammadiswa.workers.dev` | GitHub Action **FAILS** (every recent main push). Manual `scripts/redeploy.sh`. |
| App | `ferdausfs/Ftt-app-002` | `af9bf22` | `https://fttfs-navy.vercel.app` | Vercel auto |
| Bot | `ferdausfs/ftt-telegram-bot` | `2555d20` (PR #12) | `https://ftt-telegram-bot.umuhammadiswa.workers.dev` | Action **FAILS**. Manual bundle. |
| Zakat | `ferdausfs/My-zakat` | `dca5ca8` | `https://zakat-app-12c34.web.app` | Firebase |

**This sandbox cannot TLS-handshake `*.workers.dev` / Vercel / Firebase** (`SSL_ERROR_SYSCALL`). Live `/health` version is **NOT** re-verified here. Last archived health (`phase_f_forward/2026-08-12/health.json`, 05:26Z) = **v6.10.0**. PR #19 merged 09:43Z the same day — live v6.10.1 needs a Termux `redeploy.sh` + `/health.version == "6.10.1"` check.

Open leftover: **Ftt-Otc-v6 PR #18** (`arena/019ff51d-…`, `mergeable_state=dirty`) is a superseded twin of #19. Close it.

---

## 📖 A-TO-Z HISTORY (ki korlam, keno)

### Worker (Ftt-Otc-v6) — `worker/`
**v6.9.2 → v6.10.1, merged on GitHub:**
- **R1 (PR#5):** BUG-001..008 — push ReferenceError, D2 AI-rescue bypass, fillStatus, report double-count, post-AI floor, tie convention, passAI.
- **R2 (PR#5):** OTC grade structure cap, camarilla 19% over-weight, dead round-number bonus, `/11`→`/12`.
- **R3 (PR#7):** 19 fixes F3-01..19 — channel mirror crash, OTC never-resolved, NO_TRADE grade N/A, AEST→UTC, fx cache, BOS double-count, RSI zones, crypto session weights, AI skip on D2, rolling winRate...
- **F3-20 (PR#8):** r71 frozen-baseline refresh 113P/3F → 117P/0F.
- **FIX-EH (PR#9):** entryHit tautology killed (re-test semantics). Confirmed on archive: legacy-MISS WR still 100%; eh-MISS WR **51.0%**.
- **Calibration (PR#10) + signalIndicators (PR#13) + edge features (PR#15):** hour/RSI/BB/ATR/session-range/recent-form + weekly self-calib. Live as v6.10.0.
- **Auto-push restore (PR#17):** scanner `noPush` dropped after bot v4.5 killed autoScan. Version **v6.10.0**.
- **v6.10.1 (PR#19, 2026-08-12):** silent Telegram death — lock released on send-fail, durable `push:delivered24h`, `/health.push` + cached `getMe`, `await scheduledScan`, `redeploy.sh` no longer swallows Cloudflare errors.

### App (Ftt-app-002) — `app/`
- Modular refactor (`3d2e876`) — App.tsx 1911→486 lines.
- PR#4 (APP-001 grade chip + SignalHero cleanup) — **MERGED** (`5a9f1fa` / pointer `af9bf22`).

### Bot (ftt-telegram-bot) — `bot/`
- Premium v4.3 + Arena hub menu.
- v4.4.2: no-duplicate (worker = push source) + 1042 permanent.
- **v4.5.0 (PR#7):** worker = single source of truth — bot ledger/autoScan deleted.
- **PR#12:** v6.10.1 worker patch + evidence report shipped here first (worker-repo write was 403 that session), then landed as worker PR#19.

### My-zakat — `my-zakat/`
- Firebase live, Google OAuth fixed, FTT theme.

### Phase F — `data/` + `reports/`
- Forward window 08-01 → 08-12 (day 12). Breakeven **55.6% @ 80% payout**.
- **Independent re-run 2026-08-13** (`scripts/full_forward_analysis.py` on the FULL archive):
  - Pooled decided **n=3883 WR=43.5% CI[42.0–45.1] — BELOW_BE**.
  - CRYPTO 45.0% (3417) · FOREX **32.6% (466)** · BUY 41.3% · SELL 45.6%.
  - FOREX both sides bad: BUY 29.0% / SELL 36.7%. All 4 majors 29–35%.
  - Post-v6.10 (08-10..12): **42.6% (336)** — no lift vs pool.
  - Corrected entryHit: eh-HIT 46.0% vs eh-MISS 51.0% (CI overlap, no edge). Tautology dead.
- Gate: **not met**. No inversion, no pair-block, no real-money recs.

---

## 🧪 SNAPSHOT TESTS (run on this drive, 2026-08-13)

| Suite | Result |
|---|---|
| worker `node --check src/index.js` | pass |
| worker `fix_tests` | **304/0** |
| worker `phase10_integration` | 19/19 |
| worker `phase10_smoke` | 71/0 |
| worker `phase7_smoke` / `phase7_integration` | 68/0 · 36/0 |
| worker `d2` / `probe` / `entry_hit` / `fx_mode` | 39 · 34 · 7 · 20 |
| worker `r71_tests` | **not runnable in snapshot** (needs `git archive <baseline>` — no `.git` inside `worker/`) |
| bot `round2` / `menu` / `single-source` | 60 · 74 · 72 |

---

## 🚀 USE (jekono AI agent / device)

```bash
git clone https://github.com/ferdausfs/Workplace-drive-.git
mkdir -p phase_f_forward && tar -xzf data/phase_f_forward_FULL_2026-08-12.tar.gz -C .
python3 scripts/entryhit_corrected_analysis.py
python3 scripts/full_forward_analysis.py
python3 scripts/d4_run.py   # pip install pandas xgboost scikit-learn
```

## 🔁 DAILY UPDATE (Termux)
```bash
cd ~/Workplace-drive- && bash scripts/daily-push.sh
# snapshot → analysis → report → tar data → commit → push
```

## ⚠️ RULES
- **Token/secret repo-te NA** (public repo) — oi gulo shudhu Termux env-e.
- Repo public → trading data thik, personal data na.
- Worker API 30-din TTL → **ei repo-i long-term archive**.
- See `RULES.md` + `runbook/STATUS_2026-08-13.md`.
