#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
# phase_f_snapshot.sh — daily FTT Phase F forward snapshot
# Run ONCE per real UTC day. No date argument needed (uses
# `date -u +%F` internally, so a "future date" mistake is
# impossible with this version).
# Saves to ~/phase_f_forward/<UTC-DATE>/
# ============================================================
set -u

BASE="$HOME/phase_f_forward"
TODAY="$(date -u +%F)"
DIR="$BASE/$TODAY"

API="https://fttotcv6.umuhammadiswa.workers.dev"

# 18 standard pairs (exactly as in the Phase F protocol)
PAIRS="ADA/USD AUD/USD AVAX/USD BNB/BTC BNB/USD BTC/USD DOGE/USD DOT/USD ETH/USD EUR/USD GBP/CHF GBP/USD LINK/USD SOL/USD USD/CAD USD/CHF USD/JPY XRP/USD"

mkdir -p "$DIR"

echo "[1/3] Downloading history JSON for each pair..."
for P in $PAIRS; do
  SAFE="${P//\//_}"
  curl -s -m 30 "$API/api/history?pair=$P&limit=500" -o "$DIR/$SAFE.json"
done
curl -s -m 30 "$API/api/pairs" -o "$DIR/pairs.json"
curl -s -m 30 "$API/health" -o "$DIR/health.json"

echo "[2/3] Building MANIFEST.txt with HTTP codes..."
: > "$DIR/MANIFEST.txt"
for P in $PAIRS; do
  SAFE="${P//\//_}"
  CODE="$(curl -s -m 30 -o /dev/null -w '%{http_code}' "$API/api/history?pair=$P&limit=500")"
  echo "$P http=$CODE" >> "$DIR/MANIFEST.txt"
done
echo "pairs http=$(curl -s -m 30 -o /dev/null -w '%{http_code}' "$API/api/pairs")" >> "$DIR/MANIFEST.txt"
echo "health http=$(curl -s -m 30 -o /dev/null -w '%{http_code}' "$API/health")" >> "$DIR/MANIFEST.txt"

echo "[3/3] Writing SHA256SUMS.txt..."
cd "$DIR" && sha256sum *.json > SHA256SUMS.txt

echo ""
echo "✔ Snapshot saved: $DIR"
echo "Files:"; ls -1 "$DIR"
