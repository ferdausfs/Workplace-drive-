#!/data/data/com.termux/files/usr/bin/bash
# ─────────────────────────────────────────────────────────────
# FTT Telegram Bot deploy — SINGLE FILE bundle (bot.js) + 1042 fix
# Fixes: error 1042 (worker-to-worker fetch) via compatibility_flags
#        + explicit SIGNAL_WORKER service binding -> fttotcv6
# Use:  1) download bot.js into ~/ftt-telegram-bot/
#       2) bash bot_deploy2.sh   (token enter)
# ─────────────────────────────────────────────────────────────
set -u
if [ ! -f bot.js ]; then echo "❌ bot.js ekhane nai"; exit 1; fi
echo "=== FTT Bot deploy (bundle + 1042 fix) ==="
echo -n "CF API Token: "; read -rs T; echo ""
A="b3082da169faec70425179ca62500bc1"
cat > "$HOME/bot_meta.json" <<'EOF'
{
  "main_module": "bot.js",
  "compatibility_date": "2024-01-01",
  "compatibility_flags": ["global_fetch_strictly_public"],
  "bindings": [
    {"type": "kv_namespace", "name": "BOT_KV", "namespace_id": "39653d1f9b5147259cf3791658f131d7"},
    {"type": "service", "name": "SIGNAL_WORKER", "service": "fttotcv6"}
  ],
  "triggers": [{"crons": ["*/5 * * * *"]}]
}
EOF
echo "Uploading bot.js ($(wc -c < bot.js) bytes) + bindings + flags..."
R=$(curl -s -X PUT \
  "https://api.cloudflare.com/client/v4/accounts/$A/workers/scripts/ftt-telegram-bot" \
  -H "Authorization: Bearer $T" \
  -F "metadata=@$HOME/bot_meta.json;type=application/json" \
  -F "bot.js=@bot.js;type=application/javascript+module")
echo "$R" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('success:', d.get('success'))
if not d.get('success'):
    for e in d.get('errors',[]): print('ERROR:', e.get('code'), e.get('message'))
else: print('id:', (d.get('result') or {}).get('id'))
"
if echo "$R" | python3 -c "import json,sys; sys.exit(0 if json.load(sys.stdin).get('success') else 1)"; then
  echo "✅ Deployed! ~15s por bot /signal test koro — 1042 chole jabe."
fi
