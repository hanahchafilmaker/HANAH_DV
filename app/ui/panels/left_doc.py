from ttkbootstrap import Frame, Text, Scrollbar

class LeftDocPanel:
    def __init__(self, parent):
        self.parent = parent
        self.text_widget = None
        self.scrollbar = None
        self._create_widgets()

    def _create_widgets(self):
        # Create a frame for the text and scrollbar
        container = Frame(self.parent)
        container.pack(fill="both", expand=True, padx=5, pady=5)

        # Text widget for displaying footnotes (read-only)
        self.text_widget = Text(container, wrap="word", width=40, height=20)
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
            self.text_widget.insert("end", f"[{fn['fn_id']}] {fn['fn_text']}\n\n")
        self.text_widget.configure(state="disabled")