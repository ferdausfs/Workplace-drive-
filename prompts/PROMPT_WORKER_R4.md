# WORKER (Ftt-Otc-v6) — AGENT PROMPT (round 4: F3-20 r71 baseline cleanup)

**Repo:** `ferdausfs/Ftt-Otc-v6` · **Main HEAD:** `e56cd33` (round-3 merged + live)
**Reviewer:** Arena main agent — I verify everything on GitHub after you push. No "done" claims in chat until code is on a branch.

## Context (verified by reviewer)
- Round 1-3 fixes all merged (`e56cd33`) and LIVE (I verified: UTC candleTime, OTC fillStatus, NO_TRADE grade N/A, AI_SKIPPED on D2, rolling winRate, OTC auto-resolve).
- **`r71_tests.mjs` still reports 113 PASS / 3 FAIL (#1a, #2, #17).** These are NOT product bugs — they are frozen-baseline artifacts: the suite compares the current engine byte-for-byte against `git archive 71e87eb` (a stale pre-round-1 engine). Every approved change since 71e87eb (D2 blocks, AI rescue, fillStatus, /12, grade cap, round-1/2/3 fixes) intentionally changes output → mismatch. **Your job is F3-20: restore this regression guard on a KNOWN-GOOD baseline.**

## F3-20 — r71 baseline refresh (the ONLY worker task this round)

1. **Reproduce:** run `node scripts/r71_tests.mjs` on main `e56cd33` → confirm 113P/3F (#1a/#2/#17).
2. **Refresh the baseline:** the test's `verify/baseline/` tree is regenerated from `git archive 71e87eb src`. Update the reference commit to **`e56cd33` (current main tip)** so the byte-equality contract compares against the CURRENT approved engine, not the pre-round-1 one.
   - Careful: the baseline src tree is gitignored + regenerated (script line ~64). Changing the commit constant + any hardcoded expectations is the actual change.
3. **Audit EVERY remaining divergence once** — after the baseline moves to e56cd33, #1a/#17 should be byte-equal again by construction IF the comparison redaction lists are still correct. Verify the redaction lists (#14a stripRound2Changed etc.) still match what the engine emits; do NOT silently delete redactions to force green — every redacted field must map to an intentional, reviewer-approved change (FIX-A/B/C/D, F3-04 etc.).
4. **#2 comparability:** update the expectation to the CURRENT AI-layer behavior (`AI_AFFECTED` vs old `COMPARABLE_PRE_AI`) with a comment explaining the AI layer changed post-71e87eb. Do not weaken the assertion — the point is the test must now guard the CURRENT contract.
5. **Tests after:** `r71_tests` must go **113P/3F → 116P/0F** (or the new correct count) with every remaining check meaningful. All other suites stay green: `fix_tests` 151/151, `phase10_integration` 19/19, `phase7_*`, `d2_tests` 39/39, `probe_tests` 34/34, `entry_hit_tests` 7/7, `fx_mode_tests` 20/20.
6. **Do NOT touch anything in `src/`** — this PR is test-infrastructure only. If you believe a src change is needed, flag it in the PR body for reviewer decision; do not bundle it.

## Workflow
- PR-first off `main` (`e56cd33`), never push main directly.
- PR body: what changed in the test, the before/after test matrix, and the divergence audit table (each previously-failing check → why it failed pre-refresh → status post-refresh).
- After you push: I re-run every suite myself + confirm the 3 old fails are now real checks.

## Out of scope
- No engine/behavior changes (Phase F is collecting; no inversion, no pair blocks, no real-money recs).
- entryHit (BUG-023) and forex-SELL (BUG-024) remain analysis-only — do not touch.
