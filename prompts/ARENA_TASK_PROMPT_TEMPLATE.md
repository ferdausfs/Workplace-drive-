# 🧩 ARENA TASK PROMPT — copy-paste kit

**Owner:** ferdausfs · **Updated:** 2026-08-13
**Ki eta:** Arena agent-ke kaj dewar jonno ready-made prompt. Niche 3 ta block —
(A) reusable template, (B) ready prompt: Android CI chalu kora, (C) ready prompt: bug fix.
Shudhu block copy koro → chat-e paste koro → `[...]` gulo bhoro.

---

## ⚠️ Age eta jene nao (2 ta niyom)

1. **Branch fixed.** Protita Arena session ekta branch-e bandha (`arena/<id>-workplace-drive`).
   Agent-ke notun branch banate bolbe na — bolle-o parbe na. Ekta session = ekta branch.
2. **PR block hoy na.** Ekta branch-e ek shomoy ekta-i open PR thake.
   - Open PR **ache** → agent shudhu commit + push korbe, oi PR **auto-update** hobe.
   - Open PR **nai** (merge/close hoye geche) → agent **notun PR** khulbe.
   Tai tumi PR merge kore dile shathe shathe oi branch abar free — jotobar khushi notun kaj + notun PR.

---

## (A) 📋 REUSABLE TEMPLATE — jekono kajer jonno

```text
আপনি আমার Workplace-drive- রিপোজিটরিতে কাজ করছেন। আমাকে বাংলায় উত্তর দিন।

## কাজ
[এক লাইনে কী চাই]

### Context / সমস্যা
[কী ভুল হচ্ছে, কোথায়, কবে থেকে। error message/log থাকলে পুরোটা পেস্ট করুন]

### কোন ফাইল/ফোল্ডার
[যেমন: android/app/src/main/java/... অথবা "জানি না, তুমি খুঁজে বের করো"]

### Acceptance criteria (এগুলো হলেই কাজ শেষ)
- [ ] [শর্ত ১]
- [ ] [শর্ত ২]
- [ ] CI (./gradlew assembleRelease) সবুজ

### যা করবে না
- [যেমন: ai-model-family-reunion.html-এর কনটেন্ট বদলাবে না]

## PR নিয়ম (সবসময় মানুন)
1. শুধু বর্তমান ব্রাঞ্চে কাজ করুন। ব্রাঞ্চ বদলাবেন না, নতুন ব্রাঞ্চ বানাবেন না, main-এ direct push করবেন না।
2. প্রতি ধাপ শেষে: git add -A && git commit -m "..." && git push origin <বর্তমান-ব্রাঞ্চ>
3. PR খোলার আগে: gh pr list --head <বর্তমান-ব্রাঞ্চ> --state open
   - open PR থাকলে → নতুন PR না, শুধু commit+push (ওই PR আপডেট হবে)
   - না থাকলে → gh pr create --base main --head <বর্তমান-ব্রাঞ্চ>
4. PR নিজে merge/close করবেন না — শেষে জিজ্ঞেস করুন "PR merge করব?"
5. CI fail করলে fix করে আবার push করুন, সবুজ না হওয়া পর্যন্ত।
6. PR description-এ থাকবে: root cause + কী করলেন + test + logcat markers।
7. শেষে দিন: PR লিংক + CI status + বাংলা summary।
8. Sandbox-এ কিছু চালাতে না পারলে (JDK/SDK/network নেই) — লুকাবেন না, স্পষ্ট বলবেন কী verify করা গেল না।
```

---

## (B) ✅ READY PROMPT — Android CI (assembleRelease) chalu kora

> **Keno dorkar:** repo-te `.github/workflows/` folder-i nai. `android/ci-android-build.yml`
> shudhu ekta reference copy hoye pore ache — tai `./gradlew assembleRelease` **kono PR-e chole na**,
> protita PR-e "no checks reported" dekhay. Eta chalu na korle CI green/red kichui bojha jabe na.

