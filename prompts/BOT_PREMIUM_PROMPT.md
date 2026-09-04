# 🤖 FTT Telegram Bot — Premium UX + Bug-fix Prompt (PR-first)

> **এই chat-এ আপনি FTT Telegram Bot-এর message/UX premium করবেন + সব bug ঠিক করবেন।**
> **PR আকারে কাজ দিন (সরাসরি main-এ push নয়)** — independent reviewer verify করার পর merge হবে।
>
> **Repo:** `github.com/ferdausfs/ftt-telegram-bot` · **Worker:** Cloudflare (wrangler)
> **Live:** `https://ftt-telegram-bot.umuhammadiswa.workers.dev` · **Token:** দেওয়া হবে (PR-এর জন্য)

---

## 0. কাজের ফ্লো (এইটা follow করুন)

```
১. Clone (টোকেন দিয়ে) → main-এর latest পড়ুন
২. Bot-এর বর্তমান message/feature বুঝুন
৩. Premium message redesign + bug fixes (নিচের স্পেক)
৪. নিজে verify: node --check + (যতটা পারা) logic test
৫. PR তৈরি করুন (branch → main) — PUSH main-এ না, PR করুন
৬. Reviewer verify করবে → merge হবে
```

> ⚠️ **সরাসরি main-এ push নয় — PR খুলুন।** এইটা আগের agent-দের fail-থেকে শেখা নিয়ম।

---

## ১. বর্তমান Bot-এর অবস্থা (বুঝে নিন)

`src/index.js` (~2000 লাইন) — key features:

| Feature | বর্তমান |
|---|---|
| Signal message (fmtSignal) | Mode badge (⏱/💹/🔄), SL/TP, fill status, AI, structure, filters |
| Worker push message (formatSignalMessage — worker-এ) | ⚠️ **bot-এ না, worker-এ** — bot-এ শুধু fmtSignal |
| Auto scan | cronLite → autoScan (৫ মিনিট) |
| FX Mode toggle | Settings → Mode (FTT/FX/BOTH) |
| History / risk / heatmap / best pairs | আছে |
| Result tracking, reminders, summary | আছে |

---

## 2. PREMIUM MESSAGE DESIGN (আপনার মূল কাজ)

### 2a. Signal message — premium format

আজকের মতো বিক্ষিপ্ত না — **পরিষ্কার, leveled, premium:**

```
📊 BTC/USD | 5min | 💹 FX
━━━━━━━━━━━━━━━━━
🟢 BUY 92%  [A+ EXCELLENT]
━━━━━━━━━━━━━━━━━
💰 Entry: 63813.96
🛑 SL: 63900.00
🎯 TP: 63500.00 (1:2.5)
⚡ INSTANT — take now
━━━━━━━━━━━━━━━━━
📈 HTF: BUY · 🟡 Regime: RANGING
✅ Structure: ALIGNED (BUY STRONG)
━━━━━━━━━━━━━━━━━
📝 EMA trend favors BUY · RSI bullish (61)...
━━━━━━━━━━━━━━━━━
⏳ Result tracked automatically
```

**নিয়ম:**
- **Separators** (`━━━`) দিয়ে sections আলাদা — পরিষ্কার hierarchy
- **Emoji consistent** — BUY সবুজ, SELL লাল, status আইকন stable
- **Grade + confidence একসাথে** — পড়তে সহজ
- **FX-এ SL/TP prominent** — এটাই user-এর দরকার
- **Fill status** (⚡ INSTANT / ⏳ PENDING) — সবসময়
- **Empty state / NO_TRADE** — সুন্দর (ঝকঝকে, না-মলিন)
- **Text-এ কোনো MarkdownV2 নেই** (পুরনো bug — plain text/HTML-safe)

### 2b. Menu / buttons — premium

- Main menu: পরিষ্কার labels, grouped
- Settings: Mode cycle, AI only, news block — সব readable
- **Consistent emoji** — এক জিনিসে এক emoji

### 2c. Result / history messages

- WIN/LOSS — পরিষ্কার colored
- Entry hit/miss (worker-এর `entryHit`) — দেখালে ভালো
- Pending — countdown-সহ

---

## 3. BUG-FIX CHECKLIST (যেগুলো খুঁজে ঠিক করবেন)

নিচের bug-গুলো **code-এ থাকলে ঠিক করুন** (থাকলে লিখুন কোনটা ছিল):

1. **MarkdownV2 escape problem** — `esc()`/parse_mode-এ বিশেষ চরিত্র (`(`, `)`, `.`, `_`) → 400 error। plain text/HTML-safe নিশ্চিত
2. **fetchSig timeout** — 20s race আছে; network fail-এ message stuck না
3. **AutoScan dedup** — same-candle skip ঠিক আছে? duplicate message আসে?
4. **Mode cycle** — FTT→FX→BOTH→FTT — ঠিক ঘোরে? localStorage/KV persist?
5. **fill status** — INSTANT/PENDING — worker না দিলে default দেখায়?
6. **News blackout** — ±15min skip ঠিক? blocked হলে message?
7. **Custom alerts** — threshold-এ কাজ করে?
8. **Result push** — worker-এর pushResultToSubscribers — bot-এ result message ঠিক?
9. **History** — `/history`, `/risk` — সঠিক data?
10. **Channel mirror** — channel-এ signal যায়?

**প্রতিটা bug:** কোথায় ছিল, কী fix — CHANGES-এ লিখুন।

---

## 4. VERIFY (নিজে, PR-এর আগে)

```bash
node --check src/index.js          # syntax OK
# logic test (যদি পারেন): fmtSignal-এ premium format render-টা node-এ run
```

**Real check (যদি সম্ভব):** আপনার format-টা sample data দিয়ে render করে দেখুন —
সব emoji/separator ঠিক, কোনো crash নেই।

---

## 5. PR তৈরি করুন (push নয়)

```bash
git checkout -b premium-ux
git add -A
git commit -m "Bot: premium message UX + bug fixes"
git push origin premium-ux          # branch push
# GitHub-এ PR: premium-ux → main
```

**PR body-তে লিখুন:**
- কী বদলালো (message format, bug fixes)
- কোন bug ছিল → ঠিক হলো
- verification proof (node --check output)

---

## 6. Reviewer (আমি) verify করবো — merge-এর আগে

1. **PR branch-এ code** — `node --check` pass
2. **Premium format** — fmtSignal-এ separator/emoji/level ঠিক
3. **Bug fixes** — দাবিকৃত bug-গুলো আসলেই ঠিক (code-এ check)
4. **No regression** — autoScan/mode/history সব আগের মতো
5. **PR body** — detail সহ

**এই ৫টা pass = merge। কোনোটা fail = fix করে আবার PR।**

---

**আদর্শ:** "Apple-grade Telegram messages — পরিষ্কার, premium, bug-free." 
**PR-first — reviewer approve-র পরই main-এ merge।** 🎨
