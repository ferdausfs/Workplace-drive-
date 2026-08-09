# FIX-EH (entry-hit metric correction) — VERIFICATION REPORT (2026-08-07)

**Repo:** `ferdausfs/Ftt-Otc-v6` · **PR #9** · **Branch:** `arena/019fdad6` · **Head:** `4ad7847` · Base: `main` (`7b38185`)
**Reviewer:** Arena main agent — diff read line-by-line + full suites run + INDEPENDENT repro (not just the agent's tests).

---

## WHAT WAS THE BUG (recap)
`entryHit` used the expiry ±5min window with `BUY: windowLow <= entry`. Since a LOSS always ends past the entry, the losing direction always satisfies the condition → `entryHit ≈ (result == LOSS)`. Live proof: MISS WR = **100.0% on 08-05/06/07 (3/3 days)** — exactly what my 200k-row fair-coin simulation predicted. The metric carried zero information.

## THE FIX (shadow-only, matches my spec exactly)
1. `saveSignalToHistory` — records now carry `fillStatus` / `currentPrice` / `entryDistancePct` (needed to distinguish INSTANT vs PENDING_ENTRY).
2. `fetchExpiryPrice(pair, expiry, env, opts)` — accepts `startTimeISO`; fetches candles [signal−1min → expiry+1min]; returns full `candles[]` + `postSignal` (candles after signal). **Legacy `windowLow/High` (expiry±5min) preserved byte-identical** when `startTimeISO` absent → d2/probe/r71 callers unaffected.
3. `scheduledTracker` — corrected semantics:
   - **PENDING_ENTRY:** plain touch (BUY: low≤entry, SELL: high≥entry).
   - **INSTANT:** **re-test** — price must LEAVE the entry in the signal's favor (BUY: some high > entry; SELL: some low < entry) and THEN return to it.
   - `entryHit` = corrected · `entryHitLegacy` = old rule (side-by-side comparison) · window start/end recorded.

## MY VERIFICATION

### Tests I ran (all myself):
```
fix_tests          158/158   (151 + 7 new T33)
phase10_integration 19/19 · phase10_smoke 61/61
phase7_integration 36/36 · phase7_smoke 68/68
d2_tests 39/39 · probe_tests 34/34 · entry_hit_tests 7/7 · fx_mode_tests 20/20
r71_tests          117 PASS / 0 FAIL   (F3-20 baseline intact — only stats.js touched)
```

### INDEPENDENT repro (my own fixture, not the agent's):
- **Straight-down BUY LOSS** (all candle highs ≤ entry, no up-move):
  ```
  result: LOSS | entryHit: false | entryHitLegacy: true
  ```
  → **Tautology BROKEN**: old metric said "hit" (true), new metric correctly says "not a re-test" (false). WIN/LOSS unchanged.
- ⚠️ First attempt looked like a FAIL — my fixture's 2nd candle had `high 100.1 > entry 100` (not a real straight-down). Fixed the fixture → 3 OK / 0 FAIL. **The code was correct; my first fixture was wrong.** (Honesty: I double-checked my own test before blaming the agent.)

## VERDICT: ✅ PR #9 APPROVED FOR MERGE

**Scope discipline:** only `src/history/stats.js` + tests. Engine/timeframe/otcEngine untouched → r71 baseline intact. Production WR/stats/push untouched (shadow-only, as agreed).

## USER ACTION
1. **Merge PR #9** on GitHub.
2. Close/delete the leftover branch `arena/019fdad4` (an earlier duplicate attempt `e5fcd36` — NOT the PR head; ignore or clean it).
3. **Deploy:** I'll rebuild `worker.js` from the new main → you run `bash redeploy.sh` (token enter). (GitHub Actions CI is still flaky/queued.)

## AFTER DEPLOY — what I'll check live (~1-2 days of new rows)
- New history rows carry `entryHit` (corrected) + `entryHitLegacy` side by side.
- **The 100% MISS-WR tautology must disappear** (entryHit no longer ≈ result).
- Informative rows appear: `entryHit=true` + `WIN` (leave-then-return cases).
- Update my analysis scripts to read corrected vs legacy.
