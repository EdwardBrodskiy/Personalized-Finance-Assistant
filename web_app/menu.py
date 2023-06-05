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
        super().__init__(self, master, text='', onvalue='on', offvalue='off', variable=self.switch_var, **kwargs)


class Menu(customtkinter.CTkFrame):
    elements_mapping = {
        'Button': customtkinter.CTkButton,
        'Slider': customtkinter.CTkSlider,
        'OptionMenu': customtkinter.CTkOptionMenu,
        'Toggle': Toggle
    }

    def __init__(self, master, sheet, **kwargs):
        super().__init__(master, **kwargs)

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
        self.elements = {}
        for child in self.winfo_children():
            child.destroy()

        self.grid_rowconfigure(len(self.sheet), weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)
        for index, (key, settings) in enumerate(self.sheet.items()):
            element_type, text, kwargs = settings
            self.elements[key] = (
                customtkinter.CTkLabel(self, text=text),
                self.elements_mapping[element_type](self, **kwargs)
            )
            self.elements[key][0].grid(row=index, column=0)
            self.elements[key][1].grid(row=index, column=1)
