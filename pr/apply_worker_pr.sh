#!/usr/bin/env bash
# apply_worker_pr.sh — Ftt-Otc-v6 PR: redeploy.sh schedules raw-array fix + EXPECTED_BYTES doc
# Run from anywhere:  bash apply_worker_pr.sh
# What it does (PR-first, never touches main):
#   verify guards -> git apply -> verify -> bash -n -> functional check ->
#   checkout -b fix/redeploy-schedules-raw-array -> commit -> push branch (NOT main)
set -u

PATCH_B64="LS0tIGEvc2NyaXB0cy9yZWRlcGxveS5zaAorKysgYi9zY3JpcHRzL3JlZGVwbG95LnNoCkBAIC00NCw3ICs0NCw3IEBACiAjICAgU0NSSVBUX05BTUUgICAgIGRlZmF1bHQgZnR0b3RjdjYKICMgICBNRVRBICAgICAgICAgICAgZGVmYXVsdCAkSE9NRS93bWV0YS5qc29uCiAjICAgRVhQRUNURURfQllURVMgIGlmIHNldCwgYnVuZGxlIHNpemUgbXVzdCBtYXRjaCBleGFjdGx5ICh2Ni4xMC4xIGJ1bmRsZQotIyAgICAgICAgICAgICAgICAgICB3b3JrZXItdjYxMDEtMjAyNjA4MTIuanMgPSAzMjIwMDcgYnl0ZXMpCisjICAgICAgICAgICAgICAgICAgIHdvcmtlci12NjEwMS0yMDI2MDgxMi5qcyA9IDMyMjI4MyBieXRlcykKICMgICBDUk9OUyAgICAgICAgICAgY29tbWEgbGlzdCwgZGVmYXVsdCAiKi8yICogKiAqICosKi81ICogKiAqICosMCAwICogKiAqIDEiCiAjICAgSEVBTFRIX1VSTCAgICAgIGRlZmF1bHQgaHR0cHM6Ly9mdHRvdGN2Ni51bXVoYW1tYWRpc3dhLndvcmtlcnMuZGV2L2hlYWx0aAogIyAgIFNLSVBfSEVBTFRIPTEgICBza2lwIHRoZSBwb3N0LWRlcGxveSAvaGVhbHRoIHZlcmlmaWNhdGlvbgpAQCAtMjMzLDcgKzIzMyw3IEBACiAjIOKUgOKUgCAyKSBDcm9uIHRyaWdnZXJzIChzZXBhcmF0ZSBlbmRwb2ludCDigJQgTk9UIHBhcnQgb2YgdGhlIHVwbG9hZCBwYXlsb2FkKSDilIDilIAKIHNheSAiIgogc2F5ICJTZXR0aW5nIGNyb24gdHJpZ2dlcnMgb24gJFNDUklQVF9OQU1FIC4uLiIKLVNDSEVEPSIkKHB5dGhvbjMgLWMgJ2ltcG9ydCBzeXMsanNvbjsgcHJpbnQoanNvbi5kdW1wcyh7InNjaGVkdWxlcyI6W3siY3JvbiI6Yy5zdHJpcCgpfSBmb3IgYyBpbiBzeXMuYXJndlsxXS5zcGxpdCgiLCIpIGlmIGMuc3RyaXAoKV19KSknICIkQ1JPTlMiKSIKK1NDSEVEPSIkKHB5dGhvbjMgLWMgJ2ltcG9ydCBzeXMsanNvbjsgcHJpbnQoanNvbi5kdW1wcyhbeyJjcm9uIjpjLnN0cmlwKCl9IGZvciBjIGluIHN5cy5hcmd2WzFdLnNwbGl0KCIsIikgaWYgYy5zdHJpcCgpXSkpJyAiJENST05TIikiCiBzYXkgIiAgc2NoZWR1bGVzID0gJFNDSEVEIgogY2ZfY2FsbCBQVVQgIiRBUEkvYWNjb3VudHMvJENMT1VERkxBUkVfQUNDT1VOVF9JRC93b3JrZXJzL3NjcmlwdHMvJFNDUklQVF9OQU1FL3NjaGVkdWxlcyIgLS1kYXRhLWpzb24gIiRTQ0hFRCIgXAogICB8fCBkaWUgInNjaGVkdWxlIHVwZGF0ZSBmYWlsZWQg4oCUIHNlZSByYXcgcmVzcG9uc2UgYWJvdmUiCg=="
PATCH_SHA="be89ca82acb472ced78ba16bbf5619b635c25553bfe3369fcd06d07e6a43d2d0"

