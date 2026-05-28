class AppState:
    def __init__(self):
        self.docx_path = None
        self.footnotes = []
        self.selected_fn_id = None

        # results
        self.match_results = {}
        self.candidates_cache = {}  # Cache for candidates by fn_id

        # ui state
        self.candidate_visible = {}

    def update_footnotes_for_left_panel(self, footnotes):
        """Update footnotes and notify left panel"""
        self.footnotes = footnotes
        # In a more sophisticated implementation, we would notify observers
        # For now, the left panel will pull from state when needed

    def get_candidates_for_fn(self, fn_id):
        """Get cached candidates for a footnote ID"""
        return self.candidates_cache.get(fn_id, [])

    def cache_candidates_for_fn(self, fn_id, candidates):
        """Cache candidates for a footnote ID"""
        self.candidates_cache[fn_id] = candidates