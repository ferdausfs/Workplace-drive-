# FTT FX EA — Setup Guide (MetaTrader 4, DEMO-FIRST)

> **File:** `FTT_FX_EA.mq4` · **Platform:** MT4 · **Account:** Exness DEMO (or any MT4 demo)
> **Rule:** No real money. Ever. Until the engine clears breakeven (55.6%) with CI on 7-14 forward days.

---

## ধাপ ১ — Exness DEMO account

1. Exness → open account → **Demo account** (free, instant)
2. Type: **MT4** (not MT5 for this EA; ask if you want MT5)
3. Note the **Login**, **Password**, and **Server** (e.g. `Exness-MT4Trial8`)
   → these go into MT4 at login, **not** into the EA.

> If you already trade real on Exness: do NOT use that login. Open a fresh demo.

## ধাপ ২ — MT4 install + login

- Download MT4 from Exness (or your broker) → install on **Windows PC or VPS** (phone MT4 can't run EAs reliably)
- Launch → File → Login → enter **demo Login/Password/Server**

## ধাপ ৩ — EA install

1. Copy `FTT_FX_EA.mq4` into:
   ```
   <MT4 Data Folder>/MQL4/Experts/
   ```
   (File → Open Data Folder → MQL4 → Experts)
2. In MT4: **Navigator (Ctrl+N)** → Expert Advisors → right-click → Refresh
   → you should see `FTT_FX_EA`

## ধাপ ৪ — WebRequest allow (অতি জরুরি)

MT4 → **Tools → Options → Expert Advisors**:
- ✅ tick **"Allow WebRequest for listed URL"**
- **Add:** `https://fttotcv6.umuhammadiswa.workers.dev`
- (worker URL — শুধু এটাই দরকার, broker URL নয়)

## ধাপ ৫ — EA attach + inputs

1. Open any chart (e.g. EUR/USD)
2. Drag `FTT_FX_EA` onto chart → check inputs:
   - `Symbol_List` = `EUR/USD,GBP/USD,USD/JPY,AUD/USD` (broker-এ যা support করে; comma-দেওয়া)
   - `Lot_Size` = `0.01` (demo)
   - `Poll_Seconds` = `60`
   - `Enable_Trading` = `true`
3. **Enable AutoTrading** (top toolbar ⚡ button — must be green)

## ধাপ ৬ — Test

- **Experts tab** (bottom) → live log দেখবেন:
  - `FTT_EA: EUR/USD → {"pair":"EUR/USD",...,"finalSignal":"SELL",...}`
  - `FTT_EA: opened SELL EUR/USD @ ... SL ... TP ...`
- Order এলে **Trade tab**-এ দেখবেন — SL/TP বসানো আছে
- **Terminal → Journal** — error হলে সেখান থেকে

---

## ⚠️ যদি কিছু কাজ না করে

| সমস্যা | কারণ/সমাধান |
|---|---|
| `WebRequest failed (4013)` | WebRequest allow হয়নি (ধাপ ৪) — URL হুবহু দিন |
| `WebRequest failed (4014)` | URL টা allow-list-এ নেই |
| `FTT_EA: no finalSignal` | worker response-এ finalSignal নেই (NO_TRADE হলে আসে না) — স্বাভাবিক |
| `symbol not found` | Symbol_List-এ broker-এর exact name দিন (EURUSD vs EUR/USD দুটোই চলে) |
| Order খোলে না (err 133/134) | market closed/insufficient funds — demo-তে balance check |
| Order খুলেই close হয় | SL খুব কাছের? — ATR-based, স্বাভাবিক |

## 🧪 "Dry run" option

চাইলে EA-টা **trade না করে শুধু signal print** করতে পারে:
- `Enable_Trading = false` → শুধু log-এ signal দেখাবে, order খুলবে না
- এটা দিয়ে ১-২ দিন দেখুন EA ঠিকঠাক পড়ছে কিনা → তারপর `true` করুন (demo)

---

## ⚠️ সততা (আবার)

- EA-টা **demo-র জন্য** — engine এখন ~46% WR, breakeven 55.6%-এর নিচে
- **Demo-তেও প্রতিদিন ফলাফল ট্র্যাক করুন** (যেটা বলেছি — EA-র ট্রেডগুলোর result)
- **৭-১৪ দিনের forward data + probe + D4**-র পরেই সিদ্ধান্ত — EA-টা তখনই "live-ready" বলা যাবে

## চাইলে MT5 version

এইটা MT4। **MT5 লাগলে বলুন** — মিনিটে রূপান্তর করে দেবো (API একই, syntax সামান্য ভিন্ন)।
