# fix(ci): release automation — dynamic version tag + remove stale wrapper download

**Repo:** `ferdausfs/Dogs-of-KAHAF` · **Base:** `main` (`e05d9c2`) · **Branch:** `fix/ci-release-automation`

## Problem (verified)
1. **`Create GitHub Release` প্রতিটা build-এ fail** — `tag_name: v2.2.0` hardcoded; প্রথম v2.2.0
   release-র পর tag already-exists → step fail (build নিজে succeed হয়, শুধু release হয় না)।
2. **Artifact name** `guardian-shield-release-v2.2.0` — app version 2.3.1-এর সাথে মিলছে না।
3. **`Download Gradle wrapper jar` step** — 8.4.0 jar ডাউনলোড করে repo-র committed wrapper
   (gradle 8.8, `gradle-wrapper.properties` অনুযায়ী) overwrite করে। Jar already committed —
   এই step অপ্রয়োজনীয় + version mismatch-র উৎস।
4. Release body-ও stale (v2.2.0 changelog)।

## Fix (`.github/workflows/build.yml`, 1 file)
- **Dynamic version**: `versionName` extract (`app/build.gradle.kts` থেকে) → tag_name/name/artifact
  সব `v${{ steps.version.outputs.version }}`। এখন version bump করলেই release-ও automatic।
- **Wrapper download step removed** (committed jar ব্যবহার হয়)।
- Release body generic করা হয়েছে।

## ⚠️ Usage note (আপনার জন্য)
- **প্রতিটা release-এ `versionName` bump করুন** (`app/build.gradle.kts`-এ)। একই version-এ আবার
  push করলে tag conflict হয়ে release step fail হবে (APK artifact তবু upload হবে — build fail নয়)।
- Version bump এখন আগের চেয়ে গুরুত্বপূর্ণ: versionName-ই release tag।

## Verification
- YAML valid (pyyaml parse ✅) · static review ✅
- Real run = GitHub Actions (merge-এর পর push-এ trigger হবে)
