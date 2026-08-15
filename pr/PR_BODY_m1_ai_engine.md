# feat(guardian): M1 — NSFW AI detection engine port (TFLite)

**Repo:** `ferdausfs/DOK-ai` · **Base:** `main` (`a50fe7bf`) · **Branch:** `feat/guardian-m1-ai-engine`

## What this is
DOK-ai = Curbox UI/theme + Dogs-of-KAHAF-এর NSFW blocker। এটা **M1** — প্রথম milestone:
কেবল **detection engine** (UI/Service নেই, সেগুলো M2–M4)।

## Files added (`neth.iecal.curbox.guardian`)
1. **`GuardianConstants.kt`** — thresholds + model filenames (Phase-1 false-block fix-এর
   পরের মান; `SOFT_NSFW_THRESHOLD` ইচ্ছাকৃতভাবে নেই)।
2. **`GuardianKeywordMatcher.kt`** — pure-logic keyword/regex matcher, Phase-1 word-boundary
   fix-সহ (`sex` ম্যাচ করবে না "Essex"/"sextant")। JVM-testable, Android-dep free।
3. **`GuardianModelImportManager.kt`** — .tflite model import (uri → filesDir, progress StateFlow)।
4. **`GuardianAiDetector.kt`** — TFLite inference core (legacy + NSFW gate + gender),
   GPU delegate + CPU fallback + grid voting + inference-fail recovery। Phase-1 fixes:
   - `isOppositeGenderNsfw(..., requireStrongNsfw)` — full-screen call → NSFW gate 0.80
   - soft-hybrid gender-lowering (0.62) **removed** — always full genderConf (0.78)

## Adaptation (Dogs-of-KAHAF → Curbox style)
- Hilt (`@Inject @Singleton`) → plain class + `companion object get(context)` singleton
- Timber → `android.util.Log`
- `GuardianPreferences` (DataStore flow) → `GuardianConfig` data class (volatile; M3-এ
  curbox-এর DataStore-এর সাথে wire হবে)
- Package `com.guardian.shield` → `neth.iecal.curbox.guardian`

## Gradle
- `libs.versions.toml`: `tflite = 2.16.1`, `tensorflow-lite`, `tensorflow-lite-gpu`
- `app/build.gradle.kts`: +2 implementation + `androidResources { noCompress += "tflite" }`

## Verification (honest)
- 4 file-এ brace/paren balance check ✅
- `GuardianKeywordMatcher` regex semantics আগেই harness-এ verified
  (Essex/sextant/class → no match; sex/ass → match)
- ⚠️ **Compile হয়নি** — sandbox-এ Android SDK নেই। Merge-এর পর CI/build:
  `./gradlew assembleDebug`। কোনো syntax issue থাকলে CI error দেবে — আমি তখনই ঠিক করবো।

## Not in this PR (পরের milestone)
- M2: accessibility service-এ content-scan hook
- M3: settings UI (threshold sliders, gender, model import screen)
- M4: AI-block overlay + activity log

## Deploy
Merge → `./gradlew assembleDebug` → install → (M4 পর্যন্ত UI নেই, তাই এখনো user-visible নয়;
এটা শুধু engine groundwork)।
