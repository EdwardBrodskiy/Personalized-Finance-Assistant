import json
import os

import customtkinter

import theme_tk as ttk
from helper_functions import ensure_dir_exists
from web_app.components.auto_suggest_tag_entry import AutoSuggestTagEntry

'''
sheet
key: field name

tuple:
type: Button | Slider | OptionMenu | Toggle 
label_text: string
kwargs: {command etc.}
'''


class Menu(customtkinter.CTkFrame):
    elements_mapping = {
        'Button': customtkinter.CTkButton,
        'OptionMenu': ttk.OptionMenu,
        'Entry': ttk.Entry,
        'Toggle': ttk.Toggle,
        'TagEntry': AutoSuggestTagEntry
    }

    def __init__(self, master, sheet, title='', load_from_save=True, **kwargs):
        super().__init__(master, **kwargs)
        # handle title
        self.title = None
        self.title_offset = 0
        if title:
            self.frame = customtkinter.CTkFrame(self)
            self.frame.grid(row=0, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
            self.title = customtkinter.CTkLabel(self.frame, text=title)
            self.title.pack(fill='both')
            self.title_offset = 1

        # Setup save variables
        self.save_key = '-'.join(sheet.keys())
        self.load_from_save = load_from_save

        self.elements = {}
        self.sheet = sheet

    @property
    def sheet(self):
        return self._sheet

    @sheet.setter
    def sheet(self, value):
        self._sheet = value
        self.generate_elements()

    def __getitem__(self, key):
        return self.elements[key][1]

    def generate_elements(self):
        load_data = {}
        if self.load_from_save:
            self.load_from_save = False
            load_data = self._load_from_json()
        for child in self.elements.values():
            child.destroy()
        self.elements = {}

        self.grid_rowconfigure(len(self.sheet) + self.title_offset, weight=1)  # configure grid system
        self.grid_columnconfigure(1, weight=1)
        for index, (key, settings) in enumerate(self.sheet.items()):
            element_type, text, kwargs = settings
            full_kwargs = kwargs | {'command': lambda *_: self.on_change(key)}
            if key in load_data:
                full_kwargs = full_kwargs | load_data[key]
            self.elements[key] = (
                customtkinter.CTkLabel(self, text=text, width=len(text)),
                self.elements_mapping[element_type](self, **full_kwargs)
            )
            self.elements[key][0].grid(row=index + self.title_offset, column=0, sticky='w', padx=5, pady=5)
            self.elements[key][1].grid(row=index + self.title_offset, column=1, sticky='e', padx=5, pady=5)

    def on_change(self, key):
        path = os.path.join('app_storage', 'menu_states', f'{self.save_key}.json')
        ensure_dir_exists(path)
        with open(path, 'w+') as file:
            json.dump(self.serialize(), file, indent=2)

        # TODO: strange bug most obvious in copy from protected section of db manager where not the correct command runs
        if 'command' in self.sheet[key][2]:
            self.sheet[key][2]['command']()

    def _load_from_json(self):
        path = os.path.join('app_storage', 'menu_states', f'{self.save_key}.json')
        ensure_dir_exists(path)
        try:
            with open(path) as file:
                load_data = json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
            load_data = {}
        return load_data

    def serialize(self):
        save_data = {}
        for key, element in self.elements.items():
            try:
                save_data[key] = element[1].serialize()
            except AttributeError as e:
                save_data[key] = {}
        return save_data
