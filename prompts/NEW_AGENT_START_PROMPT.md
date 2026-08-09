# 🎨 NEW Frontend Architect — Start Prompt (এটা কপি করে নতুন Arena chat-এ দিন)

> **এই chat-এ আপনি আসল কোড লিখবেন + GitHub-এ push করবেন (PR আকারে)।**
> আগের agent মিথ্যা report দিয়ে বাদ — আপনি সত্যিকারের কাজ করবেন।
> শেষে reviewer verify করবে — GitHub-এ commit visible (main-এ বা PR) হলেই pass।

> **আপডেট (2026-08-05):** PR #1 (design polish) এখন **main-এ merge হয়েছে**
> (HEAD `e669f3e` — tokens/css/verify tools)। আপনার কাজ এখন:
> **১) main-এর বর্তমান state থেকে শুরু করুন** (pull latest),
> **২) আসল modular refactor** (lib/hooks/components/signal) করুন —
> design polish-এর উপরে, সেটা ভেঙে না।

---

## আপনার কাজ (৭ ধাপ)

**১. Clone (আপনার জন্য token দেওয়া হয়েছে):**
```bash
git clone https://<YOUR_TOKEN>@github.com/ferdausfs/Ftt-app-002.git
cd Ftt-app-002
git branch --show-current   # main
```

**২. বর্তমান app পড়ুন** (`src/App.tsx` ১৯১১ লাইন + components) — সব feature বুঝুন:
Signal card (direction/confidence ring/grade/entry/expiry/HTF/regime/structure),
**Mode chip (⏱ FTT/💹 FX/🔄 BOTH)**, **Fill badge (⚡ INSTANT/⏳ PENDING)**,
**SL/TP chips**, Scanner, Board, History (entry hit/miss), Analysis, Settings,
Ticker, **Honesty UI** (win-rate n-সহ, breakeven, no fake 75%)।

**৩. Modular refactor:**
```
src/lib/           api.ts (typed client), formatters.ts
src/hooks/         useSignal, useMode, useHealth, useServerStats, useLocalStorage
src/components/
  signal/          MaterialSignalCard, ConfidenceRing, ModeChip, FillBadge, SltpChip
  history/         HistoryRow, StatCard, ServerStatsCard
  settings/        SettingRow, SignalModeToggle, HealthPill
  common/          MarketClosedCard, CircuitBreakerCard, NavButton
```
- App.tsx → ~300 lines (state machine only)
- সব feature রাখুন — **একটাও বাদ না**

**৪. Verify (নিজে):**
```bash
npx tsc --noEmit    # 0 errors
npm run build       # dist/index.html
```
**Real-browser check:** dist/ local server-এ চালিয়ে (python3 -m http.server) →
headless browser-এ **Mode chip/fill badge/SL-TP DOM-এ present** নিশ্চিত করুন।
(আগের fail-টা এখানে — চিপস render হয়নি। এবার নিশ্চিত করুন।)

**৫. Push (সবচেয়ে গুরুত্বপূর্ণ):**
```bash
git add -A
git commit -m "Frontend architecture: modular refactor (components/hooks/lib)"
git push origin main
```
**Push-এর প্রমাণ:**
```bash
git log --oneline -1        # নতুন hash
git ls-remote origin HEAD   # একই hash — GitHub-এ visible!
```

**৬. CHANGES.md লিখুন** — আসল commit hash, file-by-file, verification proof, `git ls-remote` output।

**৭. Push (PR আকারে — GitHub-এ visible):**
```bash
git push origin <আপনার-branch>       # feature branch
# তারপর GitHub-এ PR খুলুন (branch → main)
```
**প্রমাণ:** PR link + `git ls-remote origin <branch>` — GitHub-এ visible।

**৮. Done** — reviewer verify করবে (main-এ merge-এর আগে আমি PR check করবো)।

---

## Token

আপনার GitHub push-এর জন্য token (শুধু `Ftt-app-002`, Contents read/write, 7 দিন):
```
<YOUR_TOKEN>
```
> ⚠️ Token-টা গোপন — কোড/CHANGES-এ লিখবেন না। শুধু clone/push-এর জন্য।

---

## Hard Rules (ভাঙলে fail)

- ❌ কোনো feature হারাবে না
- ❌ কোনো bug (render না হওয়া chips-সহ)
- ✅ tsc 0 + build pass
- ✅ Real-browser-এ chips visible
- ✅ GitHub-এ push + `git ls-remote` প্রমাণ
- ✅ Honesty UI (n-সহ win-rate, breakeven, no fake 75%)

**শেষ কথা:** রিপোর্ট-শুধু = fail। **আসল কোড + GitHub visible = pass।** শুরু করুন। 🎨
