import customtkinter as ctk

from .function_classes import StringVarAble


class Entry(StringVarAble, ctk.CTkEntry):
    def __init__(self, master, var=None, default=None, **kwargs):
        StringVarAble.__init__(self, var=var, default=default)
        if 'command' in kwargs:
            self.var.trace_add('write', kwargs['command'])
            del kwargs['command']
        ctk.CTkEntry.__init__(self, master, textvariable=self.var, **kwargs)
