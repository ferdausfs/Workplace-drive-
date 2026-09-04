# 🔬 FTT Worker — Deep Bug-Hunt Audit Prompt (HIGH-BAR)

> **এটা একটি কঠোর, high-bar audit। Arena.ai-র সেরা model-কে দেওয়া হবে।**
> আপনার কাজ: FTT worker-এর **গভীর bug/অসমঞ্জসতা খুঁজুন** — surface-level নয়।
> **প্রতিটা finding প্রমাণ-সহ** — কোড লাইন, data, বা logic দিয়ে।
>
> **Repo:** `github.com/ferdausfs/Ftt-Otc-v6` · **Live:** `https://fttotcv6.umuhammadiswa.workers.dev`
> **Stack:** Cloudflare Worker + KV · JS (ESM) · v6.9.2

---

## 0. কাজের ফ্লো (এইটা follow করুন — গুরুত্বপূর্ণ)

```
১. Clone + code পড়ুন (সব src/)
২. Live API-র সাথে code মিলিয়ে দেখুন (endpoints, response shape)
৩. Bug/অসমঞ্জসতা খুঁজুন — নিচের checklists
৪. Report লিখুন (BUG_REPORT.md) — PR branch-এ commit করুন (merge না)
   → reviewer দেখে বলবে change করবে কিনা
৫. Reviewer approve করলে — change করে merge
```

> ⚠️ **সরাসরি main-এ change/push নয়।** প্রথমে **BUG_REPORT.md** PR branch-এ
> → reviewer (independent) দেখবে → "এইটা ঠিক করো" বললে change করবে।

---

## 1. AUDIT AREAS (প্রতিটা গভীরে — surface না)

### A. Signal Engine (`src/signal/`)
- **voteFilters.js** — weighted vote, alignment, confidence, filters:
  - `decideTfDirection` — threshold/conflict logic ঠিক?
  - `MIN_CONFLUENCE=5`, `MIN_CONFIDENCE_FLOOR=72` — logic consistent?
  - HTF block, session, candle consistency, FVG, dead-market — edge cases?
- **timeframe.js** — score building:
  - RSI/stochastic/momentum — **mean-reversion vs trend** logic (RANGING-এ SELL bias?)
  - structure multiplier — CHoCH/BOS — symmetric?
- **engine.js** — pipeline order:
  - D2 blocks (TRENDING/BAD_PAIR/HIGHEST), AI rescue path — **rescue-তে block override?** (আগের bug!)
  - FX mode, fillStatus, entryHit — consistent?

### B. History / Stats (`src/history/`)
- **stats.js** — WIN/LOSS logic, tie convention, `fetchExpiryPrice` (1-min candles, ±5min window)
- **entryHit shadow** — low/high-থেকে entry-hit calculation — **কোনো edge case?** (tie, gap, wrong direction?)
- **d2store/probeStore** — dedup, cap, resolver — fail-open ঠিক?
- KV keys (`sig:`, `pending:`, `stats:`, `cb:`, `shadow:`, `d2obs:`, `probe:`) — collision/leak?

### C. API Handlers (`src/handlers/`, `src/index.js`)
- **signal.js** — pair normalization, cache, circuit breaker, push — edge cases?
- **index.js** — routing, query params (`mode=fx`, `nopush`), cron (`*/5`, `*/2`) — সব handler-এ reachable?
- **/api/stats, /api/history, /api/report, /api/batch** — response shape consistent? error handling?

### D. Live-vs-Code mismatch
- Live API-র response-এ code-এর সাথে mismatch আছে? (field নাম, shape, error)
- `structureAudit`/`entryHit`/`fxLevels` — public-এ leak নেই তো?

### E. Known-issue re-check (আগের findings — এখনও আছে?)
- **AI rescue override D2 block** — TRENDING block bypass (আগে প্রমাণিত 242 ট্রেড rescue-তে)
- **Forex SELL weak** (~20% WR) — mean-reversion RSI-র কারণে?
- **DOT/USD tie artifact** (28% ties)
- **Entry-hit paradox** (hit=12.7%, miss=100% — 08-05) — engine-এর দিক-ভুল?

---

## 2. BUG_REPORT FORMAT (প্রতিটা finding)

```
### BUG-001 — [সংক্ষিপ্ত title]
- **Severity:** Critical / High / Medium / Low
- **Location:** `file.js:line`
- **Evidence:** (কোড snippet / live API response / data)
- **Impact:** (কী ভাঙে / ভুল ফলাফল)
- **Repro:** (কীভাবে দেখা যায়)
- **Suggested fix:** (এক লাইনে)
```

**Minimum 5-10 টা real bug/issue।** কোনো ফেক/পুনরাবৃত্তি না — প্রতিটা evidence-সহ।

---

## 3. VERIFY (নিজে)

- `node --check` সব changed files
- Live API-র সাথে 몇가지 request করে code-এর সাথে match দেখুন
- প্রতিটা bug-এর evidence সত্যি — fabricate করবেন না

---

## 4. PR (merge না — report প্রথম)

```bash
git checkout -b bug-audit
# BUG_REPORT.md লিখুন + (যদি ছোট fix থাকে, আলাদা)
git add -A && git commit -m "Bug audit: BUG_REPORT.md (findings)"
git push origin bug-audit
# PR খোলো → main
```

**PR body:** findings summary। **Change-গুলো reviewer বললে** — আলাদা commit-এ।

---

## 5. Reviewer (আমি) যা করবো

1. **BUG_REPORT.md পড়বো** — প্রতিটা finding-এর evidence verify (code + live)
2. **কোনটা real, কোনটা না** — বলবো
3. **Change করবে কি না** — বলবো (প্রতিটা bug-এর জন্য: fix করো / skip)
4. Approve-র পর — agent change করে merge

---

**আদর্শ:** "Find the real bugs, prove them, don't fabricate." এটাই bar। 🔬
