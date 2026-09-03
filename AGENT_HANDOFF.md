# 🤝 AGENT HANDOFF — LIVE STATE + RUNBOOK (rolling document)

> **এই ফাইল সবসময় হালনাগদ থাকবে।** যেকোনো নতুন agent প্রথমে START_HERE.md পড়ার পর **এই ফাইলটা পড়বে** — এখানেই "এখন কী চলছে, পরের কাজ কী, কীভাবে করবে" সব আছে। প্রতি সেশনের শেষে agent এটা আপডেট করে push করবে (§৫ নিয়ম ২)।
>
> **Snapshot: 2026-08-31 · Worker LIVE: v6.13.0**

---

## ০. এখন কী চলছে (৬০ সেকেন্ডে)

- **মিশন:** FTT ট্রেডিং সিগন্যাল সিস্টেমের single accuracy (win rate) বাড়ানো।
- **কোথায় আছি:** Distortion audit (D1-D6) প্রমাণিত হয়েছে → তার ৩টা ফিক্স (FIX-1/2/3) merge + deploy হয়েছে → **লাইভ v6.13.0** → এখন **২-৩ দিনের shadow window** চলছে (শুরু **2026-08-30T07:55Z**), যেখানে প্রতিটা crypto BUY/SELL-এ `empiricalConfidence` জমছে।
- **পরের কংক্রিট কাজ:** **2026-09-01/09-02-তে** EC ladder validate করো (`python3 scripts/ec_shadow_validate.py`) → monotone হলে **এক-লাইনে `mode:'decision'` flip (v6.14.0)** → PR → merge → deploy → verify। পুরো runbook §৩-এ।
- **সতর্কতা:** shadow উইন্ডোতে Telegram-এ যাওয়া সিগন্যাল **শেখার ডেটা, ট্রেড-কোয়ালিটি নয়** — ঐতিহাসিকভাবে-খারাপ স্লাইসও আসছে (ইচ্ছাকৃত, মাপার জন্য)। কোয়ালিটি কন্ট্রোল flip-এর পর ফিরবে (EC grade-ভিত্তিক)।
- ⚡ **টোকেন স্ট্যাটাস (2026-08-31): GitHub PAT + CF token দুটোই revoke করা হয়েছে** (সিদ্ধান্ত: আগেই revoke, flip-এর দিন fresh দেওয়া হবে)। ভ্যালিডেশন চালাতে টোকেন লাগে না (public API), কিন্তু **flip + deploy-এর দিন user-এর কাছে fresh টোকেন চাওয়া হবে** (§৪, §৫-নিয়ম ১)। Worker টোকেন ছাড়াই চলছে, ডেটা জমছে।

---

## ১. কোথায় কী আছে

| জিনিস | ঠিকানা |
|---|---|
| Worker code (canonical truth) | GitHub `ferdausfs/Ftt-Otc-v6` main — ⚠️ drive-র `worker/` মিরর পুরনো, GitHub-ই truth |
| Docs/রিপোর্ট/ডেটা আর্কাইভ | এই repo (`ferdausfs/Workplace-drive-`) — `reports/`, `data/`, `scripts/`, `runbook/` |
| Live worker | `https://fttotcv6.umuhammadiswa.workers.dev` |
| API | `/health` · `/api/signal?pair=X` · `/api/history?pair=X&limit=N` — **browser User-Agent লাগবে** (403 নইলে), 30 req/60s রেট-লিমিট (req-এর মাঝে ২.৫ সে দাও) |
| Latest পুরো অডিট | `reports/SIGNAL_LOGIC_DISTORTION_AUDIT_2026-08-30.md` (D1-D6) + `reports/EDGE_DECAY_AUDIT_2026-08-30.md` + `reports/SHADOW_WINDOW_STATUS_2026-08-31.md` |
| লোকাল স্ন্যাপশট (সেশন-নির্দিষ্ট) | `/home/z/my-project/shadow_status_2026-08-31/` (১৮ পেয়ার × 500 raw) |

---

## ২. কী কেন করা হলো (ফিক্স লিনিয়েজ)

