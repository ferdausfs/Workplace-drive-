# 📱 AI Model Family Reunion — Android WebView wrapper

Native **Kotlin + WebView** app that wraps the single-file page
`ai-model-family-reunion.html` (bundled at `app/src/main/assets/reunion.html`).

## Stack
- Kotlin + `android.webkit.WebView` (zero external dependencies — platform APIs only)
- AGP 8.5.2 · Kotlin 1.9.24 · Gradle 8.7 · JDK 17
- `minSdk 26` / `targetSdk 34` / `compileSdk 34`

## Build
```bash
cd android
./gradlew assembleRelease
# APK → app/build/outputs/apk/release/app-release-unsigned.apk
```
(Release APK is unsigned — add a signing config before publishing to a store.)

## Run & logcat markers
```bash
adb install app/build/outputs/apk/release/app-release-unsigned.apk
adb logcat -s REUNION_APP
```
Expected markers: `onCreate` → `onPageStarted` → `onPageFinished` →
`onBackPressed` (only when navigating back). On an unexpected load failure you
will instead see `onReceivedError` and a branded fallback page (never a blank
screen).

## CI
A ready-to-use GitHub Actions workflow is included at
[`ci-android-build.yml`](./ci-android-build.yml). Copy it to
`.github/workflows/android-build.yml` to run `./gradlew assembleRelease` on
`ubuntu-latest` (JDK 17 + Android SDK) for any change under `android/`.
(The CI was left as a reference file because the automation token that pushed
this branch lacks the `workflows` permission required to write into
`.github/workflows/`.)
