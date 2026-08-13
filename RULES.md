# 📜 RULES — FTT WORKSPACE DRIVE (operating manual)

**Effective:** 2026-08-09 · Last status refresh: 2026-08-13 · Owner: ferdausfs + Arena main agent (independent reviewer)

---

## RULE 1 — Drive repo = source of truth
`Workplace-drive-` (https://github.com/ferdausfs/Workplace-drive-) holds **sob kichu**: 4 project code snapshots, Phase F data, scripts, reports, prompts, bundles, runbook. Kono file/knowledge shudhu local-e thakbe na.

## RULE 2 — Proti ta kaj drive-te push hobe (AGAGE) — SAB AGENT-ER JONNO
**Ei rule shudhu Arena main agent-r jonno na — PROTITA agent (worker/app/bot/analysis) er jonno BINDING.** Jekono repo-te kono kaj korle — update/result/report/change/PR/analysis aslei — **age drive (`Workplace-drive-`) te update koro, tarpor kaj aage**. Snapshot, analysis, report, script, prompt, bundle, kono file → drive-te push. Daily: `bash scripts/daily-push.sh` (snapshot → analysis → report → push auto).

**File + Command niyom (push ba update korte hole):**
- Main agent **file + command shoho debe** (heredoc/direct), user shudhu paste + run korbe.
- User push korar por main agent **drive pull kore verify korbe** (file asche kina + content thik kina).
- Kono file drive-te na gele → **context miss** → oita push kore kaj aage.
- Agent jodi kichu push kore thakeo main agent nije verify kore — blind trust nai (RULE-5).

## RULE 3 — Context check proti turn
Arena main agent **proti turn-e drive repo check korbe** (`git pull` / API list):
- Kono notun push/update thakle → tar sathe kaj miliye nibe.
- **Context miss** thakle (kono file/data ami dekhini) → **oita drive-te push kore** tarpor kaj aage nibe.
- Miss kichhu thakle user-ke honest report: "ei jinis miss chilo, ekhon push korlam".

## RULE 4 — Code change = PR-first (project repos)
`worker/`, `app/`, `bot/`, `my-zakat/` **project repos**-e kono code change **PR-first** (branch → PR → reviewer verify → user merge). Drive repo-te **docs/data/snapshots** update allowed (PR lagbe na on the drive itself; Arena session branch + PR is fine).

Drive `worker/` `app/` `bot/` folders are **snapshots**, not the live project repos. Engine changes go to `ferdausfs/Ftt-Otc-v6` first, then the snapshot is refreshed here.

## RULE 5 — Verification (kono blind trust nai)
Agent report = raw material. GitHub HEAD + code + tests + live API — sob nije check. Test suite expected counts (v6.10.1 snapshot, 2026-08-13):
- worker: `fix_tests` **304/0** · `phase10_integration` 19/19 · `phase10_smoke` 71/0 · `phase7` 68+36 · `d2` 39 · `probe` 34 · `eh` 7 · `fx` 20
- worker `r71_tests` 117P/0F — **only inside a real git clone** of Ftt-Otc-v6 (needs `git archive` baseline). Drive snapshot has no `.git`.
- bot: `round2-bugfix-test` 60/60 · `menu-test` 74/74 · `single-source-test` 72/72
- app: `tsc --noEmit` clean · `vite build` clean (not re-run this session)

## RULE 6 — Phase F discipline
Breakeven 55.6% (80% payout). Gate: ≥50 obs, ≥30/regime cell, 7–14 days, **CI-low vs 55.6%**. **No inversion, no pair block, no real-money recs until gate.**

As of the 08-01..12 archive: pooled WR **43.5% (n=3883, CI 42.0–45.1)**. Gate cannot pass. FOREX 32.6% (n=466) is the worst slice — still a **config-gate candidate**, not a shipped block.

## RULE 7 — Security
- **Token/secret repo-te NAI** (drive public!). Oi gulo shudhu Termux env-e.
- Chat-e token paste korle → revoke bolo.
- Leaked: 2 GitHub PAT (revoked ✓), Cloudflare `cfut_pTef5...` (rotation check still user-side).

## RULE 8 — Honesty
Hype nai, fake confidence nai. Bhul hoile admit ("amar fixture-i vul chilo"). Agent mittha bolle → bolo user-ke ("agent bad").
"Live verified" bolte hole `/health` ei session-e hit hote hobe. Sandbox TLS fail = **not verified**.

---

## NEXT STEPS (2026-08-13)

1. **Live verify v6.10.1** (Termux / any network that can reach workers.dev):
   ```bash
   curl -sS https://fttotcv6.umuhammadiswa.workers.dev/health \
     | python3 -c "import sys,json; h=json.load(sys.stdin); print(h.get('version'), (h.get('push') or {}))"
   ```
   Expect `version=6.10.1`, `push.tokenValid=true`, `push.delivered24h` incrementing after a watched-pair scan. If version still `6.10.0` → `cd Ftt-Otc-v6 && bash scripts/redeploy.sh` (unique bundle name, check `EXPECTED_BYTES`).
2. **Close superseded worker PR #18** (`arena/019ff51d-ftt-otc-v6`, dirty, twin of merged #19).
3. **Phase F daily** — 08-13+ snapshot when live API reachable. Archive is complete through 08-12 only. `python3 scripts/full_forward_analysis.py`.
4. **FOREX block** — evidence is Phase-F-grade (4 pairs, 12 days, 28–35%) but **do not ship** until user decision + config gate. Dropping FOREX only lifts pool to 45.0% — still below 55.6%.
5. **Cloudflare token rotation** — `cfut_pTef5...` revoke/recreate (user). GitHub Actions deploy is red on every recent main push.
6. **Deriv demo** — on hold, user decision (digital options vs CFD).
7. **Custom Alerts (F09)** — future, flag chaile.
