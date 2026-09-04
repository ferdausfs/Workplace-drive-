# fix(deploy): redeploy.sh schedules PUT body → raw array (HTTP 10026) + EXPECTED_BYTES doc

**Repo:** `ferdausfs/Ftt-Otc-v6` · **Base:** `main` (`cd3dc08`) · **Branch:** `fix/redeploy-schedules-raw-array`

## What (1 file, 2 changes — shell script only)

`scripts/redeploy.sh`:

1. **Schedules PUT body → raw JSON array.**
   The script sent `{"schedules":[...]}`; Cloudflare's schedules API expects a **raw JSON
   array** `[{"cron":"..."}]`. The wrapper returns HTTP **10026** "Could not parse request body".
   - Reference: Cloudflare API reference — "Update Cron Triggers",
     `PUT /accounts/{account_id}/workers/scripts/{script_name}/schedules`, body = array of `{cron}`.
   - **Live-proven 2026-08-14:** the raw-array PUT returned `success:true` with the 3 crons
     (`*/2`, `*/5`, `0 0 * * 1`). The self-calib cron `0 0 * * 1` was genuinely absent live until
     then (created_on 2026-08-14T08:26:29Z).

2. **Doc fix — bundle size:** the `EXPECTED_BYTES` comment said the v6.10.1 bundle is
   `322,007 bytes`. The real, verified bundle is **322,283 bytes** (sha256 `6419a433…`, confirmed by
   independent rebuild = capsule-declared SHA). The stale figure would make `redeploy.sh`
   wrongly reject the correct bundle with "size mismatch".

## Why now
- The schedules 10026 failure was previously only documented as a live-side workaround
  (PROMPT_CF_CRON_FIX_2026-08-13.md); this closes it **in-repo** so every future deploy is correct.
- The 322,007 figure was a stale typo that would block the next `EXPECTED_BYTES`-guarded deploy.

## Verification
- `git apply --check` — **PASS** (clean, 2 hunks / 2 insertions / 2 deletions)
- `bash -n scripts/redeploy.sh` — **PASS**
- Functional: SCHED generator now emits `[{"cron":"*/2 * * * *"},{"cron":"*/5 * * * *"},{"cron":"0 0 * * 1"}]` (raw array, no wrapper)
- Live: raw-array PUT already returned `success:true` (2026-08-14) — same body shape this fix produces

## Test matrix (unchanged; no engine/test code touched)
`fix_tests` 304/0 · `phase10_integration` 19/19 · `phase10_smoke` 71/71 · `phase7_integration` 36/36 ·
`phase7_smoke` 68/68 · `d2_tests` 39/39 · `probe_tests` 34/34 · `entry_hit` 7/7 · `fx_mode` 20/20

## Deploy note
No live redeploy needed — the worker is already at v6.10.1 with all 3 crons registered
(2026-08-14). This PR only fixes the deploy script + doc for the next deploy cycle.
