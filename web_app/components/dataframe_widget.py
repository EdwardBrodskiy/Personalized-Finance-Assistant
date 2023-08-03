import customtkinter
import logging
from web_app.theme_colors import colors


class DataFrameWidget(customtkinter.CTkFrame):
    def __init__(self, master, dataframe, row_of_interest, number_of_neighbors, **kwargs):
        super().__init__(master, **kwargs)

        self.dataframe = dataframe
        self.headers = []
        self.rows_of_labels = {}
        self.row_of_interest = row_of_interest
        self.number_of_neighbors = number_of_neighbors

        self.start_row = max(0, row_of_interest - number_of_neighbors)
        self.end_row = min(len(dataframe)-1, row_of_interest + number_of_neighbors)

        for column, column_name in enumerate(dataframe.columns):
            header_label = customtkinter.CTkLabel(self, text=column_name, fg_color='gray18')
            header_label.grid(row=0, column=column, sticky="nsew")
            self.headers.append(header_label)

        self._for_rows(self.start_row, self.end_row, self._draw_row)

        self.columnconfigure(list(range(len(dataframe.columns))), weight=1)
        self.rowconfigure(list(range(len(dataframe))), weight=1)

    def try_scroll(self, offset):
        if offset == 0:
            return False
        # Update row_of_interest and start_row, end_row
        new_row_of_interest = self._clamp(self.row_of_interest + offset)
        new_start_row = self._clamp(new_row_of_interest - self.number_of_neighbors)
        new_end_row = self._clamp(new_row_of_interest + self.number_of_neighbors)

        destroy_start, destroy_end = 0, 0
        create_start, create_end = 0, 0
        color_start, color_end = 0, 0
        if offset > 0:
            destroy_start = self.start_row
            destroy_end = new_start_row-1

            create_start = self.end_row+1
            create_end = new_end_row

            color_start = self.row_of_interest
            color_end = new_row_of_interest-1

        elif offset < 0:
            destroy_start = new_end_row+1
            destroy_end = self.end_row

            create_start = new_start_row
            create_end = self.start_row-1

            color_start = new_row_of_interest+1
            color_end = self.row_of_interest

        self._for_rows(destroy_start, destroy_end, self._destroy_row)
        self._for_rows(create_start, create_end, self._draw_row)
        self._for_rows(color_start, color_end,
                       lambda i: self._color_row(i, 'transparent'))

        self._color_row(new_row_of_interest, colors['primary'])

        hasScrolled = (
                new_start_row != self.row_of_interest or
                new_start_row != self.start_row or
                new_end_row != self.end_row
                )

        self.row_of_interest = new_row_of_interest
        self.start_row = new_start_row
        self.end_row = new_end_row

        return hasScrolled

    def _for_rows(self, start_index, end_index, function):
        for i in range(start_index, end_index+1):
            function(i)

    def _draw_row(self, row_index):
        row = self.dataframe.iloc[row_index]
        self.rows_of_labels[row_index] = []
        tkGridRow = row_index + 1
        for column, value in enumerate(row):
            bg_color = colors['primary'] if row_index == self.row_of_interest else None
            label = customtkinter.CTkLabel(self, text=value, fg_color=bg_color)
            label.grid(row=tkGridRow, column=column, sticky="nsew")
            self.rows_of_labels[row_index].append(label)

    def _destroy_row(self, row_index):
        if row_index not in self.rows_of_labels:
            logging.error(f"Unable to delete {row_index}, is your scroll offset larger than number_of_neighbors?")
            return
        row = self.rows_of_labels.pop(row_index)
        for label in row:
            label.destroy()

    def _color_row(self, row_index, color):
        if row_index not in self.rows_of_labels:
            return
        for label in self.rows_of_labels[row_index]:
            label.configure(fg_color=color)

    def _clamp(self, x):
        return self._clamp_range(0, len(self.dataframe)-1, x)

    def _clamp_range(self, lower, upper, x):
        return max(lower, min(upper, x))
