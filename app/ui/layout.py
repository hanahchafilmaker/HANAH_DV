from ttkbootstrap import Frame, Label

# Import components
from app.ui.components.toolbar import Toolbar
from app.ui.components.statusbar import StatusBar
from app.ui.panels.left_doc import LeftDocPanel
from app.ui.panels.center_table import CenterTablePanel
from app.ui.panels.right_editor import RightEditorPanel

class MainLayout(Frame):
    def __init__(self, root, controller, state):
        super().__init__(root)
        self.root = root
        self.controller = controller
        self.state = state

        self.root.title("Paper Citation Studio")
        self.root.geometry("1400x800")

        # Create UI components
        self.create_toolbar()
        self.create_panes()
        self.create_statusbar()

        # BIND KEYBOARD SHORTCUTS
        self.bind_shortcuts()

    def create_toolbar(self):
        self.toolbar = Toolbar(self, self.controller)
        self.toolbar.pack(fill="x", side="top", padx=5, pady=2)

    def create_panes(self):
        # MAIN PANED WINDOW (3 PANES)
        self.paned = Frame(self)
        self.paned.pack(fill="both", expand=True, padx=5, pady=2)

        # LEFT PANE (Document Context)
        self.left = Frame(self.paned)
        # CENTER PANE (Footnote Grid)
        self.center = Frame(self.paned)
        # RIGHT PANE (Detail Editor)
        self.right = Frame(self.paned)

        self.paned.add(self.left, weight=1)
        self.paned.add(self.center, weight=2)
        self.paned.add(self.right, weight=3)

        # LOAD PANELS
        self.left_panel = LeftDocPanel(self.left)
        self.center_panel = CenterTablePanel(self.center, controller, state, self.right_panel, self.set_status)
        self.right_panel = RightEditorPanel(self.right, controller, state, self.set_status)

    def create_statusbar(self):
        self.statusbar = StatusBar(self)
        self.statusbar.pack(fill="x", side="bottom", padx=5, pady=2)

    def bind_shortcuts(self):
        # Navigation
        self.root.bind("<Up>", self.move_up)
        self.root.bind("<Down>", self.move_down)

        # Selection
        self.root.bind("<Return>", self.select_candidate)

        # Save
        self.root.bind("<Control-s>", self.save)

        # Focus the treeview initially so keyboard navigation works
        self.root.after(100, lambda: self.center_panel.tree.focus_set())

    def move_up(self, event):
        # Get current selection
        selected = self.center_panel.tree.selection()
        if not selected:
            # Select first item if nothing selected
            children = self.center_panel.tree.get_children()
            if children:
                self.center_panel.tree.selection_set(children[0])
                self.center_panel.tree.focus(children[0])
                self.center_panel.on_select(None)
        else:
            # Get current item and move up
            current = selected[0]
            children = self.center_panel.tree.get_children()
            try:
                current_index = children.index(current)
                if current_index > 0:
                    prev_item = children[current_index - 1]
                    self.center_panel.tree.selection_set(prev_item)
                    self.center_panel.tree.focus(prev_item)
                    self.center_panel.on_select(None)
            except ValueError:
                pass  # current not in children

        return "break"  # Prevent default behavior

    def move_down(self, event):
        # Get current selection
        selected = self.center_panel.tree.selection()
        if not selected:
            # Select first item if nothing selected
            children = self.center_panel.tree.get_children()
            if children:
                self.center_panel.tree.selection_set(children[0])
                self.center_panel.tree.focus(children[0])
                self.center_panel.on_select(None)
        else:
            # Get current item and move down
            current = selected[0]
            children = self.center_panel.tree.get_children()
            try:
                current_index = children.index(current)
                if current_index < len(children) - 1:
                    next_item = children[current_index + 1]
                    self.center_panel.tree.selection_set(next_item)
                    self.center_panel.tree.focus(next_item)
                    self.center_panel.on_select(None)
            except ValueError:
                pass  # current not in children

        return "break"  # Prevent default behavior

    def select_candidate(self, event):
        # Get current selection from center table
        selected = self.center_panel.tree.selection()
        if not selected:
            return "break"

        fn_id = selected[0]

        # Get the match result for this footnote
        result = self.state.match_results.get(fn_id)
        if not result:
            self.set_status("No candidates available", "warning")
            return "break"

        # Determine which candidate to select
        candidate_to_select = None
        if hasattr(result, 'best_match') and result.best_match is not None:
            # Use the best match if available
            candidate_to_select = result.best_match
        elif hasattr(result, 'candidates') and result.candidates:
            # Use the first candidate if no best match
            candidate_to_select = result.candidates[0]

        if candidate_to_select:
            # Select the candidate via controller
            self.controller.select_candidate(fn_id, candidate_to_select)
            self.set_status(f"Selected candidate: {candidate_to_select.matched_ref[:50]}...", "success")
        else:
            self.set_status("No candidates to select", "warning")

        return "break"

    def save(self, event):
        # Trigger apply/save action
        self.right_panel.apply()
        return "break"

    def set_status(self, text, level="info"):
        # level can be info, success, warning, danger
        bootstyle = f"inverse-{level}"
        self.statusbar.set_status(text, level)