fail() { echo "✗ $*" >&2; exit 1; }

command -v git >/dev/null || fail "git not installed"
command -v python3 >/dev/null || fail "python3 not installed"
cd ~/Ftt-Otc-v6 || fail "~/Ftt-Otc-v6 not found"

echo "── repo state check ──"
git fetch --quiet origin 2>/dev/null
BR=$(git rev-parse --abbrev-ref HEAD)
[ "$BR" = "main" ] || fail "not on main (on '$BR') — switch: git checkout main"
DIRTY=$(git status --porcelain)
[ -z "$DIRTY" ] || fail "working tree not clean:\n$DIRTY\n  commit or stash first"

echo "── guards: expected OLD content present? ──"
grep -q '{"schedules":' scripts/redeploy.sh || fail "wrapper SCHED line not found — file differs from expected; aborting (no changes made)"
grep -q '322007' scripts/redeploy.sh || fail "322007 comment not found — file differs from expected; aborting (no changes made)"
echo "  ✓ old content confirmed"

echo "── decode + verify patch ──"
printf '%s' "$PATCH_B64" | base64 -d > $HOME/redeploy_fix.patch
ACT=$(sha256sum $HOME/redeploy_fix.patch | cut -d' ' -f1)
[ "$ACT" = "$PATCH_SHA" ] || fail "patch sha mismatch: got $ACT"
echo "  ✓ patch sha ok"

echo "── apply ──"
git apply --check $HOME/redeploy_fix.patch || fail "git apply --check failed"
git apply $HOME/redeploy_fix.patch || fail "git apply failed"
rm -f $HOME/redeploy_fix.patch

echo "── verify new content ──"
grep -q '{"schedules":' scripts/redeploy.sh && fail "wrapper STILL present after apply"
grep -q '322007' scripts/redeploy.sh && fail "322007 STILL present after apply"
grep -q 'json.dumps(\[{' scripts/redeploy.sh || fail "raw-array not present"
grep -q '322283' scripts/redeploy.sh || fail "322283 not present"
bash -n scripts/redeploy.sh || fail "bash -n failed"
CRONS="*/2 * * * *,*/5 * * * *,0 0 * * 1"
OUT=$(python3 -c 'import sys,json; print(json.dumps([{"cron":c.strip()} for c in sys.argv[1].split(",") if c.strip()]))' "$CRONS")
case "$OUT" in
  \[*) echo "  ✓ SCHED emits raw array: $OUT" ;;
  *) fail "SCHED not a raw array: $OUT" ;;
esac
echo "  ✓ all checks passed"

echo "── diff (review) ──"
git --no-pager diff -- scripts/redeploy.sh

echo "── branch + commit + push (BRANCH ONLY, never main) ──"
git checkout -b fix/redeploy-schedules-raw-array
git add scripts/redeploy.sh
git commit -m "fix(deploy): schedules PUT raw array (HTTP 10026) + EXPECTED_BYTES 322283" || fail "commit failed"
git push -u origin fix/redeploy-schedules-raw-array || fail "push failed (check auth — no tokens in chat)"

echo ""
echo "═══ DONE — branch pushed ═══"
echo "PR title : fix(deploy): redeploy.sh schedules PUT body raw array (HTTP 10026) + EXPECTED_BYTES doc"
echo "PR body  : full text in ~/Workplace-drive-/pr/PR_BODY_redeploy_fix.md (copy-paste into GitHub)"
echo "Open PR  : https://github.com/ferdausfs/Ftt-Otc-v6/compare/fix/redeploy-schedules-raw-array"
echo "After merge: git checkout main && git pull"
