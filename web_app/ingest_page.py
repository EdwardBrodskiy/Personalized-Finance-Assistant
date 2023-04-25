import customtkinter


class IngestPage(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.bt_run_indexer = customtkinter.CTkButton(self, text='Run Indexer', command=self.run_indexer)
        self.bt_run_indexer.grid(row=0, column=0)

        self.lb_indexer_result = customtkinter.CTkLabel(self, text='Indexer has not been run yet')
        self.lb_indexer_result.grid(row=0, column=1)

    def run_indexer(self):
        self.lb_indexer_result.configure(text="Indexer was run successfully")
