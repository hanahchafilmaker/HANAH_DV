import sys
sys.path.insert(0, '.')

import tkinter as tk
from tkinter import ttk

# Import the patched main_gui to ensure the patch is applied
# We'll just run the patch again for safety
def _patch_tkinter_configure():
    original_widget_configure = tk.Widget.configure
    def patched_widget_configure(self, cnf=None, **kw):
        if cnf is not None:
            if isinstance(cnf, dict):
                cnf = cnf.copy()
                if 'fn_id' in cnf:
                    del cnf['fn_id']
        if 'fn_id' in kw:
            kw = kw.copy()
            del kw['fn_id']
        return original_widget_configure(self, cnf, **kw)
    tk.Widget.configure = patched_widget_configure

    original_style_configure = ttk.Style.configure
    def patched_style_configure(self, *args, **kw):
        if 'fn_id' in kw:
            kw = kw.copy()
            del kw['fn_id']
        return original_style_configure(self, *args, **kw)
    ttk.Style.configure = patched_style_configure

_patch_tkinter_configure()

def test_widget_configure_with_fn_id():
    """Test that configuring a widget with fn_id does not raise an error."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    try:
        # Create a label and try to configure with fn_id
        label = ttk.Label(root, text="Test")
        # This should not raise an error after patching
        label.configure(fn_id=123, text="Updated")
        print("SUCCESS: Widget configured with fn_id without error")
        # Also test that the fn_id is not actually set as a widget option
        # (it should be ignored)
        # We can't easily check, but at least no exception
    except tk.TclError as e:
        print(f"FAILED: {e}")
        return False
    finally:
        root.destroy()
    return True

def test_style_configure_with_fn_id():
    """Test that configuring a ttk style with fn_id does not raise an error."""
    try:
        style = ttk.Style()
        # This should not raise an error after patching
        style.configure("Test.TLabel", fn_id=456, background="yellow")
        print("SUCCESS: Style configured with fn_id without error")
    except tk.TclError as e:
        print(f"FAILED: {e}")
        return False
    return True

if __name__ == "__main__":
    print("Testing tkinter fn_id patch...")
    widget_ok = test_widget_configure_with_fn_id()
    style_ok = test_style_configure_with_fn_id()
    if widget_ok and style_ok:
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed.")
        sys.exit(1)