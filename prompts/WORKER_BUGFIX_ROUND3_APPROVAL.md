# WORKER BUGFIX — ROUND 3 VERIFICATION & APPROVAL (2026-08-06)

**Repo:** `ferdausfs/Ftt-Otc-v6` · **Audited main:** `0c6d358` (post-PR#5 merge)
**Reviewer:** Arena main agent — every finding below independently verified (code at HEAD + runtime repro + live API).

**Two parallel audit PRs (both report-only, NO code changes):**
- **PR #6** — `arena/019fd7bf` (head `4d79f67`): BUG-011..016 + CLOCK-001
- **PR #7** — `arena/019fd7c0` (head `56055ee`): BUG-011..025

⚠️ **NUMBERING COLLISION:** BUG-011/012/013/014/015/016 mean DIFFERENT things in PR#6 vs PR#7. Must be reconciled (see agent instructions).

---

## VERDICT: ALL 22 findings CONFIRMED REAL (0 fabricated, 0 wrong)

### PR #6 findings (7)
| ID | Severity | Finding | My verification |
|----|----------|---------|-----------------|
| BUG-011 | High | `passGrade()` drops `A+` for A/AB filters | ✅ code: `g === 'A'`, `['A','B'].includes(g)` — A+ never matches |
| BUG-012 | High | OTC engine omits fillStatus/entryPrice/currentPrice/entryDistancePct | ✅ **live:** GBPUSD-OTC has none; standard signals have them |
| BUG-013 | Med | `scheduledScan` calls `handleSignalRaw` w/o `noPush:true` | ✅ code: `handleSignalRaw(pair, env, ctx)` — no opts. Severity arguable (dedup+lock guard), keep MED |
| BUG-014 | Med | `analyzeStructure` double-counts current-bar BOS (2.0+0.5) | ✅ **runtime repro:** same break in `bos` AND `recentEvents@0` → score 2.5 |
| BUG-015 | Med | RANGING momentum RSI 55-65/35-45 contradictory bias | ✅ code: `trending===false` → `rsi>=55 mU+=0.25`, `rsi<=45 mD+=0.25`. Design decision needed |
| BUG-016 | Med-Low | FVG check uses 1min first | ✅ code: `fvgCheckTF = tfResults['1min'] \|\| '5min' \|\| '15min'` (vs marketCondition 15min-first) |
| CLOCK-001 | Test | d2_tests #11b fails 12-16 UTC (HIGHEST session) | ✅ code: session.js hour12-16→HIGHEST; engine D2 block sets d2Audit; tests pass now (16:58 UTC, window over) |

### PR #7 findings (15)
| ID | Severity | Finding | My verification |
|----|----------|---------|-----------------|
| BUG-011 | High | Channel mirror `message` ReferenceError → pushLog never written | ✅ code: `message` block-scoped in map callback, referenced outside → ReferenceError |
| BUG-012 | High | OTC never auto-resolved (result:null forever) | ✅ **live:** EUR/USD-OTC `pending:9 decided:0 winRate:null`, rows since 07-31; code: `if (!isOTC && expiryTime)` |
| BUG-013 | Med | NO_TRADE carries tradable grade (B "Suitable for trading") | ✅ code: `getSignalGrade` no NO_TRADE guard; live BTC/USD NO_TRADE grade B observed |
| BUG-014 | Med | HTF hard block → 0% then alignment bonus → 8% | ✅ code: `confidence=0` then `Math.min(92, confidence + alignmentBonus)` unconditional |
| BUG-015 | Med | `mode=fx&preferCache=true` returns non-FX payload | ✅ code: preferCache path returns cached verbatim, fxMode only on fresh path |
| BUG-016 | Med | Forex candleTime is AEST (UTC+10) | ✅ **live:** generatedAt 17:02Z, candleTime 02:59 (+10h); code: no `timezone` param in candles.js |
| BUG-017 | Low-Med | AI (2 LLM calls) runs on D2-blocked then discarded | ✅ code: `aiTargetDir` uses rawDirection when finalDirection NO_TRADE; live aiValidation present + AI_RESCUE_SKIPPED |
| BUG-018 | Med (latent) | `/api/history` counts cbShadow rows, `/api/stats` excludes | ✅ code: health.js:93 no cbShadow exclusion |
| BUG-019 | Low-Med | winRate all-time vs documented 20-lookback; sampleSize mislabeled | ✅ code: stats.js:447 `wins/decided` all-time; sampleSize capped but unused; dyn adj permanent |
| BUG-020 | Low | `decideTfDirection` fallback bypasses MIN_CONFLUENCE=5 (uses ≥4) | ✅ code: `scoreDiff>=4.0 && confluence>=4` third branch |
| BUG-021 | Low | `+3` HIGHEST bonus dead for forex (D2 block zeroes it) | ✅ code: voteFilters +3 then engine D2_HIGHEST_SESSION_BLOCK for forex |
| BUG-022 | Low | Fixture tests time-of-day dependent (= CLOCK-001) | ✅ code + pass-now evidence |
| BUG-023 | Low | entryHit near-tautological (CHECK-B quantified) | ✅ **independently proven by me:** 200k-row sim + day-2 live data (miss WR=100% guaranteed) |
| BUG-024 | — | Forex SELL weakness re-check | ✅ my day-2 data: FOREX 16.1% WR, EUR/USD 0/14 |
| BUG-025 | Low | Crypto receives forex session multipliers (USD quote 1.4) | ✅ code: `getSessionWeightMultiplier` applies SESSION_PAIR_WEIGHTS.USD to BTC/USD |

**Honesty note:** This is the strongest audit so far — every single claim verified real. The agent earned trust on this round. (Does NOT mean fix everything blindly — priorities + design decisions below.)

---

## ROUND-3 FIX LIST — agent must work PR-first (never push main)

### Group 1 — CRITICAL/QUICK FIXES (do all, low risk, high value)
| # | Fix | File | Spec |
|---|-----|------|------|
| F3-01 | Channel mirror `message` scope (PR7-B11) | `pushToSubscribers.js` | hoist message into `delivered` map or recompute per subscriber; ensure pushLog written even when channel mirror fails; add unit test (1 subscriber w/ channelId → pushLog exists, no crash) |
| F3-02 | OTC auto-resolve (PR7-B12) | `stats.js:169` | decide: resolve OTC vs base-pair real price (document `isOTC` flag) OR write `result:'NOT_TRACKED'`. **User decision needed** — see below. Default recommendation: track vs base-pair price (OTC = synthetic of base pair) |
| F3-03 | passGrade A+ (PR6-B11) | `pushToSubscribers.js` | `f==='A' ? ['A+','A'].includes(g) : f==='AB' ? ['A+','A','B'].includes(g) : true` + test |
| F3-04 | OTC fillStatus (PR6-B12) | `otcEngine.js` | mirror engine.js:403-421 — compute from lowest-TF last close; attach fillStatus/entryPrice/currentPrice/entryDistancePct + test |

### Group 2 — DISPLAY/LOGIC CORRECTNESS
| # | Fix | File | Spec |
|---|-----|------|------|
| F3-05 | NO_TRADE grade (PR7-B13) | `engine.js` + `otcEngine.js` | when finalDirection==='NO_TRADE' → grade `{grade:'N/A', label:'NO_TRADE'}` (or F); do NOT score alignment at conf 0 + test |
| F3-06 | HTF block 0→8% (PR7-B14) | `voteFilters.js` | apply alignmentBonus BEFORE hard-block zeroing (or re-zero after) + test (blocked → confidence 0) |
| F3-07 | AEST→UTC (PR7-B16) | `candles.js` (+`fetchExpiryPrice` symmetry) | add `u.searchParams.set('timezone','UTC')` + test asserting candleTime ≤ generatedAt+2min |
| F3-08 | fx preferCache (PR7-B15) | `signal.js` | treat `mode=fx` as preferCache-incompatible (force fresh) or store fxLevels at scan + test |
| F3-09 | FVG order (PR6-B16) | `voteFilters.js` | `tfResults['15min'] \|\| '5min' \|\| '1min'` + test |

### Group 3 — ENGINE SCORING (design decisions — MUST flag in PR, user/Phase-F decides)
| # | Fix | File | Spec |
|---|-----|------|------|
| F3-10 | BOS double-count (PR6-B14) | `structure.js` | guard: recentEvents BOS contribution only when `!bos` (or filter barsAgo===0 overlap) + repro test (current-bar BOS = 2.0, not 2.5) |
| F3-11 | RSI middle-zone (PR6-B15) | `timeframe.js` | REMOVE `rsi>=55 mU+=0.25` / `rsi<=45 mD+=0.25` under `trending===false` — **behavior change, justify in PR** + test (RANGING RSI 62 vs 66 no contradictory flip) |
| F3-12 | +3 HIGHEST dead code (PR7-B21) | `voteFilters.js` | remove the `HIGHEST → +3` branch (block zeroes it anyway) — justify + test |
| F3-13 | crypto session weights (PR7-B25) | `filters.js`/`config.js` | decide: crypto pairs skip SESSION_PAIR_WEIGHTS (sessionMult=1 for non-forex) OR document. **User decision** — flag in PR |

### Group 4 — LOW / LATENT / TEST INFRA
| # | Fix | File | Spec |
|---|-----|------|------|
| F3-14 | scheduledScan noPush (PR6-B13) | `scheduledScan.js` | `handleSignalRaw(pair, env, ctx, { noPush: true })` + test (scanner never pushes) |
| F3-15 | AI on D2-blocked (PR7-B17) | `engine.js` | `if (d2Audit) aiTargetDir = null;` (skip LLM calls) + test (no AI call when D2 fired) |
| F3-16 | time-invariant fixtures (CLOCK-001/PR7-B22) | `d2_tests.mjs`, `probe_tests.mjs` | inject fixed session (optional `now`/session param on engine) so tests pass any hour + run both at 12-16 UTC to prove |
| F3-17 | cbShadow convention (PR7-B18) | `health.js` | exclude `cbShadow` from `/api/history` decided (match stats) — flag as convention choice + test |
| F3-18 | winRate semantics (PR7-B19) | `stats.js` | compute winRate over last WIN_RATE_LOOKBACK decided rows (ring buffer) OR rename config + document all-time. **User decision** — flag in PR |
| F3-19 | decideTfDirection fallback (PR7-B20) | `voteFilters.js` | require winning-side confluence ≥ MIN_CONFLUENCE in fallback branch + test |

### NOT IN SCOPE (Phase-F, no code)
- BUG-023 entryHit — analysis-only (corrected window metric = separate instrumentation task; user decision)
- BUG-024 forex SELL — Phase-F probe monitoring (already running); DO NOT flip SELL logic

---

## AGENT INSTRUCTIONS (round 3)
1. **Consolidate numbering:** both PRs collide on BUG-011..016. Produce ONE canonical `BUG_REPORT.md` with unique IDs (suggest PR#6's become BUG-026..032 + CLOCK-001, or renumber by group). Note the mapping in the PR body.
2. **Work PR-first:** new branch off `main` (0c6d358), one PR containing ALL round-3 fixes + consolidated report. NEVER push main directly.
3. **Tests:** extend `fix_tests.mjs` with F3-01..F3-19 unit tests (real modules, network stubbed — same pattern as before). All existing suites must stay green: `fix_tests` (77+new), `phase10_integration` 19/19, `phase7_*`, `d2_tests`, `probe_tests`, `entry_hit_tests`, `fx_mode_tests`, `r71_tests` 113P/3F unchanged.
4. **Design decisions (F3-02, F3-11, F3-12, F3-13, F3-18):** implement your recommendation BUT clearly flag each in the PR description with rationale — the user decides before merge.
5. **No "done" claims in chat** until code is on GitHub and I re-verify (full diff + run every suite myself + live API check).
