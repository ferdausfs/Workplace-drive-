# 🎨 NEW Frontend Architect — Complete Runbook (start → finish, push included)

> **নতুন agent-এর জন্য সম্পূর্ণ নির্দেশনা।** আগের agent মিথ্যা report দিয়ে বাদ পড়েছে
> (কোড লেখেনি, শুধু report দিয়েছে)। **আপনি আসল কোড লিখবেন + GitHub-এ push করবেন।**
> কাজ শেষে independent reviewer (আমি) verify করবো — শুধু কোড visible হলেই pass।

---

## 0. আপনার কাজের সম্পূর্ণ ফ্লো (এক নজরে)

```
১. GitHub-এ repo clone (PAT দিয়ে) → কোড পড়ুন
২. ফিচার/বাগ বুঝুন (সব function inventory)
৩. নতুন architecture-এ refactor + সব feature রাখুন
৪. Build + tsc + real-browser verify (নিজে)
৫. Commit + push (PAT দিয়ে) → GitHub-এ visible
৬. CHANGES.md লিখুন (আসল commit hash + proof সহ)
৭. Reviewer verify করবে
```

**এই ৭ ধাপ — একটাও বাদ না। বিশেষ করে ৫ (push) — এটাই আগের agent-এর fail ছিল।**

---

## ১. Repo + Access (PAT)

**আপনার জন্য সীমিত GitHub PAT দেওয়া হয়েছে** (শুধু `Ftt-app-002`, ৭ দিন expiry, Contents read/write)।

```bash
# Clone (PAT দিয়ে — URL-এ token বসিয়ে, অথবা credential prompt-এ)
git clone https://<TOKEN>@github.com/ferdausfs/Ftt-app-002.git
cd Ftt-app-002

# নিশ্চিত: আপনি main branch-এ, লেখার access আছে
git branch --show-current        # main
git remote -v                    # origin → আপনার repo (TOKEN সহ)
```

> ⚠️ **PAT গোপন রাখুন** — কোড/chat-এ না, environment variable বা secure store-এ।
> কাজ শেষে revoke হবে (মালিক করবেন)।

**আগের মিথ্যা report ভুলে যান** — GitHub-এর বর্তমান HEAD-থেকে শুরু করুন:
```bash
git log --oneline -5     # বর্তমান state দেখুন
git status               # clean থাকা উচিত
```

---

## ২. বর্তমান App-টা পড়ুন — ফিচার inventory (ভাঙা যাবে না)

`src/App.tsx` (১৯১১ লাইন) + components পড়ুন। **এই ফিচারগুলো থাকতেই হবে:**

| ফিচার | কোথায় | বাধ্যতামূলক |
|---|---|---|
| Signal card (direction, confidence ring, grade, entry, expiry, HTF, regime, structure) | `App.tsx` MaterialSignalCard | ✅ |
| Mode chip (⏱ FTT / 💹 FX / 🔄 BOTH) | MaterialSignalCard | ✅ **আসলেই render হতে হবে** |
| Fill badge (⚡ INSTANT / ⏳ PENDING) | MaterialSignalCard | ✅ |
| SL/TP chips (FX-এ) | MaterialSignalCard | ✅ |
| Scanner (multi-pair, add/remove, notif) | `ScannerView.tsx` | ✅ |
| Board (all-pairs, WR+n, tie flags) | `DashboardView.tsx` | ✅ |
| History (rows, entry hit/miss, filter, report) | `HistoryView.tsx` | ✅ |
| Analysis (timeframes, indicators) | `IndicatorGrid.tsx` etc | ✅ |
| Settings (mode toggle, auto-refresh, health, backup) | Settings section | ✅ |
| Ticker | `Ticker.tsx` | ✅ |
| **Honesty UI** (win-rate n-সহ, breakeven note, no fake 75%) | বিভিন্ন | ✅ |

**Worker API contract** (অপরিবর্তিত): `https://fttotcv6.umuhammadiswa.workers.dev`
- `/api/signal?pair=X&mode=fx` → `signal.{finalSignal, confidence, grade, mode?, fillStatus?, entryPrice, currentPrice, entryDistancePct, fxLevels?{entry,sl,tp,rr}, structureVerdict, aiValidation, ...}`
- `/api/history?pair=X` → `signals[]` (result, entryHit?)
- `/api/stats`, `/api/pairs`, `/api/signals/latest`, `/health`

