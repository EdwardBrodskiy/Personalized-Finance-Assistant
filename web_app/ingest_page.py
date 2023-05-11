import customtkinter
from collections import OrderedDict
from classifier_for_gui import Classifier
from indexer import index as index_input_data
from web_app.auto_suggest_entry import AutoSuggestEntry
from web_app.dataframe_widget import DataFrameWidget
from web_app.error_popup import ErrorPopup
from web_app.helper_functions import ordinal


class IngestPage(customtkinter.CTkFrame):
    def __init__(self, master, db, **kwargs):
        super().__init__(master, **kwargs)

        self.db = db
        self.classifier = Classifier(self.db)

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
        self.ingest_process = None

    def start_ingest_process(self):
        self.classifier.begin_classification()

        self.lb_classifier_result.configure(
            text=f'Classification in progress please enter the required manual information. '
                 f'{len(self.classifier.auto_existence_labeled)} classified automatically')
        self.bt_run_classifier.configure(state='disabled')

        self.ingest_label.pack_forget()
        self.ingest_process = IngestProcess(self, self.classifier, self.suggestions_pane, height=2000)
        self.ingest_process.pack(side='top', fill='both')

    def run_indexer(self):
        new = index_input_data(self.db)
        if len(new):
            self.lb_indexer_result.configure(text=f'Indexer was run successfully producing {len(new)} new rows')
        else:
            self.lb_indexer_result.configure(text=f'Indexer ran but no new rows were added!')


class IngestProcess(customtkinter.CTkScrollableFrame):
    def __init__(self, master, classifier, suggestions_pane, **kwargs):
        super().__init__(master, **kwargs)
        self.classifier = classifier

        # setup edit tracking
        self.interest_row = 0

        # Entry

        self.row_entry = RowEntry(self, suggestions_pane, on_enter=self.data_entered)
        self.row_entry.pack(fill='both', expand=True)

        # Reference
        df_reference_table = self.classifier.un_labeled.copy()
        df_reference_table['Date'] = df_reference_table['Date'].apply(
            lambda x: ordinal(x.day) + x.strftime(' %b %Y'))
        self.reference_table = DataFrameWidget(self, df_reference_table, self.interest_row, 2)
        self.reference_table.pack(fill='both', expand=True)

        self.row_entry.add_entry_row_at(*self.classifier.get_entry_prerequisites_for_manual_entry(self.interest_row))

    def data_entered(self, data):
        self.classifier.process_incoming_input(data)

        self.interest_row += 1
        self.row_entry.add_entry_row_at(*self.classifier.get_entry_prerequisites_for_manual_entry(self.interest_row))

        self.reference_table.scroll_down_one_row()

        # move scroll to the end
        self.update_idletasks()
        self._parent_canvas.yview_moveto(1)


class RowEntry(customtkinter.CTkFrame):
    def __init__(self, master, suggestions_pane, on_enter=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(height=150)
        self.suggestions_pane = suggestions_pane
        self.on_enter = on_enter

        self.fields = None
        self.enter = None
        self.row_index = 1
        self.first_table_draw = True
        self.part_labeled_row = None

    def add_entry_row_at(self, part_labeled_row, suggestions):
        self.part_labeled_row = part_labeled_row
        self.fields = OrderedDict(
            (
                ('ref', customtkinter.CTkLabel(self, anchor='w')),
                ('Who', AutoSuggestEntry(self, self.suggestions_pane, suggestions=suggestions['Who'])),
                ('What', AutoSuggestEntry(self, self.suggestions_pane, suggestions=suggestions['What'])),
                ('Description', customtkinter.CTkEntry(self, width=300)),
                ('Amount', customtkinter.CTkEntry(self)),
                ('Sub Account', AutoSuggestEntry(self, self.suggestions_pane, suggestions=suggestions['Sub Account'])),

            )
        )

        for i, (key, field) in enumerate(self.fields.items()):
            if self.first_table_draw:
                label = customtkinter.CTkLabel(self, text=key)
                label.grid(row=0, column=i, sticky='w')
            if type(field) is customtkinter.CTkLabel:
                field.configure(text=self.part_labeled_row.at[0, key])
            else:
                field.insert(0, self.part_labeled_row.at[0, key])
            field.grid(row=self.row_index, column=i, sticky='nsew')

        if self.first_table_draw:
            self.columnconfigure(list(range(len(self.fields))), weight=1)
            self.columnconfigure(list(self.fields.keys()).index('Description'), weight=10)
        self.first_table_draw = False
        self.fields[list(self.fields.keys())[-1]].bind("<Tab>", lambda event: self.submit())

        # Manually move focus to first field
        self.fields[list(self.fields.keys())[-1]].hide_suggestions()
        self.fields[list(self.fields.keys())[0]].focus_set()

        # add submit button as an alternative to <Tab> on last field
        self.enter = customtkinter.CTkButton(self, text='+', command=self.submit)
        self.enter.grid(row=self.row_index + 1, sticky='we', column=0, columnspan=len(self.fields))

    def clear_entry(self):
        for field in self.fields.values():
            field.destroy()
        self.enter.destroy()

    def submit(self):
        data = [entry.get() if type(entry) is not customtkinter.CTkLabel else str(entry.cget("text")) for entry in
                self.fields.values()]

        try:
            user_entries = Classifier.process_user_input(data, self.part_labeled_row)
        except (ValueError, ZeroDivisionError) as e:
            ErrorPopup(self, error=e)
            return

        self.clear_entry()

        for row in user_entries:
            for i, (key, value) in enumerate(row.items()):
                label = customtkinter.CTkLabel(self, text=value)
                label.grid(row=self.row_index, column=i, sticky='w')
            self.row_index += 1

        if self.on_enter is not None:
            self.on_enter(user_entries)


