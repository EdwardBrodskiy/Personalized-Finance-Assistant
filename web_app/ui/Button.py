from customtkinter import CTkButton, CTkFrame

from web_app.theme_colors import colors


class Button(CTkButton):
    variants = ('normal', 'outline')
    color_styles = ('primary', 'notification', 'info', 'warn', 'error')

    def __init__(self, master, variant='normal', color_style='primary', **kwargs):
        styles = self.determine_style(variant, color_style)

        super().__init__(master, **styles, **kwargs)
        self.color_style = color_style
        self.variant = variant

    @staticmethod
    def determine_style(variant, color_style):
        styles = {}
        if variant == 'normal':
            styles = {
                'fg_color': colors[color_style]
            }
        elif variant == 'outline':
            styles = {
                'fg_color': 'transparent',
                'border_width': 2,
                'text_color': colors['text']
            }
        return styles

    def configure(self, require_redraw=False, variant=None, color_style=None, **kwargs):
        if color_style is not None:
            self.color_style = color_style
        if variant is not None:
            self.variant = variant

        styles = self.determine_style(self.variant, self.color_style)
        super().configure(**styles, **kwargs)


class DemoButtons(CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(list(range(len(Button.color_styles))), weight=1)
        self.grid_rowconfigure(list(range(len(Button.variants))), weight=1)

        for col_i, color_style in enumerate(Button.color_styles):
            for row_i, variant in enumerate(Button.variants):
                button = Button(self, variant=variant, color_style=color_style)
                button.grid(column=col_i, row=row_i, padx=5, pady=5)
