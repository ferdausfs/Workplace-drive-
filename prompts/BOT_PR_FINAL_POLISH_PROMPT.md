# 🤖 Bot PR #2 — Final Polish Prompt (merge-এর আগে বাকি জিনিস)

> **আপনার PR #2 (premium UX + bug fixes) ভালো হয়েছে — reviewer-এ pass।**
> কিন্তু merge-এর আগে **কয়েকটা জিনিস বাকি** — সেগুলো ঠিক করে PR-এ আরও commit করুন,
> তারপর merge-এর জন্য ready।
>
> **PR branch:** `arena/019fd2e9-ftt-telegram-bot` → main

---

## ১. ফলাফল / History message-টা premium করুন

বর্তমানে **result/history message-গুলো এখনো পুরনো style** (শুধু `✅ WIN ❌ LOSS`)।
Premium signal message-এর মতো করে দিন:

```
✅ WIN — BTC/USD
━━━━━━━━━━━━━━━━━
💰 Entry: 63813.96 → Exit: 64000.00
🎯 Result: WIN (+0.29%)
━━━━━━━━━━━━━━━━━
⚡ Entry hit ✓ (price reached entry)
```

- **WIN/LOSS** — রঙ/emoji consistent
- **Entry → Exit + পিপ/পার্সেন্ট** — ফলাফল স্পষ্ট
- **Entry hit/miss** (worker-এর `entryHit` থাকলে) — `entry hit ✓` / `entry miss ⚠`
- **Pending** — countdown-সহ
- SEP separator-সহ leveled

**কোথায়:** result push handler, history row, daily summary — সব premium।

## ২. Result push-এ entryHit দেখান

Worker-এর result-এ `entryHit` থাকে — bot-এর result message-এ যোগ করুন:
- `entry hit ✓` (সবুজ) — price entry-তে পৌঁছেছিল
- `entry miss ⚠` (হলুদ) — পৌঁছায়নি (এটা জানা দরকার — "ভুয়া WIN/LOSS")

## ৩. কিছু subtle bug-check

- **fmtSignal-এ AI section** — status OK/Disagree/Uncertain — premium leveled
- **Filter badges** (D2 block) — পরিষ্কার
- **News warning** — clean
- **History command** (`/history`, `/risk`) — premium table

## ৪. Verify + commit

```bash
node --check src/index.js
# নিজের sample data-এ result message render test
git add -A && git commit -m "Bot: premium result/history messages + entryHit"
git push origin arena/019fd2e9-ftt-telegram-bot   # একই PR-এ commit
```

## ৫. Reviewer (আমি) আবার verify করবো

- result/history premium format
- entryHit display
- no regression (signal message, autoScan, mode)
- node --check

**এগুলো ঠিক করলে PR #2 merge-ready।** 🎯
