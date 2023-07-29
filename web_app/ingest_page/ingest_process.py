import customtkinter

from configuration import get_gui_settings
from web_app.components.dataframe_widget import DataFrameWidget
from helper_functions import ordinal
from web_app.components.notification import Notification
from web_app.ingest_page.row_entry import RowEntry


class IngestProcess(customtkinter.CTkScrollableFrame):
    def __init__(self, master, classifier, end_process=None, **kwargs):
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
        df_reference_table = df_reference_table.rename({f'Description{self.classifier.db.suffixes[0]}': 'Description'})
        df_reference_table = df_reference_table[get_gui_settings()['classification columns to show']]

        self.reference_table = DataFrameWidget(self, df_reference_table, self.interest_row, 2)
        self.reference_table.pack(fill='both', expand=True)

        self.last_entry_row = self.classifier.get_entry_prerequisites_for_manual_entry(self.interest_row)
        self.row_entry.add_entry_row_at(*self.last_entry_row)

    def data_entered(self, data):
        if data is not None:
            self.classifier.process_incoming_input(data)

        if self.reference_table.try_scroll(1):
            self.interest_row += 1
            self.last_entry_row = self.classifier.get_entry_prerequisites_for_manual_entry(self.interest_row)
            self.row_entry.add_entry_row_at(*self.last_entry_row)
        else:
            self.row_entry.add_entry_row_at(*self.last_entry_row)

        # move scroll to the end
        self.update_idletasks()
        self._parent_canvas.yview_moveto(1)

    def go_back(self):
        if self.reference_table.try_scroll(-1):
            self.interest_row -= 1
            self.last_entry_row = self.classifier.get_entry_prerequisites_for_manual_entry(self.interest_row)
            self.row_entry.add_entry_row_at(*self.last_entry_row)
        else:
            self.row_entry.add_entry_row_at(*self.last_entry_row)

        # move scroll to the end
        self.update_idletasks()
        self._parent_canvas.yview_moveto(1)
