import customtkinter as ctk

from .function_classes import StringVarAble


class Toggle(StringVarAble, ctk.CTkSwitch):
    def __init__(self, master, default='off', var=None, **kwargs):
        StringVarAble.__init__(self, default=default, var=var)
        ctk.CTkSwitch.__init__(self, master, text='', onvalue='on', offvalue='off', variable=self.var, **kwargs)

    def set(self, value):
        if value not in ('on', 'off'):
            raise Exception(f'Invalid state {value} only on or off permitted')
        super().set(value)
