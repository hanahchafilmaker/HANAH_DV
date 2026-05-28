class AppState:
    def __init__(self):
        self.docx_path = None
        self.footnotes = []
        self.selected_fn_id = None

        # results
        self.match_results = {}

        # ui state
        self.candidate_visible = {}