import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import shutil
import engine  # reuse style functions etc.
import footnote_manager as fm
from footnote_manager import MatchResult
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
import tempfile
import csv
import threading
import queue


class ThesisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("논문 자동 생성 시스템 (각주 기반)")
        self.root.geometry("800x600")

        self.docx_path = None
        self.footnotes = []  # list of dict from extract_footnotes
        self.edited_rows = []  # parallel list of widgets/vars for editing UI
        self.auto_match_results = {}  # Store auto-match results by fn_id
        self.ui_alive = False  # Track if footnote editor window is alive
        self._after_ids = []  # Track after() callback IDs for cleanup
        self.ui_queue = queue.Queue()  # Queue for thread-safe UI updates

        # Queue-based dispatcher for thread-safe UI updates
        self.ui_queue = queue.Queue()
        self.processing_job = False

        tk.Label(root, text="Word 문서 선택 (각주 추출 및 편집)", font=("Arial", 14)).pack(pady=10)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="DOCX 파일 선택", command=self.select_file).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="각주 편집기 열기", command=self.open_footnote_editor).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="참고문헌 생성 및 최종 문서 만들기", command=self.generate_final_docx).pack(side=tk.LEFT, padx=5)

        self.status = tk.Label(root, text="", fg="blue")
        self.status.pack(pady=5)

        # Preview area (optional)
        self.preview_label = tk.Label(root, text="", justify=tk.LEFT, anchor="w")
        self.preview_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def select_file(self):
        self.docx_path = filedialog.askopenfilename(filetypes=[("Word files", "*.docx")])
        if self.docx_path:
            self.status.config(text=f"선택됨: {os.path.basename(self.docx_path)}")
            self.preview_label.config(text="각주를 추출하려면 '각주 편집기 열기'를 클릭하세요.")
        else:
            self.status.config(text="파일이 선택되지 않았습니다.")

    def open_footnote_editor(self):
        if not self.docx_path:
            messagebox.showerror("오류", "먼저 DOCX 파일을 선택하세요.")
            return
        try:
            self.footnotes = fm.extract_footnotes(self.docx_path)
            if not self.footnotes:
                messagebox.showinfo("알림", "문서에서 각주를 찾을 수 없습니다.")
                self.status.config(text="각주 없음")
                return
            self._show_footnote_editor()
            self.status.config(text=f"{len(self.footnotes)}개 각주 추출 완료. 편집 후 확인하세요.")
        except Exception as e:
            messagebox.showerror("오류", f"각주 추출 실패:\n{e}")
            self.status.config(text="오류 발생")

    def _show_footnote_editor(self):
        # Create a toplevel window for footnote editing
        editor = tk.Toplevel(self.root)
        editor.title("각주 편집기")
        editor.geometry("900x500")
        editor.transient(self.root)
        editor.grab_set()
        # Track UI alive state
        self.ui_alive = True
        # Handle window close
        editor.protocol("WM_DELETE_WINDOW", self._on_editor_close)

        toolbar = ttk.Frame(editor)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(toolbar, text="CSV 저장", command=lambda: self._save_csv_from_editor(editor)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="참고문헌 미리보기", command=lambda: self._preview_bibliography(editor)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="BibTeX 내보내기", command=lambda: self._export_bibtex(editor)).pack(side=tk.LEFT, padx=2)

        paned = ttk.PanedWindow(editor, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left: original footnotes (read-only)
        left_frame = ttk.LabelFrame(paned, text="원본 각주")
        paned.add(left_frame, weight=1)
        left_text = tk.Text(left_frame, wrap=tk.WORD, width=40)
        left_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        # Populate left
        for fn in self.footnotes:
            left_text.insert(tk.END, f"[{fn['fn_id']}] {fn['fn_text']}\n\n")
        left_text.config(state=tk.DISABLED)

        # Right: editable area with checkboxes
        right_frame = ttk.LabelFrame(paned, text="참고문헌 편집 (matched_ref) 및 매칭 표시")
        paned.add(right_frame, weight=2)

        canvas = tk.Canvas(right_frame)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)

        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Clear previous edited rows
        self.edited_rows = []
        self.auto_match_results = {}

        # Header
        header = ttk.Frame(scrollable)
        header.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(header, text="#", width=4).pack(side=tk.LEFT)
        ttk.Label(header, text="원본 각주", width=25, anchor="w").pack(side=tk.LEFT, padx=5)
        ttk.Label(header, text="참고문헌 (편집)", width=30, anchor="w").pack(side=tk.LEFT, padx=5)
        ttk.Label(header, text="유형", width=8).pack(side=tk.LEFT)
        ttk.Label(header, text="매칭", width=8).pack(side=tk.LEFT)
        ttk.Label(header, text="확신도", width=8).pack(side=tk.LEFT)
        ttk.Label(header, text="DOI", width=10).pack(side=tk.LEFT)

        for i, fn in enumerate(self.footnotes, start=1):
            row = ttk.Frame(scrollable)
            row.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(row, text=str(i), width=4, anchor=tk.CENTER).pack(side=tk.LEFT)
            # Original text (read-only)
            orig = tk.Text(row, height=3, width=25, wrap=tk.WORD)
            orig.insert(tk.END, fn['fn_text'])
            orig.config(state=tk.DISABLED, background=editor.cget('bg'))
            orig.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=False)
            # Editable reference
            ref = tk.Text(row, height=3, width=30, wrap=tk.WORD)
            ref.insert(tk.END, '')  # start empty for user to fill
            ref.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=False)
            # Citation type label
            type_label = ttk.Label(row, text="", width=8)
            type_label.pack(side=tk.LEFT, padx=2)
            # Match checkbox
            matched_var = tk.BooleanVar(value=False)
            chk = ttk.Checkbutton(row, variable=matched_var)
            chk.pack(side=tk.LEFT, padx=5)
            # Confidence label
            conf_label = ttk.Label(row, text="", width=8)
            conf_label.pack(side=tk.LEFT, padx=2)
            # DOI label
            doi_label = ttk.Label(row, text="", width=10, foreground="blue", cursor="hand2")
            doi_label.pack(side=tk.LEFT, padx=2)
            # Make DOI label clickable
            doi_label.bind("<Button-1>", lambda e, doi="": self._show_doi_popup(doi))
            # Candidate toggle button
            candidate_btn = ttk.Button(row, text="후보 보기", width=8)
            candidate_btn.pack(side=tk.LEFT, padx=2)

            # Store UI elements for later processing
            fn['conf_label'] = conf_label
            fn['doi_label'] = doi_label
            fn['ref_widget'] = ref
            fn['type_label'] = type_label
            fn['matched_var'] = matched_var

            self.edited_rows.append({
                'fn_id': fn['fn_id'],
                'orig_widget': orig,
                'ref_widget': ref,
                'type_label': type_label,
                'matched_var': matched_var,
                'conf_label': conf_label,
                'doi_label': doi_label,
                'candidate_btn': candidate_btn,
                'index': i,
                'fn_text': fn['fn_text']
            })

            # Candidate display container (initially hidden)
            candidate_frame = ttk.Frame(scrollable)
            candidate_frame.columnconfigure(0, weight=1)
            fn['candidate_frame'] = candidate_frame
            fn['candidate_visible'] = False

            # Configure candidate button to toggle candidate display
            candidate_btn.configure(command=lambda f=fn: self._toggle_candidate_display(f))

        # Store references for later use
        self.editor_win = editor
        self.left_text = left_text
        self.right_frame = right_frame
        self.canvas = canvas

        # Start a single thread to process all footnotes in order
        threading.Thread(target=self._process_all_footnotes_matching, daemon=True).start()

        # Start UI dispatcher loop
        self.root.after(30, self._ui_dispatch_loop)


    def _process_all_footnotes_matching(self):
        """Process all footnotes in order for citation matching"""
        try:
            # Reset citation memory for this document
            fm.reset_citation_memory()

            # Process footnotes in order
            for fn in self.footnotes:
                # Check if UI is still alive before processing
                if not self.ui_alive:
                    return

                fn_text = fn['fn_text']
                fn_id = fn['fn_id']

                # Perform auto-matching
                result = fm.auto_match_reference(fn_text, fn_id)

                if result:
                    self.auto_match_results[fn_id] = result
                    # Queue UI update for main thread
                    self.ui_queue.put({
                        "type": "auto_match_result",
                        "footnote_id": fn_id,
                        "result": result
                    })

        except Exception as e:
            print(f"Error in _process_all_footnotes_matching: {e}")

    def _update_auto_match_ui_threadsafe(self, fn_id, result, conf_label, doi_label, type_label=None):
        """Thread-safe update of UI with auto-match results"""
        # Check if UI is still alive
        if not self.ui_alive:
            return
        if conf_label is None or doi_label is None or result is None:
            return

        # Find the footnote object to access UI elements
        fn_obj = None
        for fn in self.footnotes:
            if fn['fn_id'] == fn_id:
                fn_obj = fn
                break

        if fn_obj is None:
            return

        # Handle both MatchResult objects and legacy dicts for backward compatibility
        if hasattr(result, 'best_match') and result.best_match is not None:
            # New MatchResult structure
            conf_text = f"{result.best_match.confidence*100:.0f}%"
            conf_label.config(text=conf_text)

            # Update citation type
            citation_type = result.best_match.citation_type
            if type_label:
                type_label.config(text=citation_type)

            doi = result.best_match.doi
            if doi:
                doi_label.config(text=doi, foreground="blue", cursor="hand2")
                # Store DOI for click handler
                doi_label.doi = doi
                doi_label.bind("<Button-1>", lambda e, d=doi: self._show_doi_popup(d))
            else:
                doi_label.config(text="", foreground="black")

            # Always apply the best match first (auto-fill)
            # Find the corresponding row and update the reference widget
            for er in self.edited_rows:
                if er['fn_id'] == fn_id:
                    er['ref_widget'].delete("1.0", tk.END)
                    er['ref_widget'].insert(tk.END, result.best_match.matched_ref)
                    break

            # Handle candidate display (always show candidates for FULL citations)
            self._update_candidate_display(fn_obj, result)
        else:
            # Legacy dict structure (backward compatibility)
            conf_text = f"{result['confidence']*100:.0f}%"
            conf_label.config(text=conf_text)

            # Update citation type
            citation_type = result.get('citation_type', '')
            if type_label:
                type_label.config(text=citation_type)

            doi = result.get('doi', '')
            if doi:
                doi_label.config(text=doi, foreground="blue", cursor="hand2")
                # Store DOI for click handler
                doi_label.doi = doi
                doi_label.bind("<Button-1>", lambda e, d=doi: self._show_doi_popup(d))
            else:
                doi_label.config(text="", foreground="black")

            # Always apply the best match first (auto-fill)
            # Find the corresponding row and update the reference widget
            for er in self.edited_rows:
                if er['fn_id'] == fn_id:
                    er['ref_widget'].delete("1.0", tk.END)
                    er['ref_widget'].insert(tk.END, result['matched_ref'])
                    break

    def _show_doi_popup(self, doi):
        """Show DOI in a popup window"""
        if not doi:
            messagebox.showinfo("DOI", "DOI가 없습니다.")
            return
        popup = tk.Toplevel(self.editor_win)
        popup.title("DOI 정보")
        popup.geometry("300x100")
        tk.Label(popup, text=f"DOI: {doi}", font=("Arial", 10)).pack(pady=10)
        tk.Button(popup, text="복사", command=lambda: self._copy_to_clipboard(doi)).pack(pady=5)
        tk.Button(popup, text="닫기", command=popup.destroy).pack(pady=5)

    def _copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        self.editor_win.clipboard_clear()
        self.editor_win.clipboard_append(text)
        messagebox.showinfo("복사", "클립보드에 복사되었습니다.")

    def _save_csv_from_editor(self, editor_win):
        if not self.edited_rows:
            messagebox.showwarning("경고", "편집할 각주가 없습니다.")
            return
        rows = []
        for er in self.edited_rows:
            matched = er['matched_var'].get()
            status = "✅ 매칭" if matched else ""
            # Get auto-match data if available
            fn_id = er['fn_id']
            auto_result = self.auto_match_results.get(fn_id, {})
            confidence = auto_result.get('confidence', 0.0)
            source = auto_result.get('source', '')
            doi = auto_result.get('doi', '')

            rows.append({
                'fn_num': er['index'],
                'fn_type': '',
                'status': status,
                'confidence': f"{confidence:.2f}",
                'source': source,
                'doi': doi,
                'fn_text': er['fn_text'],
                'matched_ref': er['ref_widget'].get("1.0", tk.END).strip()
            })
        save_path = filedialog.asksaveasfilename(
            title="CSV 저장",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="각주_참고문헌_매칭표.csv"
        )
        if not save_path:
            return
        try:
            # Updated fieldnames to include new columns
            fieldnames = ['fn_num', 'fn_type', 'status', 'confidence', 'source', 'doi', 'fn_text', 'matched_ref']
            with open(save_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            messagebox.showinfo("완료", f"CSV 저장:\n{save_path}")
            self.status.config(text=f"CSV 저장: {os.path.basename(save_path)}")
        except Exception as e:
            messagebox.showerror("오류", f"CSV 저장 실패:\n{e}")

    def _preview_bibliography(self, editor_win):
        if not self.edited_rows:
            messagebox.showwarning("경고", "편집할 각주가 없습니다.")
            return
        # Build temp CSV and generate bibliography
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as tmp:
                tmp_path = tmp.name
                fieldnames = ['fn_num', 'fn_type', 'status', 'confidence', 'source', 'doi', 'fn_text', 'matched_ref']
                writer = csv.DictWriter(tmp, fieldnames=fieldnames)
                writer.writeheader()
                for er in self.edited_rows:
                    matched = er['matched_var'].get()
                    status = "✅ 매칭" if matched else ""
                    fn_id = er['fn_id']
                    auto_result = self.auto_match_results.get(fn_id, {})
                    confidence = auto_result.get('confidence', 0.0)
                    source = auto_result.get('source', '')
                    doi = auto_result.get('doi', '')
                    writer.writerow({
                        'fn_num': er['index'],
                        'fn_type': '',
                        'status': status,
                        'confidence': f"{confidence:.2f}",
                        'source': source,
                        'doi': doi,
                        'fn_text': er['fn_text'],
                        'matched_ref': er['ref_widget'].get("1.0", tk.END).strip()
                    })
            bibliography = fm.generate_bibliography_from_edited(tmp_path)
            if not bibliography:
                messagebox.showinfo("알림", "매칭된 각주가 없습니다.")
                return
            # Show in popup
            win = tk.Toplevel(editor_win)
            win.title("생성된 참고문헌")
            win.geometry("500x400")
            txt = tk.Text(win, wrap=tk.WORD)
            txt.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            for i, ref in enumerate(bibliography, start=1):
                txt.insert(tk.END, f"{i}. {ref}\n\n")
            txt.config(state=tk.DISABLED)
            ttk.Button(win, text="닫기", command=win.destroy).pack(pady=5)
            self.status.config(text=f"참고문헌 {len(bibliography)}건 생성")
        except Exception as e:
            messagebox.showerror("오류", f"참고문헌 생성 실패:\n{e}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass

    def _export_bibtex(self, editor_win):
        """Export bibliography to BibTeX file"""
        if not self.edited_rows:
            messagebox.showwarning("경고", "편집할 각주가 없습니다.")
            return

        # Build temporary CSV to get bibliography
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as tmp:
                tmp_path = tmp.name
                fieldnames = ['fn_num', 'fn_type', 'status', 'confidence', 'source', 'doi', 'fn_text', 'matched_ref']
                writer = csv.DictWriter(tmp, fieldnames=fieldnames)
                writer.writeheader()
                for er in self.edited_rows:
                    matched = er['matched_var'].get()
                    status = "✅ 매칭" if matched else ""
                    fn_id = er['fn_id']
                    auto_result = self.auto_match_results.get(fn_id, {})
                    confidence = auto_result.get('confidence', 0.0)
                    source = auto_result.get('source', '')
                    doi = auto_result.get('doi', '')
                    writer.writerow({
                        'fn_num': er['index'],
                        'fn_type': '',
                        'status': status,
                        'confidence': f"{confidence:.2f}",
                        'source': source,
                        'doi': doi,
                        'fn_text': er['fn_text'],
                        'matched_ref': er['ref_widget'].get("1.0", tk.END).strip()
                    })

            # Generate bibliography from edited CSV
            bibliography_strings = fm.generate_bibliography_from_edited(tmp_path)
            if not bibliography_strings:
                messagebox.showinfo("알림", "매칭된 각주가 없어 BibTeX를 생성할 수 없습니다.")
                return

            # Convert bibliography strings to entries for BibTeX generation
            # We need to extract metadata from auto-match results for BibTeX
            bibtex_entries = []
            used_dois = set()  # Track DOIs to avoid duplicates

            for i, er in enumerate(self.edited_rows):
                matched = er['matched_var'].get()
                if not matched:
                    continue

                fn_id = er['fn_id']
                auto_result = self.auto_match_results.get(fn_id, {})
                if not auto_result:
                    continue

                # Check if this entry has a DOI we've already used
                doi = auto_result.get('doi', '')
                if doi and doi in used_dois:
                    continue
                if doi:
                    used_dois.add(doi)

                # Create entry for BibTeX
                entry = {
                    'author': auto_result.get('author', ''),  # We need to extract this from auto_result
                    'title': auto_result.get('title', ''),
                    'year': auto_result.get('year', ''),
                    'journal': auto_result.get('journal', ''),
                    'publisher': auto_result.get('publisher', ''),
                    'doi': doi
                }

                # Extract author, title, year from the matched_ref or auto_result
                # For simplicity, we'll use what we have in auto_result
                # In a real implementation, we'd parse the Crossref item more thoroughly
                if 'author' not in entry or not entry['author']:
                    # Try to extract author from matched_ref
                    pass  # Simplified for now

                bibtex_entries.append(entry)

            # Generate BibTeX content
            bibtex_content = fm.bibliography_to_bibtex(bibtex_entries)
            if not bibtex_content:
                messagebox.showinfo("알림", "BibTeX 생성 실패.")
                return

            # Save BibTeX file
            output_path = filedialog.asksaveasfilename(
                title="BibTeX 파일 저장",
                defaultextension=".bib",
                filetypes=[("BibTeX files", "*.bib")],
                initialfile="참고문헌.bib"
            )
            if not output_path:
                return

            if fm.save_bibtex_file(bibtex_entries, output_path):
                messagebox.showinfo("완료", f"BibTeX 파일 저장:\n{output_path}")
                self.status.config(text=f"BibTeX 저장: {os.path.basename(output_path)}")
            else:
                messagebox.showerror("오류", "BibTeX 파일 저장 실패.")

        except Exception as e:
            messagebox.showerror("오류", f"BibTeX 내보내기 실패:\n{e}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass

    def generate_final_docx(self):
        if not self.docx_path:
            messagebox.showerror("오류", "먼저 DOCX 파일을 선택하세요.")
            return
        if not self.edited_rows:
            messagebox.showwarning("경고", "각주 편집기를 먼저 열어 각주를 추출하세요.")
            return
        # Generate bibliography from current edited state
        tmp_path = None
        processed_doc = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as tmp:
                tmp_path = tmp.name
                fieldnames = ['fn_num', 'fn_type', 'status', 'confidence', 'source', 'doi', 'fn_text', 'matched_ref']
                writer = csv.DictWriter(tmp, fieldnames=fieldnames)
                writer.writeheader()
                for er in self.edited_rows:
                    matched = er['matched_var'].get()
                    status = "✅ 매칭" if matched else ""
                    fn_id = er['fn_id']
                    auto_result = self.auto_match_results.get(fn_id, {})
                    confidence = auto_result.get('confidence', 0.0)
                    source = auto_result.get('source', '')
                    doi = auto_result.get('doi', '')
                    writer.writerow({
                        'fn_num': er['index'],
                        'fn_type': '',
                        'status': status,
                        'confidence': f"{confidence:.2f}",
                        'source': source,
                        'doi': doi,
                        'fn_text': er['fn_text'],
                        'matched_ref': er['ref_widget'].get("1.0", tk.END).strip()
                    })
            bibliography = fm.generate_bibliography_from_edited(tmp_path)
            if not bibliography:
                messagebox.showinfo("알림", "매칭된 각주가 없어 참고문헌을 생성할 수 없습니다.")
                return
            # Apply styles to the original docx (body only) and append bibliography
            output_path = filedialog.asksaveasfilename(
                title="최종 논문 저장",
                defaultextension=".docx",
                filetypes=[("Word files", "*.docx")],
                initialfile="최종_논문.docx"
            )
            if not output_path:
                return
            # Step 1: process docx for styles (using existing engine functions)
            processed_doc = os.path.join(tempfile.gettempdir(), "임시_스타일적용.docx")
            engine.process_docx(self.docx_path, processed_doc)
            # Step 2: append bibliography to processed_doc
            fm.update_docx_with_bibliography(processed_doc, bibliography, output_path)
            messagebox.showinfo("완료", f"최종 문서 저장:\n{output_path}")
            self.status.config(text=f"최종 문서 생성: {os.path.basename(output_path)}")
        except Exception as e:
            messagebox.showerror("오류", f"최종 문서 생성 실패:\n{e}")
        finally:
            # Clean up temporary files
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass
            if processed_doc and os.path.exists(processed_doc):
                try:
                    os.remove(processed_doc)
                except:
                    pass

    def _toggle_candidate_display(self, fn):
        """Toggle the display of candidate matches for a footnote"""
        if fn['candidate_visible']:
            # Hide candidate frame
            fn['candidate_frame'].pack_forget()
            fn['candidate_visible'] = False
            fn['candidate_btn'].configure(text="후보 보기")
        else:
            # Show candidate frame
            fn['candidate_frame'].pack(fill=tk.X, padx=5, pady=2, after=fn['ref_widget'].master)
            fn['candidate_visible'] = True
            fn['candidate_btn'].configure(text="후보 숨기기")

    def _apply_match(self, fn_id, match):
        """Apply a match to a footnote (used for auto-filling)"""
        # Find the footnote object
        fn_obj = None
        for fn in self.footnotes:
            if fn['fn_id'] == fn_id:
                fn_obj = fn
                break

        if fn_obj is None:
            return

        # Update the matched reference in the UI
        for er in self.edited_rows:
            if er['fn_id'] == fn_id:
                er['ref_widget'].delete("1.0", tk.END)
                er['ref_widget'].insert(tk.END, match.matched_ref)
                break

        # Update confidence label
        conf_text = f"{match.confidence*100:.0f}%"
        fn_obj['conf_label'].config(text=conf_text)

        # Update citation type label
        fn_obj['type_label'].config(text=match.citation_type)

        # Update DOI label
        if match.doi:
            fn_obj['doi_label'].config(text=match.doi, foreground="blue", cursor="hand2")
            # Store DOI for click handler
            fn_obj['doi_label'].doi = match.doi
            fn_obj['doi_label'].bind("<Button-1>", lambda e, d=match.doi: self._show_doi_popup(d))
        else:
            fn_obj['doi_label'].config(text="", foreground="black")

    def _update_candidate_display(self, fn, result):
        """Update the candidate display for a footnote"""
        # Clear previous candidates
        for widget in fn['candidate_frame'].winfo_children():
            widget.destroy()

        # Handle both MatchResult objects and legacy dicts for backward compatibility
        if hasattr(result, 'best_match') and result.best_match is not None:
            # New MatchResult structure
            candidates = result.candidates
            # Don't show candidates for REPEATED citations (they're auto-resolved)
            if result.best_match.citation_type == "REPEATED":
                return
        else:
            # Legacy dict structure (backward compatibility) - no candidate support
            return

        if not candidates:
            return

        # Add candidate header
        header_label = ttk.Label(fn['candidate_frame'], text="추천 候補:", font=("Arial", 9, "bold"))
        header_label.grid(row=0, column=0, sticky="w", pady=(5, 2))

        # Add each candidate
        for i, candidate in enumerate(candidates):
            candidate_frame = ttk.Frame(fn['candidate_frame'])
            candidate_frame.grid(row=i+1, column=0, sticky="ew", pady=1)
            candidate_frame.columnconfigure(1, weight=1)

            # Radio button to select candidate
            var = tk.BooleanVar(value=(candidate == result.best_match))
            rb = ttk.Radiobutton(candidate_frame, variable=var, value=True,
                               command=lambda c=candidate, f=fn, v=var: self._select_candidate(c, f, v))
            rb.grid(row=0, column=0, padx=(0, 5))

            # Candidate info
            info_text = f"{candidate.preview} "
            info_text += f"(신뢰도: {candidate.confidence*100:.0f}%, 출처: {candidate.source}"
            if candidate.doi:
                info_text += f", DOI: {candidate.doi}"
            info_text += ")"

            info_label = ttk.Label(candidate_frame, text=info_text, foreground="blue", cursor="hand2")
            info_label.grid(row=0, column=1, sticky="w")
            info_label.bind("<Button-1>", lambda e, c=candidate: self._show_candidate_details(c))

    def _select_candidate(self, candidate, fn, var):
        """Handle candidate selection"""
        if var.get():
            # Update the matched reference with the selected candidate
            fn['ref_widget'].delete("1.0", tk.END)
            fn['ref_widget'].insert(tk.END, candidate.matched_ref)

            # Update the auto_match_results to reflect the selection
            fn_id = fn['fn_id']
            if fn_id in self.auto_match_results:
                # Create a new MatchResult with the selected candidate as best_match
                old_result = self.auto_match_results[fn_id]
                if hasattr(old_result, 'best_match'):
                    # New MatchResult structure
                    new_candidates = [c if c == candidate else c for c in old_result.candidates]
                    # Ensure the selected candidate is first
                    new_candidates.remove(candidate)
                    new_candidates.insert(0, candidate)

                    new_result = MatchResult(
                        best_match=candidate,
                        candidates=new_candidates,
                        requires_user_selection=False  # User selected it, so no need for further selection
                    )
                    self.auto_match_results[fn_id] = new_result
                else:
                    # Legacy dict structure
                    self.auto_match_results[fn_id] = {
                        'matched_ref': candidate.matched_ref,
                        'confidence': candidate.confidence,
                        'source': candidate.source,
                        'citation_type': candidate.citation_type,
                        'doi': candidate.doi
                    }

                # Update all related UI elements to reflect the selection
                self._update_ui_after_candidate_selection(fn, candidate)

    def _update_ui_after_candidate_selection(self, fn, candidate):
        """Update UI elements after candidate selection"""
        # Update confidence label
        conf_text = f"{candidate.confidence*100:.0f}%"
        fn['conf_label'].config(text=conf_text)

        # Update citation type label
        fn['type_label'].config(text=candidate.citation_type)

        # Update DOI label
        if candidate.doi:
            fn['doi_label'].config(text=candidate.doi, foreground="blue", cursor="hand2")
            # Store DOI for click handler
            fn['doi_label'].doi = candidate.doi
            fn['doi_label'].bind("<Button-1>", lambda e, d=candidate.doi: self._show_doi_popup(d))
        else:
            fn['doi_label'].config(text="", foreground="black")

    def _on_editor_close(self):
        """Handle footnote editor window close"""
        self.ui_alive = False
        if self.editor_win:
            self.editor_win.destroy()

    def _show_candidate_details(self, candidate):
        """Show detailed information about a candidate"""
        popup = tk.Toplevel(self.editor_win)
        popup.title("후보 세부 정보")
        popup.geometry("400x200")

        text = tk.Text(popup, wrap=tk.WORD, padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True)

        details = f"매칭 참고문헌:\n{candidate.matched_ref}\n\n"
        details += f"후보 ID: {candidate.candidate_id}\n"
        details += f"신뢰도: {candidate.confidence*100:.1f}%\n"
        details += f"출처: {candidate.source}\n"
        details += f"인용 유형: {candidate.citation_type}\n"
        if candidate.doi:
            details += f"DOI: {candidate.doi}\n"
        if candidate.preview:
            details += f"미리보기: {candidate.preview}\n"

        text.insert(tk.END, details)
        text.config(state=tk.DISABLED)

        ttk.Button(popup, text="닫기", command=popup.destroy).pack(pady=5)

    def _ui_dispatch_loop(self):
        """Process UI update messages from worker thread"""
        if not self.ui_alive or not self.root.winfo_exists():
            return

        try:
            while True:
                msg = self.ui_queue.get_nowait()
                self._handle_ui_message(msg)
        except queue.Empty:
            pass

        # Reschedule the loop
        self.root.after(30, self._ui_dispatch_loop)

    def _handle_ui_message(self, msg):
        """Route UI messages to appropriate handlers"""
        msg_type = msg.get("type")

        if msg_type == "auto_match_result":
            self._apply_auto_match_result(
                msg["footnote_id"],
                msg["result"]
            )

    def _apply_auto_match_result(self, footnote_id, result):
        """Apply auto-match result to UI (runs in main thread)"""
        if not self.ui_alive or not self.root.winfo_exists():
            return

        self._update_auto_match_ui_threadsafe(footnote_id, result)


if __name__ == "__main__":
    root = tk.Tk()
    app = ThesisApp(root)
    root.mainloop()