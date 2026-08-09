# 🤖 Bot Menu Redesign — Arena-Style (Quick Actions + Premium + Settings)

> **Bot-এর message-গুলো এখন premium (v4.3)। এখন menu/button-গুলো Arena-র মতো**
> — quick actions, grouped sections, premium section, settings।
> **PR-first:** branch → PR → reviewer verify → merge। (সরাসরি main-এ push নয়)
>
> **Repo:** `ftt-telegram-bot` · **HEAD:** `38dda66` (v4.3 merged)

---

## ১. লক্ষ্য (Arena-র মতো)

Arena-র UI-তে যেমন "Quick actions" + "Premium" + "Chat history" + "Settings" আলাদা —
Telegram bot-এ ওই ফিল আনতে:

```
[Main Menu]
━━━ Quick Actions ━━━
📊 Signal Now      🔄 Start/Stop Auto
🔍 Scan All        📈 History
━━━ Explore ━━━
📅 Today      📊 Weekly      🔥 Best Pairs
📉 Risk       🕐 Heatmap    📒 Journal
━━━ Account ━━━
👁 Watchlist   ⚙️ Settings   📋 Status
━━━ Premium ━━━
⭐ Premium (যদি থাকে) / 📣 Channel
```

**মূল ধারণা:** buttons-কে **group** করো (SEP-এর মতো visual divider নেই — Telegram-এ
আলাদা row-র spacing + consistent emoji দিয়ে group বোঝাও), সবচেয়ে দরকারি (Signal,
Auto, Scan) **উপরে**, secondary নিচে।

## ২. Main Menu — quick access (Arena-র "Quick actions" equivalent)

**Top row (সবচেয়ে দরকারি — ২টা button):**
```
📊 Signal Now     🔄 Start Auto / 🔕 Stop Auto
```

**২য় row:**
```
🔍 Scan All       📈 History
```

**তারপর group:** Explore (Today/Weekly/Best/Risk/Heatmap/Journal), Account
(Watchlist/Status), Settings।

**নিয়ম:**
- **প্রতিটা group-এ consistent emoji** (🔍 scan, 📈 history...)
- **Top-এ সবচেয়ে গুরুত্বপূর্ণ** — user ১ ট্যাপে signal/auto
- **Bot-এর `mainKb`-এ** — ২টা row primary, বাকি grouped

## ৩. Settings Menu — premium

Arena-র "Settings"-এর মতো:

```
⚙️ Settings
━━━ Signal ━━━
💹 Mode: FTT/FX/BOTH     🎯 Grade Filter
📊 Min Confidence        ⏱ Interval
━━━ Auto ━━━
🤖 AI Only               📰 News Block
🔔 Alerts                🔁 Replay
━━━ Data ━━━
📡 Channel               ⬇ Export
```

**Mode cycle button-টা prominent** (FTT/FX/BOTH — user-এর দরকারি)।

## ৪. Premium section (Arena-র "Premium"-এর মতো)

যদি premium concept থাকে (আগে না), **একটা placeholder Premium menu** বানাও:
- ⭐ **Premium** button (main menu-র নিচে)
- এতে: future features list (signal priority, more pairs...)
- **Honesty:** এটা এখন informational — কোনো payment না

## ৫. Back/Navigation consistent

- প্রতিটা submenu-এ **🔙 Back** — আগের menu-তে
- **◀ Prev/Next ▶** — pagination (pair/watchlist) আগের মতো

## ৬. Verify

```bash
node --check src/index.js
# mainKb/settingsKb render test (আপনার sample-এ)
```

## ৭. PR (push নয়)

```bash
git checkout -b arena-menu-redesign
git add -A && git commit -m "Bot: Arena-style menu redesign (quick actions + groups + premium)"
git push origin arena-menu-redesign
# PR খোলো → main
```

**PR body:** কী বদলালো, main menu structure, settings, premium — detail সহ।

## ৮. Reviewer verify করবে

- mainKb grouped + top-quick-access
- settings grouped + mode prominent
- premium placeholder
- no regression (সব cmd/button intact — signal, auto, scan, history, stats...)
- node --check

**Pass = merge।** 🎯
