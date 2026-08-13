#!/data/data/com.termux/files/usr/bin/bash
# ════════════════════════════════════════════════════════════════
#  FTT Termux Restore Script — fresh install → full ecosystem
#  Run in Termux:  bash termux_restore.sh
#  Date: 2026-08-13
#  সতর্কতা: এই script token/secret রাখে না (RULE-7)।
#            Cloudflare + GitHub token আলাদা set করতে হবে।
# ════════════════════════════════════════════════════════════════
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

log()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
err()  { echo -e "${RED}[✗]${NC} $*"; }
step() { echo -e "\n${CYAN}═══ $* ═══${NC}"; }

# ─────────────────────────────────────────────────
# 0. Storage permission
# ─────────────────────────────────────────────────
step "Step 0/8 — Storage permission"
if [ ! -d ~/storage ]; then
  warn "Storage setup needed. Running termux-setup-storage..."
  termux-setup-storage 2>/dev/null || warn "termux-setup-storage failed — run manually if needed"
else
  log "Storage already set up"
fi

# ─────────────────────────────────────────────────
# 1. Core packages
# ─────────────────────────────────────────────────
step "Step 1/8 — Installing packages (nodejs-lts, python, git, gh, curl, esbuild)"

pkg update -y 2>/dev/null
pkg install -y nodejs-lts python git gh curl openssh tar gzip 2>/dev/null || {
  warn "pkg failed, trying apt..."
  apt update -y && apt install -y nodejs python git gh curl openssh tar gzip
}

# Python packages for analysis scripts
pip install pandas xgboost scikit-learn 2>/dev/null || pip3 install pandas xgboost scikit-learn 2>/dev/null || warn "pip install failed — analysis scripts may not work"

# Verify
node -v && log "Node.js: $(node -v)"
python3 --version && log "Python: $(python3 --version)"
git --version && log "Git: $(git --version)"
gh --version | head -1 && log "GitHub CLI installed"

# ─────────────────────────────────────────────────
# 2. GitHub authentication
# ─────────────────────────────────────────────────
step "Step 2/8 — GitHub authentication"
if gh auth status >/dev/null 2>&1; then
  log "GitHub CLI already authenticated"
else
  warn "GitHub CLI not authenticated!"
  echo ""
  echo "  একটা NEW fine-grained PAT বানাও:"
  echo "  1. https://github.com/settings/tokens?type=beta যাও"
  echo "  2. 'Generate new token' → 7-day expiry → single repo: ferdausfs/Workplace-drive-"
  echo "  3. Permissions: Contents(Read/Write), Pull Requests(Read/Write)"
  echo "  4. Token নিচে paste করো"
  echo ""
  echo -n "  GitHub PAT (hidden): "
  read -rs GH_TOKEN
  echo ""
  if [ -n "$GH_TOKEN" ]; then
    echo "$GH_TOKEN" | gh auth login --with-token 2>/dev/null && log "GitHub authenticated!" || err "Auth failed"
  else
    warn "Skipped — later `gh auth login` দিয়ে setup করো"
  fi
fi

# ─────────────────────────────────────────────────
# 3. Git config
# ─────────────────────────────────────────────────
step "Step 3/8 — Git config"
git config --global user.name "ferdausfs" 2>/dev/null
git config --global user.email "ftt@local" 2>/dev/null
git config --global init.defaultBranch main 2>/dev/null
log "Git config set"

# ─────────────────────────────────────────────────
# 4. Clone repos (or update drive repo)
# ─────────────────────────────────────────────────
step "Step 4/8 — Cloning / updating repos"

clone_or_pull() {
  local dir="$1" url="$2"
  if [ -d "$dir/.git" ]; then
    cd "$dir" && git pull --ff-only 2>/dev/null && log "$dir updated" || warn "$dir pull failed"
    cd ~
  else
    git clone "$url" "$dir" 2>/dev/null && log "$dir cloned" || err "$dir clone failed (check GitHub auth)"
  fi
}

# Main drive repo
clone_or_pull ~/Workplace-drive- "https://github.com/ferdausfs/Workplace-drive-.git"

# Individual project repos (for dev/test/deploy)
clone_or_pull ~/Ftt-Otc-v6 "https://github.com/ferdausfs/Ftt-Otc-v6.git"
clone_or_pull ~/Ftt-app-002 "https://github.com/ferdausfs/Ftt-app-002.git"
clone_or_pull ~/ftt-telegram-bot "https://github.com/ferdausfs/ftt-telegram-bot.git"
clone_or_pull ~/My-zakat "https://github.com/ferdausfs/My-zakat.git"

# ─────────────────────────────────────────────────
# 5. Restore data from drive (Phase F snapshots)
# ─────────────────────────────────────────────────
step "Step 5/8 — Restoring Phase F data"

DRIVE="$HOME/Workplace-drive-"
mkdir -p ~/phase_f_forward

