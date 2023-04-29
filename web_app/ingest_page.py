import customtkinter
from collections import OrderedDict
from classifier_for_gui import Classifier
from web_app.auto_suggest_entry import AutoSuggestEntry


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

        # suggestions pane
        self.suggestions_pane = customtkinter.CTkScrollableFrame(self)
        self.suggestions_pane.pack(side='right', fill='y')
        # main ingest process
        self.ingest_process = IngestProcess(self, db, self.suggestions_pane)
        self.ingest_process.pack(side='top')

    def run_indexer(self):
        self.lb_indexer_result.configure(text="Indexer was run successfully")


class IngestProcess(customtkinter.CTkFrame):
    def __init__(self, master, db, suggestions_pane, **kwargs):
        super().__init__(master, **kwargs)

        self.db = db

        # cl = Classifier(db)
        # labeled = cl.classify()
        # Entry
        self.row_entry = RowEntry(self, suggestions_pane)
        self.row_entry.pack()

        self.lb = customtkinter.CTkLabel(self, text='hi')
        self.lb.pack()


class RowEntry(customtkinter.CTkFrame):
    def __init__(self, master, suggestions_pane, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(height=150)
        ts = ('one', 'two', 'three', 'four', 'five', 'six', 'seven') * 5
        self.fields = OrderedDict(
            (
                ('Who', AutoSuggestEntry(self, suggestions_pane, suggestions=ts)),
                ('What', AutoSuggestEntry(self, suggestions_pane, suggestions=ts)),
                ('Description', customtkinter.CTkEntry(self, width=300)),
                ('Amount', customtkinter.CTkEntry(self)),
                ('Sub Account', AutoSuggestEntry(self, suggestions_pane, suggestions=ts)),

            )
        )
        # self.grid_columnconfigure(list(self.fields.keys()).index('Description'))

        self.grid_columnconfigure(list(range(len(self.fields))), pad=3)

        for index, (key, field) in enumerate(self.fields.items()):
            label = customtkinter.CTkLabel(self, text=key)
            label.grid(row=0, column=index, sticky='w')
            field.grid(row=1, column=index, sticky='n')
