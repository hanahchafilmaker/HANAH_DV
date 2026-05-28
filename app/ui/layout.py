from ttkbootstrap import Frame

class MainLayout:
    def __init__(self, root, controller, state):
        self.root = root
        self.controller = controller
        self.state = state

        self.root.title("논문 교정기 (Commercial UI)")
        self.root.geometry("1200x700")

        # container
        container = Frame(root)
        container.pack(fill="both", expand=True)

        # 3 PANES
        self.left = Frame(container, width=300)
        self.center = Frame(container, width=400)
        self.right = Frame(container, width=500)

        self.left.pack(side="left", fill="both", expand=True)
        self.center.pack(side="left", fill="both", expand=True)
        self.right.pack(side="left", fill="both", expand=True)

        # panels
        from app.ui.panels.left_doc import LeftDocPanel
        from app.ui.panels.center_table import CenterTablePanel
        from app.ui.panels.right_editor import RightEditorPanel

        self.left_panel = LeftDocPanel(self.left)
        self.center_panel = CenterTablePanel(self.center)
        self.right_panel = RightEditorPanel(self.right)