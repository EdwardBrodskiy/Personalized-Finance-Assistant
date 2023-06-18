import customtkinter as ctk

from web_app.components.auto_suggest_entry import AutoSuggestEntry
from web_app.components.notification import Notification
from web_app.ui.Button import Button


class AutoSuggestTagEntry(ctk.CTkFrame):
    def __init__(self, master, suggestions=None, selected=(), on_change=None, tag_selection_options=('',),
                 suggestions_only=False, banned_tags=None, **kwargs):
        super().__init__(master, **kwargs)
        self._suggestions_only = suggestions_only
        self.suggestions = suggestions
        self._on_change = on_change
        self._tag_selection_options = tag_selection_options

        # Tag string : Reason
        self._banned_tags = {
            '': 'Empty tag is not allowed'
        }
        if banned_tags is not None:
            self._banned_tags = self._banned_tags | banned_tags

        self.suggestions = [tag for tag in self.suggestions if tag not in self._banned_tags]

        self.grid_columnconfigure(2, weight=1)
        self.tags = {tag: None for tag in self.suggestions}

        self.entry = AutoSuggestEntry(self, suggestions=self._get_unselected_suggestions())
        self.entry.grid(column=0, row=0, sticky='news', padx=6, pady=12)

        self.enter = Button(self, text='+', width=30, command=self._add_tag)
        self.enter.grid(column=1, row=0, sticky='news', padx=6, pady=12)

        self.tag_frame = ctk.CTkScrollableFrame(self, height=self.entry.winfo_reqheight() - 14, width=500,
                                                orientation='horizontal')
        self.tag_frame.grid(column=2, row=0, sticky='news', padx=5, pady=2)

        self.entry.bind("<Shift-Return>", self._add_tag)

        for tag in selected:
            self._add_tag(tag=tag)

    def get(self, key_only=False):
        if key_only or len(self._tag_selection_options) == 1:
            return [key for key, tag in self.tags.items() if tag is not None]
        tag_states = []
        for key, tag in self.tags.items():
            if tag is not None:
                tag_states.append((key, tag.selection_state))
        return tag_states

    def insert(self, _, tags):
        for tag in tags:
            self._add_tag(tag=tag)

    def _add_tag(self, *args, tag=None):
        tag_was_none = tag is None
        state = 0
        if tag_was_none:
            tag = self.entry.get()
        elif type(tag) is list:
            tag, state = tag
        if tag in self._get_selected_suggestions():
            Notification(self, f'Tag "{tag}" is already added')
            return
        if tag in self._banned_tags:
            Notification(self, self._banned_tags[tag])
            return
        if self._suggestions_only and tag not in self.suggestions:
            Notification(self, f'Tag "{tag}" does not exist')
            return

        self.tags[tag] = TagButton(
            self.tag_frame,
            text=tag,
            command=lambda: self._remove_tag(tag),
            width=0,
            selection_options=self._tag_selection_options,
            on_state_change=self._on_change,
            initial_selection=state,
        )
        self.tags[tag].pack(side='left', padx=(0, 2))

        self.entry.suggestions = self._get_unselected_suggestions()

        self.entry.set('')
        if tag_was_none and self._on_change is not None:
            self._on_change()

    def _remove_tag(self, tag):
        self.tags[tag].destroy()
        self.tags[tag] = None
        self.entry.suggestions = self._get_unselected_suggestions()
        self._on_change()

    def _get_unselected_suggestions(self):
        return list(map(lambda kv: kv[0], filter(lambda kv: kv[1] is None, self.tags.items())))

    def _get_selected_suggestions(self):
        return list(map(lambda kv: kv[0], filter(lambda kv: kv[1] is not None, self.tags.items())))

    def hide_suggestions(self):
        self.entry.hide_suggestions()


class TagButton(Button):
    def __init__(self, *args, initial_selection=0, selection_options=('',), on_state_change=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_text = self.cget('text')
        self._selection_options = selection_options
        self._selection_state = initial_selection
        self._on_state_change = on_state_change

        self.selection_state = initial_selection

        self.bind("<Button-3>", self.change_selection)

    @property
    def selection_state(self):
        return self._selection_state

    @selection_state.setter
    def selection_state(self, value):
        if type(value) is int and 0 <= value < len(self._selection_options):
            self._selection_state = value
            self._update_button_state()
        else:
            raise IndexError(f'{value} is not a valid state index')

    def change_selection(self, *args):
        self._selection_state = (self._selection_state + 1) % len(self._selection_options)
        self._update_button_state()
        if self._on_state_change is not None:
            self._on_state_change()

    def _update_button_state(self, *args):
        super().configure(text=self._original_text + self._selection_options[self._selection_state])

    def configure(self, **kwargs):
        if 'text' in kwargs:
            self._original_text = kwargs['text']
            kwargs['text'] += self._selection_options[self._selection_state]
        super().configure(**kwargs)
