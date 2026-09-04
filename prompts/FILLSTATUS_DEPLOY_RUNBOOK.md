# Fill Status (INSTANT/PENDING) — Deploy Runbook (2026-08-05)

> সব জায়গায় এখন signal-এর **fill status** দেখা যাবে: entry-টাই сейчас নেওয়া যায় (⚡ INSTANT) নাকি price দূরে (⏳ PENDING — অপেক্ষা)। সত্যি UX — "entry হয়নি কিন্তু LOSS" আর ধোঁকা দেবে না।

## 🔄 Deploy order — ৩টা bundle (একসাথে)

### 1) Worker (সবার আগে — app/bot এটা পড়ে)
```bash
cd ~/Ftt-Otc-v6
git fetch /sdcard/Download/ftt-fillstatus-v1-2026-08-05.bundle HEAD
git merge FETCH_HEAD
git push origin main
```
→ auto-deploy (২-৩ মিনিট)। এতে entry-hit shadow + fillStatus + FX সব latest।

### 2) Bot
```bash
cd ~/ftt-telegram-bot
git fetch /sdcard/Download/ftt-bot-fillstatus-v1-2026-08-05.bundle HEAD
git merge FETCH_HEAD
git push origin main
```

### 3) App (Vercel)
```bash
cd ~/Ftt-app-002
git fetch /sdcard/Download/ftt-app-fillstatus-v1-2026-08-05.bundle HEAD
git merge FETCH_HEAD
git push origin main
```

## ✅ Deploy-এর পরে কী দেখবেন

**Bot signal message-এ:**
```
📊 BTC/USD | 5min | 💹 FX
🟢 BUY  87%
⚡ INSTANT — price at entry, take now
```
বা
```
⏳ PENDING — price away from entry (0.312%), wait for fill
```

**App signal card-এ:** একই badge (green ⚡ / amber ⏳ + %)

## 📌 নিয়ম (ভাঙা হয়নি)

- Engine-এর দিক/result **অপরিবর্তিত** — fillStatus additive output
- Entry-hit shadow আগের মতোই **শুধু সত্যি মাপে** (production WR-তে বদল নেই, ৭-১৪ দিন পরে সিদ্ধান্ত)
- PENDING বললে **অপেক্ষা করুন** — force entry নেবেন না (আপনার আজকের অভিজ্ঞতা)

## 🎯 verify (deploy-এর পরে)

```bash
# worker-এ fillStatus আছে:
curl -s "https://fttotcv6.umuhammadiswa.workers.dev/api/signal?pair=BTC/USD&mode=fx" | grep -o "fillStatus" | head -1
# → fillStatus (signal থাকলে)
```
