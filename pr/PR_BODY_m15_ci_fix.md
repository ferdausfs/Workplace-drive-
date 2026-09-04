# fix(ci): DOK-ai build workflow — replace broken curbox workflows

**Repo:** `ferdausfs/DOK-ai` · **Base:** `main` (`93cb379`) · **Branch:** `fix/ci-build-workflow`

## Problem
M1 merge-এর পর GitHub Actions-এ **কোনো build চলেনি** (runs: 0)। Root cause: DOK-ai seed-এ
curbox-এর ৪টা workflow copy হয়ে এসেছিল, সবগুলোর trigger curbox-এর `kt-rewrite` branch-এ
hardcoded — DOK-ai-র branch `main`, তাই কিছুই trigger হয় না। উপরন্তু `release.yml`-এ
DOK-ai-এর জন্য অপ্রাসঙ্গিক secrets (Discord/Telegram/VirusTotal/SIGNING_KEY) + `assembleFdroidRelease`
signing step ছিল — চললেও fail করত।

## What changed (`.github/workflows/`)
- ✅ **নতুন `build.yml`** — push/PR/main + manual trigger, JDK 17 + Android SDK,
  `./gradlew assembleFdroidDebug`, APK artifact upload (30-day)।
- 🗑️ **৪টা curbox workflow সরানো**: `pr.yml`, `release.yml`, `debug.yml`, `github-release.yml`
  (branch/secrets mismatch — DOK-ai-তে অচল)।

## Verification
- YAML-গুলো static review করা; actual build-টা merge-এর পর GitHub Actions-এই হবে
  (এটাই প্রথমবার CI trigger হবে)।
- Build pass করলে artifact `dok-ai-fdroid-debug` download-যোগ্য হবে — M1 Kotlin port-এর
  compile-check এটাই।

## Notes
- আপাতত `assembleFdroidDebug` (no network/sync flavor) — সবচেয়ে নির্ভরযোগ্য। পরে signed release
  চাইলে আলাদা workflow + আপনার keystore secrets লাগবে।
- TFLite deps + guardian engine-এর প্রথম real compile এখানেই যাচাই হবে।
