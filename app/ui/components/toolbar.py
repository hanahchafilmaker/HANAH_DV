from ttkbootstrap import Frame, Button, Label
from tkinter import filedialog, messagebox
import os

class Toolbar(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # File operations
        Button(self, text="파일 열기", command=self.open_file, bootstyle="outline").pack(side="left", padx=2, pady=2)
        Button(self, text="CSV 저장", command=self.save_csv, bootstyle="outline").pack(side="left", padx=2, pady=2)
        Button(self, text="BibTeX 내보내기", command=self.export_bibtex, bootstyle="outline").pack(side="left", padx=2, pady=2)

        # Processing
        Button(self, text="일괄 매칭", command=self.process_all, bootstyle="success").pack(side="left", padx=2, pady=2)

        # Separator
        Frame(self, width=2, bootstyle="secondary").pack(side="left", fill="y", padx=5, pady=2)

        # Search (placeholder)
        Button(self, text="검색", command=self.search, bootstyle="outline").pack(side="left", padx=2, pady=2)

        # Selected footnote indicator
        self.selected_label = Label(self, text="", font=("Segoe UI", 9))
        self.selected_label.pack(side="right", padx=10)

        # Status label for transient messages (optional, we can use bottom bar for now)
        # self.status_label = Label(self, text="", font=("Segoe UI", 9))
        # self.status_label.pack(side="right", padx=10)

    def open_file(self):
        """Open a DOCX file"""
        file_path = filedialog.askopenfilename(
            title="DOCX 파일 선택",
            filetypes=[("Word files", "*.docx"), ("All files", "*.*")]
        )
        if file_path:
            self.controller.load_doc(file_path)
            self.selected_label.config(text="")  # Clear selection when new file loaded

    def save_csv(self):
        """Save current state to CSV"""
        file_path = filedialog.asksaveasfilename(
            title="CSV 저장",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="각주_매칭결과.csv"
        )
        if file_path:
            self.controller.save_csv(file_path)

    def export_bibtex(self):
        """Export bibliography to BibTeX"""
        file_path = filedialog.asksaveasfilename(
            title="BibTeX 내보내기",
            defaultextension=".bib",
            filetypes=[("BibTeX files", "*.bib")],
            initialfile="참고문헌.bib"
        )
        if file_path:
            self.controller.export_bibtex(file_path)

    def process_all(self):
        """Process all footnotes for matching"""
        # This would iterate through all footnotes and run matching
        # For now, we'll just show a message
        messagebox.showinfo("일괄 매칭", "모든 각주에 대한 매칭을 시작합니다.")
        # self.controller.process_all()  # Would call the actual method

    def search(self):
        """Search functionality (placeholder)"""
        messagebox.showinfo("검색", "검색 기능은 준비 중입니다.")

    def set_selected_footnote(self, fn_id):
        """Set the selected footnote ID in the toolbar"""
        if fn_id:
            self.selected_label.config(text=f"Fn: {fn_id}")
        else:
            self.selected_label.config(text="")