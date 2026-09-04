# WORKER ROUND-2 FIX — AGENT PROMPT (do this now)

**Repo:** `ferdausfs/Ftt-Otc-v6` · **Spec:** `WORKER_BUGFIX_ROUND2_APPROVAL.md` (read it first — it has my evidence per finding)
**Reviewer:** Arena main agent — will re-verify EVERYTHING below on GitHub after you push. Nothing is "done" until code is on a GitHub branch and I confirm.

---

## 1. CRITICAL WORKFLOW RULE (non-negotiable)

Round-1 fixes are in PR #5 (branch `arena/019fd55e-ftt-otc-v6`, HEAD `a6e5495`). The user wants **round 1 + round 2 merged together, one merge**.

➡️ **Push your round-2 commits to the SAME branch `arena/019fd55e-ftt-otc-v6`** (PR #5 will auto-update and contain both rounds).
- If you cannot push to that branch, create a NEW branch **based on it** (`git checkout -b arena/<your-id>-ftt-otc-v6 origin/arena/019fd55e-ftt-otc-v6`) and open a new PR with base = `arena/019fd55e-ftt-otc-v6` (NOT main). Then round-2 merges into the round-1 branch, and PR #5 merges both into main.
- **NEVER push directly to main.**
- Do NOT touch finding #3 (D2_TRENDING_BLOCK vs bad-pair suspension) — that needs the user's Phase-F decision, not code.

## 2. THE 5 FIXES

### FIX-A — OTC grade structure cap (Bug #4, HIGH)
**File:** `src/signal/otcEngine.js`
- Line ~225: `const finalGrade = getSignalGrade(confidence, avgConf, alignment);` — missing the 4th argument.
- Fix: compute `const structureVerdict = buildStructureVerdict(tfResults, finalDirection);` BEFORE the grade call, pass `structureVerdict.overall` as the 4th arg, and reuse the variable in the return object (line ~240 currently calls `buildStructureVerdict(tfResults, finalDirection)` again).
- Mirror `src/signal/engine.js` line ~290 exactly.
- **Proof:** new unit test — OTC signal whose structure verdict is `AGAINST` must NEVER grade A+/A (capped at C). Reviewer repro today: 80% conf + ALL_BULLISH → `A+` without arg, `C` with AGAINST.

### FIX-B — Camarilla double-weight in OTC (Bug #5, MED-HIGH)
**File:** `src/signal/otcEngine.js` (unweight loop, lines ~26-35)
- Verified fact: 10 categories are stored WEIGHTED (`tU *= weights.trend` THEN `catScores.trend = r2(tU)`), `sr` is stored weighted (`srU *= srW`), but **camarilla is stored RAW** (`catScores.camarilla = r2(camScore.up)` — `src/signal/timeframe.js` line ~407, before the `camW` multiplier).
- The OTC loop divides every category by `rangingW[cat]` to recover "raw". Dividing raw camarilla by `0.84` inflates it (OTC contribution becomes `1/0.84 × 1.5 = 1.786×` instead of `1.5×`).
- **Fix (chosen option):** skip the `÷rW` unweight step for `camarilla` in the OTC loop — it has no regime weight stored, so nothing to undo:
  `const rawUp = cat === 'camarilla' ? (cd.up || 0) : (cd.up || 0) / rW;` (same for down)
- Do NOT change `timeframe.js` storage (would alter standard-engine display). Standard engine must be byte-identical in output for the same fixtures.
- **Proof:** math assertion test — OTC camarilla contribution == `raw × 1.5` (was `raw × 1.786`). Plus regression: standard engine signal output unchanged.

### FIX-C — Round-number bonus is dead (Bug #7, MED)
**File:** `src/analysis/otc.js` (lines ~100-105)
- Currently: `result.otcBonusUp += round.proximity * 0.4;` AND `result.otcBonusDown += round.proximity * 0.4;` — identical on both sides → cancels in `otcEngine.js:145` differential → zero effect, yet `ROUND_LEVEL_*` is shown to users (illusion).
- **Fix:** make it directional. `detectRoundNumberProximity` returns `{level, distance, stepType, proximity}`.
  - `lastClose < round.level` (price approaching round from below) → round is resistance → rejection bias DOWN → `result.otcBonusDown += round.proximity * 0.4;`
  - `lastClose > round.level` → support → rejection bias UP → `result.otcBonusUp += round.proximity * 0.4;`
  - `lastClose === round.level` (exactly on it) → apply no round bonus (ambiguous side).
  - If you disagree with this direction rule, you MUST justify in the PR with a reasoning write-up — but you must pick ONE consistent rule; no both-sides.
- **Proof:** unit test — craft a case where price is below a round level → `otcBonusUp === 0 && otcBonusDown > 0` (and the mirror case), and a confidence test through `otcEngine` showing the round bonus actually moves confidence now. Plus a test that the OLD both-sides behavior is gone.

### FIX-D — Confluence denominator 11 → 12 (Bug #2, LOW-MED display)
**Verified: max confluence = 12** (11 base vote categories: trend, momentum, macd, stochastic, bands, adx, patterns, divergence, pivots, volume, sr — camarilla is score-only, no vote; + structure = 12th).
**Files/lines (grep-verified on main):**
- `src/signal/engine.js` line ~273: `rec.confluence + '/11 categories'` → `'/12 categories'`
- `src/signal/engine.js` line ~459: `'... ' + best.confluence + '/11 confluence'` → `'/12 confluence'`
- `src/signal/otcEngine.js` line ~57: `confluenceDetail: { bullish, bearish, total: 11 }` → `total: 12`
- `src/signal/otcEngine.js` line ~198: `rec.confluence + '/11'` → `'/12'`
- `src/signal/timeframe.js` lines ~54 & ~69 (early-return paths): `total: 11` → `total: 12`
- Line ~568 already says `total: 12` — leave it.
- Then `grep -rn "'/11\|total: 11" src/` and fix EVERY remaining occurrence — no `/11` or `total: 11` may remain in `src/`.
- **Proof:** smoke — no `/11` or `total: 11` remains in `src/`; recommendations show `/12`; early returns show `total: 12`.

### HARDEN-1 — optional chaining (Bug #1, LOW, defensive)
**File:** `src/signal/timeframe.js` line ~493
- `const hasStrongStructure = structure.choch || (structure.bos && structure.multiplier.value >= 1.20);`
- → `structure.multiplier?.value >= 1.20`. No behavior change in current pipeline (analyzeStructure always sets multiplier), but every other accessor guards — this one should too.
- **Proof:** all suites green.

## 3. TESTS — RUN ALL, SHOW OUTPUT

- `scripts/fix_tests.mjs` — extend with FIX-A/B/C/D tests (FIX-D via grep-assert). Must stay 42/42 + new ones.
- `scripts/phase10_integration.mjs` — must stay **19/19**.
- `scripts/phase7_smoke.mjs`, `scripts/phase7_integration.mjs`, `scripts/phase10_smoke.mjs`, `scripts/d2_tests.mjs`, `scripts/probe_tests.mjs`, `scripts/entry_hit_tests.mjs`, `scripts/fx_mode_tests.mjs` — all green.
- `scripts/r71_tests.mjs` — must stay **113 PASS / 3 FAIL** (the 3 fails are PRE-EXISTING on main `055b6f0` — I verified. Do NOT "fix" them in this PR; do NOT let them regress to more).
- Post the pass/fail table in the PR description.

## 4. WHAT "DONE" MEANS
- Code pushed to `arena/019fd55e-ftt-otc-v6` (or your new branch off it) — visible on GitHub.
- PR #5 description updated with the round-2 table (fix → change → test proof), including your FIX-B option choice and FIX-C direction-rule justification.
- You have NOT merged anything. The reviewer (me) re-verifies: full diff read, re-run every suite myself, runtime repros (A+→C cap, camarilla 1.5× math, round-directional, `/12` grep), then tells the user it's safe to merge round 1 + round 2 together.
- **No "done" / "fixed" claims in chat until the code is on GitHub and my verification is posted.**
