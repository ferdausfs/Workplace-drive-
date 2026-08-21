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

---

## 6. Repo #2 — Dogs-of-KAHAF (Guardian Shield) — CLONED + analyzed

- **URL:** https://github.com/ferdausfs/Dogs-of-KAHAF · **Branch:** `main` · **HEAD:** `be33b71`
- **What:** "Guardian Shield" — NSFW content blocker (package `com.guardian.shield`, minSdk 26, target 35, v2.3.1)।
- **Stack:** Kotlin, MVVM+Clean, Hilt, Room v2, DataStore, Coroutines/Flow, Material 3 dark,
  AccessibilityService + **TFLite on-device AI** (3 models: guardian_model / nsfw_model / gender_model, GPU+CPU fallback)।
- **61 Kotlin files** (curbox-এর 246-এর তুলনায় ছোট)। Core: `AiDetector.kt` (563 lines), `GuardianAccessibilityService.kt` (31KB), `RulesEngine.kt`।
- **Features:** AI NSFW detect · opposite-gender filter · keyword+regex · per-app block/whitelist · schedule ·
  PIN (SHA-256) · 3-strike→24h lock · anti-uninstall · activity log · onboarding · Islamic reel reminder overlay।

## 7. 🎯 FALSE-BLOCK ROOT-CAUSE ANALYSIS (code-verified — মূল কাজ)

User report: "onek besi false block kore"। Code-এ ৬টা স্পষ্ট উৎস পাওয়া গেছে:

| # | Cause | File | Evidence | Severity |
|---|---|---|---|---|
| A | **Hybrid soft-NSFW path** — NSFW score ≥0.58 হলে gender threshold 0.78→0.62; gender model পুরো ছবিতে চলে (avatar/thumbnail/product photo সহ) → fully-clothed মহিলার ছবি + weak 0.58 = block | AiDetector.kt `isOppositeGenderNsfw` | `isSoftNsfw` + `softGenderConf = (genderConf*0.80).coerceAtLeast(0.62)` | 🔴 HIGHEST |
| B | Legacy 3-class model-এ score **sum** করছে: `(scores[1]+scores[2]).coerceAtMost(1.0)` — দুটো unsafe class যোগ হয়ে inflate → false positive | AiDetector.kt `extractGuardianScore` | `3 -> (scores[1]+scores[2])` | 🔴 HIGH |
| C | **Regex keyword-এ word-boundary নেই** — `Regex(kw, IGNORE_CASE).containsMatchIn(text)` — `sex` ম্যাচ করে "Essex"/"sextant" | RulesEngine.kt `evaluateText` | regex branch-এ `\b` missing | 🟠 MED |
| D | Min text length 10→3 ("sensitivity") — ৩-char random string-এ keyword hit বেড়েছে | RulesEngine.kt | `text.length < 2` check only | 🟠 MED |
| E | Region scan খুব broad — যেকোনো `ImageView/avatar/photo/video` view >80px ধরে, benign ছবিও scan হয় | GuardianAccessibilityService `collectImageRegions` | className contains("Image"/"avatar"/"photo") | 🟡 LOW |
| F | Default thresholds একাধিক জায়গায় ভিন্ন: Constants gender=0.82 vs prefs default 0.78 vs AiDetector cached 0.70 vs soft 0.62 — confusion source | Constants.kt / GuardianPreferences / AiDetector | 4 ভিন্ন মান | 🟡 LOW |

### প্রস্তাবিত fix (এক-একটা আলাদা PR)
1. **A**: soft-NSFW path-এ gender match + skin/body-region evidence + higher nsfw floor দাবি করা
   (soft trigger তখনই যখন nsfw ≥ 0.58 **এবং** gender conf ≥ 0.85, বা gender model-এ crop)।
2. **B**: `3 -> max(scores[1], scores[2])` (sum নয়)।
3. **C**: regex keyword-এও word-boundary (বা auto-wrap: `(?iu)\b(?:kw)\b`)।
4. **D**: min length 3→5 (অথবা config-এ ফেরত)।
5. **E/F**: region filter stricter + single source-of-truth threshold।

