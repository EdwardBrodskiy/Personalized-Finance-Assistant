import customtkinter as ctk
import matplotlib as mpl
import pandas as pd
from matplotlib import gridspec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from helper_functions import get_hex, extract_tags
from web_app.components.menu import Menu
from web_app.components.notification import Notification
from web_app.theme_colors import colors


class GraphsDisplay(ctk.CTkFrame):
    def __init__(self, master, dataframe, **kwargs):
        super().__init__(master, **kwargs)

        self._dataframe = dataframe
        self._setup_plot_colors()

        self.settings = ctk.CTkFrame(self)
        self.settings.grid_columnconfigure(0, weight=1)  # TODO: fix layout division not in the center for some reason
        self.settings.grid_columnconfigure(1, weight=1)
        self.settings.pack(fill='x')

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
                    'default': 'Date'
                }
            ),
            'y_axis': (
                'OptionMenu',
                'y axis variable',
                {
                    'values': self.dataframe.columns,
                    'command': self._on_input_change,
                    'default': 'Value'
                }
            ),
            'plot_operation': (
                'OptionMenu',
                'x axis processing operation',
                {
                    'values': list(self.plot_operations.keys()),
                    'command': self._on_input_change,
                    'default': 'Cumulative Sum'
                }
            ),
            'tags_split': (
                'TagEntry',
                'Tags to split the plot',
                {
                    'suggestions': extract_tags(self._dataframe['Tags']),
                    'command': self._on_input_change,
                    'tag_selection_options': ('',),
                    'suggestions_only': True
                }
            )
        }, title='Plot')
        self.graphic_controls_plot.grid(column=0, row=0, sticky='news', padx=5, pady=5)

        self.category_columns = self._dataframe.select_dtypes(['category']).columns
        self.pie_operations = {
            'Count': lambda x: x,
            'Amount': lambda x: x.cumsum()
        }
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
                {
                    'command': self._on_input_change,
                    'default': 10,
                }
            ),
            'pie_operation': (
                'OptionMenu',
                'x axis processing operation',
                {
                    'values': list(self.pie_operations.keys()),
                    'command': self._on_input_change,
                    'default': 'Amount'
                }
            ),
            'tags_cats': (
                'TagEntry',
                'Tags to show',
                {
                    'suggestions': extract_tags(self._dataframe['Tags']),
                    'command': self._on_input_change,
                    'tag_selection_options': (' Incl', ' Excl'),
                    'suggestions_only': True
                }
            )
        }, title='Pie Plot')
        self.graphic_controls_pie.grid(column=1, row=0, sticky='news', padx=5, pady=5)

        # Create a Figure, that will be used for creating a canvas
        self.fig = Figure(figsize=(16, 6), dpi=100, layout='tight')
        gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1])
        self.ax1 = self.fig.add_subplot(gs[0])
        self.ax2 = self.fig.add_subplot(gs[1])

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
        self.ax1.clear()
        self.ax2.clear()
        try:
            x_axis, y_axis = self.graphic_controls_plot['x_axis'].get(), self.graphic_controls_plot['y_axis'].get()
            plot_operation = self.plot_operations[self.graphic_controls_plot['plot_operation'].get()]
            selected_tags = self.graphic_controls_plot['tags_split'].get()
            if selected_tags:
                for account in selected_tags:
                    data = self._dataframe[self._dataframe['Tags'].apply(lambda x: account in x)]
                    if len(data) == 0:
                        continue
                    self.ax1.plot(data[x_axis], plot_operation(data[y_axis]), label=account)
                data = self._dataframe[self._dataframe['Tags'].apply(
                    lambda x: all(selected_tag not in x for selected_tag in selected_tags))]
                if len(data):
                    self.ax1.plot(data[x_axis], plot_operation(data[y_axis]), label='Other Tag rows')
            else:
                self.ax1.plot(self._dataframe[x_axis], plot_operation(self._dataframe[y_axis]), label='All')
            self.ax1.legend(fontsize='large')
        except Exception as e:
            Notification(self, f'Error while drawing plot "{e}"')
            print(e)
            raise e

        try:
            df = self._dataframe.copy()
            df['Count'] = 1
            pie_operation = self.graphic_controls_pie['pie_operation'].get()
            self._determine_sign(df[pie_operation])
            if self.graphic_controls_pie['positive_values'].get() == 'off':
                df[pie_operation] = df[pie_operation] * -1
            df = df[df[pie_operation] > 0]
            df['cat'] = self._produce_cat_column(self._dataframe)
            # Calculate the sums
            sums = df.groupby('cat')[pie_operation].sum()

            # Identify the top 10 categories
            top_n = sums.sort_values(ascending=False).head(self.get_max_cats() - 1)

            # Calculate the sum of the remaining categories
            other = sums[~sums.index.isin(top_n.index)].sum()

            # Add the 'other' category to the top n
            if other > 0:
                top_n['other'] = other
            percentage = top_n / top_n.sum() * 100

            labels = [f'{name}  {value:0.2f} {percent:0.0f}%' for name, value, percent in
                      zip(top_n.index, top_n, percentage)]
            self.ax2.pie(top_n, labels=labels)
            self.ax2.legend(labels, loc='upper right')
        except Exception as e:
            Notification(self, f'Error while drawing pie plot "{e}"')
            print(e)
            raise e

        # Redraw the canvas
        self.canvas.draw()

    def _determine_sign(self, series: pd.Series):
        if (series >= 0).all():
            self.graphic_controls_pie['positive_values'].set('on')
        elif (series <= 0).all():
            self.graphic_controls_pie['positive_values'].set('off')

    def _produce_cat_column(self, df):
        df = df.copy()

        show_hide_selections = self.graphic_controls_pie['tags_cats'].get()
        tags_to_show = [tag for tag, key in show_hide_selections if key == 0]
        tags_to_hide = [tag for tag, key in show_hide_selections if key == 1]
        # eliminate non informative tags
        all_tags = list(extract_tags(df['Tags']))
        for tag_for_removal in all_tags:
            # remove if present in all rows, selected for exclusion, not selected for inclusion (if any are selected)
            if GraphsDisplay.is_tag_in_all_rows(df, tag_for_removal) or \
                    tag_for_removal in tags_to_hide or (tags_to_show and tag_for_removal not in tags_to_show):
                # Remove the tag from each list in the "Tags" column
                df['Tags'] = df['Tags'].apply(lambda tags: [tag for tag in tags if tag != tag_for_removal])

        cat = df['Tags'].apply(
            lambda tags: ', '.join(sorted(tags, key=lambda tag: all_tags.index(tag))))
        # cat = cat.astype('category')

        return cat

    def get_max_cats(self):
        value = self.graphic_controls_pie['max_cats'].get()
        number = 10
        try:
            number = int(value)
        except ValueError:
            Notification(self, f'{value} is not a valid integer using {number} instead')

        if number < 2:
            Notification(self, f"Number can't be less than 2")
            number = 10

        return number

    @staticmethod
    def is_tag_in_all_rows(df, tag):
        for tags in df['Tags']:
            if tag not in tags:
                return False
        return True
