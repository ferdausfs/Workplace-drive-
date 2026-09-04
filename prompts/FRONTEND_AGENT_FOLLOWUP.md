# 📢 Frontend Architect-কে Follow-up নির্দেশনা (Push + Full Report)

> **এই নির্দেশনা পড়ুন, তারপর কাজ করুন।** আপনার আগের CHANGES.md-এ কাজের description ছিল,
> কিন্তু **GitHub-এ কিছুই push হয়নি** — verify-তে ধরা পড়েছে:
> - GitHub HEAD এখনও `c861382` (পুরনো)
> - `src/components/signal/`, `src/hooks/useSignal.ts`, `src/lib/api.ts` — নেই
> - `App.tsx` এখনও 1911 লাইন
>
> **রিপোর্ট দিলেই হবে না — আসল কোড GitHub-এ push করুন।** নিচে ঠিক কী করতে হবে।

---

## ১. আপনার কাজ আসলেই **GitHub-এ push** করুন

```bash
cd <আপনার Ftt-app-002 clone>
git status                # আপনার পরিবর্তিত/নতুন ফাইল দেখুন
git add -A
git commit -m "Frontend architecture: modular refactor (components/hooks/lib)"
git push origin main
```

**push-এর পরে verify:**
```bash
git log --oneline -1      # নতুন commit দেখাতে হবে
git ls-remote origin HEAD # remote-ও নতুন দেখাতে হবে
```

> ⚠️ **Push না করলে কাজ সম্পূর্ণ হবে না।** Reviewer GitHub-এর HEAD-থেকে verify করে —
> remote-এ না থাকলে সব fail।

---

## ২. CHANGES.md — **সম্পূর্ণ details সহ** আপডেট করুন

আগের report-এ overview ছিল — কিন্তু এটা যথেষ্ট না। **প্রতিটা ফাইলের তালিকা সহ** লিখুন:

### 2a. File-by-file change log (প্রতিটা ফাইলের জন্য):

```
## File Changes

### নতুন ফাইল (added)
| ফাইল | কী আছে |
|---|---|
| `src/lib/api.ts` | API client: fetchSignal(pair, mode?), fetchHistory, fetchStats, fetchHealth, reportSignalResult — typed |
| `src/hooks/useSignal.ts` | Signal fetching + abort + history tracking |
| `src/hooks/useMode.ts` | FTT/FX/BOTH mode + localStorage |
| `src/hooks/useHealth.ts` | Worker health check |
| `src/hooks/useLocalStorage.ts` | Typed localStorage hook |
| `src/components/signal/MaterialSignalCard.tsx` | Main signal card (default export) |
| `src/components/signal/ConfidenceRing.tsx` | Confidence progress ring |
| `src/components/signal/ModeChip.tsx` | FTT/FX/BOTH indicator |
| `src/components/signal/FillBadge.tsx` | INSTANT/PENDING fill status |
| `src/components/signal/SltpChip.tsx` | SL/TP levels (FX mode) |
| `src/components/history/HistoryRow.tsx` | History row (touch-delete) |
| `src/components/history/StatCard.tsx` | Simple stat |
| `src/components/history/ServerStatsCard.tsx` | Server WR display |
| `src/components/settings/SettingRow.tsx` | Settings row |
| `src/components/settings/SignalModeToggle.tsx` | Mode cycle control |
| `src/components/settings/HealthPill.tsx` | System status |
| `src/components/common/MarketClosedCard.tsx` | Market closed UI |
| `src/components/common/CircuitBreakerCard.tsx` | Cooldown UI |
| `src/components/common/NavButton.tsx` | Bottom nav button |

### পরিবর্তিত ফাইল (modified)
| ফাইল | কী বদলালো |
|---|---|
| `src/App.tsx` | 1912 → 1106 lines; inline logic hooks-এ সরানো; composition only |
| `src/types.ts` | যোগ: ServerPairStats, ServerAggregateStats, CoverageSummary, isAggregateStats, TradableSignalData, HistoryEntry |

### মুছে ফেলা (deleted) — **কোনোটা থাকলে লিখুন**
| ফাইল | কেন |
|---|---|
| (যদি থাকে) | ... |
```

### 2b. **Feature preservation checklist** — প্রতিটা feature নিশ্চিত:

```
## Feature Preservation (verify-এ check হবে)

- [ ] Signal card: direction, confidence ring, grade, entry, expiry, HTF, regime, structure
- [ ] Mode chip (⏱ FTT / 💹 FX / 🔄 BOTH) — **আসলেই render হয়** (আগের bug!)
- [ ] Fill badge (⚡ INSTANT / ⏳ PENDING / fill not yet resolved)
- [ ] SL/TP chips (FX/BOTH mode-এ)
- [ ] Scanner (multi-pair, add/remove, notifications)
- [ ] Board (all-pairs, WR+n, tie flags)
- [ ] History (rows, entry hit/miss, filter, report)
- [ ] Analysis (timeframes, indicators, AI)
- [ ] Settings (mode toggle, auto-refresh, System Status/health, PIN/backup)
- [ ] Ticker, premium UI
```

### 2c. **Verification proof** — build + real-render:

```
## Verification

- [ ] `npx tsc --noEmit` → 0 errors
- [ ] `npm run build` → pass (single-file dist)
- [ ] Headless browser-এ load → **rendered DOM-এ Mode chip/fill badge/SL-TP আসলেই দেখা যায়**
      (এইটা আগের fail ছিল — নিশ্চিত করুন)
- [ ] Screenshot (যদি পারেন) — প্রমাণ হিসেবে
```

---

## ৩. Reviewer (independent) যা verify করবে

1. **GitHub HEAD-এ আপনার commit** — push হয়েছে কিনা
2. **`tsc --noEmit`** — 0 errors
3. **`npm run build`** — pass
4. **Real-browser** — rendered DOM-এ Mode/fill/SL-TP chips (আগের bug)
5. **No regression** — আগের working (`7f39e25`) থেকে কোনো feature হারায়নি
6. **Honesty** — fake win-rate নেই, n-সহ
7. **Code quality** — modular, typed, no god-file

**এই ৭টা pass না করলে — কাজ অসম্পূর্ণ।**

---

**এখন করুন:** (1) push, (2) এই template অনুযায়ী CHANGES.md আপডেট, (3) verification proof যোগ।
তারপর reviewer verify করবে। 🎯