| ফাইন্ডিং | ফিক্স | PR | অবস্থা |
|---|---|---|---|
| D1-D6: confidence = consensus metric, কোনো predictive variance নেই; grade ladder উল্টো (C>A+); pseudo-confluence | **FIX-1: EC-V2** — `empiricalConfidence` = মাপা সেল থেকে স্কোর (hour .30 + rsiDirection .25 + structure .25 + fillState .20; base WR 0.45; bands A+≥0.500/A≥0.480/B≥0.460), **shadow mode**, crypto-only, NO_TRADE-তে কখনো না | #29 | merged + live |
| RSI gate SELL-leg অন্ধ (discriminate করে না: 45.7 vs 44.6) | **FIX-2:** `RSI_DIRECTION_GATE.sellPenaltyEnabled=false` (শুধু BUY chase-gate) | #30 | merged + live |
| ইউজারের চ্যালেঞ্জ সঠিক ছিল: D2 হার্ড-ব্লক (TRENDING 07-31 থেকে, RANGING_ALIGNED 08-15 থেকে) → NO_TRADE → মিন্ট-ই হয় না → হিস্ট্রি নেই → EC সেল নেই → shadow/analysis অসম্ভব (ভলিউম 175→21/দিন, −88%) | **FIX-3 (shadow-window data-unblock):** `D2_TRENDING_BLOCK_ENABLED=false` + `D2_RANGING_ALIGNED_BLOCK_ENABLED=false` + selectivity gate ঢিলা (excludeTrending/requirePendingEntry off, maxAtr null; **cryptoOnly রাখা হয়েছে**) | #31 | merged + live (v6.13.0) |

**রোলব্যাক:** সব ফিক্সই config.js-এর ফ্ল্যাগ/মোড — প্রতিটা এক-লাইনে ফেরানো যায়। নোট: selectivity push-gate শুধু Telegram চুপ করায় (signal.js-এ save আগে হয়, gate পরে) — হিস্ট্রি ও সেল ডেটা নিরাপদ।

---

## ৩. পরের agent-এর কংক্রিট কাজ (runbook)

```bash
# ধাপ ১ — ডেটা পর্যাপ্ত জমেছে কি না (09-01/09-02-র আগে চালালে শুধু progress দেখবে)
python3 scripts/ec_shadow_validate.py        # Ftt-Otc-v6 ক্লোনে

# ধাপ ২ — verdict পড়ো:
#   ল্যাডার monotone (C<B<A<A+; কমপক্ষে A+>C, top-two ব্যান্ডে n≥60)
#   + hour/fill সেল দিক ধরে রাখছে?

# ধাপ ৩ — হ্যাঁ হলে flip (এক-লাইন + version):
#   branch: feat/ec-decision-flip
#   src/config.js: EMPIRICAL_CONFIDENCE.mode: 'shadow' -> 'decision'
#   version bump 6.14.0 (health.js, index.js ×2, fix_tests.mjs T43j)
#   টেস্ট: সব ৮ suite green → PR → merge

# ধাপ ৪ — bundle + deploy + verify (§৪ দেখো) → /health = 6.14.0

# ধাপ ৫ — না হলে (non-monotone): flip কোরো না।
#   কোন ব্যান্ড/সেল ভাঙছে তা নিয়ে রিপোর্ট লিখে drive-এ push + user-এর সিদ্ধান্ত নাও।
```

**ভ্যালিডেশন টার্গেট:** শ্যাডো-শুরু 2026-08-30T07:55Z; বর্তমান হার ~95-100/দিন (crypto-only, weekend pace) → ৪৮-৭২ ঘণ্টায় ~২০০-৩০০ decided EC রেকর্ড আশা করা যায়।

---

## ৪. Deploy মেকানিক্স

```bash
# bundle (Ftt-Otc-v6 রুটে)
npx esbuild src/index.js --bundle --format=esm --target=es2022 --outfile=worker-v6140-YYYYMMDD.js
# deploy (user-এর দেওয়া CF token + account id env-এ)
CLOUDFLARE_API_TOKEN=... CLOUDFLARE_ACCOUNT_ID=... bash scripts/redeploy.sh [--fix-metadata] worker-v6140-YYYYMMDD.js
# verify
curl -H 'User-Agent: Mozilla/5.0' https://fttotcv6.umuhammadiswa.workers.dev/health
#   version, bindings (kvCache ready + rateLimiter KV-fallback + cerebrasAI ready),
#   push.tokenValid, crons (*/2, */5, Mon 00:00) — সব চেক করো
```

