# BOT (ftt-telegram-bot) — AGENT PROMPT (round 2: 2 confirmed bugs + integration re-verify)

**Repo:** `ferdausfs/ftt-telegram-bot` · **Main HEAD:** `3570f37` (menu redesign merged, live v4.4)
**Reviewer:** Arena main agent — verify everything on GitHub + live after you push. No "done" claims until code is on a branch.

## Context (verified by reviewer 2026-08-06)
- Bot is live (`https://ftt-telegram-bot.umuhammadiswa.workers.dev`, v4.4), `node --check` clean.
- **The WORKER (Ftt-Otc-v6) is now round-3 live and its response shape changed.** Two bugs below are the bot's own copies of worker bugs that were fixed worker-side but NOT ported to the bot. Both are confirmed in code.

## CONFIRMED BUGS (fix both)

### BUG-B1 (High) — bot's own `passGrade` drops A+ signals for grade-filtered users
- **File:** `src/index.js:536-540`
- **Code:**
  ```js
  const passGrade = (sig, f) => {
    ...
    return f === 'A' ? g === 'A' : f === 'AB' ? ['A', 'B'].includes(g) : true;
  };
  ```
- **Problem:** `'A+'` is neither `'A'` nor in `['A','B']` → any user with grade filter `A` or `AB` never receives A+ signals (the engine's best setups). The worker fixed the identical bug (F3-03); this copy was missed.
- **Fix (mirror worker F3-03):** `f === 'A' ? ['A+','A'].includes(g) : f === 'AB' ? ['A+','A','B'].includes(g) : true`.
- **Proof:** unit test — `passGrade({grade:{grade:'A+'}},'A')===true`, `('AB')===true`, and grade B still passes AB, grade C rejected for A/AB.

### BUG-B2 (High) — bot's own `passAI` is dead with the worker's dual-combiner shape → AI-Only mode never matches
- **File:** `src/index.js:547-551`
- **Code:**
  ```js
  const passAI = (sig, aiOnly) => {
    if (!aiOnly) return true;
    return sig.aiValidation?.status === 'OK' && sig.aiValidation?.agrees === true;
  };
  ```
- **Problem:** the worker's standard-engine `aiValidation` is now the **dual-combiner object** `{ cerebras, groq, combined, combinedAgreed, agrees }` — there is **no top-level `status`**. So `sig.aiValidation?.status === 'OK'` is always `undefined !== 'OK'` → **any user with AI-Only mode ON receives zero signals** (same class of bug as worker BUG-006/CHECK-A, fixed worker-side but not ported).
- **Fix (mirror worker CHECK-A):**
  ```js
  const v = sig?.aiValidation;
  if (!v) return false;
  const status = v.status || (v.combined && v.combined.status);
  const agreed = v.agrees !== undefined ? v.agrees : v.combinedAgreed;
  return status === 'OK' && agreed === true;
  ```
- **Proof:** unit test — dual shape `{combined:{status:'OK'}, combinedAgreed:true}` → true; OTC shape `{status:'OK', agrees:true}` → true; `{status:'SKIPPED'}` → false (D2-blocked must NOT pass AI-Only).

## Integration re-verify (worker round-3 response shapes)
1. **fillStatus on OTC:** worker OTC signals now carry `fillStatus`/`entryPrice`/`currentPrice`/`entryDistancePct` — confirm the bot's signal message (line ~520 `fillStatus: sig.fillStatus || 'INSTANT'` and the fill badge/line in fmtSignal) renders them for OTC too, not just standard.
2. **Grade `N/A`:** bot only pushes BUY/SELL, but result/history/daily-summary lines read `sig.grade?.grade` — confirm a NO_TRADE never reaches those paths (it shouldn't), and that `[N/A NO_TRADE]` can never appear in a pushed message.
3. **mode=fx:** the worker's `mode=fx` now forces fresh (never cached) — confirm the bot's fx fetch still works and SL/TP chips show.
4. **UTC candleTimes:** worker times are UTC now — confirm countdown/expiry math in the bot doesn't assume a local offset.
5. `node --check` + your existing test/smoke scripts all green; add the new unit tests above.

## Workflow
- PR off `main` (`3570f37`), never push main directly.
- PR body: fix table (bug → file/line → change → test proof), plus the integration re-verify results (live worker samples).
- After you push: I diff-read, run `node --check` + tests, live-check a push path, approve before merge.

## Out of scope
- No menu redesign (that's live), no new features. This round = the 2 confirmed bugs + integration re-verify.
- Do not touch the worker repo from here.
