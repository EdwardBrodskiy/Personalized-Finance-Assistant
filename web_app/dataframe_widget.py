import customtkinter


class DataFrameWidget(customtkinter.CTkFrame):
    def __init__(self, master, dataframe, row_of_interest, number_of_neighbors, **kwargs):
        super().__init__(master, **kwargs)

        self.dataframe = dataframe
        self.headers = []
        self.rows_of_labels = {}
        self.row_of_interest = row_of_interest
        self.number_of_neighbors = number_of_neighbors

        self.start_row = max(0, row_of_interest - number_of_neighbors)
        self.end_row = min(len(dataframe), row_of_interest + number_of_neighbors + 1)

        for column, column_name in enumerate(dataframe.columns):
            header_label = customtkinter.CTkLabel(self, text=column_name, fg_color='gray18')
            header_label.grid(row=0, column=column, sticky="nsew")
            self.headers.append(header_label)

        for row in range(self.start_row, self.end_row):
            data_row = dataframe.iloc[row]
            self.rows_of_labels[row] = []
            for column, value in enumerate(data_row):
                bg_color = "#2FA572" if row == row_of_interest else None
                label = customtkinter.CTkLabel(self, text=value, fg_color=bg_color)
                label.grid(row=row - self.start_row + 1, column=column, sticky="nsew")
                self.rows_of_labels[row].append(label)

        self.columnconfigure(list(range(len(dataframe.columns))), weight=1)
        self.rowconfigure(list(range(len(dataframe))), weight=1)

    def scroll_down_one_row(self):
        # Update row_of_interest and start_row, end_row
        self.row_of_interest += 1
        new_start_row = max(0, self.row_of_interest - self.number_of_neighbors)
        new_end_row = min(len(self.dataframe), self.row_of_interest + self.number_of_neighbors + 1)

        if new_start_row > self.start_row:
            # Remove the first row of labels
            first_row = self.rows_of_labels.pop(self.start_row)
            for label in first_row:
                label.destroy()

        for label in self.rows_of_labels[self.row_of_interest]:
            label.configure(fg_color="#2FA572")

        for label in self.rows_of_labels[self.row_of_interest - 1]:
            label.configure(fg_color='transparent')

        if new_end_row > self.end_row:
            # Add a new row at the end
            new_row = self.dataframe.iloc[self.end_row]
            self.rows_of_labels[self.end_row] = []
            for column, value in enumerate(new_row):
                label = customtkinter.CTkLabel(self, text=value)
                label.grid(row=new_end_row, column=column, sticky="nsew")
                self.rows_of_labels[self.end_row].append(label)

        self.start_row = new_start_row
        self.end_row = new_end_row