- `redeploy.sh` version check করে (`EXPECTED_VERSION` env বা default); wmeta স্টেল হলে `--fix-metadata`
- CF token কেবল Workers Scripts:Edit scope — deploy কমান্ডেই শেষ, কোথাও সেভ নয়

---

## ৫. কঠোর নিয়ম (ভাঙলে কাজ নষ্ট)

1. **টোকেন নিরাপত্তা:** GitHub PAT / CF token **শুধু git push / deploy কমান্ডে** ব্যবহার হবে। কোনো ফাইলে, কমিটে, রিপোর্টে, এই ডকে — **কখনো না।** **[2026-08-31 আপডেট:] পুরনো PAT + CF token user আগেই revoke করেছে (লাইভ 401 দিয়ে ভেরিফাইড; ডিস্ক থেকে ডেড কপি scrubbed)। Flip-এর দিন user থেকে fresh নেবে — scope: PAT-এ দুই repo-র push/PR merge; CF token Workers Scripts:Edit + account id। কাজ শেষে আবার revoke করাবে।**
2. **প্রতি সেশনে রিপোর্ট push (RULES.md RULE-2):** কাজ শেষে dated রিপোর্ট `reports/`-এ + এই ফাইলের §৬-এ এক লাইন append + drive push। রিপোর্ট ছাড়া সেশন শেষ = context miss।
3. **PR-first + টেস্ট:** সরাসরি main-এ কোড নয়; ৮টা suite green ছাড়া merge না। ইচ্ছাকৃত আউটপুট পরিবর্তন হলে r71-এর `BASELINE_COMMIT` refresh (F3-20 মেকানিজম)।
4. **No invented data:** প্রতিটা সংখ্যা live API বা সেভ করা স্ন্যাপশট থেকে; নমুনা ছোট হলে Wilson CI সহ বলবে, দাবি ছোট রাখবে।
5. **Local build ≠ deploy ≠ verify:** তিনটা আলাদা ধাপ — প্রতিটার পরে সত্যায়িত করবে।

---

## ৬. সেশন লগ (নতুন agent সবার নিচে append করবে)

- **2026-09-03 — v6.14.0 LIVE: V7 shadow engine + safety patch (tokens received, deploy done):** user দুই টোকেনই দিয়েছে (GitHub PAT + CF token+account)। চেইন: PAT/CF verify → `feat/v7-shadow` push (da421ea v7-shadow + 8ee700b safety patch) → PR#32 merged → worktree bundle (esbuild 348,915 B) → CF direct-API deploy → /health = **6.14.0** ✓। Safety patch (লাইভ ইফেক্ট): D2_TRENDING_BLOCK_ENABLED:true + excludeTrending:true + **নতুন excludeChase** (BUY rsi>55 / SELL rsi<45 push-suppress) — প্রত্যাশা ~১৬৩/দিন @ 37.3% → ~১১/দিন @ ~৫২%। V7 shadow (শুধু যন্ত্রণা-মুক্ত instrumentation): router+exclusion+trigger, v7obs: KV store, flip-gate WR≥60% n≥100 CI-lo>50%। টেস্ট: selectivity_chase 15/15 নতুন + fix 328 + rsi_gate 18 + ec_v2 43 + v7 13 সব সবুজ। রিপোর্ট: `DEPLOY_V6140_2026-09-03.md`। পরবর্তী: v7 shadow ৫-৭ দিন ডেটা জমা → weekly slice-summary → flip-gate চেক।

