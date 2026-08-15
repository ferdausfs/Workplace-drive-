# feat(guardian): M4 — AI-block overlay + activity log

**Repo:** `ferdausfs/DOK-ai` · **Base:** `main` (`daffd03`) · **Branch:** `feat/guardian-m4-overlay-log`

## What this is
M2-র block-টা ছিল go-home + toast। এটা **M4** — proper full-screen block screen +
block log (সব milestone-এর functional piece একসাথে)।

## Files (7, +200)
1. **`ui/overlay/GuardianBlockActivity.kt`** (new) — full-screen block: reason + package +
   "Go home" + "Guardian settings" (WarningActivity reuse করিনি — সেটা config/mode-driven,
   Guardian-এর জন্য independent predictable screen দরকার)।
2. **`res/layout/activity_guardian_block.xml`** (new) — block screen layout।
3. **`blockers/GuardianBlocker.kt`** — block action: `GuardianBlockActivity.start(...)` +
   `logBlock()` (SharedPreferences ring buffer, 500 entries) + fail-open go-home fallback।
4. **`ui/.../guardian/GuardianFragment.kt`** — settings screen-এ "Block log" section (view + clear)।
5. **`res/layout/fragment_guardian.xml`** — log section UI।
6. **`AndroidManifest.xml`** — `GuardianBlockActivity` registration (singleTop, not exported)।
7. **`res/values/strings.xml`** — 8 string resources।

## Verification (honest)
- Kotlin brace/paren balance ✅ (3 file) · XML well-formedness ✅ (4 file)
- ⚠️ **Compile = CI** — merge-র পর build workflow auto-run। Issue হলে আমি ঠিক করবো।

## Deploy / test
Merge → CI build → install → Guardian AI screen-এ model import + enable → NSFW content
(বা test keyword) দেখালে full-screen block + log entry। **এটাই M5 device test-এর entry point।**
