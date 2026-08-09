# 🎨 Frontend Architect — Premium Signal Pro App Rebuild (HIGH-IMPACT PROMPT)

> **সতর্কতা:** This is a HIGH-BAR prompt. Arena.ai will route this to a powerful
> frontend-capable model. Deliver production-grade work — a mid-tier effort will
> be rejected by the independent reviewer (spec §9).
>
> **তারিখ:** ২০২৬-০৮-০৫ · **App:** Signal Pro (FTT) · **Repo:** `github.com/ferdausfs/Ftt-app-002`
> **Live:** `https://fttfs-navy.vercel.app` · **Stack:** React 19 + TypeScript + Vite 7 + Tailwind 4 + `vite-plugin-singlefile`

---

## 1. MISSION (এক লাইনে)

**FTT Signal Pro** — একটি premium, dark, glassmorphism binary-options + forex signal
app — কে **world-class UI/UX + clean frontend architecture** দাও: pixel-perfect,
smooth, honest, production-grade. **একটাও function হারাবে না, কোনো bug-ও আসবে না।**

## 2. HARD RULES (ভাঙলে FAIL)

1. ❌ **কোনো feature/function সরানো যাবে না।** App-এ এখন যা আছে (Signal card,
   Scanner, Board, History, Analysis, Settings, ticker, Signal Mode toggle,
   fill status, entry hit/miss) — সব থাকতে হবে। **ভাঙা = fail।**
2. ❌ **Bug-মুক্ত বাধ্যতামূলক।** Render না হওয়া element, dead state, broken
   navigation — কিছুই চলবে না। আপনার কাজ ১০০% working।
3. ✅ **UI/UX premium + minimal + dark glassmorphism.** এটা আপনার প্রমাণের জায়গা।
4. ✅ **Clean architecture:** component separation, typed props, no god-file.
   App.tsx (১৮০০+ লাইন) — এটা ভেঙে modular করতে হবে (চিন্তা করে, risk ছাড়া)।
5. ✅ `tsc --noEmit` 0 errors + `npm run build` pass (single-file).
6. ✅ Dark-first, Tabular numerals, Bengali+English UI, responsive (mobile-first).
7. ⚠️ **Worker API contract অপরিবর্তিত** — `API_BASE`/endpoints/types ঠিক রাখো।
   শুধু frontend improve করো। Worker-এর `/api/signal` response-এর shape-এর সাথে
   types মেলাতে হবে (fillStatus, mode, fxLevels, entryHit — ইতিমধ্যে types-এ আছে)।

## 3. DESIGN LANGUAGE (বাধ্যতামূলক ভিজ্যুয়াল স্পেক)

| টোকেন | মান | ব্যবহার |
|---|---|---|
| Background | `#0B0E14` + subtle radial teal/gold glow | premium depth |
| Primary | `#4DD0E1` (teal) | action, active, highlight (এক স্ক্রিনে এক জিনিসে) |
| Secondary | `#E3B23C` (gold) | zakat/spiritual numbers শুধু |
| Cards | glass `rgba(255,255,255,0.03)` + blur 16–24px | surface |
| Border | hairline `rgba(255,255,255,0.07)` | definition |
| Radius | 10/14/20/28px | scale |
| Spacing | **4pt grid** (4,8,12,16,20,24,32,48) | perfect rhythm |
| Type | Hind Siliguri + Noto Naskh Arabic (self-hosted), Inter fallback | |
| Numerals | `font-variant-numeric: tabular-nums` — **সব নাম্বারে** | |
| Motion | 150–250ms ease-out, press scale 0.97, count-up, `prefers-reduced-motion` | |
| Accessibility | touch ≥44px, aria-label, contrast ≥4.5:1 | |

**Premium বোঝায়:** সূক্ষ্ম glow, সঠিক shadow layering, হায়ারারকি, whitespace,
micro-interaction। **কিশ-ভরা নয়** — restraint-ই premium।

## 4. SCREENS (সব rebuild করতে হবে — বর্তমান function intact রেখে)

1. **Home** — Signal hero (MaterialSignalCard): বড় direction, confidence ring,
   Mode chip (⏱ FTT / 💹 FX / 🔄 BOTH), fill status (⚡ INSTANT / ⏳ PENDING),
   SL/TP chips (FX-এ), entry/expiry, HTF/regime/structure, AI row, filters।
   + Market ticker + Board access।