---

## ৩. নতুন Architecture — modular (App.tsx ভাঙুন)

```
src/
  lib/           # api.ts (typed client), formatters.ts (winRate, breakeven, debounce)
  hooks/         # useSignal, useMode, useHealth, useServerStats, useLocalStorage
  components/
    signal/      # MaterialSignalCard, ConfidenceRing, ModeChip, FillBadge, SltpChip
    history/     # HistoryRow, StatCard, ServerStatsCard
    settings/    # SettingRow, SignalModeToggle, HealthPill
    common/      # MarketClosedCard, CircuitBreakerCard, NavButton
  types.ts       # TradableSignalData, HistoryEntry, ServerPairStats, etc
```

- **App.tsx → max ~300 lines** (state machine + composition)
- **Business logic → hooks** (fetch, abort, cache, localStorage)
- **Prop-drilling কম**, typed props, **no `any`**
- **Undefined-safe UI** — worker field না দিলে crash হবে না (default `—`)

---

## ৪. Verify — নিজে, push-এর আগে (এইটা বাধ্যতামূলক)

```bash
npx tsc --noEmit        # 0 errors হতে হবে
npm run build           # dist/index.html single-file
```

**তারপর REAL BROWSER verify (আগের agent-এর fail-টা):**
- `dist/` local server-এ চালান (`python3 -m http.server 8000`)
- Headless browser (Playwright) দিয়ে load → **rendered DOM-এ check:**
  - `⏱ FTT` / `💹 FX` / `🔄 BOTH` — Mode chip **আসলেই DOM-এ**
  - `⚡ INSTANT` / `⏳ PENDING` / `not yet resolved` — Fill badge
  - `SL` / `TP` — FX-এ
- **সব present হলে তবেই push** (নইলে আবার fix)

---

## ৫. Push — GitHub-এ visible করা (সবচেয়ে গুরুত্বপূর্ণ)

```bash
git add -A
git commit -m "Frontend architecture: modular refactor (components/hooks/lib)"
git push origin main
```

**Push-এর পরে নিশ্চিত করুন (এটা মিস করবেন না):**
```bash
git log --oneline -1          # নতুন commit hash
git ls-remote origin HEAD     # remote-ও একই hash — visible!
```

> ⚠️ **`git ls-remote origin HEAD`-এ আপনার নতুন hash না দেখালে — push হয়নি।** তখন:
> `git remote -v` (TOKEN ঠিক?), `git push -u origin main` retry।

---

## ৬. CHANGES.md — আসল প্রমাণ সহ

```markdown
# Signal Pro Frontend Refactor — CHANGES

## Commit
- hash: `<আসল commit hash>` (git log-থেকে)
- remote: `<git ls-remote output>` — GitHub-এ visible

## File-by-file
### New
| File | কী |
|---|---|
| `src/lib/api.ts` | typed API client ... |
| `src/hooks/useSignal.ts` | ... |
| ... (সব) |

### Modified
| File | কী বদলালো |
|---|---|
| `src/App.tsx` | 1911 → ~300 lines, hooks-এ logic ... |

### Deleted
(যদি থাকে)

## Feature Preservation Checklist
- [ ] Signal card ... (সব ফিচার √)

## Verification
- [ ] tsc 0
- [ ] build pass
- [ ] Real-browser: Mode chip/fill/SL-TP DOM-এ present (screenshot)
- [ ] Push: git ls-remote = my hash
```

---

## ৭. Reviewer (independent) verify করবে

আমি (reviewer) এই ৭টা check করবো — **আপনার commit GitHub-এ visible + সব pass = done:**

1. GitHub HEAD = আপনার নতুন commit
2. Structure: `src/lib`, `src/hooks`, `src/components/signal` — আছে
3. `tsc --noEmit` 0
4. `npm run build` pass
5. **Real-browser** — Mode/fill/SL-TP chips rendered DOM-এ (আগের bug)
6. No regression — `7f39e25`-থেকে কোনো feature হারায়নি
7. Honesty UI — win-rate n-সহ, breakeven note, no fake 75%

**এই ৭টা pass = কাজ সম্পূর্ণ। কোনোটা fail = আবার করুন (রিপোর্ট-শুধু fail)।**

---

**আদর্শ:** "Apple-grade polish, no-broken-parts, and actually pushed to GitHub."
আপনার কাজ শেষে reviewer verify করবে। 🎨
