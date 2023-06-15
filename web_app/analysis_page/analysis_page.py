import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from web_app.analysis_page.dataframe_viewer import DataFrameViewer
from web_app.analysis_page.insights import Insights
from web_app.components.search import Search
from web_app.analysis_page.graphs import GraphsDisplay


class AnalysisPage(ctk.CTkScrollableFrame):
    def __init__(self, master, db, **kwargs):
        super().__init__(master, **kwargs)

        self.db = db

        self.canvas = None

        self.dataframe = self.get_joined()

        self.searched_dataframe = self.dataframe.copy()

        self.search = Search(self, self.dataframe, on_search=self.on_new_search)
        self.search.pack(fill='x')

        # Graphics
        self.graphics = GraphsDisplay(self, self.searched_dataframe)
        self.graphics.pack(fill='x')

        self.insights = Insights(self, self.searched_dataframe)
        self.insights.pack(fill='x')

        # Table preview
        self.table = DataFrameViewer(self, self.searched_dataframe)
        self.table.pack(fill='x')

        # white space footer

        self.footer = ctk.CTkFrame(self, height=600)
        self.footer.pack(fill='x')

        self.on_input_change()

    def on_new_search(self, new_search):
        self.searched_dataframe = new_search
        self.on_input_change()

    def on_input_change(self, *args):
        self.graphics.dataframe = self.searched_dataframe

        self.table.dataframe = self.searched_dataframe
        self.table.current_name = self.search.file_name.get()

        self.insights.dataframe = self.searched_dataframe

    def display_figure(self, fig):
        # Create a canvas
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(expand=1)

    def get_joined(self):
        data = self.db.get_database()
        merged = self.db.get_merged()
        return data.merge(merged, on='ref')
