import customtkinter as ctk
import web_app.components.filters as filters


class Search(ctk.CTkFrame):
    def __init__(self, master, dataframe, **kwargs):
        super().__init__(master, **kwargs)

        self.dataframe = dataframe

        self.columns = {column: None for column in self.dataframe.columns}

        # new filter creation frame
        self.new_filter_frame = ctk.CTkFrame(self)
        self.new_filter_frame.pack(fill='x')

        available_columns = self._get_unfiltered_columns()
        self.column_selected = ctk.StringVar(value=available_columns[0])
        self.column_options = ctk.CTkOptionMenu(
            self.new_filter_frame, values=available_columns, variable=self.column_selected
        )
        self.column_options.grid(column=0, row=0, sticky="nsew", padx=5, pady=5)

        self.new_filter_button = ctk.CTkButton(
            self.new_filter_frame, text='Create New Filter', command=self._create_new_filter
        )
        self.new_filter_button.grid(column=1, row=0, padx=5, pady=5)

        self.new_filter_frame.grid_columnconfigure(0, weight=1)

        # filters frame
        self.filter_frame = ctk.CTkFrame(self)
        self.filter_frame.pack(fill='x')

    def _create_new_filter(self):
        column = self.column_selected.get()
        print(f'create new filter {column}')
        print(', '.join(map(str, self.dataframe.dtypes)))
        self.columns[column] = filters.type_mappings[str(self.dataframe.dtypes[column])](
            self.filter_frame,
            column,
            on_remove=lambda: self._remove_filter(column),
            on_change=self._filter_changed
        )
        self.columns[column].pack(fill='x')

        self.update_options_menu()

    def _remove_filter(self, name):
        self.columns[name] = None
        self._filter_changed()
        self.update_options_menu()

    def update_options_menu(self):
        available_columns = self._get_unfiltered_columns()
        if available_columns:
            self.column_selected.set(available_columns[0])
            self.column_options.configure(values=available_columns, state='normal')
            self.new_filter_button.configure(state='normal')
        else:
            self.column_options.configure(state='disabled')
            self.new_filter_button.configure(state='disabled')
            self.column_selected.set('All columns already have a filter!')


    def _get_unfiltered_columns(self):
        return list(map(lambda kv: kv[0], filter(lambda kv: kv[1] is None, self.columns.items())))

    def _filter_changed(self):
        print('filter changed')