## 8. INTEGRATION PLAN (curbox UI + এই blocker) — ⏳ architecture decision দরকার
- **Curbox agents.md নিয়ম:** "Ask before architectural change" — তাই ৩টা option:
  - **(ক) curbox fork + feature module**: curbox-এ "Guardian" reducer যোগ (curbox-এর নিজস্ব UI/theme-এই NSFW blocker চলে)।
  - **(খ) Dogs-of-KAHAF-এ curbox-সদৃশ UI rebuild** (app নিজে থেকে যায়, শুধু curbox-এর look)।
  - **(গ) দুটো আলাদা রেখে শুধু false-block fix** (কোন merge নয়)।
- User-এর আগের কথায় "curbox e sudu ei nsfw block add korbo" → **Option (ক)**-ই মনে হচ্ছে (curbox = shell, NSFW = feature)।
- Honest: এটা বড় কাজ (accessibility service + TFLite + Shizuku + UI integration)। ধাপে ধাপে করা হবে।

## 9. Sandbox limitation (আবার)
- **Android SDK নেই → compile সম্ভব নয়।** Kotlin code + pure-logic review/test পারি; build/device-test user-এর machine।

---

## 10. PHASE 1 STARTED — false-block fix (Dogs-of-KAHAF)

**Branch:** `fix/false-block-reduction` (base main `be33b71`). 3 files, 32+/26-.
- Fix 1: hybrid soft-gender lowering (0.62) removed → full genderConf (0.78) required.
- Fix 2: full-screen gender scan → `requireStrongNsfw=true` (NSFW gate 0.80), regions keep 0.68.
- Fix 3: regex keyword word-boundaries (unless user-anchored) — "sex" won't match "Essex".
- Deliberately NOT changed: 3-class score sum (model semantics unverifiable without .tflite) — flagged.
- Regex semantics verified with equivalent harness. **No Android build in sandbox — user must run ./gradlew assembleDebug.**
- PR body + patch: drive `pr/falseblock_fix.patch` + `pr/PR_BODY_falseblock_fix.md`.
- Next: user PR → merge → device test. Then Phase 2 (curbox integration) plan.

---

## 11. PHASE 2 — DOK-ai = MAIN APP (user decision)

**Repo:** https://github.com/ferdausfs/DOK-ai ("second version of Dog's of Kahaf", public, empty)।
**Decision:** এখানেই সব হবে — curbox UI/theme + Dogs-of-KAHAF-এর NSFW feature = DOK-ai।

### Integration surface analysis (দুটো codebase ম্যাপ)
- **curbox-এ যা আগে থেকেই আছে** (port করতে হবে না): AppBlocker, KeywordBlocker, ReelBlocker,
  AntiUninstallBlocker, FocusModeBlocker, UI/theme/settings/focus infra, uihider, nfc।
- **Dogs-of-KAHAF থেকে যা port করতে হবে** (curbox-এ নেই):
  1. AI detection engine — `AiDetector.kt` (3 TFLite: guardian/nsfw/gender + GPU/CPU + grid vote)
     + `ModelImportManager.kt` (model import UI)
  2. Content scan — accessibility event → screenshot → AI → block (curbox-এর AppBlockerService-এ merge)
  3. `RulesEngine.kt` (NSFW keyword/regex + per-app block/whitelist + schedule) — curbox-এর
     KeywordBlocker-এর সাথে মিলিয়ে/সম্প্রসারিত
  4. Settings: AI threshold / NSFW gate / gender threshold / grid-vote sliders + gender select
  5. Block overlay (AI-detection block screen) + Activity log
- **False-block fix (Phase 1)** Dogs-of-KAHAF-এ merged (`e05d9c2d`) — DOK-ai-তে port করার সময়
  ওই fix-গুলো বেসলাইনে রাখা হবে (soft-hybrid gone, requireStrongNsfw, regex \b)।

