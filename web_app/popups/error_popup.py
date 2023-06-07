import customtkinter


class ErrorPopup(customtkinter.CTkToplevel):
    def __init__(self, *args, error: Exception = "Something went wrong :(", **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry()

        self.label = customtkinter.CTkLabel(self, text=str(error))
        self.label.pack(padx=20, pady=20)
