import customtkinter as ctk


class StringVarAble:
    def __init__(self, default=None, var=None):
        if var is None:
            var = {}
        kwargs = {'value': default} | var
        self.var = ctk.StringVar(**kwargs)

    def get(self):
        return self.var.get()

    def set(self, value):
        self.var.set(value)

    def serialize(self):
        return {'var': {'value': self.get()}}
