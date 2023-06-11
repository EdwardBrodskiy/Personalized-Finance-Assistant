import customtkinter as ctk

from web_app.components.auto_suggest_entry import AutoSuggestEntry


class AutoSuggestTagEntry(ctk.CTkFrame):
    def __init__(self, master, suggestions_pane, suggestions=None, selected=(), **kwargs):
        super().__init__(master, **kwargs)
        self.suggestions = suggestions

        self.grid_columnconfigure(1, weight=1)
        self.tags = {tag: None for tag in self.suggestions}

        self.entry = AutoSuggestEntry(self, suggestions_pane, suggestions=self._get_unselected_suggestions())
        self.entry.grid(column=0, row=0, sticky='we')

        self.tag_frame = ctk.CTkFrame(self)
        self.tag_frame.grid(column=1, row=0, sticky='we')

        for tag in selected:
            self._add_tag(tag)

    def insert(self, _, tags):
        for tag in tags:
            self._add_tag(tag)

    def _add_tag(self, tag=None):
        if tag is None:
            tag = self.entry.get()

        self.tags[tag] = ctk.CTkButton(
            self.tag_frame,
            text=tag,
            command=lambda: self._remove_tag(tag),
            width=0
        )
        self.tags[tag].pack(side='left')

        self.entry.suggestions = self._get_unselected_suggestions()

    def _remove_tag(self, tag):
        self.tags[tag].destroy()
        self.tags[tag] = None
        self.entry.suggestions = self._get_unselected_suggestions()

    def _get_unselected_suggestions(self):
        return list(map(lambda kv: kv[0], filter(lambda kv: kv[1] is None, self.tags.items())))

    def _get_selected_suggestions(self):
        return list(map(lambda kv: kv[0], filter(lambda kv: kv[1] is None, self.tags.items())))

    def hide_suggestions(self):
        self.entry.hide_suggestions()
