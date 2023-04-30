import customtkinter
from collections import OrderedDict
from classifier_for_gui import Classifier
from indexer import index as index_input_data
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

        self.bt_run_classifier = customtkinter.CTkButton(self.lower_controls, text='Run classifier',
                                                         command=self.start_ingest_process)
        self.bt_run_classifier.grid(row=1, column=1, sticky='e')

        self.lb_classifier_result = customtkinter.CTkLabel(self.lower_controls, text='Classifier has not been run yet',
                                                           padx=10, pady=10)
        self.lb_classifier_result.grid(row=1, column=0, sticky='e')

        # suggestions pane
        self.suggestions_pane = customtkinter.CTkScrollableFrame(self)
        self.suggestions_pane.pack(side='right', fill='y')

        self.ingest_label = customtkinter.CTkLabel(self, text='Press "Run Classifier" to begin the ingest process.')
        self.ingest_label.pack(side='top')
        self.ingest_process = IngestProcess(self, self.db, self.suggestions_pane)

    def start_ingest_process(self):
        self.ingest_label.pack_forget()
        self.ingest_process.pack(side='top')
        self.lb_classifier_result.configure(
            text='Classification in progress please enter the required manual information.')

    def run_indexer(self):
        new = index_input_data(self.db)
        if len(new):
            self.lb_indexer_result.configure(text=f'Indexer was run successfully producing {len(new)} new rows')
        else:
            self.lb_indexer_result.configure(text=f'Indexer ran but no new rows were added!')


class IngestProcess(customtkinter.CTkFrame):
    def __init__(self, master, db, suggestions_pane, **kwargs):
        super().__init__(master, **kwargs)

        self.db = db

        # cl = Classifier(db)
        # labeled = cl.classify()
        # Entry
        self.row_entry = RowEntry(self, suggestions_pane)
        self.row_entry.pack()


class RowEntry(customtkinter.CTkFrame):
    def __init__(self, master, suggestions_pane, on_enter=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(height=150)
        self.suggestions_pane = suggestions_pane
        self.on_enter = on_enter

        # self.grid_columnconfigure(list(self.fields.keys()).index('Description'))
        self.fields = None
        self.enter = None
        self.row_index = 0
        self.first_table_draw = True
        self.add_entry_row_at()
        # self.grid_columnconfigure(list(range(len(self.fields))), pad=3)


    def add_entry_row_at(self):
        self.row_index += 1
        ts = ('one', 'two', 'three', 'four', 'five', 'six', 'seven') * 5
        self.fields = OrderedDict(
            (
                ('Who', AutoSuggestEntry(self, self.suggestions_pane, suggestions=ts)),
                ('What', AutoSuggestEntry(self, self.suggestions_pane, suggestions=ts)),
                ('Description', customtkinter.CTkEntry(self, width=300)),
                ('Amount', customtkinter.CTkEntry(self)),
                ('Sub Account', AutoSuggestEntry(self, self.suggestions_pane, suggestions=ts)),

            )
        )

        for i, (key, field) in enumerate(self.fields.items()):
            if self.first_table_draw:
                label = customtkinter.CTkLabel(self, text=key)
                label.grid(row=0, column=i, sticky='w')
            field.grid(row=self.row_index, column=i, sticky='n')
        self.first_table_draw = False
        self.fields[list(self.fields.keys())[-1]].bind("<Tab>", lambda event: self.submit())
        self.fields[list(self.fields.keys())[0]].focus_set()
        self.enter = customtkinter.CTkButton(self, text='+', command=self.submit)
        self.enter.grid(row=self.row_index + 1, sticky='we', column=0, columnspan=len(self.fields))

    def clear_entry(self):
        for field in self.fields.values():
            field.destroy()
        self.enter.destroy()

    def submit(self):
        data = [entry.get() for entry in self.fields.values()]

        # TODO: add entry form validation here

        self.clear_entry()

        for i, value in enumerate(data):
            label = customtkinter.CTkLabel(self, text=value)
            label.grid(row=self.row_index, column=i, sticky='w')

        self.add_entry_row_at()

        if self.on_enter is not None:
            self.on_enter()
