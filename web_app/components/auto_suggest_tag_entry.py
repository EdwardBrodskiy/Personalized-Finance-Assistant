import customtkinter as ctk

from web_app.components.auto_suggest_entry import AutoSuggestEntry
from web_app.components.notification import Notification
from web_app.ui.Button import Button


class AutoSuggestTagEntry(ctk.CTkFrame):
    def __init__(self, master, suggestions=None, selected=(), **kwargs):
        super().__init__(master, **kwargs)
        self.suggestions = suggestions

        self.grid_columnconfigure(1, weight=1)
        self.tags = {tag: None for tag in self.suggestions}

        self.entry = AutoSuggestEntry(self, suggestions=self._get_unselected_suggestions())
        self.entry.grid(column=0, row=0, sticky='news')

        self.tag_frame = ctk.CTkFrame(self)
        self.tag_frame.grid(column=1, row=0, sticky='we', padx=5, pady=2)

        self.entry.bind("<Shift-Return>", self._add_tag)

        for tag in selected:
            self._add_tag(tag=tag)

    def get(self):
        tag_states = []
        for key, tag in self.tags.items():
            if tag is not None:
                tag_states.append((key, tag.selection_state))
        return tag_states

    def insert(self, _, tags):
        for tag in tags:
            self._add_tag(tag=tag)

    def _add_tag(self, *args, tag=None):
        if tag is None:
            tag = self.entry.get()

        if tag in self._get_selected_suggestions():
            Notification(self, f'Tag {tag} is already added')
            return

        self.tags[tag] = TagButton(
            self.tag_frame,
            text=tag,
            command=lambda: self._remove_tag(tag),
            width=0
        )
        self.tags[tag].pack(side='left', padx=(0, 2))

        self.entry.suggestions = self._get_unselected_suggestions()

    def _remove_tag(self, tag):
        self.tags[tag].destroy()
        self.tags[tag] = None
        self.entry.suggestions = self._get_unselected_suggestions()

    def _get_unselected_suggestions(self):
        return list(map(lambda kv: kv[0], filter(lambda kv: kv[1] is None, self.tags.items())))

    def _get_selected_suggestions(self):
        return list(map(lambda kv: kv[0], filter(lambda kv: kv[1] is not None, self.tags.items())))

    def hide_suggestions(self):
        self.entry.hide_suggestions()


class TagButton(Button):
    def __init__(self, *args, selection_options=('', ' - 1', ' - 2'), **kwargs):
        super().__init__(*args, **kwargs)
        self._original_text = self.cget('text')
        self._selection_options = selection_options
        self._selection_state = 0

        self.bind("<Button-3>", self.change_selection)

    @property
    def selection_state(self):
        return self._selection_state

    @selection_state.setter
    def selection_state(self, value):
        if type(value) is int and 0 <= value < len(self._selection_options):
            self.selection_state = value
            self._update_button_state()
        else:
            raise IndexError(f'{value} is not a valid state index')

    def change_selection(self, *args):
        self._selection_state = (self._selection_state + 1) % len(self._selection_options)
        self._update_button_state()

    def _update_button_state(self, *args):
        super().configure(text=self._original_text + self._selection_options[self._selection_state])

    def configure(self, **kwargs):
        if 'text' in kwargs:
            self._original_text = kwargs['text']
            kwargs['text'] += self._selection_options[self._selection_state]
        super().configure(**kwargs)
