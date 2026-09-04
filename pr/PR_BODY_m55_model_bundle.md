# feat(guardian): M5.5 — bundle models + import validity check + status UI

**Repo:** `ferdausfs/DOK-ai` · **Base:** `main` (`4b97fb0`) · **Branch:** `feat/guardian-m55-model-bundle`

## What this is
এখন পর্যন্ত model manual import-এ চলে (M3)। এটা **M5.5**:
1. **Model bundle** — `.tflite` file-গুলো `app/src/main/assets/`-এ ship হয় → install-এই ready।
2. **Import validity check** — manual import-এর সময় input/output shape verify হয়; ভুল file
   সাথে সাথে reject হয় (চুপচাপ fail না)।
3. **Status UI** — settings screen-এ "Bundled (X KB) — ready" / "Imported (X KB)" / "Not imported"।

## Code files (4, +86)
1. **`GuardianModelImportManager.kt`** — `modelStatus()` (imported → bundled → missing),
   `verifyFile()` (TFLite interpreter দিয়ে [1,224,224,3] float32 input check), import-এ reject।
2. **`GuardianFragment.kt`** — `bindModel` এখন bundled status-ও দেখায়।
3. **`fragment_guardian.xml`** — gender-model "optional" hint।
4. **`strings.xml`** — ২ string।

## Model files (এই PR-এ নয় — আলাদা commit)
দুটো `.tflite` (NSFWJS MobileNetV2, float32, SHA `8229bafa…`) আলাদাভাবে যোগ হবে:
```bash
cd ~/DOK-ai
# DOK-ai-models.tar.gz extract করে assets-এ কপি
cp DOK-ai-models/guardian_model.tflite app/src/main/assets/
cp DOK-ai-models/guardian_model.tflite app/src/main/assets/nsfw_model.tflite
git add app/src/main/assets/
git commit -m "chore: bundle NSFW detection models (NSFWJS MobileNetV2 float32)"
git push origin main
```
(কারণ: ২০ MB binary patch-এ রাখলে transport ঝামেলা; code + model আলাদা commit)।

## Verification (honest)
- Kotlin brace/paren ✅ · XML well-formed ✅
- ⚠️ **Compile = CI** — model-সহ build-ই আসল test (TFLite asset load)।

## Deploy
Merge code PR + model commit → CI build (APK এখন ~30 MB, model সহ) → install → **model
আগে থেকেই bundled** → শুধু enable → test।
