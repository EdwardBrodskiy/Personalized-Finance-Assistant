import customtkinter

from web_app.components.dataframe_widget import DataFrameWidget
from web_app.helper_functions import ordinal
from web_app.ingest_page.row_entry import RowEntry


class IngestProcess(customtkinter.CTkScrollableFrame):
    def __init__(self, master, classifier, **kwargs):
        super().__init__(master, **kwargs)
        self.classifier = classifier

        # setup edit tracking
        self.interest_row = 0

        # Entry

        self.row_entry = RowEntry(self, on_enter=self.data_entered)
        self.row_entry.pack(fill='both', expand=True)

        # Reference
        df_reference_table = self.classifier.un_labeled.copy()
        df_reference_table['Date'] = df_reference_table['Date'].apply(
            lambda x: ordinal(x.day) + x.strftime(' %b %Y'))
        # TODO: Add checks for columns like account name drop them only if there is only one value present
        df_reference_table = df_reference_table[['ref', 'Date', 'Type', 'Description_x', 'Value', 'Balance']]
        df_reference_table = df_reference_table.rename({'Description_x': 'Description'})
        self.reference_table = DataFrameWidget(self, df_reference_table, self.interest_row, 2)
        self.reference_table.pack(fill='both', expand=True)

        self.row_entry.add_entry_row_at(*self.classifier.get_entry_prerequisites_for_manual_entry(self.interest_row))

    def data_entered(self, data):
        if data is not None:
            self.classifier.process_incoming_input(data)

        self.interest_row += 1
        self.row_entry.add_entry_row_at(*self.classifier.get_entry_prerequisites_for_manual_entry(self.interest_row))

        self.reference_table.scroll_down_one_row()

        # move scroll to the end
        self.update_idletasks()
        self._parent_canvas.yview_moveto(1)
