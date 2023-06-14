import customtkinter as ctk
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from web_app.components.menu import Menu
from web_app.components.notification import Notification
from web_app.helper_functions import get_hex, extract_tags
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
        self.max_cats = ctk.StringVar(value='10')
        self.max_cats.trace_add('write', self._on_input_change)
        self.graphic_controls_pie = Menu(self.settings, {
            'positive_values': (
                'Toggle',
                'Use positive values only',
                {
                    'command': self._on_input_change
                }
            ),
            'max_cats': (
                'Entry',
                'Maximum number of categories',
                {'textvariable': self.max_cats}
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
            print(e)

        try:
            df = self._dataframe.copy()
            df['cat'] = self._produce_cat_column(self._dataframe)
            if self.graphic_controls_pie.elements['positive_values'][1].state() == 'off':
                df['Amount'] = df['Amount'] * -1
            df = df[df['Amount'] > 0]
            sums = df.groupby('cat')['Amount'].sum()
            self.ax2.pie(sums, labels=sums.index)
        except Exception as e:
            Notification(self, f'Error while drawing pie plot "{e}"')
            print(e)

        # Redraw the canvas
        self.canvas.draw()

    def _produce_cat_column(self, df):
        # eliminate non informative tags
        all_tags = list(extract_tags(df['Tags']))
        for tag_for_removal in all_tags:
            if GraphsDisplay.is_tag_in_all_rows(df, tag_for_removal):
                # Remove the tag from each list in the "Tags" column
                df['Tags'] = df['Tags'].apply(lambda tags: [tag for tag in tags if tag != tag_for_removal])

        cat = df['Tags'].apply(
            lambda tags: '_'.join(sorted(tags, key=lambda tag: all_tags.index(tag))))
        # cat = cat.astype('category')

        categories_top = cat.value_counts().index.tolist()[:self.get_max_cats()]
        # cat = cat.cat.add_categories('other')
        return cat.where(cat.isin(categories_top), 'other')

    def get_max_cats(self):
        value = self.max_cats.get()
        number = 10
        try:
            number = int(value)
        except TypeError:
            Notification(self, f'{value} is not a valid integer')

        if number < 2:
            Notification(self, f"{number} can't be less than 2")
            number = 10

        return number

    @staticmethod
    def is_tag_in_all_rows(df, tag):
        for tags in df['Tags']:
            if tag not in tags:
                return False
        return True