### Milestones (প্রতিটা = একটা PR)
- **M0 — Seed**: curbox base DOK-ai-তে (user action, নিচে command)।
- **M1 — AI engine port**: AiDetector + ModelImportManager + TFLite deps (pure logic, UI ছাড়া)।
- **M2 — Service merge**: curbox AppBlockerService-এ content-scan hook (agents.md invariants মানতে হবে:
  feature-fail-এ crash নয়, CrashLogger.logNonFatalError)।
- **M3 — Settings UI**: curbox-এর reducer pattern-এ "Guardian AI" reducer (threshold sliders, gender, keywords)।
- **M4 — Overlay + log**: AI-block overlay + activity log (curbox-এর existing overlay/UI reuse)।
- **M5 — Device test + tune**: build/install, false-block vs miss balance।

### License note (honest)
- Curbox = GPL-3.0 → DOK-ai (curbox-ভিত্তিক) অবশ্যই **GPL-3.0** রাখতে হবে। User-এর নিজের
  Dogs-of-KAHAF কোড (Personal use) নিজেরই, তাই relicense-এ সমস্যা নেই।
- Build/compile sandbox-এ নেই → প্রতিটা milestone user-এর machine/CI-তে build হবে।

---

## 12. M0 DONE — DOK-ai seeded

- DOK-ai main = `a50fe7bf` "Initial: Curbox base (screen-time manager) — GPL-3.0" (verified via GitHub API)।
- Method: working-tree tarball (git history-র network problem এড়াতে) → local commit → force push।
- Root-এ .github, app, gradle, LICENSE, settings.gradle.kts — curbox-এর full structure।
- **M1 next:** Dogs-of-KAHAF-এর AI detection engine (AiDetector + ModelImportManager + RulesEngine + TFLite deps)
  DOK-ai-তে port (package adapt: com.guardian.shield → DOK-ai namespace)।

---

## 13. M1 DONE — AI detection engine ported to DOK-ai (PR-ready)

- DOK-ai main (`a50fe7bf`) থেকে branch `feat/guardian-m1-ai-engine`।
- **4 new files** `neth.iecal.curbox.guardian/`: GuardianConstants, GuardianKeywordMatcher (pure logic),
  GuardianModelImportManager, GuardianAiDetector (TFLite core) + TFLite gradle deps।
- **Phase-1 false-block fixes বেসলাইনে রাখা** (soft-hybrid gone, requireStrongNsfw, regex \b)।
- **Adaptation:** Hilt→plain singleton, Timber→Log, GuardianPreferences→GuardianConfig (M3-তে DataStore wire)।
- patch: drive `pr/m1_ai_engine.patch` (sha 803748c6…), PR body `pr/PR_BODY_m1_ai_engine.md`।
- ⚠️ Compile হয়নি (Android SDK নেই sandbox-এ) — user merge-এর পর CI build; syntax error হলে আমি ঠিক করবো।
- **Next M2:** accessibility service-এ content-scan hook (screenshot → region scan → block)।

---

## 14. M1.5 — CI workflow fix (DOK-ai build চালু)

- **Root cause found:** DOK-ai-তে curbox-এর ৪ workflow copy — trigger `kt-rewrite` branch-এ hardcode
  (DOK-ai = main) + Discord/Telegram/VirusTotal/SIGNING_KEY secrets mismatch → Actions runs=0।
- **Fix:** নতুন clean `build.yml` (push/PR/main, JDK17+SDK, assembleFdroidDebug, artifact upload);
  পুরনো ৪ workflow সরানো।
- patch: drive `pr/m15_ci_fix.patch` (sha ab358ba8…), PR body `pr/PR_BODY_m15_ci_fix.md`।
- Merge-এর পর Actions-এ প্রথম real compile → M1-এর TFLite port-ও compile-check হবে।
- **Next:** build সবুজ হলে M2 (accessibility service-এ NSFW scan hook)।

---

## 15. M2 DONE — accessibility service-এ NSFW scan hook (PR-ready)

- `blockers/GuardianBlocker.kt` (new, 302 lines) + `services/AppBlockerService.kt` (+15 wiring)।
- Scan path: WINDOW_STATE/CONTENT_CHANGED → keyword text scan + throttled AI screenshot (API 30+,
  full-screen requireStrongNsfw=true + legacy isUnsafe) → block = HOME + Toast (M4-এ full overlay)।
