from ttkbootstrap import Frame, Label, Button

class CandidateCard(Frame):
    def __init__(self, parent, data, on_select):
        # We call the parent's __init__ with bootstyle="light" for the card look
        super().__init__(parent, bootstyle="light")

        self.data = data
        self.on_select = on_select

        # Title of the candidate (e.g., the matched reference or a preview)
        self.label = Label(self, text=data["title"], wraplength=350)
        self.label.pack(anchor="w", padx=5, pady=(5,0))

        # Confidence label
        self.conf = Label(self, text=f"{data['confidence']*100:.1f}%")
        self.conf.pack(anchor="w", padx=5)

        # Select button
        btn = Button(self, text="Select", command=self.select, bootstyle="success")
        btn.pack(anchor="e", padx=5, pady=5)

        # Hover effect to give a Zotero-like feel
        self.bind("<Enter>", lambda e: self.config(bootstyle="info"))
        self.bind("<Leave>", lambda e: self.config(bootstyle="light"))

    def select(self):
        # When the card is selected, call the on_select callback with the candidate data
        self.on_select(self.data)