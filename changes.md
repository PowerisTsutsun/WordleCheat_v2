# Changes Log (by Chun)

Dumping the changes I made so far.

## requirements.txt
fixed invalid requirements — removed built-in modules that don’t belong in pip installs.
- Added real deps:
  - customtkinter
  - pillow
  - packaging

## solver.py
reworked the core filtering logic to respect Wordle rules more strictly, especially yellows and duplicates.
- Greens: still enforced — if we know a position (green), candidates must match there.
- Yellows: now correctly ensure the letter exists in the word but NOT at any of its forbidden indices.
- Presents: every present letter must appear somewhere.
- Grays with duplicates: only exclude words that have MORE copies of a “gray” letter than what we already know is required (from greens/yellows). This avoids falsely eliminating legit duplicate-letter words.
- Added exact_counts: when feedback shows only some instances of a guessed letter are real, I lock the exact count for that letter so candidates match the true number. Tightens suggestions on duplicates.
- Simplified “absent” rule: letters marked fully gray (no colored hits at all) are treated as truly absent and filtered out. If an exact count exists for a letter, that specific rule wins.
- API: filter_words now accepts exact_counts: Dict[str, int].

## gui.py
fixed absent-letter update in the feedback dialog. Gray letters are only added to the absent set if they aren’t green/yellow elsewhere in the same guess and not already known as present.
  - This prevents marking a letter absent when it’s actually present in another position.
- removed duplicated glass/acrylic setup from _build_layout(). Theme glass is now handled solely in apply_theme() to avoid drift and double initialization.
- avoided a duplicate bg configure — set it once in apply_theme().
- new feedback flow (no modal): press ENTER to enter feedback mode, click tiles to cycle Grey → Yellow → Green, press ENTER again (button label flips to “CONFIRM”) to apply.
- inline status: added a status label under the actions to show guidance and suggestions without popups.
- suggestions: next guess shows inline with remaining candidate count; Random also fills the row inline.
- removed Submit button — ENTER drives the flow now. While marking feedback, typing is blocked to avoid accidental edits.
- responsive board: tiles resize with the window; fonts and corner radii scale too, so it looks comfy at any size.
- theming polish: title set to “Wordle Cheat”, and status text color follows the active theme.
- keyboard UX: letters proven truly absent get disabled on the on-screen keyboard.
- hotfix: Enter now confirms while in feedback mode, and entering feedback mode defaults the row to Grey so cycling is predictable. (Chun: tiny UX papercuts, gone!)

## effects.py
- moved hwnd retrieval into a try/except after verifying we’re on Windows, so non-Windows doesn’t explode.
- fixed the pointer error you saw (“cannot be converted to pointer”) by:
  - Casting the ACCENT_POLICY pointer to c_void_p before assigning to the WCA data struct: `ctypes.cast(ctypes.byref(policy), ctypes.c_void_p)`.
  - Declaring the Win32 function prototype for SetWindowCompositionAttribute so ctypes knows the exact arg/return types. This helps avoid marshalling issues.
- Still fails gracefully — if anything goes sideways, we print a friendly message and carry on without glass.

## app.py
- uppercased the word list at load so everything downstream (UI/solver) is consistent.
- centered the window on launch; kept a sensible minimum size so it doesn’t squish. 

## utils.py
- simplified init_ctk to accept just an appearance mode and set a sane base theme (dark-blue). Palettes still define the real vibe.

## Notes I checked but didn’t change
- Title em-dash already looks clean here (UTF-8 is fine). If you prefer ASCII, swap to a hyphen.
- Resize throttling var (`self._resize_job`) is already initialized in `__init__`, so we’re good.

## Quick test suggestions
- Try toggling through themes (especially the glassy one) to confirm no pointer errors now.
- Feed in duplicate-letter words (PAPER, LEVEL, FLOOR) to see improved filtering.
- On non-Windows, glass should no-op without errors.


