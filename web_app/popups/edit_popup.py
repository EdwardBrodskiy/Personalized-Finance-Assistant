import customtkinter


class EditPopup(customtkinter.CTkToplevel):
    def __init__(self, master, edit_vars=None, read_only_keys=(), on_edit=None, **kwargs):
        if edit_vars is None:
            return
        super().__init__(master, **kwargs)

        self.geometry("+%d+%d" % self._get_window_center(master))

        self.title('Edit')
        self.lift()  # lift window on top
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.attributes("-topmost", True)  # stay on top
        self.attributes("-type", "dialog")
        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable

        self.edit_vars = edit_vars
        self.edit_fields_container = customtkinter.CTkFrame(self, fg_color="transparent")
        self.edit_fields_container.grid(row=0, columnspan=2)
        self.edit_widgets = {}
        self.read_only_keys = read_only_keys
        self._create_edit_fields(self.edit_vars, self.edit_widgets, self.edit_fields_container)


        self.on_edit = on_edit

        self.cancel_button = customtkinter.CTkButton(self, text="Cancel", fg_color="transparent", border_width=2,
                                                     text_color=("gray10", "#DCE4EE"), command=self._cancel_event)
        self.cancel_button.grid(row=1, column=0)
        self.ok_button = customtkinter.CTkButton(self, text="Submit", command=self._edit_event)
        self.ok_button.grid(row=1, column=1)

    def _edit_event(self, event=None):
        self._update_edit_vars(self.edit_vars, self.edit_widgets)

        if self.on_edit is not None:
            self.on_edit()

        self.grab_release()
        self.destroy()

    def _update_edit_vars(self, edit_vars, edit_widgets):
        for key, val in edit_widgets.items():
            if type(val) is dict:
                self._update_edit_vars(edit_vars[key], val)
                continue
            edit_vars[key] = val.get()

    def _on_closing(self):
        self.grab_release()
        self.destroy()

    def _cancel_event(self):
        self.grab_release()
        self.destroy()

    def _create_edit_fields(self, edit_vars, edit_widgets, container):
        if type(edit_vars) is list:
            iterator = enumerate(edit_vars)
            is_list = True
        elif type(edit_vars) is dict:
            iterator = edit_vars.items()
            is_list = False

        for row, (key, val) in enumerate(iterator):
            key_string = f"{key}"
            if is_list:
                key_string = ""

            if type(val) in (list, dict):
                if not is_list:
                    key_string = f"{key_string}: "

                edit_widgets[key] = {}
                label = customtkinter.CTkLabel(container, text=key_string)
                label.grid(row=row, column=0)
                new_container = customtkinter.CTkFrame(container)
                new_container.grid(row=row, column=1, padx=10, pady=10)

                self._create_edit_fields(val, edit_widgets[key], new_container)
                continue
            edit_widgets[key] = self._create_edit_field(container, row, key_string, val,
                                                        read_only=key in self.read_only_keys)

    def _create_edit_field(self, container, row, label, value=None, read_only=False):
        entry_state = "disabled" if read_only else "normal"

        label = customtkinter.CTkLabel(container, text=label)
        label.grid(row=row, column=0)
        entry = customtkinter.CTkEntry(container)
        entry.grid(row=row, column=1)
        if value is not None:
            entry.insert(0, value)
        entry.configure(state=entry_state)
        return entry

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
