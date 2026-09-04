# PROMPT: PHASE F INDEPENDENT DEEP-DIVE (multi-agent) — 2026-08-14

**কাকে:** যেকোনো independent AI agent (একসাথে একাধিক agent-কে দেওয়া যাবে — প্রতিটা আলাদাভাবে কাজ করবে)।
**Reviewer:** Arena main agent — প্রতিটা agent-এর রিপোর্ট আমি নিজে data-র সাথে verify করবো। **Agent-এর রিপোর্ট = raw material, truth না।**

---

## 0. Goal
FTT signal engine-এর Phase F forward window (2026-08-01 → 08-14, ৪,১৬১ decided signal)-এ
**নিজস্ব, স্বাধীন, সৎ** বিশ্লেষণ। আমরা খুঁজছি: (a) কোনো conditional slice 55.6% breakeven
(80% payout) **CI-সহ** ছাড়ায় কি না, (b) আমাদের আগের বিশ্লেষণে কোনো ভুল/লিকেজ/confound আছে কি না।

## 1. Data (আগে unpack করো)
```bash
mkdir -p phase_f_forward && tar -xzf data/phase_f_forward_2026-08-14.tar.gz -C phase_f_forward
```
- ১৮ pair-এর `/api/history` snapshot (2026-08-14 ~09:55Z), প্রতিটা JSON-এ `signals` array।
- **Baseline first (বাধ্যতামূলক):**
  ```bash
  python3 scripts/phase_f_baseline.py --data phase_f_forward
  ```
  → output-টা verbatim রিপোর্টে দাও। এটা নিশ্চিত করে সবাই একই data-র উপর বসে আছে।

## 2. NON-NEGOTIABLE PROTOCOL
1. **decided = WIN/LOSS only** (TIE/UNKNOWN বাদ)।
2. Forward window `timestamp >= 2026-08-01`; dedup by `id`।
3. **Breakeven 55.6%**, Wilson 95% CI। Slice "beats breakeven" তখনই বলবে যখন **CI lower bound > 55.6**।
4. **নতুন data invent করা যাবে না।** Data-তে নেই এমন price/signal বানাবে না। সব সংখ্যা data থেকে।
5. **entryHit ব্যবহার নিষিদ্ধ** signal-time model-এ (post-hoc; পুরনো metric ছিল tautology — LEGACY MISS WR=100%)। Corrected `entryHit` diagnostic-এ ব্যবহার করা যাবে, feature হিসেবে না।
6. **Chronological split** — কখনো shuffle করবে না (data day-clustered)। Train < test timestamp-এ।
7. **Multiple testing স্বীকার করো** — তুমি N-টা slice চেক করলে, found "edge"-কে Bonferroni-তে রিপোর্ট করো।

## 3. Investigate করো (pre-registered angles — এগুলোর বাইরে গেলেও ঘোষণা করে)
- Session/hour/dow slice (field: `session` list, `timestamp`)
- `marketRegime` × asset × direction cells (gate: ≥30/cell)
- `structureVerdict` / `alignment` / `aiStatus` / `aiAgreed`
- `signalIndicators` (rsi, adx, atrPct, atrPercentile, bbBandwidth, bbState, bestTF)
- grade ladder (A+/A/B/C) — কেন C > A+? কোনো confound?
- round-3 improvement-র confound check (asset-mix shift vs within-class)

## 4. Output format (একটা findings doc)
```
# PHASE F FINDINGS — <agent-name> — 2026-08-14
## Baseline (verbatim)
## 1. Findings (প্রতিটা: slice, n, WR, CI, gate-clear yes/no, Bonferroni note)
## 2. Method bugs / confounds in prior analysis (যদি পাও)
## 3. Negative results (যা edge দেয়নি — সমান গুরুত্বপূর্ণ)
## 4. Honest verdict (breakeven clear হলো কি না; hype নয়)
```
- File নাম: `PHASE_F_FINDINGS_<agent>_2026-08-14.md` → drive `reports/`-এ।

## 5. Reviewer workflow (আমি)
প্রতিটা রিপোর্ট আমি: (1) baseline number match করবো, (2) data-তে slice-গুলো নিজে re-run করবো,
(3) CI/method check করবো → verdict: **CONFIRMED / PARTIAL / OVERSTATED**। Overstated হলে agent বাদ।
একই slice একাধিক agent স্বাধীনভাবে confirm করলে সেটা শুধু তখনই গুরুত্বপূর্ণ যদি CI+holdout টিকে।

## 6. Reality check (মনে রাখো)
- একাধিক agent ≠ নতুন data। ৪,১৬১ row-ই থাকবে — শুধু perspective বাড়ে, sample না।
- নতুন data আসবে শুধু live worker চলতে থাকলে (forward window এখনো খোলা)।
- "Notun edge পাওয়া গেল" বলতে হলে: chronological holdout-এ CI lower > 55.6, এবং আমি reproduce করতে পারবো।
