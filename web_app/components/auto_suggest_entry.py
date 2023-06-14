import customtkinter as ctk


class AutoSuggestEntry(ctk.CTkEntry):
    def __init__(self, master, suggestions=None, max_suggestions=6, **kwargs):
        super().__init__(master, **kwargs)
        self.max_suggestions=max_suggestions
        self._suggestions = suggestions if suggestions else []
        self.var = ctk.StringVar()
        self.configure(textvariable=self.var)
        self.var.trace_add("write", self.show_suggestions)
        self.labels_frame = None
        self.suggested = ()
        self.selected_label_index = -1
        self.bind("<FocusOut>", self.hide_suggestions)
        self.bind('<FocusIn>', self.show_suggestions)
        self.bind("<Up>", self.move_selection_up)
        self.bind("<Down>", self.move_selection_down)
        self.bind("<Return>", self.select_suggestion)

    def set(self, value):
        self.var.set(value)
        self.icursor(ctk.END)
        self.hide_suggestions()
    @property
    def suggestions(self):
        return self._suggestions

    @suggestions.setter
    def suggestions(self, value):
        self._suggestions = value
        if self.winfo_children():
            self.show_suggestions()

    def show_suggestions(self, *args):
        self.selected_label_index = -1
        if not self.labels_frame:
            self.labels_frame = ctk.CTkFrame(self.winfo_toplevel(), fg_color='transparent', height=0)
            self.labels_frame.place(in_=self, relx=0.0, rely=1.0, bordermode="outside")

            self.labels_frame.grid_columnconfigure(0, weight=1)

        for widget in self.labels_frame.winfo_children():
            widget.destroy()

        query = self.var.get().lower()
        suggestions = [word for word in self.suggestions if word.lower().startswith(query)][:self.max_suggestions]

        self.suggested = tuple(suggestions)
        for index, suggestion in enumerate(suggestions):
            label = ctk.CTkLabel(self.labels_frame, text=suggestion, padx=3, pady=3,
                                 width=self.labels_frame.cget('width'),
                                 anchor='w')
            label.bind("<Button-1>", lambda event, text=suggestion: self.select_suggestion(event, text))
            label.bind("<Enter>", lambda event, index=index: self.highlight_label(index))
            label.bind("<Leave>", lambda event: self.highlight_label(-1))
            label.grid(row=index, column=0, sticky="w")

        self.move_selection_down(None)

    def hide_suggestions(self, event=None):
        if self.labels_frame:
            self.labels_frame.destroy()
            self.labels_frame = None

    def move_selection_up(self, event):
        if self.labels_frame:
            self.selected_label_index -= 1
            self.selected_label_index = max(self.selected_label_index, 0)
            self.highlight_label(self.selected_label_index)

    def move_selection_down(self, event):
        if self.labels_frame:
            self.selected_label_index += 1
            self.selected_label_index = min(self.selected_label_index, len(self.labels_frame.winfo_children()) - 1)
            self.highlight_label(self.selected_label_index)

    def select_suggestion(self, event=None, text=None):
        if self.labels_frame and (self.selected_label_index >= 0 or text):
            if not text:
                text = self.suggested[self.selected_label_index]
            self.set(text)
            self.hide_suggestions()

    def highlight_label(self, index):
        for label in self.labels_frame.winfo_children():
            if index == label.grid_info()["row"]:
                label.configure(fg_color="#106A43")
            else:
                label.configure(fg_color="transparent")

    def destroy(self):
        ctk.CTkEntry.destroy(self)
        self.hide_suggestions(None)


def get_position(window, widget):
    x, y = widget.winfo_x(), widget.winfo_y()
    while widget.master != window:
        widget = widget.master
        x += widget.winfo_x()
        y += widget.winfo_y()

    return x, y
