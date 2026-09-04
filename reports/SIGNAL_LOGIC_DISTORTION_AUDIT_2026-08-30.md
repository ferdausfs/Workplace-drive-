# SIGNAL LOGIC & PARAMETER DISTORTION AUDIT — 2026-08-30

**User hypothesis:** "signal logic r parameters er distortion er somossa ache" — **প্রমাণিত সঠিক।**
**Method:** Worker source audit (engine.js, voteFilters.js, timeframe.js, regime.js, config.js, grade.js) + ৫,৬১১ decided signal-এ parameter-level forward test।

---

## ১. মূল রোগ: Decision variable-ই ভুল জিনিস মাপছে

Engine-এর confidence = **consensus metric** (`weightedBuy/(total)×100` + alignment bonus) — অর্থাৎ "কতগুলো indicator একমত"। কিন্তু forward data বলছে এই metric-এর **কোনো predictive variance-ই নেই**:

### প্রমাণ ১ — Alignment system অন্ধ (crypto pool n=4,626)
```
ALL_BULLISH   43.4% (n=2017)  ┐
ALL_BEARISH   46.5% (n=2405)  ├─ ৯৯.৯৮% signal এই ২টা bucket-এ!
MOSTLY_BULL   43.4% (n=113)   │
MOSTLY_BEAR   43.3% (n=90)    ┘
```
- **৯৯.৯৮% signal "full consensus"** — MIXED_ALIGNMENT block বাকি সব মেরে দেয়, তাই survivors-এর মধ্যে alignment-এর কোনো discriminating power নেই।
- Full consensus (43.4-46.5%) vs partial (43.3-43.4%) — **প্রায় শূন্য পার্থক্য।** অর্থাৎ যে জিনিসের ওপর confidence/grade/bonus দাঁড়িয়ে আছে, সেটা কিছুই মাপছে না।

### প্রমাণ ২ — Pseudo-confluence: ১২ category আসলে ৪টা
`timeframe.js`-এ ১২টা "স্বাধীন category" আছে বলা হয়, কিন্তু গণিত অনুযায়ী:
- **Oscillator family (৫টা category!):** RSI + Stochastic + Williams %R + CCI + MFI — সবগুলোই একই close-price series-এর প্রায় একই transformation। Price band-low-এ গেলে এই ৫টা **একসাথেই** fire করে → ৫টা আলাদা ভোট নয়, **১টা observation ৫ বার গোনা**।
- RANGING weights: momentum 1.8 + stochastic 1.8 + divergence 1.8 + sr 2.2 + bands 1.4 = **oscillator/level-family ~9x trend-এর চেয়ে ভারী** (trend মাত্র 0.8)।
- ফলাফল: confluence মাপে "move কত দূর এগিয়েছে" — win probability না। যত বেশি agreement, তত late/extended entry, তত বেশি mean-reversion ঝুঁকি। **এজন্যই A+ সবচেয়ে খারাপ, C সেরা।**

### প্রমাণ ৩ — Calibrated confidence ladder আজও non-monotone (crypto)
```
conf 72-75: 46.3% | 76-79: 48.0% | 80-83: 40.6% ← সবচেয়ে খারাপ | 84-87: 43.8% | 88+: 45.9%
```
calib-v1 ঠিক করতে পারেনি — কারণ **input-ই distorted** (উপরের দুই প্রমাণ)। Garbage in → calibrated garbage out।

---

## ২. Double/triple-counting — একই তথ্য ৩-৪ জায়গায় কাউন্ট হচ্ছে

| তথ্য | কোথায় কোথায় apply হয় |
|---|---|
| **HTF (15min) trend** | (১) per-TF `htfPenalty ×0.7` (timeframe.js:413-421) · (২) `HTF_HARD_BLOCK/-18` (voteFilters.js:129-138) · (৩) agree-তে `+5` · (৪) alignment bonus-এর ভেতরেই পরোক্ষভাবে |
| **Structure** | (১) multiplier 1.35/0.65 (timeframe.js:430-448) · (২) category vote +1 (476-479) · (৩) HARD BLOCK (495-508) · (৪) calibration-এর structWR → grade |
| **Consensus** | vote-share confidence + alignment bonus + MIN_CONFLUENCE gate + AI boost — সব একই জিনিস পুনরাবৃত্তি |

একই information ৩-৪ বার গুণ হওয়ায় ছোট noise বড় confidence swing হয়ে ফুটে ওঠে — এটাই "distortion"।

---

## ৩. সবচেয়ে বড় irony: যে parameter কাজ করে, তার গলাটা চেপে ধরা আছে

