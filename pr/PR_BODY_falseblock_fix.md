# fix(detection): reduce false blocks — full gender confidence + strict full-screen NSFW + regex word boundaries

**Repo:** `ferdausfs/Dogs-of-KAHAF` · **Base:** `main` (`be33b71`) · **Branch:** `fix/false-block-reduction`

## Problem (user-reported)
"Onek besi false block kore" — benign content (avatars, thumbnails, feed content, profile photos,
normal product/news images) is being blocked too aggressively.

## Root causes (code-verified) + fixes

### 1. Hybrid "soft-NSFW" lowered the gender bar to 0.62 — 🔴 biggest false-block source
`AiDetector.isOppositeGenderNsfw` had an "ULTIMATE LEVEL" path: any image with a weak **0.58** NSFW
score got the opposite-gender confidence requirement cut from 0.78 → **0.62**. A fully-clothed person
in a thumbnail/avatar + a noisy 0.58 NSFW score → block.

**Fix:** removed the soft-lowering. The opposite-gender block now always requires the **full** gender
confidence (0.78). The NSFW gate (≥ 0.68) already ran before gender, so real NSFW with a clearly
opposite-gender subject still blocks.

### 2. Full-screen screenshot gender check was noisy
The fallback AI scan ran the gender model on the **entire screenshot** (UI chrome, text, many small
images) at the same 0.68 NSFW gate as clean content regions.

**Fix:** added `requireStrongNsfw` flag — the full-screen call now requires NSFW **≥ 0.80** before the
gender model is consulted. Content-region scans keep the normal 0.68 gate.

### 3. Regex keywords matched inside words
`RulesEngine.evaluateText` ran user regex keywords without word boundaries, so `sex` matched "Essex"/
"sextant" (the plain-keyword path already had `\b`; the regex path didn't).

**Fix:** regex keywords are wrapped in word boundaries unless the user already anchored them
(`^`, `$`, `\b`, `\B`). Verified: `sex` no longer matches "Essex"/"sextant" but still matches "sex".

## Not changed (deliberately)
- The 3-class legacy score `scores[1] + scores[2]` (union probability) — could not verify model output
  semantics without the .tflite files, so left as-is. Flagged for later (possible sigmoid-union
  `1-(1-a)(1-b)` correction).
- `SOFT_NSFW_THRESHOLD` constant is now unused (kept for reference; harmless).

## Verification
- Static review of all 3 files (diff attached as `pr/falseblock_fix.patch`).
- Word-boundary regex semantics verified with a Java-regex-equivalent harness
  (Essex/sextant/class → no match; sex/ass → match).
- ⚠️ **No compile/device test run** — this sandbox has no Android SDK. Before merge, run on your
  machine: `./gradlew assembleDebug` (GitHub Actions `build.yml` also builds on push).

## Deploy
Build + install from this branch; test: feed containing normal opposite-gender profile photos /
thumbnails should no longer block; real NSFW should still block (NSFW ≥ 0.68 + gender ≥ 0.78, or
full-screen NSFW ≥ 0.80 + gender ≥ 0.78).
