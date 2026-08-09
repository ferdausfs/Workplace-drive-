# ROUND-3 PR — FINAL VERIFICATION (2026-08-06)

**Repo:** `ferdausfs/Ftt-Otc-v6` · **PR #7** · **Branch:** `arena/019fd7c0` · **Head:** `34458e0` · Base: `main` (`0c6d358`)
**Reviewer:** Arena main agent — independent (code diff read line-by-line, tests run myself, merge tested)

---

## 1. ALL 19 FIXES PRESENT — NOTHING LEFT OUT ✅

| Fix | File(s) | Verified |
|---|---|---|
| F3-01 channel mirror `message` scope | `pushToSubscribers.js` | ✅ per-subscriber message carried `{sub,message}`; pushLog always written; no crash |
| F3-02 OTC auto-resolve | `stats.js` | ✅ `if (expiryTime)` (was `!isOTC &&`); `fetchExpiryPrice` strips `-OTC` → base-pair price |
| F3-03 passGrade A+ | `pushToSubscribers.js` | ✅ `['A+','A']` / `['A+','A','B']` |
| F3-04 OTC fillStatus | `otcEngine.js` | ✅ mirrors engine.js (entry=bestTF close, current=1min close, 0.05% threshold) |
| F3-05 NO_TRADE grade | `engine.js` + `otcEngine.js` | ✅ `{grade:'N/A', label:'NO_TRADE'}` |
| F3-06 HTF block 0→8% | `voteFilters.js` + `otcEngine.js` | ✅ alignment bonus BEFORE hard-block zeroing |
| F3-07 AEST→UTC | `candles.js` + `fetchExpiryPrice` | ✅ `timezone=UTC` on both |
| F3-08 fx preferCache | `signal.js` | ✅ `preferCache && !fxMode` |
| F3-09 FVG order | `voteFilters.js` | ✅ `15min || 5min || 1min` |
| F3-10 BOS double-count | `structure.js` | ✅ `if (!bos)` guard on recentEvents |
| F3-11 RSI middle zone | `timeframe.js` | ✅ removed 55-65/35-45 trend-following scores (RANGING) |
| F3-12 +3 HIGHEST dead code | `voteFilters.js` | ✅ removed (block zeroes it anyway) |
| F3-13 crypto session weights | `filters.js` + `engine.js` | ✅ non-FOREX → sessionMult 1.0 |
| F3-14 scanner noPush | `scheduledScan.js` | ✅ `{noPush:true}` |
| F3-15 AI skip on D2 | `engine.js` | ✅ `d2Audit → aiTargetDir=null`; `AI_SKIPPED (D2 hard block)`; no LLM calls |
| F3-16 time-invariant fixtures | `engine.js` + tests | ✅ `opts.now/session/newsBlock` injection; d2/probe/fx_mode pin them |
| F3-17 cbShadow history | `health.js` | ✅ excluded from decided/pending (rows still visible) |
| F3-18 winRate window | `stats.js` | ✅ rolling last-20 ring; lifetime kept in wins/losses/totalSignals |
| F3-19 fallback confluence | `voteFilters.js` | ✅ winning-side confluence ≥ MIN_CONFLUENCE |

**Numbering:** PR#6×PR#7 collision reconciled — canonical BUG-011..025 (PR#7) + BUG-026..032 (PR#6) + CLOCK-001→BUG-022. Mapping table in PR body. ✅

**Design-decision flags (user decides — all documented in PR body):**
- F3-02: OTC resolves against base-pair REAL price (NOT_TRACKED rejected)
- F3-11: RANGING now mean-reversion only (behavior change)
- F3-12: +3 HIGHEST bonus removed permanently (reintroduce only if D2 block lifted)
- F3-13: crypto no longer gets forex session weights
- F3-18: winRate = last-20 window (existing KV starts fresh — one-time discontinuity)

## 2. TESTS — I RAN ALL MYSELF

