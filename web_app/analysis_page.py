import customtkinter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import matplotlib as mpl

from web_app.components.dataframe_widget import DataFrameWidget
from web_app.components.search import Search
from web_app.helper_functions import get_hex
from web_app.theme_colors import colors


class AnalysisPage(customtkinter.CTkScrollableFrame):
    def __init__(self, master, db, **kwargs):
        super().__init__(master, **kwargs)

        self.db = db

        self.canvas = None
        self._setup_plot_colors()
        self.dataframe = self.get_joined()

        self.search = Search(self, self.dataframe, on_search=self.on_new_search)
        self.search.pack(fill='x')

        width = self.winfo_width()
        # Create a Figure, that will be used for creating a canvas
        self.fig = Figure(figsize=(32, 8), dpi=100, layout='tight')
        self.ax = self.fig.add_subplot(121)
        self.ax2 = self.fig.add_subplot(122)

        # Create a canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='x')

        self.df_display = None
        self.on_new_search(self.get_joined())


    def _setup_plot_colors(self):
        mpl.rcParams['text.color'] = colors['text'][1]
        mpl.rcParams['axes.labelcolor'] = colors['text'][1]
        mpl.rcParams['xtick.color'] = colors['text'][1]
        mpl.rcParams['ytick.color'] = colors['text'][1]
        mpl.rcParams['figure.facecolor'] = get_hex(self, colors['background2'][1])
        mpl.rcParams['axes.facecolor'] = get_hex(self, colors['background1'][1])
        mpl.rcParams['figure.figsize'] = [16, 9]
    def on_new_search(self, reduced_df):
        # Clear the old plot
        self.ax.clear()
        self.ax2.clear()

        for account in ('existence', 'life', 'cash'):
            data = reduced_df[reduced_df['Sub Account'] == account]
            self.ax.plot(data['Date'], data['Value'].cumsum(), label=account)

        df = self.merge_cats(reduced_df)
        self.ax2.pie(df['Amount'], labels=df.index.tolist())

        # Redraw the canvas
        self.canvas.draw()

        # TODO: add button to turn update preview separately
        '''
        # df preview
        if self.df_display is not None:
            self.df_display.destroy()
        self.df_display = DataFrameWidget(self, reduced_df, 0, 3)
        self.df_display.pack(fill='x')
        '''

    @staticmethod
    def merge_cats(df):
        who_copy = df['Who'].cat.add_categories(list(df['What'].cat.categories))
        df['What'] = df['What'].cat.add_categories(list(df['Who'].cat.categories))
        # fill na values with who labels
        df['What'] = df['What'].fillna(who_copy)
        df = df[['What', 'Amount']]
        df = df.groupby('What').sum()
        df = df[df['Amount'] < 0] * -1
        return df

    def display_figure(self, fig):
        # Create a canvas
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(expand=1)


    def get_joined(self):
        data = self.db.get_database()
        merged = self.db.get_merged()
        return data.merge(merged, on='ref')
