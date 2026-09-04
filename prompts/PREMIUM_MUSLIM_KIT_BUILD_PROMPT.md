# 🕌 Premium Muslim Kit — Build Request for Design Agent

> **তারিখ:** ২০২৬-০৮-০৩
> **Repo:** `github.com/ferdausfs/My-zakat` (local: `~/My-zakat`)
> **Live:** `https://zakat-app-12c34.web.app` (Firebase Hosting)
> **আপনার কাজ:** এই অ্যাপটাকে **premium + minimal** করে বানানো।
> **অন্য একজন independent reviewer (verify agent) আপনার কাজ review করবে।** নিচের Build Rules ও Verify Checklist মেনে চললে pass হবে।

---

## ১. Mission (এক লাইনে)

**আমার যাকাত (Muslim toolkit)** — যাকাত ক্যালকুলেটর, সালাত ট্র্যাকার, তাসবীহ, দোয়া, কিবলা, হিজরি ক্যালেন্ডার, সেটিংস — কে একটি **premium, minimal, dark-first** Islamic app বানাও, **একটাও function না হারিয়ে**।

## ২. Hard Rules (ভাঙা যাবে না)

1. ❌ **কোনো function সরানো যাবে না।** নিচের Function Inventory (ধারা ৫)-র প্রতিটা ফিচার আগে ছিল — সব থাকতে হবে, reachable হতে হবে।
2. ❌ **ডেটা/লজিক ভাঙা যাবে না।** যাকাত calculation, hijri calculation, salat time calculation, PIN, Google Drive sync, localStorage — এইগুলো অক্ষত রাখতে হবে।
3. ✅ **premium = minimal।** কম এলিমেন্ট, নিখুঁত spacing, একটা accent রঙ, ভালো টাইপোগ্রাফি।
4. ✅ **dark theme default** + light theme toggle।
5. ✅ Self-hosted font/icon (offline-capable single-file build — `vite-plugin-singlefile`)।
6. ✅ Build gate: `tsc --noEmit` 0 errors → `npm run build` pass।
7. ⚠️ Google sign-in-এর client ID `src/config.ts`-এ আছে — **সেটা স্পর্শ করবেন না** (letter `o`: `...69g2ggr225o8s97...`)। Firebase hosting config (`firebase.json`)ও রাখুন।

## ৩. Design Language (সংক্ষেপ)

| বিষয় | স্পেসিফিকেশন |
|---|---|
| Background | dark navy `#0B0E14` + subtle radial teal/gold glow |
| Primary accent | teal `#4DD0E1` (এক স্ক্রিনে একটা জিনিসে) |
| Secondary accent | gold `#E3B23C` — শুধু যাকাত/স্পিরিচুয়াল নাম্বারে |
| Cards | glassmorphism (`rgba(255,255,255,0.03)` + blur 16–24px), hairline border |
| Radius | 10 / 14 / 20 / 28px scale |
| Spacing | **4pt grid** — শুধু 4-এর গুণিতক (4,8,12,16,20,24,32,48) |
| Type | Hind Siliguri (bn) + Noto Naskh Arabic; tabular numerals সব নাম্বারে |
| Type scale | overline 10px → caption 11 → body-sm 13 → body 15 → h3 16 → h2 20 → h1 28 → display 40–56 |
| List rows | padding 12–14px, gap 8px, hairline border, icon 34px tinted box |
| Buttons | primary = teal gradient, height 48px, radius 16px, press scale 0.97 |
| Nav | bottom 5 tabs, glass, active = teal pill |
| Motion | screen fade-slide 250ms, press scale, count-up 600ms, `prefers-reduced-motion` respected |
| Accessibility | touch target ≥44px, aria-label, contrast ≥4.5:1 |

## ৪. Screens (৮টা — সব বানাতে হবে)

