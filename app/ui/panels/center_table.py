from ttkbootstrap import Treeview

class CenterTablePanel:
    def __init__(self, parent, controller, state, right_panel):
        self.controller = controller
        self.state = state
        self.right_panel = right_panel

        self.tree = Treeview(
            parent,
            columns=("id", "text", "status", "ref"),
            show="headings",
            bootstyle="primary"
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("text", text="원문")
        self.tree.heading("status", text="상태")
        self.tree.heading("ref", text="참고문헌")

        self.tree.column("id", width=60)
        self.tree.column("text", width=300)
        self.tree.column("status", width=80)
        self.tree.column("ref", width=300)

        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def load_data(self, footnotes):
        for fn in footnotes:
            # Insert the footnote into the treeview
            # We use the fn_id as the item identifier (iid)
            self.tree.insert(
                "",
                "end",
                iid=fn["fn_id"],
                values=(fn["fn_id"], fn["fn_text"], "", "")
            )

    def on_select(self, event):
        # Get the selected item
        selected = self.tree.selection()
        if not selected:
            return
        fn_id = selected[0]
        # Load the item in the right panel
        self.right_panel.load_item(fn_id)