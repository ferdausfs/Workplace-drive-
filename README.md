# 🏆 FTT SIGNAL ECOSYSTEM — FULL ARCHIVE (A to Z)
**Snapshot: 2026-08-09 · Built by Arena main agent · One repo, everything.**

> Ekta single repo-te sob kichu: 4 ta project code + Phase F data + scripts + reports + prompts + deployed bundles + runbook. Jekono AI agent shudhu ei repo clone/link diye puro context load korte parbe.

---

## 📂 STRUCTURE

| Folder | Ki ache |
|---|---|
| `worker/` | Ftt-Otc-v6 code (HEAD `7ed962a` — engine, OTC, D2, FX, FIX-EH) |
| `app/` | Ftt-app-002 code (HEAD `3d2e876` — modular React) |
| `bot/` | ftt-telegram-bot code (HEAD `8a65c5c` — v4.4.2, no-duplicate) |
| `my-zakat/` | My-zakat code (HEAD `dcc43f8`) |
| `data/` | `phase_f_forward_2026-08-09.tar.gz` — sob daily snapshot (08-02..09) |
| `scripts/` | Analysis pipeline (entryHit, day3, D4 ML) + deploy scripts + deriv test |
| `reports/` | Verification reports + Phase F analysis (17 md) |
| `prompts/` | Agent prompts + approval docs (23 md) |
| `bundles/` | Deployed artifacts: `worker-fixeh-20260807.js`, `bot-v442-20260808.js` |
| `runbook/` | `MASTER_RUNBOOK_2026-08-08.md` — full operating manual |

---

## 📖 A-TO-Z HISTORY (ki korlam, keno)

### Worker (Ftt-Otc-v6) — `worker/`
**v6.9.2 → rounds of fixes, all merged & live:**
- **R1 (PR#5):** BUG-001..008 — push ReferenceError (Telegram push never fired!), D2 AI-rescue bypass, fillStatus degenerate, report double-count, post-AI floor, tie convention, passAI.
- **R2 (PR#5):** OTC grade structure cap, camarilla 19% over-weight, dead round-number bonus, `/11`→`/12`.
- **R3 (PR#7):** 19 fixes F3-01..19 — channel mirror crash, OTC never-resolved, NO_TRADE grade N/A, AEST→UTC (candleTimes were +10h!), fx cache, BOS double-count, RSI zones, crypto session weights, AI skip on D2, rolling winRate...
- **F3-20 (PR#8):** r71 frozen-baseline refresh 113P/3F → 117P/0F.
- **FIX-EH (PR#9):** entryHit metric correction — old metric was a **tautology** (MISS WR = 100% guaranteed); new re-test semantics (shadow-only, `entryHit` + `entryHitLegacy`). Live: tautology dead.

### App (Ftt-app-002) — `app/`
- Modular refactor (`3d2e876`) — App.tsx 1911→486 lines.
- PR#4 (APP-001 grade chip + SignalHero cleanup) — **MERGED + LIVE** (2026-08-09).

### Bot (ftt-telegram-bot) — `bot/`
- Premium v4.3 + Arena hub menu (PR#3).
- PR#4 (v4.4.1): passGrade A+ drop + passAI dual-combiner + integration.
- PR#5 (v4.4.2, live): **duplicate signal fixed** (bot autoScan + worker push both sent; now worker push is single source) + **1042 permanent** (`global_fetch_strictly_public`).

### My-zakat — `my-zakat/`
- Firebase live, Google OAuth fixed, FTT theme.

### Phase F — `data/` + `reports/`
- Forward window 08-01 → 08-09 (day 9). Breakeven 55.6% @ 80% payout.
- WR trend: 42-43% (pre-R3) → 47.1% → 61.9% → 59.6% (post-R3, partial days, all crypto — gate NOT met).
- Corrected entryHit: tautology dead (eh-MISS 46.5%), no edge yet.
- D4 ML: no actionable edge. Rules: no inversion/pair-block/real-money until gate.

---

## 🚀 USE (jekono AI agent / device)

```bash
# clone everything
git clone https://github.com/<tumi>/ftt-all.git
# run analysis (data unpack)
mkdir -p phase_f_forward && tar -xzf data/phase_f_forward_2026-08-09.tar.gz -C phase_f_forward
python3 scripts/entryhit_corrected_analysis.py
python3 scripts/day3_analysis.py
python3 scripts/d4_run.py   # pip install pandas xgboost scikit-learn
# kono ekta file shudhu link diye
curl -s https://raw.githubusercontent.com/<tumi>/ftt-all/main/reports/PHASE_F_2026-08-09.md
```

## 🔁 DAILY UPDATE (Termux)
```bash
cd ~/ftt-all && bash scripts/daily-push.sh
# snapshot → analysis → report → tar data → commit → push (sob auto)
```

## ⚠️ RULES
- **Token/secret repo-te NA** (public repo) — oi gulo shudhu Termux env-e.
- Repo public → trading data thik, personal data na.
- Worker API 30-din TTL → **ei repo-i long-term archive**.
