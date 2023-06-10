import customtkinter as ctk
import pandas as pd

from web_app.theme_colors import colors


class Filter(ctk.CTkFrame):
    def __init__(self, master, column_name, on_remove=None, on_change=None, series: pd.Series = None, **kwargs):
        super().__init__(master, **kwargs)
        self._series = series

        self.on_remove_callback = on_remove
        self.on_change_callback = on_change

        self.selected_column = ctk.CTkLabel(self, text=column_name, width=150, anchor='w')
        self.selected_column.grid(column=0, row=0, sticky='w', padx=5, pady=5)

        self.selector_frame = ctk.CTkFrame(self, height=10)
        self.selector_frame.grid(column=1, row=0, sticky="we", padx=5, pady=5)

        self.remove_button = ctk.CTkButton(self, text='-', width=30, command=self._on_remove)
        self.remove_button.grid(column=2, row=0, padx=5, pady=5)

        self.grid_columnconfigure(1, weight=1)
        # self.grid_columnconfigure((0, 2), weight=0)

    def _on_remove(self):
        self.destroy()
        self.on_remove_callback()

    def _on_change(self, *args):
        if self._is_valid_input():
            self.on_change_callback()

    def get_query(self):
        raise NotImplementedError('This function should be overriden')

    def _is_valid_input(self, is_valid=True):
        if not is_valid:
            self.configure(border_color=colors['error'], border_width=1)
        else:
            self.configure(border_width=0)
        return is_valid


class StringFilter(Filter):  # TODO: StringFilter does not seem to be working at the query stage
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.query = ctk.StringVar(value='')
        self.query.trace('w', self._on_change)
        self.entry = ctk.CTkEntry(self.selector_frame, textvariable=self.query)
        self.entry.grid(column=0, row=0, sticky='nswe', padx=5, pady=5)

        self.case_sensitive = ctk.BooleanVar(value=False)
        self.checkbox = ctk.CTkCheckBox(self.selector_frame, text="Case Sensetive", command=self._on_change,
                                        variable=self.case_sensitive, onvalue=True, offvalue=False)
        self.checkbox.grid(column=1, row=0, padx=5, pady=5)

        self.selector_frame.grid_columnconfigure(0, weight=1)
        self.selector_frame.grid_columnconfigure(1, weight=0)

    def _is_valid_input(self, is_valid=True):
        if len(self.query.get()) < 2:
            is_valid = False
        return super()._is_valid_input(is_valid=is_valid)

    def get_query(self):
        if self._is_valid_input():
            return lambda series: pd.Series.str.contains(series, self.entry.get(), case=self.case_sensitive.get())


class RangeFilter(Filter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.expected_type = float

        self.lower_bound = ctk.StringVar(value='')
        self.lower_bound.trace('w', self._on_change)
        self.lb_entry = ctk.CTkEntry(self.selector_frame, textvariable=self.lower_bound)
        self.lb_entry.grid(column=0, row=0, sticky='nswe', padx=5, pady=5)

        self.separator_label = ctk.CTkLabel(self.selector_frame, text=f'<  {self.selected_column.cget("text")}  <')
        self.separator_label.grid(column=1, row=0)

        self.upper_bound = ctk.StringVar(value='')
        self.upper_bound.trace('w', self._on_change)
        self.ub_entry = ctk.CTkEntry(self.selector_frame, textvariable=self.upper_bound)
        self.ub_entry.grid(column=2, row=0, sticky='nswe', padx=5, pady=5)

        self.selector_frame.grid_columnconfigure((0, 2), weight=3)
        self.selector_frame.grid_columnconfigure(1, weight=1)

    def _is_valid_input(self, is_valid=True):
        try:
            lower_bound, upper_bound = self._grab_bounds()
            if lower_bound is not None and upper_bound is not None and upper_bound < lower_bound:
                is_valid = False
        except (TypeError, ValueError) as e:
            is_valid = False

        return super()._is_valid_input(is_valid=is_valid)

    def _grab_bounds(self):
        lower_bound, upper_bound = self.lower_bound.get(), self.upper_bound.get()
        if lower_bound == '':
            lower_bound = None
        if upper_bound == '':
            upper_bound = None
        lower_bound = None if lower_bound is None else self.expected_type(lower_bound)
        upper_bound = None if upper_bound is None else self.expected_type(upper_bound)
        return lower_bound, upper_bound

    def get_query(self):
        if self._is_valid_input():
            lower_bound, upper_bound = self._grab_bounds()
            if lower_bound is not None and upper_bound is not None:
                return lambda series: (series >= lower_bound) & (series <= upper_bound)
            elif lower_bound is not None:
                return lambda series: series >= lower_bound
            elif upper_bound is not None:
                return lambda series: series <= upper_bound


class DateTimeFilter(RangeFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.expected_type = lambda v: pd.to_datetime(v, dayfirst=True)
        self.separator_label.configure(text=f'after  {self.selected_column.cget("text")}  before')


class CategoryFilter(Filter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.true_to_str_ref = {str(cat): cat for cat in self._series.unique()}
        self.categories = {str(cat): None for cat in self._series.unique()}

        self.include = ctk.BooleanVar(value=True)
        self.checkbox = ctk.CTkCheckBox(self.selector_frame, text="Include", command=self._on_change,
                                        variable=self.include, onvalue=True, offvalue=False)
        self.checkbox.pack(side='right', padx=5, pady=5)

        available_categories = self._get_unselected_categories()
        self.category_selected = ctk.StringVar(value=available_categories[0])
        self.category_options = ctk.CTkOptionMenu(
            self.selector_frame, values=available_categories, variable=self.category_selected
        )
        self.category_options.pack(side='right', padx=5, pady=5)

        self.new_filter_button = ctk.CTkButton(
            self.selector_frame, text='Select', command=self._add_category
        )
        self.new_filter_button.pack(side='right', padx=5, pady=5)

    def _is_valid_input(self, is_valid=True):
        if len(self._get_requested_categories()) == 0:
            is_valid = False
        return super()._is_valid_input(is_valid=is_valid)

    def get_query(self):
        if self._is_valid_input():
            return lambda series: pd.Series.isin(series, self._get_requested_categories())

    def _add_category(self):
        category = self.category_selected.get()
        self.categories[category] = ctk.CTkButton(
            self.selector_frame,
            text=category,
            command=lambda: self._remove_category(category),
            width=0
        )
        self.categories[category].pack(side='left', padx=5, pady=5)
        print('on change')
        self._on_change()
        self.update_options_menu()

    def _remove_category(self, category):
        self.categories[category].destroy()
        self.categories[category] = None
        self._on_change()
        self.update_options_menu()

    def _get_requested_categories(self):
        if self.include.get():
            return self._get_selected_categories()
        return self._get_unselected_categories()

    def _get_unselected_categories(self):
        return list(map(lambda kv: kv[0], filter(lambda kv: kv[1] is None, self.categories.items())))

    def _get_selected_categories(self):
        return list(map(lambda kv: kv[0], filter(lambda kv: kv[1] is not None, self.categories.items())))

    def update_options_menu(self):
        available_columns = self._get_unselected_categories()
        if available_columns:
            self.category_selected.set(available_columns[0])
            self.category_options.configure(values=available_columns, state='normal')
            self.new_filter_button.configure(state='normal')
        else:
            self.category_options.configure(state='disabled')
            self.new_filter_button.configure(state='disabled')
            self.category_selected.set("You've selected all of the categories")


type_mappings = {
    'string': StringFilter,
    'float64': RangeFilter,
    'int64': RangeFilter,
    'datetime64[ns]': DateTimeFilter,
    'category': CategoryFilter
}
