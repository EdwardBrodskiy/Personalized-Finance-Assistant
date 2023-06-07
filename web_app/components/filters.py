import customtkinter as ctk
import pandas as pd


class Filter(ctk.CTkFrame):
    def __init__(self, master, column_name, on_remove=None, on_change=None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_remove_callback = on_remove
        self.on_change_callback = on_change

        self.selected_column = ctk.CTkLabel(self, text=column_name)
        self.selected_column.grid(column=0, row=0, sticky='w', padx=5, pady=5)

        self.selector_frame = ctk.CTkFrame(self)
        self.selector_frame.grid(column=1, row=0, sticky="we", padx=5, pady=5)

        self.remove_button = ctk.CTkButton(self, text='-', width=30, command=self._on_remove)
        self.remove_button.grid(column=2, row=0, padx=5, pady=5)

        self.grid_columnconfigure(1, weight=1)
        # self.grid_columnconfigure((0, 2), weight=0)

    def _on_remove(self):
        self.destroy()
        self.on_remove_callback()

    def _on_change(self):
        self.on_change_callback()

    def get_query(self):
        raise NotImplementedError('This function should be overriden')


class StringFilter(Filter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.query = ctk.StringVar(value='')
        self.query.trace('w', self._on_change)
        self.entry = ctk.CTkEntry(self.selector_frame, textvariable=self.query)
        self.entry.grid(column=0, row=0, sticky='nswe', padx=5, pady=5)

        self.case_sensitive = ctk.BooleanVar(value=False)
        self.checkbox = ctk.CTkCheckBox(self.selector_frame, text="Case Sensetive", command=self._on_change,
                                        variable=self.case_sensitive, onvalue=True, offvalue=False)
        self.checkbox.grid(column=1, row=0, padx=5, pady=5)

        self.selector_frame.grid_columnconfigure(0, weight=1)
        self.selector_frame.grid_columnconfigure(1, weight=0)

    def _on_change(self, *args):
        if len(self.query.get()) < 2:
            return  # search only after at least to chars
        super()._on_change()

    def get_query(self):
        return lambda df: pd.DataFrame.str.contains(df, self.entry.get(), case=self.case_sensitive.get())


type_mappings = {
    'string': StringFilter,

}