- agents.md invariants: try/catch + CrashLogger.logNonFatalError + CancellationException rethrow।
- Config: SharedPreferences `guardian_prefs` (M3 UI-র setter ready)।
- patch: drive `pr/m2_service_hook.patch` (sha d66e5b5e…), PR body `pr/PR_BODY_m2_service_hook.md`।
- ⚠️ compile = CI (মার্জের পর auto-build)। **Next M3:** settings UI (toggle/gender/threshold/model import)।

---

## 16. M3 DONE — Guardian settings UI (PR-ready)

- `GuardianFragment.kt` (new, 195 lines) + `fragment_guardian.xml` + `item_guardian_keyword.xml` +
  `card_guardian` in reducers + FragmentActivity registration + 20 strings + GuardianBlocker.refresh()।
- Controls: enable toggle, gender (None/M/F), 3 threshold sliders + grid votes, keyword add/remove,
  3 model imports (SAF picker)।
- Pattern: curbox reducer/card/fragment style, SharedPreferences + broadcast reload। No Compose।
- patch: drive `pr/m3_settings_ui.patch` (sha 6744451e…), PR body `pr/PR_BODY_m3_settings_ui.md`।
- ⚠️ compile = CI। **Next M4:** AI-block overlay (go-home+toast → proper block screen) + activity log।

---

## 17. M4 DONE — AI-block overlay + activity log (PR-ready)

- `GuardianBlockActivity.kt` (full-screen block: reason/pkg + go-home + settings) + layout +
  manifest registration + `GuardianBlocker.logBlock()` (SharedPreferences 500-entry ring buffer) +
  GuardianFragment-এ block-log view/clear + 8 strings।
- block action: GuardianBlockActivity.start() + fail-open go-home fallback।
- patch: drive `pr/m4_overlay_log.patch` (sha 3e3d706d…), PR body `pr/PR_BODY_m4_overlay_log.md`।
- ⚠️ compile = CI। **Next M5:** device test (model import + enable + false-block/miss verify)।

---

## 18. M5.5 DONE — model bundle + validity check (PR-ready)

- **Model converted নিজে:** NSFWJS MobileNetV2 (npm, uint8) → float32 TFLite 224x224x3 5-class।
  Verified: 266/266 weights dequantized+loaded, TFLite inference OK (gray img → Drawing 0.84/Porn 0.009)।
  SHA 8229bafa…, 10,317,360 bytes। Deliverable: DOK-ai-models.tar.gz (+MODEL_README)।
- **Code (4 file, +86):** GuardianModelImportManager.modelStatus() (imported/bundled/missing) +
  verifyFile() (TFLite shape check, wrong-file reject) + Fragment status UI + gender-hint।
- **Split:** code patch `pr/m55_model_bundle.patch` (sha 294ad87d…); model files আলাদা commit
  (আমার দেওয়া command-এ user করবে — 20MB binary transport এড়াতে)।
- **Next (M5 final):** merge + model commit + CI build → install → enable → device test।

---

## 19. M5.6 — NSFW-not-blocking root cause + fix (PR-ready)

- **Sandbox test:** bundled model ২ safe ছবিতে চালানো → Neutral 0.97/Porn ~0 (no false positive),
  weights meaningful। Model-এর দোষ নয়।
- **Root cause (code):** Phase-1 overcorrection-এর ৩ strictness — (1) `aiThreshold.coerceAtLeast(0.80)`
  floor (slider 0.72 অকার্যকর), (2) grid `voteNeeded=+1` (৩ cell ≥0.80 লাগত), (3) full-screen gate 0.80,
  (4) variance 200..8500।
- **Fix:** threshold `coerceIn(0.50,0.95)` · voteNeeded=gridVoteCount(2) · full-screen 0.70 · variance 150..9000।
- patch: drive `pr/m56_threshold_fix.patch` (sha a0d0e1da…), PR body `pr/PR_BODY_m56_threshold_fix.md`।
- **Honest:** NSFW-positive test user-এর phone-এই (আমি NSFW fetch/generate করিনি)। Threshold slider-এ tune।

