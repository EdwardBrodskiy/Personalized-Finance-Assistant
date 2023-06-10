import customtkinter as ctk

import pandas as pd


class Insights(ctk.CTkFrame):
    def __init__(self, master, dataframe, **kwargs):
        super().__init__(master, **kwargs)

        self._dataframe = dataframe

        self.basic = {
            'total amount': pd.Series.sum,
            'mean amount': pd.Series.mean,
            'minimum amount': pd.Series.min,
            'maximum amount': pd.Series.max,
            'row count': pd.Series.__len__,

        }
        self.basic_labels = {}
        for i, (key, operation) in enumerate(self.basic.items()):
            self.basic_labels[key] = ctk.CTkLabel(self,
                                                  text=self._format_label(key, operation(self.dataframe['Amount'])))
            self.basic_labels[key].grid(row=0, column=i, sticky='w', padx=5, pady=5)

        self.grid_columnconfigure(list(range(len(self.basic))), weight=1)

    @property
    def dataframe(self):
        return self._dataframe

    @dataframe.setter
    def dataframe(self, value):
        self._dataframe = value
        self._on_input_change()

    def _on_input_change(self):
        for key, label in self.basic_labels.items():
            label.configure(text=self._format_label(key, self.basic[key](self.dataframe['Amount'])))

    @staticmethod
    def _format_label(key, value):
        return f'{key.capitalize()}: {value:.2f}'
