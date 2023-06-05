import customtkinter


class AnalysisPage(customtkinter.CTkFrame):
    def __init__(self, master, db, **kwargs):
        super().__init__(master, **kwargs)

        self.db = db
