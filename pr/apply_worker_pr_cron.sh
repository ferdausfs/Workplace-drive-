#!/usr/bin/env bash
# apply_worker_pr_cron.sh — redeploy.sh CRONS default: 6-field -> 5-field (HTTP 10100 fix)
# Run from anywhere:  bash apply_worker_pr_cron.sh
set -u
PATCH_B64="LS0tIGEvc2NyaXB0cy9yZWRlcGxveS5zaAorKysgYi9zY3JpcHRzL3JlZGVwbG95LnNoCkBAIC00NSw3ICs0NSw3IEBACiAjICAgTUVUQSAgICAgICAgICAgIGRlZmF1bHQgJEhPTUUvd21ldGEuanNvbgogIyAgIEVYUEVDVEVEX0JZVEVTICBpZiBzZXQsIGJ1bmRsZSBzaXplIG11c3QgbWF0Y2ggZXhhY3RseSAodjYuMTAuMiBidW5kbGUKICMgICAgICAgICAgICAgICAgICAgcmVidWlsZCBhZnRlciBtZXJnZTsgc2V0IHRvIGl0cyBleGFjdCBieXRlIHNpemUpCi0jICAgQ1JPTlMgICAgICAgICAgIGNvbW1hIGxpc3QsIGRlZmF1bHQgIiovMiAqICogKiAqLCovNSAqICogKiAqLDAgMCAqICogKiAxIgorIyAgIENST05TICAgICAgICAgICBjb21tYSBsaXN0LCBkZWZhdWx0ICIqLzIgKiAqICogKiwqLzUgKiAqICogKiwwIDAgKiAqIDEiCiAjICAgSEVBTFRIX1VSTCAgICAgIGRlZmF1bHQgaHR0cHM6Ly9mdHRvdGN2Ni51bXVoYW1tYWRpc3dhLndvcmtlcnMuZGV2L2hlYWx0aAogIyAgIFNLSVBfSEVBTFRIPTEgICBza2lwIHRoZSBwb3N0LWRlcGxveSAvaGVhbHRoIHZlcmlmaWNhdGlvbgogIyBGbGFnczoKQEAgLTU2LDcgKzU2LDcgQEAKIFNDUklQVF9OQU1FPSIke1NDUklQVF9OQU1FOi1mdHRvdGN2Nn0iCiBNRVRBPSIke01FVEE6LSRIT01FL3dtZXRhLmpzb259IgogRVhQRUNURURfQllURVM9IiR7RVhQRUNURURfQllURVM6LX0iCi1DUk9OUz0iJHtDUk9OUzotKi8yICogKiAqICosKi81ICogKiAqICosMCAwICogKiAqIDF9IgorQ1JPTlM9IiR7Q1JPTlM6LSovMiAqICogKiAqLCovNSAqICogKiAqLDAgMCAqICogMX0iCiBIRUFMVEhfVVJMPSIke0hFQUxUSF9VUkw6LWh0dHBzOi8vZnR0b3RjdjYudW11aGFtbWFkaXN3YS53b3JrZXJzLmRldi9oZWFsdGh9IgogQVBJPSIke0NGX0FQSV9CQVNFOi1odHRwczovL2FwaS5jbG91ZGZsYXJlLmNvbS9jbGllbnQvdjR9IiAgICMgb3ZlcnJpZGFibGUgZm9yIHRlc3RzCiBGSVhfTUVUQURBVEE9MAo="
PATCH_SHA="3fefb6f9faee7cff7558b50092c8d9143a04b1c7b2fdac900bd11f5894ce919f"
fail() { echo "✗ $*" >&2; exit 1; }
cd ~/Ftt-Otc-v6 || fail "~/Ftt-Otc-v6 not found"
git fetch --quiet origin 2>/dev/null
BR=$(git rev-parse --abbrev-ref HEAD)
[ "$BR" = "main" ] || fail "not on main (on $BR)"
[ -z "$(git status --porcelain)" ] || fail "working tree not clean"

grep -q "0 0 \* \* \* 1" scripts/redeploy.sh || fail "expected 6-field cron not found — repo differs; aborting"
printf '%s' "$PATCH_B64" | base64 -d > $HOME/cronfix.patch
ACT=$(sha256sum $HOME/cronfix.patch | cut -d' ' -f1)
[ "$ACT" = "$PATCH_SHA" ] || fail "patch sha mismatch"
git apply --check $HOME/cronfix.patch || fail "git apply --check failed"
git apply $HOME/cronfix.patch || fail "git apply failed"
rm -f $HOME/cronfix.patch
grep -q "0 0 \* \* \* 1" scripts/redeploy.sh && fail "6-field STILL present"
grep -q "0 0 \* \* 1" scripts/redeploy.sh || fail "5-field not present"
bash -n scripts/redeploy.sh || fail "bash -n failed"
echo "  ✓ fix applied + verified"
git --no-pager diff --stat
git --no-pager diff -- scripts/redeploy.sh
git checkout -b fix/redeploy-cron-string
git add scripts/redeploy.sh
git commit -m "fix(deploy): CRONS default 6-field -> 5-field cron (HTTP 10100)" || fail "commit failed"
git push -u origin fix/redeploy-cron-string || fail "push failed"
echo ""
echo "═══ DONE ═══"
echo "Open PR : https://github.com/ferdausfs/Ftt-Otc-v6/compare/fix/redeploy-cron-string"
echo "PR body : ~/Workplace-drive-/pr/PR_BODY_redeploy_cron_fix.md"
