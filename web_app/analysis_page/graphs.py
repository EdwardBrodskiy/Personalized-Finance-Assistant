import customtkinter as ctk
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from web_app.components.menu import Menu
from web_app.components.notification import Notification
from web_app.helper_functions import get_hex
from web_app.theme_colors import colors


class GraphsDisplay(ctk.CTkFrame):
    def __init__(self, master, dataframe, **kwargs):
        super().__init__(master, **kwargs)

        self._dataframe = dataframe
        self._setup_plot_colors()

        self.settings = ctk.CTkFrame(self)
        self.settings.grid_columnconfigure((0, 1),
                                           weight=1)  # TODO: fix layout division not in the center for some reason
        self.settings.pack(fill='x')

        self.x_axis = ctk.StringVar(value='Date')
        self.y_axis = ctk.StringVar(value='Value')
        self.plot_operation = ctk.StringVar(value='Cumulative Sum')
        self.plot_operations = {
            'None': lambda x: x,
            'Cumulative Sum': lambda x: x.cumsum()
        }
        self.graphic_controls_plot = Menu(self.settings, {
            'x_axis': (
                'OptionMenu',
                'x axis variable',
                {
                    'values': self.dataframe.columns,
                    'command': self._on_input_change,
                    'variable': self.x_axis,
                }
            ),
            'y_axis': (
                'OptionMenu',
                'y axis variable',
                {
                    'values': self.dataframe.columns,
                    'command': self._on_input_change,
                    'variable': self.y_axis,
                }
            ),
            'plot_operation': (
                'OptionMenu',
                'x axis processing operation',
                {
                    'values': list(self.plot_operations.keys()),
                    'command': self._on_input_change,
                    'variable': self.plot_operation,
                }
            ),
        }, title='Plot')
        self.graphic_controls_plot.grid(column=0, row=0, sticky='new', padx=5, pady=5)

        self.category_columns = self._dataframe.select_dtypes(['category']).columns
        self.graphic_controls_pie = Menu(self.settings, {
            'category': (
                'OptionMenu',
                'x axis variable',
                {
                    'values': self.dataframe.columns,
                    'command': self._on_input_change,
                    'variable': self.x_axis,
                }
            ),
            'y_axis': (
                'OptionMenu',
                'y axis variable',
                {
                    'values': self.dataframe.columns,
                    'command': self._on_input_change,
                    'variable': self.y_axis,
                }
            ),
        }, title='Pie Plot')
        self.graphic_controls_pie.grid(column=1, row=0, sticky='new', padx=5, pady=5)

        # Create a Figure, that will be used for creating a canvas
        self.fig = Figure(figsize=(16, 6), dpi=100, layout='tight')
        self.ax = self.fig.add_subplot(121)
        self.ax2 = self.fig.add_subplot(122)

        # Create a canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='x')

    @property
    def dataframe(self):
        return self._dataframe

    @dataframe.setter
    def dataframe(self, value):
        self._dataframe = value
        self._on_input_change()

    def _setup_plot_colors(self):
        mpl.rcParams['text.color'] = colors['text'][1]
        mpl.rcParams['axes.labelcolor'] = colors['text'][1]
        mpl.rcParams['xtick.color'] = colors['text'][1]
        mpl.rcParams['ytick.color'] = colors['text'][1]
        mpl.rcParams['figure.facecolor'] = get_hex(self, colors['background2'][1])
        mpl.rcParams['axes.facecolor'] = get_hex(self, colors['background1'][1])
        mpl.rcParams['figure.figsize'] = [16, 9]
        mpl.rcParams["legend.edgecolor"] = get_hex(self, colors['background2'][1])
        mpl.rcParams["legend.facecolor"] = get_hex(self, colors['background2'][1])

    def _on_input_change(self, *args):
        # Clear the old plot
        self.ax.clear()
        self.ax2.clear()
        try:
            for account in ('existence', 'life', 'cash'):
                data = self._dataframe[self._dataframe['Sub Account'] == account]
                self.ax.plot(data[self.x_axis.get()],
                             self.plot_operations[self.plot_operation.get()](data[self.y_axis.get()]), label=account)
            self.ax.legend(fontsize='large')
        except Exception as e:
            Notification(self, f'Error while drawing plot "{e}"')

        # try:
        #     df = self.merge_cats(self._dataframe)
        #     self.ax2.pie(df['Amount'], labels=df.index.tolist())
        # except Exception as e:
        #     Notification(self, f'Error while drawing pie plot "{e}"')
        # Redraw the canvas
        self.canvas.draw()

    @staticmethod
    def _merge_cats(df, higher_level, lower_level):
        df = df.copy()
        who_copy = df[higher_level].cat.add_categories(list(df[lower_level].cat.categories))
        df[lower_level] = df[lower_level].cat.add_categories(list(df[higher_level].cat.categories))
        # fill na values with who labels
        df[lower_level] = df[lower_level].fillna(who_copy)
        df = df[['What', 'Amount']]
        df = df.groupby('What').sum()
        df = df[df['Amount'] < 0] * -1
        return df
