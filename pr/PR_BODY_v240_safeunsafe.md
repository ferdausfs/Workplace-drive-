# feat(v2.4.0): safe/unsafe detection only + gender removal + CI release fix

**Repo:** `ferdausfs/Dogs-of-KAHAF` · **Base:** `main` (`e05d9c2`) · **Branch:** `feat/v240-safeunsafe`

## What this is (আপনার spec অনুযায়ী)
- **২ class: safe vs unsafe** — ৫ class-এর দরকার নেই। Block = `max(Hentai, Porn, Sexy) ≥ threshold`
  (আগের মতোই, এখন শুধু এটাই একমাত্র পথ)।
- **Gender detection পুরো বাদ** — male/female/opposite-gender সব সরানো (service-এ আর কল হয় না,
  detector-এ method/interpreters/prefs নেই, UI-তে gender chips/sliders/model import নেই)।
- **Stable + কম false block** — threshold floor 0.80 বাদ (slider 0.30–0.95 সত্যিই কাজ করে),
  grid vote `+1` বাদ (default ২ cell)।
- **CI release fix** — hardcoded `v2.2.0` tag → dynamic `versionName` (2.4.0), stale wrapper step বাদ।

## Changes (8 files, +31/−532)
1. **`AiDetector.kt`** — gender/nsfw interpreters + `isOppositeGenderNsfw` + `extractNsfwGateScore` +
   gender/nsfw cache fields + collection সব সরানো; `threshold = cachedThreshold.coerceIn(0.50, 0.95)`;
   `voteNeeded = cachedGridVoteCount.coerceIn(1,4)`; `MODEL_NSFW`/`MODEL_GENDER` const বাদ।
2. **`GuardianAccessibilityService.kt`** — region + full-screen দুটো gender path সরানো; legacy
   `isUnsafe`-ই একমাত্র AI path।
3. **`SettingsActivity.kt`** — gender chips, gender/NSFW sliders, nsfw/gender model import/remove —
   সব listener/render বাদ।
4. **`SettingsViewModel.kt`** — `userGender`/`nsfwGateThreshold`/`genderThreshold`/gender+nsfw model
   slots UiState + setters থেকে বাদ; combine re-indexed।
5. **`GuardianPreferences.kt`** — userGender/nsfwGate/genderThreshold keys+flows+setters বাদ।
6. **`activity_settings.xml`** — gender filter, NSFW gate + gender confidence sliders, NSFW + gender
   model sections সরানো (XML well-formed verified)।
7. **`build.gradle.kts`** — versionName 2.3.1 → **2.4.0**, versionCode 9।
8. **`.github/workflows/build.yml`** — dynamic version tag/name/artifact + wrapper step বাদ।

## Verification (honest)
- ✅ brace/paren balance (clean, comment-র false-positive বাদে) ৪ file-এ 0
- ✅ XML well-formed (minidom)
- ✅ পুরো repo-তে gender/nsfw/MODEL_NSFW/MODEL_GENDER dangling reference: **0**
- ⚠️ **Compile = CI** — sandbox-এ Android SDK নেই। Merge-এর পর CI build-ই truth; কোনো issue হলে আমি
  সাথে সাথে ঠিক করবো।

## Test checklist (আপনার device)
1. Settings-এ এখন শুধু: keyword switch, AI detection switch, **একটা** threshold slider, grid votes,
   delay, temp-block, **একটা** model (guardian) import — gender/nsfw কিছুই নেই।
2. NSFW image → block + log ✅ (মিস করলে slider কমান: 0.65→0.55)
3. Safe/cartoon/Mr Bean/Oggy → block হবে না ✅ (false block হলে slider বাড়ান: 0.65→0.75)

## Note
`guardian_model.tflite`-ই একমাত্র দরকারি model। Gender/NSFW model আর লাগবে না।
