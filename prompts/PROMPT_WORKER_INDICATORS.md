# WORKER — signalIndicators INSTRUMENTATION (AGENT PROMPT)

**Repo:** `ferdausfs/Ftt-Otc-v6` · **Main HEAD:** `229acdb` (PR #11 merged)
**Reviewer:** Arena main agent — verify on GitHub + run every suite + live check. No "done" claims until code is on a branch.

---

## 0. WHY (reviewer-verified)
D4 v2 (PR #11, merged) proved the current signal-time features (conf/grade/regime/pair) cap the avoidance edge at ~52-58% — Wilson CI-low never clears 50%, so no gate is deployable. The report's §7 and my review both conclude: **the engine computes raw indicators (RSI / ATR% / ADX / BB-bandwidth) at signal time but discards them before history save** — those are the most likely source of real edge for D4 v2.1.

**This PR = pure instrumentation. Zero behavior change.** Persist a tiny indicator snapshot per history row (fail-open, ~40 bytes). No runtime consumer yet.

## 1. THE CHANGE (one file: `src/history/stats.js`)

The patch in PR #11 (`diff/signalIndicators_instrumentation.patch`) already does exactly this and **applies clean to main `229acdb`** (reviewer-tested). Your job:

1. Re-apply that patch (or re-implement equivalently) in `saveSignalToHistory` (after the `cbShadow` block, before `structureAudit`):
   ```js
   // D4 v2.1 instrumentation: persist a tiny best-TF indicator snapshot.
   // RSI / ATR% / ADX / BB-bandwidth at SIGNAL TIME. Fail-open: never break a save.
   try {
     const bestTF = signal.bestTimeframe && signal.bestTimeframe.timeframe;
     const tfa = bestTF && signal.timeframeAnalysis ? signal.timeframeAnalysis[bestTF] : null;
     const ind = tfa && tfa.indicators;
     const _last = (a) => Array.isArray(a) ? a[a.length - 1] : a;
     if (ind && bestTF) {
       const atr = _last(ind.atr);
       const close = tfa.entry ? tfa.entry.price : null;
       const num = (v) => (typeof v === 'number' && isFinite(v)) ? Math.round(v * 1000) / 1000 : null;
       record.signalIndicators = {
         bestTF,
         rsi:         ind.rsi        ? num(_last(ind.rsi))                   : null,
         atrPct:      (atr && close) ? num((atr / close) * 100)              : null,
         adx:         ind.adx        ? num(_last(ind.adx.adx))               : null,
         bbBandwidth: (ind.bollinger && Array.isArray(ind.bollinger.bandwidth))
                          ? num(_last(ind.bollinger.bandwidth))              : null,
       };
     }
   } catch (e) { /* diagnostic only — never break a save */ }
   ```
2. ⚠️ **VERIFY THE FIELD PATHS against the actual engine code** — do NOT blindly trust the patch:
   - `ind.rsi` — is it array or number? (`_last` handles array)
   - `ind.atr` — array? (yes, ATR is a series)
   - `ind.adx` — is it `{ adx: [...] }` or a bare array? **Check `src/indicators/index.js` / `indicators/regime.js` and match.**
   - `ind.bollinger.bandwidth` — exact field name? Check the indicators module.
   - If any path differs, adjust the patch and DOCUMENT the actual shape in the PR body.
3. **History serialization:** `saveSignalToHistory` writes the record as-is; `/api/history` (`health.js`) returns rows — confirm `signalIndicators` is fine to expose (it is; no secrets) and no strip needed. Do NOT add it to any leak-strip list unless it contains engine audits (it doesn't).

## 2. TESTS — REQUIRED (add to `scripts/fix_tests.mjs`, new T-section)
- **T34a:** build a signal via the real engine (network stubbed, like T15/T33) → `saveSignalToHistory` → record has `signalIndicators` with numeric `rsi`, `atrPct`, `adx` where available (may be null for some indicators — assert structure, not exact values).
- **T34b:** fail-open — monkey-patch `signal.timeframeAnalysis` to something malformed (`null`, missing `indicators`, `indicators.rsi = undefined`) → save still succeeds, `signalIndicators` absent or null, no throw.
- **T34c:** OTC path — `buildMultiTimeframeSignalOTC` output → save → `signalIndicators` present or gracefully null (OTC uses standard `analyzeTimeframe` so indicators should exist).
- **T34d:** `/api/history` round-trip — saved row with `signalIndicators` survives (mock KV → handleHistory → field present).

**Full matrix after:** `fix_tests` 160 + new · `phase10_integration` 19/19 · `phase7_*` · `d2_tests` 39/39 · `probe_tests` 34/34 · `entry_hit_tests` 7/7 · `fx_mode_tests` 20/20 · **`r71_tests` 117P/0F** (only stats.js touched — baseline untouched).

## 3. WORKFLOW RULES
- PR-first off `main` (`229acdb`), never push main directly.
- **Instrumentation only** — no gate, no config change, no behavior change. If you find yourself touching engine/otcEngine/voteFilters, STOP and flag it.
- PR body: field-shape verification table (each indicator path → actual engine shape → stored), the T34 tests, full suite matrix.

## 4. AFTER MERGE (deploy note)
- Worker deploy is manual bundle: I rebuild `worker.js` → you run `bash redeploy.sh` (filename check!).
- Then ~2-3 days of new history rows carry `signalIndicators` → I rerun D4 v2.1 with raw indicators → check if the avoidance edge CI-low finally clears 50% (≥55.6% bar). No gate until then.
- Push this prompt's result report to Workplace-drive- (RULE-2).

**Bottom line:** tiny, safe, fail-open instrumentation that unlocks the real edge data. Ship it clean.
