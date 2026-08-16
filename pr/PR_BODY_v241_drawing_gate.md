# fix(v2.4.1): cartoon false-block — use the Drawing class as gate

**Repo:** `ferdausfs/Dogs-of-KAHAF` · **Base:** `main` (`049c47ac`, = v2.4.0) · **Branch:** `fix/v241-drawing-gate`

## Problem (আপনার report: "cartoon এখনো block করে")
v2.4.0-তে `extractGuardianScore` 5-class model-এ শুধু `max(Hentai, Porn, Sexy)` নেয়।
NSFWJS-এর **`Drawing` class (= safe cartoon/anime)** পুরো ignore করা হতো। ফলে cartoon/anime/Oggy/Mr Bean
frame-এ মডেল সামান্য `Hentai` score (0.5–0.7) দিলেই block হয়ে যায় — কারণ Drawing-এর কথা কেউ দেখছিল না।

## "শুধু safe/unsafe ২-class model" আছে কি? (honest answer)
না — এমন off-the-shelf on-device model নেই যা cartoon-এ **ভালো** হবে। বরং উল্টো:
- NSFWJS-এই হলো best: এতে আলাদা **`Drawing`** class আছে — এটাই safe-cartoon-এর signal।
- **OpenNSFW2** (Yahoo) একটা binary safe/nsfw model, কিন্তু photo-NSFW-তে trained — anime/cartoon-এ
  আরও বেশি false-positive দেয় (Drawing concept-ই নেই)। তাই model বদলানো cartoon-কে আরও খারাপ করবে।
- তাই model বদলানো নয় — current model-এর **Drawing class-টা use করা**-ই সঠিক fix।

## Fix (2 files, +28/−9)
**`AiDetector.kt`** — 5-class scoring-এ এখন:
```
photoNsfw = max(Porn, Sexy)          // photo NSFW আগের মতো direct
drawnNsfw = if (Hentai > Drawing) Hentai else 0   // cartoon/anime: শুধু তখনই block,
                                                   // যখন মডেল adult-anime > safe-art confident
score     = max(photoNsfw, drawnNsfw)
```
- Cartoon (Drawing > Hentai) → `drawnNsfw = 0` → block হয় না ✅
- আসল hentai (Hentai >> Drawing) → block হয় ✅
- Plus: full-frame inference-এ per-class debug log `D=.. H=.. N=.. P=.. S=..` যাতে ভবিষ্যতে
  ঠিক কোন class trigger করছে দেখে tune করা যায়।

**`build.gradle.kts`** — versionName 2.4.0 → **2.4.1**, versionCode 10 (release tag-এর জন্য)।

## Trade-off (honest)
যে frame-এ মডেল `Drawing ≥ Hentai` (ambiguous drawn content) — সেটা এখন **safe** ধরা হবে। অর্থাৎ
আসল anime-hentai-র কিছু edge case-এ miss বাড়তে পারে (false-negative)। আপনার priority
("cartoon block হবে না") মেনে এটা intentional। Device test-এ NSFW anime দিয়েও দেখবেন — miss করলে
threshold/rule tune করবো।

## Verification (honest)
- ✅ GitHub main `049c47ac`-এর AiDetector.kt আমার base-এর সাথে **byte-identical** (curl diff) → patch clean apply হবে
- ✅ `git apply --check` OK (fresh base commit-এ)
- ✅ brace/paren balance 0 (comment-stripped)
- ⚠️ **Compile = CI** — sandbox-এ Android SDK নেই। Merge-পর CI build-ই truth।

## Test checklist (আপনার device)
1. Cartoon / Oggy / Mr Bean / anime art → **block হবে না** ✅
2. Real photo NSFW → block ✅
3. Real anime hentai → block চান তো দেখবেন ✅ (miss করলে জানান — rule tune করবো)
4. Logcat-এ এখন `Guardian classes D=.. H=.. N=.. P=.. S=..` পাবেন — কোনো frame ভুলভাবে
   block করলে ওই line-টা পাঠান, exact cause দেখবো।