1. **হোম** — next-prayer hero (নাম + বড় সময় + countdown + বাংলা/হিজরি তারিখ), ৬-টাইল quick grid (সালাত/যাকাত/তাসবীহ/দোয়া/কিবলা/হিজরি), যাকাত mini card
2. **সালাত** — ৫–৬ prayer row (নাম/সময়/করা-হয়েছে), next highlight, weekly log dots, location + calculation method picker
3. **যাকাত** — asset CRUD (নগদ/ব্যাংক/ক্রিপ্টো/সোনা/রূপা/ভাড়া...), liability, gold/silver price, nisab standard, hawl progress, 2.5% due + breakdown
4. **তাসবীহ** — বড় tap counter + ring progress + presets (সুবহানাল্লাহ/আলহামদুলিল্লাহ/আল্লাহু আকবার) + daily target + vibration
5. **দোয়া** — Arabic (right, Noto Naskh) + transliteration + বাংলা অর্থ, category filter, search
6. **কিবলা** — compass (device orientation), bearing°, distance km, N/S/E/W, sensor toggle
7. **হিজরি** — month calendar grid, today highlight, event days (gold), month nav, event cards (আশুরা, শবে বরাত, রমজান, ঈদ...)
8. **সেটিংস** — PIN lock, Google Drive sync status, backup export/import, location, method, theme toggle, app info

## ৫. Function Inventory (verify agent এগুলো চেক করবে — কিছু হারালে fail)

- [ ] যাকাত: asset add/edit/delete, liability, price, nisab gold/silver, hawl lunar-year timing, zakat due 2.5%, BDT format
- [ ] সালাত: ৫ ওয়াক্ত সময় (Karachi method + others), next/current prayer, countdown, performed/jamaat log, weekly report, location picker (ঢাকা+বেশি), DST-aware timezone
- [ ] তাসবীহ: counter, presets, daily stats, vibration
- [ ] দোয়া: Arabic + transliteration + meaning, categories
- [ ] কিবলা: bearing calculation, compass sensor
- [ ] হিজরি: gregorian↔hijri, calendar, events
- [ ] সেটিংস: PIN (attempt lockout + wipe), Google sign-in/sync (token refresh), JSON backup import/export, clear data
- [ ] সব localStorage persistence + offline

## ৬. Verify Checklist (আমি যা করবো — pass/fail)

1. `git clone` → `npm install` → `npx tsc --noEmit` (0 errors)
2. `npm run build` → single-file `dist/index.html` তৈরি
3. **Function inventory (ধারা ৫) — প্রতিটা রানটাইমে reachable:** nav/home grid থেকে ক্লিক করলে page খোলে
4. যাকাত calculation correctness: দেওয়া sample-এ exact 2.5% আসে কিনা (যেমন সম্পদ ৳১,০০,০০০ → ৳২,৫০০, nisab-এর উপরে হলে)
5. হিজরি: আজকের বাংলা+হিজরি তারিখ সঠিক
6. PIN: ভুল পিন ৫ বার → 30s lockout
7. Google client ID অপরিবর্তিত (`...225o8s97...`)
8. Theme: dark default, light toggle কাজ করে
9. Spacing/type scale: 4pt grid মেনে, tabular numerals
10. Build-এ কোনো console error নেই

## ৭. Deploy

```bash
npm run build
firebase deploy --only hosting   # → https://zakat-app-12c34.web.app
```

(আপনার push নিয়ম অনুযায়ী — reviewer verify করার আগে live না-ও করতে পারেন।)

## ৮. Delivery

- সব পরিবর্তন commit (আপনার git identity), অথবা tar/bundle তৈরি
- একটা `CHANGES.md` — কী বদলালো, কোন ফাইল, কোন function যোগ/সংশোধন (কোনোটা delete হলে সেটা fail)

---

**আদর্শ:** "Premium দেখায়, minimal লাগে, একটাও function হারায় না।" শেষ হলে reviewer verify করবে। 🕌
