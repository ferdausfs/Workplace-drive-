# feat(guardian): M3 — settings UI (Guardian AI screen)

**Repo:** `ferdausfs/DOK-ai` · **Base:** `main` (`26694f6`) · **Branch:** `feat/guardian-m3-settings-ui`

## What this is
M2-র service hook-এর configuration-এর জন্য **GUI**। Curbox-এর reducer pattern-এ
`Guardian AI` card + full settings screen।

## Files (8, +736)
1. **`ui/.../guardian/GuardianFragment.kt`** (new) — settings screen:
   - enable toggle (NSFW content blocking)
   - gender select (None/Male/Female)
   - ৩টা threshold slider (AI / NSFW gate / gender) + grid-vote slider
   - NSFW keyword list (add/remove; `regex:` prefix → regex rule)
   - ৩টা TFLite model import (SAF file picker → `GuardianModelImportManager`)
2. **`res/layout/fragment_guardian.xml`** + **`item_guardian_keyword.xml`** (new)
3. **`res/layout/fragment_reducers.xml`** — নতুন `card_guardian` (blockertools section-এ)
4. **`ReducersFragment.kt`** — card → `GuardianFragment` navigation
5. **`FragmentActivity.kt`** — `guardian` fragment registration
6. **`res/values/strings.xml`** — 20 string resources
7. **`GuardianBlocker.kt`** — `companion.refresh(context)` broadcast helper (+11)

## Pattern adherence
- curbox-এর existing reducer/card/fragment style follow করা হয়েছে (MaterialCardView,
  MaterialSwitch, MaterialSlider, back-button, strings.xml)
- No Compose / Navigation component (agents.md invariant)
- Config SharedPreferences-এ — service live-reload করে broadcast-এর মাধ্যমে

## Verification (honest)
- Kotlin brace/paren balance ✅ (৪ file)
- XML well-formedness ✅ (৪ file, minidom parse)
- ⚠️ **Compile = CI** — merge-এর পর build workflow auto-run। Slider import / string
  reference-এ কোনো issue হলে CI error দেবে, আমি ঠিক করবো।

## Not in this PR
- M4: AI-block overlay (go-home+toast বদলে proper block screen) + activity log
- M5: device test + false-block/miss tuning

## Deploy
Merge → CI build → install → **Reducers → Guardian AI** screen থেকে models import +
enable → service scan শুরু।
