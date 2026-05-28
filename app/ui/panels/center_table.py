from ttkbootstrap import Frame, Label

class CenterTablePanel(Frame):
    def __init__(self, parent, controller, state, right_panel, set_status):
        super().__init__(parent, padding=5)
        self.controller = controller
        self.state = state
        self.right_panel = right_panel
        self.set_status = set_status

        # Selected footnote ID for highlighting
        self.selected_fn_id = None

        # Container for scrollable content
        self.container = Frame(self)
        self.container.pack(fill="both", expand=True)

        # Header
        self.create_header()

        # Scrollable frame for rows
        self.rows_frame = Frame(self.container)
        self.rows_frame.pack(fill="both", expand=True, pady=(5, 0))

        # Bind selection event from state
        self.state.trace_add("selected_fn_id", self.on_state_selection_change)

    def create_header(self):
        """Create table header"""
        header_frame = Frame(self.container, bootstyle="secondary")
        header_frame.pack(fill="x", pady=(0, 2))

        # Configure column widths (approximate)
        id_label = Label(header_frame, text="ID", width=8, anchor="w", font=("Segoe UI", 9, "bold"))
        id_label.pack(side="left", padx=(5, 2))

        text_label = Label(header_frame, text="원문", width=40, anchor="w", font=("Segoe UI", 9, "bold"))
        text_label.pack(side="left", padx=2)

        status_label = Label(header_frame, text="상태", width=10, anchor="w", font=("Segoe UI", 9, "bold"))
        status_label.pack(side="left", padx=2)

        ref_label = Label(header_frame, text="참고문헌", width=40, anchor="w", font=("Segoe UI", 9, "bold"))
        ref_label.pack(side="left", padx=2, fill="x", expand=True)

    def load_data(self, footnotes):
        """Load footnotes into the table"""
        # Clear existing rows
        for widget in self.rows_frame.winfo_children():
            widget.destroy()

        # Add each footnote as a row
        for fn in footnotes:
            self.create_row(fn)

        # Update state with footnotes for left panel
        if hasattr(self.state, 'update_footnotes_for_left_panel'):
            self.state.update_footnotes_for_left_panel(footnotes)

    def create_row(self, fn):
        """Create a single row for a footnote"""
        fn_id = str(fn.get('fn_id', ''))
        fn_text = str(fn.get('fn_text', ''))[:50]  # Truncate for density

        # Determine row style
        is_selected = (fn_id == str(self.selected_fn_id))
        bootstyle = "success" if is_selected else "light"

        # Create row frame
        row_frame = Frame(self.rows_frame, bootstyle=bootstyle, relief="solid", borderwidth=1)
        row_frame.pack(fill="x", pady=1, padx=1)

        # Add hover effects
        row_frame.bind("<Enter>", lambda e, frame=row_frame: self.on_row_enter(frame, is_selected))
        row_frame.bind("<Leave>", lambda e, frame=row_frame, style=bootstyle: self.on_row_leave(frame, style))
        row_frame.bind("<Button-1>", lambda e, fid=fn_id: self.on_row_click(fid))

        # ID column
        id_label = Label(row_frame, text=fn_id, width=8, anchor="w")
        id_label.pack(side="left", padx=(5, 2))

        # Text column (truncated)
        text_label = Label(row_frame, text=fn_text, width=40, anchor="w")
        text_label.pack(side="left", padx=2)

        # Status column
        status_text = self.get_status_text(fn_id)
        status_label = Label(row_frame, text=status_text, width=10, anchor="w")
        status_label.pack(side="left", padx=2)

        # Reference column (truncated)
        ref_text = self.get_reference_text(fn_id)
        ref_label = Label(row_frame, text=ref_text, width=40, anchor="w")
        ref_label.pack(side="left", padx=2, fill="x", expand=True)

        # Store reference to update later if needed
        row_frame.fn_id = fn_id

    def get_status_text(self, fn_id):
        """Get status text for a footnote"""
        # Check if we have a match result
        match_result = self.state.match_results.get(fn_id)
        if not match_result:
            return "⏳"

        # Check if it's a MatchResult object or dict
        if hasattr(match_result, 'best_match'):
            if match_result.best_match is not None:
                return "✅"
            else:
                return "❓"
        elif isinstance(match_result, dict):
            if match_result.get('matched_ref'):
                return "✅"
            else:
                return "❓"
        else:
            return "❓"

    def get_reference_text(self, fn_id):
        """Get reference text for a footnote (truncated)"""
        match_result = self.state.match_results.get(fn_id)
        if not match_result:
            return ""

        # Get the matched reference
        matched_ref = ""
        if hasattr(match_result, 'best_match') and match_result.best_match:
            matched_ref = match_result.best_match.matched_ref
        elif isinstance(match_result, dict) and match_result.get('matched_ref'):
            matched_ref = match_result['matched_ref']

        # Truncate for density
        if len(matched_ref) > 50:
            return matched_ref[:50] + "..."
        return matched_ref

    def on_row_enter(self, row_frame, was_selected):
        """Handle mouse enter on row"""
        if not was_selected:  # Only change style if not already selected
            row_frame.configure(bootstyle="info")

    def on_row_leave(self, row_frame, original_style):
        """Handle mouse leave on row"""
        row_frame.configure(bootstyle=original_style)

    def on_row_click(self, fn_id):
        """Handle row click"""
        self.controller.select_footnote(fn_id)

    def on_state_selection_change(self, *args):
        """Handle selection change from state (e.g., from left panel)"""
        # This would be called when state.selected_fn_id changes
        # For now, we'll refresh the whole table to update selection highlights
        # In a more optimized version, we'd just update the specific row
        if hasattr(self.state, 'footnotes'):
            self.load_data(self.state.footnotes)