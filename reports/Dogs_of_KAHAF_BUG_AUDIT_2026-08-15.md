# 🔬 Dogs-of-KAHAF (Guardian Shield) — Bug Audit 2026-08-15

**Auditor:** Arena main agent · **Base:** `main` @ `e05d9c2` (false-block fix merged) ·
**Method:** static review (Android SDK নেই sandbox-এ → compile হয়নি; CI = truth)।

## Verdict summary
Code-র stability অনেক ভালো (v2.3.0-র watchdog/backoff/containment কাজ আছে)। **User-visible blocking
code-এ serious bug পাইনি** — সমস্যা মূলত **CI/release automation-এ** + কিছু version inconsistency।

## 🔴 FIXED (PR-ready): CI release automation
| # | Bug | Impact |
|---|---|---|
| 1 | `tag_name: v2.2.0` hardcoded | প্রতিটা build-এ "Create GitHub Release" fail (tag exists) |
| 2 | artifact name v2.2.0 (app 2.3.1) | stale |
| 3 | wrapper jar 8.4.0 download overwrites committed 8.8 jar | অপ্রয়োজনীয় + mismatch risk |
| 4 | release body stale | cosmetic |
→ Fix: dynamic version (versionName-থেকে tag/name/artifact) + wrapper step বাদ। `pr/ci_fix.patch`।

## 🟡 FLAGGED (fix করিনি — behavior change, আপনার call)
- **`AiDetector.isUnsafe` threshold floor:** `cachedThreshold.coerceAtLeast(0.80f)` — settings-এর
  slider 0.30–0.80 range-এ যা-ই দেন, আসলে 0.80 হয়। Slider-এর অর্ধেক range dead।
  **কিন্তু আপনি বলেছেন blocking কাজ করে** — তাই এখন ছুঁইনি। চাইলে (a) slider-কে respect করাই
  (`coerceIn(0.30,0.95)`) নাকি (b) slider-এর min 0.80 করি — বলুন।
- `voteNeeded = gridVoteCount + 1` (=৩) — screenshot-এ ৩ cell ≥0.80 লাগে। Strict (কম false-block
  কিন্তু কিছু miss)। এটাও আপনার call।

## ✅ Checked-and-clean
- Foreground service type (Android 14+): `specialUse` + compat — সঠিক ✅
- BlockingEngine: throttle + temp-block + overlay + log — সঠিক ✅
- Accessibility service: watchdog (stuck-flag reset), screenshot backoff, CancellationException
  rethrow — সব v2.3.0-র stability কাজ intact ✅
- ViewBinding `!!` — standard pattern, bug না ✅
- TODO/FIXME/HACK — 0 ✅
- false-block fix (soft-hybrid removed, requireStrongNsfw, regex \b) — main-এ present ✅

## ⚠️ Honest limitation
Sandbox-এ Android SDK নেই → **compile/run করিনি**। Runtime bug (device-specific) ধরতে গেলে
user-এর logcat/device test দরকার। Static review-এ উপরেরটুকুই পেয়েছি।

## Product direction (পরের ধাপ)
User decision: Dogs-of-KAHAF = **main app**, একে "complete productivity" বানানো। Feature roadmap
আলাদা করে প্রস্তাব করা হয়েছে (নিচে) — priority user-এর কাছে।
