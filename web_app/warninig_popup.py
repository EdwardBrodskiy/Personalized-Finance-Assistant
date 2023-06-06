import customtkinter


class WarningPopup(customtkinter.CTkToplevel):
    def __init__(self, master, message='', opta='', optb='', **kwargs):
        super().__init__(master, **kwargs)

        self.geometry("+%d+%d" % self._get_window_center(master))

        self.title('Warning')
        self.lift()  # lift window on top
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.attributes("-topmost", True)  # stay on top
        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable

        self._user_input = optb

        self.label = customtkinter.CTkLabel(self, text=message)
        self.label.grid(row=0, column=0, columnspan=2, padx=20, pady=20)

        self.opta = customtkinter.CTkButton(self, text=opta, command=self._ok_event)
        self.opta.grid(row=1, column=0)
        self.optb = customtkinter.CTkButton(self, text=optb, fg_color="transparent", border_width=2,
                                            text_color=("gray10", "#DCE4EE"), command=self._cancel_event)
        self.optb.grid(row=1, column=1)

    def _ok_event(self, event=None):
        self._user_input = self.opta.cget("text")
        self.grab_release()
        self.destroy()

    def _on_closing(self):
        self.grab_release()
        self.destroy()

    def _cancel_event(self):
        self.grab_release()
        self.destroy()

    def get_input(self):
        self.master.wait_window(self)
        return self._user_input

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
