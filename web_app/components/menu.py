import customtkinter

'''
sheet
key: field name

tuple:
type: Button | Slider | OptionMenu | Toggle 
label_text: string
kwargs: {command etc.}
'''


class Toggle(customtkinter.CTkSwitch):
    def __init__(self, master, default='off', **kwargs):
        self.switch_var = customtkinter.StringVar(value=default)
        super().__init__(master, text='', onvalue='on', offvalue='off', variable=self.switch_var, **kwargs)

    def state(self):
        return self.switch_var.get()

    def set_state(self, value):
        if value not in ('on', 'off'):
            raise Exception(f'Invalid state {value} only on or off permitted')
        self.switch_var.set(value)


class Menu(customtkinter.CTkFrame):
    elements_mapping = {
        'Button': customtkinter.CTkButton,
        'Slider': customtkinter.CTkSlider,
        'OptionMenu': customtkinter.CTkOptionMenu,
        'Entry': customtkinter.CTkEntry,
        'Toggle': Toggle
    }

    def __init__(self, master, sheet, title='', **kwargs):
        super().__init__(master, **kwargs)
        self.title = None
        self.title_offset = 0
        if title:
            self.frame = customtkinter.CTkFrame(self)
            self.frame.grid(row=0, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
            self.title = customtkinter.CTkLabel(self.frame, text=title)
            self.title.pack(fill='both')
            self.title_offset = 1
        self.elements = {}
        self.sheet = sheet

    @property
    def sheet(self):
        return self._sheet

    @sheet.setter
    def sheet(self, value):
        self._sheet = value
        self.generate_elements()

    def generate_elements(self):
        for child in self.elements.values():
            child.destroy()
        self.elements = {}

        self.grid_rowconfigure(list(range(len(self.sheet) + self.title_offset)), weight=1)  # configure grid system
        self.grid_columnconfigure((0, 1), weight=1)
        for index, (key, settings) in enumerate(self.sheet.items()):
            element_type, text, kwargs = settings
            self.elements[key] = (
                customtkinter.CTkLabel(self, text=text),
                self.elements_mapping[element_type](self, width=50, **kwargs)
            )
            self.elements[key][0].grid(row=index + self.title_offset, column=0, sticky='w', padx=5, pady=5)
            self.elements[key][1].grid(row=index + self.title_offset, column=1, sticky='e', padx=5, pady=5)
