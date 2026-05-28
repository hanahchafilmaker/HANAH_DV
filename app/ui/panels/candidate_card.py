from ttkbootstrap import Frame, Label, Button

class CandidateCard(Frame):
    def __init__(self, parent, data, on_select, selected=False):
        super().__init__(parent, bootstyle="light")

        self.data = data
        self.on_select = on_select
        self.selected = selected

        self.label = Label(self, text=data["title"], wraplength=350)
        self.label.pack(anchor="w", padx=5, pady=(5,0))

        self.conf = Label(self, text=f"{data['confidence']*100:.1f}%")
        self.conf.pack(anchor="w", padx=5)

        btn = Button(self, text="Select", command=self.select, bootstyle="success")
        btn.pack(anchor="e", padx=5, pady=5)

        # Apply initial styles based on selected state
        self.apply_styles()

        # Hover effects (only when not selected)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def apply_styles(self):
        if self.selected:
            self.configure(bootstyle="success")
        else:
            self.configure(bootstyle="light")

    def on_enter(self, event):
        if not self.selected:
            self.configure(bootstyle="info")

    def on_leave(self, event):
        if not self.selected:
            self.configure(bootstyle="light")

    def set_selected(self, selected):
        self.selected = selected
        self.apply_styles()

    def select(self):
        self.set_selected(True)
        self.on_select(self.data)