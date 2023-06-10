import customtkinter as ctk

from web_app.components.dataframe_widget import DataFrameWidget

import os
import subprocess

class DataFrameViewer(ctk.CTkFrame):
    def __init__(self, master, dataframe, **kwargs):
        super().__init__(master, **kwargs)

        self._dataframe = dataframe
        self.current_name = ''
        self.grid_columnconfigure(2, weight=1)

        self.show_table_button = ctk.CTkButton(self, text='Show Table', command=self._show_table)
        self.show_table_button.grid(column=0, row=0, padx=5, pady=5)

        self.keep_showing_table = ctk.BooleanVar(value=False)
        self.keep_showing_table_checkbox = ctk.CTkCheckBox(self,
                                                           text="Don't hide table on change (not good for performance",
                                                           variable=self.keep_showing_table, onvalue=True,
                                                           offvalue=False)
        self.keep_showing_table_checkbox.grid(column=1, row=0, padx=5, pady=5)

        self.up_key = ctk.CTkButton(self, text='Up', command=self._go_up, state='disabled')
        self.up_key.grid(column=3, row=0, padx=5, pady=5)

        self.down_key = ctk.CTkButton(self, text='Down', command=self._go_down, state='disabled')
        self.down_key.grid(column=4, row=0, padx=5, pady=5)

        self.down_key = ctk.CTkButton(self, text='Save CSV', command=self._save_to_csv)
        self.down_key.grid(column=5, row=0, padx=5, pady=5)

        self.table = None

    @property
    def dataframe(self):
        return self._dataframe

    @dataframe.setter
    def dataframe(self, value):
        self._dataframe = value
        self._on_input_change()

    def _on_input_change(self, *args):
        if self.keep_showing_table.get():
            self._show_table()
        elif self.table is not None:
            self.table.destroy()
            self.table = None
            self.set_button_states()

    def _show_table(self):
        if self.table is not None:
            self.table.destroy()
        self.table = DataFrameWidget(self, self.dataframe, 0, 3)
        self.table.grid(columnspan=4, row=1, column=0, sticky='we', padx=5, pady=5)
        self.set_button_states()

    def _go_up(self):
        print('Not implemented')

    def _go_down(self):
        self.table.scroll_down_one_row()
        self.set_button_states()

    def _save_to_csv(self):
        path = ctk.filedialog.asksaveasfilename(defaultextension=".csv", initialfile=f'{self.current_name}.csv',
                                                     filetypes=[("CSV Files", "*.csv")], initialdir='display_files')

        self._dataframe.to_csv(path)

    def set_button_states(self):
        self._set_button_state(self.show_table_button, self.table is None)
        self._set_button_state(self.up_key, self.table is not None and 0 < self.table.row_of_interest)
        self._set_button_state(self.down_key,
                               self.table is not None and self.table.row_of_interest < len(self.table.dataframe) - 1)

    @staticmethod
    def _set_button_state(button: ctk.CTkButton, condition):  # if condition is False disable button
        if condition:
            button.configure(state='normal')
        else:
            button.configure(state='disabled')
