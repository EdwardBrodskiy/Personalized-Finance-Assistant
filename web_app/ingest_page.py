import customtkinter
from collections import OrderedDict
from classifier_for_gui import Classifier


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

        # cl = Classifier(db)
        # labeled = cl.classify()
        # Entry
        self.row_entry = RowEntry(self)
        self.row_entry.pack(fill='x')


class RowEntry(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.fields = OrderedDict(
            (
                ('Who', AutoSuggestEntry(self, suggestions=('mama', 'papa', 'maria'))),
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


class AutoSuggestEntry(customtkinter.CTkEntry):
    def __init__(self, master=None, suggestions=None, **kwargs):
        super().__init__(master, **kwargs)
        self.suggestions = suggestions if suggestions else []
        self.var = customtkinter.StringVar()
        self.configure(textvariable=self.var)
        self.var.trace_add("write", self.show_suggestions)
        self.labels_frame = None
        self.suggested = ()
        self.selected_label_index = -1
        self.bind("<FocusOut>", self.hide_suggestions)
        self.bind("<Up>", self.move_selection_up)
        self.bind("<Down>", self.move_selection_down)
        self.bind("<Return>", self.select_suggestion)

    def show_suggestions(self, *args):
        if not self.labels_frame:
            self.labels_frame = customtkinter.CTkFrame(self, width=self.winfo_width(), height=0)
            self.labels_frame.grid()

        for widget in self.labels_frame.winfo_children():
            widget.destroy()

        query = self.var.get().lower()
        suggestions = [word for word in self.suggestions if word.lower().startswith(query)]

        self.suggested = tuple(suggestions)
        for index, suggestion in enumerate(suggestions):
            label = customtkinter.CTkLabel(self.labels_frame, text=suggestion, padx=3, pady=3, width=self.cget('width'),
                                           anchor='w')
            label.bind("<Button-1>", lambda event, text=suggestion: self.select_suggestion(event, text))
            label.bind("<Enter>", lambda event, index=index: self.highlight_label(index))
            label.bind("<Leave>", lambda event: self.highlight_label(-1))
            label.grid(row=index, column=0, sticky="w")

    def hide_suggestions(self, event=None):
        if self.labels_frame:
            self.labels_frame.destroy()
            self.labels_frame = None

    def move_selection_up(self, event):
        if self.labels_frame:
            self.selected_label_index -= 1
            self.selected_label_index = max(self.selected_label_index, 0)
            self.highlight_label(self.selected_label_index)

    def move_selection_down(self, event):
        if self.labels_frame:
            self.selected_label_index += 1
            self.selected_label_index = min(self.selected_label_index, len(self.labels_frame.winfo_children()) - 1)
            self.highlight_label(self.selected_label_index)

    def select_suggestion(self, event=None, text=None):
        if self.labels_frame and (self.selected_label_index >= 0 or text):
            if not text:
                text = self.suggested[self.selected_label_index]
            self.var.set(text)
            self.icursor(customtkinter.END)
            self.hide_suggestions()

    def highlight_label(self, index):
        for label in self.labels_frame.winfo_children():
            if index == label.grid_info()["row"]:
                label.configure(fg_color="#106A43")
            else:
                label.configure(fg_color="transparent")