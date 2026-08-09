#!/data/data/com.termux/files/usr/bin/bash
# ─────────────────────────────────────────────────────────────
# FTT Worker (fttotcv6) — deploy via Cloudflare API + curl
# NO wrangler needed (wrangler's workerd doesn't run on Android).
# Use:  bash worker_api_deploy.sh   (repo root: ~/Ftt-Otc-v6)
# ─────────────────────────────────────────────────────────────
set -u

# Must run from the repo root (~/Ftt-Otc-v6)
if [ ! -d src ]; then
  echo "❌ Run this from the Ftt-Otc-v6 repo root (src/ folder ekhane nai)."
  echo "   cd ~/Ftt-Otc-v6  then  bash worker_api_deploy.sh"
  exit 1
fi

WORKER="fttotcv6"
ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID:-b3082da169faec70425179ca62500bc1}"
COMPAT_DATE="2025-01-01"
KV_SIGNAL="f553a3f10915478fa1b8165dd58ff6ea"   # SIGNAL_CACHE
KV_BOT="39653d1f9b5147259cf3791658f131d7"      # BOT_KV

echo "=============================================="
echo "  FTT Worker deploy — ${WORKER}"
echo "=============================================="
git log --oneline -1 | sed 's/^/  HEAD: /'
echo ""

# 1) API token (hidden)
if [ -z "${CLOUDFLARE_API_TOKEN:-}" ]; then
  echo -n "Cloudflare API Token paste koro (hidden): "
  read -r -s CF_TOKEN
  echo ""
  CLOUDFLARE_API_TOKEN="$CF_TOKEN"
fi

# 2) metadata (module worker: main_module + KV bindings)
META="${HOME}/worker_meta.json"
cat > "$META" <<EOF
{
  "main_module": "src/index.js",
  "compatibility_date": "${COMPAT_DATE}",
  "bindings": [
    {"type": "kv_namespace", "name": "SIGNAL_CACHE", "namespace_id": "${KV_SIGNAL}"},
    {"type": "kv_namespace", "name": "BOT_KV", "namespace_id": "${KV_BOT}"}
  ]
}
EOF

# 3) build curl -F parts for every src/*.js module
PARTS=(-F "metadata=@${META};type=application/json")
while IFS= read -r f; do
  PARTS+=(-F "${f}=@${f};type=application/javascript+module")
done < <(find src -name '*.js' -type f | sort)

echo "Uploading ${#PARTS[@]} module parts (metadata + $(find src -name '*.js' | wc -l) files)..."
echo ""

# 4) PUT to Cloudflare
RESP=$(curl -s -X PUT \
  "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/workers/scripts/${WORKER}" \
  -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
  "${PARTS[@]}")

echo "$RESP" | python3 -c "
import json,sys
try:
    d = json.load(sys.stdin)
except Exception as e:
    print('  Parse error — raw response:'); print(sys.stdin.read() if False else '')
    sys.exit(1)
print('  success:', d.get('success'))
print('  id:', (d.get('result') or {}).get('id'))
print('  modified_on:', (d.get('result') or {}).get('modified_on'))
if not d.get('success'):
    for e in d.get('errors', []): print('  ERROR:', e.get('code'), e.get('message'))
"

if echo "$RESP" | grep -q '"success":true'; then
  echo ""
  echo "✅ Script uploaded! Ekhon cron triggers set kori..."
  # 5) ensure cron triggers (result checker */2 + scanner */5)
  CRON=$(curl -s -X PUT \
    "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/workers/scripts/${WORKER}/schedules" \
    -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{"schedules":[{"cron":"*/2 * * * *"},{"cron":"*/5 * * * *"}]}')
  echo "$CRON" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('  cron success:', d.get('success'), '| schedules:', [(s or {}).get('cron') for s in d.get('result',[])])
"
  echo ""
  echo "✅ Done — live check: https://fttotcv6.umuhammadiswa.workers.dev/"
else
  echo ""
  echo "❌ Upload failed — uporer error dekho. Token/account check koro."
fi
