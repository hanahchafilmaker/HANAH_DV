from ttkbootstrap import Style

def init_style():
    style = Style(theme="flatly")

    # global UI tuning
    style.configure("Treeview", rowheight=28)
    style.configure("TButton", padding=6)
    style.configure("TLabel", font=("Segoe UI", 10))

    return style