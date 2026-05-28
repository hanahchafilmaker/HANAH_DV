from ttkbootstrap import Frame, Entry, Button

class SearchBar(Frame):
    def __init__(self, parent, on_search):
        super().__init__(parent)
        self.on_search = on_search

        # Search entry
        self.entry = Entry(self, width=30)
        self.entry.pack(side="left", padx=(0, 5), fill="x", expand=True)
        self.entry.bind("<Return>", self.on_enter_key)

        # Search button
        self.button = Button(self, text="검색", command=self.on_search_click, bootstyle="outline")
        self.button.pack(side="left")

    def on_enter_key(self, event):
        """Handle Enter key press"""
        query = self.entry.get().strip()
        if query:
            self.on_search(query)

    def on_search_click(self):
        """Handle search button click"""
        query = self.entry.get().strip()
        if query:
            self.on_search(query)

    def get_query(self):
        """Get current search query"""
        return self.entry.get().strip()

    def clear(self):
        """Clear search entry"""
        self.entry.delete(0, 'end')