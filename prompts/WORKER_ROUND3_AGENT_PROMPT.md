# WORKER ROUND-3 FIX — AGENT PROMPT (ekhoni karo)

**Repo:** `ferdausfs/Ftt-Otc-v6`
**Aage poro:** `WORKER_BUGFIX_ROUND3_APPROVAL.md` (reviewer-er puro verdict + 19 ta fix-er exact spec + file + test)
**Reviewer:** Arena main agent — tumi push korar por ami PROTITA line pore + sob test nije chala + live API check kore, tarpor-e merge hobe. Chat-e "done/fixed" bole kono claim korte parba na jotokhon code GitHub-e na thake.

---

## 1. WORKFLOW (non-negotiable, agei violate korecho ekbar — abar na)
- **PR-first:** notun branch `main` (0c6d358) theke → ekta PR te SHOB round-3 fix + consolidated report. **Direct main push NAI.**
- **Numbering collision fix koro:** PR #6 ar PR #7 duitai `BUG-011..016` use koreche (alada alada bug!). Ekta canonical `BUG_REPORT.md` banao — unique ID (PR#7-r gulo BUG-011..025 thakbe, PR#6-r gulo BUG-026..032 + CLOCK-001 hobe, ba thik moto renumber koro). PR body-te mapping table dao.
- Niche Group-3-r **design-decision fix gulo** implement korba, kintu PR description-e PROTITA flag korba rationale shoho — **user decide korbe merge-er age.**

## 2. THE 19 FIXES (details `WORKER_BUGFIX_ROUND3_APPROVAL.md`-te)

### Group 1 — CRITICAL/QUICK (F3-01..F3-04)
- **F3-01** Channel mirror `message` scope (PR7-B11): hoist/recompute per subscriber; pushLog shob somoy write hobe; crash hobe na. Test: 1 subscriber channelId shoho → pushLog ache, no crash.
- **F3-02** OTC auto-resolve (PR7-B12): recommendation = base-pair real price diye resolve (isOTC flag document); alternative = `result:'NOT_TRACKED'`. **PR-te flag koro kon option nilo + keno.** Test: OTC row resolve hobe.
- **F3-03** `passGrade` A+ (PR6-B11): `f==='A' ? ['A+','A'].includes(g) : f==='AB' ? ['A+','A','B'].includes(g) : true`. Test: A+ passes A & AB.
- **F3-04** OTC fillStatus (PR6-B12): engine.js:403-421 mirror — lowest-TF last close theke fillStatus/entryPrice/currentPrice/entryDistancePct. Test: OTC signal-e fields ache.

### Group 2 — DISPLAY/LOGIC (F3-05..F3-09)
- **F3-05** NO_TRADE grade (PR7-B13): `finalDirection==='NO_TRADE'` → grade `{grade:'N/A', label:'NO_TRADE'}` (ba F). Test: NO_TRADE kakhono "B GOOD Suitable for trading" na.
- **F3-06** HTF block 0→8% (PR7-B14): alignmentBonus hard-block zero-er AGE apply (ba zero-er pore re-zero). Test: blocked → confidence 0.
- **F3-07** AEST→UTC (PR7-B16): `candles.js` + `fetchExpiryPrice`-te `timezone=UTC` param. Test: candleTime ≤ generatedAt+2min.
- **F3-08** fx preferCache (PR7-B15): `mode=fx` preferCache-incompatible (force fresh) ba scan-time fxLevels store. Test.
- **F3-09** FVG order (PR6-B16): `tfResults['15min'] || '5min' || '1min'`. Test.

### Group 3 — ENGINE SCORING (design — PR-te FLAG koro) (F3-10..F3-13)
- **F3-10** BOS double-count (PR6-B14): recentEvents BOS shudhu `!bos` hole (ba barsAgo===0 overlap filter). Repro test: current-bar BOS = 2.0 (2.5 na).
- **F3-11** RSI middle-zone (PR6-B15): `trending===false`-e `rsi>=55 mU+=0.25` / `rsi<=45 mD+=0.25` REMOVE. **Behavior change — justification likho.** Test: RANGING RSI 62 vs 66 contradictory flip nai.
- **F3-12** +3 HIGHEST dead code (PR7-B21): `HIGHEST → +3` branch remove. Justify. Test.
- **F3-13** crypto session weights (PR7-B25): crypto-r jonno sessionMult=1 (non-forex skip) ba document. **Flag.** Test: BTC/USD-te SESSION_WEIGHT nai.

### Group 4 — LOW/LATENT/TEST INFRA (F3-14..F3-19)
- **F3-14** scheduledScan noPush (PR6-B13): `handleSignalRaw(pair, env, ctx, { noPush: true })`. Test: scanner push kore na.
- **F3-15** AI on D2-blocked (PR7-B17): `if (d2Audit) aiTargetDir = null;` (LLM call skip). Test: D2 fired → no AI call.
- **F3-16** time-invariant fixtures (CLOCK-001/PR7-B22): engine-e optional `now`/session param inject. Test: 12-16 UTC-te-o pass.
- **F3-17** cbShadow convention (PR7-B18): `/api/history` decided theke cbShadow exclude (stats-er sathe match). Convention choice — flag. Test.
- **F3-18** winRate semantics (PR7-B19): last WIN_RATE_LOOKBACK rows-er upor winRate ba rename+document. **Flag.** Test.
- **F3-19** decideTfDirection fallback (PR7-B20): fallback branch-e winning-side confluence ≥ MIN_CONFLUENCE. Test.

### NOT IN SCOPE (Phase-F, code na)
- BUG-023 entryHit (analysis-only — corrected window = alada instrumentation task)
- BUG-024 forex SELL (probe already running — SELL logic ULTARA na)

## 3. TESTS — RUN ALL, OUTPUT SHOW KORO (PR description-e table)
- `fix_tests.mjs` — F3-01..19 unit test add (real modules, network stubbed — age-r pattern). 77 + new = green.
- `phase10_integration` 19/19 · `phase7_smoke` 68/68 · `phase7_integration` 36/36 · `phase10_smoke` 61/61
- `d2_tests` 39/39 · `probe_tests` 34/34 · `entry_hit_tests` 7/7 · `fx_mode_tests` 20/20
- `r71_tests` **113 PASS / 3 FAIL** (3 fail pre-existing `0c6d358`-te — TOUCH KORBE NA, beshi fail korbe na)
- `node --check` sob src + `git diff --check` clean

## 4. "DONE" ER SHORTO
1. Code GitHub-e branch-e push (PR head update) — visible.
2. PR body: consolidated BUG_REPORT summary + fix table (fix → change → test proof) + Group-3 design flags.
3. Kichhu MERGE korba na — reviewer (ami) re-verify korbe: full diff porbo, sob suite nije chalaibo, live API check (OTC fillStatus, NO_TRADE grade N/A, UTC candleTime, passGrade A+), tarpor user-ke bolbo merge safe kina.
4. Chat-e "fixed/done" claim NAI — code na thaka porjonto.
