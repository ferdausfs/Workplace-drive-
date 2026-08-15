# feat(guardian): M2 — accessibility-service content-scan hook

**Repo:** `ferdausfs/DOK-ai` · **Base:** `main` (`5af5ae3`) · **Branch:** `feat/guardian-m2-service-hook`

## What this is
M1 port করেছিল detection engine-টা; এটা **M2** — সেটাকে curbox-এর accessibility service-এ
hook করা, যেন NSFW content scan-টা সত্যিকারে চলে।

## Files
1. **`blockers/GuardianBlocker.kt`** (new, curbox-এর blocker convention):
   - `setupBlocker` / `setupReceivers` / `removeReceivers` / `onDestroy`
   - `onAccessibilityEvent(event, pkg)` — WINDOW_STATE_CHANGED / CONTENT_CHANGED-এ:
     (a) keyword text scan (`GuardianKeywordMatcher`), (b) throttled AI screenshot scan (API 30+)
   - AI scan: `takeScreenshot` → full-screen `isOppositeGenderNsfw(requireStrongNsfw=true)` +
     legacy `isUnsafe` → block হলে `GLOBAL_ACTION_HOME` + Toast (full overlay/unlock UI = M4)
   - Config: SharedPreferences `guardian_prefs` (enabled/gender/thresholds/keywords) —
     M3 settings UI-র জন্য setter helper-ও আছে
2. **`services/AppBlockerService.kt`** (wire-up, +15):
   - event hook (নিজস্ব containment boundary-তে — agents.md invariant),
   - `setupBlocker` / `setupReceivers` / `removeReceivers` / `onDestroy` wiring

## Safety (agents.md invariants মানা হয়েছে)
- প্রতিটা feature call try/catch-এ, failure → `CrashLogger.logNonFatalError`
- Coroutine-এ `CancellationException` rethrow (crash হিসেবে report হয় না)
- Screenshot fail / API<30 → fail-open (কোনো block হয় না, service অটুট)

## Verification (honest)
- Brace/paren balance ✅ (Kotlin compiler run হয়নি — sandbox-এ SDK নেই)
- ⚠️ **Real compile = CI** (মার্জের পর build workflow auto-run হবে)। কোনো issue হলে আমি ঠিক করবো।

## Not in this PR (পরের milestone)
- M3: settings UI (Guardian toggle, gender, thresholds, model import)
- M4: AI-block overlay + activity log + unlock flow (এখনো go-home + toast)

## Deploy
Merge → CI build → install → Guardian-এ model import + enable করলেই scan চালু হবে
(M3-এর আগে SharedPreferences manual/ADB দিয়ে enable করা যাবে; UI M3-তে)।
