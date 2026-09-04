#!/data/data/com.termux/files/usr/bin/bash
# ─────────────────────────────────────────────────────────────
# Cloudflare Worker deploy via HTTP API (no wrangler needed)
# ─────────────────────────────────────────────────────────────
# USAGE:
#   1. Make a Cloudflare API Token (dash.cloudflare.com → My Profile
#      → API Tokens → Create Token → "Edit Cloudflare Workers")
#      Permissions: Workers Scripts:Edit, Workers KV:Edit, Account Settings:Read
#      Account: ferdausfs / all
#   2. Run:
#        export CF_API_TOKEN="your_token_here"
#        export CF_ACCOUNT_ID="your_account_id_here"
#        ./termux_cf_deploy.sh
#
# NOTE: This updates the worker SCRIPT only. KV + service binding +
# secrets (BOT_TOKEN, SETUP_SECRET) stay as configured in the dashboard —
# they are not touched, so the bot keeps working.
# ─────────────────────────────────────────────────────────────

set -e
cd "$(dirname "$0")/ftt-telegram-bot"

if [ -z "$CF_API_TOKEN" ] || [ -z "$CF_ACCOUNT_ID" ]; then
  echo "❌ CF_API_TOKEN ও CF_ACCOUNT_ID set করুন (export ...)।"
  exit 1
fi

WORKER="ftt-telegram-bot"
SCRIPT="src/index.js"

echo "=== 1) upload script (PUT /workers/scripts/${WORKER}) ==="
curl -s -X PUT \
  "https://api.cloudflare.com/client/v4/accounts/${CF_ACCOUNT_ID}/workers/scripts/${WORKER}" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/javascript" \
  --data-binary @"${SCRIPT}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('   success:', d.get('success'), '| id:', (d.get('result') or {}).get('id'), '| errors:', d.get('errors'))"

echo "=== 2) ensure KV binding (BOT_KV) ==="
curl -s -X PUT \
  "https://api.cloudflare.com/client/v4/accounts/${CF_ACCOUNT_ID}/workers/scripts/${WORKER}/bindings" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"bindings":[{"type":"kv_namespace","name":"BOT_KV","namespace_id":"39653d1f9b5147259cf3791658f131d7"},{"type":"service","name":"SIGNAL_WORKER","service":"fttotcv6"}]}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('   success:', d.get('success'), '| errors:', d.get('errors'))"

echo "=== 3) trigger deployment ==="
curl -s -X POST \
  "https://api.cloudflare.com/client/v4/accounts/${CF_ACCOUNT_ID}/workers/scripts/${WORKER}/subdomain" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -o /dev/null -w "   subdomain endpoint: %{http_code}\n" || true

# create deployment
curl -s -X POST \
  "https://api.cloudflare.com/client/v4/accounts/${CF_ACCOUNT_ID}/workers/scripts/${WORKER}/versions" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"deployment\":{\"strategy\":\"percentage\",\"strategy_percentage\":100},\"metadata\":{\"bindings\":[{\"type\":\"kv_namespace\",\"name\":\"BOT_KV\",\"namespace_id\":\"39653d1f9b5147259cf3791658f131d7\"},{\"type\":\"service\",\"name\":\"SIGNAL_WORKER\",\"service\":\"fttotcv6\"}],\"main_module\":\"index.js\"}}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('   success:', d.get('success'), '| errors:', d.get('errors'))" 2>/dev/null || echo "   (versions endpoint optional — try 'Deploy' in dashboard if this fails)"

echo ""
echo "✅ Done — verify: curl https://ftt-telegram-bot.umuhammadiswa.workers.dev/health"
