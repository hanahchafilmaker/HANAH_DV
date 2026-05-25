import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import footnote_manager as fm

class FootnoteEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("각주 관리자 (Footnote Manager)")
        self.geometry("900x600")
        self.docx_path = None
        self.footnotes = []  # list of dict from extract_footnotes
        self.edited_rows = []  # list of dict for editor state
        self._build_ui()

    def _build_ui(self):
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(toolbar, text="DOCX 불러오기", command=self.load_docx).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="CSV 저장", command=self.save_csv).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="참고문헌 생성", command=self.generate_bibliography).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="DOCX에 반영", command=self.update_docx).pack(side=tk.LEFT, padx=2)

        # Main pane: left original, right edited
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left frame: original footnotes (read-only)
        left_frame = ttk.LabelFrame(paned, text="원본 각주 (읽기 전용)")
        paned.add(left_frame, weight=1)
        self.left_text = tk.Text(left_frame, wrap=tk.WORD, width=40)
        self.left_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.left_text.config(state=tk.DISABLED)

        # Right frame: editable fields with checkboxes
        right_frame = ttk.LabelFrame(paned, text="참고문헌 편집")
        paned.add(right_frame, weight=2)

        # Use a canvas with scrollbar for many footnotes
        self.canvas = tk.Canvas(right_frame)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Status bar
        self.status_var = tk.StringVar(value="준비")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, ipady=2)

    def load_docx(self):
        path = filedialog.askopenfilename(
            title="Word 문서 선택",
            filetypes=[("Word files", "*.docx"), ("All files", "*.*")]
        )
        if not path:
            return
        self.docx_path = path
        try:
            self.footnotes = fm.extract_footnotes(path)
            if not self.footnotes:
                messagebox.showinfo("알림", "문서에서 각주를 찾을 수 없습니다.")
                self.status_var.set("각주 없음")
                return
            self._populate_editor()
            self.status_var.set(f"{len(self.footnotes)}개 각주 로드됨")
        except Exception as e:
            messagebox.showerror("오류", f"각주 추출 실패:\n{e}")
            self.status_var.set("오류 발생")

    def _populate_editor(self):
        # Clear previous widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.edited_rows = []
        # Header
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(header_frame, text="#", width=4).pack(side=tk.LEFT)
        ttk.Label(header_frame, text="원본 각주", width=30).pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="참고문헌 (편집 가능)", width=40).pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="매칭", width=8).pack(side=tk.LEFT)

        # For each footnote, create a row
        for i, fn in enumerate(self.footnotes, start=1):
            row_frame = ttk.Frame(self.scrollable_frame)
            row_frame.pack(fill=tk.X, padx=5, pady=2)
            # Index
            ttk.Label(row_frame, text=str(i), width=4, anchor=tk.CENTER).pack(side=tk.LEFT)
            # Original (read-only text)
            orig_text = tk.Text(row_frame, height=3, width=30, wrap=tk.WORD)
            orig_text.insert(tk.END, fn['fn_text'])
            orig_text.config(state=tk.DISABLED, background=self.cget('bg'))
            orig_text.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=False)
            # Edited reference (editable)
            ref_text = tk.Text(row_frame, height=3, width=40, wrap=tk.WORD)
            ref_text.insert(tk.END, fn['fn_text'])  # start with original as placeholder
            ref_text.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=False)
            # Checkbox for matched
            matched_var = tk.BooleanVar(value=False)
            chk = ttk.Checkbutton(row_frame, variable=matched_var)
            chk.pack(side=tk.LEFT, padx=5)
            # Store references for later retrieval
            self.edited_rows.append({
                'index': i,
                'fn_id': fn['fn_id'],
                'orig_widget': orig_text,
                'ref_widget': ref_text,
                'matched_var': matched_var,
                'fn_text': fn['fn_text']
            })

    def save_csv(self):
        if not self.edited_rows:
            messagebox.showwarning("경고", "먼저 DOCX를 불러오세요.")
            return
        # Build data for CSV
        rows = []
        for er in self.edited_rows:
            matched = er['matched_var'].get()
            status = "✅ 매칭" if matched else ""
            rows.append({
                'fn_num': er['index'],
                'fn_type': '',  # leave blank; user can fill later if needed
                'status': status,
                'fn_text': er['fn_text'],
                'matched_ref': er['ref_widget'].get("1.0", tk.END).strip()
            })
        # Ask where to save
        save_path = filedialog.asksaveasfilename(
            title="CSV 저장",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="각주_참고문헌_매칭표.csv"
        )
        if not save_path:
            return
        try:
            fieldnames = ['fn_num', 'fn_type', 'status', 'fn_text', 'matched_ref']
            with open(save_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            messagebox.showinfo("완료", f"CSV 저장 완료:\n{save_path}")
            self.status_var.set(f"CSV 저장: {os.path.basename(save_path)}")
        except Exception as e:
            messagebox.showerror("오류", f"CSV 저장 실패:\n{e}")

    def generate_bibliography(self):
        if not self.edited_rows:
            messagebox.showwarning("경고", "먼저 DOCX를 불러오세요.")
            return
        # Temporarily save CSV to a temp file and use footnote_manager to generate bibliography
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as tmp:
            tmp_path = tmp.name
            fieldnames = ['fn_num', 'fn_type', 'status', 'fn_text', 'matched_ref']
            writer = csv.DictWriter(tmp, fieldnames=fieldnames)
            writer.writeheader()
            for er in self.edited_rows:
                matched = er['matched_var'].get()
                status = "✅ 매칭" if matched else ""
                writer.writerow({
                    'fn_num': er['index'],
                    'fn_type': '',
                    'status': status,
                    'fn_text': er['fn_text'],
                    'matched_ref': er['ref_widget'].get("1.0", tk.END).strip()
                })
        try:
            bibliography = fm.generate_bibliography_from_edited(tmp_path)
            os.unlink(tmp_path)
            if not bibliography:
                messagebox.showinfo("알림", "매칭된 각주가 없어 참고문헌을 생성할 수 없습니다.")
                return
            # Show bibliography in a popup
            bib_window = tk.Toplevel(self)
            bib_window.title("생성된 참고문헌")
            bib_window.geometry("500x400")
            txt = tk.Text(bib_window, wrap=tk.WORD)
            txt.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            for i, ref in enumerate(bibliography, start=1):
                txt.insert(tk.END, f"{i}. {ref}\n\n")
            txt.config(state=tk.DISABLED)
            ttk.Button(bib_window, text="닫기", command=bib_window.destroy).pack(pady=5)
            self.status_var.set(f"참고문헌 {len(bibliography)}건 생성")
        except Exception as e:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            messagebox.showerror("오류", f"참고문헌 생성 실패:\n{e}")

    def update_docx(self):
        if not self.docx_path:
            messagebox.showwarning("경고", "먼저 DOCX를 불러오세요.")
            return
        # Generate bibliography from current edits
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as tmp:
            tmp_path = tmp.name
            fieldnames = ['fn_num', 'fn_type', 'status', 'fn_text', 'matched_ref']
            writer = csv.DictWriter(tmp, fieldnames=fieldnames)
            writer.writeheader()
            for er in self.edited_rows:
                matched = er['matched_var'].get()
                status = "✅ 매칭" if matched else ""
                writer.writerow({
                    'fn_num': er['index'],
                    'fn_type': '',
                    'status': status,
                    'fn_text': er['fn_text'],
                    'matched_ref': er['ref_widget'].get("1.0", tk.END).strip()
                })
        try:
            bibliography = fm.generate_bibliography_from_edited(tmp_path)
            os.unlink(tmp_path)
            if not bibliography:
                messagebox.showinfo("알림", "매칭된 각주가 없어 참고문헌을 생성할 수 없습니다.")
                return
            # Ask for output docx path
            save_path = filedialog.asksaveasfilename(
                title="참고문헌이 포함된 문서 저장",
                defaultextension=".docx",
                filetypes=[("Word files", "*.docx")],
                initialfile="최종_논문.docx"
            )
            if not save_path:
                return
            fm.update_docx_with_bibliography(self.docx_path, bibliography, save_path)
            messagebox.showinfo("완료", f"문서 저장 완료:\n{save_path}")
            self.status_var.set(f"DOCX 업데이트: {os.path.basename(save_path)}")
        except Exception as e:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            messagebox.showerror("오류", f"DOCX 업데이트 실패:\n{e}")

if __name__ == "__main__":
    app = FootnoteEditor()
    app.mainloop()