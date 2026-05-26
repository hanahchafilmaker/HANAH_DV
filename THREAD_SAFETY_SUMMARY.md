# Thread Safety Fixes Applied

## Summary of Changes to main_gui.py

1. **Removed direct widget references from footnote data**:
   - Previously, `fn['conf_label']`, `fn['doi_label']`, etc., were stored in the footnote dictionary.
   - Now, all widget references are stored exclusively in `self.ui_registry` (a dictionary mapping `fn_id` to widget references).
   - The footnote data (`self.footnotes`) now contains only pure data (text, candidate visibility boolean, etc.).

2. **Implemented queue-based dispatcher pattern**:
   - Worker thread (`_process_all_footnotes_matching`) performs auto-matching and puts results into `self.ui_queue`.
   - UI thread runs `_ui_dispatch_loop` (scheduled via `root.after`) which processes messages from the queue.
   - All UI updates occur only in the main thread via `_handle_ui_message` → `_apply_auto_match_result` → `_update_auto_match_ui_threadsafe`.

3. **Thread-safe UI updates**:
   - `_update_auto_match_ui_threadsafe`, `_update_candidate_display`, `_select_candidate`, `_update_ui_after_candidate_selection`, `_apply_match` all:
     - Check `self.ui_alive` flag (set to False on window close).
     - Retrieve widget references from `self.ui_registry` (UI thread only).
     - Verify widget existence using `winfo_exists()` and catch `tk.TclError`.
     - Perform widget operations (config, delete, insert, etc.) only after these checks.

4. **Proper cleanup on window close**:
   - `_on_editor_close` sets `self.ui_alive = False`.
   - Cancels all pending `after()` callbacks stored in `self._after_ids`.
   - Clears `self.ui_registry` to prevent accidental accesses.
   - Destroys the editor window.

5. **Signal-slot connections use fn_id only**:
   - Buttons and callbacks now pass `fn_id` instead of footnote objects.
   - Example: `candidate_btn.configure(command=lambda f_id=fn['fn_id']: self._toggle_candidate_display(f_id))`.

## Result

- Eliminates "invalid command name" errors caused by background threads accessing destroyed Tkinter widgets.
- Ensures all Tkinter widget access occurs exclusively on the main thread.
- Provides clean shutdown of UI components when the footnote editor is closed.
- Maintains existing functionality: top-3 candidate display, auto-matching, bibliography generation, etc.

## Files Modified

- `main_gui.py`: Applied all thread safety fixes as described above.

## Testing Note

To verify the fix, open a DOCX with footnotes, launch the footnote editor, and close the window while processing is occurring (or rapidly open/close). The application should no longer crash with "invalid command name" errors.
