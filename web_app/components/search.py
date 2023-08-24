import json
import os

import customtkinter as ctk
import pandas as pd

import web_app.components.filters as filters
from helper_functions import ensure_dir_exists
from web_app.components.notification import Notification
from web_app.popups.warning_popup import WarningPopup


class Search(ctk.CTkFrame):
    saves_path = os.path.join('app_storage', 'search_states')

    def __init__(self, master, dataframe: pd.DataFrame, search_id='global', on_search=None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_search = on_search
        self.dataframe = dataframe
        self.search_id = search_id
        ensure_dir_exists(os.path.join(self.saves_path, self.search_id))

        self.columns = {column: None for column in self.dataframe.columns}

        # controls
        self.controls = ctk.CTkFrame(self)
        self.controls.pack(fill='x')
        self.controls.grid_columnconfigure(1, weight=1)
        # save and load controls
        self.save_and_load_controls = ctk.CTkFrame(self.controls)
        self.save_and_load_controls.grid(column=0, row=0, sticky='w')

        self.save = ctk.CTkButton(self.save_and_load_controls, text='Save as', command=self._save_as)
        self.save.pack(side='left', padx=5, pady=5)

        self.load = ctk.CTkButton(self.save_and_load_controls, text='Load', command=self._load)
        self.load.pack(side='left', padx=5, pady=5)

        self.delete = ctk.CTkButton(self.save_and_load_controls, text='Delete', command=self._delete)
        self.delete.pack(side='left', padx=5, pady=5)

        files_found = self._get_saves()
        self.file_name = ctk.StringVar(value=files_found[0] if len(files_found) else '')
        self.file_name_options = ctk.CTkComboBox(self.save_and_load_controls, values=files_found,
                                                 variable=self.file_name, width=250)
        self.file_name_options.pack(side='left', padx=5, pady=5)

        # new filter creation frame
        self.new_filter_frame = ctk.CTkFrame(self.controls)
        self.new_filter_frame.grid(column=2, row=0, sticky='e')

        available_columns = self._get_unfiltered_columns()
        self.column_selected = ctk.StringVar(value=available_columns[0])
        self.column_options = ctk.CTkOptionMenu(
            self.new_filter_frame, values=available_columns, variable=self.column_selected, width=250
        )
        self.column_options.grid(column=0, row=0, sticky="nsew", padx=5, pady=5)

        self.new_filter_button = ctk.CTkButton(
            self.new_filter_frame, text='Create New Filter', command=self._create_new_filter
        )
        self.new_filter_button.grid(column=1, row=0, padx=5, pady=5)

        self.new_filter_frame.grid_columnconfigure(0, weight=1)

        # filters frame
        self.filter_frame = ctk.CTkFrame(self, height=0)
        self.filter_frame.pack(fill='x')

    def _create_new_filter(self, load_data=None):
        column = self.column_selected.get()
        self.columns[column] = filters.type_mappings[str(self.dataframe.dtypes[column])](
            self.filter_frame,
            column,
            on_remove=lambda: self._remove_filter(column),
            on_change=self._filter_changed,
            series=self.dataframe[column],
            load_state=load_data
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
        selected_items = self.dataframe.copy()
        for column, filter_element in self.columns.items():

            if filter_element is None:
                continue
            query = filter_element.get_query()
            if query is None:
                continue
            selected_items = selected_items[query(selected_items[column])]

        self.on_search(selected_items)

    def _clear_all_filters(self):
        for column, filter_element in self.columns.items():
            if filter_element is None:
                continue
            filter_element.destroy()
            self.columns[column] = None

    def _save_as(self):
        file_name = self.file_name.get()
        if file_name == '':
            Notification(self, 'Please specify name.')
            return
        if '.' in file_name:
            Notification(self, 'No need to specify file type')
            return
        if file_name in self._get_saves():
            check = WarningPopup(self, message=f'Are you sure you want to overwrite {file_name}', opta='Yes Overwrite',
                                 optb='No')
            if check.get_input() == 'No':
                return

        filter_settings = {}
        for column, filter_element in self.columns.items():
            if filter_element is None:
                continue
            filter_settings[column] = filter_element.serialize()

        path = os.path.join(self.saves_path, self.search_id, file_name + '.json')

        with open(path, 'w+') as file:
            json.dump(filter_settings, file, indent=2)

        Notification(self, f'Search saved to {file_name}')

        self._update_file_options()
        if self.on_search is not None:
            self.on_search()

    def _load(self):
        file_name = self.file_name.get()
        if file_name not in self._get_saves():
            Notification(self, 'Please specify existing file name')
            return
        path = os.path.join(self.saves_path, self.search_id, file_name + '.json')
        with open(path, 'r') as file:
            filter_settings = json.load(file)

        self._clear_all_filters()

        for column, load_values in filter_settings.items():
            self.column_selected.set(column)
            self._create_new_filter(load_data=load_values)
        self._filter_changed()

        self._update_file_options()

    def _delete(self):
        file_name = self.file_name.get()
        if file_name not in self._get_saves():
            Notification(self, 'Please specify existing file name')
            return
        if file_name in self._get_saves():
            check = WarningPopup(self, message=f'Are you sure you want to delete {file_name}', opta='Yes Delete',
                                 optb='No')
            if check.get_input() == 'No':
                return

        path = os.path.join(self.saves_path, self.search_id, file_name + '.json')
        os.remove(path)

        self._update_file_options()
        self.file_name.set('')

    def _update_file_options(self):
        self.file_name_options.configure(values=self._get_saves())

    def _get_saves(self):

        path = os.path.join(self.saves_path, self.search_id)
        try:
            return [f[:-5] for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f[-5:] == '.json']
        except FileNotFoundError:
            os.makedirs(path)
            return []
