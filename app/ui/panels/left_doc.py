from ttkbootstrap import Frame, Label, Text, Scrollbar

class LeftDocPanel(Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.parent = parent
        self.text_widget = None
        self.scrollbar = None
        self.selected_fn_id = None
        self._create_widgets()

    def _create_widgets(self):
        # Header
        header_label = Label(self, text="문서 컨텍스트", font=("Segoe UI", 10, "bold"))
        header_label.pack(anchor="w", pady=(0, 5))

        # Create a frame for the text and scrollbar
        container = Frame(self)
        container.pack(fill="both", expand=True)

        # Text widget for displaying footnotes (read-only)
        self.text_widget = Text(container, wrap="word", width=40, font=("Consolas", 9))
        self.text_widget.pack(side="left", fill="both", expand=True)

        # Scrollbar
        self.scrollbar = Scrollbar(container, orient="vertical", command=self.text_widget.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.text_widget.configure(yscrollcommand=self.scrollbar.set)

        # Make text widget read-only
        self.text_widget.configure(state="disabled")

    def update_content(self, footnotes):
        """Update the left panel with the list of footnotes"""
        self.text_widget.configure(state="normal")
        self.text_widget.delete("1.0", "end")

        for fn in footnotes:
            fn_id = fn.get('fn_id', '')
            fn_text = fn.get('fn_text', '')
            # Truncate long footnotes for density
            display_text = fn_text[:100] + "..." if len(fn_text) > 100 else fn_text
            self.text_widget.insert("end", f"[{fn_id}] {display_text}\n\n",
                                  ("selected" if str(fn_id) == str(self.selected_fn_id) else ""))

        # Configure tag for selected item
        self.text_widget.tag_configure("selected", background="#e6f3ff", font=("Consolas", 9, "bold"))

        self.text_widget.configure(state="disabled")

    def set_selected_fn_id(self, fn_id):
        """Set the selected footnote ID for highlighting"""
        self.selected_fn_id = fn_id
        # Refresh content to show selection
        if hasattr(self, '_last_footnotes'):
            self.update_content(self._last_footnotes)

    def update_footnotes_with_selection(self, footnotes):
        """Update footnotes and remember for selection highlighting"""
        self._last_footnotes = footnotes
        self.update_content(footnotes)