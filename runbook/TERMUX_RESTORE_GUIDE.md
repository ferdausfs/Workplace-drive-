# 📱 Termux Full Restore Guide — FTT Ecosystem
**Date:** 2026-08-13 · **Situation:** Termux data deleted, fresh start

---

## 🔥 Quick Start (একটা command)

```bash
# Termux open করে paste করো:
pkg update -y && pkg install -y git && git clone https://github.com/ferdausfs/Workplace-drive-.git && bash Workplace-drive-/scripts/termux_restore.sh
```

এটা সব করে দেবে — packages install, repos clone, data restore, scripts copy।

---

## 📋 Step-by-step (যদি Quick Start কাজ না করে)

### Step 1: Termux Storage Permission
```bash
termux-setup-storage
```
Popup permission চাইবে → Allow করো।

### Step 2: Packages
```bash
pkg update -y
pkg install -y nodejs-lts python git gh curl openssh tar gzip
pip install pandas xgboost scikit-learn
```

### Step 3: GitHub Auth
```bash
gh auth login
```
- GitHub.com → HTTPS → Paste token → **fine-grained PAT** (7-day, single repo)
- Token বানাও: https://github.com/settings/tokens?type=beta
  - Repository: `ferdausfs/Workplace-drive-` (এবং `ferdausfs/Ftt-Otc-v6` যদি worker test চালাও)
  - Permissions: Contents (Read/Write), Pull Requests (Read/Write)
  - Expiry: 7 days

### Step 4: Clone Drive Repo
```bash
git clone https://github.com/ferdausfs/Workplace-drive-.git
cd Workplace-drive-
```

### Step 5: Clone Individual Repos (dev/test/deploy এর জন্য)
```bash
cd ~
git clone https://github.com/ferdausfs/Ftt-Otc-v6.git
git clone https://github.com/ferdausfs/Ftt-app-002.git
git clone https://github.com/ferdausfs/ftt-telegram-bot.git
git clone https://github.com/ferdausfs/My-zakat.git
```

### Step 6: Phase F Data Restore
```bash
mkdir -p ~/phase_f_forward
tar -xzf Workplace-drive-/data/phase_f_forward_FULL_2026-08-12.tar.gz -C ~/
ls ~/phase_f_forward/
```

### Step 7: Copy Scripts
```bash
# Analysis scripts → home directory
cp Workplace-drive-/scripts/*.py ~/
cp Workplace-drive-/scripts/phase_f_snapshot.sh ~/

# Deploy scripts → project dirs
cp Workplace-drive-/scripts/worker_api_deploy.sh ~/Ftt-Otc-v6/
cp Workplace-drive-/scripts/deploy_bundle.sh ~/Ftt-Otc-v6/
cp Workplace-drive-/scripts/bot_deploy2.sh ~/ftt-telegram-bot/

# Bundles → project dirs
cp Workplace-drive-/bundles/worker-fixeh-20260807.js ~/Ftt-Otc-v6/
cp Workplace-drive-/bundles/bot-v442-20260808.js ~/ftt-telegram-bot/
```

### Step 8: Worker Test Setup
```bash
cd ~/Ftt-Otc-v6
git fetch --all   # r71_tests needs BASELINE_COMMIT
node scripts/fix_tests.mjs        # should be 158/158
node scripts/phase10_integration.mjs  # should be 19/19
node scripts/r71_tests.mjs        # should be 117P/0F
```

---

## 🔄 Daily Routine (প্রতিদিন)

```bash
# 1. Snapshot (UTC date)
cd ~ && bash phase_f_snapshot.sh

# 2. Analysis
python3 entryhit_corrected_analysis.py
python3 day3_analysis.py

# 3. Push to drive
cd ~/Workplace-drive- && bash scripts/daily-push.sh
```

---

## 🔐 Token Setup (RULE-7: chat-এ paste করো না!)

### Cloudflare
```bash
export CLOUDFLARE_API_TOKEN="your_token"
export CLOUDFLARE_ACCOUNT_ID="b3082da169faec70425179ca62500bc1"
```

### Worker Deploy
```bash
cd ~/Ftt-Otc-v6
bash worker_api_deploy.sh   # token hidden input
# OR
bash deploy_bundle.sh       # single bundle deploy
```

### Bot Deploy
```bash
cd ~/ftt-telegram-bot
bash bot_deploy2.sh   # token hidden input
```

---

## 📂 Directory Map

```
~/
├── Workplace-drive-          # drive repo (archive + scripts + reports)
│   ├── worker/               # worker code snapshot
│   ├── app/                  # app code snapshot
│   ├── bot/                  # bot code snapshot
│   ├── my-zakat/             # zakat app snapshot
│   ├── data/                 # Phase F data archives
│   ├── scripts/              # analysis + deploy scripts
│   ├── bundles/              # deployed JS bundles
│   ├── reports/              # verification reports
│   ├── prompts/              # agent prompts
│   └── runbook/              # MASTER RUNBOOK
│
├── Ftt-Otc-v6/               # worker repo (live dev)
├── Ftt-app-002/              # app repo (live dev)
├── ftt-telegram-bot/         # bot repo (live dev)
├── My-zakat/                 # zakat repo
│
├── phase_f_forward/          # daily snapshots
│   ├── 2026-08-01/
│   ├── ...
│   └── 2026-08-12/
│
├── phase_f_snapshot.sh       # snapshot script
├── entryhit_corrected_analysis.py
├── day3_analysis.py
├── d4_run.py
└── .ftt_env                  # token env (chmod 600)
```

---

## ⚠️ Common Issues

| Problem | Fix |
|---------|-----|
| `gh auth` fails | Token expired → new fine-grained PAT বানাও |
| `pip install` fails | `pkg install python-pip` আগে |
| `node` not found | `pkg install nodejs-lts` |
| `r71_tests` fails | `cd ~/Ftt-Otc-v6 && git fetch --all` |
| `esbuild` not found | `npm i -g esbuild` (bundle build এর জন্য) |
| Snapshot API 403 | Worker down? → `curl https://fttotcv6.umuhammadiswa.workers.dev/health` |

---

## 🧪 Verification Checklist

```bash
# All green হওয়া উচিত:
cd ~/Ftt-Otc-v6
node scripts/fix_tests.mjs           # 158/158
node scripts/phase10_integration.mjs  # 19/19
node scripts/r71_tests.mjs           # 117P/0F

cd ~/ftt-telegram-bot
node round2-bugfix-test.mjs          # 60/60
node menu-test.mjs                   # 74/74

cd ~/Ftt-app-002
npm install && npx tsc --noEmit       # clean
npx vite build                        # clean

# Live API check:
curl -s https://fttotcv6.umuhammadiswa.workers.dev/health | python3 -m json.tool
```
