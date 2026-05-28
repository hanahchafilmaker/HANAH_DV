from ttkbootstrap import Frame

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

        # Track last scroll fractions to avoid loops
        self._last_left_fraction = None
        self._last_center_fraction = None

        self.create_toolbar()
        self.create_panes()
        self.create_statusbar()

        self.bind_shortcuts()

    # -------------------------
    # TOOLBAR
    # -------------------------
    def create_toolbar(self):
        self.toolbar = Toolbar(self, self.controller)
        self.toolbar.pack(fill="x", side="top")

    # -------------------------
    # PANES (CRITICAL FIX HERE)
    # -------------------------
    def create_panes(self):

        container = Frame(self)
        container.pack(fill="both", expand=True)

        # LEFT / CENTER / RIGHT containers
        self.left = Frame(container)
        self.center = Frame(container)
        self.right = Frame(container)

        self.left.pack(side="left", fill="both", expand=True)
        self.center.pack(side="left", fill="both", expand=True)
        self.right.pack(side="left", fill="both", expand=True)

        # -------------------------
        # IMPORTANT FIX:
        # create panels in safe order
        # -------------------------

        self.left_panel = LeftDocPanel(self.left, self.controller, self.state)
        # Set sync callback for left panel
        self.left_panel.set_sync_callback(self._on_left_scroll)

        self.right_panel = RightEditorPanel(
            self.right,
            self.controller,
            self.state,
            self.set_status
        )

        self.center_panel = CenterTablePanel(
            self.center,
            self.controller,
            self.state,
            self.right_panel,
            self.set_status
        )
        # Set back-references so controller can update panels directly
        self.controller.left_panel = self.left_panel
        self.controller.right_panel = self.right_panel
        self.controller.center_panel = self.center_panel
        # Set up toolbar reference (will be set after toolbar creation)
        # Set sync callbacks for scroll synchronization
        self.left_panel.set_sync_callback(self._on_left_scroll)
        self.center_panel.set_sync_callback(self._on_center_scroll)

    def _on_left_scroll(self, source, fraction):
        """Handle scroll event from left panel"""
        # Avoid loops
        if self._last_left_fraction == fraction:
            return
        self._last_left_fraction = fraction
        # Update center panel
        self.center_panel.scroll_to_position(fraction)
        self._last_center_fraction = fraction

    def _on_center_scroll(self, source, fraction):
        """Handle scroll event from center panel"""
        # Avoid loops
        if self._last_center_fraction == fraction:
            return
        self._last_center_fraction = fraction
        # Update left panel
        self.left_panel.scroll_to_position(fraction)
        self._last_left_fraction = fraction

    # -------------------------
    # STATUS BAR
    # -------------------------
    def create_statusbar(self):
        self.statusbar = StatusBar(self)
        self.statusbar.pack(fill="x", side="bottom")

    # -------------------------
    # STATUS UPDATE
    # -------------------------
    def set_status(self, text, level="info"):
        self.statusbar.set_status(text, level)

    # -------------------------
    # SHORTCUTS
    # -------------------------
    def bind_shortcuts(self):
        self.root.bind("<Up>", lambda e: self.center_panel.move_up())
        self.root.bind("<Down>", lambda e: self.center_panel.move_down())
        self.root.bind("<Return>", lambda e: self.center_panel.select_best())
        self.root.bind("<Control-s>", lambda e: self.right_panel.apply())