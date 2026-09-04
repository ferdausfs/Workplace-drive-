# fix(deploy): redeploy.sh CRONS default — 6-field cron → 5-field (HTTP 10100)

**Repo:** `ferdausfs/Ftt-Otc-v6` · **Base:** `main` (`380916cb`) · **Branch:** `fix/redeploy-cron-string`

## Why (live-proven 2026-08-14)
`scripts/redeploy.sh`-এর default `CRONS`-এ self-calib cron লেখা ছিল **`0 0 * * * 1` (৬ field)** — একটা
বাড়তি `*`। Cloudflare cron **৫ field** চায় (`min hour dom month dow`); ৬ field দিলে HTTP **10100
"invalid cron string"**।

- **Live evidence:** v6.10.2 deploy (13:10Z) — worker upload `success:true`, কিন্তু schedules PUT →
  `10100 invalid cron string: 0 0 * * * 1`।
- `wrangler.toml`-এ সঠিক **`0 0 * * 1`** (৫ field) — script আর config-এ mismatch ছিল।
- আগের successful cron set (08:26Z) direct curl দিয়ে সঠিক ৫-field ব্যবহার করেছিল, তাই live crons
  এখনো ঠিক আছে — এই bug-টা শুধু পরবর্তী deploy-গুলোকে ভাঙত।

## What changed
`scripts/redeploy.sh` — ২ লাইন: comment + `CRONS` default-এ `0 0 * * * 1` → `0 0 * * 1`।

## Verification
- `bash -n scripts/redeploy.sh` — PASS
- Functional: default `CRONS` এখন `[{"cron":"*/2 * * * *"},{"cron":"*/5 * * * *"},{"cron":"0 0 * * 1"}]` (৫ field)
- `git apply --check` — PASS (`380916cb` state)
- Live: worker already v6.10.2 + ৩টা cron registered (08:26 set intact) — এ PR-টা শুধু script-ই ঠিক করে।

## Note
Deploy-এ কোনো re-run লাগবে না — worker v6.10.2 live, crons ঠিক। এটা পরের deploy cycle-র জন্য।
