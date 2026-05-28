from ttkbootstrap import Window

from app.state.app_state import AppState
from app.controllers.editor_controller import EditorController
from app.ui.layout import MainLayout

def main():
    root = Window(themename="flatly")

    state = AppState()
    controller = EditorController(state)

    app = MainLayout(root, controller, state)

    root.mainloop()

if __name__ == "__main__":
    main()