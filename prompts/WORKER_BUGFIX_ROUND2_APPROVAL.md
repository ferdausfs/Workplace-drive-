# WORKER BUGFIX — ROUND 2 APPROVAL (independent reviewer)

**Repo:** `ferdausfs/Ftt-Otc-v6` · **Reviewed at:** main `055b6f0` (GitHub truth, verified via API)
**Reviewer:** Arena main agent (independent) — verified every claim by reading code at HEAD + runtime repros.
**Source audit:** Sonnet-5 audit (7 findings) — reviewed one-by-one; 4 real bugs + 1 hardening confirmed, 1 overstated, 1 design conflict.

## VERDICT ON THE 7 SONNET FINDINGS

| # | Finding | My verdict | Evidence |
|---|---------|-----------|----------|
| 1 | `hasStrongStructure` multiplier null → crash | ⚠️ **NOT a live crash — HARDEN only** | `analyzeStructure()` ALWAYS returns `multiplier:{direction,value}` (structure.js:265-268 insufficient-data path + :380-382 normal path). Runtime repro confirmed. Crash impossible in current pipeline. Add `?.` anyway (every other accessor guards; this one doesn't). |
| 2 | confluence `/11` vs `total:12` | ✅ **REAL (display, LOW-MED)** | engine.js:273 `'/11 categories'`, :459 `'/11 confluence'`; otcEngine.js:57 `total:11`, :198 `'/11'`; timeframe.js:54,69 `total:11` vs :568 `total:12`. Computed confluence correct; only denominator strings stale. |
| 3 | D2_TRENDING_BLOCK pair-agnostic vs BAD_PAIR suspension | 🟠 **DESIGN CONFLICT — no code fix now** | engine.js:165-168 TRENDING fires before :169 bad-pair check → bad pairs can never produce REAL TRENDING signals. But D2 shadow captures counterfactuals (pair+regime+session, :178-197). Phase F planning decision (user): shadow obs count or probe needed. NO engine change without user decision. |
| 4 | OTC grade missing `structureOverall` | ✅ **REAL (HIGH)** | otcEngine.js:225 `getSignalGrade(conf, avgConf, alignment)` vs engine.js:290 passes `structureVerdict.overall`. Runtime repro: 80%/ALL_BULLISH → **A+ without arg, C with AGAINST**. OTC tfResults DO carry structure (analyzeTimeframeOTC uses standard analyzeTimeframe). |
| 5 | Camarilla double-standard → OTC ~19% inflate | ✅ **REAL (MED-HIGH)** | All cats store WEIGHTED (`tU *= weights.trend` then `catScores.trend={up:r2(tU)}`), camarilla stores RAW (timeframe.js:407 pre-`camW`). OTC unweights ALL by `÷rW` (otcEngine.js:27-35, `rangingW.camarilla=0.84`) → camarilla `1/0.84×1.5 = 1.786` vs intended `1.5` = ~19% over-weight in OTC scores. Standard engine unaffected. |
| 7 | Round-number bonus dead/no-op | ✅ **REAL (MED)** | analysis/otc.js:103-104 adds SAME `proximity*0.4` to `otcBonusUp` AND `otcBonusDown`; otcEngine.js:145 uses the DIFFERENCE → net zero. `ROUND_LEVEL_*` still shown to users (otcSignals/filtersApplied/entryReason) = illusion. Consecutive (otc.js:88-89) & wick (96) are properly directional. |

## ROUND-2 FIX LIST (agent must work PR-first, never push main directly)

### FIX-A — OTC grade structure cap (Bug #4, HIGH)
- **File:** `src/signal/otcEngine.js`
- Compute `structureVerdict` BEFORE the grade call; pass `structureVerdict.overall` as 4th arg to `getSignalGrade` (mirror engine.js:289-290).
- **Proof required:** unit test — OTC signal with structure AGAINST → grade capped at C (never A+/A). Repro currently gives A+.

### FIX-B — Camarilla consistent weighting (Bug #5, MED-HIGH)
- **File:** `src/signal/otcEngine.js` (and/or `src/signal/timeframe.js`)
- OTC unweight loop must NOT divide camarilla by `rW` (it's stored RAW). Fix options (choose + justify):
  - (a) otcEngine: skip `÷rW` for `camarilla` (raw stays raw), OR
  - (b) timeframe.js: store camarilla weighted like every other cat (then OTC `÷0.84` becomes correct).
- ⚠️ Changing timeframe.js storage changes the STANDARD engine's displayed camarilla values too — verify standard engine display/logic unaffected or acceptable.
- **Proof required:** math assertion — OTC camarilla contribution == `raw × OTC weight` (1.5), NOT `raw × 1.786`. Regression: standard engine signal output unchanged for same fixtures.

### FIX-C — Round-number directional bonus (Bug #7, MED)
- **File:** `src/analysis/otc.js` (and otcEngine confidence if needed)
- Make round bonus directional: price BELOW the round level → support → `otcBonusUp`; ABOVE → resistance → `otcBonusDown`. (Or: if you choose to remove it from scoring, also remove `ROUND_LEVEL_*` from `otcSignals`/display — no user-visible illusion.)
- **Proof required:** unit test — round-level case where `otcBonusUp !== otcBonusDown`, and confidence actually moves; plus a case showing the OLD behavior (both equal) is gone.

### FIX-D — confluence denominator 11→12 (Bug #2, LOW-MED display)
- **Files:** `src/signal/engine.js` (:273, :459), `src/signal/otcEngine.js` (:57, :198), `src/signal/timeframe.js` (:54, :69)
- Unify ALL display denominators to **12** (11 base + structure category; structure always present via analyzeStructure → max confluence = 12).
- **Proof required:** smoke — recommendation strings show `/12`, early-return shows `total:12`; no `/11` remains in src.

### HARDEN-1 — optional chaining on multiplier (Bug #1, LOW)
- **File:** `src/signal/timeframe.js` line ~493
- `structure.choch || (structure.bos && structure.multiplier?.value >= 1.20)` — defensive only, zero behavior change in current pipeline.
- **Proof required:** all existing suites still green.

### NOT IN SCOPE (Phase F decision needed — user)
- Finding #3 TRENDING-block vs bad-pair data collection. No code change without user's decision (shadow obs acceptable? probe for TRENDING cells?). Flag in PR description if touched.

## MERGE GATE (round 2)
1. PR-first from a branch; never direct main push.
2. I re-verify: code diff + run `fix_tests.mjs` (extended), `phase10_integration.mjs` (19/19), full regression (phase7_*, d2/probe/entry_hit/fx_mode, r71_tests must stay == main's 113P/3F).
3. I approve → user merges (GitHub UI / Termux). I then verify live worker endpoint.

## STATUS (2026-08-06)
- Round 1 PR (#5, branch `arena/019fd55e`) — **VERIFIED BY ME: all 6 fixes + CHECK-A correct, phase10_integration 19/19, fix_tests 42/42, all regression green, r71 = main-identical (3 pre-existing fails). Merge-ready.**
- Round 2 (this doc) — **NOT yet implemented.** Assign to agent.
