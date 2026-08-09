# 🔧 Worker Bug-Fix — Reviewer Approval (আমি approve করলাম)

> **আপনার BUG_REPORT (১০ findings) reviewer-এ verify হয়েছে — ৭টা real।**
> নিচের **৬টা fix করো** (আমার approve), ২টা check, ২টা skip। PR-first (main-এ merge না)।

---

## ✅ FIX করো (৬টা — আমার approve)

### FIX-1 (BUG-001 — Critical): push ReferenceError
- `saveAndPush()`-এ `noPush` parameter pass করো (এখন undefined — ReferenceError)
- `handleSignal()` → `handleSignalRaw()`-এ `opts.noPush` forward করো
- **পরীক্ষা:** `node scripts/phase10_integration.mjs` — এখন pass হওয়া উচিত

### FIX-2 (BUG-002 — High): AI rescue D2 block override
- Rescue path-এ: **`d2Audit` set থাকলে rescue skip** (D2 = hard block)
- TRENDING/HIGHEST/BAD_PAIR block-গুলো আর AI-তে override হবে না
- **পরীক্ষা:** TRENDING signal AI agree-এও NO_TRADE থাকে

### FIX-3 (BUG-003 — High): fillStatus degenerate
- `entryPx` আর `lastClose` একই source — **আলাদা current price** ব্যবহার করো
- (নতুন quote/latest candle, নয়তো feature-টা সরাও — constant INSTANT দিও না)
- **পরীক্ষা:** fillStatus কখনো PENDING_ENTRY দেখায় (যখন entry দূরে)

### FIX-4 (BUG-005 — Medium): /api/report double-count
- `handleReport`-এ **dedup guard** — একই signal-এ একাধিক report/ resolver overwrite আটকাও
- **পরীক্ষা:** same id-এ ২ বার report → stats ১ বার count

### FIX-5 (BUG-007 — Medium): MIN_CONFIDENCE_FLOOR post-AI
- AI rescue/boost-এর **পরে** floor re-check — 72% নিচে গেলে NO_TRADE
- **পরীক্ষা:** 69% signal আর বেরোবে না

### FIX-6 (BUG-008 — Medium): tie convention
- `exit == entry` → **tie** (WIN/LOSS না — আলাদা/UNKNOWN) — অথবা অন্তত documented
- **পরীক্ষা:** tie signal-এ result misleading না

---

## 🔍 CHECK করো (২টা — report দাও, change নয়)

### CHECK-A (BUG-006): passAI never true?
- Live-এ `aiOnlyMode: true` user-এর জন্য — AI agree signal-টা push হয়?
- না হলে — passAI logic ঠিক করো (report-এ লিখো)

### CHECK-B (BUG-004): entryHit wrong window
- entry-hit-টা entry-time-থেকে measure হওয়া উচিত, expiry±5min না?
- তোমার analysis দাও — আমি পরে decide

---

## ⏭️ SKIP (২টা — এখনই না)
- BUG-009 (confluence denominator) — cosmetic
- BUG-010 (winRate semantics) — documented

---

## PR + Verify

```bash
git checkout -b bugfix-round1
# ৬টা fix + test
git add -A && git commit -m "Bugfix round 1: push noPush, D2 rescue guard, fillStatus, report dedup, floor, tie"
git push origin bugfix-round1
# PR → main
```

**PR body:** কোন fix কী করলো + test results (`phase10_integration` pass etc)।

**Reviewer (আমি) fix-গুলো আবার verify করবো** — merge-এর আগে। 🔧
