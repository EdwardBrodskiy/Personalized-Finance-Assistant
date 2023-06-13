from collections import OrderedDict

import customtkinter

from classifier.rule_classifier import Classifier
from web_app.components.auto_suggest_tag_entry import AutoSuggestTagEntry
from web_app.popups.error_popup import ErrorPopup


class RowEntry(customtkinter.CTkFrame):
    def __init__(self, master, on_enter=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(height=150)
        self.on_enter = on_enter

        self.fields = None
        self.controls = None
        self.row_index = 1
        self.first_table_draw = True
        self.part_labeled_row = None

    def add_entry_row_at(self, part_labeled_row, suggestions):
        self.part_labeled_row = part_labeled_row
        self.fields = OrderedDict(
            (
                ('ref', customtkinter.CTkLabel(self, anchor='w')),
                ('Description', customtkinter.CTkEntry(self, width=300)),
                ('Amount', customtkinter.CTkEntry(self)),
                ('Tags', AutoSuggestTagEntry(self, suggestions=suggestions['Tags']))
            )
        )

        for i, (key, field) in enumerate(self.fields.items()):
            if self.first_table_draw:
                label = customtkinter.CTkLabel(self, text=key)
                label.grid(row=0, column=i, sticky='w', padx=(0, 5), pady=5)
            if type(field) is customtkinter.CTkLabel:
                field.configure(text=self.part_labeled_row.at[0, key])
            else:
                field.insert(0, self.part_labeled_row.at[0, key])
            field.grid(row=self.row_index, column=i, sticky='nsew', padx=(0, 5), pady=5)

        if self.first_table_draw:
            self.grid_columnconfigure(list(range(len(self.fields))), weight=1)
            self.grid_columnconfigure(list(self.fields.keys()).index('Description'), weight=10)
            self.grid_columnconfigure(list(self.fields.keys()).index('Tags'), weight=10)
        self.first_table_draw = False
        self.fields[list(self.fields.keys())[-1]].bind("<Tab>", lambda event: self.submit())

        self.create_controls()

        # Manually move focus to first field
        self.fields[list(self.fields.keys())[-1]].hide_suggestions()
        self.fields[list(self.fields.keys())[1]].focus_set()

    def create_controls(self):
        # add submit button as an alternative to <Tab> on last field
        self.controls = customtkinter.CTkFrame(self)
        self.controls.grid(row=self.row_index + 1, sticky='we', column=0, columnspan=len(self.fields))
        self.controls.columnconfigure(0, weight=1)

        skip = customtkinter.CTkButton(self.controls, text='skip', command=self.skip, fg_color="transparent",
                                       border_width=2,
                                       text_color=("gray10", "#DCE4EE"))
        skip.grid(row=0, column=0, sticky='e')

        add = customtkinter.CTkButton(self.controls, text='submit', command=self.submit)
        add.grid(row=0, column=1, sticky='e')

    def clear_entry(self):
        for field in self.fields.values():
            field.destroy()
        self.controls.destroy()

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
                label.grid(row=self.row_index, column=i, sticky='w', padx=(0, 5), pady=1)
            self.row_index += 1

        if self.on_enter is not None:
            self.on_enter(user_entries)

    def skip(self):
        self.clear_entry()
        if self.on_enter is not None:
            self.on_enter(None)
