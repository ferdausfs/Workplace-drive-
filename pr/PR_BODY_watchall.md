# feat: Watch-ALL mode — bot gets access to every worker pair (bot v4.5.1 + worker)

**Repos:** `ferdausfs/ftt-telegram-bot` (v4.5.1) + `ferdausfs/Ftt-Otc-v6` (base `2249666`)

## Problem (user-reported, data-verified)
Bot পাচ্ছিল ২-৫ signal/day, worker-এর প্রতি-day emitted অনেক বেশি। Root cause:
1. Bot-এর pair list-এ **DOT/USD + LINK/USD missing** — অথচ এগুলো worker-এর best pair (50%+ WR)।
2. Watchlist cap = **৬ pair** (`MAX_WL=6`) — সব worker pair (১৪টা) watch করা অসম্ভব।
3. Worker-এর subscriber gate শুধু `pair + watchlist` ম্যাচ করে — "সব pair" করার কোনো mode ছিল না।

## What changed

### Bot (`ftt-telegram-bot`, v4.5.0 → v4.5.1)
- `PAIR_PAGES`-এ নতুন page: **DOT/USD + LINK/USD** (worker-এর best pair, আগে bot-এ অনুপস্থিত)।
- `DEF_USER`-এ `watchAll: false` field।
- Watchlist UI-তে **"⚡ Watch ALL: ON/OFF"** toggle + `/watchall` command।
- Status-এ `Watchlist: ALL ⚡` দেখায় যখন ON।

### Worker (`Ftt-Otc-v6`)
- `getMatchingSubscribers`-এ `user.watchAll === true` হলে pair/watchlist gate **bypass** —
  কিন্তু বাকি gate (autoEnabled, minConfidence, gradeFilter, aiOnly) অটুট।

## Verification
- Bot: `node --check` PASS · menu-test **74/0** · round2-bugfix **60/0** · single-source **72/0**
- Worker: `fix_tests` **326/0** (new T46: 5 assertions — watchAll matches unwatched pair,
  chatId correct, autoEnabled/gradeFilter bypass হয় না) · phase10/phase7/d2/probe/eh/fx সব green
- `git apply --check` clean (bot `2555d20`, worker `2249666`)

## Deploy note (separate step)
- Worker bundle rebuild + redeploy (push matching change)। Bot bundle rebuild + redeploy (`bot_deploy2.sh`)।
- User toggle: bot-এ `/watchall` (বা Watchlist menu-তে ⚡ Watch ALL)।

## Honest note
"Watch ALL" মানে **সব emitted signal** পাবেন — কিন্তু v6.10.3-এর পর emit-ই কম (RANGING+ALIGNED + TRENDING
block)। এটি signal-count-এর "200+" ফেরায় না; এটি নিশ্চিত করে **যে signal emit হয়, সবই bot-এ আসে**।
Profit-এর জন্য accuracy কাজ (breakeven 55.6%)-ই আসল পথ — এটি শুধু distribution fix।