# Unpack latest data archive from drive
LATEST_TAR=$(ls -t "$DRIVE/data/"phase_f_forward_*.tar.gz 2>/dev/null | head -1)
if [ -n "$LATEST_TAR" ]; then
  tar -xzf "$LATEST_TAR" -C ~/ 2>/dev/null && log "Phase F data restored: $(basename "$LATEST_TAR")" || warn "Extract failed"
  # Show what dates are available
  echo "  Available dates:"
  ls ~/phase_f_forward/ 2>/dev/null | tail -10
else
  warn "No data archive found in drive/data/"
fi

# ─────────────────────────────────────────────────
# 6. Copy deploy scripts & bundles to project dirs
# ─────────────────────────────────────────────────
step "Step 6/8 — Restoring deploy scripts & bundles"

# Worker deploy scripts
if [ -d ~/Ftt-Otc-v6 ]; then
  cp "$DRIVE/scripts/worker_api_deploy.sh" ~/Ftt-Otc-v6/ 2>/dev/null && log "worker_api_deploy.sh → ~/Ftt-Otc-v6/"
  cp "$DRIVE/scripts/deploy_bundle.sh" ~/Ftt-Otc-v6/ 2>/dev/null && log "deploy_bundle.sh → ~/Ftt-Otc-v6/"
  # Restore latest bundle
  if [ -f "$DRIVE/bundles/worker-fixeh-20260807.js" ]; then
    cp "$DRIVE/bundles/worker-fixeh-20260807.js" ~/Ftt-Otc-v6/ 2>/dev/null && log "worker-fixeh-20260807.js → ~/Ftt-Otc-v6/"
  fi
fi

# Bot deploy script + bundle
if [ -d ~/ftt-telegram-bot ]; then
  cp "$DRIVE/scripts/bot_deploy2.sh" ~/ftt-telegram-bot/ 2>/dev/null && log "bot_deploy2.sh → ~/ftt-telegram-bot/"
  if [ -f "$DRIVE/bundles/bot-v442-20260808.js" ]; then
    cp "$DRIVE/bundles/bot-v442-20260808.js" ~/ftt-telegram-bot/ 2>/dev/null && log "bot-v442-20260808.js → ~/ftt-telegram-bot/"
  fi
fi

# Copy analysis scripts to home (convenient)
cp "$DRIVE/scripts/"*.py ~/ 2>/dev/null && log "Analysis scripts → ~/ (phase_f_snapshot.sh, entryhit, day3, d4...)"
cp "$DRIVE/scripts/phase_f_snapshot.sh" ~/ 2>/dev/null && log "phase_f_snapshot.sh → ~/"

# ─────────────────────────────────────────────────
# 7. Worker test dependencies (esbuild for r71)
# ─────────────────────────────────────────────────
step "Step 7/8 — Worker test setup"

if [ -d ~/Ftt-Otc-v6 ]; then
  cd ~/Ftt-Otc-v6
  # r71_tests needs the baseline commit locally
  git fetch --unshallow 2>/dev/null || git fetch --all 2>/dev/null || warn "git fetch failed — r71_tests may fail (needs BASELINE_COMMIT)"
  log "Worker repo ready for tests"
  cd ~
fi

# ─────────────────────────────────────────────────
# 8. Cloudflare token reminder
# ─────────────────────────────────────────────────
step "Step 8/8 — Environment variables"

ENV_FILE="$HOME/.ftt_env"
cat > "$ENV_FILE" <<'ENVEOF'
# ═══ FTT Environment Variables ═══
# এই file-এ token রাখো — source করো:  source ~/.ftt_env
# RULE-7: এই file git-এ commit করো না!

# Cloudflare
# export CLOUDFLARE_API_TOKEN="your_cf_token_here"
# export CLOUDFLARE_ACCOUNT_ID="b3082da169faec70425179ca62500bc1"

# GitHub (gh auth handles this)
ENVEOF

chmod 600 "$ENV_FILE"
log "Env template: $ENV_FILE (token set করো)"

# ─────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────
echo ""
echo -e "${CYAN}══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ Termux Restore Complete!${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════${NC}"
echo ""
echo "  📂 Repos cloned/updated:"
echo "     ~/Workplace-drive-    (drive — main archive)"
echo "     ~/Ftt-Otc-v6          (worker — signal engine)"
echo "     ~/Ftt-app-002         (app — React frontend)"
echo "     ~/ftt-telegram-bot    (bot — Telegram)"
echo "     ~/My-zakat            (zakat app)"
echo ""
echo "  📊 Phase F data: ~/phase_f_forward/"
echo "  📜 Analysis scripts: ~/*.py + ~/phase_f_snapshot.sh"
echo ""
echo "  ⚠️  Token setup বাকি:"
echo "     1. source ~/.ftt_env   (file edit করে token রাখো)"
echo "     2. gh auth status      (GitHub check)"
echo ""
echo "  🔄 Daily snapshot চালাতে:"
echo "     cd ~/Workplace-drive- && bash scripts/daily-push.sh"
echo ""
echo "  🧪 Worker test চালাতে:"
echo "     cd ~/Ftt-Otc-v6 && node scripts/fix_tests.mjs"
echo ""
