import customtkinter


class ErrorPopup(customtkinter.CTkToplevel):
    def __init__(self, master, error: Exception = "Something went wrong :(", **kwargs):
        super().__init__(master, **kwargs)
        self.geometry("+%d+%d" % self._get_window_center(master))
        self.title('Warning')
        self.lift()  # lift window on top
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.attributes("-topmost", True)  # stay on top
        self.attributes("-type", "dialog")
        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable

        self.label = customtkinter.CTkLabel(self, text=str(error))
        self.label.pack(padx=20, pady=20)

    def _on_closing(self):
        self.grab_release()
        self.destroy()

    def _get_window_center(self, tk_window):
        root = tk_window.winfo_toplevel()
        x = root.winfo_x()
        y = root.winfo_y()
        width = root.winfo_width()
        height = root.winfo_height()

        my_width = 400 # self.winfo_width()
        my_height = 200 # self.winfo_height()
        center = x + (width - my_width) // 2, y + (height - my_height) // 2

        return center
