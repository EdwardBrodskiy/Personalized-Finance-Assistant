import customtkinter as ctk

from .function_classes import StringVarAble


class OptionMenu(StringVarAble, ctk.CTkOptionMenu):

    def __init__(self, master, var=None, default=None, **kwargs):
        StringVarAble.__init__(self,  var=var, default=default)
        ctk.CTkOptionMenu.__init__(self, master, variable=self.var, **kwargs)

    def get(self):
        return self.var.get()

    def set(self, value):
        self.var.set(value)
