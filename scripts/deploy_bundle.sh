#!/data/data/com.termux/files/usr/bin/bash
# ─────────────────────────────────────────────────────────────
# FTT Worker (fttotcv6) deploy — SINGLE FILE (bundled worker.js)
# Use:  1) download worker.js into this folder (~/Ftt-Otc-v6/)
#       2) bash deploy_bundle.sh   → token enter koro
# ─────────────────────────────────────────────────────────────
set -u

if [ ! -f worker.js ]; then
  echo "❌ worker.js ekhane nai — age download koro (~/Ftt-Otc-v6/worker.js)"
  exit 1
fi

echo "=== FTT Worker deploy (single bundle) ==="
echo -n "CF API Token: "; read -rs T; echo ""
A="b3082da169faec70425179ca62500bc1"

cat > "$HOME/wmeta.json" <<EOF
{"main_module":"worker.js","compatibility_date":"2025-01-01","bindings":[
{"type":"kv_namespace","name":"SIGNAL_CACHE","namespace_id":"f553a3f10915478fa1b8165dd58ff6ea"},
{"type":"kv_namespace","name":"BOT_KV","namespace_id":"39653d1f9b5147259cf3791658f131d7"}]}
EOF

echo "Uploading worker.js ($(wc -c < worker.js) bytes)..."
R=$(curl -s -X PUT \
  "https://api.cloudflare.com/client/v4/accounts/$A/workers/scripts/fttotcv6" \
  -H "Authorization: Bearer $T" \
  -F "metadata=@$HOME/wmeta.json;type=application/json" \
  -F "worker.js=@worker.js;type=application/javascript+module")

echo "$R" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('success:', d.get('success'))
if not d.get('success'):
    for e in d.get('errors',[]): print('ERROR:', e.get('code'), e.get('message'))
else:
    print('id:', (d.get('result') or {}).get('id'), '| modified:', (d.get('result') or {}).get('modified_on'))
"

if echo "$R" | python3 -c "import json,sys; sys.exit(0 if json.load(sys.stdin).get('success') else 1)"; then
  echo "Setting cron triggers..."
  curl -s -X PUT "https://api.cloudflare.com/client/v4/accounts/$A/workers/scripts/fttotcv6/schedules" \
    -H "Authorization: Bearer $T" -H "Content-Type: application/json" \
    -d '{"schedules":[{"cron":"*/2 * * * *"},{"cron":"*/5 * * * *"}]}' \
    | python3 -c "import json,sys;d=json.load(sys.stdin);print('cron:', d.get('success'))"
  echo ""
  echo "✅ DONE — https://fttotcv6.umuhammadiswa.workers.dev/"
else
  echo "Upload failed — error upore."
fi
