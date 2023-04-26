import customtkinter
from collections import OrderedDict


class IngestPage(customtkinter.CTkFrame):
    def __init__(self, master, db, **kwargs):
        super().__init__(master, **kwargs)

        self.db = db

        # lower controls
        self.lower_controls = customtkinter.CTkFrame(self)
        self.lower_controls.pack(side='bottom', anchor='s', fill='x')

        self.lower_controls.grid_columnconfigure(0, weight=1)

        self.bt_run_indexer = customtkinter.CTkButton(self.lower_controls, text='Run Indexer', command=self.run_indexer)
        self.bt_run_indexer.grid(row=0, column=1, sticky='e')

        self.lb_indexer_result = customtkinter.CTkLabel(self.lower_controls, text='Indexer has not been run yet',
                                                        padx=10, pady=10)
        self.lb_indexer_result.grid(row=0, column=0, sticky='e')

        self.bt_run_classifier = customtkinter.CTkButton(self.lower_controls, text='Run classifier')
        self.bt_run_classifier.grid(row=1, column=1, sticky='e')

        self.lb_classifier_result = customtkinter.CTkLabel(self.lower_controls, text='Classifier has not been run yet',
                                                           padx=10, pady=10)
        self.lb_classifier_result.grid(row=1, column=0, sticky='e')

        # main ingest process
        self.ingest_process = IngestProcess(self, db)
        self.ingest_process.pack(side='top')

    def run_indexer(self):
        self.lb_indexer_result.configure(text="Indexer was run successfully")


class IngestProcess(customtkinter.CTkFrame):
    def __init__(self, master, db, **kwargs):
        super().__init__(master, **kwargs)

        self.db = db
        # Entry
        self.row_entry = RowEntry(self)
        self.row_entry.pack(fill='x')


class RowEntry(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.fields = OrderedDict(
            (
                ('Who', customtkinter.CTkEntry(self)),
                ('What', customtkinter.CTkEntry(self)),
                ('Description', customtkinter.CTkEntry(self, width=300)),
                ('Amount', customtkinter.CTkEntry(self)),
                ('Sub Account', customtkinter.CTkEntry(self)),

            )
        )
        # self.grid_columnconfigure(list(self.fields.keys()).index('Description'))

        self.grid_columnconfigure(list(range(len(self.fields))), pad=3)

        for index, (key, field) in enumerate(self.fields.items()):
            label = customtkinter.CTkLabel(self, text=key)
            label.grid(row=0, column=index, sticky='w')
            field.grid(row=1, column=index, sticky='n')