```
fix_tests          151/151   (77 + 74 new round-3 tests T14–T32)
phase10_integration 19/19 · phase10_smoke 61/61
phase7_integration 36/36 · phase7_smoke 68/68
d2_tests 39/39 (time-invariant) · probe_tests 34/34 (time-invariant)
entry_hit_tests 7/7 · fx_mode_tests 20/20 (time-invariant)
r71_tests          113 PASS / 3 FAIL — SAME 3 pre-existing (#1a/#2/#17)
node --check all src ✓ · merge test: clean, no conflicts ✓
```

Spot-checked T15 (full OTC resolve: pending→tracker→WIN→stats→cleanup) and T23 (BOS overlap: bias 1.5 + BOS 2.0 = 3.5, NOT 4.0 — matches my independent repro). Real behavioral tests, not tautologies.

---

## 3. THE 3 PRE-EXISTING r71 FAILS — WHAT THEY ARE (user asked)

**They are NOT product bugs. They are stale frozen-baseline test artifacts.**

`r71_tests.mjs` compares the CURRENT engine byte-for-byte against a **frozen snapshot of the engine from commit `71e87eb`** ("Phase 11: raise MAX_SIGNALS_PER_PAIR 50→500"). The test literally does `git archive 71e87eb src | tar -x -C verify/baseline` and imports THAT old engine as the reference.

That frozen baseline predates **every approved change**: D2 blocks (TRENDING/HIGHEST/BAD_PAIR), AI rescue, fillStatus, entryHit, FX mode, `/12` denominators, grade cap, and all of rounds 1-3 fixes. So:

| Fail | What it compares | Why it fails |
|---|---|---|
| **#1a** (5 fixtures) | current vs 71e87eb engine, byte-equal | diverges at `finalSignal`/`recommendations` — D2 blocks flip signals to NO_TRADE, grades/denominators changed. Intentional. |
| **#17** (100 fuzz) | current vs 71e87eb on 100 fixtures | **100/100 mismatch** at finalSignal/recommendations — systemic intentional engine changes, not random defects |
| **#2** | comparability attribute | expects `COMPARABLE_PRE_AI` (71e87eb era), current engine reports `AI_AFFECTED` — AI layer behavior changed |

**Why nobody has fixed them (honest):**
1. Rounds 1-2 spec explicitly said "do NOT touch the 3 pre-existing fails" — to avoid masking regressions mid-fix-cycle.
2. They're not affecting production, live signals, or any other suite — they're a frozen regression guard that has simply not been refreshed.
3. The "fix" is not trivial: you can't just delete them or blindly regenerate the baseline — that could hide REAL accidental divergences. Correct fix = regenerate baseline from an approved commit + audit each divergence once to confirm intentional.

**Are they still there?** Yes — identical 113P/3F on main, on the round-3 PR, no change.

**Should they be fixed now?** My recommendation: **separate cleanup PR after round-3 merges** — regenerate `verify/baseline` from the post-round-3 main tip, re-audit #1a/#17 divergences (should all be attributable to the approved fixes), and update #2's comparability expectation to current AI behavior. That way the regression guard is restored on a KNOWN-GOOD baseline. I'll spec it as F3-20 if you want the agent to do it right after this PR merges.

---

## VERDICT: ✅ PR #7 APPROVED FOR MERGE (round-3)

- 19/19 fixes correct, nothing omitted, no regressions.
- merge test: clean, no conflicts. mergeable.
- PR #6 (old report-only) is superseded — its findings are now BUG-026..032 in PR #7's canonical report. **Close PR #6** after merging PR #7 (or delete its branch).

## USER ACTIONS
1. **Merge PR #7** (GitHub UI → Merge pull request).
2. **Close PR #6** (superseded).
3. After merge — I verify live: OTC fillStatus present, OTC history starts resolving, candleTime UTC, NO_TRADE grade N/A, `mode=fx&preferCache` returns fx levels, passGrade A+ (bot side).
4. Optional: F3-20 cleanup PR for the 3 r71 baseline fails (say the word).
