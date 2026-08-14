# 🏁 START HERE — FTT Workspace (2026-08-14)

> এই ফাইলটা drive repo-র root-এ — **যেকোনো নতুন agent/session প্রথমে এটা পড়বে।**
> সব কাজের canonical record drive + GitHub-এ আছে।

## Canonical sources (সবচেয়ে গুরুত্বপূর্ণ)
1. **Journal + সব report:** এই repo-র `reports/`
   - `SESSION_JOURNAL_2026-08-14.md` ← পুরো session-এর history (শুরুতে এটা পড়ো)
2. **Worker code (canonical):** GitHub `ferdausfs/Ftt-Otc-v6` main (`cf7200e3`)
   - ⚠️ এই drive-র `worker/` mirror capsule-era snapshot — কোডের জন্য GitHub repo-ই truth
3. **Phase F data:** `data/phase_f_forward_2026-08-14.tar.gz` (unpack: `tar -xzf ... -C phase_f_forward`)
4. **PR materials:** `pr/`
5. **Baseline + analysis scripts:** `scripts/` (`phase_f_baseline.py`, `phase_f_analysis_2026-08-14.py`, `phase_f_deep_dive.py`, `verify_agents.py`)

## Live state (2026-08-14 শেষে)
- Worker **v6.10.2** live (`https://fttotcv6.umuhammadiswa.workers.dev/health`) — push fix + PENDING_ENTRY fill-correctness + cron fix
- Phase F verdict: breakeven 55.6% **NOT cleared** (forward 44.3%); round-3 improvement real (+6.7pp within-class)
- Merged PRs: #20 (schedules raw-array) · #21 (fill-correctness) · #22 (cron-string) — সব worker repo-তে

## Open items
- Stale PR #18 close (user): https://github.com/ferdausfs/Ftt-Otc-v6/pull/18
- আগামীকাল fresh Phase F snapshot → unfilled PENDING_ENTRY আর fake WIN হবে না (v6.10.2 fix)
- পরের engine change করলে: r71 re-baseline (`BASELINE_COMMIT` update)

## Rules (সংক্ষেপ — পুরোটা RULES.md-এ)
- PR-first, Worker = single source of truth, no invented data, no secrets in git/chat,
  local build ≠ deploy ≠ live verification, Phase F: data ছাড়া conclusion নেই।

## 4-agent review summary (এক লাইনে)
৪টা independent agent + reviewer = একই verdict: **breakeven clear হয়নি**; কোনো deployable edge নেই;
round-3 improvement real কিন্তু post 48.5% এখনো sub-breakeven। বিস্তারিত: `reports/PHASE_F_MULTIAGENT_REVIEW_2026-08-14.md`।
