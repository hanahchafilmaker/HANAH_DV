Thread safety fixes have been successfully applied to resolve the "invalid command name" Tkinter error.

Changes Made to main_gui.py:

1. **Data Separation**: 
   - Removed all direct widget references from footnote data (self.footnotes)
   - self.footnotes now contains only pure data (text, candidate visibility, etc.)
   - All widget references stored exclusively in self.ui_registry (mapping fn_id → widget dict)

2. **Queue-Based Dispatcher Pattern**:
   - Worker thread (_process_all_footnotes_matching) performs computations only
   - Results placed in self.ui_queue as data-only messages (fn_id, result)
   - UI thread processes queue via _ui_dispatch_loop → _handle_ui_message → _apply_auto_match_result
   - Zero direct widget access from worker thread

3. **Thread-Safe UI Updates**:
   - All UI update methods (_update_auto_match_ui_threadsafe, _update_candidate_display, etc.) now:
     - Check self.ui_alive flag (False when window closing)
     - Retrieve widgets from self.ui_registry (UI thread only)
     - Verify widget existence with winfo_exists() and tk.TclError handling
     - Perform widget operations only after safety checks

4. **Proper Resource Cleanup**:
   - _on_editor_close: 
     - Sets self.ui_alive = False
     - Cancels all pending after() callbacks (self._after_ids)
     - Clears self.ui_registry to prevent accidental accesses
     - Destroys editor window

5. **Signal-Slot Safety**:
   - All callbacks now pass fn_id only (not footnote objects)
   - Example: lambda f_id=fn['fn_id']: self._toggle_candidate_display(f_id)

Expected Behavior:
- No more "invalid command name" errors when closing footnote editor during processing
- Safe rapid open/close cycles during auto-matching
- Clean shutdown of all UI components and background threads
- All existing functionality preserved (top-3 candidates, auto-matching, bibliography generation)

Verification Steps:
1. Open a DOCX with multiple footnotes
2. Launch footnote editor
3. While "각주 처리 중..." status is showing, rapidly close/open the editor window
4. Alternatively, close editor during processing and observe no error dialogs
5. Confirm all matching, candidate selection, and bibliography features still work correctly

The thread safety architecture now follows Tkinter best practices:
- Worker thread: Computation only, no widget access
- Main thread: Exclusive widget access via queue dispatcher
- Proper lifecycle management with cleanup on window close

This resolves the core issue described in the user's error message.