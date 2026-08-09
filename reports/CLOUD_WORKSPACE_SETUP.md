# ☁️ FTT CLOUD WORKSPACE — Full Setup Guide
**Goal:** sob kaj (data, scripts, reports, kono file) internet-e ekta public drive-te — jekono AI agent shudhu **link/ID diye** access korte parbe.

**Proven (2026-08-09):** `raw.githubusercontent.com/<user>/<repo>/main/<path>` → **HTTP 200, kono token chara** — ei-i amader drive.

---

## 🏗️ Architecture: GitHub public repo = cloud workspace

```
ftt-workspace/  (public repo)
├── data/          ← Phase F snapshots (tar.gz, daily)
├── scripts/       ← analysis + deploy scripts
├── reports/       ← verification reports (.md)
├── uploads/       ← screenshots + kono file (tumi icche moto)
├── bundles/       ← deployed worker.js / bot.js artifacts
└── README.md      ← structure + status
```

**Agent access (kono token chara):**
- File: `https://raw.githubusercontent.com/<tumi>/ftt-workspace/main/<path>` → **download**
- Repo: `https://github.com/<tumi>/ftt-workspace` → **clone**
- List: `https://api.github.com/repos/<tumi>/ftt-workspace/contents/`

---

## 🚀 SETUP (ekbar, 5 min)

### Step 1 — Repo banao (browser)
1. `github.com/new`
2. Repo name: **`ftt-workspace`** · Public ✓ · "Add a README" ✓
3. Create

### Step 2 — Termux-e clone + first push
```bash
cd ~
git clone https://github.com/<tumi>/ftt-workspace.git
cd ftt-workspace
mkdir -p data scripts reports uploads bundles
# Phase F data + scripts copy koro (age-r export)
cp -r ~/storage/downloads/phase-f-export/scripts/* scripts/ 2>/dev/null
tar -xzf ~/storage/downloads/phase_f_forward_2026-08-09.tar.gz -C . 2>/dev/null || true
git add -A && git commit -m "init: scripts + data" && git push
```

### Step 3 — Daily update script (`daily-push.sh` — ami baniye diyechi)
```bash
cd ~/ftt-workspace && bash daily-push.sh
```
→ snapshot → analysis → report → tar data → commit → push (sob auto)

---

## 📤 UPLOAD (tumi, icche moto)
```bash
cd ~/ftt-workspace
cp ~/storage/downloads/<kono-file> uploads/    # kono file
git add -A && git commit -m "add file" && git push
```
Ba GitHub **web UI** thekeo: repo → Add file → Upload files (drag-drop, no git needed!)

---

## 📥 DOWNLOAD / AGENT ACCESS (jekono AI agent)
```bash
# ami ba kono agent (internet thakle):
curl -s https://raw.githubusercontent.com/<tumi>/ftt-workspace/main/data/phase_f_forward_2026-08-09.tar.gz -o phase_f.tar.gz
curl -s https://raw.githubusercontent.com/<tumi>/ftt-workspace/main/scripts/d4_run.py -o d4_run.py
```

---

## ⚡ QUICK SHARE (ekta file, git chara — Termux theke)
```bash
# catbox (permanent, direct URL, no account):
curl -F "reqtype=fileupload" -F "fileToUpload=@<file>" https://catbox.moe/user/api.php
# → returns https://files.catbox.moe/XXXX.png — ei URL kono agent-ke dao
```
⚠️ Sandbox IP theke catbox reject kore (test korechi) — kintu **Termux theke kaj kore** (user side). URL peye gele ami oi link theke fetch korte pari.

---

## 📋 DAILY ROUTINE (updated)
```
1. bash daily-push.sh          # snapshot + analysis + push (cloud)
2. report .md repo-te thakbe    # kono agent link diye pore
3. ami clone/pull kore kaj      # fresh data theke
```

## ⚠️ RULES (honest)
- **Token/secret kakhono repo-te push koro na** — GitHub public! Oi gulo shudhu Termux env-e.
- Repo public → **je kew padhte pare** — kono sensitive business info na (trading data thik ache, personal data na).
- Private korle ami access korte token lagbe — token chat-e na → public-i bhalo amader jonno.

## 🎯 BENEFIT
- **Workspace load problem shesh** — local-e shudhu active copy, baki sob cloud.
- **Data forever safe** — worker API 30-din TTL, kintu repo-te archive thakbe.
- **Kono agent swap kora jay** — shudhu link diye context load.
- **Tumi jekono device theke** upload/download korte paro.
