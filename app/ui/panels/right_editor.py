from ttkbootstrap import Frame, Label, Text, Button

from app.ui.panels.candidate_panel import CandidateCard

class RightEditorPanel:
    def __init__(self, parent, controller, state, set_status):
        self.controller = controller
        self.state = state
        self.set_status = set_status

        self.container = Frame(parent)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        # ORIGINAL FOOTNOTE
        self.orig = Label(self.container, text="", wraplength=400)
        self.orig.pack(anchor="w", pady=5)

        # EDIT BOX
        self.text = Text(self.container, height=3)
        self.text.pack(fill="x", pady=5)

        # APPLY BUTTON
        self.apply_btn = Button(
            self.container,
            text="Apply Selection",
            command=self.apply
        )
        self.apply_btn.pack(pady=5)

        # CANDIDATES AREA
        self.cards_frame = Frame(self.container)
        self.cards_frame.pack(fill="both", expand=True)

    def load_item(self, fn_id):
        self.fn_id = fn_id
        # Note: footnotes are 0-indexed in the list, but fn_id might be string or int.
        # We assume fn_id is string and we convert to int for indexing.
        # However, we should get the footnote by fn_id from the state.footnotes list.
        # Let's find the footnote with matching fn_id.
        fn = None
        for f in self.state.footnotes:
            if str(f["fn_id"]) == str(fn_id):
                fn = f
                break
        if fn is None:
            # If not found, try to index by integer (if fn_id is integer string)
            try:
                index = int(fn_id) - 1
                if 0 <= index < len(self.state.footnotes):
                    fn = self.state.footnotes[index]
            except (ValueError, IndexError):
                pass

        if fn is None:
            self.orig.config(text="Footnote not found")
            return

        self.orig.config(text=fn["fn_text"])

        result = self.state.match_results.get(fn_id)

        # clear cards
        for w in self.cards_frame.winfo_children():
            w.destroy()

        if not result:
            return

        # Handle both MatchResult objects and legacy dicts for backward compatibility
        if hasattr(result, 'candidates'):
            candidates = result.candidates
        else:
            # Legacy dict: we don't have candidates, so we show nothing or maybe just the best match?
            # For now, we'll show the best match as a single candidate if we can.
            # But note: the legacy dict doesn't have a list of candidates.
            # We'll skip for now and maybe show a message.
            candidates = []

        # If we have candidates, show up to 5
        selected_candidate_ref = None
        if hasattr(result, 'best_match') and result.best_match is not None:
            selected_candidate_ref = result.best_match.matched_ref
        elif isinstance(result, dict) and 'matched_ref' in result:
            selected_candidate_ref = result['matched_ref']

        for c in candidates[:5]:
            # Check if this candidate is the currently selected one
            is_selected = (selected_candidate_ref is not None and
                          c.matched_ref == selected_candidate_ref)

            card = CandidateCard(
                self.cards_frame,
                c,
                self.select_candidate,
                selected=is_selected
            )
            card.pack(fill="x", pady=5)

    def select_candidate(self, candidate):
        # Update the state's match_results for the given fn_id
        # We assume the state.match_results[self.fn_id] is a MatchResult object or a dict.
        # We'll update it accordingly.
        if self.fn_id in self.state.match_results:
            current = self.state.match_results[self.fn_id]
            if hasattr(current, 'best_match'):
                # It's a MatchResult object
                # We need to create a new MatchResult with the selected candidate as best_match
                # and reorder candidates to put the selected one first.
                new_candidates = [c if c == candidate else c for c in current.candidates]
                new_candidates.remove(candidate)
                new_candidates.insert(0, candidate)

                new_result = type(current)(
                    best_match=candidate,
                    candidates=new_candidates,
                    requires_user_selection=False  # User selected it
                )
                self.state.match_results[self.fn_id] = new_result
            else:
                # It's a legacy dict
                # We'll update the matched_ref and confidence, etc.
                # We don't have a candidate list in the legacy dict, so we just update the fields.
                self.state.match_results[self.fn_id] = {
                    'matched_ref': candidate.matched_ref,
                    'confidence': candidate.confidence,
                    'source': candidate.source,
                    'citation_type': candidate.citation_type,
                    'doi': candidate.doi
                }
        else:
            # If there's no result, we create a new one? But this shouldn't happen.
            pass

        self.set_status("Candidate selected")

    def apply(self):
        # In this design, the apply button might be redundant because selecting a candidate already updates the state.
        # However, we keep it for explicit apply action.
        self.set_status("Saved ✔")