```text
আপনি আমার Workplace-drive- রিপোজিটরিতে কাজ করছেন। আমাকে বাংলায় উত্তর দিন।

## কাজ
Android build CI আসলেই চালু করুন — এখন কোনো PR-এ চেক চলে না ("no checks reported")।

### Context
- `.github/workflows/` ডিরেক্টরিটাই রিপোতে নেই।
- `android/ci-android-build.yml` শুধু reference ফাইল হিসেবে পড়ে আছে (আগের token-এ `workflows` permission ছিল না)।
- ফলে `./gradlew assembleRelease` কোথাও রান হয় না, PR-এ CI status পাওয়া যায় না।

### যা করতে হবে
1. `android/ci-android-build.yml` → `.github/workflows/android-build.yml` এ কপি করুন।
2. workflow ট্রিগার ঠিক করুন: push + pull_request, paths: `android/**` এবং workflow ফাইল নিজে।
3. Job: ubuntu-latest → checkout → JDK 17 (temurin) → android-actions/setup-android → chmod +x gradlew → `./gradlew assembleRelease --no-daemon --stacktrace` → APK artifact upload।
4. Gradle cache যোগ করুন (`gradle/actions/setup-gradle` অথবা actions/cache) যাতে বিল্ড দ্রুত হয়।
5. Push করার পর `gh pr checks` দিয়ে রান দেখুন। fail করলে লগ পড়ে fix করে আবার push — সবুজ না হওয়া পর্যন্ত।
6. সবুজ হলে `android/README.md`-এর CI সেকশন আপডেট করুন ("reference file" কথাটা বাদ, আসল status badge/path লিখুন) এবং `android/ci-android-build.yml` duplicate ফাইলটা রাখবেন কিনা সিদ্ধান্ত নিয়ে জানান।

### Acceptance criteria
- [ ] `.github/workflows/android-build.yml` রিপোতে আছে
- [ ] PR-এ "Android Build (assembleRelease)" চেক দেখা যাচ্ছে এবং ✅ সবুজ
- [ ] APK artifact ডাউনলোডযোগ্য
- [ ] android/README.md আপডেটেড

### যা করবে না
- Android source code, manifest, বা assets-এর behaviour বদলাবেন না — এটা শুধু CI wiring।
- versionCode/versionName হাত দেবেন না।

### যদি permission error আসে
`refusing to allow ... workflows permission` টাইপ error হলে থামুন, আমাকে বাংলায় বলুন কী error
এবং GitHub-এ আমার কী করতে হবে (Arena-তে GitHub reconnect / token scope)। নিজে থেকে অন্য ব্রাঞ্চে
বা অন্য পথে ঘুরিয়ে দেবেন না।

## PR নিয়ম
1. শুধু বর্তমান ব্রাঞ্চে কাজ করুন, main-এ direct push নয়।
2. প্রতি ধাপে: git add -A && git commit -m "ci: enable android assembleRelease workflow" && git push origin <বর্তমান-ব্রাঞ্চ>
3. PR খোলার আগে `gh pr list --head <ব্রাঞ্চ> --state open` চেক — open থাকলে শুধু push, না থাকলে নতুন PR।
4. PR নিজে merge করবেন না — শেষে জিজ্ঞেস করুন।
5. শেষে: PR লিংক + CI status + বাংলা summary।
```

---

## (C) ✅ READY PROMPT — bug fix (Android app)

```text
আপনি আমার Workplace-drive- রিপোজিটরিতে কাজ করছেন। আমাকে বাংলায় উত্তর দিন।

## কাজ
Android অ্যাপে এই বাগটা ঠিক করুন: [বাগের এক লাইনের বর্ণনা]

### Reproduce steps
1. [ধাপ ১]
2. [ধাপ ২]
3. যা হয়: [actual]  |  যা হওয়া উচিত: [expected]

### Device / log
- ডিভাইস: [যেমন Android 13, Samsung A14]
- logcat (`adb logcat -s REUNION_APP`):
```
[লগ এখানে পেস্ট করুন]
```

### Acceptance criteria
- [ ] বাগ আর reproduce হয় না
- [ ] `onCreate → onPageStarted → onPageFinished` markers ঠিকঠাক আসে
- [ ] `./gradlew assembleRelease` সবুজ
- [ ] অন্য কোনো আচরণ ভাঙেনি

### যা করবে না
- Root cause না বুঝে "চেষ্টা করে দেখি" প্যাচ দেবেন না। আগে কারণ ব্যাখ্যা করুন, তারপর ফিক্স।

## PR নিয়ম
(উপরের একই ৫টা নিয়ম — branch fixed, প্রতি ধাপে push, open PR চেক, নিজে merge না, শেষে PR লিংক + CI + বাংলা summary)
```

---

## 💡 Bhalo prompt-er 5 ta niyom

| করুন | করবেন না |
|---|---|
| Error/log **হুবহু পেস্ট** করুন | "কাজ করছে না" — এতটুকু লিখে থামা |
| **Acceptance criteria** চেকলিস্ট দিন | ফলাফল কেমন হবে না বলে ছেড়ে দেওয়া |
| একটা প্রম্পটে **একটা কাজ** | ৫টা আলাদা কাজ একসাথে গুঁজে দেওয়া |
| **যা করবে না** সেটাও লিখুন | agent-কে অনুমান করতে দেওয়া |
| Verify করা যায়নি এমন কিছু থাকলে **বলতে বলুন** | fake "সব সবুজ" রিপোর্ট মেনে নেওয়া (RULE-8) |
