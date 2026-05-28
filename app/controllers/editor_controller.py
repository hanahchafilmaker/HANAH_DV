import footnote_manager as fm

class EditorController:
    def __init__(self, state):
        self.state = state

    # -------------------------
    # FILE LOAD
    # -------------------------
    def load_docx(self, path):
        self.state.docx_path = path
        self.state.footnotes = fm.extract_footnotes(path)
        return self.state.footnotes

    # -------------------------
    # MATCHING ENGINE
    # -------------------------
    def process_all(self):
        fm.reset_citation_memory()

        results = {}

        for fn in self.state.footnotes:
            result = fm.auto_match_reference(fn["fn_text"], fn["fn_id"])
            results[fn["fn_id"]] = result

        self.state.match_results = results
        return results

    # -------------------------
    # SELECT CANDIDATE
    # -------------------------
    def select_candidate(self, fn_id, candidate):
        # Update the state's match_results for the given fn_id
        if fn_id in self.state.match_results:
            # We assume the state.match_results[fn_id] is a MatchResult object
            # We update its best_match and set requires_user_selection to False
            # Note: We are not changing the candidates list here, but we could if needed.
            # However, the controller's role is to update the state, and the UI will reflect the state.
            # For simplicity, we update the best_match and leave the candidates as is.
            # In a more complex scenario, we might reorder the candidates to put the selected one first.
            current_result = self.state.match_results[fn_id]
            # Create a new MatchResult with the selected candidate as best_match
            # and the same candidates list (but we might want to move the selected to front)
            # Let's keep the candidates list as is for now, but note that the UI might show the selected one as best.
            # Alternatively, we can create a new list with the selected candidate first and the rest following.
            # We'll do the latter to match the behavior in the original code.
            new_candidates = [c if c == candidate else c for c in current_result.candidates]
            new_candidates.remove(candidate)
            new_candidates.insert(0, candidate)

            new_result = type(current_result)(
                best_match=candidate,
                candidates=new_candidates,
                requires_user_selection=False  # User selected it, so no need for further selection
            )
            self.state.match_results[fn_id] = new_result
        return candidate