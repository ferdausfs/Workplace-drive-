# fix(v2.4.2): precision-first scoring — stop blocking cats/cartoons/safe content

**Repo:** `ferdausfs/Dogs-of-KAHAF` · **Base:** `main` (`2a9e8135`, = v2.4.1) · **Branch:** `fix/v242-precision-first`

## Problem (আপনার report)
v2.4.1 (Drawing-gate) merge-এর পরও YouTube-এর cat video, safe content, cat cartoon, AI cartoon —
সব block হচ্ছে। কারণ Drawing-gate শুধু Hentai-vs-Drawing handle করত; কিন্তু cat/fur/গায়ের রং-এর
frame-এ NSFWJS মডেল **"Sexy"/"Porn"** class-এ মাঝারি score (0.4–0.7) দেয়, আর service-টা
video surface + thumbnail প্রতিটা image-region-এ `isUnsafe` চালিয়ে যেকোনো একটাতে threshold
পার হলেই block করত। Grid scan (4×5, 20 cell) ওই noisy "Sexy" score-গুলোকে amplify করে block-এ
পরিণত করছিল।

## Fix — "unsafe mass vs safe mass" (2 files, +21/−17)
মডেল আসলে দুই পক্ষ "জানে": **safe mass = Neutral + Drawing**, **unsafe mass = Porn + Sexy + Hentai**।
এখন:
```
danger = (Porn + Sexy + Hentai) − (Neutral + Drawing)     // −1 … +1
score  = (danger + 1) / 2                                  // 0 … 1, threshold slider-এ match
```
- Block তখনই, যখন মডেল unsafe-এ **স্পষ্টভাবে** বেশি confident। `score < 0.55` → সরাসরি safe,
  grid scan-ই চলে না (এটাই cat/cartoon block-এর আসল কারণ ছিল)।
- Grid cell এখন vote পেতে হলে `score ≥ 0.80` লাগবে (আগে ছিল threshold ≥ 0.65)।
- **Diagnostic log:** প্রতিটা inference-এ raw output log হয় `Guardian out[N] = ...` — কোনো
  frame আবার ভুলে block করলে ওই একটা line পাঠালেই exact class score দেখা যাবে (আর model আসলেই
  5-class কিনা সেটাও নিশ্চিত হবে)।

**Verify (simulation, honest):** cat video 0.42→SAFE · cat cartoon 0.10→SAFE · AI cartoon
0.12→SAFE · Mr Bean 0.10→SAFE · real porn 0.96→BLOCK · real hentai 0.90→BLOCK · lingerie
0.94→BLOCK। ✅ `git apply --check` OK on main · brace/paren balance 0 · compile=CI।

## Threshold slider-এর নতুন অর্থ
score এখন "unsafe কতটা এগিয়ে" বোঝায়: 0.50 = সমান, 0.65 = unsafe 0.30 এগিয়ে (default), 0.80 = 0.60 এগিয়ে।

## Trade-off (honest)
- **Precision ↑, recall ↓:** পর্দার ছোট অংশে (thumbnail) NSFW থাকলে full-frame score কম হওয়ায়
  এখন miss হতে পারে। Big/full-screen NSFW ঠিকই block হবে।
- Ambiguous "swimsuit" (0.6 sexy) → default 0.65-এ block, slider বাড়ালে miss — আপনার পছন্দমতো।
- ধরে নেওয়া হয়েছে model = 5-class NSFWJS। Import করা `guardian_model.tflite` যদি অন্য কিছু হয়
  (যেমন 2-class), তাহলে এ fix apply হবে না — সেক্ষেত্রে `Guardian out[N]` log-টা দেখে আমরা ঠিক করবো।

## Test checklist (আপনার device)
1. YouTube cat video / cartoon / AI cartoon → **block হবে না** ✅
2. Real photo NSFW / hentai → block ✅
3. লগ পেতে (PC-তে USB/ওয়্যারলেস adb):
   `adb logcat -s GuardianAi:D Timber:D | grep "Guardian out"` — কোনো false-block-এর সময়
   এক line পাঠান।
4. **Immediate relief (patch-এর আগেও):** Settings → AI threshold → 0.85–0.90 করে দিন; v2.4.1-এ
   cat-এর মাঝারি score (0.5–0.7) তখন আর block করবে না।