- **2026-09-03 — V7 ডিজাইন+বিল্ড (ইউজার: "engine ekdom new kore banate chai"):** ইউজার টার্গেট ১০/দিনে ৬-৮ win। সৎ অনুবাদ: ৬/১০=৬০% > breakeven ৫৫.৬% = লাভজনক; ৮০% প্রমিস না (কোনো মাপা স্লাইস সাপোর্ট করে না)। প্যারাডাইম: vote-counting (মাপা-মৃত: pooled 37.3%, corr -0.063) বাদ — **exclusion + trigger**। v7shadow.js (regime router, %B+RSI extremes, H1 rejection trigger, veto-stack), v7store.js (v7obs: counterfactual KV, dedup 30min/pair, cap 40/pair/30d, fetchExpiryPrice resolve), handler waitUntil admission (সব crypto tick, NO_TRADE-সহ) + cron resolver; version 6.14.0। রিপোর্ট: `ENGINE_V7_DESIGN_2026-09-03.md`।
- **2026-09-03 — SHADOW WINDOW FINAL: FLIP CANCELLED:** ৬৫৫ EC রেকর্ড (৬২৯ decided, ~১৩১/দিন, ৩.৮ দিন)। ল্যাডার non-monotone বড় n-এ কনফার্মড: C 43.3% (n=240) > B 32.3% (n=316); pooled 37.2% (< base 45, breakeven 55.6)। সব বেক-করা সেল-মান স্টেল/উল্টো (hour GOOD 32.8% বনাম BAD 47.3%; PENDING 34.1% বনাম meas 56%)। TRENDING 35.4% (n=325) — পুরনো ব্লক সঠিক ছিল; TRENDING+BUY 20.5% (n=39) সবচেয়ে খারাপ স্লাইস; DOT/USD 17.4%। সেরা স্লাইসও (পুরনো gate-pass) মাত্র 46.5% — breakeven-এর ৯pp নিচে। **৪র্থ edge-decay কনফার্মেশন; বর্তমান কোয়ালিটিতে লাভজনক কনফিগ নেই।** পথ: (১) নিরাপত্তা-প্যাচ (TRENDING ব্লক আবার ON + কঠোর push-gate; token লাগবে), (২) কিছু না করা (ক্ষতিকর), (৩) আসল গবেষণা — Lever 1 entry-at-fill / নতুন সোর্স। রিপোর্ট: `EC_SHADOW_WINDOW_FINAL_2026-09-03.md` (লোকাল কমিট, push pending fresh PAT)।

- **2026-08-31 — EC shadow day-1 interim validation:** 178 EC records (~89/দিন, decided 164)। ল্যাডার non-monotone (C 42.6% n=68 > B 36.8% n=76; A+ n=2) → **flip না, deploy না**। 🔍 মূল আবিষ্কার: structure সেল regime-নির্ভর — TRENDING+ALIGNED 28.8% (n=59) কিন্তু TRENDING+AGAINST 60.7% (n=28); RANGING-এ উল্টো — অথচ EC-তে regime সেল নেই → সম্ভাব্য পথ: 09-02-তে EC-v2.1 regime-split সেল প্যাচ (তখন fresh token) অথবা ল্যাডার ঠিক হলে সরাসরি flip। A+ ব্যান্ড প্রায় অজাগতিক (178-এ ২) → flip-এর আগে bands re-derive আবশ্যক। রিপোর্ট: `EC_SHADOW_VALIDATION_INTERIM_2026-08-31.md` (লোকাল কমিট — PAT revoked, fresh PAT পেলে push)।

- **2026-08-31 — টোকেন রোটেশন:** user দুটো টোকেনই (GitHub PAT + CF) revoke করেছে — PAT লাইভ-টেস্টে **401 Bad credentials** কনফার্মড, CF টোকেন ডিস্কে ছিলই না (by design)। লোকাল স্ক্রিপ্ট থেকে ডেড PAT scrubbed (open_pr_*.py)। Flip-এর দিন fresh token দরকার হবে।
- **2026-08-31 — v6.13.0 live check (ইউজার প্রশ্ন: "engine er ki obosta?"):** shadow start 2026-08-30T07:55Z; ~১০ঘ-এ ৪১টা EC-tagged crypto signal (~৯৫-১০০/দিন pace; গেট-এরা ছিল ৪-২৪/দিন); EC attach **১০০%**; TRENDING মিন্ট ফিরেছে (৪১% of POST); প্রাথমিক ল্যাডার **monotone** A+ 50% > A 50% > B 37.5% > C 18.8% (n ছোট, informational); TRENDING WR 12.5% (n=16) — পুরনো ব্লক কেন ছিল তা এখন সেলে মাপা হচ্ছে। রিপোর্ট: `SHADOW_WINDOW_STATUS_2026-08-31.md`
- **2026-08-30 — deploy day:** PR #29/#30 merge → v6.12.0 deploy; ইউজার চ্যালেঞ্জ ("data na pele ki kore analysis korbe") → তদন্তে প্রমাণিত → FIX-3 (PR #31, merge c1065bf) → v6.13.0 deploy (`--fix-metadata`) → shadow window শুরু 07:55Z।
- **2026-08-30 — audit day:** D1-D6 distortion audit (২টা রিপোর্ট drive-এ) → FIX-1 EC-V2 + FIX-2 RSI gate PR-ready।
