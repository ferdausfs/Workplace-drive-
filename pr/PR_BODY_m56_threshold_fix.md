# fix(guardian): M5.6 — NSFW detection not blocking (threshold too strict)

**Repo:** `ferdausfs/DOK-ai` · **Base:** `main` (`e1f6c7d`) · **Branch:** `fix/guardian-threshold`

## Problem (sandbox-verified)
NSFW content block করছিল না। Model-টা **ঠিক কাজ করছে** (safe ছবিতে Neutral 0.97, Porn/Sexy ~0 —
কোনো false positive নেই)। সমস্যা **code-এর threshold-এ** — Phase-1-এর false-block-overcorrection-এর
রেশ, ৩টা জায়গায় overly strict:

| # | ছিল | Fix | কারণ |
|---|---|---|---|
| 1 | `threshold = aiThreshold.coerceAtLeast(0.80f)` | `coerceIn(0.50f, 0.95f)` | slider 0.72 দিলেও আসলে 0.80 হতো — পুরনো "Safe First" floor |
| 2 | `voteNeeded = gridVoteCount + 1` (=৩) | `gridVoteCount.coerceIn(1,4)` (=২ default) | screenshot-এ ৩টা cell ≥0.80 লাগত — partial NSFW কখনো pass করত না |
| 3 | full-screen NSFW gate 0.80 | 0.70 | gender path-ও overly strict |
| (4) | variance gate 200..8500 | 150..9000 | dark video frame-এ ছবি skip হয়ে যেত |

## Sandbox test (আমি যা verify করেছি)
- NSFWJS MobileNetV2 (bundled model) ২টা safe ছবিতে চালিয়েছি:
  - object (mug): Drawing 0.00 / Hentai 0.00 / **Neutral 0.972** / Porn 0.025 / Sexy 0.003
  - clothed person: Neutral 0.977 / Porn 0.003 / Sexy 0.015
- → নতুন 0.72 threshold-এও **কোনো false positive নেই** (সব স্কোর ≪ 0.72) ✅
- Model weights meaningful (Neutral dominant on safe, Hentai/Porn/Sexy ~0) ✅

## Honest limitation
আমি NSFW/pornographic ছবি fetch/generate করিনি — সেটা আমার পক্ষে ঠিক হবে না। NSFW-positive path-এর
**চূড়ান্ত test আপনার phone-এই** (আপনার কাছে যে content block করতে চান সেটা আছে)। Model contract
+ safe-নেগেটিভ test + code-logic — তিনটাই verify করা; threshold-এর mathematical cause-টাই ছিল মূল বাগ।

## Deploy / test
Merge → CI build → install → Guardian AI: **enable + gender=None** → আসল NSFW content দেখান →
block screen + log আসা উচিত। False-block হলে settings-এ **AI threshold slider** বাড়ান (0.72→0.80);
NSFW miss হলে কমান (0.72→0.60)। Grid votes-ও tunable (১–৪)।