2. **Scanner** — multi-pair live scan, chips, status, add/remove, notifications।
3. **Board** — all-pairs dashboard: live badges, WR+n, tie flags, breakeven honesty।
4. **History** — rows with WIN/LOSS + **entry hit ✓ / entry miss ⚠**, stats,
   filter (pair/time), report buttons।
5. **Analysis** — multi-timeframe, indicators, structure, AI validation detail।
6. **Settings** — mode toggle (FTT/FX/BOTH), auto-refresh, System Status
   (worker version + endpoint live checks + update awareness), PIN/backup/theme।

**Honesty-rule:** কোনো fake win-rate না — প্রতিটা সংখ্যা sample size (n) সহ।
"75% guaranteed" — কখনো না। **এই honesty-টা UI-তেও visible** (breakeven note)।

## 5. ARCHITECTURE (clean, modular — App.tsx ভাঙতে হবে)

```
src/
  app/            (providers, router/tab state machine)
  components/     (atomic + composite UI)
    signal/       (SignalCard, chips, confidence ring, fill badge...)
    scanner/      (ScannerView, ScannerRow, pair chips...)
    board/        (BoardView, PairCard, stats...)
    history/      (HistoryView, HistoryRow, filter...)
    settings/     (SettingsView, SystemStatus, mode toggle...)
    common/       (Card, Chip, Toggle, ProgressRing, EmptyState, Toast...)
  hooks/          (useSignal, useHealth, useLocalStorage, useMode...)
  lib/            (api client, formatters, honest-stats)
  styles/         (tokens, theme)
```

- **App.tsx max ~300 lines** (state machine + composition only)।
- Prop-drilling কম, custom hooks-এ logic। Context যেখানে অর্থপূর্ণ।
- **No dead code, no unused imports, no any.**

## 6. DATA FLOW (types worker-এর সাথে মিলতে হবে)

```ts
// /api/signal → signal (SignalData):
// finalSignal, confidence, grade, mode?: 'ftt'|'fx'|'both',
// fillStatus?: 'INSTANT'|'PENDING_ENTRY', entryPrice, currentPrice,
// entryDistancePct, fxLevels?: {entry,sl,tp,rr}, structureVerdict,
// aiValidation, marketRegime, recommendations, expiry, filtersApplied...
// /api/history → signals[] (result, entryHit?, ...)
// /api/stats, /api/pairs, /api/signals/latest, /health
```

আপনার UI-তে **undefined-safe** — worker field না দিলেও crash হবে না (default/—)।

## 7. MOTION & PREMIUM TOUCHES (যা আপনার skill দেখাবে)

- Smooth screen transition (tab switch) — 200ms
- Confidence ring animation, count-up numbers
- Skeleton/shimmer loading
- Pull-to-refresh feel (home)
- Focus/active states premium
- **Reduced-motion:** সব transform/opacity 0.001s

## 8. HONESTY IN UI (প্রতিটা সংখ্যা)

- Win-rate: always `n=...` সাথে
- Breakeven note: "at 80% payout breakeven is 55.6%"
- DOT/USD tie flag (data-quality) — Board-এ
- **No fake 75%+ claims — এটা brand**

## 9. INDEPENDENT REVIEWER (আপনাকে পর্যবেক্ষণ করবে)

> একজন independent reviewer (analysis-capable agent) আপনার কাজ verify করবে:
> 1. **Build gate:** `tsc --noEmit` 0 + `npm run build` pass
> 2. **Function inventory:** প্রতিটা screen/feature reachable + working
> 3. **Real-browser check:** headless browser-এ load → rendered DOM-এ
>    Mode/fill/SL-TP chips আসলেই দেখা যায় (আগের bug-টা ধরা পড়েছিল এখানে)
> 4. **No regression:** আগের working commit (`7f39e25`) থেকে কোনো feature হারায়নি
> 5. **Honesty:** কোনো fake win-rate নেই, n-সহ
> 6. **Code quality:** modular, typed, no god-file

**তাই আগে থেকে নিশ্চিত করো:** আপনার কাজ build + real-render + no-regression
— ৩টা-ই pass। তবেই premium বলে গন্য হবে।

## 10. DELIVERY

- সব commit (আপনার git identity), clean messages
- `CHANGES.md`: কী বদলালো, কোন ফাইল, কোন feature যোগ/সংশোধন (delete = fail)
- Build + tsc + (যদি সম্ভব) headless-browser screenshot প্রমাণ হিসেবে

---

**আদর্শ:** "Apple-grade polish, no-broken-parts." এটাই benchmark। দাও। 🎨
