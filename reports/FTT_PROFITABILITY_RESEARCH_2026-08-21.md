# FTT Engine Profitability Research — 2026-08-21

**প্রশ্ন:** engine-এ এখন কী করা যায় যাতে single accuracy (WR) বাড়ে? Signal কম হলেও চলবে, indicator add/remove চলবে — engine-টা profitable বানাতে হবে।

**Method:** worker source (engine.js, voteFilters.js, grade.js, config.js) + ৬,২৫৯ decided signal-এর full feature analysis (bivariate + combination + chronological validation)। Honest, evidence-only।

---

## ১. Engine-এর আসল অবস্থা (data থেকে)

| Metric | Value |
|---|---|
| Full forward WR | 43.5% (CI 42.3–44.8) |
| POST-FIX-EH WR | 48.0% (n=1,797) |
| Breakeven (80% payout) | 55.6% |
| D4 ML (LEGIT, signal-time features) | 34.1% confident-only → no edge |

**Core directional edge ~45-48%** — মডেল/engine দিক ঠিক ধরতে পারে না বরং coin-flip-এর নিচে। Breakeven-এ পৌঁছাতে +7-10pp দরকার।

## ২. কী কী ভাঙা আছে (fix-যোগ্য)

### A. Grade/confidence system উল্টো কাজ করে (real current bug)
Post-calibration-এর পরেও:
```
grade B  → 50.4% WR (n=383)   ← সেরা
grade C  → 46.5% WR (n=303)
grade A+ → 44.2% WR (n=215)   ← সবচেয়ে খারাপ
```
A+ মানে "excellent" বলা হয়, অথচ A+ সবচেয়ে বেশি লস দেয়। Confidence bucket-ও non-monotone (80-89 সবচেয়ে খারাপ)। অর্থাৎ **"high confidence/grade = ভালো trade" ধারণাটা data-য় ভুল**।

### B. Structure verdict উল্টো (ranging artifact)
- RANGING regime-এ structure **AGAINST** (47.5%) > **ALIGNED** (41.1%) — structure-এর confirm করা মানে লস (mean-reversion)।
- Calibration table-এ এটাই বেক করা আছে (structWR: AGAINST 0.497 > ALIGNED 0.423)।

### C. AI-agreement কোনো value add করে না
aiAgreed=True (43.8%) ≈ aiAgreed=absent (43.4%) — Cerebras/Groq validation-টা WR-এ কোনো প্রভাব ফেলে না।

## ৩. কোথায় real edge আছে (ranked by evidence)

| Feature | WR | n | Signal-time? |
|---|---|---|---|
| **fillStatus = PENDING_ENTRY** (entryDist ≥ 0.05%) | **57.9%** | 178 | ✅ |
| entryDist ≥ 0.1% | 60.0% | 95 | ✅ |
| ATR percentile < 50 (calm market) | 53.6% | 289 | ✅ |
| CRYPTO only (forex বাদ) | 46.6% vs forex 34% | 2517 | ✅ |
| marketRegime ≠ TRENDING | — | — | ✅ |
| sessionQuality ≠ HIGHEST (forex) | 11.6% WR → বাদ | 86 | ✅ |

**সবচেয়ে শক্তিশালী mechanism (non-tautological):** PENDING_ENTRY মানে entry price বর্তমান price-এর চেয়ে দূরে → "wait for pullback" setup। Chase-এর বদলে ভালো price-এ entry → WR 46.9% (INSTANT) থেকে 57.9% (PENDING)।

**সতর্কতা:** entryHit=False → 75% WR দেখাবে, কিন্তু ওটা post-hoc tautology — pre-trade filter হিসেবে use করা যাবে না (সেটাই old bug ছিল, FIX-EH-তে ভাঙা হয়েছে)।

## ৪. যা বানালাম — SELECTIVITY GATE (PR-ready)

`quality over quantity` push-filter। History/API আগের মতো সব record করে (research intact), **শুধু Telegram push** হয় তখনই যখন signal evidence-backed bar pass করে:

1. **Crypto only** (forex 34% drag বাদ)
2. **TRENDING বাদ** (38.8% WR)
3. **requirePendingEntry** — শুধু wait-for-pullback (dist ≥ 0.05%) push
4. **maxAtrPercentile < 50** — calm market only

**Expected effect (data থেকে):** push হওয়া signal-গুলোর WR ~**57-60%** (point estimate, PENDING_ENTRY slice-এর ভিত্তিতে), signal count ~৭৬% কমে (~11/day)। CI এখনো wide (lower bound ~50-52) — forward data জমলেই narrow হবে।

**Patch:** `pr/ftt_worker_selectivity_gate.patch` (sha 0328d1c1…), 3 file, +97/−1। `node --check` pass ✅, gate logic ৭টা case-এ test ✅।

## ৫. Honest expectation (কোনো hype নয়)

- Selectivity gate → push-subset WR **~57-60%** প্লাসিবল, **কিন্তু forward data-য় prove করতে হবে**। গ্যারান্টি নেই।
- **75%+ WR data-supported নয়** — engine-এর core edge ~48%, selectivity শুধু ভালো slice বেছে নেয়, নতুন edge তৈরি করে না।
- Grade/calibration inversion fix (FIX-A) আলাদা কাজ — ranking ঠিক করবে, কিন্তু WR বাড়ানোর মূল lever এই gate-ই।

## ৬. পরের ধাপ (প্রস্তাবনা)

1. **Deploy gate** → 1-2 সপ্তাহ forward data জমা → WR measure (এখন আমি worker থেকে direct pull করি, তাই daily verify হবে)।
2. Gate-এর params tune (আরও strict/loose) — forward data অনুযায়ী।
3. **FIX-A (regime-conditional calibration)** — grade inversion ঠিক করতে, আলাদা PR।
4. Optional research: নতুন indicator (এখনকার core indicators-এ edge নেই, তাই নতুন signal source খুঁজতে হবে — এটা বড়, আলাদা scope)।
