# 📱 PROJECT JOURNAL — Curbox Android (productive-app merge)

**Started:** 2026-08-15 · **Owner:** ferdausfs · **Main agent:** Arena
**Goal (user):** curbox-android-এর **সব function** + **আরও ১টা repo** (link pending) একত্র করে
একটা ভালো মানের productive Android app। User-এর ধারণা: repo-তে অনেক bug, ঠিকমতো কাজ করে না।

---

## 1. Repo #1 — curbox-android (CLONED + analyzed)

- **URL:** https://github.com/curbox-app/curbox-android
- **Default branch:** `kt-rewrite` · **HEAD:** `f86e6bf` (2026-08-15 clone)
- **What it is:** Curbox — open-source **screen-time / digital-wellbeing** app
  (F-Droid + Google Play-তে published; GPL-3.0; HowToMen/other reviewers-এ featured)।
- **Tech stack (hard constraints — agents.md):**
  - Kotlin, **classic Views + Fragments + ViewBinding** (Compose/নতুন Navigation নিষিদ্ধ)
  - JVM target 1.8 · Gradle 8.13 · Room DB · AIDL API · Shizuku · MPAndroidChart
  - Package root: `app/src/main/java/neth/iecal/curbox`
  - Modules: `:app` + `:apitester` (Curbox API-র sample client)
  - **246 Kotlin files**: ui(89) data(38) utils(28) blockers(25) services(6) trackers(5) api(5)

### Functions (Readme + code থেকে ম্যাপ করা)
| Area | Features |
|---|---|
| Blocking & Control | App/Website block · Tamper protection · Short-form (Reels/Shorts) block · Granular UI hiding · URL-path block |
| Insights | Usage analytics · Focus statistics · Live scroll counter · Attention-span tracking · Session timer |
| Mindful tools | Focus mode · Scheduled DND · Per-app grayscale · Scheduled usage limits · Home-screen widgets |
| Unlock mechanisms | Strict block · Timed unlock · Dynamic selection · **QR/Barcode unlock** · **Sentence retyping** · Unlock limits · **NFC** · **Adaptive Math** |
| Dev | **Curbox API** (AIDL, version 2, per-app permission) — external apps control focus/settings/stats |

### Key files (architecture anchors)
- `services/AppBlockerService.kt` — accessibility service (must never crash on feature failure)
- `blockers/` — AppBlocker, BrowserBlocker, FocusModeBlocker, KeywordBlocker, ReelBlocker,
  AntiUninstallBlocker, uihider/ (UI-hiding scripts)
- `data/db` (Room), `data/sync` (cross-device sync), `api/` (AIDL), `nfc/`, `trackers/`
- `agents.md` — repo-র নিজস্ব agent-guide (পড়া হয়েছে; নিয়ম মানতে হবে)

### Build/verify limitation (honest)
- **এই sandbox-এ Android SDK নেই** → build/compile চালানো যায় না।
- আমি করতে পারি: static analysis, code review, logic-bug fix, pure-logic unit test।
- **Compile/install/device-test আপনার machine (Android Studio / Termux+gradle) লাগবে।**

---

## 2. Repo #2 — ⏳ LINK PENDING
User দেবে। পাওয়ার পর:
- clone → function-map → overlap/conflict analysis → merge/integration plan
- journal-এ update

---

## 3. Bug investigation — ⏳ শুরু হয়নি (spec অপেক্ষায়)
User-এর report: "ঠিকঠাক কাজ করে না"। **কোন feature/কোন symptom** — এটা user-এর কাছ থেকে নিতে হবে:
- কোন screen/feature ভাঙা? (block কাজ করে না? scroll counter? grayscale? push?)
- কোন device/Android version?
- Logcat/error message থাকলে সেটা।

## 4. Open decisions (user-এর কাছে)
1. **Repo #2 link** — hard dependency।
2. "Merge" মানে কী: (ক) curbox-এ feature যোগ, (খ) দুইটা আলাদা app এক করা, (গ) curbox-এর ভিত্তিতে নতুন app?
3. কোন bug গুলো ঠিক করতে হবে (spec)।

## 5. Working protocol (এই session থেকে)
- PR-first (branch → change → test → PR → user merge)
- agents.md-এর non-negotiable invariants মেনে চলা (accessibility service safety ইত্যাদি)
- journal update প্রতি ধাপে → drive push
- কোডের জন্য GitHub repo = canonical; এই journal + reports drive-তে