---

## 20. DOK-ai DROPPED → Dogs-of-KAHAF = MAIN APP (user decision 2026-08-15)

- **Decision:** নতুন app (DOK-ai) বাদ। Dogs-of-KAHAF (Guardian Shield)-এই blocking কাজ করে →
  এটাই main app; একে "complete productivity" বানানো হবে। কাজ এখন `ferdausfs/Dogs-of-KAHAF`-এ।
- **Bug audit (static):** CI release automation-এ ৪ bug (tag v2.2.0 hardcoded → release fail,
  artifact name stale, wrapper jar mismatch, stale body) → FIXED (pr/ci_fix.patch)।
  Threshold floor 0.80 (slider half-range dead) → FLAGGED, behavior change তাই user-এর call।
  Stability code (watchdog/backoff/containment) intact; কোনো TODO/crash-pattern পাইনি।
  ⚠️ sandbox-এ SDK নেই — compile হয়নি, CI=truth।
- Reports: `reports/Dogs_of_KAHAF_BUG_AUDIT_2026-08-15.md` + PR body `pr/PR_BODY_ci_fix.md`।
- **Next:** productivity feature roadmap (user priority নিতে হবে)।

---

## 21. Dogs-of-KAHAF v2.4.0 — safe/unsafe + gender removal (PR-ready)

- **User final spec:** ৩ mode না, gender-ও না। শুধু **safe vs unsafe** (২ class) + gender detection
  পুরো বাদ + stable (false block কম)।
- **Changes (8 file, +31/−532):** AiDetector (gender/nsfw interpreter + isOppositeGenderNsfw + score
  extractor বাদ, threshold floor 0.80→coerceIn(0.50,0.95), vote +1→coerceIn(1,4)); Service (২ gender
  call site বাদ, legacy-only); Settings UI (gender chips/sliders/model import বাদ, XML sections সরানো);
  ViewModel/Preferences (gender keys/flows বাদ); version 2.4.0; CI release dynamic tag।
- **Verify:** brace/paren 0 (৪ file), XML valid, dangling gender/nsfw refs = 0। ⚠️ compile=CI।
- patch: `pr/v240_safeunsafe.patch` (sha 5b525591…), PR body `pr/PR_BODY_v240_safeunsafe.md`।
- **Next:** merge → CI build → device test → threshold tune (slider-ই এখন, floor নেই)।

---

## 22. v2.4.0 patch re-based (PR #16 merge → base moved) — 2026-08-15

- **PR #16 (CI release fix) merged** → `main` = `a2af6372` (build.yml dynamic tag ✅; v2.3.1 tag/release auto-created)।
- **"PR হলো না" কারণ:** আগের v2.4.0 patch-এ build.yml hunk ছিল, কিন্তু ওই change main-এ already আছে →
  `git apply` fail। Patch stale।
- **Fix:** build.yml বাদ দিয়ে 7-file patch regenerate — `pr/v240_safeunsafe_v2.patch` (sha dd988e5c…), +17/−517।
- **Verify:** `git apply --check` OK on base (e05d9c2 + merged ci_fix.patch = a2af6372-equivalent)। brace/paren 0, XML valid, dangling refs 0। ⚠️ compile=CI।
- PR body: `pr/PR_BODY_v240_safeunsafe_v2.md`। Branch `feat/v240-safeunsafe` GitHub-এ empty (== main) → delete করে fresh push।
- **Next:** apply → push → PR → merge → CI → device test → threshold tune (slider-ই এখন, floor নেই)।

---

## 23. v2.4.1 — cartoon false-block fix (Drawing-gate) — 2026-08-16

- **User report:** v2.4.0 merge + device test-এর পরও cartoon block করে। "শুধু safe/unsafe 2-class model আছে কি?" জিজ্ঞেস করেছেন।
- **Root cause (code):** v2.4.0-এ `extractGuardianScore` 5-class-এ শুধু `max(Hentai,Porn,Sexy)` — NSFWJS-এর
  **Drawing** (safe cartoon/anime) class ignore → cartoon frame-এ সামান্য Hentai score-এই block।