### ✅ যেটা কাজ করে — HOUR_MULTIPLIERS (edgeFeatures, config.js:46-51)
```
config-'good' hours (mult ≥1.05):  49.3% WR (n=1520)
neutral hours:                     45.1% WR (n=2147)
config-'bad' hours (mult ≤0.90):   38.0% WR (n=959)
```
**১১.৩pp spread** — পুরো engine-এর সবচেয়ে শক্তিশালী validated parameter (TRAIN 08-01..06-এ fit, এখনো forward-এ টিকে আছে)। কিন্তু এটা confidence-এ মাত্র ±5-10% multiplier হিসেবে ঢোকে — 72% confidence floor-এর সামনে এর ভয়েস প্রায় শূন্য।

### ✅ RSI mid-zone BUY slice (নতুন আবিষ্কার, forward-validate করতে হবে)
```
BUY RSI 45-55:  60.4% (n=101, CI 50.6-69.4)  ← breakeven-এর কাছাকাছি একমাত্র slice!
BUY RSI >55:    43.3% (gate-এর ×0.85 penalty ঠিক আছে)
SELL RSI<45:    45.7% vs SELL 45-55: 44.6%   ← SELL-side-এ gate কিছুই discriminate করে না (asymmetric bug)
```

### ✅ Mean-reversion extremes এখনো ভালো (engine-এর design অনুযায়ী)
```
BUY RSI<=35:  48.8% | SELL RSI>=65: 47.5% | mid-RSI: 44.8%
```

### ✅ Structure inversion crypto-তেও স্থায়ী
```
AGAINST: 48.0% (n=927) > ALIGNED: 44.6% (n=1929) > NEUTRAL: 40.2%
```

### ❌ যেগুলো কিছুই করে না (কিন্তু সবচেয়ে বেশি weight/সিদ্ধান্ত নেয়)
- Alignment bonus/confluence (প্রমাণ ১) · confidence ladder (প্রমাণ ৩) · AI-agreement (আগেই প্রমাণিত 43.8%≈43.4%) · grade system

---

## ৪. Structural distortion-এর সারসংক্ষেপ (৬টা point)

| # | Distortion | ফাইল:লাইন | প্রভাব |
|---|---|---|---|
| D1 | Correlated oscillators = fake independent votes | timeframe.js:134-256 | confluence/confidence inflated, anti-predictive |
| D2 | Alignment system zero variance (৯৯.৯৮% ALL_*) | voteFilters.js:87-126 | সিদ্ধান্তহীন, bonus noise |
| D3 | HTF+structure ৩-৪x recount | engine+voteFilters+timeframe | noise বিস্ফোরণ |
| D4 | Validated parameter (hour) কেবল ±10% multiplier | config.js:46-51, edgeFeatures.js | ১১pp edge অব্যবহৃত |
| D5 | Calibration static table + self-calib cell freeze (MIN_CELL_OBS=30, volume ধ্স বলে cell আর update হয় না) | config.js:124-135 | ladder পুরনো হয়ে যায় |
| D6 | Filter-stack survivor pool = max-consensus trades | সব D2/HTF/structure block | mean-reversion-এর সবচেয়ে খারাপ entry select করে |

---

## ৫. FIX PLAN (priority অনুযায়ী)

### FIX-1 (সবচেয়ে জরুরি): Confidence-কে validated-feature-based বানানো
নতুন decision score = weighted sum of **শুধু forward-validated features**:
- `hourMult` (সবচেয়ে শক্তিশালী — বড় weight)
- RSI-zone × direction (mid-zone BUY boost, extremes boost, chase penalty)
- ATR/vol state (calm bonus)
- structure AGAINST-কে ALIGNED-এর চেয়ে বেশি score (inversion মেনে নেওয়া)
Consensus vote-share → secondary-তে নামানো বা বাদ। এতে confidence-এর মানেই হবে "empirical win-probability"।

### FIX-2: Asymmetric RSI gate ঠিক করা
SELL-side penalty সরানো (প্রমাণ: discriminate করে না), BUY mid-zone-এ boost যোগ।

### FIX-3: Self-calib চাঙ্গা করা
MIN_CELL_OBS 30→15 (volume-collapse era-র জন্য), WINDOW_DAYS 14→10, প্রতি সোমবার refresh verify।

### FIX-4: Double-count বাদ
HTF/structure একবারই apply হবে (multiplier অথবা block — দুটো নয়)।

### FIX-5 (আগের audit থেকে): Entry-at-fill + gate loosen
আগের EDGE_DECAY_AUDIT report-এর Lever 1 + 3 অপরিবর্তিত।

---

## ৬. Honest caveats
- RSI 45-55 BUY slice (60.4%): n=101, multiple-comparison ঝুঁকি আছে — deploy-এর আগে forward shadow-তে validate করতে হবে।
- Hour mult-এর spread-এর কিছু অংশ selection effect-ও হতে পারে (floor-এর সাথে interaction) — কিন্তু direction স্থায়ী।
- এই audit কোনো গ্যারান্টি দেয় না — প্রতিটা change shadow → forward → gate (RULE 6) দিয়ে যাবে।

*Data: live pull 2026-08-30 · 5,611 decided (crypto n=4,626) · code refs @ main `7ed962a`+ · Wilson CI · no invented numbers*
