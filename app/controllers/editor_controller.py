import app.core.footnote_manager as fm
from app.core import engine

class EditorController:
    def __init__(self, state):
        self.state = state
        # UI components for updates (set by layout)
        self.left_panel = None
        self.toolbar = None

    # -------------------------
    # FILE OPERATIONS
    # -------------------------
    def load_doc(self, path):
        """Load document and extract footnotes"""
        self.state.docx_path = path
        self.state.footnotes = fm.extract_footnotes(path)
        # Notify UI to update
        if hasattr(self.state, 'update_footnotes_for_left_panel'):
            self.state.update_footnotes_for_left_panel(self.state.footnotes)
        self.set_status("Loaded {} footnotes".format(len(self.state.footnotes)), "info")
        return self.state.footnotes

    # -------------------------
    # FOOTNOTE SELECTION
    # -------------------------
    def select_footnote(self, fn_id):
        """Select a footnote and load its candidates"""
        self.state.selected_fn_id = fn_id

        # Get or compute candidates for this footnote
        fn = None
        for f in self.state.footnotes:
            if str(f["fn_id"]) == str(fn_id):
                fn = f
                break

        if fn:
            # Check if we have cached candidates
            cached_candidates = self.state.get_candidates_for_fn(fn_id)
            if cached_candidates:
                self.state.match_results[fn_id] = self._create_match_result_from_candidates(cached_candidates)
            else:
                # Compute candidates
                result = fm.auto_match_reference(fn["fn_text"], fn["fn_id"])
                if result:
                    self.state.match_results[fn_id] = result
                    # Cache candidates if we have them
                    if hasattr(result, 'candidates'):
                        self.state.cache_candidates_for_fn(fn_id, result.candidates)

            self.set_status("Selected footnote {}".format(fn_id), "info")

        # Explicitly refresh UI panels (MVC pattern)
        if self.left_panel:
            self.left_panel.update_footnotes_with_selection(self.state.footnotes)
        if self.center_panel:
            self.center_panel.load_data(self.state.footnotes)
        if hasattr(self, 'right_panel') and self.right_panel:
            # Right panel will be updated via the controller's refresh mechanism in layout.py
            pass

    # -------------------------
    # CANDIDATE APPLICATION
    # -------------------------
    def apply_candidate(self, fn_id, candidate):
        """Apply a candidate to a footnote"""
        if fn_id in self.state.match_results:
            current = self.state.match_results[fn_id]
            if hasattr(current, 'best_match'):
                # It's a MatchResult object
                new_candidates = [c if c == candidate else c for c in current.candidates]
                new_candidates.remove(candidate)
                new_candidates.insert(0, candidate)

                new_result = type(current)(
                    best_match=candidate,
                    candidates=new_candidates,
                    requires_user_selection=False
                )
                self.state.match_results[fn_id] = new_result
            else:
                # Legacy dict
                self.state.match_results[fn_id] = {
                    'matched_ref': candidate.matched_ref,
                    'confidence': candidate.confidence,
                    'source': candidate.source,
                    'citation_type': candidate.citation_type,
                    'doi': candidate.doi
                }

            self.set_status("Applied candidate: {}...".format(candidate.matched_ref[:30]), "success")

            # Update the state reference
            self.state.update_ref_text(candidate.matched_ref)

    # -------------------------
    # STATE UPDATES
    # -------------------------
    def update_state(self):
        """Update application state - placeholder for complex state updates"""
        # This could be used for more complex state synchronization
        pass

    # -------------------------
    # EXPORT FUNCTIONS
    # -------------------------
    def save_csv(self, path):
        """Save current state to CSV"""
        # Build data for CSV
        rows = []
        for fn in self.state.footnotes:
            fn_id = str(fn["fn_id"])
            matched_ref = ""
            confidence = 0.0
            source = ""
            doi = ""

            # Get match result
            result = self.state.match_results.get(fn_id)
            if result:
                if hasattr(result, 'best_match') and result.best_match:
                    matched_ref = result.best_match.matched_ref
                    confidence = result.best_match.confidence
                    source = result.best_match.source
                    doi = result.best_match.doi
                elif isinstance(result, dict):
                    matched_ref = result.get('matched_ref', '')
                    confidence = result.get('confidence', 0.0)
                    source = result.get('source', '')
                    doi = result.get('doi', '')

            rows.append({
                'fn_id': fn_id,
                'fn_text': fn.get('fn_text', ''),
                'matched_ref': matched_ref,
                'confidence': "{:.1f}%".format(confidence * 100),
                'source': source,
                'doi': doi,
                'status': '✅ 매칭' if matched_ref else ''
            })

        # Write CSV
        import csv
        fieldnames = ['fn_id', 'fn_text', 'matched_ref', 'confidence', 'source', 'doi', 'status']
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        self.set_status("CSV saved: {}".format(path), "success")

    def export_bibtex(self, path):
        """Export bibliography to BibTeX"""
        # Get matched references
        entries = []
        used_dois = set()

        for fn in self.state.footnotes:
            fn_id = str(fn["fn_id"])
            result = self.state.match_results.get(fn_id)

            if result:
                matched_ref = ""
                if hasattr(result, 'best_match') and result.best_match:
                    matched_ref = result.best_match.matched_ref
                    doi = result.best_match.doi
                elif isinstance(result, dict):
                    matched_ref = result.get('matched_ref', '')
                    doi = result.get('doi', '')

                if matched_ref and doi and doi not in used_dois:
                    used_dois.add(doi)
                    # Parse the matched_ref to create BibTeX entry (simplified)
                    entry = {
                        'author': '',  # Would need to parse from matched_ref
                        'title': matched_ref[:100],  # Simplified
                        'year': '',
                        'journal': '',
                        'doi': doi
                    }
                    entries.append(entry)

        # Generate BibTeX (simplified)
        bibtex_content = fm.bibliography_to_bibtex(entries)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(bibtex_content)

        self.set_status("BibTeX exported: {}".format(path), "success")

    # -------------------------
    # HELPER METHODS
    # -------------------------
    def _create_match_result_from_candidates(self, candidates):
        """Create a MatchResult object from a list of candidates"""
        if not candidates:
            return None

        # Sort by confidence descending
        sorted_candidates = sorted(candidates, key=lambda x: x.confidence, reverse=True)

        # Return MatchResult with best_match as first candidate
        import app.core.footnote_manager as fm
        return fm.MatchResult(
            best_match=sorted_candidates[0],
            candidates=sorted_candidates
        )

    def set_status(self, text, level="info"):
        """Set status bar text - delegate to UI"""
        # This would be implemented by calling UI components
        # For now, we'll store in state for UI to pick up
        self.state.status_text = text
        self.state.status_level = level