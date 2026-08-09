# WORKER — GRADE/CONFIDENCE CALIBRATION (AGENT PROMPT — HARD MODE)

**Repo:** `ferdausfs/Ftt-Otc-v6` · **Main HEAD:** `ee7fc54` (verify live before starting)
**Reviewer:** Arena main agent — I verify everything on GitHub + run every suite + holdout-test the change. No "done" claims until code is on a branch and my verification is posted.

**This task is intentionally HARD. The arena best-model is expected. Do NOT take shortcuts. Do NOT hand-wave.**

---

## 0. THE PROBLEM (reviewer-verified, data from Workplace-drive-)

The engine's **grade and confidence are miscalibrated** — the engine's own "high quality" signals are the WORST performers:

| Slice | WR (n=5097, 08-01..09) | Engine claims |
|---|---|---|
| Grade **A+** | **37.8%** (867) | "EXCELLENT — very high probability" |
| Grade **A** | 41.8% (1097) | "STRONG" |
| Grade **B** | 42.9% (2192) | "GOOD" |
| Grade **C** | **46.9%** (941) | "MODERATE — trade with caution" |
| Confidence **80-84%** | **37.4%** (1024) | high confidence |
| Confidence **72-74%** | 43.0% (907) | floor |

**The grade ladder is INVERTED.** Breakeven = 55.6% (80% payout). Overall WR = 42.5%.

**Root cause (code-verified):**
- `grade.js`: `sc = min(40, confidence*0.4) + min(35, avgConf*5) + (alignment ALL_* ? 25 : MOSTLY ? 12)`
  - **alignment +25** is "all TFs voted the same direction" — a *trend-consensus* bonus, NOT a probability measure. In trending/parked markets (the losing regime), all TFs agree → alignment 25 → A+/A — while the trade loses.
- `voteFilters.js`: `confidence = weightedBuy/(weightedBuy+weightedSell+weightedNoTrade*0.6)` — a **vote-share ratio**, NOT a calibrated win probability. High vote-share happens exactly in the strong-trend slices that lose.

**Impact:** anyone (app, bot, trader) trusting grade/confidence is systematically misled — told to take the WORST signals (A+, 80-84%) and skip the BEST (C, 72-74%).

## 1. WHAT "DONE" MEANS (hard requirements)

Your fix must make **grade and confidence monotonically track actual win rate** on the Phase F forward data. Concretely:

**Requirement R1 (the bar):** after your change, on the holdout window **2026-08-07..09** (data: see step 2), the ordered WR by grade satisfies:
```
WR(A+) > WR(A) > WR(B) > WR(C)   (currently 37.8 < 41.8 < 42.9 < 46.9 — INVERTED)
```
and the ordered WR by confidence bucket (non-overlapping 4-pt buckets 72-75, 76-79, ...) is monotonically non-decreasing (currently 80-84 is a dip below 72-74).

**Requirement R2 (no overfit):** the calibration must be **derived from TRAIN (08-01..06)** and **validated on the holdout (08-07..09)** — no peeking at holdout while designing. Document the train-rule → holdout-result table in the PR.

**Requirement R3 (production sanity):** NO_TRADE handling stays (grade `N/A`), structure cap (FIX-A) stays, D2 blocks stay, `MIN_CONFIDENCE_FLOOR` semantics stay. You may change how grades/confidence are COMPUTED, not the filter pipeline order.

## 2. DATA & TOOLING (use the drive — not your own assumptions)

Clone the drive (public, no auth):
```bash
git clone https://github.com/ferdausfs/Workplace-drive-.git wd && cd wd
mkdir -p phase_f_forward && tar -xzf data/phase_f_forward_2026-08-09.tar.gz -C phase_f_forward
mv phase_f_forward/phase_f_forward/* phase_f_forward/ && rmdir phase_f_forward/phase_f_forward
```
Scripts already in `wd/scripts/`: `slice_mine.py` (slice WR explorer), `refine_rules.py` (per-rule contribution + holdout), `filter_test.py` (chronological holdout). **Run them, understand them, reuse them.** Data fields per signal: `confidence`, `grade`, `pair`, `assetType`, `marketRegime`, `sessionQuality`, `alignment`, `structureVerdict`, `direction`, `bestTF`, `entryHit`(corrected), `result`(WIN/LOSS), `timestamp`.