- **Model প্রশ্নের honest answer:** 2-class off-the-shelf on-device model নেই যা cartoon-এ ভালো হবে।
  OpenNSFW2 binary কিন্তু photo-trained → anime/cartoon-এ worse। NSFWJS-এর Drawing class-ই সঠিক tool;
  model বদল নয়, Drawing use করাই fix।
- **Fix:** `drawnNsfw = if (Hentai > Drawing) Hentai else 0`; `photoNsfw = max(Porn,Sexy)` direct;
  score = max(photo, drawn)। + full-frame per-class debug log (D/H/N/P/S)। version 2.4.1 (code 10)।
- **Trade-off:** Drawing ≥ Hentai ambiguous case এখন safe → anime-hentai edge miss-এর সামান্য risk (intentional, user priority)।
- **Verify:** GitHub main 049c47ac AiDetector.kt byte-identical to base (curl diff) ✅; apply-check OK ✅;
  brace/paren 0 ✅। ⚠️ compile=CI।
- patch: `pr/v241_drawing_gate.patch` (sha fe4133dd…), PR body `pr/PR_BODY_v241_drawing_gate.md`।
- **Next:** merge → CI build → device test (cartoon + photo NSFW + anime hentai) → log-ভিত্তিক tune।

---

## 24. v2.4.2 — precision-first scoring (cat/cartoon/safe false-block fix) — 2026-08-16

- **User report (v2.4.1-পরেও):** YouTube-এ cat video block, safe content block, cat cartoon/AI cartoon block।
- **Root cause (code):** Drawing-gate শুধু Hentai-vs-Drawing; cat/fur/গায়ের রং → NSFWJS "Sexy"/"Porn"
  মাঝারি score (0.4–0.7)। Service `runContentAwareScan` video surface + thumbnails-এ প্রতিটা region-এ
  isUnsafe চালায়; grid (4×5) noisy Sexy-কে amplify করে threshold 0.65 পার করিয়ে block।
- **Fix:** `danger = (Porn+Sexy+Hentai) − (Neutral+Drawing)`; score = (danger+1)/2। score<0.55 → safe (no grid);
  grid vote bar 0.80। diagnostic log `Guardian out[N]=...` (model size+raw score reveal)।
- **Sim verify:** cat 0.42 SAFE · cat cartoon 0.10 SAFE · AI cartoon 0.12 SAFE · porn 0.96 BLOCK ·
  hentai 0.90 BLOCK · lingerie 0.94 BLOCK।
- **Trade-off:** precision↑ recall↓ (ছোট thumbnail NSFW miss-এর সম্ভাবনা; full-screen ঠিকই)। model=5-class
  NSFWJS ধরে নেওয়া; না হলে log-ভিত্তিক fix।
- **Verify:** apply-check OK on 2a9e8135 ✅ brace/paren 0 ✅ compile=CI। patch `pr/v242_precision_first.patch`
  (sha e4ebcdea…), PR body `pr/PR_BODY_v242_precision_first.md`।
- **Next:** merge → CI → device test (cat/cartoon + real NSFW) → log পাঠালে model size confirm।

---

## 25. Workspace cleanup + FTT daily checkup (2026-08-16)

