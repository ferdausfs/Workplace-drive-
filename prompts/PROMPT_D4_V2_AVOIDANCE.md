# WORKER/ANALYSIS — D4 v2 AVOIDANCE MODEL (AGENT PROMPT — HARD MODE)

**Repos involved:** analysis on `Workplace-drive-` data (public clone), model ships as a script + optionally as worker config gates.
**Reviewer:** Arena main agent — I re-run everything on the drive data + validate holdout + no-leakage. No "done" until evidence is posted.

**This is the profitability task. The arena best model is expected. Do NOT take shortcuts.**

---

## 0. WHY (reviewer-verified from drive data, 5097 rows 08-01..09)

The engine pool WR is 42.5% vs 55.6% breakeven. D4 v1 (predict WIN) found no edge. Calibration (PR #10, live) fixed the LABEL ladder (A+ now best) but **best calibrated grade A+ = 54.8% — still below breakeven**. Labels are honest now, but there's still no profitable subset identified.

**The missing piece: an AVOIDANCE model** — predict which signals will LOSE, and gate them out. The data shows strong loser slices (FOREX 30.4%, HIGHEST session 11.9%, AUD/USD 24.2%, USD/JPY 29.3%, GBP/USD 31.7%, conf-bucket 80-83 36.7% pre-calibration). The question is: **can a model, using ONLY signal-time features, isolate a tradeable subset with WR ≥ 55.6% on holdout?**

## 1. THE TASK

Build a **chronologically-split, no-leakage model** that decides **TRADE / SKIP** per signal, such that the TRADE subset clears breakeven on holdout. Deliver:

1. **`scripts/d4_v2_avoidance.py`** (new, re-runnable on the drive data):
   - Loads `phase_f_forward/*/*.json` (18 pairs, WIN/LOSS decided rows).
   - **Chronological split:** TRAIN = 08-01..08-06, VAL = 08-07..08-09. (If more data exists by the time you run it, extend: TRAIN = older 70%, VAL = newest 30%, strictly chronological.)
   - Features — **must be knowable at signal time** (NO result, NO entryHit, NO post-hoc fields):
     - `pair`, `assetType`, `direction`, `bestTF`, `marketRegime`, `sessionQuality`, `hour`, `dow`
     - `confidence` (raw vote-share), `coreConfidence`, `avgConfluence`, `alignment`, `structureVerdict.overall`
     - **RAW INDICATORS if present in history records** — check the schema: if `timeframeAnalysis` or indicator snapshots are stored, include RSI value, ATR%, ADX, BB bandwidth for the best TF. If NOT stored, note it (see section 4 — this is a gap we should fix).
   - Model: any (logistic regression / gradient boosting / simple rules) — but MUST be deterministic + explainable enough to ship as worker config or a small JS gate.
   - **Metrics:** TRADE-subset WR + Wilson CI on TRAIN and VAL; coverage (fraction of signals kept); the profit table: WR, avg odds implied (assume 80% payout → breakeven 55.6%), expected edge per trade.
   - Report feature importance / the decision rule so a human can audit it.

2. **Ship-able artifact:** express the final model as:
   - a **rule table** (e.g. `SKIP if pair in {AUD/USD,...} OR sessionQuality==HIGHEST OR calibScore < X`) **and/or**
   - a **logistic score** `P(loss) = sigmoid(...)` with coefficients — designed to be ported to the worker's `src/analysis/` as a deterministic JS gate (no new deps).

3. **PR body** (if you also touch the worker) or **report** (if analysis-only for now): the TRAIN/VAL tables, the TRADE-subset WR + CI vs 55.6%, coverage, the exact gate rule/coefficients, and the leakage statement.

## 2. HARD REQUIREMENTS (the bar)

- **R1 — holdout edge:** TRADE-subset WR on VAL (08-07..09) must be **≥ 55.6% with Wilson CI lower bound ≥ 50%**, AND coverage ≥ 15% of signals (so it's not 3 cherry-picked signals). If you can't hit it, say so honestly — report the best achievable and what's missing.
- **R2 — no leakage:** train only on TRAIN. Any feature derived from VAL = automatic reject. `result`/`entryHit`/`exitPrice`/`checkedAt` must never enter features.
- **R3 — monotonic sanity:** the gate must not be absurd (e.g. "skip when confidence < 90" that keeps 2 signals). Coverage + CI both reported.
- **R4 — worker-portable:** the final artifact is a config/rules/coefficients file that a JS worker can apply deterministically (no Python at runtime).

## 3. DATA & TOOLING (drive is source of truth)

```bash
git clone https://github.com/ferdausfs/Workplace-drive-.git wd && cd wd
mkdir -p phase_f_forward && tar -xzf data/phase_f_forward_2026-08-09.tar.gz -C phase_f_forward
mv phase_f_forward/phase_f_forward/* phase_f_forward/ && rmdir phase_f_forward/phase_f_forward
ls scripts/   # slice_mine.py, refine_rules.py, filter_test.py, d4_run.py, calibration_validation.py — reuse/learn from them
```
Data fields per history row: `pair, direction, confidence, grade, entryPrice, expiryTime, bestTF, alignment, marketRegime, session, sessionQuality, aiAgreed, structureVerdict, aiStatus, coreConfidence, entrySource, timestamp, result, exitPrice, entryHit(legacy/corrected — DO NOT USE as feature)`.

## 4. KNOWN GAP (address it)

History records likely DON'T store raw indicators (RSI/ATR/ADX at signal time). If true:
- **In the report, flag this as a gap** — raw indicators are the most likely source of real edge (the calibration found conf/grade predict only ~40-45%).
- **Propose the instrumentation:** worker PR to persist a small `signalIndicators` snapshot per history row (best-TF RSI/ATR%/ADX/BB bandwidth — 4-6 numbers, tiny). Then D4 v2.1 can use them once data accumulates. Do NOT fake them from post-hoc data.

## 5. WORKFLOW RULES
- Analysis-first: get the numbers on the drive data BEFORE proposing any worker change.
- If the worker change is justified (e.g. adding `signalIndicators` instrumentation), it's a **separate PR-first** worker PR — analysis report references it, but the code change goes through PR review like everything else.
- Phase F: this is analysis + optional instrumentation. **No config gate goes live** until (a) holdout proves ≥55.6% with coverage, and (b) it's been validated on 2+ holdout windows (next days' data).
- Honesty: if no model clears the bar, say so. The deliverable is the TRUTH, not a fake profitable subset.

## 6. REVIEWER WILL RE-VERIFY
- Run `d4_v2_avoidance.py` myself on drive data → R1/R2/R3 must hold.
- Sanity-check the rule/coefficients are not overfit (coverage + CI + monotonic).
- If a worker instrumentation PR exists: full suite green (fix_tests 160/160, r71 117P/0F, all others), diff read.

---

**Bottom line:** find the tradeable subset. If it exists in the data, prove it on holdout and ship the gate. If it doesn't, tell us exactly what data we're missing (raw indicators) so we instrument it. Honest edge > fake edge.
