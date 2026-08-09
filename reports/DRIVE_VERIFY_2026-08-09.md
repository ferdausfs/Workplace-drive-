# ✅ WORKSPACE DRIVE — FULL VERIFICATION (2026-08-09)

## 5 Repos — All Live & Synced

| Repo | main | WORKSPACE_DRIVE.md | Status |
|---|---|---|---|
| **Ftt-Otc-v6** (worker) | `ee7fc54` | ✅ 200 | pointer pushed |
| **Ftt-app-002** (app) | `af9bf22` | ✅ 200 | pointer pushed + PR #4 merged |
| **ftt-telegram-bot** (bot) | `67ba775` | ✅ 200 | pointer pushed |
| **My-zakat** | `dca5ca8` | ✅ 200 | pointer pushed |
| **Workplace-drive-** | `e5af1f0` | (n/a — README+RULES instead) | ✅ RULES.md present |

## Drive Test — Data from DRIVE (local file na chuye)

### EntryHit analysis (drive clone → drive data → drive script):
```
FIX-EH decided rows: 430
legacy-MISS WR: 100.0% (tautology intact — old field)
eh-MISS WR:     46.5% (tautology BROKEN — corrected metric works)
```

### D4 ML (drive clone → drive data → drive script):
```
forward decided: 3301 | days: 08-01..09
LEGIT WIN-call: 56.2% (n=16, CI 33.2-76.9) — ambiguous, no edge
Baseline engine: 43.1%
```

**Both match the local results exactly** → the drive is a working, self-contained workspace.

## RULES ACTIVE (RULE-1..8)
- RULE-1: Drive = source of truth ✅
- RULE-2: Proti kaj drive-te push ✅ (RULES.md pushed)
- RULE-3: Proti turn context check — **ami ekhon theke drive pull kore kaj korbo** ✅
- RULE-4: Code PR-first (project repos) ✅
- RULE-5-8: Verification / Phase F / Security / Honesty ✅

## NEXT STEPS (drive README/RULES-te lekha ache)
1. Phase F daily: `bash scripts/daily-push.sh` → snapshot → analysis → push drive.
2. App PR #4 merged ✓ — Vercel auto-deploy verify.
3. Cloudflare token rotation (`cfut_pTef5...`) — user check.
4. Deriv demo — on hold (user decision).
5. Custom Alerts (F09) worker-side — future.

## WORKFLOW NOW (RULE-3)
```
Proti turn:
  1. ami drive repo pull/API check → notun push ache kina
  2. miss thakle → oita drive-te push kore kaj aage
  3. user-ke honest report
```
