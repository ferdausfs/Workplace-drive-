# feat(v2.4.0): safe/unsafe detection only + gender removal (v2)

**Repo:** `ferdausfs/Dogs-of-KAHAF` · **Base:** `main` (`a2af6372`) · **Branch:** `feat/v240-safeunsafe`

## আগের চেষ্টা কেন fail হয়েছিল
PR #16 (CI release fix) আগেই merge হয়ে গেছে → `main` এখন `a2af6372`। আগের v2.4.0 patch-এর ভেতরে
ওই build.yml-এর change-ও ছিল → `git apply` fail → "PR হলো না"। **এই patch-এ build.yml নেই** —
ওই fix ইতিমধ্যে main-এ আছে (dynamic version tag + wrapper step বাদ), তাই সেটা touch করার দরকারই নেই।

## What this is (আপনার spec অনুযায়ী)
- **২ class: safe vs unsafe** — block = `max(Hentai, Porn, Sexy) ≥ threshold`। এটাই এখন একমাত্র AI পথ।
- **Gender detection পুরো বাদ** — male/female/opposite-gender সব সরানো (service-এ আর কল নেই, detector-এ
  method/interpreters নেই, prefs-এ keys নেই, UI-তে gender chips/sliders/model-import নেই)।
- **Stable + কম false block** — threshold floor 0.80 বাদ (`coerceIn(0.50, 0.95)`, slider 0.30–0.95 সত্যিই কাজ করে),
  grid vote `+1` বাদ (default ২ cell)।
- **version** 2.3.1 → **2.4.0** (versionCode 9)।

## Changes (7 files, +17/−517)
1. **`AiDetector.kt`** — gender/nsfw interpreters, cached gender/nsfw fields, collection coroutines,
   `isOppositeGenderNsfw`, `extractNsfwGateScore`, `MODEL_NSFW`/`MODEL_GENDER` const — সব বাদ;
   `threshold = cachedThreshold.coerceIn(0.50, 0.95)`; `voteNeeded = cachedGridVoteCount.coerceIn(1, 4)`।
2. **`GuardianAccessibilityService.kt`** — region + full-screen দুই gender call site বাদ; legacy `isUnsafe`-ই একমাত্র AI path।
3. **`SettingsActivity.kt`** — gender chips, gender/NSFW sliders, nsfw/gender model import/remove listener/render বাদ।
4. **`SettingsViewModel.kt`** — userGender/nsfwGateThreshold/genderThreshold + gender/nsfw model slots বাদ;
   combine re-indexed (keyword, aiDetection, delaySeconds, tempBlockDurationMins, aiThreshold, gridVoteCount, refreshTick)।
5. **`GuardianPreferences.kt`** — USER_GENDER / NSFW_GATE_THRESHOLD / GENDER_THRESHOLD keys+flows+setters বাদ।
6. **`activity_settings.xml`** — gender filter, NSFW gate + gender confidence, NSFW + gender model — ৩ section সরানো (XML well-formed verified)।
7. **`build.gradle.kts`** — versionName 2.3.1 → **2.4.0**, versionCode 9।

## Verification (honest)
- ✅ `git apply --check` OK on base `a2af6372`-equivalent (e05d9c2 + merged ci_fix build.yml)
- ✅ brace/paren balance 0 (comment-stripped) — ৪ Kotlin file
- ✅ XML well-formed (minidom)
- ✅ পুরো repo-তে gender/nsfw/MODEL_NSFW/MODEL_GENDER dangling reference: 0
- ⚠️ **Compile = CI** — sandbox-এ Android SDK নেই। Merge-পর CI build-ই truth; কোনো issue হলে সাথে সাথে ঠিক করবো।

## Test checklist (আপনার device)
1. Settings-এ এখন শুধু: keyword switch, AI detection switch, **একটা** threshold slider, grid votes,
   delay, temp-block, **একটা** model (guardian) import — gender/nsfw কিছুই নেই।
2. NSFW image → block + log ✅ (মিস করলে slider কমান: 0.65→0.55)
3. Safe/cartoon/Mr Bean/Oggy → block হবে না ✅ (false block হলে slider বাড়ান: 0.65→0.75)

## Note
`guardian_model.tflite`-ই একমাত্র দরকারি model। Gender/NSFW model আর লাগবে না।
