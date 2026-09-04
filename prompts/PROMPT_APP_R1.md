# APP (Ftt-app-002) — AGENT PROMPT (bug-hunt + polish round 1)

**Repo:** `ferdausfs/Ftt-app-002` · **Main HEAD:** `3d2e876` (modular refactor, live on Vercel)
**Reviewer:** Arena main agent — verify everything on GitHub + I run `tsc`/`build` + live check after you push. No "done" claims until code is on a branch.

## Context (verified by reviewer 2026-08-06)
- App is live (`https://fttfs-navy.vercel.app`, HTTP 200), `tsc --noEmit` clean, `vite build` clean (354 KB single-file).
- Worker backend changed a lot under the app: **round-3 live** = NO_TRADE signals now carry `grade: {grade:'N/A', label:'NO_TRADE'}`, D2-blocked signals have `aiValidation:{status:'SKIPPED'}` (no `combined`), OTC signals now carry `fillStatus`/`entryPrice`/`currentPrice`/`entryDistancePct`, `/api/stats` winRate is now a **rolling 20-trade window** (`sampleSize` = window size), candleTimes are now UTC.
- My integration scan found the app handles these gracefully (NO_TRADE → "WAIT", `deriveAiStatus` handles SKIPPED, FillBadge handles null). **One cosmetic gap found (below) + the rest is your audit.**

## Confirmed finding (fix it)
- **APP-001 (Low, cosmetic):** `src/components/signal/MaterialSignalCard.tsx:79-87` — the grade chip color chain only styles `A+/A/B`, everything else falls to the orange "warn" style. With round-3, NO_TRADE shows `"N/A · NO_TRADE"` in warn-orange — visually looks like a warning for a signal that is simply "wait". Fix: for `grade === 'N/A'` use the neutral gray chip (like FillBadge's fallback), or hide the chip when `data.signal.finalSignal === 'NO_TRADE'`. Pick the cleaner UX and justify.

## Your audit scope (bug-hunt — do it properly, show evidence)
1. **Round-3 worker integration** — hit the live API and confirm every field the app reads still exists in the exact shape:
   - `/api/signal` NO_TRADE shape (`grade.grade='N/A'`, `aiValidation.status='SKIPPED'`, no `combined`)
   - OTC signals: `fillStatus`, `entryPrice`, `currentPrice`, `entryDistancePct`, `fxLevels` absent for FTT mode (SltpChip must no-op, not crash)
   - `/api/stats`: `winRate` is now a 0–1 decimal over a window; `sampleSize` = window size. Verify `formatServerWinRate` renders correctly for e.g. `1` (100%) vs `0.5`, and the "Lookback sample" label still makes sense.
   - `/api/history`: cbShadow rows now excluded from `decided/pending` but still in `signals[]` with `cbShadow:true` — verify HistoryView/HistoryRow/ServerStatsCard don't double-count or mislabel.
2. **Dead code / orphans:** `src/components/SignalHero.tsx` — I believe it is NOT imported anywhere (the real card is `signal/MaterialSignalCard`). Verify; if orphaned, delete it or wire it. Same pass for `components/analysis/` vs `components/` duplicates (IndicatorGrid, TimeframeCard exist in both folders).
3. **Error/edge paths:** timeouts (api.ts has 10–25s), abort handling, ErrorBoundary coverage, empty-history state, offline/fetch-fail state — anything that throws instead of showing a graceful fallback.
4. **Consistency:** mode toggle (FTT/FX/BOTH), filter chips, countdown timer vs UTC candleTimes (worker now UTC — confirm the app doesn't assume a local/other tz and show wrong countdowns).
5. **Type safety:** `tsc --noEmit` must stay clean after your changes; `npm run build` must stay green.

## Deliverable
- PR off `main` (`3d2e876`), never push main directly.
- Fix APP-001 + every real bug found. For each: file/line, repro (code or live API sample), fix, test proof (tsc + build + any unit test you add).
- Explicitly list what you checked and found CLEAN (with the live sample) — so we know the audit was real, not just "everything ok".
- After you push: I re-run tsc/build, diff-read every change, spot-check live endpoints, and approve before merge.

## Out of scope
- No design overhaul / new features. This is audit + fix + polish.
- Do not touch the worker repo from here.
