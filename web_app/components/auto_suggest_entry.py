import customtkinter


class AutoSuggestEntry(customtkinter.CTkEntry):
    def __init__(self, master, suggestions_pane, suggestions=None, **kwargs):
        super().__init__(master, **kwargs)
        self.suggestions_pane = suggestions_pane
        self.suggestions = suggestions if suggestions else []
        self.var = customtkinter.StringVar()
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

    def show_suggestions(self, *args):
        self.selected_label_index = -1
        if not self.labels_frame:
            self.labels_frame = customtkinter.CTkFrame(self.suggestions_pane, fg_color='transparent')
            self.labels_frame.pack()

            self.labels_frame.grid_columnconfigure(0, weight=1)

        for widget in self.labels_frame.winfo_children():
            widget.destroy()

        query = self.var.get().lower()
        suggestions = [word for word in self.suggestions if word.lower().startswith(query)]

        self.suggested = tuple(suggestions)
        for index, suggestion in enumerate(suggestions):
            label = customtkinter.CTkLabel(self.labels_frame, text=suggestion, padx=3, pady=3,
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
            self.var.set(text)
            self.icursor(customtkinter.END)
            self.hide_suggestions()

    def highlight_label(self, index):
        for label in self.labels_frame.winfo_children():
            if index == label.grid_info()["row"]:
                label.configure(fg_color="#106A43")
            else:
                label.configure(fg_color="transparent")

    def destroy(self):
        customtkinter.CTkEntry.destroy(self)
        self.hide_suggestions(None)