## 3. FIX OPTIONS (pick ONE or a principled combo — justify with evidence)

### Option A — Empirical calibration table (simplest, evidence-first)
Build a calibration map from TRAIN: `confBucket → empirical WR`, `grade → empirical WR`. Then:
- `confidence` reported = empirical WR of its bucket (or a smoothed blend), NOT vote-share.
- `grade` assigned from the empirical WR ladder (e.g. WR ≥ 52 → A+, ≥ 48 → A, ≥ 44 → B, else C), so the labels mean something.
- Keep `avgConf`/`alignment` as *inputs* to a model if you wish, but the OUTPUT must be calibrated.
- ⚠️ Must not hardcode the 08-01..06 table literally forever — ship the mechanism (e.g. `CALIB` config computed from a training window) + the current fitted values, and document that it must be refreshed as data grows.

### Option B — Logistic calibration (principled)
Fit `P(win) = sigmoid(a + b1*confidence + b2*avgConf + b3*alignmentScore + b4*regime + b5*assetType...)` on TRAIN (sklearn LogisticRegression or manual gradient descent — you have python; `pip install numpy scikit-learn`). Then:
- reported `confidence = round(100 * P(win))`
- grade from calibrated probability thresholds.
- Report the fitted coefficients + in/out-of-sample log-loss + the R1/R2 tables.
- ⚠️ Keep it a **deterministic, dependency-light implementation** in the worker (no sklearn at runtime — precompute coefficients into config, implement sigmoid in JS).

### Option C — Feature-aware calibration (best model expected)
Anything that honestly beats A and B on R1+R2 with a clear mechanism — e.g. include `hour`, `sessionQuality`, `pair class`, `entryHit` (corrected) — but **never** use `result` itself or any post-hoc field as a feature (leakage). If you use entryHit, it must be the corrected re-test field and you must argue it's available at signal time (it is NOT for INSTANT signals at t0 — be careful; prefer features knowable at signal time).

**Choose and defend.** A is acceptable if B/C don't beat it on holdout. Do NOT ship Option A with a static table and claim victory — show the holdout numbers.

## 4. DELIVERABLES (PR must contain ALL)

1. **Code change** in `src/analysis/grade.js` (+ `src/signal/voteFilters.js` or a new `src/analysis/calibration.js` if cleaner). Worker-side: pure JS, deterministic, no new deps.
2. **`scripts/calibration_validation.py`** (new, goes to drive): reproduces R1/R2 tables — train fit, holdout grades/conf buckets with WR + Wilson CI, and the before/after comparison. Must be re-runnable on fresh data.
3. **PR body:** problem recap (data), chosen option + why, the R1/R2 tables (train-derived → holdout-validated), coefficient/table values shipped, refresh plan, and the full test matrix.
4. **All existing suites green:** `fix_tests` 158/158 · `phase10_integration` 19/19 · `phase7_*` · `d2_tests` 39/39 · `probe_tests` 34/34 · `entry_hit_tests` 7/7 · `fx_mode_tests` 20/20 · **`r71_tests` 117P/0F** (grade changes WILL affect OTC redaction list — update `OTC_APPROVED_DIVERGENT_FIELDS` only if the engine genuinely changes those fields, with justification).

## 5. HARD WORKFLOW RULES
- **PR-first** off `main` — never push main directly.
- **No leakage:** holdout (08-07..09) must never touch training/design. Violate this and the PR is rejected outright.
- **No claim without evidence:** every statement in the PR body that references WR must have the script/table behind it.
- Phase F: no inversion, no pair-block config changes, no real-money recs. This PR is **scoring/calibration only**.

## 6. REVIEWER (ME) WILL RE-VERIFY
- Run `calibration_validation.py` myself on the drive data → R1/R2 must hold.
- Re-run every test suite myself.
- Read the calibration table/coefficients and sanity-check they're not overfit (e.g. A+ ≥ B on holdout with n≥50 per grade).
- Live-check after merge+deploy: a fresh signal's grade/confidence vs its slice's historical WR.

---

**Bottom line:** the arena's best model gets a calibrated, evidence-backed grade/confidence system that makes A+ actually mean "high win rate". Ship proof, not promises.
