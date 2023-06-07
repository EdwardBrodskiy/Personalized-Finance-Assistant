import customtkinter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from web_app.components.search import Search


class AnalysisPage(customtkinter.CTkFrame):
    def __init__(self, master, db, **kwargs):
        super().__init__(master, **kwargs)

        self.db = db

        self.canvas = None

        self.search = Search(self, self.get_joined())
        self.search.pack(fill='x')
        # Create a Figure, that will be used for creating a canvas
        fig = Figure(figsize=(5, 4), dpi=100)
        t = np.arange(0, 3, .01)
        fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))

        self.display_figure(fig)

    def display_figure(self, fig):
        # Create a canvas
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack( expand=1)

    def get_joined(self):
        data = self.db.get_database()
        merged = self.db.get_merged()
        return data.merge(merged, on='ref')