- **v2.4.2 merged (PR #19)** → Dogs-of-KAHAF main `9cc1a6c5`, tag v2.4.2 released ✅ (precision-first live)।
- **FTT daily checkup (infra, sandbox-থেকে):** সব healthy —
  - Worker `fttotcv6.umuhammadiswa.workers.dev`: healthy v6.10.4; apiKeys 17/17, quota today 330;
    push enabled + token valid (@fttbotbot), delivered 26/24h; subscriber 8429957782 OK (watchlist 6,
    minConf 60); last push 03:00:44Z ADA/USD SELL (pushed 1/matched 1, no error); scan fresh (~05:10Z,
    14 pairs, 300s interval); news blackout none; **forex CLOSED (রবিবার/weekend)**, crypto 24/7।
  - Bot: live v4.5.1 ✅।
  - Repos: worker main `d6c04460` (no drift), bot main `b2e7f331` (no drift), 0 open PR ✅।
- **Phase F daily = phone-side** (data সেখানে): `phase_f_snapshot.sh`, `entryhit_corrected_analysis.py`,
  `day3_analysis.py`, `d4_run.py`। Forward WR 44.3% (breakeven 55.6% এখনো clear না) — research item।
- **Workspace cleanup:** শুধু uploads/ (user files) + journal + runbook রাখা; Dogs-of-KAHAF clone,
  পুরনো patch/PR body/sync scripts, drive clone-এর বাকি সব মুছে ফেলা। re-clone (git clone https) verified OK।
- **নিয়ম:** প্রতিবার যা লাগে re-derive/re-clone; কোনো file-এর push confirmed হলে সেটা clean।

---

## 26. Phase F daily checkup (sandbox, drive data) — 2026-08-16

- **User request:** drive-এ data আছে → sandbox-এ analysis চালাও ("আজকেরটাই দেখো")।
- **Data:** drive `data/` tarballs (FULL 08-12 + 08-14, 08-15) → 26 দিন, 6,213 signals (dedup), 5,997 decided।
  আজকের (08-16) snapshot এখনো push হয়নি; latest = 08-15 (Saturday, weekend → n=5)।
- **Results (scripts:** entryhit_corrected_analysis.py, d4_run.py, custom full_analysis.py):
  - Full forward WR **43.5%** (CI 42.3–44.8) — breakeven 55.6% ❌
  - Era: PRE 41.8% (n=4462) → **POST-FIX-EH 48.6%** (n=1535, +6.8pp) → last 7d 49.6% (n=957) — improvement real, breakeven নয়।
  - Per-day: 08-11 56.4%, 08-12 58.3% (breakeven-এর উপরে, ছোট n); 08-14 54.2%; 08-15 n=5 (weekend)।
  - FIX-EH: eh-MISS WR 53.0% (≠100%) → tautology ভাঙা ✅; entryHit selector-ও নয় (HIT 47.9% vs MISS 53.0%)।
  - D4 ML: LEGIT confident-only 47.4% (CI 32.5–62.7) → no edge; leakage diagnostic 59.7% (fake edge only)।
- **Report:** `reports/PHASE_F_DAILY_2026-08-16.md` (sync script-এ যাচ্ছে)।
- **Verdict:** system better but not profitable; aiAgreed/grade/entryHit কেউ reliable selector না; Mon 08-17 snapshot পর্যন্ত নতুন কাজ না।

---

## 27. Phase F daily checkup — 2026-08-17 (Monday, live pull from worker)

- **নতুন ক্ষমতা:** sandbox থেকে worker API direct pull → snapshot phone ছাড়া; checkup-এর জন্য drive tarball push আর লাগে না (audit trail-এর জন্য চালু থাকবে)।
- **Data:** live 18-pair × 500 signal (08-17 12:42 UTC) + drive tarballs, dedup by id → 6,099 decided।
- **Results:**
  - Full forward WR 43.5% (CI 42.3–44.8) — breakeven 55.6% ❌ (unchanged, expected)।
  - POST-FIX-EH 48.4% (n=1637) ✅ improvement টিকে আছে; PRE 41.8%।
  - **Last 7d 52.9% (CI 48.6–57.2)** — breakeven-এর দিকে, এখনো clear নয়।
  - Per-day: 08-16 55.0% (n=40), 08-17 38.5% (n=39, intraday Monday)।
  - FIX-EH: eh-MISS 52.2% → tautology ভাঙা ✅; entryHit selector নয়।
  - D4 ML: LEGIT confident-only 52.4% (CI 37.7–66.6) → no edge।
- **Report:** `reports/PHASE_F_DAILY_2026-08-17.md`।
- **Next:** 08-17 দিন শেষ হলে (UTC 08-18) আবার checkup; breakeven-clear হলে তবেই conditional strategy।
