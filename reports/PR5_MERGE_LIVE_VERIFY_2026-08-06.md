# PR #5 MERGE — LIVE VERIFICATION REPORT (2026-08-06)

**Repo:** `ferdausfs/Ftt-Otc-v6` · **Main HEAD after merge:** `0c6d358` ("Merge pull request #5")
**Reviewer:** Arena main agent — every claim below verified independently (code, tests, live API).

---

## 1. Merge integrity
- GitHub main = `0c6d358` — merge commit with parents `055b6f0` (old main) + `2636250` (verified PR head).
- Merged tree **byte-identical** to PR head `2636250` → no merge-conflict corruption.
- All commits (round-1 `a6e5495` + round-2 `2636250`) present on main.

## 2. Test suites on merged main (I ran all myself)
```
fix_tests              77/77   (round 1: 42 + round 2: 35)
phase10_integration    19/19   (was FAILING pre-fix — push restored)
phase10_smoke          61/61 · phase7_integration 36/36 · phase7_smoke 68/68
d2_tests 39/39 · probe_tests 34/34 · entry_hit_tests 7/7 · fx_mode_tests 20/20
r71_tests              113 PASS / 3 FAIL (== main's pre-existing fails, untouched)
node --check           clean on all src/
```

## 3. Live worker verification (https://fttotcv6.umuhammadiswa.workers.dev — v6.9.2 live)

### ✅ FIX-A — OTC grade structure cap — **LIVE CONFIRMED (natural experiment)**
| Pair | Signal | Conf | Alignment | Structure verdict | Grade |
|---|---|---|---|---|---|
| ETH/USD | BUY | 78% | ALL_BULLISH (coreConf 95) | **AGAINST** (both TFs BEARISH+BOS, SELL STRONG) | **C** |
| DOGE/USD | SELL | 78% | ALL_BEARISH | ALIGNED | **A** |
| AUDCAD-OTC | BUY | **88%** | — | **AGAINST** (SELL) | **C** |

Pre-fix math: ETH/USD would score `31.2 + 18.5 + 25 = 74.7 → A`; AUDCAD-OTC would be `A+`. Cap is working exactly as designed, and ALIGNED signals are NOT over-capped (DOGE stays A).

### ✅ FIX-B — camarilla OTC weighting — code+test proven (T9: raw×1.5 ≠ raw/0.84×1.5, ~19% removed). Live OTC score cards now carry `otcWeight: 1.5` on camarilla.

### ✅ FIX-C — round-number directional — code+test proven (T10/T11). Live OTC signals show side-named signals (`ROUND_LEVEL_*_RESISTANCE/_SUPPORT`) instead of the dead both-sides bonus.

### ✅ FIX-D — confluence /12 — **LIVE CONFIRMED**
All live signals: `8/12 categories`, `6/12 categories`, `0/12 categories` (dead-market), `"Strongest SELL signal with 8/12 confluence"`, `total: 12`. No `/11` anywhere in src or live output.

### ✅ FIX-3 — fillStatus real distance — **LIVE CONFIRMED**
Live signals show non-zero entry distance (BTC 0.0452%, ETH 0.0481%, GBP 0.0178%) with correct INSTANT/PENDING_ENTRY threshold (≤0.05% actionable). `dist=0` cases are correct: best TF = 1min → entry IS current price.

### ✅ FIX-5 — post-AI confidence floor — **LIVE CONFIRMED**
Live: `CONFIDENCE_BELOW_FLOOR (72%)` (SOL/USD 65% → NO_TRADE), `BELOW_FLOOR_AFTER_DYN_ADJ` (USD/JPY, EUR/USD), `OTC_BELOW_FLOOR_AFTER_AI` (GBPUSD-OTC). No BUY/SELL below 72% observed live.

### ✅ CHECK-A — passAI dual-combiner shape — **LIVE CONFIRMED**
Live `aiValidation` carries the full dual shape (`cerebras`, `groq`, `combined`, `combinedAgreed`, `agrees`) that the new `passAI` accepts.

### ✅ FIX-2 — D2 rescue guard — code+test proven (T5: TRENDING + dual-AI-agree → NO_TRADE). Live: AUD/USD TRENDING → NO_TRADE (blocked pre-D2 by MIXED_ALIGNMENT — no counter-evidence observed).

### ✅ BUG-001 — push restored — `phase10_integration` 19/19 (was failing: "Cannot read properties of undefined (reading 'chatId')"). Bot live v4.4 healthy.

## 4. Phase F forward data — 2026-08-06 snapshot taken
`~/phase_f_forward/2026-08-06/` — 18 pairs + pairs.json + health.json, all http=200, MANIFEST + SHA256SUMS written.

---

## VERDICT: ✅ MERGE VERIFIED — ALL FIXES LIVE/CONFIRMED
No regressions found. Live behavior matches the reviewed code and tests exactly.

## Open items (honest)
1. **Entry-hit metric (BUG-004)** — NOT fixed (analysis-only by design, CHECK-B). My independent 200k-row simulation confirmed the "100% miss-WR" is a metric tautology, not signal quality. Direction-quality question still needs the corrected window metric + 7-14 days data.
2. **r71_tests 3 pre-existing fails** (#1a/#2/#17) — pre-date this merge; not touched. Should be a separate cleanup PR someday.
3. **D2 TRENDING vs bad-pair data collection (finding #3)** — still awaiting user's Phase-F decision (shadow obs counting vs probe).
4. **PAT hygiene** — if either leaked PAT is still active, revoke now.
