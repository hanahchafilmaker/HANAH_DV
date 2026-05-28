from ttkbootstrap import Label

class StatusBar(Label):
    def __init__(self, parent):
        super().__init__(parent, text="Ready", anchor="w", bootstyle="inverse-secondary")
        self.pack(fill="x", side="bottom", padx=5, pady=2)

    def set_status(self, text, level="info"):
        """Set status bar text and style"""
        # level can be info, success, warning, danger
        bootstyle = f"inverse-{level}"
        self.config(text=text, bootstyle=bootstyle)