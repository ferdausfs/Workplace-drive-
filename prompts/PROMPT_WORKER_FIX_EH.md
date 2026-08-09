# WORKER — AGENT PROMPT (entry-hit metric CORRECTION — FIX-EH, shadow-only)

**Repo:** `ferdausfs/Ftt-Otc-v6` · **Main HEAD:** `7b38185` (PR #8 merged)
**Reviewer:** Arena main agent — I verify on GitHub + I re-run every suite + live check after you push. No "done" claims until code is on a branch.

---

## WHY (reviewer-verified, 3 days of live data)

The `entryHit` shadow metric is **mathematically tautological**: with the current window (`expiry ± 5min`, `stats.js fetchExpiryPrice`) and the current test (`BUY: windowLow <= entry / SELL: windowHigh >= entry`):

```
LOSS  ⟹  price ended past the entry  ⟹  the expiry-window low/high always satisfies the condition  ⟹  entryHit = true (guaranteed)
WIN   ⟹  price moved away and didn't re-cross near expiry  ⟹  entryHit = false (almost always)
```

Live proof (my independent 200k-row fair-coin simulation predicted this exactly):
- 08-05: MISS WR = 100.0% (133) · 08-06: 100.0% (183) · 08-07: 100.0% (36) — **3/3 days exact 100%**
- `entryHit=false ⟹ WIN` is GUARANTEED by the code, so the metric carries ZERO information about signal quality.

**The fix is NOT just widening the window to [signalTime → expiry]** — that still leaves the tautology, because entry == the last close at signal time, so the losing direction always crosses the entry. The correct, information-bearing definition is **re-test semantics**: did price LEAVE the entry in the signal's favor and then RETURN to it? A pure losing drift (price never moved in favor) is NOT a re-test. This breaks the tautology and gives a real "entry was re-tested after moving away" signal.

---

## THE FIX — 3 files in `src/`, shadow-only (production WR untouched)

### 1. `src/history/stats.js` — `saveSignalToHistory` (~line 99 record)
Add these shadow fields to the `record` (they exist on `signal` — FIX-3 standard + F3-04 OTC):
```js
fillStatus: signal.fillStatus || null,
currentPrice: signal.currentPrice || null,
entryDistancePct: signal.entryDistancePct == null ? null : signal.entryDistancePct,
```
(Reason: the resolver needs to know if a signal was INSTANT vs PENDING_ENTRY; history also gains display value.)

### 2. `src/history/stats.js` — `fetchExpiryPrice(pair, expiryTimeISO, env, opts = {})` (~line 279)
- Accept `opts.startTimeISO`. When present:
  - `signalMs = new Date(opts.startTimeISO).getTime()` (guard `Number.isFinite`, else fall back to legacy).
  - `startDate = new Date(signalMs - 60_000)` (1-min buffer before signal), `endDate = new Date(expiryMs + 60_000)` (keeps `timezone=UTC`, F3-07).
- Collect the candle list ONCE per successful attempt:
  ```js
  const candles = []; // {datetime, stamp, open, high, low, close}
  for (const c of data.values) { /* parse as today; skip invalid */ candles.push({...}); }
  ```
- `price` stays UNCHANGED: the close of the candle nearest `expiryMs` (that is the WIN/LOSS exit).
- Return (new shape, additive — old fields kept):
  ```js
  {
    price,                       // unchanged
    candles,                     // full ordered list for the fetched bracket (ascending by stamp)
    windowLow,  windowHigh,      // legacy semantics PRESERVED: over stamps in [expiryMs-5min, expiryMs+5min] (old bracket)
    windowStart, windowEnd,      // the actual requested bracket
    // new, computed when opts.startTimeISO present:
    postSignal: opts.startTimeISO ? candles.filter(c => c.stamp > signalMs) : null,
  }
  ```
  (When `opts.startTimeISO` absent — d2/probe/r71 stores — behavior is byte-identical to today.)
- ⚠️ Do NOT change `windowLow/windowHigh` meaning — other callers (d2store/probeStore/r71store) still rely on the old expiry±5min bracket. Add new fields, don't move old ones.

### 3. `src/history/stats.js` — `scheduledTracker` entry-hit block (~line 246-264)
- Change the fetch call to pass the signal time:
  ```js
  const fetchResult = await fetchExpiryPrice(record.pair, record.expiryTime, env, { startTimeISO: record.timestamp });
  ```
- Replace the current `entryHit` computation with the corrected semantics + keep legacy:
  ```js
  if (record.entryPrice != null && fetchResult && fetchResult.postSignal && fetchResult.postSignal.length) {
    const entry = record.entryPrice;
    const eps = 1e-9 * Math.max(Math.abs(entry), 1);
    const cs = fetchResult.postSignal; // candles strictly AFTER the signal candle (stamp > signalMs)
    const dir = record.direction;

    // LEGACY (kept for comparison) — old expiry±5min rule, from fetchResult.windowLow/High:
    let legacy = null;
    if (fetchResult.windowLow != null && fetchResult.windowHigh != null) {
      legacy = dir === 'BUY' ? fetchResult.windowLow <= entry + 1e-12
            : dir === 'SELL' ? fetchResult.windowHigh >= entry - 1e-12 : null;
    }

    // CORRECTED — re-test semantics:
    // PENDING_ENTRY (entry away from price): plain touch — BUY: low<=entry, SELL: high>=entry.
    // INSTANT (entry == price at t0): leave-then-return —
    //   BUY : some candle high > entry, then a LATER candle low <= entry
    //   SELL: some candle low  < entry, then a LATER candle high >= entry
    let corrected = false;
    if (record.fillStatus === 'PENDING_ENTRY') {
      if (dir === 'BUY')  corrected = cs.some(c => c.low  <= entry + eps);
      if (dir === 'SELL') corrected = cs.some(c => c.high >= entry - eps);
    } else if (dir === 'BUY' || dir === 'SELL') {
      let left = false;
      for (const c of cs) {
        if (dir === 'BUY'  && !left && c.high >  entry + eps) left = true;
        if (dir === 'SELL' && !left && c.low  <  entry - eps) left = true;
        if (left && dir === 'BUY'  && c.low  <= entry + eps) { corrected = true; break; }
        if (left && dir === 'SELL' && c.high >= entry - eps) { corrected = true; break; }
      }
    }

    record.entryHit = corrected;                        // NEW semantics
    record.entryHitLegacy = legacy;                     // old rule, for comparison
    record.entryHitWindowLow = fetchResult.postSignal.reduce((m,c)=>Math.min(m,c.low), Infinity);
    record.entryHitWindowHigh = fetchResult.postSignal.reduce((m,c)=>Math.max(m,c.high), -Infinity);
    record.entryHitWindowStart = record.timestamp;
    record.entryHitWindowEnd = record.expiryTime;
  } else {
    record.entryHit = null; record.entryHitLegacy = null;
  }
  ```
- `updateSignalResult` (~line 411-420): pass through the new fields alongside the old:
  ```js
  if (record.entryHit !== undefined) sig.entryHit = record.entryHit;
  if (record.entryHitLegacy !== undefined) sig.entryHitLegacy = record.entryHitLegacy;
  if (record.entryHitWindowStart !== undefined) sig.entryHitWindowStart = record.entryHitWindowStart;
  if (record.entryHitWindowEnd !== undefined) sig.entryHitWindowEnd = record.entryHitWindowEnd;
  ```
- Keep the rest of the resolver EXACTLY as-is (WIN/LOSS, TIE via classifyOutcome, stats, push — untouched).

---

## TESTS — extend `scripts/fix_tests.mjs` (T33) + keep everything green

Fixtures MUST use real UTC `datetime` strings (the new logic compares timestamps; the existing 'x' fixtures won't do). Mock `globalThis.fetch` like T15 does. Cases:

| Test | Setup | Expect |
|---|---|---|
| T33a | BUY, straight up WIN, never returns | `entryHit=false`, `entryHitLegacy=false` |
| T33b | BUY, straight down LOSS (no up-move first) | `entryHit=false` (NEW — old would be true), `entryHitLegacy=true` |
| T33c | BUY, up 101 then back to 100 then rally WIN | `entryHit=true` (re-test) AND WIN — the informative case |
| T33d | SELL, straight up LOSS (no down-move first) | `entryHit=false`, `entryHitLegacy=true` |
| T33e | SELL, down 99 then back to 100 then fall WIN | `entryHit=true` AND WIN |
| T33f | PENDING_ENTRY BUY, price reaches entry | `entryHit=true` |
| T33g | fetchExpiryPrice WITHOUT startTimeISO | returns legacy windowLow/High identical to old behavior (d2/probe/r71 unaffected) |

**After:** full suite — `fix_tests` 151 + new · `phase10_integration` 19/19 · `phase7_*` · `d2_tests` 39/39 · `probe_tests` 34/34 · `entry_hit_tests` 7/7 · `fx_mode_tests` 20/20 · **`r71_tests` stays 117P/0F** (you touch ONLY stats.js — not engine/timeframe/otcEngine — so the r71 baseline is untouched).

---

## WORKFLOW / RULES
1. PR-first off `main` (`7b38185`), never push main directly.
2. **Shadow-only:** do NOT change WIN/LOSS/TIE/stats/push behavior in any way. This is instrumentation.
3. PR body: the tautology proof recap (1 short para), fix table (file → change → test), test matrix.
4. After you push I re-verify: full diff, run every suite myself, and confirm the 3-file scope.

## AFTER MERGE (deploy note for user)
- Worker deploy is manual now (GitHub Actions CI stuck): I rebuild `worker.js` from new main, user runs `bash redeploy.sh`.
- Then ~1-2 days of NEW history rows will carry `entryHit` (corrected) + `entryHitLegacy` (old) side by side — I'll verify live that MISS-WR-100% tautology disappears (entryHit no longer ≈ result) and that T33c-style rows (hit=true + WIN) appear.
- Analysis scripts (my `entry_hit_analysis.py` / `day3_analysis.py`) will be updated to read `entryHit` vs `entryHitLegacy`.
